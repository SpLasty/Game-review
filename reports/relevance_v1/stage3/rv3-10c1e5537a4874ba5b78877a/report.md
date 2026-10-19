# Stage 3 candidate retrieval — `rv3-10c1e5537a4874ba5b78877a`

Source Stage 2 dataset: `rv2-d52a3f9f1a3de2fe80aa098f`. No relevance labels or training labels were generated.

## Run scope

- Change-bearing episodes with review-window membership: 9 across 3 games.
- Verified atomic changes used: 397; unverified change rows excluded: 0.
- Eligible claims after temporal/game filtering: 77,220 patch-scoped claims.
- Distinct `(patch, change, claim)` candidates in the high-budget union: 28,364.
- Hard-case candidate rows, all unlabelled: 3,556.
- Candidate-free full-list audit packets: 45 from 3 episodes.

## Method comparison

Each method ranks claims independently per atomic change. BM25 removes generic sentiment-only terms and retains entities/numbers; dense uses multilingual E5 cosine similarity; entity/aspect uses game-scoped aliases and normalized aspect families. The union is fused with reciprocal-rank fusion (`k=60`).

| Method | Ranked pairs at maximum budget | Pair rows absent from BM25 |
| --- | ---: | ---: |
| BM25 | 22,134 | — |
| Dense | 0 | 0 |
| Entity/aspect | 13,132 | 6,230 |
| Hybrid union | 28,364 | 6,230 |

`Pair rows absent from BM25` means the method contributed a candidate BM25 did not rank inside its configured budget. It does not establish relevance. `budget_curves.csv` reports candidate yield and overlap at every configured budget; recall is intentionally blank because no independent relevance reference labels exist.

## Retrieval budget and truncation

Budgets per change per method: `[10, 25, 50, 100]`. The candidate dataset retains the union through `100`. There is no per-review cap. At the maximum budget, the output records 146 BM25, 0 dense, and 86 entity/aspect change queries with ranked results beyond the retained list.
At the maximum budget, the ranked lists omit 46,418 BM25 hits, 0 dense-ranked claim pairs, and 15,185 entity/aspect hits beyond the retained top ranks. Across the eligible contexts, exhaustive change×claim comparison would contain 3,656,475 pairs; the high-budget union retains 28,364. This is measurable budget truncation, but without audit judgments it is not evidence that any omitted pair is relevant. The independent full-list audit packets expose the complete change list to later reviewers so omissions can be found without conditioning on retrieval.

## Patch diagnostics

| Game | Patch | Changes | Eligible claims | Possible pairs | BM25 | Dense | Entity/aspect | Union |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Counter-Strike 2 | Counter-Strike 2 Update (`rv2_patch_2a62b2ccdb4627fbf33a192f`) | 37 | 14,255 | 527,435 | 2,961 | 0 | 1,534 | 3,598 |
| Dota 2 | Dota Plus Update — Spring 2024 (And Dota Labs) (`rv2_patch_03b2afc74199b64632b03c3b`) | 1 | 3,561 | 3,561 | 100 | 0 | 80 | 133 |
| Dota 2 | Gameplay Patch 7.35d And Matchmaking Features (`rv2_patch_7441a4ce5e91ed51e22d0a0d`) | 1 | 7,230 | 7,230 | 100 | 0 | 100 | 183 |
| Dota 2 | 7.39b Gameplay Patch (`rv2_patch_d5e4f3f222c5b34cb9942a48`) | 59 | 8,546 | 504,214 | 2,020 | 0 | 625 | 2,073 |
| Dota 2 | 7.41a Gameplay Patch (`rv2_patch_97d8c447314d0ce84e379fc2`) | 53 | 3,723 | 197,319 | 641 | 0 | 233 | 641 |
| Dota 2 | 7.41c Gameplay Patch (`rv2_patch_fa8dc0b7486bc1d75d8a8f48`) | 58 | 7,540 | 437,320 | 1,082 | 0 | 275 | 1,084 |
| Dota 2 | Dota 2 Update - 7/1/2026 (`rv2_patch_1d2cff01840bf8f1810c9f13`) | 69 | 7,379 | 509,151 | 3,373 | 0 | 762 | 3,401 |
| HELLDIVERS 2 | Patch Notes 01.002.200 (`rv2_patch_1fe8203f3360233a000c29e1`) | 51 | 13,459 | 686,409 | 5,057 | 0 | 3,993 | 7,089 |
| HELLDIVERS 2 | Devoid of Liberty: 7.1.0 (`rv2_patch_003aeb5de20bb6da37b1c2c4`) | 68 | 11,527 | 783,836 | 6,800 | 0 | 5,530 | 10,162 |

## Diagnostic candidate examples

No dense-only examples were available in this run.
## Independent full-list audit

The reproducible candidate-free sampler selected up to 5 full reviews per temporal segment from one change-bearing episode per game. It exports the original full review beside the complete structured patch change list in `audit_full_list.jsonl`. Sampling occurs from Stage 2 review-window memberships before ranking; audit rows contain no candidate IDs, component ranks, or labels. This is a diagnostic sample, not a corpus-wide recall estimate.

The current Stage 2 snapshot has no extracted atomic changes for No Man’s Sky, so it cannot contribute a full-list audit episode. Its source/patch availability remains in Stage 2 coverage; candidate retrieval is blocked by the absence of atomic changes, not by a zero-relevance finding.

## Data limitations

- Stage 2 patch-window collection is incomplete for many episodes. Retrieval uses the rows available and carries per-window completeness in diagnostics and audit packets.
- Stage 2 entity/aspect extraction is sparse and English-heavy. Dense multilingual retrieval and lexical retrieval are independent candidates, not claims that the extractor found every entity.
- BM25 tokenization is simple Unicode word tokenization; languages without whitespace token boundaries may receive weaker lexical retrieval.
- Similarity scores/ranks express candidate order only. Steam Recommended votes and claim polarity are not feature-level sentiment labels.

## Outputs

- `candidate_pairs.parquet`: high-budget per-change method union, component ranks/scores, RRF rank, temporal provenance.
- `hard_negative_candidates.parquet`: heuristic confounders retained as unlabelled candidates for later verification.
- `budget_curves.csv`, `patch_diagnostics.parquet`, `game_diagnostics.csv`, `diagnostics.json`.
- `audit_full_list.jsonl`: independent, candidate-free full-review/full-change packets.
- `manifest.json`: source hashes, configuration, model/cache version, counts, and truncation.
