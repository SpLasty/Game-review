"""Conservative announcement triage; never treats every news post as a patch."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from html.parser import HTMLParser
from typing import Any

PATCH_TITLE = re.compile(
    r"\b(patch(?: notes)?|update|hotfix|balance|maintenance|version\s*[\d.]+)\b", re.I
)
CONTENT_TITLE = re.compile(
    r"\b(introducing|new expedition|expedition\s+\d+|new campaign|part\s+[ivx0-9]+|new mode|new content)\b",
    re.I,
)
VERSION_TITLE = re.compile(r"\bv?\d+(?:\.\d+){1,3}\b", re.I)
PROMO = re.compile(
    r"\b(sale|discount|weekend|livestream|giveaway|tournament|esports|event)\b", re.I
)
LOW_SIGNAL = re.compile(r"\b(localization|localized|typo|minor text|translation)\b", re.I)


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href and href.startswith(("http://", "https://")):
            self.urls.append(href)


def extract_links(body: str) -> list[str]:
    parser = _Links()
    try:
        parser.feed(body)
    except Exception:
        return []
    return list(dict.fromkeys(parser.urls))


def announcement_metadata(item: dict[str, Any], *, minimum_body_characters: int) -> dict[str, Any]:
    title = str(item.get("title") or "")
    body = str(item.get("contents") or "")
    feedname = str(item.get("feedname") or "")
    officialness = (
        "steam_community_announcement_feed"
        if feedname.casefold() == "steam_community_announcements"
        else ("other_feed_unverified" if feedname else "feed_unknown")
    )
    promo_match = bool(PROMO.search(title))
    update_match = bool(
        PATCH_TITLE.search(title) or CONTENT_TITLE.search(title) or VERSION_TITLE.search(title)
    )
    low_signal = bool(LOW_SIGNAL.search(title))
    if promo_match:
        post_type = "promotion_or_event"
        significance = "low"
    elif re.search(r"\b(major update|expansion|new season|new campaign)\b", title, re.I):
        post_type = "major_update_candidate"
        significance = "high"
    elif CONTENT_TITLE.search(title):
        post_type = "content_update_candidate"
        significance = "high"
    elif VERSION_TITLE.search(title):
        post_type = "versioned_update_candidate"
        significance = "high"
    elif re.search(r"\b(patch notes|hotfix|balance|bug fix|fixes)\b", title, re.I):
        post_type = "patch_notes_candidate"
        significance = "medium"
    elif update_match:
        post_type = "update_candidate"
        significance = "medium"
    elif low_signal:
        post_type = "low_significance_update"
        significance = "low"
    else:
        post_type = "other_or_unclassified"
        significance = "unknown"

    body_length = len(body.strip())
    candidate = (
        officialness == "steam_community_announcement_feed"
        and update_match
        and not promo_match
        and not low_signal
        and body_length >= minimum_body_characters
    )
    score = int(update_match) * 100 + min(body_length, 10_000) // 100
    score += 30 if re.search(r"\b(patch notes|hotfix|balance|fixes)\b", title, re.I) else 0
    score += (
        20 if re.search(r"\b(major update|expansion|new season|new campaign)\b", title, re.I) else 0
    )
    score += 20 if CONTENT_TITLE.search(title) else 0
    if promo_match or low_signal:
        score -= 100

    return {
        "feedname": feedname or None,
        "feedlabel": item.get("feedlabel"),
        "officialness": officialness,
        "post_type": post_type,
        "significance": significance,
        "patch_candidate": bool(candidate),
        "selection_score": score,
        "selection_reason": (
            "official announcement feed; update/content title signal; substantive body"
            if candidate
            else "retained announcement; did not meet candidate rule"
        ),
        "body_length": body_length,
        "body_present": bool(body.strip()),
        "body_truncated_suspected": bool(
            re.search(r"(?:\[truncated\]|\.\.\.$)", body.strip(), re.I)
        ),
        "linked_urls": extract_links(body),
    }


def unix_to_iso(value: Any) -> str | None:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(int(value), UTC).isoformat()
    except (OverflowError, OSError, TypeError, ValueError):
        return None


def utc_datetime(value: Any) -> datetime | None:
    iso = unix_to_iso(value)
    return datetime.fromisoformat(iso) if iso else None
