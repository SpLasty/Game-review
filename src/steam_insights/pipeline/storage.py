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
    payload = json.dumps(parts, ensure_ascii=False, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


SCHEMAS = {
    "source_records": {
        "source_record_id": TEXT, "dataset": TEXT, "source_path": TEXT,
        "source_sha256": TEXT, "source_row": INT, "source_kind": TEXT,
        "source_url": TEXT, "observed_at": TIME, "entity_id": TEXT, "revision_id": TEXT,
    },
    "quarantine": {
        "source_record_id": TEXT, "dataset": TEXT, "entity_id": TEXT,
        "reason": TEXT, "source_path": TEXT, "source_row": INT,
    },
    "review_revisions": {
        "review_revision_id": TEXT, "review_id": TEXT, "appid": INT, "game": TEXT,
        "review_text_original": TEXT, "review_text": TEXT, "language": TEXT,
        "created_utc": TIME, "updated_utc": TIME, "observed_at": TIME,
        "recommended": BOOL, "source_record_id": TEXT, "source_url": TEXT,
        "author_hash": TEXT, "author_hash_namespace": TEXT,
        "playtime_at_review_hours": FLOAT, "lifetime_playtime_hours": FLOAT,
        "word_count": INT, "text_eligible": BOOL, "text_eligibility_reason": TEXT,
        "edited": BOOL, "detected_language": TEXT, "language_probability": FLOAT,
        "language_warning": BOOL, "exact_duplicate_group": TEXT,
        "near_duplicate_group": TEXT, "split": TEXT, "cross_split_duplicate": BOOL,
    },
    "review_passages": {
        "passage_id": TEXT, "review_revision_id": TEXT, "review_id": TEXT,
        "appid": INT, "ordinal": INT, "char_start": INT, "char_end": INT,
        "text": TEXT, "split": TEXT,
    },
    "duplicate_pairs": {
        "left_revision_id": TEXT, "right_revision_id": TEXT,
        "similarity": FLOAT, "method": TEXT,
    },
}
SCHEMAS["reviews"] = SCHEMAS["review_revisions"]


def write_table(directory: Path, name: str, records: list[dict], storage: dict) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    schema = pa.schema([pa.field(key, kind) for key, kind in SCHEMAS[name].items()])
    table = pa.Table.from_pylist(records, schema=schema)
    path = directory / f"{name}.parquet"
    pq.write_table(
        table, path, compression=storage["compression"],
        compression_level=storage["compression_level"], row_group_size=storage["row_group_size"],
        write_statistics=True, version="2.6",
    )
    return {"rows": len(records), "bytes": path.stat().st_size, "schema": str(schema)}


def read_table(directory: Path, name: str) -> list[dict]:
    return pq.read_table(directory / f"{name}.parquet").to_pylist()


def create_catalog(directory: Path) -> None:
    """A rebuildable DuckDB catalog referencing the authoritative Parquet tables."""
    import duckdb
    with duckdb.connect(str(directory / "catalog.duckdb")) as connection:
        for path in sorted(directory.glob("*.parquet")):
            escaped = str(path.resolve()).replace("'", "''")
            connection.execute(f'CREATE OR REPLACE VIEW "{path.stem}" AS SELECT * FROM read_parquet(\'{escaped}\')')
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
