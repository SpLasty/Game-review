# Preserved pre-restart research

`checkpoints/2026-10-18-pre-restart/` contains a complete Git HEAD bundle, the uncommitted tracked diff, copies of pre-existing untracked audit reports, and file-level hashes of research artifacts. Restore the bundle and apply the patch in a separate directory; do not overwrite the current worktree.

`research/` contains historical handoffs, reports, architecture builds, assumption ledgers, and traces moved out of the active documentation paths. `research/data/` is a frozen local copy of the full pre-restart `data/` tree, including raw observations, snapshots, candidate tables and annotation jobs. The original `data/` paths remain available to the open notebook. The checkpoint's `research_artifacts_before_cleanup.jsonl` maps the original paths and hashes; this local archive is not an off-machine backup.

The Sea of Thieves and HELLDIVERS 2 audits under `research/reports/data_quality/` are historical research findings only. Their machine labels and old dataset IDs are not inputs to the replacement design.
