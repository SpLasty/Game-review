# Stage 3 candidate retrieval — `rv3-cef79b660029d7d5eb703567`

Source Stage 2 dataset: `rv2-d52a3f9f1a3de2fe80aa098f`. No relevance labels or training labels were generated.

## Run scope

- Change-bearing episodes with review-window membership: 9 across 3 games.
- Verified atomic changes used: 397; unverified change rows excluded: 0.
- Eligible claims after temporal/game filtering: 77,220 patch-scoped claims.
- Distinct `(patch, change, claim)` candidates in the high-budget union: 62,548.
- Hard-case candidate rows, all unlabelled: 3,646.
- Candidate-free full-list audit packets: 45 from 3 episodes.

## Method comparison

Each method ranks claims independently per atomic change. BM25 removes generic sentiment-only terms and retains entities/numbers; dense uses multilingual E5 cosine similarity when enabled; entity/aspect uses game-scoped aliases and normalized aspect families. The union is fused with reciprocal-rank fusion (`k=60`).

| Method | Ranked pairs at maximum budget | Pair rows absent from BM25 |
| --- | ---: | ---: |
| BM25 | 22,134 | — |
| Dense | 39,700 | 34,566 |
| Entity/aspect | 13,132 | 6,230 |
| Hybrid union | 62,548 | 40,414 |

Dense retrieval status: `completed` (model `intfloat/multilingual-e5-small@614241f622f53c4eeff9890bdc4f31cfecc418b3`). A zero dense candidate count means no dense output was produced when the backend is disabled; it does not mean dense retrieved no candidates.

`Pair rows absent from BM25` means the method contributed a candidate BM25 did not rank inside its configured budget. It does not establish relevance. `budget_curves.csv` reports candidate yield and overlap at every configured budget; recall is intentionally blank because no independent relevance reference labels exist.

## Retrieval budget and truncation

Budgets per change per method: `[10, 25, 50, 100]`. The candidate dataset retains the union through `100`. There is no per-review cap. At the maximum budget, the output records 146 BM25, 397 dense, and 86 entity/aspect change queries with ranked results beyond the retained list.
At the maximum budget, the ranked lists omit 46,418 BM25 hits, 3,616,775 dense-ranked claim pairs, and 15,185 entity/aspect hits beyond the retained top ranks. Across the eligible contexts, exhaustive change×claim comparison would contain 3,656,475 pairs; the high-budget union retains 62,548. This is measurable budget truncation, but without audit judgments it is not evidence that any omitted pair is relevant. The independent full-list audit packets expose the complete change list to later reviewers so omissions can be found without conditioning on retrieval.

## Budget curve

Overall candidate yield as the per-change, per-method budget grows. This is not a recall curve because no verified relevance reference set exists.

| Budget per change/method | BM25 pairs | Dense pairs | Entity/aspect pairs | Hybrid union |
| ---: | ---: | ---: | ---: | ---: |
| 10 | 3,793 | 3,970 | 2,995 | 8,383 |
| 25 | 8,241 | 9,925 | 5,239 | 19,014 |
| 50 | 13,932 | 19,850 | 8,369 | 34,977 |
| 100 | 22,134 | 39,700 | 13,132 | 62,548 |

## Hard-case candidate pool

These are heuristic confounders for later verification. Categories can overlap, and none is a negative label.

| Potential confounder | Candidate rows |
| --- | ---: |
| Same entity, different aspect | 2,009 |
| Same feature, generic/longstanding complaint | 1,856 |
| Same issue type, different trigger | 1 |
| Same game, competing patch/overlap | 0 |
| Same terminology, different mechanic | 539 |
| Contradictory directional cue | 269 |

## Patch diagnostics

| Game | Patch | Changes | Eligible claims | Possible pairs | BM25 | Dense | Entity/aspect | Union |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Counter-Strike 2 | Counter-Strike 2 Update (`rv2_patch_2a62b2ccdb4627fbf33a192f`) | 37 | 14,255 | 527,435 | 2,961 | 3,700 | 1,534 | 6,933 |
| Dota 2 | Dota Plus Update — Spring 2024 (And Dota Labs) (`rv2_patch_03b2afc74199b64632b03c3b`) | 1 | 3,561 | 3,561 | 100 | 100 | 80 | 205 |
| Dota 2 | Gameplay Patch 7.35d And Matchmaking Features (`rv2_patch_7441a4ce5e91ed51e22d0a0d`) | 1 | 7,230 | 7,230 | 100 | 100 | 100 | 245 |
| Dota 2 | 7.39b Gameplay Patch (`rv2_patch_d5e4f3f222c5b34cb9942a48`) | 59 | 8,546 | 504,214 | 2,020 | 5,900 | 625 | 7,560 |
| Dota 2 | 7.41a Gameplay Patch (`rv2_patch_97d8c447314d0ce84e379fc2`) | 53 | 3,723 | 197,319 | 641 | 5,300 | 233 | 5,768 |
| Dota 2 | 7.41c Gameplay Patch (`rv2_patch_fa8dc0b7486bc1d75d8a8f48`) | 58 | 7,540 | 437,320 | 1,082 | 5,800 | 275 | 6,688 |
| Dota 2 | Dota 2 Update - 7/1/2026 (`rv2_patch_1d2cff01840bf8f1810c9f13`) | 69 | 7,379 | 509,151 | 3,373 | 6,900 | 762 | 9,673 |
| HELLDIVERS 2 | Patch Notes 01.002.200 (`rv2_patch_1fe8203f3360233a000c29e1`) | 51 | 13,459 | 686,409 | 5,057 | 5,100 | 3,993 | 10,844 |
| HELLDIVERS 2 | Devoid of Liberty: 7.1.0 (`rv2_patch_003aeb5de20bb6da37b1c2c4`) | 68 | 11,527 | 783,836 | 6,800 | 6,800 | 5,530 | 14,632 |

## Diagnostic candidate examples

These examples are unique to a method among the three retained ranked lists. They illustrate retrieval differences and are not verified positives.

### bm25 unique candidate — example 1

Game/patch: HELLDIVERS 2 — Devoid of Liberty: 7.1.0 (`rv2_patch_003aeb5de20bb6da37b1c2c4`). BM25 rank 1, BM25 score 26.4327; absent from the other method lists at the configured budget.

Change: Fixed HDR UI brightness setting not saving on PC

Review claim: this game's ui is fun,

This is a retrieval diagnostic, not a relevance judgment.

### bm25 unique candidate — example 2

Game/patch: HELLDIVERS 2 — Devoid of Liberty: 7.1.0 (`rv2_patch_003aeb5de20bb6da37b1c2c4`). BM25 rank 2, BM25 score 21.6759; absent from the other method lists at the configured budget.

Change: Fixed HDR UI brightness setting not saving on PC

Review claim: good mechanics, UI and good balance in the different leves

This is a retrieval diagnostic, not a relevance judgment.

### bm25 unique candidate — example 3

Game/patch: HELLDIVERS 2 — Devoid of Liberty: 7.1.0 (`rv2_patch_003aeb5de20bb6da37b1c2c4`). BM25 rank 1, BM25 score 20.7685; absent from the other method lists at the configured budget.

Change: Every super destroyer will have its own leaderboard separate from everyone else. Anyone who is on your super destroyer can play a game and get added to the leaderboard. One entry per player, so one player cannot occupy multiple highscores.

Review claim: I cannot recommend anyone else waste their money on the game.

This is a retrieval diagnostic, not a relevance judgment.

### dense unique candidate — example 1

Game/patch: HELLDIVERS 2 — Devoid of Liberty: 7.1.0 (`rv2_patch_003aeb5de20bb6da37b1c2c4`). dense rank 1, cosine 0.8990; absent from the other method lists at the configured budget.

Change: Fixed an issue with Super Earth flag not showing the Super Earth logo

Review claim: mission failed.

This is a retrieval diagnostic, not a relevance judgment.

### dense unique candidate — example 2

Game/patch: HELLDIVERS 2 — Patch Notes 01.002.200 (`rv2_patch_1fe8203f3360233a000c29e1`). dense rank 2, cosine 0.8904; absent from the other method lists at the configured budget.

Change: Crash fixes

Review claim: Thanks for the dev team to fix the crashing issue.

This is a retrieval diagnostic, not a relevance judgment.

### dense unique candidate — example 3

Game/patch: HELLDIVERS 2 — Patch Notes 01.002.200 (`rv2_patch_1fe8203f3360233a000c29e1`). dense rank 1, cosine 0.8864; absent from the other method lists at the configured budget.

Change: Fixed a rare crash that happened during game shut down on PC

Review claim: Thanks for the dev team to fix the crashing issue.

This is a retrieval diagnostic, not a relevance judgment.

### entity_aspect unique candidate — example 1

Game/patch: HELLDIVERS 2 — Patch Notes 01.002.200 (`rv2_patch_1fe8203f3360233a000c29e1`). entity/aspect rank 1, entity/aspect score 3.0000; absent from the other method lists at the configured budget.

Change: Fixed Helldivers sliding around on the ground after exiting the ragdoll state (despite it being the year of the snake and despite us trying to fix this previously)

Review claim: - Helldivers will sometimes have invisible limbs, sometime their map marker is broken, sometimes theyre completely invisible AND the map marker is broken.

This is a retrieval diagnostic, not a relevance judgment.

### entity_aspect unique candidate — example 2

Game/patch: HELLDIVERS 2 — Devoid of Liberty: 7.1.0 (`rv2_patch_003aeb5de20bb6da37b1c2c4`). entity/aspect rank 1, entity/aspect score 3.0000; absent from the other method lists at the configured budget.

Change: Reduced the start time between waves from 60 seconds to 42 seconds (the time between waves at the start of the mission).

Review claim: If you want to fully upgrade multiple weapons, you're looking at a ridiculous amount of time doing the same content over and over again just to finish leveling them.

This is a retrieval diagnostic, not a relevance judgment.

### entity_aspect unique candidate — example 3

Game/patch: HELLDIVERS 2 — Devoid of Liberty: 7.1.0 (`rv2_patch_003aeb5de20bb6da37b1c2c4`). entity/aspect rank 1, entity/aspect score 3.0000; absent from the other method lists at the configured budget.

Change: Players can no longer get stuck in a state where they are unable to be reinforced even after another player throws a reinforcement stratagem or the whole squad dies. This was rare but could happen under poor network conditions

Review claim: Joined in during war for Cyberstan
-had no equipments
-dived in anyways
-died several times
-was planning to quit
-other divers lent their weapons
-started enjoing it
-took a break
-started playing again
-got better and unlocked more gear
-kept diving into super heldives
-unlocked even more stuff
-met begining diver
-lent them my weapons
-started to have fun even with randos
The cycle of democary repeats.

This is a retrieval diagnostic, not a relevance judgment.

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
