# Build Note — Patch-Scoped Labeling Pilot

| Rung | Feature | Acceptance check (one command) | Tier | Status |
|------|---------|-------------------------------|------|--------|
| F0 | Add patch-filtered, change-balanced LLM job export with an auditable lexical sidecar | `uv run --all-extras steam-insights llm-annotations-export --patch-id 9593c96b043f323204b6db3437497a9b4972e5986d637dd7e21ce7b908946839 --sample-size 200 --split train --exclude-annotated --output data/annotations/llm_jobs/sot-381-pilot` | MUST | ✅ |
| F1 | Label/import the frozen pilot and publish refreshed silver data | `uv run --all-extras steam-insights prepare-data` | MUST | ✅ |
| F2 | Summarize labeled lexical-rank sample and update the handoff | `python scripts/data/report_patch_pilot.py --job data/annotations/llm_jobs/sot-381-pilot --responses data/annotations/llm_jobs/sot-381-pilot/responses` | MUST | ✅ |
| F3 | Re-review all 200 pairs against full review and announcement context; supersede first-pass decisions | `uv run --all-extras steam-insights llm-annotations-import --job data/annotations/llm_jobs/sot-381-pilot --input data/annotations/llm_jobs/sot-381-pilot/rowwise-audit/responses-0001.jsonl --model GPT-6 --run-id codex-gpt6-sot381-row-audit-2026-10-18` | MUST | ✅ |
| F4 | Add embedding retrieval, noncandidate recall audit, and baseline model | Deferred: requires a separate model/dependency decision and broader labels | DEFERRED | ⬜ |

## Run record

- Frozen input snapshot: `5c8a356cb9aa33235617e46eb2b6597db40ed77ee1967ed71be2ec0b65f633c7`.
- Pilot job ID: `e5be0734ba84a936f015314014b153510ef9297056e592205a6ee09ccd2e733c`; 200 fresh train examples from a 348-pair lexical pool, with two earlier labeled IDs excluded.
- First-pass LLM run: model label `GPT-6`, run ID `codex-gpt6-sot381-pilot-2026-10-17`; imported all 200 responses (198 irrelevant, 2 uncertain, 0 relevant). Those decisions are preserved as superseded history.
- Rowwise correction run: model label `GPT-6`, run ID `codex-gpt6-sot381-row-audit-2026-10-18`; re-read each complete review and announcement context, superseding all 200 previous decisions. Outcomes: 190 irrelevant, 10 uncertain, 0 relevant (post-patch: 118/8/0; retrospective: 72/2/0). The same LLM workflow was used, so these remain silver and are not independent or human adjudications.
- Refreshed snapshot: `cfa34941257d2905d8a2f2681de931909e1904d97bc220e9d121f3c855b4cf56`; 500 stored annotation records including 200 superseded, 300 active decisions, 289 silver rows, 0 human rows, and 11 active uncertain decisions; all 196 publication checks passed.
- Corrected report: `data/annotations/llm_jobs/sot-381-pilot/retrieval_audit_report.md`; tracked summary: `reports/data_quality/patch_pilot_rowwise_audit.md`. It describes the stratified lexical sample and does not estimate missed-pair recall or unbiased corpus precision.
- Verification: `python -m unittest discover -s tests -p 'test_pipeline_*.py'` passed 26 tests; Ruff lint and format checks passed for changed Python files.
- Independent assumption sweep is unavailable in this turn because delegation is disabled. See `SILENT_ASSUMPTION_SWEEP.json`; deterministic tests and artifact checks were run instead.

## Deferred

- No embedding model, semantic retrieval, test-set labeling, classifier training, MLflow/DVC integration, CI/CD, or deployment is part of this first pilot.

## Blockers

- The rowwise pass found no relevant pairs in this sample and retained 10 uncertain rows. Improve lexical candidate generation and label a separately sampled set of noncandidate pairs before estimating retrieval quality or training a relevance classifier.
