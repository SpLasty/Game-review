# Legacy inventory and recovery

This inventory was made on 2026-10-18 before Stage 1. The abandoned workflow is historical evidence, not a dependency or performance benchmark for the replacement.

## Pre-cleanup state and checkpoint

- Git branch: `feature/data-inspection`, HEAD `062661689173c449caf90a6fb5648976e1596e8b` (one commit ahead of `origin/feature/data-inspection`).
- Working tree before cleanup: nine modified tracked files and two untracked reports. The exact porcelain-v2 status is in `legacy/checkpoints/2026-10-18-pre-restart/status_porcelain_v2.txt`.
- Recoverable checkpoint: `legacy/checkpoints/2026-10-18-pre-restart/head.bundle` contains the complete HEAD history; `tracked_worktree.patch` contains the uncommitted tracked diff; `untracked/` contains the two untracked audits. `checkpoint_manifest.json` records sizes and SHA-256 hashes. `git bundle verify` passed.
- `research_artifacts_before_cleanup.jsonl` records path, size, SHA-256, and tracked status for 13,330 research files (1,233,971,389 bytes) before cleanup. Its SHA-256 is `3728601adc122ffd7372d8ace4a2fb2ab59131eaa37a9409fce249298f07652f`. It includes ignored local data. A frozen local copy of the full `data/` tree is at `legacy/research/data/`; it is Git-ignored to avoid committing large review text and binary snapshots. Neither copy is an off-machine backup.
- `git fsck --connectivity-only` reported no connectivity error. It reported one dangling commit, which is not evidence of a damaged branch.

Recovery of the original code or reports is possible from the bundle plus worktree patch and copied untracked reports. For any file in the artifact manifest, first look at its original path; relocated directories are listed below. The large ignored datasets remain local and have no off-machine copy established by this restart.

## What existed

| Area | Pre-cleanup contents | Current handling |
| --- | --- | --- |
| `src/steam_insights/pipeline/` | Source recovery, announcement parsing, patch verification/windows, lexical candidates, LLM import/export, Parquet snapshots, reports, validation, model loading | Retained as an isolated **legacy research island** because the open Jupyter kernel may use notebook 03; its CLI entry point and helper scripts are retired. The proposed new package must never import it. |
| `src/steam_insights/data/`, `config.py` | Offline CSV exploration, normalization, quality report, and notebook helpers | Retained for notebooks 01/02 and their tests. `quality_report.py` is also imported by the retained legacy source recovery module. |
| `notebooks/01`, `02`, `03` and `configs/data.toml`, `configs/pipeline.toml` | Historical inspection notebooks and configurations | Retained in place to avoid breaking the open kernel. Notebook 03 is explicitly marked legacy. No new pipeline will read these configs by default. |
| `pyproject.toml`, `uv.lock`, `scripts/check_data_foundation.py` | Installed dependencies and notebook smoke check | Retained for the open notebook and existing offline data tests. The package script was removed; dependency pruning waits until the notebook/legacy package is retired. |
| `data/processed/steam_30_games/`, `data/raw/steam_30_games/` | Tracked CSV exports and collection manifests | Preserved in place as historical input. Full and balanced reviews overlap; balanced is not extra observations. Original per-game raw payloads may exist only on the collection computer. |
| Ignored `data/raw/pipeline_recovery/`, `data/interim/`, `data/datasets/`, `data/annotations/` | Recovered observations, Parquet snapshots, candidate tables, silver labels, LLM jobs and audits | Preserved in place and copied to `legacy/research/data/`; file-level hashes are in the checkpoint manifest. No new IDs or labels may be read implicitly from them. |
| `reports/data_quality/`, `reports/data_exploration/` | Tracked and ignored generated reports, including the Sea of Thieves and HELLDIVERS 2 audits | Relocated intact to `legacy/research/reports/`. The two audits remain historical findings only. |
| `docs/*` old workflow/handoff and ignored `docs/architecture/` | Prior architecture, data dictionary, handoff, PDF and build artifacts | Relocated to `legacy/research/docs/` and `legacy/research/architecture/`. |
| `implement-stage/`, `.aris/` | Assumption ledgers, build notes and research traces | Relocated to `legacy/research/implement-stage/` and `legacy/research/traces/`. |
| `proposal/Research_Proposal_Revamped.docx` | Original proposal | Retained in place as background research. |
| `.env`, `.venv`, `.local`, caches | Local secrets/environment and generated caches | Left untouched. `.env` was not copied into the checkpoint. No trained model weights were found in the repository scan. |

The Sea of Thieves 3.8.1 rowwise audit found zero confidently relevant pairs among its 200 lexical candidates; the HELLDIVERS 2 7.1.0 random full-list audit found three confirmed mentions and one concrete lexical candidate cap miss. These are single-model, historical audit findings. They do not establish model accuracy, retrieval recall, or patch causality. Read their archived reports and ignored job artifacts for the qualifications and raw evidence.

## Retired executable surface

Removed `src/steam_insights/cli.py`, `src/steam_insights/__main__.py`, the `steam-insights` package script, all 13 `scripts/data/*.py` stage wrappers/report scripts, four standalone legacy collection/export scripts, two old model/DuckDB examples, and six obsolete collector/pipeline test modules. The stale launcher in the local `.venv/bin/` was also removed. `tests/test_data_preprocessing.py` no longer imports the retired collector or tests its path parser. The old implementation is preserved by the Git checkpoint, and the legacy importable package remains solely for the open notebook dependency.

The old commands `prepare-data`, `pipeline`, `recover-sources`, `backfill-reviews`, `pipeline-validate`, annotation export/import, `inventory`, `profile`, `quality`, and `preprocess` have no installed entry point. The existing `configs/pipeline.toml`, `src/steam_insights/pipeline/`, notebook 03, `data/datasets/`, and `data/annotations/` are visibly legacy and require deliberate manual use. No compatibility wrapper was added.

## Process and schedule audit

The host process scan found no active Steam collection, annotation, training, reporting, or evaluation process; no process was stopped. An interactive `ipykernel_launcher` (PID 585495 at audit time) had cwd `notebooks/`; it was left running because its active notebook could not be identified. The user's crontab was empty. User systemd timers were unrelated (`launchpadlib-cache-clean`, firmware notifier). No repository GitHub Actions or local schedule configuration was found. These observations are a point-in-time check; the user's external schedulers were not audited.

The unresolved cleanup is removal or relocation of the legacy importable package, notebook 03, and `configs/pipeline.toml`. Doing that while the kernel may depend on them could break an active notebook. Close or identify the kernel and approve that specific retirement before deleting them. No other known active application depends on the old pipeline.

The local `uv sync --locked --offline --all-extras` could not rebuild the editable package because `setuptools>=75` was absent from the configured offline cache. The existing environment still passed the retained tests and imports; a future normal sync should refresh installed package metadata. No network fetch was performed during Stage 0.
