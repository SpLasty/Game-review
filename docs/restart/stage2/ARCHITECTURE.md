# Stage 2 extraction architecture

Stage 2 consumes only a selected Stage 1 normalized snapshot under `data/relevance_v1/normalized/`. Its import boundary is `steam_patch_relevance.stage2`; it does not import the retired `steam_insights` package, archived labels, legacy candidate tables, or old parsing code.

```text
Stage 1 announcements.parquet ──> multi-label announcement classifier
             │                         │
             │                         └──> announcement_classifications.parquet
             └──> Steam BBCode/HTML block parser ──> patch_changes.parquet

Stage 1 review_revisions.parquet ──> exact sentence/contrast spans ──> review_claims.parquet
             │
             └──> per-game term frequency and patch-name resources ──> game_terminology.parquet

Stage 1 patch candidates/windows/memberships ──> rv2 patch episodes, review windows,
                                                   memberships, and overlap tables

All outputs ──> run manifest + reproducible stratified QA sample + quality report
```

The central rows are one atomic developer change or one review claim. No cross-dataset join, candidate pair, relevance decision, or training label is created. Review-window membership represents time only.

The deterministic parser handles explicit Steam list items, nested lists, headings, bold entity labels, and inline HTML/BBCode while maintaining character offsets into the original announcement body. A change row is emitted only from a structured list item with an explicit change predicate. Narrative prose is left unextracted for review or an optional future provider. The optional provider interface in `stage2/llm_interface.py` has no implementation, credentials, or live calls in this stage; every proposed offset must be in bounds and source-verifiable.

Review claims are split at sentence boundaries and contrastive connectors such as “but” and “however.” They retain original review-revision identity and exact Unicode character offsets. The complete review remains in the source Stage 1 table and can be recovered by `review_revision_id`; Stage 2 does not duplicate full review bodies per claim. Polarity and aspect are conservative rule outputs, with unknown values left null. Single-token vocabulary matching is case-sensitive to reduce ordinary-word false matches; multiword and identifier aliases can match case-insensitively. Steam's overall recommendation is not copied into claim polarity.

Announcements from all collected feeds remain in the classification table. Only source rows identified by Stage 1 as the Steam developer-announcement feed can become patch episodes. The `patch_eligible` flag remains a rule-based triage decision, not proof of build linkage. Stage 2 extracts linked URLs from Stage 1 metadata and the announcement body, including BBCode/HTML links, but does not fetch external changelogs; linked URLs and note-completeness states remain visible.

## CLI

```bash
uv run steam-relevance stage2 extract
uv run steam-relevance stage2 extract --source-run rv1-20261019T031033900187Z-a468b544
uv run steam-relevance stage2 extract --limit-reviews 100
```

The default processes all review revisions. `--limit-reviews` is for bounded smoke runs and marks the dataset partial. Extraction is offline. A deterministic dataset ID is derived from the source-table hashes, extraction/schema versions, sample seed, and any review limit.

Outputs are written to `data/relevance_v1/processed/stage2/<dataset-id>/`; the report is written to `reports/relevance_v1/stage2/<dataset-id>/quality_report.md`. These local data paths are git-ignored. The manifest records source hashes, versions, row counts, the sample seed, and the no-pairs/no-label boundary.
