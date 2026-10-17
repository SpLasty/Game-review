import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import pyarrow.parquet as pq

from steam_insights.pipeline.reviews import prepare_review_observations, text_spans
from steam_insights.pipeline.storage import stable_id, write_table


def review_fixture(**updates):
    row = {
        "appid": "730", "game": "Example", "review_id": "18446744073709551614",
        "review_text": "Not fixed in 1.2.3 🎮. The crashes are still here every match.",
        "language": "english", "timestamp_created": "1704067200", "timestamp_updated": "1704067200",
        "recommended": "False", "author_hash": "pseudonym",
        "_source": {"source_record_id": "source-1", "source_path": "fixture.csv",
                    "source_sha256": "digest", "source_row": 2, "source_kind": "csv_export",
                    "source_url": "https://example.test/review"},
    }
    row.update(updates)
    return row


class ReviewPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.config = SimpleNamespace(work_dir=self.root, values={"reviews": {
            "minimum_words": 10, "language": "english", "language_detection_min_words": 20,
            "language_warning_probability": 0.9, "near_duplicate_similarity": 0.92,
            "near_duplicate_bucket_limit": 300, "passage_max_chars": 1200,
        }})

    def test_false_large_ids_and_source_text_survive_arrow_roundtrip(self):
        result = prepare_review_observations([review_fixture()], self.config)
        write_table(self.root, "reviews", result["reviews"], {
            "compression": "zstd", "compression_level": 3, "row_group_size": 65536})
        row = pq.read_table(self.root / "reviews.parquet").to_pylist()[0]
        self.assertEqual(row["review_id"], "18446744073709551614")
        self.assertFalse(row["recommended"])
        self.assertEqual(row["review_text_original"], review_fixture()["review_text"])
        self.assertIn("Not fixed in 1.2.3 🎮", row["review_text"])

    def test_repeated_observation_deduplicates_but_preserves_source_accounting(self):
        result = prepare_review_observations([review_fixture(), review_fixture()], self.config)
        self.assertEqual(len(result["reviews"]), 1)
        self.assertEqual(result["stats"]["repeated_observations"], 1)
        self.assertEqual(len(result["source_records"]), 2)

    def test_conflicting_same_time_vote_stops_publication(self):
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            prepare_review_observations([review_fixture(), review_fixture(recommended="True")], self.config)

    def test_invalid_record_is_quarantined_without_losing_valid_record(self):
        result = prepare_review_observations([
            review_fixture(), review_fixture(review_id="1234", recommended="maybe")], self.config)
        self.assertEqual(len(result["reviews"]), 1)
        self.assertEqual(result["stats"]["quarantined_rows"], 1)
        self.assertEqual(result["stats"]["source_rows"], 2)

    def test_short_and_non_english_rows_retained_for_votes(self):
        result = prepare_review_observations([
            review_fixture(review_text="NA"), review_fixture(review_id="1234", language="french")], self.config)
        self.assertEqual(len(result["reviews"]), 2)
        self.assertFalse(any(row["text_eligible"] for row in result["reviews"]))
        self.assertEqual(next(r for r in result["reviews"] if r["review_id"] == "18446744073709551614")["review_text_original"], "NA")

    def test_passages_reference_exact_canonical_substrings(self):
        text = "Not fixed in 1.2.3. Dr. Smith agrees.\nNumbers: 3.5 -> 4.5. " + "still broken " * 100
        spans = text_spans(text, 80)
        self.assertTrue(all(0 <= begin < end <= len(text) and end - begin <= 80 for begin, end in spans))
        self.assertTrue(any("1.2.3" in text[begin:end] for begin, end in spans))
        self.assertEqual(stable_id("id", 1), stable_id("id", 1))


if __name__ == "__main__":
    unittest.main()
