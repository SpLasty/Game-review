# Data storage boundaries

## New Stage 1 data

`relevance_v1/` is the independent Stage 1 collection root. It contains raw Steam response blobs, resumable checkpoints, per-run manifests, and normalized Parquet snapshots. The entire directory is git-ignored because it can include Steam review text and public author metadata. See [the Stage 1 schema](../docs/restart/stage1/RAW_DATA_SCHEMA.md) before exporting or moving it. The new package does not read the legacy directories below.

## Legacy research data

All data currently in this directory predates the relevance-system restart. It remains available for historical inspection and recovery, with a frozen local copy at `legacy/research/data/`. No Stage 1 code may use it implicitly.

- `processed/steam_30_games/` contains tracked CSV exports, including overlapping full and balanced review populations.
- `raw/steam_30_games/` contains tracked collection manifests; per-game raw payloads may exist only on the original collection machine.
- `raw/pipeline_recovery/`, `interim/`, `datasets/`, and `annotations/llm_jobs/` contain ignored local source observations, Parquet snapshots, candidate tables, reports, and machine annotation evidence. These are preserved in place.
- `annotations/patch_verification.jsonl` is historical patch verification evidence; `annotations/llm_labels.jsonl` and job files are machine silver labels, not human gold.

The file-level pre-cleanup manifest is at `legacy/checkpoints/2026-10-18-pre-restart/research_artifacts_before_cleanup.jsonl`. The new pipeline writes under `data/relevance_v1/` with new identifiers; see `docs/restart/ARCHITECTURE.md`.
