"""Announcement revisions, source blocks, change candidates, and patch registry."""

import re
from collections import Counter
from datetime import datetime, timezone

from steam_insights.pipeline.documents import branch_hint, extract_changes, parse_document, platform_hints
from steam_insights.pipeline.storage import explicit_bool, parse_time, stable_id
from steam_insights.pipeline.verification import load_registry, verify_document


def prepare_announcement_observations(observations: list[dict], config) -> dict:
    registry = load_registry(config.input("patch_verification"))
    legacy = {(str(r.get("appid")), str(r.get("gid"))) for r in observations
              if r.get("verification_status") == "manually_verified_patch"}
    revisions, revision_blocks, revision_evidence, sources, quarantine = {}, {}, {}, [], []
    candidates = set()
    for row in observations:
        source = dict(row["_source"])
        entity = f"{row.get('appid', '')}:{row.get('gid', '')}"
        try:
            appid = int(row["appid"])
            post_id = str(row["gid"]).strip()
            if not 0 < appid <= 2**32 - 1 or not re.fullmatch(r"[1-9]\d*", post_id):
                raise ValueError("invalid announcement source ID")
            if not str(row.get("game", "")).strip():
                raise ValueError("missing game")
            publication = parse_time(int(row["timestamp"]))
            if int(row["timestamp"]) < 0:
                raise ValueError("negative announcement timestamp")
            if row.get("date_utc") and parse_time(row["date_utc"]) != publication:
                raise ValueError("announcement ISO/epoch disagreement")
            observed = parse_time(row.get("observed_at"))
            original = str(row["contents"] if row.get("contents") is not None else row.get("text", ""))
            title = str(row.get("title", "")).strip()
            canonical, blocks, kind, structured = parse_document(original, flattened=source["source_kind"] == "csv_export")
        except (ValueError, TypeError, KeyError, OverflowError, OSError) as exc:
            quarantine.append({**source, "entity_id": entity, "reason": str(exc)})
            sources.append({**source, "observed_at": None, "entity_id": entity, "revision_id": None})
            continue
        revision_id = stable_id("announcement_revision_v1", entity, publication.isoformat(), title, original)
        source.update(entity_id=entity, revision_id=revision_id, observed_at=observed)
        sources.append(source)
        if explicit_bool(row.get("patch_candidate")) or (str(appid), post_id) in legacy:
            candidates.add((appid, post_id))
        version = re.search(r"\b\d+\.\d+(?:\.\d+)*\b", title)
        document = {
            "announcement_revision_id": revision_id, "post_id": post_id, "appid": appid, "game": row["game"],
            "title": title, "source_text_original": original, "canonical_text": canonical,
            "document_format": kind, "structure_available": structured,
            "publication_utc": publication, "observed_at": observed,
            "source_record_id": source["source_record_id"], "source_url": source["source_url"],
            "feed": row.get("feed", ""), "legacy_manual_flag": (str(appid), post_id) in legacy,
            "post_type": "unknown", "verification_status": "heuristic_unverified",
            "release_status_hint": "unknown", "release_utc": None, "release_time_basis": "unknown",
            "version_hint": version.group(0) if version else None,
            "branch": branch_hint(title), "platforms": platform_hints(title), "split": None,
        }
        for block in blocks:
            block.update(block_id=stable_id("block_v1", revision_id, block["ordinal"], block["text"]),
                         announcement_revision_id=revision_id, post_id=post_id, appid=appid)
        evidence = verify_document(document, blocks, source["source_kind"], row.get("event_type"), registry)
        previous = revisions.get(revision_id)
        if previous is None or (observed and (previous["observed_at"] is None or observed > previous["observed_at"])) or (structured and not previous["structure_available"]):
            revisions[revision_id] = document
            revision_blocks[revision_id] = blocks
            revision_evidence[revision_id] = evidence
    if not revisions:
        raise ValueError("No valid announcements remain")
    current = {}
    minimum_time = datetime.min.replace(tzinfo=timezone.utc)
    for doc in revisions.values():
        key = (doc["appid"], doc["post_id"])
        rank = (doc["observed_at"] or minimum_time, doc["structure_available"], doc["announcement_revision_id"])
        if key not in current or rank > current[key][0]:
            current[key] = (rank, doc)
    documents = sorted((value[1] for value in current.values()), key=lambda d: (d["appid"], d["publication_utc"], d["post_id"]))
    current_blocks, changes, patches = [], [], []
    for doc in documents:
        blocks = revision_blocks[doc["announcement_revision_id"]]
        current_blocks.extend(blocks)
        changes.extend(extract_changes(doc, blocks))
        verified = doc["verification_status"] in {"source_confirmed_patch_post", "human_verified_patch_post", "source_reviewed_patch_post"}
        if doc["post_type"] != "non_patch" and (verified or doc["post_type"] in {"patch_notes", "update"} or (doc["appid"], doc["post_id"]) in candidates):
            patches.append({
                "patch_id": stable_id("patch_post_v1", doc["appid"], doc["post_id"]),
                "announcement_revision_id": doc["announcement_revision_id"], "post_id": doc["post_id"],
                "appid": doc["appid"], "game": doc["game"], "title": doc["title"],
                "publication_utc": doc["publication_utc"], "release_utc": doc["release_utc"],
                "anchor_utc": doc["release_utc"] or doc["publication_utc"],
                "anchor_basis": doc["release_time_basis"] if doc["release_utc"] else "publication_proxy",
                "verification_status": doc["verification_status"],
                "source_confirmed": doc["verification_status"] in {"source_confirmed_patch_post", "source_reviewed_patch_post"},
                "human_verified": doc["verification_status"] == "human_verified_patch_post",
                "legacy_manual_flag": doc["legacy_manual_flag"], "verified_for_analysis": verified,
                "version_hint": doc["version_hint"], "branch": doc["branch"], "platforms": doc["platforms"],
                "source_url": doc["source_url"], "overlapping_patch_posts": 0, "split": None,
            })
    known_revision_ids = set(revisions)
    stale = set(registry) - known_revision_ids
    if stale:
        raise ValueError(f"Patch registry references {len(stale)} unknown announcement revisions")
    return {"announcements": documents,
            "announcement_revisions": sorted(revisions.values(), key=lambda d: (d["appid"], d["publication_utc"], d["announcement_revision_id"])),
            "announcement_blocks": current_blocks, "changes": changes, "patches": patches,
            "verification_evidence": [e for key in sorted(revision_evidence) for e in revision_evidence[key]],
            "source_records": sources, "quarantine": quarantine,
            "stats": {"source_rows": len(observations), "valid_source_rows": len(sources) - len(quarantine),
                      "quarantined_rows": len(quarantine), "unique_revisions": len(revisions),
                      "current_posts": len(documents), "structured_posts": sum(d["structure_available"] for d in documents),
                      "change_candidates": len(changes), "patch_posts": len(patches),
                      "verification_statuses": dict(Counter(p["verification_status"] for p in patches))}}
