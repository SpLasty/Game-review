# Data directories

- `games.json`: selected app IDs and game names used by the collector.
- `raw/steam_30_games/`: collection manifests; actual per-game raw payloads/resume state are local to the collection machine and Git-ignored.
- `processed/steam_30_games/`: existing CSV snapshot and legacy summaries. The new offline commands treat this directory as immutable input, despite its historical `processed` name.
- `interim/steam_30_games/`: newly generated typed Parquet tables and manifest. Git-ignored; rebuild with `uv run steam-insights preprocess`.

Do not concatenate the balanced and full review files: the balanced file is an overlapping selection. `reviews_text.parquet` is the minimum-word view of the full collection, not a new sentiment-balanced or game-capped dataset.

See [the data workflow](../docs/data_workflow.md) for schemas, validation behavior and interpretation limits. Data-bearing outputs and notebooks with executed sample excerpts should not be published by accident.
