# Initial data workflow

This guide covers the original CSV exploration commands. For the complete implemented workflow, including source recovery, structured documents, candidate matching, annotations and model inputs, see [data_pipeline.md](data_pipeline.md). Neither workflow trains a model or establishes patch causality.

## Run order

1. `uv sync --locked --extra dev` creates the local environment from the committed lockfile.
2. `uv run steam-insights inventory` records source filenames, sizes, columns, row counts, and SHA-256 fingerprints.
3. `uv run steam-insights profile` validates the source tables and produces exploratory tables/plots.
4. `uv run steam-insights quality` refreshes the profile and writes a combined data-quality report, per-game summary, and patch-window table under `reports/data_quality/`.
5. `uv run steam-insights preprocess` writes a typed snapshot to the separate interim directory. It fails if required data is invalid; warnings such as empty text do not remove a valid recommendation.
6. `uv run python -m unittest discover -s tests -v` runs collector and data checks. `uv run python scripts/check_data_foundation.py` executes the notebook cells and verifies real outputs.

All commands run from the project root. `python -m steam_insights profile` is an equivalent module entry point after installation. No credentials or internet access are needed after dependencies are installed.

## What to inspect

| Artifact | Question |
|---|---|
| `population_comparison.csv` | How much does the capped long-review selection change recommendation rates? |
| `reviews_by_game.csv` | Which games dominate? What dates, short-text and edited-review counts differ? |
| `reviews_by_day.csv` | Which dates have observations? Which first/last days may be partial? |
| `review_lengths.csv` | Are short or empty reviews common? Does recommendation vary with length? |
| `missing_values.csv` | Is a field unknown, empty, or consistently absent? |
| `announcements_by_game.csv` | Which games have sparse or capped announcement history? |
| `profile.json` | Are IDs/timestamps/booleans valid? What are the existing verification/branch flags? |
| `figures/*.png` | Visualize game volume, lengths, population differences and the calendar coverage matrix. |
| `data_quality/data_quality_report.md` | What source quality checks passed, and which patch-post windows have enough observed text reviews? |
| `data_quality/patch_window_quality.csv` | Per candidate/verified post, what are the pre/post review counts, active dates, and coverage assessment? |

Counts describe the observed convenience sample, not all Steam users. A zero in the heatmap means no saved observation on that day; neither zero nor a nonzero count establishes complete API coverage. The legacy ten-word selection and a configurable new threshold are separate policies.

The patch-window report uses the full review export and a symmetric 14-day window around announcement publication time. A window passes its exploratory screen at 30 text-eligible reviews over at least 7 distinct review dates on each side, with the full window inside the game's observed review-date bounds; 100 reviews per side is marked as stronger coverage. These configurable-in-code screening thresholds do not establish statistical power or complete source coverage. Unverified candidates that pass the coverage screen still need human confirmation as actual patch posts. The announcement publication date may differ from the effective release time.

## Preprocessed tables

`reviews.parquet` retains every validated source row. Existing fields remain, with app IDs as integers, review IDs as strings, booleans parsed explicitly, nullable playtime, and timezone-aware UTC dates. String IDs preserve Steam's large identifiers without floating-point conversion. In particular, `False` is parsed as false rather than evaluated as a truthy nonempty string.

| Added column | Meaning |
|---|---|
| `review_text_clean` | NFC Unicode and whitespace normalization; source `review_text` is untouched. |
| `word_count_computed` | Python Unicode word runs, matching the collector. Numbers can count as words. |
| `analysis_text_eligible` | Word count reaches the configured minimum and language matches configuration. |
| `is_unedited_snapshot` | Creation and recorded update timestamps match; a proxy, not edit history. |
| `review_date_utc` | UTC creation date for descriptive grouping. |
| `text_normalization_version` | Named cleaning convention, currently `nfc_whitespace_v1`. |

`reviews_text.parquet` is a view of rows with `analysis_text_eligible = true`, without a new per-game cap. At the default threshold it contains 30,788 rows, so it intentionally differs from the existing 30,000-row balanced export. Changing `minimum_words` changes this view, not the preserved all-review population or legacy eligibility fields.

`announcements.parquet` preserves the exported `text`, source URL, title, candidate flags and verification flags. It adds `text_clean`, normalization version, and `heading_context_available = false`. Flattened CSV text does not support reconstructing original headings or inventing release/fix status. Missing optional booleans remain unknown, rather than silently becoming false.

An example such as “not fixed in 1.2.3 🎮” keeps its negation, version and emoji. Do not reuse the legacy lexical-overlap stop-word list for status or sentiment: it removes “not” and “no”. The complete pipeline explicitly defines evidence offsets against versioned canonical documents, never interchangeably against original markup; see its data dictionary.

## Contracts and failures

Required review fields: `appid`, `game`, `review_id`, `review_text`, `language`, `created_utc`, `updated_utc`, `timestamp_created`, `timestamp_updated`, and `recommended`. Required announcement fields: `appid`, `game`, `gid`, `title`, `text`, `date_utc`, `timestamp`, and `source_url`.

The validator checks positive IDs, unique `(appid, source ID)` keys, parseable timestamps, agreement between ISO and epoch values, update order, configured language and explicit boolean values. Known optional playtime/count columns must be numeric when populated. Empty text is retained with a warning so recommendation statistics do not silently change. Repeated wording is reported for inspection; it is not proof of duplicate users or review manipulation and is not deleted.

Profiling writes diagnostics even when required columns are missing, then returns a nonzero CLI status. Preprocessing writes `preprocessing_validation.json` and stops on errors before replacing an existing prepared snapshot. It stages all Parquet files before replacing destinations and writes the manifest last. This is a single-writer local workflow; it is not a transactional multi-user publication system. Do not run concurrent writers into the same output directory.

## Versioning and local artifacts

Git tracks source, config, notebooks, tests and the uv lockfile. Generated interim data, report outputs, `.venv`, `.env` and notebook checkpoints are ignored. Original committed CSVs remain where they were; there is no destructive source migration in this slice. Keep notebook outputs empty before committing because sample rows may contain review text.

The manifest records source hashes, package/schema/normalization versions, configured policy, and row counts. Ordering is deterministic, but generation timestamps change on rerun. DVC tracking and MLflow experiments are later additions; no service or cloud account is required now.

## Continue with the implemented pipeline

Run `uv run --all-extras steam-insights prepare-data --online` to resume source recovery and historical review collection, then build and validate model inputs. Inspect [the enriched quality report](../reports/data_quality/pipeline/report.md), follow [the annotation guide](../data/annotations/README.md), and use the [pipeline guide](data_pipeline.md) for independent stages and model loading.
