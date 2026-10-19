# Stage 3 implementation plan and completion criteria

1. **Freeze the input boundary.** Read a complete selected Stage 2 snapshot by ID; validate its manifest and source tables. Keep candidate IDs, storage, module paths, and CLI under `rv3_`/`stage3`, without importing retired candidate code.
2. **Build independent retrieval signals.** Implement BM25, multilingual Sentence Transformers embeddings with content/model-revision caching, and game-scoped entity/aspect ranking. Preserve each score/rank and use deterministic ties.
3. **Combine without premature filtering.** Union each component's configurable top-budget list; retain multiple reviews per change and multiple changes per review; use RRF; record exact query and pair truncation.
4. **Create later-verification pools.** Tag hard confounder candidates without converting rule outputs into negative labels. Preserve competing patch memberships.
5. **Create independent audit packets.** Sample full reviews from temporal windows before ranking and include the full structured patch list. Keep the audit file free of candidate ranks/IDs/labels.
6. **Validate and hand off.** Fixture-test algorithm boundaries and overlapping windows, run a bounded offline/full-snapshot smoke, emit per-game/patch diagnostics and candidate-yield curves, document source limitations, and stop before relevance labeling/training.

## Completion status

- **Completed:** Fresh Stage 3 namespace and CLI; independent BM25, multilingual dense E5, and game-scoped entity/aspect ranks; RRF; configurable windows/budgets; unlabelled hard-case pool; deterministic candidate-free audit sampler; fixture tests; full hybrid run `rv3-cef79b660029d7d5eb703567`.
- **Validated:** Full Stage 2 input snapshot processed with the dense model pinned to `614241f622f53c4eeff9890bdc4f31cfecc418b3`; 75 repository tests pass; Ruff and diff checks pass.
- **Acceptance boundary:** Do not claim recall or mark hard cases as negative until a separate independent audit has reviewed full-list packets. Do not produce Stage 4 labels or training data in this stage.
