"""HTTPX clients for the documented public Steam endpoints."""

from __future__ import annotations

import json
import random
import time
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any, Callable

import httpx

from steam_patch_relevance.models import APIResponse

PUBLIC_BASE = "https://api.steampowered.com"
NEWS_PATH = "/ISteamNews/GetNewsForApp/v2/"
REVIEWS_PATH = "/IUserReviewsService/GetAppReviews/v1/"
APP_LIST_URL = f"{PUBLIC_BASE}/IStoreService/GetAppList/v1/"


class RequestBudgetExceeded(RuntimeError):
    pass


class SteamAPIError(RuntimeError):
    pass


class RequestBudget:
    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.used = 0

    def consume(self) -> None:
        if self.used >= self.limit:
            raise RequestBudgetExceeded(f"Request budget exhausted ({self.limit} attempts)")
        self.used += 1


class SteamAPI:
    def __init__(
        self,
        *,
        budget: RequestBudget,
        timeout: float = 30,
        min_request_interval: float = 0.5,
        retries: int = 5,
        backoff_base: float = 0.75,
        backoff_max: float = 30,
        client: httpx.Client | None = None,
        sleeper: Callable[[float], None] = time.sleep,
        random_value: Callable[[], float] = random.random,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self.budget = budget
        self.retries = retries
        self.min_request_interval = max(0.0, min_request_interval)
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.sleeper = sleeper
        self.random_value = random_value
        self.clock = clock
        self.monotonic = monotonic
        self._last_request_at: float | None = None
        self.client = client or httpx.Client(timeout=timeout, follow_redirects=True)
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self.client.close()

    def __enter__(self) -> SteamAPI:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def get_news(self, appid: int, *, count: int, enddate: int | None) -> APIResponse:
        params: dict[str, Any] = {"appid": appid, "count": count, "maxlength": 0}
        if enddate is not None:
            params["enddate"] = enddate
        return self._get_json("news", appid, NEWS_PATH, params)

    def get_reviews(
        self,
        appid: int,
        *,
        start_unix: int,
        end_unix: int,
        cursor: str,
        languages: tuple[str, ...] | list[str] = ("all",),
        num_per_page: int = 100,
    ) -> APIResponse:
        input_json = {
            "appid": appid,
            "filter": 1,
            "languages": list(languages),
            "cursor": cursor,
            "review_type": 0,
            "purchase_type": 1,
            "num_per_page": num_per_page,
            "filter_offtopic_activity": False,
            "date_range_start": start_unix,
            "date_range_end": end_unix,
        }
        return self._get_json("reviews", appid, REVIEWS_PATH, {"input_json": input_json})

    def get_app_list(
        self, *, api_key: str, last_appid: int | None, max_results: int
    ) -> APIResponse:
        input_json: dict[str, Any] = {"max_results": max_results, "include_games": True}
        if last_appid is not None:
            input_json["last_appid"] = last_appid
        return self._get_json(
            "app_list",
            0,
            APP_LIST_URL,
            {"input_json": input_json, "key": api_key, "format": "json"},
            source_url=APP_LIST_URL,
        )

    def _get_json(
        self,
        source_kind: str,
        appid: int,
        path: str,
        params: dict[str, Any],
        *,
        source_url: str | None = None,
    ) -> APIResponse:
        safe_params = _safe_params(params)
        wire_params = dict(params)
        if "input_json" in wire_params:
            wire_params["input_json"] = json.dumps(
                wire_params["input_json"], ensure_ascii=False, separators=(",", ":")
            )
        url = path if path.startswith("https://") else f"{PUBLIC_BASE}{path}"
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            self.budget.consume()
            self._pace()
            try:
                response = self.client.get(url, params=wire_params)
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt >= self.retries:
                    raise SteamAPIError(f"Network error calling {source_kind}: {exc}") from exc
                self._backoff(attempt, retry_after=None)
                continue

            if response.status_code == 429 or response.status_code >= 500:
                if attempt >= self.retries:
                    raise SteamAPIError(
                        f"Steam {source_kind} returned HTTP {response.status_code} after retries"
                    )
                self._backoff(attempt, retry_after=response.headers.get("Retry-After"))
                continue
            if response.status_code >= 400:
                raise SteamAPIError(f"Steam {source_kind} returned HTTP {response.status_code}")
            try:
                payload = response.json()
            except ValueError as exc:
                raise SteamAPIError(f"Steam {source_kind} returned invalid JSON") from exc
            if not isinstance(payload, dict):
                raise SteamAPIError(f"Steam {source_kind} returned a non-object JSON response")
            return APIResponse(
                source_kind=source_kind,
                appid=appid,
                endpoint=url.split("?", 1)[0],
                source_url=source_url or url.split("?", 1)[0],
                request_params=safe_params,
                status_code=response.status_code,
                retrieved_at_utc=self.clock(),
                payload_bytes=response.content,
                payload=payload,
            )
        raise SteamAPIError(f"Steam {source_kind} request failed: {last_error}")

    def _backoff(self, attempt: int, *, retry_after: str | None) -> None:
        delay: float | None = None
        if retry_after:
            try:
                delay = max(0.0, float(retry_after))
            except ValueError:
                try:
                    retry_at = parsedate_to_datetime(retry_after)
                    if retry_at.tzinfo is None:
                        retry_at = retry_at.replace(tzinfo=UTC)
                    delay = max(0.0, (retry_at - self.clock()).total_seconds())
                except (TypeError, ValueError, OverflowError):
                    delay = None
        if delay is None:
            base = min(self.backoff_max, self.backoff_base * (2**attempt))
            delay = base * (0.75 + self.random_value() * 0.5)
        self.sleeper(min(self.backoff_max, delay))

    def _pace(self) -> None:
        now = self.monotonic()
        if self._last_request_at is not None:
            wait = self.min_request_interval - (now - self._last_request_at)
            if wait > 0:
                self.sleeper(wait)
        self._last_request_at = self.monotonic()


def _safe_params(params: dict[str, Any]) -> dict[str, Any]:
    safe = dict(params)
    safe.pop("key", None)
    return safe
