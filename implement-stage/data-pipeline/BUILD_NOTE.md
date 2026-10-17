# Build record — data pipeline

Effort: balanced. ASK: never. Assurance: draft. Existing quality-report working tree is preserved.

| Rung | Feature | Acceptance command | Tier | Status |
| --- | --- | --- | --- | --- |
| F0 | Configured entry point to source manifest | `uv run steam-insights pipeline --stage inventory` | MUST | passed |
| F1 | Explicit schemas, normalized review revisions/passages, Parquet/DuckDB | `uv run steam-insights pipeline --stage reviews` | MUST | passed |
| F2 | Structured announcements, evidence, changes, bounded source recovery | `uv run steam-insights pipeline --stage announcements` | MUST | passed |
| F3 | Windows, candidates, split/annotation/model exports and atomic snapshots | `uv run steam-insights pipeline` | MUST | passed |
| F4 | Invariants, actual snapshot, documentation and handoff | `uv run steam-insights pipeline-validate` and unittest suite | MUST | pending |

## Run record

## Deferred

None of the approved implementation stages deferred. Human annotations and unavailable historical content are data prerequisites, not implemented labels.

## Blockers

None recorded at start.

F0: `uv run steam-insights pipeline --stage inventory` exited 0; source inventory written. Dependencies installed after sandbox DNS failure using approved escalation.

F1: full review stage exited 0: 73,336 current reviews/revisions, 0 quarantined, 479 independent language warnings, 135 near-duplicate candidate pairs, no saturated buckets. All 44 unit tests pass. One test initially assumed row ordering; fixed to select by ID. Earlier inventory command passed.

F2: announcement stage passed on original and recovered data. 12 public requests recovered all 35 prioritized IDs; 1,107 structured current posts, 237 source-confirmed patch posts. All 50 tests passed; cached review and announcement stages passed. A regression caught future-tense `will be fixed`; rule now preserves planned status and explicit negation.

F3: `steam-insights prepare-data` completed the actual offline workflow, published snapshot b1a7c5e1038c0b4a50d32e7c7b1800c060466c456bd66a13c38e2f860e8ce5f7, passed 175 dataset gates, refreshed reports and exported a development annotation queue. The SQL temporal check caught a real America/Denver daylight-saving discrepancy; all SQL interval arithmetic now explicitly uses UTC, with a regression test. All 18 new pipeline tests pass. No human labels were invented.
