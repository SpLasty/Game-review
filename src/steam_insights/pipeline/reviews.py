"""Conservative review preparation, exact evidence spans, and duplicate inspection."""

import difflib
import hashlib
import json
import re
from collections import Counter, defaultdict

import numpy as np

from steam_insights.data.io import write_json
from steam_insights.data.text import clean_text, word_count
from steam_insights.pipeline.storage import explicit_bool, optional_float, parse_time, stable_id


def text_spans(text: str, maximum: int) -> list[tuple[int, int]]:
    """Bounded passages over canonical text; preserve decimals and common abbreviations."""
    boundaries = [0]
    abbreviations = {"mr.", "mrs.", "dr.", "e.g.", "i.e.", "vs.", "etc."}
    for match in re.finditer(r"\n+|(?<=[.!?])\s+(?=[A-Z\"“])", text):
        last = text[:match.start()].split()[-1:] or [""]
        if last[0].lower() not in abbreviations:
            boundaries.append(match.end())
    boundaries.append(len(text))
    parts = []
    for begin, end in zip(boundaries, boundaries[1:]):
        while begin < end and text[begin].isspace():
            begin += 1
        while end > begin and text[end - 1].isspace():
            end -= 1
        while end - begin > maximum:
            split = text.rfind(" ", begin + 1, begin + maximum)
            if split <= begin:
                split = begin + maximum
            parts.append((begin, split))
            begin = split
            while begin < end and text[begin].isspace():
                begin += 1
        if end > begin:
            parts.append((begin, end))
    merged = []
    for begin, end in parts:
        if merged and end - merged[-1][0] <= maximum:
            merged[-1] = (merged[-1][0], end)
        else:
            merged.append((begin, end))
    return merged


def _near_duplicates(rows: list[dict], settings: dict) -> tuple[list[dict], dict]:
    representatives = {}
    for row in rows:
        if row["text_eligible"] and row["exact_duplicate_group"]:
            representatives.setdefault(row["exact_duplicate_group"], row)
    buckets = defaultdict(list)
    parent = {key: key for key in representatives}
    def root(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key
    pairs = []
    saturated = 0
    for key, row in sorted(representatives.items()):
        terms = re.findall(r"\w+", row["review_text"].casefold())
        shingles = {" ".join(terms[i:i + 3]) for i in range(max(1, len(terms) - 2))}
        hashes = [int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big") for s in shingles]
        bits = np.unpackbits(np.array(hashes, dtype=">u8").view(np.uint8)).reshape(-1, 64)
        signature = int.from_bytes(np.packbits(bits.sum(axis=0) * 2 >= len(hashes)).tobytes(), "big")
        candidate_keys = set()
        for band in range(4):
            bucket = buckets[(band, (signature >> (16 * band)) & 65535)]
            if len(bucket) >= settings["near_duplicate_bucket_limit"]:
                saturated += 1
            candidate_keys.update(bucket[:settings["near_duplicate_bucket_limit"]])
            bucket.append((key, signature))
        for other_key, other_signature in sorted(candidate_keys):
            if (signature ^ other_signature).bit_count() > 3:
                continue
            other = representatives[other_key]
            a, b = row["review_text"].casefold(), other["review_text"].casefold()
            if min(len(a), len(b)) / max(len(a), len(b)) < settings["near_duplicate_similarity"]:
                continue
            similarity = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
            if similarity >= settings["near_duplicate_similarity"]:
                first, second = sorted([root(key), root(other_key)])
                parent[second] = first
                pairs.append({"left_revision_id": row["review_revision_id"],
                              "right_revision_id": other["review_revision_id"],
                              "similarity": similarity, "method": "simhash64_hamming3_sequence_ratio"})
    families = defaultdict(list)
    for key in representatives:
        families[root(key)].append(key)
    mapping = {member: stable_id("near_duplicate", sorted(members))
               for members in families.values() if len(members) > 1 for member in members}
    for row in rows:
        row["near_duplicate_group"] = mapping.get(row["exact_duplicate_group"])
    return pairs, {"near_duplicate_pairs": len(pairs), "saturated_bucket_visits": saturated,
                   "near_duplicate_detection_exhaustive": False}


def prepare_review_observations(observations: list[dict], config) -> dict:
    settings = config.values["reviews"]
    cache_path = config.work_dir / "language_cache.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    from langdetect import DetectorFactory, LangDetectException, detect_langs
    DetectorFactory.seed = 0
    revisions, sources, quarantine = {}, [], []
    payloads = {}
    created_times = {}
    reasons = Counter()
    for source_row in observations:
        source = dict(source_row["_source"])
        entity = f"{source_row.get('appid', '')}:{source_row.get('review_id', '')}"
        try:
            appid = int(source_row["appid"])
            review_id = str(source_row["review_id"]).strip()
            if not 0 < appid <= 2**32 - 1 or not re.fullmatch(r"[1-9]\d*", review_id):
                raise ValueError("invalid source ID")
            if not str(source_row.get("game", "")).strip():
                raise ValueError("missing game")
            created = parse_time(int(source_row["timestamp_created"]))
            updated = parse_time(int(source_row["timestamp_updated"]))
            if updated < created or int(source_row["timestamp_created"]) < 0:
                raise ValueError("invalid review timestamp order")
            for field, expected in (("created_utc", created), ("updated_utc", updated)):
                if source_row.get(field) and parse_time(source_row[field]) != expected:
                    raise ValueError(f"{field} ISO/epoch disagreement")
            observed = parse_time(source_row.get("observed_at"))
            vote = explicit_bool(source_row["recommended"])
            if vote is None:
                raise ValueError("missing recommendation")
            original = str(source_row.get("review_text", ""))
            canonical = clean_text(original)
            words = word_count(original)
            language = str(source_row.get("language", "unknown")).strip().lower()
            for optional in ("unedited", "steam_purchase", "refunded", "primarily_steam_deck"):
                if optional in source_row:
                    explicit_bool(source_row[optional])
            playtime = optional_float(source_row.get("playtime_at_review_hours"))
            lifetime = optional_float(source_row.get("lifetime_playtime_hours"))
        except (ValueError, TypeError, KeyError, OverflowError, OSError) as exc:
            reason = str(exc)
            quarantine.append({**source, "entity_id": entity, "reason": reason})
            source.update(entity_id=entity, revision_id=None, observed_at=None)
            sources.append(source)
            reasons[reason] += 1
            continue
        revision_id = stable_id("review_revision_v1", entity, updated.isoformat(), original, vote)
        conflict_key = (entity, updated)
        if conflict_key in payloads and payloads[conflict_key] != revision_id:
            raise ValueError(f"Conflicting review text/vote for same ID and update time: {entity}")
        if entity in created_times and created_times[entity] != created:
            raise ValueError(f"Conflicting review creation timestamp: {entity}")
        created_times[entity] = created
        payloads[conflict_key] = revision_id
        source.update(entity_id=entity, revision_id=revision_id, observed_at=observed)
        sources.append(source)
        detected, probability = None, None
        key = stable_id("langdetect_1.0.9_seed0", canonical)
        if words >= settings["language_detection_min_words"]:
            if key not in cache:
                try:
                    best = detect_langs(canonical)[0]
                    cache[key] = [best.lang, float(best.prob)]
                except LangDetectException:
                    cache[key] = [None, None]
            detected, probability = cache[key]
        eligible = language == settings["language"] and words >= settings["minimum_words"]
        eligibility = "eligible" if eligible else "source_language" if language != settings["language"] else "short_or_empty_text"
        row = {
            "review_revision_id": revision_id, "review_id": review_id, "appid": appid,
            "game": source_row["game"], "review_text_original": original, "review_text": canonical,
            "language": language, "created_utc": created, "updated_utc": updated,
            "observed_at": observed, "recommended": vote, "source_record_id": source["source_record_id"],
            "source_url": source["source_url"], "author_hash": source_row.get("author_hash") or None,
            "author_hash_namespace": source_row.get("author_hash_namespace") or "legacy_collector",
            "playtime_at_review_hours": playtime, "lifetime_playtime_hours": lifetime,
            "word_count": words, "text_eligible": eligible, "text_eligibility_reason": eligibility,
            "edited": created != updated, "detected_language": detected, "language_probability": probability,
            "language_warning": bool(detected and detected != "en" and probability >= settings["language_warning_probability"]),
            "exact_duplicate_group": stable_id("exact_text_v1", " ".join(canonical.casefold().split())) if canonical else None,
            "near_duplicate_group": None, "split": None, "cross_split_duplicate": False,
        }
        previous = revisions.get(revision_id)
        if previous is None or (observed is not None and (previous["observed_at"] is None or observed > previous["observed_at"])):
            revisions[revision_id] = row
    write_json(cache_path, cache)
    if not revisions:
        raise ValueError("No valid reviews remain; dataset publication stopped")
    rows = sorted(revisions.values(), key=lambda r: (r["appid"], r["created_utc"], r["review_id"], r["updated_utc"], r["review_revision_id"]))
    current = {}
    for row in rows:
        key = (row["appid"], row["review_id"])
        if key not in current or row["updated_utc"] > current[key]["updated_utc"]:
            current[key] = row
    latest = sorted(current.values(), key=lambda r: (r["appid"], r["created_utc"], r["review_id"]))
    duplicates, duplicate_stats = _near_duplicates(latest, settings)
    passages = []
    for row in latest:
        if row["text_eligible"]:
            for ordinal, (start, end) in enumerate(text_spans(row["review_text"], settings["passage_max_chars"])):
                passages.append({"passage_id": stable_id("passage_v1", row["review_revision_id"], start, end),
                                 "review_revision_id": row["review_revision_id"], "review_id": row["review_id"],
                                 "appid": row["appid"], "ordinal": ordinal,
                                 "char_start": start, "char_end": end, "text": row["review_text"][start:end], "split": None})
    return {"reviews": latest, "review_revisions": rows, "review_passages": passages,
            "source_records": sources, "quarantine": quarantine, "duplicate_pairs": duplicates,
            "stats": {"source_rows": len(observations), "valid_source_rows": len(sources) - len(quarantine),
                      "quarantined_rows": len(quarantine), "unique_revisions": len(rows),
                      "current_reviews": len(latest), "repeated_observations": len(sources) - len(quarantine) - len(rows),
                      "language_warnings": sum(r["language_warning"] for r in latest),
                      "quarantine_reasons": dict(reasons), **duplicate_stats}}
