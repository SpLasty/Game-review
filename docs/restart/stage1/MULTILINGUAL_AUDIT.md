# Stage 1.5 multilingual readiness audit

Audit date: 2026-10-18. Scope: the fresh `steam_patch_relevance` implementation and the materialized Stage 1 pilot only. No archived `steam_insights` collector or annotation data was used.

## Findings

Steam's [GetAppReviews contract](https://partner.steamgames.com/doc/webapi/IUserReviewsService) documents `languages` as a list: an empty list means English, and `all` means every language. The API method calls the field optional but does not document a separate behavior for omitting it. The safe request is therefore explicit `languages=["all"]`. Steam's original response field `language` is an API language code, and `review` is the source text. The [supported language reference](https://partner.steamgames.com/doc/store/localization/languages) distinguishes Steam API codes from other language labels.

The Stage 1 client already sent `languages=["all"]` as a hard-coded value. The newly added audit of stored request provenance confirms all **1,708** page references for the latest selected 84 patch windows used `languages=["all"]`; the latest run's 750 review request observations also recorded that filter. Therefore no language-coverage backfill is required. Steam review pagination/page budgets left many windows incomplete, but those are collection-depth gaps, not English-only collection.

Stage 1 preserved `review` in `review_text_original` and Steam's `language` value in a separate string field. Parquet uses `large_string`, so Unicode writing systems are supported. The ingestion path does not translate or transliterate text. Its stable revision ID is based on app, review ID, update timestamp, and text hash, not the language filter; changing filters does not create a second logical review. Before this audit, however, the language filter was absent from the config/manifest and query-specific checkpoint isolation was not implemented. Explicit-filter collection could therefore overwrite the shared window checkpoint. Stage 1.5 records the filter in config, manifest and request metadata, and gives non-default filter sets their own resumable checkpoint keys. The default `all` filter retains the historical checkpoint key and query signature so existing checkpoints remain resumable.

No English assumption was found in the new `steam_patch_relevance` normalization or storage path. Its historical `steam_insights` predecessor contains English-specific code, but that package is retired from the supported CLI and is not imported by the new collector. Announcement language is a separate nullable field: none of the **1,331** unique Stage 1 news items in the available source checkpoints supplied a language property, so the report records those as missing rather than inferring a language from text.

## Existing pilot coverage

The coverage report is computed from the saved raw Steam pages for run `rv1-20261019T031033900187Z-a468b544`:

| Game | English | Recognized non-English | English share | Non-English share | Review revisions |
| --- | ---: | ---: | ---: | ---: | ---: |
| Counter-Strike 2 | 16,664 | 55,328 | 23.1% | 76.9% | 71,992 |
| Dota 2 | 8,329 | 27,659 | 23.1% | 76.9% | 35,988 |
| HELLDIVERS 2 | 20,848 | 12,630 | 62.3% | 37.7% | 33,478 |
| No Man's Sky | 12,679 | 14,155 | 47.2% | 52.8% | 26,834 |
| **Total** | **58,520** | **109,772** | **34.8%** | **65.2%** | **168,292** |

The 168,292 collected revisions contain **31 distinct documented Steam API language codes**. The audit found zero missing language values, unexpected codes, non-string language values, or same-revision language conflicts. Counts describe the collected pages, not population estimates: 16 of 84 selected patch windows are complete, and 68 are partial under the existing request/page budgets. Steam News did not provide an announcement-language field in the 1,331 inspected posts.

Detailed outputs:

- [Language coverage report](../../../reports/relevance_v1/stage1/latest/language_coverage.md)
- [Per-game/per-language counts](../../../reports/relevance_v1/stage1/latest/language_by_game.csv)
- [Per-window/per-language counts](../../../reports/relevance_v1/stage1/latest/language_by_patch_window.csv)
- [Machine-readable summary](../../../reports/relevance_v1/stage1/latest/language_coverage.json)

The current window incompleteness remains material for later evaluation: none of the 21 CS2 or 21 Dota 2 windows is complete; HELLDIVERS 2 has 4/21 complete windows and No Man's Sky has 12/21. Stage 2 extraction may proceed on the preserved source material. Stage 3 evaluation must select sufficiently covered windows or account for collection completeness and language-dependent sample sizes.

## Stage 1.5 changes

- `reviews.languages` is configurable and defaults to `["all"]`; an empty list is rejected because Steam defines it as English.
- Steam language codes remain verbatim. Missing, non-string and unexpected values receive status flags while raw JSON remains recoverable.
- `review_text_original` remains unchanged Unicode. New nullable `detected_language` and `detected_language_confidence` fields are schema placeholders only; no detection or translation is run.
- Announcement language is stored separately from review language. It remains null where Steam does not return a source value.
- Reports now include per-game and per-window language counts, known-code English/non-English proportions, and incomplete-window status.
- Checkpoint identity includes explicit filters. Review revision identity does not include the filter, so records collected through overlapping modes deduplicate logically.

## Stage 2 readiness

**Stage 2 can safely begin** with Unicode-safe, language-aware patch/review normalization. This finding does not certify the partial review windows as a representative evaluation corpus. Complete additional window collection before making cross-language performance or language-share claims beyond the observed pages. Future stages should preserve source spans, test embedded English game terms in non-English reviews, compare multilingual embeddings against lexical/entity retrieval, and report by language and cross-language pair. Translation should be targeted to demonstrated error cases, not applied to the entire dataset.
