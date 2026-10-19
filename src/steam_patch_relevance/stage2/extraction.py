"""Conservative, provenance-preserving announcement and review extraction."""

from __future__ import annotations

import html
import json
import re
from collections import Counter
from typing import Any, Iterable

from steam_patch_relevance.stage2.ids import rv2_id
from steam_patch_relevance.stage2.markup import TextBlock, iter_blocks, split_bold_prefix

CLASSIFIER_VERSION = "stage2-rules-5"
CHANGE_EXTRACTOR_VERSION = "stage2-atomic-rules-9"
CLAIM_EXTRACTOR_VERSION = "stage2-claim-spans-6"

CATEGORIES = (
    "major_gameplay_or_balance_update",
    "specific_bug_fix",
    "performance_or_stability_change",
    "new_feature_or_content",
    "minor_cosmetic_or_localization_update",
    "developer_acknowledgement_or_future_plan",
    "promotional_or_non_patch_announcement",
    "other_announcement_unclassified",
)

GENERIC_CONTEXT = {
    "overview",
    "general",
    "gameplay",
    "balancing",
    "balance",
    "bug fixes",
    "bugs",
    "fixes",
    "performance",
    "stability",
    "primary weapons",
    "secondary weapons",
    "weapons",
    "stratagems",
    "armor",
    "armour",
    "misc",
    "miscellaneous",
    "sound",
    "graphics",
    "animation",
    "maps",
    "map",
    "ui",
    "settings",
    "improvements",
    "features",
    "patch highlights",
    "patch notes",
    "known issues",
    "community feedback",
    "general gameplay",
    "new content",
    "localization",
    "localisation",
    "cosmetics",
    "heroes",
    "hero",
    "items",
    "abilities",
    "crash fixes",
    "hangs",
    "soft-locks",
    "minor mix adjustments",
    "general fixes",
    "minor fixes",
    "miscellaneous fixes",
    "quality of life",
    "additional changes",
    "social menu fixes",
    "crash fixes, hangs and soft-locks",
}

TERM_STOPWORDS = {
    "if",
    "for",
    "as",
    "when",
    "where",
    "after",
    "before",
    "while",
    "then",
    "there",
    "your",
    "my",
    "you",
    "we",
    "they",
    "steam",
    "review",
    "players",
    "update",
    "developer",
    "passing",
    "example",
    "url",
    "http",
    "https",
    "id",
    "the",
    "it",
    "i",
    "a",
    "an",
    "and",
    "or",
    "but",
    "this",
    "that",
    "these",
    "those",
    "all",
    "also",
    "any",
    "no",
    "to",
    "in",
    "from",
    "of",
    "on",
    "with",
    "by",
    "can",
    "instead",
    "resolved",
    "starting",
    "changes",
    "enemies",
    "crashes",
    "based",
    "note",
    "however",
}

ACTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("fixed", re.compile(r"\b(?:fixed|fixes|corrected|resolved|addressed)\b", re.I)),
    (
        "added",
        re.compile(r"\b(?:added|adds|introduces?|introduced|implemented|now supports?)\b", re.I),
    ),
    ("removed", re.compile(r"\b(?:removed|removes|disabled|no longer)\b", re.I)),
    ("increased", re.compile(r"\b(?:increased|increases|raised|boosted|expanded|higher)\b", re.I)),
    (
        "decreased",
        re.compile(r"\b(?:decreased|decreases|reduced|lowers?|lowered|shortened|nerfed)\b", re.I),
    ),
    (
        "adjusted",
        re.compile(
            r"\b(?:adjusted|updated|changed|reworked|improved|optimized|optimised|tuned)\b", re.I
        ),
    ),
)

ASPECT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("gameplay", re.compile(r"\b(gameplay|combat|play style|playstyle)\b", re.I)),
    ("purchase_price_or_cost", re.compile(r"\b(price|cost|buy|purchase|economy)\b", re.I)),
    ("damage_or_attack_power", re.compile(r"\b(damage|attack power|dps|firepower)\b", re.I)),
    ("health_or_durability", re.compile(r"\b(health|hp|durability|armor|armour)\b", re.I)),
    ("speed_or_movement", re.compile(r"\b(speed|movement|mobility|stamina|jump|landing)\b", re.I)),
    ("range_or_radius", re.compile(r"\b(range|radius|reach|fall-off|falloff)\b", re.I)),
    (
        "cooldown_or_timing",
        re.compile(r"\b(cooldown|cool-down|reload time|latency|delay|timing)\b", re.I),
    ),
    ("accuracy_or_spread", re.compile(r"\b(accuracy|spread|recoil|inaccuracy|precision)\b", re.I)),
    (
        "capacity_or_ammunition",
        re.compile(r"\b(magazine|ammo|ammunition|capacity|number of uses|charges?)\b", re.I),
    ),
    ("armor_penetration", re.compile(r"\b(penetration|armor pen|armour pen)\b", re.I)),
    ("matchmaking_or_ranked", re.compile(r"\b(matchmaking|rank|ranked|skill group|queue)\b", re.I)),
    (
        "performance_or_network",
        re.compile(r"\b(performance|fps|crashes?|stutter|lag|ping|network|server|chance)\b", re.I),
    ),
    (
        "bug_or_functionality",
        re.compile(r"\b(issue|bug|incorrect|fail(?:ed|ure)?|broken|stuck|crash)\b", re.I),
    ),
    (
        "visuals_or_graphics",
        re.compile(r"\b(graphics|visual|texture|render|lighting|animation)\b", re.I),
    ),
    ("audio", re.compile(r"\b(audio|sound|volume|music|voice)\b", re.I)),
    ("map_or_level", re.compile(r"\b(map|level|arena|biome|planet)\b", re.I)),
    (
        "interface_or_settings",
        re.compile(r"\b(ui|menu|interface|settings|tooltip|hud|crosshair)\b", re.I),
    ),
    (
        "rewards_or_progression",
        re.compile(r"\b(reward|ticket|progression|unlock|experience|xp)\b", re.I),
    ),
    (
        "content_or_feature",
        re.compile(r"\b(feature|mode|mission|quest|content|expedition|campaign)\b", re.I),
    ),
    (
        "cosmetic_or_localization",
        re.compile(r"\b(cosmetic|skin|sticker|charm|translation|locali[sz]ation|text)\b", re.I),
    ),
)

TEMPORAL_CUES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "after_update",
        re.compile(r"\b(after|since)\s+(?:the\s+)?(?:update|patch|hotfix|nerf|buff)\b", re.I),
    ),
    ("still_or_remains", re.compile(r"\b(still|remains?|continues? to)\b", re.I)),
    (
        "before_update",
        re.compile(r"\b(before|prior to)\s+(?:the\s+)?(?:update|patch|hotfix)\b", re.I),
    ),
    ("recent_change", re.compile(r"\b(now|anymore|used to|recently)\b", re.I)),
)

NEGATION = re.compile(
    r"\b(not|never|no|isn't|wasn't|don't|doesn't|didn't|cannot|can't|without|hardly)\b", re.I
)
UNCERTAINTY = re.compile(
    r"\b(maybe|perhaps|possibly|probably|seems?|might|could|i think|not sure|apparently)\b", re.I
)
CLAUSE_CONNECTOR = re.compile(r"\s+(?:but|however|although|though|yet|whereas)\s+", re.I)
SENTENCE_END = re.compile(r"[.!?。！？]+(?:[\"’”)]*)?(?=\s|$)")
NUMBER = re.compile(
    r"(?<![A-Za-z])(?:\$|€|£)?\s*-?\d+(?:[.,]\d+)?\s*(?:%|ms|msec|sec(?:ond)?s?|s|fps|frames?|units?)?",
    re.I,
)
FROM_TO = re.compile(
    r"\bfrom\s+(\$?\s*-?\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)*\s*(?:%|ms|sec(?:ond)?s?|s|fps)?)\s+to\s+(\$?\s*-?\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)*\s*(?:%|ms|sec(?:ond)?s?|s|fps)?)",
    re.I,
)
DELTA = re.compile(r"\bby\s+(\$?\s*-?[\d.,]+\s*(?:%|ms|sec(?:ond)?s?|s|fps)?)", re.I)
BUG_SHAPE = re.compile(
    r"\b(?:fixed|corrected|resolved)\s+(?:an?\s+)?(?:issue|bug|case)(?:\s+where)?\s+(.+)", re.I
)
TRIGGER = re.compile(r"\b(?:when|while|after|if|during|under|where|upon)\b", re.I)
ACTION_SPLIT = re.compile(
    r";\s+|,\s+(?=(?:and\s+)?(?:added|removed|fixed|increased|reduced|decreased|adjusted|updated|introduced|improved)\b)"
    r"|\s+and\s+(?=(?:added|removed|fixed|increased|reduced|decreased|adjusted|updated|introduced|improved)\b)",
    re.I,
)
NAMED_ENTITY_AFTER_ACTION = re.compile(
    r"(?i:\b(?:added|introduced|removed|fixed|updated|changed|moved|increased|reduced|decreased|adjusted|improved|boosted|nerfed)\s+(?:(?:the|an?)\s+)?)([A-Z][A-Za-z0-9’'&-]*(?:\s+[A-Z][A-Za-z0-9’'&-]*){0,3})",
)
NAMED_ENTITY_AFTER_PREPOSITION = re.compile(
    r"\b(?:of|for|on|against|to)\s+(?:the\s+)?([A-Z][A-Za-z0-9’'&-]*(?:\s+[A-Z][A-Za-z0-9’'&-]*){0,2})"
)
CAPITALIZED_TERM = re.compile(
    r"\b[A-Z][A-Za-z0-9’'&-]*(?:\s+(?:[A-Z][A-Za-z0-9’'&-]*|of|the|and)){0,3}\b"
)

POSITIVE = re.compile(
    r"\b(good|great|love|loved|fun|enjoy|enjoyed|better|improved|excellent|smooth|responsive|balanced)\b",
    re.I,
)
NEGATIVE = re.compile(
    r"\b(bad|hate|hated|boring|worse|broken|crash(?:es|ed)?|lag(?:gy|s|ged)?|bug(?:gy|s)?|unbalanced|nerfed|awful|terrible|unplayable|frustrating)\b",
    re.I,
)
FEATURE_TERMS = re.compile(
    r"\b(matchmaking|server|network|lag|ping|weapon|gun|damage|balance|rank|map|graphics|visuals?|sound|audio|crash|bug|mission|content|price|cost|recoil|spread|aim|movement|fps|performance|stability|update|patch|feature|ui|menu|controller|input|progression|reward|ship|planet|hero|ability|item|stratagem|enemy|armor|armour|weapon|locali[sz]ation)\b",
    re.I,
)


def _visible_text(body: str) -> str:
    return " ".join(block.text for block in iter_blocks(body))


def classify_announcement(announcement: dict[str, Any]) -> dict[str, Any]:
    title = str(announcement.get("title") or "")
    body = str(announcement.get("body_original") or "")
    text = f"{title}\n{_visible_text(body)}"
    labels: list[str] = []
    evidence: dict[str, list[str]] = {}

    def add(label: str, pattern: re.Pattern[str]) -> None:
        matches = list(dict.fromkeys(m.group(0) for m in pattern.finditer(text)))
        if matches:
            labels.append(label)
            evidence[label] = matches[:5]

    add(
        "promotional_or_non_patch_announcement",
        re.compile(
            r"\b(sale|discount|giveaway|livestream|tournament|esports|anniversary|community event|weekend event)\b",
            re.I,
        ),
    )
    add(
        "developer_acknowledgement_or_future_plan",
        re.compile(
            r"\b(?:we(?:'re| are)\s+(?:aware|investigating|looking into|working on)|known issue|investigating (?:an? |the )?(?:issue|problem|bug)|plan to|intend to|will address|will fix|upcoming|coming soon|feedback has been|we hear you)\b",
            re.I,
        ),
    )
    add(
        "specific_bug_fix",
        re.compile(
            r"\b(fixed|fixes|corrected|resolved|bug fix|crash fix|addresses? an issue)\b", re.I
        ),
    )
    add(
        "performance_or_stability_change",
        re.compile(
            r"\b(performance|optimization|optimisation|stability|crash|frame rate|fps|latency|memory usage|server load)\b",
            re.I,
        ),
    )
    add(
        "major_gameplay_or_balance_update",
        re.compile(
            r"\b(balance|balancing|gameplay|nerf(?:ed)?|buff(?:ed)?|weapon tuning|combat tuning|major update|gameplay update)\b",
            re.I,
        ),
    )
    add(
        "minor_cosmetic_or_localization_update",
        re.compile(
            r"\b(locali[sz]ation|translation|typo|cosmetic|sticker|charm|skin|visual customization)\b",
            re.I,
        ),
    )
    add(
        "new_feature_or_content",
        re.compile(
            r"\b(added|introduc(?:e|ed)|new (?:feature|mode|mission|map|content|expedition|campaign|weapon|enemy|ship|system)|launch(?:es|ed)? today|available now)\b",
            re.I,
        ),
    )
    if not labels:
        labels.append("other_announcement_unclassified")
        evidence[labels[0]] = ["no implemented patch-change signal detected"]

    implementation_labels = {
        "specific_bug_fix",
        "performance_or_stability_change",
        "major_gameplay_or_balance_update",
        "minor_cosmetic_or_localization_update",
        "new_feature_or_content",
    }
    official_source = announcement.get("officialness") == "steam_community_announcement_feed"
    title_has_update_signal = bool(
        re.search(
            r"\b(patch|update|hotfix|release notes|gameplay|balance|version\s*[\d.]|introducing|introduces|new expedition|new campaign)\b",
            title,
            re.I,
        )
    )
    structured_change_signal = any(
        block.kind == "item" and _action_for(block.text) for block in iter_blocks(body)
    )
    is_patch = (
        official_source
        and bool(implementation_labels.intersection(labels))
        and (title_has_update_signal or structured_change_signal)
    )
    confidence = 0.82 if is_patch and len(implementation_labels.intersection(labels)) else 0.62
    linked_urls = list(
        dict.fromkeys(_json_list(announcement.get("linked_urls_json")) + _extract_body_links(body))
    )
    linked_patch_notes = any(
        re.search(r"(patch|update|notes|changelog|/patches?/)", url, re.I) for url in linked_urls
    )
    if is_patch and linked_patch_notes:
        full_notes_status = "announcement_body_and_linked_notes_unverified"
    elif is_patch and body.strip():
        full_notes_status = "announcement_body_only_completeness_unverified"
    elif linked_urls:
        full_notes_status = "linked_content_not_fetched"
    else:
        full_notes_status = "no_patch_notes_signal"
    return {
        "announcement_revision_id": announcement.get("announcement_revision_id"),
        "announcement_id": announcement.get("announcement_id"),
        "appid": announcement.get("appid"),
        "title": title,
        "body_original": body,
        "published_unix": announcement.get("published_unix"),
        "published_at_utc": announcement.get("published_at_utc"),
        "source_url": announcement.get("source_url"),
        "source_observation_id": announcement.get("source_observation_id"),
        "payload_sha256": announcement.get("payload_sha256"),
        "linked_urls_json": json.dumps(linked_urls, ensure_ascii=False),
        "linked_urls_extraction_method": "stage1_metadata_plus_stage2_bbcode_html_and_plain_url_scan",
        "officialness": announcement.get("officialness"),
        "feedname": announcement.get("feedname"),
        "feedlabel": announcement.get("feedlabel"),
        "author": announcement.get("author"),
        "is_external_url": announcement.get("is_external_url"),
        "post_type": announcement.get("post_type"),
        "significance": announcement.get("significance"),
        "announcement_language": announcement.get("announcement_language"),
        "body_length": announcement.get("body_length"),
        "body_present": announcement.get("body_present"),
        "body_truncated_suspected": announcement.get("body_truncated_suspected"),
        "categories": labels,
        "category_evidence_json": json.dumps(evidence, ensure_ascii=False, sort_keys=True),
        "classification_confidence": confidence,
        "classifier_version": CLASSIFIER_VERSION,
        "patch_eligible": is_patch,
        "patch_id": rv2_id("patch", announcement.get("announcement_revision_id"))
        if is_patch
        else None,
        "full_patch_notes_status": full_notes_status,
    }


def _json_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    try:
        result = json.loads(str(value))
        return [str(item) for item in result] if isinstance(result, list) else []
    except (TypeError, ValueError, json.JSONDecodeError):
        return []


def _extract_body_links(body: str) -> list[str]:
    patterns = [
        re.compile(r"\[(?:url|link)\s*=\s*['\"]?([^\]\s'\"]+)", re.I),
        re.compile(r"<a\b[^>]*\bhref\s*=\s*['\"]([^'\"]+)['\"]", re.I),
        re.compile(r"https?://[^\s\]<>\"']+", re.I),
    ]
    urls = []
    for pattern in patterns:
        for match in pattern.finditer(body):
            url = match.group(1) if match.lastindex else match.group(0)
            url = html.unescape(url).rstrip(".,;)")
            if url.startswith(("https://", "http://")):
                urls.append(url)
    return list(dict.fromkeys(urls))


def _is_heading(block: TextBlock, next_block: TextBlock | None) -> bool:
    value = block.text.strip().rstrip(":")
    if block.kind == "heading" or block.forced_heading or block.bold_only:
        return True
    if re.fullmatch(r"\[\s*[A-Z0-9][A-Z0-9 /&'’_-]{1,80}\s*\]", value):
        return True
    if (
        len(value) <= 55
        and len(value.split()) <= 7
        and value.isupper()
        and not re.search(r"[.!?]", value)
        and not _action_for(value)
    ):
        return True
    if (
        next_block
        and next_block.depth > block.depth
        and len(value) <= 100
        and len(value.split()) <= 10
        and not _action_for(value)
    ):
        return True
    if len(value) <= 50 and len(value.split()) <= 5 and not _action_for(value):
        if re.search(r"[.!?]", value) is None and next_block and next_block.kind == "item":
            return True
    return False


def _action_for(text: str) -> str | None:
    if re.search(
        r"\b(?:we(?:'re| are)\s+(?:aware|investigating|looking into|working on)|known issue|investigating (?:an? |the )?(?:issue|problem|bug)|will address|will fix|plan to|intend to|considering)\b",
        text,
        re.I,
    ):
        return "acknowledged"
    for action, pattern in ACTION_PATTERNS:
        if pattern.search(text):
            return action
    if re.search(r"\b(?:requires?|takes?)\s+(?:fewer|less)\b", text, re.I):
        return "decreased"
    if re.search(r"\b(?:requires?|takes?)\s+(?:more|additional)\b", text, re.I):
        return "increased"
    if re.search(
        r"\b(?:now|no longer)\s+(?:allows?|requires?|shows?|displays?|applies?|uses?|affects?)\b",
        text,
        re.I,
    ):
        return "modified"
    return None


def _clean_context(value: str) -> bool:
    clean = value.strip()
    return (
        bool(clean)
        and len(clean) <= 80
        and len(clean.split()) <= 10
        and clean.casefold().strip(":[] ") not in GENERIC_CONTEXT
    )


def _source_span(block: TextBlock, start: int, end: int) -> tuple[int, int]:
    local = block.char_sources[start:end]
    if local:
        return min(span[0] for span in local), max(span[1] for span in local)
    return block.source_start, block.source_end


def _split_action_text(text: str) -> list[tuple[int, int, str]]:
    pieces = []
    cursor = 0
    for match in ACTION_SPLIT.finditer(text):
        if match.start() > cursor:
            pieces.append((cursor, match.start(), text[cursor : match.start()].strip()))
        cursor = match.end()
    if cursor < len(text):
        pieces.append((cursor, len(text), text[cursor:].strip()))
    return [(a, b, value) for a, b, value in pieces if value]


def _aspect(text: str) -> str | None:
    for name, pattern in ASPECT_PATTERNS:
        if pattern.search(text):
            return name
    return None


def _entity(text: str, context: list[str]) -> tuple[str | None, list[str]]:
    candidates = [
        value
        for value in context
        if _clean_context(value)
        and len(value.split()) <= 2
        and value.casefold() not in GENERIC_CONTEXT
        and value.casefold().split()[0] not in TERM_STOPWORDS
    ]
    action_match = NAMED_ENTITY_AFTER_ACTION.search(text)
    prep_match = NAMED_ENTITY_AFTER_PREPOSITION.search(text)
    explicit = action_match.group(1).strip(" .,;:") if action_match else None
    if explicit and explicit.casefold() not in GENERIC_CONTEXT:
        # Avoid capturing sentence-initial common pronouns and change verbs.
        if (
            explicit.split()[0].casefold()
            not in {"the", "a", "an", "all", "players", "game", "issue", "various", "some"}
            and _aspect(explicit) is None
        ):
            return explicit, [explicit]
    stop_terms = {
        "fixed",
        "added",
        "removed",
        "updated",
        "changed",
        "increased",
        "reduced",
        "decreased",
        "adjusted",
        "improved",
        "various",
        "some",
        "the",
        "players",
        "game",
        "issue",
        "bug",
        "case",
        "we",
        "this",
        "those",
        "general",
        *TERM_STOPWORDS,
    }
    named_terms = []
    for match in CAPITALIZED_TERM.finditer(text):
        explicit_term = match.group().strip(" .,;:")
        first_word = explicit_term.split()[0].casefold()
        if (
            first_word not in stop_terms
            and explicit_term.casefold() not in GENERIC_CONTEXT
            and _aspect(explicit_term) is None
            and explicit_term.casefold() not in {item.casefold() for item in named_terms}
        ):
            named_terms.append(explicit_term)
    if len(named_terms) == 1:
        return named_terms[0], named_terms
    if len(named_terms) > 1:
        return None, named_terms
    if candidates:
        return candidates[-1], [candidates[-1]]
    if prep_match:
        value = prep_match.group(1).strip(" .,;:")
        if value.casefold() not in GENERIC_CONTEXT:
            return value, [value]
    return None, []


def _status(text: str) -> str:
    low = text.casefold()
    if re.search(
        r"\b(?:believe|think|may have|might have|possibly)\b.{0,40}\b(?:fixed|resolved|corrected)\b",
        low,
    ):
        return "claimed_fix_with_uncertainty"
    if re.search(
        r"\b(?:we(?:'re| are)\s+(?:aware|investigating|looking into|working on)|known issue|investigating (?:an? |the )?(?:issue|problem|bug)|will address|will fix|plan to|intend to)\b",
        low,
    ):
        return "acknowledged_or_planned"
    if re.search(r"\b(fixed|corrected|resolved)\b", low):
        return "implemented_bug_fix"
    if _action_for(text):
        return "implemented_change"
    return "unclear"


def _direction(text: str, action: str | None) -> str | None:
    if action in {"increased", "decreased"}:
        return action
    if action == "added":
        return "added"
    if action == "removed":
        return "removed"
    if action == "fixed":
        return "corrected"
    if action == "adjusted":
        return "modified"
    return None


def _number_fields(
    text: str, direction: str | None
) -> tuple[str | None, str | None, float | None, str | None]:
    match = FROM_TO.search(text)
    if match:
        previous, new = match.group(1).strip(), match.group(2).strip()
        return previous, new, None, None
    values = list(NUMBER.finditer(text))
    if len(values) >= 2 and re.search(r"\bfrom\b", text, re.I) and re.search(r"\bto\b", text, re.I):
        return values[0].group().strip(), values[1].group().strip(), None, None
    delta = DELTA.search(text)
    if delta:
        raw = delta.group(1).strip()
        numeric = _parse_numeric(raw)
        if numeric is not None and direction == "decreased":
            numeric = -abs(numeric)
        elif numeric is not None and direction == "increased":
            numeric = abs(numeric)
        unit = "currency" if "$" in raw or "€" in raw or "£" in raw else None
        return None, None, numeric, unit
    return None, None, None, None


def _parse_numeric(value: str) -> float | None:
    cleaned = re.sub(r"[^\d,.-]", "", value)
    if not cleaned:
        return None
    if "," in cleaned and "." not in cleaned:
        cleaned = cleaned.replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _bug_details(text: str) -> tuple[str | None, str | None]:
    match = BUG_SHAPE.search(text)
    if not match:
        return None, None
    detail = match.group(1).strip(" .;:")
    trigger = TRIGGER.search(detail)
    if trigger:
        return detail[: trigger.start()].strip(" ,;"), detail[trigger.start() :].strip(" .;,")
    return detail, None


def extract_patch_changes(
    announcements: Iterable[dict[str, Any]],
    classifications: dict[str, dict[str, Any]],
    game_names: dict[int, str],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for announcement in announcements:
        revision_id = announcement.get("announcement_revision_id")
        classification = classifications.get(str(revision_id))
        if not classification or not classification["patch_eligible"]:
            continue
        body = str(announcement.get("body_original") or "")
        if not body:
            continue
        raw_blocks = list(iter_blocks(body))
        blocks = [part for block in raw_blocks for part in split_bold_prefix(block)]
        headings: list[tuple[int, str]] = []
        contexts: list[tuple[int, str]] = []
        for index, block in enumerate(blocks):
            next_block = blocks[index + 1] if index + 1 < len(blocks) else None
            heading = _is_heading(block, next_block)
            if heading:
                value = block.text.strip().strip("[] ").rstrip(":")
                if not value:
                    continue
                explicit_heading = (
                    block.kind == "heading"
                    or block.forced_heading
                    or block.bold_only
                    or bool(re.fullmatch(r"\[\s*[A-Z0-9][A-Z0-9 /&'’_-]{1,80}\s*\]", value))
                )
                if explicit_heading:
                    headings = [(d, v) for d, v in headings if d < block.depth]
                    contexts = [(d, v) for d, v in contexts if d < block.depth]
                    headings.append((block.depth, value))
                else:
                    # Plain labels such as a weapon name before a nested list are
                    # hierarchy context, not replacements for the section heading.
                    contexts = [(d, v) for d, v in contexts if d < block.depth]
                    contexts.append((block.depth, value))
                continue

            has_children = bool(next_block and next_block.depth > block.depth)
            action = _action_for(block.text)
            if has_children and (block.kind == "item" or block.kind == "paragraph"):
                # Parent labels such as hero, weapon, or feature names are context.
                value = block.text.strip().rstrip(":")
                if value and (action is None or value.endswith(":")):
                    contexts = [(d, v) for d, v in contexts if d < block.depth]
                    if _clean_context(value):
                        contexts.append((block.depth, value))
                    continue
                if action and value.endswith(":"):
                    contexts = [(d, v) for d, v in contexts if d < block.depth]
                    contexts.append((block.depth, value[:-1]))
                    continue

            if block.kind != "item":
                # Ambiguous narrative prose is left for the optional extraction
                # provider rather than emitted as a deterministic change.
                continue
            spans = [(0, len(block.text))]
            context = [v for _, v in sorted(headings + contexts, key=lambda item: item[0])]
            for local_start, local_end in spans:
                sentence = block.text[local_start:local_end].strip()
                if not sentence:
                    continue
                clauses = _split_action_text(sentence)
                if not clauses:
                    clauses = [(0, len(sentence), sentence)]
                for clause_start, clause_end, clause in clauses:
                    action = _action_for(clause)
                    status = _status(clause)
                    if action is None:
                        continue
                    # Do not retain broad summaries when a nested list contains the
                    # granular changes. Keep them as hierarchy context above.
                    offset_start = local_start + clause_start
                    offset_end = local_start + clause_end
                    while offset_start < offset_end and block.text[offset_start].isspace():
                        offset_start += 1
                    while offset_end > offset_start and block.text[offset_end - 1].isspace():
                        offset_end -= 1
                    raw_start, raw_end = _source_span(block, offset_start, offset_end)
                    rendered = clause.strip()
                    source_bounds_valid = 0 <= raw_start < raw_end <= len(body)
                    exact_raw = body[raw_start:raw_end] if source_bounds_valid else None
                    aspect = _aspect(rendered)
                    if aspect is None and status == "implemented_bug_fix":
                        aspect = "bug_or_functionality"
                    entity, entity_candidates = _entity(rendered, context)
                    direction = _direction(rendered, action)
                    previous, new, delta, unit = _number_fields(rendered, direction)
                    bug_symptom, bug_trigger = _bug_details(rendered)
                    heading_path = [
                        v for _, v in sorted(headings + contexts, key=lambda item: item[0])
                    ]
                    source_verified = (
                        raw_start >= 0
                        and raw_end <= len(body)
                        and bool(exact_raw)
                        and body[raw_start:raw_end] == exact_raw
                    )
                    quality_flags = []
                    if not entity:
                        quality_flags.append("entity_unresolved")
                    if not entity and len(entity_candidates) > 1:
                        quality_flags.append("entity_ambiguous")
                    if status == "unclear":
                        quality_flags.append("developer_status_unclear")
                    if status == "claimed_fix_with_uncertainty":
                        quality_flags.append("developer_fix_qualified")
                    if aspect is None:
                        quality_flags.append("aspect_unresolved")
                    if not source_verified:
                        quality_flags.append("source_span_invalid")
                    if re.search(
                        r"\b(?:a number of|several|multiple|various)\s+(?:issues|bugs|problems|fixes)\b",
                        rendered,
                        re.I,
                    ):
                        quality_flags.append("broad_change_summary")
                    if re.search(r"\b(?:issues?|bugs?|cases?)\s+with\b.+\bwhere\b", rendered, re.I):
                        quality_flags.append("bug_trigger_symptom_ambiguous")
                    output.append(
                        {
                            "change_id": rv2_id(
                                "change", revision_id, raw_start, raw_end, rendered
                            ),
                            "patch_id": classification["patch_id"],
                            "announcement_id": announcement.get("announcement_id"),
                            "announcement_revision_id": revision_id,
                            "game_id": announcement.get("appid"),
                            "game_name": game_names.get(int(announcement.get("appid") or 0)),
                            "title": announcement.get("title"),
                            "published_at_utc": announcement.get("published_at_utc"),
                            "source_url": announcement.get("source_url"),
                            "payload_sha256": announcement.get("payload_sha256"),
                            "source_span_start": raw_start,
                            "source_span_end": raw_end,
                            "source_span_raw": exact_raw,
                            "change_text": rendered,
                            "heading_path": heading_path,
                            "entity": entity,
                            "entity_candidates": entity_candidates,
                            "aspect": aspect,
                            "action": action,
                            "direction": direction,
                            "previous_value": previous,
                            "new_value": new,
                            "numeric_delta": delta,
                            "numeric_unit": unit,
                            "developer_status": status,
                            "bug_symptom": bug_symptom,
                            "bug_trigger": bug_trigger,
                            "extraction_confidence": (
                                0.90
                                if entity
                                and aspect
                                and status != "claimed_fix_with_uncertainty"
                                and source_verified
                                else 0.68
                                if status == "claimed_fix_with_uncertainty" and source_verified
                                else 0.50
                                if len(entity_candidates) > 1 and source_verified
                                else (0.62 if source_verified else 0.0)
                            ),
                            "extraction_method": "deterministic_rule_extraction",
                            "extraction_version": CHANGE_EXTRACTOR_VERSION,
                            "source_span_verified": source_verified,
                            "quality_flags": quality_flags,
                        }
                    )
    return output


def _sentence_spans(text: str) -> list[tuple[int, int]]:
    spans = []
    cursor = 0
    for match in SENTENCE_END.finditer(text):
        end = match.end()
        if text[cursor:end].strip():
            spans.append((cursor, end))
        cursor = end
    if cursor < len(text) and text[cursor:].strip():
        spans.append((cursor, len(text)))
    return spans or ([(0, len(text))] if text.strip() else [])


def _review_claim_spans(text: str) -> list[tuple[int, int]]:
    clauses: list[tuple[int, int]] = []
    for start, end in _sentence_spans(text):
        segment = text[start:end]
        cursor = 0
        for match in CLAUSE_CONNECTOR.finditer(segment):
            left_end = match.start()
            right_start = match.end()
            if segment[cursor:left_end].strip():
                clauses.append((start + cursor, start + left_end))
            cursor = right_start
        if segment[cursor:].strip():
            clauses.append((start + cursor, end))
    result = []
    for start, end in clauses:
        while start < end and text[start].isspace():
            start += 1
        while end > start and text[end - 1].isspace():
            end -= 1
        words = re.findall(r"[^\W_]+", text[start:end], re.UNICODE)
        if words and (len(words) >= 2 or words[0].casefold() not in {"i", "it", "yes", "no"}):
            result.append((start, end))
    return result


def extract_review_claims(
    reviews: Iterable[dict[str, Any]],
    game_names: dict[int, str],
    terminology: dict[int, list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    terms_by_game: dict[int, list[tuple[str, bool]]] = {}
    spellings_by_game: dict[int, dict[str, str]] = {}
    for appid, terms in (terminology or {}).items():
        spellings: dict[str, str] = {}
        term_patterns: list[tuple[str, bool]] = []
        for term in terms:
            if not term.get("is_entity_matchable"):
                continue
            canonical = str(term["term"])
            aliases = {canonical, *(str(alias) for alias in term.get("aliases", []))}
            for alias in aliases:
                # Multiword names and identifiers are often lowercased by reviewers;
                # a lone ordinary-looking proper noun must retain case to avoid
                # turning words such as "back" into a feature mention.
                case_insensitive = (
                    len(alias.split()) > 1 or bool(re.search(r"[0-9_-]", alias)) or alias.isupper()
                )
                pattern_alias = alias if case_insensitive else canonical
                spellings[pattern_alias.casefold()] = canonical
                term_patterns.append((pattern_alias, case_insensitive))
        spellings_by_game[appid] = spellings
        terms_by_game[appid] = term_patterns
    output: list[dict[str, Any]] = []
    compiled_patterns: dict[int, re.Pattern[str] | None] = {}
    term_spellings: dict[int, dict[str, str]] = {}
    for appid, aliases in terms_by_game.items():
        unique = sorted(set(aliases), key=lambda item: (-len(item[0]), item[0].casefold()))
        term_spellings[appid] = spellings_by_game.get(appid, {})
        alternatives = [
            f"(?i:{re.escape(alias)})" if insensitive else re.escape(alias)
            for alias, insensitive in unique
        ]
        compiled_patterns[appid] = (
            re.compile(r"(?<!\w)(" + "|".join(alternatives) + r")(?!\w)", re.UNICODE)
            if unique
            else None
        )
    for review in reviews:
        text = str(review.get("review_text_original") or "")
        if not text.strip():
            continue
        appid = int(review.get("appid") or 0)
        for start, end in _review_claim_spans(text):
            claim = text[start:end]
            aspect = _review_aspect(claim)
            term_pattern = compiled_patterns.get(appid)
            entity_match = term_pattern.search(claim) if term_pattern else None
            entity = (
                term_spellings.get(appid, {}).get(entity_match.group(1).casefold())
                if entity_match
                else None
            )
            opinion_terms = list(
                dict.fromkeys(
                    [m.group(0).casefold() for m in POSITIVE.finditer(claim)]
                    + [m.group(0).casefold() for m in NEGATIVE.finditer(claim)]
                )
            )
            has_feature = (
                entity is not None or aspect is not None or bool(FEATURE_TERMS.search(claim))
            )
            polarity = _polarity(claim, has_feature)
            confidence = (
                0.83 if entity and aspect and polarity else (0.68 if aspect or entity else 0.48)
            )
            if len(claim.strip()) < 12 or len(claim.split()) < 3:
                confidence = min(confidence, 0.42)
            temporal_cues = [name for name, pattern in TEMPORAL_CUES if pattern.search(claim)]
            if (
                re.search(r"\b(now|broken|nerfed|unbalanced)\b", claim, re.I)
                and "after_update" not in temporal_cues
            ):
                temporal_cues.append("not_patch_specific_by_word_alone")
            output.append(
                {
                    "claim_id": rv2_id(
                        "claim", review.get("review_revision_id"), start, end, claim
                    ),
                    "review_revision_id": review.get("review_revision_id"),
                    "logical_revision_key": review.get("logical_revision_key"),
                    "review_id": review.get("recommendation_id"),
                    "source_payload_sha256": review.get("source_payload_sha256"),
                    "game_id": appid,
                    "game_name": game_names.get(appid),
                    "review_created_at_utc": review.get("created_at_utc"),
                    "review_updated_at_utc": review.get("updated_at_utc"),
                    "review_language": review.get("language"),
                    "language_metadata_status": review.get("language_metadata_status"),
                    "detected_language": review.get("detected_language"),
                    "detected_language_confidence": review.get("detected_language_confidence"),
                    "claim_span_start": start,
                    "claim_span_end": end,
                    "claim_text_original": claim,
                    "referenced_entity": entity,
                    "aspect": aspect,
                    "opinion_or_issue": claim,
                    "opinion_terms": opinion_terms,
                    "polarity": polarity,
                    "temporal_cues": temporal_cues,
                    "negated": bool(NEGATION.search(claim)),
                    "uncertain": bool(UNCERTAINTY.search(claim)),
                    "extraction_confidence": confidence,
                    "extraction_method": "sentence_and_contrast_clause_rules",
                    "extraction_version": CLAIM_EXTRACTOR_VERSION,
                    "patch_specificity": "not_assigned",
                }
            )
    return output


def _review_aspect(text: str) -> str | None:
    low = text.casefold()
    for aspect, pattern in ASPECT_PATTERNS:
        if pattern.search(text):
            return aspect
    # Low-cost broad-language aspect cues. These identify a topic only and do not
    # score feature sentiment or imply any patch relationship.
    multilingual = (
        (
            "performance_or_network",
            r"\b(lag|laggy|ping|crash|crashes|fps|lento|lent|ralent|ruckel|краш|лагает|лаг)\b",
        ),
        (
            "matchmaking_or_ranked",
            r"\b(matchmaking|matchmaking|emparejam|matchmaking|matchmaking|подбор)\b",
        ),
        ("purchase_price_or_cost", r"\b(precio|prix|preis|preço|цена|costo|coste)\b"),
        ("gameplay", r"\b(игр|juego|jeu|spiel|jogar|gameplay)\b"),
    )
    for aspect, pattern in multilingual:
        if re.search(pattern, low):
            return aspect
    return None


def _polarity(text: str, has_feature: bool) -> str | None:
    positive_matches = list(POSITIVE.finditer(text))
    negative_matches = list(NEGATIVE.finditer(text))
    if positive_matches and negative_matches:
        return "mixed"
    if not has_feature:
        return None
    match = (positive_matches or negative_matches or [None])[0]
    if match is None:
        return None
    prefix = text[: match.start()]
    negated_here = bool(
        re.search(
            r"\b(?:not|never|no|isn't|wasn't|don't|doesn't|didn't|cannot|can't|without)\b(?:\W+\w+){0,2}\W*$",
            prefix,
            re.I,
        )
    )
    if positive_matches:
        return "negative" if negated_here else "positive"
    return "positive" if negated_here else "negative"


def _find_term(text: str, terms: list[str]) -> str | None:
    folded = text.casefold()
    for term in terms:
        if not term or len(term) < 2:
            continue
        needle = term.casefold()
        if re.search(r"(?<!\w)" + re.escape(needle) + r"(?!\w)", folded, re.UNICODE):
            return term
    return None


def build_terminology(
    announcements: Iterable[dict[str, Any]],
    changes: Iterable[dict[str, Any]],
    reviews: Iterable[dict[str, Any]],
    game_names: dict[int, str],
    *,
    max_terms_per_game: int = 500,
) -> tuple[list[dict[str, Any]], dict[int, list[dict[str, Any]]]]:
    """Build small per-game terms from patch entities/headings and repeated review names."""
    evidence: dict[int, dict[str, Counter[str]]] = {}

    def record(appid: int, term: str, source: str) -> None:
        term = re.sub(r"\s+", " ", term).strip(" .,;:[]()\t\n")
        key = term.casefold()
        if (
            len(term) < 2
            or len(term) > 60
            or key in GENERIC_CONTEXT
            or key.split()[0] in TERM_STOPWORDS
            or not re.search(r"[A-Za-z0-9]", term)
        ):
            return
        evidence.setdefault(appid, {}).setdefault(key, Counter())[source] += 1

    for change in changes:
        appid = int(change.get("game_id") or 0)
        if change.get("entity"):
            record(appid, str(change["entity"]), "extracted_change_entity")
        for heading in change.get("heading_path") or []:
            if _clean_context(str(heading)):
                record(appid, str(heading), "patch_note_hierarchy")
        for value in (change.get("change_text") or "",):
            for match in re.finditer(
                r"\b[A-Z0-9][A-Za-z0-9’'&-]*(?:\s+[A-Z0-9][A-Za-z0-9’'&-]*){0,2}\b", value
            ):
                record(appid, match.group(), "patch_note_name")
    for announcement in announcements:
        appid = int(announcement.get("appid") or 0)
        for block in iter_blocks(str(announcement.get("body_original") or "")):
            if block.bold_only or _is_heading(block, None):
                if _clean_context(block.text):
                    record(appid, block.text, "patch_note_hierarchy")

    # Reviews contribute only repeated proper-name-like strings, never the review text
    # itself. This avoids turning a cross-game universal ontology into a dependency.
    review_counts: dict[int, Counter[str]] = {}
    for review in reviews:
        appid = int(review.get("appid") or 0)
        text = str(review.get("review_text_original") or "")
        per_review: set[str] = set()
        review_candidates = 0
        counter = review_counts.setdefault(appid, Counter())
        for match in CAPITALIZED_TERM.finditer(text):
            term = match.group().strip()
            folded = term.casefold()
            first_word = folded.split()[0]
            if (
                folded in GENERIC_CONTEXT
                or first_word in TERM_STOPWORDS
                or first_word
                in {
                    "i",
                    "the",
                    "this",
                    "that",
                    "after",
                    "before",
                    "while",
                    "when",
                    "a",
                    "an",
                    "am",
                    "you",
                    "we",
                    "he",
                    "she",
                    "it",
                    "con",
                    "game",
                    "players",
                    "steam",
                    "review",
                    "great",
                    "good",
                    "bad",
                    "love",
                    "update",
                    "very",
                    "some",
                    "new",
                    "no",
                    "yes",
                    "not",
                    "valve",
                    "developer",
                }
                or len(term.split()) == 1
                and not re.search(r"\d|[-_]", term)
                and term.islower()
            ):
                continue
            if len(counter) >= 20_000 and folded not in counter:
                continue
            per_review.add(term)
            review_candidates += 1
            if review_candidates >= 50:
                break
        counter.update(per_review)
    terminology: list[dict[str, Any]] = []
    lookup: dict[int, list[dict[str, Any]]] = {}
    for appid, counts in review_counts.items():
        for term, count in counts.most_common(1500):
            if count >= 4:
                record(appid, term, "repeated_review_name_candidate")
    for appid, terms in evidence.items():
        selected = []
        ranked = sorted(
            terms.items(),
            key=lambda item: (
                0 if "extracted_change_entity" in item[1] else 1,
                -sum(item[1].values()),
                item[0],
            ),
        )[:max_terms_per_game]
        for folded, source_counts in ranked:
            source_name = max(source_counts, key=source_counts.get)
            # Preserve an observed spelling, which may carry game capitalization.
            spelling = folded
            for change in changes:
                if int(change.get("game_id") or 0) == appid:
                    for candidate in [change.get("entity"), *(change.get("heading_path") or [])]:
                        if candidate and str(candidate).casefold() == folded:
                            spelling = str(candidate)
                            break
            record_obj = {
                "term_id": rv2_id("term", appid, folded),
                "game_id": appid,
                "game_name": game_names.get(appid),
                "term": spelling,
                "normalized_term": folded,
                "aliases": sorted({folded, re.sub(r"[-_]+", " ", folded)}),
                "evidence_sources": sorted(source_counts),
                "evidence_count": int(sum(source_counts.values())),
                "primary_evidence_source": source_name,
                "is_game_specific": True,
                "is_entity_matchable": (
                    bool(
                        {
                            "extracted_change_entity",
                            "patch_note_hierarchy",
                            "patch_note_name",
                        }.intersection(source_counts)
                    )
                    and folded != str(game_names.get(appid, "")).casefold()
                    and folded not in GENERIC_CONTEXT
                    and folded.split()[0] not in TERM_STOPWORDS
                ),
                "resource_version": "stage2-vocab-2",
            }
            terminology.append(record_obj)
            selected.append(record_obj)
        lookup[appid] = sorted(
            selected, key=lambda row: (-len(row["term"]), row["normalized_term"])
        )
    return terminology, lookup
