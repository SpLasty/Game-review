# Dataset contracts

Generated from `src/steam_insights/pipeline/storage.py::SCHEMAS`. Every table is an individual `.parquet` file inside a versioned snapshot. The manifest records the exact schema, row count and checksum. Nullable fields preserve unknown metadata; required identifiers and relationships are checked at publication.

Steam review/post IDs and internal identifiers are strings; app IDs are int64. Timestamps use UTC microseconds. Span offsets are zero-based Unicode character positions with exclusive ends in canonical text. `recommended` describes the recommendation vote only. Hints, candidate scores and verification of post type are not gold model labels.

## source_records

Lineage for every imported observation, including quarantined records.

| Field | Arrow type |
| --- | --- |
| `source_record_id` | `string` |
| `dataset` | `string` |
| `source_path` | `string` |
| `source_sha256` | `string` |
| `source_row` | `int64` |
| `source_kind` | `string` |
| `source_url` | `string` |
| `observed_at` | `timestamp[us, tz=UTC]` |
| `entity_id` | `string` |
| `revision_id` | `string` |

## quarantine

Invalid records and actionable reasons; not silently dropped.

| Field | Arrow type |
| --- | --- |
| `source_record_id` | `string` |
| `dataset` | `string` |
| `entity_id` | `string` |
| `reason` | `string` |
| `source_path` | `string` |
| `source_row` | `int64` |

## review_revisions

Distinct observed review states; original and canonical text.

| Field | Arrow type |
| --- | --- |
| `review_revision_id` | `string` |
| `review_id` | `string` |
| `appid` | `int64` |
| `game` | `string` |
| `review_text_original` | `string` |
| `review_text` | `string` |
| `language` | `string` |
| `created_utc` | `timestamp[us, tz=UTC]` |
| `updated_utc` | `timestamp[us, tz=UTC]` |
| `observed_at` | `timestamp[us, tz=UTC]` |
| `recommended` | `bool` |
| `source_record_id` | `string` |
| `source_url` | `string` |
| `author_hash` | `string` |
| `author_hash_namespace` | `string` |
| `playtime_at_review_hours` | `double` |
| `lifetime_playtime_hours` | `double` |
| `steam_purchase` | `bool` |
| `received_for_free` | `bool` |
| `refunded` | `bool` |
| `primarily_steam_deck` | `bool` |
| `written_during_early_access` | `bool` |
| `supplied_word_count` | `int64` |
| `word_count_mismatch` | `bool` |
| `word_count` | `int64` |
| `text_eligible` | `bool` |
| `text_eligibility_reason` | `string` |
| `edited` | `bool` |
| `detected_language` | `string` |
| `language_probability` | `double` |
| `language_warning` | `bool` |
| `exact_duplicate_group` | `string` |
| `near_duplicate_group` | `string` |
| `split` | `string` |
| `cross_split_duplicate` | `bool` |

## review_passages

Bounded canonical review spans, preserving exact offsets.

| Field | Arrow type |
| --- | --- |
| `passage_id` | `string` |
| `review_revision_id` | `string` |
| `review_id` | `string` |
| `appid` | `int64` |
| `ordinal` | `int64` |
| `char_start` | `int64` |
| `char_end` | `int64` |
| `text` | `string` |
| `split` | `string` |

## duplicate_pairs

Approximate duplicate evidence, not relevance labels.

| Field | Arrow type |
| --- | --- |
| `left_revision_id` | `string` |
| `right_revision_id` | `string` |
| `similarity` | `double` |
| `method` | `string` |

## reviews

Latest valid state of each review; full analytics population.

| Field | Arrow type |
| --- | --- |
| `review_revision_id` | `string` |
| `review_id` | `string` |
| `appid` | `int64` |
| `game` | `string` |
| `review_text_original` | `string` |
| `review_text` | `string` |
| `language` | `string` |
| `created_utc` | `timestamp[us, tz=UTC]` |
| `updated_utc` | `timestamp[us, tz=UTC]` |
| `observed_at` | `timestamp[us, tz=UTC]` |
| `recommended` | `bool` |
| `source_record_id` | `string` |
| `source_url` | `string` |
| `author_hash` | `string` |
| `author_hash_namespace` | `string` |
| `playtime_at_review_hours` | `double` |
| `lifetime_playtime_hours` | `double` |
| `steam_purchase` | `bool` |
| `received_for_free` | `bool` |
| `refunded` | `bool` |
| `primarily_steam_deck` | `bool` |
| `written_during_early_access` | `bool` |
| `supplied_word_count` | `int64` |
| `word_count_mismatch` | `bool` |
| `word_count` | `int64` |
| `text_eligible` | `bool` |
| `text_eligibility_reason` | `string` |
| `edited` | `bool` |
| `detected_language` | `string` |
| `language_probability` | `double` |
| `language_warning` | `bool` |
| `exact_duplicate_group` | `string` |
| `near_duplicate_group` | `string` |
| `split` | `string` |
| `cross_split_duplicate` | `bool` |

## announcement_revisions

All observed document revisions.

| Field | Arrow type |
| --- | --- |
| `announcement_revision_id` | `string` |
| `post_id` | `string` |
| `appid` | `int64` |
| `game` | `string` |
| `title` | `string` |
| `source_text_original` | `string` |
| `canonical_text` | `string` |
| `document_format` | `string` |
| `structure_available` | `bool` |
| `publication_utc` | `timestamp[us, tz=UTC]` |
| `observed_at` | `timestamp[us, tz=UTC]` |
| `source_record_id` | `string` |
| `source_url` | `string` |
| `feed` | `string` |
| `legacy_manual_flag` | `bool` |
| `post_type` | `string` |
| `verification_status` | `string` |
| `release_status_hint` | `string` |
| `release_utc` | `timestamp[us, tz=UTC]` |
| `release_time_basis` | `string` |
| `version_hint` | `string` |
| `branch` | `string` |
| `platforms` | `list<item: string>` |
| `split` | `string` |

## announcement_blocks

Headings, paragraphs, list items and table rows with context.

| Field | Arrow type |
| --- | --- |
| `block_id` | `string` |
| `announcement_revision_id` | `string` |
| `post_id` | `string` |
| `appid` | `int64` |
| `ordinal` | `int64` |
| `block_type` | `string` |
| `heading_path` | `list<item: string>` |
| `list_depth` | `int64` |
| `heading_origin` | `string` |
| `text` | `string` |
| `char_start` | `int64` |
| `char_end` | `int64` |

## announcement_links

Outgoing source references and extracted destinations.

| Field | Arrow type |
| --- | --- |
| `link_id` | `string` |
| `announcement_revision_id` | `string` |
| `post_id` | `string` |
| `appid` | `int64` |
| `label` | `string` |
| `original_url` | `string` |
| `target_url` | `string` |
| `target_host` | `string` |
| `reference_kind` | `string` |

## changes

Structural change candidates; rule hints are not human labels.

| Field | Arrow type |
| --- | --- |
| `change_id` | `string` |
| `announcement_revision_id` | `string` |
| `block_id` | `string` |
| `post_id` | `string` |
| `appid` | `int64` |
| `game` | `string` |
| `title` | `string` |
| `heading_path` | `list<item: string>` |
| `text` | `string` |
| `char_start` | `int64` |
| `char_end` | `int64` |
| `context_text` | `string` |
| `status_hint` | `string` |
| `topic_hints` | `list<item: string>` |
| `entity_hint` | `string` |
| `version_hint` | `string` |
| `branch` | `string` |
| `platforms` | `list<item: string>` |
| `old_value` | `string` |
| `new_value` | `string` |
| `needs_review` | `bool` |
| `extraction_method` | `string` |
| `source_url` | `string` |
| `split` | `string` |

## patches

Patch-post identity, verification, release anchor and scope.

| Field | Arrow type |
| --- | --- |
| `patch_id` | `string` |
| `announcement_revision_id` | `string` |
| `post_id` | `string` |
| `appid` | `int64` |
| `game` | `string` |
| `title` | `string` |
| `publication_utc` | `timestamp[us, tz=UTC]` |
| `release_utc` | `timestamp[us, tz=UTC]` |
| `anchor_utc` | `timestamp[us, tz=UTC]` |
| `anchor_basis` | `string` |
| `verification_status` | `string` |
| `source_confirmed` | `bool` |
| `human_verified` | `bool` |
| `legacy_manual_flag` | `bool` |
| `verified_for_analysis` | `bool` |
| `version_hint` | `string` |
| `branch` | `string` |
| `platforms` | `list<item: string>` |
| `source_url` | `string` |
| `overlapping_patch_posts` | `int64` |
| `split` | `string` |

## verification_evidence

Exact quoted source evidence, actor provenance and post-type/release decisions.

| Field | Arrow type |
| --- | --- |
| `evidence_id` | `string` |
| `announcement_revision_id` | `string` |
| `source_record_id` | `string` |
| `field` | `string` |
| `method` | `string` |
| `value` | `string` |
| `evidence_text` | `string` |
| `char_start` | `int64` |
| `char_end` | `int64` |
| `source_url` | `string` |
| `checked_by` | `string` |
| `checked_at` | `timestamp[us, tz=UTC]` |

## announcements

Current canonical documents and structure quality.

| Field | Arrow type |
| --- | --- |
| `announcement_revision_id` | `string` |
| `post_id` | `string` |
| `appid` | `int64` |
| `game` | `string` |
| `title` | `string` |
| `source_text_original` | `string` |
| `canonical_text` | `string` |
| `document_format` | `string` |
| `structure_available` | `bool` |
| `publication_utc` | `timestamp[us, tz=UTC]` |
| `observed_at` | `timestamp[us, tz=UTC]` |
| `source_record_id` | `string` |
| `source_url` | `string` |
| `feed` | `string` |
| `legacy_manual_flag` | `bool` |
| `post_type` | `string` |
| `verification_status` | `string` |
| `release_status_hint` | `string` |
| `release_utc` | `timestamp[us, tz=UTC]` |
| `release_time_basis` | `string` |
| `version_hint` | `string` |
| `branch` | `string` |
| `platforms` | `list<item: string>` |
| `split` | `string` |

## games

Frozen allocation of game IDs to train/validation/test.

| Field | Arrow type |
| --- | --- |
| `appid` | `int64` |
| `game` | `string` |
| `split` | `string` |

## patch_windows

Descriptive review availability around each post/event.

| Field | Arrow type |
| --- | --- |
| `patch_id` | `string` |
| `appid` | `int64` |
| `game` | `string` |
| `title` | `string` |
| `anchor_utc` | `timestamp[us, tz=UTC]` |
| `anchor_basis` | `string` |
| `window_start_utc` | `timestamp[us, tz=UTC]` |
| `window_end_utc` | `timestamp[us, tz=UTC]` |
| `pre_reviews` | `int64` |
| `post_reviews` | `int64` |
| `pre_eligible_reviews` | `int64` |
| `post_eligible_reviews` | `int64` |
| `pre_active_dates` | `int64` |
| `post_active_dates` | `int64` |
| `pre_edited_reviews` | `int64` |
| `post_edited_reviews` | `int64` |
| `pre_negative_recommendation_share` | `double` |
| `post_negative_recommendation_share` | `double` |
| `observed_bounds_cover_window` | `bool` |
| `window_coverage_evidence` | `string` |
| `coverage_screen_met` | `bool` |
| `stronger_coverage_screen_met` | `bool` |
| `verified_patch_post` | `bool` |
| `verification_status` | `string` |
| `overlapping_patch_posts` | `int64` |
| `pre_reviews_needed_for_screen` | `int64` |
| `post_reviews_needed_for_screen` | `int64` |
| `review_collection_complete` | `bool` |
| `assessment` | `string` |
| `split` | `string` |

## candidates

Bounded lexical review/change retrieval candidates by task.

| Field | Arrow type |
| --- | --- |
| `candidate_id` | `string` |
| `review_revision_id` | `string` |
| `review_id` | `string` |
| `change_id` | `string` |
| `announcement_revision_id` | `string` |
| `patch_id` | `string` |
| `appid` | `int64` |
| `task` | `string` |
| `lag_days` | `double` |
| `shared_terms` | `list<item: string>` |
| `lexical_score` | `double` |
| `scope_compatibility` | `string` |
| `split` | `string` |
| `cross_split_duplicate` | `bool` |

## annotations

Validated human labels, evidence, adjudication and supersession.

| Field | Arrow type |
| --- | --- |
| `annotation_id` | `string` |
| `candidate_id` | `string` |
| `annotator_id` | `string` |
| `label_source` | `string` |
| `adjudicated` | `bool` |
| `created_at` | `timestamp[us, tz=UTC]` |
| `relevance` | `string` |
| `sentiment` | `string` |
| `fix_status` | `string` |
| `review_evidence_start` | `int64` |
| `review_evidence_end` | `int64` |
| `review_evidence_text` | `string` |
| `change_evidence_start` | `int64` |
| `change_evidence_end` | `int64` |
| `change_evidence_text` | `string` |
| `supersedes` | `list<item: string>` |

## model_review_inputs

Whitelisted text/context for review inference.

| Field | Arrow type |
| --- | --- |
| `passage_id` | `string` |
| `review_revision_id` | `string` |
| `appid` | `int64` |
| `text` | `string` |
| `review_context` | `string` |
| `char_start` | `int64` |
| `char_end` | `int64` |
| `split` | `string` |
| `cross_split_duplicate` | `bool` |
| `language_warning` | `bool` |

## model_change_inputs

Whitelisted change and heading context for inference.

| Field | Arrow type |
| --- | --- |
| `change_id` | `string` |
| `announcement_revision_id` | `string` |
| `appid` | `int64` |
| `text` | `string` |
| `context_text` | `string` |
| `title` | `string` |
| `heading_path` | `list<item: string>` |
| `char_start` | `int64` |
| `char_end` | `int64` |
| `split` | `string` |
| `needs_review` | `bool` |

## model_pair_inputs

Unlabeled review/change pairs with full context.

| Field | Arrow type |
| --- | --- |
| `candidate_id` | `string` |
| `review_revision_id` | `string` |
| `change_id` | `string` |
| `appid` | `int64` |
| `task` | `string` |
| `review_text` | `string` |
| `review_passage_text` | `string` |
| `change_text` | `string` |
| `change_context` | `string` |
| `title` | `string` |
| `heading_path` | `list<item: string>` |
| `review_char_start` | `int64` |
| `review_char_end` | `int64` |
| `change_char_start` | `int64` |
| `change_char_end` | `int64` |
| `split` | `string` |
| `cross_split_duplicate` | `bool` |
| `language_warning` | `bool` |

## labeled_pairs

Consistent adjudicated labels, excluding cross-split duplicate leakage.

| Field | Arrow type |
| --- | --- |
| `candidate_id` | `string` |
| `review_revision_id` | `string` |
| `change_id` | `string` |
| `appid` | `int64` |
| `task` | `string` |
| `review_text` | `string` |
| `review_passage_text` | `string` |
| `change_text` | `string` |
| `change_context` | `string` |
| `title` | `string` |
| `heading_path` | `list<item: string>` |
| `review_char_start` | `int64` |
| `review_char_end` | `int64` |
| `change_char_start` | `int64` |
| `change_char_end` | `int64` |
| `split` | `string` |
| `cross_split_duplicate` | `bool` |
| `language_warning` | `bool` |
| `annotation_id` | `string` |
| `relevance` | `string` |
| `sentiment` | `string` |
| `fix_status` | `string` |

## llm_annotations

Validated machine decisions, evidence, model/run/prompt provenance, rationale and self-reported confidence. No human adjudication.

| Field | Arrow type |
| --- | --- |
| `annotation_id` | `string` |
| `candidate_id` | `string` |
| `annotator_id` | `string` |
| `label_source` | `string` |
| `adjudicated` | `bool` |
| `created_at` | `timestamp[us, tz=UTC]` |
| `relevance` | `string` |
| `sentiment` | `string` |
| `fix_status` | `string` |
| `review_evidence_start` | `int64` |
| `review_evidence_end` | `int64` |
| `review_evidence_text` | `string` |
| `change_evidence_start` | `int64` |
| `change_evidence_end` | `int64` |
| `change_evidence_text` | `string` |
| `supersedes` | `list<item: string>` |
| `model_name` | `string` |
| `run_id` | `string` |
| `job_id` | `string` |
| `prompt_version` | `string` |
| `dataset_id` | `string` |
| `rationale` | `string` |
| `confidence` | `double` |

## silver_pairs

Machine-labeled pairs for explicit weak supervision. Uncertain/conflicting decisions and cross-split duplicates excluded; human gold remains separate.

| Field | Arrow type |
| --- | --- |
| `candidate_id` | `string` |
| `review_revision_id` | `string` |
| `change_id` | `string` |
| `appid` | `int64` |
| `task` | `string` |
| `review_text` | `string` |
| `review_passage_text` | `string` |
| `change_text` | `string` |
| `change_context` | `string` |
| `title` | `string` |
| `heading_path` | `list<item: string>` |
| `review_char_start` | `int64` |
| `review_char_end` | `int64` |
| `change_char_start` | `int64` |
| `change_char_end` | `int64` |
| `split` | `string` |
| `cross_split_duplicate` | `bool` |
| `language_warning` | `bool` |
| `annotation_id` | `string` |
| `relevance` | `string` |
| `sentiment` | `string` |
| `fix_status` | `string` |
| `label_source` | `string` |
| `model_name` | `string` |
| `run_id` | `string` |
| `prompt_version` | `string` |
| `confidence` | `double` |
