# Steam API contracts verified for Stage 1

Verified against Valve's Steamworks documentation on 2026-10-18. This document separates documented behavior from fields observed in live public responses. A live smoke test made one bounded page request per endpoint/game; it did not enumerate the full catalog or collect the review windows.

## `IUserReviewsService/GetAppReviews`

Official method: [`GetAppReviews`](https://partner.steamgames.com/doc/webapi/IUserReviewsService), `GET https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/`.

This is a Service interface and accepts a URL-encoded JSON object in `input_json`. The method is public and does not require a key. A publisher key associated with the app can raise the rate limit. Anonymous responses may be cached for up to ten minutes; requests can receive HTTP 429, and Valve does not publish a numeric anonymous quota in this method's contract.

The collector uses `appid`, `filter=1` (Recent), `languages=["all"]`, `cursor`, `review_type=0` (All), `purchase_type=1` (All), `num_per_page=100` (documented maximum), `filter_offtopic_activity=false`, `date_range_start`, and `date_range_end`. Steam documents an empty `languages` list as English-only and `"all"` as every language. The Stage 1.5 config defaults to `reviews.languages = ["all"]`; explicit Steam API language-code lists can be configured, and an empty list is rejected to prevent accidental English-only collection. The selected filter is written in the collection manifest, query signature, request observation, and per-window checkpoint identity. The service documents `cursor="*"` or omission for the first page and requires the returned cursor on subsequent pages. Recent and Updated filters are documented for exhausting pages until the result list is empty; Helpful can widen its `day_range`, so it is not used for collection. Date bounds are Unix seconds, inclusive, and both must be set. The source review's created and updated timestamps are separate.

Response wrapper is `response`, containing `query_summary`, `reviews`, `cursor`, and `total_matching` (the exact fields can vary by query/page). A review has `recommendationid`, `author`, `language`, `review`, `timestamp_created`, `timestamp_updated`, `voted_up`, voting/comment metadata, purchase/free/early-access flags, and optional developer-response/device fields. The author object includes SteamID and playtime metadata. Steam explicitly says to check HTTP status rather than a legacy `success` field. The deprecated `/appreviews` endpoint is not used.

`language` is stored as Steam's exact API code, separate from any future detected-language field. Review text is retained without translation or transliteration and written to a Unicode-capable Arrow string column. The original raw response remains the source of truth for malformed or missing metadata.

The live check returned HTTP 200 and confirmed the wrapper and the documented current field names: `response.query_summary`, `response.reviews`, `response.cursor`, and `response.total_matching`. On live terminal pages, Steam omitted the empty `reviews` array but returned `query_summary.num_reviews=0`; the collector treats that exact combination as an empty terminal page and retains the raw response. A missing `reviews` field without that zero-count summary is still marked malformed. Only field names and counts were inspected; review text and SteamIDs were not printed.

## `ISteamNews/GetNewsForApp`

Official method: [`GetNewsForApp`](https://partner.steamgames.com/doc/webapi/ISteamNews), `GET https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/`.

Documented parameters are required `appid`, optional `maxlength` (0 returns full content; nonzero creates a blurb), `enddate` (Unix timestamp; return posts earlier than this date), `count` (default 20), and `feeds` (comma-separated feed names). No cursor or page token is documented. The collector advances by setting `enddate` to one second before the oldest post date from the prior page, and guards against a non-advancing boundary. Public news does not require an API key. `GetNewsForAppAuthed` is a separate partner-only method for publisher-owned apps, requires a publisher key, and is intended to expose unreleased-game information; it is not used here.

Live public responses used the `appnews` wrapper with an `appid` and `newsitems`. Observed item fields include `gid`, `title`, `url`, `is_external_url`, `author`, `contents`, `feedlabel`, `date`, and `feedname`; some items also contain `tags`. Valve's method page documents parameters but does not enumerate this item schema, so code validates these observed fields defensively. `maxlength=0` was requested and live items had non-empty `contents`.

The API can return mixed feed content: Steam Community Announcements and other feeds were both observed. `is_external_url` was true even on items whose `feedname` was `steam_community_announcements`; it is not used alone to decide whether a post is publisher-originated. Non-Steam feed entries are retained with an unverified source classification. No event-type filter or public `event_type` field is assumed.

## `IStoreService/GetAppList`

Official method: [`GetAppList`](https://partner.steamgames.com/doc/webapi/IStoreService), documented as `GET https://partner.steam-api.com/IStoreService/GetAppList/v1/`.

This Service method documents `if_modified_since`, `have_description_language`, inclusion flags for games/DLC/software/videos/hardware, `last_appid`, and `max_results` (default 10,000; maximum 50,000). Results are ordered by app ID; the next call uses the last app ID returned. The API returns `last_modified` and `price_change_number` for items. The method page describes the key as “any web API key,” while Valve's [Web API overview](https://partner.steamgames.com/doc/webapi_overview) says every request to the partner-only host requires a valid publisher key and that a regular user key commonly returns 403 with strict IP rate limits. The partner-host request returned 403 in the live follow-up. The public `api.steampowered.com` URL pattern suggested by the user then succeeded with `format=json`; the collector now uses that live-tested route, while noting that the method page still documents the partner host.

There was no `STEAM_WEB_API_KEY` in the runtime environment during the initial Stage 1 pilot. A later run loaded the key from ignored `.env` and collected a complete 194,280-row game catalog snapshot over four pages from the public host; all four pilot IDs were present. See [`CATALOG_FOLLOWUP.md`](CATALOG_FOLLOWUP.md) and the [catalog report](../../../reports/relevance_v1/stage1/catalog/rv1-catalog-20261019T035528Z/report.md). The key is excluded from request observations and manifests. `STEAM_DOMAIN_NAME` is registration metadata and is not sent as a `GetAppList` request parameter.

## Steam event / patch-note semantics

Valve distinguishes Patch Notes, Regular Updates, and Major Updates in its [Small Update / Patch Notes](https://partner.steamgames.com/doc/marketing/event_tools/type_patchnotes) and [Major Update](https://partner.steamgames.com/doc/marketing/event_tools/type_majorupdate) guidance. Patch-note posts may be linked to current/future Steam builds by the publisher; Valve says older events cannot be linked retroactively. Thus the public news feed can establish that an announcement exists and when it was posted, but it does not by itself establish a build ID or exact effective release timestamp. The public `GetNewsForApp` parameter contract does not expose a documented `event_type=12/13` filter. Category and release time are stored only when directly available with provenance; neither is inferred from a title as ground truth.

## Cross-cutting request behavior

Valve's [Web API overview](https://partner.steamgames.com/doc/webapi_overview) describes public versus protected methods, the public `api.steampowered.com` host, and URL-encoded `input_json` for Service interfaces. Requests use HTTPS. The collector is sequential with a configurable 0.5-second default minimum interval between attempts; it records status and honors HTTP 429, `Retry-After` delay/date values, and transient 5xx/network errors with capped exponential backoff. Because Valve does not publish an exact request quota here, configured request budgets are local safety limits rather than claims about Steam's quota.

## References

- [IUserReviewsService](https://partner.steamgames.com/doc/webapi/IUserReviewsService)
- [Languages Supported on Steam](https://partner.steamgames.com/doc/store/localization/languages)
- [ISteamNews](https://partner.steamgames.com/doc/webapi/ISteamNews)
- [IStoreService](https://partner.steamgames.com/doc/webapi/IStoreService)
- [Web API Overview](https://partner.steamgames.com/doc/webapi_overview)
- [Event Type: Small Update / Patch Notes](https://partner.steamgames.com/doc/marketing/event_tools/type_patchnotes)
- [Event Type: Major Update](https://partner.steamgames.com/doc/marketing/event_tools/type_majorupdate)

