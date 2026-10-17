"""Game-held-out splits, descriptive windows, and bounded unlabeled candidate retrieval."""

import math
import re
from collections import Counter, defaultdict
from datetime import timedelta

from steam_insights.pipeline.storage import parse_time, stable_id

STOP = set(
    "the and that this with was were for when have had are but will can could would should from into your you they their there then than also game games patch update fixed fixes issue issues bug bugs please been being its our these those some more all just has get got very really much how what which who about after before now new one not".split()
)
# Negation remains in model text; retrieval ignores common scaffolding terms only.
STOP.discard("not")


def terms(text: str) -> set[str]:
    return {
        term
        for term in re.findall(r"\b\w+(?:[-.]\w+)*\b", text.casefold())
        if len(term) >= 3 and term not in STOP
    }


def assign_splits(
    review_result: dict, announcement_result: dict, config
) -> tuple[list[dict], dict]:
    names = {
        r["appid"]: r["game"]
        for r in review_result["reviews"] + announcement_result["announcements"]
    }
    settings = config.values["splits"]
    ordered = sorted(names, key=lambda appid: stable_id("game_split_v1", settings["seed"], appid))
    test_count, validation_count = settings["test_games"], settings["validation_games"]
    if test_count + validation_count >= len(ordered):
        raise ValueError(
            "Split game counts leave no training games; adjust splits in pipeline.toml"
        )
    split_map = {
        appid: "test"
        if index < test_count
        else "validation"
        if index < test_count + validation_count
        else "train"
        for index, appid in enumerate(ordered)
    }
    for result in (review_result, announcement_result):
        for name, rows in result.items():
            if isinstance(rows, list):
                for row in rows:
                    if "split" in row and "appid" in row:
                        row["split"] = split_map[row["appid"]]
    group_splits = defaultdict(set)
    for row in review_result["review_revisions"]:
        for field in ("exact_duplicate_group", "near_duplicate_group"):
            if row.get(field):
                group_splits[(field, row[field])].add(row["split"])
    crossing = {key for key, splits in group_splits.items() if len(splits) > 1}
    for row in review_result["review_revisions"]:
        row["cross_split_duplicate"] = any(
            (field, row.get(field)) in crossing
            for field in ("exact_duplicate_group", "near_duplicate_group")
        )
    return [
        {"appid": appid, "game": names[appid], "split": split_map[appid]} for appid in sorted(names)
    ], {
        "allocation": dict(Counter(split_map.values())),
        "cross_split_duplicate_families": len(crossing),
        "current_reviews_excluded_from_supervised_for_duplicate_leakage": sum(
            r["cross_split_duplicate"] for r in review_result["reviews"]
        ),
    }


def build_windows(
    reviews: list[dict], patches: list[dict], config, collection_report=None
) -> list[dict]:
    by_game = defaultdict(list)
    for row in reviews:
        by_game[row["appid"]].append(row)
    by_game_patches = defaultdict(list)
    for patch in patches:
        by_game_patches[patch["appid"]].append(patch)
    completed = defaultdict(set)
    for window in (collection_report or {}).get("windows", []):
        if window["complete_as_of_fetch"]:
            completed[window["patch_id"]].add(
                (window["side"], parse_time(window["start_utc"]), parse_time(window["end_utc"]))
            )
    settings = config.values["windows"]
    before_delta, after_delta = (
        timedelta(days=settings["days_before"]),
        timedelta(days=settings["days_after"]),
    )
    results = []
    for patch in patches:
        at = patch["anchor_utc"]
        start, end = at - before_delta, at + after_delta
        game_reviews = by_game[patch["appid"]]
        before = [r for r in game_reviews if start <= r["created_utc"] < at]
        after = [r for r in game_reviews if at <= r["created_utc"] < end]
        pre_text, post_text = (
            [r for r in before if r["text_eligible"]],
            [r for r in after if r["text_eligible"]],
        )
        pre_dates, post_dates = (
            len({r["created_utc"].date() for r in pre_text}),
            len({r["created_utc"].date() for r in post_text}),
        )
        full = bool(
            game_reviews
            and min(r["created_utc"] for r in game_reviews) <= start
            and max(r["created_utc"] for r in game_reviews) >= end
        )
        enough = (
            full
            and min(len(pre_text), len(post_text)) >= settings["minimum_reviews"]
            and min(pre_dates, post_dates) >= settings["minimum_review_dates"]
        )
        stronger = (
            enough and min(len(pre_text), len(post_text)) >= settings["stronger_minimum_reviews"]
        )
        overlap = sum(
            p["patch_id"] != patch["patch_id"] and start <= p["anchor_utc"] < end
            for p in by_game_patches[patch["appid"]]
        )
        patch["overlapping_patch_posts"] = overlap
        status = (
            "verified_post_coverage_passes"
            if patch["verified_for_analysis"] and enough
            else "candidate_coverage_passes_needs_verification"
            if enough
            else "insufficient_or_edge_censored"
        )
        results.append(
            {
                "patch_id": patch["patch_id"],
                "appid": patch["appid"],
                "game": patch["game"],
                "title": patch["title"],
                "anchor_utc": at,
                "anchor_basis": patch["anchor_basis"],
                "window_start_utc": start,
                "window_end_utc": end,
                "pre_reviews": len(before),
                "post_reviews": len(after),
                "pre_eligible_reviews": len(pre_text),
                "post_eligible_reviews": len(post_text),
                "pre_active_dates": pre_dates,
                "post_active_dates": post_dates,
                "pre_edited_reviews": sum(r["edited"] for r in before),
                "post_edited_reviews": sum(r["edited"] for r in after),
                "pre_negative_recommendation_share": sum(not r["recommended"] for r in before)
                / len(before)
                if before
                else None,
                "post_negative_recommendation_share": sum(not r["recommended"] for r in after)
                / len(after)
                if after
                else None,
                "observed_bounds_cover_window": full,
                "coverage_screen_met": enough,
                "stronger_coverage_screen_met": stronger,
                "verified_patch_post": patch["verified_for_analysis"],
                "verification_status": patch["verification_status"],
                "overlapping_patch_posts": overlap,
                "pre_reviews_needed_for_screen": max(
                    settings["minimum_reviews"] - len(pre_text), 0
                ),
                "post_reviews_needed_for_screen": max(
                    settings["minimum_reviews"] - len(post_text), 0
                ),
                "review_collection_complete": {("pre", start, at), ("post", at, end)}
                <= completed[patch["patch_id"]],
                "assessment": status,
                "split": patch["split"],
            }
        )
    return sorted(results, key=lambda r: (r["appid"], r["anchor_utc"], r["patch_id"]))


def build_candidates(reviews, announcements, changes, patches, config) -> list[dict]:
    settings = config.values["candidates"]
    docs = {d["announcement_revision_id"]: d for d in announcements}
    patch_map = {p["announcement_revision_id"]: p for p in patches}
    indexes = defaultdict(lambda: defaultdict(list))
    change_terms = {}
    changes_by_id = {c["change_id"]: c for c in changes}
    for change in changes:
        vocabulary = terms(change["text"] + " " + " ".join(change["heading_path"]))
        change_terms[change["change_id"]] = vocabulary
        for term in vocabulary:
            indexes[change["appid"]][term].append(change["change_id"])
    results = []
    for review in reviews:
        if not review["text_eligible"]:
            continue
        vocabulary = terms(review["review_text"])
        overlaps = Counter()
        for term in vocabulary:
            overlaps.update(indexes[review["appid"]].get(term, []))
        per_task = defaultdict(list)
        for change_id, count in overlaps.items():
            if count < settings["minimum_shared_terms"]:
                continue
            change = changes_by_id[change_id]
            doc = docs[change["announcement_revision_id"]]
            patch = patch_map.get(change["announcement_revision_id"])
            published_lag = (review["created_utc"] - doc["publication_utc"]).total_seconds() / 86400
            task, lag = None, published_lag
            if published_lag >= 0 and patch:
                lag = (review["created_utc"] - patch["anchor_utc"]).total_seconds() / 86400
                if 0 <= lag < settings["feedback_days"]:
                    task = "post_patch_feedback"
            elif -settings["resolution_days"] <= published_lag < 0:
                task = "retrospective_complaint_resolution"
            if task is None:
                continue
            score = count / math.sqrt(
                max(1, len(vocabulary)) * max(1, len(change_terms[change_id]))
            )
            per_task[task].append((score, change_id, lag))
        for task, ranked in sorted(per_task.items()):
            for score, change_id, lag in sorted(ranked, key=lambda x: (-x[0], x[1]))[
                : settings["max_per_review_per_task"]
            ]:
                change = changes_by_id[change_id]
                patch = patch_map.get(change["announcement_revision_id"])
                results.append(
                    {
                        "candidate_id": stable_id(
                            "candidate_v1", review["review_revision_id"], change_id, task
                        ),
                        "review_revision_id": review["review_revision_id"],
                        "review_id": review["review_id"],
                        "change_id": change_id,
                        "announcement_revision_id": change["announcement_revision_id"],
                        "patch_id": patch["patch_id"] if patch else None,
                        "appid": review["appid"],
                        "task": task,
                        "lag_days": lag,
                        "shared_terms": sorted(vocabulary & change_terms[change_id]),
                        "lexical_score": score,
                        "scope_compatibility": "unknown_review_platform_or_branch",
                        "split": review["split"],
                        "cross_split_duplicate": review["cross_split_duplicate"],
                    }
                )
    return sorted(
        results,
        key=lambda r: (
            r["appid"],
            r["review_revision_id"],
            r["task"],
            -r["lexical_score"],
            r["change_id"],
        ),
    )


def model_exports(review_result, changes, candidates) -> dict:
    reviews = {r["review_revision_id"]: r for r in review_result["reviews"]}
    by_change = {r["change_id"]: r for r in changes}
    passages = defaultdict(list)
    for passage in review_result["review_passages"]:
        passages[passage["review_revision_id"]].append(passage)
    model_reviews = []
    for passage in review_result["review_passages"]:
        review = reviews[passage["review_revision_id"]]
        model_reviews.append(
            {
                **passage,
                "review_context": review["review_text"],
                "cross_split_duplicate": review["cross_split_duplicate"],
                "language_warning": review["language_warning"],
            }
        )
    model_changes = [{**c} for c in changes]
    model_pairs = []
    for candidate in candidates:
        review, change = reviews[candidate["review_revision_id"]], by_change[candidate["change_id"]]
        shared = set(candidate["shared_terms"])
        selected = max(
            passages[review["review_revision_id"]],
            key=lambda p: (len(terms(p["text"]) & shared), -p["ordinal"]),
        )
        model_pairs.append(
            {
                **candidate,
                "review_text": review["review_text"],
                "review_passage_text": selected["text"],
                "change_text": change["text"],
                "change_context": change["context_text"],
                "title": change["title"],
                "heading_path": change["heading_path"],
                "review_char_start": selected["char_start"],
                "review_char_end": selected["char_end"],
                "change_char_start": change["char_start"],
                "change_char_end": change["char_end"],
                "language_warning": review["language_warning"],
            }
        )
    return {
        "model_review_inputs": model_reviews,
        "model_change_inputs": model_changes,
        "model_pair_inputs": model_pairs,
    }
