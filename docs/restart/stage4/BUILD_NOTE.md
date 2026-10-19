# Stage 4 build note

Implemented in `src/steam_patch_relevance/stage4/` and exposed as `steam-relevance stage4 export` and `steam-relevance stage4 import`.

Validation performed:

- Stage 4 fixture tests cover exact quote rejection, category 3 temporal/evidence rules, abstention, audit privacy from retrieval metadata, numbered full lists, prompt-hash provenance, deterministic stratified sampling, held-out-game diagnostic wording, and immutable completed-run reimport.
- The bounded pilot exported 24 candidate jobs and six audit jobs (348 numbered change entries across the six prompts).
- All 30 responses imported; zero unanswered jobs, zero validation errors, and zero fabricated/unresolvable quote spans.
- The CLI report says the sample is **not ready for fine-tuning**. No training code ran.

Focused checks: **9 Stage 4 tests passed**. The complete repository suite passed: **84 tests**. Ruff passed for `src/steam_patch_relevance/` and `tests/relevance_v1/`; `git diff --check` passed. No network collection or model training was run.
