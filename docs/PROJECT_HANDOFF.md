# Project Handoff

Updated: 2026-10-17

## Purpose and scope

Build a system that accepts a Steam game lookup, collects reviews and developer announcements, distinguishes patch notes from promotional posts, links individual changes to review feedback, and summarizes what players liked or disliked. The longer-term goal includes real-time Steam lookup, scheduled collection, model deployment, CI/CD, data/model versioning, and monitoring.

The user does not have human annotators and chose an LLM-only labeling route. LLM judgments are machine-generated **silver** labels, never human gold. They need exact source evidence for relevant pairs and remain distinct from Steam's Recommended vote.

The intended progression remains: Phase 1, reliable local data collection/processing and a useful patch report; Phase 2, stronger tests, retrieval evaluation, labeling coverage and a baseline; Phase 3, CI/CD, DVC/MLflow lineage, model release/deployment and monitoring. Real-time arbitrary-game lookup through Steam is a target capability but is not implemented by the current local pipeline. This order stabilizes source, candidate and label contracts before automating model releases.

## Where to find the accumulated design context

- `docs/data_pipeline.md` describes the end-to-end processing stages, publication/storage rationale, patch-window semantics, review-change matching, splits and model loading.
- `docs/data_dictionary.md` defines table/field contracts; `docs/data_pipeline_status.md` records earlier implementation and verification history.
- `docs/llm_annotation_workflow.md` documents file-based LLM labeling and import, including evidence rules and the new patch-scoped audit.
- `reports/data_quality/data_quality_report.md` and `reports/data_quality/pipeline/report.md` are the generated source-quality and patch-window reports.
- `implement-stage/data-pipeline/` and `implement-stage/patch-pilot/` hold the specs, assumption ledgers and build notes for those implementation slices.

## Current implementation

- The data workflow normalizes review revisions, parses announcement revisions and individual change blocks, screens patch windows, generates review/change candidates, stores immutable Parquet snapshots, and validates published tables. DuckDB is available for exploration.
- LLM labeling uses provider-neutral files, frozen candidate membership, exact quote validation, run/model/prompt provenance, and a separate `silver_pairs.parquet` export. No API credentials or human annotation are needed for the file-based workflow.
- Patch-scoped export now supports `--patch-id` and `--exclude-annotated`. It balances sampling over change/task/split groups, prioritizes the highest lexical scores within each group, and writes `retrieval_audit.csv` outside the model prompt.
- `scripts/data/report_patch_pilot.py` joins the returned LLM labels to the lexical audit and reports label coverage by task and lexical rank. It explicitly does not estimate missed-pair recall or patch causality.

## Data snapshots and labels

| Stage | Snapshot | Result |
|---|---|---|
| Before the patch pilot | `5c8a356cb9aa33235617e46eb2b6597db40ed77ee1967ed71be2ec0b65f633c7` | 100 initial GPT-6 decisions; 99 silver rows (76 train, 23 validation); 6 relevant, 93 irrelevant, 1 uncertain. |
| Current | `5eb4842f3daaf8125a9daaaeef18c9e9f0c304dcd8703c5b100a5cfd39c77c9f` | 300 machine decisions; 297 silver rows; 0 human annotation rows; all 196 snapshot checks passed. Three machine decisions are uncertain/conflicted and excluded from silver rows. |

The current corpus has 30 games, 30,194 review/change candidate pairs, 255 source-confirmed or reviewed patch posts, and 16 patch windows that pass the configured review-coverage screen. See `reports/data_quality/pipeline/report.md` and `reports/data_quality/data_quality_report.md` for current source-quality findings.

## Sea of Thieves 3.8.1 pilot

The selected patch is Release Notes 3.8.1, patch ID `9593c96b043f323204b6db3437497a9b4972e5986d637dd7e21ce7b908946839`. It has 156 eligible reviews before and 134 after the patch, with no overlapping patch post in the configured window. The lexical retriever produced 348 candidate pairs for this patch.

The pilot job is `data/annotations/llm_jobs/sot-381-pilot`, frozen against snapshot `5c8a356cb9aa33235617e46eb2b6597db40ed77ee1967ed71be2ec0b65f633c7`. It contains 200 new train examples (126 post-patch feedback, 74 retrospective complaint-resolution), excluding two previously labeled candidates. The response pass used model label `GPT-6`, run ID `codex-gpt6-sot381-pilot-2026-10-17`, and imported all 200 labels: 198 irrelevant, 2 uncertain, 0 relevant. The two uncertain examples share a symptom with a change but lack enough context to establish the specific issue. Together with the earlier two labels, 202 candidates in this patch have stored decisions: 200 irrelevant and 2 uncertain.

The sample was stratified across change/task groups and prioritized by lexical score. **The zero-relevant result is provisional:** most irrelevant responses were produced with a shared rationale, and every pair was not individually checked against its full announcement context. The current label rate must not be treated as retrieval precision or used to tune a threshold until the 200 pairs receive that per-example review. The audit's most common shared terms are generic game vocabulary (`players` 40, `ship` 34, `seas` 19, `player` 18), which is a useful clue about the overlap scorer but does not verify each label. The tokenizer removes common English stopwords but the scorer has no inverse-document-frequency weighting or phrase-level match. The sample does not measure missed-pair recall. The audit report is `data/annotations/llm_jobs/sot-381-pilot/retrieval_audit_report.md`; the full lexical pool and ranks are in `retrieval_audit.csv`. Prompt files, responses, and Parquet data are local artifacts and are ignored by Git; back them up with the data storage policy.

## Commands and result locations

Run from the `Game-review/` repository root:

```bash
# Rebuild and validate the current snapshot from cached/local sources
uv run --all-extras steam-insights prepare-data

# Check the latest published snapshot
uv run --all-extras steam-insights pipeline-validate

# Recreate the patch audit report from saved LLM responses
python scripts/data/report_patch_pilot.py \
  --job data/annotations/llm_jobs/sot-381-pilot \
  --responses data/annotations/llm_jobs/sot-381-pilot/responses
```

To export more examples for the same patch, rebuild first so the current machine labels are represented, then use a new output directory:

```bash
uv run --all-extras steam-insights llm-annotations-export \
  --patch-id 9593c96b043f323204b6db3437497a9b4972e5986d637dd7e21ce7b908946839 \
  --sample-size 100 --split train --exclude-annotated \
  --output data/annotations/llm_jobs/sot-381-followup
```

Before any follow-up export, individually audit the existing 200 responses against each full review and announcement context, correct any labels with a new run ID, and regenerate the report. Do not use the preliminary zero-relevant result to tune retrieval. See `docs/llm_annotation_workflow.md` for export, response, import, and model-loading steps.

## Decisions and limits

- A Steam Recommended vote is not sentiment toward an individual patch change.
- Relevance means the review discusses the specific change or the specific complaint it addresses. Generic discussion of graphics, bugs, ships, matchmaking, loot, or PvP does not establish a match by itself.
- Relevant machine labels require exact review and announcement quotes. Uncertain decisions and disagreements remain stored, but are excluded from silver training rows.
- The earlier broad 100-example pass has only six relevant examples across the corpus. The patch pilot adds no relevant example. There is not yet enough positive coverage to train a reliable relevance classifier, and there is no basis to train change sentiment or fix-status models.
- LLM agreement/evaluation measures consistency with the labeling process, not independently verified human accuracy. Keep model and prompt versions fixed for comparisons.
- Review/patch-window comparisons are observational. They do not show that a patch caused a sentiment change.
- The pilot audit covers only pairs emitted by the lexical retriever. A semantic retriever and a separately labeled sample of currently missed/noncandidate pairs are needed to audit recall.

## Next work

1. Audit the 200 pilot decisions individually against full review and announcement context, recording a candidate-specific rationale and correcting any labels in a distinct run. Then inspect false positives and retrieval terms for Sea of Thieves 3.8.1.
2. Improve retrieval: compare domain-specific stop terms and IDF-weighted overlap against phrase-level matching; inspect change-block context and the per-review candidate cap. Version the new candidate-generation contract so existing candidate IDs and pilot labels remain auditable.
3. Add a second retrieval rung with a small, maintained sentence-embedding model and rerank lexical plus semantic candidates. Add a controlled LLM-labeled sample of pairs the lexical system did not emit, so retrieval changes can be assessed for newly surfaced matches. Keep the limits of LLM-only evaluation explicit.
4. Run the revised retriever on multiple coverage-screened patches, label a fresh stratified batch, and measure relevance by task, patch, rank, and label coverage before setting a production threshold.
5. Only after positive labels cover games, changes, and sentiment classes, establish a simple relevance baseline and then consider sentiment/fix-status models. Keep game-held-out validation and a frozen test set.
6. Build a patch report with exact evidence, coverage warnings, and descriptive before/after review summaries.
7. Stabilize source, candidate, label, and prediction contracts before adding live Steam lookup/cache/rate controls, scheduled collection, DVC/MLflow lineage, GitHub Actions checks, model release/deployment, and monitoring.

## Handoff update log

- 2026-10-17: Recorded the initial 100-example GPT-6 pass and 99 silver rows.
- 2026-10-17: Added patch-scoped balanced export, the lexical retrieval sidecar and report, then imported 200 Sea of Thieves 3.8.1 LLM decisions. Rebuilt snapshot `5eb4842f3daaf8125a9daaaeef18c9e9f0c304dcd8703c5b100a5cfd39c77c9f`; all 196 publication checks passed. Later review found the 198 irrelevant responses used shared rationale and were not individually checked against full announcement context. Treat the 0-relevant result as provisional and individually audit the pilot before retrieval tuning.
