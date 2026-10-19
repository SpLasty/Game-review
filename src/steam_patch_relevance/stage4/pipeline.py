"""Stage 4 file-based silver annotation, independent audit, and readiness checks."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from steam_patch_relevance import __version__
from steam_patch_relevance.stage4 import (
    LABELER_VERSION,
    PROMPT_VERSION,
    STAGE4_SCHEMA_VERSION,
)

DEFAULT_STAGE3_DATASET = "rv3-cef79b660029d7d5eb703567"
DEFAULT_OUTPUT_ROOT = Path("data/relevance_v1/processed/stage4")
DEFAULT_REPORT_ROOT = Path("reports/relevance_v1/stage4")
LABEL_CATEGORIES = {0, 1, 2, 3}
POLARITIES = {"positive", "negative", "mixed", "neutral", "unknown"}

LABEL_SCHEMA = pa.schema(
    [
        ("label_id", pa.string()),
        ("input_id", pa.string()),
        ("source_stage3_dataset_id", pa.string()),
        ("source_candidate_id", pa.string()),
        ("patch_id", pa.string()),
        ("game_id", pa.int64()),
        ("game_name", pa.string()),
        ("patch_title", pa.string()),
        ("change_id", pa.string()),
        ("change_text", pa.large_string()),
        ("claim_id", pa.string()),
        ("review_revision_id", pa.string()),
        ("review_id", pa.string()),
        ("claim_text", pa.large_string()),
        ("review_text", pa.large_string()),
        ("relevance_category", pa.int8()),
        ("confidence", pa.float64()),
        ("review_evidence", pa.large_string()),
        ("review_evidence_start", pa.int64()),
        ("review_evidence_end", pa.int64()),
        ("announcement_evidence", pa.large_string()),
        ("announcement_evidence_start", pa.int64()),
        ("announcement_evidence_end", pa.int64()),
        ("explanation", pa.large_string()),
        ("feature_polarity", pa.string()),
        ("ambiguity_reason", pa.large_string()),
        ("abstained", pa.bool_()),
        ("label_source", pa.string()),
        ("provider", pa.string()),
        ("model_name", pa.string()),
        ("model_version", pa.string()),
        ("prompt_version", pa.string()),
        ("prompt_sha256", pa.string()),
        ("source_review_created_at_utc", pa.string()),
        ("patch_anchor_at_utc", pa.string()),
        ("temporal_relation", pa.string()),
        ("created_at_utc", pa.string()),
    ]
)

AUDIT_SCHEMA = pa.schema(
    [
        ("audit_finding_id", pa.string()),
        ("input_id", pa.string()),
        ("source_stage3_dataset_id", pa.string()),
        ("source_audit_id", pa.string()),
        ("source_candidate_id", pa.string()),
        ("retrieval_omission", pa.bool_()),
        ("game_id", pa.int64()),
        ("game_name", pa.string()),
        ("patch_title", pa.string()),
        ("patch_id", pa.string()),
        ("change_id", pa.string()),
        ("change_text", pa.large_string()),
        ("claim_id", pa.string()),
        ("review_revision_id", pa.string()),
        ("review_id", pa.string()),
        ("claim_text", pa.large_string()),
        ("review_text", pa.large_string()),
        ("relevance_category", pa.int8()),
        ("confidence", pa.float64()),
        ("review_evidence", pa.large_string()),
        ("review_evidence_start", pa.int64()),
        ("review_evidence_end", pa.int64()),
        ("announcement_evidence", pa.large_string()),
        ("announcement_evidence_start", pa.int64()),
        ("announcement_evidence_end", pa.int64()),
        ("explanation", pa.large_string()),
        ("feature_polarity", pa.string()),
        ("ambiguity_reason", pa.large_string()),
        ("provider", pa.string()),
        ("model_name", pa.string()),
        ("model_version", pa.string()),
        ("prompt_version", pa.string()),
        ("prompt_sha256", pa.string()),
    ]
)


def _sha(value: str | bytes) -> str:
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(raw).hexdigest()


def _stable_id(prefix: str, *parts: str) -> str:
    identity = _sha("\0".join(parts))[:24]
    return f"{prefix}_{identity}"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on {path}:{line_number}: {exc}") from exc
    return rows


def _read_table(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Required source table does not exist: {path}")
    return pq.read_table(path).to_pylist()


def _read_manifest(path: Path, expected_id: str | None = None) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required source manifest does not exist: {path}")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if expected_id and manifest.get("dataset_id") != expected_id:
        raise ValueError(f"Manifest ID does not match requested dataset: {expected_id}")
    if manifest.get("complete") is False:
        raise ValueError(f"Refusing incomplete upstream dataset: {path}")
    return manifest


def _iso(value: Any) -> str | None:
    return value.isoformat() if hasattr(value, "isoformat") else value


def _prompt_sha(task_type: str) -> str:
    return _sha(_prompt_text(task_type))


def _prompt_text(task_type: str) -> str:
    common = (
        "You are labeling whether a Steam review claim concerns one specific developer change. "
        "Use only the supplied evidence. Temporal proximity, shared topic, sentiment, or the "
        "review's overall Recommended/Not Recommended vote do not establish attribution. "
        "Keep feature sentiment separate from relevance. Do not invent quotes. Exact quote fields "
        "must be copied verbatim from the supplied review and announcement text. Abstain when "
        "the evidence does not support a stable judgment.\n\n"
        "Categories: 0 unrelated; 1 topical only (same feature/mechanic, no reliable link to this "
        "specific change); 2 plausibly related (some update-specific evidence, attribution still "
        "uncertain); 3 clearly attributable (explicit update reference or strong, specific evidence "
        "linking the claim to this change). A 3 requires exact review and announcement evidence.\n\n"
        "Return one JSON object matching the response schema in the job. Do not include retrieval "
        "ranks or infer causality from time alone."
    )
    if task_type == "candidate_pair":
        return common
    return (
        common
        + "\n\nThis is an independent full-list audit. Read the entire review and inspect every "
        "numbered change. Return every change with at least topical evidence (category 1, 2, or 3), "
        "including its exact supporting review quote and exact change-note quote. Do not return "
        "unrelated pairs. If none is topical, return an empty discovered_pairs array and explain. "
        "Report the exact number of changes examined. This response is a machine judgment, not "
        "human verification."
    )


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def _patch_context(
    change: dict[str, Any], patch_changes: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    same_patch = [
        row
        for row in patch_changes
        if row["patch_id"] == change["patch_id"] and row.get("source_span_verified")
    ]
    same_patch.sort(key=lambda row: (row.get("source_span_start") or 0, row["change_id"]))
    index = next(
        (i for i, row in enumerate(same_patch) if row["change_id"] == change["change_id"]), None
    )
    if index is None:
        return []
    heading = change.get("heading_path") or []
    peers = [i for i, row in enumerate(same_patch) if (row.get("heading_path") or []) == heading]
    local = peers.index(index) if index in peers else -1
    selected: list[dict[str, Any]] = []
    if local >= 0:
        for peer_index in peers[max(0, local - 2) : local + 3]:
            row = same_patch[peer_index]
            if row["change_id"] == change["change_id"]:
                continue
            selected.append(
                {
                    "change_id": row["change_id"],
                    "source_span_raw": row.get("source_span_raw"),
                    "change_text": row.get("change_text"),
                    "heading_path": row.get("heading_path") or [],
                    "source_span_verified": bool(row.get("source_span_verified")),
                }
            )
    return selected


def _neighboring_patches(
    candidate: dict[str, Any],
    patch_by_id: dict[str, dict[str, Any]],
    change_by_id: dict[str, dict[str, Any]],
    ambiguities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    neighbors: dict[str, set[str]] = defaultdict(set)
    for row in ambiguities:
        if row["change_id_a"] == candidate["change_id"]:
            neighbors[row["patch_id_b"]].add("same normalized feature in overlapping episodes")
        elif row["change_id_b"] == candidate["change_id"]:
            neighbors[row["patch_id_a"]].add("same normalized feature in overlapping episodes")
    for other in candidate.get("competing_feature_patch_ids") or []:
        neighbors[other].add("retrieval identified a potentially competing feature patch")

    output = []
    target = change_by_id[candidate["change_id"]]
    for neighbor_id in sorted(neighbors):
        patch = patch_by_id.get(neighbor_id)
        if not patch or patch.get("game_id") != candidate.get("game_id"):
            continue
        related = []
        for row in ambiguities:
            if row.get("patch_id_a") == neighbor_id and row.get("change_id_a") in change_by_id:
                related.append(change_by_id[row["change_id_a"]])
            if row.get("patch_id_b") == neighbor_id and row.get("change_id_b") in change_by_id:
                related.append(change_by_id[row["change_id_b"]])
        if not related:
            related = [
                row
                for row in change_by_id.values()
                if row["patch_id"] == neighbor_id
                and target.get("entity")
                and row.get("entity")
                and row["entity"].casefold() == target["entity"].casefold()
            ][:5]
        output.append(
            {
                "patch_id": neighbor_id,
                "title": patch.get("title"),
                "published_at_utc": _iso(patch.get("published_at_utc")),
                "reasons": sorted(neighbors[neighbor_id]),
                "related_changes": [
                    {
                        "change_id": row["change_id"],
                        "change_text": row.get("change_text"),
                        "entity": row.get("entity"),
                        "aspect": row.get("aspect"),
                        "source_span_verified": bool(row.get("source_span_verified")),
                    }
                    for row in related[:5]
                ],
            }
        )
    return output


def _temporal_relation(review_created: Any, patch_anchor: Any) -> str:
    if not review_created or not patch_anchor:
        return "unknown"
    delta_days = (review_created - patch_anchor).total_seconds() / 86_400
    if delta_days < 0:
        return "before_patch_anchor"
    if delta_days < 7:
        return "after_patch_0_7d"
    if delta_days < 14:
        return "after_patch_8_14d"
    return "later_than_14d"


def _specific_tokens(value: str | None) -> set[str]:
    ignored = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "that",
        "this",
        "were",
        "was",
        "are",
        "have",
        "has",
        "into",
        "after",
        "before",
        "when",
        "where",
        "fixed",
        "fix",
        "issue",
        "issues",
        "game",
        "player",
        "players",
        "really",
        "just",
        "still",
        "good",
        "bad",
        "broken",
        "problem",
        "problems",
        "update",
        "patch",
        "new",
        "now",
        "not",
        "working",
        "work",
        "bug",
        "bugs",
    }
    return {
        token.casefold().rstrip("s")
        for token in re.findall(r"[A-Za-z0-9]+", value or "")
        if len(token) > 2 and token.casefold() not in ignored
    }


def _diverse_take(
    rows: list[dict[str, Any]], count: int, seed: str, *, rank_field: str = "fused_rank"
) -> list[dict[str, Any]]:
    def quality(row: dict[str, Any]) -> tuple[Any, ...]:
        anchor = row.get("patch_anchor_at_utc")
        created = row.get("review_created_at_utc")
        post_patch = anchor is not None and created is not None and created >= anchor

        shared = _specific_tokens(row.get("change_text")) & _specific_tokens(row.get("claim_text"))
        specific_entity = bool(row.get("matched_entity")) and str(
            row["matched_entity"]
        ).casefold() not in {
            "fixed",
            "fix",
            "bug",
            "issue",
            "crash",
            "player",
            "game",
            "added",
            "removed",
        }
        rank = row.get(rank_field) or 10**9
        score = max(row.get("bm25_score") or 0, row.get("dense_cosine_score") or 0)
        return (
            not post_patch,
            -len(shared),
            not specific_entity,
            -(row.get("entity_match_score") or 0),
            -(row.get("aspect_match_score") or 0),
            rank,
            -score,
            _sha(f"{seed}\0{row['candidate_id']}"),
        )

    ranked = sorted(rows, key=quality)
    selected: list[dict[str, Any]] = []
    seen_changes: set[str] = set()
    seen_reviews: set[str] = set()
    for row in ranked:
        if row["change_id"] in seen_changes or row["review_revision_id"] in seen_reviews:
            continue
        selected.append(row)
        seen_changes.add(row["change_id"])
        seen_reviews.add(row["review_revision_id"])
        if len(selected) >= count:
            return selected
    for row in ranked:
        if row not in selected:
            selected.append(row)
            if len(selected) >= count:
                break
    return selected


def _select_candidates(
    candidates: list[dict[str, Any]],
    hard_rows: list[dict[str, Any]],
    *,
    per_game: int,
    seed: str,
) -> tuple[list[tuple[dict[str, Any], str]], dict[str, dict[str, int]]]:
    hard_ids = {row["candidate_id"] for row in hard_rows}
    selected: list[tuple[dict[str, Any], str]] = []
    counts: dict[str, dict[str, int]] = {}
    games = sorted({row["game_name"] for row in candidates})
    # Keep each game's pilot balanced among hard cases, semantic-only discoveries,
    # specific lexical overlap, and top fused ranks. The labeler does not see these strata.
    quarter = max(1, per_game // 4)
    for game in games:
        game_rows = [row for row in candidates if row["game_name"] == game]
        chosen: list[tuple[dict[str, Any], str]] = []
        strata = [
            (
                "hard_case",
                [row for row in game_rows if row["candidate_id"] in hard_ids],
                quarter,
                "fused_rank",
            ),
            (
                "semantic_discovery",
                [
                    row
                    for row in game_rows
                    if row.get("dense_rank") is not None
                    and row.get("bm25_rank") is None
                    and row.get("entity_aspect_rank") is None
                ],
                quarter,
                "dense_rank",
            ),
            (
                "specific_lexical_overlap",
                [
                    row
                    for row in game_rows
                    if row.get("bm25_rank") is not None
                    and _specific_tokens(row.get("change_text"))
                    & _specific_tokens(row.get("claim_text"))
                ],
                quarter,
                "bm25_rank",
            ),
            (
                "high_fused_rank",
                sorted(
                    game_rows, key=lambda row: (row.get("fused_rank") or 10**9, row["candidate_id"])
                ),
                max(0, per_game - 3 * quarter),
                "fused_rank",
            ),
        ]
        used: set[str] = set()
        strata_counts: dict[str, int] = {}
        for name, pool, desired, rank_field in strata:
            pool = [row for row in pool if row["candidate_id"] not in used]
            take = _diverse_take(pool, desired, f"{seed}:{game}:{name}", rank_field=rank_field)
            chosen.extend((row, name) for row in take)
            used.update(row["candidate_id"] for row in take)
            strata_counts[name] = len(take)
        if len(chosen) < per_game:
            remaining = [row for row in game_rows if row["candidate_id"] not in used]
            extra = _diverse_take(remaining, per_game - len(chosen), f"{seed}:{game}:fill")
            chosen.extend((row, "high_fused_rank") for row in extra)
            strata_counts["high_fused_rank"] += len(extra)
        chosen = chosen[:per_game]
        selected.extend(chosen)
        counts[game] = strata_counts
    return selected, counts


def _build_candidate_job(
    candidate: dict[str, Any],
    *,
    input_id: str,
    review: dict[str, Any],
    claim: dict[str, Any],
    change: dict[str, Any],
    announcement: dict[str, Any],
    patch: dict[str, Any],
    context_changes: list[dict[str, Any]],
    neighboring_patches: list[dict[str, Any]],
) -> dict[str, Any]:
    created = review.get("created_at_utc")
    patch_time = patch.get("anchor_at_utc")
    task = {
        "input_id": input_id,
        "schema_version": STAGE4_SCHEMA_VERSION,
        "prompt_version": PROMPT_VERSION,
        "prompt": _prompt_text("candidate_pair"),
        "prompt_sha256": _prompt_sha("candidate_pair"),
        "task_type": "candidate_pair",
        "input": {
            "game": {"game_id": candidate["game_id"], "game_name": candidate["game_name"]},
            "patch": {
                "patch_id": candidate["patch_id"],
                "title": candidate["patch_title"],
                "published_at_utc": _iso(patch.get("published_at_utc")),
                "anchor_at_utc": _iso(patch_time),
                "anchor_source": candidate.get("patch_anchor_source"),
                "time_is_release_verified": patch.get("time_is_release_verified"),
                "review_temporal_relation": _temporal_relation(created, patch_time),
                "review_window_segments": candidate.get("window_segments") or [],
                "announcement_source_url": candidate.get("change_source_url"),
                "announcement_text": announcement.get("body_original") or "",
                "target_change_context": {
                    "change_id": change["change_id"],
                    "change_text": change.get("change_text"),
                    "source_span_raw": change.get("source_span_raw"),
                    "source_span_start": change.get("source_span_start"),
                    "source_span_end": change.get("source_span_end"),
                    "heading_path": change.get("heading_path") or [],
                    "entity": change.get("entity"),
                    "aspect": change.get("aspect"),
                    "action": change.get("action"),
                    "direction": change.get("direction"),
                    "developer_status": change.get("developer_status"),
                    "source_span_verified": bool(change.get("source_span_verified")),
                    "source_url": change.get("source_url"),
                },
                "surrounding_changes": context_changes,
                "neighboring_patch_information": neighboring_patches,
            },
            "review": {
                "review_id": candidate["review_id"],
                "review_revision_id": candidate["review_revision_id"],
                "language": review.get("language"),
                "created_at_utc": _iso(created),
                "updated_at_utc": _iso(review.get("updated_at_utc")),
                "full_text": review.get("review_text_original") or "",
                "target_claim": {
                    "claim_id": claim["claim_id"],
                    "text": claim.get("claim_text_original"),
                    "start": claim.get("claim_span_start"),
                    "end": claim.get("claim_span_end"),
                    "referenced_entity": claim.get("referenced_entity"),
                    "aspect": claim.get("aspect"),
                    "temporal_cues": claim.get("temporal_cues") or [],
                    "negated": claim.get("negated"),
                    "uncertain": claim.get("uncertain"),
                },
            },
        },
        "response_schema": {
            "status": "labeled | abstain",
            "relevance_category": "0 | 1 | 2 | 3 | null",
            "confidence": "number in [0,1]",
            "review_evidence": "exact quote from target claim, or empty string",
            "announcement_evidence": "exact quote from target change source span, or empty string",
            "explanation": "specific, evidence-grounded explanation",
            "feature_polarity": "positive | negative | mixed | neutral | unknown",
            "ambiguity_reason": "string; empty when no material ambiguity",
        },
        "response": None,
    }
    return task


def _build_audit_job(
    row: dict[str, Any],
    *,
    input_id: str,
    claims_by_revision: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    claims = claims_by_revision.get(row["review_revision_id"], [])
    return {
        "input_id": input_id,
        "schema_version": STAGE4_SCHEMA_VERSION,
        "prompt_version": PROMPT_VERSION,
        "prompt": _prompt_text("full_list_audit"),
        "prompt_sha256": _prompt_sha("independent_full_list_audit"),
        "task_type": "independent_full_list_audit",
        "candidate_independent": True,
        "input": {
            "game": {"game_id": row["game_id"], "game_name": row["game_name"]},
            "patch": {
                "patch_id": row["patch_id"],
                "title": row["patch_title"],
                "source_url": row["patch_source_url"],
                "anchor_at_utc": row["patch_anchor_at_utc"],
                "anchor_source": row["patch_anchor_source"],
                "review_temporal_relation": _temporal_relation(
                    datetime.fromisoformat(row["review_created_at_utc"]),
                    datetime.fromisoformat(row["patch_anchor_at_utc"]),
                ),
                "window_segment": row["window_segment"],
                "window_collection_status": row["window_collection_status"],
                "window_review_coverage_fraction": row["window_review_coverage_fraction"],
                "full_change_count": row["full_change_count"],
                "full_change_list": [
                    {**change, "number": index}
                    for index, change in enumerate(row["full_change_list"], 1)
                ],
            },
            "review": {
                "review_id": row["review_id"],
                "review_revision_id": row["review_revision_id"],
                "language": row["review_language"],
                "created_at_utc": row["review_created_at_utc"],
                "updated_at_utc": row["review_updated_at_utc"],
                "full_text": row["review_text"],
                "extracted_claims": [
                    {
                        "claim_id": claim["claim_id"],
                        "text": claim["claim_text_original"],
                        "start": claim["claim_span_start"],
                        "end": claim["claim_span_end"],
                    }
                    for claim in claims
                ],
            },
        },
        "response_schema": {
            "full_change_list_examined": "boolean",
            "changes_examined_count": "integer; must equal full_change_count",
            "discovered_pairs": [
                {
                    "change_id": "one ID from full_change_list",
                    "claim_id": "one extracted_claim ID or null",
                    "claim_evidence": "exact quote from full review",
                    "announcement_evidence": "exact quote from this change's source_span_raw/change_text",
                    "relevance_category": "1 | 2 | 3",
                    "confidence": "number in [0,1]",
                    "explanation": "specific, evidence-grounded explanation",
                    "feature_polarity": "positive | negative | mixed | neutral | unknown",
                    "ambiguity_reason": "string",
                }
            ],
            "no_matches_reason": "string when discovered_pairs is empty",
        },
        "response": None,
    }


def export_full_list_review_audit(
    *,
    repo_root: Path,
    patch_id: str,
    window_segment: str = "after_0_7d",
    review_count: int = 300,
    seed: str = "stage4-full-list-audit-300-v1",
    source_dataset: str = "rv2-d52a3f9f1a3de2fe80aa098f",
    output_root: Path = DEFAULT_OUTPUT_ROOT / "independent_audit",
    report_root: Path = DEFAULT_REPORT_ROOT / "independent_audit",
) -> dict[str, Any]:
    """Export a deterministic review sample with the complete patch change list.

    Sampling comes only from Stage 2 patch-window memberships and Stage 1 review
    revisions. Stage 3 candidate tables and ranks are deliberately not read.
    """
    if review_count < 1:
        raise ValueError("review_count must be positive")
    if window_segment not in {"after_0_7d", "after_8_14d"}:
        raise ValueError("full-list audit sampling requires a post-patch window segment")

    stage2_root = repo_root / "data/relevance_v1/processed/stage2" / source_dataset
    stage2_manifest = _read_manifest(stage2_root / "manifest.json", source_dataset)
    stage1_id = stage2_manifest["source_stage1_run_id"]
    stage1_root = repo_root / "data/relevance_v1/normalized" / stage1_id
    if not stage1_root.is_dir():
        raise FileNotFoundError(f"Stage 1 source run does not exist: {stage1_root}")

    episodes = [
        row for row in _read_table(stage2_root / "patch_episodes.parquet")
        if row["patch_id"] == patch_id
    ]
    if len(episodes) != 1:
        raise ValueError(f"Expected one Stage 2 patch episode for {patch_id}, found {len(episodes)}")
    episode = episodes[0]
    windows = [
        row for row in _read_table(stage2_root / "patch_review_windows.parquet")
        if row["patch_id"] == patch_id and row["segment"] == window_segment
    ]
    if len(windows) != 1:
        raise ValueError(
            f"Expected one {window_segment} window for {patch_id}, found {len(windows)}"
        )
    window = windows[0]

    changes = [
        row for row in _read_table(stage2_root / "patch_changes.parquet")
        if row["patch_id"] == patch_id
        and row.get("source_span_verified")
        and str(row.get("developer_status") or "").startswith("implemented")
    ]
    changes.sort(key=lambda row: (row.get("source_span_start") or 0, row["change_id"]))
    if not changes:
        raise ValueError(f"Patch {patch_id} has no verified implemented changes")

    revision_rows = _read_table(stage1_root / "review_revisions.parquet")
    review_by_revision = {row["review_revision_id"]: row for row in revision_rows}
    memberships = [
        row for row in _read_table(stage2_root / "review_window_memberships.parquet")
        if row["patch_id"] == patch_id
        and row["window_segment"] == window_segment
        and row["review_revision_id"] in review_by_revision
        and (review_by_revision[row["review_revision_id"]].get("review_text_original") or "").strip()
    ]

    # A review may have multiple collected revisions in the same window. Keep
    # the newest observed revision per logical Steam review, then sample IDs.
    latest_by_review: dict[str, tuple[tuple[Any, ...], dict[str, Any]]] = {}
    for membership in memberships:
        review = review_by_revision[membership["review_revision_id"]]
        review_id = membership["review_id"]
        revision_rank = (
            review.get("updated_unix") or 0,
            review.get("created_unix") or 0,
            review["review_revision_id"],
        )
        current = latest_by_review.get(review_id)
        if current is None or revision_rank > current[0]:
            latest_by_review[review_id] = (revision_rank, membership)
    population = [entry[1] for entry in latest_by_review.values()]
    if review_count > len(population):
        raise ValueError(
            f"Requested {review_count} unique reviews, but only {len(population)} are available"
        )
    population.sort(key=lambda row: _sha(f"{seed}\0{row['review_id']}"))
    selected_memberships = population[:review_count]

    claims_by_revision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in _read_table(stage2_root / "review_claims.parquet"):
        claims_by_revision[claim["review_revision_id"]].append(claim)

    source_url = episode.get("source_url") or ""
    full_change_list = [
        {
            "change_id": row["change_id"],
            "change_text": row.get("change_text") or "",
            "source_span_raw": row.get("source_span_raw") or "",
            "source_span_start": row.get("source_span_start"),
            "source_span_end": row.get("source_span_end"),
            "source_url": row.get("source_url") or source_url,
            "heading_path": row.get("heading_path") or [],
            "entity": row.get("entity"),
            "entity_candidates": row.get("entity_candidates") or [],
            "aspect": row.get("aspect"),
            "action": row.get("action"),
            "direction": row.get("direction"),
            "previous_value": row.get("previous_value"),
            "new_value": row.get("new_value"),
            "developer_status": row.get("developer_status"),
            "source_span_verified": True,
        }
        for row in changes
    ]

    source_hashes = {
        name: _sha((stage_root / name).read_bytes())
        for stage_root, names in (
            (stage2_root, ("manifest.json", "patch_episodes.parquet", "patch_changes.parquet",
                           "patch_review_windows.parquet", "review_window_memberships.parquet",
                           "review_claims.parquet")),
            (stage1_root, ("review_revisions.parquet",)),
        )
        for name in names
    }
    config = {
        "source_stage2_dataset_id": source_dataset,
        "source_stage1_run_id": stage1_id,
        "patch_id": patch_id,
        "window_segment": window_segment,
        "review_count": review_count,
        "selection_seed": seed,
        "selection_rule": "SHA-256 rank of unique Steam review ID within the selected Stage 2 window; one latest collected revision per review ID",
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": _prompt_sha("independent_full_list_audit"),
        "source_hashes": source_hashes,
    }
    run_id = f"rv4audit-{_sha(json.dumps(config, sort_keys=True))[:24]}"
    output_dir = repo_root / output_root / run_id
    report_dir = repo_root / report_root / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    jobs: list[dict[str, Any]] = []
    selection_rows: list[dict[str, Any]] = []
    for membership in selected_memberships:
        review = review_by_revision[membership["review_revision_id"]]
        audit_row = {
            "audit_id": _stable_id(
                "rv4audit_review", patch_id, window_segment, membership["review_revision_id"]
            ),
            "selection_rule": config["selection_rule"],
            "selection_seed": seed,
            "patch_id": patch_id,
            "game_id": episode["game_id"],
            "game_name": episode["game_name"],
            "patch_title": episode["title"],
            "patch_source_url": source_url,
            "patch_anchor_at_utc": _iso(episode["anchor_at_utc"]),
            "patch_anchor_source": episode["anchor_source"],
            "window_segment": window_segment,
            "window_collection_status": window["collection_status"],
            "window_review_coverage_fraction": window["review_coverage_fraction"],
            "review_revision_id": review["review_revision_id"],
            "review_id": membership["review_id"],
            "review_created_at_utc": _iso(review.get("created_at_utc")),
            "review_updated_at_utc": _iso(review.get("updated_at_utc")),
            "review_language": review.get("language"),
            "review_text": review.get("review_text_original") or "",
            "full_change_count": len(full_change_list),
            "full_change_list": full_change_list,
        }
        input_id = _stable_id("rv4_input", run_id, audit_row["audit_id"])
        job = _build_audit_job(
            audit_row, input_id=input_id, claims_by_revision=claims_by_revision
        )
        job["_selection_provenance"] = {
            "source_audit_id": audit_row["audit_id"],
            "source_stage1_review_revision_id": review["review_revision_id"],
            "candidate_independent": True,
        }
        jobs.append(job)
        selection_rows.append(
            {
                "input_id": input_id,
                "source_audit_id": audit_row["audit_id"],
                "review_id": membership["review_id"],
                "review_revision_id": review["review_revision_id"],
                "patch_id": patch_id,
                "window_segment": window_segment,
                "candidate_independent": True,
            }
        )

    jobs_path = output_dir / "annotation_jobs.jsonl"
    _write_jsonl(jobs_path, jobs)
    (output_dir / "selection_manifest.json").write_text(
        json.dumps(
            {
                **config,
                "dataset_id": run_id,
                "population_unique_reviews": len(population),
                "selected_inputs": selection_rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    manifest = {
        "dataset_id": run_id,
        "stage": 4,
        "status": "awaiting_silver_responses",
        "task_type": "independent_full_list_audit",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "config": config,
        "source_ids": {
            "source_stage1_run_id": stage1_id,
            "source_stage2_dataset_id": source_dataset,
            # This is consulted only during import to compare independently found
            # pairs with retrieval output; it is never used to select audit reviews.
            "source_stage3_dataset_id": DEFAULT_STAGE3_DATASET,
        },
        "source_stage2_manifest_sha256": source_hashes["manifest.json"],
        "patch_window": {
            "patch_title": episode["title"],
            "game_name": episode["game_name"],
            "patch_anchor_at_utc": _iso(episode["anchor_at_utc"]),
            "anchor_source": episode["anchor_source"],
            "collection_status": window["collection_status"],
            "review_coverage_fraction": window["review_coverage_fraction"],
            "available_unique_reviews": len(population),
            "verified_implemented_changes": len(full_change_list),
        },
        "counts": {
            "candidate_pair_inputs": 0,
            "independent_full_list_audit_inputs": len(jobs),
            "review_jobs": len(jobs),
            "unique_review_ids": len({row["review_id"] for row in selection_rows}),
            "full_list_changes_exposed": len(jobs) * len(full_change_list),
        },
        "paths": {
            "output": str(output_dir),
            "annotation_jobs": str(jobs_path),
            "selection_manifest": str(output_dir / "selection_manifest.json"),
            "report": str(report_dir / "report.md"),
        },
        "candidate_independence": "Reviews sampled from Stage 2 patch-window memberships before and without consulting Stage 3 candidate tables, ranks, or labels.",
        "labeling_boundary": "Export creates prompts only; it does not create responses or labels.",
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = [
        f"# Independent full-list review audit — `{run_id}`",
        "",
        f"- Game: {episode['game_name']} (Steam app {episode['game_id']})",
        f"- Patch: {episode['title']} (`{patch_id}`)",
        f"- Patch anchor: {_iso(episode['anchor_at_utc'])} ({episode['anchor_source']})",
        f"- Window: `{window_segment}`; collection status `{window['collection_status']}`; reported review coverage {window['review_coverage_fraction']:.1%}.",
        f"- Sampling population: {len(population)} unique review IDs with non-empty text; selected {len(jobs)} by seeded SHA-256 ranking.",
        f"- Full patch list: {len(full_change_list)} source-span-verified implemented changes, numbered in source order in every job.",
        "- Candidate independence: selected directly from Stage 2 window memberships; Stage 3 candidate tables and ranks were not read.",
        f"- Stage 3 dataset used only for retrieval-omission comparison after import: `{DEFAULT_STAGE3_DATASET}`.",
        "- Each job contains the full original review and all extracted Stage 2 claims for that revision.",
        "- No relevance labels are present in this export.",
        "",
        f"Jobs: `{jobs_path}`",
        f"Selection and source hashes: `{output_dir / 'selection_manifest.json'}`",
    ]
    (report_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return {
        "status": "awaiting_silver_responses",
        "dataset_id": run_id,
        "output": str(output_dir),
        "report": str(report_dir / "report.md"),
        "available_unique_reviews": len(population),
        "review_jobs": len(jobs),
        "verified_implemented_changes": len(full_change_list),
        "collection_status": window["collection_status"],
        "review_coverage_fraction": window["review_coverage_fraction"],
    }


def export_annotation_pilot(
    *,
    repo_root: Path,
    source_dataset: str = DEFAULT_STAGE3_DATASET,
    candidate_pairs: int = 24,
    audit_reviews: int = 6,
    per_game_candidates: int = 8,
    seed: str = "stage4-pilot-v1",
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    report_root: Path = DEFAULT_REPORT_ROOT,
) -> dict[str, Any]:
    if candidate_pairs < 1 or audit_reviews < 0:
        raise ValueError("candidate_pairs must be positive and audit_reviews nonnegative")
    if candidate_pairs % 3:
        raise ValueError(
            "candidate_pairs must be divisible by 3 for this three-game stratified pilot"
        )
    per_game = candidate_pairs // 3
    if per_game != per_game_candidates:
        per_game_candidates = per_game
    stage3_root = repo_root / "data/relevance_v1/processed/stage3" / source_dataset
    stage3_manifest = _read_manifest(stage3_root / "manifest.json", source_dataset)
    stage2_id = stage3_manifest["source_stage2_dataset_id"]
    stage2_root = repo_root / "data/relevance_v1/processed/stage2" / stage2_id
    stage2_manifest = _read_manifest(stage2_root / "manifest.json", stage2_id)
    stage1_root = (
        repo_root / "data/relevance_v1/normalized" / stage2_manifest["source_stage1_run_id"]
    )

    candidates = _read_table(stage3_root / "candidate_pairs.parquet")
    hard_rows = _read_table(stage3_root / "hard_negative_candidates.parquet")
    audits = _read_jsonl(stage3_root / "audit_full_list.jsonl")
    changes = _read_table(stage2_root / "patch_changes.parquet")
    claims = _read_table(stage2_root / "review_claims.parquet")
    patches = _read_table(stage2_root / "patch_episodes.parquet")
    ambiguities = _read_table(stage2_root / "change_temporal_ambiguities.parquet")
    announcements = _read_table(stage2_root / "announcement_classifications.parquet")
    reviews = _read_table(stage1_root / "review_revisions.parquet")

    change_by_id = {row["change_id"]: row for row in changes}
    claim_by_id = {row["claim_id"]: row for row in claims}
    patch_by_id = {row["patch_id"]: row for row in patches}
    announcement_by_revision = {row["announcement_revision_id"]: row for row in announcements}
    review_by_revision = {row["review_revision_id"]: row for row in reviews}
    claims_by_revision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        claims_by_revision[claim["review_revision_id"]].append(claim)

    selected, stratum_counts = _select_candidates(
        candidates,
        hard_rows,
        per_game=per_game_candidates,
        seed=seed,
    )
    if len(selected) != candidate_pairs:
        raise ValueError(
            f"Requested {candidate_pairs} candidate labels but only {len(selected)} could be sampled"
        )
    selected_review_revisions = {row["review_revision_id"] for row, _ in selected}

    audits_by_game_segment: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for audit in audits:
        if audit["review_revision_id"] not in selected_review_revisions:
            audits_by_game_segment[(audit["game_name"], audit["window_segment"])].append(audit)
    for group in audits_by_game_segment.values():
        group.sort(key=lambda row: _sha(f"{seed}\0{row['audit_id']}"))
    selected_audits: list[dict[str, Any]] = []
    games = sorted({row["game_name"] for row in candidates})
    # Two candidate-independent reviews per game: one early post-patch and one pre-patch.
    # If a requested temporal stratum is unavailable, fill from any other segment in that game.
    audit_targets = [(game, "after_0_7d") for game in games] + [
        (game, "before_14d") for game in games
    ]
    for game, segment in audit_targets:
        if len(selected_audits) >= audit_reviews:
            break
        pool = audits_by_game_segment.get((game, segment), [])
        if not pool:
            pool = [
                row
                for (g, _), group in audits_by_game_segment.items()
                if g == game
                for row in group
            ]
            pool = sorted(pool, key=lambda row: _sha(f"{seed}\0{row['audit_id']}"))
        chosen_audit = next(
            (
                row
                for row in pool
                if row["audit_id"] not in {x["audit_id"] for x in selected_audits}
            ),
            None,
        )
        if chosen_audit:
            selected_audits.append(chosen_audit)
    if len(selected_audits) < audit_reviews:
        rest = sorted(
            [row for row in audits if row["review_revision_id"] not in selected_review_revisions],
            key=lambda row: _sha(f"{seed}\0fill\0{row['audit_id']}"),
        )
        for row in rest:
            if row["audit_id"] not in {x["audit_id"] for x in selected_audits}:
                selected_audits.append(row)
            if len(selected_audits) == audit_reviews:
                break
    if len(selected_audits) != audit_reviews:
        raise ValueError(
            f"Requested {audit_reviews} independent audit reviews but found {len(selected_audits)}"
        )

    config = {
        "source_stage3_dataset_id": source_dataset,
        "source_stage2_dataset_id": stage2_id,
        "source_stage1_run_id": stage2_manifest["source_stage1_run_id"],
        "candidate_pairs": candidate_pairs,
        "audit_reviews": audit_reviews,
        "per_game_candidates": per_game_candidates,
        "selection_seed": seed,
        "schema_version": STAGE4_SCHEMA_VERSION,
        "labeler_version": LABELER_VERSION,
        "prompt_version": PROMPT_VERSION,
        "candidate_prompt_sha256": _prompt_sha("candidate_pair"),
        "audit_prompt_sha256": _prompt_sha("independent_full_list_audit"),
    }
    run_id = f"rv4-{_sha(json.dumps(config, sort_keys=True))[:24]}"
    output_dir = repo_root / output_root / run_id
    report_dir = repo_root / report_root / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    jobs: list[dict[str, Any]] = []
    selection_rows: list[dict[str, Any]] = []
    for candidate, stratum in selected:
        change = change_by_id.get(candidate["change_id"])
        claim = claim_by_id.get(candidate["claim_id"])
        review = review_by_revision.get(candidate["review_revision_id"])
        patch = patch_by_id.get(candidate["patch_id"])
        if not all((change, claim, review, patch)):
            raise ValueError(
                f"Candidate source references missing Stage 1/2 rows: {candidate['candidate_id']}"
            )
        if review.get("appid") != candidate.get("game_id"):
            raise ValueError(f"Candidate review game mismatch: {candidate['candidate_id']}")
        review_text = review.get("review_text_original") or ""
        claim_text = claim.get("claim_text_original") or ""
        claim_start, claim_end = claim.get("claim_span_start"), claim.get("claim_span_end")
        if (
            claim_start is None
            or claim_end is None
            or review_text[claim_start:claim_end] != claim_text
        ):
            raise ValueError(
                f"Source claim offsets do not match original review: {candidate['claim_id']}"
            )
        announcement = announcement_by_revision.get(change["announcement_revision_id"], {})
        input_id = _stable_id(
            "rv4_input", source_dataset, "candidate_pair", candidate["candidate_id"]
        )
        job = _build_candidate_job(
            candidate,
            input_id=input_id,
            review=review,
            claim=claim,
            change=change,
            announcement=announcement,
            patch=patch,
            context_changes=_patch_context(change, changes),
            neighboring_patches=_neighboring_patches(
                candidate, patch_by_id, change_by_id, ambiguities
            ),
        )
        jobs.append(job)
        selection_rows.append(
            {
                "input_id": input_id,
                "task_type": "candidate_pair",
                "source_candidate_id": candidate["candidate_id"],
                "selection_stratum": stratum,
                "game_name": candidate["game_name"],
                "patch_id": candidate["patch_id"],
                "change_id": candidate["change_id"],
                "claim_id": candidate["claim_id"],
                "review_revision_id": candidate["review_revision_id"],
                "selection_seed": seed,
            }
        )
    for audit in selected_audits:
        input_id = _stable_id(
            "rv4_input", source_dataset, "independent_full_list_audit", audit["audit_id"]
        )
        job = _build_audit_job(
            audit,
            input_id=input_id,
            claims_by_revision=claims_by_revision,
        )
        jobs.append(job)
        selection_rows.append(
            {
                "input_id": input_id,
                "task_type": "independent_full_list_audit",
                "source_audit_id": audit["audit_id"],
                "game_name": audit["game_name"],
                "patch_id": audit["patch_id"],
                "review_revision_id": audit["review_revision_id"],
                "selection_seed": seed,
                "candidate_independent": True,
            }
        )
    _write_jsonl(output_dir / "annotation_jobs.jsonl", jobs)
    (output_dir / "selection_manifest.json").write_text(
        json.dumps(
            {
                "seed": seed,
                "source_stage3_dataset_id": source_dataset,
                "candidate_strata_by_game": stratum_counts,
                "selected_inputs": selection_rows,
                "audit_selection_rule": "candidate-independent Stage 3 full-list packets; exclude candidate-labeled review revisions",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (output_dir / "schema.json").write_text(
        json.dumps(
            {
                "schema_version": STAGE4_SCHEMA_VERSION,
                "categories": {
                    "0": "unrelated",
                    "1": "topical only",
                    "2": "plausibly related",
                    "3": "clearly attributable",
                },
                "polarity_values": sorted(POLARITIES),
                "abstention": "set status=abstain and relevance_category=null",
                "evidence_rule": "quotes must be verbatim spans in the original review claim and target change source span; category 3 requires both",
                "prompt_version": PROMPT_VERSION,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    manifest = {
        "dataset_id": run_id,
        "stage": 4,
        "status": "awaiting_silver_responses",
        "schema_version": STAGE4_SCHEMA_VERSION,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "labeler_version": LABELER_VERSION,
        "code_version": __version__,
        "source_ids": config,
        "source_manifests": {
            "stage3_manifest_sha256": _sha((stage3_root / "manifest.json").read_bytes()),
            "stage2_manifest_sha256": _sha((stage2_root / "manifest.json").read_bytes()),
            "stage1_run_id": stage2_manifest["source_stage1_run_id"],
        },
        "counts": {
            "candidate_pair_inputs": sum(job["task_type"] == "candidate_pair" for job in jobs),
            "independent_full_list_audit_inputs": sum(
                job["task_type"] == "independent_full_list_audit" for job in jobs
            ),
            "full_list_changes_exposed": sum(
                len(job["input"]["patch"]["full_change_list"])
                for job in jobs
                if job["task_type"] == "independent_full_list_audit"
            ),
        },
        "paths": {
            "output": str(output_dir),
            "annotation_jobs": str(output_dir / "annotation_jobs.jsonl"),
            "selection_manifest": str(output_dir / "selection_manifest.json"),
        },
        "labeling_boundary": "No response, label, or human review has been created by export.",
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {
        "status": "awaiting_silver_responses",
        "dataset_id": run_id,
        "output": str(output_dir),
        "report": str(report_dir),
        "candidate_pair_inputs": manifest["counts"]["candidate_pair_inputs"],
        "independent_full_list_audit_inputs": manifest["counts"][
            "independent_full_list_audit_inputs"
        ],
        "full_list_changes_exposed": manifest["counts"]["full_list_changes_exposed"],
        "candidate_strata_by_game": stratum_counts,
    }


def _validate_quote(
    quote: Any, text: str, field: str, *, required: bool
) -> tuple[int | None, int | None]:
    if not isinstance(quote, str):
        raise ValueError(f"{field} must be a string")
    if not quote:
        if required:
            raise ValueError(f"{field} is required")
        return None, None
    start = text.find(quote)
    if start < 0:
        raise ValueError(f"{field} is not an exact substring of its source text")
    return start, start + len(quote)


def _validate_common_response(response: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
    if response.get("input_id") != job["input_id"]:
        raise ValueError("response input_id does not match job")
    if response.get("prompt_version") != PROMPT_VERSION:
        raise ValueError("response prompt_version is missing or does not match this run")
    if response.get("prompt_sha256") != job.get("prompt_sha256"):
        raise ValueError("response prompt_sha256 is missing or does not match the exported prompt")
    if (
        not response.get("provider")
        or not response.get("model_name")
        or not response.get("model_version")
    ):
        raise ValueError("provider, model_name, and model_version provenance are required")
    output = response.get("output")
    if not isinstance(output, dict):
        raise ValueError("response.output must be an object")
    return output


def _annotation_row(
    job: dict[str, Any],
    response: dict[str, Any],
    output: dict[str, Any],
    stage3_id: str,
) -> dict[str, Any]:
    source = job["_selection_provenance"]
    payload = job["input"]
    target = payload["patch"]["target_change_context"]
    review = payload["review"]
    claim = review["target_claim"]
    abstained = output.get("status") == "abstain"
    if output.get("status") not in {"labeled", "abstain"}:
        raise ValueError("candidate output.status must be labeled or abstain")
    category = output.get("relevance_category")
    if abstained:
        if category is not None:
            raise ValueError("abstentions must have relevance_category=null")
    elif category not in LABEL_CATEGORIES:
        raise ValueError("relevance_category must be one of 0, 1, 2, 3")
    confidence = output.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise ValueError("confidence must be in [0,1]")
    review_quote = output.get("review_evidence", "")
    claim_quote_start, claim_quote_end = _validate_quote(
        review_quote, claim["text"] or "", "review_evidence", required=category == 3
    )
    review_quote_start_full, review_quote_end_full = _validate_quote(
        review_quote, review["full_text"], "review_evidence/full_review", required=category == 3
    )
    if review_quote and claim_quote_start is None:
        raise ValueError("review evidence must be in the exact target claim")
    if category == 3 and review["created_at_utc"] < payload["patch"]["anchor_at_utc"]:
        raise ValueError("category 3 is impossible when the review predates the patch anchor")
    if category == 3 and not target.get("source_span_verified"):
        raise ValueError("category 3 requires a source-span-verified developer change")
    announcement_quote = output.get("announcement_evidence", "")
    change_source = target.get("source_span_raw") or target.get("change_text") or ""
    announcement_start, announcement_end = _validate_quote(
        announcement_quote, change_source, "announcement_evidence", required=category == 3
    )
    if announcement_start is not None:
        announcement_start += target.get("source_span_start") or 0
        announcement_end += target.get("source_span_start") or 0
        announcement_text = payload["patch"].get("announcement_text") or ""
        if (
            announcement_text
            and announcement_text[announcement_start:announcement_end] != announcement_quote
        ):
            raise ValueError(
                "announcement evidence offsets do not resolve inside the original announcement"
            )
    polarity = output.get("feature_polarity", "unknown")
    if polarity not in POLARITIES:
        raise ValueError(f"feature_polarity must be one of {sorted(POLARITIES)}")
    if not isinstance(output.get("explanation"), str) or not output["explanation"].strip():
        raise ValueError("explanation must be nonempty")
    # Save offsets into the complete review and the exact source span, not just the claim.
    if review_quote:
        review_quote_start_full = claim["start"] + claim_quote_start
        review_quote_end_full = review_quote_start_full + len(review_quote)
        if review["full_text"][review_quote_start_full:review_quote_end_full] != review_quote:
            raise ValueError("review evidence offsets do not resolve inside the full review")
    return {
        "label_id": _stable_id(
            "rv4_label",
            job["input_id"],
            response["provider"],
            response["model_name"],
            response["model_version"],
            json.dumps(output, ensure_ascii=False, sort_keys=True),
        ),
        "input_id": job["input_id"],
        "source_stage3_dataset_id": stage3_id,
        "source_candidate_id": source["source_candidate_id"],
        "patch_id": payload["patch"]["patch_id"],
        "game_id": payload["game"]["game_id"],
        "game_name": payload["game"]["game_name"],
        "patch_title": payload["patch"]["title"],
        "change_id": target["change_id"],
        "change_text": target["change_text"],
        "claim_id": claim["claim_id"],
        "review_revision_id": review["review_revision_id"],
        "review_id": review["review_id"],
        "claim_text": claim["text"],
        "review_text": review["full_text"],
        "relevance_category": category,
        "confidence": float(confidence),
        "review_evidence": review_quote,
        "review_evidence_start": review_quote_start_full,
        "review_evidence_end": review_quote_end_full,
        "announcement_evidence": announcement_quote,
        "announcement_evidence_start": announcement_start,
        "announcement_evidence_end": announcement_end,
        "explanation": output["explanation"],
        "feature_polarity": polarity,
        "ambiguity_reason": output.get("ambiguity_reason", ""),
        "abstained": abstained,
        "label_source": "silver_candidate_pair",
        "provider": response["provider"],
        "model_name": response["model_name"],
        "model_version": response["model_version"],
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": job["prompt_sha256"]
        if "prompt_sha256" in job
        else _prompt_sha("candidate_pair"),
        "source_review_created_at_utc": review["created_at_utc"],
        "patch_anchor_at_utc": payload["patch"]["anchor_at_utc"],
        "temporal_relation": payload["patch"]["review_temporal_relation"],
        "created_at_utc": datetime.now(UTC).isoformat(),
    }


def _build_split_manifest(labels: list[dict[str, Any]], stage2_root: Path) -> dict[str, Any]:
    labels = [
        row
        for row in labels
        if not row.get("abstained") and row.get("relevance_category") is not None
    ]
    overlaps = _read_table(stage2_root / "patch_episode_overlaps.parquet")
    parent: dict[str, str] = {}

    def find(value: str) -> str:
        parent.setdefault(value, value)
        if parent[value] != value:
            parent[value] = find(parent[value])
        return parent[value]

    def union(left: str, right: str) -> None:
        a, b = find(left), find(right)
        if a != b:
            parent[max(a, b)] = min(a, b)

    patch_keys = {label["patch_id"] for label in labels if label["patch_id"]}
    for patch_id in patch_keys:
        find(f"patch:{patch_id}")
    for row in overlaps:
        a, b = row["patch_id_a"], row["patch_id_b"]
        if a in patch_keys and b in patch_keys:
            union(f"patch:{a}", f"patch:{b}")
    for label in labels:
        find(f"review:{label['review_id']}")
    for i, left in enumerate(labels):
        for right in labels[i + 1 :]:
            same_review = left["review_id"] == right["review_id"]
            same_patch_group = find(f"patch:{left['patch_id']}") == find(
                f"patch:{right['patch_id']}"
            )
            if same_review or same_patch_group:
                union(f"row:{left['input_id']}", f"row:{right['input_id']}")
            else:
                find(f"row:{left['input_id']}")
    components: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for label in labels:
        components[find(f"row:{label['input_id']}")].append(label)
    ordered = sorted(
        components.items(),
        key=lambda item: max((row.get("patch_anchor_at_utc") or "" for row in item[1]), default=""),
    )
    if not ordered:
        assignments = {}
        status = "no_non_abstained_labels"
        reason = "No labeled candidate pairs are available for partitioning."
    elif len(ordered) < 3:
        assignments = {label["input_id"]: "unassigned" for label in labels}
        status = "pilot_insufficient_independent_groups"
        reason = (
            "Fewer than three independent review/patch groups remain after grouping all revisions "
            "of a review and overlapping patch episodes; train/validation/test would be misleading."
        )
    else:
        n = len(ordered)
        train_end = max(1, int(n * 0.70))
        validation_end = max(train_end + 1, int(n * 0.85))
        validation_end = min(validation_end, n - 1)
        assignments = {}
        for i, (_, rows) in enumerate(ordered):
            partition = "train" if i < train_end else "validation" if i < validation_end else "test"
            for label in rows:
                assignments[label["input_id"]] = partition
        status, reason = (
            "created_grouped_chronological_partitions",
            "Whole connected review/patch groups kept together.",
        )
    groups = []
    for group_id, rows in ordered:
        groups.append(
            {
                "group_id": _stable_id("rv4_split_group", group_id),
                "input_ids": [row["input_id"] for row in rows],
                "review_ids": sorted({row["review_id"] for row in rows}),
                "patch_ids": sorted({row["patch_id"] for row in rows}),
                "latest_patch_anchor_at_utc": max(
                    (row.get("patch_anchor_at_utc") or "" for row in rows), default=None
                ),
                "partition": assignments.get(rows[0]["input_id"], "unassigned"),
            }
        )
    positive_games = {row["game_name"] for row in labels if row.get("relevance_category") in {2, 3}}
    observed_games = {row["game_name"] for row in labels}
    return {
        "status": status,
        "reason": reason,
        "rule": "union rows by same Steam review_id or patch episodes connected by Stage 2 overlap table; chronological component ordering",
        "counts": dict(Counter(assignments.values())),
        "assignments": assignments,
        "groups": groups,
        "held_out_game_evaluation": {
            "status": "not_supported",
            "reason": (
                f"Only {len(positive_games)} of {len(observed_games)} sampled games have category 2–3 "
                "candidate labels; this pilot is too small to hold out a game while retaining "
                "useful positive training coverage."
            ),
        },
    }


def _audit_finding_row(
    job: dict[str, Any],
    response: dict[str, Any],
    pair: dict[str, Any],
    candidate_lookup: dict[tuple[str, str, str], dict[str, Any]],
    stage3_id: str,
) -> dict[str, Any]:
    payload = job["input"]
    review = payload["review"]
    patch = payload["patch"]
    change_id = pair["change_id"]
    change_entry = next(row for row in patch["full_change_list"] if row["change_id"] == change_id)
    claim_id = pair.get("claim_id")
    extracted_claim = (
        next((row for row in review["extracted_claims"] if row["claim_id"] == claim_id), None)
        if claim_id
        else None
    )
    if claim_id and not extracted_claim:
        raise ValueError("audit claim_id is not present in the supplied extracted claims")
    review_quote = pair.get("claim_evidence", "")
    review_start, review_end = _validate_quote(
        review_quote, review["full_text"], "audit claim_evidence", required=True
    )
    if extracted_claim:
        if review_quote not in extracted_claim["text"]:
            raise ValueError("audit claim_evidence is not contained in the referenced claim")
    note_text = change_entry.get("source_span_raw") or change_entry.get("change_text") or ""
    announcement_start, announcement_end = _validate_quote(
        pair.get("announcement_evidence", ""),
        note_text,
        "audit announcement_evidence",
        required=True,
    )
    if announcement_start is not None:
        announcement_start += change_entry.get("source_span_start") or 0
        announcement_end += change_entry.get("source_span_start") or 0
    category = pair.get("relevance_category")
    if category not in {1, 2, 3}:
        raise ValueError("audit discovered_pairs must have relevance category 1, 2, or 3")
    if category == 3 and review["created_at_utc"] < patch["anchor_at_utc"]:
        raise ValueError("audit category 3 is impossible when the review predates the patch anchor")
    if category == 3 and not change_entry.get("source_span_verified"):
        raise ValueError("audit category 3 requires a source-span-verified change")
    confidence = pair.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise ValueError("audit pair confidence must be in [0,1]")
    key = (patch["patch_id"], change_id, review["review_revision_id"])
    candidate = candidate_lookup.get(key)
    polarity = pair.get("feature_polarity", "unknown")
    if polarity not in POLARITIES:
        raise ValueError("invalid feature_polarity in audit pair")
    return {
        "audit_finding_id": _stable_id(
            "rv4_audit_finding", job["input_id"], change_id, review_quote
        ),
        "input_id": job["input_id"],
        "source_stage3_dataset_id": stage3_id,
        "source_audit_id": job["_selection_provenance"]["source_audit_id"],
        "source_candidate_id": candidate["candidate_id"] if candidate else None,
        "retrieval_omission": candidate is None and category >= 2,
        "game_id": payload["game"]["game_id"],
        "game_name": payload["game"]["game_name"],
        "patch_title": patch["title"],
        "patch_id": patch["patch_id"],
        "change_id": change_id,
        "change_text": change_entry.get("change_text"),
        "claim_id": claim_id,
        "review_revision_id": review["review_revision_id"],
        "review_id": review["review_id"],
        "claim_text": extracted_claim["text"] if extracted_claim else review_quote,
        "review_text": review["full_text"],
        "relevance_category": category,
        "confidence": float(confidence),
        "review_evidence": review_quote,
        "review_evidence_start": review_start,
        "review_evidence_end": review_end,
        "announcement_evidence": pair["announcement_evidence"],
        "announcement_evidence_start": announcement_start,
        "announcement_evidence_end": announcement_end,
        "explanation": pair.get("explanation", ""),
        "feature_polarity": polarity,
        "ambiguity_reason": pair.get("ambiguity_reason", ""),
        "provider": response["provider"],
        "model_name": response["model_name"],
        "model_version": response["model_version"],
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": job["prompt_sha256"],
    }


def _write_report(
    report_path: Path,
    *,
    run_id: str,
    candidate_labels: list[dict[str, Any]],
    audit_findings: list[dict[str, Any]],
    validation_errors: list[str],
    split_manifest: dict[str, Any],
    expected_audit_count: int,
    responses_count: int,
) -> None:
    category_counts = Counter(
        str(row["relevance_category"]) if row["relevance_category"] is not None else "abstain"
        for row in candidate_labels
    )
    positive = [row for row in candidate_labels if row["relevance_category"] in {2, 3}]
    strong = [row for row in candidate_labels if row["relevance_category"] == 3]
    games = sorted({row["game_name"] for row in positive})
    patches = sorted({row["patch_id"] for row in positive})
    omitted = [row for row in audit_findings if row["retrieval_omission"]]
    readiness = (
        "not ready for relevance-model fine-tuning"
        if len(positive) < 30
        or len(games) < 3
        or split_manifest["status"] != "created_grouped_chronological_partitions"
        else "pilot labels exist; evaluation design still requires human verification"
    )
    lines = [
        f"# Stage 4 silver-label pilot — `{run_id}`",
        "",
        "This is a bounded pilot. All judgments are LLM-generated silver labels from a single assistant session; no person reviewed or verified them. Do not treat confidence as calibrated probability.",
        "",
        "## Scope",
        "",
        f"- Candidate-pair responses accepted: {responses_count}; candidate labels accepted: {len(candidate_labels)}.",
        f"- Independent full-list audit jobs selected: {expected_audit_count}; audit findings: {len(audit_findings)}.",
        f"- Candidate relevance counts: {json.dumps(dict(category_counts), sort_keys=True)}.",
        f"- Category 2–3 candidate positives: {len(positive)}; category 3: {len(strong)}; games: {len(games)}; patch episodes: {len(patches)}.",
        f"- Independent-audit category 2–3 findings: {sum(row['relevance_category'] >= 2 for row in audit_findings)}; retrieval omissions among those: {len(omitted)}.",
        f"- Evidence/schema validation failures: {len(validation_errors)}.",
        "",
        "## Interpretation",
        "",
        f"Readiness recommendation: **{readiness}**. This pilot is too small and machine-only to establish a reliable evaluation set. The audit is a tiny stratified probe, not a corpus-wide recall estimate.",
        "Category 0/1/2/3 describes change-specific relevance only. Feature polarity is stored separately. Stage 1 review recommendation was not used.",
        "The full-list audit job and its findings remain separate from candidate labels; category 2–3 omissions are a machine-discovered retrieval-miss signal, not verified ground truth.",
        "",
        "## Positive coverage by game and patch",
        "",
    ]
    coverage: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in positive:
        coverage[(row["game_name"], row["patch_title"])].append(row)
    if not coverage:
        lines.append("No category 2–3 candidate labels in this pilot.")
    else:
        for (game, patch), rows in sorted(coverage.items()):
            lines.append(
                f"- {game} — {patch}: {len(rows)} category 2–3 labels ({sum(row['relevance_category'] == 3 for row in rows)} category 3)."
            )
    lines.extend(
        [
            "",
            "## Audited examples",
            "",
        ]
    )
    examples = strong[:4] + [row for row in positive if row["relevance_category"] == 2][:4]
    if not examples:
        lines.append("No positive candidate examples.")
    for row in examples:
        lines.extend(
            [
                f"### {row['game_name']} — category {row['relevance_category']} ({row['confidence']:.2f})",
                "",
                f"Change: {row['change_text']}",
                f"Claim: {row['claim_text']}",
                f"Evidence: review `{row['review_evidence']}`; note `{row['announcement_evidence']}`.",
                f"Reason: {row['explanation']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Split and evaluation status",
            "",
            f"- Split status: `{split_manifest['status']}`; groups: {len(split_manifest['groups'])}; partitions: {json.dumps(split_manifest['counts'], sort_keys=True)}.",
            f"- {split_manifest['reason']}",
            f"- Held-out-game evaluation: {split_manifest['held_out_game_evaluation']['status']} — {split_manifest['held_out_game_evaluation']['reason']}",
            "- No training, threshold calibration, or model selection should use these pilot labels.",
            "",
            "## Limitations and next action",
            "",
            "The candidate sample is intentionally stratified across hard cases, semantic-only discoveries, specific lexical overlap, and top fused ranks; its label distribution does not estimate corpus prevalence. The independent audit samples complete patch lists but only a few reviews. A category 3 label requires quote-span validation, but exact quotes alone do not prove causal attribution.",
            "Review the human-inspection queue before scaling. Human reviewers should independently inspect likely category 2/3 cases, low-confidence disagreements, and any candidate-independent omissions. The queue is explicitly marked unreviewed.",
            "",
        ]
    )
    if validation_errors:
        lines.extend(["## Rejected responses", ""])
        lines.extend(f"- {message}" for message in validation_errors)
        lines.append("")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def import_annotation_responses(
    *,
    repo_root: Path,
    run_id: str,
    responses_path: Path,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    report_root: Path = DEFAULT_REPORT_ROOT,
) -> dict[str, Any]:
    output_dir = repo_root / output_root / run_id
    report_dir = repo_root / report_root / run_id
    manifest_path = output_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("dataset_id") != run_id or manifest.get("status") not in {
        "awaiting_silver_responses",
        "silver_pilot_completed",
        "silver_pilot_partial",
    }:
        raise ValueError(f"Stage 4 job manifest not found or is in an unsupported state: {run_id}")
    responses_sha256 = _sha(responses_path.read_bytes())
    receipt_path = output_dir / "import_receipt.json"
    if manifest.get("status") == "silver_pilot_completed" and receipt_path.exists():
        previous_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if previous_receipt.get("responses_sha256") != responses_sha256:
            raise ValueError(
                "This completed Stage 4 run already has a different response file; export a new run "
                "instead of replacing its silver labels."
            )
        return {
            "status": manifest["status"],
            "dataset_id": run_id,
            "candidate_silver_labels": manifest["counts"].get(
                "candidate_silver_labels_accepted", 0
            ),
            "independent_audit_findings": manifest["counts"].get("independent_audit_findings", 0),
            "category_2_3_audit_omissions": manifest["counts"].get(
                "retrieval_omissions_category_2_or_3", 0
            ),
            "validation_errors": manifest["counts"].get("invalid_responses", 0),
            "unanswered_jobs": manifest["counts"].get("unanswered_jobs", 0),
            "output": manifest["paths"]["output"],
            "report": manifest["paths"]["readiness_report"],
            "readiness": "not_ready_for_fine_tuning",
            "idempotent_reimport": True,
        }
    jobs = _read_jsonl(output_dir / "annotation_jobs.jsonl")
    selection_manifest = json.loads(
        (output_dir / "selection_manifest.json").read_text(encoding="utf-8")
    )
    selection_by_id = {row["input_id"]: row for row in selection_manifest["selected_inputs"]}
    for job in jobs:
        job["_selection_provenance"] = selection_by_id.get(job["input_id"], {})
    responses = _read_jsonl(responses_path)
    job_by_id = {job["input_id"]: job for job in jobs}
    response_by_id = {}
    for response in responses:
        input_id = response.get("input_id")
        if input_id in response_by_id:
            raise ValueError(f"Duplicate response input_id: {input_id}")
        if input_id not in job_by_id:
            raise ValueError(f"Response has unknown input_id: {input_id}")
        response_by_id[input_id] = response
    stage3_id = manifest["source_ids"]["source_stage3_dataset_id"]
    stage3_root = repo_root / "data/relevance_v1/processed/stage3" / stage3_id
    stage2_id = manifest["source_ids"]["source_stage2_dataset_id"]
    stage2_root = repo_root / "data/relevance_v1/processed/stage2" / stage2_id
    stage3_candidates = _read_table(stage3_root / "candidate_pairs.parquet")
    candidate_lookup = {
        (row["patch_id"], row["change_id"], row["review_revision_id"]): row
        for row in stage3_candidates
    }
    candidate_labels: list[dict[str, Any]] = []
    audit_findings: list[dict[str, Any]] = []
    validation_errors: list[str] = []
    audit_job_count = 0
    response_candidate_count = 0
    response_audit_count = 0
    accepted_job_ids: set[str] = set()
    for input_id, response in response_by_id.items():
        job = job_by_id[input_id]
        try:
            output = _validate_common_response(response, job)
            if job["task_type"] == "candidate_pair":
                label = _annotation_row(job, response, output, stage3_id)
                candidate_labels.append(label)
                accepted_job_ids.add(input_id)
                response_candidate_count += 1
                continue
            audit_job_count += 1
            response_audit_count += 1
            patch = job["input"]["patch"]
            if output.get("full_change_list_examined") is not True:
                raise ValueError("independent audit must attest full_change_list_examined=true")
            if output.get("changes_examined_count") != patch["full_change_count"]:
                raise ValueError(
                    "independent audit changes_examined_count must match complete list size"
                )
            discovered = output.get("discovered_pairs")
            if not isinstance(discovered, list):
                raise ValueError("audit discovered_pairs must be a list")
            seen_pairs = set()
            current_findings = []
            for pair in discovered:
                pair_key = (pair.get("change_id"), pair.get("claim_evidence"))
                if pair_key in seen_pairs:
                    raise ValueError(f"duplicate audit pair in {input_id}: {pair_key}")
                seen_pairs.add(pair_key)
                if pair.get("change_id") not in {
                    row["change_id"] for row in patch["full_change_list"]
                }:
                    raise ValueError(
                        f"audit pair refers to change outside full list: {pair.get('change_id')}"
                    )
                current_findings.append(
                    _audit_finding_row(job, response, pair, candidate_lookup, stage3_id)
                )
            if not discovered and not isinstance(output.get("no_matches_reason"), str):
                raise ValueError("empty independent audit must explain no_matches_reason")
            audit_findings.extend(current_findings)
            accepted_job_ids.add(input_id)
        except (KeyError, TypeError, ValueError) as exc:
            validation_errors.append(f"{input_id}: {exc}")

    # Import is all-or-nothing for supplied rows: invalid responses are reported and excluded,
    # while missing responses remain explicit in the manifest and can be resumed later.
    _read_manifest(stage3_root / "manifest.json", stage3_id)
    _read_manifest(stage2_root / "manifest.json", stage2_id)
    candidate_schema = LABEL_SCHEMA
    pq.write_table(
        pa.Table.from_pylist(candidate_labels, schema=candidate_schema),
        output_dir / "silver_labels.parquet",
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(audit_findings, schema=AUDIT_SCHEMA),
        output_dir / "independent_audit_findings.parquet",
        compression="zstd",
    )
    split_manifest = _build_split_manifest(candidate_labels, stage2_root)
    (output_dir / "split_manifest.json").write_text(
        json.dumps(split_manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    queue_rows = []
    for row in candidate_labels:
        likely_relevant = row["relevance_category"] in {2, 3}
        low_confidence = row["confidence"] < 0.7 or row["abstained"]
        priority = "high" if likely_relevant or low_confidence else "normal"
        if likely_relevant:
            reason = "silver judgment suggests a specific-change match"
        elif low_confidence:
            reason = "low-confidence judgment or abstention"
        else:
            reason = "sampled negative or topical-only candidate"
        queue_rows.append(
            {
                "input_id": row["input_id"],
                "source": "candidate_pair_silver",
                "game_name": row["game_name"],
                "patch_title": row["patch_title"],
                "change_id": row["change_id"],
                "review_id": row["review_id"],
                "relevance_category": row["relevance_category"],
                "confidence": row["confidence"],
                "priority": priority,
                "reason": reason,
                "human_review_status": "not_reviewed",
                "recommended_independent_reviewers": 2 if priority == "high" else 1,
            }
        )
    for job in jobs:
        if job["task_type"] != "independent_full_list_audit":
            continue
        response = response_by_id.get(job["input_id"], {})
        output = response.get("output", {})
        findings = output.get("discovered_pairs", [])
        high = any(pair.get("relevance_category") in {2, 3} for pair in findings)
        queue_rows.append(
            {
                "input_id": job["input_id"],
                "source": "independent_full_list_audit",
                "game_name": job["input"]["game"]["game_name"],
                "patch_title": job["input"]["patch"]["title"],
                "change_id": "",
                "review_id": job["input"]["review"]["review_id"],
                "relevance_category": "",
                "confidence": "",
                "priority": "high" if high else "normal",
                "reason": "candidate-independent full-list result requires spot-check"
                if findings
                else "candidate-independent audit returned no topical change; spot-check the negative result",
                "human_review_status": "not_reviewed",
                "recommended_independent_reviewers": 2 if high else 1,
            }
        )
    for row in audit_findings:
        if row["retrieval_omission"]:
            priority = "highest"
            reason = "candidate-independent category 2–3 finding may be a retrieval omission"
        elif row["relevance_category"] == 3:
            priority = "highest"
            reason = "candidate-independent clear match requires verification"
        elif row["relevance_category"] == 2:
            priority = "high"
            reason = "candidate-independent plausible match requires verification"
        else:
            priority = "normal"
            reason = "candidate-independent topical-only finding; verify feature boundary"
        queue_rows.append(
            {
                "input_id": row["input_id"],
                "source": "independent_audit_finding",
                "game_name": row["game_name"],
                "patch_title": row["patch_title"],
                "change_id": row["change_id"],
                "review_id": row["review_id"],
                "relevance_category": row["relevance_category"],
                "confidence": row["confidence"],
                "priority": priority,
                "reason": reason,
                "human_review_status": "not_reviewed",
                "recommended_independent_reviewers": 2 if priority != "normal" else 1,
            }
        )
    with (output_dir / "human_inspection_queue.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        fields = list(queue_rows[0]) if queue_rows else ["input_id", "human_review_status"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(queue_rows)
    report_path = report_dir / "readiness_report.md"
    expected_audits = manifest["counts"]["independent_full_list_audit_inputs"]
    _write_report(
        report_path,
        run_id=run_id,
        candidate_labels=candidate_labels,
        audit_findings=audit_findings,
        validation_errors=validation_errors,
        split_manifest=split_manifest,
        expected_audit_count=expected_audits,
        responses_count=response_candidate_count,
    )
    missing_input_ids = sorted(set(job_by_id) - accepted_job_ids)
    import_status = (
        "silver_pilot_completed"
        if not missing_input_ids and not validation_errors
        else "silver_pilot_partial"
    )
    import_receipt = {
        "responses_sha256": responses_sha256,
        "accepted_candidate_label_count": len(candidate_labels),
        "accepted_audit_finding_count": len(audit_findings),
        "response_count": len(responses),
        "missing_input_ids": missing_input_ids,
        "validation_errors": validation_errors,
        "candidate_stage3_manifest_sha256": _sha((stage3_root / "manifest.json").read_bytes()),
        "source_stage2_manifest_sha256": _sha((stage2_root / "manifest.json").read_bytes()),
        "imported_at_utc": datetime.now(UTC).isoformat(),
    }
    (output_dir / "import_receipt.json").write_text(
        json.dumps(import_receipt, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    manifest.update(
        {
            "status": import_status,
            "labeling_completed_at_utc": datetime.now(UTC).isoformat(),
            "labeler_provenance": sorted(
                {
                    json.dumps(
                        {
                            "provider": response["provider"],
                            "model_name": response["model_name"],
                            "model_version": response["model_version"],
                        },
                        sort_keys=True,
                    )
                    for input_id, response in response_by_id.items()
                    if input_id in accepted_job_ids
                }
            ),
            "counts": {
                **manifest["counts"],
                "candidate_responses_received": response_candidate_count,
                "candidate_silver_labels_accepted": len(candidate_labels),
                "audit_responses_received": response_audit_count,
                "independent_audit_findings": len(audit_findings),
                "invalid_responses": len(validation_errors),
                "unanswered_jobs": len(import_receipt["missing_input_ids"]),
                "raw_responses_received": len(responses),
                "retrieval_omissions_category_2_or_3": sum(
                    row["retrieval_omission"] for row in audit_findings
                ),
            },
            "paths": {
                **manifest["paths"],
                "silver_labels": str(output_dir / "silver_labels.parquet"),
                "independent_audit_findings": str(
                    output_dir / "independent_audit_findings.parquet"
                ),
                "split_manifest": str(output_dir / "split_manifest.json"),
                "human_inspection_queue": str(output_dir / "human_inspection_queue.csv"),
                "readiness_report": str(report_path),
                "responses": str(responses_path),
                "import_receipt": str(output_dir / "import_receipt.json"),
            },
            "labeling_boundary": "All imported labels are silver LLM judgments; no human-verified gold labels exist.",
        }
    )
    (manifest_path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "status": manifest["status"],
        "dataset_id": run_id,
        "candidate_silver_labels": len(candidate_labels),
        "independent_audit_findings": len(audit_findings),
        "category_2_3_audit_omissions": manifest["counts"]["retrieval_omissions_category_2_or_3"],
        "validation_errors": len(validation_errors),
        "unanswered_jobs": len(import_receipt["missing_input_ids"]),
        "output": str(output_dir),
        "report": str(report_path),
        "readiness": "not_ready_for_fine_tuning",
    }
