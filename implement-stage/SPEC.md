# Initial data foundation

Target: set up the `feature/data-inspection` branch with a runnable repository structure, exploratory analysis, and conservative preprocessing of the existing Steam CSV snapshot.

Inputs: the three CSVs in `data/processed/steam_30_games/`, read without modification. The existing collector and its recovery tests remain supported.

Outputs: `reports/data_exploration/` contains aggregate JSON/CSV tables, plots and a human-readable report; `data/interim/steam_30_games/` contains typed Parquet tables and a preparation manifest. `notebooks/` contains exploration and preprocessing walkthroughs. Source, configuration and tests are tracked; generated text-bearing data and local environments are ignored.

Success commands: `uv run steam-insights profile`, `uv run steam-insights preprocess`, and `uv run python -m unittest discover -s tests -v`.

Base commit: `1478b4991077c81f4bee512d94d63bcfbea7d7a0`.

Scope cuts: no training, invented labels, patch attribution, live collection, app, database service, DVC/MLflow server, or deployment. No source data migration. The architecture files and local `.env` already present are preserved.
