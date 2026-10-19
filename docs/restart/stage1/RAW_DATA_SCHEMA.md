# Stage 1 raw and normalized schema

All files live under the new `data/relevance_v1/` namespace. Raw JSON pages are immutable by content hash; Parquet tables are derived per collection run. A rerun can reuse the raw page blobs and checkpoints without importing the archived dataset.

## Raw layout

```text
data/relevance_v1/
  raw/blobs/<first-two-hex>/<sha256>.json
  checkpoints/news_<appid>_<query-hash>.json
  checkpoints/reviews_<window-hash>.json
  runs/<run-id>/manifest.json
  runs/<run-id>/source_observations.jsonl
  normalized/<run-id>/*.parquet
```

Coverage reports are written separately under `reports/relevance_v1/stage1/<run-id>/`.

Each raw blob is the exact response body bytes returned by HTTPX. `payload_sha256` is the SHA-256 of those bytes. The JSONL observation records the source method, app ID, requested endpoint, source URL, retrieval UTC time, sanitized parameters, page number, status, source identity, payload hash, and local blob path. The Steam API key is excluded from observations and manifests.

## Parquet tables

| Table | Row grain | Important columns |
| --- | --- | --- |
| `games` | One curated game seed | `appid`, `game_name`, `metadata_source`, `catalog_discovery_used` |
| `announcements` | One source announcement revision | `announcement_id` (Steam GID), `announcement_revision_id`, title, original body, Unix and UTC publication time, source URL, feed labels, separate nullable `announcement_language` and metadata status, source classification, rule-based post type/significance, linked URLs, raw payload and observation IDs |
| `patch_candidates` | One selected update-announcement candidate | Stable `rv1_patch_` ID, source GID/revision, publication anchor, candidate score/reason, release-time availability, rule version |
| `review_revisions` | One unique returned review content revision | App/review ID, updated timestamp, stable logical revision key and content revision ID, exact `review_text_original` Unicode string, exact Steam `language` code plus metadata status, nullable `detected_language` and `detected_language_confidence` for later processing, overall vote, documented review/author metadata, raw source references |
| `review_window_memberships` | One review revision in one patch window segment | Patch ID, review revision ID, segment, inclusive bounds, anchor source, membership rule |
| `review_windows` | One patch × before/early/late time segment | Exact UTC/Unix bounds, page and review counts, Steam-reported total when present, collection status, issues |
| `source_observations` | One response-page observation in this run | Endpoint, sanitized request parameters, retrieval time, status, source identity, payload path/hash |
| `catalog_apps` | One distinct game app ID in a paged Store catalog snapshot | `appid`, `name`, `last_modified`, `price_change_number`, source observation ID, payload hash |

`review_revisions.voted_up` is the overall Steam recommendation only. It is not copied to a change-level sentiment field. SteamIDs occur in Steam's raw author object and are also retained in this initial normalized source table for provenance; restrict local access and remove them from any public/derived exports.

Steam's review API language filter is stored as a configuration list. The default is `['all']`; an empty list means English according to Steam's contract and is rejected by config validation. Explicit language lists are preserved as supplied. Changing the filter changes the query/checkpoint identity but not the stable review revision identity, and each run writes its own normalized snapshot. `language` is never overwritten by later language detection. The nullable detected fields are schema placeholders only; Stage 1.5 does not run a detector.

The language coverage report writes `language_by_game.csv`, `language_by_patch_window.csv`, `language_coverage.json`, and `language_coverage.md`. Review language and announcement language are separate fields; the public news records may not supply announcement-language metadata. Reported window counts are memberships and can exceed unique review counts because windows overlap. English/non-English proportions use recognized Steam codes; missing and unexpected values are shown separately.

Timestamps retain source Unix seconds and UTC timestamp columns. The review-window API bounds are inclusive. For a publication anchor `t`, the defaults are:

| Segment | Inclusive interval |
| --- | --- |
| before | `[t - 14 days, t - 1 second]` |
| after 0–7 days | `[t, t + 7 days]` |
| after 8–14 days | `[t + 7 days + 1 second, t + 14 days]` |

The gap-free segments do not overlap for one patch. A review revision may belong to multiple patch windows; this is represented by repeated membership rows while the review revision is stored once per run.

