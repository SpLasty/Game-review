# Stage 1 Steam source coverage

Run: `rv1-20261019T030055913462Z-c468bc85`

## Game coverage

| App ID | Game | News status | Announcements | Official feed | Usable official | Selected candidates | Unique review revisions | Review population coverage | Complete windows / total |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 730 | Counter-Strike 2 | complete | 260 | 241 | 241 | 5 | 38998 | 0.1134 | 0 / 15 |
| 570 | Dota 2 | complete | 140 | 101 | 101 | 5 | 14996 | 0.1666 | 0 / 15 |
| 553850 | HELLDIVERS 2 | complete | 811 | 164 | 164 | 5 | 15000 | 0.3488 | 0 / 15 |
| 275850 | No Man's Sky | complete | 120 | 29 | 29 | 5 | 14269 | 0.5061 | 3 / 15 |

## Selected patch candidates

These are rule-based candidates from Steam's publisher announcement feed, not build-verified patches. The public news record does not supply a verified effective release timestamp; review windows use publication time.

- **Counter-Strike 2 — Counter-Strike 2 Update** (2024-11-13 23:21:44+00:00); type `update_candidate`, score 148, id `rv1_patch_716cae5ff2f8f020dd4a0f43`.
- **Counter-Strike 2 — Counter-Strike 2 Update** (2025-10-01 23:43:04+00:00); type `update_candidate`, score 144, id `rv1_patch_1b43a025c748da0a873756d9`.
- **Counter-Strike 2 — Counter-Strike 2 Update** (2026-01-21 22:58:08+00:00); type `update_candidate`, score 142, id `rv1_patch_e9f7f8a436d761f5f0884254`.
- **Counter-Strike 2 — Introducing TrueView** (2025-11-05 00:00:20+00:00); type `content_update_candidate`, score 138, id `rv1_patch_9e4767883a6bb501cd5ce8d3`.
- **Counter-Strike 2 — Counter-Strike 2 Update** (2026-09-22 23:37:36+00:00); type `update_candidate`, score 136, id `rv1_patch_22f5df4b1dd3f51539637070`.
- **Dota 2 — Dota 2 Update - 7/1/2026** (2026-07-01 23:26:01+00:00); type `update_candidate`, score 175, id `rv1_patch_2f9c777bc8caa3cc9120ca2d`.
- **Dota 2 — 7.39b Gameplay Patch** (2025-05-29 23:36:02+00:00); type `update_candidate`, score 166, id `rv1_patch_471fd3bcb731d8974461e63c`.
- **Dota 2 — Gameplay Patch 7.35d And Matchmaking Features** (2024-03-21 22:32:58+00:00); type `update_candidate`, score 166, id `rv1_patch_c202a7b3a6c28b059cc10b43`.
- **Dota 2 — Introducing Kez and Crownfall Act IV** (2024-11-08 02:22:13+00:00); type `content_update_candidate`, score 162, id `rv1_patch_d26f2fd105ca827b49019c3f`.
- **Dota 2 — 7.41c Gameplay Patch** (2026-05-06 22:17:55+00:00); type `update_candidate`, score 157, id `rv1_patch_43401a37d5a22b59bf036928`.
- **HELLDIVERS 2 — Patch Notes 01.002.200** (2025-03-18 10:00:43+00:00); type `versioned_update_candidate`, score 201, id `rv1_patch_8db9d73e134f7107b2160f2f`.
- **HELLDIVERS 2 — Devoid of Liberty: 7.1.0** (2026-09-22 09:00:27+00:00); type `versioned_update_candidate`, score 200, id `rv1_patch_c3e321881ea3c18094c58bf3`.
- **HELLDIVERS 2 — Devoid of Liberty: 7.0.0** (2026-08-12 09:01:30+00:00); type `versioned_update_candidate`, score 200, id `rv1_patch_8a5db9c3871ee362abb09b81`.
- **HELLDIVERS 2 — Machinery of Oppression: 6.3.0** (2026-06-16 09:00:24+00:00); type `versioned_update_candidate`, score 200, id `rv1_patch_248a927eaef7d1feda3fbcac`.
- **HELLDIVERS 2 — Machinery of Oppression: 6.2.2** (2026-04-28 09:01:36+00:00); type `versioned_update_candidate`, score 200, id `rv1_patch_416686405cd90b9173c2ea3e`.
- **No Man's Sky — Introducing...No Man's Sky Breach** (2025-10-22 12:58:44+00:00); type `content_update_candidate`, score 200, id `rv1_patch_8817ee1b1ca62a5245b5db53`.
- **No Man's Sky — Introducing...No Man's Sky: Voyagers** (2025-08-27 13:06:30+00:00); type `content_update_candidate`, score 185, id `rv1_patch_b7b2088d6c9bfc5314320a6a`.
- **No Man's Sky — Introducing..The Cursed Expedition!** (2024-10-23 13:03:17+00:00); type `content_update_candidate`, score 181, id `rv1_patch_90416030f08a2a07bcc1fa19`.
- **No Man's Sky — Introducing...No Man's Sky Aquarius** (2024-09-04 13:17:20+00:00); type `content_update_candidate`, score 181, id `rv1_patch_e5cdaa37bc2918f13e608106`.
- **No Man's Sky — A complete overhaul to space arrives in the form of No Man's Sky COSMOS (7.0)** (2026-09-09 13:00:12+00:00); type `versioned_update_candidate`, score 167, id `rv1_patch_e7deb506b52b82388ec62ea8`.

## Source gaps and interpretation

- `GetNewsForApp` returned mixed publisher/community and other feed entries. All were preserved; only the explicitly named Steam Community Announcements feed can enter the candidate rule.
- `maxlength=0` requests full Steam post content. A body can still be empty or link to an off-site changelog. Links are retained, but arbitrary external sites are not fetched automatically; the `announcements` Parquet table flags empty bodies and stores links.
- This run has 0 announcements with no body, 0 with a truncation heuristic flag, and 681 with one or more links.
- Steam's public news API does not document an event-type/build filter or an exact build release time. Candidate counts are not verified patch counts.
- Verified build-linked patches in this dataset: 0; selected announcement candidates remain unverified.
- The Reviews API returns current review revisions. SteamIDs and author playtime may appear in the raw source blobs; keep raw data local and restrict access.
- Review collection uses inclusive creation-time bounds. A window is complete only after an empty cursor page; `page_budget_reached`, `request_budget_reached`, and request errors remain explicit partial states.
- `Recommended` is stored as an overall review vote only; it is not used as feature-level sentiment.
- Game IDs are curated seeds. `IStoreService/GetAppList` was not called because no Web API key was configured.

## Patch-window coverage

- `730` `1783238125194269` / `before_14d`: page_budget_reached, 3000 / 22620 reviews (0.1326), 30 pages.
- `730` `1783238125194269` / `after_0_7d`: page_budget_reached, 3000 / 12771 reviews (0.2349), 30 pages.
- `730` `1783238125194269` / `after_8_14d`: page_budget_reached, 3000 / 11366 reviews (0.2639), 30 pages.
- `730` `1811772772457461` / `before_14d`: page_budget_reached, 3000 / 31341 reviews (0.0957), 30 pages.
- `730` `1811772772457461` / `after_0_7d`: page_budget_reached, 3000 / 18259 reviews (0.1643), 30 pages.
- `730` `1811772772457461` / `after_8_14d`: page_budget_reached, 2999 / 16134 reviews (0.1859), 30 pages.
- `730` `1822556746157780` / `before_14d`: page_budget_reached, 3000 / 36055 reviews (0.0832), 30 pages.
- `730` `1822556746157780` / `after_0_7d`: page_budget_reached, 3000 / 25378 reviews (0.1182), 30 pages.
- `730` `1822556746157780` / `after_8_14d`: page_budget_reached, 2999 / 20664 reviews (0.1451), 30 pages.
- `730` `1815580768210748` / `before_14d`: page_budget_reached, 1000 / 42477 reviews (0.0235), 10 pages.
- `730` `1815580768210748` / `after_0_7d`: page_budget_reached, 1000 / 17791 reviews (0.0562), 10 pages.
- `730` `1815580768210748` / `after_8_14d`: page_budget_reached, 1000 / 18451 reviews (0.0542), 10 pages.
- `730` `1844751498216924` / `before_14d`: page_budget_reached, 3000 / 32286 reviews (0.0929), 30 pages.
- `730` `1844751498216924` / `after_0_7d`: page_budget_reached, 3000 / 20476 reviews (0.1465), 30 pages.
- `730` `1844751498216924` / `after_8_14d`: page_budget_reached, 3000 / 17888 reviews (0.1677), 30 pages.
- `570` `1836506165566626` / `before_14d`: page_budget_reached, 1000 / 9118 reviews (0.1097), 10 pages.
- `570` `1836506165566626` / `after_0_7d`: page_budget_reached, 1000 / 4228 reviews (0.2365), 10 pages.
- `570` `1836506165566626` / `after_8_14d`: page_budget_reached, 1000 / 4772 reviews (0.2096), 10 pages.
- `570` `1800991756325775` / `before_14d`: page_budget_reached, 1000 / 8432 reviews (0.1186), 10 pages.
- `570` `1800991756325775` / `after_0_7d`: page_budget_reached, 999 / 4073 reviews (0.2453), 10 pages.
- `570` `1800991756325775` / `after_8_14d`: page_budget_reached, 1000 / 3832 reviews (0.261), 10 pages.
- `570` `5686430301719384803` / `before_14d`: page_budget_reached, 1000 / 11767 reviews (0.085), 10 pages.
- `570` `5686430301719384803` / `after_0_7d`: page_budget_reached, 1000 / 4981 reviews (0.2008), 10 pages.
- `570` `5686430301719384803` / `after_8_14d`: page_budget_reached, 1000 / 4300 reviews (0.2326), 10 pages.
- `570` `6148070194801613786` / `before_14d`: page_budget_reached, 1000 / 8999 reviews (0.1111), 10 pages.
- `570` `6148070194801613786` / `after_0_7d`: page_budget_reached, 1000 / 5569 reviews (0.1796), 10 pages.
- `570` `6148070194801613786` / `after_8_14d`: page_budget_reached, 1000 / 5264 reviews (0.19), 10 pages.
- `570` `1832065502810383` / `before_14d`: page_budget_reached, 998 / 7434 reviews (0.1342), 10 pages.
- `570` `1832065502810383` / `after_0_7d`: page_budget_reached, 999 / 3622 reviews (0.2758), 10 pages.
- `570` `1832065502810383` / `after_8_14d`: page_budget_reached, 1000 / 3631 reviews (0.2754), 10 pages.
- `553850` `1794102528231829` / `before_14d`: page_budget_reached, 1000 / 3637 reviews (0.275), 10 pages.
- `553850` `1794102528231829` / `after_0_7d`: page_budget_reached, 1000 / 3247 reviews (0.308), 10 pages.
- `553850` `1794102528231829` / `after_8_14d`: page_budget_reached, 1000 / 2057 reviews (0.4861), 10 pages.
- `553850` `1844115010503588` / `before_14d`: page_budget_reached, 1000 / 2701 reviews (0.3702), 10 pages.
- `553850` `1844115010503588` / `after_0_7d`: page_budget_reached, 1000 / 1589 reviews (0.6293), 10 pages.
- `553850` `1844115010503588` / `after_8_14d`: page_budget_reached, 1000 / 1309 reviews (0.7639), 10 pages.
- `553850` `1840944183773413` / `before_14d`: page_budget_reached, 1000 / 2179 reviews (0.4589), 10 pages.
- `553850` `1840944183773413` / `after_0_7d`: page_budget_reached, 1000 / 3350 reviews (0.2985), 10 pages.
- `553850` `1840944183773413` / `after_8_14d`: page_budget_reached, 1000 / 2344 reviews (0.4266), 10 pages.
- `553850` `1835236783573530` / `before_14d`: page_budget_reached, 1000 / 2383 reviews (0.4196), 10 pages.
- `553850` `1835236783573530` / `after_0_7d`: page_budget_reached, 1000 / 1292 reviews (0.774), 10 pages.
- `553850` `1835236783573530` / `after_8_14d`: page_budget_reached, 1000 / 1292 reviews (0.774), 10 pages.
- `553850` `1830797770244667` / `before_14d`: page_budget_reached, 1000 / 3160 reviews (0.3165), 10 pages.
- `553850` `1830797770244667` / `after_0_7d`: page_budget_reached, 1000 / 8195 reviews (0.122), 10 pages.
- `553850` `1830797770244667` / `after_8_14d`: page_budget_reached, 1000 / 4264 reviews (0.2345), 10 pages.
- `275850` `1814309641410480` / `before_14d`: page_budget_reached, 1000 / 1723 reviews (0.5804), 10 pages.
- `275850` `1814309641410480` / `after_0_7d`: page_budget_reached, 1000 / 1638 reviews (0.6105), 10 pages.
- `275850` `1814309641410480` / `after_8_14d`: page_budget_reached, 1000 / 1038 reviews (0.9634), 10 pages.
- `275850` `1809235871553552` / `before_14d`: complete, 765 / 765 reviews (1.0), 9 pages.
- `275850` `1809235871553552` / `after_0_7d`: page_budget_reached, 999 / 5403 reviews (0.1849), 10 pages.
- `275850` `1809235871553552` / `after_8_14d`: page_budget_reached, 1000 / 4378 reviews (0.2284), 10 pages.
- `275850` `6212245217911788827` / `before_14d`: complete, 899 / 899 reviews (1.0), 10 pages.
- `275850` `6212245217911788827` / `after_0_7d`: page_budget_reached, 910 / 910 reviews (1.0), 10 pages.
- `275850` `6212245217911788827` / `after_8_14d`: complete, 784 / 784 reviews (1.0), 9 pages.
- `275850` `6242640076593093458` / `before_14d`: page_budget_reached, 1000 / 1314 reviews (0.761), 10 pages.
- `275850` `6242640076593093458` / `after_0_7d`: page_budget_reached, 1000 / 1764 reviews (0.5669), 10 pages.
- `275850` `6242640076593093458` / `after_8_14d`: page_budget_reached, 1000 / 1339 reviews (0.7468), 10 pages.
- `275850` `1843481262688949` / `before_14d`: page_budget_reached, 912 / 912 reviews (1.0), 10 pages.
- `275850` `1843481262688949` / `after_0_7d`: page_budget_reached, 1000 / 3378 reviews (0.296), 10 pages.
- `275850` `1843481262688949` / `after_8_14d`: page_budget_reached, 1000 / 1947 reviews (0.5136), 10 pages.

## Quality summary

```json
{
  "news_schema_issues": {},
  "announcement_rows_missing_body": 0,
  "announcement_rows_truncation_suspected": 0,
  "announcement_rows_with_links": 681,
  "selected_patch_candidates_with_verified_build_linkage": 0,
  "invalid_review_records": 0,
  "repeated_review_records_within_windows": 0,
  "conflicting_same_update_text_versions": 0,
  "patch_candidate_count_by_game": {
    "730": 5,
    "570": 5,
    "553850": 5,
    "275850": 5
  },
  "windows_complete": 3,
  "windows_total": 60
}
```
