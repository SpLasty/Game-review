# Stage 2 data contracts

All tables are Parquet with Zstandard compression and live in a dataset-ID directory under `data/relevance_v1/processed/stage2/`. IDs use the `rv2_` namespace. Source text is Unicode and character offsets are zero-based, half-open Python string offsets into the named Stage 1 source revision.

| Table | Row grain | Contract and cautions |
| --- | --- | --- |
| `announcement_classifications` | One Stage 1 announcement revision | Preserves original title/body, publication metadata, feed/source metadata, source URL, linked URLs, truncation and body fields; `categories` is multi-label. `patch_eligible` is conservative rule-based triage. Nonofficial feeds remain classified but are not patch episodes. |
| `patch_changes` | One structured list-item change clause | `change_id`, `patch_id`, source announcement/revision/hash, exact raw source slice and offsets, rendered change text, heading hierarchy, entity and alternative entity candidates, aspect/action/direction, numeric values/delta, developer status, bug symptom/trigger, confidence, method/version and quality flags. Missing or ambiguous entity/aspect is flagged, never silently repaired. |
| `review_claims` | One review sentence or contrast clause for one revision | `claim_id`, review/revision/logical IDs, source payload hash, language metadata, timestamps, exact original claim text and offsets, entity/aspect/opinion, nullable polarity, temporal cues, negation/uncertainty, confidence, and `patch_specificity=not_assigned`. Join `review_revision_id` to Stage 1 `review_revisions.parquet` for the complete original review. |
| `game_terminology` | One term/alias resource entry per game | Per-game resource derived from official patch-note entities/hierarchy and repeated review name forms. `is_entity_matchable` distinguishes patch-backed terms used by claim extraction from review-only vocabulary candidates. Single-token aliases match case-sensitively to reduce ordinary-word false matches. It is deliberately not a global mechanics ontology. |
| `patch_episodes` | One rule-eligible developer announcement | Preserves announcement and publication/release timestamps. When no release time is verified, announcement publication time is the explicitly unverified temporal anchor. |
| `patch_review_windows` | One collected window segment per patch | Carries start/end, Steam-reported counts, coverage fraction, collection status, and issues. A segment is a temporal observation interval, not a relevance judgment. |
| `review_window_memberships` | One source review revision in one collected patch-window segment | Re-namespaces the source patch ID and preserves segment bounds and membership rule. Multiple rows for the same review are expected when windows overlap. `membership_semantics` is always temporal-only. |
| `patch_episode_overlaps` | One overlapping pair of same-game patch time windows | Stores intersection bounds and explicitly states temporal-only interpretation. |
| `change_temporal_ambiguities` | Same-entity changes across distinct episodes with overlapping windows | Records a possible temporal ambiguity; it does not resolve attribution or create a review/change pair. |
| `qa_sample` | One deterministically selected change or claim audit example | Stores stable sample ID/stratum/seed, source excerpt, extracted fields, selection rule, and manual-review status. |

## Identifier and provenance rules

- `rv2_patch_*` IDs identify announcement revisions in this extraction dataset; they do not claim verified build identity.
- `rv2_change_*` IDs are content/source-span stable within the Stage 2 extractor version.
- `rv2_claim_*` IDs include review revision, exact span, and claim text, so edited review revisions remain distinct.
- Announcement spans slice `body_original` exactly. `source_span_raw` must equal that source slice; markup is retained in this field. `change_text` is the visible, normalized text derived from the span.
- Review spans slice `review_text_original` exactly, including original Unicode and punctuation.
- Steam `voted_up` is absent from feature polarity. Stage 2 does not infer sentiment about a change or connect a claim to a patch.

## Known extraction limits

The deterministic change extractor is intentionally restricted to structured Steam list items with explicit action language. Prose descriptions, external changelog pages, implicit actions, and game-specific phrases without an explicit entity remain unextracted or flagged. Broad issue summaries and ambiguous bug syntax are flagged rather than treated as fully structured. Aspect/polarity lexicons are English-heavy; the original language and null uncertainty are retained instead of machine translation. Time windows are based on Stage 1's collection snapshot and can be incomplete.
