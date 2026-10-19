# Stage 2 extraction quality report — rv2-98a672e4a158674b8d8f42dd

Source Stage 1 run: `rv1-20261019T031033900187Z-a468b544`.
This report covers announcement classification, atomic patch-change extraction, review-claim segmentation, game-specific vocabulary, and temporal structure.
No patch-review pairs or relevance/training labels were generated.

## Dataset counts

| Dataset | Rows |
| --- | ---: |
| Announcements classified | 1,331 |
| Patch changes extracted | 5,249 |
| Review claims extracted | 74 |
| Game terminology entries | 1,671 |
| Patch episodes | 626 |
| Review-window membership rows | 161,282 |
| Overlapping patch episode pairs | 5,773 |
| Same-entity temporal ambiguities | 4,093 |

## Extraction QA metrics

- Change rows with one or more unresolved fields: 3,280 (62.5%).
- Exact source-span validation failures: 202 (3.8%).
- Non-empty reviews with no claim row: 5.
- Low-confidence claims (<0.5): 48.
- Claims without an entity/aspect: 46 / 71; unknown polarity: 66.
- Change quality flags: `{"aspect_unresolved": 2465, "entity_unresolved": 1527, "source_span_invalid": 202}`.
- Heading-only false changes: headings are maintained in hierarchy and are not emitted as changes.
- Patch specificity: claims remain `not_assigned`; temporal membership is not treated as relevance.

## Announcement categories

- `developer_acknowledgement_or_future_plan`: 117
- `major_gameplay_or_balance_update`: 210
- `minor_cosmetic_or_localization_update`: 63
- `new_feature_or_content`: 266
- `performance_or_stability_change`: 240
- `promotional_or_non_patch_announcement`: 713
- `specific_bug_fix`: 350

## Data limitations and common failure modes

- Deterministic rules are strongest for explicit Steam lists and numeric phrases. Nested hierarchy is retained, but prose without an explicit action predicate is omitted from `patch_changes`.
- Entity/aspect extraction may remain unresolved when a patch sentence uses implicit context or game-specific shorthand; those rows have quality flags and confidence values.
- A Steam announcement can link to a full official changelog that was not collected by Stage 1. Such URLs and completeness states are retained; Stage 2 did not fetch external pages.
- Review claims are sentence/contrast-clause spans. Aspect and polarity rules are conservative and English-heavy; non-English review text is retained verbatim, while unknown polarity remains null.
- Words such as `now`, `broken`, `nerfed`, and `unbalanced` do not make a claim patch-specific. The pipeline records lexical temporal cues only and assigns no patch relevance.
- Source review windows are incomplete for some patches in Stage 1; all memberships are explicitly temporal-only.

## Reproducible stratified audit sample

Selection seed: `stage2-audit-sample-2026-10`. The sample uses stable SHA-256 ranking within game/section for changes and game/Steam-language for claims, at up to 2 rows per stratum.
The sample records the original source excerpt beside the extracted fields. Spans refer to the original raw announcement body or exact review revision text.

### patch_change — `game=570;section=A SACK OF GIFTS TAKEN (BUT OFTEN BROUGHT BACK).` — `rv2_change_003af0639af5522b6e8559d1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
He emptied a sack and adjusted his helm.
```

Extracted fields:

```json
{
  "change_text": "He emptied a sack and adjusted his helm.",
  "heading_path": [
    "A SACK OF GIFTS TAKEN (BUT OFTEN BROUGHT BACK)."
  ],
  "entity": "A SACK OF GIFTS TAKEN (BUT OFTEN BROUGHT BACK).",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1143,
  "source_span_end": 1183,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Ability Draft` — `rv2_change_6a0033cc954e5479fd003792`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated ability pool to match the added/removed abilities for 7.41
```

Extracted fields:

```json
{
  "change_text": "Updated ability pool to match the added/removed abilities for 7.41",
  "heading_path": [
    "Ability Draft"
  ],
  "entity": "Ability Draft",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1494,
  "source_span_end": 1560,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Ability Draft` — `rv2_change_f4b64829c7376595e910819c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed Rearm not granting Keen Conveyance
```

Extracted fields:

```json
{
  "change_text": "Fixed Rearm not granting Keen Conveyance",
  "heading_path": [
    "Ability Draft"
  ],
  "entity": "Ability Draft",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1649,
  "source_span_end": 1689,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Ability Draft Fixes` — `rv2_change_33dee9c048bb5579ff7dab74`

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
    "A number of previously unavailable Scepter/Shard abilities are now granted, some abilities are accessed by toggling auto-cast on the base spell",
    "Unrefined Fireblast granted with Fireblast"
  ],
  "entity": "Unrefined Fireblast granted with Fireblast",
  "aspect": null,
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
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Ability Draft Fixes` — `rv2_change_5176e64ebd32130c40555954`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed Ogre Magi getting Multicast instead of Dumb Luck as an innate.
```

Extracted fields:

```json
{
  "change_text": "Fixed Ogre Magi getting Multicast instead of Dumb Luck as an innate.",
  "heading_path": [
    "Ability Draft Fixes",
    "A number of previously unavailable Scepter/Shard abilities are now granted, some abilities are accessed by toggling auto-cast on the base spell",
    "Unrefined Fireblast granted with Fireblast"
  ],
  "entity": "Unrefined Fireblast granted with Fireblast",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5441,
  "source_span_end": 5509,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Bug Fixes` — `rv2_change_f018fc6af3b1f48503e42017`

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
    "entity_unresolved"
  ]
}
```

### patch_change — `game=570;section=Bug Fixes` — `rv2_change_e1c874f5943127b8695665c3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed highlighting on the Neutral Item Slot to only highlight when there is at least one free token in the stash, rather than any item from any teammate
```

Extracted fields:

```json
{
  "change_text": "Fixed highlighting on the Neutral Item Slot to only highlight when there is at least one free token in the stash, rather than any item from any teammate",
  "heading_path": [
    "Bug Fixes"
  ],
  "entity": "Neutral Item Slot",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4853,
  "source_span_end": 5005,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Controlled Chaos` — `rv2_change_408f766dbb9903b243e1f4f9`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
At this point, we were no longer looking for game-breaking issues, but ways to adjust, balance and polish to a shine what we already knew was workin
```

Extracted fields:

```json
{
  "change_text": "At this point, we were no longer looking for game-breaking issues, but ways to adjust, balance and polish to a shine what we already knew was working.",
  "heading_path": [
    "Controlled Chaos"
  ],
  "entity": "Controlled Chaos",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 14138,
  "source_span_end": 14286,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=570;section=Controlled Chaos` — `rv2_change_7354d2498a264421ba6336f5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Even with a mostly finished game, we were still working on [i]Nest of Thorns[/i] right up until we shipped Act IV of Crownfall.
```

Extracted fields:

```json
{
  "change_text": "Even with a mostly finished game, we were still working on Nest of Thorns right up until we shipped Act IV of Crownfall.",
  "heading_path": [
    "Controlled Chaos"
  ],
  "entity": "Controlled Chaos",
  "aspect": null,
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 15335,
  "source_span_end": 15462,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Crownfall Act IV: The Spires of Skywrath` — `rv2_change_3989a8d9d5e7567204e07deb`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We've even added bonus content for Pathfinder pack owners for each act
```

Extracted fields:

```json
{
  "change_text": "We've even added bonus content for Pathfinder pack owners for each act.",
  "heading_path": [
    "Crownfall Act IV: The Spires of Skywrath"
  ],
  "entity": "Crownfall Act IV: The Spires of Skywrath",
  "aspect": "content_or_feature",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2545,
  "source_span_end": 2615,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=570;section=Dark Carnival` — `rv2_change_a05749fbb85c372e645cff15`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed Candy Shop Rerolls granted from the Fortune Teller being capped by the weekly maximum
```

Extracted fields:

```json
{
  "change_text": "Fixed Candy Shop Rerolls granted from the Fortune Teller being capped by the weekly maximum",
  "heading_path": [
    "Dark Carnival"
  ],
  "entity": "Dark Carnival",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 752,
  "source_span_end": 843,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Dark Carnival` — `rv2_change_82cbe5cc6881f7513b063cf8`

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
  "entity": "Dark Carnival",
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

### patch_change — `game=570;section=Dota Labs Updates` — `rv2_change_2ed871371993cb432fc553ba`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Lastly, because we've gotten so many useful submissions from the Feedback button built into the Crownfall map, we've added one to the Dota Labs UI as well.
```

Extracted fields:

```json
{
  "change_text": "Lastly, because we've gotten so many useful submissions from the Feedback button built into the Crownfall map, we've added one to the Dota Labs UI as well.",
  "heading_path": [
    "Dota Labs Updates",
    "We announced Dota Labs a couple months ago, and since then we've continued to iterate quietly on the features in it as we get feedback and data. \"Quietly\" is fine, but sometimes it can be useful to be a bit louder so today we're turning up the volume a little"
  ],
  "entity": "We announced Dota Labs a couple months ago, and since then we've continued to iterate quietly on the features in it as we get feedback and data. \"Quietly\" is fine, but sometimes it can be useful to be a bit louder so today we're turning up the volume a little",
  "aspect": "map_or_level",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 885,
  "source_span_end": 1040,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=570;section=Dota Plus Pre-Match Matchmaker Analytics` — `rv2_change_d238748c695377471cd1940b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Some prefer to get into a match as quickly as possible, and are willing to accept a higher skill variance in the game to save some time
```

Extracted fields:

```json
{
  "change_text": "Some prefer to get into a match as quickly as possible, and are willing to accept a higher skill variance in the game to save some time.",
  "heading_path": [
    "Dota Plus Pre-Match Matchmaker Analytics"
  ],
  "entity": "Dota Plus Pre-Match Matchmaker Analytics",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3114,
  "source_span_end": 3249,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=570;section=Dota Plus Pre-Match Matchmaker Analytics` — `rv2_change_2dcaf00b4bb7b95f7eb588fe`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
First, while players are good at describing their preferences to other people, they aren't necessarily good at describing their preferences as inputs to a complex, global matchmaking algorithm ("I value skill variance 13% higher than the average Dota player!"). How can we create tools that let players express their preferences naturally and directly?
```

Extracted fields:

```json
{
  "change_text": "First, while players are good at describing their preferences to other people, they aren't necessarily good at describing their preferences as inputs to a complex, global matchmaking algorithm (\"I value skill variance 13% higher than the average Dota player!\"). How can we create tools that let players express their preferences naturally and directly?",
  "heading_path": [
    "Dota Plus Pre-Match Matchmaker Analytics",
    "We've long wanted to build features to let players find matches that better align with their individual preferences. Early attempts ran into two main problems"
  ],
  "entity": "We've long wanted to build features to let players find matches that better align with their individual preferences. Early attempts ran into two main problems",
  "aspect": "matchmaking_or_ranked",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3672,
  "source_span_end": 4024,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=570;section=For clarity, Frostivus Gift contents vary per account` — `rv2_change_3e3a84daa79b73190f404a20`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
For all other accounts: free cosmetic items, with higher behavior score accounts receiving higher-tier items
```

Extracted fields:

```json
{
  "change_text": "For all other accounts: free cosmetic items, with higher behavior score accounts receiving higher-tier items",
  "heading_path": [
    "For clarity, Frostivus Gift contents vary per account"
  ],
  "entity": "For clarity, Frostivus Gift contents vary per account",
  "aspect": "cosmetic_or_localization",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1358,
  "source_span_end": 1466,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=570;section=Frostivus Forge` — `rv2_change_ea128712fa628f99a0a9e2d6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Each item requires a different recipe to craft, and you can unlock higher tiers by completing rewards in the lower tiers first
```

Extracted fields:

```json
{
  "change_text": "Each item requires a different recipe to craft, and you can unlock higher tiers by completing rewards in the lower tiers first.",
  "heading_path": [
    "Frostivus Forge"
  ],
  "entity": "Frostivus Forge",
  "aspect": "rewards_or_progression",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2961,
  "source_span_end": 3087,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=570;section=General` — `rv2_change_b6b708b0c9deff14d316fd54`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed bots getting stuck while dewarding
```

Extracted fields:

```json
{
  "change_text": "Fixed bots getting stuck while dewarding",
  "heading_path": [
    "General"
  ],
  "entity": null,
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1631,
  "source_span_end": 1671,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved"
  ]
}
```

### patch_change — `game=570;section=General` — `rv2_change_9819bb2c33975f9010031316`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed Tower Glyph of Fortification Multishot attacks incorrectly having True Strike
```

Extracted fields:

```json
{
  "change_text": "Fixed Tower Glyph of Fortification Multishot attacks incorrectly having True Strike",
  "heading_path": [
    "General"
  ],
  "entity": "Fortification Multishot",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2106,
  "source_span_end": 2189,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=General Fixes` — `rv2_change_e127e64ca3b73aeab215ad54`

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
  "entity": "General Fixes",
  "aspect": null,
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
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=General Fixes` — `rv2_change_da80f179151a4af3eaae7924`

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
  "entity": "General Fixes",
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
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Hero Builds` — `rv2_change_229e4e7fa4b150d3f3ef9521`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
But more importantly, their [i]goals[/i] changed.
```

Extracted fields:

```json
{
  "change_text": "But more importantly, their goals changed.",
  "heading_path": [
    "Hero Builds"
  ],
  "entity": "Hero Builds",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8218,
  "source_span_end": 8267,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Hero Builds` — `rv2_change_830afd8b11c66b2b3928eebd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
After a playtest, we'd sometimes find that coworkers no longer wanted to talk to us about their highs and lows
```

Extracted fields:

```json
{
  "change_text": "After a playtest, we'd sometimes find that coworkers no longer wanted to talk to us about their highs and lows.",
  "heading_path": [
    "Hero Builds"
  ],
  "entity": "Hero Builds",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9929,
  "source_span_end": 10039,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=570;section=Heroes` — `rv2_change_baffbbc98ef744031c2982ff`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed Ember Spirit's Fire Remnant's Shard Upgrade tooltip not specifying a Fire Remnant is spawned when Ember Spirit dies
```

Extracted fields:

```json
{
  "change_text": "Fixed Ember Spirit's Fire Remnant's Shard Upgrade tooltip not specifying a Fire Remnant is spawned when Ember Spirit dies",
  "heading_path": [
    "Heroes"
  ],
  "entity": "Heroes",
  "aspect": "interface_or_settings",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4370,
  "source_span_end": 4491,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=570;section=Heroes` — `rv2_change_1a912b3d4e9b164a06b0912d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed Rubick not spawning an urnaconda when stealing it from Shadow Shaman
```

Extracted fields:

```json
{
  "change_text": "Fixed Rubick not spawning an urnaconda when stealing it from Shadow Shaman",
  "heading_path": [
    "Heroes"
  ],
  "entity": "Heroes",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6371,
  "source_span_end": 6445,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Introducing Dota Labs` — `rv2_change_ba38a71a9c0eb563ae5b1f58`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
"The last time you introduced a new named Dota thing, you called it Between the Lanes, and it's been some months since you last posted one of those.
```

Extracted fields:

```json
{
  "change_text": "\"The last time you introduced a new named Dota thing, you called it Between the Lanes, and it's been some months since you last posted one of those.\"",
  "heading_path": [
    "Introducing Dota Labs",
    "The initial set of Dota Labs features includes",
    "High-Visibility Local Hero Healthbar"
  ],
  "entity": "High-Visibility Local Hero Healthbar",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4660,
  "source_span_end": 4808,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=570;section=Introducing Dota Labs` — `rv2_change_61b7819788280290a36ed5d7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
In addition to the Dota+ content, today's update introduces a set of experimental features available to all Dota players, and a new way for us to ship experiments like them: Dota Labs.
```

Extracted fields:

```json
{
  "change_text": "In addition to the Dota+ content, today's update introduces a set of experimental features available to all Dota players, and a new way for us to ship experiments like them: Dota Labs.",
  "heading_path": [
    "Introducing Dota Labs"
  ],
  "entity": "Introducing Dota Labs",
  "aspect": "content_or_feature",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2254,
  "source_span_end": 2438,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=570;section=Items` — `rv2_change_a1e16ccbb1ceb7de60f5300a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed Gem of True Sight radius not updating dynamically with Area of Effect changing values
```

Extracted fields:

```json
{
  "change_text": "Fixed Gem of True Sight radius not updating dynamically with Area of Effect changing values",
  "heading_path": [
    "Items"
  ],
  "entity": "Items",
  "aspect": "range_or_radius",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2846,
  "source_span_end": 2937,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=570;section=Items` — `rv2_change_1f5177ac9537d24767ec20a7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Soul Ring's temporary mana now displays as a separate segment in the mana bar while it's available
```

Extracted fields:

```json
{
  "change_text": "Soul Ring's temporary mana now displays as a separate segment in the mana bar while it's available",
  "heading_path": [
    "Items"
  ],
  "entity": "Items",
  "aspect": null,
  "action": "modified",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2593,
  "source_span_end": 2691,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Kez` — `rv2_change_29c5e1c29f8868a5378ef75f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed Shen and Dragonus arcana style unlocks not applying to respective cursor icon packs
```

Extracted fields:

```json
{
  "change_text": "Fixed Shen and Dragonus arcana style unlocks not applying to respective cursor icon packs",
  "heading_path": [
    "Kez"
  ],
  "entity": "Kez",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1037,
  "source_span_end": 1126,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Kez` — `rv2_change_985520031e48ccf7878791a2`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Spoon Man: fixed an issue where the mouse cursor would stay invisible after a popup
```

Extracted fields:

```json
{
  "change_text": "Spoon Man: fixed an issue where the mouse cursor would stay invisible after a popup",
  "heading_path": [
    "Kez"
  ],
  "entity": "Kez",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "after a popup",
  "bug_symptom": "the mouse cursor would stay invisible",
  "source_span_start": 1724,
  "source_span_end": 1807,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=570;section=Like last year, awards will be granted to participating players based on their performance relative to everyone else. The Tyrian Regalia treasure is making a royal return with five refashioned Immortal items, exclusively available to the top performing players. New this year is the Terrain Token, which will allow winners to choose one of six returning custom terrains, including Reef's Edge and Immortal Gardens. Look for more information, including reward tiers and lots of details, in the Rewards section of the main Dota 2 menu.` — `rv2_change_7f8818d4a45bce4442f4bd88`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Good news for you: We also just shipped a new gameplay patch along with a ton of content fixes.
```

Extracted fields:

```json
{
  "change_text": "Good news for you: We also just shipped a new gameplay patch along with a ton of content fixes.",
  "heading_path": [
    "Like last year, awards will be granted to participating players based on their performance relative to everyone else. The Tyrian Regalia treasure is making a royal return with five refashioned Immortal items, exclusively available to the top performing players. New this year is the Terrain Token, which will allow winners to choose one of six returning custom terrains, including Reef's Edge and Immortal Gardens. Look for more information, including reward tiers and lots of details, in the Rewards section of the main Dota 2 menu.",
    "All of this is great but I did my predictions and my fantasy and supported the teams and talent already. What do I do now?"
  ],
  "entity": "All of this is great but I did my predictions and my fantasy and supported the teams and talent already. What do I do now?",
  "aspect": "gameplay",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3869,
  "source_span_end": 3964,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=570;section=Looking Back` — `rv2_change_2f9727374cf3883be0eef73c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Every fan cheering in the arena, every fantasy roster and prediction made around the world, all the strategy proclamations made from the safety of your own home, the production staff that builds the show, and of course the players competing in the booths — it all adds up to an incredibly special event that we're honored to take part in
```

Extracted fields:

```json
{
  "change_text": "Every fan cheering in the arena, every fantasy roster and prediction made around the world, all the strategy proclamations made from the safety of your own home, the production staff that builds the show, and of course the players competing in the booths — it all adds up to an incredibly special event that we're honored to take part in.",
  "heading_path": [
    "Looking Back"
  ],
  "entity": "Looking Back",
  "aspect": "map_or_level",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2890,
  "source_span_end": 3227,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=570;section=Matchmaking Hero Ban Rework` — `rv2_change_ceb5b3353f27d59fa73f52e8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
As we investigate each cheat, we're primarily focused on understanding what they're doing and how we can track and stop it
```

Extracted fields:

```json
{
  "change_text": "As we investigate each cheat, we're primarily focused on understanding what they're doing and how we can track and stop it.",
  "heading_path": [
    "Matchmaking Hero Ban Rework"
  ],
  "entity": "Matchmaking Hero Ban Rework",
  "aspect": null,
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 497,
  "source_span_end": 619,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=570;section=Matchmaking Hero Ban Rework` — `rv2_change_26dc0be85ced9ac8a320accf`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
With today's update, we've removed the start-of-match ban phase and replaced it with ban preferences stored with your account.
```

Extracted fields:

```json
{
  "change_text": "With today's update, we've removed the start-of-match ban phase and replaced it with ban preferences stored with your account.",
  "heading_path": [
    "Matchmaking Hero Ban Rework"
  ],
  "entity": "Matchmaking Hero Ban Rework",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1720,
  "source_span_end": 1846,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Over the last few days we've made the following changes` — `rv2_change_9142050cb397840bc3c30d35`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Crownfall: Fixed Nest of Thorns Loading Screen not being visible.
```

Extracted fields:

```json
{
  "change_text": "Crownfall: Fixed Nest of Thorns Loading Screen not being visible.",
  "heading_path": [
    "Over the last few days we've made the following changes"
  ],
  "entity": "Over the last few days we've made the following changes",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 995,
  "source_span_end": 1060,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Over the last few days we've made the following changes` — `rv2_change_65b79d204ee0086bfb373d88`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Nest of Thorns: Fixed Rot's Scepter obscuring various visual elements in the game.
```

Extracted fields:

```json
{
  "change_text": "Nest of Thorns: Fixed Rot's Scepter obscuring various visual elements in the game.",
  "heading_path": [
    "Over the last few days we've made the following changes"
  ],
  "entity": "Over the last few days we've made the following changes",
  "aspect": "visuals_or_graphics",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1532,
  "source_span_end": 1614,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=570;section=Predictions are back: How will the Swiss matches shake out? What about the bracket? Fun fact: Exactly zero have ever gotten the full Swiss stage results correct. Will you be the first this year? Not if you don't get your guesses in before the first match starts (10am CST, Thursday 8/13).` — `rv2_change_843f5f0943a7415cf99cdf5b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We've introduced a new customization point: You
```

Extracted fields:

```json
{
  "change_text": "We've introduced a new customization point: You.",
  "heading_path": [
    "Predictions are back: How will the Swiss matches shake out? What about the bracket? Fun fact: Exactly zero have ever gotten the full Swiss stage results correct. Will you be the first this year? Not if you don't get your guesses in before the first match starts (10am CST, Thursday 8/13).",
    "I'm a huge fan of my favorite team but also I dislike all of their choices and wish I was in charge."
  ],
  "entity": "I'm a huge fan of my favorite team but also I dislike all of their choices and wish I was in charge.",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2694,
  "source_span_end": 2741,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=570;section=Predictions are back: How will the Swiss matches shake out? What about the bracket? Fun fact: Exactly zero have ever gotten the full Swiss stage results correct. Will you be the first this year? Not if you don't get your guesses in before the first match starts (10am CST, Thursday 8/13).` — `rv2_change_d9b8f3419c6dc3e155e51c74`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We've also updated prefixes, suffixes, and the player drafting rules
```

Extracted fields:

```json
{
  "change_text": "We've also updated prefixes, suffixes, and the player drafting rules.",
  "heading_path": [
    "Predictions are back: How will the Swiss matches shake out? What about the bracket? Fun fact: Exactly zero have ever gotten the full Swiss stage results correct. Will you be the first this year? Not if you don't get your guesses in before the first match starts (10am CST, Thursday 8/13).",
    "I'm a huge fan of my favorite team but also I dislike all of their choices and wish I was in charge."
  ],
  "entity": "I'm a huge fan of my favorite team but also I dislike all of their choices and wish I was in charge.",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2841,
  "source_span_end": 2909,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=570;section=RELATED LINKS` — `rv2_change_f8e1b3960f1eefb703f386b7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Sizable VAC ban wave hits supposedly innocent CS2 players, including one of the creators behind a newly added map
```

Extracted fields:

```json
{
  "change_text": "Sizable VAC ban wave hits supposedly innocent CS2 players, including one of the creators behind a newly added map",
  "heading_path": [
    "RELATED LINKS"
  ],
  "entity": "RELATED LINKS",
  "aspect": "map_or_level",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1440,
  "source_span_end": 1553,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=570;section=THE MOONLIGHT TIARA, AND MUCH MORE,` — `rv2_change_a9df1945c76984c4c6678532`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
"[b]SOME GIFTS I'VE IMPROVED, AND SOME I'VE DERANGED.
```

Extracted fields:

```json
{
  "change_text": "\"SOME GIFTS I'VE IMPROVED, AND SOME I'VE DERANGED.",
  "heading_path": [
    "THE MOONLIGHT TIARA, AND MUCH MORE,"
  ],
  "entity": "THE MOONLIGHT TIARA, AND MUCH MORE,",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1543,
  "source_span_end": 1596,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=The First Six Minutes` — `rv2_change_8cd323e741b43ccbf33b37a6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Eventually they figured out the precise combination of overpowered abilities that we hadn't fine-tuned yet, and beat the part of the game that wasn't meant to be beaten.
```

Extracted fields:

```json
{
  "change_text": "Eventually they figured out the precise combination of overpowered abilities that we hadn't fine-tuned yet, and beat the part of the game that wasn't meant to be beaten.",
  "heading_path": [
    "The First Six Minutes"
  ],
  "entity": "The First Six Minutes",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 13595,
  "source_span_end": 13764,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=The International` — `rv2_change_cb42c30b5d6dcb3319a0d705`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Their opponents: the dangerous Gaimin Gladiators, the squad that swept this year's Major tournaments and whose in-your-face early-game tactics had already shattered the hopes of so many lower bracket teams.
```

Extracted fields:

```json
{
  "change_text": "Their opponents: the dangerous Gaimin Gladiators, the squad that swept this year's Major tournaments and whose in-your-face early-game tactics had already shattered the hopes of so many lower bracket teams.",
  "heading_path": [
    "The International"
  ],
  "entity": "The International",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2713,
  "source_span_end": 2919,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=The International` — `rv2_change_38b95c9fd63e8be3448d5fdd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
As an added bonus, all eight teams who reach The International will have at least one signing session at the arena on Thursday or Friday
```

Extracted fields:

```json
{
  "change_text": "As an added bonus, all eight teams who reach The International will have at least one signing session at the arena on Thursday or Friday.",
  "heading_path": [
    "The International"
  ],
  "entity": "The International",
  "aspect": "range_or_radius",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1999,
  "source_span_end": 2135,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=570;section=The International Team and Talent Bundles` — `rv2_change_9b2dc13f64846f1eaf7a66cb`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
All around the world fans gather to support their local communities in [i]their[/i] language and so for the first time, we've added supporter bundles for some of the larger community broadcasts as well
```

Extracted fields:

```json
{
  "change_text": "All around the world fans gather to support their local communities in their language and so for the first time, we've added supporter bundles for some of the larger community broadcasts as well.",
  "heading_path": [
    "The International Team and Talent Bundles"
  ],
  "entity": "The International Team and Talent Bundles",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1041,
  "source_span_end": 1242,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=570;section=Tinker's Keen Conveyance` — `rv2_change_e2e771a45395f08c0c094471`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed Hoodwink and Ogre Magi's ultimate abilities not being levelable via hotkey
```

Extracted fields:

```json
{
  "change_text": "Fixed Hoodwink and Ogre Magi's ultimate abilities not being levelable via hotkey",
  "heading_path": [
    "Tinker's Keen Conveyance"
  ],
  "entity": "Tinker's Keen Conveyance",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4055,
  "source_span_end": 4135,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=Tinker's Keen Conveyance` — `rv2_change_e53a063e0aab5739a1012d8f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed Roshan's Roar not playing the fx/animation
```

Extracted fields:

```json
{
  "change_text": "Fixed Roshan's Roar not playing the fx/animation",
  "heading_path": [
    "Tinker's Keen Conveyance"
  ],
  "entity": "Tinker's Keen Conveyance",
  "aspect": "visuals_or_graphics",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3118,
  "source_span_end": 3166,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=570;section=Updated Seasonal Quests & Guild Rewards` — `rv2_change_5514425d51898d1863dd1a5c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Guild rewards have also been updated, making new emoticons, sprays, and chat wheels available to high-scoring guilds
```

Extracted fields:

```json
{
  "change_text": "Guild rewards have also been updated, making new emoticons, sprays, and chat wheels available to high-scoring guilds.",
  "heading_path": [
    "Updated Seasonal Quests & Guild Rewards"
  ],
  "entity": "Updated Seasonal Quests & Guild Rewards",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1493,
  "source_span_end": 1609,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=570;section=Winter 2024 Heroes' Hoard` — `rv2_change_cd63c5de6c80b8ac8081aab4`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Then we added some new taunts
```

Extracted fields:

```json
{
  "change_text": "Then we added some new taunts.",
  "heading_path": [
    "Winter 2024 Heroes' Hoard"
  ],
  "entity": "Winter 2024 Heroes' Hoard",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3692,
  "source_span_end": 3721,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=570;section=unsectioned` — `rv2_change_3e154dc997d0aecea3604d31`

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
  "entity": null,
  "aspect": null,
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
  "quality_flags": [
    "entity_unresolved",
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=570;section=unsectioned` — `rv2_change_d57956df61c50a36957392ad`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed Lich's Level 25 "Frost Shield Provides +50 HP Regen" working on units with pip-based health (Undying Tombstone, Shadow Shaman Mass Serpent Wards, etc)
```

Extracted fields:

```json
{
  "change_text": "Fixed Lich's Level 25 \"Frost Shield Provides +50 HP Regen\" working on units with pip-based health (Undying Tombstone, Shadow Shaman Mass Serpent Wards, etc)",
  "heading_path": [],
  "entity": null,
  "aspect": "health_or_durability",
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1077,
  "source_span_end": 1233,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved"
  ]
}
```

### patch_change — `game=730;section=A Call to Arms-ory` — `rv2_change_27c1c7410d41881e71efe7d8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
To submit weapon finishes and/or stickers to the Call to Arms, select the appropriate option using the updated Counter-Strike 2 Workshop Tool:
```

Extracted fields:

```json
{
  "change_text": "To submit weapon finishes and/or stickers to the Call to Arms, select the appropriate option using the updated Counter-Strike 2 Workshop Tool:",
  "heading_path": [
    "A Call to Arms-ory",
    "We are also looking for stickers inspired by two different themes"
  ],
  "entity": "Counter-Strike",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 969,
  "source_span_end": 1111,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Agency` — `rv2_change_b5ece2efe681e28059e7e224`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3339983232"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Agency"
  ],
  "entity": "Agency",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 41,
  "source_span_end": 198,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Agency` — `rv2_change_af946217dd7f268337dd48a2`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3339983232"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Agency"
  ],
  "entity": "Agency",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 973,
  "source_span_end": 1130,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Alpine` — `rv2_change_cdaf85184a1537167cc83521`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3221491619"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Alpine"
  ],
  "entity": "Alpine",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 448,
  "source_span_end": 605,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Ancient` — `rv2_change_d14867c6f4fbd73e87206ba4`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a case where player shadows could be seen through geometry
```

Extracted fields:

```json
{
  "change_text": "Fixed a case where player shadows could be seen through geometry",
  "heading_path": [
    "Ancient"
  ],
  "entity": "Ancient",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "player shadows could be seen through geometry",
  "source_span_start": 4704,
  "source_span_end": 4768,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Ancient` — `rv2_change_48b1d23ffb1c3b1bf8a549ef`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Adjusted Flip knife animation when inspecting immediately after deploying.
```

Extracted fields:

```json
{
  "change_text": "Adjusted Flip knife animation when inspecting immediately after deploying.",
  "heading_path": [
    "Ancient"
  ],
  "entity": "Ancient",
  "aspect": "visuals_or_graphics",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 347,
  "source_span_end": 421,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Ancient and Shoots` — `rv2_change_821161c60ac1744ea327c0bd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed knife slashes applying a 'dry' attack decal on wet surfaces.
```

Extracted fields:

```json
{
  "change_text": "Fixed knife slashes applying a 'dry' attack decal on wet surfaces.",
  "heading_path": [
    "Ancient and Shoots"
  ],
  "entity": "Ancient and Shoots",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 525,
  "source_span_end": 591,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Ancient and Shoots` — `rv2_change_a4868db11c77a9bc941cf116`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Improved deploy +quick inspect animations for the AK, Galil, AUG, PP-Bizon.
```

Extracted fields:

```json
{
  "change_text": "Improved deploy +quick inspect animations for the AK, Galil, AUG, PP-Bizon.",
  "heading_path": [
    "Ancient and Shoots"
  ],
  "entity": "Ancient and Shoots",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 652,
  "source_span_end": 727,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Answering the Call` — `rv2_change_8a9e01db4f42842ba12e4dde`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Two new sticker collections, Fruits & Vegetables and Auto Racing, have also been added to the Armory.
```

Extracted fields:

```json
{
  "change_text": "Two new sticker collections, Fruits & Vegetables and Auto Racing, have also been added to the Armory.",
  "heading_path": [
    "Answering the Call"
  ],
  "entity": "Answering the Call",
  "aspect": "cosmetic_or_localization",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1491,
  "source_span_end": 1592,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Anubis` — `rv2_change_2271316bbf82dede4e12f4e5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added a Settings Recommendation popup if NVIDIA G-Sync support is detected but not enabled at startup. Using G-Sync is generally recommended if your system supports it.
```

Extracted fields:

```json
{
  "change_text": "Added a Settings Recommendation popup if NVIDIA G-Sync support is detected but not enabled at startup. Using G-Sync is generally recommended if your system supports it.",
  "heading_path": [
    "Anubis",
    "Settings Recommendations"
  ],
  "entity": "Settings Recommendations",
  "aspect": "interface_or_settings",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1505,
  "source_span_end": 1673,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Anubis` — `rv2_change_3a0464738cfa1b81f92d1e65`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed clipping above walkway stairs in Palace
```

Extracted fields:

```json
{
  "change_text": "Fixed clipping above walkway stairs in Palace",
  "heading_path": [
    "Anubis"
  ],
  "entity": "Anubis",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2814,
  "source_span_end": 2859,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Assembly` — `rv2_change_345e5260938f767e35681579`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url=https://steamcommunity.com/sharedfiles/filedetails/changelog/3071005299]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Assembly"
  ],
  "entity": "Assembly",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1375,
  "source_span_end": 1530,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Assembly` — `rv2_change_09c825efb18d0896fd215e8c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url=https://steamcommunity.com/sharedfiles/filedetails/changelog/3071005299]Update Notes[/url]).
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes).",
  "heading_path": [
    "Assembly"
  ],
  "entity": "Assembly",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 179,
  "source_span_end": 335,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Baggage` — `rv2_change_247fa250b7c3259886d582c1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed movement hitch on lower conveyor
```

Extracted fields:

```json
{
  "change_text": "Fixed movement hitch on lower conveyor",
  "heading_path": [
    "Baggage"
  ],
  "entity": "Baggage",
  "aspect": "speed_or_movement",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2685,
  "source_span_end": 2723,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Baggage` — `rv2_change_1e69f01ea05b66b7c5fe0da4`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Lowered height of central conveyor tray to help open sniper view
```

Extracted fields:

```json
{
  "change_text": "Lowered height of central conveyor tray to help open sniper view",
  "heading_path": [
    "Baggage"
  ],
  "entity": "Baggage",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2727,
  "source_span_end": 2791,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Basalt` — `rv2_change_54d3db4d80bf8026d458bd38`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url=https://steamcommunity.com/sharedfiles/filedetails/changelog/3329258290]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Basalt"
  ],
  "entity": "Basalt",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 628,
  "source_span_end": 783,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Basalt` — `rv2_change_0229718293c556296476a492`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to latest version from Community Workshop ([url=https://steamcommunity.com/sharedfiles/filedetails/changelog/3329258290]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to latest version from Community Workshop (Update Notes)",
  "heading_path": [
    "Basalt"
  ],
  "entity": "Basalt",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2222,
  "source_span_end": 2369,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Boulder` — `rv2_change_a4e5229a59dec4fe1ddabbbf`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3663186989"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Boulder"
  ],
  "entity": "Boulder",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 42,
  "source_span_end": 199,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Boulder` — `rv2_change_e53d7de05e525b6f773384c2`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3663186989"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Boulder"
  ],
  "entity": "Boulder",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 468,
  "source_span_end": 625,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Brewery` — `rv2_change_9a163d7f02a0566c64e72439`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url=https://steamcommunity.com/sharedfiles/filedetails/changelog/3070290240]Update Notes[/url]).
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes).",
  "heading_path": [
    "Brewery"
  ],
  "entity": "Brewery",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 533,
  "source_span_end": 689,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Cache` — `rv2_change_8c734329182ebcfe50dc73f6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Disabled player collision on sign and removed lamp by squeaky.
```

Extracted fields:

```json
{
  "change_text": "Disabled player collision on sign and removed lamp by squeaky.",
  "heading_path": [
    "Cache"
  ],
  "entity": "Cache",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 133,
  "source_span_end": 195,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Cache` — `rv2_change_e7e86b92cdc21d13b805fc88`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed hole in world on door in Sun Room.
```

Extracted fields:

```json
{
  "change_text": "Fixed hole in world on door in Sun Room.",
  "heading_path": [
    "Cache"
  ],
  "entity": "Cache",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 465,
  "source_span_end": 505,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Community Maps` — `rv2_change_e1e15236a668071bed303fed`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3329258290]Basalt[/url] and [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3328169568]Edin[/url] to Competitive, Casual, and Deathmatch modes.
```

Extracted fields:

```json
{
  "change_text": "Added Basalt and Edin to Competitive, Casual, and Deathmatch modes.",
  "heading_path": [
    "Community Maps"
  ],
  "entity": "Community Maps",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2292,
  "source_span_end": 2513,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Community Maps` — `rv2_change_bb64fa22c9016c9c1315e204`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added community maps [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3165559377]Memento[/url] and [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3071005299]Assembly[/url] to the Wingman map pool
```

Extracted fields:

```json
{
  "change_text": "Added community maps Memento and Assembly to the Wingman map pool",
  "heading_path": [
    "Community Maps"
  ],
  "entity": "Community Maps",
  "aspect": "map_or_level",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 287,
  "source_span_end": 506,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Debris` — `rv2_change_3799ece2400cc553b1b6acf1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3539217452"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Debris"
  ],
  "entity": "Debris",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 665,
  "source_span_end": 822,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Demo/Replay viewer improvements` — `rv2_change_f76d74912c69162fc1a17580`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Camera controls now use click-and-drag scheme
```

Extracted fields:

```json
{
  "change_text": "Camera controls now use click-and-drag scheme",
  "heading_path": [
    "Demo/Replay viewer improvements"
  ],
  "entity": "Demo/Replay viewer improvements",
  "aspect": "capacity_or_ammunition",
  "action": "modified",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 125,
  "source_span_end": 170,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Demo/Replay viewer improvements` — `rv2_change_bd4c0b15079fa9e730eb813a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed some minor issues when seeking to a different position in the demo file
```

Extracted fields:

```json
{
  "change_text": "Fixed some minor issues when seeking to a different position in the demo file",
  "heading_path": [
    "Demo/Replay viewer improvements"
  ],
  "entity": "Demo/Replay viewer improvements",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 251,
  "source_span_end": 328,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Deprecated "Couch" viewmodel position setting` — `rv2_change_3b28106faf9737bd35f63aa1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased Zeus movement speed and adjusted the attack cone
```

Extracted fields:

```json
{
  "change_text": "Increased Zeus movement speed and adjusted the attack cone",
  "heading_path": [
    "Deprecated \"Couch\" viewmodel position setting"
  ],
  "entity": "Deprecated \"Couch\" viewmodel position setting",
  "aspect": "speed_or_movement",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1437,
  "source_span_end": 1495,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Deprecated "Couch" viewmodel position setting` — `rv2_change_6197fbf9494073922e213920`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added a "Dropped Weapons" panel, which shows (and allows the direct pickup of) weapons that have been dropped by teammates that are standing in the buy zone
```

Extracted fields:

```json
{
  "change_text": "Added a \"Dropped Weapons\" panel, which shows (and allows the direct pickup of) weapons that have been dropped by teammates that are standing in the buy zone",
  "heading_path": [
    "Deprecated \"Couch\" viewmodel position setting"
  ],
  "entity": "Deprecated \"Couch\" viewmodel position setting",
  "aspect": "purchase_price_or_cost",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1111,
  "source_span_end": 1267,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Dogtown` — `rv2_change_731f1309d15634db5847df7f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Various fixes for running on Linux with SDL_VIDEODRIVER=wayland.
```

Extracted fields:

```json
{
  "change_text": "Various fixes for running on Linux with SDL_VIDEODRIVER=wayland.",
  "heading_path": [
    "Dogtown"
  ],
  "entity": "Dogtown",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1014,
  "source_span_end": 1078,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Dogtown` — `rv2_change_baf130da6321513377a66243`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3414036782"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Dogtown"
  ],
  "entity": "Dogtown",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1171,
  "source_span_end": 1328,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Dust 2` — `rv2_change_cbb248efb613f348b86ebf3f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed hole in brick stack on bombsite B
```

Extracted fields:

```json
{
  "change_text": "Fixed hole in brick stack on bombsite B",
  "heading_path": [
    "Dust 2"
  ],
  "entity": "Dust 2",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 220,
  "source_span_end": 259,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Dust 2` — `rv2_change_469c42ffbdf9fd7b1bd21894`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed bug preventing custom sounds from being played in community maps
```

Extracted fields:

```json
{
  "change_text": "Fixed bug preventing custom sounds from being played in community maps",
  "heading_path": [
    "Dust 2"
  ],
  "entity": "Dust 2",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "preventing custom sounds from being played in community maps",
  "source_span_start": 263,
  "source_span_end": 333,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Dust II` — `rv2_change_aa8a503ee2fdd131d1da708a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a gap in geometry.
```

Extracted fields:

```json
{
  "change_text": "Fixed a gap in geometry.",
  "heading_path": [
    "Dust II"
  ],
  "entity": "Dust II",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1368,
  "source_span_end": 1392,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Dust II` — `rv2_change_11d805cd35160302282c441e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a pixel gap in a door Outside Long.
```

Extracted fields:

```json
{
  "change_text": "Fixed a pixel gap in a door Outside Long.",
  "heading_path": [
    "Dust II"
  ],
  "entity": "Dust II",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 366,
  "source_span_end": 407,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Dust2` — `rv2_change_eb8f24fe27047538d385273e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed some clipping at B site
```

Extracted fields:

```json
{
  "change_text": "Fixed some clipping at B site",
  "heading_path": [
    "Dust2"
  ],
  "entity": "Dust2",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5143,
  "source_span_end": 5172,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Dust2` — `rv2_change_7492ba5364affbac77ba2458`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Changed the collision properties on railings to emit the correct footstep sounds
```

Extracted fields:

```json
{
  "change_text": "Changed the collision properties on railings to emit the correct footstep sounds",
  "heading_path": [
    "Dust2"
  ],
  "entity": "Dust2",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1390,
  "source_span_end": 1470,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Edin` — `rv2_change_5c0f0d099cfb883e1c0b1c28`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url=https://steamcommunity.com/sharedfiles/filedetails/changelog/3328169568]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Edin"
  ],
  "entity": "Edin",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 739,
  "source_span_end": 894,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=El Dorado` — `rv2_change_875ec447c5b705b8eccf92fb`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3408790618"]Update Notes[/url]).
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes).",
  "heading_path": [
    "El Dorado"
  ],
  "entity": "El Dorado",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 642,
  "source_span_end": 800,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Fachwerk` — `rv2_change_44d9eee09896c921a665c497`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3442040035"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Fachwerk"
  ],
  "entity": "Fachwerk",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 680,
  "source_span_end": 837,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Fachwerk` — `rv2_change_ff8c724868fbd8542c3e54d9`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3442040035"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Fachwerk"
  ],
  "entity": "Fachwerk",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 270,
  "source_span_end": 427,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Get out of there, it's gonna blow!` — `rv2_change_9acc3f332f173448cb289dc1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Season 5 has arrived with some explosive changes to CS2--bomb damage has been completely reworked.
```

Extracted fields:

```json
{
  "change_text": "Season 5 has arrived with some explosive changes to CS2--bomb damage has been completely reworked.",
  "heading_path": [
    "Get out of there, it's gonna blow!"
  ],
  "entity": "Get out of there, it's gonna blow!",
  "aspect": "damage_or_attack_power",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 481,
  "source_span_end": 579,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Grail` — `rv2_change_cea7e2a430e9e928b5d0a753`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3246527710"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Grail"
  ],
  "entity": "Grail",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 776,
  "source_span_end": 933,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Grail` — `rv2_change_4fb3a1caadf1cb25eb163dad`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a case where fire was visible through smoke.
```

Extracted fields:

```json
{
  "change_text": "Fixed a case where fire was visible through smoke.",
  "heading_path": [
    "Grail"
  ],
  "entity": "Grail",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "fire was visible through smoke",
  "source_span_start": 365,
  "source_span_end": 415,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=In support of Animgraph 2, the logic adjusting player height on sloped surfaces has been refactored.` — `rv2_change_9c3396deeda7d4bca7306498`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
As a result of this change, grenade lineups on sloped surfaces may have changed.
```

Extracted fields:

```json
{
  "change_text": "As a result of this change, grenade lineups on sloped surfaces may have changed.",
  "heading_path": [
    "In support of Animgraph 2, the logic adjusting player height on sloped surfaces has been refactored."
  ],
  "entity": "In support of Animgraph 2, the logic adjusting player height on sloped surfaces has been refactored.",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1047,
  "source_span_end": 1127,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=In support of Animgraph 2, the logic adjusting player height on sloped surfaces has been refactored.` — `rv2_change_7e7cf5a3fed27e6f72448edf`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Player height on ramps is now consistent and no longer depends on approach direction.
```

Extracted fields:

```json
{
  "change_text": "Player height on ramps is now consistent and no longer depends on approach direction.",
  "heading_path": [
    "In support of Animgraph 2, the logic adjusting player height on sloped surfaces has been refactored."
  ],
  "entity": "In support of Animgraph 2, the logic adjusting player height on sloped surfaces has been refactored.",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 948,
  "source_span_end": 1033,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Incendiary Grenade` — `rv2_change_07a48919cdc6f7fc0110f89b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced area covered by spreading flames
```

Extracted fields:

```json
{
  "change_text": "Reduced area covered by spreading flames",
  "heading_path": [
    "Incendiary Grenade"
  ],
  "entity": "Incendiary Grenade",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 652,
  "source_span_end": 692,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Incendiary Grenade` — `rv2_change_cbd9325a651a2b9f41e19d68`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced duration
```

Extracted fields:

```json
{
  "change_text": "Reduced duration",
  "heading_path": [
    "Incendiary Grenade"
  ],
  "entity": "Incendiary Grenade",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 632,
  "source_span_end": 648,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Inferno` — `rv2_change_8d18e6b89d289574dcede129`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added roughness texture to foil stickers in the Item Editor
```

Extracted fields:

```json
{
  "change_text": "Added roughness texture to foil stickers in the Item Editor",
  "heading_path": [
    "Inferno"
  ],
  "entity": "Inferno",
  "aspect": "visuals_or_graphics",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3052,
  "source_span_end": 3111,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Inferno` — `rv2_change_6c5795d6f809db1a6664c87f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Changed the collision properties on railings to emit the correct footstep sounds
```

Extracted fields:

```json
{
  "change_text": "Changed the collision properties on railings to emit the correct footstep sounds",
  "heading_path": [
    "Inferno"
  ],
  "entity": "Inferno",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1204,
  "source_span_end": 1284,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Italy` — `rv2_change_65367be49468c73633897522`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added to competitive matchmaking
```

Extracted fields:

```json
{
  "change_text": "Added to competitive matchmaking",
  "heading_path": [
    "Italy"
  ],
  "entity": "Italy",
  "aspect": "matchmaking_or_ranked",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5202,
  "source_span_end": 5234,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Italy` — `rv2_change_6bb36663d712b88d14fcc821`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed some bad boost spots.
```

Extracted fields:

```json
{
  "change_text": "Fixed some bad boost spots.",
  "heading_path": [
    "Italy"
  ],
  "entity": "Italy",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2952,
  "source_span_end": 2979,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Italy, Nuke, Mirage, Inferno` — `rv2_change_0f2cf18aa67d7d2fb8be0ec7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Changed some player collision surface types
```

Extracted fields:

```json
{
  "change_text": "Changed some player collision surface types",
  "heading_path": [
    "Italy, Nuke, Mirage, Inferno"
  ],
  "entity": "Italy, Nuke, Mirage, Inferno",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 327,
  "source_span_end": 370,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Jura` — `rv2_change_bd28867f253ca265c24284c4`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url=https://steamcommunity.com/sharedfiles/filedetails/changelog/3261289969]Update Notes[/url]).
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes).",
  "heading_path": [
    "Jura"
  ],
  "entity": "Jura",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 165,
  "source_span_end": 321,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Jura` — `rv2_change_5f29dc3e4b99762c0d09c6dc`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop.
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop.",
  "heading_path": [
    "Jura"
  ],
  "entity": "Jura",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 632,
  "source_span_end": 690,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Made jump animations directional` — `rv2_change_073a0e8345096ab96f85bbf9`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed an issue where sometimes a Sabre agent would say hostage related lines when cheering
```

Extracted fields:

```json
{
  "change_text": "Fixed an issue where sometimes a Sabre agent would say hostage related lines when cheering",
  "heading_path": [
    "Made jump animations directional"
  ],
  "entity": "Made jump animations directional",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "when cheering",
  "bug_symptom": "sometimes a Sabre agent would say hostage related lines",
  "source_span_start": 1041,
  "source_span_end": 1131,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Made jump animations directional` — `rv2_change_f3a2c6463d5cffe51e2696ca`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed issue with Shadow Daggers playing catch sound during looping inspect animation
```

Extracted fields:

```json
{
  "change_text": "Fixed issue with Shadow Daggers playing catch sound during looping inspect animation",
  "heading_path": [
    "Made jump animations directional"
  ],
  "entity": "Made jump animations directional",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "during looping inspect animation",
  "bug_symptom": "with Shadow Daggers playing catch sound",
  "source_span_start": 662,
  "source_span_end": 746,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Memento` — `rv2_change_9162ca500875d6e22ffa1bd5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url=https://steamcommunity.com/sharedfiles/filedetails/changelog/3165559377]Update Notes[/url]).
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes).",
  "heading_path": [
    "Memento"
  ],
  "entity": "Memento",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 369,
  "source_span_end": 525,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Memento` — `rv2_change_a02d11e327af1af8ae096707`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added 2024 Copenhagen Major trophies to player profiles.
```

Extracted fields:

```json
{
  "change_text": "Added 2024 Copenhagen Major trophies to player profiles.",
  "heading_path": [
    "Memento"
  ],
  "entity": "Memento",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 652,
  "source_span_end": 708,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Mills` — `rv2_change_3570bd475fa75346d0cbec7e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed erroneous target aim punch animation during client-side shooting.
```

Extracted fields:

```json
{
  "change_text": "Fixed erroneous target aim punch animation during client-side shooting.",
  "heading_path": [
    "Mills"
  ],
  "entity": "Mills",
  "aspect": "visuals_or_graphics",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 494,
  "source_span_end": 565,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Mills` — `rv2_change_ab76a58bb708ab842932ef87`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url=https://steamcommunity.com/sharedfiles/filedetails/changelog/3152430710]Update Notes[/url]).
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes).",
  "heading_path": [
    "Mills"
  ],
  "entity": "Mills",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 147,
  "source_span_end": 303,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Minor mix adjustments` — `rv2_change_e85dbb1592932fa85c9d2558`

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

### patch_change — `game=730;section=Minor mix adjustments` — `rv2_change_189a45bd91a373a8e842aab7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The amount of peeker's advantage in the steady state is reduced by 16ms
```

Extracted fields:

```json
{
  "change_text": "The amount of peeker's advantage in the steady state is reduced by 16ms",
  "heading_path": [
    "Minor mix adjustments"
  ],
  "entity": "Minor mix adjustments",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": -16.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2715,
  "source_span_end": 2786,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Minor style adjustments` — `rv2_change_97522fc37230fbf74b8d6398`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced the amount of performance stutter at end-of-round time
```

Extracted fields:

```json
{
  "change_text": "Reduced the amount of performance stutter at end-of-round time",
  "heading_path": [
    "Minor style adjustments"
  ],
  "entity": "Minor style adjustments",
  "aspect": "performance_or_network",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 313,
  "source_span_end": 375,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Mirage` — `rv2_change_67c264c3dbefd4e189b21c18`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a bug where certain keys not found on US keyboards (such as the backslash key on UK keyboards) couldn't be bound
```

Extracted fields:

```json
{
  "change_text": "Fixed a bug where certain keys not found on US keyboards (such as the backslash key on UK keyboards) couldn't be bound",
  "heading_path": [
    "Mirage"
  ],
  "entity": "Mirage",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "certain keys not found on US keyboards (such as the backslash key on UK keyboards) couldn't be bound",
  "source_span_start": 1008,
  "source_span_end": 1126,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Mirage` — `rv2_change_ab5a8b571cd746eb46edc0c8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed disappearing geometry in apartments.
```

Extracted fields:

```json
{
  "change_text": "Fixed disappearing geometry in apartments.",
  "heading_path": [
    "Mirage"
  ],
  "entity": "Mirage",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 165,
  "source_span_end": 207,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=New Armory Content` — `rv2_change_68af6cae782b044a0d2753d3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
[video webm="{STEAM_CLAN_IMAGE}/3381077/9b6ecf851f93202f7c7e3a1a6c1e80fd29e71239.webm" mp4="{STEAM_CLAN_IMAGE}/3381077/c2e64c689b7e6aa8ea134de7c06b6e0cea790a4d.mp4" poster="https://clan.akamai.steamstatic.com/images/3381077/7490b11599e34e5b309e1680892689cde14a69eb.png" autoplay="true" controls="false"][/video]A few months ago we added charms to the workshop, and you responded.
```

Extracted fields:

```json
{
  "change_text": "[video webm=\"{STEAM_CLAN_IMAGE}/3381077/9b6ecf851f93202f7c7e3a1a6c1e80fd29e71239.webm\" mp4=\"{STEAM_CLAN_IMAGE}/3381077/c2e64c689b7e6aa8ea134de7c06b6e0cea790a4d.mp4\" poster=\"https://clan.akamai.steamstatic.com/images/3381077/7490b11599e34e5b309e1680892689cde14a69eb.png\" autoplay=\"true\" controls=\"false\"]A few months ago we added charms to the workshop, and you responded.",
  "heading_path": [
    "New Armory Content"
  ],
  "entity": "New Armory Content",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1294,
  "source_span_end": 1673,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=New Drop Collections` — `rv2_change_6e06ecb66d63bb5bc39ff96e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Three new weapon collections have been added to the care package drop list, so keep an eye out for items from the all-new Ascent, Boreal, and Radiant collections
```

Extracted fields:

```json
{
  "change_text": "Three new weapon collections have been added to the care package drop list, so keep an eye out for items from the all-new Ascent, Boreal, and Radiant collections.",
  "heading_path": [
    "New Drop Collections"
  ],
  "entity": "New Drop Collections",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 266,
  "source_span_end": 427,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=730;section=New additions to the Armory` — `rv2_change_c89e8d1d4b1819c1382fe219`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
And one more thing, we have added a new Limited Edition Item: the XM1014 | Solitude.
```

Extracted fields:

```json
{
  "change_text": "And one more thing, we have added a new Limited Edition Item: the XM1014 | Solitude.",
  "heading_path": [
    "New additions to the Armory"
  ],
  "entity": "New additions to the Armory",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5391,
  "source_span_end": 5475,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Nuke` — `rv2_change_72ff2192365734d2e42c9c4c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed some disappearing geometry
```

Extracted fields:

```json
{
  "change_text": "Fixed some disappearing geometry",
  "heading_path": [
    "Nuke"
  ],
  "entity": "Nuke",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5457,
  "source_span_end": 5489,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Nuke` — `rv2_change_b8e744629ce987a8513afd71`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fix for the sun material not blooming and adjusted the size of the material
```

Extracted fields:

```json
{
  "change_text": "Fix for the sun material not blooming and adjusted the size of the material",
  "heading_path": [
    "Nuke"
  ],
  "entity": "Nuke",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 830,
  "source_span_end": 905,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Office` — `rv2_change_78bb4cd5565c770aa93a9088`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed some lighting errors on low settings
```

Extracted fields:

```json
{
  "change_text": "Fixed some lighting errors on low settings",
  "heading_path": [
    "Office",
    "General grenade clip polish"
  ],
  "entity": "General grenade clip polish",
  "aspect": "visuals_or_graphics",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5182,
  "source_span_end": 5224,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Office` — `rv2_change_0c910175099437685ec47211`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed geometry in the problematic jumping corner.
```

Extracted fields:

```json
{
  "change_text": "Fixed geometry in the problematic jumping corner.",
  "heading_path": [
    "Office"
  ],
  "entity": "Office",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 979,
  "source_span_end": 1028,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Overpass` — `rv2_change_cef3c6a8223e639dc99561e6`

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

### patch_change — `game=730;section=Overpass` — `rv2_change_15a4d2808f1a792f3e21cfba`

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

### patch_change — `game=730;section=Overpass, Nuke, Vertigo, Mirage and Office` — `rv2_change_c3d6b09706bc95832bde91a4`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Bug and exploit fixes
```

Extracted fields:

```json
{
  "change_text": "Bug and exploit fixes",
  "heading_path": [
    "Overpass, Nuke, Vertigo, Mirage and Office"
  ],
  "entity": "Overpass, Nuke, Vertigo, Mirage and Office",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2475,
  "source_span_end": 2496,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Overpass, Nuke, Vertigo, Mirage and Office` — `rv2_change_513eae85268e21be0cfcb39c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
USP-S | Jawbreaker: Corrected ambient occlusion texture
```

Extracted fields:

```json
{
  "change_text": "USP-S | Jawbreaker: Corrected ambient occlusion texture",
  "heading_path": [
    "Overpass, Nuke, Vertigo, Mirage and Office",
    "Minor performance improvements"
  ],
  "entity": "Minor performance improvements",
  "aspect": "visuals_or_graphics",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2677,
  "source_span_end": 2732,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Palais` — `rv2_change_0abb0a6c127d478ae2d94c58`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added r_allow_low_gpu_memory_mode setting to allow running CS2 Workshop Tools in low memory GPU conditions.
```

Extracted fields:

```json
{
  "change_text": "Added r_allow_low_gpu_memory_mode setting to allow running CS2 Workshop Tools in low memory GPU conditions.",
  "heading_path": [
    "Palais"
  ],
  "entity": "Palais",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1251,
  "source_span_end": 1358,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Palais` — `rv2_change_07c8a39696bdeed3e235079b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed various bugs in Hammer.
```

Extracted fields:

```json
{
  "change_text": "Fixed various bugs in Hammer.",
  "heading_path": [
    "Palais"
  ],
  "entity": "Palais",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1363,
  "source_span_end": 1392,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Pool Day` — `rv2_change_1a18ace477a7bf24f74fc971`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url=https://steamcommunity.com/sharedfiles/filedetails/changelog/3263935964]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Pool Day"
  ],
  "entity": "Pool Day",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 225,
  "source_span_end": 380,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Pool Day` — `rv2_change_627138880790c1cbcfcd7fe7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed G-Sync detection to also work in non-windowed fullscreen mode
```

Extracted fields:

```json
{
  "change_text": "Fixed G-Sync detection to also work in non-windowed fullscreen mode",
  "heading_path": [
    "Pool Day"
  ],
  "entity": "Pool Day",
  "aspect": "content_or_feature",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 429,
  "source_span_end": 496,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Poseidon` — `rv2_change_5a9d5270f5c36015cf96018c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3522144043"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Poseidon"
  ],
  "entity": "Poseidon",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 573,
  "source_span_end": 730,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Poseidon` — `rv2_change_f0104ef19295f0808487bf9c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3522144043"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Poseidon"
  ],
  "entity": "Poseidon",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 467,
  "source_span_end": 624,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Q. How do souvenirs work this time?` — `rv2_change_e05140dd506e08727f282f09`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
If the weapon had any existing stickers, they will be removed before you craft your souvenir.
```

Extracted fields:

```json
{
  "change_text": "If the weapon had any existing stickers, they will be removed before you craft your souvenir.",
  "heading_path": [
    "Q. How do souvenirs work this time?"
  ],
  "entity": "Q. How do souvenirs work this time?",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5305,
  "source_span_end": 5398,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Q. What if the sticker price goes down after I redeem my tokens?` — `rv2_change_7ea0b311b0d0bb6ad3d79e71`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
If the price of any redeemed sticker decreases by 25 tokens or more within the next 24 hours, we'll automatically issue you a refund of tokens for the difference between your redemption price and the lowest price in that period.
```

Extracted fields:

```json
{
  "change_text": "If the price of any redeemed sticker decreases by 25 tokens or more within the next 24 hours, we'll automatically issue you a refund of tokens for the difference between your redemption price and the lowest price in that period.",
  "heading_path": [
    "Q. What if the sticker price goes down after I redeem my tokens?"
  ],
  "entity": "Q. What if the sticker price goes down after I redeem my tokens?",
  "aspect": "purchase_price_or_cost",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": -25.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4622,
  "source_span_end": 4850,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Re-organized Casual and Deathmatch map groups.` — `rv2_change_f8f7bab327514ecae365cbd5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Removed snd_setmixer, snd_setmixlayer, snd_soundmixer_setmixlayer_amount, and snd_soundmixer_set_trigger_factor console commands.
```

Extracted fields:

```json
{
  "change_text": "Removed snd_setmixer, snd_setmixlayer, snd_soundmixer_setmixlayer_amount, and snd_soundmixer_set_trigger_factor console commands.",
  "heading_path": [
    "Re-organized Casual and Deathmatch map groups."
  ],
  "entity": "Re-organized Casual and Deathmatch map groups.",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1019,
  "source_span_end": 1148,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Re-organized Casual and Deathmatch map groups.` — `rv2_change_f98b9dc9c519baef44775fc8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added "Main Menu Ambience Volume" setting.
```

Extracted fields:

```json
{
  "change_text": "Added \"Main Menu Ambience Volume\" setting.",
  "heading_path": [
    "Re-organized Casual and Deathmatch map groups."
  ],
  "entity": "Re-organized Casual and Deathmatch map groups.",
  "aspect": "audio",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 782,
  "source_span_end": 824,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Revised some common chat strings` — `rv2_change_3bbbbbdaf3b2c1bdbc936826`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed case where round stats in the Watch Menu would be assigned to the wrong side
```

Extracted fields:

```json
{
  "change_text": "Fixed case where round stats in the Watch Menu would be assigned to the wrong side",
  "heading_path": [
    "Revised some common chat strings"
  ],
  "entity": "Revised some common chat strings",
  "aspect": "interface_or_settings",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "round stats in the Watch Menu would be assigned to the wrong side",
  "source_span_start": 3146,
  "source_span_end": 3228,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Revised some common chat strings` — `rv2_change_d01618a533560410d82be647`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed round-delayed stats not updating at match end
```

Extracted fields:

```json
{
  "change_text": "Fixed round-delayed stats not updating at match end",
  "heading_path": [
    "Revised some common chat strings"
  ],
  "entity": "Revised some common chat strings",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2766,
  "source_span_end": 2817,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Sanctum` — `rv2_change_51b950271062d67ac71b5fc0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3643331442"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Sanctum"
  ],
  "entity": "Sanctum",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1012,
  "source_span_end": 1169,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Sanctum` — `rv2_change_ed126bdee9298b9b8ea7d7aa`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3643331442"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Sanctum"
  ],
  "entity": "Sanctum",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 958,
  "source_span_end": 1115,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Shelter` — `rv2_change_25b3dc6d19e3534971c7ff6f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3737179295"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Shelter"
  ],
  "entity": "Shelter",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 878,
  "source_span_end": 1035,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Shelter` — `rv2_change_901afa7b4711cdf30aa4a20f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3737179295"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Shelter"
  ],
  "entity": "Shelter",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 373,
  "source_span_end": 530,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Shoots` — `rv2_change_b8ba08329d1dd822e72dd6f3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Various grenade and player clipping fixes.
```

Extracted fields:

```json
{
  "change_text": "Various grenade and player clipping fixes.",
  "heading_path": [
    "Shoots"
  ],
  "entity": "Shoots",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 695,
  "source_span_end": 737,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Smokes now cast shadows` — `rv2_change_343339aff2fefec625f1527c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added a "Refund All" button to the buy menu
```

Extracted fields:

```json
{
  "change_text": "Added a \"Refund All\" button to the buy menu",
  "heading_path": [
    "Smokes now cast shadows"
  ],
  "entity": "Smokes now cast shadows",
  "aspect": "purchase_price_or_cost",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1263,
  "source_span_end": 1306,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Smokes now cast shadows` — `rv2_change_10276565cc79da3a3351e300`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added a setting to disable first person bullet tracers
```

Extracted fields:

```json
{
  "change_text": "Added a setting to disable first person bullet tracers",
  "heading_path": [
    "Smokes now cast shadows"
  ],
  "entity": "Smokes now cast shadows",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1310,
  "source_span_end": 1364,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Souvenir Highlight Packages` — `rv2_change_c79209e6557458084d7c0a56`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
So stay tuned—Souvenir Highlight Packages will be redeemable shortly after the Major comes to a close
```

Extracted fields:

```json
{
  "change_text": "So stay tuned—Souvenir Highlight Packages will be redeemable shortly after the Major comes to a close!",
  "heading_path": [
    "Souvenir Highlight Packages"
  ],
  "entity": "Souvenir Highlight Packages",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1153,
  "source_span_end": 1254,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=730;section=Stronghold` — `rv2_change_a20df1208722c8ee93fa8d67`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3477094554"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Stronghold"
  ],
  "entity": "Stronghold",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 374,
  "source_span_end": 531,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Stronghold` — `rv2_change_40135112276bf527903ddb8f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3477094554"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Stronghold"
  ],
  "entity": "Stronghold",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 931,
  "source_span_end": 1088,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Today we are releasing six new music kits with NIGHTMODE Records. NIGHTMODE II Music Kits are now available in the STORE tab, featuring` — `rv2_change_554249c5f65a167dfecffb30`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Alongside new music kits, we've continued updating Cache and made other miscellaneous fixes.
```

Extracted fields:

```json
{
  "change_text": "Alongside new music kits, we've continued updating Cache and made other miscellaneous fixes.",
  "heading_path": [
    "Today we are releasing six new music kits with NIGHTMODE Records. NIGHTMODE II Music Kits are now available in the STORE tab, featuring",
    "Pirapus, EVERYNITE"
  ],
  "entity": "Pirapus, EVERYNITE",
  "aspect": "audio",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 414,
  "source_span_end": 506,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Train` — `rv2_change_51880237861e35173663a973`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed some holes in the world
```

Extracted fields:

```json
{
  "change_text": "Fixed some holes in the world",
  "heading_path": [
    "Train"
  ],
  "entity": "Train",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1024,
  "source_span_end": 1053,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Train` — `rv2_change_98462f2c649b0febff5bab51`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed weekly care package preview of weapon cases not having a close button
```

Extracted fields:

```json
{
  "change_text": "Fixed weekly care package preview of weapon cases not having a close button",
  "heading_path": [
    "Train"
  ],
  "entity": "Train",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 712,
  "source_span_end": 787,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Various adjustments to sub-tick shooting` — `rv2_change_a8cc14dddc5cf05fec230b7a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed an issue where collisions between players were jittery
```

Extracted fields:

```json
{
  "change_text": "Fixed an issue where collisions between players were jittery",
  "heading_path": [
    "Various adjustments to sub-tick shooting"
  ],
  "entity": "Various adjustments to sub-tick shooting",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "collisions between players were jittery",
  "source_span_start": 1698,
  "source_span_end": 1758,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Various adjustments to sub-tick shooting` — `rv2_change_90d4d29dd85ff26adaa9b365`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added the option to change your microphone threshold (the minimum loudness before we start transmitting audio) from the audio options menu, as well as metering for your current mic loudness
```

Extracted fields:

```json
{
  "change_text": "Added the option to change your microphone threshold (the minimum loudness before we start transmitting audio) from the audio options menu, as well as metering for your current mic loudness",
  "heading_path": [
    "Various adjustments to sub-tick shooting"
  ],
  "entity": "Various adjustments to sub-tick shooting",
  "aspect": "audio",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2033,
  "source_span_end": 2222,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Various animation system optimizations` — `rv2_change_9eaf78a66ba563d2932b4412`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a bug where starting pistols weren't showing in the Pistols tab of the Equipment view
```

Extracted fields:

```json
{
  "change_text": "Fixed a bug where starting pistols weren't showing in the Pistols tab of the Equipment view",
  "heading_path": [
    "Various animation system optimizations"
  ],
  "entity": "Various animation system optimizations",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "starting pistols weren't showing in the Pistols tab of the Equipment view",
  "source_span_start": 343,
  "source_span_end": 434,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Various animation system optimizations` — `rv2_change_09c45ca5ced6f3130fafca73`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed an issue where silencers would not be shown on weapons when held by characters in the UI
```

Extracted fields:

```json
{
  "change_text": "Fixed an issue where silencers would not be shown on weapons when held by characters in the UI",
  "heading_path": [
    "Various animation system optimizations"
  ],
  "entity": "Various animation system optimizations",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "when held by characters in the UI",
  "bug_symptom": "silencers would not be shown on weapons",
  "source_span_start": 438,
  "source_span_end": 532,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=Vertigo` — `rv2_change_3aea554d20dd932382718558`

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
  "aspect": null,
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
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Vertigo` — `rv2_change_44f40426ba25026c5bbe0ff9`

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
  "entity": "Vertigo",
  "aspect": null,
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
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Warden` — `rv2_change_1d62144d0ee6fd7d1574d44b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3256988376"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Warden"
  ],
  "entity": "Warden",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 814,
  "source_span_end": 971,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=Warden` — `rv2_change_977b0f04e2a957d21d494fe7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated to the latest version from the Community Workshop ([url="https://steamcommunity.com/sharedfiles/filedetails/changelog/3256988376"]Update Notes[/url])
```

Extracted fields:

```json
{
  "change_text": "Updated to the latest version from the Community Workshop (Update Notes)",
  "heading_path": [
    "Warden"
  ],
  "entity": "Warden",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 760,
  "source_span_end": 917,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=\` — `rv2_change_ae33eaf503ad41e9899ad25c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added Entity.GetAbsAngularVelocity()
```

Extracted fields:

```json
{
  "change_text": "Added Entity.GetAbsAngularVelocity()",
  "heading_path": [
    "\\"
  ],
  "entity": "\\",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1286,
  "source_span_end": 1322,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=730;section=\` — `rv2_change_1b3399b72edbd18f76c39d27`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed bug where CSDamageTypes was exported under the name CSDamageType
```

Extracted fields:

```json
{
  "change_text": "Fixed bug where CSDamageTypes was exported under the name CSDamageType",
  "heading_path": [
    "\\"
  ],
  "entity": "\\",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "under the name CSDamageType",
  "bug_symptom": "CSDamageTypes was exported",
  "source_span_start": 928,
  "source_span_end": 998,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=730;section=unsectioned` — `rv2_change_80e42969891e9a42529026da`

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
  "quality_flags": []
}
```

### patch_change — `game=730;section=unsectioned` — `rv2_change_48ba191ed3cfbdd8295578b5`

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

### patch_change — `game=275850;section=Development Update` — `rv2_change_a0bd19ed4f56781d3a4742ed`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
If you'd like to stay updated with news about Light No Fire, you can wishlist it on Steam[url="https://store.steampowered.com/app/2719590/Light_No_Fire/"] [u]here
```

Extracted fields:

```json
{
  "change_text": "If you'd like to stay updated with news about Light No Fire, you can wishlist it on Steam here.",
  "heading_path": [
    "Development Update"
  ],
  "entity": "Development Update",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6015,
  "source_span_end": 6177,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=275850;section=No Man's Sky` — `rv2_change_28cf9a3a2b91ad580f0b4666`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
No Man's Sky adds a game changing quality-of-life feature, eight years later
```

Extracted fields:

```json
{
  "change_text": "No Man's Sky adds a game changing quality-of-life feature, eight years later",
  "heading_path": [
    "No Man's Sky",
    "RELATED LINKS"
  ],
  "entity": "RELATED LINKS",
  "aspect": "content_or_feature",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1042,
  "source_span_end": 1118,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=275850;section=Quality of Life` — `rv2_change_5d7a2f94dd480ee0345d66b3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Notably, [b]snapping is greatly improved[/b], [b]collision is more robust[/b], and the Corvette Workshop now offers the option to [b]apply a colour palette to an entire corvette
```

Extracted fields:

```json
{
  "change_text": "Notably, snapping is greatly improved, collision is more robust, and the Corvette Workshop now offers the option to apply a colour palette to an entire corvette.",
  "heading_path": [
    "Quality of Life"
  ],
  "entity": "Quality of Life",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3879,
  "source_span_end": 4056,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=275850;section=Quality of Life` — `rv2_change_a8525ee0920967e51186be6e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
In addition to the bundle of fixes, improvements, and new features in today’s update, the No Man’s Sky team have been hard at work on improving Voyagers since its launch in August.
```

Extracted fields:

```json
{
  "change_text": "In addition to the bundle of fixes, improvements, and new features in today’s update, the No Man’s Sky team have been hard at work on improving Voyagers since its launch in August.",
  "heading_path": [
    "Quality of Life"
  ],
  "entity": "Quality of Life",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3698,
  "source_span_end": 3878,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=275850;section=RELATED LINKS` — `rv2_change_f3d145f50a65e3fe0f0f7463`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
No Man's Sky just added trillions of new planets to the game out of nowhere
```

Extracted fields:

```json
{
  "change_text": "No Man's Sky just added trillions of new planets to the game out of nowhere",
  "heading_path": [
    "RELATED LINKS"
  ],
  "entity": "RELATED LINKS",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1025,
  "source_span_end": 1100,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=275850;section=RELATED LINKS` — `rv2_change_c75eb9360f3933bbb9504490`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
No Man's Sky just added trillions of new planets to the game out of nowhere
```

Extracted fields:

```json
{
  "change_text": "No Man's Sky just added trillions of new planets to the game out of nowhere",
  "heading_path": [
    "RELATED LINKS"
  ],
  "entity": "RELATED LINKS",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 880,
  "source_span_end": 955,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=275850;section=Reach Stars` — `rv2_change_cf14b51c8c46d53f462f891d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We’ve a lot of exciting things still to come, so we’ve added a form on the store where you can sign up if you’d like to be sent updates as we add to our collection.
```

Extracted fields:

```json
{
  "change_text": "We’ve a lot of exciting things still to come, so we’ve added a form on the store where you can sign up if you’d like to be sent updates as we add to our collection.",
  "heading_path": [
    "Reach Stars"
  ],
  "entity": "Reach Stars",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4967,
  "source_span_end": 5131,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=275850;section=Reach Stars` — `rv2_change_bb3fc397f0be3208a6bdcd66`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
It is like a museum of each update, unlocking the features of each update as we added them, along with a spacelog of interesting facts and developers commentary for each update.
```

Extracted fields:

```json
{
  "change_text": "It is like a museum of each update, unlocking the features of each update as we added them, along with a spacelog of interesting facts and developers commentary for each update.",
  "heading_path": [
    "Reach Stars"
  ],
  "entity": "Reach Stars",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4225,
  "source_span_end": 4402,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=275850;section=unsectioned` — `rv2_change_6e83bd6edf3f4deecd8ccc82`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Following on from last month’s massive [url=https://www.nomanssky.com/worlds-part-ii-update]Worlds Part II[/url] update, today we are launching our seventeenth expedition: TITAN, and inviting the entire community to explore some of the new planets introduced in [url=https://www.nomanssky.com/worlds-part-ii-update]Worlds Part II[/url].
```

Extracted fields:

```json
{
  "change_text": "Following on from last month’s massive Worlds Part II update, today we are launching our seventeenth expedition: TITAN, and inviting the entire community to explore some of the new planets introduced in Worlds Part II.",
  "heading_path": [],
  "entity": null,
  "aspect": "content_or_feature",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 17,
  "source_span_end": 353,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved"
  ]
}
```

### patch_change — `game=275850;section=unsectioned` — `rv2_change_74bc837880f6733d024bcb24`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We haven’t introduced ship customisation previously, because so many players love exploring to find the perfect ship already out there to purchase.
```

Extracted fields:

```json
{
  "change_text": "We haven’t introduced ship customisation previously, because so many players love exploring to find the perfect ship already out there to purchase.",
  "heading_path": [],
  "entity": null,
  "aspect": "purchase_price_or_cost",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1739,
  "source_span_end": 1886,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved"
  ]
}
```

### patch_change — `game=553850;section=10x Sniper Scope` — `rv2_change_1752b48f0aa3add552ac0e30`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased ergonomic modifier from (-9) to (-4)
```

Extracted fields:

```json
{
  "change_text": "Decreased ergonomic modifier from (-9) to (-4)",
  "heading_path": [
    "10x Sniper Scope"
  ],
  "entity": "10x Sniper Scope",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "-9",
  "new_value": "-4",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1761,
  "source_span_end": 1807,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=10x Sniper Scope` — `rv2_change_e7f04433d41c971ea47aeb22`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
is also effected by this change so it will get an increased ergonomics from 26 to 31
```

Extracted fields:

```json
{
  "change_text": "is also effected by this change so it will get an increased ergonomics from 26 to 31",
  "heading_path": [
    "10x Sniper Scope",
    "APW-1 Anti-Materiel Rifle"
  ],
  "entity": "APW-1 Anti-Materiel Rifle",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "26",
  "new_value": "31",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1854,
  "source_span_end": 1938,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=2x Tube Red Dot` — `rv2_change_68777ac4804fa45320bb53f4`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased ergonomic modifier from (-3) to (-1)
```

Extracted fields:

```json
{
  "change_text": "Decreased ergonomic modifier from (-3) to (-1)",
  "heading_path": [
    "2x Tube Red Dot"
  ],
  "entity": "2x Tube Red Dot",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "-3",
  "new_value": "-1",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1551,
  "source_span_end": 1597,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=4x Combat Scope` — `rv2_change_34c6b75d9144c5d5463509bf`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased ergonomic modifier from (-6) to (-2)
```

Extracted fields:

```json
{
  "change_text": "Decreased ergonomic modifier from (-6) to (-2)",
  "heading_path": [
    "4x Combat Scope"
  ],
  "entity": "4x Combat Scope",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "-6",
  "new_value": "-2",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1655,
  "source_span_end": 1701,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=63CS Diligence Counter Sniper` — `rv2_change_121c726d714fe84e4b6e765a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Ergonomics improved
```

Extracted fields:

```json
{
  "change_text": "Ergonomics improved",
  "heading_path": [
    "63CS Diligence Counter Sniper"
  ],
  "entity": "63CS Diligence Counter Sniper",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2490,
  "source_span_end": 2509,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=63CS Diligence Counter Sniper` — `rv2_change_da4a9a433118cc71c0b3c787`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 128 to 140
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 128 to 140",
  "heading_path": [
    "63CS Diligence Counter Sniper"
  ],
  "entity": "63CS Diligence Counter Sniper",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "128",
  "new_value": "140",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2453,
  "source_span_end": 2485,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=A/ARC-3 Tesla Tower` — `rv2_change_ae0ea499f291297f1e0ec846`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased health by 33%
```

Extracted fields:

```json
{
  "change_text": "Increased health by 33%",
  "heading_path": [
    "A/ARC-3 Tesla Tower"
  ],
  "entity": "A/ARC-3 Tesla Tower",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": 33.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3645,
  "source_span_end": 3668,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=A/FLAM-40 Flame sentry` — `rv2_change_f7bb4a09dc279e5de6dc7fb5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fire damage resistance increased from 0 to 95%
```

Extracted fields:

```json
{
  "change_text": "Fire damage resistance increased from 0 to 95%",
  "heading_path": [
    "A/FLAM-40 Flame sentry"
  ],
  "entity": "A/FLAM-40 Flame sentry",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "0",
  "new_value": "95%",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2529,
  "source_span_end": 2575,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=A/FLAM-40 Flame sentry` — `rv2_change_24980b02c95ef7af2af092e7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Cooldown reduced from 150 to 100 sec
```

Extracted fields:

```json
{
  "change_text": "Cooldown reduced from 150 to 100 sec",
  "heading_path": [
    "A/FLAM-40 Flame sentry"
  ],
  "entity": "A/FLAM-40 Flame sentry",
  "aspect": "cooldown_or_timing",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "150",
  "new_value": "100 sec",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2602,
  "source_span_end": 2638,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=A/MG-43 Machine gun Sentry, A/G-16 Gatling Sentry, A/MLS-4X Rocket Sentry, A/AC-8 Autocannon Sentry, A/M-12 Mortar Sentry, A/M-23 EMS Mortar Sentry` — `rv2_change_cb187a7625bf8f964dc597fe`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durability* from 0% to 80%
```

Extracted fields:

```json
{
  "change_text": "Increased durability* from 0% to 80%",
  "heading_path": [
    "A/MG-43 Machine gun Sentry, A/G-16 Gatling Sentry, A/MLS-4X Rocket Sentry, A/AC-8 Autocannon Sentry, A/M-12 Mortar Sentry, A/M-23 EMS Mortar Sentry"
  ],
  "entity": "A/MG-43 Machine gun Sentry, A/G-16 Gatling Sentry, A/MLS-4X Rocket Sentry, A/AC-8 Autocannon Sentry, A/M-12 Mortar Sentry, A/M-23 EMS Mortar Sentry",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": "0%",
  "new_value": "80%",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1985,
  "source_span_end": 2021,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=A/MG-43 Machine gun Sentry, A/G-16 Gatling Sentry, A/MLS-4X Rocket Sentry, A/AC-8 Autocannon Sentry, A/M-12 Mortar Sentry, A/M-23 EMS Mortar Sentry` — `rv2_change_8fb2bb71e628b215b7c560de`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We have increased the durability* factor of the turrets to make them more resistant to small arms fire.
```

Extracted fields:

```json
{
  "change_text": "We have increased the durability* factor of the turrets to make them more resistant to small arms fire.",
  "heading_path": [
    "A/MG-43 Machine gun Sentry, A/G-16 Gatling Sentry, A/MLS-4X Rocket Sentry, A/AC-8 Autocannon Sentry, A/M-12 Mortar Sentry, A/M-23 EMS Mortar Sentry"
  ],
  "entity": "A/MG-43 Machine gun Sentry, A/G-16 Gatling Sentry, A/MLS-4X Rocket Sentry, A/AC-8 Autocannon Sentry, A/M-12 Mortar Sentry, A/M-23 EMS Mortar Sentry",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1927,
  "source_span_end": 2030,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=A/MG-43 Machine gun sentry` — `rv2_change_3315f5196462fc944bd11620`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced cooldown from 180 sec to 120 sec.
```

Extracted fields:

```json
{
  "change_text": "Reduced cooldown from 180 sec to 120 sec.",
  "heading_path": [
    "A/MG-43 Machine gun sentry"
  ],
  "entity": "A/MG-43 Machine gun sentry",
  "aspect": "cooldown_or_timing",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "180 sec",
  "new_value": "120 sec",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1769,
  "source_span_end": 1810,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=A/MG-43 Machine gun sentry` — `rv2_change_89543d8ef891384e750f83f1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We lowered the cooldown to make it more available and more useful when changing position often.
```

Extracted fields:

```json
{
  "change_text": "We lowered the cooldown to make it more available and more useful when changing position often.",
  "heading_path": [
    "A/MG-43 Machine gun sentry"
  ],
  "entity": "A/MG-43 Machine gun sentry",
  "aspect": "cooldown_or_timing",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1480,
  "source_span_end": 1575,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=A/MG-43 Machinegun Sentry` — `rv2_change_4d0c1d3bf147bd08dbc7abac`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased health to match other Sentries
```

Extracted fields:

```json
{
  "change_text": "Increased health to match other Sentries",
  "heading_path": [
    "A/MG-43 Machinegun Sentry"
  ],
  "entity": "A/MG-43 Machinegun Sentry",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3558,
  "source_span_end": 3598,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=A/MLS-4X Rocket Sentry` — `rv2_change_fc8ccadd9105042b2f8ae41e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased projectile damage from 200 to 300
```

Extracted fields:

```json
{
  "change_text": "Increased projectile damage from 200 to 300",
  "heading_path": [
    "A/MLS-4X Rocket Sentry",
    "Prioritize larger targets"
  ],
  "entity": "Prioritize larger targets",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "200",
  "new_value": "300",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1672,
  "source_span_end": 1715,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=A/MLS-4X Rocket Sentry` — `rv2_change_7e3da2bc592fbcb859d3117f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased Rockets per salvo 2 to 1 (to get a better ammo economy)
```

Extracted fields:

```json
{
  "change_text": "Decreased Rockets per salvo 2 to 1 (to get a better ammo economy)",
  "heading_path": [
    "A/MLS-4X Rocket Sentry",
    "Prioritize larger targets"
  ],
  "entity": "Prioritize larger targets",
  "aspect": "purchase_price_or_cost",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1389,
  "source_span_end": 1454,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=AC- 8 Autocannon` — `rv2_change_24f25852409cb08a157ac639`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 260 to 325
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 260 to 325",
  "heading_path": [
    "AC- 8 Autocannon"
  ],
  "entity": "AC- 8 Autocannon",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "260",
  "new_value": "325",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8622,
  "source_span_end": 8654,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=APW-1 Anti-Materiel Rifle` — `rv2_change_6ad9c3ff1b1422645cf7f07d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Starting magazines increased from 4 to 5
```

Extracted fields:

```json
{
  "change_text": "Starting magazines increased from 4 to 5",
  "heading_path": [
    "APW-1 Anti-Materiel Rifle"
  ],
  "entity": "APW-1 Anti-Materiel Rifle",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "4",
  "new_value": "5",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8470,
  "source_span_end": 8510,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=APW-1 Anti-Materiel Rifle` — `rv2_change_de4dd296135c9a5aed50870f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Max spare magazines increased from 6 to 8
```

Extracted fields:

```json
{
  "change_text": "Max spare magazines increased from 6 to 8",
  "heading_path": [
    "APW-1 Anti-Materiel Rifle"
  ],
  "entity": "APW-1 Anti-Materiel Rifle",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "6",
  "new_value": "8",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8524,
  "source_span_end": 8565,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=AR-19 Liberator` — `rv2_change_23dbccb453cb3155aac787c6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 55 to 60
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 55 to 60",
  "heading_path": [
    "AR-19 Liberator"
  ],
  "entity": "AR-19 Liberator",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "55",
  "new_value": "60",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3005,
  "source_span_end": 3035,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=AR-23 Liberator` — `rv2_change_8440aaa9fb7647b1023690fc`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Durable damage increased from 15 to 22
```

Extracted fields:

```json
{
  "change_text": "Durable damage increased from 15 to 22",
  "heading_path": [
    "AR-23 Liberator"
  ],
  "entity": "AR-23 Liberator",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "15",
  "new_value": "22",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2535,
  "source_span_end": 2573,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=AR-23 Liberator` — `rv2_change_65f8cd246be019a0e77dc44c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 80 to 90
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 80 to 90",
  "heading_path": [
    "AR-23 Liberator"
  ],
  "entity": "AR-23 Liberator",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "80",
  "new_value": "90",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2491,
  "source_span_end": 2521,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=AR-23 Liberator, M-105 Stalwart and AX/AR-23 “Guard dog”` — `rv2_change_0016d6c50bfc276ca67a3e4e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased projectile damage against durable* body parts from 10% to 23%
```

Extracted fields:

```json
{
  "change_text": "Increased projectile damage against durable* body parts from 10% to 23%",
  "heading_path": [
    "AR-23 Liberator, M-105 Stalwart and AX/AR-23 “Guard dog”"
  ],
  "entity": "AR-23 Liberator, M-105 Stalwart and AX/AR-23 “Guard dog”",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "10%",
  "new_value": "23%",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4322,
  "source_span_end": 4393,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=AR-23A Liberator Carbine` — `rv2_change_23b363c38c708ed9ad1712ca`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 80 to 90
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 80 to 90",
  "heading_path": [
    "AR-23A Liberator Carbine"
  ],
  "entity": "AR-23A Liberator Carbine",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "80",
  "new_value": "90",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2638,
  "source_span_end": 2668,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=AR-23A Liberator Carbine` — `rv2_change_741da5c5663773950ef5eaef`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Durable damage increased from 15 to 22
```

Extracted fields:

```json
{
  "change_text": "Durable damage increased from 15 to 22",
  "heading_path": [
    "AR-23A Liberator Carbine"
  ],
  "entity": "AR-23A Liberator Carbine",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "15",
  "new_value": "22",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2682,
  "source_span_end": 2720,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=AR-23C Liberator Concussive` — `rv2_change_d314b3b2ce82ac95ff716902`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Ergonomic effect increased from 0 to -10
```

Extracted fields:

```json
{
  "change_text": "Ergonomic effect increased from 0 to -10",
  "heading_path": [
    "AR-23C Liberator Concussive"
  ],
  "entity": "AR-23C Liberator Concussive",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "0",
  "new_value": "-10",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1783,
  "source_span_end": 1823,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=AR-23C Liberator Concussive` — `rv2_change_63fa04ca6aba6e753f33e434`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 65 to 75
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 65 to 75",
  "heading_path": [
    "AR-23C Liberator Concussive"
  ],
  "entity": "AR-23C Liberator Concussive",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "65",
  "new_value": "75",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2886,
  "source_span_end": 2916,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=AR-23P Liberator Penetrator` — `rv2_change_a061e0e636a6181e0099db4b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 60 to 65
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 60 to 65",
  "heading_path": [
    "AR-23P Liberator Penetrator"
  ],
  "entity": "AR-23P Liberator Penetrator",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "60",
  "new_value": "65",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2788,
  "source_span_end": 2818,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=AR-32 Pacifier` — `rv2_change_e72f7ced104ff76cf0081369`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Starting magazines increased from 5 to 6
```

Extracted fields:

```json
{
  "change_text": "Starting magazines increased from 5 to 6",
  "heading_path": [
    "AR-32 Pacifier"
  ],
  "entity": "AR-32 Pacifier",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "5",
  "new_value": "6",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1134,
  "source_span_end": 1174,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=AR-32 Pacifier` — `rv2_change_84d8190ffdabf598d188ca5c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Max amount of magazines increased from 7 to 8
```

Extracted fields:

```json
{
  "change_text": "Max amount of magazines increased from 7 to 8",
  "heading_path": [
    "AR-32 Pacifier"
  ],
  "entity": "AR-32 Pacifier",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "7",
  "new_value": "8",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1201,
  "source_span_end": 1246,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=AR-59 Suppressor` — `rv2_change_f8b0641c56879d6612c27db5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased spare magazines 12 to 16
```

Extracted fields:

```json
{
  "change_text": "Increased spare magazines 12 to 16",
  "heading_path": [
    "AR-59 Suppressor"
  ],
  "entity": "AR-59 Suppressor",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8403,
  "source_span_end": 8437,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=AR-59 Suppressor` — `rv2_change_d00edd133588e3e121fdc6cd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased starting magazines 7 to 9
```

Extracted fields:

```json
{
  "change_text": "Increased starting magazines 7 to 9",
  "heading_path": [
    "AR-59 Suppressor"
  ],
  "entity": "AR-59 Suppressor",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8444,
  "source_span_end": 8479,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=AR-61 Tenderizer` — `rv2_change_faf90296eca98c213549915c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased stagger strength
```

Extracted fields:

```json
{
  "change_text": "Increased stagger strength",
  "heading_path": [
    "AR-61 Tenderizer"
  ],
  "entity": "AR-61 Tenderizer",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4933,
  "source_span_end": 4959,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=AR-61 Tenderizer` — `rv2_change_7d7279667756d7a48bfcaf11`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased ammo capacity from 35 to 30
```

Extracted fields:

```json
{
  "change_text": "Decreased ammo capacity from 35 to 30",
  "heading_path": [
    "AR-61 Tenderizer"
  ],
  "entity": "AR-61 Tenderizer",
  "aspect": "capacity_or_ammunition",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "35",
  "new_value": "30",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4844,
  "source_span_end": 4881,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=ARC-12 Blitzer` — `rv2_change_ecb20daa40aee8df343b3349`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased shots per minute from 30 to 45
```

Extracted fields:

```json
{
  "change_text": "Increased shots per minute from 30 to 45",
  "heading_path": [
    "ARC-12 Blitzer"
  ],
  "entity": "ARC-12 Blitzer",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "30",
  "new_value": "45",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1748,
  "source_span_end": 1788,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=AX/AR-23 Guard Dog` — `rv2_change_32577ccd89158830e883e8e7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased number of magazines from 6 to 8
```

Extracted fields:

```json
{
  "change_text": "Increased number of magazines from 6 to 8",
  "heading_path": [
    "AX/AR-23 Guard Dog"
  ],
  "entity": "AX/AR-23 Guard Dog",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "6",
  "new_value": "8",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3100,
  "source_span_end": 3141,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=AX/AR-23 Guard Dog` — `rv2_change_dc7db6cf5bafc2ea8cc7885a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We believe that increased ammo capacity along with the fix to the ammo crates will improve its viability as a support companion
```

Extracted fields:

```json
{
  "change_text": "We believe that increased ammo capacity along with the fix to the ammo crates will improve its viability as a support companion.",
  "heading_path": [
    "AX/AR-23 Guard Dog"
  ],
  "entity": "AX/AR-23 Guard Dog",
  "aspect": "capacity_or_ammunition",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3246,
  "source_span_end": 3373,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=Added support for upscalers` — `rv2_change_ec0cf6dd605f7aa8e0549e22`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added support for DRS on PC
```

Extracted fields:

```json
{
  "change_text": "Added support for DRS on PC",
  "heading_path": [
    "Added support for upscalers",
    "FSR 3.1.5"
  ],
  "entity": "FSR 3.1.5",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1166,
  "source_span_end": 1193,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Added support for upscalers` — `rv2_change_177d52640bd6bd982f794902`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added NVIDIA's Reflex for NVIDIA GPUs
```

Extracted fields:

```json
{
  "change_text": "Added NVIDIA's Reflex for NVIDIA GPUs",
  "heading_path": [
    "Added support for upscalers",
    "FSR 3.1.5"
  ],
  "entity": "FSR 3.1.5",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1207,
  "source_span_end": 1244,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Advanced Visual Optimizations` — `rv2_change_b7cca1fefbc9a42c54601185`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased resolution to 1440p in the “Performance” preset on PS5 and Xbox Series X, as well as the “Quality” preset on PS5 Power Saving Mode.
```

Extracted fields:

```json
{
  "change_text": "Increased resolution to 1440p in the “Performance” preset on PS5 and Xbox Series X, as well as the “Quality” preset on PS5 Power Saving Mode.",
  "heading_path": [
    "Advanced Visual Optimizations",
    "Beyond resolution, we are introducing several features to smooth out your gameplay experience and optimize GPU workload.",
    "Dynamic Resolution Scaling (DRS)",
    "Integrated for both PS5, Xbox Series X and PC to maintain stable frame rates during more graphically demanding scenarios."
  ],
  "entity": "Integrated for both PS5, Xbox Series X and PC to maintain stable frame rates during more graphically demanding scenarios.",
  "aspect": "performance_or_network",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2023,
  "source_span_end": 2164,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=All Exosuits` — `rv2_change_bc0846cc7117c2a316e7bae5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased health from 1600 to 1800
```

Extracted fields:

```json
{
  "change_text": "Increased health from 1600 to 1800",
  "heading_path": [
    "All Exosuits"
  ],
  "entity": "All Exosuits",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": "1600",
  "new_value": "1800",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 11599,
  "source_span_end": 11633,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=All Exosuits` — `rv2_change_979e7ac1cdecba16e3778404`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Cooldown reduced from 10 minutes down to 8 minutes
```

Extracted fields:

```json
{
  "change_text": "Cooldown reduced from 10 minutes down to 8 minutes",
  "heading_path": [
    "All Exosuits"
  ],
  "entity": "All Exosuits",
  "aspect": "cooldown_or_timing",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "10",
  "new_value": "8",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 11755,
  "source_span_end": 11805,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=All Tanks main body (bottom part)` — `rv2_change_02321c36332348ad970a2416`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased armor on back vents from Medium to Heavy (3 to 4)
```

Extracted fields:

```json
{
  "change_text": "Increased armor on back vents from Medium to Heavy (3 to 4)",
  "heading_path": [
    "All Tanks main body (bottom part)"
  ],
  "entity": "All Tanks main body (bottom part)",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": "3",
  "new_value": "4",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9703,
  "source_span_end": 9762,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=All Tanks main body (bottom part)` — `rv2_change_ce5199cf011ebc73d890754a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased health on back vents from 750 to 1500
```

Extracted fields:

```json
{
  "change_text": "Increased health on back vents from 750 to 1500",
  "heading_path": [
    "All Tanks main body (bottom part)"
  ],
  "entity": "All Tanks main body (bottom part)",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": "750",
  "new_value": "1500",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9642,
  "source_span_end": 9689,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=All Warrior variants` — `rv2_change_8d71d79846360fcb17023e76`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage",
  "heading_path": [
    "All Warrior variants"
  ],
  "entity": "All Warrior variants",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8028,
  "source_span_end": 8052,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Alpha commander` — `rv2_change_3974fadabaa9af5e534b0f4b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Removed cowardly behavior, it will now be more aggressive.
```

Extracted fields:

```json
{
  "change_text": "Removed cowardly behavior, it will now be more aggressive.",
  "heading_path": [
    "Alpha commander"
  ],
  "entity": "Alpha commander",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 12521,
  "source_span_end": 12579,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=And coming a bit further down the line, we’re tackling` — `rv2_change_5313856ca1ac07b091e552a2`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We've assembled a task force to prototype fixes for this issue and we're hoping to have it solved by the end of the year
```

Extracted fields:

```json
{
  "change_text": "We've assembled a task force to prototype fixes for this issue and we're hoping to have it solved by the end of the year.",
  "heading_path": [
    "And coming a bit further down the line, we’re tackling"
  ],
  "entity": "And coming a bit further down the line, we’re tackling",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8773,
  "source_span_end": 8893,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=And coming a bit further down the line, we’re tackling` — `rv2_change_29ac442b631900681f9f71e3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixes to the Warbond and Superstore menus that make them easier to navigate.
```

Extracted fields:

```json
{
  "change_text": "Fixes to the Warbond and Superstore menus that make them easier to navigate.",
  "heading_path": [
    "And coming a bit further down the line, we’re tackling"
  ],
  "entity": "And coming a bit further down the line, we’re tackling",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9255,
  "source_span_end": 9331,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Answer` — `rv2_change_dea5383aaced191fc7c29a22`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
For the longest time our features would be considered ready and implemented in the release build at the very last minute.
```

Extracted fields:

```json
{
  "change_text": "For the longest time our features would be considered ready and implemented in the release build at the very last minute.",
  "heading_path": [
    "Answer"
  ],
  "entity": "Answer",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2411,
  "source_span_end": 2532,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Armor Passive Change` — `rv2_change_8d0e6753a414078648ec6135`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased Melee Damage by 50%
```

Extracted fields:

```json
{
  "change_text": "Increased Melee Damage by 50%",
  "heading_path": [
    "Armor Passive Change",
    "We have been monitoring your feedback in regards to armors and their passives. We have made some adjustments to the Masters of Ceremony armors, adding 2 extra perks"
  ],
  "entity": "We have been monitoring your feedback in regards to armors and their passives. We have made some adjustments to the Masters of Ceremony armors, adding 2 extra perks",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": 50.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 759,
  "source_span_end": 788,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Armor Passive Change` — `rv2_change_a173e15cb8ba67cc799434dc`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased Reload Speed of primary weapons by 30%
```

Extracted fields:

```json
{
  "change_text": "Increased Reload Speed of primary weapons by 30%",
  "heading_path": [
    "Armor Passive Change",
    "We have been monitoring your feedback in regards to armors and their passives. We have made some adjustments to the Masters of Ceremony armors, adding 2 extra perks"
  ],
  "entity": "We have been monitoring your feedback in regards to armors and their passives. We have made some adjustments to the Masters of Ceremony armors, adding 2 extra perks",
  "aspect": "speed_or_movement",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": 30.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 706,
  "source_span_end": 754,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Armor Passives` — `rv2_change_3ee62984c2fb6ea68643b2df`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased the melee damage bonus gained by the Peak Physique armor passive by 100%
```

Extracted fields:

```json
{
  "change_text": "Increased the melee damage bonus gained by the Peak Physique armor passive by 100%",
  "heading_path": [
    "Armor Passives",
    "Peak Physique"
  ],
  "entity": "Peak Physique",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": 100.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4103,
  "source_span_end": 4185,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Armor Passives` — `rv2_change_b8a4422e7ba9c828557356df`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Now also increases armor rating by 25
```

Extracted fields:

```json
{
  "change_text": "Now also increases armor rating by 25",
  "heading_path": [
    "Armor Passives",
    "Integrated Explosives"
  ],
  "entity": "Integrated Explosives",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": 25.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1446,
  "source_span_end": 1483,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Arrowhead Game Studios` — `rv2_change_781937505cea9385da012180`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
released a quick patch to help with <strong>Helldiver 2's</strong> matchmaking issues yesterday, and has now said it's working on a long-term fix.
```

Extracted fields:

```json
{
  "change_text": "released a quick patch to help with Helldiver 2's matchmaking issues yesterday, and has now said it's working on a long-term fix.",
  "heading_path": [
    "Arrowhead Game Studios"
  ],
  "entity": "Arrowhead Game Studios",
  "aspect": "matchmaking_or_ranked",
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 181,
  "source_span_end": 327,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Autocannon Flak` — `rv2_change_1b3210ea27a3906d00779367`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased Shrapnel spawned from 25 to 30
```

Extracted fields:

```json
{
  "change_text": "Increased Shrapnel spawned from 25 to 30",
  "heading_path": [
    "Autocannon Flak"
  ],
  "entity": "Autocannon Flak",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "25",
  "new_value": "30",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4569,
  "source_span_end": 4609,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Automatons` — `rv2_change_733663b0a519ae2683b7f236`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced the number of Reinforced Scout Striders spawning on higher difficulty levels
```

Extracted fields:

```json
{
  "change_text": "Reduced the number of Reinforced Scout Striders spawning on higher difficulty levels",
  "heading_path": [
    "Automatons",
    "Reinforced Scout Strider"
  ],
  "entity": "Reinforced Scout Strider",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5461,
  "source_span_end": 5545,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Automatons` — `rv2_change_963b7df0bcaa4e2fbc6513a0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Heavy projectiles damage reduced from 65 to 60, used by enemies like the Heavy Emplacements and Scout Striders
```

Extracted fields:

```json
{
  "change_text": "Heavy projectiles damage reduced from 65 to 60, used by enemies like the Heavy Emplacements and Scout Striders",
  "heading_path": [
    "Automatons",
    "Automaton projectiles"
  ],
  "entity": "Automaton projectiles",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "65",
  "new_value": "60,",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10764,
  "source_span_end": 10874,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=BALANCE & OTHER FIXES` — `rv2_change_d1d6eeb22f583b423838d6f3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated Mission End screen to display Experience and Requisition multiplier.
```

Extracted fields:

```json
{
  "change_text": "Updated Mission End screen to display Experience and Requisition multiplier.",
  "heading_path": [
    "BALANCE & OTHER FIXES"
  ],
  "entity": "BALANCE & OTHER FIXES",
  "aspect": "rewards_or_progression",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1404,
  "source_span_end": 1480,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=BALANCE & OTHER FIXES` — `rv2_change_553465f67360f2c24a639401`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Issue where multiple of the same stratagems could be brought to a mission has been resolved.
```

Extracted fields:

```json
{
  "change_text": "Issue where multiple of the same stratagems could be brought to a mission has been resolved.",
  "heading_path": [
    "BALANCE & OTHER FIXES"
  ],
  "entity": "BALANCE & OTHER FIXES",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1485,
  "source_span_end": 1577,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=BR-14 Adjudicator` — `rv2_change_341baa232ba133f57e1284eb`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The increased magazine capacity should make the weapon more forgiving of mistakes and encourage a more aggressive playstyle.
```

Extracted fields:

```json
{
  "change_text": "The increased magazine capacity should make the weapon more forgiving of mistakes and encourage a more aggressive playstyle.",
  "heading_path": [
    "BR-14 Adjudicator"
  ],
  "entity": "BR-14 Adjudicator",
  "aspect": "gameplay",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8492,
  "source_span_end": 8616,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=BR-14 Adjudicator` — `rv2_change_7c0718ef21bdf75bff68b7f3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased projectile damage against durable* body parts from 10% to 20%
```

Extracted fields:

```json
{
  "change_text": "Increased projectile damage against durable* body parts from 10% to 20%",
  "heading_path": [
    "BR-14 Adjudicator"
  ],
  "entity": "BR-14 Adjudicator",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "10%",
  "new_value": "20%",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4608,
  "source_span_end": 4679,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Backpacks` — `rv2_change_a38d9d1e0373bb3901c47e83`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Cooldown reduced from 20 to 15 sec
```

Extracted fields:

```json
{
  "change_text": "Cooldown reduced from 20 to 15 sec",
  "heading_path": [
    "Backpacks",
    "LIFT-850 Jump Pack"
  ],
  "entity": "LIFT-850 Jump Pack",
  "aspect": "cooldown_or_timing",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "20",
  "new_value": "15 sec",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6835,
  "source_span_end": 6869,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Backpacks` — `rv2_change_82527d4594a420437440ddfc`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The targeting range has been increased from 10 to 20m
```

Extracted fields:

```json
{
  "change_text": "The targeting range has been increased from 10 to 20m",
  "heading_path": [
    "Backpacks"
  ],
  "entity": "Backpacks",
  "aspect": "range_or_radius",
  "action": "increased",
  "direction": "increased",
  "previous_value": "10",
  "new_value": "20",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2503,
  "source_span_end": 2556,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Balance Changes` — `rv2_change_bb9983bbb254e854b7f1ae12`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Armor Penetration decreased on shrapnel projectiles from 3-3-3-0 to 3-3-2-0
```

Extracted fields:

```json
{
  "change_text": "Armor Penetration decreased on shrapnel projectiles from 3-3-3-0 to 3-3-2-0",
  "heading_path": [
    "Balance Changes"
  ],
  "entity": "Balance Changes",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "3",
  "new_value": "-3",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4186,
  "source_span_end": 4261,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Balance Changes` — `rv2_change_b964c5fd7aedeac499a10d66`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Each of these numbers represent an angle threshold, which means we’ve reduced the AP value of 3 to 2 in the last range where a shrapnel projectile would penetrate an enemy.
```

Extracted fields:

```json
{
  "change_text": "Each of these numbers represent an angle threshold, which means we’ve reduced the AP value of 3 to 2 in the last range where a shrapnel projectile would penetrate an enemy.",
  "heading_path": [
    "Balance Changes"
  ],
  "entity": "Balance Changes",
  "aspect": "range_or_radius",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4273,
  "source_span_end": 4445,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Balancing` — `rv2_change_4a8cb8d17f02ba4f06a55f2e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Balanced and adjusted spawn rates for the various planet hazards including tremors, meteor showers, volcanic activity, fire tornados, and ion storms. Hazards should now spawn less frequently during missions.
```

Extracted fields:

```json
{
  "change_text": "Balanced and adjusted spawn rates for the various planet hazards including tremors, meteor showers, volcanic activity, fire tornados, and ion storms. Hazards should now spawn less frequently during missions.",
  "heading_path": [
    "Balancing"
  ],
  "entity": null,
  "aspect": "map_or_level",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 328,
  "source_span_end": 535,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Balancing` — `rv2_change_a0aad8da553d9ac5a25d3e44`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced rock velocity slightly
```

Extracted fields:

```json
{
  "change_text": "Reduced rock velocity slightly",
  "heading_path": [
    "Balancing"
  ],
  "entity": null,
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 959,
  "source_span_end": 989,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Balancing changes - EVACUATE HIGH-VALUE ASSETS` — `rv2_change_d02a8e023324694e8bbc0fe4`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added 10 common samples to collect throughout the mission.
```

Extracted fields:

```json
{
  "change_text": "Added 10 common samples to collect throughout the mission.",
  "heading_path": [
    "Balancing changes - EVACUATE HIGH-VALUE ASSETS",
    "Level Design changes"
  ],
  "entity": "Level Design changes",
  "aspect": "content_or_feature",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4058,
  "source_span_end": 4116,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Balancing changes - EVACUATE HIGH-VALUE ASSETS` — `rv2_change_0b43c1490afd745cf5f0d663`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced the start time between waves from 60 seconds to 42 seconds (the time between waves at the start of the mission).
```

Extracted fields:

```json
{
  "change_text": "Reduced the start time between waves from 60 seconds to 42 seconds (the time between waves at the start of the mission).",
  "heading_path": [
    "Balancing changes - EVACUATE HIGH-VALUE ASSETS",
    "Changes"
  ],
  "entity": "Changes",
  "aspect": "content_or_feature",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "60 seconds",
  "new_value": "42 seconds",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3184,
  "source_span_end": 3304,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Ballistic Shield changes` — `rv2_change_065004e16ebf6e87109d7833`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Changed shield poses so that less of the helldiver is exposed
```

Extracted fields:

```json
{
  "change_text": "Changed shield poses so that less of the helldiver is exposed",
  "heading_path": [
    "Ballistic Shield changes"
  ],
  "entity": "Ballistic Shield changes",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4890,
  "source_span_end": 4951,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Ballistic Shield changes` — `rv2_change_dcf44bf66e9ed0135bcc6b45`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Addressed bug where parts of the helldiver would become vulnerable while using the shield in first person
```

Extracted fields:

```json
{
  "change_text": "Addressed bug where parts of the helldiver would become vulnerable while using the shield in first person",
  "heading_path": [
    "Ballistic Shield changes"
  ],
  "entity": "Ballistic Shield changes",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4956,
  "source_span_end": 5061,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Bang bang less…` — `rv2_change_b5304a177e030ec495b360a4`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Helldivers are going deep behind enemy lines where their normal reliance on air superiority is no longer an option
```

Extracted fields:

```json
{
  "change_text": "Helldivers are going deep behind enemy lines where their normal reliance on air superiority is no longer an option.",
  "heading_path": [
    "Bang bang less…"
  ],
  "entity": "Bang bang less…",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 561,
  "source_span_end": 675,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=Bang bang less…` — `rv2_change_bed0411eb44cb1b4ae8b2564`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
This patch is deploying some important updates to suppressed weapons, allowing Helldivers to eliminate threats with reduced detection and tighter tactical control
```

Extracted fields:

```json
{
  "change_text": "This patch is deploying some important updates to suppressed weapons, allowing Helldivers to eliminate threats with reduced detection and tighter tactical control.",
  "heading_path": [
    "Bang bang less…"
  ],
  "entity": "Bang bang less…",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 75,
  "source_span_end": 237,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=Barrager tank turret` — `rv2_change_12a2d9480e04b3e8c8b7ddd5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased health on weak spot on front and back from 750 to 1500
```

Extracted fields:

```json
{
  "change_text": "Increased health on weak spot on front and back from 750 to 1500",
  "heading_path": [
    "Barrager tank turret"
  ],
  "entity": "Barrager tank turret",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": "750",
  "new_value": "1500",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10273,
  "source_span_end": 10337,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Berserkers` — `rv2_change_6bdda8fb6b44beec1c4d4434`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
increased durable damage
```

Extracted fields:

```json
{
  "change_text": "increased durable damage",
  "heading_path": [
    "Berserkers"
  ],
  "entity": "Berserkers",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8835,
  "source_span_end": 8859,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Bile Spewer` — `rv2_change_5669de784b647d9d04c16179`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased force impulse on artillery explosion from 60 to 40
```

Extracted fields:

```json
{
  "change_text": "Decreased force impulse on artillery explosion from 60 to 40",
  "heading_path": [
    "Bile Spewer"
  ],
  "entity": "Bile Spewer",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "60",
  "new_value": "40",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3384,
  "source_span_end": 3444,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Bile Spewer` — `rv2_change_b33489cde92c47e35c7c5988`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased force strength on artillery explosion from 50 to 30
```

Extracted fields:

```json
{
  "change_text": "Decreased force strength on artillery explosion from 50 to 30",
  "heading_path": [
    "Bile Spewer"
  ],
  "entity": "Bile Spewer",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "50",
  "new_value": "30",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3309,
  "source_span_end": 3370,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Bile Spewer Variations` — `rv2_change_4adc53994cdd2c902018e1bd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased size of its mouth weak spot
```

Extracted fields:

```json
{
  "change_text": "Increased size of its mouth weak spot",
  "heading_path": [
    "Bile Spewer Variations"
  ],
  "entity": "Bile Spewer Variations",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 11472,
  "source_span_end": 11509,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Bile Spewers` — `rv2_change_feecacf1162bf0b5a096c7ea`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage on melee attack
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage on melee attack",
  "heading_path": [
    "Bile Spewers"
  ],
  "entity": "Bile Spewers",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7596,
  "source_span_end": 7636,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Bile Titan` — `rv2_change_b7423bab8afbbd60f6c96b1b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased Explosion outer radius from 3.5 to 2.2
```

Extracted fields:

```json
{
  "change_text": "Decreased Explosion outer radius from 3.5 to 2.2",
  "heading_path": [
    "Bile Titan"
  ],
  "entity": "Bile Titan",
  "aspect": "range_or_radius",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "3.5",
  "new_value": "2.2",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7226,
  "source_span_end": 7274,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Bile Titan` — `rv2_change_b7b13d6c26528aa506870b6a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased Explosion inner radius from 2.25 to 1
```

Extracted fields:

```json
{
  "change_text": "Decreased Explosion inner radius from 2.25 to 1",
  "heading_path": [
    "Bile Titan"
  ],
  "entity": "Bile Titan",
  "aspect": "range_or_radius",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "2.25",
  "new_value": "1",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7165,
  "source_span_end": 7212,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Bonus note` — `rv2_change_5d4d11734f648ae8391ff6e1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We have now introduced validation checks on launch to help address potential issues caused by out of date drivers.
```

Extracted fields:

```json
{
  "change_text": "We have now introduced validation checks on launch to help address potential issues caused by out of date drivers.",
  "heading_path": [
    "Bonus note"
  ],
  "entity": "Bonus note",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 13964,
  "source_span_end": 14078,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Booster` — `rv2_change_fdf78a036c48b069627d736a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased stagger strength 10 -> 50
```

Extracted fields:

```json
{
  "change_text": "Increased stagger strength 10 -> 50",
  "heading_path": [
    "Booster",
    "Stun Hellpod"
  ],
  "entity": "Stun Hellpod",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4181,
  "source_span_end": 4216,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Booster` — `rv2_change_29a675b1293a8bde81678a4d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased stagger impulse 20 → 0
```

Extracted fields:

```json
{
  "change_text": "Decreased stagger impulse 20 → 0",
  "heading_path": [
    "Booster",
    "Stun Hellpod"
  ],
  "entity": "Stun Hellpod",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4230,
  "source_span_end": 4262,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Boosters` — `rv2_change_2890d8eeb3186a89cfcf46b7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased the bonus gained by the Expert Extraction Pilot Booster by 100%
```

Extracted fields:

```json
{
  "change_text": "Increased the bonus gained by the Expert Extraction Pilot Booster by 100%",
  "heading_path": [
    "Boosters",
    "Expert Extraction Pilot"
  ],
  "entity": "Expert Extraction Pilot",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": 100.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3760,
  "source_span_end": 3833,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Boosters` — `rv2_change_0b3856a3fae07147cee795e5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased the bonus gained by the Flexible Reinforcement Budget Booster by 150%
```

Extracted fields:

```json
{
  "change_text": "Increased the bonus gained by the Flexible Reinforcement Budget Booster by 150%",
  "heading_path": [
    "Boosters",
    "Flexible Reinforcement Budget"
  ],
  "entity": "Flexible Reinforcement Budget",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": 150.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3637,
  "source_span_end": 3716,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=CB-9 Exploding Crossbow` — `rv2_change_6388847dc0822e46455c65f1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Muzzle velocity increased
```

Extracted fields:

```json
{
  "change_text": "Muzzle velocity increased",
  "heading_path": [
    "CB-9 Exploding Crossbow",
    "Slight reduction in ergonomics"
  ],
  "entity": "Slight reduction in ergonomics",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 909,
  "source_span_end": 934,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=CB-9 Exploding Crossbow` — `rv2_change_8af71945bfd38c6aa78aed74`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased stagger
```

Extracted fields:

```json
{
  "change_text": "Increased stagger",
  "heading_path": [
    "CB-9 Exploding Crossbow",
    "Slightly smaller explosion"
  ],
  "entity": "Slightly smaller explosion",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 733,
  "source_span_end": 750,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=CB-9 Explosive Crossbow` — `rv2_change_05e0517b988e955f32b14843`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Similarly to the Purifier, the crossbow's bolt didn't always deal its full damage due to the explosion having lower armor penetration than the projectile.
```

Extracted fields:

```json
{
  "change_text": "Similarly to the Purifier, the crossbow's bolt didn't always deal its full damage due to the explosion having lower armor penetration than the projectile.",
  "heading_path": [
    "CB-9 Explosive Crossbow"
  ],
  "entity": "CB-9 Explosive Crossbow",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9556,
  "source_span_end": 9710,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CB-9 Explosive Crossbow` — `rv2_change_7b37f91dc108a71f906e8e41`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased explosion armor penetration to be the same as the projectile
```

Extracted fields:

```json
{
  "change_text": "Increased explosion armor penetration to be the same as the projectile",
  "heading_path": [
    "CB-9 Explosive Crossbow"
  ],
  "entity": "CB-9 Explosive Crossbow",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5164,
  "source_span_end": 5234,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-1 One True Flag` — `rv2_change_b03fccc31bc1ee968beed0fc`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage from 55 to 100
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage from 55 to 100",
  "heading_path": [
    "CQC-1 One True Flag"
  ],
  "entity": "CQC-1 One True Flag",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "55",
  "new_value": "100",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7507,
  "source_span_end": 7546,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-1 One True Flag` — `rv2_change_791cd5a908f194d3e572b2af`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased damage from 110 to 200
```

Extracted fields:

```json
{
  "change_text": "Increased damage from 110 to 200",
  "heading_path": [
    "CQC-1 One True Flag"
  ],
  "entity": "CQC-1 One True Flag",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "110",
  "new_value": "200",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7461,
  "source_span_end": 7493,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-19 Stun Lance` — `rv2_change_19c94091ccb61c5292b67d88`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage from 55 to 83
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage from 55 to 83",
  "heading_path": [
    "CQC-19 Stun Lance"
  ],
  "entity": "CQC-19 Stun Lance",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "55",
  "new_value": "83",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6171,
  "source_span_end": 6209,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-19 Stun Lance` — `rv2_change_13fa55fc0145d8e5649a3a71`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased damage from 110 to 165
```

Extracted fields:

```json
{
  "change_text": "Increased damage from 110 to 165",
  "heading_path": [
    "CQC-19 Stun Lance"
  ],
  "entity": "CQC-19 Stun Lance",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "110",
  "new_value": "165",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6125,
  "source_span_end": 6157,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-2 Saber` — `rv2_change_f35da6bb37214ccc9c3750eb`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Durable damage increased from 55 to 65
```

Extracted fields:

```json
{
  "change_text": "Durable damage increased from 55 to 65",
  "heading_path": [
    "CQC-2 Saber"
  ],
  "entity": "CQC-2 Saber",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "55",
  "new_value": "65",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4930,
  "source_span_end": 4968,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-2 Saber` — `rv2_change_c32df29673e8911332929b29`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased damage from 125 to 188
```

Extracted fields:

```json
{
  "change_text": "Increased damage from 125 to 188",
  "heading_path": [
    "CQC-2 Saber"
  ],
  "entity": "CQC-2 Saber",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "125",
  "new_value": "188",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6261,
  "source_span_end": 6293,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-30 Stun Baton` — `rv2_change_8cb103b8aadac12fe93d4ac5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage from 25 to 38
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage from 25 to 38",
  "heading_path": [
    "CQC-30 Stun Baton"
  ],
  "entity": "CQC-30 Stun Baton",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "25",
  "new_value": "38",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6029,
  "source_span_end": 6067,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-30 Stun Baton` — `rv2_change_53487f99a870fd1a7b8405cc`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased damage from 50 to 75
```

Extracted fields:

```json
{
  "change_text": "Increased damage from 50 to 75",
  "heading_path": [
    "CQC-30 Stun Baton"
  ],
  "entity": "CQC-30 Stun Baton",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "50",
  "new_value": "75",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5985,
  "source_span_end": 6015,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-42 Machete` — `rv2_change_3ceedcad376d33cfca3d8eb0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 170 to 200
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 170 to 200",
  "heading_path": [
    "CQC-42 Machete"
  ],
  "entity": "CQC-42 Machete",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "170",
  "new_value": "200",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5220,
  "source_span_end": 5252,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-42 Machete` — `rv2_change_43d98177b3ac1f0cf6e9afdb`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage from 100 to 150
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage from 100 to 150",
  "heading_path": [
    "CQC-42 Machete"
  ],
  "entity": "CQC-42 Machete",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "100",
  "new_value": "150",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6592,
  "source_span_end": 6632,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-5 Combat Hatches` — `rv2_change_7408d4b8e7ee5348f24a5fa1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage from 80 to 120
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage from 80 to 120",
  "heading_path": [
    "CQC-5 Combat Hatches"
  ],
  "entity": "CQC-5 Combat Hatches",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "80",
  "new_value": "120",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6452,
  "source_span_end": 6491,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-5 Combat Hatches` — `rv2_change_fc0dc5afe21f67e67dad51c0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased damage from 160 to 240
```

Extracted fields:

```json
{
  "change_text": "Increased damage from 160 to 240",
  "heading_path": [
    "CQC-5 Combat Hatches"
  ],
  "entity": "CQC-5 Combat Hatches",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "160",
  "new_value": "240",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6406,
  "source_span_end": 6438,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-5 Combat Hatchet` — `rv2_change_8436d0151453ebd343213796`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Durable damage increased from 55 to 80
```

Extracted fields:

```json
{
  "change_text": "Durable damage increased from 55 to 80",
  "heading_path": [
    "CQC-5 Combat Hatchet"
  ],
  "entity": "CQC-5 Combat Hatchet",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "55",
  "new_value": "80",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5075,
  "source_span_end": 5113,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-5 Combat Hatchet` — `rv2_change_e187f9bd693701c4bab83007`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Attack speed has been slightly reduced
```

Extracted fields:

```json
{
  "change_text": "Attack speed has been slightly reduced",
  "heading_path": [
    "CQC-5 Combat Hatchet"
  ],
  "entity": "CQC-5 Combat Hatchet",
  "aspect": "speed_or_movement",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5127,
  "source_span_end": 5165,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-9 Defoliation Tool` — `rv2_change_21611447a9cd0d8008e97af0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased damage from 300 to 450
```

Extracted fields:

```json
{
  "change_text": "Increased damage from 300 to 450",
  "heading_path": [
    "CQC-9 Defoliation Tool"
  ],
  "entity": "CQC-9 Defoliation Tool",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "300",
  "new_value": "450",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7315,
  "source_span_end": 7347,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=CQC-9 Defoliation Tool` — `rv2_change_8192ff9bbe0324f5aac4a203`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage from 150 to 225
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage from 150 to 225",
  "heading_path": [
    "CQC-9 Defoliation Tool"
  ],
  "entity": "CQC-9 Defoliation Tool",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "150",
  "new_value": "225",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7361,
  "source_span_end": 7401,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Charger` — `rv2_change_37e0be56e9b1aa75d57f538d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
To compensate for this, charge speed has been slightly increased (8->9m/s)
```

Extracted fields:

```json
{
  "change_text": "To compensate for this, charge speed has been slightly increased (8->9m/s)",
  "heading_path": [
    "Charger"
  ],
  "entity": "Charger",
  "aspect": "speed_or_movement",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 12383,
  "source_span_end": 12457,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Charger` — `rv2_change_6f37cacff7b708700d0b383a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Adjusted the chargers turning arc to make them easier to avoid
```

Extracted fields:

```json
{
  "change_text": "Adjusted the chargers turning arc to make them easier to avoid",
  "heading_path": [
    "Charger"
  ],
  "entity": "Charger",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 12120,
  "source_span_end": 12182,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Claws` — `rv2_change_1a841fc7c458dec287ef6b5d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Armor decreased from 3 → 1
```

Extracted fields:

```json
{
  "change_text": "Armor decreased from 3 → 1",
  "heading_path": [
    "Claws"
  ],
  "entity": "Claws",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 509,
  "source_span_end": 535,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Command Bunker Turret` — `rv2_change_c69f70e66465a92bd1d43a89`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Removed ragdolling from its projectiles explosion
```

Extracted fields:

```json
{
  "change_text": "Removed ragdolling from its projectiles explosion",
  "heading_path": [
    "Command Bunker Turret"
  ],
  "entity": "Command Bunker Turret",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 12868,
  "source_span_end": 12917,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Crash Fixes` — `rv2_change_f3038f4afc370c9965318885`

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
  "entity": "Crash Fixes",
  "aspect": "performance_or_network",
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

### patch_change — `game=553850;section=Crash Fixes` — `rv2_change_8f53997df9c09172f78c66fe`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a crash that occurred when switching between fullscreen and windowed modes
```

Extracted fields:

```json
{
  "change_text": "Fixed a crash that occurred when switching between fullscreen and windowed modes",
  "heading_path": [
    "Crash Fixes"
  ],
  "entity": "Crash Fixes",
  "aspect": "performance_or_network",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 598,
  "source_span_end": 678,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Crash Fixes & Softlocks` — `rv2_change_02c5a1b142e8de1554005fe7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a rare crash caused by multiple players having the MA5C AR equipped on the super destroyer
```

Extracted fields:

```json
{
  "change_text": "Fixed a rare crash caused by multiple players having the MA5C AR equipped on the super destroyer",
  "heading_path": [
    "Crash Fixes & Softlocks"
  ],
  "entity": "Crash Fixes & Softlocks",
  "aspect": "performance_or_network",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4364,
  "source_span_end": 4460,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Crash Fixes & Softlocks` — `rv2_change_d776c63092dce47c650a7d05`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a rare crash that would occur when combat music would start
```

Extracted fields:

```json
{
  "change_text": "Fixed a rare crash that would occur when combat music would start",
  "heading_path": [
    "Crash Fixes & Softlocks"
  ],
  "entity": "Crash Fixes & Softlocks",
  "aspect": "gameplay",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4799,
  "source_span_end": 4864,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Crash Fixes and Soft-locks` — `rv2_change_6b1020e0f736f2790b1eb684`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
General crash fixes
```

Extracted fields:

```json
{
  "change_text": "General crash fixes",
  "heading_path": [
    "Crash Fixes and Soft-locks"
  ],
  "entity": "Crash Fixes and Soft-locks",
  "aspect": "performance_or_network",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7996,
  "source_span_end": 8015,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Crash Fixes and Soft-locks` — `rv2_change_629f871ca38b08e0156e626c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed some potential crashes when the player quits the game
```

Extracted fields:

```json
{
  "change_text": "Fixed some potential crashes when the player quits the game",
  "heading_path": [
    "Crash Fixes and Soft-locks"
  ],
  "entity": "Crash Fixes and Soft-locks",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 249,
  "source_span_end": 308,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Crash Fixes, Hangs and Soft-locks` — `rv2_change_8669e74a4f78c677a3c7694d`

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
  "aspect": null,
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
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Crash Fixes, Hangs and Soft-locks` — `rv2_change_7d3340e40760e037e6a36ec7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a crash that occurred during extraction
```

Extracted fields:

```json
{
  "change_text": "Fixed a crash that occurred during extraction",
  "heading_path": [
    "Crash Fixes, Hangs and Soft-locks"
  ],
  "entity": "Crash Fixes, Hangs and Soft-locks",
  "aspect": "performance_or_network",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4941,
  "source_span_end": 4986,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Crash fixes & Soft Locks` — `rv2_change_3a672fa13f85e55a8fcb38d2`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixes a crash which could happen when the player or a hot-joiner first spawns into a mission
```

Extracted fields:

```json
{
  "change_text": "Fixes a crash which could happen when the player or a hot-joiner first spawns into a mission",
  "heading_path": [
    "Crash fixes & Soft Locks"
  ],
  "entity": "Crash fixes & Soft Locks",
  "aspect": "performance_or_network",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 209,
  "source_span_end": 301,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Crash fixes & Soft Locks` — `rv2_change_195c5d76e08917f864e5db6c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a rare crash that could occur with carriable items and looking at the minimap at the same time
```

Extracted fields:

```json
{
  "change_text": "Fixed a rare crash that could occur with carriable items and looking at the minimap at the same time",
  "heading_path": [
    "Crash fixes & Soft Locks"
  ],
  "entity": "Crash fixes & Soft Locks",
  "aspect": "performance_or_network",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 306,
  "source_span_end": 406,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Crashes` — `rv2_change_4b52bbee6983590fd14d8868`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed crash when opening social menu and having many blocked players and/or friend requests.
```

Extracted fields:

```json
{
  "change_text": "Fixed crash when opening social menu and having many blocked players and/or friend requests.",
  "heading_path": [
    "Crashes"
  ],
  "entity": "Crashes",
  "aspect": "performance_or_network",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 751,
  "source_span_end": 843,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Crashes` — `rv2_change_1598d5aa7dcbbfeee5641f52`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a crash when minimizing after changing fullscreen mode.
```

Extracted fields:

```json
{
  "change_text": "Fixed a crash when minimizing after changing fullscreen mode.",
  "heading_path": [
    "Crashes"
  ],
  "entity": "Crashes",
  "aspect": "performance_or_network",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 848,
  "source_span_end": 909,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Crescent Overseer` — `rv2_change_f9baf743331859d72114e332`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased the damage of its direct shot attack
```

Extracted fields:

```json
{
  "change_text": "Increased the damage of its direct shot attack",
  "heading_path": [
    "Crescent Overseer"
  ],
  "entity": "Crescent Overseer",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10452,
  "source_span_end": 10498,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Crescent Overseer` — `rv2_change_0227abd8049cb426337f726f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Crescent Overseer`s weapon now deals increased damage vs Durable targets
```

Extracted fields:

```json
{
  "change_text": "Crescent Overseer`s weapon now deals increased damage vs Durable targets",
  "heading_path": [
    "Crescent Overseer"
  ],
  "entity": "Crescent Overseer",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10512,
  "source_span_end": 10584,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Devastator` — `rv2_change_18d2621433c023b32b1a1ba9`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Removed durable on arms
```

Extracted fields:

```json
{
  "change_text": "Removed durable on arms",
  "heading_path": [
    "Devastator"
  ],
  "entity": "Devastator",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9738,
  "source_span_end": 9761,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Devastators` — `rv2_change_d338c3ef315dd88e1d3e1017`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
increased durable damage on melee attack
```

Extracted fields:

```json
{
  "change_text": "increased durable damage on melee attack",
  "heading_path": [
    "Devastators"
  ],
  "entity": "Devastators",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8919,
  "source_span_end": 8959,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Drag` — `rv2_change_47897cc3c62bde3e4b07f192`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We've increased drag for pistol-caliber ammunition (used in SMGs and some sidearms) to better represent its shorter, wider projectile compared to rifle rounds
```

Extracted fields:

```json
{
  "change_text": "We've increased drag for pistol-caliber ammunition (used in SMGs and some sidearms) to better represent its shorter, wider projectile compared to rifle rounds.",
  "heading_path": [
    "Drag"
  ],
  "entity": "Drag",
  "aspect": "capacity_or_ammunition",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2534,
  "source_span_end": 2692,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=Dragon Roach` — `rv2_change_53b58ceff9da1f1e4e56948f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage on its flame attack
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage on its flame attack",
  "heading_path": [
    "Dragon Roach"
  ],
  "entity": "Dragon Roach",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8347,
  "source_span_end": 8391,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Dragon roach` — `rv2_change_fabc9632401aaa48a53d8b42`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Spawn rate decreased
```

Extracted fields:

```json
{
  "change_text": "Spawn rate decreased",
  "heading_path": [
    "Dragon roach"
  ],
  "entity": "Dragon roach",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 11798,
  "source_span_end": 11818,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Dragon roach` — `rv2_change_b43a0a53abfd79738e63df3b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased how much damage wings take from explosion
```

Extracted fields:

```json
{
  "change_text": "Increased how much damage wings take from explosion",
  "heading_path": [
    "Dragon roach",
    "Destruction of the wings results in instant termination of the Dragon"
  ],
  "entity": "Destruction of the wings results in instant termination of the Dragon",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 12112,
  "source_span_end": 12163,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Durable damage for rifle calibers` — `rv2_change_ff7d6476f3b887d0ee3a3222`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
In general, the higher your caliber of weapon the better the effect is against durable body parts.
```

Extracted fields:

```json
{
  "change_text": "In general, the higher your caliber of weapon the better the effect is against durable body parts.",
  "heading_path": [
    "Durable damage for rifle calibers",
    "These changes affect",
    "A/G-16 Gatling Sentry"
  ],
  "entity": "A/G-16 Gatling Sentry",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7936,
  "source_span_end": 8034,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=E/MG-101 HMG Emplacement` — `rv2_change_21c595970846de1a950fb5c0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The HMG Emplacement is intended to be a way of defending a fixed position but due to its immobility and the drawback that presents, the slow rotation speed was a bit too much of an additional drawback.
```

Extracted fields:

```json
{
  "change_text": "The HMG Emplacement is intended to be a way of defending a fixed position but due to its immobility and the drawback that presents, the slow rotation speed was a bit too much of an additional drawback.",
  "heading_path": [
    "E/MG-101 HMG Emplacement"
  ],
  "entity": "E/MG-101 HMG Emplacement",
  "aspect": "speed_or_movement",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2065,
  "source_span_end": 2266,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=E/MG-101 HMG Emplacement` — `rv2_change_461ef6f8ded28157ea3d674b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Therefore we have increased the rotation speed significantly.
```

Extracted fields:

```json
{
  "change_text": "Therefore we have increased the rotation speed significantly.",
  "heading_path": [
    "E/MG-101 HMG Emplacement"
  ],
  "entity": "E/MG-101 HMG Emplacement",
  "aspect": "speed_or_movement",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2268,
  "source_span_end": 2329,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=EXO-45 Patriot Exosuit` — `rv2_change_13cc51a9f8571355491e2136`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Rotary gun ammo capacity increased from 1000 to 1350
```

Extracted fields:

```json
{
  "change_text": "Rotary gun ammo capacity increased from 1000 to 1350",
  "heading_path": [
    "EXO-45 Patriot Exosuit"
  ],
  "entity": "EXO-45 Patriot Exosuit",
  "aspect": "capacity_or_ammunition",
  "action": "increased",
  "direction": "increased",
  "previous_value": "1000",
  "new_value": "1350",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9245,
  "source_span_end": 9297,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=EXO-45 Patriot Exosuit` — `rv2_change_a09e6d2b68c8a12b261cc6a5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Missile Armor penetration in worse angles increased from 6-6-4-0 to 6-6-5-0
```

Extracted fields:

```json
{
  "change_text": "Missile Armor penetration in worse angles increased from 6-6-4-0 to 6-6-5-0",
  "heading_path": [
    "EXO-45 Patriot Exosuit"
  ],
  "entity": "EXO-45 Patriot Exosuit",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": "6",
  "new_value": "-6",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9156,
  "source_span_end": 9231,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=EXO-49 Emancipator Exosuit and EXO-45 Patriot Exosuit` — `rv2_change_ea07fc2bea7aa53b90acb947`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Arm health pool increased from 250 to 350
```

Extracted fields:

```json
{
  "change_text": "Arm health pool increased from 250 to 350",
  "heading_path": [
    "EXO-49 Emancipator Exosuit and EXO-45 Patriot Exosuit",
    "Both exosuits have been rebalanced to improve durability and extend combat effectiveness, while preserving a sense of vulnerability as they now gradually break down from sustained damage. The intention is to improve the experience with Exosuits by adding more gameplay depth"
  ],
  "entity": "Both exosuits have been rebalanced to improve durability and extend combat effectiveness, while preserving a sense of vulnerability as they now gradually break down from sustained damage. The intention is to improve the experience with Exosuits by adding more gameplay depth",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": "250",
  "new_value": "350",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5116,
  "source_span_end": 5157,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=EXO-49 Emancipator Exosuit and EXO-45 Patriot Exosuit` — `rv2_change_45ed64f7a2423d18a22faa8d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Arm armor decreased from 3 to 2
```

Extracted fields:

```json
{
  "change_text": "Arm armor decreased from 3 to 2",
  "heading_path": [
    "EXO-49 Emancipator Exosuit and EXO-45 Patriot Exosuit",
    "Both exosuits have been rebalanced to improve durability and extend combat effectiveness, while preserving a sense of vulnerability as they now gradually break down from sustained damage. The intention is to improve the experience with Exosuits by adding more gameplay depth"
  ],
  "entity": "Both exosuits have been rebalanced to improve durability and extend combat effectiveness, while preserving a sense of vulnerability as they now gradually break down from sustained damage. The intention is to improve the experience with Exosuits by adding more gameplay depth",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "3",
  "new_value": "2",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5162,
  "source_span_end": 5193,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Eagle 110MM Rocket Pods` — `rv2_change_0c512d4e1ca4a0f54aad75b6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased projectile damage 600 to 250 (to compensate for the improved targeting and the extra damage from the increased armor penetration.)
```

Extracted fields:

```json
{
  "change_text": "Decreased projectile damage 600 to 250 (to compensate for the improved targeting and the extra damage from the increased armor penetration.)",
  "heading_path": [
    "Eagle 110MM Rocket Pods",
    "While these changes may look like a straight up nerf, that is not the intention. Please see the blogpost for more information."
  ],
  "entity": "While these changes may look like a straight up nerf, that is not the intention. Please see the blogpost for more information.",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "600",
  "new_value": "250",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3070,
  "source_span_end": 3210,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Eagle 110MM Rocket Pods` — `rv2_change_5fbf0caf649d3bbab74d3d12`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased explosion armor penetration (explosion can no longer damage heavily armored enemies)
```

Extracted fields:

```json
{
  "change_text": "Decreased explosion armor penetration (explosion can no longer damage heavily armored enemies)",
  "heading_path": [
    "Eagle 110MM Rocket Pods",
    "While these changes may look like a straight up nerf, that is not the intention. Please see the blogpost for more information."
  ],
  "entity": "While these changes may look like a straight up nerf, that is not the intention. Please see the blogpost for more information.",
  "aspect": "damage_or_attack_power",
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3215,
  "source_span_end": 3309,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Eagle 110mm Rocket Pods` — `rv2_change_2785eb60d27f7bca1fb771dc`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased explosion armor penetration Medium to Heavy
```

Extracted fields:

```json
{
  "change_text": "Increased explosion armor penetration Medium to Heavy",
  "heading_path": [
    "Eagle 110mm Rocket Pods",
    "Intent: Make it better at one shotting smaller heavies like Chargers, Hulks, Harvesters (without shields). It can also kill some larger enemies like Tanks well. It is still not a 100% guaranteed kill, but it will be more reliable."
  ],
  "entity": "Intent: Make it better at one shotting smaller heavies like Chargers, Hulks, Harvesters (without shields). It can also kill some larger enemies like Tanks well. It is still not a 100% guaranteed kill, but it will be more reliable.",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9073,
  "source_span_end": 9126,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Eagle 110mm Rocket Pods` — `rv2_change_b0e08663de4b983f3ca74ddf`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased explosion durable damage 200 to 300
```

Extracted fields:

```json
{
  "change_text": "Increased explosion durable damage 200 to 300",
  "heading_path": [
    "Eagle 110mm Rocket Pods",
    "Intent: Make it better at one shotting smaller heavies like Chargers, Hulks, Harvesters (without shields). It can also kill some larger enemies like Tanks well. It is still not a 100% guaranteed kill, but it will be more reliable."
  ],
  "entity": "Intent: Make it better at one shotting smaller heavies like Chargers, Hulks, Harvesters (without shields). It can also kill some larger enemies like Tanks well. It is still not a 100% guaranteed kill, but it will be more reliable.",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9014,
  "source_span_end": 9059,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Eagle Strafing Run` — `rv2_change_c7304453bad639a08969246e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased armor penetration, can now damage heavily armored enemies.
```

Extracted fields:

```json
{
  "change_text": "Increased armor penetration, can now damage heavily armored enemies.",
  "heading_path": [
    "Eagle Strafing Run"
  ],
  "entity": "Eagle Strafing Run",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3386,
  "source_span_end": 3454,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Eagle Strafing Run` — `rv2_change_bfce74330fdeb6b369bc2d5d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
To that end we have increased its armor penetration to be able to reliably penetrate medium armored targets and soften up heavily armored enemies.
```

Extracted fields:

```json
{
  "change_text": "To that end we have increased its armor penetration to be able to reliably penetrate medium armored targets and soften up heavily armored enemies.",
  "heading_path": [
    "Eagle Strafing Run"
  ],
  "entity": "Eagle Strafing Run",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4712,
  "source_span_end": 4858,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Elevated Overseer` — `rv2_change_66a3f3f96c142905505d1a5a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Arms health decreased from 300 to 250
```

Extracted fields:

```json
{
  "change_text": "Arms health decreased from 300 to 250",
  "heading_path": [
    "Elevated Overseer"
  ],
  "entity": "Elevated Overseer",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "300",
  "new_value": "250",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10247,
  "source_span_end": 10284,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Elevated Overseer` — `rv2_change_809da6337a5be5b4ed3d9534`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Torso health decreased from 600 to 450
```

Extracted fields:

```json
{
  "change_text": "Torso health decreased from 600 to 450",
  "heading_path": [
    "Elevated Overseer"
  ],
  "entity": "Elevated Overseer",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "600",
  "new_value": "450",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10195,
  "source_span_end": 10233,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Enemies` — `rv2_change_54cd7315b04c11a9c364a57c`

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
  "entity": "Enemies",
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
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Enemies` — `rv2_change_9f2b269b44c1fbc1ce0d503e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Charge damage increased by 50%
```

Extracted fields:

```json
{
  "change_text": "Charge damage increased by 50%",
  "heading_path": [
    "Enemies",
    "Charger (All versions)",
    "Now charge less often"
  ],
  "entity": "Now charge less often",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": 50.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 14154,
  "source_span_end": 14184,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Enemy fixes` — `rv2_change_e4e09bd70716bed56e0bdba0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced the explosion radius of Tentacles Stabbing ability and Light Rockets. This should alleviate the excessive ragdolling caused by the Impaler and Automaton enemies using light rockets. We are still working on improving the ragdoll behavior overall.
```

Extracted fields:

```json
{
  "change_text": "Reduced the explosion radius of Tentacles Stabbing ability and Light Rockets. This should alleviate the excessive ragdolling caused by the Impaler and Automaton enemies using light rockets. We are still working on improving the ragdoll behavior overall.",
  "heading_path": [
    "Enemy fixes"
  ],
  "entity": "Enemy fixes",
  "aspect": "range_or_radius",
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 794,
  "source_span_end": 1047,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Enemy fixes` — `rv2_change_d1540523b19be2c3564a21cf`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a bug where the Impaler's tentacles could chase you indefinitely in some cases.
```

Extracted fields:

```json
{
  "change_text": "Fixed a bug where the Impaler's tentacles could chase you indefinitely in some cases.",
  "heading_path": [
    "Enemy fixes"
  ],
  "entity": "Enemy fixes",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "the Impaler's tentacles could chase you indefinitely in some cases",
  "source_span_start": 1053,
  "source_span_end": 1138,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Exo suits rebalance` — `rv2_change_d1ea2c9ffff4913f2eac109a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Exo suits no longer lose all mobility when both legs are broken.
```

Extracted fields:

```json
{
  "change_text": "Exo suits no longer lose all mobility when both legs are broken.",
  "heading_path": [
    "Exo suits rebalance",
    "We agree with the community that the Exosuits can take too little damage and break too easily, especially against the Automaton faction. Therefore we have made a bigger balance pass to increase its durability."
  ],
  "entity": "We agree with the community that the Exosuits can take too little damage and break too easily, especially against the Automaton faction. Therefore we have made a bigger balance pass to increase its durability.",
  "aspect": "speed_or_movement",
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3848,
  "source_span_end": 3912,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Exo suits rebalance` — `rv2_change_1858f19180f33d7935d2c4b6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Removed constitution and bleedout on the Exo suit arms.
```

Extracted fields:

```json
{
  "change_text": "Removed constitution and bleedout on the Exo suit arms.",
  "heading_path": [
    "Exo suits rebalance",
    "We agree with the community that the Exosuits can take too little damage and break too easily, especially against the Automaton faction. Therefore we have made a bigger balance pass to increase its durability."
  ],
  "entity": "We agree with the community that the Exosuits can take too little damage and break too easily, especially against the Automaton faction. Therefore we have made a bigger balance pass to increase its durability.",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3779,
  "source_span_end": 3834,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Expanded Emote Slots` — `rv2_change_105388203f767fa4a845f11b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The emote wheel capacity has been raised from 4 to 8 emotes
```

Extracted fields:

```json
{
  "change_text": "The emote wheel capacity has been raised from 4 to 8 emotes.",
  "heading_path": [
    "Expanded Emote Slots"
  ],
  "entity": "Expanded Emote Slots",
  "aspect": "capacity_or_ammunition",
  "action": "increased",
  "direction": "increased",
  "previous_value": "4",
  "new_value": "8",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3016,
  "source_span_end": 3075,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=FAF-14 Spear` — `rv2_change_782c243bbd93d600e6391f80`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added reload stage reload after the spent missile had been discarded
```

Extracted fields:

```json
{
  "change_text": "Added reload stage reload after the spent missile had been discarded",
  "heading_path": [
    "FAF-14 Spear"
  ],
  "entity": "FAF-14 Spear",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3708,
  "source_span_end": 3776,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=FLAM-40 Flamethrower` — `rv2_change_5952d339abf74a5e90219286`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Max spare canisters increased from 4 to 5
```

Extracted fields:

```json
{
  "change_text": "Max spare canisters increased from 4 to 5",
  "heading_path": [
    "FLAM-40 Flamethrower"
  ],
  "entity": "FLAM-40 Flamethrower",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "4",
  "new_value": "5",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8309,
  "source_span_end": 8350,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=FLAM-40 Flamethrower` — `rv2_change_788947c2c2a7781fbae2590c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Canister capacity increased from 130 to 150
```

Extracted fields:

```json
{
  "change_text": "Canister capacity increased from 130 to 150",
  "heading_path": [
    "FLAM-40 Flamethrower"
  ],
  "entity": "FLAM-40 Flamethrower",
  "aspect": "capacity_or_ammunition",
  "action": "increased",
  "direction": "increased",
  "previous_value": "130",
  "new_value": "150",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8198,
  "source_span_end": 8241,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=FRV` — `rv2_change_bbcdb923d86dbb44f52fc9f8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Tuned FRV handling for a better driving experience when cornering
```

Extracted fields:

```json
{
  "change_text": "Tuned FRV handling for a better driving experience when cornering",
  "heading_path": [
    "FRV"
  ],
  "entity": "FRV",
  "aspect": "rewards_or_progression",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1132,
  "source_span_end": 1197,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=FRV` — `rv2_change_bffe31f926ed3eaede37fc73`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a bug where some enemies such as the Brood Commander was launched away further than intended when hit by the FRV
```

Extracted fields:

```json
{
  "change_text": "Fixed a bug where some enemies such as the Brood Commander was launched away further than intended when hit by the FRV",
  "heading_path": [
    "FRV"
  ],
  "entity": "FRV",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "when hit by the FRV",
  "bug_symptom": "some enemies such as the Brood Commander was launched away further than intended",
  "source_span_start": 7208,
  "source_span_end": 7326,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Fire and Flamethrowers` — `rv2_change_e57a7a01ffc81b1bd02ab2f7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Health increased from 1500 to 5000
```

Extracted fields:

```json
{
  "change_text": "Health increased from 1500 to 5000",
  "heading_path": [
    "Fire and Flamethrowers",
    "Damage",
    "Enemies",
    "Bulk Fabricator"
  ],
  "entity": "Bulk Fabricator",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": "1500",
  "new_value": "5000",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 11444,
  "source_span_end": 11478,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Fire and Flamethrowers` — `rv2_change_20ed136286528d8ae6714afd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased Spread from 30 to 8
```

Extracted fields:

```json
{
  "change_text": "Decreased Spread from 30 to 8",
  "heading_path": [
    "Fire and Flamethrowers",
    "Damage",
    "Sidearm Weapons",
    "P-113 Verdict"
  ],
  "entity": "P-113 Verdict",
  "aspect": "accuracy_or_spread",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "30",
  "new_value": "8",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9928,
  "source_span_end": 9957,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Firebomb Hellpod` — `rv2_change_00933bbefca49370d073d290`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Demolition strength decreased from 40 to 20 because we now correctly also additively apply the normal Hellpod explosion
```

Extracted fields:

```json
{
  "change_text": "Demolition strength decreased from 40 to 20 because we now correctly also additively apply the normal Hellpod explosion",
  "heading_path": [
    "Firebomb Hellpod"
  ],
  "entity": "Firebomb Hellpod",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "40",
  "new_value": "20",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2976,
  "source_span_end": 3095,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Firebomb Hellpod` — `rv2_change_95df77053b7d01b16b9e8136`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Now affects the Hellpods default explosion as well
```

Extracted fields:

```json
{
  "change_text": "Now affects the Hellpods default explosion as well",
  "heading_path": [
    "Firebomb Hellpod"
  ],
  "entity": "Firebomb Hellpod",
  "aspect": null,
  "action": "modified",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2827,
  "source_span_end": 2877,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Fix` — `rv2_change_c4638822c9266f9b428fadf0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a common crash that occurs when killing the Impaler inside a Stronghold
```

Extracted fields:

```json
{
  "change_text": "Fixed a common crash that occurs when killing the Impaler inside a Stronghold",
  "heading_path": [
    "Fix",
    "This patch is an emergency hot fix addressing the Impaler crash. We deemed it worth bringing this one crash fix in now in an attempt to minimize the crashes during the weekend. Thank you for your understanding."
  ],
  "entity": "This patch is an emergency hot fix addressing the Impaler crash. We deemed it worth bringing this one crash fix in now in an attempt to minimize the crashes during the weekend. Thank you for your understanding.",
  "aspect": "performance_or_network",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 237,
  "source_span_end": 314,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Fixes` — `rv2_change_9e67f8a77fea640c6ae030ca`

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
  "entity": "Impaler",
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
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Fixes` — `rv2_change_1f5ee6d6ce2328c1531e918f`

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

### patch_change — `game=553850;section=Fleshmob` — `rv2_change_80abfcd0693023bbad4342fd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Main health decreased from 6000 to 5000
```

Extracted fields:

```json
{
  "change_text": "Main health decreased from 6000 to 5000",
  "heading_path": [
    "Fleshmob"
  ],
  "entity": "Fleshmob",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "6000",
  "new_value": "5000",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9807,
  "source_span_end": 9846,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=For this patch, our area of focus is` — `rv2_change_8807156ec58a0c02f9053da5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Defend Events have been fixed and received an update
```

Extracted fields:

```json
{
  "change_text": "Defend Events have been fixed and received an update",
  "heading_path": [
    "For this patch, our area of focus is"
  ],
  "entity": "For this patch, our area of focus is",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 141,
  "source_span_end": 193,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=For this patch, our area of focus is` — `rv2_change_e385412dc0d744603292d242`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
🔧 Fixes
```

Extracted fields:

```json
{
  "change_text": "🔧 Fixes",
  "heading_path": [
    "For this patch, our area of focus is"
  ],
  "entity": "For this patch, our area of focus is",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 122,
  "source_span_end": 129,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=For this patch, our major areas of focus were` — `rv2_change_cd7808ba3effe3cbd0a99022`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
🔧 Fixes
```

Extracted fields:

```json
{
  "change_text": "🔧 Fixes",
  "heading_path": [
    "For this patch, our major areas of focus were",
    "Optimizing our server"
  ],
  "entity": "Optimizing our server",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 230,
  "source_span_end": 237,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=For this patch, our major areas of focus were` — `rv2_change_075ea6187affb77f3c456e75`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The following issues have been fixed for this version.
```

Extracted fields:

```json
{
  "change_text": "The following issues have been fixed for this version.",
  "heading_path": [
    "For this patch, our major areas of focus were",
    "Optimizing our server"
  ],
  "entity": "Optimizing our server",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 238,
  "source_span_end": 292,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=For this patch, we have focused on the following areas` — `rv2_change_c524710a66b50452b65d94d6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Game no longer crashes when users disconnect during the joining cutscene.
```

Extracted fields:

```json
{
  "change_text": "Game no longer crashes when users disconnect during the joining cutscene.",
  "heading_path": [
    "For this patch, we have focused on the following areas"
  ],
  "entity": "For this patch, we have focused on the following areas",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 585,
  "source_span_end": 658,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=For this patch, we have focused on the following areas` — `rv2_change_e0c11db3e29fd22a07e9f38a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Game no longer crashes during extraction cutscene.
```

Extracted fields:

```json
{
  "change_text": "Game no longer crashes during extraction cutscene.",
  "heading_path": [
    "For this patch, we have focused on the following areas"
  ],
  "entity": "For this patch, we have focused on the following areas",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 398,
  "source_span_end": 448,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=For this patch, we have made improvements and changes to the following areas` — `rv2_change_f8793520cb4aeaec87c9e18a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Crash fixes
```

Extracted fields:

```json
{
  "change_text": "Crash fixes",
  "heading_path": [
    "For this patch, we have made improvements and changes to the following areas",
    "Some weapon and enemy balancing"
  ],
  "entity": "Some weapon and enemy balancing",
  "aspect": "performance_or_network",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 279,
  "source_span_end": 290,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=For this patch, we have made improvements and changes to the following areas` — `rv2_change_5d44d3e3afc7f54a66f78614`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
General fixes and improvements
```

Extracted fields:

```json
{
  "change_text": "General fixes and improvements",
  "heading_path": [
    "For this patch, we have made improvements and changes to the following areas",
    "Misaligned scopes fix"
  ],
  "entity": "Misaligned scopes fix",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 363,
  "source_span_end": 393,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Frag Grenade` — `rv2_change_2a1ea8ce3b3a061c33f77af7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased Shrapnel spawned from 30 to 35
```

Extracted fields:

```json
{
  "change_text": "Increased Shrapnel spawned from 30 to 35",
  "heading_path": [
    "Frag Grenade"
  ],
  "entity": "Frag Grenade",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "30",
  "new_value": "35",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4486,
  "source_span_end": 4526,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Front Legs` — `rv2_change_c3d8ce3704a72dc03bb9d73e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Armor increased from 2 → 3
```

Extracted fields:

```json
{
  "change_text": "Armor increased from 2 → 3",
  "heading_path": [
    "Front Legs"
  ],
  "entity": "Front Legs",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 457,
  "source_span_end": 483,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=G-10 Incendiary` — `rv2_change_e52481d76b7a4f6d22567b97`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased start amount from 3 to 4
```

Extracted fields:

```json
{
  "change_text": "Increased start amount from 3 to 4",
  "heading_path": [
    "G-10 Incendiary"
  ],
  "entity": "G-10 Incendiary",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "3",
  "new_value": "4",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8206,
  "source_span_end": 8240,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-10 Incendiary` — `rv2_change_e80dfc2d257f3034b538d6b8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased refill from 2 to 3
```

Extracted fields:

```json
{
  "change_text": "Increased refill from 2 to 3",
  "heading_path": [
    "G-10 Incendiary"
  ],
  "entity": "G-10 Incendiary",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "2",
  "new_value": "3",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8254,
  "source_span_end": 8282,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-109 Urchin` — `rv2_change_7e9ff00ed8ff51c73eda3891`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased max amount from 4 to 5
```

Extracted fields:

```json
{
  "change_text": "Increased max amount from 4 to 5",
  "heading_path": [
    "G-109 Urchin"
  ],
  "entity": "G-109 Urchin",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "4",
  "new_value": "5",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8110,
  "source_span_end": 8142,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-109 Urchin` — `rv2_change_14bd55ca5fec93b53db02708`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased start amount from 2 to 4
```

Extracted fields:

```json
{
  "change_text": "Increased start amount from 2 to 4",
  "heading_path": [
    "G-109 Urchin"
  ],
  "entity": "G-109 Urchin",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "2",
  "new_value": "4",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8020,
  "source_span_end": 8054,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-12 High Explosive` — `rv2_change_533fa909d4a71647aacb5bb0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased Start amount from 3 to 4
```

Extracted fields:

```json
{
  "change_text": "Increased Start amount from 3 to 4",
  "heading_path": [
    "G-12 High Explosive"
  ],
  "entity": "G-12 High Explosive",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "3",
  "new_value": "4",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7291,
  "source_span_end": 7325,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-12 High Explosive` — `rv2_change_c45c530a7f0a66c49d9f902d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased max amount from 4 to 5
```

Extracted fields:

```json
{
  "change_text": "Increased max amount from 4 to 5",
  "heading_path": [
    "G-12 High Explosive"
  ],
  "entity": "G-12 High Explosive",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "4",
  "new_value": "5",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7381,
  "source_span_end": 7413,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-13 Incendiary Impact` — `rv2_change_ad5bab3d5281f62d81603e5b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased refill from 2 to 3
```

Extracted fields:

```json
{
  "change_text": "Increased refill from 2 to 3",
  "heading_path": [
    "G-13 Incendiary Impact"
  ],
  "entity": "G-13 Incendiary Impact",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "2",
  "new_value": "3",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8447,
  "source_span_end": 8475,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-13 Incendiary Impact` — `rv2_change_c182570249d877609cf9d24c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased max amount from 4 to 5
```

Extracted fields:

```json
{
  "change_text": "Increased max amount from 4 to 5",
  "heading_path": [
    "G-13 Incendiary Impact"
  ],
  "entity": "G-13 Incendiary Impact",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "4",
  "new_value": "5",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8489,
  "source_span_end": 8521,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-13 Incendiary impact` — `rv2_change_212f2a7ae8179052d154e311`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The amount of fuel has been increased in the grenade, resulting in a longer-lasting fire duration
```

Extracted fields:

```json
{
  "change_text": "The amount of fuel has been increased in the grenade, resulting in a longer-lasting fire duration",
  "heading_path": [
    "G-13 Incendiary impact"
  ],
  "entity": "G-13 Incendiary impact",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2341,
  "source_span_end": 2438,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-16 Impact` — `rv2_change_6aedb0b17332feb0a68b56d5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased Start amount from 3 to 4
```

Extracted fields:

```json
{
  "change_text": "Increased Start amount from 3 to 4",
  "heading_path": [
    "G-16 Impact"
  ],
  "entity": "G-16 Impact",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "3",
  "new_value": "4",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7473,
  "source_span_end": 7507,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-16 Impact` — `rv2_change_5d1de07f787c86aa22f0b8ce`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased refill from 2 to 3
```

Extracted fields:

```json
{
  "change_text": "Increased refill from 2 to 3",
  "heading_path": [
    "G-16 Impact"
  ],
  "entity": "G-16 Impact",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "2",
  "new_value": "3",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7521,
  "source_span_end": 7549,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-23 Stun` — `rv2_change_88b4fa37c48743742b478626`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased max amount from 4 to 5
```

Extracted fields:

```json
{
  "change_text": "Increased max amount from 4 to 5",
  "heading_path": [
    "G-23 Stun"
  ],
  "entity": "G-23 Stun",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "4",
  "new_value": "5",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7927,
  "source_span_end": 7959,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-23 Stun` — `rv2_change_fed4af886c021f2643ba9719`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased start amount from 3 to 4
```

Extracted fields:

```json
{
  "change_text": "Increased start amount from 3 to 4",
  "heading_path": [
    "G-23 Stun"
  ],
  "entity": "G-23 Stun",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "3",
  "new_value": "4",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7837,
  "source_span_end": 7871,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-3 Smoke` — `rv2_change_ecb2ccccc9e8bfe6d6daf154`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Uses increased from 4 to 5
```

Extracted fields:

```json
{
  "change_text": "Uses increased from 4 to 5",
  "heading_path": [
    "G-3 Smoke"
  ],
  "entity": "G-3 Smoke",
  "aspect": "capacity_or_ammunition",
  "action": "increased",
  "direction": "increased",
  "previous_value": "4",
  "new_value": "5",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7146,
  "source_span_end": 7172,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=G-31 Arc` — `rv2_change_c82818bfe478e2489b719545`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased max amount uses 4 to 5
```

Extracted fields:

```json
{
  "change_text": "Increased max amount uses 4 to 5",
  "heading_path": [
    "G-31 Arc"
  ],
  "entity": "G-31 Arc",
  "aspect": "capacity_or_ammunition",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6933,
  "source_span_end": 6965,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=G-31 Arc` — `rv2_change_29585ca96faef9daaea79412`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased start amount uses 3 to 4
```

Extracted fields:

```json
{
  "change_text": "Increased start amount uses 3 to 4",
  "heading_path": [
    "G-31 Arc"
  ],
  "entity": "G-31 Arc",
  "aspect": "capacity_or_ammunition",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6979,
  "source_span_end": 7013,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=G-48 Giga Grenade` — `rv2_change_c06722eab678a7ef68da066d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased refill from 1 to 2
```

Extracted fields:

```json
{
  "change_text": "Increased refill from 1 to 2",
  "heading_path": [
    "G-48 Giga Grenade"
  ],
  "entity": "G-48 Giga Grenade",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "1",
  "new_value": "2",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6917,
  "source_span_end": 6945,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-50 Seeker` — `rv2_change_a5f61e856925eb239f2957e7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Higher priority for flying enemies
```

Extracted fields:

```json
{
  "change_text": "Higher priority for flying enemies",
  "heading_path": [
    "G-50 Seeker"
  ],
  "entity": "G-50 Seeker",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6886,
  "source_span_end": 6920,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-50 Seeker` — `rv2_change_b25478d40d60a0425c00634a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 400 to 500
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 400 to 500",
  "heading_path": [
    "G-50 Seeker"
  ],
  "entity": "G-50 Seeker",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "400",
  "new_value": "500",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6989,
  "source_span_end": 7021,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=G-6 Frag` — `rv2_change_ac68992e96c3964e7aea5d4b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Uses increased from 5 to 6
```

Extracted fields:

```json
{
  "change_text": "Uses increased from 5 to 6",
  "heading_path": [
    "G-6 Frag"
  ],
  "entity": "G-6 Frag",
  "aspect": "capacity_or_ammunition",
  "action": "increased",
  "direction": "increased",
  "previous_value": "5",
  "new_value": "6",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7070,
  "source_span_end": 7096,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=G-7 Pineapple` — `rv2_change_5a3ba55825a56c8b54101e1a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Demolition strength on the main explosion increased from 20 to 30
```

Extracted fields:

```json
{
  "change_text": "Demolition strength on the main explosion increased from 20 to 30",
  "heading_path": [
    "G-7 Pineapple"
  ],
  "entity": "G-7 Pineapple",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "20",
  "new_value": "30",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6511,
  "source_span_end": 6576,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=G-7 Pineapple` — `rv2_change_fbdf2fc32819f2309f7e9aaf`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Shrapnel from the shrapnel explosion decreased from 6 to 0
```

Extracted fields:

```json
{
  "change_text": "Shrapnel from the shrapnel explosion decreased from 6 to 0",
  "heading_path": [
    "G-7 Pineapple"
  ],
  "entity": "G-7 Pineapple",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "6",
  "new_value": "0",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6776,
  "source_span_end": 6834,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=GATER Upgrades` — `rv2_change_7975cd35601a1d784480381c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Super Earth engineers have replaced the engine and transmission in the GATER in favor of a much more powerful Super V48 Interceptor engine, this has improved its speed and handling.
```

Extracted fields:

```json
{
  "change_text": "Super Earth engineers have replaced the engine and transmission in the GATER in favor of a much more powerful Super V48 Interceptor engine, this has improved its speed and handling.",
  "heading_path": [
    "GATER Upgrades"
  ],
  "entity": "GATER Upgrades",
  "aspect": "speed_or_movement",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3486,
  "source_span_end": 3667,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=GL-21 Grenade Launcher` — `rv2_change_8e5fdfb7b1219cc9511906f7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased armor penetration level from Medium to Heavy
```

Extracted fields:

```json
{
  "change_text": "Increased armor penetration level from Medium to Heavy",
  "heading_path": [
    "GL-21 Grenade Launcher"
  ],
  "entity": "GL-21 Grenade Launcher",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7914,
  "source_span_end": 7968,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=GL-21 Grenade Launcher` — `rv2_change_aaedbe82a8162672e98b03ca`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased explosion damage by from 350 to 400
```

Extracted fields:

```json
{
  "change_text": "Increased explosion damage by from 350 to 400",
  "heading_path": [
    "GL-21 Grenade Launcher"
  ],
  "entity": "GL-21 Grenade Launcher",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "350",
  "new_value": "400",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3504,
  "source_span_end": 3549,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=GL-52 De-Escalator` — `rv2_change_0971964aa1d9fb33c6d0a99c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Durable damage increased from 55 to 70
```

Extracted fields:

```json
{
  "change_text": "Durable damage increased from 55 to 70",
  "heading_path": [
    "GL-52 De-Escalator"
  ],
  "entity": "GL-52 De-Escalator",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "55",
  "new_value": "70",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8758,
  "source_span_end": 8796,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=GL-52 De-Escalator` — `rv2_change_e17a37657b0bacf025f5df7c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 55 to 100
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 55 to 100",
  "heading_path": [
    "GL-52 De-Escalator"
  ],
  "entity": "GL-52 De-Escalator",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "55",
  "new_value": "100",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8713,
  "source_span_end": 8744,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=GP-20 Ultimatum` — `rv2_change_2873a7bb6e2f179c7c2596db`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased sway modifier from 1.3 to 1
```

Extracted fields:

```json
{
  "change_text": "Decreased sway modifier from 1.3 to 1",
  "heading_path": [
    "GP-20 Ultimatum"
  ],
  "entity": "GP-20 Ultimatum",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "1.3",
  "new_value": "1",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5890,
  "source_span_end": 5927,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=GP-31 Grenade Pistol` — `rv2_change_399cd0e5e065d1c7d0acb7a9`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased ammo capacity from 8 to 6
```

Extracted fields:

```json
{
  "change_text": "Decreased ammo capacity from 8 to 6",
  "heading_path": [
    "GP-31 Grenade Pistol"
  ],
  "entity": "GP-31 Grenade Pistol",
  "aspect": "capacity_or_ammunition",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "8",
  "new_value": "6",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2875,
  "source_span_end": 2910,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=GP-31 Grenade Pistol` — `rv2_change_0b942073ac6cb6d5e17018ec`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased the number of rounds replenished from an ammo box from 2 to 4
```

Extracted fields:

```json
{
  "change_text": "Increased the number of rounds replenished from an ammo box from 2 to 4",
  "heading_path": [
    "GP-31 Grenade Pistol"
  ],
  "entity": "GP-31 Grenade Pistol",
  "aspect": "capacity_or_ammunition",
  "action": "increased",
  "direction": "increased",
  "previous_value": "2",
  "new_value": "4",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2915,
  "source_span_end": 2986,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Gameplay` — `rv2_change_abecc6dd6c6710d7d231e8fb`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
A new grief protection system has been added that allows kicked players to continue in their own mission. This allows players to complete the mission and get full rewards despite being kicked.
```

Extracted fields:

```json
{
  "change_text": "A new grief protection system has been added that allows kicked players to continue in their own mission. This allows players to complete the mission and get full rewards despite being kicked.",
  "heading_path": [
    "Gameplay"
  ],
  "entity": null,
  "aspect": "content_or_feature",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4064,
  "source_span_end": 4256,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Gameplay` — `rv2_change_ff924958727a48a82ce02f1e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The sound when stimming no longer plays while being interrupted
```

Extracted fields:

```json
{
  "change_text": "The sound when stimming no longer plays while being interrupted",
  "heading_path": [
    "Gameplay"
  ],
  "entity": null,
  "aspect": "audio",
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1294,
  "source_span_end": 1357,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved"
  ]
}
```

### patch_change — `game=553850;section=General` — `rv2_change_bfdbeea3e6542a45ca264afd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We want to look over the operation modifiers in the future. Right now there are too few of them which become repetitive and the ones we have do not create variety or promote different playstyles. For now, we removed this one because it only encourages the players to bring the best stratagems and does not promote variety
```

Extracted fields:

```json
{
  "change_text": "We want to look over the operation modifiers in the future. Right now there are too few of them which become repetitive and the ones we have do not create variety or promote different playstyles. For now, we removed this one because it only encourages the players to bring the best stratagems and does not promote variety",
  "heading_path": [
    "General"
  ],
  "entity": null,
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6112,
  "source_span_end": 6433,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=General` — `rv2_change_a508a52a5193eddd8dada1f4`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Enemies Aim calculations were not always updated when there were many enemies trying to aim, making Automatons on higher difficulties a bit bad at aiming.
```

Extracted fields:

```json
{
  "change_text": "Enemies Aim calculations were not always updated when there were many enemies trying to aim, making Automatons on higher difficulties a bit bad at aiming.",
  "heading_path": [
    "General"
  ],
  "entity": null,
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9013,
  "source_span_end": 9167,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=General Changes` — `rv2_change_7d210ae20cc214f02a9bd15d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Implemented a timer for the Illuminate dropship wreckages to despawn to prevent them from obstructing paths in the colonies
```

Extracted fields:

```json
{
  "change_text": "Implemented a timer for the Illuminate dropship wreckages to despawn to prevent them from obstructing paths in the colonies",
  "heading_path": [
    "General Changes"
  ],
  "entity": "General Changes",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 628,
  "source_span_end": 751,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=General Changes` — `rv2_change_2dc03228841df151ef1e5885`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The duration of the gas status effect from spray weapons has been increased from 6 to 10 sec
```

Extracted fields:

```json
{
  "change_text": "The duration of the gas status effect from spray weapons has been increased from 6 to 10 sec",
  "heading_path": [
    "General Changes"
  ],
  "entity": "General Changes",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "6",
  "new_value": "10 sec",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 531,
  "source_span_end": 623,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=General Gameplay` — `rv2_change_2898172ae79b621dfbb2f0d0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Bug infested zones have had their fog and effects adjusted for better visibility.
```

Extracted fields:

```json
{
  "change_text": "Bug infested zones have had their fog and effects adjusted for better visibility.",
  "heading_path": [
    "General Gameplay",
    "Bug infestation zone visuals -"
  ],
  "entity": "Bug infestation zone visuals -",
  "aspect": "bug_or_functionality",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1317,
  "source_span_end": 1398,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=General Gameplay` — `rv2_change_86d64a877461061fdf6c273b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Bug infested zones, such as the areas around bug outposts and bug objectives, have had their visuals changed to integrate more with the biome/planet they’re on. Zones should now look more different from planet to planet.
```

Extracted fields:

```json
{
  "change_text": "Bug infested zones, such as the areas around bug outposts and bug objectives, have had their visuals changed to integrate more with the biome/planet they’re on. Zones should now look more different from planet to planet.",
  "heading_path": [
    "General Gameplay",
    "Bug infestation zone visuals -"
  ],
  "entity": "Bug infestation zone visuals -",
  "aspect": "bug_or_functionality",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1093,
  "source_span_end": 1313,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=General Weapon and Stratagem Fixes` — `rv2_change_cd508f718a91bc7e356b187f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Thermite grenades no longer make the orbital cannon objective incompletable.
```

Extracted fields:

```json
{
  "change_text": "Thermite grenades no longer make the orbital cannon objective incompletable.",
  "heading_path": [
    "General Weapon and Stratagem Fixes"
  ],
  "entity": "General Weapon and Stratagem Fixes",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 459,
  "source_span_end": 535,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=General Weapon and Stratagem Fixes` — `rv2_change_4ef125f6c04f6be1a375fd11`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a bug where flamethrower weapons bounce off energy shields, making them useless when firing within shield generator relay domes.
```

Extracted fields:

```json
{
  "change_text": "Fixed a bug where flamethrower weapons bounce off energy shields, making them useless when firing within shield generator relay domes.",
  "heading_path": [
    "General Weapon and Stratagem Fixes"
  ],
  "entity": "General Weapon and Stratagem Fixes",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "when firing within shield generator relay domes",
  "bug_symptom": "flamethrower weapons bounce off energy shields, making them useless",
  "source_span_start": 610,
  "source_span_end": 744,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=General Weapon and Stratagem fixes` — `rv2_change_fa1951a5c6f167450279c84d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed an issue where flamethrower particles would ignore enemies.
```

Extracted fields:

```json
{
  "change_text": "Fixed an issue where flamethrower particles would ignore enemies.",
  "heading_path": [
    "General Weapon and Stratagem fixes"
  ],
  "entity": "General Weapon and Stratagem fixes",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "flamethrower particles would ignore enemies",
  "source_span_start": 619,
  "source_span_end": 684,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=General changes` — `rv2_change_80ff54d9ff58c5e113b197d8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Removed ricochets from Orbital Stratagem projectiles, Eagle-1 bombs and FAF-14 Spear missiles
```

Extracted fields:

```json
{
  "change_text": "Removed ricochets from Orbital Stratagem projectiles, Eagle-1 bombs and FAF-14 Spear missiles",
  "heading_path": [
    "General changes",
    "Additional Supply Items are now visible on the minimap",
    "Exosuits"
  ],
  "entity": "Exosuits",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1805,
  "source_span_end": 1898,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=General changes` — `rv2_change_56cf57f3b636619de7845e2b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Light armor increases damage taken by 25%, down from 33%
```

Extracted fields:

```json
{
  "change_text": "Light armor increases damage taken by 25%, down from 33%",
  "heading_path": [
    "General changes",
    "Heavy armor reduces damage taken by 25%, up from 20%"
  ],
  "entity": "Heavy armor reduces damage taken by 25%, up from 20%",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": 25.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2133,
  "source_span_end": 2189,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=General changes overview` — `rv2_change_ca82a5dabe706dd25173aaf5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Melee weapons and Armor passive with increased melee damage re-balance
```

Extracted fields:

```json
{
  "change_text": "Melee weapons and Armor passive with increased melee damage re-balance",
  "heading_path": [
    "General changes overview"
  ],
  "entity": "General changes overview",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1617,
  "source_span_end": 1687,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=General changes overview` — `rv2_change_2e01a7bbe61c9b25f459b59f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Enemies detection radius when being fired at, but not being hit, is reduced in some units
```

Extracted fields:

```json
{
  "change_text": "Enemies detection radius when being fired at, but not being hit, is reduced in some units",
  "heading_path": [
    "General changes overview",
    "Suppressors are now more effective"
  ],
  "entity": "Suppressors are now more effective",
  "aspect": "range_or_radius",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1737,
  "source_span_end": 1826,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Goal with stratagem balance changes this patch` — `rv2_change_35d3093d451ac9148e6a6123`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We also changed a few to make them more consistent, but the goal was to keep a similar or higher power level
```

Extracted fields:

```json
{
  "change_text": "We also changed a few to make them more consistent, but the goal was to keep a similar or higher power level.",
  "heading_path": [
    "Goal with stratagem balance changes this patch"
  ],
  "entity": "Goal with stratagem balance changes this patch",
  "aspect": "map_or_level",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 864,
  "source_span_end": 972,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=Goal with stratagem balance changes this patch` — `rv2_change_5ece63663526dca6ebe6381c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We are looking into the stratagems more to see if there are any other stratagems that might need some buffs or changes to make them more viable.
```

Extracted fields:

```json
{
  "change_text": "We are looking into the stratagems more to see if there are any other stratagems that might need some buffs or changes to make them more viable.",
  "heading_path": [
    "Goal with stratagem balance changes this patch"
  ],
  "entity": "Goal with stratagem balance changes this patch",
  "aspect": null,
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 974,
  "source_span_end": 1118,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Grenades` — `rv2_change_aa4c97adff0fb94f092580e8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Explosion radius increased
```

Extracted fields:

```json
{
  "change_text": "Explosion radius increased",
  "heading_path": [
    "Grenades",
    "Frag Grenade"
  ],
  "entity": "Frag Grenade",
  "aspect": "range_or_radius",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9710,
  "source_span_end": 9736,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Grenades` — `rv2_change_771aa78188e577cfabffe213`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Max number decreased from 4 to 3
```

Extracted fields:

```json
{
  "change_text": "Max number decreased from 4 to 3",
  "heading_path": [
    "Grenades",
    "Thermite Grenade"
  ],
  "entity": "Thermite Grenade",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "4",
  "new_value": "3",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9912,
  "source_span_end": 9944,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Gunship` — `rv2_change_f09b5637500b20991d66c968`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
updated its targeting software and should now be better at hitting their targets
```

Extracted fields:

```json
{
  "change_text": "updated its targeting software and should now be better at hitting their targets",
  "heading_path": [
    "Gunship"
  ],
  "entity": "Gunship",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10026,
  "source_span_end": 10106,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Gunship` — `rv2_change_1962b66d3061a22e59e8009b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Rockets now deals increased damage vs Durable targets
```

Extracted fields:

```json
{
  "change_text": "Rockets now deals increased damage vs Durable targets",
  "heading_path": [
    "Gunship"
  ],
  "entity": "Gunship",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10120,
  "source_span_end": 10173,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Hang Detection` — `rv2_change_54597f81454811746f07fcbc`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
As part of our ongoing war against bugs and instability we have introduced a “hang detection” feature in the PC version.
```

Extracted fields:

```json
{
  "change_text": "As part of our ongoing war against bugs and instability we have introduced a “hang detection” feature in the PC version.",
  "heading_path": [
    "Hang Detection"
  ],
  "entity": "Hang Detection",
  "aspect": "content_or_feature",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10997,
  "source_span_end": 11117,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Head` — `rv2_change_a418d307cd928ca070cd70c7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Armor decreased from 4 → 3
```

Extracted fields:

```json
{
  "change_text": "Armor decreased from 4 → 3",
  "heading_path": [
    "Head"
  ],
  "entity": "Head",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 400,
  "source_span_end": 426,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Helldiver` — `rv2_change_181ad0ece8945d587ebf15c9`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced the time it takes for the Helldiver to regain control after ragdolling from 0.8 to 0.5 sec
```

Extracted fields:

```json
{
  "change_text": "Reduced the time it takes for the Helldiver to regain control after ragdolling from 0.8 to 0.5 sec",
  "heading_path": [
    "Helldiver"
  ],
  "entity": "Helldiver",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "0.8",
  "new_value": "0.5 sec",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 380,
  "source_span_end": 478,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Helldiver` — `rv2_change_8bd326ef7757d8a29b97e1d6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased chest injury bleed damage from 1 to 10.
```

Extracted fields:

```json
{
  "change_text": "Increased chest injury bleed damage from 1 to 10.",
  "heading_path": [
    "Helldiver"
  ],
  "entity": "Helldiver",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "1",
  "new_value": "10.",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 492,
  "source_span_end": 541,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Helldivers 2` — `rv2_change_cef049b9866254c1b8d0748f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
developer Arrowhead has addressed the lack of communication over the next, delayed patch.
```

Extracted fields:

```json
{
  "change_text": "developer Arrowhead has addressed the lack of communication over the next, delayed patch.",
  "heading_path": [
    "Helldivers 2"
  ],
  "entity": "Helldivers 2",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 168,
  "source_span_end": 257,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Helldivers 2` — `rv2_change_1c36b5d23bdcf0f37b2d8779`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Helldivers 2 patch 1.000.100 is out now on PC, with the PlayStation 5 update set to follow soon, and it introduces new planetary hazards along with some balance changes to some of the weapons considered to be "quite strong with too little downside.
```

Extracted fields:

```json
{
  "change_text": "Helldivers 2 patch 1.000.100 is out now on PC, with the PlayStation 5 update set to follow soon, and it introduces new planetary hazards along with some balance changes to some of the weapons considered to be \"quite strong with too little downside.\"",
  "heading_path": [
    "Helldivers 2"
  ],
  "entity": "Helldivers 2",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 546,
  "source_span_end": 794,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=Hive Lord` — `rv2_change_820d7c8e636ffe9cf61705e4`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage on many of its physical attacks
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage on many of its physical attacks",
  "heading_path": [
    "Hive Lord"
  ],
  "entity": "Hive Lord",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8230,
  "source_span_end": 8286,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Hive Lord` — `rv2_change_ef37201dcc4ab303ee4df6e3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Improved performance during Hive Lord encounters.
```

Extracted fields:

```json
{
  "change_text": "Improved performance during Hive Lord encounters.",
  "heading_path": [
    "Hive Lord"
  ],
  "entity": "Hive Lord",
  "aspect": "performance_or_network",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 12378,
  "source_span_end": 12427,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Hive guard` — `rv2_change_34837fd536488c0bb3535e19`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased armor on head and front legs from Medium to Heavy (3 to 4)
```

Extracted fields:

```json
{
  "change_text": "Increased armor on head and front legs from Medium to Heavy (3 to 4)",
  "heading_path": [
    "Hive guard"
  ],
  "entity": "Hive guard",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": "3",
  "new_value": "4",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7333,
  "source_span_end": 7401,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Hive guard` — `rv2_change_6e1e5554640b32a0410696ad`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased health on body from 500 to 375
```

Extracted fields:

```json
{
  "change_text": "Decreased health on body from 500 to 375",
  "heading_path": [
    "Hive guard"
  ],
  "entity": "Hive guard",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "500",
  "new_value": "375",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7495,
  "source_span_end": 7535,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=How we Heralded it in HELLDIVERS 2` — `rv2_change_4b2693870a86355717392c87`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We wanted those bones to serve as a promise to eventually show you the beast in its full glory and to be a motivator for us internally of what the game should eventually introduce
```

Extracted fields:

```json
{
  "change_text": "We wanted those bones to serve as a promise to eventually show you the beast in its full glory and to be a motivator for us internally of what the game should eventually introduce.",
  "heading_path": [
    "How we Heralded it in HELLDIVERS 2"
  ],
  "entity": "How we Heralded it in HELLDIVERS 2",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1756,
  "source_span_end": 1935,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=Hulk` — `rv2_change_b4934120b3db8ff5408d334d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage on flamer attack
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage on flamer attack",
  "heading_path": [
    "Hulk"
  ],
  "entity": "Hulk",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9332,
  "source_span_end": 9373,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Hulk Bruiser` — `rv2_change_7edbc6c9a5c0112c06464477`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Rockets now deals increased damage vs Durable targets
```

Extracted fields:

```json
{
  "change_text": "Rockets now deals increased damage vs Durable targets",
  "heading_path": [
    "Hulk Bruiser"
  ],
  "entity": "Hulk Bruiser",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9925,
  "source_span_end": 9978,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Hunters` — `rv2_change_f3b445a13ca61ceda5cc0a2a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced durable damage of normal attack from 50 to 40
```

Extracted fields:

```json
{
  "change_text": "Reduced durable damage of normal attack from 50 to 40",
  "heading_path": [
    "Hunters"
  ],
  "entity": "Hunters",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "50",
  "new_value": "40",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 12635,
  "source_span_end": 12688,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Hunters` — `rv2_change_7f3804bdd55da4e223050ba6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced durable damage of pounce attack from 50 to 35
```

Extracted fields:

```json
{
  "change_text": "Reduced durable damage of pounce attack from 50 to 35",
  "heading_path": [
    "Hunters"
  ],
  "entity": "Hunters",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "50",
  "new_value": "35",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 12769,
  "source_span_end": 12822,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Illuminate` — `rv2_change_391b64df6a888b38417f02e6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Projectile damage was reduced from 1500 to 350.
```

Extracted fields:

```json
{
  "change_text": "Projectile damage was reduced from 1500 to 350.",
  "heading_path": [
    "Illuminate",
    "Leviathan"
  ],
  "entity": "Leviathan",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "1500",
  "new_value": "350.",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3114,
  "source_span_end": 3161,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Illuminate` — `rv2_change_cd8739a080202c2a7f9f0903`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced the frequency of Elevated Overseers spawning during Prevent Invasion Foothold missions
```

Extracted fields:

```json
{
  "change_text": "Reduced the frequency of Elevated Overseers spawning during Prevent Invasion Foothold missions",
  "heading_path": [
    "Illuminate",
    "Overseers"
  ],
  "entity": "Overseers",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2847,
  "source_span_end": 2941,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Illuminate Exostorms` — `rv2_change_e1ceac63cff0ee335a01722e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The strength of the storms can vary, with higher class storms presenting greater risk.
```

Extracted fields:

```json
{
  "change_text": "The strength of the storms can vary, with higher class storms presenting greater risk.",
  "heading_path": [
    "Illuminate Exostorms",
    "Planets in Illuminate space have been sieged by powerful Illuminate Exostorms, with high-intensity wind and lightning strikes."
  ],
  "entity": "Planets in Illuminate space have been sieged by powerful Illuminate Exostorms, with high-intensity wind and lightning strikes.",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2781,
  "source_span_end": 2867,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Illuminates` — `rv2_change_95542e5a607450b03f4f9bf8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage",
  "heading_path": [
    "Illuminates",
    "Fleshmobs"
  ],
  "entity": "Fleshmobs",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10414,
  "source_span_end": 10438,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Illuminates` — `rv2_change_551666f2dfdd1923014bc744`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Lower destruction strength needed to destroy it from 30 to 20
```

Extracted fields:

```json
{
  "change_text": "Lower destruction strength needed to destroy it from 30 to 20",
  "heading_path": [
    "Illuminates",
    "Tesla tower"
  ],
  "entity": "Tesla tower",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "30",
  "new_value": "20",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10491,
  "source_span_end": 10552,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Impaler` — `rv2_change_439c75094d2703a2a7724f79`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased stagger force needed from 45 to 50
```

Extracted fields:

```json
{
  "change_text": "Increased stagger force needed from 45 to 50",
  "heading_path": [
    "Impaler"
  ],
  "entity": "Impaler",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "45",
  "new_value": "50",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8447,
  "source_span_end": 8491,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=In multiple updates there have been hidden changes to weapons or enemies. Why were they not announced in patch notes?` — `rv2_change_f65c6ac5049906d0f68e3714`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We are also working on how we explain balance updates more clearly, especially when a change can have effects across multiple weapons, enemies, and gameplay systems.
```

Extracted fields:

```json
{
  "change_text": "We are also working on how we explain balance updates more clearly, especially when a change can have effects across multiple weapons, enemies, and gameplay systems.",
  "heading_path": [
    "In multiple updates there have been hidden changes to weapons or enemies. Why were they not announced in patch notes?"
  ],
  "entity": "In multiple updates there have been hidden changes to weapons or enemies. Why were they not announced in patch notes?",
  "aspect": "gameplay",
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1811,
  "source_span_end": 1976,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Increased level cap` — `rv2_change_6fb941a45f4bfcb01dfe121f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Level cap has been increased from 50 to 150
```

Extracted fields:

```json
{
  "change_text": "Level cap has been increased from 50 to 150",
  "heading_path": [
    "Increased level cap"
  ],
  "entity": "Increased level cap",
  "aspect": "map_or_level",
  "action": "increased",
  "direction": "increased",
  "previous_value": "50",
  "new_value": "150",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 535,
  "source_span_end": 578,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Introducing Supply Lines & Origin of Attacks` — `rv2_change_1fd41fee4e25c96bad82fed6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We have also updated visuals in the sector and planet info pop-ups
```

Extracted fields:

```json
{
  "change_text": "We have also updated visuals in the sector and planet info pop-ups.",
  "heading_path": [
    "Introducing Supply Lines & Origin of Attacks"
  ],
  "entity": "Introducing Supply Lines & Origin of Attacks",
  "aspect": "map_or_level",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 14320,
  "source_span_end": 14386,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=Is Helldivers 2 Steam Deck compatible?` — `rv2_change_58a50edc36897541b2991e34`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
If you'd like to complete this game on your Steam Deck, the experience has finally been adjusted to make it playable, but performance is still far off from where we would like it to be
```

Extracted fields:

```json
{
  "change_text": "If you'd like to complete this game on your Steam Deck, the experience has finally been adjusted to make it playable, but performance is still far off from where we would like it to be.",
  "heading_path": [
    "Is Helldivers 2 Steam Deck compatible?"
  ],
  "entity": "Is Helldivers 2 Steam Deck compatible?",
  "aspect": "performance_or_network",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 303,
  "source_span_end": 487,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=JAR-5 Dominator` — `rv2_change_55d104b055217ade652e43e8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage decreased from 300 to 275
```

Extracted fields:

```json
{
  "change_text": "Damage decreased from 300 to 275",
  "heading_path": [
    "JAR-5 Dominator"
  ],
  "entity": "JAR-5 Dominator",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "300",
  "new_value": "275",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3163,
  "source_span_end": 3195,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Key developments` — `rv2_change_a6f99425e6e559c26531461e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
In terms of performance, we’ve made some big changes under the hood to ensure a more responsive and optimized experience as you bring freedom and justice to Super Earth:
```

Extracted fields:

```json
{
  "change_text": "In terms of performance, we’ve made some big changes under the hood to ensure a more responsive and optimized experience as you bring freedom and justice to Super Earth:",
  "heading_path": [
    "Key developments"
  ],
  "entity": "Key developments",
  "aspect": "performance_or_network",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 908,
  "source_span_end": 1077,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Key developments` — `rv2_change_b0ebb0ef7227fa303286fe04`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We’ve improved our internal systems and teams—automated testing has gotten better and our Engine team has expanded to help us refine our processes for long-term stability and smoother gameplay
```

Extracted fields:

```json
{
  "change_text": "We’ve improved our internal systems and teams—automated testing has gotten better and our Engine team has expanded to help us refine our processes for long-term stability and smoother gameplay",
  "heading_path": [
    "Key developments"
  ],
  "entity": "Key developments",
  "aspect": "gameplay",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1208,
  "source_span_end": 1400,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Known Issues` — `rv2_change_6d6e7835e908b850ba2b4279`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
These are issues that were either introduced by this patch and are being worked on, or are from a previous version and have not yet been fixed.
```

Extracted fields:

```json
{
  "change_text": "These are issues that were either introduced by this patch and are being worked on, or are from a previous version and have not yet been fixed.",
  "heading_path": [
    "Known Issues"
  ],
  "entity": null,
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1321,
  "source_span_end": 1464,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Known Issues` — `rv2_change_20dfbc81c52bc2a051043182`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
These are issues that were either introduced by this patch and are being worked on, or are from a previous version and have not yet been fixed.
```

Extracted fields:

```json
{
  "change_text": "These are issues that were either introduced by this patch and are being worked on, or are from a previous version and have not yet been fixed.",
  "heading_path": [
    "Known Issues"
  ],
  "entity": null,
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1937,
  "source_span_end": 2080,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Known Issues (Same as last patch)` — `rv2_change_e7aea487e9f82078b79aebe0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
These are the highest priority issues that were either introduced by this patch and are being worked on, or are from a previous version and have not yet been fixed.
```

Extracted fields:

```json
{
  "change_text": "These are the highest priority issues that were either introduced by this patch and are being worked on, or are from a previous version and have not yet been fixed.",
  "heading_path": [
    "Known Issues (Same as last patch)"
  ],
  "entity": "Known Issues (Same as last patch)",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 507,
  "source_span_end": 671,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Known Issues (Unchanged from patch 1.000.200)` — `rv2_change_12c33be280a16edb9e105ea0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
These are issues that were either introduced by this patch and are being worked on, or are from a previous version and have not yet been fixed.
```

Extracted fields:

```json
{
  "change_text": "These are issues that were either introduced by this patch and are being worked on, or are from a previous version and have not yet been fixed.",
  "heading_path": [
    "Known Issues (Unchanged from patch 1.000.200)"
  ],
  "entity": "Known Issues (Unchanged from patch 1.000.200)",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 256,
  "source_span_end": 399,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Known issues` — `rv2_change_f5a1404244d768005adf0755`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Players added to the 'Recent Players' list will appear in the middle of the list.
```

Extracted fields:

```json
{
  "change_text": "Players added to the 'Recent Players' list will appear in the middle of the list.",
  "heading_path": [
    "Known issues"
  ],
  "entity": null,
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1562,
  "source_span_end": 1643,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Known issues` — `rv2_change_f057e9d50781076258f6567b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
These are issues that were either introduced by this patch and are being worked on, or are from a previous version and have not yet been fixed.
```

Extracted fields:

```json
{
  "change_text": "These are issues that were either introduced by this patch and are being worked on, or are from a previous version and have not yet been fixed.",
  "heading_path": [
    "Known issues"
  ],
  "entity": null,
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1267,
  "source_span_end": 1410,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=LAS-16 Sickle` — `rv2_change_ffb73a6cb096bcd9d04163a8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 55 to 60
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 55 to 60",
  "heading_path": [
    "LAS-16 Sickle"
  ],
  "entity": "LAS-16 Sickle",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "55",
  "new_value": "60",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4002,
  "source_span_end": 4032,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=LAS-16 Sickle` — `rv2_change_a65b3cef19da644a01d1513c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased amount of magazines from 6 down to 3
```

Extracted fields:

```json
{
  "change_text": "Decreased amount of magazines from 6 down to 3",
  "heading_path": [
    "LAS-16 Sickle"
  ],
  "entity": "LAS-16 Sickle",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "6",
  "new_value": "3",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2008,
  "source_span_end": 2054,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=LAS-5 Scythe` — `rv2_change_2215edc36d2c632ba316247a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased max number of mags from 6 down to 4
```

Extracted fields:

```json
{
  "change_text": "Decreased max number of mags from 6 down to 4",
  "heading_path": [
    "LAS-5 Scythe"
  ],
  "entity": "LAS-5 Scythe",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "6",
  "new_value": "4",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2131,
  "source_span_end": 2176,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=LAS-5 Scythe` — `rv2_change_b1ff5147cce9a157e82e2e8e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased damage from 300 to 350
```

Extracted fields:

```json
{
  "change_text": "Increased damage from 300 to 350",
  "heading_path": [
    "LAS-5 Scythe"
  ],
  "entity": "LAS-5 Scythe",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "300",
  "new_value": "350",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2094,
  "source_span_end": 2126,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=LAS-58 Talon` — `rv2_change_794b9764103825923bed1f7e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a visual effect issue when holding down the fire button
```

Extracted fields:

```json
{
  "change_text": "Fixed a visual effect issue when holding down the fire button",
  "heading_path": [
    "LAS-58 Talon"
  ],
  "entity": "LAS-58 Talon",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1357,
  "source_span_end": 1418,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=LAS-58 Talon` — `rv2_change_deb799a3f9736b113f94c758`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed an issue for not being able to reload without overheating
```

Extracted fields:

```json
{
  "change_text": "Fixed an issue for not being able to reload without overheating",
  "heading_path": [
    "LAS-58 Talon"
  ],
  "entity": "LAS-58 Talon",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "for not being able to reload without overheating",
  "source_span_start": 1179,
  "source_span_end": 1242,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=LAS-7 Dagger` — `rv2_change_ee6719535689f39ffda5f0ab`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased damage from 150 to 200
```

Extracted fields:

```json
{
  "change_text": "Increased damage from 150 to 200",
  "heading_path": [
    "LAS-7 Dagger"
  ],
  "entity": "LAS-7 Dagger",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "150",
  "new_value": "200",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2930,
  "source_span_end": 2962,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=LAS-7 Dagger` — `rv2_change_0d4fae5fa1dfba5d1dfe386e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased sway modifier from 1.2 to 1
```

Extracted fields:

```json
{
  "change_text": "Decreased sway modifier from 1.2 to 1",
  "heading_path": [
    "LAS-7 Dagger"
  ],
  "entity": "LAS-7 Dagger",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "1.2",
  "new_value": "1",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5137,
  "source_span_end": 5174,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=LAS-98 Laser Cannon` — `rv2_change_e5c414009dcb0fd59a0c07e3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Slightly reduced damage versus large volume bodies
```

Extracted fields:

```json
{
  "change_text": "Slightly reduced damage versus large volume bodies",
  "heading_path": [
    "LAS-98 Laser Cannon"
  ],
  "entity": "LAS-98 Laser Cannon",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1343,
  "source_span_end": 1393,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=LAS-98 Laser Cannon` — `rv2_change_68d27f2066fde6e7eb4fe8ad`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Slightly increased damage
```

Extracted fields:

```json
{
  "change_text": "Slightly increased damage",
  "heading_path": [
    "LAS-98 Laser Cannon"
  ],
  "entity": "LAS-98 Laser Cannon",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1313,
  "source_span_end": 1338,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=LAS-99 Quasar Cannon` — `rv2_change_ff5bada839e9dd997849bd5e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased recharge time by 5 seconds
```

Extracted fields:

```json
{
  "change_text": "Increased recharge time by 5 seconds",
  "heading_path": [
    "LAS-99 Quasar Cannon"
  ],
  "entity": "LAS-99 Quasar Cannon",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": 5.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 982,
  "source_span_end": 1018,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Let me update you on what we did so far with the latest patch being deployed` — `rv2_change_e52c7ffc634783594044cbda`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
To compensate for lost rewards, we are working on an increased reward event
```

Extracted fields:

```json
{
  "change_text": "To compensate for lost rewards, we are working on an increased reward event",
  "heading_path": [
    "Let me update you on what we did so far with the latest patch being deployed"
  ],
  "entity": "Let me update you on what we did so far with the latest patch being deployed",
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

### patch_change — `game=553850;section=Let me update you on what we did so far with the latest patch being deployed` — `rv2_change_c2fe1e55d52c2c8447ae2dbb`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Based on the testing we have done we believe we have fixed future mission rewards but will continue to monitor this closely as it is our top priority
```

Extracted fields:

```json
{
  "change_text": "Based on the testing we have done we believe we have fixed future mission rewards but will continue to monitor this closely as it is our top priority",
  "heading_path": [
    "Let me update you on what we did so far with the latest patch being deployed"
  ],
  "entity": "Let me update you on what we did so far with the latest patch being deployed",
  "aspect": "content_or_feature",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 703,
  "source_span_end": 852,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Level Cap Increased` — `rv2_change_014eecfb94616860c1680177`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We've expanded the Helldiver rank system beyond Level 150, adding 15 new ranks and titles that carry Helldivers all the way up to Level 300.
```

Extracted fields:

```json
{
  "change_text": "We've expanded the Helldiver rank system beyond Level 150, adding 15 new ranks and titles that carry Helldivers all the way up to Level 300.",
  "heading_path": [
    "Level Cap Increased"
  ],
  "entity": "Level Cap Increased",
  "aspect": "matchmaking_or_ranked",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2518,
  "source_span_end": 2658,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Light vs. Medium Penetration Weapons` — `rv2_change_e365dabff388d77eafff336f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Light penetration weapons generally deal a higher percentage of their total damage against durable enemies, differentiating them more clearly from medium penetration options
```

Extracted fields:

```json
{
  "change_text": "Light penetration weapons generally deal a higher percentage of their total damage against durable enemies, differentiating them more clearly from medium penetration options",
  "heading_path": [
    "Light vs. Medium Penetration Weapons"
  ],
  "entity": "Light vs. Medium Penetration Weapons",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1274,
  "source_span_end": 1447,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Long term` — `rv2_change_fc300f5643de2c9f5c0134ec`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Looking further into the future, we plan to make improvements to the engine which will ensure we never waste RAM loading common data that isn’t needed - eliminating one of the drawbacks of the above technique.
```

Extracted fields:

```json
{
  "change_text": "Looking further into the future, we plan to make improvements to the engine which will ensure we never waste RAM loading common data that isn’t needed - eliminating one of the drawbacks of the above technique.",
  "heading_path": [
    "Long term"
  ],
  "entity": "Long term",
  "aspect": null,
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5825,
  "source_span_end": 6034,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=M-102 Fast Recon Vehicle` — `rv2_change_922eb3d68713e26a6a158194`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased health of tires from 300 to 350
```

Extracted fields:

```json
{
  "change_text": "Increased health of tires from 300 to 350",
  "heading_path": [
    "M-102 Fast Recon Vehicle"
  ],
  "entity": "M-102 Fast Recon Vehicle",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": "300",
  "new_value": "350",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 11972,
  "source_span_end": 12013,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=M-102 Fast Recon Vehicle` — `rv2_change_83b49b645a24a6962921e751`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased health of doors by 50%
```

Extracted fields:

```json
{
  "change_text": "Increased health of doors by 50%",
  "heading_path": [
    "M-102 Fast Recon Vehicle"
  ],
  "entity": "M-102 Fast Recon Vehicle",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": 50.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 11926,
  "source_span_end": 11958,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=M-105 Stalwart` — `rv2_change_8d71c08a96c4953a193e8be7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 80 to 90
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 80 to 90",
  "heading_path": [
    "M-105 Stalwart"
  ],
  "entity": "M-105 Stalwart",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "80",
  "new_value": "90",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8055,
  "source_span_end": 8085,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=M-105 Stalwart` — `rv2_change_05da9d7c684fbb2b1bcde9c3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Durable damage increased from 15 to 22
```

Extracted fields:

```json
{
  "change_text": "Durable damage increased from 15 to 22",
  "heading_path": [
    "M-105 Stalwart"
  ],
  "entity": "M-105 Stalwart",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "15",
  "new_value": "22",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8099,
  "source_span_end": 8137,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=M6C/SOCOM` — `rv2_change_6c8b315fd9489cd426ad95b4`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Drag increased from 0.6 to 1.2
```

Extracted fields:

```json
{
  "change_text": "Drag increased from 0.6 to 1.2",
  "heading_path": [
    "M6C/SOCOM"
  ],
  "entity": "M6C/SOCOM",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "0.6",
  "new_value": "1.2",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5891,
  "source_span_end": 5921,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=M6C/SOCOM` — `rv2_change_ce01ee20ed2cb60557598bca`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 100 to 110
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 100 to 110",
  "heading_path": [
    "M6C/SOCOM"
  ],
  "entity": "M6C/SOCOM",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "100",
  "new_value": "110",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5845,
  "source_span_end": 5877,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=M6C/SOCOM Pistol` — `rv2_change_34a7b321d2bfdefb8df3a057`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage from  25 to 28
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage from  25 to 28",
  "heading_path": [
    "M6C/SOCOM Pistol"
  ],
  "entity": "M6C/SOCOM Pistol",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "25",
  "new_value": "28",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3077,
  "source_span_end": 3116,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=M6C/SOCOM Pistol` — `rv2_change_bcb87a2b5b5619a7b47c5003`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased damage from 110 to 125
```

Extracted fields:

```json
{
  "change_text": "Increased damage from 110 to 125",
  "heading_path": [
    "M6C/SOCOM Pistol"
  ],
  "entity": "M6C/SOCOM Pistol",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "110",
  "new_value": "125",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3031,
  "source_span_end": 3063,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=M7S SMG` — `rv2_change_57bd16999defbc146198766a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage from 16 to 18
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage from 16 to 18",
  "heading_path": [
    "M7S SMG"
  ],
  "entity": "M7S SMG",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "16",
  "new_value": "18",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2392,
  "source_span_end": 2430,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=M7S SMG` — `rv2_change_c3f5238de362997e91f9b18f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased sway modifier from 1.2 to 1
```

Extracted fields:

```json
{
  "change_text": "Decreased sway modifier from 1.2 to 1",
  "heading_path": [
    "M7S SMG"
  ],
  "entity": "M7S SMG",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "1.2",
  "new_value": "1",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4293,
  "source_span_end": 4330,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=M90A Shotgun` — `rv2_change_98a13bfaa1181ea99fcdc099`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage 15 to 20
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage 15 to 20",
  "heading_path": [
    "M90A Shotgun"
  ],
  "entity": "M90A Shotgun",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2571,
  "source_span_end": 2604,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=MA5C Assault Rifle` — `rv2_change_f244f0b30c218b98b13d885b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 80 to 90
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 80 to 90",
  "heading_path": [
    "MA5C Assault Rifle"
  ],
  "entity": "MA5C Assault Rifle",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "80",
  "new_value": "90",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4141,
  "source_span_end": 4171,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=MATCHMAKING` — `rv2_change_61adfaa84bdf3bee28b44e8e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Improved lobby sorting to increase chance of connectivity.
```

Extracted fields:

```json
{
  "change_text": "Improved lobby sorting to increase chance of connectivity.",
  "heading_path": [
    "MATCHMAKING"
  ],
  "entity": "MATCHMAKING",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1070,
  "source_span_end": 1128,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=MATCHMAKING` — `rv2_change_ac6775bc67e69766501276c5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed an issue that caused us to send invalid data to multiplayer services.
```

Extracted fields:

```json
{
  "change_text": "Fixed an issue that caused us to send invalid data to multiplayer services.",
  "heading_path": [
    "MATCHMAKING"
  ],
  "entity": "MATCHMAKING",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "that caused us to send invalid data to multiplayer services",
  "source_span_start": 990,
  "source_span_end": 1065,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=MD-6 Anti-Personnel Minefield` — `rv2_change_0ef0e0fb319d8f4bc702d42f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased explosion damage from 250 to 350
```

Extracted fields:

```json
{
  "change_text": "Increased explosion damage from 250 to 350",
  "heading_path": [
    "MD-6 Anti-Personnel Minefield"
  ],
  "entity": "MD-6 Anti-Personnel Minefield",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "250",
  "new_value": "350",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2162,
  "source_span_end": 2204,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=MD-I4 Incendiary Mines` — `rv2_change_91a46cc99fb00d9d2134b61b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased explosion damage from 150 to 210
```

Extracted fields:

```json
{
  "change_text": "Increased explosion damage from 150 to 210",
  "heading_path": [
    "MD-I4 Incendiary Mines"
  ],
  "entity": "MD-I4 Incendiary Mines",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "150",
  "new_value": "210",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2254,
  "source_span_end": 2296,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=MG-206 Heavy Machine Gun` — `rv2_change_4005e39f220a244af27f0c41`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased reload time from 7 to 5.5 sec
```

Extracted fields:

```json
{
  "change_text": "Decreased reload time from 7 to 5.5 sec",
  "heading_path": [
    "MG-206 Heavy Machine Gun"
  ],
  "entity": "MG-206 Heavy Machine Gun",
  "aspect": "cooldown_or_timing",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "7",
  "new_value": "5.5 sec",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3780,
  "source_span_end": 3819,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=MG-206 Heavy Machine Gun` — `rv2_change_e18711de5bc7634d33759778`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased projectile damage against durable* body parts from 23% to 33%
```

Extracted fields:

```json
{
  "change_text": "Increased projectile damage against durable* body parts from 23% to 33%",
  "heading_path": [
    "MG-206 Heavy Machine Gun"
  ],
  "entity": "MG-206 Heavy Machine Gun",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "23%",
  "new_value": "33%",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3648,
  "source_span_end": 3719,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=MG-43 Machine Gun` — `rv2_change_7d9f46d0e3ec3d281a30cdf8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased max amount of Magazines from 3 to 4
```

Extracted fields:

```json
{
  "change_text": "Increased max amount of Magazines from 3 to 4",
  "heading_path": [
    "MG-43 Machine Gun"
  ],
  "entity": "MG-43 Machine Gun",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "3",
  "new_value": "4",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3943,
  "source_span_end": 3988,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=MG-43 Machine Gun` — `rv2_change_c865efbd9d61c99d2a759632`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased reload time from 4 to 3.5 seconds
```

Extracted fields:

```json
{
  "change_text": "Decreased reload time from 4 to 3.5 seconds",
  "heading_path": [
    "MG-43 Machine Gun"
  ],
  "entity": "MG-43 Machine Gun",
  "aspect": "cooldown_or_timing",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "4",
  "new_value": "3.5 seconds",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3895,
  "source_span_end": 3938,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=MG-43 Machine Gun, A/MG-43 Machine gun Sentry, A/G-16 Gatling Sentry and EXO-45 Patriot Exosuits Gatling` — `rv2_change_109507ab21f526b5d2a52355`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased projectile damage from 80 to 90
```

Extracted fields:

```json
{
  "change_text": "Increased projectile damage from 80 to 90",
  "heading_path": [
    "MG-43 Machine Gun, A/MG-43 Machine gun Sentry, A/G-16 Gatling Sentry and EXO-45 Patriot Exosuits Gatling"
  ],
  "entity": "MG-43 Machine Gun, A/MG-43 Machine gun Sentry, A/G-16 Gatling Sentry and EXO-45 Patriot Exosuits Gatling",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "80",
  "new_value": "90",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4120,
  "source_span_end": 4161,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=MG-43 Machine Gun, A/MG-43 Machine gun Sentry, A/G-16 Gatling Sentry and EXO-45 Patriot Exosuits Gatling` — `rv2_change_e13eb3ca66df4e6065f2f781`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased projectile damage against durable* body parts from 7.5% to 25%
```

Extracted fields:

```json
{
  "change_text": "Increased projectile damage against durable* body parts from 7.5% to 25%",
  "heading_path": [
    "MG-43 Machine Gun, A/MG-43 Machine gun Sentry, A/G-16 Gatling Sentry and EXO-45 Patriot Exosuits Gatling"
  ],
  "entity": "MG-43 Machine Gun, A/MG-43 Machine gun Sentry, A/G-16 Gatling Sentry and EXO-45 Patriot Exosuits Gatling",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "7.5%",
  "new_value": "25%",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4165,
  "source_span_end": 4237,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=MG-43 Machine Gun, A/MG-43 Machine gun Sentry, A/G-16 Gatling Sentry, EXO-45 Patriot Exosuits Gatling` — `rv2_change_35d5cbc31d754b75ee3916f0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The family of machine gun stratagems that used the 8mm rifle round were underperforming slightly and we have therefore increased the damage slightly.
```

Extracted fields:

```json
{
  "change_text": "The family of machine gun stratagems that used the 8mm rifle round were underperforming slightly and we have therefore increased the damage slightly.",
  "heading_path": [
    "MG-43 Machine Gun, A/MG-43 Machine gun Sentry, A/G-16 Gatling Sentry, EXO-45 Patriot Exosuits Gatling"
  ],
  "entity": "MG-43 Machine Gun, A/MG-43 Machine gun Sentry, A/G-16 Gatling Sentry, EXO-45 Patriot Exosuits Gatling",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6887,
  "source_span_end": 7036,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=MP-98 Knight` — `rv2_change_e425f9f42198e375f8624171`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased sway modifier from 1.2 to 1
```

Extracted fields:

```json
{
  "change_text": "Decreased sway modifier from 1.2 to 1",
  "heading_path": [
    "MP-98 Knight"
  ],
  "entity": "MP-98 Knight",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "1.2",
  "new_value": "1",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4022,
  "source_span_end": 4059,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=MP-98 Knight` — `rv2_change_75834dc7edc5b05b9f46b3bc`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 70 to 90
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 70 to 90",
  "heading_path": [
    "MP-98 Knight"
  ],
  "entity": "MP-98 Knight",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "70",
  "new_value": "90",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3446,
  "source_span_end": 3476,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=MS-11 Solo Silo` — `rv2_change_6420601f19c571accf04c34a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced cooldown from 210 seconds to 180 seconds
```

Extracted fields:

```json
{
  "change_text": "Reduced cooldown from 210 seconds to 180 seconds",
  "heading_path": [
    "MS-11 Solo Silo"
  ],
  "entity": "MS-11 Solo Silo",
  "aspect": "cooldown_or_timing",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "210 seconds",
  "new_value": "180 seconds",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 250,
  "source_span_end": 298,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=MS-11 Solo Silo` — `rv2_change_20d411de79c05c951b61bb12`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Health increased from 800 to 1500
```

Extracted fields:

```json
{
  "change_text": "Health increased from 800 to 1500",
  "heading_path": [
    "MS-11 Solo Silo"
  ],
  "entity": "MS-11 Solo Silo",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": "800",
  "new_value": "1500",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8852,
  "source_span_end": 8885,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Magazines` — `rv2_change_04f6265b93f11d3c4fab8b2b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Spare magazines increased from 2 to 3
```

Extracted fields:

```json
{
  "change_text": "Spare magazines increased from 2 to 3",
  "heading_path": [
    "Magazines"
  ],
  "entity": "Magazines",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "2",
  "new_value": "3",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3030,
  "source_span_end": 3067,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Magazines` — `rv2_change_b2ddbaa4951d7177b72ee42c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Starting magazines increased from 1 to 2
```

Extracted fields:

```json
{
  "change_text": "Starting magazines increased from 1 to 2",
  "heading_path": [
    "Magazines"
  ],
  "entity": "Magazines",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "1",
  "new_value": "2",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2985,
  "source_span_end": 3025,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Main Body` — `rv2_change_52ff8f81c48dd15b6289e031`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Armor increased from 1 → 2
```

Extracted fields:

```json
{
  "change_text": "Armor increased from 1 → 2",
  "heading_path": [
    "Main Body"
  ],
  "entity": "Main Body",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 311,
  "source_span_end": 337,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Main Body` — `rv2_change_05d454081aad62f8893b6539`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Health increased from 375 → 500
```

Extracted fields:

```json
{
  "change_text": "Health increased from 375 → 500",
  "heading_path": [
    "Main Body"
  ],
  "entity": "Main Body",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 344,
  "source_span_end": 375,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Major Updates` — `rv2_change_a4b5b199e756e207283ca3b7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
To address this, we've reworked armor penetration, anti-tank weapons, enemy armor and health values.
```

Extracted fields:

```json
{
  "change_text": "To address this, we've reworked armor penetration, anti-tank weapons, enemy armor and health values.",
  "heading_path": [
    "Major Updates"
  ],
  "entity": "Major Updates",
  "aspect": "health_or_durability",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1071,
  "source_span_end": 1171,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Major Updates` — `rv2_change_3181c0a3261edcfb572b1bf5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
On the Bot front, Hulks have also had their armor reduced, making them more vulnerable to a wider range of weapons.
```

Extracted fields:

```json
{
  "change_text": "On the Bot front, Hulks have also had their armor reduced, making them more vulnerable to a wider range of weapons.",
  "heading_path": [
    "Major Updates"
  ],
  "entity": "Major Updates",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1531,
  "source_span_end": 1646,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Matchmaking` — `rv2_change_45c94163c9bbd9e4098cf19c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
These are issues that were either introduced by this patch and are being worked on, or are from a previous version and have not yet been fixed.
```

Extracted fields:

```json
{
  "change_text": "These are issues that were either introduced by this patch and are being worked on, or are from a previous version and have not yet been fixed.",
  "heading_path": [
    "Matchmaking",
    "Stability and crashes"
  ],
  "entity": "Stability and crashes",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 985,
  "source_span_end": 1128,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Matchmaking` — `rv2_change_99f67657058b6a8e9da06587`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Playfab environment optimized - All lobbies now have proper data to run more effective matchmaking
```

Extracted fields:

```json
{
  "change_text": "Playfab environment optimized - All lobbies now have proper data to run more effective matchmaking",
  "heading_path": [
    "Matchmaking",
    "Playfab optimization"
  ],
  "entity": "Playfab optimization",
  "aspect": "matchmaking_or_ranked",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 341,
  "source_span_end": 439,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Matchmaking & Connection Issues` — `rv2_change_8bd3c58814707220e46b3a8b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Addressed an issue which forced disconnections in specific gameplay conditions during Illuminate missions
```

Extracted fields:

```json
{
  "change_text": "Addressed an issue which forced disconnections in specific gameplay conditions during Illuminate missions",
  "heading_path": [
    "Matchmaking & Connection Issues"
  ],
  "entity": "Matchmaking & Connection Issues",
  "aspect": "gameplay",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 338,
  "source_span_end": 443,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Medium Priority` — `rv2_change_98e7ba6ecce37f489f5b2c09`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Higher zoom functions do not zoom the camera in through the scope on the LAS-5 Scythe
```

Extracted fields:

```json
{
  "change_text": "Higher zoom functions do not zoom the camera in through the scope on the LAS-5 Scythe",
  "heading_path": [
    "Medium Priority"
  ],
  "entity": "Medium Priority",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10067,
  "source_span_end": 10152,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Medium Priority` — `rv2_change_7d8192a6ed8f906dbdc68ccf`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Firebomb Hellpods can no longer destroy larger enemy types such as tanks
```

Extracted fields:

```json
{
  "change_text": "Firebomb Hellpods can no longer destroy larger enemy types such as tanks",
  "heading_path": [
    "Medium Priority"
  ],
  "entity": "Medium Priority",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3249,
  "source_span_end": 3321,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Melee Weapons and Throwables` — `rv2_change_f754b2a76b80387ac1bc2cab`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Melee weapons and throwables have been improved to make each feel more impactful and unique in their function
```

Extracted fields:

```json
{
  "change_text": "Melee weapons and throwables have been improved to make each feel more impactful and unique in their function",
  "heading_path": [
    "Melee Weapons and Throwables"
  ],
  "entity": "Melee Weapons and Throwables",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1774,
  "source_span_end": 1883,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Misc` — `rv2_change_21f4860f023fbf3b42d8ed1f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed an issue where a Helldiver using a terminal could appear to other players to be facing the wrong direction
```

Extracted fields:

```json
{
  "change_text": "Fixed an issue where a Helldiver using a terminal could appear to other players to be facing the wrong direction",
  "heading_path": [
    "Misc"
  ],
  "entity": null,
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "a Helldiver using a terminal could appear to other players to be facing the wrong direction",
  "source_span_start": 9897,
  "source_span_end": 10009,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Misc` — `rv2_change_c082db921ce24104de30b1a9`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed enemy traversal issues in one of the hive world oil pump objectives
```

Extracted fields:

```json
{
  "change_text": "Fixed enemy traversal issues in one of the hive world oil pump objectives",
  "heading_path": [
    "Misc"
  ],
  "entity": null,
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10691,
  "source_span_end": 10764,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Misc Fixes` — `rv2_change_f203a79ee59365f0b73b9f92`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed issue where Spore Spewer would appear purple on certain planets.
```

Extracted fields:

```json
{
  "change_text": "Fixed issue where Spore Spewer would appear purple on certain planets.",
  "heading_path": [
    "Misc Fixes"
  ],
  "entity": "Misc Fixes",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "Spore Spewer would appear purple on certain planets",
  "source_span_start": 876,
  "source_span_end": 946,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Misc Fixes` — `rv2_change_7d417f3fe8095c515c3da3a5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Improved performance on PS5 when CPU bound
```

Extracted fields:

```json
{
  "change_text": "Improved performance on PS5 when CPU bound",
  "heading_path": [
    "Misc Fixes"
  ],
  "entity": "Misc Fixes",
  "aspect": "performance_or_network",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2916,
  "source_span_end": 2958,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Misc weapon fixes` — `rv2_change_505676cefda501667525cb8d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a bug where weapons would be held sideways after interrupting a stratagem with a stim heal.
```

Extracted fields:

```json
{
  "change_text": "Fixed a bug where weapons would be held sideways after interrupting a stratagem with a stim heal.",
  "heading_path": [
    "Misc weapon fixes"
  ],
  "entity": "Misc weapon fixes",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "after interrupting a stratagem with a stim heal",
  "bug_symptom": "weapons would be held sideways",
  "source_span_start": 6105,
  "source_span_end": 6202,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Misc weapon fixes` — `rv2_change_8dd331bcd38e02335f98771d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added in missing haptics when firing the AR-61 Tenderizer.
```

Extracted fields:

```json
{
  "change_text": "Added in missing haptics when firing the AR-61 Tenderizer.",
  "heading_path": [
    "Misc weapon fixes"
  ],
  "entity": "Misc weapon fixes",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6563,
  "source_span_end": 6621,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Miscellaneous` — `rv2_change_5c6158a75e79b74fc79c1be8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed mesh clipping for the arms on some animations
```

Extracted fields:

```json
{
  "change_text": "Fixed mesh clipping for the arms on some animations",
  "heading_path": [
    "Miscellaneous"
  ],
  "entity": null,
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 16246,
  "source_span_end": 16297,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Miscellaneous` — `rv2_change_a07a06f63bb660d6367dd6ee`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a bug where Hive Lord body parts would not spawn properly
```

Extracted fields:

```json
{
  "change_text": "Fixed a bug where Hive Lord body parts would not spawn properly",
  "heading_path": [
    "Miscellaneous"
  ],
  "entity": null,
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "Hive Lord body parts would not spawn properly",
  "source_span_start": 15743,
  "source_span_end": 15806,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Miscellaneous Fixes` — `rv2_change_4366ef1854c06ab2476064f4`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a bug where the Helldivers head twitched in the end screen, before and after using Victory Poses
```

Extracted fields:

```json
{
  "change_text": "Fixed a bug where the Helldivers head twitched in the end screen, before and after using Victory Poses",
  "heading_path": [
    "Miscellaneous Fixes"
  ],
  "entity": "Miscellaneous Fixes",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "after using Victory Poses",
  "bug_symptom": "the Helldivers head twitched in the end screen, before and",
  "source_span_start": 13119,
  "source_span_end": 13221,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Miscellaneous Fixes` — `rv2_change_9fe949be2d9070765df407d7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed strange movement after falling while marching
```

Extracted fields:

```json
{
  "change_text": "Fixed strange movement after falling while marching",
  "heading_path": [
    "Miscellaneous Fixes"
  ],
  "entity": "Miscellaneous Fixes",
  "aspect": "speed_or_movement",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6252,
  "source_span_end": 6303,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Miscellaneous fixes` — `rv2_change_694f243304bbd586cb4b48e6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed effects tab sometimes showing scrambled.
```

Extracted fields:

```json
{
  "change_text": "Fixed effects tab sometimes showing scrambled.",
  "heading_path": [
    "Miscellaneous fixes"
  ],
  "entity": "Miscellaneous fixes",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 11295,
  "source_span_end": 11341,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Miscellaneous fixes` — `rv2_change_55c16264239bd64a5d11de0b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced the intensity of the Experimental Infusion booster visual effect.
```

Extracted fields:

```json
{
  "change_text": "Reduced the intensity of the Experimental Infusion booster visual effect.",
  "heading_path": [
    "Miscellaneous fixes"
  ],
  "entity": "Miscellaneous fixes",
  "aspect": "visuals_or_graphics",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8062,
  "source_span_end": 8135,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Missions` — `rv2_change_fd34392492d597dbf8c21e6b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed an issue where horde missions would spawn at Difficulties lower than 5, which would break some functionality.
```

Extracted fields:

```json
{
  "change_text": "Fixed an issue where horde missions would spawn at Difficulties lower than 5, which would break some functionality.",
  "heading_path": [
    "Missions"
  ],
  "entity": "Missions",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "horde missions would spawn at Difficulties lower than 5, which would break some functionality",
  "source_span_start": 2546,
  "source_span_end": 2661,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Missions` — `rv2_change_cd6cfcb4ed95a2324d493c66`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Miscellaneous Fixes
```

Extracted fields:

```json
{
  "change_text": "Miscellaneous Fixes",
  "heading_path": [
    "Missions",
    "Enemies"
  ],
  "entity": "Enemies",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10630,
  "source_span_end": 10649,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=New Enemies & Dangerous Swamps` — `rv2_change_67a658e994b213c59cbf307d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
No longer can you run from the bugs when the Impaler is around–big, imposing, and destructive, it demands to be dealt with
```

Extracted fields:

```json
{
  "change_text": "No longer can you run from the bugs when the Impaler is around–big, imposing, and destructive, it demands to be dealt with.",
  "heading_path": [
    "New Enemies & Dangerous Swamps"
  ],
  "entity": "New Enemies & Dangerous Swamps",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3052,
  "source_span_end": 3174,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=New environmental hazards` — `rv2_change_d49b20931a02a2265615e869`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Acid Storms - Temporarily lowers armor for enemies and the player.
```

Extracted fields:

```json
{
  "change_text": "Acid Storms - Temporarily lowers armor for enemies and the player.",
  "heading_path": [
    "New environmental hazards"
  ],
  "entity": "New environmental hazards",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2462,
  "source_span_end": 2528,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Note` — `rv2_change_cb0208e3b07e28e5b780ede2`

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
    "Note",
    "We recognize that changes in this area could have a significant impact on the player experience, both positively and negatively, so we are moving forward cautiously. While we are more certain about some changes, others require further thought. These are the adjustments we are currently testing"
  ],
  "entity": "We recognize that changes in this area could have a significant impact on the player experience, both positively and negatively, so we are moving forward cautiously. While we are more certain about some changes, others require further thought. These are the adjustments we are currently testing",
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

### patch_change — `game=553850;section=Optimizations` — `rv2_change_07d860a79c7b0d349016e06e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Optimized Dragonroach fire attack VFX
```

Extracted fields:

```json
{
  "change_text": "Optimized Dragonroach fire attack VFX",
  "heading_path": [
    "Optimizations"
  ],
  "entity": "Optimizations",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 19303,
  "source_span_end": 19340,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Optimizations` — `rv2_change_89fff460eee72914564fdb82`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Optimized asset distribution in Hiveworlds and Terminid caves
```

Extracted fields:

```json
{
  "change_text": "Optimized asset distribution in Hiveworlds and Terminid caves",
  "heading_path": [
    "Optimizations"
  ],
  "entity": "Optimizations",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 18903,
  "source_span_end": 18964,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Orbital 120mm HE Barrage` — `rv2_change_aa08e1f730681fc63dc4b5b1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased cooldown from 240s to 180s
```

Extracted fields:

```json
{
  "change_text": "Decreased cooldown from 240s to 180s",
  "heading_path": [
    "Orbital 120mm HE Barrage"
  ],
  "entity": "Orbital 120mm HE Barrage",
  "aspect": "cooldown_or_timing",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "240s",
  "new_value": "180s",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3313,
  "source_span_end": 3349,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital 120mm HE Barrage` — `rv2_change_6e4f4ad07a3a95632ff81d01`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased explosion damage 750 to 1200
```

Extracted fields:

```json
{
  "change_text": "Increased explosion damage 750 to 1200",
  "heading_path": [
    "Orbital 120mm HE Barrage"
  ],
  "entity": "Orbital 120mm HE Barrage",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10782,
  "source_span_end": 10820,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital 380mm HE Barrage` — `rv2_change_fcc942158ee40b7236ee21be`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased explosion damage 1000 to 1500
```

Extracted fields:

```json
{
  "change_text": "Increased explosion damage 1000 to 1500",
  "heading_path": [
    "Orbital 380mm HE Barrage"
  ],
  "entity": "Orbital 380mm HE Barrage",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9893,
  "source_span_end": 9932,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital 380mm HE Barrage` — `rv2_change_51191e6e17a2c149011b52fd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased projectile durable damage 3500 to 4000
```

Extracted fields:

```json
{
  "change_text": "Increased projectile durable damage 3500 to 4000",
  "heading_path": [
    "Orbital 380mm HE Barrage"
  ],
  "entity": "Orbital 380mm HE Barrage",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9831,
  "source_span_end": 9879,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital Airburst Strike` — `rv2_change_cee5212bcc2a9866f8325b6c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased cooldown from 120 sec to 100 sec
```

Extracted fields:

```json
{
  "change_text": "Decreased cooldown from 120 sec to 100 sec",
  "heading_path": [
    "Orbital Airburst Strike"
  ],
  "entity": "Orbital Airburst Strike",
  "aspect": "cooldown_or_timing",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "120 sec",
  "new_value": "100 sec",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2719,
  "source_span_end": 2761,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital Airburst Strike` — `rv2_change_e6a79b1a57914568dbf7ee7e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
To make it a more attractive option we lowered the cooldown which should also make it more competitive in comparison to Eagle stratagems.
```

Extracted fields:

```json
{
  "change_text": "To make it a more attractive option we lowered the cooldown which should also make it more competitive in comparison to Eagle stratagems.",
  "heading_path": [
    "Orbital Airburst Strike"
  ],
  "entity": "Orbital Airburst Strike",
  "aspect": "cooldown_or_timing",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3981,
  "source_span_end": 4118,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital E.M.S` — `rv2_change_c425579134178a133eb5b418`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased Projectile Damage 250 → 300
```

Extracted fields:

```json
{
  "change_text": "Increased Projectile Damage 250 → 300",
  "heading_path": [
    "Orbital E.M.S"
  ],
  "entity": "Orbital E.M.S",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3132,
  "source_span_end": 3169,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital E.M.S` — `rv2_change_799530dcd76f896a37669117`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased Projectile Demolition strength 30 → 50
```

Extracted fields:

```json
{
  "change_text": "Increased Projectile Demolition strength 30 → 50",
  "heading_path": [
    "Orbital E.M.S"
  ],
  "entity": "Orbital E.M.S",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3227,
  "source_span_end": 3275,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Orbital Gatling` — `rv2_change_fed4127db24a9df9a9b4aa5a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased armor penetration (Can damage heavy armored enemies)
```

Extracted fields:

```json
{
  "change_text": "Increased armor penetration (Can damage heavy armored enemies)",
  "heading_path": [
    "Orbital Gatling"
  ],
  "entity": "Orbital Gatling",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2415,
  "source_span_end": 2477,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital Gatling` — `rv2_change_49e84ed46c45944977be9989`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased rounds per salvo from 30 to 60
```

Extracted fields:

```json
{
  "change_text": "Increased rounds per salvo from 30 to 60",
  "heading_path": [
    "Orbital Gatling"
  ],
  "entity": "Orbital Gatling",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "30",
  "new_value": "60",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2370,
  "source_span_end": 2410,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Orbital Precision Strike` — `rv2_change_062dd2078dff87af1cc3d37f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased projectile damage 3500 to 4000
```

Extracted fields:

```json
{
  "change_text": "Increased projectile damage 3500 to 4000",
  "heading_path": [
    "Orbital Precision Strike"
  ],
  "entity": "Orbital Precision Strike",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9488,
  "source_span_end": 9528,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital Precision Strike` — `rv2_change_3841ba3a2b38e02ed58f275e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The Orbital Precision Strikes original intent was to be used against spawners and fixed positions.
```

Extracted fields:

```json
{
  "change_text": "The Orbital Precision Strikes original intent was to be used against spawners and fixed positions.",
  "heading_path": [
    "Orbital Precision Strike"
  ],
  "entity": "Orbital Precision Strike",
  "aspect": "accuracy_or_spread",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3223,
  "source_span_end": 3321,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital Precision strike` — `rv2_change_3c11ca3293fe23c4b1425420`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased cooldown from 100 sec to 90 sec
```

Extracted fields:

```json
{
  "change_text": "Decreased cooldown from 100 sec to 90 sec",
  "heading_path": [
    "Orbital Precision strike"
  ],
  "entity": "Orbital Precision strike",
  "aspect": "cooldown_or_timing",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "100 sec",
  "new_value": "90 sec",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2574,
  "source_span_end": 2615,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital Precision strike` — `rv2_change_2698a50618df23666623dfa9`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased Spawn/Call-in time from 4 sec to 2 sec
```

Extracted fields:

```json
{
  "change_text": "Decreased Spawn/Call-in time from 4 sec to 2 sec",
  "heading_path": [
    "Orbital Precision strike"
  ],
  "entity": "Orbital Precision strike",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "4 sec",
  "new_value": "2 sec",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2620,
  "source_span_end": 2668,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Orbital Railcannon Strike` — `rv2_change_1381883847d530d9bc1370fc`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Cooldown decreased from 210 to 180 sec
```

Extracted fields:

```json
{
  "change_text": "Cooldown decreased from 210 to 180 sec",
  "heading_path": [
    "Orbital Railcannon Strike"
  ],
  "entity": "Orbital Railcannon Strike",
  "aspect": "cooldown_or_timing",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "210",
  "new_value": "180 sec",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9055,
  "source_span_end": 9093,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital Railcannon Strike` — `rv2_change_ea06cd2c74df7db3e8b8f730`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased projectile damage 7500 to 10 000
```

Extracted fields:

```json
{
  "change_text": "Increased projectile damage 7500 to 10 000",
  "heading_path": [
    "Orbital Railcannon Strike"
  ],
  "entity": "Orbital Railcannon Strike",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10946,
  "source_span_end": 10988,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital Walking Barrage` — `rv2_change_f7082b6bfd4fef2723d05dea`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased explosion damage 1000 to 1500
```

Extracted fields:

```json
{
  "change_text": "Increased explosion damage 1000 to 1500",
  "heading_path": [
    "Orbital Walking Barrage"
  ],
  "entity": "Orbital Walking Barrage",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10189,
  "source_span_end": 10228,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital Walking Barrage` — `rv2_change_e42ef3ddd45e6e1b728e3805`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased projectile damage 3500 to 4000
```

Extracted fields:

```json
{
  "change_text": "Increased projectile damage 3500 to 4000",
  "heading_path": [
    "Orbital Walking Barrage"
  ],
  "entity": "Orbital Walking Barrage",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10073,
  "source_span_end": 10113,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital smoke` — `rv2_change_2a31122cf52e3bde90f7b9fe`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased Projectile Damage  0 → 300
```

Extracted fields:

```json
{
  "change_text": "Increased Projectile Damage  0 → 300",
  "heading_path": [
    "Orbital smoke"
  ],
  "entity": "Orbital smoke",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2936,
  "source_span_end": 2972,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Orbital smoke` — `rv2_change_05ab766b168340035224fc88`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased Projectile AP 0 → 7
```

Extracted fields:

```json
{
  "change_text": "Increased Projectile AP 0 → 7",
  "heading_path": [
    "Orbital smoke"
  ],
  "entity": "Orbital smoke",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2987,
  "source_span_end": 3016,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Orbitals damage rebalance` — `rv2_change_34d007b2fd8c8719295ef6ee`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Larger projectiles explosions like the 380mm and 120mm are increased to make close hits more effective vs larger enemies like Chargers.
```

Extracted fields:

```json
{
  "change_text": "Larger projectiles explosions like the 380mm and 120mm are increased to make close hits more effective vs larger enemies like Chargers.",
  "heading_path": [
    "Orbitals damage rebalance"
  ],
  "entity": "Orbitals damage rebalance",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6128,
  "source_span_end": 6263,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Other` — `rv2_change_d32c04e49749668137040167`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Total purchased counter on the right side of the Robotics Workshop section no longer displays 7 / 8 despite all stratagems being purchased
```

Extracted fields:

```json
{
  "change_text": "Total purchased counter on the right side of the Robotics Workshop section no longer displays 7 / 8 despite all stratagems being purchased",
  "heading_path": [
    "Other"
  ],
  "entity": "Other",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3441,
  "source_span_end": 3579,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Other` — `rv2_change_0b7afb0761c7d933b91427bd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated Recoil stance modifiers: We made changes to the recoil stance modifiers to make them more consistent and also reward being prone more. Almost all of them will improve the recoil and only a two have been made worse (and only by 10%).
```

Extracted fields:

```json
{
  "change_text": "Updated Recoil stance modifiers: We made changes to the recoil stance modifiers to make them more consistent and also reward being prone more. Almost all of them will improve the recoil and only a two have been made worse (and only by 10%).",
  "heading_path": [
    "Other"
  ],
  "entity": "Other",
  "aspect": "accuracy_or_spread",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": 10.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5694,
  "source_span_end": 5934,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Other Fixes` — `rv2_change_d1d5ecc7aad61ead77ce5304`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed hang that could occur while navigating the social menu.
```

Extracted fields:

```json
{
  "change_text": "Fixed hang that could occur while navigating the social menu.",
  "heading_path": [
    "Other Fixes"
  ],
  "entity": "Other Fixes",
  "aspect": "interface_or_settings",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1149,
  "source_span_end": 1210,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Other Fixes` — `rv2_change_a25d390b8f91c94fdde1f6f3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Picking up Medals and Super Credits will no longer lock the player in place.
```

Extracted fields:

```json
{
  "change_text": "Picking up Medals and Super Credits will no longer lock the player in place.",
  "heading_path": [
    "Other Fixes"
  ],
  "entity": "Other Fixes",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1215,
  "source_span_end": 1291,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Our aim within the next 60 days` — `rv2_change_af2a5a9fe39f1d93806b52ae`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Re-prioritize bug fixes so that the more immediate  gameplay-impacting bugs are prioritized.
```

Extracted fields:

```json
{
  "change_text": "Re-prioritize bug fixes so that the more immediate  gameplay-impacting bugs are prioritized.",
  "heading_path": [
    "Our aim within the next 60 days"
  ],
  "entity": "Our aim within the next 60 days",
  "aspect": "gameplay",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1188,
  "source_span_end": 1280,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Our commitment to You moving forward` — `rv2_change_8ba965a069b13cc5fff2c9c6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
As we keep building this game, we are committed to keeping the lines of communication open through regular player surveys, improved patch notes, and more frequent updates via blog posts and streams.
```

Extracted fields:

```json
{
  "change_text": "As we keep building this game, we are committed to keeping the lines of communication open through regular player surveys, improved patch notes, and more frequent updates via blog posts and streams.",
  "heading_path": [
    "Our commitment to You moving forward"
  ],
  "entity": "Our commitment to You moving forward",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1459,
  "source_span_end": 1657,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Overseer` — `rv2_change_8f68b2ac5d885e22ca97adcd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Overseer`s weapon now deals increased damage vs Durable targets
```

Extracted fields:

```json
{
  "change_text": "Overseer`s weapon now deals increased damage vs Durable targets",
  "heading_path": [
    "Overseer"
  ],
  "entity": "Overseer",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10256,
  "source_span_end": 10319,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Overseer variants` — `rv2_change_a0bd110264c29376aec44401`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Unarmored Torso healthzone armor decreased from 2 to 1
```

Extracted fields:

```json
{
  "change_text": "Unarmored Torso healthzone armor decreased from 2 to 1",
  "heading_path": [
    "Overseer variants"
  ],
  "entity": "Overseer variants",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "2",
  "new_value": "1",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4028,
  "source_span_end": 4082,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Overview` — `rv2_change_7757556d16acdfe2bb898b9f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Stability fixes
```

Extracted fields:

```json
{
  "change_text": "Stability fixes",
  "heading_path": [
    "Overview",
    "This update includes"
  ],
  "entity": "This update includes",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 120,
  "source_span_end": 135,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Overview` — `rv2_change_7b3d3472237d6242d895e4c0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Weapon Fixes
```

Extracted fields:

```json
{
  "change_text": "Weapon Fixes",
  "heading_path": [
    "Overview",
    "Balancing"
  ],
  "entity": null,
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 437,
  "source_span_end": 449,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=P-11 Stim Pistol` — `rv2_change_848d1c5c1c6319160df0b7be`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased sway modifier from 1.2 to 1
```

Extracted fields:

```json
{
  "change_text": "Decreased sway modifier from 1.2 to 1",
  "heading_path": [
    "P-11 Stim Pistol"
  ],
  "entity": "P-11 Stim Pistol",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "1.2",
  "new_value": "1",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5510,
  "source_span_end": 5547,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=P-113 Verdict` — `rv2_change_188e1b702d572dbddaea7858`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased max spare magazines from 8 to 10
```

Extracted fields:

```json
{
  "change_text": "Increased max spare magazines from 8 to 10",
  "heading_path": [
    "P-113 Verdict"
  ],
  "entity": "P-113 Verdict",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "8",
  "new_value": "10",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9419,
  "source_span_end": 9461,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=P-113 Verdict` — `rv2_change_bf9d30a7b46d622be8a45c41`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 125 to 135
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 125 to 135",
  "heading_path": [
    "P-113 Verdict"
  ],
  "entity": "P-113 Verdict",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "125",
  "new_value": "135",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5719,
  "source_span_end": 5751,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=P-19 Redeemer` — `rv2_change_b2f2775924aaa502830a0c45`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased spare magazines from 4 to 6
```

Extracted fields:

```json
{
  "change_text": "Increased spare magazines from 4 to 6",
  "heading_path": [
    "P-19 Redeemer"
  ],
  "entity": "P-19 Redeemer",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "4",
  "new_value": "6",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9684,
  "source_span_end": 9721,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=P-19 Redeemer` — `rv2_change_4ccf3f988576061992287615`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 60 to 70
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 60 to 70",
  "heading_path": [
    "P-19 Redeemer"
  ],
  "entity": "P-19 Redeemer",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "60",
  "new_value": "70",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5540,
  "source_span_end": 5570,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=P-2 Peacemaker` — `rv2_change_bd6c171542408f34c628d026`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 85 to 95
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 85 to 95",
  "heading_path": [
    "P-2 Peacemaker"
  ],
  "entity": "P-2 Peacemaker",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "85",
  "new_value": "95",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5360,
  "source_span_end": 5390,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=P-2 Peacemaker` — `rv2_change_a0a7b54a44b7238d9bb570a1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Drag increased from 0.6 to 1.2
```

Extracted fields:

```json
{
  "change_text": "Drag increased from 0.6 to 1.2",
  "heading_path": [
    "P-2 Peacemaker"
  ],
  "entity": "P-2 Peacemaker",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "0.6",
  "new_value": "1.2",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5456,
  "source_span_end": 5486,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=P-4 Senator` — `rv2_change_8ce5e845336eee400e709e00`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased sway modifier from 1.3 to 1
```

Extracted fields:

```json
{
  "change_text": "Decreased sway modifier from 1.3 to 1",
  "heading_path": [
    "P-4 Senator"
  ],
  "entity": "P-4 Senator",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "1.3",
  "new_value": "1",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5797,
  "source_span_end": 5834,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=P-72 Crisper` — `rv2_change_dda227c811ee8c33c2188665`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased magazine capacity from 30 to 50
```

Extracted fields:

```json
{
  "change_text": "Increased magazine capacity from 30 to 50",
  "heading_path": [
    "P-72 Crisper"
  ],
  "entity": "P-72 Crisper",
  "aspect": "capacity_or_ammunition",
  "action": "increased",
  "direction": "increased",
  "previous_value": "30",
  "new_value": "50",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4705,
  "source_span_end": 4746,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=P-72 Crisper` — `rv2_change_f6b11067d043c3e62006e0a0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased sway modifier from 1.2 to 1
```

Extracted fields:

```json
{
  "change_text": "Decreased sway modifier from 1.2 to 1",
  "heading_path": [
    "P-72 Crisper"
  ],
  "entity": "P-72 Crisper",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "1.2",
  "new_value": "1",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4760,
  "source_span_end": 4797,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=P-8 Senator` — `rv2_change_4a377920aee79841a66207a3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Speedloader added when reloading on an empty cylinder–speeds up reload on empty considerably
```

Extracted fields:

```json
{
  "change_text": "Speedloader added when reloading on an empty cylinder–speeds up reload on empty considerably",
  "heading_path": [
    "P-8 Senator"
  ],
  "entity": "P-8 Senator",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2798,
  "source_span_end": 2890,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=P-8 Senator` — `rv2_change_0089915384def212b4d462f6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased damage from 150 to 175
```

Extracted fields:

```json
{
  "change_text": "Increased damage from 150 to 175",
  "heading_path": [
    "P-8 Senator"
  ],
  "entity": "P-8 Senator",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "150",
  "new_value": "175",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2761,
  "source_span_end": 2793,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=P-92 Warrant` — `rv2_change_b70c6be3ee3c16671f8379b3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Gravity multiplier decreased from 1 to 0.3
```

Extracted fields:

```json
{
  "change_text": "Gravity multiplier decreased from 1 to 0.3",
  "heading_path": [
    "P-92 Warrant"
  ],
  "entity": "P-92 Warrant",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "1",
  "new_value": "0.3",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6017,
  "source_span_end": 6059,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=P-92 Warrant` — `rv2_change_98e54376b35c41f53ebaf2f6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed its crosshair not updating when toggling its weapon function through the new input bindings
```

Extracted fields:

```json
{
  "change_text": "Fixed its crosshair not updating when toggling its weapon function through the new input bindings",
  "heading_path": [
    "P-92 Warrant"
  ],
  "entity": "P-92 Warrant",
  "aspect": "interface_or_settings",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 15120,
  "source_span_end": 15217,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=PLAS-101 Purifier` — `rv2_change_2f0b10eb19e43413a7e1c467`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased projectile armor penetration to be the same as the explosion
```

Extracted fields:

```json
{
  "change_text": "Increased projectile armor penetration to be the same as the explosion",
  "heading_path": [
    "PLAS-101 Purifier"
  ],
  "entity": "PLAS-101 Purifier",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5004,
  "source_span_end": 5074,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=PLAS-101 Purifier` — `rv2_change_e571020555ff0c49225eee0f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased explosion damage falloff
```

Extracted fields:

```json
{
  "change_text": "Decreased explosion damage falloff",
  "heading_path": [
    "PLAS-101 Purifier"
  ],
  "entity": "PLAS-101 Purifier",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5079,
  "source_span_end": 5113,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=PLAS-15 Loyalist` — `rv2_change_57b6a0caa0d3e8f2dae38174`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased sway modifier from 1.2 to 1
```

Extracted fields:

```json
{
  "change_text": "Decreased sway modifier from 1.2 to 1",
  "heading_path": [
    "PLAS-15 Loyalist"
  ],
  "entity": "PLAS-15 Loyalist",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "1.2",
  "new_value": "1",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5416,
  "source_span_end": 5453,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=PLAS-39 Accelerator Rifle` — `rv2_change_1546db84ba05273c953f468b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Extra spare magazines increased from 8 to 12
```

Extracted fields:

```json
{
  "change_text": "Extra spare magazines increased from 8 to 12",
  "heading_path": [
    "PLAS-39 Accelerator Rifle"
  ],
  "entity": "PLAS-39 Accelerator Rifle",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "8",
  "new_value": "12",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4591,
  "source_span_end": 4635,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=PLAS-39 Accelerator Rifle` — `rv2_change_c27e48315f6b117fd71cb29d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Ergonomics increased from 40 to 60
```

Extracted fields:

```json
{
  "change_text": "Ergonomics increased from 40 to 60",
  "heading_path": [
    "PLAS-39 Accelerator Rifle"
  ],
  "entity": "PLAS-39 Accelerator Rifle",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "40",
  "new_value": "60",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4649,
  "source_span_end": 4683,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=PLAS-45 Epoch` — `rv2_change_f1008f52e0a9a7ebb6a35eaf`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Demolition strength on overcharged projectile increased from 10 to 30
```

Extracted fields:

```json
{
  "change_text": "Demolition strength on overcharged projectile increased from 10 to 30",
  "heading_path": [
    "PLAS-45 Epoch"
  ],
  "entity": "PLAS-45 Epoch",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "10",
  "new_value": "30",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7931,
  "source_span_end": 8000,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=PLAS-45 Epoch` — `rv2_change_d72fe44626d3368f6d47c87a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Duration until explosion increased from 3 to 3.25 sec
```

Extracted fields:

```json
{
  "change_text": "Duration until explosion increased from 3 to 3.25 sec",
  "heading_path": [
    "PLAS-45 Epoch"
  ],
  "entity": "PLAS-45 Epoch",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "3",
  "new_value": "3.25 sec",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7635,
  "source_span_end": 7688,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Patch Highlights` — `rv2_change_0c8d489a0f1af9aea99df49c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased Exo Suit Cooldown
```

Extracted fields:

```json
{
  "change_text": "Decreased Exo Suit Cooldown",
  "heading_path": [
    "Patch Highlights",
    "Enemy Rebalances"
  ],
  "entity": "Enemy Rebalances",
  "aspect": "cooldown_or_timing",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1427,
  "source_span_end": 1454,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Patch Highlights` — `rv2_change_43f071a8f169e18f45c05c0c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Crash Fixes
```

Extracted fields:

```json
{
  "change_text": "Crash Fixes",
  "heading_path": [
    "Patch Highlights",
    "Stratagem Rebalances"
  ],
  "entity": "Stratagem Rebalances",
  "aspect": "performance_or_network",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1712,
  "source_span_end": 1723,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Patrol Spawning` — `rv2_change_5c3afae3e73211c897bdc8a8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Previously, once the mission was completed but before extraction, we significantly increased patrol spawns across the entire map.
```

Extracted fields:

```json
{
  "change_text": "Previously, once the mission was completed but before extraction, we significantly increased patrol spawns across the entire map.",
  "heading_path": [
    "Patrol Spawning"
  ],
  "entity": "Patrol Spawning",
  "aspect": "map_or_level",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9218,
  "source_span_end": 9347,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Patrol Spawning` — `rv2_change_53ab5c788eb7d916fa6865a2`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
the increased patrol spawns are concentrated around the extraction site, with more patrols appearing the closer you are to it.
```

Extracted fields:

```json
{
  "change_text": "the increased patrol spawns are concentrated around the extraction site, with more patrols appearing the closer you are to it.",
  "heading_path": [
    "Patrol Spawning",
    "Now,"
  ],
  "entity": "Now,",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9361,
  "source_span_end": 9487,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Patterns, Boosters, and More` — `rv2_change_cd791dab5ef50bd0f2acc7d5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
There’s also a new booster called Experimental Infusion, which gives your stims the added bonus of boosting your movement speed and reducing the damage you take for a short time.
```

Extracted fields:

```json
{
  "change_text": "There’s also a new booster called Experimental Infusion, which gives your stims the added bonus of boosting your movement speed and reducing the damage you take for a short time.",
  "heading_path": [
    "Patterns, Boosters, and More"
  ],
  "entity": "Patterns, Boosters, and More",
  "aspect": "damage_or_attack_power",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4455,
  "source_span_end": 4633,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Peak Physique` — `rv2_change_6f1f9e15e36274d5eb6e30b3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased melee damage bonus from 100% to 40%
```

Extracted fields:

```json
{
  "change_text": "Decreased melee damage bonus from 100% to 40%",
  "heading_path": [
    "Peak Physique"
  ],
  "entity": "Peak Physique",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "100%",
  "new_value": "40%",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8172,
  "source_span_end": 8217,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Planets & Hazards` — `rv2_change_16657443203b838ead4e75cd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
No longer causes bleed or stamina drain if hit by the plant explosion or spikes.
```

Extracted fields:

```json
{
  "change_text": "No longer causes bleed or stamina drain if hit by the plant explosion or spikes.",
  "heading_path": [
    "Planets & Hazards",
    "Spike Plant"
  ],
  "entity": "Spike Plant",
  "aspect": "speed_or_movement",
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7809,
  "source_span_end": 7889,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Planets & Hazards` — `rv2_change_50f049a54b5b7c92888f9a14`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
While a fire tornado storm takes place, enemy vision is reduced. Player vision is unaffected.
```

Extracted fields:

```json
{
  "change_text": "While a fire tornado storm takes place, enemy vision is reduced. Player vision is unaffected.",
  "heading_path": [
    "Planets & Hazards",
    "Fire Tornados"
  ],
  "entity": "Fire Tornados",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8159,
  "source_span_end": 8252,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Planets and Modifiers` — `rv2_change_7d8bafea92d96422279237b4`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The Intense Heat and Extreme Cold modifiers are no longer static throughout the entire mission, and may now change based on time of day or different weather conditions
```

Extracted fields:

```json
{
  "change_text": "The Intense Heat and Extreme Cold modifiers are no longer static throughout the entire mission, and may now change based on time of day or different weather conditions",
  "heading_path": [
    "Planets and Modifiers"
  ],
  "entity": "Planets and Modifiers",
  "aspect": "content_or_feature",
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 15368,
  "source_span_end": 15535,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Primary Weapons` — `rv2_change_6fd8c9d16a1c6b0b15ddd078`

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
  "entity": "Miscellaneous Fixes",
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
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Primary Weapons` — `rv2_change_f4d57fd7cad8cc49b16efef9`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Explosion damage increased from 150 to 350
```

Extracted fields:

```json
{
  "change_text": "Explosion damage increased from 150 to 350",
  "heading_path": [
    "Primary Weapons",
    "Crossbow"
  ],
  "entity": "Crossbow",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "150",
  "new_value": "350",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5225,
  "source_span_end": 5267,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Primary weapons` — `rv2_change_5e8ac816aaca313959d6076c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased ergonomics from 35 to 50
```

Extracted fields:

```json
{
  "change_text": "Increased ergonomics from 35 to 50",
  "heading_path": [
    "Primary weapons",
    "R-2 Amendment"
  ],
  "entity": "R-2 Amendment",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "35",
  "new_value": "50",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 752,
  "source_span_end": 786,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Primary weapons` — `rv2_change_8bfecd05a320aa520dccdc61`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Magazine capacity increased from 20 to 25
```

Extracted fields:

```json
{
  "change_text": "Magazine capacity increased from 20 to 25",
  "heading_path": [
    "Primary weapons",
    "R-63 Diligence"
  ],
  "entity": "R-63 Diligence",
  "aspect": "capacity_or_ammunition",
  "action": "increased",
  "direction": "increased",
  "previous_value": "20",
  "new_value": "25",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 509,
  "source_span_end": 550,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Primary, Secondary, & Support Weapons` — `rv2_change_b2318673354626e5b7fafe2d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Arc Thrower: reduced distance from 50m to 35m.
```

Extracted fields:

```json
{
  "change_text": "Arc Thrower: reduced distance from 50m to 35m.",
  "heading_path": [
    "Primary, Secondary, & Support Weapons"
  ],
  "entity": "Primary, Secondary, & Support Weapons",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "50",
  "new_value": "35",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1382,
  "source_span_end": 1428,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Primary, Secondary, & Support Weapons` — `rv2_change_299284ee66751411c000e217`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Slugger: reduced damage from 280 to 250.
```

Extracted fields:

```json
{
  "change_text": "Slugger: reduced damage from 280 to 250.",
  "heading_path": [
    "Primary, Secondary, & Support Weapons"
  ],
  "entity": "Primary, Secondary, & Support Weapons",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "280",
  "new_value": "250.",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1978,
  "source_span_end": 2018,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Problem we want to solve` — `rv2_change_9baee6db2cea301f493a88b8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Find a specific weapon in the loadout can be hard to do with all the new weapons added to the arsenal
```

Extracted fields:

```json
{
  "change_text": "Find a specific weapon in the loadout can be hard to do with all the new weapons added to the arsenal",
  "heading_path": [
    "Problem we want to solve"
  ],
  "entity": "Problem we want to solve",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4828,
  "source_span_end": 4929,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Problem we want to solve` — `rv2_change_5a95a1ace4c977d2a3f8b8a0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The player lost control for a long time when landing on the feet from a higher fall.
```

Extracted fields:

```json
{
  "change_text": "The player lost control for a long time when landing on the feet from a higher fall.",
  "heading_path": [
    "Problem we want to solve"
  ],
  "entity": "Problem we want to solve",
  "aspect": "speed_or_movement",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5859,
  "source_span_end": 5943,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Q. What about the beta testing you mentioned previously?` — `rv2_change_9fff8c3a957942d75acacd67`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
They have been a testbed for the program and we intend to expand it in the future and invite a wider variety of testers to playtest our upcoming updates
```

Extracted fields:

```json
{
  "change_text": "They have been a testbed for the program and we intend to expand it in the future and invite a wider variety of testers to playtest our upcoming updates.",
  "heading_path": [
    "Q. What about the beta testing you mentioned previously?"
  ],
  "entity": "Q. What about the beta testing you mentioned previously?",
  "aspect": null,
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2894,
  "source_span_end": 3046,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=Question` — `rv2_change_a8256b13af6cf0bcba581b35`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Alex, can you introduce the production role on Helldivers 2.
```

Extracted fields:

```json
{
  "change_text": "Alex, can you introduce the production role on Helldivers 2.",
  "heading_path": [
    "Question"
  ],
  "entity": "Question",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 250,
  "source_span_end": 310,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=R-2 Amendment` — `rv2_change_c034c221c3da211e05aaeab6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased Bayonet melee damage from 110 to 165
```

Extracted fields:

```json
{
  "change_text": "Increased Bayonet melee damage from 110 to 165",
  "heading_path": [
    "R-2 Amendment"
  ],
  "entity": "R-2 Amendment",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "110",
  "new_value": "165",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3857,
  "source_span_end": 3903,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=R-2 Amendment` — `rv2_change_5ba42b61c8c8dc69ca056dfa`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Bayonet stagger strength increased from 20 to 25
```

Extracted fields:

```json
{
  "change_text": "Bayonet stagger strength increased from 20 to 25",
  "heading_path": [
    "R-2 Amendment"
  ],
  "entity": "R-2 Amendment",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "20",
  "new_value": "25",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1765,
  "source_span_end": 1813,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=R-2124 Constitution` — `rv2_change_ee2102ca94d18148cd07ed1e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added a full stripper clip reload when reloading if the magazine is empty.
```

Extracted fields:

```json
{
  "change_text": "Added a full stripper clip reload when reloading if the magazine is empty.",
  "heading_path": [
    "R-2124 Constitution"
  ],
  "entity": "R-2124 Constitution",
  "aspect": "capacity_or_ammunition",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8071,
  "source_span_end": 8145,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=R-2124 Constitution` — `rv2_change_0edf06ec283e7a7389e7e971`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased Bayonet melee durable damage from 55 to 83
```

Extracted fields:

```json
{
  "change_text": "Increased Bayonet melee durable damage from 55 to 83",
  "heading_path": [
    "R-2124 Constitution"
  ],
  "entity": "R-2124 Constitution",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "55",
  "new_value": "83",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3751,
  "source_span_end": 3803,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=R-36 Eruptor` — `rv2_change_df2c934ec9840e8b4ee7d80c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
and introduced some unexpected interactions
```

Extracted fields:

```json
{
  "change_text": "and introduced some unexpected interactions.",
  "heading_path": [
    "R-36 Eruptor"
  ],
  "entity": "R-36 Eruptor",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10206,
  "source_span_end": 10249,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=R-36 Eruptor` — `rv2_change_393d6973a506820e72999414`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased explosion damage by 40 and removed shrapnel from the explosion
```

Extracted fields:

```json
{
  "change_text": "Increased explosion damage by 40 and removed shrapnel from the explosion",
  "heading_path": [
    "R-36 Eruptor"
  ],
  "entity": "R-36 Eruptor",
  "aspect": "damage_or_attack_power",
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": 40.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 507,
  "source_span_end": 579,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=R-63 Diligence` — `rv2_change_2b681fe21437a96f73579f3e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 112 to 125
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 112 to 125",
  "heading_path": [
    "R-63 Diligence"
  ],
  "entity": "R-63 Diligence",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "112",
  "new_value": "125",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2551,
  "source_span_end": 2583,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=R-63 Diligence` — `rv2_change_81a508c34f6eefce9eebf082`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased projectile damage against durable* body parts from 10% to 25%
```

Extracted fields:

```json
{
  "change_text": "Increased projectile damage against durable* body parts from 10% to 25%",
  "heading_path": [
    "R-63 Diligence"
  ],
  "entity": "R-63 Diligence",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "10%",
  "new_value": "25%",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5490,
  "source_span_end": 5561,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=RELATED LINKS` — `rv2_change_8fff576b04380a3e5b7badce`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Helldivers 2 patch 1.000.100 nerfs its best weapons, adds new hazards
```

Extracted fields:

```json
{
  "change_text": "Helldivers 2 patch 1.000.100 nerfs its best weapons, adds new hazards",
  "heading_path": [
    "RELATED LINKS"
  ],
  "entity": "RELATED LINKS",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1017,
  "source_span_end": 1086,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=RELATED LINKS` — `rv2_change_32eb8cce229618d7a4ce657a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Helldivers 2 patch 1.000.10 fixes crashes, PC black screens, and more
```

Extracted fields:

```json
{
  "change_text": "Helldivers 2 patch 1.000.10 fixes crashes, PC black screens, and more",
  "heading_path": [
    "RELATED LINKS"
  ],
  "entity": "RELATED LINKS",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 915,
  "source_span_end": 984,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=RESEARCH & DEVELOPMENT` — `rv2_change_053dff7b8a3df7b28fd09ebf`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
You can already see those Galactic War improvements starting to take shape, because in our last update we introduced something the community has been pining for…
```

Extracted fields:

```json
{
  "change_text": "You can already see those Galactic War improvements starting to take shape, because in our last update we introduced something the community has been pining for…",
  "heading_path": [
    "RESEARCH & DEVELOPMENT"
  ],
  "entity": "RESEARCH & DEVELOPMENT",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6701,
  "source_span_end": 6862,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=RESEARCH & DEVELOPMENT` — `rv2_change_7057252e4740e33fe2e58225`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Alex also mentioned that, with the push for higher quality updates, we will be able to use this additional time to test content more thoroughly.
```

Extracted fields:

```json
{
  "change_text": "Alex also mentioned that, with the push for higher quality updates, we will be able to use this additional time to test content more thoroughly.",
  "heading_path": [
    "RESEARCH & DEVELOPMENT"
  ],
  "entity": "RESEARCH & DEVELOPMENT",
  "aspect": "capacity_or_ammunition",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5543,
  "source_span_end": 5687,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=RL-77 Airburst Rocket Launcher` — `rv2_change_b3a9b14f6014c89b277f184c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Playing Rock, Paper, Scissors in front of the ship no longer causes player to fall out into space.
```

Extracted fields:

```json
{
  "change_text": "Playing Rock, Paper, Scissors in front of the ship no longer causes player to fall out into space.",
  "heading_path": [
    "RL-77 Airburst Rocket Launcher",
    "Crash fixes"
  ],
  "entity": "Crash fixes",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8929,
  "source_span_end": 9027,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=RL-77 Airburst Rocket Launcher` — `rv2_change_a5b21d0f31e8a72777645ad0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed several issues where weapon thumbnails would disappear when scrolling through Armory.
```

Extracted fields:

```json
{
  "change_text": "Fixed several issues where weapon thumbnails would disappear when scrolling through Armory.",
  "heading_path": [
    "RL-77 Airburst Rocket Launcher",
    "Crash fixes"
  ],
  "entity": "Crash fixes",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7753,
  "source_span_end": 7844,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=RS-422 Railgun` — `rv2_change_a6d45b14d39bc75686230369`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased armor penetration in both safe mode and unsafe mode
```

Extracted fields:

```json
{
  "change_text": "Increased armor penetration in both safe mode and unsafe mode",
  "heading_path": [
    "RS-422 Railgun"
  ],
  "entity": "RS-422 Railgun",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2218,
  "source_span_end": 2279,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=RS-422 Railgun` — `rv2_change_169f792aad807060ac715a46`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Stagger force slightly reduced
```

Extracted fields:

```json
{
  "change_text": "Stagger force slightly reduced",
  "heading_path": [
    "RS-422 Railgun"
  ],
  "entity": "RS-422 Railgun",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2284,
  "source_span_end": 2314,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Raiders` — `rv2_change_49a185e7823004028c686651`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
increased durable damage of the melee attacks
```

Extracted fields:

```json
{
  "change_text": "increased durable damage of the melee attacks",
  "heading_path": [
    "Raiders"
  ],
  "entity": "Raiders",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8632,
  "source_span_end": 8677,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Reduced Latency for Split-Second Reactions` — `rv2_change_62d66b52d2c3ffddca2ce477`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
This update, along with additional fixes, will drop on [b]May 27, 2026[/b].
```

Extracted fields:

```json
{
  "change_text": "This update, along with additional fixes, will drop on May 27, 2026.",
  "heading_path": [
    "Reduced Latency for Split-Second Reactions",
    "Responsiveness is critical during tense battles, and we’ve worked with hardware partners to reduce input latency.",
    "AMD Anti-Lag 2"
  ],
  "entity": "AMD Anti-Lag 2",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2613,
  "source_span_end": 2688,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Reinforced Epaulettes` — `rv2_change_b4c5563b8ca0663d096b0b50`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased melee damage bonus from 50% to 20%
```

Extracted fields:

```json
{
  "change_text": "Decreased melee damage bonus from 50% to 20%",
  "heading_path": [
    "Reinforced Epaulettes"
  ],
  "entity": "Reinforced Epaulettes",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "50%",
  "new_value": "20%",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8375,
  "source_span_end": 8419,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Reloading improvements` — `rv2_change_2a652ad9a7406fafc4e0ee0f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Introduced the concept of delayed reloads.
```

Extracted fields:

```json
{
  "change_text": "Introduced the concept of delayed reloads.",
  "heading_path": [
    "Reloading improvements"
  ],
  "entity": "Reloading improvements",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4988,
  "source_span_end": 5030,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Resolved Top Priority issues` — `rv2_change_977459bf26df10bbdbd2d9e1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Resolved an issue where, under heavy server load, some players did not immediately receive their Super Credit purchases after payment
```

Extracted fields:

```json
{
  "change_text": "Resolved an issue where, under heavy server load, some players did not immediately receive their Super Credit purchases after payment",
  "heading_path": [
    "Resolved Top Priority issues"
  ],
  "entity": "Resolved Top Priority issues",
  "aspect": "performance_or_network",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "under heavy server load, some players did not immediately receive their Super Credit purchases after payment",
  "bug_symptom": "where",
  "source_span_start": 6046,
  "source_span_end": 6179,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Resolved Top Priority issues` — `rv2_change_9f7bae1b60754de69b233ce0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The spawn rate of Reinforced Scout Striders on higher difficulty levels has been reduced
```

Extracted fields:

```json
{
  "change_text": "The spawn rate of Reinforced Scout Striders on higher difficulty levels has been reduced",
  "heading_path": [
    "Resolved Top Priority issues"
  ],
  "entity": "Resolved Top Priority issues",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6702,
  "source_span_end": 6790,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Resolved known issues` — `rv2_change_231de015297888cd1890b775`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Destroying the Air Base Control Tower with a portable Hellbomb no longer blocks objective progression.
```

Extracted fields:

```json
{
  "change_text": "Destroying the Air Base Control Tower with a portable Hellbomb no longer blocks objective progression.",
  "heading_path": [
    "Resolved known issues"
  ],
  "entity": "Resolved known issues",
  "aspect": "rewards_or_progression",
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1879,
  "source_span_end": 1981,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Resolved known issues` — `rv2_change_9575f707fd5d0762196107bd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Enthusiastic Mirth emote sound has been fixed, laughter is once again permitted on the battlefield.
```

Extracted fields:

```json
{
  "change_text": "Enthusiastic Mirth emote sound has been fixed, laughter is once again permitted on the battlefield.",
  "heading_path": [
    "Resolved known issues"
  ],
  "entity": "Resolved known issues",
  "aspect": "audio",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1996,
  "source_span_end": 2095,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Rock Solid` — `rv2_change_886815786b67d59b478be8dd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased melee damage bonus from 100% to 40%
```

Extracted fields:

```json
{
  "change_text": "Decreased melee damage bonus from 100% to 40%",
  "heading_path": [
    "Rock Solid"
  ],
  "entity": "Rock Solid",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "100%",
  "new_value": "40%",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8268,
  "source_span_end": 8313,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Rocket Devastator` — `rv2_change_b8d50457637f2acb773c11dd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased stagger strength on rockets projectile from 50 to 35
```

Extracted fields:

```json
{
  "change_text": "Decreased stagger strength on rockets projectile from 50 to 35",
  "heading_path": [
    "Rocket Devastator"
  ],
  "entity": "Rocket Devastator",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "50",
  "new_value": "35",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9217,
  "source_span_end": 9279,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Rocket Devastator` — `rv2_change_1e290374a850d5b633de177b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Rockets now deals increased damage vs Durable targets
```

Extracted fields:

```json
{
  "change_text": "Rockets now deals increased damage vs Durable targets",
  "heading_path": [
    "Rocket Devastator"
  ],
  "entity": "Rocket Devastator",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9819,
  "source_span_end": 9872,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Rocket Raider` — `rv2_change_2c197abd4a7b65e633a37649`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Rockets now deals increased damage vs Durable targets
```

Extracted fields:

```json
{
  "change_text": "Rockets now deals increased damage vs Durable targets",
  "heading_path": [
    "Rocket Raider"
  ],
  "entity": "Rocket Raider",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9634,
  "source_span_end": 9687,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Rupture Strain enemies` — `rv2_change_50264f0f697a13eac455bff6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Updated textures for all Rupture Strain enemies for better readability
```

Extracted fields:

```json
{
  "change_text": "Updated textures for all Rupture Strain enemies for better readability",
  "heading_path": [
    "Rupture Strain enemies"
  ],
  "entity": "Rupture Strain enemies",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10719,
  "source_span_end": 10789,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Rupture Warrior` — `rv2_change_3c067fbfd37b72b6cfc7bc52`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Front legs armor decreased from 3 to 2
```

Extracted fields:

```json
{
  "change_text": "Front legs armor decreased from 3 to 2",
  "heading_path": [
    "Rupture Warrior"
  ],
  "entity": "Rupture Warrior",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "3",
  "new_value": "2",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 11127,
  "source_span_end": 11165,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Rupture Warrior` — `rv2_change_c5a18654d789b295ed085693`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Movement speed when underground has been decreased
```

Extracted fields:

```json
{
  "change_text": "Movement speed when underground has been decreased",
  "heading_path": [
    "Rupture Warrior"
  ],
  "entity": "Rupture Warrior",
  "aspect": "speed_or_movement",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10853,
  "source_span_end": 10903,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=S-11 Speargun` — `rv2_change_4b67bbb6bf1a529ada2672ca`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased reload duration 3.5 -> 2.5 sec
```

Extracted fields:

```json
{
  "change_text": "Decreased reload duration 3.5 -> 2.5 sec",
  "heading_path": [
    "S-11 Speargun"
  ],
  "entity": "S-11 Speargun",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 154,
  "source_span_end": 194,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=SEAF Artillery Explosive/High Yield Explosive` — `rv2_change_cf8ef037c1e765b60dfd4846`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased projectile durable damage 3500 to 4000
```

Extracted fields:

```json
{
  "change_text": "Increased projectile durable damage 3500 to 4000",
  "heading_path": [
    "SEAF Artillery Explosive/High Yield Explosive"
  ],
  "entity": "SEAF Artillery Explosive/High Yield Explosive",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10437,
  "source_span_end": 10485,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=SEAF Artillery Explosive/High Yield Explosive` — `rv2_change_72dd3b800651c6530c7a8ad9`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased explosion durable damage 1000 to  1500
```

Extracted fields:

```json
{
  "change_text": "Increased explosion durable damage 1000 to  1500",
  "heading_path": [
    "SEAF Artillery Explosive/High Yield Explosive"
  ],
  "entity": "SEAF Artillery Explosive/High Yield Explosive",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10553,
  "source_span_end": 10601,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=SEAF Support` — `rv2_change_a582045a0f1a888f90730811`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Helldivers will be able to be supported by friendly SEAF NPC troops, with new and improved behavior, weaponry and updated visual
```

Extracted fields:

```json
{
  "change_text": "Helldivers will be able to be supported by friendly SEAF NPC troops, with new and improved behavior, weaponry and updated visuals",
  "heading_path": [
    "SEAF Support",
    "Super Earth Armed Forces (SEAF) can now appear as a planet modifier, joining you in battle in your missions and enhancing your combat capabilities with a range of new tools (Stim pistols, Heavy Machine guns and more)"
  ],
  "entity": "Super Earth Armed Forces (SEAF) can now appear as a planet modifier, joining you in battle in your missions and enhancing your combat capabilities with a range of new tools (Stim pistols, Heavy Machine guns and more)",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2336,
  "source_span_end": 2464,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=SG-22 Bushwhacker` — `rv2_change_bb57236cfe41dca5fff4e71c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased sway modifier from 1.3 to 1
```

Extracted fields:

```json
{
  "change_text": "Decreased sway modifier from 1.3 to 1",
  "heading_path": [
    "SG-22 Bushwhacker"
  ],
  "entity": "SG-22 Bushwhacker",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "1.3",
  "new_value": "1",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5605,
  "source_span_end": 5642,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=SG-225 Breaker` — `rv2_change_08a9a0161e9eec8f98d0794a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Max spare amount of magazines decreased from 10 to 7
```

Extracted fields:

```json
{
  "change_text": "Max spare amount of magazines decreased from 10 to 7",
  "heading_path": [
    "SG-225 Breaker"
  ],
  "entity": "SG-225 Breaker",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "10",
  "new_value": "7",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1917,
  "source_span_end": 1969,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=SG-225 Breaker` — `rv2_change_c6946b17642d5f5584cd44fa`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Starting magazine amount decreased from 6 to 5
```

Extracted fields:

```json
{
  "change_text": "Starting magazine amount decreased from 6 to 5",
  "heading_path": [
    "SG-225 Breaker"
  ],
  "entity": "SG-225 Breaker",
  "aspect": "capacity_or_ammunition",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "6",
  "new_value": "5",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1866,
  "source_span_end": 1912,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=SG-225IE Breaker Incendiary` — `rv2_change_6b881b9fc07a22bfc2fd5d58`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased recoil from 28 to 41
```

Extracted fields:

```json
{
  "change_text": "Increased recoil from 28 to 41",
  "heading_path": [
    "SG-225IE Breaker Incendiary"
  ],
  "entity": "SG-225IE Breaker Incendiary",
  "aspect": "accuracy_or_spread",
  "action": "increased",
  "direction": "increased",
  "previous_value": "28",
  "new_value": "41",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2797,
  "source_span_end": 2827,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=SG-225IE Breaker Incendiary` — `rv2_change_92b5bdf0613310d182f41d97`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased magazines spare magazines 9 to 11
```

Extracted fields:

```json
{
  "change_text": "Increased magazines spare magazines 9 to 11",
  "heading_path": [
    "SG-225IE Breaker Incendiary"
  ],
  "entity": "SG-225IE Breaker Incendiary",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8990,
  "source_span_end": 9033,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=SG-225SP Breaker Spray&Pray` — `rv2_change_6d9a3b66b6f12adf5b99909d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased spare magazines 16 to 20
```

Extracted fields:

```json
{
  "change_text": "Increased spare magazines 16 to 20",
  "heading_path": [
    "SG-225SP Breaker Spray&Pray"
  ],
  "entity": "SG-225SP Breaker Spray&Pray",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9175,
  "source_span_end": 9209,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=SG-225SP Breaker Spray&Pray` — `rv2_change_1639809aef81755afd701dcc`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased starting magazines 11 to 12
```

Extracted fields:

```json
{
  "change_text": "Increased starting magazines 11 to 12",
  "heading_path": [
    "SG-225SP Breaker Spray&Pray"
  ],
  "entity": "SG-225SP Breaker Spray&Pray",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9216,
  "source_span_end": 9253,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=SG-8P Punisher Plasma` — `rv2_change_362cf2b0b2aac3a9be9bee87`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage projectile decreased from 100 to 0
```

Extracted fields:

```json
{
  "change_text": "Damage projectile decreased from 100 to 0",
  "heading_path": [
    "SG-8P Punisher Plasma"
  ],
  "entity": "SG-8P Punisher Plasma",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "100",
  "new_value": "0",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2200,
  "source_span_end": 2241,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=SG-8P Punisher Plasma` — `rv2_change_50d21c8052265cfcf419ecf8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage explosion increased from 150 to 225
```

Extracted fields:

```json
{
  "change_text": "Damage explosion increased from 150 to 225",
  "heading_path": [
    "SG-8P Punisher Plasma"
  ],
  "entity": "SG-8P Punisher Plasma",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "150",
  "new_value": "225",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2255,
  "source_span_end": 2297,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=SG-8S Slugger` — `rv2_change_462b0c0db6e49e5ca200ec18`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Durable damage increased from 75 to 90
```

Extracted fields:

```json
{
  "change_text": "Durable damage increased from 75 to 90",
  "heading_path": [
    "SG-8S Slugger"
  ],
  "entity": "SG-8S Slugger",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "75",
  "new_value": "90",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2397,
  "source_span_end": 2435,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=SG-8S Slugger` — `rv2_change_8247a354eea697479c3eb2d7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased stagger force
```

Extracted fields:

```json
{
  "change_text": "Increased stagger force",
  "heading_path": [
    "SG-8S Slugger"
  ],
  "entity": "SG-8S Slugger",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2633,
  "source_span_end": 2656,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=SMG-32 Reprimand` — `rv2_change_4cef62371448ed73cdd452d7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Drag increased from 0.6 to 1.2
```

Extracted fields:

```json
{
  "change_text": "Drag increased from 0.6 to 1.2",
  "heading_path": [
    "SMG-32 Reprimand"
  ],
  "entity": "SMG-32 Reprimand",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "0.6",
  "new_value": "1.2",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3674,
  "source_span_end": 3704,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=SMG-32 Reprimand` — `rv2_change_8b8794f35f4f5b1d05b179f2`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased damage from 135 to 140
```

Extracted fields:

```json
{
  "change_text": "Increased damage from 135 to 140",
  "heading_path": [
    "SMG-32 Reprimand"
  ],
  "entity": "SMG-32 Reprimand",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "135",
  "new_value": "140",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2268,
  "source_span_end": 2300,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=SMG-37 Defender` — `rv2_change_3a3c090307a3f63926aa44ff`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Durable damage increased from 8 to 18
```

Extracted fields:

```json
{
  "change_text": "Durable damage increased from 8 to 18",
  "heading_path": [
    "SMG-37 Defender"
  ],
  "entity": "SMG-37 Defender",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "8",
  "new_value": "18",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3312,
  "source_span_end": 3349,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=SMG-37 Defender` — `rv2_change_a3ad8a654692d30e811c0327`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 80 to 100
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 80 to 100",
  "heading_path": [
    "SMG-37 Defender"
  ],
  "entity": "SMG-37 Defender",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "80",
  "new_value": "100",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3267,
  "source_span_end": 3298,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=SMG-72 Pummeler` — `rv2_change_4c747335779355ce7bf5debe`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Stun duration increased from 1.5 to 3 sec
```

Extracted fields:

```json
{
  "change_text": "Stun duration increased from 1.5 to 3 sec",
  "heading_path": [
    "SMG-72 Pummeler"
  ],
  "entity": "SMG-72 Pummeler",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "1.5",
  "new_value": "3 sec",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1372,
  "source_span_end": 1413,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=SMG-72 Pummeler` — `rv2_change_cd932f23d0a61d2b2771ba6a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Durable damage increased from 7 to 18
```

Extracted fields:

```json
{
  "change_text": "Durable damage increased from 7 to 18",
  "heading_path": [
    "SMG-72 Pummeler"
  ],
  "entity": "SMG-72 Pummeler",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "7",
  "new_value": "18",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3804,
  "source_span_end": 3841,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=SMG/FLAM-34 Stoker` — `rv2_change_9fc0ab433f69eafdbca6645d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased spare magazines 10 to 13
```

Extracted fields:

```json
{
  "change_text": "Increased spare magazines 10 to 13",
  "heading_path": [
    "SMG/FLAM-34 Stoker"
  ],
  "entity": "SMG/FLAM-34 Stoker",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8744,
  "source_span_end": 8778,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=SMG/FLAM-34 Stoker` — `rv2_change_0a2662483fc73bac1da581f6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased reload duration 2.8 sec to 2.3 sec
```

Extracted fields:

```json
{
  "change_text": "Decreased reload duration 2.8 sec to 2.3 sec",
  "heading_path": [
    "SMG/FLAM-34 Stoker"
  ],
  "entity": "SMG/FLAM-34 Stoker",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8827,
  "source_span_end": 8871,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=SMGs and Pistols` — `rv2_change_30fbe8c294e3a77b2fd3326e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
SMGs and pistols have been adjusted to emphasize their role as close-quarters weapons.
```

Extracted fields:

```json
{
  "change_text": "SMGs and pistols have been adjusted to emphasize their role as close-quarters weapons.",
  "heading_path": [
    "SMGs and Pistols"
  ],
  "entity": "SMGs and Pistols",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1494,
  "source_span_end": 1580,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=SMGs and Pistols` — `rv2_change_dba65e367e2c76d67fc78da8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Close-range damage has been increased, and damage falloff has been increased to reinforce their short-range combat identit
```

Extracted fields:

```json
{
  "change_text": "Close-range damage has been increased, and damage falloff has been increased to reinforce their short-range combat identity",
  "heading_path": [
    "SMGs and Pistols"
  ],
  "entity": "SMGs and Pistols",
  "aspect": "gameplay",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1581,
  "source_span_end": 1703,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=STABILITY/CRASHES` — `rv2_change_e043073760ceabf2ae4518c0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a crash when getting disconnected during the joining cutscene.
```

Extracted fields:

```json
{
  "change_text": "Fixed a crash when getting disconnected during the joining cutscene.",
  "heading_path": [
    "STABILITY/CRASHES"
  ],
  "entity": "STABILITY/CRASHES",
  "aspect": "performance_or_network",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 580,
  "source_span_end": 648,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=STABILITY/CRASHES` — `rv2_change_614a9e50d28c38aded4d8ead`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a crash during extraction cutscene relating to text to speech.
```

Extracted fields:

```json
{
  "change_text": "Fixed a crash during extraction cutscene relating to text to speech.",
  "heading_path": [
    "STABILITY/CRASHES"
  ],
  "entity": "STABILITY/CRASHES",
  "aspect": "performance_or_network",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 390,
  "source_span_end": 458,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Scavengers` — `rv2_change_a2d2651d7693a4c14d38a930`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage",
  "heading_path": [
    "Scavengers"
  ],
  "entity": "Scavengers",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7856,
  "source_span_end": 7880,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Scout strider` — `rv2_change_e86b43f03304624bd3fee565`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Legs durable resistance has been increased
```

Extracted fields:

```json
{
  "change_text": "Legs durable resistance has been increased",
  "heading_path": [
    "Scout strider"
  ],
  "entity": "Scout strider",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3908,
  "source_span_end": 3950,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Scout strider` — `rv2_change_9d793b6896c8259a53151b89`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Legs armor decreased from 3 to 2
```

Extracted fields:

```json
{
  "change_text": "Legs armor decreased from 3 to 2",
  "heading_path": [
    "Scout strider"
  ],
  "entity": "Scout strider",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "3",
  "new_value": "2",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3849,
  "source_span_end": 3881,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Sentry health rebalance` — `rv2_change_5647e76480e8b63813177e9b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased the health of all sentries by 100% to compensate for the general damage increase of enemies vs vehicles.
```

Extracted fields:

```json
{
  "change_text": "Increased the health of all sentries by 100% to compensate for the general damage increase of enemies vs vehicles.",
  "heading_path": [
    "Sentry health rebalance"
  ],
  "entity": "Sentry health rebalance",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": 100.0,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4295,
  "source_span_end": 4409,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Sentry health rebalance` — `rv2_change_cbe91a2a98fbd1df2d33bb0f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We have previously increased durable damage on a lot of enemies and since sentries are durable they have lost some of their utility.
```

Extracted fields:

```json
{
  "change_text": "We have previously increased durable damage on a lot of enemies and since sentries are durable they have lost some of their utility.",
  "heading_path": [
    "Sentry health rebalance"
  ],
  "entity": "Sentry health rebalance",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4425,
  "source_span_end": 4557,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Settings` — `rv2_change_15c404496dde5ce57ad4cc53`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The Stratagem loadout menu has undergone an updated categorization of the different stratagem groupings
```

Extracted fields:

```json
{
  "change_text": "The Stratagem loadout menu has undergone an updated categorization of the different stratagem groupings",
  "heading_path": [
    "Settings"
  ],
  "entity": null,
  "aspect": "interface_or_settings",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3264,
  "source_span_end": 3367,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Settings` — `rv2_change_ddf2b5df482d71fc01be88c7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added new separate settings for inverting the gyro input instead of using the Invert Look settings
```

Extracted fields:

```json
{
  "change_text": "Added new separate settings for inverting the gyro input instead of using the Invert Look settings",
  "heading_path": [
    "Settings"
  ],
  "entity": null,
  "aspect": "interface_or_settings",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3161,
  "source_span_end": 3259,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Short term` — `rv2_change_1d206acf8ee2259eef1a26fb`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We’ve made some small gains in the next update by sweeping our systems for unused assets and obvious problems, but you will not likely notice them because the new stuff we’ve added will eat those gains.
```

Extracted fields:

```json
{
  "change_text": "We’ve made some small gains in the next update by sweeping our systems for unused assets and obvious problems, but you will not likely notice them because the new stuff we’ve added will eat those gains.",
  "heading_path": [
    "Short term"
  ],
  "entity": "Short term",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4595,
  "source_span_end": 4797,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Shrapnel spawning` — `rv2_change_13abd9497565450d21a062a2`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Shrapnel now has reduced effectiveness at poor impact angles, to reflect its lack of design for armor penetration in such situations
```

Extracted fields:

```json
{
  "change_text": "Shrapnel now has reduced effectiveness at poor impact angles, to reflect its lack of design for armor penetration in such situations.",
  "heading_path": [
    "Shrapnel spawning"
  ],
  "entity": "Shrapnel spawning",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3887,
  "source_span_end": 4019,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=Shrapnel spawning` — `rv2_change_d4645205554681e00fcaf943`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
In addition, we’ve adjusted shrapnel performance against armor.
```

Extracted fields:

```json
{
  "change_text": "In addition, we’ve adjusted shrapnel performance against armor.",
  "heading_path": [
    "Shrapnel spawning"
  ],
  "entity": "Shrapnel spawning",
  "aspect": "health_or_durability",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3823,
  "source_span_end": 3886,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Shredder Tank turret` — `rv2_change_a30039a4dea537b0cc9802e5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced turn speed
```

Extracted fields:

```json
{
  "change_text": "Reduced turn speed",
  "heading_path": [
    "Shredder Tank turret"
  ],
  "entity": "Shredder Tank turret",
  "aspect": "speed_or_movement",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10187,
  "source_span_end": 10205,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Shriekers` — `rv2_change_8e9c940f5bd2c8122fb84862`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage",
  "heading_path": [
    "Shriekers"
  ],
  "entity": "Shriekers",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7774,
  "source_span_end": 7798,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Sidearms` — `rv2_change_1bbb4da81560c5db6be54a53`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Projectile damage increased from 175 to 200
```

Extracted fields:

```json
{
  "change_text": "Projectile damage increased from 175 to 200",
  "heading_path": [
    "Sidearms",
    "P-4 Senator"
  ],
  "entity": "P-4 Senator",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "175",
  "new_value": "200",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5302,
  "source_span_end": 5345,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Sidearms` — `rv2_change_24220ce98a89707a8e167d1d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Removed recoil
```

Extracted fields:

```json
{
  "change_text": "Removed recoil",
  "heading_path": [
    "Sidearms",
    "Dagger",
    "Gains heat more slowly"
  ],
  "entity": "Gains heat more slowly",
  "aspect": "accuracy_or_spread",
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6605,
  "source_span_end": 6619,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Sidearms weapons` — `rv2_change_5a604ebd48c29392ed10d11c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased stamina cost from 5% to 3%
```

Extracted fields:

```json
{
  "change_text": "Decreased stamina cost from 5% to 3%",
  "heading_path": [
    "Sidearms weapons",
    "CQC-2 Saber"
  ],
  "entity": "CQC-2 Saber",
  "aspect": "purchase_price_or_cost",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "5%",
  "new_value": "3%",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5385,
  "source_span_end": 5421,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Sidearms weapons` — `rv2_change_c0f7c84174091e199ce976c5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased stamina cost from 5% to 4%
```

Extracted fields:

```json
{
  "change_text": "Decreased stamina cost from 5% to 4%",
  "heading_path": [
    "Sidearms weapons",
    "CQC-5 Combat Hatchet"
  ],
  "entity": "CQC-5 Combat Hatchet",
  "aspect": "purchase_price_or_cost",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "5%",
  "new_value": "4%",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5482,
  "source_span_end": 5518,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Social & Multiplayer Fixes` — `rv2_change_06fc87f2dfe7c82ad553bb19`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed an issue on low-activity planets where Quickplay would always join your friends game, even if they were not playing on the same difficulty
```

Extracted fields:

```json
{
  "change_text": "Fixed an issue on low-activity planets where Quickplay would always join your friends game, even if they were not playing on the same difficulty",
  "heading_path": [
    "Social & Multiplayer Fixes"
  ],
  "entity": "Social & Multiplayer Fixes",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "if they were not playing on the same difficulty",
  "bug_symptom": "on low-activity planets where Quickplay would always join your friends game, even",
  "source_span_start": 4673,
  "source_span_end": 4817,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Social & Multiplayer Fixes` — `rv2_change_73449cee8c9a7a4bd59f2521`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed an issue where adding, removing, blocking, or unblocking friends caused player cards in the friend list to display with white text and missing information until you close and open the panel again
```

Extracted fields:

```json
{
  "change_text": "Fixed an issue where adding, removing, blocking, or unblocking friends caused player cards in the friend list to display with white text and missing information until you close and open the panel again",
  "heading_path": [
    "Social & Multiplayer Fixes"
  ],
  "entity": "Social & Multiplayer Fixes",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "adding, removing, blocking, or unblocking friends caused player cards in the friend list to display with white text and missing information until you close and open the panel again",
  "source_span_start": 5024,
  "source_span_end": 5225,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Social Issues` — `rv2_change_5b72cb3677d15cd437eb8714`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Removed the ability for players to use hex codes in usernames, which was exploited to impersonate developers and crash other players' clients
```

Extracted fields:

```json
{
  "change_text": "Removed the ability for players to use hex codes in usernames, which was exploited to impersonate developers and crash other players' clients",
  "heading_path": [
    "Social Issues"
  ],
  "entity": "Social Issues",
  "aspect": "capacity_or_ammunition",
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9462,
  "source_span_end": 9603,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Social Issues` — `rv2_change_ab1ff947a35af70ef8a5e9a6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed an issue that prevented the social menu from displaying your friends' updated nicknames
```

Extracted fields:

```json
{
  "change_text": "Fixed an issue that prevented the social menu from displaying your friends' updated nicknames",
  "heading_path": [
    "Social Issues"
  ],
  "entity": "Social Issues",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "that prevented the social menu from displaying your friends' updated nicknames",
  "source_span_start": 9066,
  "source_span_end": 9159,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Social Issues & Matchmaking` — `rv2_change_5efa9cf8c6e9fa58c92e5429`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Improved the matchmaking logic to better match players with players from nearby regions
```

Extracted fields:

```json
{
  "change_text": "Improved the matchmaking logic to better match players with players from nearby regions",
  "heading_path": [
    "Social Issues & Matchmaking"
  ],
  "entity": "Social Issues & Matchmaking",
  "aspect": "matchmaking_or_ranked",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5442,
  "source_span_end": 5529,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Social Issues & Matchmaking` — `rv2_change_26a0d9f3806fbf406aba4416`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed an issue where the chat history was cleared when going to a mission and returning from it
```

Extracted fields:

```json
{
  "change_text": "Fixed an issue where the chat history was cleared when going to a mission and returning from it",
  "heading_path": [
    "Social Issues & Matchmaking"
  ],
  "entity": "Social Issues & Matchmaking",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "when going to a mission and returning from it",
  "bug_symptom": "the chat history was cleared",
  "source_span_start": 5651,
  "source_span_end": 5746,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Social Menu Fixes` — `rv2_change_3d848dd4222c023c5416df68`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
PC players adding friends through friend codes can no longer show up as “Unknown”
```

Extracted fields:

```json
{
  "change_text": "PC players adding friends through friend codes can no longer show up as “Unknown”",
  "heading_path": [
    "Social Menu Fixes"
  ],
  "entity": "Social Menu Fixes",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2706,
  "source_span_end": 2787,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Social Menu Fixes` — `rv2_change_3be3b91793eb2619ae553fc1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed issue where non-host players could kick others indiscriminately including the host
```

Extracted fields:

```json
{
  "change_text": "Fixed issue where non-host players could kick others indiscriminately including the host",
  "heading_path": [
    "Social Menu Fixes"
  ],
  "entity": "Social Menu Fixes",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "non-host players could kick others indiscriminately including the host",
  "source_span_start": 3320,
  "source_span_end": 3408,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Social Menu fixes` — `rv2_change_4cf6673819806802298fe617`

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

### patch_change — `game=553850;section=Social Menu fixes` — `rv2_change_acfa1839a2f89b450b26a69e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed issues regarding squad menu block button.
```

Extracted fields:

```json
{
  "change_text": "Fixed issues regarding squad menu block button.",
  "heading_path": [
    "Social Menu fixes"
  ],
  "entity": "Social Menu fixes",
  "aspect": "interface_or_settings",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6790,
  "source_span_end": 6837,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Special Shoutout` — `rv2_change_38edcf63c7c5da59ace94b4f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Stimming is no longer interrupted by stagger
```

Extracted fields:

```json
{
  "change_text": "Stimming is no longer interrupted by stagger",
  "heading_path": [
    "Special Shoutout"
  ],
  "entity": "Special Shoutout",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 14065,
  "source_span_end": 14109,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Spread` — `rv2_change_6554d9a1a39e6c514e6a43f3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
This rebalance primarily targets SMGs and sidearms, which previously had noticeably higher spread values
```

Extracted fields:

```json
{
  "change_text": "This rebalance primarily targets SMGs and sidearms, which previously had noticeably higher spread values.",
  "heading_path": [
    "Spread"
  ],
  "entity": "Spread",
  "aspect": "accuracy_or_spread",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2125,
  "source_span_end": 2229,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=StA-11 SMG` — `rv2_change_ed868b61d50e409a75df1efb`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 70 to 90
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 70 to 90",
  "heading_path": [
    "StA-11 SMG"
  ],
  "entity": "StA-11 SMG",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "70",
  "new_value": "90",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4400,
  "source_span_end": 4430,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=StA-11 SMG` — `rv2_change_57d796f083288b4d49e1fc97`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Drag increased from 0.6 to 1.2
```

Extracted fields:

```json
{
  "change_text": "Drag increased from 0.6 to 1.2",
  "heading_path": [
    "StA-11 SMG"
  ],
  "entity": "StA-11 SMG",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "0.6",
  "new_value": "1.2",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4495,
  "source_span_end": 4525,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Stalker` — `rv2_change_c2b80182862a9233c1838c21`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased force strength from 40 to 35 when a tongue attack hits the player
```

Extracted fields:

```json
{
  "change_text": "Decreased force strength from 40 to 35 when a tongue attack hits the player",
  "heading_path": [
    "Stalker"
  ],
  "entity": "Stalker",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "40",
  "new_value": "35",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3492,
  "source_span_end": 3567,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Stalkers` — `rv2_change_557be31ab751eebc444f7759`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage",
  "heading_path": [
    "Stalkers"
  ],
  "entity": "Stalkers",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7693,
  "source_span_end": 7717,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Stalkers` — `rv2_change_db45591a4d4f6f634e1056c0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced durable damage of tongue attack from 50 to 35
```

Extracted fields:

```json
{
  "change_text": "Reduced durable damage of tongue attack from 50 to 35",
  "heading_path": [
    "Stalkers"
  ],
  "entity": "Stalkers",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "50",
  "new_value": "35",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 13001,
  "source_span_end": 13054,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Starting with the good news: there is an incoming update (mid October-ish) where we’ll start chipping away at` — `rv2_change_337ea70a6d97c25eb8c235e3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed the Primary weapon/Side-arm audio that stops during a mission
```

Extracted fields:

```json
{
  "change_text": "Fixed the Primary weapon/Side-arm audio that stops during a mission",
  "heading_path": [
    "Starting with the good news: there is an incoming update (mid October-ish) where we’ll start chipping away at"
  ],
  "entity": "Starting with the good news: there is an incoming update (mid October-ish) where we’ll start chipping away at",
  "aspect": "audio",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 688,
  "source_span_end": 755,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Starting with the good news: there is an incoming update (mid October-ish) where we’ll start chipping away at` — `rv2_change_c99becd2837359844fa5e414`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Short term, we think the above will make a noticeable improvement and beyond that we’ll keep working on the top issues you keep raising
```

Extracted fields:

```json
{
  "change_text": "Short term, we think the above will make a noticeable improvement and beyond that we’ll keep working on the top issues you keep raising.",
  "heading_path": [
    "Starting with the good news: there is an incoming update (mid October-ish) where we’ll start chipping away at"
  ],
  "entity": "Starting with the good news: there is an incoming update (mid October-ish) where we’ll start chipping away at",
  "aspect": null,
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1339,
  "source_span_end": 1474,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=Stratagem Support Weapons` — `rv2_change_d90fa4936a3c74ff12163c16`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Removed the crosshair drift recoil
```

Extracted fields:

```json
{
  "change_text": "Removed the crosshair drift recoil",
  "heading_path": [
    "Stratagem Support Weapons",
    "TX-41 Sterilizer"
  ],
  "entity": "TX-41 Sterilizer",
  "aspect": "accuracy_or_spread",
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1385,
  "source_span_end": 1419,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Stratagem Support Weapons` — `rv2_change_deb8d483e90e23ae084dc82e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Max spare magazines increased from 1 to 2
```

Extracted fields:

```json
{
  "change_text": "Max spare magazines increased from 1 to 2",
  "heading_path": [
    "Stratagem Support Weapons",
    "LAS-98 Laser Cannon"
  ],
  "entity": "LAS-98 Laser Cannon",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "1",
  "new_value": "2",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3483,
  "source_span_end": 3524,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Stratagems` — `rv2_change_195fa025125dc9e506b64845`

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

### patch_change — `game=553850;section=Stratagems` — `rv2_change_c46dd9a32e64f226924bc657`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We will continue working on these changes and include them in a future patc
```

Extracted fields:

```json
{
  "change_text": "We will continue working on these changes and include them in a future patch",
  "heading_path": [
    "Stratagems",
    "A/AC-8 Autocannon Sentry"
  ],
  "entity": "A/AC-8 Autocannon Sentry",
  "aspect": null,
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 8499,
  "source_span_end": 8574,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=Stun Pods` — `rv2_change_dc874ee1b2ae8a7e77cdc70f`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Now affects the Hellpods default explosion as well
```

Extracted fields:

```json
{
  "change_text": "Now affects the Hellpods default explosion as well",
  "heading_path": [
    "Stun Pods"
  ],
  "entity": "Stun Pods",
  "aspect": null,
  "action": "modified",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3145,
  "source_span_end": 3195,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Stun Pods` — `rv2_change_82ef300809641b7b86a9ab6c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Demolition strength decreased from 40 to 20 because we now correctly also additively apply the normal Hellpod explosion
```

Extracted fields:

```json
{
  "change_text": "Demolition strength decreased from 40 to 20 because we now correctly also additively apply the normal Hellpod explosion",
  "heading_path": [
    "Stun Pods"
  ],
  "entity": "Stun Pods",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "40",
  "new_value": "20",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3293,
  "source_span_end": 3412,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Support Weapons` — `rv2_change_925c699d77d0621a32764b07`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Max spare magazines increased from 2 to 3
```

Extracted fields:

```json
{
  "change_text": "Max spare magazines increased from 2 to 3",
  "heading_path": [
    "Support Weapons",
    "Grenade Launcher"
  ],
  "entity": "Grenade Launcher",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "2",
  "new_value": "3",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7753,
  "source_span_end": 7794,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Support Weapons` — `rv2_change_9c6a3c67ae526205ef131480`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Starting spare magazines increased from 1 to 2
```

Extracted fields:

```json
{
  "change_text": "Starting spare magazines increased from 1 to 2",
  "heading_path": [
    "Support Weapons",
    "Grenade Launcher"
  ],
  "entity": "Grenade Launcher",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "1",
  "new_value": "2",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7702,
  "source_span_end": 7748,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Sway` — `rv2_change_b50a7828aff147721ed9443c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
It represents the weapon's inertia and stability—so weapons with lower ergonomics will experience less sway, while those with higher ergonomics will have more
```

Extracted fields:

```json
{
  "change_text": "It represents the weapon's inertia and stability—so weapons with lower ergonomics will experience less sway, while those with higher ergonomics will have more.",
  "heading_path": [
    "Sway"
  ],
  "entity": "Sway",
  "aspect": "rewards_or_progression",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2882,
  "source_span_end": 3040,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=TED-63 Dynamite` — `rv2_change_0aa240165aa2dad39308b02e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased max amount from 3 to 4
```

Extracted fields:

```json
{
  "change_text": "Increased max amount from 3 to 4",
  "heading_path": [
    "TED-63 Dynamite"
  ],
  "entity": "TED-63 Dynamite",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "3",
  "new_value": "4",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7009,
  "source_span_end": 7041,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=TED-63 Dynamite` — `rv2_change_8467f227e2e3847ead568ddd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 700 to 1000
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 700 to 1000",
  "heading_path": [
    "TED-63 Dynamite"
  ],
  "entity": "TED-63 Dynamite",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "700",
  "new_value": "1000",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 6155,
  "source_span_end": 6188,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=TX-41 Sterilizer` — `rv2_change_18c05bf6f6a156e3c058b1a8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased ammo capacity from 100 to 125
```

Extracted fields:

```json
{
  "change_text": "Increased ammo capacity from 100 to 125",
  "heading_path": [
    "TX-41 Sterilizer"
  ],
  "entity": "TX-41 Sterilizer",
  "aspect": "capacity_or_ammunition",
  "action": "increased",
  "direction": "increased",
  "previous_value": "100",
  "new_value": "125",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 11385,
  "source_span_end": 11424,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=TX-41 Sterilizer` — `rv2_change_9bc94aed6fbe68ed7936114d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased starting amount of magazines from 2 to 3
```

Extracted fields:

```json
{
  "change_text": "Increased starting amount of magazines from 2 to 3",
  "heading_path": [
    "TX-41 Sterilizer"
  ],
  "entity": "TX-41 Sterilizer",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "2",
  "new_value": "3",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 11438,
  "source_span_end": 11488,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Terminids` — `rv2_change_4f5589f6960c074449fc941e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Spewer puke now applies the acid effect.
```

Extracted fields:

```json
{
  "change_text": "Spewer puke now applies the acid effect.",
  "heading_path": [
    "Terminids",
    "Bile Spewer and Nursing Spewer"
  ],
  "entity": "Bile Spewer and Nursing Spewer",
  "aspect": null,
  "action": "modified",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 11751,
  "source_span_end": 11791,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Terminids` — `rv2_change_8cc7848d39ef14f8b8d7d8a6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Legs health reduced from 300 to 200
```

Extracted fields:

```json
{
  "change_text": "Legs health reduced from 300 to 200",
  "heading_path": [
    "Terminids",
    "Bile Spewers"
  ],
  "entity": "Bile Spewers",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "300",
  "new_value": "200",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 9785,
  "source_span_end": 9820,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=The Modern Era: SSDs` — `rv2_change_79dd87e7b23a119f6383458a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increasingly, modern games are optimized for the sequential read speeds of SSDs and do not need to rely on the older method of duplicating assets.
```

Extracted fields:

```json
{
  "change_text": "Increasingly, modern games are optimized for the sequential read speeds of SSDs and do not need to rely on the older method of duplicating assets.",
  "heading_path": [
    "The Modern Era: SSDs"
  ],
  "entity": "The Modern Era: SSDs",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2819,
  "source_span_end": 2965,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=The Problem with Mechanical Hard Drives` — `rv2_change_05ec24c290a544a339c9398e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
If the data for these objects is scattered all over the hard drive, the read head has to physically jump around the disk, which adds a lot of time to the loading process
```

Extracted fields:

```json
{
  "change_text": "If the data for these objects is scattered all over the hard drive, the read head has to physically jump around the disk, which adds a lot of time to the loading process.",
  "heading_path": [
    "The Problem with Mechanical Hard Drives"
  ],
  "entity": "The Problem with Mechanical Hard Drives",
  "aspect": "speed_or_movement",
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1625,
  "source_span_end": 1794,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=The change we made` — `rv2_change_6dccfc9cd9f76d4d4455ad10`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased explosion radius 8 to 10m
```

Extracted fields:

```json
{
  "change_text": "Increased explosion radius 8 to 10m",
  "heading_path": [
    "The change we made"
  ],
  "entity": "The change we made",
  "aspect": "range_or_radius",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 10306,
  "source_span_end": 10341,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=The change we made` — `rv2_change_7ea37f02dde4a6388aff593d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased Exomech melee’s force strength from 25 to 40
```

Extracted fields:

```json
{
  "change_text": "Increased Exomech melee’s force strength from 25 to 40",
  "heading_path": [
    "The change we made"
  ],
  "entity": "The change we made",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "25",
  "new_value": "40",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 12475,
  "source_span_end": 12529,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=The new enemy variants earned their teeth.` — `rv2_change_23c3faf471fe39dc48974535`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We also expanded on the Illuminate Fleet system, and grouped all Illuminate enemies into different Fleets, which gives flavour but also adds to the believability and gives you more to consider when choosing loadouts
```

Extracted fields:

```json
{
  "change_text": "We also expanded on the Illuminate Fleet system, and grouped all Illuminate enemies into different Fleets, which gives flavour but also adds to the believability and gives you more to consider when choosing loadouts.",
  "heading_path": [
    "The new enemy variants earned their teeth."
  ],
  "entity": "The new enemy variants earned their teeth.",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2388,
  "source_span_end": 2603,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=The new enemy variants earned their teeth.` — `rv2_change_0b39b62f62348767bc9c799b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Going forward, this sort of thing is what we’re considering for all factions
```

Extracted fields:

```json
{
  "change_text": "Going forward, this sort of thing is what we’re considering for all factions.",
  "heading_path": [
    "The new enemy variants earned their teeth."
  ],
  "entity": "The new enemy variants earned their teeth.",
  "aspect": null,
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2605,
  "source_span_end": 2681,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=These big beats should run for longer, and the endings should be more clearly shaped by the community.` — `rv2_change_03ec2d4e245165c45e5c88f5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
That's the part we're working on iterating on for the next big update
```

Extracted fields:

```json
{
  "change_text": "That's the part we're working on iterating on for the next big update.",
  "heading_path": [
    "These big beats should run for longer, and the endings should be more clearly shaped by the community."
  ],
  "entity": "These big beats should run for longer, and the endings should be more clearly shaped by the community.",
  "aspect": null,
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4844,
  "source_span_end": 4913,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=This update includes` — `rv2_change_c1c45f79e70bcbf7e4555d30`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
- Increased Level Cap
```

Extracted fields:

```json
{
  "change_text": "- Increased Level Cap",
  "heading_path": [
    "This update includes"
  ],
  "entity": "This update includes",
  "aspect": "map_or_level",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 377,
  "source_span_end": 398,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=This update includes` — `rv2_change_ba6f16963209f7f437b79687`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
-General fixes and stability improvements.
```

Extracted fields:

```json
{
  "change_text": "-General fixes and stability improvements.",
  "heading_path": [
    "This update includes"
  ],
  "entity": "This update includes",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 334,
  "source_span_end": 376,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Throwables` — `rv2_change_1ee22cd9a3755249c673c538`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased stagger impulse 15 -> 0
```

Extracted fields:

```json
{
  "change_text": "Decreased stagger impulse 15 -> 0",
  "heading_path": [
    "Throwables",
    "Urchin"
  ],
  "entity": "Urchin",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3800,
  "source_span_end": 3833,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Throwables` — `rv2_change_e60e84b8f9de1935f264bcdc`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Demolition strength increased from 10 to 30
```

Extracted fields:

```json
{
  "change_text": "Demolition strength increased from 10 to 30",
  "heading_path": [
    "Throwables",
    "G4 Gas Grenade"
  ],
  "entity": "G4 Gas Grenade",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": "10",
  "new_value": "30",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2807,
  "source_span_end": 2850,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Throwing knifes` — `rv2_change_99d9f7f9ba1cea0ac70e0cdc`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Durable damage increased from 100 to 150
```

Extracted fields:

```json
{
  "change_text": "Durable damage increased from 100 to 150",
  "heading_path": [
    "Throwing knifes"
  ],
  "entity": "Throwing knifes",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "100",
  "new_value": "150",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7274,
  "source_span_end": 7314,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Throwing knifes` — `rv2_change_c6985e17e7abeda26f87ddbf`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage increased from 250 to 300
```

Extracted fields:

```json
{
  "change_text": "Damage increased from 250 to 300",
  "heading_path": [
    "Throwing knifes"
  ],
  "entity": "Throwing knifes",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "250",
  "new_value": "300",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 7228,
  "source_span_end": 7260,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Update` — `rv2_change_2a5359822585f5b9e1aa2178`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Our testing shows that for the small percentage of players still using mechanical hard disk drives, mission loading times have only increased by a few seconds in the worst cases
```

Extracted fields:

```json
{
  "change_text": "Our testing shows that for the small percentage of players still using mechanical hard disk drives, mission loading times have only increased by a few seconds in the worst cases.",
  "heading_path": [
    "Update"
  ],
  "entity": "Update",
  "aspect": "content_or_feature",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1223,
  "source_span_end": 1400,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=Update` — `rv2_change_ef4ed16ee3c8db7f52587d4c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
While this was a good start, our short term fixes have not been enough to keep up with all of the new content in the latest patch
```

Extracted fields:

```json
{
  "change_text": "While this was a good start, our short term fixes have not been enough to keep up with all of the new content in the latest patch.",
  "heading_path": [
    "Update"
  ],
  "entity": "Update",
  "aspect": "content_or_feature",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 573,
  "source_span_end": 702,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=VG-70 Variable` — `rv2_change_75ab55361250fad572de0c3c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased durable damage 20 to 23
```

Extracted fields:

```json
{
  "change_text": "Increased durable damage 20 to 23",
  "heading_path": [
    "VG-70 Variable"
  ],
  "entity": "VG-70 Variable",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2485,
  "source_span_end": 2518,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Vehicle armor and enemies AP rebalance` — `rv2_change_4f8ea362eb151afa11bb7ea0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Some enemies have had their durable damage reduced
```

Extracted fields:

```json
{
  "change_text": "Some enemies have had their durable damage reduced",
  "heading_path": [
    "Vehicle armor and enemies AP rebalance"
  ],
  "entity": "Vehicle armor and enemies AP rebalance",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3301,
  "source_span_end": 3351,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Vehicle armor and enemies AP rebalance` — `rv2_change_e31cfef288abf31d75d1c0d3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Some enemies have received increased armor penetration values so they can deal with the vehicles, but not all.
```

Extracted fields:

```json
{
  "change_text": "Some enemies have received increased armor penetration values so they can deal with the vehicles, but not all.",
  "heading_path": [
    "Vehicle armor and enemies AP rebalance"
  ],
  "entity": "Vehicle armor and enemies AP rebalance",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 2760,
  "source_span_end": 2870,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Vox Engine` — `rv2_change_dafbb99bd150d8a0ca0b7e43`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced the armor of their cannon turrets from 5 to 4
```

Extracted fields:

```json
{
  "change_text": "Reduced the armor of their cannon turrets from 5 to 4",
  "heading_path": [
    "Vox Engine"
  ],
  "entity": "Vox Engine",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "5",
  "new_value": "4",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 13486,
  "source_span_end": 13539,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Vox Engine` — `rv2_change_638001037d3c8fd9c9ece7aa`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced health of their cannon turrets from 8000 down to 3500
```

Extracted fields:

```json
{
  "change_text": "Reduced health of their cannon turrets from 8000 down to 3500",
  "heading_path": [
    "Vox Engine"
  ],
  "entity": "Vox Engine",
  "aspect": "health_or_durability",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "8000",
  "new_value": "3500",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 13411,
  "source_span_end": 13472,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=War Strider` — `rv2_change_a1e641a14401da75aaf5c7e7`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Added weak spots aim for the eyes and the vents on the back
```

Extracted fields:

```json
{
  "change_text": "Added weak spots aim for the eyes and the vents on the back",
  "heading_path": [
    "War Strider"
  ],
  "entity": "War Strider",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 13224,
  "source_span_end": 13283,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=War Strider` — `rv2_change_7bcfc28c555aea850d567778`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Removed ragdolling from its projectiles explosions
```

Extracted fields:

```json
{
  "change_text": "Removed ragdolling from its projectiles explosions",
  "heading_path": [
    "War Strider"
  ],
  "entity": "War Strider",
  "aspect": null,
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 13160,
  "source_span_end": 13210,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=War strider` — `rv2_change_bc54c0fcd20525b4d09956fd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Decreased force strength on grenade explosion from 50 to 30
```

Extracted fields:

```json
{
  "change_text": "Decreased force strength on grenade explosion from 50 to 30",
  "heading_path": [
    "War strider"
  ],
  "entity": "War strider",
  "aspect": null,
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "50",
  "new_value": "30",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3198,
  "source_span_end": 3257,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Warrior` — `rv2_change_3762ad7b431db0250478974d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Damage needed to gib Warriors increased from 500 to 750 damage
```

Extracted fields:

```json
{
  "change_text": "Damage needed to gib Warriors increased from 500 to 750 damage",
  "heading_path": [
    "Warrior"
  ],
  "entity": "Warrior",
  "aspect": "damage_or_attack_power",
  "action": "increased",
  "direction": "increased",
  "previous_value": "500",
  "new_value": "750",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3607,
  "source_span_end": 3669,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Warriors and spewers` — `rv2_change_eee172f3c9c628dc3534f032`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Reduced durable damage of normal attack from 80 to 65
```

Extracted fields:

```json
{
  "change_text": "Reduced durable damage of normal attack from 80 to 65",
  "heading_path": [
    "Warriors and spewers"
  ],
  "entity": "Warriors and spewers",
  "aspect": "damage_or_attack_power",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": "80",
  "new_value": "65",
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 12891,
  "source_span_end": 12944,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Weapon & Stratagem Fixes` — `rv2_change_b9050cb42e2041332c57a55e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a bug where picking up an SSSD drive would cause ballistic shields to be dropped.
```

Extracted fields:

```json
{
  "change_text": "Fixed a bug where picking up an SSSD drive would cause ballistic shields to be dropped.",
  "heading_path": [
    "Weapon & Stratagem Fixes",
    "SH-20 Ballistic Shield Backpack"
  ],
  "entity": "SH-20 Ballistic Shield Backpack",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "picking up an SSSD drive would cause ballistic shields to be dropped",
  "source_span_start": 5808,
  "source_span_end": 5895,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Weapon & Stratagem Fixes` — `rv2_change_2e43a31ebbb869bc5eb2ba8e`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed ballistic shield to not collide with player as long as wielded.
```

Extracted fields:

```json
{
  "change_text": "Fixed ballistic shield to not collide with player as long as wielded.",
  "heading_path": [
    "Weapon & Stratagem Fixes",
    "SH-20 Ballistic Shield Backpack"
  ],
  "entity": "SH-20 Ballistic Shield Backpack",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5900,
  "source_span_end": 5969,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Weapons` — `rv2_change_e4cfdbcd90f13a1621ed78bc`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed armor penetration values in the Stats Menu for CQC-5 Combat Hatchet, CQC-30 Stun Baton,CQC-19 Stun Lance, CQC-2 Saber, CQC-1 One True Flag and the G-7 Pineapple grenade
```

Extracted fields:

```json
{
  "change_text": "Fixed armor penetration values in the Stats Menu for CQC-5 Combat Hatchet, CQC-30 Stun Baton,CQC-19 Stun Lance, CQC-2 Saber, CQC-1 One True Flag and the G-7 Pineapple grenade",
  "heading_path": [
    "Weapons"
  ],
  "entity": "CQC-5 Combat Hatchet",
  "aspect": "gameplay",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 14851,
  "source_span_end": 15025,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Weapons` — `rv2_change_b4bd69907621a386984e1db4`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Improved initial bullet alignment while strafing and riding in vehicles
```

Extracted fields:

```json
{
  "change_text": "Improved initial bullet alignment while strafing and riding in vehicles",
  "heading_path": [
    "Weapons"
  ],
  "entity": null,
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 15105,
  "source_span_end": 15176,
  "source_span_verified": true,
  "quality_flags": [
    "entity_unresolved",
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Weapons & Stratagem Fixes` — `rv2_change_dab476b236455c3f96ea62da`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed the StA X3 WASP Launcher firemode - it will no longer fire in Semi-Auto mode after switching from Artillery firing mode
```

Extracted fields:

```json
{
  "change_text": "Fixed the StA X3 WASP Launcher firemode - it will no longer fire in Semi-Auto mode after switching from Artillery firing mode",
  "heading_path": [
    "Weapons & Stratagem Fixes"
  ],
  "entity": "Weapons & Stratagem Fixes",
  "aspect": "content_or_feature",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5078,
  "source_span_end": 5203,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Weapons & Stratagem Fixes` — `rv2_change_051e8c0a325d15873af223c5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed display related to no ammo being shown for Infinite Ammo weapons
```

Extracted fields:

```json
{
  "change_text": "Fixed display related to no ammo being shown for Infinite Ammo weapons",
  "heading_path": [
    "Weapons & Stratagem Fixes"
  ],
  "entity": "Weapons & Stratagem Fixes",
  "aspect": "capacity_or_ammunition",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5790,
  "source_span_end": 5860,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Weapons Stratagems & Boosters` — `rv2_change_d186135c18a88765529d50cc`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed issue with the AR-32 PACIFIER being unable to fire for a second after reloading
```

Extracted fields:

```json
{
  "change_text": "Fixed issue with the AR-32 PACIFIER being unable to fire for a second after reloading",
  "heading_path": [
    "Weapons Stratagems & Boosters"
  ],
  "entity": "Weapons Stratagems & Boosters",
  "aspect": "bug_or_functionality",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": "after reloading",
  "bug_symptom": "with the AR-32 PACIFIER being unable to fire for a second",
  "source_span_start": 1197,
  "source_span_end": 1282,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=Weapons Stratagems & Boosters` — `rv2_change_d553b5f2ed0b23c612e096c0`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The Laser turret now displays correct heat build up
```

Extracted fields:

```json
{
  "change_text": "The Laser turret now displays correct heat build up",
  "heading_path": [
    "Weapons Stratagems & Boosters"
  ],
  "entity": "Weapons Stratagems & Boosters",
  "aspect": null,
  "action": "modified",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 817,
  "source_span_end": 868,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Weapons and Stratagems` — `rv2_change_ab94513ba11e4c3270488797`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed weapons being unable to fire after stimming while using a mounted weapon.
```

Extracted fields:

```json
{
  "change_text": "Fixed weapons being unable to fire after stimming while using a mounted weapon.",
  "heading_path": [
    "Weapons and Stratagems"
  ],
  "entity": "Weapons and Stratagems",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 302,
  "source_span_end": 381,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=Weapons and Stratagems` — `rv2_change_07b13b6b4437b580941b7adb`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed Weapons with selectable ammo (Recoilless Rifle, Autocannon, etc) having their icons overwritten by the Warrant’s “Guided/Unguided” Mode.
```

Extracted fields:

```json
{
  "change_text": "Fixed Weapons with selectable ammo (Recoilless Rifle, Autocannon, etc) having their icons overwritten by the Warrant’s “Guided/Unguided” Mode.",
  "heading_path": [
    "Weapons and Stratagems"
  ],
  "entity": "Weapons and Stratagems",
  "aspect": "capacity_or_ammunition",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1365,
  "source_span_end": 1507,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=We’re excited to share more details about our upcoming update, which will include significant changes aimed at refining and improving your experience in Helldivers 2. This includes` — `rv2_change_a29d1739c672d67210e0c745`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We are overhauling a number of different enemies to make them feel more rewarding to kill when you use the proper tools to handle them but ensure they still feel formidable. Enemy bots, including Hulks, will have lower armor, and the number of rockets fired by enemies like the Devastator and Gunship will be limited, making combat more balanced. The armor values of particularly tough bug enemies like the Charger, Impaler, and Bile Titan will also be reduced.
```

Extracted fields:

```json
{
  "change_text": "We are overhauling a number of different enemies to make them feel more rewarding to kill when you use the proper tools to handle them but ensure they still feel formidable. Enemy bots, including Hulks, will have lower armor, and the number of rockets fired by enemies like the Devastator and Gunship will be limited, making combat more balanced. The armor values of particularly tough bug enemies like the Charger, Impaler, and Bile Titan will also be reduced.",
  "heading_path": [
    "We’re excited to share more details about our upcoming update, which will include significant changes aimed at refining and improving your experience in Helldivers 2. This includes"
  ],
  "entity": "We’re excited to share more details about our upcoming update, which will include significant changes aimed at refining and improving your experience in Helldivers 2. This includes",
  "aspect": "gameplay",
  "action": "decreased",
  "direction": "decreased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 829,
  "source_span_end": 1290,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=We’re excited to share more details about our upcoming update, which will include significant changes aimed at refining and improving your experience in Helldivers 2. This includes` — `rv2_change_bc01d63e8ef46426a90d581b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Stay tuned for more updates in the coming weeks as we work together to make Helldivers 2 the best it can be
```

Extracted fields:

```json
{
  "change_text": "Stay tuned for more updates in the coming weeks as we work together to make Helldivers 2 the best it can be.",
  "heading_path": [
    "We’re excited to share more details about our upcoming update, which will include significant changes aimed at refining and improving your experience in Helldivers 2. This includes"
  ],
  "entity": "We’re excited to share more details about our upcoming update, which will include significant changes aimed at refining and improving your experience in Helldivers 2. This includes",
  "aspect": null,
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1933,
  "source_span_end": 2040,
  "source_span_verified": false,
  "quality_flags": [
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=What are the Helldivers 2 system requirements?` — `rv2_change_029189d4edcc76b5ee18842a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
The follow-up to indie hit Helldivers is past its initial rocky launch and Democracy is still in need of saving, if you can find a spot in its newly expanded online servers.
```

Extracted fields:

```json
{
  "change_text": "The follow-up to indie hit Helldivers is past its initial rocky launch and Democracy is still in need of saving, if you can find a spot in its newly expanded online servers.",
  "heading_path": [
    "What are the Helldivers 2 system requirements?"
  ],
  "entity": "What are the Helldivers 2 system requirements?",
  "aspect": null,
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 208,
  "source_span_end": 381,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=What are the Helldivers 2 system requirements?` — `rv2_change_2af07642112c8349db4347a1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
While Helldivers 2 isn't quite optimized for the <a href="https://www.pcgamesn.com/steam-deck/helldivers-2">Steam Deck</a>, its general PC performance, when you meet its requirements, is very impressive
```

Extracted fields:

```json
{
  "change_text": "While Helldivers 2 isn't quite optimized for the Steam Deck, its general PC performance, when you meet its requirements, is very impressive.",
  "heading_path": [
    "What are the Helldivers 2 system requirements?"
  ],
  "entity": "What are the Helldivers 2 system requirements?",
  "aspect": "performance_or_network",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 659,
  "source_span_end": 861,
  "source_span_verified": false,
  "quality_flags": [
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=What are the best Helldivers 2 builds?` — `rv2_change_831871466e7c3bb1d9ea3432`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Helldivers 2 patch 1.000.10 fixes crashes, PC black screens, and more
```

Extracted fields:

```json
{
  "change_text": "Helldivers 2 patch 1.000.10 fixes crashes, PC black screens, and more",
  "heading_path": [
    "What are the best Helldivers 2 builds?",
    "RELATED LINKS"
  ],
  "entity": "RELATED LINKS",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1366,
  "source_span_end": 1435,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=What is the team focusing on right now? What are their current priorities?` — `rv2_change_c2d9cf0a1b4edac24fc6c9f3`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We’ve significantly expanded the team working in this area, reflecting how important these long-term systems are for the overall player experience.
```

Extracted fields:

```json
{
  "change_text": "We’ve significantly expanded the team working in this area, reflecting how important these long-term systems are for the overall player experience.",
  "heading_path": [
    "What is the team focusing on right now? What are their current priorities?"
  ],
  "entity": "What is the team focusing on right now? What are their current priorities?",
  "aspect": "rewards_or_progression",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 757,
  "source_span_end": 904,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=When will we get new red stratagems and ship modules?` — `rv2_change_f109e0093e633c13d856c288`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We’ve got teams actively working on both new red stratagems, evolving ships, and player progression to level 150… and beyond!
```

Extracted fields:

```json
{
  "change_text": "We’ve got teams actively working on both new red stratagems, evolving ships, and player progression to level 150… and beyond!",
  "heading_path": [
    "When will we get new red stratagems and ship modules?"
  ],
  "entity": "When will we get new red stratagems and ship modules?",
  "aspect": "map_or_level",
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 5436,
  "source_span_end": 5561,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=unsectioned` — `rv2_change_b58735065b1ca4b945dd8fa2`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
A new <a href="https://www.vg247.com/games/helldivers-2">Helldivers 2</a> patch has been implemented into the game which nerfs heavy enemies, with an emphasis on Terminids like Chargers and Bile Titans.
```

Extracted fields:

```json
{
  "change_text": "A new Helldivers 2 patch has been implemented into the game which nerfs heavy enemies, with an emphasis on Terminids like Chargers and Bile Titans.",
  "heading_path": [],
  "entity": "Terminids",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 148,
  "source_span_end": 350,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=unsectioned` — `rv2_change_c7916c4e50fce47670159bea`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Arrowhead has also now laid out a 60-day plan to improve the game and overhaul some of its practices
```

Extracted fields:

```json
{
  "change_text": "Arrowhead has also now laid out a 60-day plan to improve the game and overhaul some of its practices.",
  "heading_path": [],
  "entity": null,
  "aspect": null,
  "action": "acknowledged",
  "direction": null,
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "acknowledged_or_planned",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 442,
  "source_span_end": 542,
  "source_span_verified": false,
  "quality_flags": [
    "entity_unresolved",
    "aspect_unresolved",
    "source_span_invalid"
  ]
}
```

### patch_change — `game=553850;section=⚖️ Balancing` — `rv2_change_21a3bea41b611b535b33ecbe`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Increased the health of Mega Shrieker nests.
```

Extracted fields:

```json
{
  "change_text": "Increased the health of Mega Shrieker nests.",
  "heading_path": [
    "⚖️ Balancing"
  ],
  "entity": "⚖️ Balancing",
  "aspect": "health_or_durability",
  "action": "increased",
  "direction": "increased",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 509,
  "source_span_end": 553,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=🌍 Overview` — `rv2_change_6a5d612db861c49ca09b8b00`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixes
```

Extracted fields:

```json
{
  "change_text": "Fixes",
  "heading_path": [
    "🌍 Overview"
  ],
  "entity": "🌍 Overview",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 229,
  "source_span_end": 234,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=🌍 Overview` — `rv2_change_27d1cc79c13a57af99ce396b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Mission Fixes
```

Extracted fields:

```json
{
  "change_text": "Mission Fixes",
  "heading_path": [
    "🌍 Overview"
  ],
  "entity": "🌍 Overview",
  "aspect": "content_or_feature",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 200,
  "source_span_end": 213,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=🎮 Gameplay` — `rv2_change_dfb8adfdb47f35ebb8bb7395`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed instances of flickering textures in various city locations
```

Extracted fields:

```json
{
  "change_text": "Fixed instances of flickering textures in various city locations",
  "heading_path": [
    "🎮 Gameplay",
    "Keybind options for quick weapon function"
  ],
  "entity": "Keybind options for quick weapon function",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4626,
  "source_span_end": 4690,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=🎮 Gameplay` — `rv2_change_dd77a1e1944c4cffeb742f14`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We updated how First Person View (FPV) works with the intention of improving the aiming experience across different FOV settings (Field of view).
```

Extracted fields:

```json
{
  "change_text": "We updated how First Person View (FPV) works with the intention of improving the aiming experience across different FOV settings (Field of view).",
  "heading_path": [
    "🎮 Gameplay",
    "Keybind options for quick weapon function"
  ],
  "entity": "Keybind options for quick weapon function",
  "aspect": "interface_or_settings",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 4245,
  "source_span_end": 4390,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=📍 Patch Highlights` — `rv2_change_483086a43442e87329573145`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Chinese VO has been added to Helldivers 2!
```

Extracted fields:

```json
{
  "change_text": "Chinese VO has been added to Helldivers 2!",
  "heading_path": [
    "📍 Patch Highlights"
  ],
  "entity": "📍 Patch Highlights",
  "aspect": null,
  "action": "added",
  "direction": "added",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1055,
  "source_span_end": 1097,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=🔧 Fixes` — `rv2_change_74964fed5a50d77016626d2a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed an issue where status effect damage were attempting to apply more times than intended
```

Extracted fields:

```json
{
  "change_text": "Fixed an issue where status effect damage were attempting to apply more times than intended",
  "heading_path": [
    "🔧 Fixes",
    "Enemies"
  ],
  "entity": "Enemies",
  "aspect": "damage_or_attack_power",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": "status effect damage were attempting to apply more times than intended",
  "source_span_start": 4485,
  "source_span_end": 4576,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=🔧 Fixes` — `rv2_change_24ff3d6366cfff9c442825f8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed a rare instance where Primary Weapon audio would go missing
```

Extracted fields:

```json
{
  "change_text": "Fixed a rare instance where Primary Weapon audio would go missing",
  "heading_path": [
    "🔧 Fixes"
  ],
  "entity": "🔧 Fixes",
  "aspect": "audio",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1009,
  "source_span_end": 1074,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=🔧Fixes` — `rv2_change_bdd21cd6107fe321daca41b8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Improved VRAM management on PC to improve performance on systems with limited VRAM.
```

Extracted fields:

```json
{
  "change_text": "Improved VRAM management on PC to improve performance on systems with limited VRAM.",
  "heading_path": [
    "🔧Fixes"
  ],
  "entity": "🔧Fixes",
  "aspect": "performance_or_network",
  "action": "adjusted",
  "direction": "modified",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1789,
  "source_span_end": 1872,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=🔧Fixes` — `rv2_change_75e5b97b9b996227a6d840de`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Fixed multiple rendering issues and improved performance and image quality across all platforms.
```

Extracted fields:

```json
{
  "change_text": "Fixed multiple rendering issues and improved performance and image quality across all platforms.",
  "heading_path": [
    "🔧Fixes"
  ],
  "entity": "🔧Fixes",
  "aspect": "performance_or_network",
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1479,
  "source_span_end": 1575,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=🤝 Community Feedback Changes` — `rv2_change_23ea9ba8c01375c2f45f2cda`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
We’re trying out a new section to shout out some of the fixes and changes that are high up on the community’s wishlist!
```

Extracted fields:

```json
{
  "change_text": "We’re trying out a new section to shout out some of the fixes and changes that are high up on the community’s wishlist!",
  "heading_path": [
    "🤝 Community Feedback Changes"
  ],
  "entity": "🤝 Community Feedback Changes",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 3330,
  "source_span_end": 3449,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=🤝 Community Feedback Changes` — `rv2_change_2c18b037952db6e9eb9f1de9`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Players can no longer get stuck in a state where they are unable to be reinforced even after another player throws a reinforcement stratagem or the whole squad dies. This was rare but could happen under poor network conditions
```

Extracted fields:

```json
{
  "change_text": "Players can no longer get stuck in a state where they are unable to be reinforced even after another player throws a reinforcement stratagem or the whole squad dies. This was rare but could happen under poor network conditions",
  "heading_path": [
    "🤝 Community Feedback Changes"
  ],
  "entity": "🤝 Community Feedback Changes",
  "aspect": "performance_or_network",
  "action": "removed",
  "direction": "removed",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_change",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 266,
  "source_span_end": 492,
  "source_span_verified": true,
  "quality_flags": []
}
```

### patch_change — `game=553850;section=🧠 Known Issues` — `rv2_change_d9976557e1016d698c700e1c`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Listed below are significant issues that are being worked on and were either introduced by this patch or are from a previous version and have not yet been fixed.
```

Extracted fields:

```json
{
  "change_text": "Listed below are significant issues that are being worked on and were either introduced by this patch or are from a previous version and have not yet been fixed.",
  "heading_path": [
    "🧠 Known Issues"
  ],
  "entity": "🧠 Known Issues",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 1612,
  "source_span_end": 1773,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### patch_change — `game=553850;section=🧠 Known Issues` — `rv2_change_db9b74ecd495c8c11aa760c5`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
These are issues that were either introduced by this patch and are being worked on, or are from a previous version and have not yet been fixed.
```

Extracted fields:

```json
{
  "change_text": "These are issues that were either introduced by this patch and are being worked on, or are from a previous version and have not yet been fixed.",
  "heading_path": [
    "🧠 Known Issues"
  ],
  "entity": "🧠 Known Issues",
  "aspect": null,
  "action": "fixed",
  "direction": "corrected",
  "previous_value": null,
  "new_value": null,
  "numeric_delta": null,
  "developer_status": "implemented_bug_fix",
  "bug_trigger": null,
  "bug_symptom": null,
  "source_span_start": 91,
  "source_span_end": 234,
  "source_span_verified": true,
  "quality_flags": [
    "aspect_unresolved"
  ]
}
```

### review_claim — `game=730;language=brazilian` — `rv2_claim_ab48e0335fd9675574d6a569`

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

### review_claim — `game=730;language=brazilian` — `rv2_claim_d708e1c56d5e8c344ff2d911`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Top
```

Extracted fields:

```json
{
  "claim_text_original": "Top",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "Top",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 3,
  "review_revision_id": "rv1_review_revision_570f7a88be0c036af4dfad20",
  "review_created_at_utc": "2024-11-13 22:42:21+00:00",
  "review_updated_at_utc": "2024-11-13 22:42:21+00:00"
}
```

### review_claim — `game=730;language=bulgarian` — `rv2_claim_5e83a64cad8ea8e1078dddfd`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
trash games
```

Extracted fields:

```json
{
  "claim_text_original": "trash games",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "trash games",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 11,
  "review_revision_id": "rv1_review_revision_e8718e55c85b8781fc661947",
  "review_created_at_utc": "2024-11-13 22:22:37+00:00",
  "review_updated_at_utc": "2024-11-13 22:22:37+00:00"
}
```

### review_claim — `game=730;language=czech` — `rv2_claim_d888dee9be20adb9f306ac4b`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
všetko
```

Extracted fields:

```json
{
  "claim_text_original": "všetko",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "všetko",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 6,
  "review_revision_id": "rv1_review_revision_7dd3fbaff8f7cf2624ddaf34",
  "review_created_at_utc": "2024-11-13 22:31:48+00:00",
  "review_updated_at_utc": "2024-11-13 22:31:48+00:00"
}
```

### review_claim — `game=730;language=english` — `rv2_claim_d2e8a405420379c7ef333672`

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

### review_claim — `game=730;language=english` — `rv2_claim_8a66ea13973ccadeb37068a6`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
Thank You Valve For Making Our Childhood Great.
```

Extracted fields:

```json
{
  "claim_text_original": "Thank You Valve For Making Our Childhood Great.",
  "referenced_entity": "valve",
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

### review_claim — `game=730;language=french` — `rv2_claim_084c9ea118a9f94249ceada0`

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

### review_claim — `game=730;language=french` — `rv2_claim_4c54cc1993264c8a16f545ea`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
festival du cheat et de l'insulte en Russe ou je ne sais quelle langue...
```

Extracted fields:

```json
{
  "claim_text_original": "festival du cheat et de l'insulte en Russe ou je ne sais quelle langue...",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "festival du cheat et de l'insulte en Russe ou je ne sais quelle langue...",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.48,
  "claim_span_start": 0,
  "claim_span_end": 73,
  "review_revision_id": "rv1_review_revision_044c7acaaacb1af0aa9874cb",
  "review_created_at_utc": "2024-11-13 22:41:31+00:00",
  "review_updated_at_utc": "2024-11-13 22:41:31+00:00"
}
```

### review_claim — `game=730;language=polish` — `rv2_claim_0af21c1528361fb51a1f7528`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
fajna gierka
```

Extracted fields:

```json
{
  "claim_text_original": "fajna gierka",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "fajna gierka",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 12,
  "review_revision_id": "rv1_review_revision_328b81b937b81b9423eda26f",
  "review_created_at_utc": "2024-11-13 23:15:25+00:00",
  "review_updated_at_utc": "2024-11-13 23:15:25+00:00"
}
```

### review_claim — `game=730;language=romanian` — `rv2_claim_7ffdad724666898603ff47f1`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
the  best  shet  in world -> (first review in *Posted: 14 Nov, 2024 @ 1:18am*)
the shetest shet in world -> (second review in *Posted: 18.08.2026 @ 8.55am*)
```

Extracted fields:

```json
{
  "claim_text_original": "the  best  shet  in world -> (first review in *Posted: 14 Nov, 2024 @ 1:18am*)\nthe shetest shet in world -> (second review in *Posted: 18.08.2026 @ 8.55am*)",
  "referenced_entity": "the",
  "aspect": null,
  "opinion_or_issue": "the  best  shet  in world -> (first review in *Posted: 14 Nov, 2024 @ 1:18am*)\nthe shetest shet in world -> (second review in *Posted: 18.08.2026 @ 8.55am*)",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.68,
  "claim_span_start": 0,
  "claim_span_end": 156,
  "review_revision_id": "rv1_review_revision_4376e8fa7533724b94ddb73f",
  "review_created_at_utc": "2024-11-13 23:18:50+00:00",
  "review_updated_at_utc": "2026-08-18 05:56:15+00:00"
}
```

### review_claim — `game=730;language=russian` — `rv2_claim_68032c4a9fb08f379e3293a1`

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

### review_claim — `game=730;language=russian` — `rv2_claim_b0bf0cffd4a2138c721859ca`

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

### review_claim — `game=730;language=spanish` — `rv2_claim_8c7ef58fdca941a8d04c2bf8`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
no me gusta
```

Extracted fields:

```json
{
  "claim_text_original": "no me gusta",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "no me gusta",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": true,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 11,
  "review_revision_id": "rv1_review_revision_f25168ec2a097e62a9fb931f",
  "review_created_at_utc": "2024-11-13 22:42:14+00:00",
  "review_updated_at_utc": "2024-11-20 22:05:00+00:00"
}
```

### review_claim — `game=730;language=spanish` — `rv2_claim_c85a93f1297aa2a2308c8897`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
ya po
```

Extracted fields:

```json
{
  "claim_text_original": "ya po",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "ya po",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 5,
  "review_revision_id": "rv1_review_revision_2c1037039bda5c8d03addc05",
  "review_created_at_utc": "2024-11-13 22:38:31+00:00",
  "review_updated_at_utc": "2025-12-13 22:06:47+00:00"
}
```

### review_claim — `game=730;language=swedish` — `rv2_claim_a3164cec87a62b782a9b6827`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
bra spel
```

Extracted fields:

```json
{
  "claim_text_original": "bra spel",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "bra spel",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 8,
  "review_revision_id": "rv1_review_revision_4c8879e0ecf995cc02ec49f0",
  "review_created_at_utc": "2024-11-13 23:01:16+00:00",
  "review_updated_at_utc": "2024-11-13 23:01:16+00:00"
}
```

### review_claim — `game=730;language=turkish` — `rv2_claim_4c96f509422b433d634e741a`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
asdasd
```

Extracted fields:

```json
{
  "claim_text_original": "asdasd",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "asdasd",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 6,
  "review_revision_id": "rv1_review_revision_46d34a7dc085ce716e6b0bf8",
  "review_created_at_utc": "2024-11-13 23:16:09+00:00",
  "review_updated_at_utc": "2024-11-13 23:16:09+00:00"
}
```

### review_claim — `game=730;language=turkish` — `rv2_claim_39a7b87bc4716cc170be5c9d`

Manual review status: `awaiting_manual_inspection`.

Original source excerpt:

```text
hayatbitti.
```

Extracted fields:

```json
{
  "claim_text_original": "hayatbitti.",
  "referenced_entity": null,
  "aspect": null,
  "opinion_or_issue": "hayatbitti.",
  "opinion_terms": [],
  "polarity": null,
  "temporal_cues": [],
  "negated": false,
  "uncertain": false,
  "extraction_confidence": 0.42,
  "claim_span_start": 0,
  "claim_span_end": 11,
  "review_revision_id": "rv1_review_revision_47cd350e32ea33b342caa4e6",
  "review_created_at_utc": "2024-11-13 22:18:59+00:00",
  "review_updated_at_utc": "2025-05-18 13:15:44+00:00"
}
```

## Output paths

The companion `manifest.json` records source table hashes, schema/extractor versions, and row counts. Parquet outputs are stored under the dataset directory printed by the CLI.
