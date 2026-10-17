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

The 200 sampled pairs have stored labels of 198 irrelevant and 2 uncertain, with no relevant labels. Most irrelevant responses used a shared rationale and were not individually checked against the full announcement context. Treat this as an unverified first pass, not as a reliable estimate of candidate quality or retrieval recall. Audit each pair before tuning the retriever; then assess a noncandidate sample to examine missed matches.
