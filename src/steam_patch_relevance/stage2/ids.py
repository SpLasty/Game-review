"""Stage 2 identifiers, deliberately namespaced separately from Stage 1."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def rv2_id(kind: str, *parts: Any) -> str:
    payload = json.dumps(parts, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
    return f"rv2_{kind}_{digest}"


def content_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
