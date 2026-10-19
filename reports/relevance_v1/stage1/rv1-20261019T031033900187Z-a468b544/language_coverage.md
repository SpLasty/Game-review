# Multilingual review coverage

Run: `rv1-20261019T031033900187Z-a468b544`
Requested Steam review language filters: `all`
Collection phase: `pre_backfill`

Steam documents an empty `languages` list as English-only and `['all']` as every language. The saved Stage 1 requests were checked in their raw observation metadata. Steam's original language codes and review text are retained unchanged; this report does not detect or translate language.

English and non-English proportions below use records with recognized Steam language codes as the denominator. Missing and unexpected codes are reported separately. Per-window counts represent review-window memberships, so the same review may appear in multiple patch windows.

## Overall review language status

- Unique review revisions: **168,292**.
- English: **58,520** (34.8% of recognized-code reviews).
- Non-English recognized codes: **109,772** (65.2% of recognized-code reviews).
- Missing language: **0**; non-string metadata: **0**; unexpected codes: **0**.
- Selected patch windows complete: **16 / 84**.

## Game-level distribution

| App ID | Game | English | Recognized non-English | Missing | Unexpected/non-string | Total | English share of known | Non-English share of known |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 570 | Dota 2 | 8,329 | 27,659 | 0 | 0 | 35,988 | 23.1% | 76.9% |
| 730 | Counter-Strike 2 | 16,664 | 55,328 | 0 | 0 | 71,992 | 23.1% | 76.9% |
| 275850 | No Man's Sky | 12,679 | 14,155 | 0 | 0 | 26,834 | 47.2% | 52.8% |
| 553850 | HELLDIVERS 2 | 20,848 | 12,630 | 0 | 0 | 33,478 | 62.3% | 37.7% |

## Announcement language metadata

Announcement language metadata statuses: `{'missing': 1331}`. This is kept separate from review language; absent announcement metadata is not inferred from announcement text or the API request locale.

## Before/after language backfill

This materialization contains **168,292** unique review revisions in `pre_backfill`. A separate language backfill contributes **0** revisions in the post-backfill phase. Existing raw review requests used `languages=['all']`; the review windows remain partial where the page/request budget was reached, not because the collector requested English only.

## Detailed outputs

- `language_by_game.csv`: one row per game and exact Steam language code, with missing and unexpected metadata retained as separate groups.
- `language_by_patch_window.csv`: one row per patch window and exact Steam language code, plus collection status and English/non-English proportions.
- `language_coverage.json`: machine-readable quality summary.

Language codes follow Steam's API spelling. This report flags codes absent from the documented Steam API language list but never rewrites or maps source codes.
