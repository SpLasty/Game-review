from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from steam_patch_relevance.stage3.bm25 import BM25Index, tokenize
from steam_patch_relevance.stage3.dense import (
    SentenceTransformerEncoder,
    _snapshot_revision,
    top_cosine_hits,
)
from steam_patch_relevance.stage3.entity import GameVocabulary, aspect_family, entity_aspect_score
from steam_patch_relevance.stage3.pipeline import run_stage3


def _write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), path)


def test_bm25_accepts_one_content_token_and_ignores_sentiment_only_terms() -> None:
    index = BM25Index(
        [
            ("matching", "MAC-10 purchase price reduced"),
            ("sentiment-only", "bad broken awful unbalanced"),
            ("other", "Dota hero movement speed"),
        ]
    )

    assert [hit.item_id for hit in index.rank("MAC-10", limit=10)] == ["matching"]
    assert index.rank("bad broken awful", limit=10) == []
    assert "1050" in tokenize("price is now 1050")


def test_entity_aliases_are_game_scoped_and_aspect_families_allow_wording_variants() -> None:
    vocabulary = GameVocabulary(
        [
            {
                "term": "MAC-10",
                "normalized_term": "mac 10",
                "aliases": ["MAC10"],
                "is_entity_matchable": True,
            }
        ]
    )
    change = {
        "entity": "MAC-10",
        "entity_candidates": [],
        "change_text": "Reduced the MAC-10 purchase price.",
        "heading_path": [],
        "aspect": "purchase price",
    }
    claim = {
        "referenced_entity": None,
        "claim_text_original": "MAC10 costs less now.",
        "aspect": "cost",
    }
    wrong_game_vocabulary = GameVocabulary([])

    score, entity_score, aspect_score, matched = entity_aspect_score(change, claim, vocabulary)
    wrong_game_score, wrong_game_entity_score, *_ = entity_aspect_score(
        change, claim, wrong_game_vocabulary
    )

    assert score == 3.0
    assert entity_score == 1.0
    assert aspect_score == 1.0
    assert matched == "mac 10"
    assert (
        wrong_game_score == 1.0
    )  # Aspect can retrieve a candidate without cross-game entity aliasing.
    assert wrong_game_entity_score == 0.0
    assert aspect_family("fire rate") == "fire_rate"


def test_dense_cosine_ranking_and_e5_query_passage_prefixes() -> None:
    hits = top_cosine_hits(
        np.asarray([1.0, 0.0], dtype=np.float32),
        np.asarray([[0.6, 0.8], [1.0, 0.0], [-1.0, 0.0]], dtype=np.float32),
        ["a", "b", "c"],
        limit=2,
    )

    assert hits[0] == ("b", 1.0)
    assert hits[1][0] == "a"
    assert hits[1][1] == pytest.approx(0.6)
    assert SentenceTransformerEncoder._prefix("entity changed", "query") == "query: entity changed"
    assert SentenceTransformerEncoder._prefix("review claim", "passage") == "passage: review claim"


def test_dense_cache_version_resolves_immutable_hugging_face_snapshot() -> None:
    snapshot = Path("cache/models--org--model/snapshots/0123456789abcdef0123456789abcdef01234567")
    assert _snapshot_revision(snapshot / "config.json") == snapshot.name
    assert _snapshot_revision(Path("cache/models--org--model/config.json")) is None


def _stage2_fixture(root: Path) -> tuple[str, str, str]:
    source_dataset = "rv2-fixture-stage3"
    source_stage1_run = "rv1-fixture-stage3"
    stage2_root = root / "data/relevance_v1/processed/stage2" / source_dataset
    stage1_root = root / "data/relevance_v1/normalized" / source_stage1_run
    patch_a = "rv2_patch_fixture_a"
    patch_b = "rv2_patch_fixture_b"
    patch_other_game = "rv2_patch_fixture_other_game"
    anchor = 1_700_000_000
    timestamp = datetime.fromtimestamp(anchor, UTC)
    changes = [
        {
            "change_id": "rv2_change_mac_price",
            "patch_id": patch_a,
            "game_id": 440,
            "game_name": "Team Fortress 2",
            "title": "Balance patch A",
            "published_at_utc": timestamp,
            "source_url": "https://example.test/patch-a",
            "source_span_start": 0,
            "source_span_end": 40,
            "source_span_raw": "Reduced the MAC-10 purchase price.",
            "change_text": "Reduced the MAC-10 purchase price.",
            "heading_path": ["Economy"],
            "entity": "MAC-10",
            "entity_candidates": [],
            "aspect": "purchase price",
            "action": "reduce",
            "direction": "decrease",
            "previous_value": "1100",
            "new_value": "1050",
            "developer_status": "implemented",
            "bug_symptom": None,
            "bug_trigger": None,
            "extraction_confidence": 0.9,
            "source_span_verified": True,
            "quality_flags": [],
        },
        {
            "change_id": "rv2_change_mac_fire_rate",
            "patch_id": patch_b,
            "game_id": 440,
            "game_name": "Team Fortress 2",
            "title": "Balance patch B",
            "published_at_utc": timestamp,
            "source_url": "https://example.test/patch-b",
            "source_span_start": 0,
            "source_span_end": 42,
            "source_span_raw": "Reduced the MAC-10 fire rate.",
            "change_text": "Reduced the MAC-10 fire rate.",
            "heading_path": ["Weapons"],
            "entity": "MAC-10",
            "entity_candidates": [],
            "aspect": "fire rate",
            "action": "reduce",
            "direction": "decrease",
            "previous_value": "900",
            "new_value": "850",
            "developer_status": "implemented",
            "bug_symptom": None,
            "bug_trigger": None,
            "extraction_confidence": 0.9,
            "source_span_verified": True,
            "quality_flags": [],
        },
        {
            "change_id": "rv2_change_other_game",
            "patch_id": patch_other_game,
            "game_id": 730,
            "game_name": "Counter-Strike 2",
            "title": "Other game patch",
            "published_at_utc": timestamp,
            "source_url": "https://example.test/patch-c",
            "source_span_start": 0,
            "source_span_end": 24,
            "source_span_raw": "Increased MAC-10 damage.",
            "change_text": "Increased MAC-10 damage.",
            "heading_path": [],
            "entity": "MAC-10",
            "entity_candidates": [],
            "aspect": "damage",
            "action": "increase",
            "direction": "increase",
            "previous_value": None,
            "new_value": None,
            "developer_status": "implemented",
            "bug_symptom": None,
            "bug_trigger": None,
            "extraction_confidence": 0.9,
            "source_span_verified": True,
            "quality_flags": [],
        },
    ]
    episodes = [
        {
            "patch_id": patch_id,
            "game_id": game_id,
            "game_name": game_name,
            "announcement_id": f"announcement-{patch_id}",
            "announcement_revision_id": f"revision-{patch_id}",
            "title": title,
            "source_url": f"https://example.test/{patch_id}",
            "published_at_utc": timestamp,
            "published_unix": anchor,
            "anchor_at_utc": timestamp,
            "anchor_unix": anchor,
            "anchor_source": "announcement_publication_time_unverified",
            "window_start_unix": anchor - 14 * 86400,
            "window_end_unix": anchor + 14 * 86400,
            "categories": ["balance"],
            "full_patch_notes_status": "body_present",
            "time_is_release_verified": False,
        }
        for patch_id, game_id, game_name, title in [
            (patch_a, 440, "Team Fortress 2", "Balance patch A"),
            (patch_b, 440, "Team Fortress 2", "Balance patch B"),
            (patch_other_game, 730, "Counter-Strike 2", "Other game patch"),
        ]
    ]
    claims = [
        {
            "claim_id": "rv2_claim_mac_price",
            "review_revision_id": "rv1_revision_price",
            "logical_revision_key": "review-price",
            "review_id": "review-price",
            "source_payload_sha256": "abc",
            "game_id": 440,
            "game_name": "Team Fortress 2",
            "review_created_at_utc": timestamp,
            "review_updated_at_utc": timestamp,
            "review_language": "english",
            "claim_text_original": "The MAC10 costs less now.",
            "referenced_entity": None,
            "aspect": "cost",
            "polarity": "positive",
            "temporal_cues": [],
            "negated": False,
            "uncertain": False,
            "opinion_or_issue": "costs less",
        },
        {
            "claim_id": "rv2_claim_sentiment_only",
            "review_revision_id": "rv1_revision_sentiment",
            "logical_revision_key": "review-sentiment",
            "review_id": "review-sentiment",
            "source_payload_sha256": "def",
            "game_id": 440,
            "game_name": "Team Fortress 2",
            "review_created_at_utc": timestamp,
            "review_updated_at_utc": timestamp,
            "review_language": "english",
            "claim_text_original": "Bad and broken.",
            "referenced_entity": None,
            "aspect": None,
            "polarity": "negative",
            "temporal_cues": [],
            "negated": False,
            "uncertain": False,
            "opinion_or_issue": "bad and broken",
        },
        {
            "claim_id": "rv2_claim_other_game",
            "review_revision_id": "rv1_revision_other_game",
            "logical_revision_key": "review-other-game",
            "review_id": "review-other-game",
            "source_payload_sha256": "ghi",
            "game_id": 730,
            "game_name": "Counter-Strike 2",
            "review_created_at_utc": timestamp,
            "review_updated_at_utc": timestamp,
            "review_language": "english",
            "claim_text_original": "MAC-10 damage feels higher.",
            "referenced_entity": "MAC-10",
            "aspect": "damage",
            "polarity": "positive",
            "temporal_cues": [],
            "negated": False,
            "uncertain": False,
            "opinion_or_issue": "damage feels higher",
        },
    ]
    memberships = []
    for patch_id, game_id, revisions in [
        (patch_a, 440, ["rv1_revision_price", "rv1_revision_sentiment"]),
        (patch_b, 440, ["rv1_revision_price"]),
        (patch_other_game, 730, ["rv1_revision_other_game"]),
    ]:
        for index, revision_id in enumerate(revisions):
            memberships.append(
                {
                    "membership_id": f"membership-{patch_id}-{revision_id}",
                    "patch_id": patch_id,
                    "source_patch_id": patch_id,
                    "game_id": game_id,
                    "announcement_id": f"announcement-{patch_id}",
                    "review_revision_id": revision_id,
                    "review_id": revision_id,
                    "window_segment": "after_0_7d" if index else "before_14d",
                    "window_start_unix": anchor - 14 * 86400,
                    "window_end_unix": anchor + 14 * 86400,
                    "anchor_unix": anchor,
                    "anchor_source": "announcement_publication_time_unverified",
                    "created_unix": anchor,
                    "membership_rule": "window",
                    "membership_semantics": "temporal_only",
                }
            )
    windows = [
        {
            "window_id": f"window-{patch_id}-{segment}",
            "patch_id": patch_id,
            "source_patch_id": patch_id,
            "game_id": game_id,
            "announcement_id": f"announcement-{patch_id}",
            "segment": segment,
            "start_unix": anchor - 14 * 86400,
            "end_unix": anchor + 14 * 86400,
            "start_at_utc": timestamp,
            "end_at_utc": timestamp,
            "anchor_unix": anchor,
            "anchor_source": "announcement_publication_time_unverified",
            "collection_status": "page_budget_reached",
            "page_count": 1,
            "unique_review_revisions": len(memberships),
            "unique_review_ids": len(memberships),
            "total_matching_reported": 10,
            "review_coverage_fraction": 0.5,
            "issues_json": "[]",
            "membership_semantics": "temporal_only",
        }
        for patch_id, game_id in [(patch_a, 440), (patch_b, 440), (patch_other_game, 730)]
        for segment in ["before_14d", "after_0_7d", "after_8_14d"]
    ]
    terminology = [
        {
            "term_id": "term-mac10",
            "game_id": 440,
            "game_name": "Team Fortress 2",
            "term": "MAC-10",
            "normalized_term": "mac 10",
            "aliases": ["MAC10"],
            "evidence_sources": ["patch"],
            "evidence_count": 1,
            "primary_evidence_source": "patch",
            "is_game_specific": True,
            "is_entity_matchable": True,
            "resource_version": "fixture",
        },
        {
            "term_id": "term-mac10-cs",
            "game_id": 730,
            "game_name": "Counter-Strike 2",
            "term": "MAC-10",
            "normalized_term": "mac 10",
            "aliases": ["MAC10"],
            "evidence_sources": ["patch"],
            "evidence_count": 1,
            "primary_evidence_source": "patch",
            "is_game_specific": True,
            "is_entity_matchable": True,
            "resource_version": "fixture",
        },
    ]
    for filename, rows in [
        ("patch_changes", changes),
        ("review_claims", claims),
        ("patch_episodes", episodes),
        ("patch_review_windows", windows),
        ("review_window_memberships", memberships),
        ("game_terminology", terminology),
    ]:
        _write_rows(stage2_root / f"{filename}.parquet", rows)
    (stage2_root / "manifest.json").write_text(
        json.dumps(
            {
                "dataset_id": source_dataset,
                "complete": True,
                "source_stage1_run_id": source_stage1_run,
            }
        ),
        encoding="utf-8",
    )
    reviews = [
        {
            "review_revision_id": revision_id,
            "recommendation_id": review_id,
            "created_at_utc": timestamp,
            "updated_at_utc": timestamp,
            "language": "english",
            "review_text_original": text,
        }
        for revision_id, review_id, text in [
            ("rv1_revision_price", "review-price", "The MAC10 costs less now. I like it."),
            ("rv1_revision_sentiment", "review-sentiment", "Bad and broken."),
            ("rv1_revision_other_game", "review-other-game", "MAC-10 damage feels higher."),
        ]
    ]
    _write_rows(stage1_root / "review_revisions.parquet", reviews)
    return source_dataset, patch_a, patch_b


def test_stage3_outputs_candidate_union_hard_cases_and_candidate_free_audit(tmp_path: Path) -> None:
    source_dataset, patch_a, patch_b = _stage2_fixture(tmp_path)

    result = run_stage3(
        repo_root=tmp_path,
        source_dataset=source_dataset,
        budgets=[1, 2],
        dense=False,
        audit_per_segment=2,
    )

    output = Path(result["output"])
    candidates = pq.read_table(output / "candidate_pairs.parquet").to_pylist()
    mac_price = [row for row in candidates if row["claim_id"] == "rv2_claim_mac_price"]
    audit_jobs = [
        json.loads(line)
        for line in (output / "audit_full_list.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    hard_rows = pq.read_table(output / "hard_negative_candidates.parquet").to_pylist()
    patch_diagnostics = pq.read_table(output / "patch_diagnostics.parquet").to_pylist()
    with (output / "game_diagnostics.csv").open(encoding="utf-8") as handle:
        game_names = {row["game_name"] for row in csv.DictReader(handle)}
    with (output / "budget_curves.csv").open(encoding="utf-8") as handle:
        overall_budget_rows = [row for row in csv.DictReader(handle) if row["scope"] == "overall"]

    assert {(row["patch_id"], row["change_id"]) for row in mac_price} == {
        (patch_a, "rv2_change_mac_price"),
        (patch_b, "rv2_change_mac_fire_rate"),
    }
    assert all("rv2_claim_sentiment_only" != row["claim_id"] for row in candidates)
    assert all(row["game_id"] == 440 for row in candidates if row["patch_id"] in {patch_a, patch_b})
    assert all(
        row["patch_id"] != patch_a and row["patch_id"] != patch_b
        for row in candidates
        if row["claim_id"] == "rv2_claim_other_game"
    )
    assert all(row["candidate_id"].startswith("rv3_candidate_") for row in candidates)
    assert all(row["other_window_patch_ids"] for row in mac_price)
    assert all(row["retrieval_methods"] for row in candidates)
    for row in candidates:
        expected_rrf = sum(
            1 / (60 + row[rank])
            for rank in ("bm25_rank", "dense_rank", "entity_aspect_rank")
            if row[rank] is not None
        )
        assert row["rrf_score"] == pytest.approx(expected_rrf)
    assert all("label" not in row and "relevance" not in row for row in audit_jobs)
    assert all(row["candidate_independent"] is True for row in audit_jobs)
    assert all(row["full_change_count"] >= 1 for row in audit_jobs)
    assert all("candidate_id" not in row and "dense_rank" not in row for row in audit_jobs)
    assert all("label" not in row and "relevance" not in row for row in hard_rows)
    assert any("same_entity_different_aspect" in row["hard_case_types"] for row in hard_rows)
    assert {row["patch_id"] for row in patch_diagnostics} >= {patch_a, patch_b}
    assert {"Team Fortress 2", "Counter-Strike 2"} <= game_names
    assert manifest["counts"]["candidate_pairs"] == len(candidates)
    assert manifest["budget_curves_interpretation"].startswith("candidate yield")
    assert [int(row["budget_per_change_per_method"]) for row in overall_budget_rows] == [1, 2]
    assert [int(row["hybrid_union_pairs"]) for row in overall_budget_rows] == sorted(
        int(row["hybrid_union_pairs"]) for row in overall_budget_rows
    )
    assert (output / "hard_negative_candidates.parquet").exists()
    assert (output / "budget_curves.csv").exists()
