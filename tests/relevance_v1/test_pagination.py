from __future__ import annotations

import json
from dataclasses import replace

import httpx
import pyarrow.parquet as pq

from steam_patch_relevance.api import RequestBudget, SteamAPI
from steam_patch_relevance.collect import (
    _collect_news,
    _collect_review_window,
    _materialize,
    _review_checkpoint_key,
    _schemas,
    make_windows,
)
from steam_patch_relevance.identity import stable_id
from steam_patch_relevance.models import Game
from steam_patch_relevance.storage import LocalStore


def test_news_paginates_with_decreasing_enddate_and_resumes_idempotently(tmp_path, config):
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        params = request.url.params
        calls.append(params.get("enddate"))
        if len(calls) == 1:
            items = [{"gid": "new", "date": 200, "title": "Patch", "contents": "body"}]
        else:
            items = [{"gid": "old", "date": 100, "title": "Patch", "contents": "body"}]
        return httpx.Response(200, json={"appnews": {"appid": 730, "newsitems": items}})

    http = httpx.Client(transport=httpx.MockTransport(handler))
    api = SteamAPI(budget=RequestBudget(2), client=http)
    store = LocalStore(tmp_path / "data", "run-1")
    local_config = replace(config, news_since="1970-01-01T00:01:40Z", max_news_pages_per_game=5)
    refs, state = _collect_news(api, store, Game(730, "CS2"), local_config, refresh=False)
    assert state["status"] == "complete"
    assert len(refs) == 2
    assert calls == [None, "199"]

    rerun = SteamAPI(budget=RequestBudget(1), client=http)
    refs_again, state_again = _collect_news(
        rerun, store, Game(730, "CS2"), local_config, refresh=False
    )
    assert state_again["status"] == "complete"
    assert len(refs_again) == 2
    assert len(calls) == 3  # one newest-page poll checks for newly published items


def test_partial_news_collection_resumes_from_checkpoint(tmp_path, config):
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        enddate = request.url.params.get("enddate")
        calls.append(enddate)
        if enddate is None:
            items = [{"gid": "new", "date": 200, "title": "Patch", "contents": "body"}]
        else:
            items = [{"gid": "old", "date": 100, "title": "Patch", "contents": "body"}]
        return httpx.Response(200, json={"appnews": {"appid": 730, "newsitems": items}})

    http = httpx.Client(transport=httpx.MockTransport(handler))
    store = LocalStore(tmp_path / "data", "run-1")
    one_page = replace(config, news_since="1970-01-01T00:01:40Z", max_news_pages_per_game=1)
    first_api = SteamAPI(budget=RequestBudget(1), client=http)
    refs, state = _collect_news(first_api, store, Game(730, "CS2"), one_page, refresh=False)
    assert state["status"] == "page_budget_reached"
    assert len(refs) == 1

    two_pages = replace(one_page, max_news_pages_per_game=2)
    second_api = SteamAPI(budget=RequestBudget(1), client=http)
    refs, state = _collect_news(second_api, store, Game(730, "CS2"), two_pages, refresh=False)
    assert state["status"] == "complete"
    assert len(refs) == 2
    assert calls == [None, "199"]


def test_review_pagination_uses_returned_cursor_and_skips_completed_checkpoint(tmp_path, config):
    cursors = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.url.params["input_json"])
        cursors.append(payload["cursor"])
        if payload["cursor"] == "*":
            reviews = [
                {
                    "recommendationid": "r1",
                    "timestamp_created": payload["date_range_start"],
                    "timestamp_updated": payload["date_range_start"],
                    "review": "A test review",
                    "author": {},
                }
            ]
            next_cursor = "cursor +/="
        elif payload["cursor"] == "cursor +/=":
            reviews, next_cursor = [], ""
        else:
            return httpx.Response(400)
        return httpx.Response(
            200,
            json={"response": {"reviews": reviews, "cursor": next_cursor, "total_matching": 1}},
        )

    http = httpx.Client(transport=httpx.MockTransport(handler))
    store = LocalStore(tmp_path / "data", "run-1")
    window = make_windows(
        appid=730,
        announcement_id="g1",
        title="patch",
        anchor_unix=1_800_000_000,
        days_before=14,
        days_after_early=7,
        days_after_late=7,
    )[0]
    api = SteamAPI(budget=RequestBudget(3), client=http)
    state = _collect_review_window(api, store, window, config, refresh=False)
    assert state["status"] == "complete"
    assert state["page_count"] == 2
    assert cursors == ["*", "cursor +/="]

    second = SteamAPI(budget=RequestBudget(1), client=http)
    state_again = _collect_review_window(second, store, window, config, refresh=False)
    assert state_again["status"] == "complete"
    assert len(cursors) == 2


def test_review_window_partial_checkpoint_resumes_from_saved_cursor(tmp_path, config):
    cursors = []

    def handler(request: httpx.Request) -> httpx.Response:
        cursor = json.loads(request.url.params["input_json"])["cursor"]
        cursors.append(cursor)
        if cursor == "*":
            payload = {
                "response": {
                    "reviews": [
                        {
                            "recommendationid": "r1",
                            "timestamp_created": 1_800_000_000,
                            "timestamp_updated": 1_800_000_000,
                            "review": "resume fixture",
                            "author": {},
                        }
                    ],
                    "cursor": "resume-cursor",
                }
            }
        else:
            payload = {"response": {"query_summary": {"num_reviews": 0}, "cursor": "terminal"}}
        return httpx.Response(200, json=payload)

    http = httpx.Client(transport=httpx.MockTransport(handler))
    store = LocalStore(tmp_path / "data", "run-1")
    window = make_windows(
        appid=730,
        announcement_id="resume",
        title="patch",
        anchor_unix=1_800_000_000,
        days_before=14,
        days_after_early=7,
        days_after_late=7,
    )[0]
    one_page_per_run = replace(config, max_pages_per_review_window=1)
    first = _collect_review_window(
        SteamAPI(budget=RequestBudget(1), client=http),
        store,
        window,
        one_page_per_run,
        refresh=False,
    )
    assert first["status"] == "page_budget_reached"
    assert first["next_cursor"] == "resume-cursor"

    second = _collect_review_window(
        SteamAPI(budget=RequestBudget(1), client=http),
        store,
        window,
        one_page_per_run,
        refresh=False,
    )
    assert second["status"] == "complete"
    assert cursors == ["*", "resume-cursor"]


def test_malformed_news_response_is_retained_but_marked_invalid(tmp_path, config):
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": {"newsitems": []}})

    http = httpx.Client(transport=httpx.MockTransport(handler))
    api = SteamAPI(budget=RequestBudget(1), client=http)
    store = LocalStore(tmp_path / "data", "run-1")
    refs, state = _collect_news(
        api,
        store,
        Game(730, "CS2"),
        replace(config, news_since="2026-01-01T00:00:00Z"),
        refresh=False,
    )
    assert len(refs) == 1
    assert state["status"] == "invalid_response"
    assert store.payload_for(refs[0]) == {"unexpected": {"newsitems": []}}


def test_reviews_service_empty_page_without_reviews_array_uses_zero_summary(tmp_path, config):
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"response": {"query_summary": {"num_reviews": 0}, "cursor": "terminal"}},
        )

    http = httpx.Client(transport=httpx.MockTransport(handler))
    api = SteamAPI(budget=RequestBudget(1), client=http)
    store = LocalStore(tmp_path / "data", "run-1")
    window = make_windows(
        appid=275850,
        announcement_id="empty",
        title="update",
        anchor_unix=1_800_000_000,
        days_before=14,
        days_after_early=7,
        days_after_late=7,
    )[0]
    state = _collect_review_window(api, store, window, config, refresh=False)
    assert state["status"] == "complete"
    assert state["page_count"] == 1
    assert state["page_refs"]


def test_missing_reviews_array_without_zero_summary_is_invalid(tmp_path, config):
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": {"cursor": "next"}})

    http = httpx.Client(transport=httpx.MockTransport(handler))
    api = SteamAPI(budget=RequestBudget(1), client=http)
    store = LocalStore(tmp_path / "data", "run-1")
    window = make_windows(
        appid=275850,
        announcement_id="malformed",
        title="update",
        anchor_unix=1_800_000_000,
        days_before=14,
        days_after_early=7,
        days_after_late=7,
    )[0]
    state = _collect_review_window(api, store, window, config, refresh=False)
    assert state["status"] == "invalid_response"
    assert "without an empty-page summary" in state["issues"][0]


def test_duplicate_review_ids_and_same_timestamp_conflicts_are_preserved_and_reported(
    tmp_path, config
):
    cursors = []
    base_review = {
        "recommendationid": "same-id",
        "timestamp_created": 15,
        "timestamp_updated": 16,
        "language": "english",
        "voted_up": True,
        "author": {},
    }

    def handler(request: httpx.Request) -> httpx.Response:
        cursor = json.loads(request.url.params["input_json"])["cursor"]
        cursors.append(cursor)
        if cursor == "*":
            one = {**base_review, "review": "same text"}
            payload = {"response": {"reviews": [one, one], "cursor": "c1"}}
        elif cursor == "c1":
            payload = {
                "response": {
                    "reviews": [{**base_review, "review": "edited without timestamp change"}],
                    "cursor": "c2",
                }
            }
        else:
            payload = {"response": {"reviews": [], "cursor": ""}}
        return httpx.Response(200, json=payload)

    http = httpx.Client(transport=httpx.MockTransport(handler))
    store = LocalStore(tmp_path / "data", "run-1")
    window = make_windows(
        appid=730,
        announcement_id="g1",
        title="patch",
        anchor_unix=30,
        days_before=1,
        days_after_early=1,
        days_after_late=1,
    )[0]
    state = _collect_review_window(
        SteamAPI(budget=RequestBudget(3), client=http), store, window, config, refresh=False
    )
    key = stable_id("window", window.patch_id, window.segment, window.start_unix, window.end_unix)
    materialized = _materialize(
        store,
        config,
        {730: []},
        {730: {"status": "complete"}},
        [],
        [window],
        {key: state},
        {},
    )
    review_rows, memberships, window_rows, quality = (
        materialized[3],
        materialized[4],
        materialized[5],
        materialized[6],
    )
    assert cursors == ["*", "c1", "c2"]
    assert len(review_rows) == 2
    assert len({row["logical_revision_key"] for row in review_rows}) == 1
    assert len(memberships) == 2
    assert quality["repeated_review_records_within_windows"] == 1
    assert quality["conflicting_same_update_text_versions"] == 1
    assert window_rows[0]["collection_status"] == "complete"


def test_overlapping_patch_windows_share_review_row_and_preserve_both_memberships(tmp_path, config):
    review_time = 1_800_000_000 + 4 * 86_400

    def handler(request: httpx.Request) -> httpx.Response:
        cursor = json.loads(request.url.params["input_json"])["cursor"]
        if cursor == "*":
            payload = {
                "response": {
                    "reviews": [
                        {
                            "recommendationid": "overlap-review",
                            "timestamp_created": review_time,
                            "timestamp_updated": review_time,
                            "review": "This revision belongs to both temporal windows.",
                            "author": {},
                        }
                    ],
                    "cursor": "next",
                }
            }
        else:
            payload = {"response": {"reviews": [], "cursor": ""}}
        return httpx.Response(200, json=payload)

    http = httpx.Client(transport=httpx.MockTransport(handler))
    store = LocalStore(tmp_path / "data", "run-1")
    first_windows = make_windows(
        appid=730,
        announcement_id="patch-one",
        title="one",
        anchor_unix=1_800_000_000,
        days_before=14,
        days_after_early=7,
        days_after_late=7,
    )
    second_windows = make_windows(
        appid=730,
        announcement_id="patch-two",
        title="two",
        anchor_unix=1_800_000_000 + 3 * 86_400,
        days_before=14,
        days_after_early=7,
        days_after_late=7,
    )
    windows = [first_windows[1], second_windows[1]]
    states = {}
    for window in windows:
        key = stable_id(
            "window", window.patch_id, window.segment, window.start_unix, window.end_unix
        )
        states[key] = _collect_review_window(
            SteamAPI(budget=RequestBudget(2), client=http),
            store,
            window,
            config,
            refresh=False,
        )
    result = _materialize(
        store,
        config,
        {730: []},
        {730: {"status": "complete"}},
        [],
        windows,
        states,
        {},
    )
    review_rows, memberships = result[3], result[4]
    assert len(review_rows) == 1
    assert len(memberships) == 2
    assert len({row["patch_id"] for row in memberships}) == 2


def test_unicode_review_roundtrips_and_language_modes_keep_stable_identity(tmp_path, config):
    text = "运行很稳定 — tactical combat feels great; 日本語の用語も残します。"
    review = {
        "recommendationid": "unicode-review",
        "timestamp_created": 1_800_000_100,
        "timestamp_updated": 1_800_000_200,
        "review": text,
        "language": "schinese",
        "voted_up": True,
        "author": {},
    }
    window = make_windows(
        appid=730,
        announcement_id="unicode-patch",
        title="Patch",
        anchor_unix=1_800_000_000,
        days_before=14,
        days_after_early=7,
        days_after_late=7,
    )[1]

    def collect_mode(root, run_id, languages):
        requests = []

        def handler(request: httpx.Request) -> httpx.Response:
            payload = json.loads(request.url.params["input_json"])
            requests.append((payload["languages"], payload["cursor"]))
            if payload["cursor"] == "*":
                body = {"response": {"reviews": [review], "cursor": "next"}}
            else:
                body = {"response": {"reviews": [], "cursor": ""}}
            return httpx.Response(200, json=body)

        local = replace(
            config,
            review_languages=languages,
            max_pages_per_review_window=2,
        )
        store = LocalStore(root, run_id)
        client = httpx.Client(transport=httpx.MockTransport(handler))
        api = SteamAPI(budget=RequestBudget(4), client=client)
        state = _collect_review_window(api, store, window, local, refresh=False)
        before_repeat = len(requests)
        repeated = _collect_review_window(api, store, window, local, refresh=False)
        assert repeated["status"] == "complete"
        assert len(requests) == before_repeat  # completed filtered snapshot is resumable/idempotent
        assert all(requested == list(languages) for requested, _ in requests)
        key = stable_id(
            "window", window.patch_id, window.segment, window.start_unix, window.end_unix
        )
        materialized = _materialize(
            store,
            local,
            {730: []},
            {730: {"status": "complete"}},
            [],
            [window],
            {key: state},
            {},
        )
        review_rows = materialized[3]
        parquet = store.write_table("review_revisions", review_rows, _schemas()["review_revisions"])
        round_tripped = pq.read_table(parquet).to_pylist()
        assert round_tripped[0]["review_text_original"] == text
        assert round_tripped[0]["language"] == "schinese"
        assert round_tripped[0]["detected_language"] is None
        assert round_tripped[0]["detected_language_confidence"] is None
        return review_rows[0]["review_revision_id"], state, store

    all_id, _, store = collect_mode(tmp_path / "data", "all-run", ("all",))
    explicit_id, _, explicit_store = collect_mode(tmp_path / "data", "schinese-run", ("schinese",))
    assert store.checkpoint_root == explicit_store.checkpoint_root
    assert store.load_checkpoint(_review_checkpoint_key(window, ("all",)))["status"] == "complete"
    assert (
        store.load_checkpoint(_review_checkpoint_key(window, ("schinese",)))["status"] == "complete"
    )
    assert all_id == explicit_id
