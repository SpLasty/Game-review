# Stage 2 extraction quality report — rv2-b04a38cfdab527a59b39556b

Source Stage 1 run: `rv1-20261019T031033900187Z-a468b544`.
This report covers announcement classification, atomic patch-change extraction, review-claim segmentation, game-specific vocabulary, and temporal structure.
No patch-review pairs or relevance/training labels were generated.

## Dataset counts

| Dataset | Rows |
| --- | ---: |
| Announcements classified | 1,331 |
| Patch changes extracted | 3,154 |
| Review claims extracted | 74 |
| Game terminology entries | 1,516 |
| Patch episodes | 316 |
| Patch review-window segments | 60 |
| Review-window membership rows | 133,842 |
| Overlapping patch episode pairs | 1,161 |
| Same-entity temporal ambiguities | 806 |

## Coverage by game

| Game | Official-feed posts | Eligible episodes | Atomic changes | Review claims | Review revisions with claims | Complete window segments |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Counter-Strike 2 | 241 | 178 | 976 | 74 | 45 | 0/0 |
| Dota 2 | 101 | 52 | 777 | 0 | 0 | 0/0 |
| HELLDIVERS 2 | 164 | 75 | 1,401 | 0 | 0 | 0/0 |
| No Man's Sky | 29 | 11 | 0 | 0 | 0 | 0/0 |

## Extraction QA metrics

- Change rows with one or more unresolved fields: 1,260 (39.9%).
- Exact source-span validation failures: 0 (0.0%).
- Non-empty reviews with no claim row: 5.
- Low-confidence claims (<0.5): 48.
- Claims without an entity/aspect: 45 / 71; unknown polarity: 66.
- Change quality flags: `{"aspect_unresolved": 662, "developer_fix_qualified": 1, "entity_ambiguous": 347, "entity_unresolved": 776}`.
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

Inspection status: `awaiting_inspection` (0 of 34 sample rows recorded).

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
  "entity_candidates": [
    "If",
    "Steam"
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
  "source_span_start": 2030,
  "source_span_end": 2222,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "entity_ambiguous"
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
  "bug_trigger": null,
  "bug_symptom": "with Play Unranked where ticking Show All Modes could make the section unusable",
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
  "previous_value": "15",
  "new_value": "12",
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
  "bug_trigger": "when opening the pause menu",
  "bug_symptom": "for Linux users where the game would hang",
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

### patch_change — `game=730;status=implemented_change;quality=flagged` — `rv2_change_80e42969891e9a42529026da`

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
  "entity": null,
  "entity_candidates": [
    "Steam Workshop",
    "For",
    "ID",
    "URL",
    "Passing",
    "After the"
  ],
  "aspect": "capacity_or_ammunition",
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
  "quality_flags": [
    "entity_unresolved",
    "entity_ambiguous"
  ]
}
```

### patch_change — `game=730;status=implemented_change;quality=resolved` — `rv2_change_e85dbb1592932fa85c9d2558`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added an option to buffer server updates and user commands by one or more packets. This can be used to smooth over stuttering due to packet loss, at the expense of increased latency
```

Extracted fields:

```json
{
  "change_text": "Added an option to buffer server updates and user commands by one or more packets. This can be used to smooth over stuttering due to packet loss, at the expense of increased latency",
  "heading_path": [
    "Minor mix adjustments"
  ],
  "entity": "Minor mix adjustments",
  "entity_candidates": [
    "Minor mix adjustments"
  ],
  "aspect": "cooldown_or_timing",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3019,
  "source_span_end": 3200,
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

### patch_change — `game=553850;status=acknowledged_or_planned;quality=resolved` — `rv2_change_e52c7ffc634783594044cbda`

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
  "entity": "To",
  "entity_candidates": [
    "To"
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
  "source_span_start": 857,
  "source_span_end": 932,
  "source_span_verified": true,
  "quality_flags": []
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

### review_claim — `game=730;language_group=english` — `rv2_claim_d2e8a405420379c7ef333672`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
zobye
```

Extracted fields:

```json
{
  "claim_text_original": "zobye",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "zobye",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 5,
  "review_revision_id": "rv1_review_revision_e7b70be3de0f6c9e7e12e17d",
  "review_created_at_utc": "2024-11-13 22:33:17+00:00",
  "review_updated_at_utc": "2024-11-13 22:33:17+00:00"
}
```

### review_claim — `game=730;language_group=english` — `rv2_claim_8a66ea13973ccadeb37068a6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Thank You Valve For Making Our Childhood Great.
```

Extracted fields:

```json
{
  "claim_text_original": "Thank You Valve For Making Our Childhood Great.",
  "referenced_entity": "for",
  "aspect": null,
  "opinion_or_issue": "Thank You Valve For Making Our Childhood Great.",
  "opinion_terms": [
    "great"
  ],
  "polarity": "positive",
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.68,
  "claim_span_start": 934,
  "claim_span_end": 981,
  "review_revision_id": "rv1_review_revision_2bfc41900499208e97919dd2",
  "review_created_at_utc": "2024-11-13 23:14:54+00:00",
  "review_updated_at_utc": "2024-11-13 23:15:16+00:00"
}
```

### review_claim — `game=730;language_group=other_languages` — `rv2_claim_ab48e0335fd9675574d6a569`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
a comunidade é cheia de ragers mas o jogo é bom
```

Extracted fields:

```json
{
  "claim_text_original": "a comunidade é cheia de ragers mas o jogo é bom",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "a comunidade é cheia de ragers mas o jogo é bom",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 0,
  "claim_span_end": 47,
  "review_revision_id": "rv1_review_revision_b4e13e97c99456bb1b53f91e",
  "review_created_at_utc": "2024-11-13 22:42:01+00:00",
  "review_updated_at_utc": "2024-11-13 22:42:01+00:00"
}
```

### review_claim — `game=730;language_group=other_languages` — `rv2_claim_084c9ea118a9f94249ceada0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
compliqué de trouver des parties "correct"
```

Extracted fields:

```json
{
  "claim_text_original": "compliqué de trouver des parties \"correct\"",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "compliqué de trouver des parties \"correct\"",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 74,
  "claim_span_end": 116,
  "review_revision_id": "rv1_review_revision_044c7acaaacb1af0aa9874cb",
  "review_created_at_utc": "2024-11-13 22:41:31+00:00",
  "review_updated_at_utc": "2024-11-13 22:41:31+00:00"
}
```

### review_claim — `game=730;language_group=russian` — `rv2_claim_68032c4a9fb08f379e3293a1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
игра сынов ебучий блядей
```

Extracted fields:

```json
{
  "claim_text_original": "игра сынов ебучий блядей",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "игра сынов ебучий блядей",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 0,
  "claim_span_end": 24,
  "review_revision_id": "rv1_review_revision_c9f2bf66807769b3a141a368",
  "review_created_at_utc": "2024-11-13 22:37:20+00:00",
  "review_updated_at_utc": "2025-08-23 10:30:58+00:00"
}
```

### review_claim — `game=730;language_group=russian` — `rv2_claim_b0bf0cffd4a2138c721859ca`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
И как говорится "людям ошибаться свойственно" но вы видимо не человек а даже ЛУЧШЕ, так как если вы "совершите ошибку" то вас ждут бурные эмоции и овации от союзников, и желание встретиться с вами и вашей матушкой(да она у меня на расхват) видимо чтобы пожать вам руку.
```

Extracted fields:

```json
{
  "claim_text_original": "И как говорится \"людям ошибаться свойственно\" но вы видимо не человек а даже ЛУЧШЕ, так как если вы \"совершите ошибку\" то вас ждут бурные эмоции и овации от союзников, и желание встретиться с вами и вашей матушкой(да она у меня на расхват) видимо чтобы пожать вам руку.",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "И как говорится \"людям ошибаться свойственно\" но вы видимо не человек а даже ЛУЧШЕ, так как если вы \"совершите ошибку\" то вас ждут бурные эмоции и овации от союзников, и желание встретиться с вами и вашей матушкой(да она у меня на расхват) видимо чтобы пожать вам руку.",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 735,
  "claim_span_end": 1004,
  "review_revision_id": "rv1_review_revision_a14ad6a13e765b1eafa0da15",
  "review_created_at_utc": "2024-11-13 23:18:52+00:00",
  "review_updated_at_utc": "2024-12-08 16:59:47+00:00"
}
```

## Output paths

The companion `manifest.json` records source table hashes, schema/extractor versions, and row counts. Parquet outputs are stored under the dataset directory printed by the CLI.
Patch-level and game-level summaries are in `patch_extraction_coverage.csv` and `game_extraction_coverage.csv` beside this report.
