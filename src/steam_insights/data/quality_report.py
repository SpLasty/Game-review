"""Build a reproducible snapshot-quality and patch-window coverage report."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from steam_insights.config import DataConfig
from steam_insights.data.exploration import profile
from steam_insights.data.io import read_csv
from steam_insights.data.preprocessing import word_count
from steam_insights.data.validation import boolean_values, utc_dates

WINDOW_DAYS = 14
MIN_REVIEWS_PER_SIDE = 30
MIN_ACTIVE_DAYS_PER_SIDE = 7
STRONG_REVIEWS_PER_SIDE = 100


def _markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    def cell(value: object) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(cell(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def _side_summary(frame: pd.DataFrame) -> dict[str, object]:
    votes = frame["_vote"]
    valid_votes = votes.notna()
    negative = votes.eq(False)
    eligible = frame["_eligible"]
    return {
        "reviews": len(frame),
        "text_eligible_reviews": int(eligible.sum()),
        "text_eligible_days": int(frame.loc[eligible, "_date"].nunique()),
        "valid_recommendation_votes": int(valid_votes.sum()),
        "negative_recommendations": int((negative & valid_votes).sum()),
        "negative_recommendation_share": (
            float((negative & valid_votes).sum() / valid_votes.sum()) if valid_votes.any() else None
        ),
    }


def patch_window_table(
    reviews: pd.DataFrame,
    announcements: pd.DataFrame,
    *,
    language: str = "english",
    minimum_words: int = 10,
    window_days: int = WINDOW_DAYS,
) -> pd.DataFrame:
    """Count observed review coverage around candidate or manually verified patch posts.

    Windows are anchored on the announcement publication timestamp, which may differ from
    the actual release time. Only the full English review snapshot is used; the capped balanced
    export is excluded because it overlaps that snapshot.
    """
    review_work = reviews[["appid", "created_utc", "review_text", "language", "recommended"]].copy()
    review_work["_created"] = utc_dates(review_work["created_utc"])
    review_work["_date"] = review_work["_created"].dt.floor("D")
    review_work["_words"] = review_work["review_text"].fillna("").map(word_count)
    review_work["_eligible"] = review_work["_words"].ge(minimum_words) & review_work["language"].eq(
        language
    )
    review_work["_vote"] = boolean_values(review_work["recommended"])
    review_work = review_work.loc[review_work["_created"].notna()]
    bounds = review_work.groupby("appid", sort=False)["_created"].agg(["min", "max"])
    grouped_reviews = {
        appid: group.sort_values("_created")
        for appid, group in review_work.groupby("appid", sort=False)
    }

    note_work = announcements.copy()
    note_work["_date"] = utc_dates(note_work["date_utc"])
    candidate = boolean_values(note_work["patch_candidate"]).fillna(False)
    verification = note_work["verification_status"].astype("string").str.strip().str.lower()
    verified = verification.eq("manually_verified_patch").fillna(False)
    note_work["_candidate"] = candidate
    note_work["_verified"] = verified
    note_work = note_work.loc[(candidate | verified) & note_work["_date"].notna()].copy()

    window = timedelta(days=window_days)
    rows: list[dict[str, object]] = []
    for note in note_work.to_dict(orient="records"):
        appid = str(note["appid"])
        event_at = note["_date"]
        before_start = event_at - window
        after_end = event_at + window
        game_reviews = grouped_reviews.get(appid, review_work.iloc[0:0])
        before = game_reviews.loc[
            game_reviews["_created"].ge(before_start) & game_reviews["_created"].lt(event_at)
        ]
        after = game_reviews.loc[
            game_reviews["_created"].ge(event_at) & game_reviews["_created"].lt(after_end)
        ]
        before_summary = _side_summary(before)
        after_summary = _side_summary(after)
        has_bounds = appid in bounds.index and (
            bounds.loc[appid, "min"] <= before_start and bounds.loc[appid, "max"] >= after_end
        )
        enough_counts = (
            before_summary["text_eligible_reviews"] >= MIN_REVIEWS_PER_SIDE
            and after_summary["text_eligible_reviews"] >= MIN_REVIEWS_PER_SIDE
        )
        enough_days = (
            before_summary["text_eligible_days"] >= MIN_ACTIVE_DAYS_PER_SIDE
            and after_summary["text_eligible_days"] >= MIN_ACTIVE_DAYS_PER_SIDE
        )
        exploratory_coverage = bool(has_bounds and enough_counts and enough_days)
        strong_coverage = bool(
            exploratory_coverage
            and before_summary["text_eligible_reviews"] >= STRONG_REVIEWS_PER_SIDE
            and after_summary["text_eligible_reviews"] >= STRONG_REVIEWS_PER_SIDE
        )
        is_verified = bool(note["_verified"])
        if is_verified and strong_coverage:
            status = "verified_patch_strong_exploratory_coverage"
        elif is_verified and exploratory_coverage:
            status = "verified_patch_screening_sufficient"
        elif is_verified:
            status = "verified_patch_insufficient_or_edge_censored"
        elif strong_coverage:
            status = "unverified_candidate_strong_coverage_verify_patch"
        elif exploratory_coverage:
            status = "unverified_candidate_screening_coverage_verify_patch"
        else:
            status = "unverified_candidate_insufficient_or_edge_censored"

        rows.append(
            {
                "appid": appid,
                "game": note["game"],
                "gid": str(note["gid"]),
                "title": note["title"],
                "source_url": note["source_url"],
                "announcement_published_utc": event_at.isoformat(),
                "window_start_utc": before_start.isoformat(),
                "window_split_utc": event_at.isoformat(),
                "window_end_utc": after_end.isoformat(),
                "release_branch_hint": note.get("release_branch_hint", ""),
                "patch_candidate_heuristic": bool(note["_candidate"]),
                "verification_status": str(note["verification_status"]),
                "manually_verified_patch": is_verified,
                "review_date_bounds_cover_full_window": bool(has_bounds),
                "pre_reviews": before_summary["reviews"],
                "pre_text_eligible_reviews": before_summary["text_eligible_reviews"],
                "pre_text_eligible_days": before_summary["text_eligible_days"],
                "pre_valid_recommendation_votes": before_summary["valid_recommendation_votes"],
                "pre_negative_recommendation_share": before_summary[
                    "negative_recommendation_share"
                ],
                "post_reviews": after_summary["reviews"],
                "post_text_eligible_reviews": after_summary["text_eligible_reviews"],
                "post_text_eligible_days": after_summary["text_eligible_days"],
                "post_valid_recommendation_votes": after_summary["valid_recommendation_votes"],
                "post_negative_recommendation_share": after_summary[
                    "negative_recommendation_share"
                ],
                "exploratory_coverage_threshold_met": exploratory_coverage,
                "stronger_coverage_threshold_met": strong_coverage,
                "coverage_assessment": status,
            }
        )
    columns = [
        "appid",
        "game",
        "gid",
        "title",
        "source_url",
        "announcement_published_utc",
        "window_start_utc",
        "window_split_utc",
        "window_end_utc",
        "release_branch_hint",
        "patch_candidate_heuristic",
        "verification_status",
        "manually_verified_patch",
        "review_date_bounds_cover_full_window",
        "pre_reviews",
        "pre_text_eligible_reviews",
        "pre_text_eligible_days",
        "pre_valid_recommendation_votes",
        "pre_negative_recommendation_share",
        "post_reviews",
        "post_text_eligible_reviews",
        "post_text_eligible_days",
        "post_valid_recommendation_votes",
        "post_negative_recommendation_share",
        "exploratory_coverage_threshold_met",
        "stronger_coverage_threshold_met",
        "coverage_assessment",
    ]
    return (
        pd.DataFrame(rows, columns=columns)
        .sort_values(["game", "announcement_published_utc", "gid"], kind="stable")
        .reset_index(drop=True)
    )


def _game_window_summary(windows: pd.DataFrame) -> pd.DataFrame:
    if windows.empty:
        return pd.DataFrame(
            columns=[
                "appid",
                "game",
                "candidate_or_verified_windows",
                "manually_verified_patches",
                "verified_screening_sufficient",
                "verified_strong_coverage",
                "unverified_candidates_screening_coverage",
            ]
        )
    return (
        windows.groupby(["appid", "game"], sort=True)
        .agg(
            candidate_or_verified_windows=("gid", "size"),
            manually_verified_patches=("manually_verified_patch", "sum"),
            verified_screening_sufficient=(
                "coverage_assessment",
                lambda values: (
                    values.eq("verified_patch_screening_sufficient").sum()
                    + values.eq("verified_patch_strong_exploratory_coverage").sum()
                ),
            ),
            verified_strong_coverage=(
                "coverage_assessment",
                lambda values: values.eq("verified_patch_strong_exploratory_coverage").sum(),
            ),
            unverified_candidates_screening_coverage=(
                "coverage_assessment",
                lambda values: (
                    values.eq("unverified_candidate_screening_coverage_verify_patch").sum()
                    + values.eq("unverified_candidate_strong_coverage_verify_patch").sum()
                ),
            ),
        )
        .reset_index()
    )


def _report_markdown(config: DataConfig, profile_result: dict, windows: pd.DataFrame) -> str:
    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        "# Steam data quality and patch-window report",
        "",
        f"Generated: `{generated}`",
        "",
        "## Scope and overall assessment",
        "",
        "This report checks the current CSV snapshot and measures review availability around "
        "developer announcement posts. It is a data-readiness report, not a model result or a "
        "causal estimate of patch impact.",
        "",
        "The full English review export is the review denominator. The balanced export is "
        "reported separately and is not added to it because the two files overlap. A Steam "
        "recommendation is a game-level vote, not sentiment toward each change mentioned in a review.",
        "",
        "### Source snapshots",
        "",
    ]
    inventory_sources = profile_result.get("sources", {})
    source_rows = []
    for name, source in inventory_sources.items():
        source_rows.append(
            [
                name,
                f"{source.get('rows', 0):,}",
                source.get("sha256", ""),
                source.get("path", ""),
            ]
        )
    lines.append(_markdown_table(["Dataset", "Rows", "SHA-256", "Source"], source_rows))
    lines.extend(["", "### Review population summary", ""])
    population_rows = []
    for item in profile_result.get("review_populations", []):
        population_rows.append(
            [
                item["dataset"],
                f"{item['reviews']:,}",
                item["games"],
                f"{item['negative_share']:.2%}" if item["negative_share"] is not None else "n/a",
                f"{item['below_minimum_words']:,}",
                f"{item['edited_latest_snapshot']:,}",
                item["earliest_created_utc"],
                item["latest_created_utc"],
            ]
        )
    lines.append(
        _markdown_table(
            [
                "Population",
                "Reviews",
                "Games",
                "Negative vote share",
                "Below text threshold",
                "Edited timestamp proxy",
                "First review UTC",
                "Last review UTC",
            ],
            population_rows,
        )
    )
    lines.extend(
        [
            "",
            "The edited count compares creation and latest update timestamps; the export does not "
            "preserve historical review text or vote revisions. The collected reviews are a "
            "time-skewed snapshot, not a complete census of Steam reviews.",
            "",
            "## Validation and missingness",
            "",
            "The validator checks required fields, duplicate `(appid, source ID)` keys, language, "
            "timestamp parsing and ISO/epoch agreement, timestamp order, explicit booleans, "
            "playtime/count fields, empty text, and repeated wording.",
            "",
        ]
    )
    validation_rows = []
    for dataset in profile_result.get("validation", []):
        issues = dataset.get("issues", [])
        errors = sum(issue["count"] for issue in issues if issue["severity"] == "error")
        warnings = sum(issue["count"] for issue in issues if issue["severity"] == "warning")
        validation_rows.append(
            [
                dataset["dataset"],
                f"{dataset['rows']:,}",
                "passed" if dataset["valid"] else "failed",
                errors,
                warnings,
            ]
        )
    lines.append(
        _markdown_table(
            ["Dataset", "Rows", "Validation", "Error rows/checks", "Warning counts"],
            validation_rows,
        )
    )
    lines.extend(["", "Observed nonzero validation findings:", ""])
    issue_rows = []
    for dataset in profile_result.get("validation", []):
        for issue in dataset.get("issues", []):
            issue_rows.append(
                [
                    dataset["dataset"],
                    issue["check"],
                    issue["count"],
                    issue["severity"],
                    issue["detail"],
                ]
            )
    lines.append(
        _markdown_table(["Dataset", "Check", "Count", "Severity", "Interpretation"], issue_rows)
        if issue_rows
        else "No nonzero validation findings were recorded."
    )

    quality_dir = config.quality_dir or config.root / "reports" / "data_quality"
    missing_path = config.reports_dir / "missing_values.csv"
    missing_rows = []
    if missing_path.exists():
        missing = pd.read_csv(missing_path, dtype={"dataset": "string", "column": "string"})
        missing = missing.loc[missing["missing"].gt(0)]
        missing_rows = [
            [row.dataset, row.column, f"{int(row.missing):,}", f"{int(row.rows):,}"]
            for row in missing.itertuples(index=False)
        ]
    lines.extend(["", "Nonzero missing/blank field counts:", ""])
    lines.append(
        _markdown_table(["Dataset", "Field", "Missing or blank", "Rows"], missing_rows)
        if missing_rows
        else "No missing or blank field values were found in the source columns."
    )

    lines.extend(["", "## Game-level review and announcement coverage", ""])
    reviews_by_game_path = config.reports_dir / "reviews_by_game.csv"
    notes_by_game_path = config.reports_dir / "announcements_by_game.csv"
    reviews_by_game = (
        pd.read_csv(reviews_by_game_path, dtype={"appid": "string"})
        if reviews_by_game_path.exists()
        else pd.DataFrame()
    )
    notes_by_game = (
        pd.read_csv(notes_by_game_path, dtype={"appid": "string"})
        if notes_by_game_path.exists()
        else pd.DataFrame()
    )
    game_windows = _game_window_summary(windows)
    if not reviews_by_game.empty:
        coverage = reviews_by_game.merge(
            notes_by_game,
            on=["appid", "game"],
            how="outer",
            suffixes=("_reviews", "_announcements"),
        )
        coverage = coverage.merge(game_windows, on=["appid", "game"], how="left")
        coverage = coverage.fillna(
            {
                "reviews": 0,
                "valid_votes": 0,
                "short_reviews": 0,
                "edited_reviews": 0,
                "announcements": 0,
                "candidate_or_verified_windows": 0,
                "manually_verified_patches": 0,
                "verified_screening_sufficient": 0,
                "verified_strong_coverage": 0,
                "unverified_candidates_screening_coverage": 0,
            }
        )
        coverage.to_csv(quality_dir / "game_quality_summary.csv", index=False)
        game_rows = [
            [
                row.game,
                f"{int(row.reviews):,}",
                row.earliest_created_utc,
                row.latest_created_utc,
                f"{int(row.announcements):,}",
                int(row.manually_verified_patches),
                int(row.verified_screening_sufficient),
                int(row.unverified_candidates_screening_coverage),
            ]
            for row in coverage.sort_values("game").itertuples(index=False)
        ]
        lines.append(
            _markdown_table(
                [
                    "Game",
                    "Reviews",
                    "First review UTC",
                    "Last review UTC",
                    "Announcement posts",
                    "Verified patches",
                    "Verified with enough window data",
                    "Unverified candidates with enough window data",
                ],
                game_rows,
            )
        )
    else:
        lines.append(
            "Per-game review tables were unavailable because required profile inputs were invalid."
        )

    announcement_info = profile_result.get("announcements", {})
    lines.extend(["", "## Announcement quality", ""])
    lines.append(
        f"The snapshot contains **{announcement_info.get('posts', 0):,} posts** across "
        f"**{announcement_info.get('games', 0)} games**. **{announcement_info.get('heuristic_patch_candidates', 0):,}** "
        "are marked as heuristic patch candidates. Verification flags: "
        + ", ".join(
            f"`{name}` {count:,}"
            for name, count in announcement_info.get("verification_flags", {}).items()
        )
        + "."
    )
    branch_rows = [
        [name, f"{count:,}"] for name, count in announcement_info.get("branch_hints", {}).items()
    ]
    if branch_rows:
        lines.extend(
            [
                "",
                "Existing branch-hint values:",
                "",
                _markdown_table(["Hint", "Posts"], branch_rows),
            ]
        )
    lines.extend(
        [
            "",
            "A candidate flag is not a verified patch-note label; only manually verified posts "
            "are treated as confirmed patch announcements below. `date_utc` is the post "
            "publication time, not necessarily the release time. The export has no dedicated "
            "platform field, and flattened text cannot recover original headings.",
            "",
            "## Patch-window review coverage",
            "",
            f"Each included candidate or manually verified post is centered on its publication "
            f"timestamp. The pre window is `[post time - {WINDOW_DAYS} days, post time)` and the "
            f"post window is `[post time, post time + {WINDOW_DAYS} days)`. Review eligibility "
            f"requires at least {config.minimum_words} Unicode word runs and language `{config.language}`. "
            "Counts use the full review snapshot only; the overlapping balanced export is excluded.",
            "",
            f"For this report, a window passes the **exploratory coverage screen** when each side "
            f"has at least {MIN_REVIEWS_PER_SIDE} text-eligible reviews on at least "
            f"{MIN_ACTIVE_DAYS_PER_SIDE} distinct review dates, and the game's observed review "
            "date range spans the complete 28-day window. The stronger coverage flag raises "
            f"the count threshold to {STRONG_REVIEWS_PER_SIDE} per side. These are transparent "
            "screening rules, not a guarantee of statistical power or complete Steam coverage.",
            "",
        ]
    )
    if windows.empty:
        lines.append("No candidate or manually verified announcement windows could be assessed.")
    else:
        counts = windows["coverage_assessment"].value_counts()
        summary_rows = [
            [name.replace("_", " "), f"{int(count):,}"] for name, count in counts.items()
        ]
        lines.append(_markdown_table(["Assessment", "Announcement windows"], summary_rows))
        sufficient_verified = windows.loc[
            windows["manually_verified_patch"] & windows["exploratory_coverage_threshold_met"]
        ]
        if sufficient_verified.empty:
            finding = "No manually verified patch window passes the exploratory coverage screen."
        else:
            examples = []
            for row in sufficient_verified.itertuples(index=False):
                examples.append(
                    f"**{row.game} — {row.title}** (published {row.announcement_published_utc}; "
                    f"window {row.window_start_utc} to {row.window_end_utc}, with "
                    f"{int(row.pre_text_eligible_reviews):,}/{int(row.post_text_eligible_reviews):,} "
                    "eligible reviews over "
                    f"{int(row.pre_text_eligible_days)}/{int(row.post_text_eligible_days)} "
                    "active dates before/after)."
                )
            finding = (
                f"**{len(sufficient_verified)} manually verified patch window(s)** pass the "
                "exploratory coverage screen: " + " ".join(examples)
            )
        lines.extend(["", finding])
        verified_windows = windows.loc[windows["manually_verified_patch"]]
        verified_rows = []
        for row in verified_windows.itertuples(index=False):
            title = str(row.title).replace("]", "\\]")
            title_cell = f"[{title}]({row.source_url})" if row.source_url else title
            verified_rows.append(
                [
                    row.game,
                    row.announcement_published_utc,
                    title_cell,
                    f"{int(row.pre_text_eligible_reviews)} ({int(row.pre_text_eligible_days)} d)",
                    f"{int(row.post_text_eligible_reviews)} ({int(row.post_text_eligible_days)} d)",
                    "yes" if row.review_date_bounds_cover_full_window else "no",
                    row.coverage_assessment.replace("_", " "),
                ]
            )
        if verified_rows:
            lines.extend(
                [
                    "",
                    "### Manually verified patch posts",
                    "",
                    _markdown_table(
                        [
                            "Game",
                            "Post published UTC",
                            "Announcement",
                            "Pre eligible (days)",
                            "Post eligible (days)",
                            "Full observed bounds",
                            "Coverage screen",
                        ],
                        verified_rows,
                    ),
                ]
            )
        candidate_coverage = windows.loc[
            ~windows["manually_verified_patch"] & windows["exploratory_coverage_threshold_met"]
        ]
        lines.extend(
            [
                "",
                f"**{len(candidate_coverage):,} unverified candidate windows** pass the review "
                "coverage screen but still require manual confirmation that each post is a patch "
                "and that its publication time is a suitable event anchor. The detailed CSV lists "
                "all assessed windows, counts, dates, titles, links, branch hints, and status.",
            ]
        )
    lines.extend(
        [
            "",
            "### Interpretation limits",
            "",
            "- Coverage thresholds measure the saved snapshot, not the Steam review population; "
            "missing review dates do not prove zero activity or complete API collection.",
            "- Windows are anchored to announcement publication time. A later effective release "
            "time, hotfix, staged rollout, or beta-only change can shift the true event.",
            "- Review text and recommendation votes are the latest exported state. A review "
            "created before a patch may have been edited after it.",
            "- Nearby or duplicate announcement posts can create overlapping windows; the report "
            "keeps posts separate and does not infer independent interventions.",
            "- The report describes vote patterns and text availability. It does not label "
            "change-specific sentiment, establish causality, or evaluate whether a fix worked.",
            "",
            "## Supporting files",
            "",
            "- `patch_window_quality.csv`: one row for every heuristic candidate or manually "
            "verified patch post, with pre/post counts and screening status.",
            "- `game_quality_summary.csv`: per-game review, announcement, and patch-window counts.",
            "- `../data_exploration/`: source inventory, validation details, missingness, review "
            "coverage tables, and plots.",
            "",
        ]
    )
    if (quality_dir / "pipeline" / "report.md").exists():
        lines.extend(
            [
                "## End-to-end preprocessing update",
                "",
                "The [versioned pipeline report](pipeline/report.md) adds recovered announcement "
                "structure, evidence-backed patch-post confirmation, individual change candidates, "
                "model input exports, leakage controls, and current data-readiness gaps. "
                "The counts above describe the original CSV snapshot; the pipeline report also "
                "includes subsequent public source observations.",
                "",
            ]
        )
    return "\n".join(lines)


def generate_quality_report(config: DataConfig) -> dict[str, Path | int]:
    """Refresh exploration artifacts, then write the combined quality report and tables."""
    profile_result = profile(config)
    output_dir = config.quality_dir or config.root / "reports" / "data_quality"
    output_dir.mkdir(parents=True, exist_ok=True)
    reviews = read_csv(config.source("reviews"))
    announcements = read_csv(config.source("announcements"))
    windows = patch_window_table(
        reviews,
        announcements,
        language=config.language,
        minimum_words=config.minimum_words,
    )
    window_path = output_dir / "patch_window_quality.csv"
    windows.to_csv(window_path, index=False)
    game_path = output_dir / "game_quality_summary.csv"
    report_path = output_dir / "data_quality_report.md"
    report_path.write_text(_report_markdown(config, profile_result, windows), encoding="utf-8")
    return {
        "report": report_path,
        "patch_windows": window_path,
        "game_summary": game_path,
        "patch_window_count": len(windows),
    }
