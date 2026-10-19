"""Behavioral checks for data meaning, source preservation and snapshot contracts."""

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from steam_insights.config import DataConfig, load_config
from steam_insights.data.exploration import profile
from steam_insights.data.io import read_csv, sha256
from steam_insights.data.pipeline import preprocess
from steam_insights.data.preprocessing import clean_text, prepare_announcements, prepare_reviews
from steam_insights.data.text import word_count
from steam_insights.data.validation import validate_reviews


def reviews_fixture() -> pd.DataFrame:
    # Synthetic source-format fixtures, never model results or human labels.
    return pd.DataFrame(
        [
            {
                "appid": "730",
                "game": "Example",
                "review_id": "18446744073709551610",
                "review_text": "  This is NOT fixed. 🎮\r\nVersion 1.2.3 is still broken.  ",
                "language": "english",
                "created_utc": "2024-01-01T00:00:00+00:00",
                "updated_utc": "2024-01-01T00:00:00+00:00",
                "timestamp_created": "1704067200",
                "timestamp_updated": "1704067200",
                "recommended": "False",
                "unedited": "True",
                "playtime_at_review_hours": "",
                "primarily_steam_deck": "",
            },
            {
                "appid": "730",
                "game": "Example",
                "review_id": "2",
                "review_text": "Great update!",
                "language": "english",
                "created_utc": "2024-01-01T00:00:00+00:00",
                "updated_utc": "2024-01-02T00:00:00+00:00",
                "timestamp_created": "1704067200",
                "timestamp_updated": "1704153600",
                "recommended": "True",
                "unedited": "False",
                "playtime_at_review_hours": "5.5",
                "primarily_steam_deck": "False",
            },
            {
                "appid": "570",
                "game": "Other",
                "review_id": "3",
                "review_text": "",
                "language": "english",
                "created_utc": "2024-01-01T00:00:00+00:00",
                "updated_utc": "2024-01-01T00:00:00+00:00",
                "timestamp_created": "1704067200",
                "timestamp_updated": "1704067200",
                "recommended": "True",
                "unedited": "True",
                "playtime_at_review_hours": "0",
                "primarily_steam_deck": "True",
            },
        ],
        dtype="string",
    )


def announcements_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "appid": "730",
                "game": "Example",
                "gid": "18446744073709551611",
                "title": "UNSTABLE update",
                "text": "Known Issues\n\n- Inventory crash",
                "date_utc": "2024-01-01T00:00:00+00:00",
                "timestamp": "1704067200",
                "source_url": "https://example.com/announcement",
                "patch_candidate": "True",
                "verification_status": "unverified_candidate",
            },
        ],
        dtype="string",
    )


class PreparationTests(unittest.TestCase):
    def test_false_vote_is_false_and_large_ids_stay_exact(self):
        prepared = prepare_reviews(reviews_fixture())
        row = prepared.loc[prepared["review_id"].eq("18446744073709551610")].iloc[0]
        self.assertFalse(row["recommended"])
        self.assertEqual(str(prepared["recommended"].dtype), "boolean")
        self.assertEqual(row["review_id"], "18446744073709551610")

    def test_original_text_case_negation_version_and_emoji_are_preserved(self):
        source = reviews_fixture()
        prepared = prepare_reviews(source)
        row = prepared.loc[prepared["review_id"].eq(source.loc[0, "review_id"])].iloc[0]
        self.assertEqual(row["review_text"], source.loc[0, "review_text"])
        self.assertIn("NOT fixed. 🎮\nVersion 1.2.3", row["review_text_clean"])
        self.assertEqual(source.loc[0, "review_text"], reviews_fixture().loc[0, "review_text"])

    def test_short_and_empty_reviews_are_retained_with_a_separate_flag(self):
        prepared = prepare_reviews(reviews_fixture(), minimum_words=10)
        self.assertEqual(len(prepared), 3)
        self.assertEqual(int(prepared["analysis_text_eligible"].sum()), 1)
        self.assertEqual(int(prepared["recommended"].eq(False).sum()), 1)
        relaxed = prepare_reviews(reviews_fixture(), minimum_words=1)
        self.assertEqual(int(relaxed["analysis_text_eligible"].sum()), 2)

    def test_optional_unknown_boolean_and_playtime_remain_null(self):
        row = (
            prepare_reviews(reviews_fixture()).query("review_id == '18446744073709551610'").iloc[0]
        )
        self.assertTrue(pd.isna(row["playtime_at_review_hours"]))
        self.assertTrue(pd.isna(row["primarily_steam_deck"]))

    def test_dates_are_utc_and_edit_status_is_a_snapshot_proxy(self):
        prepared = prepare_reviews(reviews_fixture())
        self.assertEqual(str(prepared["created_utc"].dt.tz), "UTC")
        self.assertFalse(
            prepared.loc[prepared["review_id"].eq("2"), "is_unedited_snapshot"].iloc[0]
        )

    def test_duplicate_source_ids_fail_instead_of_dropping_a_revision(self):
        frame = reviews_fixture()
        duplicate = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "duplicate_keys"):
            prepare_reviews(duplicate)

    def test_invalid_required_boolean_is_rejected(self):
        for value in ("maybe", ""):
            frame = reviews_fixture()
            frame.loc[0, "recommended"] = value
            with self.assertRaisesRegex(ValueError, "invalid_boolean_recommended"):
                prepare_reviews(frame)

    def test_iso_epoch_disagreement_is_rejected(self):
        frame = reviews_fixture()
        frame.loc[0, "timestamp_created"] = "1704067201"
        with self.assertRaisesRegex(ValueError, "timestamp_mismatch"):
            prepare_reviews(frame)

    def test_updated_before_created_is_rejected(self):
        frame = reviews_fixture()
        frame.loc[0, "updated_utc"] = "2023-12-31T00:00:00+00:00"
        frame.loc[0, "timestamp_updated"] = "1703980800"
        with self.assertRaisesRegex(ValueError, "updated_before_created"):
            prepare_reviews(frame)

    def test_nonenglish_is_reported_not_silently_dropped(self):
        frame = reviews_fixture()
        frame.loc[0, "language"] = "french"
        self.assertFalse(validate_reviews(frame).valid)
        with self.assertRaisesRegex(ValueError, "unexpected_language"):
            prepare_reviews(frame)

    def test_fractional_legacy_word_count_is_reported_before_conversion(self):
        frame = reviews_fixture()
        frame["word_count"] = "1.5"
        with self.assertRaisesRegex(ValueError, "invalid_word_count"):
            prepare_reviews(frame)

    def test_announcements_do_not_invent_headings_or_fix_labels(self):
        prepared = prepare_announcements(announcements_fixture())
        self.assertEqual(prepared.loc[0, "gid"], "18446744073709551611")
        self.assertEqual(prepared.loc[0, "verification_status"], "unverified_candidate")
        self.assertFalse(prepared.loc[0, "heading_context_available"])
        self.assertNotIn("fix_status", prepared)

    def test_unicode_normalization_is_conservative(self):
        self.assertEqual(
            clean_text("cafe\u0301\t NOT fixed\r\n\r\n\r\n0.1"), "café NOT fixed\n\n0.1"
        )

    def test_word_count_uses_the_source_unicode_convention(self):
        frame = reviews_fixture()
        frame.loc[0, "review_text"] = "café naïve 中文 кириллица"
        frame["word_count"] = frame["review_text"].map(word_count).astype("string")
        report = validate_reviews(frame)
        self.assertNotIn("word_count_mismatch", [item["check"] for item in report.issues])
        row = (
            prepare_reviews(frame, minimum_words=4)
            .loc[lambda x: x["review_id"].eq(frame.loc[0, "review_id"])]
            .iloc[0]
        )
        self.assertEqual(row["word_count_computed"], 4)
        self.assertTrue(row["analysis_text_eligible"])


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.config = DataConfig(
            root,
            root / "data/input",
            root / "data/interim",
            root / "reports",
            "reviews.csv",
            "balanced.csv",
            "notes.csv",
        )
        self.config.source_dir.mkdir(parents=True)
        for kind, frame in (
            ("reviews", reviews_fixture()),
            ("balanced", reviews_fixture().iloc[[0]]),
            ("announcements", announcements_fixture()),
        ):
            frame.to_csv(self.config.source(kind), index=False, encoding="utf-8-sig")

    def test_parquet_round_trip_keeps_source_text_votes_ids_and_all_rows(self):
        before = {
            kind: sha256(self.config.source(kind))
            for kind in ("reviews", "balanced", "announcements")
        }
        result = preprocess(self.config)
        saved = pd.read_parquet(self.config.interim_dir / "reviews.parquet")
        self.assertEqual(result["outputs"]["reviews.parquet"], 3)
        self.assertEqual(result["outputs"]["reviews_text.parquet"], 1)
        row = saved.loc[saved["review_id"].eq("18446744073709551610")].iloc[0]
        self.assertEqual(row["review_text"], reviews_fixture().loc[0, "review_text"])
        self.assertFalse(row["recommended"])
        self.assertEqual(before, {kind: sha256(self.config.source(kind)) for kind in before})

    def test_validation_failure_preserves_an_existing_prepared_snapshot(self):
        preprocess(self.config)
        previous = (self.config.interim_dir / "manifest.json").read_bytes()
        frame = reviews_fixture()
        frame.loc[0, "recommended"] = "invalid"
        frame.to_csv(self.config.source("reviews"), index=False)
        with self.assertRaises(ValueError):
            preprocess(self.config)
        self.assertEqual((self.config.interim_dir / "manifest.json").read_bytes(), previous)
        report = json.loads((self.config.reports_dir / "preprocessing_validation.json").read_text())
        self.assertFalse(report["datasets"][0]["valid"])

    def test_profile_keeps_population_denominators_separate(self):
        result = profile(self.config)
        self.assertEqual([item["reviews"] for item in result["review_populations"]], [3, 1])
        self.assertEqual(result["review_populations"][0]["negative_share"], 1 / 3)
        self.assertEqual(result["review_populations"][1]["negative_share"], 1)
        self.assertTrue((self.config.reports_dir / "figures/coverage_by_game_day.png").is_file())
        self.assertNotIn(
            reviews_fixture().loc[0, "review_text"],
            (self.config.reports_dir / "README.md").read_text(),
        )

    def test_missing_column_still_produces_a_validation_report(self):
        frame = reviews_fixture().drop(columns="recommended")
        frame.to_csv(self.config.source("reviews"), index=False)
        result = profile(self.config)
        self.assertFalse(result["validation"][0]["valid"])
        self.assertTrue((self.config.reports_dir / "profile.json").exists())

    def test_heatmap_handles_different_game_date_coverage(self):
        frame = reviews_fixture()
        frame.loc[2, ["created_utc", "updated_utc"]] = "2024-01-03T00:00:00+00:00"
        frame.loc[2, ["timestamp_created", "timestamp_updated"]] = "1704240000"
        frame.to_csv(self.config.source("reviews"), index=False)
        result = profile(self.config)
        self.assertTrue(result["validation"][0]["valid"])
        self.assertTrue((self.config.reports_dir / "figures/coverage_by_game_day.png").is_file())

    def test_literal_na_text_is_not_treated_as_missing(self):
        frame = reviews_fixture()
        frame.loc[0, "review_text"] = "NA"
        frame.to_csv(self.config.source("reviews"), index=False)
        self.assertEqual(read_csv(self.config.source("reviews")).loc[0, "review_text"], "NA")

    def test_config_rejects_outputs_overlapping_the_sources(self):
        config_dir = self.config.root / "configs"
        config_dir.mkdir()
        source = Path("configs/data.toml").read_text()
        path = config_dir / "data.toml"
        path.write_text(
            source.replace(
                'interim_dir = "data/interim/steam_30_games"',
                'interim_dir = "data/processed/steam_30_games/prepared"',
            )
        )
        with self.assertRaisesRegex(ValueError, "separate"):
            load_config(path)


if __name__ == "__main__":
    unittest.main()
