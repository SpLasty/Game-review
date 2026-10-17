"""Aggregate exploration through DuckDB views over the latest Parquet snapshot."""

import duckdb

from steam_insights.pipeline.loader import latest_dataset
from steam_insights.pipeline.settings import load_pipeline_config

config = load_pipeline_config()
directory = latest_dataset(config)
with duckdb.connect(str(directory / "catalog.duckdb"), read_only=True) as connection:
    connection.execute("SET TimeZone = 'UTC'")
    print(
        connection.sql(
            "SELECT game, count(*) AS reviews FROM reviews GROUP BY game ORDER BY reviews DESC"
        )
        .df()
        .to_string(index=False)
    )
    print(
        connection.sql(
            "SELECT verification_status, count(*) AS posts FROM patches GROUP BY verification_status"
        )
        .df()
        .to_string(index=False)
    )
    print(
        connection.sql(
            "SELECT game, count(*) AS periods FROM patch_windows WHERE verified_patch_post AND coverage_screen_met GROUP BY game"
        )
        .df()
        .to_string(index=False)
    )
