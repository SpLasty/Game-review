# Steam game catalog snapshot

Run: `rv1-catalog-20261019T035528Z`. Status: **complete**.

The public `IStoreService/GetAppList` route returned 194,280 distinct game records over 4 pages (up to 50,000 per page). The final page was short, so pagination reached the end of the current game-only result set. Highest returned app ID: 5,453,610.

## Pilot app-ID verification

| App ID | Configured game | Steam catalog name |
| ---: | --- | --- |
| 730 | Counter-Strike 2 | Counter-Strike 2 |
| 570 | Dota 2 | Dota 2 |
| 553850 | HELLDIVERS™ 2 | HELLDIVERS™ 2 |
| 275850 | No Man's Sky | No Man's Sky |

Normalized metadata: [`catalog_apps.parquet`](../../../../../data/relevance_v1/normalized/rv1-catalog-20261019T035528Z/catalog_apps.parquet). Exact response pages remain under git-ignored `data/relevance_v1/raw/blobs/`; the run manifest records page observations and sanitized query parameters.

This query included games; it did not request DLC, software, videos, or hardware. The method reference lists the partner API host, but the public host route was the one tested successfully with the configured key; see [`CATALOG_FOLLOWUP.md`](../../../../../docs/restart/stage1/CATALOG_FOLLOWUP.md).
