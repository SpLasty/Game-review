"""Evidence-backed post classification; no automatic claim of fix effectiveness."""

import json
import re

from steam_insights.pipeline.documents import ACTION
from steam_insights.pipeline.storage import parse_time, stable_id

PATCH_TITLE = re.compile(r"\b(?:patch(?:\s+notes)?|hotfix|release\s+notes)\b", re.I)


def classify_post(title: str, canonical: str) -> str:
    if PATCH_TITLE.search(title):
        return "patch_notes"
    if re.search(r"\b(?:sale|discount|free weekend|giveaway|merch)\b", title, re.I):
        return "promotion"
    if re.search(r"\b(?:known issues?|roadmap|devlog|development update)\b", title, re.I):
        return "development"
    if re.search(r"\b(?:update|released|stable|unstable)\b", title, re.I) and (
        re.search(r"\b\d+\.\d+", title) or len(ACTION.findall(canonical)) >= 2
    ):
        return "update"
    if re.search(r"\b(?:event|livestream|tournament|anniversary)\b", title, re.I):
        return "event"
    return "unknown"


def load_registry(path) -> dict[str, dict]:
    if not path.exists():
        return {}
    result = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        required = {"announcement_revision_id", "decision", "actor_type", "checked_by", "checked_at", "evidence_field", "evidence_text"}
        if required - row.keys():
            raise ValueError(f"Patch registry line {number}: missing {sorted(required - row.keys())}")
        if row["decision"] not in {"confirm_patch", "non_patch", "uncertain"} or row["actor_type"] not in {"human", "source_review"}:
            raise ValueError(f"Patch registry line {number}: invalid decision/actor type")
        parse_time(row["checked_at"])
        key = row["announcement_revision_id"]
        if key in result and result[key] != row:
            raise ValueError(f"Patch registry has unresolved conflicting decisions: {key}")
        result[key] = row
    return result


def verify_document(document: dict, blocks: list[dict], source_kind: str, event_type, registry: dict) -> list[dict]:
    evidence = []
    def add(field, method, value, quote, checker="pipeline_rules_v1", checked_at=None):
        text = document["title"] if field == "title" else document["canonical_text"]
        start = text.find(quote)
        if not quote or start < 0:
            raise ValueError("Verification evidence is not an exact source substring")
        evidence.append({"evidence_id": stable_id(document["announcement_revision_id"], field, method, value, start, quote),
                         "announcement_revision_id": document["announcement_revision_id"],
                         "source_record_id": document["source_record_id"], "field": field,
                         "method": method, "value": value, "evidence_text": quote,
                         "char_start": start, "char_end": start + len(quote),
                         "source_url": document["source_url"], "checked_by": checker,
                         "checked_at": parse_time(checked_at)})
    document["post_type"] = classify_post(document["title"], document["canonical_text"])
    document["verification_status"] = "legacy_manual_assertion" if document["legacy_manual_flag"] else "heuristic_unverified"
    primary = source_kind in {"collector_json", "public_api_snapshot"} and document["feed"] == "steam_community_announcements"
    structural_items = sum(b["block_type"] in {"list_item", "table_row"} for b in blocks)
    body_action = ACTION.search(document["canonical_text"])
    explicit_patch = bool(PATCH_TITLE.search(document["title"])) and bool(body_action or structural_items >= 2)
    explicit_update = document["post_type"] == "update" and document["version_hint"] and structural_items >= 2 and len(ACTION.findall(document["canonical_text"])) >= 2
    category = str(event_type or "").lower() in {"patch_notes", "small_update", "regular_update", "major_update"}
    if primary and document["canonical_text"] and (explicit_patch or explicit_update or (category and body_action)):
        document["verification_status"] = "source_confirmed_patch_post"
        add("title", "official_feed_explicit_patch_or_update", "patch_post", document["title"])
        if body_action:
            begin, end = body_action.span()
            add("canonical_text", "change_language", "patch_content", document["canonical_text"][max(0, begin - 40):min(len(document["canonical_text"]), end + 100)])
    release_claim = re.search(r"\b(?:released|available now|out now|is now live|has been deployed)\b", document["title"] + "\n" + document["canonical_text"], re.I)
    document["release_status_hint"] = "released_claim" if release_claim else "unknown"
    if re.search(r"\b(?:will be released|scheduled for|upcoming|planned for)\b", document["title"], re.I):
        document["release_status_hint"] = "planned"
    # Only explicit, timezone-qualified timestamps are candidates for actual release time.
    released = re.search(r"\breleased\s+(?:on\s+)?(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?\s*(?:UTC|Z))", document["canonical_text"], re.I)
    if released:
        raw = released.group(1).strip().replace(" UTC", "+00:00").replace(" utc", "+00:00")
        document["release_utc"] = parse_time(raw)
        document["release_time_basis"] = "explicit_release_statement"
        add("canonical_text", "explicit_release_timestamp", document["release_utc"].isoformat(), released.group(0))
    decision = registry.get(document["announcement_revision_id"])
    if decision:
        field = decision["evidence_field"]
        if field not in {"title", "canonical_text"}:
            raise ValueError("Patch evidence_field must be title or canonical_text")
        add(field, decision["actor_type"], decision["decision"], decision["evidence_text"], decision["checked_by"], decision["checked_at"])
        if decision["decision"] == "confirm_patch":
            document["verification_status"] = "human_verified_patch_post" if decision["actor_type"] == "human" else "source_reviewed_patch_post"
            document["post_type"] = "patch_notes"
        elif decision["decision"] == "non_patch":
            document["verification_status"] = "reviewed_non_patch"
            document["post_type"] = "non_patch"
        else:
            document["verification_status"] = "reviewed_uncertain"
        if decision.get("release_utc"):
            quote = decision.get("release_evidence_text", "")
            add("canonical_text", "reviewed_release_time", decision["release_utc"], quote, decision["checked_by"], decision["checked_at"])
            document["release_utc"] = parse_time(decision["release_utc"])
            document["release_time_basis"] = "reviewed_release_statement"
    return evidence
