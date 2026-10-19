"""Configuration loading and validation."""

from __future__ import annotations

import tomllib
from pathlib import Path

from steam_patch_relevance.models import CollectionConfig, Game


def load_config(path: Path, *, max_requests: int | None = None) -> CollectionConfig:
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    collection = raw["collection"]
    selection = raw["patch_selection"]
    windows = raw["windows"]
    configured_languages = raw.get("reviews", {}).get("languages", ["all"])
    if not isinstance(configured_languages, list):
        raise ValueError("reviews.languages must be a list of Steam API language codes")
    review_languages = tuple(configured_languages)
    games = tuple(Game(appid=int(row["appid"]), name=str(row["name"])) for row in raw["games"])
    config = CollectionConfig(
        storage_root=str(collection["storage_root"]),
        report_root=str(collection["report_root"]),
        news_since=str(collection["news_since"]),
        news_page_size=int(collection["news_page_size"]),
        max_news_pages_per_game=int(collection["max_news_pages_per_game"]),
        max_pages_per_review_window=int(collection["max_pages_per_review_window"]),
        max_requests=int(max_requests or collection["max_requests"]),
        max_retries=int(collection["max_retries"]),
        request_timeout_seconds=float(collection["request_timeout_seconds"]),
        min_request_interval_seconds=float(collection["min_request_interval_seconds"]),
        backoff_base_seconds=float(collection["backoff_base_seconds"]),
        backoff_max_seconds=float(collection["backoff_max_seconds"]),
        max_patches_per_game=int(selection["max_patches_per_game"]),
        minimum_body_characters=int(selection["minimum_body_characters"]),
        days_before=int(windows["days_before"]),
        days_after_early=int(windows["days_after_early"]),
        days_after_late=int(windows["days_after_late"]),
        games=games,
        review_languages=review_languages,
    )
    if not config.games or len({game.appid for game in config.games}) != len(config.games):
        raise ValueError("Configuration must contain unique game app IDs")
    if config.max_requests < 1 or config.news_page_size < 1:
        raise ValueError("Request budget and page size must be positive")
    if min(config.days_before, config.days_after_early, config.days_after_late) < 1:
        raise ValueError("Review window lengths must be positive")
    if (
        not config.review_languages
        or any(
            not isinstance(language, str) or not language or language.strip() != language
            for language in config.review_languages
        )
        or len(set(config.review_languages)) != len(config.review_languages)
        or ("all" in config.review_languages and config.review_languages != ("all",))
    ):
        raise ValueError(
            "reviews.languages must be a non-empty list of unique Steam API language codes; "
            "use ['all'] for every language, since an empty list means English"
        )
    return config
