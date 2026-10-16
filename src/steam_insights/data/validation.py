"""Snapshot contracts: report defects rather than silently deleting observations."""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from steam_insights.data.text import word_count

REVIEW_REQUIRED = {
    "appid",
    "game",
    "review_id",
    "review_text",
    "language",
    "created_utc",
    "updated_utc",
    "timestamp_created",
    "timestamp_updated",
    "recommended",
}
ANNOUNCEMENT_REQUIRED = {
    "appid",
    "game",
    "gid",
    "title",
    "text",
    "date_utc",
    "timestamp",
    "source_url",
}
REVIEW_BOOLEANS = (
    "recommended",
    "unedited",
    "text_eligible",
    "primarily_steam_deck",
    "steam_purchase",
    "refunded",
    "mentions_update",
    "mentions_stability",
    "mentions_balance",
    "mentions_monetization",
    "mentions_cheating",
    "mentions_bugs",
    "mentions_version",
)


@dataclass
class ValidationReport:
    dataset: str
    rows: int
    issues: list[dict] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(issue["severity"] == "error" for issue in self.issues)

    def add(self, check: str, count: int, detail: str, severity: str = "error") -> None:
        if count:
            self.issues.append(
                {"check": check, "count": int(count), "severity": severity, "detail": detail}
            )

    def to_dict(self) -> dict:
        return {
            "dataset": self.dataset,
            "rows": self.rows,
            "valid": self.valid,
            "issues": self.issues,
        }

    def require_valid(self) -> None:
        if not self.valid:
            failures = "; ".join(
                f"{item['check']}={item['count']}"
                for item in self.issues
                if item["severity"] == "error"
            )
            raise ValueError(f"{self.dataset} failed validation: {failures}")


def utc_dates(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, format="ISO8601", errors="coerce", utc=True)


def boolean_values(series: pd.Series) -> pd.Series:
    return (
        series.astype("string")
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False})
        .astype("boolean")
    )


def _common(frame: pd.DataFrame, report: ValidationReport, required: set[str], key: str) -> bool:
    missing = sorted(required - set(frame.columns))
    report.add("missing_columns", len(missing), ", ".join(missing))
    report.add("empty_dataset", int(frame.empty), "No observations to process")
    if missing:
        return False
    for column in ("appid", key):
        values = frame[column].astype("string").str.strip()
        valid_id = values.str.fullmatch(r"[1-9][0-9]*", na=False)
        report.add(f"invalid_{column}", (~valid_id).sum(), "Expected a positive decimal ID")
        if column == "appid":
            numeric = pd.to_numeric(values, errors="coerce")
            report.add(
                "appid_out_of_range", (numeric > 2**32 - 1).sum(), "Expected a uint32 app ID"
            )
    keys = frame[["appid", key]].astype("string").apply(lambda s: s.str.strip())
    report.add(
        "duplicate_keys",
        keys.duplicated(keep=False).sum(),
        "All rows sharing (appid, source ID); no implicit revision selection",
    )
    report.add(
        "missing_game",
        frame["game"].isna().sum() + frame["game"].eq("").sum(),
        "A game display name is required",
    )
    return True


def _boolean_checks(
    frame: pd.DataFrame, report: ValidationReport, columns: tuple[str, ...]
) -> None:
    for column in columns:
        if column not in frame:
            continue
        values = frame[column].astype("string").str.strip().str.lower()
        absent = values.isna() | values.eq("")
        invalid = ~values.isin(["true", "false"]) & ~absent
        if column == "recommended":
            invalid = invalid | absent
        report.add(
            f"invalid_boolean_{column}", invalid.sum(), "Expected true/false, not truthiness"
        )


def _timestamps(frame: pd.DataFrame, report: ValidationReport, iso: str, epoch: str) -> pd.Series:
    parsed = utc_dates(frame[iso])
    number = pd.to_numeric(frame[epoch], errors="coerce")
    epoch_dates = pd.to_datetime(number, unit="s", errors="coerce", utc=True)
    invalid_number = number.isna() | (number < 0) | (number % 1 != 0)
    report.add(f"invalid_{epoch}", invalid_number.sum(), "Expected nonnegative epoch seconds")
    report.add(f"invalid_{iso}", parsed.isna().sum(), "Expected an ISO timestamp")
    comparable = parsed.notna() & epoch_dates.notna()
    report.add(
        f"timestamp_mismatch_{iso}",
        (comparable & parsed.ne(epoch_dates)).sum(),
        "ISO and epoch representations must agree",
    )
    return parsed


def validate_reviews(
    frame: pd.DataFrame, name: str = "reviews", language: str = "english"
) -> ValidationReport:
    report = ValidationReport(name, len(frame))
    if not _common(frame, report, REVIEW_REQUIRED, "review_id"):
        return report
    _boolean_checks(frame, report, REVIEW_BOOLEANS)
    created = _timestamps(frame, report, "created_utc", "timestamp_created")
    updated = _timestamps(frame, report, "updated_utc", "timestamp_updated")
    report.add(
        "updated_before_created", (updated < created).sum(), "Updates cannot precede creation"
    )
    report.add(
        "unexpected_language",
        frame["language"].ne(language).sum(),
        f"This snapshot is configured for {language!r}",
    )
    if "unedited" in frame:
        exported = boolean_values(frame["unedited"])
        report.add(
            "unedited_flag_mismatch",
            exported.ne(created.eq(updated)).fillna(False).sum(),
            "The exported unedited flag must match timestamp equality",
        )
    for column in ("playtime_at_review_hours", "lifetime_playtime_hours"):
        if column in frame:
            original = frame[column].astype("string")
            number = pd.to_numeric(original, errors="coerce")
            present = original.notna() & original.ne("")
            finite = pd.Series(
                np.isfinite(number.to_numpy(dtype=float, na_value=np.nan)), index=frame.index
            )
            report.add(
                f"invalid_{column}",
                (present & (~finite | number.lt(0))).sum(),
                "Playtime is nullable, otherwise finite and nonnegative",
            )
    text = frame["review_text"].fillna("")
    if "word_count" in frame:
        original = frame["word_count"].astype("string")
        number = pd.to_numeric(original, errors="coerce")
        present = original.notna() & original.ne("")
        invalid = present & (number.isna() | number.lt(0) | number.mod(1).ne(0))
        report.add("invalid_word_count", invalid.sum(), "Expected a nullable nonnegative integer")
        computed = text.map(word_count)
        report.add(
            "word_count_mismatch",
            (present & ~invalid & number.ne(computed)).sum(),
            "Computed word counts drive eligibility; supplied counts are preserved",
            "warning",
        )
    report.add(
        "empty_text",
        text.str.strip().eq("").sum(),
        "Retained for vote counts; has no usable text",
        "warning",
    )
    report.add(
        "repeated_review_text",
        text[text.str.strip().ne("")].duplicated().sum(),
        "Repeated wording is retained; inspect for memes or duplicate families",
        "warning",
    )
    return report


def validate_announcements(frame: pd.DataFrame) -> ValidationReport:
    report = ValidationReport("announcements", len(frame))
    if not _common(frame, report, ANNOUNCEMENT_REQUIRED, "gid"):
        return report
    _timestamps(frame, report, "date_utc", "timestamp")
    _boolean_checks(frame, report, ("patch_candidate",))
    for column in ("title", "text", "source_url"):
        report.add(
            f"empty_{column}",
            frame[column].fillna("").str.strip().eq("").sum(),
            "Source coverage needs inspection",
            "warning",
        )
    return report
