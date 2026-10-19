# Assumption Ledger — Patch-Scoped Labeling Pilot
<!-- ASK mode: never -->

| ID | Under-determined by the request | Chosen | Class | Source |
|----|--------------------------------|--------|-------|--------|
| A-001 | Which patch should anchor the first focused pilot? | Sea of Thieves Release Notes 3.8.1, source-confirmed and coverage-screen passing | semantic | user (accepted prior recommendation) |
| A-002 | Whether to include pairs the current retriever did not create | This rung samples only existing lexical candidates and explicitly does not estimate recall | semantic | default |
| A-003 | Which split and scale should the focused job use? | Train split only, 200 examples, excluding candidate IDs already machine-labeled | interface | default |
| A-004 | How should examples be sampled within one patch? | Deterministic round-robin across change, task, and split groups; record lexical score metadata in a separate audit sidecar | semantic | default |

## Notes

- **A-002** — The current repository has no configured embedding model or inference credentials. A patch-scoped labeled sample can assess surfaced-pair usefulness, but it cannot reveal missed pairs. Add semantic retrieval and a miss-audit only after selecting and validating an embedding path.
- **A-004** — The audit is descriptive because the sample is stratified, not a probability sample. It must not be presented as population precision or retrieval recall.

## Observed result

The initial 200 decisions (198 irrelevant, 2 uncertain) were re-read pair by pair against the complete review and announcement context. A distinct GPT-6 run superseded all 200 decisions with 190 irrelevant and 10 uncertain; no pair in the sample was judged relevant. Uncertainty was retained for heading-only extraction and overlapping symptoms with different or missing triggers. This is still LLM-only silver labeling, not human or independent adjudication. The stratified lexical sample does not estimate precision or recall; a separately sampled set of noncandidate pairs is still required to examine missed matches.
