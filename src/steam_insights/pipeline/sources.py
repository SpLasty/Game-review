"""Bounded, resumable public Steam collection with immutable sanitized observations."""

import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

import pandas as pd

from steam_insights.data.io import read_csv, write_json
from steam_insights.data.quality_report import patch_window_table
from steam_insights.pipeline.ingestion import api_news_row, api_review_row
from steam_insights.pipeline.storage import parse_time, read_table, stable_id, utc_now


class CollectionStopped(RuntimeError):
    """A budget, persisted cooldown, or source failure stopped a resumable collection."""


class PublicSteamClient:
    def __init__(self, config, *, refresh=False, opener=None, sleeper=time.sleep):
        self.config, self.refresh = config, refresh
        self.settings = config.values["collection"]
        self.directory = config.input("recovery_dir")
        self.directory.mkdir(parents=True, exist_ok=True)
        self.opener = opener or urllib.request.urlopen
        self.sleep = sleeper
        self.requests = 0
        self.last_request = 0.0
        self.index_path = self.directory / "cache_index.json"
        self.index = json.loads(self.index_path.read_text()) if self.index_path.exists() else {}
        salt_path = config.root / ".local" / "pipeline_author_salt"
        salt_path.parent.mkdir(parents=True, exist_ok=True)
        if not salt_path.exists():
            salt_path.write_bytes(os.urandom(32))
        self.salt = salt_path.read_bytes()

    def _sanitize(self, payload):
        result = payload.get("response", payload)
        for row in result.get("reviews", []):
            author = row.get("author", {})
            steamid = author.get("steamid")
            safe = {
                key: author[key]
                for key in (
                    "playtime_forever",
                    "playtime_at_review",
                    "playtime_last_two_weeks",
                    "num_reviews",
                    "last_played",
                    "deck_playtime_at_review",
                    "author_hash",
                )
                if key in author
            }
            if steamid is not None:
                safe["author_hash"] = hashlib.sha256(self.salt + str(steamid).encode()).hexdigest()
                row["author_hash_namespace"] = hashlib.sha256(self.salt).hexdigest()[:16]
            row["author"] = safe
        return payload

    def get(self, endpoint: str, parameters: dict) -> tuple[dict, str]:
        if urllib.parse.urlparse(endpoint).hostname != "api.steampowered.com":
            raise ValueError("This collector accepts only documented public Steam API endpoints")
        signature = stable_id(endpoint, parameters)
        if not self.refresh and signature in self.index:
            cached = json.loads((self.directory / self.index[signature]).read_text())
            return cached["payload"], cached["fetched_utc"]
        cooldown = self.directory / "cooldown.json"
        if cooldown.exists() and parse_time(
            json.loads(cooldown.read_text())["resume_after_utc"]
        ) > datetime.now(timezone.utc):
            raise CollectionStopped("Steam cooldown is active; rerun after cooldown.json timestamp")
        url = endpoint + "?" + urllib.parse.urlencode(parameters)
        for attempt in range(self.settings["retry_count"] + 1):
            if self.requests >= self.settings["max_requests"]:
                raise CollectionStopped("request_budget_reached")
            delay = self.settings["request_interval_seconds"] - (
                time.monotonic() - self.last_request
            )
            if delay > 0:
                self.sleep(delay)
            self.requests += 1
            self.last_request = time.monotonic()
            try:
                request = urllib.request.Request(
                    url, headers={"User-Agent": "SteamPatchInsights/1.0 (research data collection)"}
                )
                with self.opener(request, timeout=self.settings["timeout_seconds"]) as response:
                    payload = self._sanitize(json.load(response))
                fetched = utc_now()
                observation = stable_id(signature, fetched, payload)
                relative = f"responses/{observation}.json"
                write_json(
                    self.directory / relative,
                    {
                        "endpoint": endpoint,
                        "parameters": parameters,
                        "fetched_utc": fetched,
                        "payload": payload,
                        "sanitized_author_identifiers": True,
                    },
                )
                self.index[signature] = relative
                write_json(self.index_path, self.index)
                return payload, fetched
            except urllib.error.HTTPError as exc:
                if exc.code == 429:
                    header = exc.headers.get("Retry-After", "60")
                    try:
                        seconds = max(float(header), 1)
                    except ValueError:
                        from email.utils import parsedate_to_datetime

                        try:
                            seconds = max(
                                (
                                    parsedate_to_datetime(header) - datetime.now(timezone.utc)
                                ).total_seconds(),
                                1,
                            )
                        except (ValueError, TypeError):
                            seconds = 60
                    write_json(
                        cooldown,
                        {
                            "resume_after_utc": (
                                datetime.now(timezone.utc) + timedelta(seconds=seconds)
                            ).isoformat()
                        },
                    )
                    raise CollectionStopped(f"HTTP 429; saved {seconds:.0f}s cooldown") from exc
                if exc.code < 500 or attempt == self.settings["retry_count"]:
                    raise CollectionStopped(f"HTTP {exc.code}") from exc
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
                if attempt == self.settings["retry_count"]:
                    raise CollectionStopped(
                        f"source_request_failed: {type(exc).__name__}: {exc}"
                    ) from exc
            self.sleep(min(2**attempt, 10))
        raise CollectionStopped("retry_limit_reached")

    def save_record(self, kind: str, record: dict, fetched: str):
        entity = record.get("review_id", record.get("gid"))
        identifier = stable_id(record, fetched)
        write_json(
            self.directory
            / "records"
            / kind
            / str(record["appid"])
            / f"{entity}-{identifier}.json",
            {
                "fetched_utc": fetched,
                "record": record,
            },
        )


def recover_sources(config, *, refresh=False, client=None) -> dict:
    """Recover full developer posts around legacy verified and well-covered candidate IDs."""
    client = client or PublicSteamClient(config, refresh=refresh)
    reviews, notes = (
        read_csv(config.data.source("reviews")),
        read_csv(config.data.source("announcements")),
    )
    windows = patch_window_table(
        reviews, notes, minimum_words=config.values["reviews"]["minimum_words"]
    )
    targets = windows.loc[
        windows["manually_verified_patch"] | windows["exploratory_coverage_threshold_met"]
    ]
    reports = []
    for (appid, game), group in targets.groupby(["appid", "game"], sort=True):
        target_ids = set(group["gid"].astype(str))
        scope = stable_id("news_scope_v1", str(appid), sorted(target_ids))
        state_path = client.directory / "state" / f"news-{scope}.json"
        state = (
            json.loads(state_path.read_text())
            if state_path.exists() and not refresh
            else {
                "pages": 0,
                "enddate": int(
                    pd.to_datetime(group["announcement_published_utc"], utc=True).max().timestamp()
                )
                + 1,
                "found": [],
                "exhausted": False,
            }
        )
        status = "target_ids_found" if target_ids <= set(state["found"]) else "page_limit_reached"
        starting_pages = state["pages"]
        try:
            while (
                state["pages"] - starting_pages < config.values["collection"]["news_pages_per_game"]
                and not state["exhausted"]
                and not target_ids <= set(state["found"])
            ):
                parameters = {
                    "appid": str(appid),
                    "count": 100,
                    "maxlength": 0,
                    "feeds": "steam_community_announcements",
                    "enddate": state["enddate"],
                }
                payload, fetched = client.get(
                    "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/", parameters
                )
                items = payload.get("appnews", {}).get("newsitems")
                if not isinstance(items, list):
                    raise CollectionStopped("invalid_news_response")
                for item in items:
                    row = api_news_row(item, int(appid), game)
                    client.save_record("announcements", row, fetched)
                state["pages"] += 1
                state["found"] = sorted(set(state["found"]) | {str(r["gid"]) for r in items})
                if not items:
                    state["exhausted"] = True
                else:
                    earliest = min(int(r["date"]) for r in items)
                    if earliest >= state["enddate"]:
                        raise CollectionStopped("news_pagination_did_not_advance")
                    state["enddate"] = earliest
                write_json(state_path, state)
            status = (
                "target_ids_found"
                if target_ids <= set(state["found"])
                else "source_exhausted"
                if state["exhausted"]
                else "page_limit_reached"
            )
        except CollectionStopped as exc:
            status = str(exc)
            write_json(state_path, state)
        reports.append(
            {
                "appid": str(appid),
                "game": game,
                "target_posts": len(target_ids),
                "target_posts_found": len(target_ids & set(state["found"])),
                "pages": state["pages"],
                "status": status,
                "missing_target_ids": sorted(target_ids - set(state["found"])),
            }
        )
        if client.requests >= config.values["collection"]["max_requests"]:
            break
    result = {
        "kind": "announcement_recovery",
        "generated_at_utc": utc_now(),
        "requests": client.requests,
        "target_windows": len(targets),
        "games": reports,
        "limitation": "Matching is by exact (appid, gid); newly fetched bodies are new observations, not historical reconstruction.",
    }
    write_json(client.directory / "announcement_recovery_report.json", result)
    return result


def backfill_reviews(config, *, refresh=False, client=None) -> dict:
    client = client or PublicSteamClient(config, refresh=refresh)
    stage_dir = config.work_dir / "announcements"
    if not (stage_dir / "patches.parquet").exists():
        raise ValueError("Run pipeline --stage announcements before backfill-reviews")
    patches = read_table(stage_dir, "patches")
    review_path = config.work_dir / "reviews"
    if not (review_path / "reviews.parquet").exists():
        raise ValueError("Run pipeline --stage reviews before backfill-reviews")
    from steam_insights.pipeline.datasets import build_windows

    windows = {
        w["patch_id"]: w for w in build_windows(read_table(review_path, "reviews"), patches, config)
    }
    now = datetime.now(timezone.utc)
    eligible = [
        p
        for p in patches
        if (p["verified_for_analysis"] or p["legacy_manual_flag"])
        and p["anchor_utc"] + timedelta(days=config.values["windows"]["days_after"]) <= now
        and not windows[p["patch_id"]]["coverage_screen_met"]
    ]
    selected = sorted(
        eligible,
        key=lambda p: (
            not p["legacy_manual_flag"],
            not p["verified_for_analysis"],
            -p["anchor_utc"].timestamp(),
            p["patch_id"],
        ),
    )[: config.values["collection"]["max_patch_windows"]]
    reports = []
    for patch in selected:
        for side in ("pre", "post"):
            at = patch["anchor_utc"]
            start = (
                at - timedelta(days=config.values["windows"]["days_before"])
                if side == "pre"
                else at
            )
            end = (
                at if side == "pre" else at + timedelta(days=config.values["windows"]["days_after"])
            )
            scope = stable_id(
                "review_window_v1", patch["appid"], start.isoformat(), end.isoformat()
            )
            path = client.directory / "state" / f"reviews-{scope}.json"
            state = (
                json.loads(path.read_text())
                if path.exists() and not refresh
                else {
                    "cursor": "*",
                    "pages": 0,
                    "review_ids": [],
                    "exhausted": False,
                }
            )
            status = "page_limit_reached"
            starting_pages = state["pages"]
            try:
                while (
                    not state["exhausted"]
                    and state["pages"] - starting_pages
                    < config.values["collection"]["review_pages_per_window"]
                ):
                    request = {
                        "appid": patch["appid"],
                        "filter": 1,
                        "languages": ["english"],
                        "purchase_type": 1,
                        "review_type": 0,
                        "num_per_page": 100,
                        "filter_offtopic_activity": False,
                        "cursor": state["cursor"],
                        "date_range_start": int(start.timestamp()),
                        "date_range_end": int(end.timestamp()) - 1,
                    }
                    payload, fetched = client.get(
                        "https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/",
                        {"input_json": json.dumps(request, separators=(",", ":"))},
                    )
                    response = payload.get("response", {})
                    items = response.get("reviews")
                    if not isinstance(items, list):
                        raise CollectionStopped("invalid_reviews_response")
                    for item in items:
                        created = parse_time(item.get("timestamp_created"))
                        if created is None or not start <= created < end:
                            raise CollectionStopped("review_outside_requested_date_range")
                        client.save_record(
                            "reviews", api_review_row(item, patch["appid"], patch["game"]), fetched
                        )
                    ids = {str(r["recommendationid"]) for r in items}
                    previous = set(state["review_ids"])
                    next_cursor = response.get("cursor")
                    state["pages"] += 1
                    state["review_ids"] = sorted(previous | ids)
                    state["total_matching"] = response.get("total_matching")
                    if not items:
                        state["exhausted"] = True
                        state["exhausted_fetched_utc"] = fetched
                    elif not next_cursor or next_cursor == state["cursor"] or ids <= previous:
                        raise CollectionStopped("reviews_pagination_did_not_advance")
                    else:
                        state["cursor"] = next_cursor
                    write_json(path, state)
                status = "source_exhausted" if state["exhausted"] else "page_limit_reached"
            except CollectionStopped as exc:
                status = str(exc)
                write_json(path, state)
            future = end > datetime.now(timezone.utc)
            reports.append(
                {
                    "patch_id": patch["patch_id"],
                    "appid": patch["appid"],
                    "game": patch["game"],
                    "side": side,
                    "start_utc": start.isoformat(),
                    "end_utc": end.isoformat(),
                    "pages": state["pages"],
                    "unique_reviews": len(state["review_ids"]),
                    "status": status,
                    "complete_as_of_fetch": bool(
                        state["exhausted"]
                        and not future
                        and state.get("exhausted_fetched_utc")
                        and parse_time(state["exhausted_fetched_utc"]) >= end
                    ),
                    "future_window_end": future,
                }
            )
            if client.requests >= config.values["collection"]["max_requests"]:
                break
        if client.requests >= config.values["collection"]["max_requests"]:
            break
    report_path = client.directory / "review_backfill_report.json"
    previous = (
        json.loads(report_path.read_text()).get("windows", []) if report_path.exists() else []
    )
    merged = {
        (r["patch_id"], r["side"], r["start_utc"], r["end_utc"]): r for r in previous + reports
    }
    result = {
        "kind": "review_backfill",
        "generated_at_utc": utc_now(),
        "requests": client.requests,
        "windows": list(merged.values()),
        "windows_attempted_this_run": len(reports),
        "eligible_past_patch_windows": len(eligible),
        "future_patch_windows_skipped": sum(
            p["anchor_utc"] + timedelta(days=config.values["windows"]["days_after"]) > now
            for p in patches
        ),
        "limitation": "Creation-date bounds select reviews, but content/votes are the current returned state.",
    }
    write_json(report_path, result)
    return result
