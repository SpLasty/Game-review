"""Read immutable source exports without interpreting IDs as floating point."""

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from steam_insights.config import DataConfig


def read_csv(path: Path) -> pd.DataFrame:
    # Do not let pandas turn literal review text such as "NA" into a missing value.
    return pd.read_csv(path, encoding="utf-8-sig", dtype="string", keep_default_na=False)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def inventory(config: DataConfig) -> dict:
    sources = {}
    for kind in ("reviews", "balanced", "announcements"):
        path = config.source(kind)
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            columns = next(reader)
            rows = sum(1 for _ in reader)
        sources[kind] = {
            "path": path.relative_to(config.root).as_posix(),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "rows": rows,
            "columns": columns,
        }
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
    }
