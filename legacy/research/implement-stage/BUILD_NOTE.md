# Build note — initial data foundation

| Rung | Feature | Acceptance check | Tier | Status |
|---|---|---|---|---|
| F0 | Package/config/CLI reads real CSVs and writes a small source inventory | `uv run steam-insights inventory` | MUST | Passed |
| F1 | Validation, conservative preprocessing, and aggregate exploration | `uv run python -m unittest discover -s tests -v` | MUST | Passed |
| F2 | Starter notebooks, documented full-data runs, output verification | `uv run python scripts/check_data_foundation.py` | MUST | Passed |

## Run record

- Initial checkout: branch `feature/data-inspection`, base commit as in SPEC.md; existing `.env` and architecture documentation preserved.
- F0: installed a project-local uv environment and lockfile; `uv run steam-insights inventory` exited 0 and wrote `reports/data_exploration/source_inventory.json` for the three actual CSVs. No placeholders or model outputs.
- F1: all 38 tests passed, including the 15 original tests. Full-data `profile` and `preprocess` exited 0, producing aggregate reports/plots and 73,336 all-review, 30,788 long-text and 3,445 announcement Parquet rows. Added regression coverage for differing game/date coverage and the Python-versus-Arrow Unicode regex discrepancy found during the full-data run.
- F2: both starter notebooks' Python cells executed against the actual data, and the verification command exited 0. Compared all review/announcement source strings and recommendation votes after Parquet round-trip; checked the long-text view and verified all three source fingerprints remained unchanged. This checks Python cells, not Jupyter browser/kernel integration. Ruff checks and formatting passed. Report plotting uses independent Agg canvases without switching an interactive notebook's global backend.

## Deferred

- Heading-preserving raw announcement ingestion, supervised labels, train/test splits, models, live API refresh, application serving, and production tooling are separate next steps.

## Data meaning and interfaces

The full decisions are in [ASSUMPTIONS.md](ASSUMPTIONS.md), with ASK mode `never` and default-sourced choices declared before their implementation. In particular:

- **A-001:** count the full English-review population; compare the overlapping balanced file separately.
- **A-002:** preserve source text, case, negation, numbers and emoji; normalize NFC/whitespace only in added columns, without inferred headings.
- **A-003:** keep short, edited and negative reviews; create a separate configurable eligibility view with no sentiment balancing.
- **A-004:** heuristic patch/keyword flags are not gold labels, and Steam recommendation is not target sentiment.
- **A-005:** report invalid data and duplicate keys; fail preprocessing instead of silently dropping/repairing records; optional unknowns remain nullable.
- **A-006:** export times describe latest saved state, not historical edits or causal patch effects.
- **A-011:** Python Unicode word runs match the collector; Arrow regex semantics cannot substitute for that definition.

Interface choices A-007–A-010 define the src package/CLI/TOML paths, separate generated outputs, empty-output notebook workflow, and compatible safe nested collector snapshot paths. No live placeholders survive.

## Assumption review

One fresh GPT-6-Astra xhigh review found zero undeclared assumptions and zero stale rows. The response is saved verbatim in `SILENT_ASSUMPTION_SWEEP.json` and the prompt/response trace in `.aris/traces/research-implement-feature/2026-10-16_run01/`. This is **same-family / provisional** semantic review, not a cross-family correctness guarantee. The execution checks independently passed: the spine runs and every MUST rung's check passed. No model-quality claims were evaluated.

## Blockers

None. The initial collector default-path defect was fixed as A-010 and all 15 original tests pass within the 38-test suite.
