# Build Note — Patch-Scoped Labeling Pilot

| Rung | Feature | Acceptance check (one command) | Tier | Status |
|------|---------|-------------------------------|------|--------|
| F0 | Add patch-filtered, change-balanced LLM job export with an auditable lexical sidecar | `uv run --all-extras steam-insights llm-annotations-export --patch-id 9593c96b043f323204b6db3437497a9b4972e5986d637dd7e21ce7b908946839 --sample-size 200 --split train --exclude-annotated --output data/annotations/llm_jobs/sot-381-pilot` | MUST | ✅ |
| F1 | Label/import the frozen pilot and publish refreshed silver data | `uv run --all-extras steam-insights prepare-data` | MUST | ✅ |
| F2 | Summarize labeled lexical-rank sample and update the handoff | `python scripts/data/report_patch_pilot.py --job data/annotations/llm_jobs/sot-381-pilot --responses data/annotations/llm_jobs/sot-381-pilot/responses` | MUST | ✅ |
| F3 | Add embedding retrieval, noncandidate recall audit, and baseline model | Deferred: requires a separate model/dependency decision and broader labels | DEFERRED | ⬜ |

## Run record

- Frozen input snapshot: `5c8a356cb9aa33235617e46eb2b6597db40ed77ee1967ed71be2ec0b65f633c7`.
- Pilot job ID: `e5be0734ba84a936f015314014b153510ef9297056e592205a6ee09ccd2e733c`; 200 fresh train examples from a 348-pair lexical pool, with two earlier labeled IDs excluded.
- LLM run: model label `GPT-6`, run ID `codex-gpt6-sot381-pilot-2026-10-17`; imported all 200 responses (198 irrelevant, 2 uncertain, 0 relevant). The 198 irrelevant responses shared a generic rationale and were not individually checked against all full announcement context; the zero-relevant result is provisional until those pairs are audited individually.
- Refreshed snapshot: `5eb4842f3daaf8125a9daaaeef18c9e9f0c304dcd8703c5b100a5cfd39c77c9f`; 300 machine decisions, 297 silver rows, 0 human rows; all 196 publication checks passed.
- Descriptive pilot report: `data/annotations/llm_jobs/sot-381-pilot/retrieval_audit_report.md`. It records no relevant examples among lexical ranks 1–2, but the label result needs per-example semantic audit before it can guide retrieval tuning. It does not measure recall or unbiased corpus precision.
- Verification: `python -m unittest discover -s tests -p 'test_pipeline_*.py'` passed 26 tests; Ruff lint and format checks passed for changed Python files.
- Independent assumption sweep is unavailable in this turn because delegation is disabled. See `SILENT_ASSUMPTION_SWEEP.json`; deterministic tests and artifact checks were run instead.

## Deferred

- No embedding model, semantic retrieval, test-set labeling, classifier training, MLflow/DVC integration, CI/CD, or deployment is part of this first pilot.

## Blockers

- The first-pass labels are not yet a reliable retrieval-quality estimate: most irrelevant decisions used shared rationale without a row-by-row full-context audit. Recheck the 200 responses individually, then inspect retrieval and label some pairs outside the lexical candidate set before expanding labels or training a classifier.
