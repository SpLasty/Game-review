import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from steam_insights.pipeline.annotations import labeled_exports, validate_annotations
from steam_insights.pipeline.datasets import build_candidates
from steam_insights.pipeline.loader import iter_model_batches, latest_dataset
from steam_insights.pipeline.runner import run_pipeline
from steam_insights.pipeline.settings import load_pipeline_config
from steam_insights.pipeline.storage import read_table


class DatasetRuleTests(unittest.TestCase):
    def test_future_announcement_is_resolution_candidate_never_feedback(self):
        at = datetime(2024, 1, 10, tzinfo=timezone.utc)
        config = SimpleNamespace(
            values={
                "candidates": {
                    "feedback_days": 14,
                    "resolution_days": 90,
                    "minimum_shared_terms": 2,
                    "max_per_review_per_task": 1,
                }
            }
        )
        reviews = [
            {
                "review_revision_id": "r",
                "review_id": "1",
                "appid": 1,
                "created_utc": at,
                "review_text": "terminal crashes are terrible",
                "text_eligible": True,
                "split": "train",
                "cross_split_duplicate": False,
            }
        ]
        docs = [{"announcement_revision_id": "d", "publication_utc": at + timedelta(days=1)}]
        changes = [
            {
                "change_id": "c",
                "announcement_revision_id": "d",
                "appid": 1,
                "text": "Fixed terminal crashes",
                "heading_path": [],
            }
        ]
        patches = [
            {"patch_id": "p", "announcement_revision_id": "d", "anchor_utc": at + timedelta(days=1)}
        ]
        result = build_candidates(reviews, docs, changes, patches, config)
        self.assertEqual([r["task"] for r in result], ["retrospective_complaint_resolution"])
        docs[0]["publication_utc"] = at - timedelta(days=1)
        patches[0]["anchor_utc"] = at - timedelta(days=1)
        result = build_candidates(reviews, docs, changes, patches, config)
        self.assertEqual([r["task"] for r in result], ["post_patch_feedback"])

    def test_relevant_labels_require_real_evidence_and_human_provenance(self):
        candidates = [
            {"candidate_id": "p", "review_revision_id": "r", "announcement_revision_id": "d"}
        ]
        reviews = [{"review_revision_id": "r", "review_text": "terminal still crashes"}]
        docs = [
            {"announcement_revision_id": "d", "canonical_text": "Known Issues\nterminal crashes"}
        ]
        record = {
            "candidate_id": "p",
            "annotator_id": "annotator-1",
            "label_source": "human",
            "adjudicated": True,
            "created_at": "2024-02-01T12:00:00Z",
            "relevance": "relevant",
            "sentiment": "negative",
            "fix_status": "acknowledged",
            "review_evidence": {"start": 0, "end": 22, "text": "terminal still crashes"},
            "change_evidence": {"start": 13, "end": 29, "text": "terminal crashes"},
        }
        record["change_evidence"]["end"] = len(docs[0]["canonical_text"])
        good = validate_annotations([record], candidates, reviews, docs)
        reordered = dict(reversed(list(record.items())))
        self.assertEqual(
            good[0]["annotation_id"],
            validate_annotations([reordered], candidates, reviews, docs)[0]["annotation_id"],
        )
        bad = {**record, "review_evidence": {"start": 0, "end": 2, "text": "fabricated"}}
        with self.assertRaisesRegex(ValueError, "evidence"):
            validate_annotations([bad], candidates, reviews, docs)
        with self.assertRaisesRegex(ValueError, "human"):
            validate_annotations([{**record, "label_source": "rule"}], candidates, reviews, docs)

    def test_conflicting_adjudications_and_duplicate_leakage_do_not_enter_training(self):
        base = {
            "annotation_id": "a",
            "candidate_id": "p",
            "adjudicated": True,
            "relevance": "relevant",
            "sentiment": "negative",
            "fix_status": "released_fix",
            "supersedes": [],
        }
        pairs = [{"candidate_id": "p", "cross_split_duplicate": False, "split": "train"}]
        conflict = {**base, "annotation_id": "b", "sentiment": "positive"}
        self.assertEqual(labeled_exports(pairs, [base, conflict])[0], [])
        resolved = {**conflict, "supersedes": ["a"]}
        self.assertEqual(len(labeled_exports(pairs, [base, resolved])[0]), 1)
        pairs[0]["cross_split_duplicate"] = True
        self.assertEqual(labeled_exports(pairs, [base])[0], [])


class FullPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "configs").mkdir()
        (self.root / "configs/data.toml").write_text(Path("configs/data.toml").read_text())
        pipeline = (
            Path("configs/pipeline.toml")
            .read_text()
            .replace("test_games = 20", "test_games = 1")
            .replace("validation_games = 2", "validation_games = 1")
        )
        (self.root / "configs/pipeline.toml").write_text(pipeline)
        self.config = load_pipeline_config(self.root / "configs/pipeline.toml")
        source = self.config.data.source_dir
        source.mkdir(parents=True)
        review_rows, note_rows = [], []
        for appid in [1, 2, 3]:
            for index, date in enumerate([1704067200, 1704844800]):
                review_rows.append(
                    {
                        "appid": str(appid),
                        "game": f"Game {appid}",
                        "review_id": str(18446744073709551000 + appid * 10 + index),
                        "review_text": f"Terminal crashes are terrible and affect every round of my session number {appid}.",
                        "language": "english",
                        "timestamp_created": date,
                        "timestamp_updated": date,
                        "recommended": False,
                    }
                )
            note_rows.append(
                {
                    "appid": str(appid),
                    "game": f"Game {appid}",
                    "gid": str(9000 + appid),
                    "title": "Patch 1.2.3",
                    "timestamp": 1704412800,
                    "text": "Fixes\n\n- Fixed terminal crashes during every round.",
                    "source_url": "https://steamcommunity.com/news/example",
                    "feed": "steam_community_announcements",
                    "patch_candidate": True,
                }
            )
        self.review_frame = pd.DataFrame(review_rows)
        self.review_frame.to_csv(self.config.data.source("reviews"), index=False)
        self.review_frame.to_csv(self.config.data.source("balanced"), index=False)
        pd.DataFrame(note_rows).to_csv(self.config.data.source("announcements"), index=False)

    def test_full_build_publishes_valid_typed_views_and_reuses_snapshot(self):
        first = run_pipeline(self.config)
        directory = latest_dataset(self.config)
        self.assertGreater(first["validation_checks"], 100)
        self.assertEqual(first["rows"]["reviews"], 6)
        self.assertEqual(first["rows"]["labeled_pairs"], 0)
        self.assertFalse(first["readiness"]["supervised_training_ready"])
        self.assertEqual(
            {r["split"] for r in read_table(directory, "games")}, {"train", "validation", "test"}
        )
        batches = list(iter_model_batches(directory, kind="pairs", batch_size=2))
        self.assertTrue(batches)
        self.assertNotIn("recommended", batches[0].schema.names)
        self.assertNotIn("status_hint", batches[0].schema.names)
        self.assertEqual(list(iter_model_batches(directory, labeled=True)), [])
        before = (directory / "manifest.json").read_bytes()
        second = run_pipeline(self.config)
        self.assertEqual(first["dataset_id"], second["dataset_id"])
        self.assertTrue(second["reused"])
        self.assertEqual(before, (directory / "manifest.json").read_bytes())

    def test_failed_build_preserves_previous_published_pointer(self):
        run_pipeline(self.config)
        pointer = self.config.output("datasets_dir") / "latest.json"
        before = pointer.read_bytes()
        self.review_frame["recommended"] = "maybe"
        self.review_frame.to_csv(self.config.data.source("reviews"), index=False)
        with self.assertRaisesRegex(ValueError, "No valid reviews"):
            run_pipeline(self.config)
        self.assertEqual(before, pointer.read_bytes())
        self.assertFalse((self.config.output("datasets_dir") / ".build.lock").exists())

    def test_ninety_day_resolution_boundary_is_utc_across_daylight_saving(self):
        created = datetime(2024, 1, 1, 12, tzinfo=timezone.utc)
        self.review_frame["timestamp_created"] = int(created.timestamp())
        self.review_frame["timestamp_updated"] = int(created.timestamp())
        self.review_frame.to_csv(self.config.data.source("reviews"), index=False)
        notes = pd.read_csv(self.config.data.source("announcements"))
        notes["timestamp"] = int((created + timedelta(days=90)).timestamp())
        notes.to_csv(self.config.data.source("announcements"), index=False)
        run_pipeline(self.config)
        candidates = read_table(latest_dataset(self.config), "candidates")
        self.assertTrue(candidates)
        self.assertTrue(
            all(
                c["task"] == "retrospective_complaint_resolution" and c["lag_days"] == -90
                for c in candidates
            )
        )


if __name__ == "__main__":
    unittest.main()
