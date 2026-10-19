# Stage 2 handoff — atomic changes and review claims

Stage 2 is complete. It transforms the approved Stage 1 normalized snapshot into separate announcement, atomic-change, review-claim, vocabulary, and temporal datasets. It does **not** join changes to claims, produce relevance judgments, or make training labels.

## Reproduce this run

```bash
uv run --all-extras steam-relevance stage2 extract \
  --source-run rv1-20261019T031033900187Z-a468b544
```

This command is offline. The selected Stage 1 files are hash-recorded in the manifest; the Stage 2 dataset ID is `rv2-d52a3f9f1a3de2fe80aa098f` (schema `2.7.0`).

- Parquet datasets and `manual_review.json`: `data/relevance_v1/processed/stage2/rv2-d52a3f9f1a3de2fe80aa098f/`
- Full quality report with concrete examples and the audited sample: `reports/relevance_v1/stage2/rv2-d52a3f9f1a3de2fe80aa098f/quality_report.md`
- Machine-readable report and per-game/per-patch coverage: beside the report as `quality_report.json`, `game_extraction_coverage.csv`, and `patch_extraction_coverage.csv`
- Table field meanings: [`DATA_CONTRACTS.md`](DATA_CONTRACTS.md)

## Output counts

| Output | Rows |
| --- | ---: |
| Announcement classifications | 1,331 |
| Atomic patch changes | 3,154 |
| Review claim spans | 297,500 |
| Game terminology entries | 2,000 (up to 500 per game) |
| Rule-eligible patch episodes | 316 |
| Patch review-window segments | 60 |
| Time-window membership rows | 133,842 |
| Overlapping episode pairs | 1,161 |
| Same-entity temporal ambiguities | 662 |
| Stratified QA examples inspected | 51 (27 changes, 24 claims) |

The 297,500 claim spans come from 167,706 non-empty review revisions in the Stage 1 snapshot. Another 5,244 non-empty reviews produced no span, generally because they contain too little lexical text for the sentence/contrast splitter. Review-claim counts are not counts of patch-related opinions.

| Game | Official-feed posts | Rule-eligible episodes | Extracted changes | Review claims | Complete / collected window segments |
| --- | ---: | ---: | ---: | ---: | ---: |
| Counter-Strike 2 | 241 | 178 | 976 | 86,761 | 0 / 21 |
| Dota 2 | 101 | 52 | 777 | 45,616 | 0 / 21 |
| HELLDIVERS 2 | 164 | 75 | 1,401 | 92,815 | 2 / 6 |
| No Man’s Sky | 29 | 11 | 0 | 72,308 | 5 / 12 |

## QA findings and limits

All 51 sampled spans were checked against their corresponding Stage 1 source revisions at the stored half-open offsets: **zero source-span mismatches**. The sample confirmed preservation of slash-separated Dota balance values and distinguished implemented fixes from acknowledgements and qualified fix claims. Broad “several issues” summaries and ambiguous bug syntax receive explicit flags.

The structural source-span result does not imply semantic completeness. About **50.1%** of change rows have one or more unresolved/quality flags, chiefly unresolved entities (1,138 rows), unresolved aspects (667), and ambiguous entity candidates (291); flags overlap. Claim extraction is much weaker for semantic fields: **85.5%** of claims have confidence below 0.5, **93.0%** lack a matched entity, **89.9%** lack an aspect, and **95.9%** have unknown polarity. The rules and sentiment lexicon are English-heavy, so short praise, noisy text, and non-English claims often remain unknown. These nulls are intentional where evidence is insufficient; Steam’s overall Recommended vote is not used as aspect sentiment.

No Man’s Sky has no atomic changes because its collected Steam announcements do not expose structured change lists in the source body. Across the four games, 122 of 316 episodes produced no structured changes. Stage 2 found 65 official-feed announcements with external or otherwise unverified linked-note content, but does not fetch those pages. Full patch notes, exact build/release linkage, and complete review windows remain source gaps; only 7 of the 60 carried-forward window segments are complete. Stage 1 uses announcement time as an unverified proxy where Steam’s public source does not provide a verified release time.

The 51-row sample is an extraction-quality audit, not independent patch/review relevance labeling and not a gold set. The dataset is suitable for the next stage to define and test relevance judgments; it should not be treated as a validated feature-level sentiment corpus.

## Validation

- `uv run --all-extras pytest -q`: **70 passed**.
- Ruff check and format check: passed.
- `git diff --check`: passed.
- The full Stage 2 run completed offline with `llm_calls: 0` and no pair/label outputs.

Next work should start with source-note completeness and a separately designed full-list relevance pilot. Preserve the distinction between extraction confidence, review aspect sentiment, and whether a claim is actually about a patch.
