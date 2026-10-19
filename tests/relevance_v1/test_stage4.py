from __future__ import annotations

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from steam_patch_relevance.stage4.pipeline import (
    _annotation_row,
    _build_audit_job,
    _build_split_manifest,
    _select_candidates,
    _validate_common_response,
    export_full_list_review_audit,
    import_annotation_responses,
)


def _candidate_job(*, review_at: str = "2026-10-02T00:00:00+00:00"):
    return {
        "input_id": "rv4_input_fixture",
        "task_type": "candidate_pair",
        "_selection_provenance": {"source_candidate_id": "rv3_candidate_fixture"},
        "input": {
            "game": {"game_id": 730, "game_name": "Counter-Strike 2"},
            "patch": {
                "patch_id": "rv2_patch_fixture",
                "title": "Balance Update",
                "anchor_at_utc": "2026-10-01T00:00:00+00:00",
                "review_temporal_relation": "after_patch_0_7d",
                "target_change_context": {
                    "change_id": "rv2_change_fixture",
                    "change_text": "Reduced the MAC-10 purchase price.",
                    "source_span_raw": "Reduced the MAC-10 purchase price.",
                    "source_span_verified": True,
                },
            },
            "review": {
                "review_id": "123",
                "review_revision_id": "rv1_review_fixture",
                "created_at_utc": review_at,
                "full_text": "The reduced MAC-10 price makes eco rounds easier.",
                "target_claim": {
                    "claim_id": "rv2_claim_fixture",
                    "text": "The reduced MAC-10 price makes eco rounds easier.",
                    "start": 0,
                    "end": 49,
                },
            },
        },
    }


def _response(job, output):
    return {
        "input_id": job["input_id"],
        "provider": "fixture",
        "model_name": "fixture-model",
        "model_version": "fixture-rev-1",
        "prompt_version": "patch-review-silver-v1",
        "output": output,
    }


def test_category_three_requires_verbatim_review_and_change_evidence():
    job = _candidate_job()
    output = {
        "status": "labeled",
        "relevance_category": 3,
        "confidence": 0.91,
        "review_evidence": "The reduced MAC-10 price makes eco rounds easier.",
        "announcement_evidence": "Reduced the MAC-10 purchase price.",
        "explanation": "The review explicitly attributes the eco-round effect to the price reduction.",
        "feature_polarity": "positive",
        "ambiguity_reason": "",
    }
    row = _annotation_row(job, _response(job, output), output, "rv3-fixture")
    assert row["relevance_category"] == 3
    assert row["feature_polarity"] == "positive"
    assert row["review_evidence_start"] == 0
    assert row["review_evidence_end"] == len(job["input"]["review"]["full_text"])
    assert row["label_source"] == "silver_candidate_pair"


def test_category_three_rejects_fabricated_quotes():
    job = _candidate_job()
    output = {
        "status": "labeled",
        "relevance_category": 3,
        "confidence": 0.9,
        "review_evidence": "This update made eco rounds easier.",
        "announcement_evidence": "Reduced the MAC-10 purchase price.",
        "explanation": "specific attribution",
        "feature_polarity": "positive",
    }
    with pytest.raises(ValueError, match="exact substring"):
        _annotation_row(job, _response(job, output), output, "rv3-fixture")


def test_category_three_rejected_for_pre_patch_review():
    job = _candidate_job(review_at="2026-09-30T00:00:00+00:00")
    output = {
        "status": "labeled",
        "relevance_category": 3,
        "confidence": 0.9,
        "review_evidence": "The reduced MAC-10 price makes eco rounds easier.",
        "announcement_evidence": "Reduced the MAC-10 purchase price.",
        "explanation": "specific attribution",
        "feature_polarity": "positive",
    }
    with pytest.raises(ValueError, match="predates the patch anchor"):
        _annotation_row(job, _response(job, output), output, "rv3-fixture")


def test_abstention_has_no_relevance_category_and_keeps_sentiment_separate():
    job = _candidate_job()
    output = {
        "status": "abstain",
        "relevance_category": None,
        "confidence": 0.42,
        "review_evidence": "",
        "announcement_evidence": "",
        "explanation": "The review is too vague to attribute.",
        "feature_polarity": "unknown",
        "ambiguity_reason": "No specific mechanic is mentioned.",
    }
    row = _annotation_row(job, _response(job, output), output, "rv3-fixture")
    assert row["abstained"] is True
    assert row["relevance_category"] is None
    assert row["feature_polarity"] == "unknown"


def test_full_list_audit_job_contains_no_retrieval_metadata():
    audit = {
        "audit_id": "rv3_audit_fixture",
        "selection_rule": "sampled before retrieval",
        "selection_seed": "fixture",
        "patch_id": "rv2_patch_fixture",
        "game_id": 730,
        "game_name": "Counter-Strike 2",
        "patch_title": "Balance Update",
        "patch_source_url": "https://example.test/patch",
        "patch_anchor_at_utc": "2026-10-01T00:00:00+00:00",
        "patch_anchor_source": "publication_time",
        "window_segment": "after_0_7d",
        "window_collection_status": "complete",
        "window_review_coverage_fraction": 1.0,
        "review_revision_id": "rv1_review_fixture",
        "review_id": "123",
        "review_created_at_utc": "2026-10-02T00:00:00+00:00",
        "review_updated_at_utc": "2026-10-02T00:00:00+00:00",
        "review_language": "english",
        "review_text": "The reduced MAC-10 price makes eco rounds easier.",
        "full_change_count": 1,
        "full_change_list": [{"change_id": "rv2_change_fixture", "change_text": "Reduced price."}],
    }
    job = _build_audit_job(audit, input_id="rv4_input_fixture", claims_by_revision={})
    assert job["candidate_independent"] is True
    assert job["input"]["patch"]["full_change_count"] == 1
    assert job["input"]["patch"]["full_change_list"][0]["number"] == 1
    assert "candidate_id" not in job["input"]
    assert "fused_rank" not in job["input"]
    assert job["task_type"] == "independent_full_list_audit"


def test_full_list_audit_export_samples_unique_reviews_independent_of_stage3(tmp_path):
    import json
    from pathlib import Path

    import pyarrow as pa
    import pyarrow.parquet as pq

    source_dataset = "rv2-fixture"
    stage2 = tmp_path / "data/relevance_v1/processed/stage2" / source_dataset
    stage1 = tmp_path / "data/relevance_v1/normalized/rv1-fixture"
    stage2.mkdir(parents=True)
    stage1.mkdir(parents=True)
    (stage2 / "manifest.json").write_text(
        json.dumps(
            {
                "dataset_id": source_dataset,
                "complete": True,
                "source_stage1_run_id": "rv1-fixture",
            }
        ),
        encoding="utf-8",
    )
    pq.write_table(
        pa.Table.from_pylist(
            [
                {
                    "patch_id": "patch-x",
                    "game_id": 553850,
                    "game_name": "HELLDIVERS 2",
                    "title": "Big Update",
                    "source_url": "https://example.test/patch",
                    "anchor_at_utc": "2026-01-01T00:00:00+00:00",
                    "anchor_source": "publication_time",
                }
            ]
        ),
        stage2 / "patch_episodes.parquet",
    )
    pq.write_table(
        pa.Table.from_pylist(
            [
                {
                    "patch_id": "patch-x",
                    "segment": "after_0_7d",
                    "collection_status": "complete",
                    "review_coverage_fraction": 1.0,
                }
            ]
        ),
        stage2 / "patch_review_windows.parquet",
    )
    pq.write_table(
        pa.Table.from_pylist(
            [
                {
                    "patch_id": "patch-x",
                    "change_id": "change-x",
                    "source_span_verified": True,
                    "developer_status": "implemented_change",
                    "source_span_start": 0,
                    "source_span_end": 20,
                    "source_span_raw": "Added a new weapon.",
                    "change_text": "Added a new weapon.",
                    "source_url": "https://example.test/patch",
                    "heading_path": [],
                }
            ]
        ),
        stage2 / "patch_changes.parquet",
    )
    revisions = [
        {
            "review_revision_id": f"rev-{i}",
            "review_id": f"review-{i}",
            "appid": 553850,
            "created_unix": 1_767_225_600 + i,
            "updated_unix": 1_767_225_600 + i,
            "created_at_utc": "2026-01-02T00:00:00+00:00",
            "updated_at_utc": "2026-01-02T00:00:00+00:00",
            "language": "english",
            "review_text_original": f"Review text {i}",
        }
        for i in range(3)
    ]
    pq.write_table(pa.Table.from_pylist(revisions), stage1 / "review_revisions.parquet")
    pq.write_table(
        pa.Table.from_pylist(
            [
                {
                    "patch_id": "patch-x",
                    "window_segment": "after_0_7d",
                    "review_revision_id": f"rev-{i}",
                    "review_id": f"review-{i}",
                }
                for i in range(3)
            ]
        ),
        stage2 / "review_window_memberships.parquet",
    )
    pq.write_table(pa.table({"review_revision_id": [], "claim_id": []}), stage2 / "review_claims.parquet")

    result = export_full_list_review_audit(
        repo_root=tmp_path,
        source_dataset=source_dataset,
        patch_id="patch-x",
        review_count=2,
        seed="fixed",
        output_root=Path("out"),
        report_root=Path("reports"),
    )
    jobs_path = Path(result["output"]) / "annotation_jobs.jsonl"
    jobs = [json.loads(line) for line in jobs_path.read_text(encoding="utf-8").splitlines()]
    assert len(jobs) == 2
    assert len({job["input"]["review"]["review_id"] for job in jobs}) == 2
    assert all(job["candidate_independent"] for job in jobs)
    assert all(len(job["input"]["patch"]["full_change_list"]) == 1 for job in jobs)
    manifest = json.loads((Path(result["output"]) / "manifest.json").read_text())
    assert manifest["source_ids"]["source_stage2_dataset_id"] == source_dataset
    assert manifest["source_ids"]["source_stage3_dataset_id"]
    assert manifest["counts"]["candidate_pair_inputs"] == 0
    assert manifest["counts"]["independent_full_list_audit_inputs"] == 2
    assert not (tmp_path / "data/relevance_v1/processed/stage3").exists()


def test_common_response_requires_exact_exported_prompt_hash():
    job = {
        "input_id": "rv4_input_fixture",
        "prompt_sha256": "expected-hash",
    }
    response = {
        "input_id": job["input_id"],
        "prompt_version": "patch-review-silver-v1",
        "prompt_sha256": "wrong-hash",
        "provider": "fixture",
        "model_name": "fixture-model",
        "model_version": "fixture-rev-1",
        "output": {},
    }
    with pytest.raises(ValueError, match="prompt_sha256"):
        _validate_common_response(response, job)


def test_split_manifest_reports_supported_positive_game_coverage(tmp_path):
    pq.write_table(
        pa.table(
            {
                "patch_id_a": pa.array([], type=pa.string()),
                "patch_id_b": pa.array([], type=pa.string()),
            }
        ),
        tmp_path / "patch_episode_overlaps.parquet",
    )
    labels = [
        {
            "input_id": f"input-{index}",
            "patch_id": f"patch-{index}",
            "review_id": f"review-{index}",
            "game_name": game,
            "patch_anchor_at_utc": f"2026-10-0{index + 1}T00:00:00+00:00",
            "relevance_category": category,
            "abstained": False,
        }
        for index, (game, category) in enumerate([("A", 2), ("B", 3), ("C", 0)], start=1)
    ]
    manifest = _build_split_manifest(labels, tmp_path)
    assert manifest["held_out_game_evaluation"]["status"] == "not_supported"
    assert "Only 2 of 3 sampled games" in manifest["held_out_game_evaluation"]["reason"]


def test_completed_run_reimport_is_idempotent_and_rejects_changed_responses(tmp_path):
    import hashlib
    import json
    from pathlib import Path

    run_id = "rv4-fixture-run"
    output_dir = tmp_path / "out" / run_id
    output_dir.mkdir(parents=True)
    responses = tmp_path / "responses.jsonl"
    responses.write_text("same response", encoding="utf-8")
    response_hash = hashlib.sha256(responses.read_bytes()).hexdigest()
    (output_dir / "manifest.json").write_text(
        json.dumps(
            {
                "dataset_id": run_id,
                "status": "silver_pilot_completed",
                "counts": {
                    "candidate_silver_labels_accepted": 2,
                    "independent_audit_findings": 1,
                    "retrieval_omissions_category_2_or_3": 0,
                    "invalid_responses": 0,
                    "unanswered_jobs": 0,
                },
                "paths": {
                    "output": str(output_dir),
                    "readiness_report": str(tmp_path / "report.md"),
                },
            }
        ),
        encoding="utf-8",
    )
    (output_dir / "import_receipt.json").write_text(
        json.dumps({"responses_sha256": response_hash}), encoding="utf-8"
    )

    result = import_annotation_responses(
        repo_root=tmp_path,
        run_id=run_id,
        responses_path=responses,
        output_root=Path("out"),
        report_root=Path("reports"),
    )
    assert result["idempotent_reimport"] is True
    assert result["candidate_silver_labels"] == 2

    responses.write_text("different response", encoding="utf-8")
    with pytest.raises(ValueError, match="different response file"):
        import_annotation_responses(
            repo_root=tmp_path,
            run_id=run_id,
            responses_path=responses,
            output_root=Path("out"),
            report_root=Path("reports"),
        )


def test_candidate_sampler_is_seed_deterministic_and_game_stratified():
    candidates = []
    hard = []
    for game in ("A", "B", "C"):
        for index in range(20):
            row = {
                "candidate_id": f"{game}-{index}",
                "game_name": game,
                "change_id": f"change-{game}-{index}",
                "review_revision_id": f"review-{game}-{index}",
                "dense_rank": index + 1,
                "bm25_rank": None if index < 10 else index + 1,
                "entity_aspect_rank": None,
                "fused_rank": index + 1,
            }
            candidates.append(row)
            if index < 4:
                hard.append(row)
    first, first_counts = _select_candidates(candidates, hard, per_game=8, seed="fixed")
    second, second_counts = _select_candidates(candidates, hard, per_game=8, seed="fixed")
    assert [row[0]["candidate_id"] for row in first] == [row[0]["candidate_id"] for row in second]
    assert len(first) == 24
    assert len({row[0]["game_name"] for row in first}) == 3
    assert first_counts == second_counts
