import csv
import json
import unittest

import test_pipeline_datasets as fixtures

from steam_insights.pipeline.llm_annotations import (
    _evidence,
    export_llm_job,
    import_llm_responses,
    read_responses,
)
from steam_insights.pipeline.loader import iter_model_batches, latest_dataset
from steam_insights.pipeline.runner import run_pipeline
from steam_insights.pipeline.storage import read_table


class LLMWorkflowTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.FullPipelineTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.root, self.config = fixture.root, fixture.config
        texts = {
            "1": "Terminal crashes ruin my tactical rifle battles and competitive multiplayer matches every evening.",
            "2": "Terminal crashes interrupt dragon exploration across enchanted forests filled with treasure and magic.",
            "3": "Terminal crashes destroy agriculture production during harvest because tractor simulation loses saved crops.",
        }
        fixture.review_frame["review_text"] = fixture.review_frame["appid"].map(texts)
        fixture.review_frame.to_csv(self.config.data.source("reviews"), index=False)
        run_pipeline(self.config)
        self.directory = latest_dataset(self.config)
        self.job = self.root / "job"
        export_llm_job(self.directory, self.job, sample_size=100, batch_size=1)
        self.requests = [
            json.loads(s) for s in (self.job / "requests.jsonl").read_text().splitlines()
        ]
        self.assertTrue(self.requests)

    def response(self):
        request = self.requests[0]
        return {
            "candidate_id": request["candidate_id"],
            "relevance": "relevant",
            "sentiment": "negative",
            "fix_status": "released_fix",
            "review_evidence": {"text": request["review_text"]},
            "change_evidence": {"text": request["change_text"]},
            "rationale": "The review describes the same terminal crash addressed by the change.",
            "confidence": 0.85,
        }

    def submit(self, response, *, run_id="pass-1"):
        path = self.root / "responses.jsonl"
        path.write_text(json.dumps(response) + "\n")
        return import_llm_responses(
            self.config, self.job, path, model_name="test-model", run_id=run_id
        )

    def test_self_contained_jobs_keep_full_context_and_development_isolation(self):
        manifest = json.loads((self.job / "manifest.json").read_text())
        self.assertTrue(all(r["split"] != "test" for r in self.requests))
        batch = (self.job / manifest["batches"][0]["file"]).read_text()
        self.assertIn("untrusted quoted data", batch)
        self.assertIn("announcement_text", batch)
        self.assertIn("not whether the fix actually worked", batch)
        self.assertNotIn("recommended", self.requests[0])
        with self.assertRaisesRegex(ValueError, "already exists"):
            export_llm_job(self.directory, self.job)

    def test_evidence_uses_unicode_offsets_and_repeated_quotes_need_disambiguation(self):
        self.assertEqual(
            _evidence({"text": "crash"}, "🎮 crash"), {"start": 2, "end": 7, "text": "crash"}
        )
        with self.assertRaisesRegex(ValueError, "repeated"):
            _evidence({"text": "crash"}, "crash crash")
        self.assertEqual(_evidence({"text": "crash", "start": 6}, "crash crash")["end"], 11)

    def test_machine_import_is_idempotent_and_never_enters_human_gold(self):
        first = self.submit(self.response())
        second = self.submit(self.response())
        self.assertEqual(first["machine_annotations"], second["machine_annotations"])
        self.assertEqual(first["machine_annotations"], 1)
        self.assertFalse(self.config.input("annotations").exists())
        result = run_pipeline(self.config)
        self.directory = latest_dataset(self.config)
        self.assertEqual(result["rows"]["annotations"], 0)
        self.assertEqual(result["rows"]["labeled_pairs"], 0)
        self.assertEqual(result["rows"]["silver_pairs"], 1)
        self.assertEqual(list(iter_model_batches(self.directory, labeled=True)), [])
        batches = list(iter_model_batches(self.directory, labeled=True, label_source="llm"))
        self.assertEqual(sum(b.num_rows for b in batches), 1)
        self.assertEqual(batches[0].to_pylist()[0]["label_source"], "llm")

    def test_patch_scoped_job_is_change_balanced_auditable_and_can_skip_labeled_pairs(self):
        candidates = read_table(self.directory, "candidates")
        patch_id = candidates[0]["patch_id"]
        patch_job = self.root / "patch-job"
        result = export_llm_job(
            self.directory,
            patch_job,
            sample_size=100,
            splits=("train", "validation", "test"),
            patch_id=patch_id,
        )
        patch_requests = [
            json.loads(line) for line in (patch_job / "requests.jsonl").read_text().splitlines()
        ]
        manifest = json.loads((patch_job / "manifest.json").read_text())
        with (patch_job / "retrieval_audit.csv").open(encoding="utf-8") as handle:
            audit = list(csv.DictReader(handle))

        self.assertEqual(result["examples"], len(patch_requests))
        self.assertTrue(patch_requests)
        self.assertEqual(manifest["patch_id"], patch_id)
        self.assertEqual(manifest["sampling_strategy"], "round_robin_by_change_task_split")
        candidates_by_id = {row["candidate_id"]: row for row in candidates}
        self.assertTrue(
            all(
                candidates_by_id[row["candidate_id"]]["patch_id"] == patch_id
                for row in patch_requests
            )
        )
        self.assertTrue(all(row["patch_id"] == patch_id for row in audit))
        self.assertEqual(
            sum(row["sampled_for_labeling"] == "True" for row in audit), len(patch_requests)
        )

        first = patch_requests[0]
        response = {
            "candidate_id": first["candidate_id"],
            "relevance": "irrelevant",
            "sentiment": "not_applicable",
            "fix_status": "not_applicable",
            "review_evidence": None,
            "change_evidence": None,
            "rationale": "The review does not discuss this specific change.",
            "confidence": 0.9,
        }
        response_path = self.root / "patch-response.jsonl"
        response_path.write_text(json.dumps(response) + "\n")
        imported = import_llm_responses(
            self.config,
            patch_job,
            response_path,
            model_name="test-model",
            run_id="patch-pilot",
        )
        self.assertEqual(imported["imported_responses"], 1)

        run_pipeline(self.config)
        self.directory = latest_dataset(self.config)
        fresh_job = self.root / "patch-job-fresh"
        export_llm_job(
            self.directory,
            fresh_job,
            sample_size=100,
            splits=("train", "validation", "test"),
            patch_id=patch_id,
            exclude_annotated=True,
        )
        fresh_ids = {
            json.loads(line)["candidate_id"]
            for line in (fresh_job / "requests.jsonl").read_text().splitlines()
        }
        fresh_manifest = json.loads((fresh_job / "manifest.json").read_text())
        self.assertNotIn(first["candidate_id"], fresh_ids)
        self.assertTrue(fresh_manifest["exclude_annotated"])
        self.assertGreaterEqual(fresh_manifest["existing_machine_labeled_in_pool"], 1)

    def test_bad_quotes_unknown_ids_and_fake_human_provenance_are_atomic_failures(self):
        self.submit(self.response())
        before = self.config.input("llm_annotations").read_bytes()
        for update in [
            {"review_evidence": {"text": "invented source quote"}},
            {"candidate_id": "outside-job"},
            {"label_source": "human"},
            {"adjudicated": True},
            {"confidence": 2},
            {"confidence": True},
            {"relevance": "invented-label"},
        ]:
            with self.subTest(update=update), self.assertRaises(ValueError):
                self.submit({**self.response(), **update}, run_id="bad-pass")
            self.assertEqual(before, self.config.input("llm_annotations").read_bytes())

    def test_conflicting_models_are_preserved_but_excluded_until_explicit_resolution(self):
        first = self.submit(self.response())
        self.assertEqual(first["machine_annotations"], 1)
        disagreement = {
            **self.response(),
            "relevance": "irrelevant",
            "sentiment": "not_applicable",
            "fix_status": "not_applicable",
            "review_evidence": None,
            "change_evidence": None,
        }
        self.submit(disagreement, run_id="pass-2")
        result = run_pipeline(self.config)
        self.assertEqual(result["rows"]["llm_annotations"], 2)
        self.assertEqual(result["rows"]["silver_pairs"], 0)
        self.assertEqual(result["readiness"]["machine_label_conflicts_or_uncertainty"], 1)
        old = read_table(latest_dataset(self.config), "llm_annotations")
        corrected = {**self.response(), "supersedes": [r["annotation_id"] for r in old]}
        self.submit(corrected, run_id="pass-3")
        result = run_pipeline(self.config)
        self.assertEqual(result["rows"]["silver_pairs"], 1)

    def test_uncertainty_is_retained_without_becoming_silver_training_data(self):
        self.submit(
            {
                **self.response(),
                "relevance": "uncertain",
                "sentiment": "unknown",
                "fix_status": "unknown",
                "review_evidence": None,
                "change_evidence": None,
            }
        )
        result = run_pipeline(self.config)
        self.assertEqual(result["rows"]["llm_annotations"], 1)
        self.assertEqual(result["rows"]["silver_pairs"], 0)

    def test_json_array_and_single_fence_response_files_are_accepted(self):
        path = self.root / "array.json"
        path.write_text("```json\n" + json.dumps([self.response()]) + "\n```\n")
        self.assertEqual(len(read_responses(path)), 1)
        response_dir = self.root / "responses"
        response_dir.mkdir()
        (response_dir / "batch-1.jsonl").write_text(json.dumps(self.response()) + "\n")
        self.assertEqual(len(read_responses(response_dir)), 1)


if __name__ == "__main__":
    unittest.main()
