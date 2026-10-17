import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from steam_insights.pipeline.announcements import prepare_announcement_observations
from steam_insights.pipeline.documents import parse_document, status_hint
from steam_insights.pipeline.sources import PublicSteamClient


def news_fixture(**updates):
    row = {
        "appid": "730",
        "game": "Example",
        "gid": "18446744073709551613",
        "title": "Patch 1.2.3",
        "timestamp": "1704067200",
        "contents": "[h2]Fixes[/h2][list][*]Fixed terminal crashes.[/list][h2]Known Issues[/h2][list][*]Fixed crashes may still occur.[/list]",
        "text": "flattened",
        "feed": "steam_community_announcements",
        "source_url": "https://steamcommunity.com/games/730/announcements/detail/123",
        "_source": {
            "source_record_id": "news-source",
            "source_path": "news.json",
            "source_sha256": "digest",
            "source_row": 1,
            "source_kind": "collector_json",
            "source_url": "https://steamcommunity.com/news/123",
        },
    }
    row.update(updates)
    return row


class DocumentTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.config = SimpleNamespace(input=lambda name: Path(self.temporary.name) / name)

    def test_bbcode_heading_context_changes_fix_hint_and_spans_remain_exact(self):
        result = prepare_announcement_observations([news_fixture()], self.config)
        doc = result["announcements"][0]
        changes = result["changes"]
        self.assertTrue(doc["structure_available"])
        self.assertEqual(doc["verification_status"], "source_confirmed_patch_post")
        self.assertEqual(
            [row["status_hint"] for row in changes], ["released_fix_claim", "known_issue"]
        )
        for row in changes:
            self.assertEqual(
                doc["canonical_text"][row["char_start"] : row["char_end"]], row["text"]
            )

    def test_html_nested_bullets_and_tables_preserve_context_and_values(self):
        source = "<h2>Balance</h2><ul><li>Changed rifle damage.<ul><li>Increased from 3.5 to 4.5.</li></ul></li></ul><table><tr><td>Reload changed</td><td>2.0 -> 1.5</td></tr></table>"
        canonical, blocks, kind, structured = parse_document(source)
        self.assertEqual(kind, "html")
        self.assertTrue(structured)
        self.assertEqual(sum(b["block_type"] == "list_item" for b in blocks), 2)
        self.assertTrue(any(b["block_type"] == "table_row" for b in blocks))
        result = prepare_announcement_observations([news_fixture(contents=source)], self.config)
        numeric = [row for row in result["changes"] if row["old_value"]]
        self.assertEqual(
            {(r["old_value"].strip(), r["new_value"].strip()) for r in numeric},
            {("3.5", "4.5"), ("2.0", "1.5")},
        )
        for block in blocks:
            self.assertEqual(canonical[block["char_start"] : block["char_end"]], block["text"])

    def test_flattened_content_cannot_be_source_confirmed_by_keyword_alone(self):
        row = news_fixture(contents=None, text="Fixes\n\n- Fixed terminal crashes.")
        row["_source"]["source_kind"] = "csv_export"
        result = prepare_announcement_observations([row], self.config)
        self.assertFalse(result["announcements"][0]["structure_available"])
        self.assertEqual(result["patches"][0]["verification_status"], "heuristic_unverified")
        self.assertTrue(all(r["needs_review"] for r in result["changes"]))

    def test_publication_does_not_become_effective_release_time(self):
        doc = prepare_announcement_observations([news_fixture()], self.config)["announcements"][0]
        self.assertIsNone(doc["release_utc"])
        self.assertEqual(status_hint("This will be fixed next week."), "planned")
        self.assertEqual(status_hint("Fixed terminal bug", "Known Issues"), "known_issue")

    def test_sale_is_not_a_patch_and_missing_body_is_preserved(self):
        result = prepare_announcement_observations(
            [news_fixture(title="Winter sale", contents="Discounts now available")], self.config
        )
        self.assertEqual(result["announcements"][0]["post_type"], "promotion")
        self.assertEqual(result["patches"], [])


class CollectionTests(unittest.TestCase):
    def test_persisted_response_has_no_author_steamid_and_reuses_cache(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = SimpleNamespace(
                root=root,
                input=lambda name: root / "recovery",
                values={
                    "collection": {
                        "retry_count": 0,
                        "max_requests": 1,
                        "timeout_seconds": 1,
                        "request_interval_seconds": 0,
                    }
                },
            )
            payload = {
                "response": {
                    "reviews": [
                        {
                            "author": {"steamid": "76561198000000001", "playtime_at_review": 120},
                            "review": "exact text",
                        }
                    ]
                }
            }
            calls = []

            def opener(*args, **kwargs):
                calls.append(args)
                return io.BytesIO(json.dumps(payload).encode())

            client = PublicSteamClient(config, opener=opener)
            first, fetched = client.get(
                "https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/",
                {"input_json": "{}"},
            )
            second, _ = client.get(
                "https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/",
                {"input_json": "{}"},
            )
            self.assertEqual(len(calls), 1)
            self.assertNotIn("steamid", first["response"]["reviews"][0]["author"])
            self.assertEqual(first, second)
            for path in (root / "recovery").glob("responses/*.json"):
                self.assertNotIn("76561198000000001", path.read_text())


if __name__ == "__main__":
    unittest.main()
