# Build note — initial data foundation

| Rung | Feature | Acceptance check | Tier | Status |
|---|---|---|---|---|
| F0 | Package/config/CLI reads real CSVs and writes a small source inventory | `uv run steam-insights inventory` | MUST | Passed |
| F1 | Validation, conservative preprocessing, and aggregate exploration | `uv run python -m unittest discover -s tests -v` | MUST | Passed |
| F2 | Starter notebooks, documented full-data runs, output verification | `uv run python scripts/check_data_foundation.py` | MUST | Pending |

## Run record

- Initial checkout: branch `feature/data-inspection`, base commit as in SPEC.md; existing `.env` and architecture documentation preserved.
- F0: installed a project-local uv environment and lockfile; `uv run steam-insights inventory` exited 0 and wrote `reports/data_exploration/source_inventory.json` for the three actual CSVs. No placeholders or model outputs.
- F1: all 38 tests passed, including the 15 original tests. Full-data `profile` and `preprocess` exited 0, producing aggregate reports/plots and 73,336 all-review, 30,788 long-text and 3,445 announcement Parquet rows. Added regression coverage for differing game/date coverage and the Python-versus-Arrow Unicode regex discrepancy found during the full-data run.

## Deferred

- Heading-preserving raw announcement ingestion, supervised labels, train/test splits, models, live API refresh, application serving, and production tooling are separate next steps.

## Blockers

None identified. Existing collector tests require the invalid default snapshot path fix recorded as A-010.
