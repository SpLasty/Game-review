# End-to-end data pipeline

Base commit: `ac5cbdfa15ce9bfccb62e8e9703ca63884aead43`. Pre-existing working-tree changes implement the approved quality report; preserve them.

Target: implement the user's approved twelve-item preprocessing plan. Inputs: existing Steam CSV exports, optional original collector JSON, public source recovery snapshots, human annotation files. Outputs: immutable versioned Parquet datasets (reviews/revisions/passages, announcements/blocks/changes, patches/evidence, windows/candidates/splits/model inputs/labels), DuckDB views, row-accounting and provenance manifests, quality reports and documentation.

Success command: `uv run steam-insights pipeline --config configs/pipeline.toml`, followed by `uv run steam-insights pipeline-validate --config configs/pipeline.toml`. Small stage scripts and bounded online source recovery/backfill commands must also be runnable. Dataset tables must preserve original text and large IDs, validate evidence offsets and relationships, prevent split leakage, and distinguish weak metadata from annotations.

Human labeling and historical states missing from the sources cannot be manufactured. Publish inference/annotation readiness independently from supervised training readiness. Record source failures and incomplete collection. No model training or cloud deployment is in scope. Effort: balanced; ASK: never; assurance: draft.
