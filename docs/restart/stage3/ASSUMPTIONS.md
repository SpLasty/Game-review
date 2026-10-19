# Assumption ledger — Stage 3 retrieval
<!-- ASK mode: never -->

| ID | Under-determined by the request | Chosen | Class | Source |
| --- | --- | --- | --- | --- |
| A-001 | Which Stage 2 snapshot and episode scope? | Use the approved `rv2-d52a3f9f1a3de2fe80aa098f` snapshot; retrieve every episode with at least one verified atomic change and at least one collected temporal membership. Empty-change episodes remain visible in coverage but cannot form change pairs. | semantic | default |
| A-002 | How are review windows applied? | Use Stage 2 temporal membership rows and all available segments, including pre-patch rows; never infer patch relevance from membership. Duplicate reviews across distinct patch episodes remain separate episode-scoped candidates. | semantic | default |
| A-003 | How large are per-method ranked lists? | Default budgets are 10, 25, 50, and 100 claims per change per method; the maximum is configurable, all truncation is recorded, and there is no per-review cap. The Stage 3 pair dataset is the union at the configured maximum. | interface | default |
| A-004 | How are independent rankings combined? | Reciprocal-rank fusion with `k=60`, summing `1/(k+rank)` for BM25, dense cosine, and entity/aspect rank lists. Component ranks and scores remain available. | semantic | default |
| A-005 | Which dense model and inference contract? | `intfloat/multilingual-e5-small` through Sentence Transformers, pinned by default to `614241f622f53c4eeff9890bdc4f31cfecc418b3`; patch changes use the `query:` prefix, claims use `passage:`, and normalized vectors use cosine-equivalent dot product. Cache keys include the immutable model revision and prefixed content hash. | semantic | default |
| A-006 | What is the independent audit sample? | Select one change-bearing episode per game with review-window data (largest atomic-change list, deterministic tie-break), then uniformly sample up to five review revisions per available temporal segment using a fixed seed. Export full reviews and the complete patch change list without retrieval ranks or labels. Games without extracted changes are reported as unavailable for this audit. | semantic | default |
| A-007 | What can budget curves claim without reference labels? | Report candidate-pool yield, method overlap, and whether pairs are retained at each budget. Do not report recall. The candidate-free audit export enables later independent judgments but does not create labels in Stage 3. | semantic | user |
| A-008 | How are aliases and aspect similarity handled? | Resolve entities only within each game's Stage 2 terminology resource; match term/alias variants and textual mentions. Rank exact entity plus compatible aspect above entity-only, and allow broad aspect-family matches at lower score. This signal discovers candidates, not relevance. | semantic | default |
| A-009 | How are candidate IDs and provenance scoped? | Use a fresh `rv3_candidate_` ID derived from Stage 3 schema version, Stage 2 dataset, patch, change, and claim. Preserve all component ranks/scores, temporal segments, and source dataset IDs. | interface | default |
| A-010 | How are hard negatives represented? | Keep rule-generated confounders in a separate unlabelled hard-candidate pool. A heuristic reason never sets a relevance/negative label. | semantic | user |

## Notes

- A-001 limits this run to the review-covered portion of Stage 2. The current source has extracted changes for only nine collected episodes across three games; No Man's Sky has no Stage 2 atomic changes, so retrieval cannot operate there until extraction coverage improves.
- A-003 is a retrieval budget, not a confidence threshold. Increasing it can expand candidate storage and computation; the configured budget curves make this cost visible.
- A-005 keeps dense retrieval multilingual because the Stage 2 reviews span multiple languages. The model's prescribed asymmetric prefixes are applied before caching. The pinned revision makes reruns independent of a moving branch name.
- A-006 samples from patch-window membership before candidate generation and never conditions selection on candidate inclusion. Sampling is reproducible and stratified by temporal segment, but it is a diagnostic sample, not a corpus-wide recall estimate.
