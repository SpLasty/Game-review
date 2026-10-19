# Stage 3 retrieval architecture

Stage 3 ranks possible links between one verified atomic change and one review claim. It consumes only the selected Stage 2 Parquet snapshot plus Stage 1 full review text for the separate audit export. It does not import Stage 1 collectors or Stage 2 extractors, and it does not read legacy candidate/label data.

```text
Stage 2 changes ─┐
Stage 2 claims ──┼─ same app + configured time-window membership ─┬─ BM25 ranks
Stage 2 aliases ─┤                                                  ├─ multilingual dense ranks
Stage 2 windows ─┘                                                  └─ entity/aspect ranks
                                                                         │
                                                independent lists ───────┤
                                                                         ├─ union at configured budget
                                                                         └─ RRF fused ranking
                                                                               │
                                                      candidates / hard-case pool / diagnostics

Stage 2 memberships ── seeded review sampler ── Stage 1 full review text
Stage 2 full change lists ─────────────────────┘
                └─ candidate-free full-list audit packets (separate artifact)
```

## Retrieval decisions

- **Eligibility:** A claim enters an episode only through the same-game Stage 2 membership and configurable anchor-relative bounds (default 14 days before through 14 days after). Membership remains temporal evidence only. Pre-patch claims are kept for retrospective issue feedback. A claim in overlapping episodes can be ranked for each episode and records its other episode memberships and competing same-entity/aspect episode IDs.
- **BM25:** A transparent Okapi implementation (`k1=1.5`, `b=0.75`) ranks content terms, identifiers, numbers, and local heading context. Generic sentiment-only words are removed. One shared content token can rank a claim; there is no overlap threshold. Unicode word tokenization keeps numbers, but languages without whitespace token boundaries may have weaker lexical results.
- **Dense:** Sentence Transformers encodes changes and claims with pretrained `intfloat/multilingual-e5-small`, pinned by default to immutable revision `614241f622f53c4eeff9890bdc4f31cfecc418b3`. Changes use `query: ` and claims use `passage: `; normalized vectors are compared by dot product, equivalent to cosine similarity. The model card lists 94 supported languages. The maintained Sentence Transformers API documents embedding similarity and cosine scoring ([model card](https://huggingface.co/intfloat/multilingual-e5-small), [similarity documentation](https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html)). The model remains an optional `retrieval` extra. Cache keys include the immutable model revision and prefixed-content hash.
- **Entity/aspect:** Stage 2 terminology is loaded independently per Steam app ID. Exact entities, game aliases, and mentions in the text are resolved to that game's own terms. A small set of aspect families supports wording variants such as `purchase price`/`cost` while keeping the candidate scoped to the same game. Entity and aspect scores remain separate.
- **Fusion:** The three independent lists are unioned and sorted with reciprocal-rank fusion: `sum(1 / (60 + component_rank))`. Component ranks and raw scores are retained. There is no similarity threshold and no per-review cap.
- **Budget:** Defaults are 10, 25, 50, and 100 claims per change per method. The maximum budget defines the candidate-pair artifact; the manifest and patch report count change queries and pair rows omitted beyond each method's maximum. Budgets are CLI-configurable. Curves describe pool growth, not recall, until an independent reference set exists.
- **Hard cases:** Rule-generated confounders are copied into `hard_negative_candidates.parquet`, always with `hard_case_basis` and no relevance label. Categories include same entity/different aspect, generic persistent symptoms, competing overlapping patch windows, terminology confounds, different bug triggers, and contradictory directional cues. A rule does not make a pair negative.
- **Independent audit:** Before ranking, Stage 3 selects one change-bearing patch per represented game, then hash-ranks reviews within each available temporal segment and language. The JSONL packet contains the complete original review and the entire patch change list, but no candidate IDs/ranks/labels. This supports later full-list review of retrieval omissions without candidate-membership bias. It is a diagnostic sample, not a corpus-wide recall estimate.

## Module and artifact boundary

```text
src/steam_patch_relevance/stage3/
  bm25.py       Unicode tokenizer and Okapi BM25 ranking
  dense.py      Sentence Transformers adapter, normalized cosine, content/model cache
  entity.py     per-game aliases and aspect-family ranking
  pipeline.py   time/game eligibility, independent lists, RRF, audit export, diagnostics

data/relevance_v1/processed/stage3/<rv3-dataset-id>/
  candidate_pairs.parquet
  hard_negative_candidates.parquet
  patch_diagnostics.parquet
  game_diagnostics.csv
  budget_curves.csv
  diagnostics.json
  audit_full_list.jsonl
  manifest.json

reports/relevance_v1/stage3/<rv3-dataset-id>/report.md
```

Dense embeddings are cached beneath `data/relevance_v1/processed/stage3/cache/<model-revision>/`. All Stage 3 data/cache paths remain git-ignored under `data/relevance_v1/`; the human-readable report and documentation are repository files.

## CLI

```bash
# Full hybrid run after installing the optional retrieval extra and model weights.
uv run --all-extras steam-relevance stage3 retrieve \
  --source-dataset rv2-d52a3f9f1a3de2fe80aa098f \
  --budgets 10 25 50 100 --before-days 14 --after-days 14 \
  --dense-revision 614241f622f53c4eeff9890bdc4f31cfecc418b3

# Offline BM25 + entity/aspect smoke run (does not claim to have run dense retrieval).
uv run --all-extras steam-relevance stage3 retrieve \
  --source-dataset rv2-d52a3f9f1a3de2fe80aa098f --no-dense
```

Use `--patch-id` or `--game-id` repeatedly to bound a run, and `--audit-per-segment`/`--audit-seed` to set the independent sample. The manifest captures every option and source table hash.
