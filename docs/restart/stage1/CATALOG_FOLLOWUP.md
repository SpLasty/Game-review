# GetAppList credential and host follow-up

Updated: 2026-10-18 (local date). These calls happened after the initial Stage 1 pilot run.

The user added `STEAM_WEB_API_KEY` and `STEAM_DOMAIN_NAME` to the ignored `.env`. I loaded the values into the process without printing them. The key was sent only in the HTTPS query parameter expected by the method; it was never written to a manifest, observation, report, or source file.

The first request used the endpoint listed by the method page, `partner.steam-api.com/IStoreService/GetAppList/v1/`. The restricted-network attempt could not resolve the host. A network-enabled retry reached Steam and received **HTTP 403** on its first request, so I stopped calling that host to avoid repeated 403s.

Valve's [GetAppList method page](https://partner.steamgames.com/doc/webapi/IStoreService) describes the required key as “any web API key,” while Valve's [Web API overview](https://partner.steamgames.com/doc/webapi_overview) says the partner-only host requires a valid publisher Web API key and warns that a regular user key commonly returns 403, which can trigger strict IP rate limits. The partner-host result is consistent with that host-level requirement.

Following the user's suggested URL pattern, I tested `https://api.steampowered.com/IStoreService/GetAppList/v1/?...&format=json`. That public-host route returned HTTP 200 with the same `.env` key. A bounded first page of 1,000 records included Dota 2 (570) and Counter-Strike 2 (730). I then paged at the documented maximum of 50,000 records per request, resuming the checkpoint until Steam returned a short final page. The resulting game catalog snapshot is **complete for the query**: 194,280 distinct game records across four pages, through app ID 5,453,610. All four pilot IDs were present:

| App ID | Catalog name |
| ---: | --- |
| 570 | Dota 2 |
| 730 | Counter-Strike 2 |
| 275850 | No Man's Sky |
| 553850 | HELLDIVERS™ 2 |

The method page still documents the partner host, so public-host compatibility is recorded as live-observed behavior and should be rechecked if Steam changes its routing. `STEAM_DOMAIN_NAME` is key-registration metadata, not a documented `GetAppList` parameter or HTTP header, so it was not sent.

The normalized table is `data/relevance_v1/normalized/rv1-catalog-20261019T035528Z/catalog_apps.parquet`; exact responses remain in content-addressed raw storage. The [catalog report](../../../reports/relevance_v1/stage1/catalog/rv1-catalog-20261019T035528Z/report.md) has the pilot lookup and snapshot counts. Attempt manifests are under the ignored `data/relevance_v1/runs/` tree and contain credential-source metadata only. The successful public-host collection did not print or persist the key.
