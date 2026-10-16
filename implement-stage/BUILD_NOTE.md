# Build note — initial data foundation

| Rung | Feature | Acceptance check | Tier | Status |
|---|---|---|---|---|
| F0 | Package/config/CLI reads real CSVs and writes a small source inventory | `uv run steam-insights inventory` | MUST | Passed |
| F1 | Validation, conservative preprocessing, and aggregate exploration | `uv run python -m unittest discover -s tests -v` | MUST | Pending |
| F2 | Starter notebooks, documented full-data runs, output verification | `uv run python scripts/check_data_foundation.py` | MUST | Pending |

## Run record

- Initial checkout: branch `feature/data-inspection`, base commit as in SPEC.md; existing `.env` and architecture documentation preserved.
- F0: installed a project-local uv environment and lockfile; `uv run steam-insights inventory` exited 0 and wrote `reports/data_exploration/source_inventory.json` for the three actual CSVs. No placeholders or model outputs.

## Deferred

- Heading-preserving raw announcement ingestion, supervised labels, train/test splits, models, live API refresh, application serving, and production tooling are separate next steps.

## Blockers

None identified. Existing collector tests require the invalid default snapshot path fix recorded as A-010.
