# Project Handoff

Updated: 2026-10-18

## Purpose and scope

Build a system that accepts a Steam game lookup, collects reviews and developer announcements, distinguishes patch notes from promotional posts, links individual changes to review feedback, and summarizes what players liked or disliked. The longer-term goal includes real-time Steam lookup, scheduled collection, model deployment, CI/CD, data/model versioning, and monitoring.

The user does not have human annotators and chose an LLM-only labeling route. LLM judgments are machine-generated **silver** labels, never human gold. They need exact source evidence for relevant pairs and remain distinct from Steam's Recommended vote.

The intended progression remains: Phase 1, reliable local data collection/processing and a useful patch report; Phase 2, stronger tests, retrieval evaluation, labeling coverage and a baseline; Phase 3, CI/CD, DVC/MLflow lineage, model release/deployment and monitoring. Real-time arbitrary-game lookup through Steam is a target capability but is not implemented by the current local pipeline. This order stabilizes source, candidate and label contracts before automating model releases.

## Where to find the accumulated design context

- `docs/data_pipeline.md` describes the end-to-end processing stages, publication/storage rationale, patch-window semantics, review-change matching, splits and model loading.
- `docs/data_dictionary.md` defines table/field contracts; `docs/data_pipeline_status.md` records earlier implementation and verification history.
- `docs/llm_annotation_workflow.md` documents file-based LLM labeling and import, including evidence rules and patch-scoped audits. `reports/data_quality/helldivers_710_full_list_review_audit.md` records a separate random full-list review audit.
- `reports/data_quality/data_quality_report.md` and `reports/data_quality/pipeline/report.md` are the generated source-quality and patch-window reports.
- `implement-stage/data-pipeline/` and `implement-stage/patch-pilot/` hold the specs, assumption ledgers and build notes for those implementation slices.

## Current implementation

- The data workflow normalizes review revisions, parses announcement revisions and individual change blocks, screens patch windows, generates review/change candidates, stores immutable Parquet snapshots, and validates published tables. DuckDB is available for exploration.
- LLM labeling uses provider-neutral files, frozen candidate membership, exact quote validation, run/model/prompt provenance, and a separate `silver_pairs.parquet` export. No API credentials or human annotation are needed for the file-based workflow.
- Patch-scoped export now supports `--patch-id` and `--exclude-annotated`. It balances sampling over change/task/split groups, prioritizes the highest lexical scores within each group, and writes `retrieval_audit.csv` outside the model prompt.
- The first Sea of Thieves 3.8.1 response pass was re-reviewed row by row against full review and announcement context. A distinct LLM run supersedes, rather than deletes, the first-pass decisions.
- `scripts/data/report_patch_pilot.py` joins the returned LLM labels to the lexical audit and reports label coverage by task and lexical rank. It explicitly does not estimate missed-pair recall or patch causality. A separate random review audit gave the labeler the complete numbered patch list for every review and did not use lexical candidates.

## Data snapshots and labels

| Stage | Snapshot | Result |
|---|---|---|
| Before the patch pilot | `5c8a356cb9aa33235617e46eb2b6597db40ed77ee1967ed71be2ec0b65f633c7` | 100 initial GPT-6 decisions; 99 silver rows (76 train, 23 validation); 6 relevant, 93 irrelevant, 1 uncertain. |
| Current | `cfa34941257d2905d8a2f2681de931909e1904d97bc220e9d121f3c855b4cf56` | 500 stored machine annotation records, including 200 superseded first-pass records; 289 active silver rows; 0 human annotation rows; all 196 snapshot checks passed. The 300 active decisions are 6 relevant, 283 irrelevant, and 11 uncertain. |

The current corpus has 30 games, 30,194 review/change candidate pairs, 255 source-confirmed or reviewed patch posts, and 16 patch windows that pass the configured review-coverage screen. See `reports/data_quality/pipeline/report.md` and `reports/data_quality/data_quality_report.md` for current source-quality findings.

## Sea of Thieves 3.8.1 pilot

The selected patch is Release Notes 3.8.1, patch ID `9593c96b043f323204b6db3437497a9b4972e5986d637dd7e21ce7b908946839`. It has 156 eligible reviews before and 134 after the patch, with no overlapping patch post in the configured window. The lexical retriever produced 348 candidate pairs for this patch.

The pilot job is `data/annotations/llm_jobs/sot-381-pilot`, frozen against snapshot `5c8a356cb9aa33235617e46eb2b6597db40ed77ee1967ed71be2ec0b65f633c7`. It contains 200 new train examples (126 post-patch feedback, 74 retrospective complaint-resolution), excluding two previously labeled candidates. The first GPT-6 run (`codex-gpt6-sot381-pilot-2026-10-17`) labeled all 200 as 198 irrelevant and 2 uncertain, but used largely shared rationales. A second GPT-6 run (`codex-gpt6-sot381-row-audit-2026-10-18`) re-read every full review and its exact announcement passage, then superseded all 200 earlier decisions: 190 are irrelevant and 10 uncertain, with no relevant pairs. The rowwise results are 118 irrelevant/8 uncertain for post-patch feedback and 72 irrelevant/2 uncertain for retrospective complaint-resolution. Including the two earlier candidates, 202 patch candidates now have active decisions: 192 irrelevant and 10 uncertain.

The sample is stratified across change/task groups and prioritized by lexical score. The zero-relevant result is now a rowwise contextual re-review, but remains a single-model silver judgment rather than independent or human adjudication. The 10 uncertain rows were retained where only a section heading was extracted or a symptom matched while its trigger did not. A follow-up comparison of the rationales against frozen pair inputs found two uncertain rationales describing review text that is absent from their stored pairs (`0580a1eb…` and `caad4bdf…`); both pairs appear irrelevant and need a corrected annotation run before the 190/10 counts are treated as final. The common shared terms (`players` 40, `ship` 34, `seas` 19, `player` 18) show why raw word overlap is weak for this patch. This sample does not estimate corpus precision or missed-pair recall and cannot establish patch causality. See the tracked summary `reports/data_quality/patch_pilot_rowwise_audit.md`, the generated `data/annotations/llm_jobs/sot-381-pilot/retrieval_audit_report.md`, and the full 348-row lexical pool in `retrieval_audit.csv`. The new rowwise responses and all Parquet data are local artifacts ignored by Git; back them up with the data storage policy. The first-pass report and decisions are retained under `rowwise-audit/` for traceability.

## HELLDIVERS 2 7.1.0 full-list review audit

A separate, reproducible random sample of 300 post-patch reviews was assessed against the complete 101-fragment change list for “Devoid of Liberty: 7.1.0”. The sample was drawn without replacement from 708 eligible review records in snapshot `cfa34941257d2905d8a2f2681de931909e1904d97bc220e9d121f3c855b4cf56`, using seed `steam-full-list-20261018-v1`. The labeler recorded 3 confirmed review/change mentions, 30 uncertain topical overlaps, and 267 reviews with no specific item identified. Confirmed mentions were two reviews about enemy spawn placement (change 12) and one review directly quoting the GL-52 De-Escalator self-damage change (change 47). A join to `candidates.parquet` found 2 of these 3 exact pairs. The omitted change-12 pair cleared the two-term minimum but scored 0.067, below five selected alternatives; `max_per_review_per_task = 5` explains this concrete cap miss, not a corpus recall estimate.

This is a full-list audit independent of the lexical candidate pool. It is a single GPT-6 assistant labeling pass, not human or independent-model adjudication. No external API, provider-side prompt cache, or cost measurement was used; the shared prefix is saved in a cache-ready form. The collection is incomplete, one other patch post overlaps the analysis period, and 65 of the 101 extracted fragments are flagged for review. These results do not measure label accuracy, recall, sentiment toward changes, or patch causality. The tracked report lists every uncertain review/change candidate. Full inputs and machine-readable outputs live in Git-ignored `data/annotations/llm_jobs/helldivers-710-full-list/`; `prompts.jsonl` materializes all 300 complete prompts, each with the full numbered list and one review.

## Commands and result locations

Run from the `Game-review/` repository root:

```bash
# Rebuild and validate the current snapshot from cached/local sources
uv run --all-extras steam-insights prepare-data

# Check the latest published snapshot
uv run --all-extras steam-insights pipeline-validate

# Recreate the current report after the rowwise context review
python scripts/data/report_patch_pilot.py \
  --job data/annotations/llm_jobs/sot-381-pilot \
  --responses data/annotations/llm_jobs/sot-381-pilot/rowwise-audit/responses-0001.jsonl \
  --rowwise-context-audited --audit-model GPT-6 \
  --audit-run-id codex-gpt6-sot381-row-audit-2026-10-18
```

The response artifact can be imported and the corrected dataset rebuilt with:

```bash
uv run --all-extras steam-insights llm-annotations-import \
  --job data/annotations/llm_jobs/sot-381-pilot \
  --input data/annotations/llm_jobs/sot-381-pilot/rowwise-audit/responses-0001.jsonl \
  --model GPT-6 --run-id codex-gpt6-sot381-row-audit-2026-10-18
uv run --all-extras steam-insights prepare-data
uv run --all-extras steam-insights pipeline-validate
```

To export more examples for the same patch, rebuild first so the current machine labels are represented, then use a new output directory:

```bash
uv run --all-extras steam-insights llm-annotations-export \
  --patch-id 9593c96b043f323204b6db3437497a9b4972e5986d637dd7e21ce7b908946839 \
  --sample-size 100 --split train --exclude-annotated \
  --output data/annotations/llm_jobs/sot-381-followup
```

The 200-pair context audit is complete. Before treating relevance rates as system performance, sample pairs outside the lexical candidate set and improve retrieval. Do not use this candidate-only sample as a recall estimate. See `docs/llm_annotation_workflow.md` for export, response, import, superseding, and model-loading steps.

## Decisions and limits

- A Steam Recommended vote is not sentiment toward an individual patch change.
- Relevance means the review discusses the specific change or the specific complaint it addresses. Generic discussion of graphics, bugs, ships, matchmaking, loot, or PvP does not establish a match by itself.
- Relevant machine labels require exact review and announcement quotes. Uncertain decisions and disagreements remain stored, but are excluded from silver training rows.
- The earlier broad 100-example pass has only six relevant examples across the corpus. The patch pilot adds no relevant example. There is not yet enough positive coverage to train a reliable relevance classifier, and there is no basis to train change sentiment or fix-status models.
- LLM agreement/evaluation measures consistency with the labeling process, not independently verified human accuracy. Keep model and prompt versions fixed for comparisons.
- Review/patch-window comparisons are observational. They do not show that a patch caused a sentiment change.
- The rowwise context audit covers only pairs emitted by the lexical retriever. A semantic retriever and a separately labeled sample of currently missed/noncandidate pairs are needed to audit recall.

## Next work

1. Inspect the 10 uncertain rows and targeted false positives to decide whether announcement parsing should emit finer-grained changes instead of section headings.
2. Improve retrieval: compare domain-specific stop terms and IDF-weighted overlap against phrase-level matching; inspect change-block context and the per-review candidate cap. Version the candidate-generation contract so existing candidate IDs and pilot labels remain auditable.
3. Label a controlled sample of pairs outside the lexical candidate set. Combine that with surfaced-pair review to assess both false matches and missed matches; keep the limits of LLM-only evaluation explicit.
4. Inspect the 30 uncertain reviews from the HELLDIVERS 2 full-list audit and repeat a separately sampled full-list audit on another coverage-screened patch; fix broad/heading-only extraction before change-level sentiment analysis.
5. Add a second retrieval rung with a small, maintained sentence-embedding model and rerank lexical plus semantic candidates. Evaluate it on multiple coverage-screened patches before setting a production threshold.
6. Only after positive labels cover games, changes, and sentiment classes, establish a simple relevance baseline and then consider sentiment/fix-status models. Keep game-held-out validation and a frozen test set.
7. Build a patch report with exact evidence, coverage warnings, and descriptive before/after review summaries.
8. Stabilize source, candidate, label, and prediction contracts before adding live Steam lookup/cache/rate controls, scheduled collection, DVC/MLflow lineage, GitHub Actions checks, model release/deployment, and monitoring.

## Handoff update log

- 2026-10-17: Recorded the initial 100-example GPT-6 pass and 99 silver rows.
- 2026-10-17: Added patch-scoped balanced export and imported the first 200 Sea of Thieves 3.8.1 decisions. The first run is retained but its decisions are superseded below.
- 2026-10-18: Re-read all 200 full review/change pairs, recorded candidate-specific rationales, and superseded all first-pass decisions in a distinct GPT-6 run. The revised sample contains 190 irrelevant and 10 uncertain pairs; it has no relevant pair and does not measure recall. Rebuilt snapshot `cfa34941257d2905d8a2f2681de931909e1904d97bc220e9d121f3c855b4cf56`; all 196 publication checks passed. Corrected report: `reports/data_quality/patch_pilot_rowwise_audit.md`.
- 2026-10-18: Compared the uncertain-row rationales to the frozen pair inputs. Two rationales describe review complaints that are absent from their stored pairs; those pairs appear irrelevant and need superseding annotations plus a dataset rebuild. See the follow-up consistency note in `reports/data_quality/patch_pilot_rowwise_audit.md`.
- 2026-10-18: Completed a random full-list audit of 300 HELLDIVERS 2 7.1.0 post-patch reviews against all 101 extracted changes. Results: 3 confirmed, 30 uncertain, 267 with no specific match; validation confirmed all review IDs join and all evidence quotes are exact. See `reports/data_quality/helldivers_710_full_list_review_audit.md`; row-level outputs are in the Git-ignored `data/annotations/llm_jobs/helldivers-710-full-list/`. This separate audit was not imported into the training snapshot.
