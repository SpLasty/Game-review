# Restart status

For the consolidated Stage 1–4 project handoff, including the 300-review full-list audit, see [`PROJECT_HANDOFF.md`](PROJECT_HANDOFF.md). This file remains the detailed chronological implementation status.

Updated: 2026-10-19. Current stage: **4 — bounded silver-label pilot complete; full-scale labeling awaits user approval**. Stage 0 evidence preservation, Stage 1 source collection, Stage 1.5 multilingual audit, and Stage 2 atomic extraction remain the foundation. Stage 3 uses its own `rv3-` datasets and candidate-free full-list audit packets. Stage 4 creates a separate provider-neutral LLM-silver dataset; no model training has occurred.

## Decisions now in force

1. The research question is whether a review discusses a specific atomic change in a specific patch.
2. The old lexical candidate, patch-window screening and machine silver pipeline is retired from the supported CLI. Its outputs are historical evidence only.
3. The new implementation uses a separate `steam_patch_relevance` namespace, `data/relevance_v1/` artifacts, `rv1_` identifiers and `steam-relevance` CLI. It has no imports from `steam_insights`.
4. Historical data and audits are preserved. The Sea of Thieves and HELLDIVERS 2 findings are not acceptance criteria for the new system.
5. The legacy importable package and notebooks remain isolated for historical reproducibility. A process check after Stage 1 found no active project collector or Jupyter kernel; no unrelated process was stopped.
6. Stage 3 method rankings are independent and unioned with RRF. Time membership filters eligibility but does not assign relevance; hard-case rules never label negatives.
7. Stage 4 labels are silver judgments from an LLM, never gold. Its candidate-free full-list audit is kept separate from candidate labels and is not a corpus-wide recall estimate.

## Verification and remaining boundary

The original 71-test suite passed before cleanup. The checkpoint bundle verified. The file-level evidence inventory hashes 13,330 files. Host process, cron and user timer checks found no abandoned project job or schedule; one Jupyter kernel in `notebooks/` was retained. No process was stopped.

The old `src/steam_insights/` island, notebook 03, and `configs/pipeline.toml` remain in the working tree as isolated legacy material; the new package does not import them. The Stage 0 inventory and evidence checkpoint explain their provenance. A frozen local copy of `data/` exists under `legacy/research/data/`, but no off-machine backup was established. Do not delete both local copies without a verified external copy.

## Stage 0 completion update

- The remaining notebook/preprocessing suite passed: **21 tests**. Ruff passed. All 17 retained legacy pipeline modules import, and both notebook data imports work. The old CLI module and generated launcher are absent.
- `git diff --check` passed. The bundle was cloned into a temporary repository and the pre-cleanup tracked diff applied cleanly there.
- All **13,327 unchanged** research files from the pre-cleanup manifest were found at their original or documented archive paths with matching SHA-256 hashes. Three README/notebook files were intentionally edited and are also recoverable from the checkpoint.
- The full pre-restart `data/` tree was copied to `legacy/research/data/` after the checkpoint. **13,259 archived data files** matched the pre-cleanup manifest; the intentionally edited `data/README.md` is recoverable from the checkpoint.
- Stage 0's offline `uv sync --locked --all-extras` could not refresh the editable install because the local offline cache lacked `setuptools>=75`; during Stage 1, retrying sync also failed because DNS resolution for `pypi.org` was unavailable. The existing `.venv` tests and imports work.
- Git working tree at completion: seven modified tracked files (README, data/reports READMEs, `.gitignore`, package metadata, notebook 03 and retained test); 60 tracked deletions from archived/retired paths; new `docs/restart/` and `legacy/` trees. The archived data copy is Git-ignored. No new collection, labeling, model run, or Stage 1 code was created.

## Stage 1 implementation update

- Added the standalone `steam_patch_relevance` package, `steam-relevance` CLI, and `configs/relevance_v1.toml`; the old collector modules and archived datasets are not imported.
- Verified current Steamworks contracts and a bounded live response shape check; see `stage1/STEAM_API_CONTRACTS.md`.
- Added content-addressed exact raw response storage, HTTP-attempt budgets, sequential pacing, retries, Steam News enddate pagination with newest-watermark polling, review cursor pagination, resumable checkpoints, stable IDs, Parquet source/coverage tables, and DuckDB inspection.
- Added fixture tests for request fields, source classification, date boundaries, pagination, retries, storage idempotence, malformed responses, duplicate/conflicting review revisions, checkpoint resume, and catalog normalization. **41 tests pass**; Ruff and `git diff --check` pass.
- Bounded pilot: four seeded games, 28 announcement candidates (7/game), 168,292 unique review revisions from a reported 723,539 in selected windows, and 16/84 complete windows. Per-game and patch-window coverage is in `reports/relevance_v1/stage1/latest/`; run summary and limits are in `stage1/HANDOFF.md`.
- No verified build-linked patches were available from the public sources used. Candidate windows use announcement publication time. `GetAppList` was not called because `STEAM_WEB_API_KEY` was not configured; linked off-site changelogs are retained but not fetched.
- Post-run follow-up loaded the new `.env` values. The documented partner host returned 403, but the user-suggested public `api.steampowered.com` route succeeded. The resulting catalog has 194,280 distinct game records over four pages, including all four pilot IDs; see `stage1/CATALOG_FOLLOWUP.md` and the catalog report.
- The catalog is stored as `catalog_apps.parquet` with exact response pages preserved in raw storage. `inspect` and default `materialize` filter out catalog-only run IDs so the catalog does not shadow the review collection run.
- The Stage 1 `uv sync --locked --all-extras` attempt could not fetch `setuptools>=75` because DNS resolution for `pypi.org` failed. A network-enabled retry during Stage 1.5 succeeded with the lock unchanged.
- Stage 1 deliberately stops before atomic-change extraction, review/change matching, LLM annotation, or model training.

## Stage 1.5 multilingual audit update

- Verified the current Steamworks contract: `languages=[]` means English and `languages=["all"]` means all languages. The fresh Stage 1 client already hard-coded `all`, but it had not exposed the value in config/manifests or separated checkpoints by filter.
- Audited the latest selected 84 patch windows directly from their immutable raw pages. All **1,708** review page references used `languages=["all"]`; the latest run's 750 request observations also show that filter. There are **168,292** unique revisions across **31** documented Steam API language codes: **58,520 English**, **109,772 non-English**, and zero missing, unexpected, non-string, or conflicting language metadata. No language backfill was required.
- None of **1,331** inspected news items supplies announcement-language metadata. This is reported separately and not inferred from post text.
- Added `[reviews].languages` default `['all']`; empty lists are rejected. Explicit filter values are recorded and use isolated resumable checkpoint names; the default continues existing all-language checkpoints. Stable review revision IDs exclude language-filter configuration.
- Added explicit source language-status fields, nullable `detected_language` and `detected_language_confidence` placeholders, announcement-language provenance, and exact Unicode preservation. No translation or language detection runs at ingestion.
- Generated per-game and per-patch-window language coverage at `reports/relevance_v1/stage1/latest/`. The [audit report](stage1/MULTILINGUAL_AUDIT.md) documents the counts and limitations. Existing 16/84 complete-window status is unchanged; partial windows reflect collection budgets.
- Offline materialization regenerated the current derived Parquet snapshot without new network requests or changes to raw blobs. Counts remain 4 games, 1,331 announcements, 28 patch candidates, 168,292 review revisions, and 84 windows. The new review schema fields are present.
- Validation: **46 fixture tests passed**; Ruff check/format and `git diff --check` passed. Unicode round-trip, explicit language filters, checkpoint isolation/resumption, filter-independent review IDs, and coverage statistics are covered.
- Stage 1.5 preserved all-language review collection and reported collection-depth gaps. Stage 2's carried-forward coverage is 0/21 complete windows for CS2, 0/21 for Dota 2, 2/6 for HELLDIVERS 2, and 5/12 for No Man's Sky. Before evaluation claims, increase coverage or explicitly account for these partial windows.

## Stage 2 implementation update

- Added isolated `steam_patch_relevance.stage2` classifiers/extractors, `rv2_` dataset IDs, explicit schemas, a `steam-relevance stage2 extract` CLI, and separate `data/relevance_v1/processed/stage2/` outputs. No legacy parser, cached Stage 2 snapshot, candidate logic, or label pipeline is imported.
- Full offline run on Stage 1 snapshot `rv1-20261019T031033900187Z-a468b544` produced dataset `rv2-d52a3f9f1a3de2fe80aa098f`: 1,331 announcement classifications, 3,154 atomic changes, 297,500 review claims, 2,000 game terminology entries, 316 patch episodes, 60 review-window segments, 133,842 memberships, 1,161 episode overlaps, and 662 same-entity temporal ambiguities.
- Game change counts: CS2 976, Dota 2 777, HELLDIVERS 2 1,401, No Man's Sky 0. The latter has Steam announcements without structured body changes; 65 official eligible announcements have external or unverified linked-note content that Stage 2 preserves but does not fetch.
- The deterministic 51-row sample (27 changes and 24 claims) was inspected. Every sampled offset matched its exact original Stage 1 text; zero source-span mismatches. The report documents unresolved entities/aspects, English-heavy polarity, broad summaries, incomplete windows, and the distinction between extraction QA and relevance labeling.
- Validation: **70 tests passed**, Ruff check/format and `git diff --check` passed. The run made zero LLM calls and produced no patch-review pairs or labels.
- See [`stage2/HANDOFF.md`](stage2/HANDOFF.md), the [quality report](../../reports/relevance_v1/stage2/rv2-d52a3f9f1a3de2fe80aa098f/quality_report.md), and [data contracts](stage2/DATA_CONTRACTS.md).

## Stage 3 implementation update

- Added an independent `steam_patch_relevance.stage3` retrieval package and `steam-relevance stage3 retrieve` CLI. It consumes the complete approved Stage 2 dataset, new `rv3-` IDs, and `data/relevance_v1/processed/stage3/` artifacts.
- Implemented BM25 without sentiment-only terms, game-scoped entity/aspect retrieval, multilingual Sentence Transformers dense retrieval using `intfloat/multilingual-e5-small` pinned to revision `614241f622f53c4eeff9890bdc4f31cfecc418b3`, normalized cosine similarity and content/model-revision embedding cache, plus RRF fusion.
- Added configurable pre/post windows and per-change budgets (10/25/50/100), no per-review cap, exact retained-list truncation counts, method-specific diagnostics, hard-case candidates with no labels, and a seeded candidate-free audit sampler carrying complete reviews and full patch change lists.
- The canonical full-snapshot hybrid run is `rv3-cef79b660029d7d5eb703567`: 397 changes in 9 episodes/3 games; 77,220 patch-scoped claims; 3,656,475 possible change/claim comparisons; 62,548 candidates; 34,566 dense candidates absent from BM25; 6,230 entity/aspect candidates absent from BM25; 3,646 unlabelled hard-case rows; and 45 full-list audit packets.
- At budget 100, the methods omit 46,418 BM25 hits, 3,616,775 dense pairs, and 15,185 entity/aspect hits beyond retained lists. This demonstrates large truncation but does not establish that omitted pairs are relevant. The independent audit packets are not yet judged.
- Coverage remains limited: only nine Stage 2 episodes have both verified atomic changes and collected window claims; 53/60 review-window segments are incomplete; No Man’s Sky has no extracted atomic changes. No same-game competing-patch hard case was surfaced in the available memberships.
- Validation: **75 repository tests passed**, Stage 3 fixture suite 5 passed, Ruff check/format and `git diff --check` pass. See [`stage3/HANDOFF.md`](stage3/HANDOFF.md), [`stage3/ARCHITECTURE.md`](stage3/ARCHITECTURE.md), and [`stage3/DATA_CONTRACTS.md`](stage3/DATA_CONTRACTS.md).

## Stage 4 bounded pilot update

- Implemented a fresh provider-neutral `steam-relevance stage4 export/import` workflow under `src/steam_patch_relevance/stage4/`, with new `rv4-` IDs, category 0–3 relevance, separate feature polarity, abstention, prompt/model provenance, and exact quote/source-offset validation. No retired annotation modules or jobs are imported.
- Canonical pilot: `rv4-02c10d1f84099a6d45e2a04a`, based on frozen Stage 3 `rv3-cef79b660029d7d5eb703567`. It labels 24 candidate pairs (8 each from CS2, Dota 2, and HELLDIVERS 2) across hard, semantic-only, specific lexical, and high-fused strata; six candidate-independent audit reviews expose all 348 change-list entries.
- Candidate labels: 14 unrelated, 8 topical-only, 1 plausibly related, 1 clearly attributable. Two category 2–3 pairs span CS2 and HELLDIVERS 2. The audit found two topical-only Dota 2 pairs and no category 2–3 possible retrieval omissions.
- All 30 responses passed validation; no unanswered jobs or evidence failures. The judgments came from one GPT-6 Codex session with no immutable serving revision exposed. No human verified them; the queue is `not_reviewed`.
- The readiness report recommends **not fine-tuning**: only two category 2–3 examples, across two games/patches, and no meaningful evaluation set. Full-scale labeling remains paused for user approval. No training, calibration, collection, or deployment occurred.
- Nine Stage 4 fixture tests pass; the full repository suite passes (**84 tests**). Ruff and `git diff --check` pass. See [`stage4/HANDOFF.md`](stage4/HANDOFF.md), [`stage4/DATA_CONTRACTS.md`](stage4/DATA_CONTRACTS.md), and the [readiness report](../../reports/relevance_v1/stage4/rv4-02c10d1f84099a6d45e2a04a/readiness_report.md).
