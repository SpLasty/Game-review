"""Explicit Arrow contracts and deterministic dataset IO."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

TEXT = pa.string()
INT = pa.int64()
BOOL = pa.bool_()
FLOAT = pa.float64()
TIME = pa.timestamp("us", tz="UTC")
TEXTS = pa.list_(TEXT)


def stable_id(*parts: object) -> str:
    payload = json.dumps(
        parts, ensure_ascii=False, separators=(",", ":"), default=str, sort_keys=True
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


SCHEMAS = {
    "source_records": {
        "source_record_id": TEXT,
        "dataset": TEXT,
        "source_path": TEXT,
        "source_sha256": TEXT,
        "source_row": INT,
        "source_kind": TEXT,
        "source_url": TEXT,
        "observed_at": TIME,
        "entity_id": TEXT,
        "revision_id": TEXT,
    },
    "quarantine": {
        "source_record_id": TEXT,
        "dataset": TEXT,
        "entity_id": TEXT,
        "reason": TEXT,
        "source_path": TEXT,
        "source_row": INT,
    },
    "review_revisions": {
        "review_revision_id": TEXT,
        "review_id": TEXT,
        "appid": INT,
        "game": TEXT,
        "review_text_original": TEXT,
        "review_text": TEXT,
        "language": TEXT,
        "created_utc": TIME,
        "updated_utc": TIME,
        "observed_at": TIME,
        "recommended": BOOL,
        "source_record_id": TEXT,
        "source_url": TEXT,
        "author_hash": TEXT,
        "author_hash_namespace": TEXT,
        "playtime_at_review_hours": FLOAT,
        "lifetime_playtime_hours": FLOAT,
        "steam_purchase": BOOL,
        "received_for_free": BOOL,
        "refunded": BOOL,
        "primarily_steam_deck": BOOL,
        "written_during_early_access": BOOL,
        "supplied_word_count": INT,
        "word_count_mismatch": BOOL,
        "word_count": INT,
        "text_eligible": BOOL,
        "text_eligibility_reason": TEXT,
        "edited": BOOL,
        "detected_language": TEXT,
        "language_probability": FLOAT,
        "language_warning": BOOL,
        "exact_duplicate_group": TEXT,
        "near_duplicate_group": TEXT,
        "split": TEXT,
        "cross_split_duplicate": BOOL,
    },
    "review_passages": {
        "passage_id": TEXT,
        "review_revision_id": TEXT,
        "review_id": TEXT,
        "appid": INT,
        "ordinal": INT,
        "char_start": INT,
        "char_end": INT,
        "text": TEXT,
        "split": TEXT,
    },
    "duplicate_pairs": {
        "left_revision_id": TEXT,
        "right_revision_id": TEXT,
        "similarity": FLOAT,
        "method": TEXT,
    },
}
SCHEMAS["reviews"] = SCHEMAS["review_revisions"]
SCHEMAS.update(
    {
        "announcement_revisions": {
            "announcement_revision_id": TEXT,
            "post_id": TEXT,
            "appid": INT,
            "game": TEXT,
            "title": TEXT,
            "source_text_original": TEXT,
            "canonical_text": TEXT,
            "document_format": TEXT,
            "structure_available": BOOL,
            "publication_utc": TIME,
            "observed_at": TIME,
            "source_record_id": TEXT,
            "source_url": TEXT,
            "feed": TEXT,
            "legacy_manual_flag": BOOL,
            "post_type": TEXT,
            "verification_status": TEXT,
            "release_status_hint": TEXT,
            "release_utc": TIME,
            "release_time_basis": TEXT,
            "version_hint": TEXT,
            "branch": TEXT,
            "platforms": TEXTS,
            "split": TEXT,
        },
        "announcement_blocks": {
            "block_id": TEXT,
            "announcement_revision_id": TEXT,
            "post_id": TEXT,
            "appid": INT,
            "ordinal": INT,
            "block_type": TEXT,
            "heading_path": TEXTS,
            "list_depth": INT,
            "heading_origin": TEXT,
            "text": TEXT,
            "char_start": INT,
            "char_end": INT,
        },
        "announcement_links": {
            "link_id": TEXT,
            "announcement_revision_id": TEXT,
            "post_id": TEXT,
            "appid": INT,
            "label": TEXT,
            "original_url": TEXT,
            "target_url": TEXT,
            "target_host": TEXT,
            "reference_kind": TEXT,
        },
        "changes": {
            "change_id": TEXT,
            "announcement_revision_id": TEXT,
            "block_id": TEXT,
            "post_id": TEXT,
            "appid": INT,
            "game": TEXT,
            "title": TEXT,
            "heading_path": TEXTS,
            "text": TEXT,
            "char_start": INT,
            "char_end": INT,
            "context_text": TEXT,
            "status_hint": TEXT,
            "topic_hints": TEXTS,
            "entity_hint": TEXT,
            "version_hint": TEXT,
            "branch": TEXT,
            "platforms": TEXTS,
            "old_value": TEXT,
            "new_value": TEXT,
            "needs_review": BOOL,
            "extraction_method": TEXT,
            "source_url": TEXT,
            "split": TEXT,
        },
        "patches": {
            "patch_id": TEXT,
            "announcement_revision_id": TEXT,
            "post_id": TEXT,
            "appid": INT,
            "game": TEXT,
            "title": TEXT,
            "publication_utc": TIME,
            "release_utc": TIME,
            "anchor_utc": TIME,
            "anchor_basis": TEXT,
            "verification_status": TEXT,
            "source_confirmed": BOOL,
            "human_verified": BOOL,
            "legacy_manual_flag": BOOL,
            "verified_for_analysis": BOOL,
            "version_hint": TEXT,
            "branch": TEXT,
            "platforms": TEXTS,
            "source_url": TEXT,
            "overlapping_patch_posts": INT,
            "split": TEXT,
        },
        "verification_evidence": {
            "evidence_id": TEXT,
            "announcement_revision_id": TEXT,
            "source_record_id": TEXT,
            "field": TEXT,
            "method": TEXT,
            "value": TEXT,
            "evidence_text": TEXT,
            "char_start": INT,
            "char_end": INT,
            "source_url": TEXT,
            "checked_by": TEXT,
            "checked_at": TIME,
        },
    }
)
SCHEMAS["announcements"] = SCHEMAS["announcement_revisions"]
SCHEMAS.update(
    {
        "games": {"appid": INT, "game": TEXT, "split": TEXT},
        "patch_windows": {
            "patch_id": TEXT,
            "appid": INT,
            "game": TEXT,
            "title": TEXT,
            "anchor_utc": TIME,
            "anchor_basis": TEXT,
            "window_start_utc": TIME,
            "window_end_utc": TIME,
            "pre_reviews": INT,
            "post_reviews": INT,
            "pre_eligible_reviews": INT,
            "post_eligible_reviews": INT,
            "pre_active_dates": INT,
            "post_active_dates": INT,
            "pre_edited_reviews": INT,
            "post_edited_reviews": INT,
            "pre_negative_recommendation_share": FLOAT,
            "post_negative_recommendation_share": FLOAT,
            "observed_bounds_cover_window": BOOL,
            "coverage_screen_met": BOOL,
            "stronger_coverage_screen_met": BOOL,
            "verified_patch_post": BOOL,
            "verification_status": TEXT,
            "overlapping_patch_posts": INT,
            "pre_reviews_needed_for_screen": INT,
            "post_reviews_needed_for_screen": INT,
            "review_collection_complete": BOOL,
            "assessment": TEXT,
            "split": TEXT,
        },
        "candidates": {
            "candidate_id": TEXT,
            "review_revision_id": TEXT,
            "review_id": TEXT,
            "change_id": TEXT,
            "announcement_revision_id": TEXT,
            "patch_id": TEXT,
            "appid": INT,
            "task": TEXT,
            "lag_days": FLOAT,
            "shared_terms": TEXTS,
            "lexical_score": FLOAT,
            "scope_compatibility": TEXT,
            "split": TEXT,
            "cross_split_duplicate": BOOL,
        },
        "annotations": {
            "annotation_id": TEXT,
            "candidate_id": TEXT,
            "annotator_id": TEXT,
            "label_source": TEXT,
            "adjudicated": BOOL,
            "created_at": TIME,
            "relevance": TEXT,
            "sentiment": TEXT,
            "fix_status": TEXT,
            "review_evidence_start": INT,
            "review_evidence_end": INT,
            "review_evidence_text": TEXT,
            "change_evidence_start": INT,
            "change_evidence_end": INT,
            "change_evidence_text": TEXT,
            "supersedes": TEXTS,
        },
        "model_review_inputs": {
            "passage_id": TEXT,
            "review_revision_id": TEXT,
            "appid": INT,
            "text": TEXT,
            "review_context": TEXT,
            "char_start": INT,
            "char_end": INT,
            "split": TEXT,
            "cross_split_duplicate": BOOL,
            "language_warning": BOOL,
        },
        "model_change_inputs": {
            "change_id": TEXT,
            "announcement_revision_id": TEXT,
            "appid": INT,
            "text": TEXT,
            "context_text": TEXT,
            "title": TEXT,
            "heading_path": TEXTS,
            "char_start": INT,
            "char_end": INT,
            "split": TEXT,
            "needs_review": BOOL,
        },
        "model_pair_inputs": {
            "candidate_id": TEXT,
            "review_revision_id": TEXT,
            "change_id": TEXT,
            "appid": INT,
            "task": TEXT,
            "review_text": TEXT,
            "review_passage_text": TEXT,
            "change_text": TEXT,
            "change_context": TEXT,
            "title": TEXT,
            "heading_path": TEXTS,
            "review_char_start": INT,
            "review_char_end": INT,
            "change_char_start": INT,
            "change_char_end": INT,
            "split": TEXT,
            "cross_split_duplicate": BOOL,
            "language_warning": BOOL,
        },
    }
)
SCHEMAS["labeled_pairs"] = {
    **SCHEMAS["model_pair_inputs"],
    "annotation_id": TEXT,
    "relevance": TEXT,
    "sentiment": TEXT,
    "fix_status": TEXT,
}


def write_table(directory: Path, name: str, records: list[dict], storage: dict) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    schema = pa.schema([pa.field(key, kind) for key, kind in SCHEMAS[name].items()])
    table = pa.Table.from_pylist(records, schema=schema)
    path = directory / f"{name}.parquet"
    pq.write_table(
        table,
        path,
        compression=storage["compression"],
        compression_level=storage["compression_level"],
        row_group_size=storage["row_group_size"],
        write_statistics=True,
        version="2.6",
    )
    return {"rows": len(records), "bytes": path.stat().st_size, "schema": str(schema)}


def read_table(directory: Path, name: str) -> list[dict]:
    return pq.read_table(directory / f"{name}.parquet").to_pylist()


def create_catalog(directory: Path) -> None:
    """A rebuildable DuckDB catalog referencing the authoritative Parquet tables."""
    import duckdb

    with duckdb.connect(str(directory / "catalog.duckdb")) as connection:
        connection.execute("SET TimeZone = 'UTC'")
        for path in sorted(directory.glob("*.parquet")):
            escaped = str(path.resolve()).replace("'", "''")
            connection.execute(
                f"CREATE OR REPLACE VIEW \"{path.stem}\" AS SELECT * FROM read_parquet('{escaped}')"
            )
        if (directory / "reviews.parquet").exists():
            connection.execute("""CREATE OR REPLACE VIEW review_daily AS
                SELECT appid, game, date_trunc('day', created_utc) AS review_date,
                    count(*) AS reviews, count(*) FILTER (WHERE text_eligible) AS eligible_reviews,
                    avg(CASE WHEN recommended THEN 0.0 ELSE 1.0 END) AS negative_recommendation_share
                FROM reviews GROUP BY ALL""")


def parse_time(value: object):
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        result = value
    elif isinstance(value, (int, float)):
        result = datetime.fromtimestamp(value, timezone.utc)
    else:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Timestamp has no timezone")
    return result.astimezone(timezone.utc)


def optional_float(value: object):
    if value is None or value == "":
        return None
    result = float(value)
    if not __import__("math").isfinite(result) or result < 0:
        raise ValueError("Expected finite nonnegative number")
    return result


def explicit_bool(value: object):
    if value is None or value == "":
        return None
    if value is True or value == "True" or value == "true":
        return True
    if value is False or value == "False" or value == "false":
        return False
    raise ValueError("Expected explicit boolean")
