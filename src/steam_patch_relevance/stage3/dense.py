"""Optional multilingual dense retrieval and content/model-versioned embedding cache."""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq


class DenseDependencyError(RuntimeError):
    """Raised when the optional Sentence Transformers dependency is unavailable."""


_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def _snapshot_revision(config_path: str | Path | None) -> str | None:
    """Return the immutable Hugging Face snapshot ID for a cached model config."""
    if not isinstance(config_path, (str, Path)):
        return None
    snapshot = Path(config_path).parent
    revision = snapshot.name
    if snapshot.parent.name == "snapshots" and _COMMIT_RE.fullmatch(revision):
        return revision
    return None


class SentenceTransformerEncoder:
    def __init__(self, model_name: str, revision: str = "main") -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise DenseDependencyError(
                "Dense retrieval requires the optional extra: `uv sync --extra retrieval`"
            ) from exc
        self.model_name = model_name
        self.revision = revision
        self.model = SentenceTransformer(model_name, revision=revision)
        resolved_revision = revision if _COMMIT_RE.fullmatch(revision) else None
        if resolved_revision is None:
            try:
                from huggingface_hub import try_to_load_from_cache

                config_path = try_to_load_from_cache(model_name, "config.json", revision=revision)
                resolved_revision = _snapshot_revision(config_path)
            except (ImportError, OSError, ValueError):
                resolved_revision = None
        if resolved_revision is None:
            for module in self.model._modules.values():
                config = getattr(getattr(module, "auto_model", None), "config", None)
                commit_hash = getattr(config, "_commit_hash", None)
                if isinstance(commit_hash, str) and _COMMIT_RE.fullmatch(commit_hash):
                    resolved_revision = commit_hash
                    break
        if resolved_revision is None:
            raise DenseDependencyError(
                "Could not resolve the dense model to an immutable 40-character revision. "
                "Pass a commit SHA with --dense-revision so cached embeddings are reproducible."
            )
        self.resolved_revision = resolved_revision
        self.model_version = f"{model_name}@{self.resolved_revision}"

    @staticmethod
    def _prefix(text: str, role: str) -> str:
        prefix = "query: " if role == "query" else "passage: "
        return prefix + text.strip()

    def encode(self, texts: list[str], *, role: str, batch_size: int) -> np.ndarray:
        prepared = [self._prefix(text, role) for text in texts]
        if not prepared:
            return np.empty((0, self.model.get_sentence_embedding_dimension()), dtype=np.float32)
        vectors = self.model.encode(
            prepared,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return np.asarray(vectors, dtype=np.float32)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


class EmbeddingCache:
    """Single Parquet cache keyed by the model revision and prefixed content hash."""

    def __init__(self, root: Path, encoder: SentenceTransformerEncoder) -> None:
        self.encoder = encoder
        self.path = root / _slug(encoder.model_version) / "embeddings.parquet"

    def encode_documents(
        self,
        documents: dict[str, str],
        *,
        role: str,
        batch_size: int = 64,
    ) -> dict[str, np.ndarray]:
        cache_rows: dict[str, tuple[str, list[float]]] = {}
        if self.path.exists():
            table = pq.read_table(self.path, columns=["cache_key", "content_sha256", "vector"])
            cache_rows = {
                row["cache_key"]: (row["content_sha256"], row["vector"])
                for row in table.to_pylist()
            }
        cache_keys: dict[str, str] = {}
        missing: dict[str, str] = {}
        for document_id, text in documents.items():
            prefixed = self.encoder._prefix(text, role)
            key_material = f"{self.encoder.model_version}\0{prefixed}"
            key = _hash(key_material)
            cache_keys[document_id] = key
            if key not in cache_rows:
                missing.setdefault(key, text)
        if missing:
            keys = list(missing)
            vectors = self.encoder.encode(
                [missing[key] for key in keys], role=role, batch_size=batch_size
            )
            for key, text, vector in zip(keys, (missing[k] for k in keys), vectors, strict=True):
                prefixed = self.encoder._prefix(text, role)
                cache_rows[key] = (_hash(prefixed), vector.astype(np.float32).tolist())
            self.path.parent.mkdir(parents=True, exist_ok=True)
            ordered = sorted(cache_rows)
            table = pa.table(
                {
                    "cache_key": pa.array(ordered, type=pa.string()),
                    "content_sha256": pa.array(
                        [cache_rows[key][0] for key in ordered], type=pa.string()
                    ),
                    "model_version": pa.array(
                        [self.encoder.model_version] * len(ordered), type=pa.string()
                    ),
                    "vector": pa.array(
                        [cache_rows[key][1] for key in ordered], type=pa.list_(pa.float32())
                    ),
                }
            )
            temporary = self.path.with_suffix(".parquet.tmp")
            pq.write_table(table, temporary, compression="zstd")
            os.replace(temporary, self.path)
        return {
            document_id: np.asarray(cache_rows[key][1], dtype=np.float32)
            for document_id, key in cache_keys.items()
        }


def top_cosine_hits(
    query: np.ndarray,
    document_vectors: np.ndarray,
    document_ids: list[str],
    *,
    limit: int,
) -> list[tuple[str, float]]:
    if limit < 1:
        raise ValueError("dense limit must be positive")
    if len(document_ids) != len(document_vectors):
        raise ValueError("document IDs and dense vectors must have equal length")
    if not len(document_ids):
        return []
    scores = document_vectors @ query
    indexes = np.argpartition(-scores, min(limit, len(scores)) - 1)[:limit]
    ordered = sorted(indexes.tolist(), key=lambda i: (-float(scores[i]), document_ids[i]))
    return [(document_ids[index], float(scores[index])) for index in ordered]
