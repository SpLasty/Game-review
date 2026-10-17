"""Aggregate readiness reports; no review excerpts are published here."""

from collections import Counter

import pandas as pd

from steam_insights.data.io import write_json


def _table(headers, rows):
    def escape(value):
        return str(value).replace("|", "\\|").replace("\n", " ")

    return "\n".join(
        ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
        + ["| " + " | ".join(escape(v) for v in row) + " |" for row in rows]
    )


def write_readiness_report(directory, manifest, reviews, announcements, games, windows):
    counts = manifest["tables"]
    verified = [w for w in windows if w["verified_patch_post"]]
    adequate = [w for w in verified if w["coverage_screen_met"]]
    gap = manifest["readiness"]
    lines = [
        "# Model-ingestion data readiness report",
        "",
        f"Dataset: `{manifest['dataset_id']}`",
        "",
        "## Processing completed",
        "",
        f"{len(reviews):,} current reviews and {len(announcements):,} current announcement posts were processed. "
        f"{counts['changes']['rows']:,} structural change candidates and {counts['candidates']['rows']:,} review/change candidates were exported. "
        "Candidates and rule hints remain distinct from adjudicated human labels.",
        "",
        _table(
            ["Artifact", "Rows"], [[name, f"{info['rows']:,}"] for name, info in counts.items()]
        ),
        "",
        "## Patch verification and window coverage",
        "",
        _table(
            ["Verification status", "Patch posts"],
            [
                [name, count]
                for name, count in sorted(
                    Counter(w["verification_status"] for w in windows).items()
                )
            ],
        ),
        "",
        f"**{len(verified):,} source-confirmed or reviewed patch posts**; **{len(adequate):,} pass the configured exploratory review-coverage screen**. "
        "The legacy ten manual flags are preserved separately. Source confirmation establishes post type; fix effectiveness and actual deployment remain separate questions.",
        "",
        "The screen uses configured before/after intervals (default 14 days each), at least 30 text-eligible reviews across at least 7 UTC dates per side, "
        "and observed review bounds spanning the entire interval. A 14-day interval beginning midday can intersect 15 UTC calendar dates. "
        "These are operational availability thresholds, not statistical-power or causal criteria.",
        "",
        "## Per-game readiness",
        "",
    ]
    game_rows = []
    for game in games:
        appid = game["appid"]
        rs, ds, ws = (
            [r for r in reviews if r["appid"] == appid],
            [d for d in announcements if d["appid"] == appid],
            [w for w in windows if w["appid"] == appid],
        )
        game_rows.append(
            {
                "appid": appid,
                "game": game["game"],
                "split": game["split"],
                "reviews": len(rs),
                "eligible_reviews": sum(r["text_eligible"] for r in rs),
                "language_warnings": sum(r["language_warning"] for r in rs),
                "posts": len(ds),
                "structured_posts": sum(d["structure_available"] for d in ds),
                "confirmed_patch_posts": sum(w["verified_patch_post"] for w in ws),
                "confirmed_windows_passing_screen": sum(
                    w["verified_patch_post"] and w["coverage_screen_met"] for w in ws
                ),
                "first_review_utc": min((r["created_utc"].isoformat() for r in rs), default=None),
                "last_review_utc": max((r["created_utc"].isoformat() for r in rs), default=None),
            }
        )
    lines.append(
        _table(
            [
                "Game",
                "Split",
                "Reviews",
                "Eligible",
                "Structured posts",
                "Confirmed patches",
                "Confirmed windows passing",
            ],
            [
                [
                    r["game"],
                    r["split"],
                    r["reviews"],
                    r["eligible_reviews"],
                    r["structured_posts"],
                    r["confirmed_patch_posts"],
                    r["confirmed_windows_passing_screen"],
                ]
                for r in game_rows
            ],
        )
    )
    lines += [
        "",
        "## Model ingestion readiness",
        "",
        f"- Inference inputs available: **{gap['inference_inputs_ready']}**.",
        f"- Adjudicated labeled pairs: **{gap['labeled_pairs']:,}**; supervised training ready: **{gap['supervised_training_ready']}**. "
        "This flag indicates that some training rows exist, not that label volume, class coverage, or evaluation quality is sufficient.",
        f"- Cross-split duplicate families: **{gap['cross_split_duplicate_families']:,}**; affected pairs are excluded from supervised export.",
        f"- Source metadata/independent language-detector disagreements: **{gap['language_warnings']:,}**; retained as inspection flags.",
        "",
        "## More data and decisions required",
        "",
        f"- **{gap['flattened_or_plain_posts']:,} posts** still have no original heading/list markup available. "
        "Their extracted fragments retain a degraded-source warning.",
        f"- **{gap['unknown_release_times']:,} patch posts** have no supported effective release timestamp. "
        "Publication time is an explicitly marked proxy.",
        "- Backfill historical review windows where before/after counts or date coverage are insufficient. "
        "The window CSV records deficits. Exhausting a dated API query is tracked separately from passing the sample-density screen.",
        "- Complete human annotations for relevance, change-specific sentiment, and fix-status evidence. "
        "A recommendation vote does not supply these labels. Inspect representative parser/verification outputs before using weak hints.",
        "- Historical review and announcement revisions absent from the archive cannot be reconstructed by fetching their current state. "
        "Edited reviews and newly recovered posts are current observations, with their observation times preserved.",
        "- Overlapping patch posts, beta/platform scope, and external full changelog links need source inspection. "
        "Unknown review branch/platform never silently becomes a scope match.",
        "",
        "## Reproducibility and outputs",
        "",
        "`manifest.json` records input/config/code fingerprints, Arrow contracts, row counts, table hashes, and readiness. "
        "`validation.json` contains the publication gates. `catalog.duckdb` is rebuildable from the authoritative Parquet tables. "
        "Split allocation is frozen by game ID and seed; held-out labels do not guide parser rules or candidate thresholds.",
        "",
        "See `patch_window_quality.csv` for individual post periods and `game_quality_summary.csv` for all games. "
        "The report describes the observed convenience sample. It does not establish patch causality.",
        "",
    ]
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "report.md").write_text("\n".join(lines), encoding="utf-8")
    pd.DataFrame(game_rows).to_csv(directory / "game_quality_summary.csv", index=False)
    pd.DataFrame(windows).to_csv(directory / "patch_window_quality.csv", index=False)
    write_json(directory / "readiness.json", {"dataset_id": manifest["dataset_id"], **gap})
