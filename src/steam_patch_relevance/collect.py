"""End-to-end raw Steam collection and Stage 1 coverage materialization."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow as pa

from steam_patch_relevance import __version__
from steam_patch_relevance.api import (
    RequestBudget,
    RequestBudgetExceeded,
    SteamAPI,
    SteamAPIError,
)
from steam_patch_relevance.classification import announcement_metadata, utc_datetime
from steam_patch_relevance.identity import canonical_json, config_hash, stable_id
from steam_patch_relevance.language_reporting import (
    language_metadata_status,
    write_language_reports,
)
from steam_patch_relevance.models import CollectionConfig, Game, ReviewWindow
from steam_patch_relevance.storage import LocalStore, read_jsonl, write_csv, write_json

DAY = 86_400
ANNOUNCEMENT_RULE_VERSION = "steam-news-triage-v2"


def make_windows(
    *,
    appid: int,
    announcement_id: str,
    title: str,
    anchor_unix: int,
    days_before: int,
    days_after_early: int,
    days_after_late: int,
) -> list[ReviewWindow]:
    patch_id = stable_id("patch", appid, announcement_id)
    before_start = anchor_unix - days_before * DAY
    early_end = anchor_unix + days_after_early * DAY
    late_end = anchor_unix + (days_after_early + days_after_late) * DAY
    values = [
        ("before_14d", before_start, anchor_unix - 1),
        ("after_0_7d", anchor_unix, early_end),
        ("after_8_14d", early_end + 1, late_end),
    ]
    return [
        ReviewWindow(
            patch_id=patch_id,
            appid=appid,
            announcement_id=announcement_id,
            title=title,
            segment=segment,
            start_unix=start,
            end_unix=end,
            anchor_unix=anchor_unix,
            anchor_source="announcement_publication_time",
        )
        for segment, start, end in values
    ]


def run_collection(
    config: CollectionConfig,
    *,
    repo_root: Path,
    refresh: bool = False,
    api: SteamAPI | None = None,
) -> dict[str, Any]:
    started = datetime.now(UTC)
    resolved_storage = _resolve(repo_root, config.storage_root)
    resolved_reports = _resolve(repo_root, config.report_root)
    cfg_hash = config_hash(config.public_dict())
    run_id = f"rv1-{started.strftime('%Y%m%dT%H%M%S%fZ')}-{cfg_hash[:8]}"
    store = LocalStore(resolved_storage, run_id)
    code_fingerprint = _code_fingerprint(repo_root)
    budget = api.budget if api else RequestBudget(config.max_requests)
    client = api or SteamAPI(
        budget=budget,
        timeout=config.request_timeout_seconds,
        min_request_interval=config.min_request_interval_seconds,
        retries=config.max_retries,
        backoff_base=config.backoff_base_seconds,
        backoff_max=config.backoff_max_seconds,
    )
    owns_api = api is None
    manifest: dict[str, Any] = {
        "run_id": run_id,
        "dataset_namespace": "relevance_v1",
        "status": "running",
        "started_at_utc": started.isoformat(),
        "finished_at_utc": None,
        "config_hash": cfg_hash,
        "config": config.public_dict(),
        "code": {
            "package_version": __version__,
            "git_revision": _git_revision(repo_root),
            "code_fingerprint_sha256": code_fingerprint,
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "refresh": refresh,
        "language_collection_phase": "pre_backfill",
        "language_backfill_performed": False,
        "review_language_filters_configured": list(config.review_languages),
        "request_budget_limit": config.max_requests,
        "request_attempts_used": 0,
        "request_budget_exhausted": False,
        "game_seeds": [game.__dict__ for game in config.games],
        "source_observations_file": str(store.observation_path),
        "outputs": {},
        "notes": [
            "Game IDs are curated pilot seeds; IStoreService/GetAppList was not used.",
            "Patch candidates are deterministic triage candidates, not build-verified updates.",
        ],
    }
    write_json(store.run_root / "manifest.json", manifest)

    news_refs_by_app: dict[int, list[dict[str, Any]]] = {}
    news_states: dict[int, dict[str, Any]] = {}
    selected_patches: list[dict[str, Any]] = []
    news_quality: dict[int, list[str]] = defaultdict(list)
    try:
        for game in config.games:
            if budget.used >= config.max_requests:
                news_states[game.appid] = {
                    "appid": game.appid,
                    "status": "request_budget_reached",
                    "page_refs": [],
                    "page_count": 0,
                }
                manifest["request_budget_exhausted"] = True
                continue
            print(f"[news] {game.name} ({game.appid})", flush=True)
            refs, state = _collect_news(
                client,
                store,
                game,
                config,
                refresh=refresh,
            )
            news_refs_by_app[game.appid] = refs
            news_states[game.appid] = state
            if state.get("status") == "request_budget_reached":
                manifest["request_budget_exhausted"] = True
            news_items, issues = _news_items_for_refs(store, refs, appid=game.appid)
            news_quality[game.appid].extend(issues)
            selected_patches.extend(_select_patch_candidates(news_items, game, config))

        windows: list[ReviewWindow] = []
        for selected in selected_patches:
            windows.extend(
                make_windows(
                    appid=selected["appid"],
                    announcement_id=selected["announcement_id"],
                    title=selected["title"],
                    anchor_unix=selected["published_unix"],
                    days_before=config.days_before,
                    days_after_early=config.days_after_early,
                    days_after_late=config.days_after_late,
                )
            )

        review_states: dict[str, dict[str, Any]] = {}
        for window in windows:
            print(
                f"[reviews] {window.appid} {window.announcement_id} {window.segment}",
                flush=True,
            )
            try:
                review_states[_window_key(window)] = _collect_review_window(
                    client,
                    store,
                    window,
                    config,
                    refresh=refresh,
                )
            except RequestBudgetExceeded as exc:
                review_states[_window_key(window)] = _budget_partial_state(window, str(exc))
                manifest["request_budget_exhausted"] = True
            if review_states[_window_key(window)].get("status") == "request_budget_reached":
                manifest["request_budget_exhausted"] = True

        for window in windows:
            key = _window_key(window)
            if key not in review_states:
                review_states[key] = {
                    **_budget_partial_state(
                        window, "not requested because the run stopped at its request budget"
                    ),
                    "status": "not_started",
                }

        (
            game_rows,
            announcement_rows,
            patch_rows,
            review_rows,
            membership_rows,
            window_rows,
            quality,
        ) = _materialize(
            store,
            config,
            news_refs_by_app,
            news_states,
            selected_patches,
            windows,
            review_states,
            news_quality,
        )
        schemas = _schemas()
        output_paths = {
            "games": store.write_table("games", game_rows, schemas["games"]),
            "announcements": store.write_table(
                "announcements", announcement_rows, schemas["announcements"]
            ),
            "patch_candidates": store.write_table(
                "patch_candidates", patch_rows, schemas["patch_candidates"]
            ),
            "review_revisions": store.write_table(
                "review_revisions", review_rows, schemas["review_revisions"]
            ),
            "review_window_memberships": store.write_table(
                "review_window_memberships", membership_rows, schemas["review_window_memberships"]
            ),
            "review_windows": store.write_table(
                "review_windows", window_rows, schemas["review_windows"]
            ),
            "source_observations": store.write_table(
                "source_observations",
                _observations_for_run(store, news_refs_by_app, review_states),
                schemas["source_observations"],
            ),
        }
        report_paths = _write_reports(
            resolved_reports,
            run_id,
            game_rows,
            announcement_rows,
            patch_rows,
            review_rows,
            membership_rows,
            window_rows,
            quality,
            news_states,
            config.review_languages,
            "pre_backfill",
        )
        ended = datetime.now(UTC)
        complete = all(state.get("status") == "complete" for state in news_states.values()) and all(
            row["collection_status"] == "complete" for row in window_rows
        )
        manifest.update(
            {
                "status": "complete" if complete else "partial",
                "finished_at_utc": ended.isoformat(),
                "request_attempts_used": budget.used,
                "review_language_filters_observed": _observed_review_filters(review_states),
                "quality": quality,
                "row_counts": {
                    "games": len(game_rows),
                    "announcements": len(announcement_rows),
                    "patch_candidates": len(patch_rows),
                    "review_revisions": len(review_rows),
                    "review_window_memberships": len(membership_rows),
                    "review_windows": len(window_rows),
                },
                "outputs": {name: str(path) for name, path in output_paths.items()},
                "reports": {name: str(path) for name, path in report_paths.items()},
            }
        )
    except RequestBudgetExceeded as exc:
        manifest["status"] = "partial"
        manifest["request_budget_exhausted"] = True
        manifest["error"] = str(exc)
        manifest["request_attempts_used"] = budget.used
        manifest["finished_at_utc"] = datetime.now(UTC).isoformat()
    except Exception as exc:
        manifest["status"] = "failed"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest["request_attempts_used"] = budget.used
        manifest["finished_at_utc"] = datetime.now(UTC).isoformat()
        raise
    except KeyboardInterrupt:
        manifest["status"] = "interrupted_resumable"
        manifest["error"] = (
            "Collection interrupted; completed-page checkpoints and raw blobs are preserved."
        )
        manifest["request_attempts_used"] = budget.used
        manifest["finished_at_utc"] = datetime.now(UTC).isoformat()
        raise
    finally:
        if owns_api:
            client.close()
        manifest["request_attempts_used"] = budget.used
        write_json(store.run_root / "manifest.json", manifest)
    print(json.dumps(manifest, indent=2), flush=True)
    return manifest


def materialize_from_checkpoints(
    config: CollectionConfig,
    *,
    repo_root: Path,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Rebuild normalized tables and reports offline from this pipeline's raw checkpoints."""
    storage_root = _resolve(repo_root, config.storage_root)
    report_root = _resolve(repo_root, config.report_root)
    runs_root = storage_root / "runs"
    available = (
        sorted(
            path.name
            for path in runs_root.iterdir()
            if path.is_dir() and _is_collection_run_name(path.name)
        )
        if runs_root.exists()
        else []
    )
    if not available:
        raise FileNotFoundError(f"No Stage 1 collection runs under {runs_root}")
    selected_run_id = run_id or available[-1]
    run_root = runs_root / selected_run_id
    manifest_path = run_root / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No collection manifest for run {selected_run_id}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    store = LocalStore(storage_root, selected_run_id)
    cfg_hash = config_hash(config.public_dict())
    news_refs_by_app: dict[int, list[dict[str, Any]]] = {}
    news_states: dict[int, dict[str, Any]] = {}
    news_quality: dict[int, list[str]] = defaultdict(list)
    selected_patches: list[dict[str, Any]] = []
    for game in config.games:
        since = int(datetime.fromisoformat(config.news_since.replace("Z", "+00:00")).timestamp())
        signature = config_hash(
            {"source": "news", "appid": game.appid, "since": since, "count": config.news_page_size}
        )
        checkpoint = store.load_checkpoint(f"news_{game.appid}_{signature[:10]}")
        if checkpoint is None:
            news_refs_by_app[game.appid] = []
            news_states[game.appid] = {
                "appid": game.appid,
                "status": "not_collected",
                "page_refs": [],
            }
            continue
        refs = list(checkpoint.get("page_refs", []))
        news_refs_by_app[game.appid] = refs
        news_states[game.appid] = checkpoint
        items, issues = _news_items_for_refs(store, refs, appid=game.appid)
        news_quality[game.appid].extend(issues)
        selected_patches.extend(_select_patch_candidates(items, game, config))

    windows: list[ReviewWindow] = []
    for selected in selected_patches:
        windows.extend(
            make_windows(
                appid=selected["appid"],
                announcement_id=selected["announcement_id"],
                title=selected["title"],
                anchor_unix=selected["published_unix"],
                days_before=config.days_before,
                days_after_early=config.days_after_early,
                days_after_late=config.days_after_late,
            )
        )
    review_states: dict[str, dict[str, Any]] = {}
    for window in windows:
        key = _window_key(window)
        checkpoint_key = _review_checkpoint_key(window, config.review_languages)
        checkpoint = store.load_checkpoint(checkpoint_key)
        if checkpoint:
            checkpoint = _reconcile_empty_review_page(store, checkpoint, checkpoint_key)
        review_states[key] = checkpoint or {
            "source_kind": "reviews",
            "appid": window.appid,
            "patch_id": window.patch_id,
            "announcement_id": window.announcement_id,
            "segment": window.segment,
            "start_unix": window.start_unix,
            "end_unix": window.end_unix,
            "status": "not_started",
            "page_count": 0,
            "page_refs": [],
        }

    game_rows, announcement_rows, patch_rows, review_rows, membership_rows, window_rows, quality = (
        _materialize(
            store,
            config,
            news_refs_by_app,
            news_states,
            selected_patches,
            windows,
            review_states,
            news_quality,
        )
    )
    schemas = _schemas()
    outputs = {
        "games": store.write_table("games", game_rows, schemas["games"]),
        "announcements": store.write_table(
            "announcements", announcement_rows, schemas["announcements"]
        ),
        "patch_candidates": store.write_table(
            "patch_candidates", patch_rows, schemas["patch_candidates"]
        ),
        "review_revisions": store.write_table(
            "review_revisions", review_rows, schemas["review_revisions"]
        ),
        "review_window_memberships": store.write_table(
            "review_window_memberships", membership_rows, schemas["review_window_memberships"]
        ),
        "review_windows": store.write_table(
            "review_windows", window_rows, schemas["review_windows"]
        ),
        "source_observations": store.write_table(
            "source_observations",
            _observations_for_run(store, news_refs_by_app, review_states),
            schemas["source_observations"],
        ),
    }
    report_paths = _write_reports(
        report_root,
        selected_run_id,
        game_rows,
        announcement_rows,
        patch_rows,
        review_rows,
        membership_rows,
        window_rows,
        quality,
        news_states,
        config.review_languages,
        manifest.get("language_collection_phase", "pre_backfill"),
    )
    manifest["review_language_filters_configured"] = list(config.review_languages)
    manifest["review_language_filters_observed"] = _observed_review_filters(review_states)
    manifest.setdefault("language_collection_phase", "pre_backfill")
    manifest.setdefault("language_backfill_performed", False)
    row_counts = {
        "games": len(game_rows),
        "announcements": len(announcement_rows),
        "patch_candidates": len(patch_rows),
        "review_revisions": len(review_rows),
        "review_window_memberships": len(membership_rows),
        "review_windows": len(window_rows),
    }
    manifest["materialization"] = {
        "status": "complete_from_available_checkpoints",
        "materialized_at_utc": datetime.now(UTC).isoformat(),
        "config_hash": cfg_hash,
        "code_fingerprint_sha256": _code_fingerprint(repo_root),
        "quality": quality,
        "row_counts": row_counts,
        "outputs": {name: str(path) for name, path in outputs.items()},
        "reports": {name: str(path) for name, path in report_paths.items()},
    }
    write_json(manifest_path, manifest)
    result = {
        "run_id": selected_run_id,
        "materialization_status": "complete_from_available_checkpoints",
        "source_collection_status": manifest.get("status"),
        "normalized_path": str(store.normalized_root),
        "report": str(report_paths["report"]),
        "row_counts": row_counts,
        "quality": quality,
    }
    print(json.dumps(result, indent=2), flush=True)
    return result


def _collect_news(
    api: SteamAPI,
    store: LocalStore,
    game: Game,
    config: CollectionConfig,
    *,
    refresh: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    since = int(datetime.fromisoformat(config.news_since.replace("Z", "+00:00")).timestamp())
    signature = config_hash(
        {"source": "news", "appid": game.appid, "since": since, "count": config.news_page_size}
    )
    checkpoint_key = f"news_{game.appid}_{signature[:10]}"
    previous = store.load_checkpoint(checkpoint_key)
    incremental_watermark = None
    if previous and previous.get("query_signature") == signature and not refresh:
        refs = list(previous.get("page_refs", []))
        if previous.get("status") == "complete":
            incremental_watermark = previous.get("newest_date")
            enddate = None
            page_number = 0
        else:
            enddate = previous.get("next_enddate")
            page_number = int(previous.get("page_count", 0))
    else:
        refs, enddate, page_number = [], None, 0

    state = {
        "query_signature": signature,
        "source_kind": "news",
        "appid": game.appid,
        "since_unix": since,
        "status": "partial",
        "next_enddate": enddate,
        "page_count": page_number,
        "page_refs": refs,
        "item_count": int(previous.get("item_count", 0)) if previous else 0,
        "newest_date": previous.get("newest_date") if previous else None,
        "incremental_watermark": incremental_watermark,
    }
    seen_pages = {ref["payload_sha256"] for ref in refs}
    try:
        pages_this_run = 0
        while pages_this_run < config.max_news_pages_per_game:
            response = api.get_news(game.appid, count=config.news_page_size, enddate=enddate)
            page_number += 1
            pages_this_run += 1
            ref = store.save_response(response, page_number=page_number)
            payload_hash = ref["payload_sha256"]
            if payload_hash not in seen_pages:
                refs.append(ref)
                seen_pages.add(payload_hash)
            wrapper = response.payload.get("appnews")
            if not isinstance(wrapper, dict):
                state["status"] = "invalid_response"
                state["issues"] = ["missing appnews response object"]
                break
            response_appid = wrapper.get("appid")
            if response_appid is not None and int(response_appid) != game.appid:
                state["status"] = "invalid_response"
                state["issues"] = [f"appnews.appid mismatch: {response_appid}"]
                break
            items = wrapper.get("newsitems")
            if not isinstance(items, list):
                state["status"] = "invalid_response"
                state["issues"] = ["missing or malformed appnews.newsitems list"]
                break
            state["item_count"] += len(items)
            if not items:
                state["status"] = "complete"
                state["next_enddate"] = None
                break
            valid_dates = [
                int(item["date"])
                for item in items
                if isinstance(item, dict) and _valid_unix(item.get("date"))
            ]
            if not valid_dates:
                state["status"] = "partial"
                state["issues"] = ["news page has no valid date boundary"]
                break
            oldest = min(valid_dates)
            newest = max(valid_dates)
            state["newest_date"] = max(_optional_int(state.get("newest_date")) or newest, newest)
            if incremental_watermark is not None and oldest <= int(incremental_watermark):
                state["status"] = "complete"
                state["next_enddate"] = None
                break
            if oldest <= since:
                state["status"] = "complete"
                state["next_enddate"] = None
                break
            next_enddate = oldest - 1
            if enddate is not None and next_enddate >= enddate:
                state["status"] = "no_progress"
                state["issues"] = ["news enddate failed to move backward"]
                break
            enddate = next_enddate
            state["next_enddate"] = enddate
            state["page_count"] = page_number
            state["page_refs"] = refs
            store.save_checkpoint(checkpoint_key, state)
        else:
            state["status"] = "page_budget_reached"
    except RequestBudgetExceeded:
        state["status"] = "request_budget_reached"
        state["next_enddate"] = enddate
    except SteamAPIError as exc:
        state["status"] = "request_error"
        state["issues"] = [str(exc)]
    state["page_count"] = page_number
    state["page_refs"] = refs
    store.save_checkpoint(checkpoint_key, state)
    return refs, state


def _collect_review_window(
    api: SteamAPI,
    store: LocalStore,
    window: ReviewWindow,
    config: CollectionConfig,
    *,
    refresh: bool,
) -> dict[str, Any]:
    query = {
        "source": "reviews",
        "appid": window.appid,
        "patch_id": window.patch_id,
        "segment": window.segment,
        "start": window.start_unix,
        "end": window.end_unix,
        # Keep the historical query signature for the default all-language snapshot so
        # its resumable checkpoints are continued instead of fetched again.
        **(
            {"language": "all"}
            if config.review_languages == ("all",)
            else {"languages": list(config.review_languages)}
        ),
        "filter": 1,
        "review_type": 0,
        "purchase_type": 1,
    }
    signature = config_hash(query)
    window_id = stable_id(
        "window", window.patch_id, window.segment, window.start_unix, window.end_unix
    )
    checkpoint_key = _review_checkpoint_key(window, config.review_languages)
    previous = store.load_checkpoint(checkpoint_key)
    if previous:
        previous = _reconcile_empty_review_page(store, previous, checkpoint_key)
    if previous and previous.get("query_signature") == signature and not refresh:
        if previous.get("status") == "complete":
            return previous
        refs = list(previous.get("page_refs", []))
        cursor = str(previous.get("next_cursor") or "*")
        page_number = int(previous.get("page_count", 0))
    else:
        refs, cursor, page_number = [], "*", 0
    state: dict[str, Any] = {
        "query_signature": signature,
        "source_kind": "reviews",
        "window_id": window_id,
        "appid": window.appid,
        "patch_id": window.patch_id,
        "announcement_id": window.announcement_id,
        "segment": window.segment,
        "start_unix": window.start_unix,
        "end_unix": window.end_unix,
        "status": "partial",
        "next_cursor": cursor,
        "page_count": page_number,
        "page_refs": refs,
    }
    seen_cursors: set[str] = set()
    try:
        pages_this_run = 0
        while pages_this_run < config.max_pages_per_review_window:
            response = api.get_reviews(
                window.appid,
                start_unix=window.start_unix,
                end_unix=window.end_unix,
                cursor=cursor,
                languages=config.review_languages,
            )
            page_number += 1
            pages_this_run += 1
            ref = store.save_response(response, page_number=page_number)
            if not any(item.get("payload_sha256") == ref["payload_sha256"] for item in refs):
                refs.append(ref)
            wrapper = response.payload.get("response")
            if not isinstance(wrapper, dict):
                state["status"] = "invalid_response"
                state["issues"] = ["missing response object"]
                break
            review_list = wrapper.get("reviews")
            if review_list is None:
                summary = wrapper.get("query_summary")
                if isinstance(summary, dict) and _optional_int(summary.get("num_reviews")) == 0:
                    review_list = []
                else:
                    state["status"] = "invalid_response"
                    state["issues"] = [
                        "missing response.reviews list without an empty-page summary"
                    ]
                    break
            if not isinstance(review_list, list):
                state["status"] = "invalid_response"
                state["issues"] = ["response.reviews is not a list"]
                break
            if not review_list:
                state["status"] = "complete"
                state["next_cursor"] = None
                break
            next_cursor = wrapper.get("cursor")
            if not isinstance(next_cursor, str) or not next_cursor:
                state["status"] = "invalid_response"
                state["issues"] = ["nonempty review page has no cursor"]
                break
            if next_cursor == cursor or next_cursor in seen_cursors:
                state["status"] = "no_progress"
                state["issues"] = ["review cursor repeated"]
                break
            seen_cursors.add(next_cursor)
            cursor = next_cursor
            state["next_cursor"] = cursor
            state["page_count"] = page_number
            state["page_refs"] = refs
            store.save_checkpoint(checkpoint_key, state)
        else:
            state["status"] = "page_budget_reached"
    except RequestBudgetExceeded:
        state["status"] = "request_budget_reached"
        state["next_cursor"] = cursor
    except SteamAPIError as exc:
        state["status"] = "request_error"
        state["issues"] = [str(exc)]
    state["page_count"] = page_number
    state["page_refs"] = refs
    store.save_checkpoint(checkpoint_key, state)
    return state


def _budget_partial_state(window: ReviewWindow, message: str) -> dict[str, Any]:
    return {
        "source_kind": "reviews",
        "appid": window.appid,
        "patch_id": window.patch_id,
        "announcement_id": window.announcement_id,
        "segment": window.segment,
        "start_unix": window.start_unix,
        "end_unix": window.end_unix,
        "status": "request_budget_reached",
        "page_count": 0,
        "page_refs": [],
        "issues": [message],
    }


def _news_items_for_refs(
    store: LocalStore,
    refs: list[dict[str, Any]],
    *,
    appid: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    items_by_revision: dict[str, dict[str, Any]] = {}
    issues: list[str] = []
    for ref in refs:
        payload = store.payload_for(ref)
        wrapper = payload.get("appnews")
        if not isinstance(wrapper, dict) or not isinstance(wrapper.get("newsitems"), list):
            issues.append(f"{ref['observation_id']}: malformed news wrapper")
            continue
        for item in wrapper["newsitems"]:
            if not isinstance(item, dict):
                issues.append(f"{ref['observation_id']}: non-object news item")
                continue
            if not item.get("gid"):
                issues.append(f"{ref['observation_id']}: news item missing gid")
                continue
            revision = stable_id(
                "announcement_revision",
                appid,
                str(item["gid"]),
                item.get("title"),
                item.get("date"),
                item.get("contents"),
            )
            enriched = dict(item)
            enriched["_payload_sha256"] = ref["payload_sha256"]
            enriched["_observation_id"] = ref["observation_id"]
            enriched["_announcement_revision_id"] = revision
            items_by_revision.setdefault(revision, enriched)
    return list(items_by_revision.values()), issues


def _select_patch_candidates(
    items: list[dict[str, Any]], game: Game, config: CollectionConfig
) -> list[dict[str, Any]]:
    since = int(datetime.fromisoformat(config.news_since.replace("Z", "+00:00")).timestamp())
    candidates: list[dict[str, Any]] = []
    for item in items:
        try:
            published_unix = int(item.get("date"))
        except (TypeError, ValueError):
            continue
        if published_unix < since:
            continue
        metadata = announcement_metadata(
            item, minimum_body_characters=config.minimum_body_characters
        )
        if not metadata["patch_candidate"]:
            continue
        announcement_id = str(item["gid"])
        candidates.append(
            {
                "appid": game.appid,
                "game_name": game.name,
                "announcement_id": announcement_id,
                "announcement_revision_id": item["_announcement_revision_id"],
                "patch_id": stable_id("patch", game.appid, announcement_id),
                "title": str(item.get("title") or ""),
                "published_unix": published_unix,
                "published_at_utc": utc_datetime(published_unix),
                "source_url": item.get("url"),
                "feedname": metadata["feedname"],
                "post_type": metadata["post_type"],
                "significance": metadata["significance"],
                "selection_score": metadata["selection_score"],
                "selection_reason": metadata["selection_reason"],
                "body_length": metadata["body_length"],
                "release_at_utc": None,
                "release_time_status": "not_exposed_by_public_news_record",
                "build_linkage_status": "unverified_public_news_record",
                "source_observation_id": item["_observation_id"],
                "payload_sha256": item["_payload_sha256"],
            }
        )
    candidates.sort(
        key=lambda row: (row["selection_score"], row["published_unix"], row["announcement_id"]),
        reverse=True,
    )
    selected = candidates[: config.max_patches_per_game]
    return selected


def _materialize(
    store: LocalStore,
    config: CollectionConfig,
    news_refs_by_app: dict[int, list[dict[str, Any]]],
    news_states: dict[int, dict[str, Any]],
    selected_patches: list[dict[str, Any]],
    windows: list[ReviewWindow],
    review_states: dict[str, dict[str, Any]],
    news_quality: dict[int, list[str]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
]:
    game_rows = [
        {
            "appid": game.appid,
            "game_name": game.name,
            "metadata_source": game.metadata_source,
            "catalog_discovery_used": False,
        }
        for game in config.games
    ]
    announcement_rows: list[dict[str, Any]] = []
    announcement_seen: set[str] = set()
    for game in config.games:
        items, _ = _news_items_for_refs(
            store, news_refs_by_app.get(game.appid, []), appid=game.appid
        )
        for item in items:
            metadata = announcement_metadata(
                item, minimum_body_characters=config.minimum_body_characters
            )
            published = int(item["date"]) if _valid_unix(item.get("date")) else None
            row_id = item["_announcement_revision_id"]
            if row_id in announcement_seen:
                continue
            announcement_seen.add(row_id)
            announcement_rows.append(
                {
                    "announcement_revision_id": row_id,
                    "appid": game.appid,
                    "announcement_id": str(item.get("gid") or ""),
                    "title": str(item.get("title") or ""),
                    "body_original": str(item.get("contents") or ""),
                    "announcement_language": (
                        item.get("language") if isinstance(item.get("language"), str) else None
                    ),
                    "announcement_language_metadata_status": language_metadata_status(
                        item.get("language")
                    ),
                    "published_unix": published,
                    "published_at_utc": utc_datetime(published),
                    "source_url": item.get("url"),
                    "author": item.get("author"),
                    "feedname": metadata["feedname"],
                    "feedlabel": metadata["feedlabel"],
                    "is_external_url": item.get("is_external_url"),
                    "officialness": metadata["officialness"],
                    "post_type": metadata["post_type"],
                    "significance": metadata["significance"],
                    "body_present": metadata["body_present"],
                    "body_length": metadata["body_length"],
                    "body_truncated_suspected": metadata["body_truncated_suspected"],
                    "linked_urls_json": canonical_json(metadata["linked_urls"]),
                    "patch_candidate_rule_match": metadata["patch_candidate"],
                    "classification_rule_version": ANNOUNCEMENT_RULE_VERSION,
                    "source_observation_id": item["_observation_id"],
                    "payload_sha256": item["_payload_sha256"],
                }
            )
    announcement_rows.sort(key=lambda row: (row["appid"], row["published_unix"] or 0))

    patch_rows = [
        {
            **candidate,
            "selection_rank": rank,
            "classification_rule_version": ANNOUNCEMENT_RULE_VERSION,
        }
        for game in config.games
        for rank, candidate in enumerate(
            [row for row in selected_patches if row["appid"] == game.appid], start=1
        )
    ]

    review_rows: dict[str, dict[str, Any]] = {}
    revision_contents: dict[str, set[str]] = defaultdict(set)
    revision_languages: dict[str, set[str]] = defaultdict(set)
    membership_rows: list[dict[str, Any]] = []
    membership_seen: set[tuple[str, str]] = set()
    window_rows: list[dict[str, Any]] = []
    invalid_reviews = 0
    repeated_reviews = 0
    window_by_key = {_window_key(window): window for window in windows}
    for key, state in review_states.items():
        window = window_by_key.get(key)
        if window is None:
            continue
        current_keys: set[str] = set()
        current_review_ids: set[str] = set()
        for ref in state.get("page_refs", []):
            payload = store.payload_for(ref)
            wrapper = payload.get("response")
            entries = wrapper.get("reviews", []) if isinstance(wrapper, dict) else []
            if not isinstance(entries, list):
                continue
            for review in entries:
                if not isinstance(review, dict) or review.get("recommendationid") is None:
                    invalid_reviews += 1
                    continue
                recommendation_id = str(review["recommendationid"])
                updated = _optional_int(review.get("timestamp_updated"))
                created = _optional_int(review.get("timestamp_created"))
                body_value = review.get("review")
                body = body_value if isinstance(body_value, str) else None
                content_bytes = (
                    body.encode("utf-8") if body is not None else b"<missing-review-text>"
                )
                content_hash = hashlib.sha256(content_bytes).hexdigest()
                language_value = review.get("language")
                language_code = language_value if isinstance(language_value, str) else None
                language_status = language_metadata_status(language_value)
                revision_key = stable_id("review_key", window.appid, recommendation_id, updated)
                revision_id = stable_id(
                    "review_revision", window.appid, recommendation_id, updated, content_hash
                )
                revision_contents[revision_key].add(content_hash)
                revision_languages[revision_id].add(canonical_json(language_value))
                if revision_id in current_keys:
                    repeated_reviews += 1
                current_keys.add(revision_id)
                current_review_ids.add(recommendation_id)
                if revision_id not in review_rows:
                    author = review.get("author") if isinstance(review.get("author"), dict) else {}
                    review_rows[revision_id] = {
                        "review_revision_id": revision_id,
                        "logical_revision_key": revision_key,
                        "appid": window.appid,
                        "recommendation_id": recommendation_id,
                        "created_unix": created,
                        "updated_unix": updated,
                        "created_at_utc": utc_datetime(created),
                        "updated_at_utc": utc_datetime(updated),
                        "review_text_original": body,
                        "language": language_code,
                        "language_metadata_status": language_status,
                        "detected_language": None,
                        "detected_language_confidence": None,
                        "voted_up": review.get("voted_up"),
                        "votes_up": _optional_int(review.get("votes_up")),
                        "votes_funny": _optional_int(review.get("votes_funny")),
                        "weighted_vote_score": _optional_float(review.get("weighted_vote_score")),
                        "comment_count": _optional_int(review.get("comment_count")),
                        "steam_purchase": review.get("steam_purchase"),
                        "received_for_free": review.get("received_for_free"),
                        "written_during_early_access": review.get("written_during_early_access"),
                        "primarily_steam_deck": review.get("primarily_steam_deck"),
                        "refunded": review.get("refunded"),
                        "author_steamid": str(author.get("steamid"))
                        if author.get("steamid")
                        else None,
                        "author_playtime_at_review": _optional_int(
                            author.get("playtime_at_review")
                        ),
                        "source_payload_sha256": ref["payload_sha256"],
                        "source_observation_id": ref["observation_id"],
                    }
                membership_key = (key, revision_id)
                if membership_key not in membership_seen:
                    membership_seen.add(membership_key)
                    membership_rows.append(
                        {
                            "patch_id": window.patch_id,
                            "appid": window.appid,
                            "announcement_id": window.announcement_id,
                            "review_revision_id": revision_id,
                            "review_id": recommendation_id,
                            "window_segment": window.segment,
                            "window_start_unix": window.start_unix,
                            "window_end_unix": window.end_unix,
                            "anchor_unix": window.anchor_unix,
                            "anchor_source": window.anchor_source,
                            "created_unix": created,
                            "membership_rule": "inclusive_steam_date_range",
                        }
                    )
        window_rows.append(
            {
                "window_id": stable_id(
                    "window", window.patch_id, window.segment, window.start_unix, window.end_unix
                ),
                "patch_id": window.patch_id,
                "appid": window.appid,
                "announcement_id": window.announcement_id,
                "segment": window.segment,
                "start_unix": window.start_unix,
                "end_unix": window.end_unix,
                "start_at_utc": utc_datetime(window.start_unix),
                "end_at_utc": utc_datetime(window.end_unix),
                "anchor_unix": window.anchor_unix,
                "anchor_source": window.anchor_source,
                "collection_status": state.get("status", "not_started"),
                "page_count": int(state.get("page_count", 0)),
                "unique_review_revisions": len(current_keys),
                "unique_review_ids": len(current_review_ids),
                "total_matching_reported": _reported_total(store, state),
                "review_coverage_fraction": _coverage_fraction(
                    len(current_keys), _reported_total(store, state)
                ),
                "issues_json": canonical_json(state.get("issues", [])),
            }
        )
    duplicate_conflicts = sum(1 for hashes in revision_contents.values() if len(hashes) > 1)
    language_conflicts = sum(1 for values in revision_languages.values() if len(values) > 1)
    language_status_counts = Counter(
        row["language_metadata_status"] for row in review_rows.values()
    )
    quality = {
        "news_schema_issues": {str(key): values for key, values in news_quality.items() if values},
        "announcement_rows_missing_body": sum(not row["body_present"] for row in announcement_rows),
        "announcement_rows_truncation_suspected": sum(
            row["body_truncated_suspected"] for row in announcement_rows
        ),
        "announcement_rows_with_links": sum(
            bool(json.loads(row["linked_urls_json"])) for row in announcement_rows
        ),
        "selected_patch_candidates_with_verified_build_linkage": sum(
            row.get("build_linkage_status") == "verified" for row in patch_rows
        ),
        "invalid_review_records": invalid_reviews,
        "repeated_review_records_within_windows": repeated_reviews,
        "conflicting_same_update_text_versions": duplicate_conflicts,
        "conflicting_review_language_metadata": language_conflicts,
        "review_language_metadata_status_counts": dict(sorted(language_status_counts.items())),
        "patch_candidate_count_by_game": {
            str(game.appid): sum(1 for row in patch_rows if row["appid"] == game.appid)
            for game in config.games
        },
        "windows_complete": sum(1 for row in window_rows if row["collection_status"] == "complete"),
        "windows_total": len(window_rows),
    }
    return (
        game_rows,
        announcement_rows,
        patch_rows,
        list(review_rows.values()),
        membership_rows,
        window_rows,
        quality,
    )


def _reported_total(store: LocalStore, state: dict[str, Any]) -> int | None:
    total: int | None = None
    for ref in state.get("page_refs", []):
        payload = store.payload_for(ref)
        wrapper = payload.get("response")
        if isinstance(wrapper, dict):
            value = wrapper.get("total_matching")
            if value is not None:
                try:
                    total = max(total or 0, int(value))
                except (ValueError, TypeError):
                    pass
    return total


def _reconcile_empty_review_page(
    store: LocalStore, state: dict[str, Any], checkpoint_key: str
) -> dict[str, Any]:
    """Treat an omitted empty reviews array as terminal only when Steam says count is zero."""
    issues = " ".join(state.get("issues", []))
    if state.get("status") != "invalid_response" or not state.get("page_refs"):
        return state
    if "missing response.reviews list" not in issues:
        return state
    payload = store.payload_for(state["page_refs"][-1])
    wrapper = payload.get("response")
    summary = wrapper.get("query_summary") if isinstance(wrapper, dict) else None
    if (
        isinstance(wrapper, dict)
        and "reviews" not in wrapper
        and isinstance(summary, dict)
        and _optional_int(summary.get("num_reviews")) == 0
    ):
        state = dict(state)
        state["status"] = "complete"
        state["next_cursor"] = None
        state["issues"] = []
        store.save_checkpoint(checkpoint_key, state)
    return state


def _write_reports(
    report_root: Path,
    run_id: str,
    game_rows: list[dict[str, Any]],
    announcement_rows: list[dict[str, Any]],
    patch_rows: list[dict[str, Any]],
    review_rows: list[dict[str, Any]],
    membership_rows: list[dict[str, Any]],
    window_rows: list[dict[str, Any]],
    quality: dict[str, Any],
    news_states: dict[int, dict[str, Any]],
    review_languages: tuple[str, ...],
    collection_phase: str,
) -> dict[str, Path]:
    current = report_root / run_id
    current.mkdir(parents=True, exist_ok=True)
    language_summary, language_paths = write_language_reports(
        current,
        run_id=run_id,
        review_languages=review_languages,
        game_rows=game_rows,
        announcement_rows=announcement_rows,
        review_rows=review_rows,
        membership_rows=membership_rows,
        window_rows=window_rows,
        collection_phase=collection_phase,
    )
    quality["language_coverage"] = language_summary
    announcements_by_app: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in announcement_rows:
        announcements_by_app[row["appid"]].append(row)
    patches_by_app: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in patch_rows:
        patches_by_app[row["appid"]].append(row)
    windows_by_app: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in window_rows:
        windows_by_app[row["appid"]].append(row)
    reviews_by_app: dict[int, set[str]] = defaultdict(set)
    for row in review_rows:
        reviews_by_app[row["appid"]].add(row["review_revision_id"])
    membership_by_app: dict[int, set[str]] = defaultdict(set)
    for row in membership_rows:
        membership_by_app[row["appid"]].add(row["review_revision_id"])

    game_summary: list[dict[str, Any]] = []
    for game in game_rows:
        appid = int(game["appid"])
        news_state = news_states.get(appid, {})
        app_windows = windows_by_app[appid]
        game_summary.append(
            {
                "appid": appid,
                "game_name": game["game_name"],
                "news_collection_status": news_state.get("status", "not_started"),
                "announcements_seen": len(announcements_by_app[appid]),
                "steam_community_feed_announcements": sum(
                    row["officialness"] == "steam_community_announcement_feed"
                    for row in announcements_by_app[appid]
                ),
                "usable_official_announcements": sum(
                    row["officialness"] == "steam_community_announcement_feed"
                    and row["body_present"]
                    for row in announcements_by_app[appid]
                ),
                "announcements_missing_body": sum(
                    not row["body_present"] for row in announcements_by_app[appid]
                ),
                "announcements_with_links": sum(
                    bool(json.loads(row["linked_urls_json"])) for row in announcements_by_app[appid]
                ),
                "patch_candidates_selected": len(patches_by_app[appid]),
                "unique_review_revisions": len(reviews_by_app[appid]),
                "review_window_memberships": len(membership_by_app[appid]),
                "review_window_revisions_collected": sum(
                    row["unique_review_revisions"] for row in app_windows
                ),
                "review_window_total_reported": sum(
                    row["total_matching_reported"] or 0 for row in app_windows
                ),
                "review_window_coverage_fraction": _coverage_fraction(
                    sum(row["unique_review_revisions"] for row in app_windows),
                    sum(row["total_matching_reported"] or 0 for row in app_windows),
                ),
                "review_windows_complete": sum(
                    row["collection_status"] == "complete" for row in app_windows
                ),
                "review_windows_total": len(app_windows),
                "all_patch_windows_complete": bool(app_windows)
                and all(row["collection_status"] == "complete" for row in app_windows),
            }
        )
    write_csv(
        current / "game_coverage.csv",
        game_summary,
        [
            "appid",
            "game_name",
            "news_collection_status",
            "announcements_seen",
            "steam_community_feed_announcements",
            "usable_official_announcements",
            "announcements_missing_body",
            "announcements_with_links",
            "patch_candidates_selected",
            "unique_review_revisions",
            "review_window_memberships",
            "review_window_revisions_collected",
            "review_window_total_reported",
            "review_window_coverage_fraction",
            "review_windows_complete",
            "review_windows_total",
            "all_patch_windows_complete",
        ],
    )
    write_csv(
        current / "patch_coverage.csv",
        window_rows,
        [
            "appid",
            "patch_id",
            "announcement_id",
            "segment",
            "start_at_utc",
            "end_at_utc",
            "collection_status",
            "page_count",
            "unique_review_revisions",
            "unique_review_ids",
            "total_matching_reported",
            "review_coverage_fraction",
            "issues_json",
        ],
    )
    report = [
        "# Stage 1 Steam source coverage",
        "",
        f"Run: `{run_id}`",
        "",
        "## Game coverage",
        "",
        "| App ID | Game | News status | Announcements | Official feed | Usable official | Selected candidates | Unique review revisions | Review population coverage | Complete windows / total |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in game_summary:
        report.append(
            f"| {row['appid']} | {row['game_name']} | {row['news_collection_status']} | "
            f"{row['announcements_seen']} | {row['steam_community_feed_announcements']} | "
            f"{row['usable_official_announcements']} | {row['patch_candidates_selected']} | "
            f"{row['unique_review_revisions']} | {row['review_window_coverage_fraction']} | "
            f"{row['review_windows_complete']} / {row['review_windows_total']} |"
        )
    report.extend(
        [
            "",
            "## Selected patch candidates",
            "",
            "These are rule-based candidates from Steam's publisher announcement feed, not build-verified patches. The public news record does not supply a verified effective release timestamp; review windows use publication time.",
            "",
        ]
    )
    for patch in patch_rows:
        report.append(
            f"- **{patch['game_name']} — {patch['title']}** ({patch['published_at_utc']}); "
            f"type `{patch['post_type']}`, score {patch['selection_score']}, id `{patch['patch_id']}`."
        )
    report.extend(
        [
            "",
            "## Source gaps and interpretation",
            "",
            "- `GetNewsForApp` returned mixed publisher/community and other feed entries. All were preserved; only the explicitly named Steam Community Announcements feed can enter the candidate rule.",
            "- `maxlength=0` requests full Steam post content. A body can still be empty or link to an off-site changelog. Links are retained, but arbitrary external sites are not fetched automatically; the `announcements` Parquet table flags empty bodies and stores links.",
            f"- This run has {quality['announcement_rows_missing_body']} announcements with no body, {quality['announcement_rows_truncation_suspected']} with a truncation heuristic flag, and {quality['announcement_rows_with_links']} with one or more links.",
            "- Steam's public news API does not document an event-type/build filter or an exact build release time. Candidate counts are not verified patch counts.",
            f"- Verified build-linked patches in this dataset: {quality['selected_patch_candidates_with_verified_build_linkage']}; selected announcement candidates remain unverified.",
            "- The Reviews API returns current review revisions. SteamIDs and author playtime may appear in the raw source blobs; keep raw data local and restrict access.",
            "- Review collection uses inclusive creation-time bounds. A window is complete only after an empty cursor page; `page_budget_reached`, `request_budget_reached`, and request errors remain explicit partial states.",
            "- `Recommended` is stored as an overall review vote only; it is not used as feature-level sentiment.",
            "- Game IDs in this collection run were curated seeds because no key was configured then. A separate follow-up collected a complete game catalog and confirmed all four IDs; see [the catalog report](../catalog/rv1-catalog-20261019T035528Z/report.md).",
            "",
            "## Patch-window coverage",
            "",
            "The multilingual language distribution for games and each selected patch window is available in [language_coverage.md](language_coverage.md), with machine-readable CSVs alongside it.",
            "",
        ]
    )
    for row in window_rows:
        report.append(
            f"- `{row['appid']}` `{row['announcement_id']}` / `{row['segment']}`: "
            f"{row['collection_status']}, {row['unique_review_revisions']} / "
            f"{row['total_matching_reported']} reviews ({row['review_coverage_fraction']}), "
            f"{row['page_count']} pages."
        )
    report.extend(
        ["", "## Quality summary", "", "```json", json.dumps(quality, indent=2), "```", ""]
    )
    (current / "report.md").write_text("\n".join(report), encoding="utf-8")
    write_json(current / "quality.json", quality)
    latest = report_root / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    for name in (
        "game_coverage.csv",
        "patch_coverage.csv",
        "report.md",
        "quality.json",
        "language_by_game.csv",
        "language_by_patch_window.csv",
        "language_coverage.json",
        "language_coverage.md",
    ):
        source = current / name
        target = latest / name
        target.write_bytes(source.read_bytes())
    return {
        "report": current / "report.md",
        "game_coverage": current / "game_coverage.csv",
        "patch_coverage": current / "patch_coverage.csv",
        "latest_report": latest / "report.md",
        **language_paths,
        "latest_language_report": latest / "language_coverage.md",
    }


def _schemas() -> dict[str, pa.Schema]:
    utc = pa.timestamp("us", tz="UTC")
    return {
        "games": pa.schema(
            [
                ("appid", pa.int64()),
                ("game_name", pa.string()),
                ("metadata_source", pa.string()),
                ("catalog_discovery_used", pa.bool_()),
            ]
        ),
        "announcements": pa.schema(
            [
                ("announcement_revision_id", pa.string()),
                ("appid", pa.int64()),
                ("announcement_id", pa.string()),
                ("title", pa.string()),
                ("body_original", pa.large_string()),
                ("published_unix", pa.int64()),
                ("published_at_utc", utc),
                ("source_url", pa.string()),
                ("author", pa.string()),
                ("announcement_language", pa.string()),
                ("announcement_language_metadata_status", pa.string()),
                ("feedname", pa.string()),
                ("feedlabel", pa.string()),
                ("is_external_url", pa.bool_()),
                ("officialness", pa.string()),
                ("post_type", pa.string()),
                ("significance", pa.string()),
                ("body_present", pa.bool_()),
                ("body_length", pa.int64()),
                ("body_truncated_suspected", pa.bool_()),
                ("linked_urls_json", pa.large_string()),
                ("patch_candidate_rule_match", pa.bool_()),
                ("classification_rule_version", pa.string()),
                ("source_observation_id", pa.string()),
                ("payload_sha256", pa.string()),
            ]
        ),
        "patch_candidates": pa.schema(
            [
                ("appid", pa.int64()),
                ("game_name", pa.string()),
                ("announcement_id", pa.string()),
                ("announcement_revision_id", pa.string()),
                ("patch_id", pa.string()),
                ("title", pa.string()),
                ("published_unix", pa.int64()),
                ("published_at_utc", utc),
                ("source_url", pa.string()),
                ("feedname", pa.string()),
                ("post_type", pa.string()),
                ("significance", pa.string()),
                ("selection_score", pa.int64()),
                ("selection_reason", pa.string()),
                ("body_length", pa.int64()),
                ("release_at_utc", utc),
                ("release_time_status", pa.string()),
                ("build_linkage_status", pa.string()),
                ("source_observation_id", pa.string()),
                ("payload_sha256", pa.string()),
                ("selection_rank", pa.int64()),
                ("classification_rule_version", pa.string()),
            ]
        ),
        "review_revisions": pa.schema(
            [
                ("review_revision_id", pa.string()),
                ("logical_revision_key", pa.string()),
                ("appid", pa.int64()),
                ("recommendation_id", pa.string()),
                ("created_unix", pa.int64()),
                ("updated_unix", pa.int64()),
                ("created_at_utc", utc),
                ("updated_at_utc", utc),
                ("review_text_original", pa.large_string()),
                ("language", pa.string()),
                ("language_metadata_status", pa.string()),
                ("detected_language", pa.string()),
                ("detected_language_confidence", pa.float64()),
                ("voted_up", pa.bool_()),
                ("votes_up", pa.int64()),
                ("votes_funny", pa.int64()),
                ("weighted_vote_score", pa.float64()),
                ("comment_count", pa.int64()),
                ("steam_purchase", pa.bool_()),
                ("received_for_free", pa.bool_()),
                ("written_during_early_access", pa.bool_()),
                ("primarily_steam_deck", pa.bool_()),
                ("refunded", pa.bool_()),
                ("author_steamid", pa.string()),
                ("author_playtime_at_review", pa.int64()),
                ("source_payload_sha256", pa.string()),
                ("source_observation_id", pa.string()),
            ]
        ),
        "review_window_memberships": pa.schema(
            [
                ("patch_id", pa.string()),
                ("appid", pa.int64()),
                ("announcement_id", pa.string()),
                ("review_revision_id", pa.string()),
                ("review_id", pa.string()),
                ("window_segment", pa.string()),
                ("window_start_unix", pa.int64()),
                ("window_end_unix", pa.int64()),
                ("anchor_unix", pa.int64()),
                ("anchor_source", pa.string()),
                ("created_unix", pa.int64()),
                ("membership_rule", pa.string()),
            ]
        ),
        "review_windows": pa.schema(
            [
                ("window_id", pa.string()),
                ("patch_id", pa.string()),
                ("appid", pa.int64()),
                ("announcement_id", pa.string()),
                ("segment", pa.string()),
                ("start_unix", pa.int64()),
                ("end_unix", pa.int64()),
                ("start_at_utc", utc),
                ("end_at_utc", utc),
                ("anchor_unix", pa.int64()),
                ("anchor_source", pa.string()),
                ("collection_status", pa.string()),
                ("page_count", pa.int64()),
                ("unique_review_revisions", pa.int64()),
                ("unique_review_ids", pa.int64()),
                ("total_matching_reported", pa.int64()),
                ("review_coverage_fraction", pa.float64()),
                ("issues_json", pa.large_string()),
            ]
        ),
        "source_observations": pa.schema(
            [
                ("observation_id", pa.string()),
                ("source_identity", pa.string()),
                ("appid", pa.int64()),
                ("source_kind", pa.string()),
                ("endpoint", pa.string()),
                ("source_url", pa.string()),
                ("retrieved_at_utc", pa.string()),
                ("request_params_json", pa.large_string()),
                ("page_number", pa.int64()),
                ("http_status", pa.int64()),
                ("payload_sha256", pa.string()),
                ("payload_path", pa.string()),
            ]
        ),
    }


def _observations_as_rows(path: Path) -> list[dict[str, Any]]:
    rows = read_jsonl(path)
    return rows


def _observations_for_run(
    store: LocalStore,
    news_refs_by_app: dict[int, list[dict[str, Any]]],
    review_states: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows_by_id = {
        row["observation_id"]: row for row in _observations_as_rows(store.observation_path)
    }
    for refs in news_refs_by_app.values():
        for ref in refs:
            rows_by_id[ref["observation_id"]] = ref
    for state in review_states.values():
        for ref in state.get("page_refs", []):
            rows_by_id[ref["observation_id"]] = ref
    return list(rows_by_id.values())


def _resolve(root: Path, path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def _is_collection_run_name(name: str) -> bool:
    return name.startswith("rv1-") and len(name) > 4 and name[4].isdigit()


def _valid_unix(value: Any) -> bool:
    try:
        int(value)
        return True
    except (TypeError, ValueError, OverflowError):
        return False


def _optional_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError, OverflowError):
        return None


def _optional_float(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError, OverflowError):
        return None


def _coverage_fraction(collected: int, reported: int | None) -> float | None:
    if reported is None or reported <= 0:
        return None
    return round(min(1.0, collected / reported), 4)


def _window_key(window: ReviewWindow) -> str:
    return stable_id("window", window.patch_id, window.segment, window.start_unix, window.end_unix)


def _review_checkpoint_key(window: ReviewWindow, languages: tuple[str, ...]) -> str:
    window_id = _window_key(window)
    base = f"reviews_{window_id[4:]}"
    if languages == ("all",):
        # Preserve and continue the Stage 1 all-language checkpoint names.
        return base
    return f"{base}_lang_{config_hash({'languages': list(languages)})[:10]}"


def _observed_review_filters(review_states: dict[str, dict[str, Any]]) -> list[list[str]]:
    observed: set[tuple[str, ...]] = set()
    for state in review_states.values():
        for ref in state.get("page_refs", []):
            params = ref.get("request_params_json", {})
            if isinstance(params, str):
                try:
                    params = json.loads(params)
                except json.JSONDecodeError:
                    continue
            input_json = params.get("input_json", {}) if isinstance(params, dict) else {}
            languages = input_json.get("languages") if isinstance(input_json, dict) else None
            if isinstance(languages, list) and all(isinstance(code, str) for code in languages):
                observed.add(tuple(languages))
    return [list(languages) for languages in sorted(observed)]


def _git_revision(repo_root: Path) -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _code_fingerprint(repo_root: Path) -> str:
    root = repo_root / "src" / "steam_patch_relevance"
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*.py")):
        digest.update(path.relative_to(repo_root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()
