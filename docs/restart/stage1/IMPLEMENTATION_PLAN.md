# Stage 1 implementation and verification plan

## Ordered implementation

1. **Verify contracts** — cite official Steamworks pages; confirm live wrapper and fields with bounded requests; separate documented behavior from observed payloads.
2. **Create isolated package and configuration** — `steam_patch_relevance`, `configs/relevance_v1.toml`, and `steam-relevance`; no import of `steam_insights`, archived data, prior candidate tables, or silver labels.
3. **Implement public-source clients** — Steam News full-content paging by `enddate` with newest-watermark polling; Reviews Service cursor paging with bounded date intervals; optional keyed Store catalog paging; sequential pacing, 429/transient retries, sanitized configuration, attempt budgets.
4. **Persist evidence** — exact raw page bytes by SHA-256, append-only run observations, atomic checkpoints, stable source and review revision identifiers.
5. **Select a small pilot** — preserve and classify every encountered announcement; select up to seven candidates per game by a versioned publisher-feed/title/body rule, reporting the evidence and the fact that this is not build verification.
6. **Collect temporal windows** — publication-time fallback anchor, inclusive before/early/late date ranges, resume page cursors, deduplicate review revisions, and store many-to-many window membership.
7. **Materialize and inspect** — Parquet source/coverage tables, CSV/Markdown coverage, DuckDB `inspect`, collection manifest with code/config fingerprints.
8. **Test and bounded live run** — mock fixtures for pagination, boundaries, idempotence, source classification, malformed fields, retries, partial-resume behavior and duplicates; then bounded Steam collection and report review.

## Completion criteria

- The package, CLI, and config are independent from the retired `steam_insights` collectors and use only the `relevance_v1` namespace.
- A repeated fixture run produces stable row IDs and content hashes; checkpoints resume without dropping prior raw pages.
- News items from other feeds/promotions remain in the source table and do not become patch candidates solely because they exist.
- Review pages use the returned cursor and stop only at an empty page or an explicit partial/error condition.
- Review window boundaries and overlap memberships are covered by tests.
- Every output report states which windows are complete and identifies candidate patches as unverified when release/build evidence is unavailable.
- Bounded live run does not exceed the configured HTTP-attempt budget; secrets are never written to files or logs.
- Tests and static checks pass; Stage 1 stops before change extraction, pair generation, LLM annotation, or training.

## Completion record

Stage 1 is complete. The fixture suite passed (41 tests); Ruff lint/format, `uv lock --check`, and `git diff --check` passed. The bounded live review run materialized 28 announcement candidates over four seeded games, 168,292 review revisions, and 16 complete of 84 review windows. A separate `GetAppList` follow-up collected a complete 194,280-row game catalog snapshot and verified all four pilot IDs. The review run is deliberately partial under its page budgets; see [`HANDOFF.md`](HANDOFF.md), [`CATALOG_FOLLOWUP.md`](CATALOG_FOLLOWUP.md), and [`reports/relevance_v1/stage1/latest/report.md`](../../../reports/relevance_v1/stage1/latest/report.md). A locked dependency sync was attempted but could not reach PyPI to fetch `setuptools>=75`, so rerun it on a network-enabled machine before installing the console script.

