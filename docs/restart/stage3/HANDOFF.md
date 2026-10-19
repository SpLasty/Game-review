# Stage 3 handoff — hybrid patch/review candidate retrieval

## Completed implementation

Stage 3 reads the frozen Stage 2 dataset and ranks each verified atomic change against same-game review claims in configurable patch-centered windows. It independently runs Okapi BM25, multilingual dense retrieval, and per-game entity/aspect retrieval, then fuses their union with reciprocal-rank fusion. It keeps component scores/ranks, overlapping patch memberships, unlabelled hard-case candidates, and a candidate-free full-list audit sample. There are no relevance labels, inferred negatives, recall estimates, or model training outputs.

The canonical dense run is `rv3-cef79b660029d7d5eb703567`, derived from Stage 2 `rv2-d52a3f9f1a3de2fe80aa098f`. The full [diagnostic report](../../../reports/relevance_v1/stage3/rv3-cef79b660029d7d5eb703567/report.md) and git-ignored data artifact are available. The dense model is `intfloat/multilingual-e5-small` at immutable Hugging Face revision `614241f622f53c4eeff9890bdc4f31cfecc418b3`; embeddings are cached by model revision and prefixed content hash.

## Full-snapshot result

- 397 verified changes from 9 review-covered patch episodes in Counter-Strike 2, Dota 2, and HELLDIVERS 2; 77,220 patch-scoped review claims and 3,656,475 possible change/claim pairs.
- BM25 ranked 22,134 pairs. Dense ranked 39,700, including **34,566 pairs absent from BM25** at the same maximum budget. Entity/aspect ranked 13,132, including **6,230 absent from BM25**. The union contains 62,548 pairs, of which 40,414 are absent from BM25; 34,184 are exclusive to dense among all three methods.
- These are candidate counts, not confirmed matches. The report includes method-exclusive examples: dense retrieves a plausible paraphrase about developers fixing a “crashing issue” for a “Crash fixes” patch entry, alongside weak semantic associations such as “mission failed” for a Super Earth flag-logo fix. Independent verification is still required.
- The unlabelled hard-case pool has 3,646 rows: 2,009 same-entity/different-aspect; 1,856 generic or potentially longstanding feature complaints; 539 terminology confounds; 269 contradictory directional cues; and one same-issue/different-trigger case. Counts can overlap. No same-game competing-patch case was generated from current memberships; that zero is a data-coverage result, not evidence that such confusion does not occur.
- Candidate yield grows from 8,383 at budget 10 to 19,014 at 25, 34,977 at 50, and 62,548 at 100. At 100, the output records 46,418 BM25 hits, 3,616,775 dense-ranked pairs, and 15,185 entity/aspect hits beyond retained lists. This confirms substantial truncation, but no omitted pair has been verified as relevant yet.
- The independent sampler exported 45 full review/full patch-list audit packets from one large episode in each represented game, selected from temporal memberships before retrieval. No audit judgments were created; this is not a recall sample estimate.
- Coverage is narrow: only 9/316 Stage 2 episodes entered retrieval, 53/60 collected window segments are incomplete, and No Man’s Sky has no atomic changes in Stage 2. Retrieval cannot run there until extraction coverage improves.

## Run and inspect

Install the optional model dependency, then run the default-pinned model revision:

```bash
uv sync --locked --all-extras
uv run --all-extras steam-relevance stage3 retrieve \
  --source-dataset rv2-d52a3f9f1a3de2fe80aa098f \
  --budgets 10 25 50 100 --before-days 14 --after-days 14 \
  --dense-revision 614241f622f53c4eeff9890bdc4f31cfecc418b3
```

The manifest records input hashes, model revision, collection/window settings, candidate counts, method truncation, and paths. Outputs include `candidate_pairs.parquet`, `hard_negative_candidates.parquet`, patch/game diagnostics, budget curves, `audit_full_list.jsonl`, and `manifest.json`. The report is under `reports/relevance_v1/stage3/<dataset-id>/`. The embedding cache and data artifacts stay under the ignored `data/relevance_v1/processed/stage3/` tree. In this CPU-only environment, installing Sentence Transformers/PyTorch fetched about 4.2 GB of Python wheels, including CUDA libraries not used for inference; model weights were about 0.56 GB.

For a model-free smoke run, add `--no-dense`; its outputs identify dense retrieval as disabled rather than treating zero dense rows as a negative result.

## Boundary

The next independent audit must compare sampled reviews to each complete patch change list, including matches missing from all three candidate lists. That review belongs to the next stage. Stage 3 ends with retrieval and diagnostic artifacts only; it does not assign any relevance or sentiment label.
