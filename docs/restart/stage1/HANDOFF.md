# Stage 1 handoff — raw Steam source collection

Stage 1 is implemented and the bounded pilot collection is materialized. The Stage 1 collector itself stops at raw source ingestion and temporal coverage. Atomic change and review-claim extraction is implemented separately in Stage 2; review/change matching, annotation, and model training have not started.

## What is in place

- Independent `steam_patch_relevance` package and `steam-relevance` CLI, with configuration in `configs/relevance_v1.toml`. The new code does not import the retired `steam_insights` pipeline or read its snapshots, candidate tables, or labels.
- Official API contracts and observed response details in [`STEAM_API_CONTRACTS.md`](STEAM_API_CONTRACTS.md), raw/normalized contracts in [`RAW_DATA_SCHEMA.md`](RAW_DATA_SCHEMA.md), and explicit implementation assumptions in [`ASSUMPTIONS.md`](ASSUMPTIONS.md).
- Exact response payloads stored content-addressed under the git-ignored `data/relevance_v1/raw/blobs/`; request observations and checkpoints are stored separately. Parquet tables, run manifests, and CSV/Markdown coverage reports are regenerated from these raw records.
- Sequential requests, per-run attempt/page budgets, retry/backoff with `Retry-After`, stable source IDs, cursor/date pagination, and checkpoint resumption. Re-running `collect` with the same config continues incomplete review windows from their last saved cursor; it also checks the newest news page for incremental posts. `--refresh` explicitly reacquires completed ranges.
- All encountered announcement feeds are preserved and classified. Candidate selection is conservative triage, not proof that a post is a patch or that it is linked to a build.

## Bounded pilot result

The latest materialized run is `rv1-20261019T031033900187Z-a468b544` (UTC). It contains four seeded games and 28 announcement candidates, seven per game. Across the selected windows, it has 168,292 unique review revisions from a reported eligible population of 723,539 (about 23.3%); 16 of 84 windows are complete. The remaining windows are explicitly partial because collection page budgets were reached. These counts include resumable pages accumulated across earlier Stage 1 run attempts in the same isolated `relevance_v1` checkpoint store. Use the detailed patch-window table for individual counts.

| Game | Official-feed announcements | Selected candidates | Unique review revisions | Reported population coverage | Complete windows |
| --- | ---: | ---: | ---: | ---: | ---: |
| Counter-Strike 2 | 241 | 7 | 71,992 | 14.60% | 0 / 21 |
| Dota 2 | 101 | 7 | 35,988 | 27.93% | 0 / 21 |
| HELLDIVERS 2 | 164 | 7 | 33,478 | 50.23% | 4 / 21 |
| No Man's Sky | 29 | 7 | 26,834 | 77.04% | 12 / 21 |

For all 1,331 announcements, the run found zero empty bodies and zero truncation-heuristic flags; 681 had links, which are preserved. There are zero verified build-linked patches. The selected timestamps are announcement publication times, not verified release times. The `Recommended` vote remains review-level metadata only.

The canonical human-readable report is [`reports/relevance_v1/stage1/latest/report.md`](../../../reports/relevance_v1/stage1/latest/report.md); adjacent CSVs provide game and patch-window coverage. Raw source data and per-run manifests are local-only under the ignored `data/relevance_v1/` tree. The latest local run manifest is `data/relevance_v1/runs/rv1-20261019T031033900187Z-a468b544/manifest.json`.

## Stage 1.5 multilingual audit

The [multilingual audit](MULTILINGUAL_AUDIT.md) confirms that Stage 1 used `languages=["all"]` for every page in the selected patch windows. The [language coverage report](../../../reports/relevance_v1/stage1/latest/language_coverage.md) covers **168,292** unique revisions across 31 Steam API language codes: **58,520 English (34.8%)** and **109,772 recognized non-English (65.2%)**, with no missing, unexpected, or non-string language metadata. All **1,708** selected-window page requests recorded `languages=["all"]`; the latest run's 750 source observations do as well. No language backfill is needed. The 68 incomplete windows are page/request-budget gaps.

Stage 1.5 adds the configurable `[reviews].languages` setting (default `['all']`), rejects an empty list, isolates non-default filter checkpoints, preserves filter-independent review IDs, separates announcement language from review language, and adds nullable detected-language fields without running detection. The existing run's valid raw responses remain untouched. The full details and sources are in [`MULTILINGUAL_AUDIT.md`](MULTILINGUAL_AUDIT.md).

## Continue or inspect collection

After installing dependencies in an environment with package-index access:

```bash
uv sync --locked --all-extras
uv run --all-extras steam-relevance collect --online
uv run --all-extras steam-relevance materialize
uv run --all-extras steam-relevance inspect
```

The collection command exits with status 2 when the run is safely partial due to configured request/page limits; this is expected for the current pilot. Re-run it with the same configuration to continue saved cursors, then materialize and inspect again. Raising `max_pages_per_review_window` in a copied TOML config or using a larger `--max-requests` budget allows more pages in each invocation. Keep raw Steam responses local because review payloads can include SteamID and author playtime metadata.

## Source limitations

- Steam's public Reviews Service is usable without a key but does not document a numeric anonymous quota; the collector uses a conservative local pace/budget and handles 429/transient failures. A review page with no reviews is recognized only when Steam also reports `query_summary.num_reviews=0`.
- The public News API exposes `enddate` pagination, mixed feeds, and full Steam post content when `maxlength=0`; it does not document a patch event-type filter, exact release timestamp, or build linkage. Off-site links are retained but not fetched automatically.
- The initial pilot used curated app IDs because no key was configured then. A later partner-host request returned 403, but the user's suggested public `api.steampowered.com` route succeeded with the `.env` key. The resulting complete game-catalog snapshot contains 194,280 distinct IDs across four pages and includes all four pilot games. See [`CATALOG_FOLLOWUP.md`](CATALOG_FOLLOWUP.md) and the [catalog report](../../../reports/relevance_v1/stage1/catalog/rv1-catalog-20261019T035528Z/report.md). The key was never printed or persisted.
- The live pilot is useful source-coverage evidence, not a complete census. Review population percentages are per selected temporal windows and must not be interpreted as match relevance or sentiment.

## Verification

- The Stage 1 baseline fixture suite had 41 tests. Stage 1.5 extends the full suite to **46 passing tests**, including Unicode round-trip, explicit language filters, per-filter checkpoint resumption, stable IDs across filter modes, and language reporting.
- Ruff lint/format, `uv lock --check`, and `git diff --check` pass.
- Offline materialization regenerated the selected run's Parquet and reports from saved checkpoints. Counts stayed at 4 games, 1,331 announcements, 28 candidates, 168,292 review revisions, and 84 windows; no live Steam requests were made.
- The Stage 1 dependency sync first failed because the environment could not resolve `pypi.org`; the locked sync later succeeded during Stage 1.5. No lockfile or raw source data was discarded.
- The bounded live collection stayed within its configured request budget. No project collection or Jupyter process remains active.

## Next stage boundary

Stage 2 now consumes this frozen source snapshot. Its output counts, extracted-span QA, source gaps, and handoff are documented in [`../stage2/HANDOFF.md`](../stage2/HANDOFF.md). The 28 Stage 1 candidates remain seeds rather than verified build-linked patches. For later evaluation, select adequately covered windows or model collection completeness explicitly. This Stage 1 handoff does not establish review-to-change relevance.
