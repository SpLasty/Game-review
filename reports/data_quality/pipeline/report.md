# Model-ingestion data readiness report

Dataset: `f6ed010d3a378a5a12a4d9e502a41aae540c77b863356eae972189164cec0240`

## Processing completed

73,336 current reviews and 3,638 current announcement posts were processed. 32,759 structural change candidates and 27,684 review/change candidates were exported. Candidates and rule hints remain distinct from adjudicated human labels.

| Artifact | Rows |
| --- | --- |
| source_records | 77,981 |
| quarantine | 0 |
| review_revisions | 73,336 |
| review_passages | 33,537 |
| duplicate_pairs | 135 |
| reviews | 73,336 |
| announcement_revisions | 4,635 |
| announcement_blocks | 108,956 |
| announcement_links | 2,221 |
| changes | 32,759 |
| patches | 1,100 |
| verification_evidence | 504 |
| announcements | 3,638 |
| games | 30 |
| patch_windows | 1,100 |
| candidates | 27,684 |
| annotations | 0 |
| model_review_inputs | 33,537 |
| model_change_inputs | 32,759 |
| model_pair_inputs | 27,684 |
| labeled_pairs | 0 |

## Patch verification and window coverage

| Verification status | Patch posts |
| --- | --- |
| heuristic_unverified | 845 |
| source_confirmed_patch_post | 249 |
| source_reviewed_patch_post | 6 |

**255 source-confirmed or reviewed patch posts**; **15 pass the configured exploratory review-coverage screen**. The legacy ten manual flags are preserved separately. Source confirmation establishes post type; fix effectiveness and actual deployment remain separate questions.

The screen uses configured before/after intervals (default 14 days each), at least 30 text-eligible reviews across at least 7 UTC dates per side, and either observed review bounds spanning the entire interval or fully exhausted dated API queries on both sides. API completion is stronger evidence than observed-date bounds and is recorded separately. A 14-day interval beginning midday can intersect 15 UTC calendar dates. These are operational availability thresholds, not statistical-power or causal criteria.

## Per-game readiness

| Game | Split | Reviews | Eligible | Structured posts | Confirmed patches | Confirmed windows passing |
| --- | --- | --- | --- | --- | --- | --- |
| Dota 2 | test | 4199 | 1017 | 0 | 0 | 0 |
| Counter-Strike 2 | train | 4656 | 1025 | 93 | 3 | 0 |
| Terraria | train | 3000 | 1032 | 0 | 0 | 0 |
| Project Zomboid | test | 2200 | 1002 | 92 | 31 | 0 |
| Warframe | test | 2300 | 1027 | 0 | 0 | 0 |
| War Thunder | test | 2600 | 1043 | 0 | 0 | 0 |
| Path of Exile | test | 2400 | 1047 | 87 | 5 | 0 |
| Rust | train | 2789 | 1020 | 0 | 0 | 0 |
| No Man's Sky | test | 1800 | 1054 | 0 | 0 | 0 |
| RimWorld | test | 2000 | 1039 | 0 | 0 | 0 |
| The Elder Scrolls Online | validation | 1700 | 1001 | 99 | 2 | 1 |
| Rainbow Six Siege | test | 3100 | 1010 | 0 | 0 | 0 |
| Dead by Daylight | test | 2299 | 1007 | 0 | 0 | 0 |
| Stardew Valley | test | 2500 | 1030 | 0 | 0 | 0 |
| Factorio | test | 2299 | 1048 | 0 | 0 | 0 |
| Satisfactory | test | 2100 | 1040 | 100 | 66 | 0 |
| Deep Rock Galactic | test | 2499 | 1026 | 98 | 26 | 1 |
| HELLDIVERS 2 | test | 2400 | 1017 | 93 | 37 | 0 |
| PUBG BATTLEGROUNDS | train | 3299 | 1022 | 0 | 0 | 0 |
| Hunt Showdown 1896 | validation | 1799 | 1002 | 48 | 11 | 2 |
| Noita | test | 1900 | 1030 | 0 | 0 | 0 |
| Valheim | train | 2000 | 1040 | 0 | 0 | 0 |
| Destiny 2 | test | 2300 | 1022 | 0 | 0 | 0 |
| Baldur's Gate 3 | test | 2100 | 1007 | 0 | 0 | 0 |
| Cyberpunk 2077 | test | 2300 | 1030 | 0 | 0 | 0 |
| Apex Legends | train | 2899 | 1026 | 100 | 4 | 0 |
| Sea of Thieves | train | 2299 | 1007 | 97 | 30 | 3 |
| Guild Wars 2 | train | 1900 | 1058 | 0 | 0 | 0 |
| World of Tanks | test | 2000 | 1039 | 100 | 11 | 8 |
| V Rising | test | 1699 | 1020 | 100 | 29 | 0 |

## Model ingestion readiness

- Inference inputs available: **True**.
- Adjudicated labeled pairs: **0**; supervised training ready: **False**. This flag indicates that some training rows exist, not that label volume, class coverage, or evaluation quality is sufficient.
- Cross-split duplicate families: **1,053**; affected pairs are excluded from supervised export.
- Source metadata/independent language-detector disagreements: **479**; retained as inspection flags.

## More data and decisions required

- **2,531 posts** still have no original heading/list markup available. Their extracted fragments retain a degraded-source warning.
- **1,100 patch posts** have no supported effective release timestamp. Publication time is an explicitly marked proxy.
- Backfill historical review windows where before/after counts or date coverage are insufficient. The window CSV records deficits. Exhausting a dated API query is tracked separately from passing the sample-density screen.
- Complete human annotations for relevance, change-specific sentiment, and fix-status evidence. A recommendation vote does not supply these labels. Inspect representative parser/verification outputs before using weak hints.
- Historical review and announcement revisions absent from the archive cannot be reconstructed by fetching their current state. Edited reviews and newly recovered posts are current observations, with their observation times preserved.
- Overlapping patch posts, beta/platform scope, and external full changelog links need source inspection. Unknown review branch/platform never silently becomes a scope match.

## Reproducibility and outputs

`manifest.json` records input/config/code fingerprints, Arrow contracts, row counts, table hashes, and readiness. `validation.json` contains the publication gates. `catalog.duckdb` is rebuildable from the authoritative Parquet tables. Split allocation is frozen by game ID and seed; held-out labels do not guide parser rules or candidate thresholds.

See `patch_window_quality.csv` for individual post periods and `game_quality_summary.csv` for all games. The report describes the observed convenience sample. It does not establish patch causality.
