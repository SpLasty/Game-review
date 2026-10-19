"""Language metadata summaries that preserve Steam's original API codes."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

# Steam API language codes, kept in Steam's spelling rather than mapped to ISO codes.
STEAM_API_LANGUAGE_CODES = frozenset(
    {
        "arabic",
        "bulgarian",
        "schinese",
        "tchinese",
        "czech",
        "danish",
        "dutch",
        "english",
        "finnish",
        "french",
        "german",
        "greek",
        "hungarian",
        "indonesian",
        "italian",
        "japanese",
        "koreana",
        "malay",
        "norwegian",
        "polish",
        "portuguese",
        "brazilian",
        "romanian",
        "russian",
        "spanish",
        "latam",
        "swedish",
        "thai",
        "turkish",
        "ukrainian",
        "vietnamese",
    }
)


def language_metadata_status(value: Any) -> str:
    if not isinstance(value, str):
        return "missing" if value is None else "non_string"
    if not value.strip():
        return "missing"
    if value == "english":
        return "english"
    if value in STEAM_API_LANGUAGE_CODES:
        return "non_english"
    return "unexpected_code"


def write_language_reports(
    report_dir: Path,
    *,
    run_id: str,
    review_languages: tuple[str, ...],
    game_rows: list[dict[str, Any]],
    announcement_rows: list[dict[str, Any]],
    review_rows: list[dict[str, Any]],
    membership_rows: list[dict[str, Any]],
    window_rows: list[dict[str, Any]],
    collection_phase: str = "current_snapshot",
) -> tuple[dict[str, Any], dict[str, Path]]:
    """Write language counts at game, patch-window, and announcement metadata grains."""
    report_dir.mkdir(parents=True, exist_ok=True)
    games = {int(row["appid"]): row["game_name"] for row in game_rows}
    reviews = {row["review_revision_id"]: row for row in review_rows}
    game_counts: dict[tuple[int, str], int] = Counter()
    language_status_counts: Counter[str] = Counter()
    for review in review_rows:
        status = review.get("language_metadata_status") or language_metadata_status(
            review.get("language")
        )
        language_status_counts[status] += 1
        game_counts[(int(review["appid"]), _language_key(review.get("language"), status))] += 1

    by_game: dict[int, Counter[str]] = defaultdict(Counter)
    for (appid, code), count in game_counts.items():
        by_game[appid][code] += count

    game_language_rows: list[dict[str, Any]] = []
    for appid in sorted(games):
        counts = by_game[appid]
        total = sum(counts.values())
        known_total = sum(
            count
            for code, count in counts.items()
            if _code_status(code) in {"english", "non_english"}
        )
        english = counts.get("english", 0)
        non_english = sum(
            count for code, count in counts.items() if _code_status(code) == "non_english"
        )
        unexpected = sum(
            count
            for code, count in counts.items()
            if _code_status(code) in {"unexpected_code", "non_string"}
        )
        missing = counts.get("<missing>", 0)
        for code, count in sorted(counts.items()):
            status = _code_status(code)
            game_language_rows.append(
                {
                    "run_id": run_id,
                    "collection_phase": collection_phase,
                    "appid": appid,
                    "game_name": games[appid],
                    "language_code": code,
                    "language_status": status,
                    "review_revisions": count,
                    "share_of_game": _fraction(count, total),
                    "game_total_reviews": total,
                    "english_reviews": english,
                    "non_english_reviews": non_english,
                    "unexpected_or_non_string_reviews": unexpected,
                    "missing_language_reviews": missing,
                    "english_share_of_known_languages": _fraction(english, known_total),
                    "non_english_share_of_known_languages": _fraction(non_english, known_total),
                    "requested_language_filters": ",".join(review_languages),
                }
            )

    window_lookup = {(row["patch_id"], row["segment"]): row for row in window_rows}
    counts_by_window: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for membership in membership_rows:
        key = (membership["patch_id"], membership["window_segment"])
        review = reviews.get(membership["review_revision_id"])
        if review is None:
            continue
        status = review.get("language_metadata_status") or language_metadata_status(
            review.get("language")
        )
        counts_by_window[key][_language_key(review.get("language"), status)] += 1

    patch_language_rows: list[dict[str, Any]] = []
    for key, window in sorted(window_lookup.items()):
        counts = counts_by_window.get(key, Counter())
        total = sum(counts.values())
        known_total = sum(
            count
            for code, count in counts.items()
            if _code_status(code) in {"english", "non_english"}
        )
        english = counts.get("english", 0)
        non_english = sum(
            count for code, count in counts.items() if _code_status(code) == "non_english"
        )
        unexpected = sum(
            count for code, count in counts.items() if _code_status(code) == "unexpected_code"
        )
        missing = counts.get("<missing>", 0)
        for code, count in sorted(counts.items()):
            status = _code_status(code)
            patch_language_rows.append(
                {
                    "run_id": run_id,
                    "collection_phase": collection_phase,
                    "appid": window["appid"],
                    "patch_id": window["patch_id"],
                    "announcement_id": window["announcement_id"],
                    "window_segment": window["segment"],
                    "collection_status": window["collection_status"],
                    "language_code": code,
                    "language_status": status,
                    "review_revisions": count,
                    "share_of_window": _fraction(count, total),
                    "window_total_reviews": total,
                    "english_reviews": english,
                    "non_english_reviews": non_english,
                    "unexpected_code_reviews": unexpected,
                    "missing_language_reviews": missing,
                    "english_share_of_known_languages": _fraction(english, known_total),
                    "non_english_share_of_known_languages": _fraction(non_english, known_total),
                    "requested_language_filters": ",".join(review_languages),
                }
            )

    announcement_status_counts: Counter[str] = Counter(
        row.get("announcement_language_metadata_status")
        or language_metadata_status(row.get("announcement_language"))
        for row in announcement_rows
    )
    known_total = language_status_counts["english"] + language_status_counts["non_english"]
    summary = {
        "run_id": run_id,
        "requested_review_languages": list(review_languages),
        "collection_phase": collection_phase,
        "review_revisions": len(review_rows),
        "review_language_status_counts": dict(sorted(language_status_counts.items())),
        "english_reviews": language_status_counts["english"],
        "non_english_reviews": language_status_counts["non_english"],
        "unexpected_code_reviews": language_status_counts["unexpected_code"],
        "missing_language_reviews": language_status_counts["missing"],
        "non_string_language_metadata": language_status_counts["non_string"],
        "english_share_of_known_languages": _fraction(
            language_status_counts["english"], known_total
        ),
        "non_english_share_of_known_languages": _fraction(
            language_status_counts["non_english"], known_total
        ),
        "language_backfill_performed": collection_phase == "post_backfill",
        "announcement_language_status_counts": dict(sorted(announcement_status_counts.items())),
        "review_window_count": len(window_rows),
        "review_windows_complete": sum(
            row["collection_status"] == "complete" for row in window_rows
        ),
        "review_windows_incomplete": sum(
            row["collection_status"] != "complete" for row in window_rows
        ),
        "patch_window_language_rows": len(patch_language_rows),
    }

    game_path = report_dir / "language_by_game.csv"
    patch_path = report_dir / "language_by_patch_window.csv"
    summary_path = report_dir / "language_coverage.json"
    report_path = report_dir / "language_coverage.md"
    game_fields = [
        "run_id",
        "collection_phase",
        "appid",
        "game_name",
        "language_code",
        "language_status",
        "review_revisions",
        "share_of_game",
        "game_total_reviews",
        "english_reviews",
        "non_english_reviews",
        "unexpected_or_non_string_reviews",
        "missing_language_reviews",
        "english_share_of_known_languages",
        "non_english_share_of_known_languages",
        "requested_language_filters",
    ]
    patch_fields = [
        "run_id",
        "collection_phase",
        "appid",
        "patch_id",
        "announcement_id",
        "window_segment",
        "collection_status",
        "language_code",
        "language_status",
        "review_revisions",
        "share_of_window",
        "window_total_reviews",
        "english_reviews",
        "non_english_reviews",
        "unexpected_code_reviews",
        "missing_language_reviews",
        "english_share_of_known_languages",
        "non_english_share_of_known_languages",
        "requested_language_filters",
    ]
    _write_csv(game_path, game_language_rows, game_fields)
    _write_csv(patch_path, patch_language_rows, patch_fields)
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Multilingual review coverage",
        "",
        f"Run: `{run_id}`",
        f"Requested Steam review language filters: `{', '.join(review_languages)}`",
        f"Collection phase: `{collection_phase}`",
        "",
        "Steam documents an empty `languages` list as English-only and `['all']` as every language. The saved Stage 1 requests were checked in their raw observation metadata. Steam's original language codes and review text are retained unchanged; this report does not detect or translate language.",
        "",
        "English and non-English proportions below use records with recognized Steam language codes as the denominator. Missing and unexpected codes are reported separately. Per-window counts represent review-window memberships, so the same review may appear in multiple patch windows.",
        "",
        "## Overall review language status",
        "",
        f"- Unique review revisions: **{len(review_rows):,}**.",
        f"- English: **{language_status_counts['english']:,}** ({_percent(language_status_counts['english'], known_total)} of recognized-code reviews).",
        f"- Non-English recognized codes: **{language_status_counts['non_english']:,}** ({_percent(language_status_counts['non_english'], known_total)} of recognized-code reviews).",
        f"- Missing language: **{language_status_counts['missing']:,}**; non-string metadata: **{language_status_counts['non_string']:,}**; unexpected codes: **{language_status_counts['unexpected_code']:,}**.",
        f"- Selected patch windows complete: **{summary['review_windows_complete']} / {len(window_rows)}**.",
        "",
        "## Game-level distribution",
        "",
        "| App ID | Game | English | Recognized non-English | Missing | Unexpected/non-string | Total | English share of known | Non-English share of known |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for appid in sorted(games):
        counts = by_game[appid]
        total = sum(counts.values())
        recognized = sum(
            count
            for code, count in counts.items()
            if _code_status(code) in {"english", "non_english"}
        )
        english = counts.get("english", 0)
        non_english = sum(
            count for code, count in counts.items() if _code_status(code) == "non_english"
        )
        unknown = counts.get("<missing>", 0)
        unexpected = sum(
            count
            for code, count in counts.items()
            if _code_status(code) in {"non_string", "unexpected_code"}
        )
        lines.append(
            f"| {appid} | {games[appid]} | {english:,} | {non_english:,} | {unknown:,} | {unexpected:,} | {total:,} | {_percent(english, recognized)} | {_percent(non_english, recognized)} |"
        )
    lines.extend(
        [
            "",
            "## Announcement language metadata",
            "",
            f"Announcement language metadata statuses: `{dict(sorted(announcement_status_counts.items()))}`. This is kept separate from review language; absent announcement metadata is not inferred from announcement text or the API request locale.",
            "",
            "## Before/after language backfill",
            "",
            f"This materialization contains **{len(review_rows):,}** unique review revisions in `{collection_phase}`. A separate language backfill contributes **{len(review_rows) if collection_phase == 'post_backfill' else 0:,}** revisions in the post-backfill phase. Existing raw review requests used `languages={list(review_languages)!r}`; the review windows remain partial where the page/request budget was reached, not because the collector requested English only.",
            "",
            "## Detailed outputs",
            "",
            "- `language_by_game.csv`: one row per game and exact Steam language code, with missing and unexpected metadata retained as separate groups.",
            "- `language_by_patch_window.csv`: one row per patch window and exact Steam language code, plus collection status and English/non-English proportions.",
            "- `language_coverage.json`: machine-readable quality summary.",
            "",
            "Language codes follow Steam's API spelling. This report flags codes absent from the documented Steam API language list but never rewrites or maps source codes.",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return summary, {
        "language_by_game": game_path,
        "language_by_patch_window": patch_path,
        "language_coverage": summary_path,
        "language_report": report_path,
    }


def _language_key(value: Any, status: str | None = None) -> str:
    if isinstance(value, str) and value.strip():
        return value
    return "<non_string>" if status == "non_string" else "<missing>"


def _code_status(code: str) -> str:
    if code == "<missing>":
        return "missing"
    if code == "<non_string>":
        return "non_string"
    return language_metadata_status(code)


def _fraction(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def _percent(numerator: int, denominator: int) -> str:
    value = _fraction(numerator, denominator)
    return f"{value:.1%}" if value is not None else "n/a"


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
