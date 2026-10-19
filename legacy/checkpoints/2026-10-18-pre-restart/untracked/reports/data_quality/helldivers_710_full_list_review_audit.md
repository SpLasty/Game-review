# HELLDIVERS 2 7.1.0 full-list review audit

Updated: 2026-10-18

## Question and design

This pilot tests whether a labeler can identify which changes a review discusses when it sees the **entire patch change list**, instead of a retrieval-generated review/change pair. I used HELLDIVERS 2 “Devoid of Liberty: 7.1.0” because the frozen snapshot contains a large extracted list and enough post-patch reviews.

| Field | Value |
|---|---|
| Snapshot | `cfa34941257d2905d8a2f2681de931909e1904d97bc220e9d121f3c855b4cf56` |
| Patch ID | `d945a03afefbc285de3d65fe2ddbdbba217a003eb033b28760f4540969d12288` |
| Patch anchor | 2026-09-22 09:00:27 UTC |
| Post window | 2026-09-22 09:00:27 to 2026-10-06 09:00:27 UTC |
| Eligible reviews in snapshot window | 708 (1,638 total post-window review records) |
| Sample | 300 unique Steam reviews without replacement (42.4% of 708 eligible); SHA-256 ordering with seed `steam-full-list-20261018-v1` |
| Change list | All 101 extracted fragments, 9,368 change-text characters; 65 fragments carry `extraction needs review` |
| Patch overlap | One other patch post overlaps the broader analysis period |
| Collection status | Review collection is incomplete; this is a sample of the frozen snapshot, not all Steam reviews |

The complete ordered list and numbering are frozen in `patch_prefix.md`; each of the 300 materialized prompts in `prompts.jsonl` contains that full prefix plus exactly one review. Steam Recommended was excluded. The instruction asked only for specific change discussion: no sentiment, fix success, or causal attribution was labeled. A match required a specific change topic and exact review quote; related symptoms without the listed trigger remain `ambiguous`; unrelated or generic commentary is `none`.

The 101 extracted fragments are not all clean atomic changes: some are headings, intent/problem text, or broad paragraphs. The 65 extraction-review flags make that a material limit on both matches and nonmatches.

## Results

| Label | Reviews | Share | Meaning |
|---|---:|---:|---|
| Confirmed match | 3 | 1.0% | Specific listed change discussion supported by review evidence |
| Ambiguous | 30 | 10.0% | Plausible topical overlap, but insufficient detail to identify the listed change confidently |
| No specific match | 267 | 89.0% | No listed change identified under the evidence rule |
| **Total** | **300** | **100%** | |

Only two items received confirmed associations:

| Change # | Change | Confirmed reviews | Evidence examples |
|---:|---|---:|---|
| 12 | Enemies preferentially spawn near a Helldiver at low local pressure when the global enemy cap is reached. | 2 | One review asks developers to “Change the spawn logic”; another explicitly describes far enemies despawning and new enemies spawning in front of players. |
| 47 | GL-52 De-Escalator arc explosion can hit its wielder. | 1 | The review quotes the patch note and objects to the weapon harming its user. |

These are 3 review-to-change assignments across 3 reviews. The first item has two direct discussions; the second has one direct discussion. A broad “enemy count” or “crash” complaint was not promoted to a confirmed match.

I also joined the three confirmed review/change assignments to the snapshot’s `candidates.parquet`. The lexical candidate generator emitted 2 of the 3 exact pairs. It missed the direct discussion of change 12 in Steam review `236182741` (sample 30). The other two pairs were emitted, with lexical scores 0.516 (change 47) and 0.114 (change 12).

The missed pair is specifically explained by the configured per-review cap. Review `236182741` already had five candidate rows for this patch, the configured `max_per_review_per_task = 5`. Change 12 shared three terms with the review (`enemy`, `pressure`, `where`), clearing the minimum of two shared terms, but its computed lexical score was 0.067. The five selected alternatives scored 0.086–0.121 (#86, #61, #70, #71, #101), so change 12 fell below the top-five cutoff. This is a concrete cap/ranking miss in the sample; 3 confirmed assignments are far too few to estimate recall.

## Uncertain review/change candidates

These 30 reviews should be treated as follow-up candidates, not positive labels. The change numbers refer to the frozen numbered list in `patch_prefix.md`; exact stable change IDs are in `responses_enriched.jsonl` and `responses.csv`.

| Sample | Steam review ID | Possible change #s | Review evidence / unresolved overlap |
|---:|---:|---|---|
| 1 | `235871882` | 43, 44, 45, 100 | randomly crashes with the current update; doesn't last more than 2 minutes before crashing |
| 15 | `236691446` | 85 | I do experience frame drops or hitches on my system |
| 17 | `236651424` | 4, 36 | ragdoll, weapon flinching |
| 39 | `236495629` | 3, 43 | connectivity glitches and issues trying to play with friends a while ago |
| 43 | `236749527` | 4, 12, 75 | Spawn rates for certain enemies do not match major order requirements; Ragdolling has been a major issue; Being sent flying across the map |
| 50 | `236416348` | 12, 16, 17, 21, 22, 23 | бесконечные патрули вызывающие бесконечные подкрепления у края карты; Невозможно эвакуироваться нормально |
| 92 | `236908029` | 12 | 10 Bile Titans spawned right next to you |
| 96 | `235863438` | 31, 32, 33, 36 | Weapons feel weaker; balance changes |
| 97 | `235926379` | 16, 21 | you actually increase the number of enemies |
| 101 | `235859922` | 51 | any enemy type being able to phase through any object to get to you |
| 113 | `236619145` | 56 | your turret does a 270' spin to shoot you directly in the head |
| 120 | `236069929` | 31, 32, 33, 36 | The weapon balancing it very bad. They don't patch older weapons very often |
| 147 | `236503246` | 43, 44, 45, 100 | crash mid and end of missions |
| 148 | `236549525` | 8, 51 | visual, there's lots of fog, on top of a sandstorm in unlogical locations like cities...; invisible "walls" cause enemies dies and you have no idea if there's enemies mostly on bugs enemies |
| 156 | `235995210` | 43, 44, 45, 100 | crash issues for pc players |
| 162 | `235852844` | 12 | patrols not act as if they subconciously know where you are at all times |
| 177 | `235839361` | 43, 44, 45, 100 | the new update crash then i lost all my grind |
| 186 | `235881878` | 43, 44, 45, 100 | The game always crash or get crashes every two months |
| 188 | `236361716` | 4, 75 | die repeatedly due to ragdoll effects; bad landing areas |
| 198 | `236464741` | 21, 22, 23 | Fewer enemies. |
| 199 | `236142761` | 51 | Enemies who can swim and walk trew concrete |
| 204 | `236644247` | 75 | WAY too much ragdoll; throw me around for a solid 5-10 seconds |
| 224 | `236243509` | 4, 12, 75 | Ragdolling always has been and is still one of the most frustrating aspects; a very common, medium-armor-enemy now getting heavy armor |
| 230 | `236642210` | 12 | inconsistent enemy spawns on D10 and probably others due to the enemy point system |
| 235 | `236570221` | 43, 44, 45, 100 | game crashes that also crash your computer; half time you can't skip and have to close the game to try again |
| 239 | `236899368` | 12 | difficulty is subtly enemies spawning beyond recognition |
| 257 | `236330763` | 12 | enemies will hard target you the moment you spawn back in; spawning in multiple factory striders, war striders, bile titans |
| 279 | `236456557` | 43, 44, 45, 100 | it keep crashing |
| 286 | `236372238` | 43, 44, 45, 51, 75, 100 | enemy corpses having huge hit/collision boxes; stratagems bouncing when they are not supposed to; getting ragdolled on random flat surfaces; getting stuck on poorly made terrain; any number of the ways this game finds to crash itself |
| 298 | `236188757` | 75 | After the latest update the ragdoll is absurd: a little crossfire launches you across the map |

The most frequent uncertainty groups are generic crash complaints (#43, #44, #45, #100), enemy spawn/pressure comments (#12), and broad ragdoll complaints (#4, #75). These are exactly where the complete list helps expose candidate topics, but many reviews still omit the patch-specific mission, weapon, hazard, or trigger. The list’s extraction quality also limits decisions for broad fragments.

## Interpretation

This provides an initial estimate of how often this snapshot’s post-patch reviews explicitly name one of the 101 extracted items: 3/300 were confirmed by this single labeling pass, while 30/300 remain plausible but unresolved. It found one direct change mention absent from the lexical candidate table because it fell below the configured top-five candidate cap, demonstrating a concrete miss in this sample. It does not establish recall or label accuracy. The 267 `none` decisions could include missed paraphrases, especially where extraction is broad or incomplete.

The sample is independent of the lexical candidate list, but it covers only this patch and the 708 eligible review records currently in an incomplete collection. One other patch post overlaps the analysis period, so some reviews can refer to content outside this patch. This is not a patch-caused sentiment estimate. Steam recommendation was not used as sentiment toward any change.

Per the instruction to use this assistant as the inexpensive labeler, the annotations were made in the GPT-6 assistant pass. No separately metered low-cost API model was called, and cost/latency were not measured. The shared prefix is prepared so an API workflow can cache/reuse it; provider-side prompt caching was not invoked here. These are single-model silver labels, not human or independent-model adjudication.

## Artifacts

- Full prefix and numbered list: `data/annotations/llm_jobs/helldivers-710-full-list/patch_prefix.md` (local, Git-ignored).
- Frozen review inputs and sample order: `requests.jsonl` (local, Git-ignored).
- Full materialized prompt for every review, each containing the complete numbered list plus that review: `prompts.jsonl` (local, Git-ignored).
- Row-level decisions: `responses.jsonl`; includes exact evidence, confirmed IDs and possible IDs.
- Change-ID-enriched decisions plus lexical candidate presence for confirmed pairs: `responses_enriched.jsonl`.
- Spreadsheet-friendly view: `responses.csv`.
- Counts, change frequencies and validation flags: `summary.json`.
- Sampling/model/data provenance: `manifest.json`.
- This tracked report: `reports/data_quality/helldivers_710_full_list_review_audit.md`.

## Next steps

1. Inspect the 30 uncertain cases and prioritize the repeated spawn, ragdoll, and crash groups; keep them uncertain unless the review identifies the listed mechanic or trigger.
2. Improve announcement parsing so section headings and problem statements are not treated as standalone changes; revisit the 65 flagged fragments before using item-level sentiment analysis.
3. Repeat the full-list sample on another coverage-screened patch and compare direct-match rates and uncertainty patterns.
4. For automated runs, use one versioned shared prefix and one review suffix per request, with provider prompt caching where available; retain model/version, prompt hash, dataset/patch IDs, and per-row evidence.
