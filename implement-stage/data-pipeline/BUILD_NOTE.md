# Build record — data pipeline

Effort: balanced. ASK: never. Assurance: draft. Existing quality-report working tree is preserved.

| Rung | Feature | Acceptance command | Tier | Status |
| --- | --- | --- | --- | --- |
| F0 | Configured entry point to source manifest | `uv run steam-insights pipeline --stage inventory` | MUST | passed |
| F1 | Explicit schemas, normalized review revisions/passages, Parquet/DuckDB | `uv run steam-insights pipeline --stage reviews` | MUST | passed |
| F2 | Structured announcements, evidence, changes, bounded source recovery | `uv run steam-insights pipeline --stage announcements` | MUST | passed |
| F3 | Windows, candidates, split/annotation/model exports and atomic snapshots | `uv run steam-insights pipeline` | MUST | passed |
| F4 | Invariants, actual snapshot, documentation and handoff | `uv run steam-insights pipeline-validate` and unittest suite | MUST | passed |

## Run record

## Deferred

None of the approved implementation stages deferred. Human annotations and unavailable historical content are data prerequisites, not implemented labels.

## Blockers

None recorded at start.

F0: `uv run steam-insights pipeline --stage inventory` exited 0; source inventory written. Dependencies installed after sandbox DNS failure using approved escalation.

F1: full review stage exited 0: 73,336 current reviews/revisions, 0 quarantined, 479 independent language warnings, 135 near-duplicate candidate pairs, no saturated buckets. All 44 unit tests pass. One test initially assumed row ordering; fixed to select by ID. Earlier inventory command passed.

F2: announcement stage passed on original and recovered data. 12 public requests recovered all 35 prioritized IDs; 1,107 structured current posts, 237 source-confirmed patch posts. All 50 tests passed; cached review and announcement stages passed. A regression caught future-tense `will be fixed`; rule now preserves planned status and explicit negation.

F3: `steam-insights prepare-data` completed the actual offline workflow, published snapshot b1a7c5e1038c0b4a50d32e7c7b1800c060466c456bd66a13c38e2f860e8ce5f7, passed 175 dataset gates, refreshed reports and exported a development annotation queue. The SQL temporal check caught a real America/Denver daylight-saving discrepancy; all SQL interval arithmetic now explicitly uses UTC, with a regression test. All 18 new pipeline tests pass. No human labels were invented.

F4: `uv run --all-extras steam-insights prepare-data` exited 0 on the actual repository data, published snapshot f6ed010d3a378a5a12a4d9e502a41aae540c77b863356eae972189164cec0240, passed 175 dataset gates, refreshed the combined quality report and exported a development annotation queue. `uv run --all-extras python -m unittest discover -s tests -v` passed 62 tests; Ruff passed. Both example scripts and all Python cells in notebook 03 executed against the actual published tables. Original three CSV SHA-256 values remain unchanged.

The final snapshot contains 73,336 current reviews, 3,638 current announcements, 32,759 structural changes and 27,684 unlabeled candidate pairs. There are 249 automatically source-confirmed patch posts and six assistant source-reviewed posts; 15 confirmed/reviewed windows pass the availability screen. No human training annotations exist.

Final regressions cover Valve BBCode image/list/table markup, canonical annotation context and preservation, resumable review cursors, advancing beyond exhausted sparse windows, title/heading status scope including Workarounds, stable identity despite operational timestamp changes, and failure on ambiguous announcement revisions. One intermediate build was intentionally refused after source code changed during processing; it preserved the preceding pointer and the subsequent unchanged-source build succeeded.

Historical review backfill is implemented and tested with simulated responses but has not been run against Steam here. The handoff command `uv run --all-extras steam-insights prepare-data --online` performs it under the shared request budget. Source-only recovery already ran using 12 public requests. Missing human labels, historical revisions, deployment times and source gaps remain documented prerequisites. No live stubs or pending implementation rungs remain.

Repeated offline `prepare-data` exited 0, reused the same final snapshot, preserved its existing annotation queue, and completed report refresh. Both the orchestration journal and publication validation record 175 passed gates.

Assumption sweep: round one found four undeclared semantic defaults and three stale rows. P27-P33 document these choices; title/status context, conflicting observation handling and operational metadata identity were corrected and covered by regressions. Round two returned zero undeclared assumptions and zero stale rows. The raw replies are saved alongside this note; review independence is **same-family**, acceptance **provisional**. This is not a claim of independent correctness. All five MUST rung checks passed.
