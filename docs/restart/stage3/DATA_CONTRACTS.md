# Stage 3 data contracts

Stage 3 uses schema `3.0.0` and dataset IDs `rv3-<config-and-source fingerprint>`. Candidate IDs use the new `rv3_candidate_` prefix and are stable for `(schema, Stage 2 dataset, patch, change, claim)`. The current implementation reads Stage 2 dataset `rv2-d52a3f9f1a3de2fe80aa098f`; it does not mutate or reserialize Stage 2 tables.

| Artifact | Grain | Contract |
| --- | --- | --- |
| `candidate_pairs.parquet` | One `(patch_id, change_id, claim_id)` present in at least one retained component list | Keeps same-game/window eligibility, change and claim IDs/text summaries, Stage 2 temporal segments, other episode memberships, competing same-entity/aspect episode IDs, each component's rank and score, dense model version, RRF score/rank, and retrieval method list. The file is the union through the configured maximum budget. It contains no relevance label. |
| `hard_negative_candidates.parquet` | One candidate pair with one or more heuristic confounder types | Contains the same component provenance plus `hard_case_types` and an explicit unlabelled basis. It is a review pool, not a negative dataset. |
| `patch_diagnostics.parquet` | One Stage 2 patch episode | Covers all patch episodes, including ineligible episodes and their status. Reports Stage 2/verified change counts, configured-window membership and claim counts, exhaustive possible pair count for eligible episodes, per-method ranks, exact budget omissions, and window completeness. |
| `game_diagnostics.csv` | One game | Stage 2 episode counts, episodes with window memberships/verified changes, retrieval episode count, candidate pool sizes, and status. Games without extracted changes remain visible with zero retrieval rows. |
| `budget_curves.csv` | One scope (`overall`, `game`, or `patch`) and per-change/per-method budget | Method counts and union counts at each configured budget. `reference_recall` remains null because no independent relevance reference is created in Stage 3. |
| `audit_full_list.jsonl` | One independently sampled review revision in one patch window | Original complete review, complete structured patch change list, patch/source/time/window context, deterministic sample provenance, and reviewer prompt. It has no candidate IDs, component ranks, or labels. |
| `diagnostics.json` | One run summary | Counts, method-unique examples, and hard-case category counts. Examples are retrieval observations only. |
| `manifest.json` | One run | Source Stage 2 and Stage 1 identities/hashes, Stage 3 schema/retriever/code version, full configuration, model revision/cache location, counts, hard-case counts, coverage, and output paths. |

## Scoring and rank meanings

- BM25 is a lexical ranking over the eligible claims for one patch episode and one atomic change. Sentiment-only vocabulary does not create BM25 matches. Numeric and game-specific terms remain available.
- Dense score is cosine similarity between a change query vector and claim passage vectors. Model revision is stored per candidate and in the run manifest. Cache content uses both revision and prefixed-text content hashes.
- Entity/aspect score is `2 × entity_match_score + aspect_match_score`. Entity and aspect component values are retained separately, and a pair can enter from an aspect match without an entity match. All vocabulary resolution is app-specific.
- `rrf_score` adds `1/(60 + rank)` for every method where the pair appears. `fused_rank` is scoped to a specific change, within the union retained at the maximum component budget.
- A null component rank/score means that component did not return the pair within its configured budget. It is not a negative judgment.

## Temporal and identity rules

- Window bounds use membership `created_unix` relative to membership `anchor_unix` and are half-open: `[anchor - before_days, anchor + after_days)`. The default is `[-14d,+14d)`.
- The same claim may appear once for each eligible patch. That is intentional. `window_segments`, `other_window_patch_ids`, and `competing_feature_patch_ids` preserve temporal ambiguity rather than choosing a patch.
- Stage 2 `source_span_verified=true` changes are eligible for retrieval. Unverified changes are not used as change queries, but are preserved in the complete Stage 3 audit list when that episode is sampled.
- Stage 1 review recommendation is not present in candidate sentiment fields. Claim polarity is carried as context only and is not an opinion label for the patch change.

## Limits and interpretation

The current Stage 2 snapshot contains 20 episodes with collected memberships but only nine with verified changes and claim rows; No Man's Sky has no atomic changes. Many review windows are partial. Method pool counts and budget omissions are measurable, but omitted candidates cannot be called missed positives without full-list audit judgments. Stage 3 produces no relevance labels, no training pairs, and no cross-encoder scores.
