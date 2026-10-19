# Stage 2 implementation and completion criteria

1. **Isolated contracts and IDs** — add `steam_patch_relevance.stage2`, `rv2_` identifiers, schemas, and paths distinct from Stage 1 and archived implementation.
2. **Announcement classification** — retain every source revision and assign multi-label categories, explicit official-feed provenance, patch-eligibility triage, and linked-note completeness state.
3. **Atomic changes** — parse Steam structured blocks and nested headings; preserve exact raw source offsets, entity/aspect/action/direction/value/status, and uncertainty flags. Do not emit heading-only rows.
4. **Review claims** — split exact revision text into sentence/contrast spans; preserve offsets, edit identity, language, temporal cues, negation, uncertainty, and conservative nullable polarity.
5. **Per-game vocabulary** — create small term resources from official patch content and repeated review name forms, with no cross-game shared ontology.
6. **Temporal relations** — represent episodes, collected window segments, review memberships, window overlap, and repeated-entity episode ambiguity. Never treat time as relevance.
7. **Audit and validation** — select a deterministic stratified sample; inspect concrete examples; test splits, hierarchy, numerical direction, headings, bug details, sentiment, negation, edit offsets, and overlapping episodes.

**Completed.** Validation includes fixture tests, a bounded smoke run, a full deterministic Stage 1 snapshot run, zero unverifiable emitted change spans, documented source/extraction gaps, and an LLM-inspected stratified audit sample with exact source text. Stage 2 does not fetch data, resolve external URLs, generate candidate pairs, or train models. See [`HANDOFF.md`](HANDOFF.md) for the final dataset ID, counts, caveats, and verification.
