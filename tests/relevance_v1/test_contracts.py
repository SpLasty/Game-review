from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import httpx

from steam_patch_relevance.api import RequestBudget, SteamAPI
from steam_patch_relevance.classification import announcement_metadata, utc_datetime
from steam_patch_relevance.cli import _catalog_rows, _is_collection_run_name
from steam_patch_relevance.collect import _review_checkpoint_key, make_windows
from steam_patch_relevance.config import load_config
from steam_patch_relevance.identity import sha256_bytes
from steam_patch_relevance.language_reporting import write_language_reports
from steam_patch_relevance.models import APIResponse
from steam_patch_relevance.storage import LocalStore

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_review_request_uses_service_input_json_and_exact_filters():
    observed = {}

    def handler(request: httpx.Request) -> httpx.Response:
        observed.update(request.url.params)
        return httpx.Response(200, json={"response": {"reviews": [], "cursor": ""}})

    http = httpx.Client(transport=httpx.MockTransport(handler))
    with SteamAPI(budget=RequestBudget(1), client=http) as api:
        api.get_reviews(730, start_unix=10, end_unix=20, cursor="abc +/=")
    payload = json.loads(observed["input_json"])
    assert payload == {
        "appid": 730,
        "filter": 1,
        "languages": ["all"],
        "cursor": "abc +/=",
        "review_type": 0,
        "purchase_type": 1,
        "num_per_page": 100,
        "filter_offtopic_activity": False,
        "date_range_start": 10,
        "date_range_end": 20,
    }


def test_review_request_accepts_explicit_language_filter():
    observed = {}

    def handler(request: httpx.Request) -> httpx.Response:
        observed.update(request.url.params)
        return httpx.Response(200, json={"response": {"reviews": [], "cursor": ""}})

    http = httpx.Client(transport=httpx.MockTransport(handler))
    with SteamAPI(budget=RequestBudget(1), client=http) as api:
        api.get_reviews(730, start_unix=10, end_unix=20, cursor="*", languages=["french", "german"])
    assert json.loads(observed["input_json"])["languages"] == ["french", "german"]


def test_config_defaults_to_all_and_preserves_explicit_steam_codes(tmp_path):
    source = (REPO_ROOT / "configs" / "relevance_v1.toml").read_text(encoding="utf-8")
    default_config = load_config(REPO_ROOT / "configs" / "relevance_v1.toml")
    assert default_config.review_languages == ("all",)

    explicit = tmp_path / "explicit.toml"
    explicit.write_text(source.replace('languages = ["all"]', 'languages = ["schinese", "german"]'))
    assert load_config(explicit).review_languages == ("schinese", "german")

    empty = tmp_path / "empty.toml"
    empty.write_text(source.replace('languages = ["all"]', "languages = []"))
    try:
        load_config(empty)
    except ValueError as error:
        assert "empty list means English" in str(error)
    else:
        raise AssertionError("an empty language list would silently request English-only reviews")


def test_review_checkpoint_identity_is_separate_by_filter_but_reuses_all():
    window = make_windows(
        appid=730,
        announcement_id="filter-identity",
        title="Patch",
        anchor_unix=1_800_000_000,
        days_before=14,
        days_after_early=7,
        days_after_late=7,
    )[0]
    all_key = _review_checkpoint_key(window, ("all",))
    assert all_key.startswith("reviews_") and "_lang_" not in all_key
    assert _review_checkpoint_key(window, ("french",)) != all_key
    assert _review_checkpoint_key(window, ("german",)) != _review_checkpoint_key(
        window, ("french",)
    )


def test_language_coverage_reports_unicode_language_codes_and_missing_metadata(tmp_path):
    games = [{"appid": 730, "game_name": "Counter-Strike 2"}]
    reviews = [
        {
            "review_revision_id": "en",
            "appid": 730,
            "language": "english",
            "language_metadata_status": "english",
        },
        {
            "review_revision_id": "zh",
            "appid": 730,
            "language": "schinese",
            "language_metadata_status": "non_english",
        },
        {
            "review_revision_id": "missing",
            "appid": 730,
            "language": None,
            "language_metadata_status": "missing",
        },
    ]
    windows = [
        {
            "window_id": "window",
            "patch_id": "patch",
            "appid": 730,
            "announcement_id": "announcement",
            "segment": "after_0_7d",
            "collection_status": "partial",
        }
    ]
    memberships = [
        {
            "patch_id": "patch",
            "window_segment": "after_0_7d",
            "review_revision_id": row["review_revision_id"],
        }
        for row in reviews
    ]
    summary, paths = write_language_reports(
        tmp_path,
        run_id="fixture",
        review_languages=("all",),
        game_rows=games,
        announcement_rows=[{"announcement_language": None}],
        review_rows=reviews,
        membership_rows=memberships,
        window_rows=windows,
        collection_phase="pre_backfill",
    )
    assert summary["english_reviews"] == 1
    assert summary["non_english_reviews"] == 1
    assert summary["missing_language_reviews"] == 1
    assert summary["language_backfill_performed"] is False
    assert "schinese" in paths["language_by_game"].read_text(encoding="utf-8")
    assert "after_0_7d" in paths["language_by_patch_window"].read_text(encoding="utf-8")


def test_app_list_key_is_not_in_saved_request_parameters():
    observed = {}

    def handler(request: httpx.Request) -> httpx.Response:
        observed.update(request.url.params)
        observed["host"] = request.url.host
        return httpx.Response(200, json={"response": {"apps": []}})

    http = httpx.Client(transport=httpx.MockTransport(handler))
    with SteamAPI(budget=RequestBudget(1), client=http) as api:
        response = api.get_app_list(api_key="never-log-this", last_appid=None, max_results=10)
    assert observed["key"] == "never-log-this"
    assert observed["format"] == "json"
    assert observed["host"] == "api.steampowered.com"
    assert "never-log-this" not in json.dumps(response.request_params)
    assert "key" not in response.request_params


def test_catalog_rows_normalize_app_metadata_and_keep_raw_references(tmp_path):
    payload = {
        "response": {
            "apps": [
                {
                    "appid": 730,
                    "name": "Counter-Strike 2",
                    "last_modified": 100,
                    "price_change_number": 2,
                },
                {"appid": "570", "name": "Dota 2"},
                {"appid": "not-an-id", "name": "Malformed"},
            ]
        }
    }
    response = APIResponse(
        source_kind="app_list",
        appid=0,
        endpoint="https://api.steampowered.com/IStoreService/GetAppList/v1/",
        source_url="https://api.steampowered.com/IStoreService/GetAppList/v1/",
        request_params={"format": "json", "input_json": "{}"},
        status_code=200,
        retrieved_at_utc=datetime(2026, 10, 18, tzinfo=UTC),
        payload_bytes=json.dumps(payload).encode(),
        payload=payload,
    )
    store = LocalStore(tmp_path, "rv1-catalog-fixture")
    ref = store.save_response(response, page_number=1)

    rows = _catalog_rows(store, [ref])

    assert [row["appid"] for row in rows] == [570, 730]
    assert rows[0]["name"] == "Dota 2"
    assert rows[0]["last_modified"] is None
    assert rows[1]["last_modified"] == 100
    assert rows[1]["source_observation_id"] == ref["observation_id"]
    assert rows[1]["payload_sha256"] == ref["payload_sha256"]


def test_catalog_runs_are_not_mistaken_for_review_collection_runs():
    assert _is_collection_run_name("rv1-20261019T031033900187Z-a468b544")
    assert not _is_collection_run_name("rv1-catalog-20261019T035528Z")


def test_rate_limit_retries_and_obeys_retry_after():
    calls = 0
    delays = []

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(429, headers={"Retry-After": "2"})
        return httpx.Response(200, json={"appnews": {"newsitems": []}})

    http = httpx.Client(transport=httpx.MockTransport(handler))
    with SteamAPI(
        budget=RequestBudget(2),
        client=http,
        min_request_interval=0,
        retries=1,
        sleeper=delays.append,
        random_value=lambda: 0.5,
        clock=lambda: datetime(2026, 10, 18, tzinfo=UTC),
    ) as api:
        response = api.get_news(730, count=20, enddate=None)
    assert response.status_code == 200
    assert calls == 2
    assert delays == [2.0]


def test_sequential_requests_obey_configured_minimum_interval():
    calls = 0
    monotonic_now = [0.0]
    delays = []

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={"appnews": {"newsitems": []}})

    def sleep(delay: float) -> None:
        delays.append(delay)
        monotonic_now[0] += delay

    http = httpx.Client(transport=httpx.MockTransport(handler))
    with SteamAPI(
        budget=RequestBudget(2),
        client=http,
        min_request_interval=0.5,
        sleeper=sleep,
        monotonic=lambda: monotonic_now[0],
    ) as api:
        api.get_news(730, count=20, enddate=None)
        api.get_news(730, count=20, enddate=100)
    assert calls == 2
    assert delays == [0.5]


def test_raw_payload_storage_is_content_addressed_and_records_provenance(tmp_path):
    raw = b'{"appnews":{"appid":730,"newsitems":[]}}'
    response = APIResponse(
        source_kind="news",
        appid=730,
        endpoint="https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/",
        source_url="https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/",
        request_params={"appid": 730, "maxlength": 0},
        status_code=200,
        retrieved_at_utc=datetime(2026, 10, 18, tzinfo=UTC),
        payload_bytes=raw,
        payload=json.loads(raw),
    )
    store = LocalStore(tmp_path / "data", "run-a")
    first = store.save_response(response, page_number=1)
    second = store.save_response(response, page_number=1)
    assert first["payload_sha256"] == sha256_bytes(raw)
    assert first["observation_id"] == second["observation_id"]
    assert len(store.observation_path.read_text().splitlines()) == 1
    assert store.payload_for(first) == response.payload
    assert first["retrieved_at_utc"].endswith("+00:00")
    repeated = APIResponse(
        **{
            **response.__dict__,
            "retrieved_at_utc": datetime(2026, 10, 18, 0, 1, tzinfo=UTC),
        }
    )
    later = store.save_response(repeated, page_number=1)
    assert later["payload_sha256"] == first["payload_sha256"]
    assert later["observation_id"] != first["observation_id"]
    assert len(store.observation_path.read_text().splitlines()) == 2


def test_review_time_segments_have_exact_inclusive_second_boundaries():
    anchor = 1_800_000_000
    windows = make_windows(
        appid=730,
        announcement_id="g1",
        title="patch",
        anchor_unix=anchor,
        days_before=14,
        days_after_early=7,
        days_after_late=7,
    )
    assert [(w.segment, w.start_unix, w.end_unix) for w in windows] == [
        ("before_14d", anchor - 14 * 86_400, anchor - 1),
        ("after_0_7d", anchor, anchor + 7 * 86_400),
        ("after_8_14d", anchor + 7 * 86_400 + 1, anchor + 14 * 86_400),
    ]
    assert windows[1].end_unix + 1 == windows[2].start_unix


def test_overlapping_patch_windows_are_allowed_and_reportable():
    first = make_windows(
        appid=730,
        announcement_id="g1",
        title="update 1",
        anchor_unix=1_800_000_000,
        days_before=14,
        days_after_early=7,
        days_after_late=7,
    )
    second = make_windows(
        appid=730,
        announcement_id="g2",
        title="update 2",
        anchor_unix=1_800_000_000 + 3 * 86_400,
        days_before=14,
        days_after_early=7,
        days_after_late=7,
    )
    assert max(first[1].start_unix, second[1].start_unix) <= min(
        first[1].end_unix, second[1].end_unix
    )


def test_announcement_feed_classification_keeps_other_feeds_and_promotions():
    official = announcement_metadata(
        {
            "feedname": "steam_community_announcements",
            "title": "Counter-Strike 2 Update",
            "contents": "<p>Gameplay update</p><a href='https://steamcommunity.com/test'>details</a>",
        },
        minimum_body_characters=10,
    )
    other = announcement_metadata(
        {"feedname": "ThirdPartyFeed", "title": "Dota 2 Update", "contents": "x" * 150},
        minimum_body_characters=10,
    )
    promo = announcement_metadata(
        {
            "feedname": "steam_community_announcements",
            "title": "Autumn Sale Event",
            "contents": "Save today",
        },
        minimum_body_characters=1,
    )
    empty = announcement_metadata(
        {"feedname": "steam_community_announcements", "title": "Patch Notes", "contents": ""},
        minimum_body_characters=1,
    )
    assert official["officialness"] == "steam_community_announcement_feed"
    assert official["patch_candidate"] is True
    assert official["linked_urls"] == ["https://steamcommunity.com/test"]
    assert other["officialness"] == "other_feed_unverified"
    assert not other["patch_candidate"]
    assert promo["post_type"] == "promotion_or_event"
    assert not promo["patch_candidate"]
    assert empty["body_present"] is False
    assert empty["patch_candidate"] is False
    content_update = announcement_metadata(
        {
            "feedname": "steam_community_announcements",
            "title": "Introducing a new arena",
            "contents": "A substantial content update." * 12,
        },
        minimum_body_characters=10,
    )
    versioned_update = announcement_metadata(
        {
            "feedname": "steam_community_announcements",
            "title": "No Man's Sky COSMOS (7.0)",
            "contents": "A substantial content update." * 12,
        },
        minimum_body_characters=10,
    )
    assert content_update["post_type"] == "content_update_candidate"
    assert versioned_update["post_type"] == "versioned_update_candidate"
    truncated = announcement_metadata(
        {
            "feedname": "steam_community_announcements",
            "title": "Patch Notes",
            "contents": "Patch body [truncated]",
        },
        minimum_body_characters=1,
    )
    assert truncated["body_truncated_suspected"] is True


def test_timestamp_conversion_is_utc_and_rejects_malformed_values():
    assert utc_datetime("0") == datetime(1970, 1, 1, tzinfo=UTC)
    assert utc_datetime("not a timestamp") is None
