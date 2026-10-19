# Steam Patch Relevance — project handoff

Updated: 2026-10-19

This is the end-to-end handoff for the restarted Steam patch/review relevance project. It summarizes the completed Stage 1–4 work and points to the detailed contracts, implementation notes, and reports. The current objective is to determine whether a specific review claim discusses a specific atomic change in a specific Steam update. A review's overall Recommended vote is not a feature-level sentiment label, and temporal proximity alone is not evidence of relevance.

## Current state

Stages 1–3 are implemented and their local datasets are materialized. Stage 4 has a 24-pair candidate-label pilot and a separate 300-review candidate-independent full-list audit. The latter two are LLM-generated silver judgments, not human-verified ground truth. No model has been trained, calibrated, or deployed. Full candidate-pair labeling beyond the 24-pair pilot has not started.

The supported implementation is the isolated `steam_patch_relevance` package, the `steam-relevance` CLI, and the `data/relevance_v1/` storage namespace. The retired `steam_insights` pipeline and its historical outputs are not inputs to this implementation.

## Stage outcomes

| Stage | State and canonical artifact | Main result | Main limitation |
| --- | --- | --- | --- |
| 1 — raw source collection | Complete bounded pilot; `rv1-20261019T031033900187Z-a468b544` | Four games; 1,331 announcements; 28 selected patch candidates; 168,292 unique review revisions from a reported 723,539 in selected windows; all-language collection. | Only 16/84 windows complete; zero verified build-linked patches. Steam News is a mixed announcement feed, and publication time is used where release time is unavailable. |
| 1.5 — multilingual audit | Complete; details in the Stage 1 handoff | 168,292 review revisions across 31 Steam language codes: 58,520 English and 109,772 non-English. All 1,708 inspected review-page references used `languages=["all"]`. | 68/84 windows remain incomplete; announcement language is not supplied in the inspected source metadata. |
| 2 — atomic extraction | Complete; `rv2-d52a3f9f1a3de2fe80aa098f` | 1,331 announcement classifications; 3,154 change rows; 297,500 review claims; 316 episodes; 133,842 review-window memberships; 2,000 terminology entries. The audited 51-row sample had zero source-span offset mismatches. | No Man’s Sky yielded zero atomic changes. Change and claim semantics have substantial unresolved/null fields; extraction is not relevance labeling. |
| 3 — hybrid candidate retrieval | Complete; `rv3-cef79b660029d7d5eb703567` | 397 changes across 9 review-covered episodes / 3 games; 77,220 eligible claims; 3,656,475 possible pairs; 62,548 retrieved candidates; 3,646 unlabelled hard-case rows; 45 independent full-list audit packets. | Candidate counts are not matches. Only 9/316 episodes were usable; 53/60 window segments were incomplete. Large dense-retrieval truncation is measured, but omitted-pair relevance is unknown. |
| 4 — silver-label pilot | Complete small pilot; `rv4-02c10d1f84099a6d45e2a04a` | 24 candidate pairs: 14 unrelated, 8 topical-only, 1 plausibly related, 1 clearly attributable. Six candidate-independent reviews exposed to full change lists found two topical-only items and no category 2–3 omission. | Only two category 2–3 candidate labels; not enough to train or evaluate a model. One-session LLM judgments are uncalibrated and unreviewed by a person. |
| 4 — 300-review independent audit | Complete diagnostic; `rv4audit-a60c181629f3cc8195cc4c44` | 300 deterministically sampled Dota 2 reviews were each shown the same complete list of 69 extracted changes. It found one topical-only item and one plausible role-queue match; the latter was already retrieved (BM25 rank 50, fused rank 79). No category 3 or category 2–3 retrieval omission was found. | Sample comes from a single patch’s incomplete post-patch pool (reported 47.28% coverage). It is not a corpus-wide recall estimate; patch-note completeness is unverified. |

## Key interpretation

- Stage 3 retrieves possible pairs through BM25, multilingual dense embeddings, and game-specific entity/aspect matching, fused with reciprocal-rank fusion. Its independent full-list review audit does not depend on retrieved candidates.
- Stage 4 uses category 0–3 relevance judgments: unrelated, topical-only, plausible patch/change relevance, and clearly attributable. Category 1 is not a positive relevance label. Feature polarity is separate from relevance.
- The 300-review audit suggests that this one sampled Dota 2 window did not expose a missed plausible-or-clear match under the current extraction and LLM audit. It cannot establish recall for other patches, languages, games, or the full corpus.
- Data artifacts under `data/relevance_v1/` are local and git-ignored. The handoffs and reports in `docs/` and `reports/` explain their schemas and provenance. Keep raw review data local because payloads may contain Steam account identifiers and author metadata.

## What remains before modeling

1. Improve source coverage: continue bounded review collection for useful windows, prioritize patch notes with verified release/build context, and investigate official linked changelog pages where allowed.
2. Improve extraction coverage and quality, especially No Man’s Sky and the unresolved entity/aspect fields. Preserve source spans and audit changes before retrieval.
3. Expand candidate-independent audits across several patches, games, and languages, with an explicit sampling and adjudication design. Keep these separate from candidate-selected examples.
4. Only after a sufficiently diverse verified set exists, label a planned candidate sample, define leakage-resistant group splits, and decide whether a supervised model is justified. The current evidence does not support fine-tuning.
5. Do not claim model performance or corpus-wide recall from the current pilots. No Stage 5/model training, threshold tuning, CI/CD, or deployment work is complete.

## Detailed documentation and outputs

- Restart scope and architecture: [`ARCHITECTURE.md`](ARCHITECTURE.md), [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md), [`LEGACY_INVENTORY.md`](LEGACY_INVENTORY.md), and [`STATUS.md`](STATUS.md).
- Stage 1 source contracts, raw schema, multilingual audit, and detailed results: [`stage1/HANDOFF.md`](stage1/HANDOFF.md), [`stage1/STEAM_API_CONTRACTS.md`](stage1/STEAM_API_CONTRACTS.md), [`stage1/RAW_DATA_SCHEMA.md`](stage1/RAW_DATA_SCHEMA.md), and [`stage1/MULTILINGUAL_AUDIT.md`](stage1/MULTILINGUAL_AUDIT.md).
- Stage 2 schemas and extraction QA: [`stage2/HANDOFF.md`](stage2/HANDOFF.md), [`stage2/DATA_CONTRACTS.md`](stage2/DATA_CONTRACTS.md), and [`quality report`](../../reports/relevance_v1/stage2/rv2-d52a3f9f1a3de2fe80aa098f/quality_report.md).
- Stage 3 methods, diagnostics, and candidate-free audit design: [`stage3/HANDOFF.md`](stage3/HANDOFF.md), [`stage3/ARCHITECTURE.md`](stage3/ARCHITECTURE.md), and [`retrieval report`](../../reports/relevance_v1/stage3/rv3-cef79b660029d7d5eb703567/report.md).
- Stage 4 labels, exact pilot pairs, and 300-review audit findings: [`stage4/HANDOFF.md`](stage4/HANDOFF.md), [`candidate-pair inspection`](../../reports/relevance_v1/stage4/rv4-02c10d1f84099a6d45e2a04a/candidate_pairs_for_inspection.md), [`pilot readiness report`](../../reports/relevance_v1/stage4/rv4-02c10d1f84099a6d45e2a04a/readiness_report.md), and [`300-review audit report`](../../reports/relevance_v1/stage4/independent_audit/rv4audit-a60c181629f3cc8195cc4c44/readiness_report.md).

## Reproduction entry points

These commands reproduce derived processing from the frozen local artifacts; they do not recollect Steam data or rerun the in-session LLM judgments:

```bash
uv run --all-extras steam-relevance stage2 extract \
  --source-run rv1-20261019T031033900187Z-a468b544

uv run --all-extras steam-relevance stage3 retrieve \
  --source-dataset rv2-d52a3f9f1a3de2fe80aa098f \
  --budgets 10 25 50 100 --before-days 14 --after-days 14 \
  --dense-revision 614241f622f53c4eeff9890bdc4f31cfecc418b3
```

The Stage 4 job files, response files, manifests, and import receipts are preserved under the run paths listed in [`stage4/HANDOFF.md`](stage4/HANDOFF.md). Their judgments cannot be reproduced by rerunning the CLI alone; the original response artifacts are required.
