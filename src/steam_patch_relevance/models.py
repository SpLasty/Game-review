"""Small typed records shared by the Stage 1 source collectors."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Game:
    appid: int
    name: str
    metadata_source: str = "curated_pilot_seed"


@dataclass(frozen=True)
class CollectionConfig:
    storage_root: str
    report_root: str
    news_since: str
    news_page_size: int
    max_news_pages_per_game: int
    max_pages_per_review_window: int
    max_requests: int
    max_retries: int
    request_timeout_seconds: float
    min_request_interval_seconds: float
    backoff_base_seconds: float
    backoff_max_seconds: float
    max_patches_per_game: int
    minimum_body_characters: int
    days_before: int
    days_after_early: int
    days_after_late: int
    games: tuple[Game, ...]
    review_languages: tuple[str, ...] = ("all",)

    def public_dict(self) -> dict[str, Any]:
        return {
            "storage_root": self.storage_root,
            "report_root": self.report_root,
            "news_since": self.news_since,
            "news_page_size": self.news_page_size,
            "max_news_pages_per_game": self.max_news_pages_per_game,
            "max_pages_per_review_window": self.max_pages_per_review_window,
            "max_requests": self.max_requests,
            "max_retries": self.max_retries,
            "request_timeout_seconds": self.request_timeout_seconds,
            "min_request_interval_seconds": self.min_request_interval_seconds,
            "backoff_base_seconds": self.backoff_base_seconds,
            "backoff_max_seconds": self.backoff_max_seconds,
            "max_patches_per_game": self.max_patches_per_game,
            "minimum_body_characters": self.minimum_body_characters,
            "days_before": self.days_before,
            "days_after_early": self.days_after_early,
            "days_after_late": self.days_after_late,
            "review_languages": list(self.review_languages),
            "games": [game.__dict__ for game in self.games],
        }


@dataclass(frozen=True)
class APIResponse:
    source_kind: str
    appid: int
    endpoint: str
    source_url: str
    request_params: dict[str, Any]
    status_code: int
    retrieved_at_utc: datetime
    payload_bytes: bytes
    payload: dict[str, Any]


@dataclass(frozen=True)
class ReviewWindow:
    patch_id: str
    appid: int
    announcement_id: str
    title: str
    segment: str
    start_unix: int
    end_unix: int
    anchor_unix: int
    anchor_source: str
