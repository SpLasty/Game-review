"""Stable, typed IDs and content hashes for the v1 ingestion boundary."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def stable_id(prefix: str, *parts: Any) -> str:
    encoded = canonical_json(parts).encode("utf-8")
    return f"rv1_{prefix}_{hashlib.sha256(encoded).hexdigest()[:24]}"


def config_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
