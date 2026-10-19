"""Content-addressed raw storage, resumable checkpoints, and Parquet writers."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

import pyarrow as pa
import pyarrow.parquet as pq

from steam_patch_relevance.identity import canonical_json, sha256_bytes, stable_id
from steam_patch_relevance.models import APIResponse


class LocalStore:
    def __init__(self, root: Path, run_id: str) -> None:
        self.root = root
        self.raw_root = root / "raw"
        self.blob_root = self.raw_root / "blobs"
        self.checkpoint_root = root / "checkpoints"
        self.run_root = root / "runs" / run_id
        self.normalized_root = root / "normalized" / run_id
        for path in (self.blob_root, self.checkpoint_root, self.run_root, self.normalized_root):
            path.mkdir(parents=True, exist_ok=True)
        self.observation_path = self.run_root / "source_observations.jsonl"
        self._observation_ids: set[str] = set()
        if self.observation_path.exists():
            for line in self.observation_path.read_text(encoding="utf-8").splitlines():
                if line:
                    self._observation_ids.add(json.loads(line)["observation_id"])

    def save_response(self, response: APIResponse, *, page_number: int) -> dict[str, Any]:
        payload_hash = sha256_bytes(response.payload_bytes)
        blob_path = self.blob_root / payload_hash[:2] / f"{payload_hash}.json"
        blob_path.parent.mkdir(parents=True, exist_ok=True)
        if blob_path.exists():
            if sha256_bytes(blob_path.read_bytes()) != payload_hash:
                raise IOError(f"Raw blob hash mismatch at {blob_path}")
        else:
            blob_path.write_bytes(response.payload_bytes)
        observation_id = stable_id(
            "observation",
            response.source_kind,
            response.appid,
            response.endpoint,
            response.request_params,
            payload_hash,
            response.retrieved_at_utc.isoformat(),
        )
        row = {
            "observation_id": observation_id,
            "source_identity": _source_identity(response),
            "appid": response.appid,
            "source_kind": response.source_kind,
            "endpoint": response.endpoint,
            "source_url": response.source_url,
            "retrieved_at_utc": response.retrieved_at_utc.isoformat(),
            "request_params_json": canonical_json(response.request_params),
            "page_number": page_number,
            "http_status": response.status_code,
            "payload_sha256": payload_hash,
            "payload_path": str(blob_path),
        }
        if observation_id not in self._observation_ids:
            with self.observation_path.open("a", encoding="utf-8") as stream:
                stream.write(canonical_json(row) + "\n")
            self._observation_ids.add(observation_id)
        return row

    def save_checkpoint(self, key: str, value: dict[str, Any]) -> None:
        _atomic_json(self.checkpoint_root / f"{key}.json", value)

    def load_checkpoint(self, key: str) -> dict[str, Any] | None:
        path = self.checkpoint_root / f"{key}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def payload_for(self, page_ref: dict[str, Any]) -> dict[str, Any]:
        path = (
            self.blob_root / page_ref["payload_sha256"][:2] / f"{page_ref['payload_sha256']}.json"
        )
        raw = path.read_bytes()
        if sha256_bytes(raw) != page_ref["payload_sha256"]:
            raise IOError(f"Raw payload failed hash verification: {path}")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError(f"Raw source payload is not a JSON object: {path}")
        return payload

    def write_table(self, name: str, rows: list[dict[str, Any]], schema: pa.Schema) -> Path:
        path = self.normalized_root / f"{name}.parquet"
        table = pa.Table.from_pylist(rows, schema=schema)
        pq.write_table(table, path, compression="zstd", version="2.6")
        return path


def _source_identity(response: APIResponse) -> str:
    if response.source_kind == "news":
        wrapper = response.payload.get("appnews", {})
        items = wrapper.get("newsitems", []) if isinstance(wrapper, dict) else []
        identities = [str(item.get("gid")) for item in items if isinstance(item, dict)]
        return stable_id("news_page", response.appid, *identities)
    if response.source_kind == "reviews":
        wrapper = response.payload.get("response", {})
        entries = wrapper.get("reviews", []) if isinstance(wrapper, dict) else []
        identities = [
            (str(item.get("recommendationid")), item.get("timestamp_updated"))
            for item in entries
            if isinstance(item, dict)
        ]
        return stable_id("review_page", response.appid, *identities)
    return stable_id("catalog_page", response.request_params)


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_json(path: Path, value: dict[str, Any]) -> None:
    _atomic_json(path, value)


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
