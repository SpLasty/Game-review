# Steam data quality and patch-window report

Generated: `2026-10-17T03:57:25+00:00`

## Scope and overall assessment

This report checks the current CSV snapshot and measures review availability around developer announcement posts. It is a data-readiness report, not a model result or a causal estimate of patch impact.

The full English review export is the review denominator. The balanced export is reported separately and is not added to it because the two files overlap. A Steam recommendation is a game-level vote, not sentiment toward each change mentioned in a review.

### Source snapshots

| Dataset | Rows | SHA-256 | Source |
| --- | --- | --- | --- |
| reviews | 73,336 | 7d9d123428e311f262a04b27930fdcf414bf844150fe7cf9e7558452b0d5e200 | data/processed/steam_30_games/all_english_reviews.csv |
| balanced | 30,000 | 7c481c1e6713e2232da7b13bf914650fa12fcb3a487f314eea08f70eeb75d839 | data/processed/steam_30_games/balanced_reviews.csv |
| announcements | 3,445 | 799fe82ee9b5b0f521745271f624abaa769340b5e803545e16032823545a307f | data/processed/steam_30_games/developer_announcements.csv |

### Review population summary

| Population | Reviews | Games | Negative vote share | Below text threshold | Edited timestamp proxy | First review UTC | Last review UTC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| reviews | 73,336 | 30 | 18.95% | 42,548 | 3,470 | 2026-01-14T23:28:05+00:00 | 2026-10-14T19:47:59+00:00 |
| balanced | 30,000 | 30 | 25.06% | 0 | 2,466 | 2026-01-23T16:56:45+00:00 | 2026-10-14T19:47:59+00:00 |

The edited count compares creation and latest update timestamps; the export does not preserve historical review text or vote revisions. The collected reviews are a time-skewed snapshot, not a complete census of Steam reviews.

## Validation and missingness

The validator checks required fields, duplicate `(appid, source ID)` keys, language, timestamp parsing and ISO/epoch agreement, timestamp order, explicit booleans, playtime/count fields, empty text, and repeated wording.

| Dataset | Rows | Validation | Error rows/checks | Warning counts |
| --- | --- | --- | --- | --- |
| reviews | 73,336 | passed | 0 | 13851 |
| balanced | 30,000 | passed | 0 | 89 |
| announcements | 3,445 | passed | 0 | 2 |

Observed nonzero validation findings:

| Dataset | Check | Count | Severity | Interpretation |
| --- | --- | --- | --- | --- |
| reviews | empty_text | 291 | warning | Retained for vote counts; has no usable text |
| reviews | repeated_review_text | 13560 | warning | Repeated wording is retained; inspect for memes or duplicate families |
| balanced | repeated_review_text | 89 | warning | Repeated wording is retained; inspect for memes or duplicate families |
| announcements | empty_text | 2 | warning | Source coverage needs inspection |

Nonzero missing/blank field counts:

| Dataset | Field | Missing or blank | Rows |
| --- | --- | --- | --- |
| reviews | review_text | 291 | 73,336 |
| announcements | text | 2 | 3,445 |

## Game-level review and announcement coverage

| Game | Reviews | First review UTC | Last review UTC | Announcement posts | Verified patches | Verified with enough window data | Unverified candidates with enough window data |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Apex Legends | 2,899 | 2026-09-06 13:47:08+00:00 | 2026-10-14 19:25:57+00:00 | 300 | 0 | 0 | 3 |
| Baldur's Gate 3 | 2,100 | 2026-09-18 02:34:12+00:00 | 2026-10-14 19:34:35+00:00 | 17 | 0 | 0 | 0 |
| Counter-Strike 2 | 4,656 | 2026-10-07 20:54:31+00:00 | 2026-10-14 19:05:18+00:00 | 167 | 3 | 0 | 0 |
| Cyberpunk 2077 | 2,300 | 2026-09-26 07:19:09+00:00 | 2026-10-14 19:47:59+00:00 | 14 | 0 | 0 | 0 |
| Dead by Daylight | 2,299 | 2026-09-19 04:35:37+00:00 | 2026-10-14 19:04:28+00:00 | 144 | 0 | 0 | 0 |
| Deep Rock Galactic | 2,499 | 2026-06-10 09:47:16+00:00 | 2026-10-14 18:44:42+00:00 | 61 | 1 | 1 | 0 |
| Destiny 2 | 2,300 | 2026-08-24 11:27:58+00:00 | 2026-10-14 19:04:56+00:00 | 140 | 0 | 0 | 0 |
| Dota 2 | 4,199 | 2026-09-06 12:49:30+00:00 | 2026-10-14 18:58:27+00:00 | 62 | 0 | 0 | 0 |
| Factorio | 2,299 | 2026-07-19 18:35:40+00:00 | 2026-10-14 18:05:37+00:00 | 45 | 0 | 0 | 0 |
| Guild Wars 2 | 1,900 | 2026-04-05 04:50:47+00:00 | 2026-10-14 17:18:34+00:00 | 138 | 0 | 0 | 0 |
| HELLDIVERS 2 | 2,400 | 2026-09-23 00:13:17+00:00 | 2026-10-14 18:56:06+00:00 | 104 | 4 | 0 | 0 |
| Hunt Showdown 1896 | 1,799 | 2026-07-02 15:00:12+00:00 | 2026-10-14 19:04:11+00:00 | 300 | 0 | 0 | 3 |
| No Man's Sky | 1,800 | 2026-09-21 17:36:10+00:00 | 2026-10-14 17:32:01+00:00 | 23 | 0 | 0 | 0 |
| Noita | 1,900 | 2026-04-21 21:56:33+00:00 | 2026-10-14 18:34:28+00:00 | 1 | 0 | 0 | 0 |
| PUBG BATTLEGROUNDS | 3,299 | 2026-09-24 14:18:49+00:00 | 2026-10-14 18:48:45+00:00 | 300 | 0 | 0 | 0 |
| Path of Exile | 2,400 | 2026-04-15 23:03:13+00:00 | 2026-10-14 16:49:53+00:00 | 186 | 0 | 0 | 2 |
| Project Zomboid | 2,200 | 2026-09-25 19:16:49+00:00 | 2026-10-14 18:35:35+00:00 | 64 | 2 | 0 | 0 |
| Rainbow Six Siege | 3,100 | 2026-10-03 14:31:49+00:00 | 2026-10-14 18:46:11+00:00 | 108 | 0 | 0 | 0 |
| RimWorld | 2,000 | 2026-07-30 19:30:48+00:00 | 2026-10-14 18:58:28+00:00 | 23 | 0 | 0 | 0 |
| Rust | 2,789 | 2026-09-15 18:14:22+00:00 | 2026-10-14 18:56:17+00:00 | 38 | 0 | 0 | 0 |
| Satisfactory | 2,100 | 2026-08-17 19:06:17+00:00 | 2026-10-14 19:34:55+00:00 | 49 | 0 | 0 | 1 |
| Sea of Thieves | 2,299 | 2026-07-05 22:46:56+00:00 | 2026-10-14 17:59:48+00:00 | 124 | 0 | 0 | 3 |
| Stardew Valley | 2,500 | 2026-09-11 01:39:44+00:00 | 2026-10-14 19:31:05+00:00 | 12 | 0 | 0 | 0 |
| Terraria | 3,000 | 2026-09-19 01:18:40+00:00 | 2026-10-14 19:21:17+00:00 | 32 | 0 | 0 | 0 |
| The Elder Scrolls Online | 1,700 | 2026-04-23 14:40:16+00:00 | 2026-10-14 18:07:34+00:00 | 143 | 0 | 0 | 2 |
| V Rising | 1,699 | 2026-05-25 11:14:34+00:00 | 2026-10-14 19:06:42+00:00 | 42 | 0 | 0 | 1 |
| Valheim | 2,000 | 2026-10-02 13:51:16+00:00 | 2026-10-14 18:56:37+00:00 | 47 | 0 | 0 | 0 |
| War Thunder | 2,600 | 2026-09-18 21:35:19+00:00 | 2026-10-14 19:25:10+00:00 | 300 | 0 | 0 | 0 |
| Warframe | 2,300 | 2026-09-06 09:59:51+00:00 | 2026-10-14 19:08:18+00:00 | 274 | 0 | 0 | 0 |
| World of Tanks | 2,000 | 2026-01-14 23:28:05+00:00 | 2026-10-14 18:19:04+00:00 | 187 | 0 | 0 | 10 |

## Announcement quality

The snapshot contains **3,445 posts** across **30 games**. **890** are marked as heuristic patch candidates. Verification flags: `unverified_other` 2,554, `unverified_candidate` 881, `manually_verified_patch` 10.

Existing branch-hint values:

| Hint | Posts |
| --- | --- |
| unspecified | 3,375 |
| unstable | 38 |
| stable | 32 |

A candidate flag is not a verified patch-note label; only manually verified posts are treated as confirmed patch announcements below. `date_utc` is the post publication time, not necessarily the release time. The export has no dedicated platform field, and flattened text cannot recover original headings.

## Patch-window review coverage

Each included candidate or manually verified post is centered on its publication timestamp. The pre window is `[post time - 14 days, post time)` and the post window is `[post time, post time + 14 days)`. Review eligibility requires at least 10 Unicode word runs and language `english`. Counts use the full review snapshot only; the overlapping balanced export is excluded.

For this report, a window passes the **exploratory coverage screen** when each side has at least 30 text-eligible reviews on at least 7 distinct review dates, and the game's observed review date range spans the complete 28-day window. The stronger coverage flag raises the count threshold to 100 per side. These are transparent screening rules, not a guarantee of statistical power or complete Steam coverage.

| Assessment | Announcement windows |
| --- | --- |
| unverified candidate insufficient or edge censored | 856 |
| unverified candidate screening coverage verify patch | 16 |
| unverified candidate strong coverage verify patch | 9 |
| verified patch insufficient or edge censored | 9 |
| verified patch screening sufficient | 1 |

**1 manually verified patch window(s)** pass the exploratory coverage screen: **Deep Rock Galactic — PATCH NOTES - S06.05.02** (published 2026-08-06T09:12:17+00:00; window 2026-07-23T09:12:17+00:00 to 2026-08-20T09:12:17+00:00, with 129/96 eligible reviews over 15/14 active dates before/after).

### Manually verified patch posts

| Game | Post published UTC | Announcement | Pre eligible (days) | Post eligible (days) | Full observed bounds | Coverage screen |
| --- | --- | --- | --- | --- | --- | --- |
| Counter-Strike 2 | 2026-10-02T22:24:13+00:00 | [Counter-Strike 2 Update](https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/1845383656387875) | 0 (0 d) | 1025 (8 d) | no | verified patch insufficient or edge censored |
| Counter-Strike 2 | 2026-10-05T23:39:43+00:00 | [Counter-Strike 2 Update](https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/1845383656394875) | 0 (0 d) | 1025 (8 d) | no | verified patch insufficient or edge censored |
| Counter-Strike 2 | 2026-10-08T22:36:49+00:00 | [Counter-Strike 2 Update](https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/1846018067931597) | 178 (2 d) | 847 (7 d) | no | verified patch insufficient or edge censored |
| Deep Rock Galactic | 2026-08-06T09:12:17+00:00 | [PATCH NOTES - S06.05.02](https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/1840310314341287) | 129 (15 d) | 96 (14 d) | yes | verified patch screening sufficient |
| HELLDIVERS 2 | 2026-08-17T08:59:59+00:00 | [Devoid of Liberty: 7.0.1](https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/1840944183785447) | 0 (0 d) | 0 (0 d) | no | verified patch insufficient or edge censored |
| HELLDIVERS 2 | 2026-08-25T09:01:09+00:00 | [Devoid of Liberty: 7.0.2](https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/1841579228677702) | 0 (0 d) | 0 (0 d) | no | verified patch insufficient or edge censored |
| HELLDIVERS 2 | 2026-09-22T09:00:27+00:00 | [Devoid of Liberty: 7.1.0](https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/1844115010503588) | 0 (0 d) | 630 (14 d) | no | verified patch insufficient or edge censored |
| HELLDIVERS 2 | 2026-09-24T09:00:23+00:00 | [Devoid of Liberty: 7.1.1](https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/1844751498220713) | 93 (2 d) | 623 (15 d) | no | verified patch insufficient or edge censored |
| Project Zomboid | 2026-09-23T16:08:16+00:00 | [Re-population of the Dead: Build 42.21 Unstable Released](https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/1844751498218925) | 0 (0 d) | 601 (13 d) | no | verified patch insufficient or edge censored |
| Project Zomboid | 2026-09-28T12:07:08+00:00 | [Build 42.21 Stable Released](https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/1844751498231307) | 141 (4 d) | 730 (15 d) | no | verified patch insufficient or edge censored |

**25 unverified candidate windows** pass the review coverage screen but still require manual confirmation that each post is a patch and that its publication time is a suitable event anchor. The detailed CSV lists all assessed windows, counts, dates, titles, links, branch hints, and status.

### Interpretation limits

- Coverage thresholds measure the saved snapshot, not the Steam review population; missing review dates do not prove zero activity or complete API collection.
- Windows are anchored to announcement publication time. A later effective release time, hotfix, staged rollout, or beta-only change can shift the true event.
- Review text and recommendation votes are the latest exported state. A review created before a patch may have been edited after it.
- Nearby or duplicate announcement posts can create overlapping windows; the report keeps posts separate and does not infer independent interventions.
- The report describes vote patterns and text availability. It does not label change-specific sentiment, establish causality, or evaluate whether a fix worked.

## Supporting files

- `patch_window_quality.csv`: one row for every heuristic candidate or manually verified patch post, with pre/post counts and screening status.
- `game_quality_summary.csv`: per-game review, announcement, and patch-window counts.
- `../data_exploration/`: source inventory, validation details, missingness, review coverage tables, and plots.

## End-to-end preprocessing update

The [versioned pipeline report](pipeline/report.md) adds recovered announcement structure, evidence-backed patch-post confirmation, individual change candidates, model input exports, leakage controls, and current data-readiness gaps. The counts above describe the original CSV snapshot; the pipeline report also includes subsequent public source observations.
