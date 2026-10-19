"""Versioned, independent retrieval signals over the approved Stage 2 tables."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from steam_patch_relevance import __version__
from steam_patch_relevance.stage3 import RETRIEVER_VERSION, STAGE3_SCHEMA_VERSION
from steam_patch_relevance.stage3.bm25 import (
    BM25Index,
    change_query_text,
    claim_document_text,
)
from steam_patch_relevance.stage3.dense import (
    EmbeddingCache,
    SentenceTransformerEncoder,
    top_cosine_hits,
)
from steam_patch_relevance.stage3.entity import (
    GameVocabulary,
    aspect_family,
    normalize_term,
    rank_entity_aspect,
)

DEFAULT_SOURCE_DATASET = "rv2-d52a3f9f1a3de2fe80aa098f"
DEFAULT_DATA_ROOT = Path("data/relevance_v1")
DEFAULT_OUTPUT_ROOT = DEFAULT_DATA_ROOT / "processed" / "stage3"
DEFAULT_REPORT_ROOT = Path("reports/relevance_v1/stage3")
DEFAULT_DENSE_MODEL = "intfloat/multilingual-e5-small"
DEFAULT_DENSE_REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"
DEFAULT_AUDIT_SEED = "stage3-full-list-audit-v1"
RRF_K = 60
SECONDS_PER_DAY = 86_400

STRING_LIST = pa.list_(pa.string())
TIMESTAMP = pa.timestamp("us", tz="UTC")

CANDIDATE_SCHEMA = pa.schema(
    [
        ("candidate_id", pa.string()),
        ("dataset_id", pa.string()),
        ("source_stage2_dataset_id", pa.string()),
        ("patch_id", pa.string()),
        ("game_id", pa.int64()),
        ("game_name", pa.string()),
        ("patch_title", pa.string()),
        ("patch_anchor_at_utc", TIMESTAMP),
        ("patch_anchor_source", pa.string()),
        ("change_id", pa.string()),
        ("change_text", pa.large_string()),
        ("change_entity", pa.string()),
        ("change_aspect", pa.string()),
        ("change_direction", pa.string()),
        ("change_source_url", pa.string()),
        ("claim_id", pa.string()),
        ("review_revision_id", pa.string()),
        ("review_id", pa.string()),
        ("claim_text", pa.large_string()),
        ("claim_entity", pa.string()),
        ("claim_aspect", pa.string()),
        ("claim_polarity", pa.string()),
        ("review_language", pa.string()),
        ("review_created_at_utc", TIMESTAMP),
        ("window_segments", STRING_LIST),
        ("other_window_patch_ids", STRING_LIST),
        ("competing_feature_patch_ids", STRING_LIST),
        ("bm25_rank", pa.int32()),
        ("bm25_score", pa.float64()),
        ("dense_rank", pa.int32()),
        ("dense_cosine_score", pa.float64()),
        ("dense_model_version", pa.string()),
        ("entity_aspect_rank", pa.int32()),
        ("entity_aspect_score", pa.float64()),
        ("entity_match_score", pa.float64()),
        ("aspect_match_score", pa.float64()),
        ("matched_entity", pa.string()),
        ("rrf_score", pa.float64()),
        ("fused_rank", pa.int32()),
        ("retrieval_methods", STRING_LIST),
        ("at_maximum_budget", pa.bool_()),
    ]
)

HARD_SCHEMA = pa.schema(
    [*CANDIDATE_SCHEMA, ("hard_case_types", STRING_LIST), ("hard_case_basis", pa.large_string())]
)

PATCH_DIAGNOSTIC_SCHEMA = pa.schema(
    [
        ("patch_id", pa.string()),
        ("retrieval_status", pa.string()),
        ("game_id", pa.int64()),
        ("game_name", pa.string()),
        ("patch_title", pa.string()),
        ("anchor_at_utc", TIMESTAMP),
        ("atomic_change_count", pa.int64()),
        ("stage2_change_count", pa.int64()),
        ("temporal_membership_count", pa.int64()),
        ("source_span_unverified_changes_excluded", pa.int64()),
        ("eligible_review_claim_count", pa.int64()),
        ("eligible_review_revision_count", pa.int64()),
        ("window_segment_count", pa.int64()),
        ("incomplete_window_segment_count", pa.int64()),
        ("possible_change_claim_pairs", pa.int64()),
        ("bm25_ranked_pairs", pa.int64()),
        ("dense_ranked_pairs", pa.int64()),
        ("entity_aspect_ranked_pairs", pa.int64()),
        ("hybrid_union_pairs", pa.int64()),
        ("bm25_queries_truncated", pa.int64()),
        ("dense_queries_truncated", pa.int64()),
        ("entity_queries_truncated", pa.int64()),
        ("bm25_pairs_omitted_by_budget", pa.int64()),
        ("dense_pairs_omitted_by_budget", pa.int64()),
        ("entity_pairs_omitted_by_budget", pa.int64()),
        ("candidate_pair_count", pa.int64()),
    ]
)

GENERIC_SYMPTOM_RE = re.compile(
    r"\b(crash(?:es|ed|ing)?|lag(?:gy|ging)?|disconnect(?:ed|ion)?|"
    r"bug(?:gy|s)?|glitch(?:es|y)?|freez(?:e|es|ing)|stutter(?:ing)?|"
    r"rubber[ -]?band(?:ing)?|desync(?:ed|hronized)?|server(?:s)? down)\b",
    re.IGNORECASE,
)
DIRECTION_CUES = {
    "increase": re.compile(
        r"\b(nerf(?:ed)?|reduce[ds]?|decreas(?:e|ed)|lower(?:ed)?|less|weaker)\b", re.I
    ),
    "decrease": re.compile(
        r"\b(buff(?:ed)?|rais(?:e|ed)|increas(?:e|ed)|higher|more|stronger)\b", re.I
    ),
}
HARD_CASE_TYPES = (
    "same_entity_different_aspect",
    "same_feature_generic_longstanding_complaint",
    "same_issue_type_different_trigger",
    "same_game_wrong_patch_or_overlap_candidate",
    "same_terminology_different_mechanic",
    "explicitly_contradictory_directional_cue",
)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _stable_id(prefix: str, *parts: str) -> str:
    payload = "\0".join(parts).encode("utf-8")
    return f"{prefix}_{_sha256_bytes(payload)[:24]}"


def _stable_order(seed: str, *parts: str) -> str:
    return _sha256_bytes("\0".join((seed, *parts)).encode("utf-8"))


def _read_rows(path: Path, *, columns: list[str] | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Required Stage 2/Stage 1 table is missing: {path}")
    return pq.read_table(path, columns=columns).to_pylist()


def _load_stage2_inputs(repo_root: Path, source_dataset: str) -> dict[str, Any]:
    source_root = repo_root / DEFAULT_DATA_ROOT / "processed" / "stage2" / source_dataset
    manifest_path = source_root / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Stage 2 dataset not found: {source_root}")
    stage2_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if stage2_manifest.get("dataset_id") != source_dataset or not stage2_manifest.get("complete"):
        raise ValueError(f"Stage 2 input is not a complete matching snapshot: {source_dataset}")
    columns = {
        "review_claims": [
            "claim_id",
            "review_revision_id",
            "review_id",
            "game_id",
            "game_name",
            "review_created_at_utc",
            "review_language",
            "claim_text_original",
            "referenced_entity",
            "aspect",
            "polarity",
            "temporal_cues",
            "negated",
            "uncertain",
            "opinion_or_issue",
        ],
    }
    tables = {}
    for name in (
        "patch_changes",
        "review_claims",
        "patch_episodes",
        "patch_review_windows",
        "review_window_memberships",
        "game_terminology",
    ):
        tables[name] = _read_rows(source_root / f"{name}.parquet", columns=columns.get(name))
    stage1_root = (
        repo_root / "data" / "relevance_v1" / "normalized" / stage2_manifest["source_stage1_run_id"]
    )
    tables["stage1_root"] = stage1_root
    tables["stage2_root"] = source_root
    tables["stage2_manifest"] = stage2_manifest
    return tables


def _windowed_memberships(
    memberships: list[dict[str, Any]],
    *,
    before_days: int,
    after_days: int,
    selected_patch_ids: set[str] | None,
    selected_game_ids: set[int] | None,
) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in memberships:
        if selected_patch_ids and row["patch_id"] not in selected_patch_ids:
            continue
        if selected_game_ids and row["game_id"] not in selected_game_ids:
            continue
        anchor = row.get("anchor_unix")
        created = row.get("created_unix")
        if anchor is None or created is None:
            continue
        start = anchor - before_days * SECONDS_PER_DAY
        end = anchor + after_days * SECONDS_PER_DAY
        if start <= created < end:
            output[row["patch_id"]].append(row)
    return output


def _join_patch_claims(
    memberships_by_patch: dict[str, list[dict[str, Any]]],
    claims: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[tuple[str, str], set[str]]]:
    claims_by_revision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        claims_by_revision[claim["review_revision_id"]].append(claim)
    by_patch: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    claim_patch_segments: dict[tuple[str, str], set[str]] = defaultdict(set)
    for patch_id, members in memberships_by_patch.items():
        for member in members:
            for claim in claims_by_revision.get(member["review_revision_id"], ()):
                if claim["game_id"] != member["game_id"]:
                    continue
                claim_id = claim["claim_id"]
                row = by_patch[patch_id].setdefault(claim_id, dict(claim))
                row["window_segments"] = sorted(
                    set(row.get("window_segments", []))
                    | {member.get("window_segment") or "unknown"}
                )
                claim_patch_segments[(claim_id, patch_id)].add(
                    member.get("window_segment") or "unknown"
                )
    return (
        {patch_id: list(rows.values()) for patch_id, rows in by_patch.items()},
        claim_patch_segments,
    )


def _select_audit_patches(
    eligible_changes: dict[str, list[dict[str, Any]]],
    memberships_by_patch: dict[str, list[dict[str, Any]]],
    episodes: dict[str, dict[str, Any]],
) -> list[str]:
    per_game: dict[int, list[str]] = defaultdict(list)
    for patch_id, changes in eligible_changes.items():
        if memberships_by_patch.get(patch_id) and changes:
            per_game[int(episodes[patch_id]["game_id"])].append(patch_id)
    selected = []
    for game_id, patch_ids in sorted(per_game.items()):
        selected.append(
            min(
                patch_ids,
                key=lambda patch_id: (
                    -len(eligible_changes[patch_id]),
                    episodes[patch_id].get("published_unix") or 0,
                    patch_id,
                ),
            )
        )
    return selected


def _read_audit_reviews(source_root: Path, wanted: set[str]) -> dict[str, dict[str, Any]]:
    path = source_root / "review_revisions.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Stage 1 review revisions are needed for full-list audit: {path}")
    reader = pq.ParquetFile(path)
    columns = [
        "review_revision_id",
        "recommendation_id",
        "created_at_utc",
        "updated_at_utc",
        "language",
        "review_text_original",
    ]
    found = {}
    for batch in reader.iter_batches(columns=columns, batch_size=8192):
        for row in batch.to_pylist():
            revision_id = row["review_revision_id"]
            if revision_id in wanted:
                found[revision_id] = row
        if len(found) == len(wanted):
            break
    return found


def _sample_languages(
    rows: list[dict[str, Any]], *, limit: int, seed: str, patch_id: str, segment: str
) -> list[dict[str, Any]]:
    strata: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        language = str(row.get("language") or "unknown").casefold()
        strata[language].append(row)
    for language, members in strata.items():
        members.sort(
            key=lambda row: _stable_order(
                seed, patch_id, segment, language, row["review_revision_id"]
            )
        )
    languages = sorted(strata, key=lambda lang: (-len(strata[lang]), lang))
    selected = []
    offset = 0
    while len(selected) < limit:
        progressed = False
        for language in languages:
            if offset < len(strata[language]):
                selected.append(strata[language][offset])
                progressed = True
                if len(selected) == limit:
                    break
        if not progressed:
            break
        offset += 1
    return selected


def _build_audit_jobs(
    *,
    selected_patch_ids: list[str],
    memberships_by_patch: dict[str, list[dict[str, Any]]],
    changes_by_patch: dict[str, list[dict[str, Any]]],
    episodes: dict[str, dict[str, Any]],
    windows_by_patch: dict[str, list[dict[str, Any]]],
    stage1_root: Path,
    seed: str,
    per_segment: int,
) -> list[dict[str, Any]]:
    patch_revisions: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    wanted = set()
    for patch_id in selected_patch_ids:
        for member in memberships_by_patch.get(patch_id, []):
            revision_id = member["review_revision_id"]
            segment = member.get("window_segment") or "unknown"
            patch_revisions[patch_id][segment].add(revision_id)
            wanted.add(revision_id)
    full_reviews = _read_audit_reviews(stage1_root, wanted)
    jobs = []
    for patch_id in selected_patch_ids:
        episode = episodes[patch_id]
        changes = sorted(
            changes_by_patch[patch_id],
            key=lambda row: (row.get("source_span_start") or 0, row["change_id"]),
        )
        windows = {row["segment"]: row for row in windows_by_patch.get(patch_id, [])}
        for segment in sorted(patch_revisions[patch_id]):
            candidates = [
                full_reviews[revision_id]
                for revision_id in patch_revisions[patch_id][segment]
                if revision_id in full_reviews
            ]
            chosen = _sample_languages(
                candidates,
                limit=per_segment,
                seed=seed,
                patch_id=patch_id,
                segment=segment,
            )
            for review in chosen:
                change_list = [
                    {
                        key: change.get(key)
                        for key in (
                            "change_id",
                            "change_text",
                            "source_span_raw",
                            "source_span_start",
                            "source_span_end",
                            "source_url",
                            "heading_path",
                            "entity",
                            "entity_candidates",
                            "aspect",
                            "action",
                            "direction",
                            "previous_value",
                            "new_value",
                            "developer_status",
                            "bug_symptom",
                            "bug_trigger",
                            "source_span_verified",
                        )
                    }
                    for change in changes
                ]
                prompt = (
                    "Given the complete Steam review and the complete numbered change list, "
                    "identify only changes the review actually discusses. Temporal proximity "
                    "is not evidence; a recommended review is not feature-level sentiment. "
                    "Return JSON with change_id, exact supporting review quote, rationale, "
                    "and uncertainty, or an empty matches list. Do not infer from generic "
                    "sentiment alone.\n\n"
                    f"Review:\n{review.get('review_text_original') or ''}\n\n"
                    "Complete patch change list:\n"
                    + "\n".join(
                        f"{index}. [{item['change_id']}] {item.get('heading_path') or []}: {item.get('change_text') or item.get('source_span_raw') or ''}"
                        for index, item in enumerate(change_list, 1)
                    )
                )
                window = windows.get(segment, {})
                jobs.append(
                    {
                        "audit_id": _stable_id(
                            "rv3_audit", patch_id, review["review_revision_id"], seed
                        ),
                        "selection_seed": seed,
                        "selection_rule": "hash-ranked sample stratified by patch, temporal segment, and review language; selected before retrieval",
                        "candidate_independent": True,
                        "patch_id": patch_id,
                        "game_id": episode["game_id"],
                        "game_name": episode["game_name"],
                        "patch_title": episode["title"],
                        "patch_source_url": episode.get("source_url"),
                        "patch_anchor_at_utc": episode.get("anchor_at_utc"),
                        "patch_anchor_source": episode.get("anchor_source"),
                        "window_segment": segment,
                        "window_collection_status": window.get("collection_status"),
                        "window_review_coverage_fraction": window.get("review_coverage_fraction"),
                        "review_revision_id": review["review_revision_id"],
                        "review_id": review.get("recommendation_id"),
                        "review_created_at_utc": review.get("created_at_utc"),
                        "review_updated_at_utc": review.get("updated_at_utc"),
                        "review_language": review.get("language"),
                        "review_text": review.get("review_text_original") or "",
                        "full_change_count": len(change_list),
                        "full_change_list": change_list,
                        "prompt": prompt,
                    }
                )
    return jobs


def _bm25_rank_key(change_id: str, claim_id: str) -> tuple[str, str]:
    return change_id, claim_id


def _candidate_row_base(
    *,
    dataset_id: str,
    source_dataset: str,
    episode: dict[str, Any],
    change: dict[str, Any],
    claim: dict[str, Any],
) -> dict[str, Any]:
    return {
        "candidate_id": _stable_id(
            "rv3_candidate",
            STAGE3_SCHEMA_VERSION,
            source_dataset,
            episode["patch_id"],
            change["change_id"],
            claim["claim_id"],
        ),
        "dataset_id": dataset_id,
        "source_stage2_dataset_id": source_dataset,
        "patch_id": episode["patch_id"],
        "game_id": episode["game_id"],
        "game_name": episode["game_name"],
        "patch_title": episode["title"],
        "patch_anchor_at_utc": episode.get("anchor_at_utc"),
        "patch_anchor_source": episode.get("anchor_source"),
        "change_id": change["change_id"],
        "change_text": change.get("change_text"),
        "change_entity": change.get("entity"),
        "change_aspect": change.get("aspect"),
        "change_direction": change.get("direction"),
        "change_source_url": change.get("source_url"),
        "claim_id": claim["claim_id"],
        "review_revision_id": claim["review_revision_id"],
        "review_id": claim["review_id"],
        "claim_text": claim.get("claim_text_original"),
        "claim_entity": claim.get("referenced_entity"),
        "claim_aspect": claim.get("aspect"),
        "claim_polarity": claim.get("polarity"),
        "review_language": claim.get("review_language"),
        "review_created_at_utc": claim.get("review_created_at_utc"),
        "window_segments": claim.get("window_segments") or [],
        "other_window_patch_ids": [],
        "competing_feature_patch_ids": [],
        "bm25_rank": None,
        "bm25_score": None,
        "dense_rank": None,
        "dense_cosine_score": None,
        "dense_model_version": None,
        "entity_aspect_rank": None,
        "entity_aspect_score": None,
        "entity_match_score": None,
        "aspect_match_score": None,
        "matched_entity": None,
        "rrf_score": 0.0,
        "fused_rank": None,
        "retrieval_methods": [],
        "at_maximum_budget": True,
    }


def _direction_conflict(direction: str | None, claim_text: str) -> bool:
    norm = normalize_term(direction)
    if norm in {"increase", "increased", "increasing", "up", "raised", "buff"}:
        key = "increase"
    elif norm in {"decrease", "decreased", "decreasing", "down", "reduced", "nerf"}:
        key = "decrease"
    else:
        return False
    return bool(DIRECTION_CUES[key].search(claim_text))


def _hard_case_types(
    change: dict[str, Any],
    claim: dict[str, Any],
    component: dict[str, Any],
    vocabulary: GameVocabulary,
    change_entities: set[str],
    claim_entities: set[str],
    other_patch_entity_index: dict[str, set[str]],
    claim_patch_ids: set[str],
) -> list[str]:
    types = []
    shared_entities = change_entities & claim_entities
    change_aspect = aspect_family(change.get("aspect"))
    claim_aspect = aspect_family(claim.get("aspect"))
    if shared_entities and change_aspect and claim_aspect and change_aspect != claim_aspect:
        types.append("same_entity_different_aspect")
    claim_text = str(claim.get("claim_text_original") or "")
    if (
        shared_entities
        and not (claim.get("temporal_cues") or [])
        and GENERIC_SYMPTOM_RE.search(claim_text)
    ):
        types.append("same_feature_generic_longstanding_complaint")
    trigger = str(change.get("bug_trigger") or "").strip()
    symptom = str(change.get("bug_symptom") or "").strip()
    if (
        trigger
        and symptom
        and symptom.casefold() in claim_text.casefold()
        and trigger.casefold() not in claim_text.casefold()
    ):
        types.append("same_issue_type_different_trigger")
    if shared_entities and claim_patch_ids:
        if any(
            patch_id != change.get("patch_id")
            and bool(other_patch_entity_index.get(patch_id, set()) & claim_entities)
            for patch_id in claim_patch_ids
        ):
            types.append("same_game_wrong_patch_or_overlap_candidate")
    if component.get("bm25_rank") and change_entities and claim_entities:
        claim_aliases = vocabulary.mentioned_aliases(claim_text)
        change_text = (
            str(change.get("change_text") or "") + " " + " ".join(change.get("heading_path") or [])
        )
        if claim_aliases & vocabulary.mentioned_aliases(change_text) and (
            not shared_entities
            or (change_aspect and claim_aspect and change_aspect != claim_aspect)
        ):
            types.append("same_terminology_different_mechanic")
    if _direction_conflict(change.get("direction"), claim_text):
        types.append("explicitly_contradictory_directional_cue")
    return sorted(set(types))


def _write_parquet(path: Path, rows: list[dict[str, Any]], schema: pa.Schema) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(rows, schema=schema)
    pq.write_table(table, path, compression="zstd", version="2.6")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        if columns:
            writer.writeheader()
            writer.writerows(rows)


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8"
    )


def _write_audit_jsonl(path: Path, jobs: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for job in jobs:
            handle.write(json.dumps(job, ensure_ascii=False, default=str) + "\n")


def _budget_rows(
    *,
    budgets: list[int],
    ranked: dict[tuple[str, str], dict[str, Any]],
    patch_by_change: dict[str, str],
    game_by_patch: dict[str, tuple[int, str]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for budget in budgets:
        totals: dict[str, Counter[str]] = defaultdict(Counter)
        for (change_id, claim_id), components in ranked.items():
            patch_id = patch_by_change[change_id]
            game_id, _ = game_by_patch[patch_id]
            method_pairs = {
                method
                for method in ("bm25", "dense", "entity_aspect")
                if components.get(f"{method}_rank") is not None
                and components[f"{method}_rank"] <= budget
            }
            if not method_pairs:
                continue
            scopes = [("overall", "all")] + [("game", str(game_id)), ("patch", patch_id)]
            for scope, scope_id in scopes:
                counter = totals[(scope, scope_id)]
                for method in method_pairs:
                    counter[method] += 1
                counter["union"] += 1
        scope_ids = (
            {("overall", "all")}
            | {("game", str(game_id)) for game_id, _ in game_by_patch.values()}
            | {("patch", patch_id) for patch_id in patch_by_change.values()}
        )
        for scope, scope_id in sorted(scope_ids):
            counts = totals[(scope, scope_id)]
            if scope == "game":
                game_name = next(
                    (name for game_id, name in game_by_patch.values() if str(game_id) == scope_id),
                    None,
                )
            elif scope == "patch":
                game_name = game_by_patch.get(scope_id, (None, None))[1]
            else:
                game_name = "all games"
            output.append(
                {
                    "scope": scope,
                    "scope_id": scope_id,
                    "game_name": game_name,
                    "budget_per_change_per_method": budget,
                    "bm25_pairs": counts["bm25"],
                    "dense_pairs": counts["dense"],
                    "entity_aspect_pairs": counts["entity_aspect"],
                    "hybrid_union_pairs": counts["union"],
                    "reference_recall": None,
                    "interpretation": "candidate yield only; no relevance labels/reference set",
                }
            )
    return output


def _render_report(
    *,
    dataset_id: str,
    manifest: dict[str, Any],
    patch_diagnostics: list[dict[str, Any]],
    budget_rows: list[dict[str, Any]],
    examples: list[dict[str, Any]],
) -> str:
    counts = manifest["counts"]
    lines = [
        f"# Stage 3 candidate retrieval — `{dataset_id}`",
        "",
        f"Source Stage 2 dataset: `{manifest['source_stage2_dataset_id']}`. No relevance labels or training labels were generated.",
        "",
        "## Run scope",
        "",
        f"- Change-bearing episodes with review-window membership: {counts['retrieved_patch_episodes']:,} across {counts['retrieved_games']:,} games.",
        f"- Verified atomic changes used: {counts['verified_changes_used']:,}; unverified change rows excluded: {counts['unverified_changes_excluded']:,}.",
        f"- Eligible claims after temporal/game filtering: {counts['eligible_change_claim_contexts']:,} patch-scoped claims.",
        f"- Distinct `(patch, change, claim)` candidates in the high-budget union: {counts['candidate_pairs']:,}.",
        f"- Hard-case candidate rows, all unlabelled: {counts['hard_candidate_rows']:,}.",
        f"- Candidate-free full-list audit packets: {counts['audit_packets']:,} from {counts['audit_patch_episodes']:,} episodes.",
        "",
        "## Method comparison",
        "",
        "Each method ranks claims independently per atomic change. BM25 removes generic sentiment-only terms and retains entities/numbers; dense uses multilingual E5 cosine similarity when enabled; entity/aspect uses game-scoped aliases and normalized aspect families. The union is fused with reciprocal-rank fusion (`k=60`).",
        "",
        "| Method | Ranked pairs at maximum budget | Pair rows absent from BM25 |",
        "| --- | ---: | ---: |",
        f"| BM25 | {counts['bm25_ranked_pairs']:,} | — |",
        f"| Dense | {counts['dense_ranked_pairs']:,} | {counts['dense_only_pairs']:,} |",
        f"| Entity/aspect | {counts['entity_aspect_ranked_pairs']:,} | {counts['entity_aspect_only_pairs']:,} |",
        f"| Hybrid union | {counts['candidate_pairs']:,} | {counts['hybrid_only_pairs']:,} |",
        "",
        f"Dense retrieval status: `{manifest['dense']['status']}` (model `{manifest['dense']['model_version']}`). A zero dense candidate count means no dense output was produced when the backend is disabled; it does not mean dense retrieved no candidates.",
        "",
        "`Pair rows absent from BM25` means the method contributed a candidate BM25 did not rank inside its configured budget. It does not establish relevance. `budget_curves.csv` reports candidate yield and overlap at every configured budget; recall is intentionally blank because no independent relevance reference labels exist.",
        "",
        "## Retrieval budget and truncation",
        "",
        f"Budgets per change per method: `{manifest['config']['budgets']}`. The candidate dataset retains the union through `{manifest['config']['maximum_budget']}`. There is no per-review cap. At the maximum budget, the output records {counts['bm25_queries_truncated']:,} BM25, {counts['dense_queries_truncated']:,} dense, and {counts['entity_aspect_queries_truncated']:,} entity/aspect change queries with ranked results beyond the retained list.",
        f"At the maximum budget, the ranked lists omit {counts['bm25_pairs_omitted_by_budget']:,} BM25 hits, {counts['dense_pairs_omitted_by_budget']:,} dense-ranked claim pairs, and {counts['entity_aspect_pairs_omitted_by_budget']:,} entity/aspect hits beyond the retained top ranks. Across the eligible contexts, exhaustive change×claim comparison would contain {counts['possible_change_claim_pairs']:,} pairs; the high-budget union retains {counts['candidate_pairs']:,}. This is measurable budget truncation, but without audit judgments it is not evidence that any omitted pair is relevant. The independent full-list audit packets expose the complete change list to later reviewers so omissions can be found without conditioning on retrieval.",
        "",
        "## Patch diagnostics",
        "",
        "| Game | Patch | Changes | Eligible claims | Possible pairs | BM25 | Dense | Entity/aspect | Union |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    patch_section_index = lines.index("## Patch diagnostics")
    overall_budget_rows = [row for row in budget_rows if row["scope"] == "overall"]
    hard_case_labels = {
        "same_entity_different_aspect": "Same entity, different aspect",
        "same_feature_generic_longstanding_complaint": "Same feature, generic/longstanding complaint",
        "same_issue_type_different_trigger": "Same issue type, different trigger",
        "same_game_wrong_patch_or_overlap_candidate": "Same game, competing patch/overlap",
        "same_terminology_different_mechanic": "Same terminology, different mechanic",
        "explicitly_contradictory_directional_cue": "Contradictory directional cue",
    }
    inserted_lines = [
        "## Budget curve",
        "",
        "Overall candidate yield as the per-change, per-method budget grows. This is not a recall curve because no verified relevance reference set exists.",
        "",
        "| Budget per change/method | BM25 pairs | Dense pairs | Entity/aspect pairs | Hybrid union |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    inserted_lines.extend(
        f"| {row['budget_per_change_per_method']} | {row['bm25_pairs']:,} | {row['dense_pairs']:,} | {row['entity_aspect_pairs']:,} | {row['hybrid_union_pairs']:,} |"
        for row in overall_budget_rows
    )
    inserted_lines.extend(
        [
            "",
            "## Hard-case candidate pool",
            "",
            "These are heuristic confounders for later verification. Categories can overlap, and none is a negative label.",
            "",
            "| Potential confounder | Candidate rows |",
            "| --- | ---: |",
        ]
    )
    inserted_lines.extend(
        f"| {hard_case_labels[case_type]} | {manifest['hard_case_counts'].get(case_type, 0):,} |"
        for case_type in HARD_CASE_TYPES
    )
    inserted_lines.append("")
    lines[patch_section_index:patch_section_index] = inserted_lines
    for row in patch_diagnostics:
        if row["retrieval_status"] != "retrieval available":
            continue
        lines.append(
            f"| {row['game_name']} | {row['patch_title']} (`{row['patch_id']}`) | {row['atomic_change_count']:,} | {row['eligible_review_claim_count']:,} | {row['possible_change_claim_pairs']:,} | {row['bm25_ranked_pairs']:,} | {row['dense_ranked_pairs']:,} | {row['entity_aspect_ranked_pairs']:,} | {row['hybrid_union_pairs']:,} |"
        )
    lines.extend(
        [
            "",
            "## Diagnostic candidate examples",
            "",
            "These examples are unique to a method among the three retained ranked lists. They illustrate retrieval differences and are not verified positives.",
            "",
        ]
    )
    for method in ("bm25", "dense", "entity_aspect"):
        method_examples = examples.get(method, [])
        if not method_examples:
            lines.extend(
                [
                    f"### {method} unique candidates",
                    "",
                    "No method-unique examples were produced in this run.",
                    "",
                ]
            )
            continue
        score_name, rank_name, score_field, rank_field = {
            "bm25": ("BM25 score", "BM25 rank", "bm25_score", "bm25_rank"),
            "dense": ("cosine", "dense rank", "dense_cosine_score", "dense_rank"),
            "entity_aspect": (
                "entity/aspect score",
                "entity/aspect rank",
                "entity_aspect_score",
                "entity_aspect_rank",
            ),
        }[method]
        for index, row in enumerate(method_examples[:3], 1):
            lines.extend(
                [
                    f"### {method} unique candidate — example {index}",
                    "",
                    f"Game/patch: {row['game_name']} — {row['patch_title']} (`{row['patch_id']}`). {rank_name} {row[rank_field]}, {score_name} {row[score_field]:.4f}; absent from the other method lists at the configured budget.",
                    "",
                    f"Change: {row['change_text']}",
                    "",
                    f"Review claim: {row['claim_text']}",
                    "",
                    "This is a retrieval diagnostic, not a relevance judgment.",
                    "",
                ]
            )
    lines.extend(
        [
            "## Independent full-list audit",
            "",
            f"The reproducible candidate-free sampler selected up to {manifest['config']['audit_per_segment']} full reviews per temporal segment from one change-bearing episode per game. It exports the original full review beside the complete structured patch change list in `audit_full_list.jsonl`. Sampling occurs from Stage 2 review-window memberships before ranking; audit rows contain no candidate IDs, component ranks, or labels. This is a diagnostic sample, not a corpus-wide recall estimate.",
            "",
            "The current Stage 2 snapshot has no extracted atomic changes for No Man’s Sky, so it cannot contribute a full-list audit episode. Its source/patch availability remains in Stage 2 coverage; candidate retrieval is blocked by the absence of atomic changes, not by a zero-relevance finding.",
            "",
            "## Data limitations",
            "",
            "- Stage 2 patch-window collection is incomplete for many episodes. Retrieval uses the rows available and carries per-window completeness in diagnostics and audit packets.",
            "- Stage 2 entity/aspect extraction is sparse and English-heavy. Dense multilingual retrieval and lexical retrieval are independent candidates, not claims that the extractor found every entity.",
            "- BM25 tokenization is simple Unicode word tokenization; languages without whitespace token boundaries may receive weaker lexical retrieval.",
            "- Similarity scores/ranks express candidate order only. Steam Recommended votes and claim polarity are not feature-level sentiment labels.",
            "",
            "## Outputs",
            "",
            "- `candidate_pairs.parquet`: high-budget per-change method union, component ranks/scores, RRF rank, temporal provenance.",
            "- `hard_negative_candidates.parquet`: heuristic confounders retained as unlabelled candidates for later verification.",
            "- `budget_curves.csv`, `patch_diagnostics.parquet`, `game_diagnostics.csv`, `diagnostics.json`.",
            "- `audit_full_list.jsonl`: independent, candidate-free full-review/full-change packets.",
            "- `manifest.json`: source hashes, configuration, model/cache version, counts, and truncation.",
            "",
        ]
    )
    return "\n".join(lines)


def run_stage3(
    *,
    repo_root: Path,
    source_dataset: str = DEFAULT_SOURCE_DATASET,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    report_root: Path = DEFAULT_REPORT_ROOT,
    budgets: list[int] | None = None,
    before_days: int = 14,
    after_days: int = 14,
    rrf_k: int = RRF_K,
    dense: bool = True,
    dense_model: str = DEFAULT_DENSE_MODEL,
    dense_revision: str = DEFAULT_DENSE_REVISION,
    dense_batch_size: int = 64,
    audit_per_segment: int = 5,
    audit_seed: str = DEFAULT_AUDIT_SEED,
    patch_ids: list[str] | None = None,
    game_ids: list[int] | None = None,
) -> dict[str, Any]:
    """Run independent signal retrieval and write versioned Stage 3 artifacts."""
    budgets = sorted(set(budgets or [10, 25, 50, 100]))
    if not budgets or budgets[0] < 1 or before_days < 0 or after_days < 0:
        raise ValueError("budgets must be positive; temporal window sizes cannot be negative")
    if rrf_k < 1 or dense_batch_size < 1 or audit_per_segment < 1:
        raise ValueError("RRF k, dense batch size, and audit-per-segment must be positive")
    maximum_budget = max(budgets)
    inputs = _load_stage2_inputs(repo_root, source_dataset)
    changes_all = inputs["patch_changes"]
    episodes_all = inputs["patch_episodes"]
    episode_by_id = {row["patch_id"]: row for row in episodes_all}
    windows_by_patch: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in inputs["patch_review_windows"]:
        windows_by_patch[row["patch_id"]].append(row)
    selected_patch_ids = set(patch_ids or []) or None
    selected_game_ids = set(game_ids or []) or None
    memberships_by_patch = _windowed_memberships(
        inputs["review_window_memberships"],
        before_days=before_days,
        after_days=after_days,
        selected_patch_ids=selected_patch_ids,
        selected_game_ids=selected_game_ids,
    )
    verified_changes_by_patch: dict[str, list[dict[str, Any]]] = defaultdict(list)
    all_changes_by_patch: dict[str, list[dict[str, Any]]] = defaultdict(list)
    all_change_count_by_patch: Counter[str] = Counter()
    unverified_changes = 0
    for change in changes_all:
        all_change_count_by_patch[change["patch_id"]] += 1
        all_changes_by_patch[change["patch_id"]].append(change)
        if change.get("source_span_verified") is True:
            verified_changes_by_patch[change["patch_id"]].append(change)
        else:
            unverified_changes += 1
    changes_by_patch = {
        patch_id: rows
        for patch_id, rows in verified_changes_by_patch.items()
        if memberships_by_patch.get(patch_id) and patch_id in episode_by_id
    }
    changes_by_patch = {
        patch_id: rows
        for patch_id, rows in changes_by_patch.items()
        if (not selected_game_ids or episode_by_id[patch_id]["game_id"] in selected_game_ids)
    }
    memberships_by_patch = {
        patch_id: rows
        for patch_id, rows in memberships_by_patch.items()
        if patch_id in episode_by_id
        and (not selected_game_ids or episode_by_id[patch_id]["game_id"] in selected_game_ids)
    }
    claims_by_patch, claim_patch_segments = _join_patch_claims(
        memberships_by_patch, inputs["review_claims"]
    )
    claim_patch_ids_by_claim: dict[str, set[str]] = defaultdict(set)
    for (claim_id, patch_id), segments in claim_patch_segments.items():
        if segments:
            claim_patch_ids_by_claim[claim_id].add(patch_id)
    changes_by_patch = {
        patch_id: rows
        for patch_id, rows in changes_by_patch.items()
        if claims_by_patch.get(patch_id)
    }
    eligible_patch_ids = sorted(changes_by_patch)
    if not eligible_patch_ids:
        raise ValueError("No Stage 2 patch episodes have verified changes and time-windowed claims")
    episodes = {patch_id: episode_by_id[patch_id] for patch_id in eligible_patch_ids}

    audit_patch_ids = _select_audit_patches(changes_by_patch, memberships_by_patch, episodes)
    audit_jobs = _build_audit_jobs(
        selected_patch_ids=audit_patch_ids,
        memberships_by_patch=memberships_by_patch,
        changes_by_patch={patch_id: all_changes_by_patch[patch_id] for patch_id in audit_patch_ids},
        episodes=episodes,
        windows_by_patch=windows_by_patch,
        stage1_root=inputs["stage1_root"],
        seed=audit_seed,
        per_segment=audit_per_segment,
    )

    encoder = None
    model_version = "disabled"
    if dense:
        encoder = SentenceTransformerEncoder(dense_model, dense_revision)
        model_version = encoder.model_version
    config = {
        "source_stage2_dataset_id": source_dataset,
        "budgets": budgets,
        "maximum_budget": maximum_budget,
        "before_days": before_days,
        "after_days": after_days,
        "rrf_k": rrf_k,
        "dense_enabled": dense,
        "dense_model": dense_model if dense else None,
        "dense_revision": model_version if dense else None,
        "dense_batch_size": dense_batch_size if dense else None,
        "audit_seed": audit_seed,
        "audit_per_segment": audit_per_segment,
        "selected_patch_ids": sorted(patch_ids or []),
        "selected_game_ids": sorted(game_ids or []),
    }
    dataset_payload = json.dumps(
        {"schema": STAGE3_SCHEMA_VERSION, "retriever": RETRIEVER_VERSION, "config": config},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    dataset_id = f"rv3-{_sha256_bytes(dataset_payload)[:24]}"

    vocab_by_game: dict[int, GameVocabulary] = {}
    terminology_by_game: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in inputs["game_terminology"]:
        terminology_by_game[int(row["game_id"])].append(row)
    for game_id, rows in terminology_by_game.items():
        vocab_by_game[game_id] = GameVocabulary(rows)

    claim_text_by_id = {
        claim["claim_id"]: claim_document_text(claim)
        for patch_id in eligible_patch_ids
        for claim in claims_by_patch[patch_id]
    }
    claim_by_id = {
        claim["claim_id"]: claim
        for patch_id in eligible_patch_ids
        for claim in claims_by_patch[patch_id]
    }
    change_by_id = {
        change["change_id"]: change
        for patch_id in eligible_patch_ids
        for change in changes_by_patch[patch_id]
    }
    dense_claim_vectors: dict[str, np.ndarray] = {}
    dense_change_vectors: dict[str, np.ndarray] = {}
    if encoder is not None:
        cache = EmbeddingCache(repo_root / output_root / "cache", encoder)
        dense_claim_vectors = cache.encode_documents(
            claim_text_by_id, role="passage", batch_size=dense_batch_size
        )
        dense_change_vectors = cache.encode_documents(
            {change_id: change_query_text(row) for change_id, row in change_by_id.items()},
            role="query",
            batch_size=dense_batch_size,
        )

    ranked: dict[tuple[str, str], dict[str, Any]] = {}
    patch_rank_stats: dict[str, dict[str, Any]] = {}
    patch_by_change: dict[str, str] = {}
    game_by_patch = {
        patch_id: (int(episode["game_id"]), str(episode["game_name"]))
        for patch_id, episode in episodes.items()
    }
    change_entities: dict[str, set[str]] = {}
    claim_entities: dict[str, set[str]] = {}
    patch_entity_index: dict[str, set[str]] = {}
    patch_aspect_index: dict[str, set[str]] = {}

    for patch_id in eligible_patch_ids:
        episode = episodes[patch_id]
        game_id = int(episode["game_id"])
        vocabulary = vocab_by_game.get(game_id, GameVocabulary([]))
        changes = sorted(changes_by_patch[patch_id], key=lambda row: row["change_id"])
        claims = sorted(claims_by_patch[patch_id], key=lambda row: row["claim_id"])
        claim_ids = [row["claim_id"] for row in claims]
        claim_texts = [(row["claim_id"], claim_text_by_id[row["claim_id"]]) for row in claims]
        bm25_index = BM25Index(claim_texts)
        claim_entities_for_patch = {
            row["claim_id"]: vocabulary.entity_set(row, change=False) for row in claims
        }
        claim_entities.update(claim_entities_for_patch)
        for change in changes:
            change_id = change["change_id"]
            patch_by_change[change_id] = patch_id
            change_entities[change_id] = vocabulary.entity_set(change, change=True)
            patch_entity_index.setdefault(patch_id, set()).update(change_entities[change_id])
            family = aspect_family(change.get("aspect"))
            if family:
                patch_aspect_index.setdefault(patch_id, set()).add(family)
        patch_rank_stats[patch_id] = {
            "bm25_truncated": 0,
            "dense_truncated": 0,
            "entity_truncated": 0,
            "bm25_omitted": 0,
            "dense_omitted": 0,
            "entity_omitted": 0,
            "bm25_pairs": 0,
            "dense_pairs": 0,
            "entity_pairs": 0,
            "possible_pairs": len(changes) * len(claims),
        }
        claim_vectors = (
            np.stack([dense_claim_vectors[claim_id] for claim_id in claim_ids])
            if encoder is not None and claim_ids
            else np.empty((0, 0), dtype=np.float32)
        )
        for change in changes:
            change_id = change["change_id"]
            bm25_hits_all = bm25_index.rank(change_query_text(change), limit=None)
            if len(bm25_hits_all) > maximum_budget:
                patch_rank_stats[patch_id]["bm25_truncated"] += 1
                patch_rank_stats[patch_id]["bm25_omitted"] += len(bm25_hits_all) - maximum_budget
            bm25_hits = bm25_hits_all[:maximum_budget]
            for hit in bm25_hits:
                pair = _bm25_rank_key(change_id, hit.item_id)
                ranked.setdefault(pair, {})["bm25_rank"] = hit.rank
                ranked[pair]["bm25_score"] = hit.score
                patch_rank_stats[patch_id]["bm25_pairs"] += 1

            entity_hits = rank_entity_aspect(
                change,
                claims,
                vocabulary,
                limit=None,
                change_entities=change_entities[change_id],
                claim_entities_by_id=claim_entities_for_patch,
            )
            if len(entity_hits) > maximum_budget:
                patch_rank_stats[patch_id]["entity_truncated"] += 1
                patch_rank_stats[patch_id]["entity_omitted"] += len(entity_hits) - maximum_budget
            entity_hits = entity_hits[:maximum_budget]
            for hit, entity_score, aspect_score, matched_entity in entity_hits:
                pair = (change_id, hit.item_id)
                ranked.setdefault(pair, {})["entity_aspect_rank"] = hit.rank
                ranked[pair]["entity_aspect_score"] = hit.score
                ranked[pair]["entity_match_score"] = entity_score
                ranked[pair]["aspect_match_score"] = aspect_score
                ranked[pair]["matched_entity"] = matched_entity
                patch_rank_stats[patch_id]["entity_pairs"] += 1

            if encoder is not None:
                dense_hits = top_cosine_hits(
                    dense_change_vectors[change_id], claim_vectors, claim_ids, limit=maximum_budget
                )
                if len(dense_hits) == maximum_budget and len(claims) > maximum_budget:
                    patch_rank_stats[patch_id]["dense_truncated"] += 1
                    patch_rank_stats[patch_id]["dense_omitted"] += len(claims) - maximum_budget
                for rank, (claim_id, score) in enumerate(dense_hits, 1):
                    pair = (change_id, claim_id)
                    ranked.setdefault(pair, {})["dense_rank"] = rank
                    ranked[pair]["dense_cosine_score"] = score
                    ranked[pair]["dense_model_version"] = model_version
                    patch_rank_stats[patch_id]["dense_pairs"] += 1

    # RRF is applied only after preserving each method's independent ranking.
    by_change: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for (change_id, claim_id), components in ranked.items():
        rrf_score = sum(
            1.0 / (rrf_k + components[f"{method}_rank"])
            for method in ("bm25", "dense", "entity_aspect")
            if components.get(f"{method}_rank") is not None
        )
        components["rrf_score"] = rrf_score
        by_change[change_id].append((claim_id, components))
    for change_id, pairs in by_change.items():
        pairs.sort(key=lambda row: (-row[1]["rrf_score"], row[0]))
        for rank, (_, components) in enumerate(pairs, 1):
            components["fused_rank"] = rank

    candidate_rows = []
    candidate_by_id: dict[str, dict[str, Any]] = {}
    pair_keys_by_patch: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for (change_id, claim_id), components in ranked.items():
        patch_id = patch_by_change[change_id]
        episode = episodes[patch_id]
        row = _candidate_row_base(
            dataset_id=dataset_id,
            source_dataset=source_dataset,
            episode=episode,
            change=change_by_id[change_id],
            claim=claim_by_id[claim_id],
        )
        row.update(components)
        other_patch_ids = sorted(
            patch for patch in claim_patch_ids_by_claim.get(claim_id, set()) if patch != patch_id
        )
        row["other_window_patch_ids"] = other_patch_ids
        change_entity_set = change_entities.get(change_id, set())
        change_aspect_family = aspect_family(change_by_id[change_id].get("aspect"))
        row["competing_feature_patch_ids"] = [
            other_patch
            for other_patch in other_patch_ids
            if episodes.get(other_patch, {}).get("game_id") == episode.get("game_id")
            and (
                bool(change_entity_set & patch_entity_index.get(other_patch, set()))
                or bool(
                    change_aspect_family
                    and change_aspect_family in patch_aspect_index.get(other_patch, set())
                )
            )
        ]
        row["retrieval_methods"] = [
            method
            for method in ("bm25", "dense", "entity_aspect")
            if components.get(f"{method}_rank") is not None
        ]
        candidate_rows.append(row)
        candidate_by_id[(change_id, claim_id)] = row
        pair_keys_by_patch[patch_id].add((change_id, claim_id))
    candidate_rows.sort(
        key=lambda row: (row["patch_id"], row["change_id"], row["fused_rank"], row["claim_id"])
    )

    patch_diagnostics = []
    window_status_by_patch: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in inputs["patch_review_windows"]:
        window_status_by_patch[row["patch_id"]].append(row)
    for patch_id in eligible_patch_ids:
        episode = episodes[patch_id]
        changes = changes_by_patch[patch_id]
        claims = claims_by_patch[patch_id]
        stats = patch_rank_stats[patch_id]
        win_rows = window_status_by_patch.get(patch_id, [])
        patch_diagnostics.append(
            {
                "patch_id": patch_id,
                "retrieval_status": "retrieval available",
                "game_id": episode["game_id"],
                "game_name": episode["game_name"],
                "patch_title": episode["title"],
                "anchor_at_utc": episode.get("anchor_at_utc"),
                "atomic_change_count": len(changes),
                "stage2_change_count": all_change_count_by_patch[patch_id],
                "temporal_membership_count": len(memberships_by_patch.get(patch_id, [])),
                "source_span_unverified_changes_excluded": all_change_count_by_patch[patch_id]
                - len(verified_changes_by_patch.get(patch_id, [])),
                "eligible_review_claim_count": len(claims),
                "eligible_review_revision_count": len(
                    {row["review_revision_id"] for row in claims}
                ),
                "window_segment_count": len(
                    {row.get("window_segment") for row in memberships_by_patch.get(patch_id, [])}
                ),
                "incomplete_window_segment_count": sum(
                    row.get("collection_status") != "complete"
                    for row in win_rows
                    if row.get("segment")
                    in {
                        member.get("window_segment")
                        for member in memberships_by_patch.get(patch_id, [])
                    }
                ),
                "possible_change_claim_pairs": stats["possible_pairs"],
                "bm25_ranked_pairs": stats["bm25_pairs"],
                "dense_ranked_pairs": stats["dense_pairs"],
                "entity_aspect_ranked_pairs": stats["entity_pairs"],
                "hybrid_union_pairs": len(pair_keys_by_patch[patch_id]),
                "bm25_queries_truncated": stats["bm25_truncated"],
                "dense_queries_truncated": stats["dense_truncated"],
                "entity_queries_truncated": stats["entity_truncated"],
                "bm25_pairs_omitted_by_budget": stats["bm25_omitted"],
                "dense_pairs_omitted_by_budget": stats["dense_omitted"],
                "entity_pairs_omitted_by_budget": stats["entity_omitted"],
                "candidate_pair_count": len(pair_keys_by_patch[patch_id]),
            }
        )
    diagnostic_patch_ids = {row["patch_id"] for row in patch_diagnostics}
    for episode in episodes_all:
        patch_id = episode["patch_id"]
        if patch_id in diagnostic_patch_ids:
            continue
        stage2_change_count = all_change_count_by_patch[patch_id]
        member_rows = memberships_by_patch.get(patch_id, [])
        if selected_patch_ids and patch_id not in selected_patch_ids:
            status = "outside_selected_patch_scope"
        elif selected_game_ids and episode["game_id"] not in selected_game_ids:
            status = "outside_selected_game_scope"
        elif not verified_changes_by_patch.get(patch_id):
            status = "no_verified_atomic_changes"
        elif not member_rows:
            status = "no_memberships_in_configured_window"
        else:
            status = "no_joinable_review_claims"
        rows = window_status_by_patch.get(patch_id, [])
        active_segments = {row.get("window_segment") for row in member_rows}
        patch_diagnostics.append(
            {
                "patch_id": patch_id,
                "retrieval_status": status,
                "game_id": episode["game_id"],
                "game_name": episode["game_name"],
                "patch_title": episode["title"],
                "anchor_at_utc": episode.get("anchor_at_utc"),
                "atomic_change_count": 0,
                "stage2_change_count": stage2_change_count,
                "temporal_membership_count": len(member_rows),
                "source_span_unverified_changes_excluded": stage2_change_count
                - len(verified_changes_by_patch.get(patch_id, [])),
                "eligible_review_claim_count": 0,
                "eligible_review_revision_count": 0,
                "window_segment_count": len(active_segments),
                "incomplete_window_segment_count": sum(
                    row.get("collection_status") != "complete"
                    for row in rows
                    if row.get("segment") in active_segments
                ),
                "possible_change_claim_pairs": 0,
                "bm25_ranked_pairs": 0,
                "dense_ranked_pairs": 0,
                "entity_aspect_ranked_pairs": 0,
                "hybrid_union_pairs": 0,
                "bm25_queries_truncated": 0,
                "dense_queries_truncated": 0,
                "entity_queries_truncated": 0,
                "bm25_pairs_omitted_by_budget": 0,
                "dense_pairs_omitted_by_budget": 0,
                "entity_pairs_omitted_by_budget": 0,
                "candidate_pair_count": 0,
            }
        )
    patch_diagnostics.sort(
        key=lambda row: (row["game_name"], row["anchor_at_utc"] or datetime.min.replace(tzinfo=UTC))
    )

    other_patch_entity_index: dict[str, set[str]] = {
        patch_id: patch_entity_index.get(patch_id, set()) for patch_id in eligible_patch_ids
    }
    hard_rows = []
    hard_case_counts: Counter[str] = Counter({case_type: 0 for case_type in HARD_CASE_TYPES})
    for row in candidate_rows:
        pair = (row["change_id"], row["claim_id"])
        change = change_by_id[row["change_id"]]
        claim = claim_by_id[row["claim_id"]]
        patch_id = row["patch_id"]
        vocabulary = vocab_by_game[int(row["game_id"])]
        types = _hard_case_types(
            change,
            claim,
            ranked[pair],
            vocabulary,
            change_entities[row["change_id"]],
            claim_entities.get(row["claim_id"], set()),
            other_patch_entity_index,
            claim_patch_ids_by_claim.get(row["claim_id"], set()),
        )
        if types:
            hard_case_counts.update(types)
            hard = dict(row)
            hard["hard_case_types"] = types
            hard["hard_case_basis"] = (
                "heuristic confounder; candidate remains unlabelled and requires later verification"
            )
            hard_rows.append(hard)

    patch_by_change_id = {
        change["change_id"]: patch_id
        for patch_id, rows in changes_by_patch.items()
        for change in rows
    }
    budget_rows = _budget_rows(
        budgets=budgets,
        ranked=ranked,
        patch_by_change=patch_by_change_id,
        game_by_patch=game_by_patch,
    )
    game_diagnostics: dict[int, dict[str, Any]] = {}
    for episode in episodes_all:
        game_id = int(episode["game_id"])
        summary = game_diagnostics.setdefault(
            game_id,
            {
                "game_id": game_id,
                "game_name": episode["game_name"],
                "stage2_patch_episodes": 0,
                "episodes_with_window_memberships": 0,
                "episodes_with_verified_changes": 0,
                "retrieval_episodes": 0,
                "atomic_changes": 0,
                "eligible_review_claims_patch_scoped": 0,
                "possible_change_claim_pairs": 0,
                "candidate_pairs": 0,
                "bm25_ranked_pairs": 0,
                "dense_ranked_pairs": 0,
                "entity_aspect_ranked_pairs": 0,
                "incomplete_window_segments": 0,
                "retrieval_status": "no verified changes or no temporal memberships",
            },
        )
        summary["stage2_patch_episodes"] += 1
        if memberships_by_patch.get(episode["patch_id"]):
            summary["episodes_with_window_memberships"] += 1
        if verified_changes_by_patch.get(episode["patch_id"]):
            summary["episodes_with_verified_changes"] += 1
    for patch_row in patch_diagnostics:
        if patch_row["retrieval_status"] != "retrieval available":
            continue
        summary = game_diagnostics[int(patch_row["game_id"])]
        summary["retrieval_episodes"] += 1
        summary["atomic_changes"] += patch_row["atomic_change_count"]
        summary["eligible_review_claims_patch_scoped"] += patch_row["eligible_review_claim_count"]
        summary["possible_change_claim_pairs"] += patch_row["possible_change_claim_pairs"]
        summary["candidate_pairs"] += patch_row["candidate_pair_count"]
        summary["bm25_ranked_pairs"] += patch_row["bm25_ranked_pairs"]
        summary["dense_ranked_pairs"] += patch_row["dense_ranked_pairs"]
        summary["entity_aspect_ranked_pairs"] += patch_row["entity_aspect_ranked_pairs"]
        summary["incomplete_window_segments"] += patch_row["incomplete_window_segment_count"]
        summary["retrieval_status"] = "retrieval available"

    bm25_pairs = {
        pair for pair, components in ranked.items() if components.get("bm25_rank") is not None
    }
    dense_pairs = {
        pair for pair, components in ranked.items() if components.get("dense_rank") is not None
    }
    entity_pairs = {
        pair
        for pair, components in ranked.items()
        if components.get("entity_aspect_rank") is not None
    }
    method_sets = {"bm25": bm25_pairs, "dense": dense_pairs, "entity_aspect": entity_pairs}
    method_examples: dict[str, list[dict[str, Any]]] = {}
    for method, own_pairs in method_sets.items():
        other_pairs = set().union(
            *(pairs for other, pairs in method_sets.items() if other != method)
        )
        unique_pairs = own_pairs - other_pairs
        score_field = {
            "bm25": "bm25_score",
            "dense": "dense_cosine_score",
            "entity_aspect": "entity_aspect_score",
        }[method]
        rank_field = {
            "bm25": "bm25_rank",
            "dense": "dense_rank",
            "entity_aspect": "entity_aspect_rank",
        }[method]
        ordered_pairs = sorted(
            unique_pairs,
            key=lambda pair: (-ranked[pair][score_field], ranked[pair][rank_field], pair),
        )[:10]
        method_examples[method] = []
        for pair in ordered_pairs:
            row = candidate_by_id[pair]
            method_examples[method].append(
                {
                    "game_name": row["game_name"],
                    "patch_id": row["patch_id"],
                    "patch_title": row["patch_title"],
                    "change_id": row["change_id"],
                    "claim_id": row["claim_id"],
                    "change_text": row["change_text"],
                    "claim_text": row["claim_text"],
                    "bm25_rank": row["bm25_rank"],
                    "bm25_score": row["bm25_score"],
                    "dense_rank": row["dense_rank"],
                    "dense_cosine_score": row["dense_cosine_score"],
                    "entity_aspect_rank": row["entity_aspect_rank"],
                    "entity_aspect_score": row["entity_aspect_score"],
                }
            )

    candidate_ids = {(row["change_id"], row["claim_id"]) for row in candidate_rows}
    possible_pairs = sum(row["possible_change_claim_pairs"] for row in patch_diagnostics)
    audit_patch_total = len(audit_patch_ids)
    counts = {
        "retrieved_patch_episodes": len(eligible_patch_ids),
        "retrieved_games": len({episodes[patch_id]["game_id"] for patch_id in eligible_patch_ids}),
        "all_stage2_patch_episodes": len(episodes_all),
        "all_stage2_patch_episodes_with_configured_window_memberships": len(memberships_by_patch),
        "all_stage2_episodes_with_any_verified_changes": sum(
            bool(rows) for rows in verified_changes_by_patch.values()
        ),
        "verified_changes_used": sum(len(rows) for rows in changes_by_patch.values()),
        "unverified_changes_excluded": unverified_changes,
        "eligible_change_claim_contexts": sum(
            len(claims_by_patch[patch_id]) for patch_id in eligible_patch_ids
        ),
        "possible_change_claim_pairs": possible_pairs,
        "candidate_pairs": len(candidate_rows),
        "bm25_ranked_pairs": len(bm25_pairs),
        "dense_ranked_pairs": len(dense_pairs),
        "entity_aspect_ranked_pairs": len(entity_pairs),
        "dense_only_pairs": len(dense_pairs - bm25_pairs),
        "entity_aspect_only_pairs": len(entity_pairs - bm25_pairs),
        "hybrid_only_pairs": len(candidate_ids - bm25_pairs),
        "bm25_unique_pairs": len(bm25_pairs - dense_pairs - entity_pairs),
        "dense_unique_pairs": len(dense_pairs - bm25_pairs - entity_pairs),
        "entity_aspect_unique_pairs": len(entity_pairs - bm25_pairs - dense_pairs),
        "hard_candidate_rows": len(hard_rows),
        "audit_packets": len(audit_jobs),
        "audit_patch_episodes": audit_patch_total,
        "bm25_queries_truncated": sum(row["bm25_queries_truncated"] for row in patch_diagnostics),
        "dense_queries_truncated": sum(row["dense_queries_truncated"] for row in patch_diagnostics),
        "entity_aspect_queries_truncated": sum(
            row["entity_queries_truncated"] for row in patch_diagnostics
        ),
        "bm25_pairs_omitted_by_budget": sum(
            row["bm25_pairs_omitted_by_budget"] for row in patch_diagnostics
        ),
        "dense_pairs_omitted_by_budget": sum(
            row["dense_pairs_omitted_by_budget"] for row in patch_diagnostics
        ),
        "entity_aspect_pairs_omitted_by_budget": sum(
            row["entity_pairs_omitted_by_budget"] for row in patch_diagnostics
        ),
    }
    games_with_verified_changes = {
        int(episode_by_id[patch_id]["game_id"])
        for patch_id, rows in verified_changes_by_patch.items()
        if rows
    }
    no_atomic_change_games = sorted(
        {
            str(episode["game_name"])
            for episode in episodes_all
            if int(episode["game_id"]) not in games_with_verified_changes
        }
    )
    manifest = {
        "dataset_id": dataset_id,
        "stage": 3,
        "schema_version": STAGE3_SCHEMA_VERSION,
        "retriever_version": RETRIEVER_VERSION,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "source_stage2_dataset_id": source_dataset,
        "source_stage2_manifest_sha256": _sha256_file(inputs["stage2_root"] / "manifest.json"),
        "source_stage2_tables_sha256": {
            name: _sha256_file(inputs["stage2_root"] / f"{name}.parquet")
            for name in (
                "patch_changes",
                "review_claims",
                "patch_episodes",
                "patch_review_windows",
                "review_window_memberships",
                "game_terminology",
            )
        },
        "source_stage1_run_id": inputs["stage2_manifest"]["source_stage1_run_id"],
        "source_stage1_review_revisions_sha256": _sha256_file(
            inputs["stage1_root"] / "review_revisions.parquet"
        ),
        "code_version": __version__,
        "config": config,
        "dense": {
            "enabled": dense,
            "status": "completed" if dense else "not_run_backend_disabled",
            "library": "sentence-transformers" if dense else None,
            "model": dense_model if dense else None,
            "requested_revision": dense_revision if dense else None,
            "model_version": model_version,
            "similarity": "cosine similarity via dot product over normalized embeddings"
            if dense
            else None,
            "query_prefix": "query: " if dense else None,
            "claim_prefix": "passage: " if dense else None,
            "cache_path": str((repo_root / output_root / "cache") if dense else ""),
        },
        "retrieval": {
            "methods": ["bm25", "dense", "entity_aspect"] if dense else ["bm25", "entity_aspect"],
            "bm25": {
                "algorithm": "Okapi BM25",
                "k1": 1.5,
                "b": 0.75,
                "sentiment_only_terms_excluded": True,
                "one_content_token_can_rank": True,
            },
            "entity_aspect": {
                "vocabulary_scope": "per Steam game",
                "aliases": "Stage 2 game_terminology",
                "aspect_families": "small normalized aspect dimensions",
            },
            "fusion": {"method": "reciprocal_rank_fusion", "k": rrf_k},
            "ranked_list_truncation": {
                "top_per_change_per_method": maximum_budget,
                "configurable": True,
                "per_review_cap": None,
            },
            "candidate_eligibility": "same game plus Stage 2 temporal membership within configured patch-centered window; membership is not relevance",
        },
        "counts": counts,
        "hard_case_counts": dict(sorted(hard_case_counts.items())),
        "coverage": {
            "patch_windows_incomplete": sum(
                row["incomplete_window_segment_count"] for row in patch_diagnostics
            ),
            "patch_windows_total": sum(row["window_segment_count"] for row in patch_diagnostics),
            "no_atomic_change_games": no_atomic_change_games,
        },
        "budget_curves_interpretation": "candidate yield/overlap only; no independent relevance reference set; recall is not estimated",
        "audit": {
            "independent_from_candidate_membership": True,
            "selection_seed": audit_seed,
            "selection_rule": "one largest change-bearing episode per game with available review-window memberships; hash-ranked review sample per segment/language",
            "audit_patch_ids": audit_patch_ids,
            "label_status": "no labels generated",
            "candidate_ranks_in_packet": False,
            "full_structured_change_list": True,
        },
        "paths": {},
        "boundary": "Candidate retrieval only. No relevance labels, cross-encoder, or training dataset is produced.",
    }
    output_dir = repo_root / output_root / dataset_id
    report_dir = repo_root / report_root / dataset_id
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_parquet(output_dir / "candidate_pairs.parquet", candidate_rows, CANDIDATE_SCHEMA)
    _write_parquet(output_dir / "hard_negative_candidates.parquet", hard_rows, HARD_SCHEMA)
    _write_parquet(
        output_dir / "patch_diagnostics.parquet", patch_diagnostics, PATCH_DIAGNOSTIC_SCHEMA
    )
    _write_csv(output_dir / "budget_curves.csv", budget_rows)
    _write_csv(output_dir / "game_diagnostics.csv", list(game_diagnostics.values()))
    _write_json(
        output_dir / "diagnostics.json",
        {
            "counts": counts,
            "method_unique_examples": method_examples,
            "hard_case_counts": dict(hard_case_counts),
        },
    )
    _write_audit_jsonl(output_dir / "audit_full_list.jsonl", audit_jobs)
    manifest["paths"] = {
        "output": str(output_dir),
        "candidate_pairs": str(output_dir / "candidate_pairs.parquet"),
        "hard_negative_candidates": str(output_dir / "hard_negative_candidates.parquet"),
        "patch_diagnostics": str(output_dir / "patch_diagnostics.parquet"),
        "budget_curves": str(output_dir / "budget_curves.csv"),
        "audit_full_list": str(output_dir / "audit_full_list.jsonl"),
        "report": str(report_dir / "report.md"),
    }
    _write_json(output_dir / "manifest.json", manifest)
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "report.md").write_text(
        _render_report(
            dataset_id=dataset_id,
            manifest=manifest,
            patch_diagnostics=patch_diagnostics,
            budget_rows=budget_rows,
            examples=method_examples,
        ),
        encoding="utf-8",
    )
    return {
        "status": "retrieval_complete",
        "dataset_id": dataset_id,
        "output": str(output_dir),
        "report": str(report_dir / "report.md"),
        "counts": counts,
        "dense_model_version": model_version,
        "note": "No relevance labels or training data were generated; budget curves report candidate yield, not recall.",
    }
