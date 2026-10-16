"""Conservative text preparation; source strings remain available verbatim."""

import pandas as pd

from steam_insights.data.text import NORMALIZATION_VERSION, clean_text, word_count
from steam_insights.data.validation import (
    REVIEW_BOOLEANS,
    boolean_values,
    utc_dates,
    validate_announcements,
    validate_reviews,
)


def prepare_reviews(
    frame: pd.DataFrame, minimum_words: int = 10, language: str = "english"
) -> pd.DataFrame:
    validate_reviews(frame, language=language).require_valid()
    result = frame.copy()
    result["appid"] = result["appid"].astype("int64")
    result["review_id"] = result["review_id"].astype("string").str.strip()
    for column in ("created_utc", "updated_utc"):
        result[column] = utc_dates(result[column])
    for column in ("timestamp_created", "timestamp_updated"):
        result[column] = pd.to_numeric(result[column]).astype("int64")
    for column in REVIEW_BOOLEANS:
        if column in result:
            result[column] = boolean_values(result[column])
    for column in ("playtime_at_review_hours", "lifetime_playtime_hours"):
        if column in result:
            result[column] = pd.to_numeric(result[column], errors="coerce").astype("Float64")
    if "word_count" in result:
        # Keep the legacy value as supplied; the independently computed count drives this pipeline.
        result["word_count"] = pd.to_numeric(result["word_count"], errors="coerce").astype("Int64")
    result["review_text_clean"] = result["review_text"].fillna("").map(clean_text).astype("string")
    result["word_count_computed"] = result["review_text"].fillna("").map(word_count).astype("int64")
    result["analysis_text_eligible"] = (
        result["word_count_computed"].ge(minimum_words) & result["language"].eq(language)
    ).astype("boolean")
    result["is_unedited_snapshot"] = (
        result["created_utc"].eq(result["updated_utc"]).astype("boolean")
    )
    result["review_date_utc"] = result["created_utc"].dt.floor("D")
    result["text_normalization_version"] = NORMALIZATION_VERSION
    return result.sort_values(["appid", "created_utc", "review_id"], kind="stable").reset_index(
        drop=True
    )


def prepare_announcements(frame: pd.DataFrame) -> pd.DataFrame:
    validate_announcements(frame).require_valid()
    result = frame.copy()
    result["appid"] = result["appid"].astype("int64")
    result["gid"] = result["gid"].astype("string").str.strip()
    result["date_utc"] = utc_dates(result["date_utc"])
    result["timestamp"] = pd.to_numeric(result["timestamp"]).astype("int64")
    if "patch_candidate" in result:
        result["patch_candidate"] = boolean_values(result["patch_candidate"])
    result["text_clean"] = result["text"].fillna("").map(clean_text).astype("string")
    result["text_normalization_version"] = NORMALIZATION_VERSION
    # CSVs contain flattened text, so do not fabricate original heading paths.
    result["heading_context_available"] = False
    return result.sort_values(["appid", "date_utc", "gid"], kind="stable").reset_index(drop=True)
