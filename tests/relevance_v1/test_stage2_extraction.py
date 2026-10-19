from __future__ import annotations

from collections import Counter

import steam_patch_relevance.stage2.extraction as extraction_module
from steam_patch_relevance.stage2.extraction import (
    _entity,
    _review_aspect,
    build_terminology,
    classify_announcement,
    extract_patch_changes,
    extract_review_claims,
)
from steam_patch_relevance.stage2.llm_interface import ProposedChange, validate_proposal
from steam_patch_relevance.stage2.markup import iter_blocks
from steam_patch_relevance.stage2.pipeline import (
    _append_claim_samples,
    _make_episode_overlaps,
    _make_review_windows,
    _manifest_run_id,
)


def _announcement(body: str, *, title: str = "Gameplay Update", appid: int = 730) -> dict:
    return {
        "announcement_revision_id": "announcement-revision-1",
        "announcement_id": "announcement-1",
        "appid": appid,
        "title": title,
        "body_original": body,
        "published_unix": 1_700_000_000,
        "published_at_utc": None,
        "source_url": "https://steamcommunity.com/example",
        "source_observation_id": "source-1",
        "payload_sha256": "hash-1",
        "linked_urls_json": "[]",
        "officialness": "steam_community_announcement_feed",
        "feedname": "steam_community_announcements",
        "announcement_language": None,
        "body_truncated_suspected": False,
    }


def _extract(body: str) -> list[dict]:
    announcement = _announcement(body)
    classification = classify_announcement(announcement)
    return extract_patch_changes(
        [announcement],
        {announcement["announcement_revision_id"]: classification},
        {730: "Counter-Strike 2"},
    )


def test_structured_list_splits_changes_and_keeps_exact_raw_source_spans() -> None:
    body = "[h2]Gameplay[/h2][list][*]Reduced price of the MAC-10 by $100.[*]Added Anubis to the map pool.[/list]"
    blocks = list(iter_blocks(body))
    assert [block.text for block in blocks] == [
        "Gameplay",
        "Reduced price of the MAC-10 by $100.",
        "Added Anubis to the map pool.",
    ]
    changes = _extract(body)
    assert len(changes) == 2
    for row in changes:
        assert row["source_span_verified"] is True
        start, end = row["source_span_start"], row["source_span_end"]
        assert body[start:end] == row["source_span_raw"]
    assert changes[0]["numeric_delta"] == -100.0
    assert changes[0]["direction"] == "decreased"
    assert changes[0]["entity"] == "MAC-10"
    assert changes[0]["aspect"] == "purchase_price_or_cost"


def test_invalid_source_span_is_retained_with_an_explicit_quality_flag(monkeypatch) -> None:
    monkeypatch.setattr(extraction_module, "_source_span", lambda *_args: (-1, 100_000))
    change = _extract("[list][*]Reduced the MAC-10 price.[/list]")[0]
    assert change["source_span_verified"] is False
    assert change["source_span_raw"] is None
    assert "source_span_invalid" in change["quality_flags"]


def test_section_heading_is_hierarchy_not_an_atomic_change() -> None:
    body = "[b]Gameplay Improvements[/b][list][*]Reduced recoil by 10%.[/list]"
    changes = _extract(body)
    assert len(changes) == 1
    assert changes[0]["change_text"] == "Reduced recoil by 10%."
    assert "Gameplay Improvements" in changes[0]["heading_path"]


def test_generic_note_heading_is_not_used_as_a_change_entity() -> None:
    assert _entity("We are investigating the issue.", ["Note"]) == (None, [])
    assert _entity("Fixed the hero ability.", ["Kez"]) == ("Kez", ["Kez"])
    assert _entity("Added mission samples.", ["Level Design changes"]) == (None, [])


def test_multiple_actions_in_one_list_item_are_split_into_atomic_rows() -> None:
    body = "[list][*]We have increased damage and reduced spread by 10%.[/list]"
    changes = _extract(body)
    assert len(changes) == 2
    assert [row["direction"] for row in changes] == ["increased", "decreased"]
    for row in changes:
        assert body[row["source_span_start"] : row["source_span_end"]] == row["source_span_raw"]


def test_nested_weapon_context_and_numeric_values_are_preserved() -> None:
    body = "[b]Primary weapons[/b] MP-98 Knight [list][*]Damage increased from 65 to 70[/list]"
    changes = _extract(body)
    assert len(changes) == 1
    change = changes[0]
    assert change["entity"] == "MP-98 Knight"
    assert change["aspect"] == "damage_or_attack_power"
    assert change["action"] == "increased"
    assert change["direction"] == "increased"
    assert change["previous_value"] == "65"
    assert change["new_value"] == "70"
    assert change["heading_path"] == ["Primary weapons", "MP-98 Knight"]


def test_slash_separated_balance_values_remain_intact() -> None:
    body = "[list][*]Talon Toss: Cooldown increased from 15/12/9/6 to 16/13/10/7.[/list]"
    change = _extract(body)[0]
    assert change["previous_value"] == "15/12/9/6"
    assert change["new_value"] == "16/13/10/7"
    assert change["direction"] == "increased"


def test_acknowledged_issue_is_not_mislabeled_as_implemented_fix() -> None:
    body = "[list][*]We are aware that matchmaking can fail when the server is full.[*]Fixed an issue where players crashed when joining a match.[/list]"
    changes = _extract(body)
    assert len(changes) == 2
    assert changes[0]["developer_status"] == "acknowledged_or_planned"
    assert changes[1]["developer_status"] == "implemented_bug_fix"
    assert changes[1]["bug_symptom"] == "players crashed"
    assert changes[1]["bug_trigger"] == "when joining a match"


def test_broad_fix_summaries_and_ambiguous_bug_syntax_are_flagged() -> None:
    body = "[list][*]Fixed a number of issues with Play Unranked where toggling modes breaks the page.[/list]"
    change = _extract(body)[0]
    assert "broad_change_summary" in change["quality_flags"]
    assert "bug_trigger_symptom_ambiguous" in change["quality_flags"]


def test_qualified_fix_claim_is_distinguished_from_confirmed_implementation() -> None:
    body = "[list][*]We believe we have fixed the mission reward issue but will continue to monitor it.[/list]"
    changes = _extract(body)
    assert len(changes) == 1
    assert changes[0]["developer_status"] == "claimed_fix_with_uncertainty"
    assert "developer_fix_qualified" in changes[0]["quality_flags"]


def test_ambiguous_multiple_game_entities_are_flagged_instead_of_guessing() -> None:
    body = "[list][*]Fixed an issue where Chronosphere froze Gem of True Sight cooldown.[/list]"
    changes = _extract(body)
    assert len(changes) == 1
    assert changes[0]["entity"] is None
    assert len(changes[0]["entity_candidates"]) >= 2
    assert "entity_ambiguous" in changes[0]["quality_flags"]


def test_mixed_review_sentiment_negation_and_temporal_cues_keep_exact_offsets() -> None:
    text = "The damage is great, but matchmaking is not good after the update. The weapon is not broken now."
    review = {
        "review_revision_id": "revision-current",
        "logical_revision_key": "logical-review-1",
        "recommendation_id": "review-1",
        "source_payload_sha256": "payload-current",
        "appid": 730,
        "created_at_utc": None,
        "updated_at_utc": None,
        "language": "english",
        "review_text_original": text,
    }
    claims = extract_review_claims([review], {730: "Counter-Strike 2"})
    assert [claim["claim_text_original"] for claim in claims] == [
        "The damage is great,",
        "matchmaking is not good after the update.",
        "The weapon is not broken now.",
    ]
    for claim in claims:
        assert (
            text[claim["claim_span_start"] : claim["claim_span_end"]]
            == claim["claim_text_original"]
        )
        assert claim["patch_specificity"] == "not_assigned"
    assert claims[0]["polarity"] == "positive"
    assert claims[1]["polarity"] == "negative"
    assert claims[1]["negated"] is True
    assert "after_update" in claims[1]["temporal_cues"]
    assert claims[2]["polarity"] == "positive"
    assert "not_patch_specific_by_word_alone" in claims[2]["temporal_cues"]


def test_review_edits_have_distinct_revision_identity_and_unicode_offsets() -> None:
    base = {
        "logical_revision_key": "logical-1",
        "recommendation_id": "review-1",
        "source_payload_sha256": "hash",
        "appid": 570,
        "created_at_utc": None,
        "language": "english",
    }
    first = dict(
        base,
        review_revision_id="rev-1",
        updated_at_utc=None,
        review_text_original="Жарко! The Dota 2 menu is clunky.",
    )
    edited = dict(
        base,
        review_revision_id="rev-2",
        updated_at_utc=None,
        review_text_original="Жарко! The Dota 2 menu is much better.",
    )
    claims = extract_review_claims([first, edited], {570: "Dota 2"})
    assert {row["review_revision_id"] for row in claims} == {"rev-1", "rev-2"}
    for review in (first, edited):
        for claim in (
            row for row in claims if row["review_revision_id"] == review["review_revision_id"]
        ):
            assert (
                review["review_text_original"][claim["claim_span_start"] : claim["claim_span_end"]]
                == claim["claim_text_original"]
            )


def test_two_patch_windows_overlap_without_assigning_review_relevance() -> None:
    episodes = [
        {"patch_id": "a", "game_id": 570, "window_start_unix": 100, "window_end_unix": 300},
        {"patch_id": "b", "game_id": 570, "window_start_unix": 250, "window_end_unix": 400},
        {"patch_id": "c", "game_id": 730, "window_start_unix": 150, "window_end_unix": 250},
    ]
    overlaps = _make_episode_overlaps(episodes)
    assert len(overlaps) == 1
    assert {overlaps[0]["patch_id_a"], overlaps[0]["patch_id_b"]} == {"a", "b"}
    assert overlaps[0]["temporal_only"] is True


def test_review_window_rows_keep_game_identity() -> None:
    rows = _make_review_windows(
        [{"appid": 570, "patch_id": "source-patch", "window_segment": "post_1_7d"}],
        {"source-patch": "rv2-patch"},
    )
    assert rows[0]["game_id"] == 570


def test_bbcode_linked_patch_notes_are_preserved_and_not_fetched() -> None:
    row = _announcement(
        "[list][*]Reduced recoil by 10%.[/list] [url=https://example.com/patch-notes]Full notes[/url]"
    )
    result = classify_announcement(row)
    assert "https://example.com/patch-notes" in result["linked_urls_json"]
    assert result["full_patch_notes_status"] == "announcement_body_and_linked_notes_unverified"


def test_review_entity_lookup_uses_patch_backed_terms_not_capitalized_words() -> None:
    announcement = _announcement("[list][*]Reduced MAC-10 recoil.[/list]")
    classification = classify_announcement(announcement)
    changes = extract_patch_changes(
        [announcement],
        {announcement["announcement_revision_id"]: classification},
        {730: "Counter-Strike 2"},
    )
    review = {
        "review_revision_id": "review-revision-1",
        "logical_revision_key": "review-logical-1",
        "recommendation_id": "review-1",
        "source_payload_sha256": "review-hash",
        "appid": 730,
        "review_text_original": "After the update, recoil feels awful. MAC-10 is useful.",
    }
    terms, lookup = build_terminology([announcement], changes, [review], {730: "Counter-Strike 2"})
    claims = extract_review_claims([review], {730: "Counter-Strike 2"}, lookup)
    matchable_terms = {row["term"] for row in terms if row["is_entity_matchable"]}
    assert "MAC-10" in matchable_terms
    assert claims[0]["referenced_entity"] is None
    assert claims[1]["referenced_entity"] == "MAC-10"


def test_single_word_game_entity_matching_preserves_case() -> None:
    review = {
        "review_revision_id": "review-revision-2",
        "logical_revision_key": "review-logical-2",
        "recommendation_id": "review-2",
        "source_payload_sha256": "review-hash-2",
        "appid": 553850,
        "review_text_original": "I came back to the game again.",
    }
    vocabulary = {
        553850: [
            {
                "term": "Back",
                "aliases": ["back"],
                "is_entity_matchable": True,
            }
        ]
    }
    claim = extract_review_claims([review], {553850: "HELLDIVERS 2"}, vocabulary)[0]
    assert claim["referenced_entity"] is None


def test_generic_use_verb_does_not_imply_ammunition_capacity() -> None:
    assert _review_aspect("You can use them correctly.") is None


def test_qa_sample_records_the_review_language_bucket() -> None:
    rows = []
    _append_claim_samples(
        rows,
        "rv2-test",
        {(570, "russian"): [{"claim_id": "claim-1", "claim_text_original": "Хорошая игра"}]},
        Counter({(570, "russian"): 10}),
        1,
    )
    assert rows[0]["language"] == "russian"
    assert "russian" in rows[0]["stratum"]


def test_sample_size_changes_the_versioned_dataset_identity() -> None:
    args = ("rv1-test", {"reviews.parquet": "sha256"}, None)
    assert _manifest_run_id(*args, 1)[0] != _manifest_run_id(*args, 2)[0]


def test_optional_llm_spans_are_rejected_when_not_verifiable() -> None:
    good = ProposedChange(0, 5, "MAC-10", "cost", "reduced", "decreased", "implemented_change", 0.9)
    bad = ProposedChange(0, 50, "MAC-10", "cost", "reduced", "decreased", "implemented_change", 0.9)
    assert validate_proposal("price down", good) == (True, None)
    assert validate_proposal("price down", bad) == (False, "offset_out_of_bounds")


def test_classification_can_assign_multiple_announcement_categories() -> None:
    row = _announcement(
        "[list][*]Fixed a crash when loading the new mission.[*]Performance improved on large maps.[/list]",
        title="Major Gameplay Update",
        appid=553850,
    )
    labels = classify_announcement(row)["categories"]
    assert "specific_bug_fix" in labels
    assert "performance_or_stability_change" in labels
    assert "major_gameplay_or_balance_update" in labels


def test_nonofficial_news_is_classified_but_never_becomes_a_patch_episode() -> None:
    row = _announcement("[list][*]Added a new mission.[/list]", title="New Mission Update")
    row["officialness"] = "other_feed_unverified"
    result = classify_announcement(row)
    assert "new_feature_or_content" in result["categories"]
    assert result["patch_eligible"] is False
    assert result["patch_id"] is None
