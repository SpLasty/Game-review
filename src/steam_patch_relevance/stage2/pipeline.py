"""Stage 2 datasets built from the approved Stage 1 normalized snapshot only."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Iterator

import pyarrow as pa
import pyarrow.parquet as pq

from steam_patch_relevance.stage2 import STAGE2_SCHEMA_VERSION
from steam_patch_relevance.stage2.extraction import (
    CHANGE_EXTRACTOR_VERSION,
    CLAIM_EXTRACTOR_VERSION,
    CLASSIFIER_VERSION,
    build_terminology,
    classify_announcement,
    extract_patch_changes,
    extract_review_claims,
)
from steam_patch_relevance.stage2.ids import content_hash, rv2_id

DEFAULT_NORMALIZED_ROOT = Path("data/relevance_v1/normalized")
DEFAULT_OUTPUT_ROOT = Path("data/relevance_v1/processed/stage2")
DEFAULT_REPORT_ROOT = Path("reports/relevance_v1/stage2")
SAMPLE_SEED = "stage2-audit-sample-2026-10"

TIMESTAMP = pa.timestamp("us", tz="UTC")
STRING_LIST = pa.list_(pa.string())

SCHEMAS: dict[str, pa.Schema] = {
    "announcement_classifications": pa.schema(
        [
            ("announcement_revision_id", pa.string()),
            ("announcement_id", pa.string()),
            ("appid", pa.int64()),
            ("game_name", pa.string()),
            ("title", pa.string()),
            ("body_original", pa.large_string()),
            ("published_unix", pa.int64()),
            ("published_at_utc", TIMESTAMP),
            ("source_url", pa.string()),
            ("source_observation_id", pa.string()),
            ("payload_sha256", pa.string()),
            ("linked_urls_json", pa.large_string()),
            ("linked_urls_extraction_method", pa.string()),
            ("officialness", pa.string()),
            ("feedname", pa.string()),
            ("feedlabel", pa.string()),
            ("author", pa.string()),
            ("is_external_url", pa.bool_()),
            ("post_type", pa.string()),
            ("significance", pa.string()),
            ("announcement_language", pa.string()),
            ("body_length", pa.int64()),
            ("body_present", pa.bool_()),
            ("body_truncated_suspected", pa.bool_()),
            ("categories", STRING_LIST),
            ("category_evidence_json", pa.large_string()),
            ("classification_confidence", pa.float64()),
            ("classifier_version", pa.string()),
            ("patch_eligible", pa.bool_()),
            ("patch_id", pa.string()),
            ("full_patch_notes_status", pa.string()),
        ]
    ),
    "patch_changes": pa.schema(
        [
            ("change_id", pa.string()),
            ("patch_id", pa.string()),
            ("announcement_id", pa.string()),
            ("announcement_revision_id", pa.string()),
            ("game_id", pa.int64()),
            ("game_name", pa.string()),
            ("title", pa.string()),
            ("published_at_utc", TIMESTAMP),
            ("source_url", pa.string()),
            ("payload_sha256", pa.string()),
            ("source_span_start", pa.int64()),
            ("source_span_end", pa.int64()),
            ("source_span_raw", pa.large_string()),
            ("change_text", pa.large_string()),
            ("heading_path", STRING_LIST),
            ("entity", pa.string()),
            ("entity_candidates", STRING_LIST),
            ("aspect", pa.string()),
            ("action", pa.string()),
            ("direction", pa.string()),
            ("previous_value", pa.string()),
            ("new_value", pa.string()),
            ("numeric_delta", pa.float64()),
            ("numeric_unit", pa.string()),
            ("developer_status", pa.string()),
            ("bug_symptom", pa.string()),
            ("bug_trigger", pa.string()),
            ("extraction_confidence", pa.float64()),
            ("extraction_method", pa.string()),
            ("extraction_version", pa.string()),
            ("source_span_verified", pa.bool_()),
            ("quality_flags", STRING_LIST),
        ]
    ),
    "review_claims": pa.schema(
        [
            ("claim_id", pa.string()),
            ("review_revision_id", pa.string()),
            ("logical_revision_key", pa.string()),
            ("review_id", pa.string()),
            ("source_payload_sha256", pa.string()),
            ("game_id", pa.int64()),
            ("game_name", pa.string()),
            ("review_created_at_utc", TIMESTAMP),
            ("review_updated_at_utc", TIMESTAMP),
            ("review_language", pa.string()),
            ("language_metadata_status", pa.string()),
            ("detected_language", pa.string()),
            ("detected_language_confidence", pa.float64()),
            ("claim_span_start", pa.int64()),
            ("claim_span_end", pa.int64()),
            ("claim_text_original", pa.large_string()),
            ("referenced_entity", pa.string()),
            ("aspect", pa.string()),
            ("opinion_or_issue", pa.large_string()),
            ("opinion_terms", STRING_LIST),
            ("polarity", pa.string()),
            ("temporal_cues", STRING_LIST),
            ("negated", pa.bool_()),
            ("uncertain", pa.bool_()),
            ("extraction_confidence", pa.float64()),
            ("extraction_method", pa.string()),
            ("extraction_version", pa.string()),
            ("patch_specificity", pa.string()),
        ]
    ),
    "game_terminology": pa.schema(
        [
            ("term_id", pa.string()),
            ("game_id", pa.int64()),
            ("game_name", pa.string()),
            ("term", pa.string()),
            ("normalized_term", pa.string()),
            ("aliases", STRING_LIST),
            ("evidence_sources", STRING_LIST),
            ("evidence_count", pa.int64()),
            ("primary_evidence_source", pa.string()),
            ("is_game_specific", pa.bool_()),
            ("is_entity_matchable", pa.bool_()),
            ("resource_version", pa.string()),
        ]
    ),
    "patch_episodes": pa.schema(
        [
            ("patch_id", pa.string()),
            ("game_id", pa.int64()),
            ("game_name", pa.string()),
            ("announcement_id", pa.string()),
            ("announcement_revision_id", pa.string()),
            ("title", pa.string()),
            ("source_url", pa.string()),
            ("published_at_utc", TIMESTAMP),
            ("published_unix", pa.int64()),
            ("release_at_utc", TIMESTAMP),
            ("release_time_status", pa.string()),
            ("anchor_at_utc", TIMESTAMP),
            ("anchor_source", pa.string()),
            ("window_start_unix", pa.int64()),
            ("window_end_unix", pa.int64()),
            ("categories", STRING_LIST),
            ("full_patch_notes_status", pa.string()),
            ("time_is_release_verified", pa.bool_()),
        ]
    ),
    "review_window_memberships": pa.schema(
        [
            ("membership_id", pa.string()),
            ("patch_id", pa.string()),
            ("source_patch_id", pa.string()),
            ("game_id", pa.int64()),
            ("announcement_id", pa.string()),
            ("review_revision_id", pa.string()),
            ("review_id", pa.string()),
            ("window_segment", pa.string()),
            ("window_start_unix", pa.int64()),
            ("window_end_unix", pa.int64()),
            ("anchor_unix", pa.int64()),
            ("anchor_source", pa.string()),
            ("created_unix", pa.int64()),
            ("membership_rule", pa.string()),
            ("membership_semantics", pa.string()),
        ]
    ),
    "patch_review_windows": pa.schema(
        [
            ("window_id", pa.string()),
            ("patch_id", pa.string()),
            ("source_patch_id", pa.string()),
            ("game_id", pa.int64()),
            ("announcement_id", pa.string()),
            ("segment", pa.string()),
            ("start_unix", pa.int64()),
            ("end_unix", pa.int64()),
            ("start_at_utc", TIMESTAMP),
            ("end_at_utc", TIMESTAMP),
            ("anchor_unix", pa.int64()),
            ("anchor_source", pa.string()),
            ("collection_status", pa.string()),
            ("page_count", pa.int64()),
            ("unique_review_revisions", pa.int64()),
            ("unique_review_ids", pa.int64()),
            ("total_matching_reported", pa.int64()),
            ("review_coverage_fraction", pa.float64()),
            ("issues_json", pa.large_string()),
            ("membership_semantics", pa.string()),
        ]
    ),
    "patch_episode_overlaps": pa.schema(
        [
            ("overlap_id", pa.string()),
            ("game_id", pa.int64()),
            ("patch_id_a", pa.string()),
            ("patch_id_b", pa.string()),
            ("overlap_start_unix", pa.int64()),
            ("overlap_end_unix", pa.int64()),
            ("overlap_seconds", pa.int64()),
            ("temporal_only", pa.bool_()),
            ("interpretation", pa.string()),
        ]
    ),
    "change_temporal_ambiguities": pa.schema(
        [
            ("ambiguity_id", pa.string()),
            ("game_id", pa.int64()),
            ("change_id_a", pa.string()),
            ("change_id_b", pa.string()),
            ("patch_id_a", pa.string()),
            ("patch_id_b", pa.string()),
            ("entity_normalized", pa.string()),
            ("aspect_a", pa.string()),
            ("aspect_b", pa.string()),
            ("reason", pa.string()),
        ]
    ),
    "qa_sample": pa.schema(
        [
            ("sample_id", pa.string()),
            ("dataset_id", pa.string()),
            ("sample_kind", pa.string()),
            ("stratum", pa.string()),
            ("source_row_id", pa.string()),
            ("game_id", pa.int64()),
            ("language", pa.string()),
            ("source_excerpt", pa.large_string()),
            ("extracted_fields_json", pa.large_string()),
            ("selection_seed", pa.string()),
            ("selection_rule", pa.string()),
            ("manual_review_status", pa.string()),
        ]
    ),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _find_source_run(root: Path, requested: str | None) -> Path:
    if requested:
        path = root / requested
        if not path.is_dir():
            raise FileNotFoundError(f"Stage 1 source run not found: {path}")
        return path
    runs = (
        sorted(
            (path for path in root.iterdir() if path.is_dir() and path.name.startswith("rv1-")),
            key=lambda path: path.name,
            reverse=True,
        )
        if root.exists()
        else []
    )
    runs = [path for path in runs if (path / "announcements.parquet").exists()]
    if not runs:
        raise FileNotFoundError(f"No Stage 1 normalized run found under {root}")
    return runs[0]


def _parquet_rows(path: Path, *, batch_size: int = 4096) -> Iterator[dict[str, Any]]:
    parquet = pq.ParquetFile(path)
    for batch in parquet.iter_batches(batch_size=batch_size):
        yield from batch.to_pylist()


def _write_rows(
    path: Path, rows: Iterable[dict[str, Any]], schema: pa.Schema, batch_size: int = 4096
) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    writer: pq.ParquetWriter | None = None
    count = 0
    chunk: list[dict[str, Any]] = []
    try:
        for row in rows:
            chunk.append(row)
            if len(chunk) >= batch_size:
                table = pa.Table.from_pylist(chunk, schema=schema)
                if writer is None:
                    writer = pq.ParquetWriter(path, schema, compression="zstd", version="2.6")
                writer.write_table(table, row_group_size=batch_size)
                count += len(chunk)
                chunk = []
        if chunk:
            table = pa.Table.from_pylist(chunk, schema=schema)
            if writer is None:
                writer = pq.ParquetWriter(path, schema, compression="zstd", version="2.6")
            writer.write_table(table, row_group_size=batch_size)
            count += len(chunk)
        if writer is None:
            pq.write_table(pa.Table.from_pylist([], schema=schema), path, compression="zstd")
    finally:
        if writer is not None:
            writer.close()
    return count


def _review_batch_rows(
    path: Path, batch_size: int, limit: int | None = None
) -> Iterator[list[dict[str, Any]]]:
    emitted = 0
    for batch in pq.ParquetFile(path).iter_batches(batch_size=batch_size):
        rows = batch.to_pylist()
        if limit is not None and emitted + len(rows) > limit:
            rows = rows[: limit - emitted]
        if rows:
            emitted += len(rows)
            yield rows
        if limit is not None and emitted >= limit:
            break


def _manifest_run_id(
    source_run: str,
    source_hashes: dict[str, str],
    limit: int | None,
    sample_per_stratum: int,
) -> tuple[str, str]:
    fingerprint = content_hash(
        {
            "source_run": source_run,
            "source_hashes": source_hashes,
            "schema_version": STAGE2_SCHEMA_VERSION,
            "classifier_version": CLASSIFIER_VERSION,
            "change_extractor_version": CHANGE_EXTRACTOR_VERSION,
            "claim_extractor_version": CLAIM_EXTRACTOR_VERSION,
            "sample_seed": SAMPLE_SEED,
            "sample_per_stratum": sample_per_stratum,
            "limit_reviews": limit,
        }
    )
    return f"rv2-{fingerprint[:24]}", fingerprint


def run_stage2(
    *,
    repo_root: Path,
    source_run: str | None = None,
    normalized_root: Path = DEFAULT_NORMALIZED_ROOT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    report_root: Path = DEFAULT_REPORT_ROOT,
    review_batch_size: int = 2048,
    limit_reviews: int | None = None,
    sample_per_stratum: int = 2,
) -> dict[str, Any]:
    """Extract versioned Stage 2 datasets; this intentionally creates no pairs/labels."""
    source_dir = _find_source_run(repo_root / normalized_root, source_run)
    required = [
        "games.parquet",
        "announcements.parquet",
        "patch_candidates.parquet",
        "review_revisions.parquet",
        "review_windows.parquet",
        "review_window_memberships.parquet",
    ]
    missing = [name for name in required if not (source_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Stage 1 source run is missing required inputs: {missing}")
    source_hashes = {name: _sha256(source_dir / name) for name in required}
    dataset_id, fingerprint = _manifest_run_id(
        source_dir.name, source_hashes, limit_reviews, sample_per_stratum
    )
    output_dir = repo_root / output_root / dataset_id
    report_dir = repo_root / report_root / dataset_id
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    games = pq.read_table(source_dir / "games.parquet").to_pylist()
    game_names = {int(row["appid"]): row["game_name"] for row in games}
    announcements = pq.read_table(source_dir / "announcements.parquet").to_pylist()
    classifications = [classify_announcement(row) for row in announcements]
    for row in classifications:
        row["game_name"] = game_names.get(int(row.get("appid") or 0))
    classification_by_revision = {
        str(row["announcement_revision_id"]): row for row in classifications
    }
    changes = extract_patch_changes(announcements, classification_by_revision, game_names)
    review_path = source_dir / "review_revisions.parquet"
    eligible_announcements = [
        row
        for row in announcements
        if classification_by_revision[str(row.get("announcement_revision_id"))]["patch_eligible"]
    ]

    def all_review_rows() -> Iterator[dict[str, Any]]:
        for batch in _review_batch_rows(review_path, review_batch_size, limit_reviews):
            yield from batch

    terminology_rows, terminology_by_game = build_terminology(
        eligible_announcements,
        changes,
        all_review_rows(),
        game_names,
    )

    patch_candidates = pq.read_table(source_dir / "patch_candidates.parquet").to_pylist()
    candidate_by_revision = {str(row["announcement_revision_id"]): row for row in patch_candidates}
    episodes = _make_patch_episodes(classifications, candidate_by_revision, game_names)
    episode_by_id = {row["patch_id"]: row for row in episodes}
    episode_by_announcement = {row["announcement_revision_id"]: row for row in episodes}
    old_to_new_patch = {
        str(candidate["patch_id"]): episode_by_announcement[
            str(candidate["announcement_revision_id"])
        ]["patch_id"]
        for candidate in patch_candidates
        if str(candidate["announcement_revision_id"]) in episode_by_announcement
    }
    source_windows = pq.read_table(source_dir / "review_windows.parquet").to_pylist()
    source_memberships = pq.read_table(source_dir / "review_window_memberships.parquet").to_pylist()
    memberships = _make_memberships(
        source_memberships, source_windows, old_to_new_patch, episode_by_id
    )
    stage2_windows = _make_review_windows(source_windows, old_to_new_patch)
    overlaps = _make_episode_overlaps(episodes)
    ambiguities = _make_change_ambiguities(changes, episodes)

    sample_rows = _make_qa_sample(
        dataset_id,
        changes,
        terminology_rows,
        output_dir,
        sample_per_stratum,
    )
    # Review samples are appended while streaming claims; this keeps memory bounded.
    claim_output_path = output_dir / "review_claims.parquet"
    claim_writer: pq.ParquetWriter | None = None
    claim_count = 0
    nonempty_review_count = 0
    no_claim_review_count = 0
    no_claim_review_ids: list[str] = []
    claim_group_counts: Counter[tuple[int, str]] = Counter()
    claim_review_ids_by_game: dict[int, set[str]] = defaultdict(set)
    claim_samples: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    claim_quality_counters: Counter[str] = Counter()
    try:
        for batch in _review_batch_rows(review_path, review_batch_size, limit_reviews):
            for review in batch:
                if str(review.get("review_text_original") or "").strip():
                    nonempty_review_count += 1
            batch_claims = extract_review_claims(batch, game_names, terminology_by_game)
            claim_count += len(batch_claims)
            claimed_reviews = {str(row["review_revision_id"]) for row in batch_claims}
            for review in batch:
                if (
                    str(review.get("review_revision_id")) not in claimed_reviews
                    and str(review.get("review_text_original") or "").strip()
                ):
                    no_claim_review_count += 1
                    if len(no_claim_review_ids) < 50:
                        no_claim_review_ids.append(str(review.get("review_revision_id")))
            table = pa.Table.from_pylist(batch_claims, schema=SCHEMAS["review_claims"])
            if claim_writer is None:
                claim_writer = pq.ParquetWriter(
                    claim_output_path, SCHEMAS["review_claims"], compression="zstd", version="2.6"
                )
            if batch_claims:
                claim_writer.write_table(table, row_group_size=review_batch_size)
            for claim in batch_claims:
                key = (int(claim["game_id"] or 0), str(claim.get("review_language") or "unknown"))
                claim_group_counts[key] += 1
                claim_review_ids_by_game[int(claim["game_id"] or 0)].add(
                    str(claim["review_revision_id"])
                )
                claim_samples[key].append(claim)
                claim_samples[key].sort(key=lambda row: _sample_hash(row["claim_id"]))
                del claim_samples[key][sample_per_stratum:]
                claim_quality_counters["low_confidence_below_0_5"] += int(
                    claim["extraction_confidence"] < 0.5
                )
                claim_quality_counters["entity_unresolved"] += int(
                    claim["referenced_entity"] is None
                )
                claim_quality_counters["aspect_unresolved"] += int(claim["aspect"] is None)
                claim_quality_counters["polarity_unknown"] += int(claim["polarity"] is None)
    finally:
        if claim_writer is not None:
            claim_writer.close()
        else:
            pq.write_table(
                pa.Table.from_pylist([], schema=SCHEMAS["review_claims"]),
                claim_output_path,
                compression="zstd",
            )

    _append_claim_samples(
        sample_rows, dataset_id, claim_samples, claim_group_counts, sample_per_stratum
    )
    manual_review_path = output_dir / "manual_review.json"
    manual_review = _load_manual_review(manual_review_path, dataset_id, sample_rows)
    reviewed_ids = set(manual_review.get("reviewed_sample_ids", []))
    for row in sample_rows:
        if row["sample_id"] in reviewed_ids:
            row["manual_review_status"] = "llm_inspected"
    counts = {
        "announcements": _write_rows(
            output_dir / "announcement_classifications.parquet",
            classifications,
            SCHEMAS["announcement_classifications"],
        ),
        "patch_changes": _write_rows(
            output_dir / "patch_changes.parquet", changes, SCHEMAS["patch_changes"]
        ),
        "game_terminology": _write_rows(
            output_dir / "game_terminology.parquet", terminology_rows, SCHEMAS["game_terminology"]
        ),
        "patch_episodes": _write_rows(
            output_dir / "patch_episodes.parquet", episodes, SCHEMAS["patch_episodes"]
        ),
        "review_window_memberships": _write_rows(
            output_dir / "review_window_memberships.parquet",
            memberships,
            SCHEMAS["review_window_memberships"],
        ),
        "patch_review_windows": _write_rows(
            output_dir / "patch_review_windows.parquet",
            stage2_windows,
            SCHEMAS["patch_review_windows"],
        ),
        "patch_episode_overlaps": _write_rows(
            output_dir / "patch_episode_overlaps.parquet",
            overlaps,
            SCHEMAS["patch_episode_overlaps"],
        ),
        "change_temporal_ambiguities": _write_rows(
            output_dir / "change_temporal_ambiguities.parquet",
            ambiguities,
            SCHEMAS["change_temporal_ambiguities"],
        ),
        "qa_sample": _write_rows(
            output_dir / "qa_sample.parquet", sample_rows, SCHEMAS["qa_sample"]
        ),
        "review_claims": claim_count,
    }
    game_coverage, patch_coverage = _make_coverage_rows(
        games,
        classifications,
        changes,
        episodes,
        stage2_windows,
        memberships,
        claim_group_counts,
        claim_review_ids_by_game,
    )
    _write_csv(report_dir / "game_extraction_coverage.csv", game_coverage)
    _write_csv(report_dir / "patch_extraction_coverage.csv", patch_coverage)
    quality = _quality_summary(
        dataset_id,
        source_dir.name,
        counts,
        classifications,
        changes,
        terminology_rows,
        memberships,
        overlaps,
        ambiguities,
        nonempty_review_count,
        no_claim_review_count,
        no_claim_review_ids,
        claim_group_counts,
        claim_quality_counters,
        sample_rows,
        sample_per_stratum,
        limit_reviews,
    )
    quality["game_extraction_coverage"] = game_coverage
    quality["patch_extraction_coverage"] = {
        "episode_rows": len(patch_coverage),
        "episodes_with_zero_extracted_changes": sum(
            row["patch_change_count"] == 0 for row in patch_coverage
        ),
        "episodes_with_partial_stage1_review_windows": sum(
            row["partial_review_window_segments"] > 0 for row in patch_coverage
        ),
    }
    quality["qa_sample"]["manual_review_status"] = (
        "llm_inspected"
        if sample_rows and all(row["sample_id"] in reviewed_ids for row in sample_rows)
        else "partially_llm_inspected"
        if reviewed_ids
        else "awaiting_inspection"
    )
    quality["qa_sample"]["manual_reviewed_rows"] = len(reviewed_ids)
    quality["qa_sample"]["manual_review_summary"] = manual_review.get("summary")
    quality["qa_sample"]["manual_findings"] = manual_review.get("findings", [])
    quality["qa_sample"]["manual_reviewer_type"] = manual_review.get("reviewer_type")
    report = _render_quality_report(quality, sample_rows)
    (report_dir / "quality_report.md").write_text(report, encoding="utf-8")
    (report_dir / "quality_report.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8"
    )
    manifest = {
        "dataset_id": dataset_id,
        "dataset_fingerprint": fingerprint,
        "stage": 2,
        "schema_version": STAGE2_SCHEMA_VERSION,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "source_stage1_run_id": source_dir.name,
        "source_tables_sha256": source_hashes,
        "code_versions": {
            "announcement_classifier": CLASSIFIER_VERSION,
            "patch_change_extractor": CHANGE_EXTRACTOR_VERSION,
            "review_claim_extractor": CLAIM_EXTRACTOR_VERSION,
        },
        "sample_seed": SAMPLE_SEED,
        "sample_per_stratum": sample_per_stratum,
        "review_batch_size": review_batch_size,
        "review_limit": limit_reviews,
        "complete": limit_reviews is None,
        "manual_review_status": quality["qa_sample"]["manual_review_status"],
        "manual_review_path": str(manual_review_path) if manual_review else None,
        "counts": counts,
        "paths": {
            "output": str(output_dir),
            "quality_report": str(report_dir / "quality_report.md"),
        },
        "boundary": "No patch-review pairs, relevance labels, or training labels are generated.",
        "llm_calls": 0,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8"
    )
    (report_root_abs(repo_root, report_root) / "latest.json").write_text(
        json.dumps(
            {"dataset_id": dataset_id, "report": str(report_dir / "quality_report.md")}, indent=2
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "status": "complete" if limit_reviews is None else "partial_smoke_run",
        "dataset_id": dataset_id,
        "source_run_id": source_dir.name,
        "output": str(output_dir),
        "report": str(report_dir / "quality_report.md"),
        "counts": counts,
    }


def _load_manual_review(
    path: Path, dataset_id: str, sample_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    if not path.exists():
        return {}
    review = json.loads(path.read_text(encoding="utf-8"))
    if review.get("dataset_id") != dataset_id:
        raise ValueError(f"Manual review artifact dataset_id does not match {dataset_id}")
    sample_ids = {row["sample_id"] for row in sample_rows}
    reviewed = set(review.get("reviewed_sample_ids", []))
    unknown = reviewed - sample_ids
    if unknown:
        raise ValueError(
            f"Manual review references sample IDs outside this dataset: {sorted(unknown)[:3]}"
        )
    return review


def _make_coverage_rows(
    games: list[dict[str, Any]],
    classifications: list[dict[str, Any]],
    changes: list[dict[str, Any]],
    episodes: list[dict[str, Any]],
    windows: list[dict[str, Any]],
    memberships: list[dict[str, Any]],
    claim_groups: Counter[tuple[int, str]],
    claim_review_ids_by_game: dict[int, set[str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_app_class: dict[int, list[dict[str, Any]]] = defaultdict(list)
    by_app_changes: dict[int, list[dict[str, Any]]] = defaultdict(list)
    by_patch_changes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_patch_memberships: Counter[str] = Counter()
    for row in classifications:
        by_app_class[int(row.get("appid") or 0)].append(row)
    for row in changes:
        appid = int(row.get("game_id") or 0)
        by_app_changes[appid].append(row)
        by_patch_changes[str(row.get("patch_id"))].append(row)
    for row in memberships:
        by_patch_memberships[str(row.get("patch_id"))] += 1
    languages_by_game: dict[int, set[str]] = defaultdict(set)
    claims_by_game: Counter[int] = Counter()
    for (appid, language), count in claim_groups.items():
        claims_by_game[appid] += count
        languages_by_game[appid].add(language)
    windows_by_game: dict[int, list[dict[str, Any]]] = defaultdict(list)
    windows_by_patch: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in windows:
        windows_by_game[int(row.get("game_id") or 0)].append(row)
        windows_by_patch[str(row.get("patch_id"))].append(row)
    game_rows = []
    for game in games:
        appid = int(game["appid"])
        announcements = by_app_class[appid]
        official = [
            row
            for row in announcements
            if row.get("officialness") == "steam_community_announcement_feed"
        ]
        eligible = [row for row in announcements if row.get("patch_eligible")]
        game_changes = by_app_changes[appid]
        game_windows = windows_by_game[appid]
        game_rows.append(
            {
                "game_id": appid,
                "game_name": game["game_name"],
                "announcements_classified": len(announcements),
                "official_developer_feed_announcements": len(official),
                "rule_eligible_patch_episodes": len(eligible),
                "atomic_changes": len(game_changes),
                "changes_with_verified_source_spans": sum(
                    bool(row.get("source_span_verified")) for row in game_changes
                ),
                "changes_with_unresolved_fields": sum(
                    bool(row.get("quality_flags")) for row in game_changes
                ),
                "review_claims": claims_by_game[appid],
                "review_revisions_with_claims": len(claim_review_ids_by_game.get(appid, set())),
                "claim_languages": ";".join(sorted(languages_by_game[appid])),
                "collected_review_window_segments": len(game_windows),
                "complete_review_window_segments": sum(
                    row.get("collection_status") == "complete" for row in game_windows
                ),
                "temporal_membership_rows": sum(
                    by_patch_memberships[row["patch_id"]]
                    for row in episodes
                    if int(row.get("game_id") or 0) == appid
                ),
            }
        )
    patch_rows = []
    for episode in episodes:
        patch_id = str(episode["patch_id"])
        patch_changes = by_patch_changes[patch_id]
        patch_windows = windows_by_patch[patch_id]
        patch_rows.append(
            {
                "patch_id": patch_id,
                "game_id": episode.get("game_id"),
                "game_name": episode.get("game_name"),
                "announcement_id": episode.get("announcement_id"),
                "title": episode.get("title"),
                "published_at_utc": episode.get("published_at_utc"),
                "release_at_utc": episode.get("release_at_utc"),
                "release_time_status": episode.get("release_time_status"),
                "time_is_release_verified": episode.get("time_is_release_verified"),
                "categories": ";".join(episode.get("categories") or []),
                "full_patch_notes_status": episode.get("full_patch_notes_status"),
                "patch_change_count": len(patch_changes),
                "source_verified_change_count": sum(
                    bool(row.get("source_span_verified")) for row in patch_changes
                ),
                "unresolved_change_count": sum(
                    bool(row.get("quality_flags")) for row in patch_changes
                ),
                "review_window_segment_count": len(patch_windows),
                "complete_review_window_segments": sum(
                    row.get("collection_status") == "complete" for row in patch_windows
                ),
                "partial_review_window_segments": sum(
                    row.get("collection_status") != "complete" for row in patch_windows
                ),
                "review_window_membership_rows": by_patch_memberships[patch_id],
            }
        )
    return game_rows, patch_rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def report_root_abs(repo_root: Path, report_root: Path) -> Path:
    path = repo_root / report_root
    path.mkdir(parents=True, exist_ok=True)
    return path


def _make_patch_episodes(
    classifications: list[dict[str, Any]],
    candidate_by_revision: dict[str, dict[str, Any]],
    game_names: dict[int, str],
) -> list[dict[str, Any]]:
    episodes = []
    for row in classifications:
        if not row.get("patch_eligible"):
            continue
        candidate = candidate_by_revision.get(str(row["announcement_revision_id"]), {})
        release_at = candidate.get("release_at_utc")
        published = row.get("published_at_utc")
        anchor = release_at or published
        anchor_unix = candidate.get("release_at_unix") if release_at else row.get("published_unix")
        if anchor_unix is None and anchor is not None:
            anchor_unix = int(anchor.timestamp())
        if anchor_unix is None:
            start = end = None
        else:
            start = int(anchor_unix) - 14 * 86400
            end = int(anchor_unix) + 14 * 86400
        episodes.append(
            {
                "patch_id": row["patch_id"],
                "game_id": row.get("appid"),
                "game_name": game_names.get(int(row.get("appid") or 0)),
                "announcement_id": row.get("announcement_id"),
                "announcement_revision_id": row.get("announcement_revision_id"),
                "title": row.get("title"),
                "source_url": row.get("source_url"),
                "published_at_utc": published,
                "published_unix": row.get("published_unix"),
                "release_at_utc": release_at,
                "release_time_status": candidate.get("release_time_status", "not_verified"),
                "anchor_at_utc": anchor,
                "anchor_source": "verified_release_time"
                if release_at
                else "announcement_publication_time_unverified_proxy",
                "window_start_unix": start,
                "window_end_unix": end,
                "categories": row.get("categories") or [],
                "full_patch_notes_status": row.get("full_patch_notes_status"),
                "time_is_release_verified": bool(release_at),
            }
        )
    return episodes


def _make_memberships(
    source_memberships: list[dict[str, Any]],
    source_windows: list[dict[str, Any]],
    old_to_new_patch: dict[str, str],
    episode_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for row in source_memberships:
        new_patch = old_to_new_patch.get(str(row.get("patch_id")))
        if not new_patch or new_patch not in episode_by_id:
            continue
        rows.append(
            {
                "membership_id": rv2_id(
                    "membership",
                    new_patch,
                    row.get("review_revision_id"),
                    row.get("window_segment"),
                ),
                "patch_id": new_patch,
                "source_patch_id": row.get("patch_id"),
                "game_id": row.get("appid"),
                "announcement_id": row.get("announcement_id"),
                "review_revision_id": row.get("review_revision_id"),
                "review_id": row.get("review_id"),
                "window_segment": row.get("window_segment"),
                "window_start_unix": row.get("window_start_unix"),
                "window_end_unix": row.get("window_end_unix"),
                "anchor_unix": row.get("anchor_unix"),
                "anchor_source": row.get("anchor_source"),
                "created_unix": row.get("created_unix"),
                "membership_rule": row.get("membership_rule"),
                "membership_semantics": "temporal_window_membership_only_not_patch_relevance",
            }
        )
    return rows


def _make_review_windows(
    source_windows: list[dict[str, Any]],
    old_to_new_patch: dict[str, str],
) -> list[dict[str, Any]]:
    rows = []
    for row in source_windows:
        patch_id = old_to_new_patch.get(str(row.get("patch_id")))
        if not patch_id:
            continue
        output = dict(row)
        output.update(
            {
                "patch_id": patch_id,
                "source_patch_id": row.get("patch_id"),
                "game_id": row.get("appid"),
                "membership_semantics": "collection_window_coverage_not_patch_relevance",
            }
        )
        rows.append(output)
    return rows


def _make_episode_overlaps(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    by_game: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in episodes:
        if row.get("window_start_unix") is not None:
            by_game[int(row["game_id"])].append(row)
    for appid, game_episodes in by_game.items():
        ordered = sorted(game_episodes, key=lambda row: (row["window_start_unix"], row["patch_id"]))
        for index, left in enumerate(ordered):
            for right in ordered[index + 1 :]:
                if right["window_start_unix"] > left["window_end_unix"]:
                    break
                start = max(left["window_start_unix"], right["window_start_unix"])
                end = min(left["window_end_unix"], right["window_end_unix"])
                if start <= end:
                    rows.append(
                        {
                            "overlap_id": rv2_id(
                                "patch_overlap",
                                appid,
                                left["patch_id"],
                                right["patch_id"],
                                start,
                                end,
                            ),
                            "game_id": appid,
                            "patch_id_a": left["patch_id"],
                            "patch_id_b": right["patch_id"],
                            "overlap_start_unix": start,
                            "overlap_end_unix": end,
                            "overlap_seconds": int(end - start + 1),
                            "temporal_only": True,
                            "interpretation": "review time may fall in both episodes; this is not relevance evidence",
                        }
                    )
    return rows


def _make_change_ambiguities(
    changes: list[dict[str, Any]],
    episodes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    episode_map = {row["patch_id"]: row for row in episodes}
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for change in changes:
        entity = str(change.get("entity") or "").strip()
        if not entity or change.get("extraction_confidence", 0) < 0.5:
            continue
        normalized = re.sub(r"[^\w]+", " ", entity.casefold(), flags=re.UNICODE).strip()
        if len(normalized) > 1:
            grouped[(int(change["game_id"]), normalized)].append(change)
    rows = []
    for (appid, normalized), group in grouped.items():
        group.sort(key=lambda row: row["change_id"])
        for i, left in enumerate(group):
            for right in group[i + 1 :]:
                if left["patch_id"] == right["patch_id"]:
                    continue
                event_a = episode_map.get(left["patch_id"])
                event_b = episode_map.get(right["patch_id"])
                if not event_a or not event_b:
                    continue
                if max(event_a["window_start_unix"], event_b["window_start_unix"]) > min(
                    event_a["window_end_unix"], event_b["window_end_unix"]
                ):
                    continue
                rows.append(
                    {
                        "ambiguity_id": rv2_id("ambiguity", left["change_id"], right["change_id"]),
                        "game_id": appid,
                        "change_id_a": left["change_id"],
                        "change_id_b": right["change_id"],
                        "patch_id_a": left["patch_id"],
                        "patch_id_b": right["patch_id"],
                        "entity_normalized": normalized,
                        "aspect_a": left.get("aspect"),
                        "aspect_b": right.get("aspect"),
                        "reason": "same normalized entity appears in temporally overlapping patch episodes",
                    }
                )
    return rows


def _make_qa_sample(
    dataset_id: str,
    changes: list[dict[str, Any]],
    terminology: list[dict[str, Any]],
    output_dir: Path,
    sample_per_stratum: int,
) -> list[dict[str, Any]]:
    rows = []
    change_groups: dict[tuple[int, str, str], list[dict[str, Any]]] = defaultdict(list)
    for change in changes:
        status = str(change.get("developer_status") or "unclear")
        quality = "flagged" if change.get("quality_flags") else "resolved"
        key = (int(change.get("game_id") or 0), status, quality)
        change_groups[key].append(change)
    for (appid, status, quality), group in sorted(change_groups.items()):
        chosen = sorted(group, key=lambda row: _sample_hash(row["change_id"]))[:sample_per_stratum]
        for change in chosen:
            rows.append(
                {
                    "sample_id": rv2_id("qa", dataset_id, "change", change["change_id"]),
                    "dataset_id": dataset_id,
                    "sample_kind": "patch_change",
                    "stratum": f"game={appid};status={status};quality={quality}",
                    "source_row_id": change["change_id"],
                    "game_id": appid,
                    "language": None,
                    "source_excerpt": str(
                        change.get("source_span_raw") or change.get("change_text") or ""
                    )[:1200],
                    "extracted_fields_json": json.dumps(
                        {
                            key: change.get(key)
                            for key in (
                                "change_text",
                                "heading_path",
                                "entity",
                                "entity_candidates",
                                "aspect",
                                "action",
                                "direction",
                                "previous_value",
                                "new_value",
                                "numeric_delta",
                                "developer_status",
                                "bug_trigger",
                                "bug_symptom",
                                "source_span_start",
                                "source_span_end",
                                "source_span_verified",
                                "quality_flags",
                            )
                        },
                        ensure_ascii=False,
                    ),
                    "selection_seed": SAMPLE_SEED,
                    "selection_rule": f"lowest stable SHA-256 ranks within game, developer status, and quality group; n={sample_per_stratum}",
                    "manual_review_status": "awaiting_manual_inspection",
                }
            )
    return rows


def _sample_hash(value: str) -> str:
    return hashlib.sha256(f"{SAMPLE_SEED}|{value}".encode()).hexdigest()


def _append_claim_samples(
    rows: list[dict[str, Any]],
    dataset_id: str,
    groups: dict[tuple[int, str], list[dict[str, Any]]],
    language_counts: Counter[tuple[int, str]],
    sample_per_stratum: int,
) -> None:
    top_languages: dict[int, set[str]] = defaultdict(set)
    by_game: dict[int, list[tuple[str, int]]] = defaultdict(list)
    for (appid, language), count in language_counts.items():
        by_game[appid].append((language, count))
    for appid, entries in by_game.items():
        top_languages[appid] = {
            language for language, _ in sorted(entries, key=lambda row: (-row[1], row[0]))[:2]
        }
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for (appid, language), group in groups.items():
        bucket = language if language in top_languages[appid] else "other_languages"
        grouped[(appid, bucket)].extend(group)
    for (appid, language_bucket), group in sorted(grouped.items()):
        chosen = sorted(group, key=lambda row: _sample_hash(row["claim_id"]))[:sample_per_stratum]
        for claim in chosen:
            text = str(claim["claim_text_original"])
            rows.append(
                {
                    "sample_id": rv2_id("qa", dataset_id, "claim", claim["claim_id"]),
                    "dataset_id": dataset_id,
                    "sample_kind": "review_claim",
                    "stratum": f"game={appid};language_group={language_bucket}",
                    "source_row_id": claim["claim_id"],
                    "game_id": appid,
                    "language": language_bucket,
                    "source_excerpt": text[:700],
                    "extracted_fields_json": json.dumps(
                        {
                            key: claim.get(key)
                            for key in (
                                "claim_text_original",
                                "referenced_entity",
                                "aspect",
                                "opinion_or_issue",
                                "opinion_terms",
                                "polarity",
                                "temporal_cues",
                                "negated",
                                "uncertain",
                                "extraction_confidence",
                                "claim_span_start",
                                "claim_span_end",
                                "review_revision_id",
                                "review_created_at_utc",
                                "review_updated_at_utc",
                            )
                        },
                        ensure_ascii=False,
                        default=str,
                    ),
                    "selection_seed": SAMPLE_SEED,
                    "selection_rule": f"lowest stable SHA-256 ranks within game and top two observed Steam languages plus other-languages group; n={sample_per_stratum}",
                    "manual_review_status": "awaiting_manual_inspection",
                }
            )


def _quality_summary(
    dataset_id: str,
    source_run: str,
    counts: dict[str, int],
    classifications: list[dict[str, Any]],
    changes: list[dict[str, Any]],
    terminology: list[dict[str, Any]],
    memberships: list[dict[str, Any]],
    overlaps: list[dict[str, Any]],
    ambiguities: list[dict[str, Any]],
    nonempty_reviews: int,
    no_claim_review_count: int,
    no_claim_review_ids: list[str],
    claim_groups: Counter[tuple[int, str]],
    claim_quality_counters: Counter[str],
    sample_rows: list[dict[str, Any]],
    sample_per_stratum: int,
    limit_reviews: int | None,
) -> dict[str, Any]:
    category_counts: Counter[str] = Counter()
    game_announcement_counts: Counter[int] = Counter()
    external_linked = 0
    for row in classifications:
        game_announcement_counts[int(row.get("appid") or 0)] += 1
        category_counts.update(row.get("categories") or [])
        if row.get("patch_eligible") and row.get("full_patch_notes_status") in {
            "announcement_body_and_linked_notes_unverified",
            "linked_content_not_fetched",
        }:
            external_linked += 1
    change_flags: Counter[str] = Counter()
    for row in changes:
        change_flags.update(row.get("quality_flags") or [])
    change_unresolved = sum(bool(row.get("quality_flags")) for row in changes)
    span_failures = sum(not row.get("source_span_verified") for row in changes)
    return {
        "dataset_id": dataset_id,
        "source_stage1_run_id": source_run,
        "complete_review_population": limit_reviews is None,
        "review_limit": limit_reviews,
        "counts": {
            **counts,
            "nonempty_reviews_processed": nonempty_reviews,
            "nonempty_reviews_without_claim_rows": no_claim_review_count,
        },
        "announcement_category_counts": dict(category_counts),
        "announcement_counts_by_game": {
            str(key): value for key, value in sorted(game_announcement_counts.items())
        },
        "change_quality": {
            "rows_with_any_quality_flag": change_unresolved,
            "flagged_rate": change_unresolved / len(changes) if changes else 0.0,
            "source_span_failures": span_failures,
            "source_span_failure_rate": span_failures / len(changes) if changes else 0.0,
            "flag_counts": dict(change_flags),
            "no_change_rows_generated_for_headings": True,
        },
        "claim_quality": {
            "low_confidence_rows_below_0_5": claim_quality_counters["low_confidence_below_0_5"],
            "entity_unresolved_rows": claim_quality_counters["entity_unresolved"],
            "aspect_unresolved_rows": claim_quality_counters["aspect_unresolved"],
            "polarity_unknown_rows": claim_quality_counters["polarity_unknown"],
            "nonempty_reviews_without_claim_rows": no_claim_review_count,
            "review_rows_without_claim_sample_ids": no_claim_review_ids,
            "language_claim_counts": {
                f"{appid}:{language}": value
                for (appid, language), value in sorted(claim_groups.items())
            },
        },
        "terminology": {
            "resource_count": len(terminology),
            "game_counts": dict(Counter(str(row["game_id"]) for row in terminology)),
            "cross_game_global_ontology": False,
        },
        "temporal": {
            "window_membership_rows": len(memberships),
            "patch_episode_overlaps": len(overlaps),
            "same_entity_change_ambiguities": len(ambiguities),
            "membership_semantics": "time-window membership only; not patch relevance",
            "review_claims_assigned_to_patches": 0,
        },
        "source_gaps": {
            "announcements_with_external_or_unverified_note_links": external_linked,
            "external_link_fetching": "not performed in Stage 2; only Stage 1 captured URLs",
            "release_times": "publication time is used as an explicitly unverified window anchor where no release time exists",
            "manual_translation": "not performed; original review language is preserved",
        },
        "qa_sample": {
            "sample_seed": SAMPLE_SEED,
            "sample_per_stratum": sample_per_stratum,
            "rows": len(sample_rows),
            "manual_review_status": "awaiting_inspection",
            "change_strata": sum(row["sample_kind"] == "patch_change" for row in sample_rows),
            "claim_strata": sum(row["sample_kind"] == "review_claim" for row in sample_rows),
        },
        "disallowed_outputs": [
            "patch-review candidate pairs",
            "relevance labels",
            "training labels",
        ],
    }


def _render_quality_report(quality: dict[str, Any], sample_rows: list[dict[str, Any]]) -> str:
    counts = quality["counts"]
    change_quality = quality["change_quality"]
    lines = [
        f"# Stage 2 extraction quality report — {quality['dataset_id']}",
        "",
        f"Source Stage 1 run: `{quality['source_stage1_run_id']}`.",
        "This report covers announcement classification, atomic patch-change extraction, review-claim segmentation, game-specific vocabulary, and temporal structure.",
        "No patch-review pairs or relevance/training labels were generated.",
        "",
        "## Dataset counts",
        "",
        "| Dataset | Rows |",
        "| --- | ---: |",
        f"| Announcements classified | {counts.get('announcements', 0):,} |",
        f"| Patch changes extracted | {counts.get('patch_changes', 0):,} |",
        f"| Review claims extracted | {counts.get('review_claims', 0):,} |",
        f"| Game terminology entries | {counts.get('game_terminology', 0):,} |",
        f"| Patch episodes | {counts.get('patch_episodes', 0):,} |",
        f"| Patch review-window segments | {counts.get('patch_review_windows', 0):,} |",
        f"| Review-window membership rows | {counts.get('review_window_memberships', 0):,} |",
        f"| Overlapping patch episode pairs | {counts.get('patch_episode_overlaps', 0):,} |",
        f"| Same-entity temporal ambiguities | {counts.get('change_temporal_ambiguities', 0):,} |",
        "",
        "## Coverage by game",
        "",
        "| Game | Official-feed posts | Eligible episodes | Atomic changes | Review claims | Review revisions with claims | Complete window segments |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in quality.get("game_extraction_coverage", []):
        lines.append(
            f"| {row['game_name']} | {row['official_developer_feed_announcements']:,} | {row['rule_eligible_patch_episodes']:,} | {row['atomic_changes']:,} | {row['review_claims']:,} | {row['review_revisions_with_claims']:,} | {row['complete_review_window_segments']:,}/{row['collected_review_window_segments']:,} |"
        )
    lines += [
        "",
        "## Extraction QA metrics",
        "",
        f"- Change rows with one or more unresolved fields: {change_quality['rows_with_any_quality_flag']:,} ({change_quality['flagged_rate']:.1%}).",
        f"- Exact source-span validation failures: {change_quality['source_span_failures']:,} ({change_quality['source_span_failure_rate']:.1%}).",
        f"- Non-empty reviews with no claim row: {quality['claim_quality']['nonempty_reviews_without_claim_rows']:,}.",
        f"- Low-confidence claims (<0.5): {quality['claim_quality']['low_confidence_rows_below_0_5']:,}.",
        f"- Claims without an entity/aspect: {quality['claim_quality']['entity_unresolved_rows']:,} / {quality['claim_quality']['aspect_unresolved_rows']:,}; unknown polarity: {quality['claim_quality']['polarity_unknown_rows']:,}.",
        f"- Change quality flags: `{json.dumps(change_quality['flag_counts'], ensure_ascii=False, sort_keys=True)}`.",
        "- Heading-only false changes: headings are maintained in hierarchy and are not emitted as changes.",
        "- Patch specificity: claims remain `not_assigned`; temporal membership is not treated as relevance.",
        "",
        "## Announcement categories",
        "",
    ]
    for name, value in sorted(quality["announcement_category_counts"].items()):
        lines.append(f"- `{name}`: {value:,}")
    lines += [
        "",
        "## Data limitations and common failure modes",
        "",
        "- Deterministic rules are strongest for explicit Steam lists and numeric phrases. Nested hierarchy is retained, but prose without an explicit action predicate is omitted from `patch_changes`.",
        "- Entity/aspect extraction may remain unresolved when a patch sentence uses implicit context or game-specific shorthand; those rows have quality flags and confidence values.",
        "- A Steam announcement can link to a full official changelog that was not collected by Stage 1. Such URLs and completeness states are retained; Stage 2 did not fetch external pages.",
        "- Review claims are sentence/contrast-clause spans. Aspect and polarity rules are conservative and English-heavy; non-English review text is retained verbatim, while unknown polarity remains null.",
        "- Words such as `now`, `broken`, `nerfed`, and `unbalanced` do not make a claim patch-specific. The pipeline records lexical temporal cues only and assigns no patch relevance.",
        "- Source review windows are incomplete for some patches in Stage 1; all memberships are explicitly temporal-only.",
        "",
        "## Manual sample inspection",
        "",
        f"Inspection status: `{quality['qa_sample'].get('manual_review_status', 'awaiting_inspection')}` ({quality['qa_sample'].get('manual_reviewed_rows', 0):,} of {len(sample_rows):,} sample rows recorded).",
    ]
    if quality["qa_sample"].get("manual_reviewer_type"):
        lines.append(f"Reviewer type: `{quality['qa_sample']['manual_reviewer_type']}`.")
    if quality["qa_sample"].get("manual_review_summary"):
        lines.append(quality["qa_sample"]["manual_review_summary"])
    for finding in quality["qa_sample"].get("manual_findings", []):
        lines.append(f"- `{finding.get('judgment', 'note')}` — {finding.get('finding', '')}")
    lines += [
        "",
        "## Reproducible stratified audit sample",
        "",
        f"Selection seed: `{quality['qa_sample']['sample_seed']}`. The sample uses stable SHA-256 ranking within game/developer-status/quality groups for changes and game/top-two-language-plus-other groups for claims, at up to {quality['qa_sample']['sample_per_stratum']} rows per stratum.",
        "The sample records the original source excerpt beside the extracted fields. Spans refer to the original raw announcement body or exact review revision text.",
        "",
    ]
    for row in sample_rows:
        lines.extend(
            [
                f"### {row['sample_kind']} — `{row['stratum']}` — `{row['source_row_id']}`",
                "",
                f"Manual review status: `{row['manual_review_status']}`.",
                "",
                "Original source excerpt:",
                "",
                "```text",
                str(row["source_excerpt"]).replace("```", "'''"),
                "```",
                "",
                "Extracted fields:",
                "",
                "```json",
                json.dumps(
                    json.loads(row["extracted_fields_json"]),
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                ),
                "```",
                "",
            ]
        )
    lines += [
        "## Output paths",
        "",
        "The companion `manifest.json` records source table hashes, schema/extractor versions, and row counts. Parquet outputs are stored under the dataset directory printed by the CLI.",
        "Patch-level and game-level summaries are in `patch_extraction_coverage.csv` and `game_extraction_coverage.csv` beside this report.",
        "",
    ]
    return "\n".join(lines)
