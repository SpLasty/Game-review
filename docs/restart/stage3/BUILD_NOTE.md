# Build note — Stage 3 hybrid retrieval

| Rung | Feature | Acceptance check | Tier | Status |
| --- | --- | --- | --- | --- |
| F0 | Stage 2 loader → candidate-free audit artifact | `uv run --all-extras pytest tests/relevance_v1/test_stage3.py -q` | MUST | ✅ |
| F1 | Independent BM25, entity/aspect and dense ranks with RRF | Fixture tests plus full dense run | MUST | ✅ |
| F2 | Versioned Parquet outputs, hard-candidate pool, budgets and diagnostics | Full Stage 2 snapshot retrieval | MUST | ✅ |
| F3 | Full-list audit export and useful run report | Full Stage 2 snapshot retrieval | MUST | ✅ |

## Run record

- Full hybrid retrieval on Stage 2 `rv2-d52a3f9f1a3de2fe80aa098f`: dataset `rv3-cef79b660029d7d5eb703567`, exit 0; 62,548 candidates, 3,646 unlabelled hard-case rows, and 45 independent full-list packets.
- Dense model: `intfloat/multilingual-e5-small@614241f622f53c4eeff9890bdc4f31cfecc418b3`. Dense retrieval added 34,566 pairs absent from BM25 at budget 100; no pair has been relevance-verified.
- Full repository suite: **75 passed**. Stage 3 fixture suite: **5 passed**. Ruff check, Ruff format, and `git diff --check`: pass.
- Offline lexical/entity run remains available as a separate smoke artifact `rv3-b823a42f5884e56edca26a34`; it has no dense results and is not the canonical hybrid run.

## Deferred

- Independent full-list audit judgments are not generated here; Stage 3 exports candidate-free review packets for a later independent reviewer/LLM.

