"""Validate and publish a small offline snapshot into an output-only directory."""

import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from steam_insights import __version__
from steam_insights.config import DataConfig
from steam_insights.data.io import inventory, read_csv, write_json
from steam_insights.data.preprocessing import (
    NORMALIZATION_VERSION,
    prepare_announcements,
    prepare_reviews,
)
from steam_insights.data.validation import validate_announcements, validate_reviews


def preprocess(config: DataConfig) -> dict:
    reviews = read_csv(config.source("reviews"))
    announcements = read_csv(config.source("announcements"))
    reports = [
        validate_reviews(reviews, language=config.language),
        validate_announcements(announcements),
    ]
    write_json(
        config.reports_dir / "preprocessing_validation.json",
        {"datasets": [report.to_dict() for report in reports]},
    )
    for report in reports:
        report.require_valid()
    prepared = prepare_reviews(reviews, config.minimum_words, config.language)
    notes = prepare_announcements(announcements)
    text_view = prepared.loc[prepared["analysis_text_eligible"]].reset_index(drop=True)
    manifest = inventory(config)
    manifest.update(
        {
            "package_version": __version__,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "normalization_version": NORMALIZATION_VERSION,
            "policy": {
                "minimum_words": config.minimum_words,
                "language": config.language,
                "invalid_rows": "fail",
                "short_reviews": "retain",
                "source_text": "preserved",
            },
            "outputs": {
                "reviews.parquet": len(prepared),
                "reviews_text.parquet": len(text_view),
                "announcements.parquet": len(notes),
            },
            "limitations": [
                "Latest exported state is not a historical edit log.",
                "Keyword and patch flags are unverified heuristics, not supervised labels.",
                "Original announcement headings are unavailable in the CSV export.",
                "The long-text view is not a representative recommendation population.",
            ],
        }
    )
    config.interim_dir.mkdir(parents=True, exist_ok=True)
    # Finish every artifact in staging before replacing any destination. The manifest is last.
    # This is an offline single-writer workflow, not a transactional online publication service.
    staging = Path(tempfile.mkdtemp(prefix=".prepare-", dir=config.interim_dir.parent))
    try:
        for name, frame in (
            ("reviews.parquet", prepared),
            ("reviews_text.parquet", text_view),
            ("announcements.parquet", notes),
        ):
            frame.to_parquet(staging / name, engine="pyarrow", index=False)
        write_json(staging / "manifest.json", manifest)
        for name in (*manifest["outputs"], "manifest.json"):
            os.replace(staging / name, config.interim_dir / name)
    finally:
        shutil.rmtree(staging)
    return manifest
