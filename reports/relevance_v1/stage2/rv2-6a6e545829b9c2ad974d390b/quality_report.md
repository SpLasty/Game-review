# Stage 2 extraction quality report — rv2-6a6e545829b9c2ad974d390b

Source Stage 1 run: `rv1-20261019T031033900187Z-a468b544`.
This report covers announcement classification, atomic patch-change extraction, review-claim segmentation, game-specific vocabulary, and temporal structure.
No patch-review pairs or relevance/training labels were generated.

## Dataset counts

| Dataset | Rows |
| --- | ---: |
| Announcements classified | 1,331 |
| Patch changes extracted | 3,154 |
| Review claims extracted | 297,500 |
| Game terminology entries | 2,000 |
| Patch episodes | 316 |
| Patch review-window segments | 60 |
| Review-window membership rows | 133,842 |
| Overlapping patch episode pairs | 1,161 |
| Same-entity temporal ambiguities | 796 |

## Coverage by game

| Game | Official-feed posts | Eligible episodes | Atomic changes | Review claims | Review revisions with claims | Complete window segments |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Counter-Strike 2 | 241 | 178 | 976 | 86,761 | 68,694 | 0/21 |
| Dota 2 | 101 | 52 | 777 | 45,616 | 34,866 | 0/21 |
| HELLDIVERS 2 | 164 | 75 | 1,401 | 92,815 | 32,793 | 2/6 |
| No Man's Sky | 29 | 11 | 0 | 72,308 | 26,109 | 5/12 |

## Extraction QA metrics

- Change rows with one or more unresolved fields: 1,309 (41.5%).
- Exact source-span validation failures: 0 (0.0%).
- Non-empty reviews with no claim row: 5,244.
- Low-confidence claims (<0.5): 255,475.
- Claims without an entity/aspect: 279,189 / 267,511; unknown polarity: 285,396.
- Change quality flags: `{"aspect_unresolved": 667, "developer_fix_qualified": 1, "entity_ambiguous": 293, "entity_unresolved": 799}`.
- Heading-only false changes: headings are maintained in hierarchy and are not emitted as changes.
- Patch specificity: claims remain `not_assigned`; temporal membership is not treated as relevance.

## Announcement categories

- `developer_acknowledgement_or_future_plan`: 59
- `major_gameplay_or_balance_update`: 210
- `minor_cosmetic_or_localization_update`: 63
- `new_feature_or_content`: 266
- `other_announcement_unclassified`: 645
- `performance_or_stability_change`: 240
- `promotional_or_non_patch_announcement`: 89
- `specific_bug_fix`: 350

## Data limitations and common failure modes

- Deterministic rules are strongest for explicit Steam lists and numeric phrases. Nested hierarchy is retained, but prose without an explicit action predicate is omitted from `patch_changes`.
- Entity/aspect extraction may remain unresolved when a patch sentence uses implicit context or game-specific shorthand; those rows have quality flags and confidence values.
- A Steam announcement can link to a full official changelog that was not collected by Stage 1. Such URLs and completeness states are retained; Stage 2 did not fetch external pages.
- Review claims are sentence/contrast-clause spans. Aspect and polarity rules are conservative and English-heavy; non-English review text is retained verbatim, while unknown polarity remains null.
- Words such as `now`, `broken`, `nerfed`, and `unbalanced` do not make a claim patch-specific. The pipeline records lexical temporal cues only and assigns no patch relevance.
- Source review windows are incomplete for some patches in Stage 1; all memberships are explicitly temporal-only.

## Manual sample inspection

Inspection status: `awaiting_inspection` (0 of 53 sample rows recorded).

## Reproducible stratified audit sample

Selection seed: `stage2-audit-sample-2026-10`. The sample uses stable SHA-256 ranking within game/developer-status/quality groups for changes and game/top-two-language-plus-other groups for claims, at up to 2 rows per stratum.
The sample records the original source excerpt beside the extracted fields. Spans refer to the original raw announcement body or exact review revision text.

### patch_change — `game=570;status=implemented_bug_fix;quality=flagged` — `rv2_change_e127e64ca3b73aeab215ad54`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a number of issues that would prevent guides from loading in-game (If you manually enabled Steam background downloads to try to work around this problem, you can safely disable it again)
```

Extracted fields:

```json
{
  "change_text": "Fixed a number of issues that would prevent guides from loading in-game (If you manually enabled Steam background downloads to try to work around this problem, you can safely disable it again)",
  "heading_path": [
    "General Fixes"
  ],
  "entity": null,
  "entity_candidates": [],
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2030,
  "source_span_end": 2222,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved"
  ]
}
```

### patch_change — `game=570;status=implemented_bug_fix;quality=flagged` — `rv2_change_f018fc6af3b1f48503e42017`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed an issue with Play Unranked where ticking Show All Modes could make the section unusable
```

Extracted fields:

```json
{
  "change_text": "Fixed an issue with Play Unranked where ticking Show All Modes could make the section unusable",
  "heading_path": [
    "Bug Fixes"
  ],
  "entity": null,
  "entity_candidates": [
    "Play Unranked",
    "Show All Modes"
  ],
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "where ticking Show All Modes could make the section unusable",
  "bug_symptom": "with Play Unranked",
  "source_span_start": 5563,
  "source_span_end": 5657,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "entity_ambiguous"
  ]
}
```

### patch_change — `game=570;status=implemented_bug_fix;quality=resolved` — `rv2_change_33dee9c048bb5579ff7dab74`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed Alchemist have 4 basic abilities at draft, which would push other abilities off by one.
```

Extracted fields:

```json
{
  "change_text": "Fixed Alchemist have 4 basic abilities at draft, which would push other abilities off by one.",
  "heading_path": [
    "Ability Draft Fixes",
    "Unrefined Fireblast granted with Fireblast"
  ],
  "entity": "Alchemist",
  "entity_candidates": [
    "Alchemist"
  ],
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4898,
  "source_span_end": 4991,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=570;status=implemented_bug_fix;quality=resolved` — `rv2_change_3e154dc997d0aecea3604d31`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed Drow Ranger's Sidestep being cancellable by issuing an attack order
```

Extracted fields:

```json
{
  "change_text": "Fixed Drow Ranger's Sidestep being cancellable by issuing an attack order",
  "heading_path": [],
  "entity": "Drow Ranger's Sidestep",
  "entity_candidates": [
    "Drow Ranger's Sidestep"
  ],
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 672,
  "source_span_end": 745,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=570;status=implemented_change;quality=flagged` — `rv2_change_da80f179151a4af3eaae7924`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added spell icons for Windranger's Gale Force when using Compass of the Rising Gale
```

Extracted fields:

```json
{
  "change_text": "Added spell icons for Windranger's Gale Force when using Compass of the Rising Gale",
  "heading_path": [
    "General Fixes"
  ],
  "entity": null,
  "entity_candidates": [
    "Windranger's Gale Force",
    "Compass of the Rising",
    "Gale"
  ],
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3707,
  "source_span_end": 3790,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "entity_ambiguous",
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;status=implemented_change;quality=flagged` — `rv2_change_084d6b1cd4ef2523c4b6d99e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Spectator options and hotkey settings for Facets have been removed
```

Extracted fields:

```json
{
  "change_text": "Spectator options and hotkey settings for Facets have been removed",
  "heading_path": [],
  "entity": null,
  "entity_candidates": [
    "Spectator",
    "Facets"
  ],
  "aspect": "interface_or_settings",
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 342,
  "source_span_end": 408,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "entity_ambiguous"
  ]
}
```

### patch_change — `game=570;status=implemented_change;quality=resolved` — `rv2_change_82cbe5cc6881f7513b063cf8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The Dark Carnival Hero Filter button now shows a tooltip displaying the ticket requirement for the next reward
```

Extracted fields:

```json
{
  "change_text": "The Dark Carnival Hero Filter button now shows a tooltip displaying the ticket requirement for the next reward",
  "heading_path": [
    "Dark Carnival"
  ],
  "entity": "Filter",
  "entity_candidates": [
    "Filter"
  ],
  "aspect": "interface_or_settings",
  "action": "modified",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 486,
  "source_span_end": 596,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=570;status=implemented_change;quality=resolved` — `rv2_change_1a2d7eace81e9e2b54b3083f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Talon Toss: Cooldown increased from 15/12/9/6 to 16/13/10/7
```

Extracted fields:

```json
{
  "change_text": "Talon Toss: Cooldown increased from 15/12/9/6 to 16/13/10/7",
  "heading_path": [
    "Kez"
  ],
  "entity": "Talon Toss",
  "entity_candidates": [
    "Talon Toss"
  ],
  "aspect": "cooldown_or_timing",
  "action": "increased",
  "direction": "increased",
  "previous_value": "15/12/9/6",
  "new_value": "16/13/10/7",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 305,
  "source_span_end": 364,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;status=implemented_bug_fix;quality=flagged` — `rv2_change_44f40426ba25026c5bbe0ff9`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed grenade clipping around AC unit at B-site
```

Extracted fields:

```json
{
  "change_text": "Fixed grenade clipping around AC unit at B-site",
  "heading_path": [
    "Vertigo"
  ],
  "entity": null,
  "entity_candidates": [
    "AC",
    "B-site"
  ],
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1866,
  "source_span_end": 1913,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "entity_ambiguous"
  ]
}
```

### patch_change — `game=730;status=implemented_bug_fix;quality=flagged` — `rv2_change_0c0a733279a8dc475ce7bd68`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a bug where the game would stop taking keyboard input during the end-of-match map vote.
```

Extracted fields:

```json
{
  "change_text": "Fixed a bug where the game would stop taking keyboard input during the end-of-match map vote.",
  "heading_path": [],
  "entity": null,
  "entity_candidates": [],
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "during the end-of-match map vote",
  "bug_symptom": "the game would stop taking keyboard input",
  "source_span_start": 20,
  "source_span_end": 113,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved"
  ]
}
```

### patch_change — `game=730;status=implemented_bug_fix;quality=resolved` — `rv2_change_3aea554d20dd932382718558`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed some light fixtures being misaligned
```

Extracted fields:

```json
{
  "change_text": "Fixed some light fixtures being misaligned",
  "heading_path": [
    "Vertigo"
  ],
  "entity": "Vertigo",
  "entity_candidates": [
    "Vertigo"
  ],
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6538,
  "source_span_end": 6580,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;status=implemented_bug_fix;quality=resolved` — `rv2_change_0a3ecb2e60f0d80cfbe2005b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a case for Linux users where the game would hang when opening the pause menu.
```

Extracted fields:

```json
{
  "change_text": "Fixed a case for Linux users where the game would hang when opening the pause menu.",
  "heading_path": [],
  "entity": "Linux",
  "entity_candidates": [
    "Linux"
  ],
  "aspect": "interface_or_settings",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "where the game would hang when opening the pause menu",
  "bug_symptom": "for Linux users",
  "source_span_start": 347,
  "source_span_end": 430,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;status=implemented_change;quality=flagged` — `rv2_change_cef3c6a8223e639dc99561e6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added color correction, roughness, and normal adjustments to foliage shader and static overlays
```

Extracted fields:

```json
{
  "change_text": "Added color correction, roughness, and normal adjustments to foliage shader and static overlays",
  "heading_path": [
    "Overpass"
  ],
  "entity": "Overpass",
  "entity_candidates": [
    "Overpass"
  ],
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5848,
  "source_span_end": 5943,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;status=implemented_change;quality=flagged` — `rv2_change_48ba191ed3cfbdd8295578b5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Improved clock synchronization to better handle downstream jitter bursts.
```

Extracted fields:

```json
{
  "change_text": "Improved clock synchronization to better handle downstream jitter bursts.",
  "heading_path": [],
  "entity": null,
  "entity_candidates": [],
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 157,
  "source_span_end": 230,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;status=implemented_change;quality=resolved` — `rv2_change_80e42969891e9a42529026da`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added support for updating existing map annotations on Steam Workshop. For example use "workshop_annotation_submit 123456" to update your submission ID=123456 found in the workshop URL. Passing an ID that does not belong to you will create a brand new submission. After the first update the ID will get embedded in the annotation file and you can submit more changes without having to provide the ID again.
```

Extracted fields:

```json
{
  "change_text": "Added support for updating existing map annotations on Steam Workshop. For example use \"workshop_annotation_submit 123456\" to update your submission ID=123456 found in the workshop URL. Passing an ID that does not belong to you will create a brand new submission. After the first update the ID will get embedded in the annotation file and you can submit more changes without having to provide the ID again.",
  "heading_path": [],
  "entity": "Steam Workshop",
  "entity_candidates": [
    "Steam Workshop"
  ],
  "aspect": "map_or_level",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 205,
  "source_span_end": 611,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;status=implemented_change;quality=resolved` — `rv2_change_15a4d2808f1a792f3e21cfba`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Adjusted clipping to remove exploitable ledges and improve player movement
```

Extracted fields:

```json
{
  "change_text": "Adjusted clipping to remove exploitable ledges and improve player movement",
  "heading_path": [
    "Overpass"
  ],
  "entity": "Overpass",
  "entity_candidates": [
    "Overpass"
  ],
  "aspect": "speed_or_movement",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 622,
  "source_span_end": 696,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;status=acknowledged_or_planned;quality=flagged` — `rv2_change_3ff66f297c4ad042f2382a5c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We are aware and currently investigating some performance issues with difficulty 10, we have begun working on a fix
```

Extracted fields:

```json
{
  "change_text": "We are aware and currently investigating some performance issues with difficulty 10, we have begun working on a fix",
  "heading_path": [
    "Known Issues"
  ],
  "entity": null,
  "entity_candidates": [],
  "aspect": "performance_or_network",
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 13594,
  "source_span_end": 13709,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved"
  ]
}
```

### patch_change — `game=553850;status=acknowledged_or_planned;quality=flagged` — `rv2_change_e52c7ffc634783594044cbda`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
To compensate for lost rewards, we are working on an increased reward event
```

Extracted fields:

```json
{
  "change_text": "To compensate for lost rewards, we are working on an increased reward event",
  "heading_path": [],
  "entity": null,
  "entity_candidates": [],
  "aspect": "rewards_or_progression",
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 857,
  "source_span_end": 932,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved"
  ]
}
```

### patch_change — `game=553850;status=acknowledged_or_planned;quality=resolved` — `rv2_change_2a2bf6ad81baf2f01b00675e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Social menu fixes. We have fixed several issues and still have things to improve but know that we are aware and working tirelessly on this, we thank you for your patience and understanding.
```

Extracted fields:

```json
{
  "change_text": "Social menu fixes. We have fixed several issues and still have things to improve but know that we are aware and working tirelessly on this, we thank you for your patience and understanding.",
  "heading_path": [
    "Overview",
    "New swamp world"
  ],
  "entity": "Social",
  "entity_candidates": [
    "Social"
  ],
  "aspect": "interface_or_settings",
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 382,
  "source_span_end": 571,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;status=acknowledged_or_planned;quality=resolved` — `rv2_change_cb0208e3b07e28e5b780ede2`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We are investigating how we can further improve the play experience against this enemy.
```

Extracted fields:

```json
{
  "change_text": "We are investigating how we can further improve the play experience against this enemy.",
  "heading_path": [
    "Note"
  ],
  "entity": "Note",
  "entity_candidates": [
    "Note"
  ],
  "aspect": "rewards_or_progression",
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3119,
  "source_span_end": 3206,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;status=claimed_fix_with_uncertainty;quality=flagged` — `rv2_change_c2fe1e55d52c2c8447ae2dbb`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Based on the testing we have done we believe we have fixed future mission rewards but will continue to monitor this closely as it is our top priority
```

Extracted fields:

```json
{
  "change_text": "Based on the testing we have done we believe we have fixed future mission rewards but will continue to monitor this closely as it is our top priority",
  "heading_path": [],
  "entity": "Based",
  "entity_candidates": [
    "Based"
  ],
  "aspect": "content_or_feature",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "claimed_fix_with_uncertainty",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 703,
  "source_span_end": 852,
  "source_span_verified": true,
  "quality_flags": [
    "developer_fix_qualified"
  ]
}
```

### patch_change — `game=553850;status=implemented_bug_fix;quality=flagged` — `rv2_change_9e67f8a77fea640c6ae030ca`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed an issue where you could find several Confidential Data assets in Fortress locations
```

Extracted fields:

```json
{
  "change_text": "Fixed an issue where you could find several Confidential Data assets in Fortress locations",
  "heading_path": [
    "Fixes",
    "Impaler"
  ],
  "entity": null,
  "entity_candidates": [
    "Confidential Data",
    "Fortress"
  ],
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "you could find several Confidential Data assets in Fortress locations",
  "source_span_start": 24744,
  "source_span_end": 24834,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "entity_ambiguous"
  ]
}
```

### patch_change — `game=553850;status=implemented_bug_fix;quality=flagged` — `rv2_change_6fd8c9d16a1c6b0b15ddd078`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a bug with camera getting disjointed if entering ADS (Aim Down Sights) as you ragdoll
```

Extracted fields:

```json
{
  "change_text": "Fixed a bug with camera getting disjointed if entering ADS (Aim Down Sights) as you ragdoll",
  "heading_path": [
    "Primary Weapons",
    "SG-8P Punisher Plasma",
    "Miscellaneous Fixes"
  ],
  "entity": null,
  "entity_candidates": [
    "ADS",
    "Aim Down Sights"
  ],
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "if entering ADS (Aim Down Sights) as you ragdoll",
  "bug_symptom": "with camera getting disjointed",
  "source_span_start": 8272,
  "source_span_end": 8363,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "entity_ambiguous"
  ]
}
```

### patch_change — `game=553850;status=implemented_bug_fix;quality=resolved` — `rv2_change_4cf6673819806802298fe617`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed Various UI issues in the social menu.
```

Extracted fields:

```json
{
  "change_text": "Fixed Various UI issues in the social menu.",
  "heading_path": [
    "Social Menu fixes"
  ],
  "entity": "Social Menu fixes",
  "entity_candidates": [
    "Social Menu fixes"
  ],
  "aspect": "interface_or_settings",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6842,
  "source_span_end": 6885,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;status=implemented_bug_fix;quality=resolved` — `rv2_change_f3038f4afc370c9965318885`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed crash which could occur when browsing the acquisition center menus and alt-tabbing. (Windows)
```

Extracted fields:

```json
{
  "change_text": "Fixed crash which could occur when browsing the acquisition center menus and alt-tabbing. (Windows)",
  "heading_path": [
    "Crash Fixes"
  ],
  "entity": "Windows",
  "entity_candidates": [
    "Windows"
  ],
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4730,
  "source_span_end": 4829,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;status=implemented_change;quality=flagged` — `rv2_change_54cd7315b04c11a9c364a57c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We’ve increased the number of AI calculations the game can perform. This primarily impacts scenarios with a high number of spawned enemies, improving their response times in those situations. However, this comes with a slight trade-off in game performance.
```

Extracted fields:

```json
{
  "change_text": "We’ve increased the number of AI calculations the game can perform. This primarily impacts scenarios with a high number of spawned enemies, improving their response times in those situations. However, this comes with a slight trade-off in game performance.",
  "heading_path": [
    "Enemies"
  ],
  "entity": null,
  "entity_candidates": [
    "We’ve",
    "AI",
    "However"
  ],
  "aspect": "performance_or_network",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2084,
  "source_span_end": 2340,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "entity_ambiguous"
  ]
}
```

### patch_change — `game=553850;status=implemented_change;quality=flagged` — `rv2_change_1f5ee6d6ce2328c1531e918f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced situations where blue stratagems would bounce when placed next to the detector tower.
```

Extracted fields:

```json
{
  "change_text": "Reduced situations where blue stratagems would bounce when placed next to the detector tower.",
  "heading_path": [
    "Fixes"
  ],
  "entity": null,
  "entity_candidates": [],
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 16697,
  "source_span_end": 16790,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;status=implemented_change;quality=resolved` — `rv2_change_195fa025125dc9e506b64845`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 350 to 700
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 350 to 700",
  "heading_path": [
    "Stratagems",
    "MD-6 Anti-Personnel Minefield"
  ],
  "entity": "MD-6 Anti-Personnel Minefield",
  "entity_candidates": [
    "MD-6 Anti-Personnel Minefield"
  ],
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "350",
  "new_value": "700",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2764,
  "source_span_end": 2796,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;status=implemented_change;quality=resolved` — `rv2_change_8669e74a4f78c677a3c7694d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced the chance for crashes caused by fires
```

Extracted fields:

```json
{
  "change_text": "Reduced the chance for crashes caused by fires",
  "heading_path": [
    "Crash Fixes, Hangs and Soft-locks"
  ],
  "entity": "Crash Fixes, Hangs and Soft-locks",
  "entity_candidates": [
    "Crash Fixes, Hangs and Soft-locks"
  ],
  "aspect": "performance_or_network",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4396,
  "source_span_end": 4442,
  "source_span_verified": true,
  "quality_flags": []
}
```

### review_claim — `game=570;language_group=english` — `rv2_claim_bb9a8d4d1b30f9d199427556`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The Best Game
```

Extracted fields:

```json
{
  "claim_text_original": "The Best Game",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "The Best Game",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 0,
  "claim_span_end": 13,
  "review_revision_id": "rv1_review_revision_42875454bfc72c27d5a299cf",
  "review_created_at_utc": "2025-06-11 20:22:23+00:00",
  "review_updated_at_utc": "2025-06-11 20:22:23+00:00"
}
```

### review_claim — `game=570;language_group=english` — `rv2_claim_e3fe4e5a5248fa22ebe870b4`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
AFTER U MAKE THIS GAME U WANT PEOPLE TO SUFFER OR WHAT ?????
```

Extracted fields:

```json
{
  "claim_text_original": "AFTER U MAKE THIS GAME U WANT PEOPLE TO SUFFER OR WHAT ?????",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "AFTER U MAKE THIS GAME U WANT PEOPLE TO SUFFER OR WHAT ?????",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 437,
  "claim_span_end": 497,
  "review_revision_id": "rv1_review_revision_4665de0cfac53b6680ef3249",
  "review_created_at_utc": "2026-05-05 06:42:04+00:00",
  "review_updated_at_utc": "2026-05-05 06:42:04+00:00"
}
```

### review_claim — `game=570;language_group=other_languages` — `rv2_claim_f58cbc6b940b1aabcee45b28`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
very good
```

Extracted fields:

```json
{
  "claim_text_original": "very good",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "very good",
  "opinion_terms": [
    "good"
  ],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 9,
  "review_revision_id": "rv1_review_revision_27bf24295ab62ca1ad0c1f36",
  "review_created_at_utc": "2025-06-11 15:31:49+00:00",
  "review_updated_at_utc": "2025-06-11 15:31:49+00:00"
}
```

### review_claim — `game=570;language_group=other_languages` — `rv2_claim_65e95773b69fe5a3642d968c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
NADA MAS QUE AÑADIR
```

Extracted fields:

```json
{
  "claim_text_original": "NADA MAS QUE AÑADIR",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "NADA MAS QUE AÑADIR",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 20,
  "claim_span_end": 39,
  "review_revision_id": "rv1_review_revision_aa7e86c658fe9bd28f3b7757",
  "review_created_at_utc": "2026-05-03 15:37:19+00:00",
  "review_updated_at_utc": "2026-05-03 15:37:19+00:00"
}
```

### review_claim — `game=570;language_group=russian` — `rv2_claim_cafa27eb0171d5f1d679e09c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
откатите патч прошу 500 птс слито, удаляю игру до следующего пачта
```

Extracted fields:

```json
{
  "claim_text_original": "откатите патч прошу 500 птс слито, удаляю игру до следующего пачта",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "откатите патч прошу 500 птс слито, удаляю игру до следующего пачта",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 0,
  "claim_span_end": 66,
  "review_revision_id": "rv1_review_revision_358380acef19432ac1ec42b5",
  "review_created_at_utc": "2026-04-03 19:15:12+00:00",
  "review_updated_at_utc": "2026-04-03 19:15:12+00:00"
}
```

### review_claim — `game=570;language_group=russian` — `rv2_claim_bd44c9bfc90021d1f7924a93`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
после игры на инвокере научился играть на пианино
```

Extracted fields:

```json
{
  "claim_text_original": "после игры на инвокере научился играть на пианино",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "после игры на инвокере научился играть на пианино",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 0,
  "claim_span_end": 49,
  "review_revision_id": "rv1_review_revision_a1c2c09c5020da33b108f01c",
  "review_created_at_utc": "2026-05-17 17:35:06+00:00",
  "review_updated_at_utc": "2026-05-17 17:35:06+00:00"
}
```

### review_claim — `game=730;language_group=english` — `rv2_claim_527551bb99c02066d95cde0a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
https://steamcommunity.com/id/prollekings/inventory/#730_2_1905952422
```

Extracted fields:

```json
{
  "claim_text_original": "https://steamcommunity.com/id/prollekings/inventory/#730_2_1905952422",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "https://steamcommunity.com/id/prollekings/inventory/#730_2_1905952422",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 69,
  "review_revision_id": "rv1_review_revision_2e2d83a9ca967148be6c6702",
  "review_created_at_utc": "2025-11-11 19:22:49+00:00",
  "review_updated_at_utc": "2025-11-11 19:22:49+00:00"
}
```

### review_claim — `game=730;language_group=english` — `rv2_claim_dbce59780ba1663d3d4abb35`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The current status of the game is an absolute joke, and the developers seem completely detached from the community.
```

Extracted fields:

```json
{
  "claim_text_original": "The current status of the game is an absolute joke, and the developers seem completely detached from the community.",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "The current status of the game is an absolute joke, and the developers seem completely detached from the community.",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": true,
  "extraction_confidence": 0.48,
  "claim_span_start": 176,
  "claim_span_end": 291,
  "review_revision_id": "rv1_review_revision_97aed13e5f43b939007cd248",
  "review_created_at_utc": "2026-09-28 11:49:33+00:00",
  "review_updated_at_utc": "2026-09-28 11:49:33+00:00"
}
```

### review_claim — `game=730;language_group=other_languages` — `rv2_claim_0987340cfe7533bb825f7c74`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
ruskigame
```

Extracted fields:

```json
{
  "claim_text_original": "ruskigame",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "ruskigame",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 9,
  "review_revision_id": "rv1_review_revision_e33bf71252217dd023ea168e",
  "review_created_at_utc": "2026-07-22 21:18:04+00:00",
  "review_updated_at_utc": "2026-07-22 21:18:04+00:00"
}
```

### review_claim — `game=730;language_group=other_languages` — `rv2_claim_48dfca876f05a887e9d40141`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
mükemmel
```

Extracted fields:

```json
{
  "claim_text_original": "mükemmel",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "mükemmel",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 8,
  "review_revision_id": "rv1_review_revision_e89f7fe62c8f5226f9cf5614",
  "review_created_at_utc": "2024-11-13 18:50:45+00:00",
  "review_updated_at_utc": "2024-11-13 18:50:45+00:00"
}
```

### review_claim — `game=730;language_group=russian` — `rv2_claim_46694175f221219bc0487518`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
govno prime ne popukaite
```

Extracted fields:

```json
{
  "claim_text_original": "govno prime ne popukaite",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "govno prime ne popukaite",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 0,
  "claim_span_end": 24,
  "review_revision_id": "rv1_review_revision_52bef885dcc73572227a5974",
  "review_created_at_utc": "2025-11-04 15:10:37+00:00",
  "review_updated_at_utc": "2025-11-04 15:10:37+00:00"
}
```

### review_claim — `game=730;language_group=russian` — `rv2_claim_ad1f69ba2d92d5d0404f2ff1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
VALVE ВЫ ДЕТИ ЖАДНЫХ БЛЯДЕЙ КОТОРЫЕ СДОХНУТ В НИЩЕТЕ
```

Extracted fields:

```json
{
  "claim_text_original": "VALVE ВЫ ДЕТИ ЖАДНЫХ БЛЯДЕЙ КОТОРЫЕ СДОХНУТ В НИЩЕТЕ",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "VALVE ВЫ ДЕТИ ЖАДНЫХ БЛЯДЕЙ КОТОРЫЕ СДОХНУТ В НИЩЕТЕ",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 116,
  "claim_span_end": 168,
  "review_revision_id": "rv1_review_revision_51e8bd54663f3f13817c7cfa",
  "review_created_at_utc": "2026-02-04 06:04:18+00:00",
  "review_updated_at_utc": "2026-02-04 06:04:18+00:00"
}
```

### review_claim — `game=275850;language_group=english` — `rv2_claim_4f80da5c42c69edd55abbd46`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
After you have overcome the initial survival part it gets easier and even one planet has enough to do for hours of gameplay.
```

Extracted fields:

```json
{
  "claim_text_original": "After you have overcome the initial survival part it gets easier and even one planet has enough to do for hours of gameplay.",
  "referenced_entity": null,
  "aspect": "gameplay",
  "opinion_or_issue": "After you have overcome the initial survival part it gets easier and even one planet has enough to do for hours of gameplay.",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.68,
  "claim_span_start": 54,
  "claim_span_end": 178,
  "review_revision_id": "rv1_review_revision_c9f1b75811461d228a9570dd",
  "review_created_at_utc": "2025-06-13 11:53:50+00:00",
  "review_updated_at_utc": "2025-06-13 11:53:50+00:00"
}
```

### review_claim — `game=275850;language_group=english` — `rv2_claim_4c01f087ce74552836cef36f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
am EXTREAMLY dissapointed in how poorly it works on PC
```

Extracted fields:

```json
{
  "claim_text_original": "am EXTREAMLY dissapointed in how poorly it works on PC",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "am EXTREAMLY dissapointed in how poorly it works on PC",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 346,
  "claim_span_end": 400,
  "review_revision_id": "rv1_review_revision_0c1c29d0c8f4386f8aeb2377",
  "review_created_at_utc": "2025-09-10 00:24:13+00:00",
  "review_updated_at_utc": "2025-09-10 00:24:13+00:00"
}
```

### review_claim — `game=275850;language_group=other_languages` — `rv2_claim_6cb6b9a4cab2aeb52474d32b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
While you are overwhelmed by thousands of mechanics, which provide a lot of fun if you use them correctly, the publisher even creates more content in their enormous updates.
```

Extracted fields:

```json
{
  "claim_text_original": "While you are overwhelmed by thousands of mechanics, which provide a lot of fun if you use them correctly, the publisher even creates more content in their enormous updates.",
  "referenced_entity": null,
  "aspect": "content_or_feature",
  "opinion_or_issue": "While you are overwhelmed by thousands of mechanics, which provide a lot of fun if you use them correctly, the publisher even creates more content in their enormous updates.",
  "opinion_terms": [
    "fun"
  ],
  "polarity": "positive",
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.68,
  "claim_span_start": 56,
  "claim_span_end": 229,
  "review_revision_id": "rv1_review_revision_bd8d337670bd6e0aa7488c8a",
  "review_created_at_utc": "2026-04-09 14:59:14+00:00",
  "review_updated_at_utc": "2026-04-09 14:59:14+00:00"
}
```

### review_claim — `game=275850;language_group=other_languages` — `rv2_claim_f2910c874ebef7fe7f649a67`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Con cada actualización mejora todavía más.
```

Extracted fields:

```json
{
  "claim_text_original": "Con cada actualización mejora todavía más.",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "Con cada actualización mejora todavía más.",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 54,
  "claim_span_end": 96,
  "review_revision_id": "rv1_review_revision_259c494a61312bb60e4ed1a3",
  "review_created_at_utc": "2025-10-25 11:34:31+00:00",
  "review_updated_at_utc": "2025-10-25 11:34:31+00:00"
}
```

### review_claim — `game=275850;language_group=russian` — `rv2_claim_637a9c872902fa84b0333b01`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Для каждого действия приходится ждать порой чуть ли не до восьми (!!!)
```

Extracted fields:

```json
{
  "claim_text_original": "Для каждого действия приходится ждать порой чуть ли не до восьми (!!!)",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "Для каждого действия приходится ждать порой чуть ли не до восьми (!!!)",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 7190,
  "claim_span_end": 7260,
  "review_revision_id": "rv1_review_revision_e8e2677c1e17150d158b2968",
  "review_created_at_utc": "2025-08-14 14:53:40+00:00",
  "review_updated_at_utc": "2025-11-25 16:40:48+00:00"
}
```

### review_claim — `game=275850;language_group=russian` — `rv2_claim_87b9d76f2d0ea6a06e89adf0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Торговые посты, ну вы понимаете что из себя представляют.
```

Extracted fields:

```json
{
  "claim_text_original": "Торговые посты, ну вы понимаете что из себя представляют.",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "Торговые посты, ну вы понимаете что из себя представляют.",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 4181,
  "claim_span_end": 4238,
  "review_revision_id": "rv1_review_revision_fe711609c3d2d2055454c7dc",
  "review_created_at_utc": "2025-10-28 00:00:25+00:00",
  "review_updated_at_utc": "2026-10-07 00:07:26+00:00"
}
```

### review_claim — `game=553850;language_group=english` — `rv2_claim_f4e27444f5a8a11925649242`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
I come back to find the same old problems and worse issues with performance.
```

Extracted fields:

```json
{
  "claim_text_original": "I come back to find the same old problems and worse issues with performance.",
  "referenced_entity": null,
  "aspect": "performance_or_network",
  "opinion_or_issue": "I come back to find the same old problems and worse issues with performance.",
  "opinion_terms": [
    "worse"
  ],
  "polarity": "negative",
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.68,
  "claim_span_start": 3025,
  "claim_span_end": 3101,
  "review_revision_id": "rv1_review_revision_4ef826f8cc8d7a8c0f8cea42",
  "review_created_at_utc": "2026-06-30 08:59:26+00:00",
  "review_updated_at_utc": "2026-06-30 08:59:26+00:00"
}
```

### review_claim — `game=553850;language_group=english` — `rv2_claim_2825fbfcdf718014ce368030`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Get some Liberty
```

Extracted fields:

```json
{
  "claim_text_original": "Get some Liberty",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "Get some Liberty",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 0,
  "claim_span_end": 16,
  "review_revision_id": "rv1_review_revision_f87b9ff578e8fe6c9032a2c1",
  "review_created_at_utc": "2026-03-16 06:02:08+00:00",
  "review_updated_at_utc": "2026-03-16 06:02:08+00:00"
}
```

### review_claim — `game=553850;language_group=other_languages` — `rv2_claim_0728bba357d44736974baad9`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
这次更新箭头暂时恢复人籍
```

Extracted fields:

```json
{
  "claim_text_original": "这次更新箭头暂时恢复人籍",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "这次更新箭头暂时恢复人籍",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 12,
  "review_revision_id": "rv1_review_revision_d059525dd39a718a686b9a07",
  "review_created_at_utc": "2026-06-16 15:22:04+00:00",
  "review_updated_at_utc": "2026-06-16 15:22:04+00:00"
}
```

### review_claim — `game=553850;language_group=other_languages` — `rv2_claim_b34320f50c32bd24f3b92a68`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
good game
```

Extracted fields:

```json
{
  "claim_text_original": "good game",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "good game",
  "opinion_terms": [
    "good"
  ],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 9,
  "review_revision_id": "rv1_review_revision_d52ce64817819ee405214a2d",
  "review_created_at_utc": "2025-03-29 15:19:33+00:00",
  "review_updated_at_utc": "2025-03-29 15:19:33+00:00"
}
```

### review_claim — `game=553850;language_group=russian` — `rv2_claim_90435cec037e7e54f8f330d6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
На миссиях прикрывать друг другу спину, без единого сказанного слова это что-то с чем-то...
```

Extracted fields:

```json
{
  "claim_text_original": "На миссиях прикрывать друг другу спину, без единого сказанного слова это что-то с чем-то...",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "На миссиях прикрывать друг другу спину, без единого сказанного слова это что-то с чем-то...",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 3279,
  "claim_span_end": 3370,
  "review_revision_id": "rv1_review_revision_f01d3d7ab2be73c5a3d1ee31",
  "review_created_at_utc": "2026-09-20 08:54:09+00:00",
  "review_updated_at_utc": "2026-09-20 09:24:11+00:00"
}
```

### review_claim — `game=553850;language_group=russian` — `rv2_claim_8fb27d56412419a5f25f2bce`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Просто для этого нужно играть, а не ныть.
```

Extracted fields:

```json
{
  "claim_text_original": "Просто для этого нужно играть, а не ныть.",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "Просто для этого нужно играть, а не ныть.",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 190,
  "claim_span_end": 231,
  "review_revision_id": "rv1_review_revision_3cc044aaabab269c7f1d5fe8",
  "review_created_at_utc": "2026-09-16 22:38:09+00:00",
  "review_updated_at_utc": "2026-09-16 22:38:09+00:00"
}
```

## Output paths

The companion `manifest.json` records source table hashes, schema/extractor versions, and row counts. Parquet outputs are stored under the dataset directory printed by the CLI.
Patch-level and game-level summaries are in `patch_extraction_coverage.csv` and `game_extraction_coverage.csv` beside this report.
