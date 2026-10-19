# Steam patch relevance restart

The repository is restarting around a patch-grounded question: does a Steam review discuss a specific change in a specific update? Stage 0 preserved the old research evidence and retired the previous collector/label workflow. Stage 1 builds an independent source collection package in `steam_patch_relevance`; it does not import the legacy `steam_insights` code or read the archived data.

## Stage 1 collection

Install the locked project environment, then collect the four curated pilot app IDs:

```bash
uv sync --locked --all-extras
uv run --all-extras steam-relevance collect --online
uv run --all-extras steam-relevance materialize
uv run --all-extras steam-relevance inspect
```

The `--online` flag is required for live Steam requests. `--max-requests N` overrides the configured HTTP-attempt budget; each retry attempt counts toward it. Re-running resumes incomplete checkpoints and checks the newest Steam News page for new posts. A safe partial collection exits with status 2 when configured page/request limits are reached; rerun to continue from saved cursors. Use `--refresh` to reacquire previously completed source ranges/windows. `materialize` rebuilds tables/reports offline from already collected raw blobs and checkpoints.

Raw response bytes, hashes, checkpoints, and manifests go under the git-ignored `data/relevance_v1/`. Normalized Parquet tables are written per run; game, patch-window, and multilingual coverage reports go to `reports/relevance_v1/stage1/`. The review API defaults to `languages = ["all"]` in `configs/relevance_v1.toml`; you can set a list of Steam API codes such as `["german", "schinese"]`. Do not use an empty list: Steam defines it as English-only. Filter-specific checkpoints keep explicit language runs separate, while stable review revision IDs remain the same across collection filters. Run `inspect` with DuckDB to view the latest local counts. A Steam Web API key is not needed for the seeded pilot. To load a local ignored `.env` for optional catalog discovery, run `uv run --env-file .env --all-extras steam-relevance catalog --online --max-pages 3 --max-results 50000`. The public URL route succeeded in the bounded live run; details are in [`CATALOG_FOLLOWUP.md`](docs/restart/stage1/CATALOG_FOLLOWUP.md).

The source contract, schema, assumptions, and Stage 1 handoff are in [`docs/restart/stage1/`](docs/restart/stage1/). The [Stage 1.5 multilingual audit](docs/restart/stage1/MULTILINGUAL_AUDIT.md) explains the all-language request evidence and coverage results. API limitations matter: public Steam News does not provide a documented event-type/build link or exact release timestamp, and `GetAppList` requires a key. Patch candidates therefore remain explicitly unverified and use announcement publication time as the review-window anchor. The workflow stops before generating patch-review pairs, relevance labels, or model training data.

## Stage 2 extraction

Build atomic changes, review claims, announcement classifications, game-specific terminology, and temporal tables from a frozen Stage 1 snapshot:

```bash
uv run --all-extras steam-relevance stage2 extract --source-run rv1-20261019T031033900187Z-a468b544
```

This step is offline. It preserves original text and exact source spans, extracts only structured announcement changes, and does not assign patch relevance or create pairs/labels. Outputs are versioned under `data/relevance_v1/processed/stage2/<dataset-id>/`; QA and coverage reports are under `reports/relevance_v1/stage2/<dataset-id>/`. The CLI prints both paths. See [`Stage 2 handoff`](docs/restart/stage2/HANDOFF.md) for the current run and known gaps, and [`Stage 2 data contracts`](docs/restart/stage2/DATA_CONTRACTS.md) for table grain and field meaning.

## Stage 3 hybrid retrieval

Rank each atomic patch change against review claims in the configured time window, then inspect the independent full-list audit packets:

```bash
uv run --all-extras steam-relevance stage3 retrieve \
  --source-dataset rv2-d52a3f9f1a3de2fe80aa098f \
  --budgets 10 25 50 100 --before-days 14 --after-days 14 \
  --dense-revision 614241f622f53c4eeff9890bdc4f31cfecc418b3
```

This full command uses BM25, multilingual dense embeddings, and per-game entity/aspect retrieval. Install dependencies with `uv sync --locked --all-extras`; the first run downloads the pinned model. The offline smoke mode explicitly skips dense scoring:

```bash
uv run --all-extras steam-relevance stage3 retrieve \
  --source-dataset rv2-d52a3f9f1a3de2fe80aa098f --no-dense
```

Stage 3 writes versioned candidates and diagnostics under `data/relevance_v1/processed/stage3/`, with run reports under `reports/relevance_v1/stage3/`. Candidate scores are retrieval evidence only; no relevance labels or recall estimates are produced. See [`Stage 3 handoff`](docs/restart/stage3/HANDOFF.md), [architecture](docs/restart/stage3/ARCHITECTURE.md), and [data contracts](docs/restart/stage3/DATA_CONTRACTS.md).

## Stage 4 bounded silver-label pilot

Stage 4 exports provider-neutral JSONL jobs for specific change/claim pairs plus a separate, candidate-independent full-list audit. The current 24-pair/6-review pilot is complete as `rv4-02c10d1f84099a6d45e2a04a`; see its [readiness report](reports/relevance_v1/stage4/rv4-02c10d1f84099a6d45e2a04a/readiness_report.md) and [handoff](docs/restart/stage4/HANDOFF.md). The pilot contains 24 LLM-silver candidate judgments and two topical-only full-list findings. It is not ready for fine-tuning, and full-scale labeling awaits approval.

To reproduce the same bounded export:

```bash
uv run --all-extras steam-relevance stage4 export \
  --source-dataset rv3-cef79b660029d7d5eb703567 \
  --candidate-pairs 24 --audit-reviews 6 --seed stage4-pilot-v5
```

The response import requires a JSONL file whose entries echo the exported `input_id`, `prompt_version`, and `prompt_sha256`, plus provider/model/version provenance. The complete schema and validation rules are in [`Stage 4 data contracts`](docs/restart/stage4/DATA_CONTRACTS.md). LLM labels remain silver unless a person actually reviews them; the pilot's inspection queue is explicitly unreviewed.

## Historical research

Historical handoffs, candidate tables, labels, and archived source data remain under `legacy/` and the original `data/` paths. They are evidence only; the new pipeline uses separate IDs and paths. The retained `steam_insights` package and notebooks remain isolated while an interactive notebook kernel may depend on them.
