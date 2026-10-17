# Steam Patch Insights

Analyze Steam reviews and developer announcements to build evidence-backed patch reports. This branch provides the processing pipeline through versioned model inputs: source recovery, normalization, structured changes, patch evidence, quality reports, candidate pairs and human annotation contracts. Model training and the application come later.

## Complete data preparation

From `Game-review/`:

```bash
uv sync --locked --all-extras
uv run --all-extras steam-insights prepare-data --online
```

This resumes bounded Steam collection, builds Parquet tables and DuckDB views, validates the published snapshot, refreshes reports and exports a development annotation queue. Repeat to continue collection beyond the per-run request budget. Omit `--online` to process local inputs only. Existing annotation queues are preserved.

Read the [pipeline guide](docs/data_pipeline.md), [completion and handoff record](docs/data_pipeline_status.md), [data dictionary](docs/data_dictionary.md), and [current readiness report](reports/data_quality/pipeline/report.md). Source confirmation identifies patch-note posts; human labels and sufficient historical review coverage remain separate requirements.

## Quick start

Use Python 3.11+ and [uv](https://docs.astral.sh/uv/). Run these commands from the repository root (`Game-review/`):

```bash
uv sync --locked --extra dev
uv run steam-insights inventory
uv run steam-insights profile
uv run steam-insights quality
uv run steam-insights preprocess
uv run python -m unittest discover -s tests -v
```

These commands use the existing CSVs and make no Steam API calls. Configuration is in [configs/data.toml](configs/data.toml). Pass `--config path/to/data.toml` after a command to use another configuration. Alternatively, install with `python -m pip install -e ".[dev]"` inside your own virtual environment and run the CLI directly.

Start with the generated [exploration report](reports/data_exploration/README.md) and the combined [data-quality report](reports/data_quality/data_quality_report.md), then the two notebooks:

```bash
uv sync --locked --extra dev --extra notebooks
uv run --extra notebooks jupyter lab
```

1. [01_data_exploration.ipynb](notebooks/01_data_exploration.ipynb): populations, validation, missing values, time coverage, edits, lengths, and announcement flags.
2. [02_preprocessing.ipynb](notebooks/02_preprocessing.ipynb): prepare Parquet tables, inspect types and eligibility, and check source-text preservation.
3. [03_pipeline_duckdb.ipynb](notebooks/03_pipeline_duckdb.ipynb): query the published dataset, inspect patch periods, and load model input batches.

Use the project environment as the notebook kernel. Committed notebooks have empty outputs; clear outputs before sharing to avoid publishing review excerpts accidentally.

## Repository layout

```text
configs/data.toml                 Input/output paths and text-eligibility policy
src/steam_insights/
  cli.py                         inventory / profile / preprocess / quality commands
  config.py                      TOML configuration and output-path protection
  data/
    io.py                        BOM-safe CSV loading and input fingerprints
    validation.py                Schema, IDs, booleans and timestamp checks
    text.py                      Shared Unicode counting and light text cleaning
    preprocessing.py             Typed tables and explicit derived columns
    exploration.py               Aggregate tables, plots and exploration report
    quality_report.py            Review validation and patch-window coverage report
    pipeline.py                  Validated CSV-to-Parquet workflow
notebooks/                       Exploration and preprocessing walkthroughs
scripts/                         Existing collection/export scripts; workflow smoke check
tests/                           Existing collector tests plus data-contract tests
data/processed/steam_30_games/    Existing CSV snapshot, treated as immutable input
data/interim/steam_30_games/      Generated Parquet and manifest (Git-ignored)
reports/data_exploration/         Generated aggregate reports/plots (Git-ignored)
reports/data_quality/             Combined quality report and patch-window tables
docs/data_workflow.md             Data contracts, decisions and next steps
proposal/                        Original research proposal
implement-stage/                 Build decisions and verification record
pyproject.toml / uv.lock          Package metadata and locked dependencies
```

The new `src/steam_insights/pipeline/` modules implement the complete processing flow; small stage wrappers live in `scripts/data/`, and model/DuckDB examples live in `examples/`. See the pipeline guide for their responsibilities.

## Existing data and interpretation

- `all_english_reviews.csv`: 73,336 reviews; use this population for collected recommendation statistics, including short reviews.
- `balanced_reviews.csv`: 30,000 reviews, capped at 1,000 per game with at least ten words. It overlaps the full file and has no positive/negative sentiment quota. Do not concatenate it with the full file as extra observations.
- `developer_announcements.csv`: 3,445 posts, including news and marketing. Existing patch/keyword flags are heuristics, not gold labels.

The collection began on October 14, 2026; review creation dates span January 14–October 14. About 77% were posted in September or October because collection requested recent reviews and stopped once each game met its target. An edited review's text and vote represent the exported latest state, not its original state.

Raw per-game payloads and resumable state live on the collection machine under `data/raw/steam_30_games/` and are excluded from Git. This checkout may contain only their manifests. The CSVs flatten announcement formatting; they cannot recover the original heading hierarchy.

## Outputs and checks

`profile` writes `profile.json`, per-game/day counts, length bins, missing-value tables, population comparisons, announcement coverage, and four PNG plots. `quality` refreshes those artifacts and writes `reports/data_quality/data_quality_report.md`, `patch_window_quality.csv`, and `game_quality_summary.csv`. Patch windows use 14 days before and after the announcement publication timestamp; the report distinguishes manually verified patches from heuristic candidates and applies transparent review-count/day thresholds. Validation failures still produce diagnostics and a nonzero exit status. Reports use aggregate counts and public announcement metadata, not copied review text.

`preprocess` writes all valid reviews to `reviews.parquet`, the configurable long-text view to `reviews_text.parquet`, and posts to `announcements.parquet`. It preserves original text and adds cleaned text; no stop words, negation, punctuation, versions or emoji are removed. Invalid required fields or duplicate IDs stop preprocessing instead of silently dropping rows. The manifest records input checksums, policy and output counts.

```bash
uv run --extra dev ruff check
uv run --extra dev ruff format --check src tests/test_data_preprocessing.py scripts/check_data_foundation.py
uv run python scripts/check_data_foundation.py
```

The final command executes both notebooks' Python cells against the actual snapshot and verifies the generated Parquet data against the unchanged source inputs. It does not require Jupyter to run. See [the workflow guide](docs/data_workflow.md) for schemas and limitations.

## Legacy collection

`scripts/run_collection.ps1` runs the original network collection, analysis and balanced export on a collection machine. It can rewrite the legacy CSV exports. The new pipeline does not invoke it; `prepare-data --online` saves separate immutable recovered observations and leaves those CSVs unchanged.
