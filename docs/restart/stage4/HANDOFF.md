# Stage 4 handoff — bounded silver-label pilot

## Outcome

Stage 4's fresh export/import path is implemented and exercised on the requested small subset. The canonical pilot run is `rv4-02c10d1f84099a6d45e2a04a`, based on Stage 3 dataset `rv3-cef79b660029d7d5eb703567`, Stage 2 dataset `rv2-d52a3f9f1a3de2fe80aa098f`, and Stage 1 run `rv1-20261019T031033900187Z-a468b544`.

The pilot labeled **24 candidate pairs** (eight each from Counter-Strike 2, Dota 2, and HELLDIVERS 2) and **six candidate-independent full-list audit reviews** (two per game). Each game contributed two hard cases, two semantic-only candidates, two specific lexical-overlap candidates, and two high-fused-rank candidates. Each audit prompt exposed the entire numbered change list; there were **348 change entries across the six audit jobs**. The labels were generated in one OpenAI GPT-6 Codex session. The runtime's immutable serving revision was unavailable. No person reviewed these outputs.

## Results

| Candidate label | Count |
| --- | ---: |
| 0 — unrelated | 14 |
| 1 — topical only | 8 |
| 2 — plausibly related | 1 |
| 3 — clearly attributable | 1 |

The two category 2–3 candidate judgments are:

- **Counter-Strike 2, damage prediction:** a review explicitly refers to an update and paraphrases the note's distinct “shots feel more responsive” claim. It calls the mechanism “Tickrate,” so attribution is strong but terminology is imprecise; it was labeled category 3, confidence 0.91, mixed feature polarity.
- **HELLDIVERS 2, unavailable mission stratagem:** a review describes being unable to call down mission stratagems and an extraction soft-lock, matching a patch's fix for required called-down equipment being unavailable. It does not confirm that this patch fixed the symptom; it was labeled category 2, confidence 0.84, negative feature polarity.

The candidate-free audit found **two category 1 topical-only pairs** in one pre-patch Spanish Dota 2 review: general discussion of cosmetic rewards versus a Candyworks owned-item display, and solo ranked/MMR frustration versus a role-queue preference rule. The other four sampled reviews yielded no topical change. No category 2–3 audit finding was found, so this tiny audit identified **zero possible retrieval omissions**. These six reviews cannot support a corpus-wide recall claim.

All **30/30 responses passed** schema and exact-quote validation; there were zero invalid responses and zero unanswered jobs. Category 2–3 candidates span two games and two patch episodes. The report recommends **not fine-tuning**: there are only two supported positives, one category 2 and one category 3, and no meaningful validation set. The generated chronological split has six patch/review groups, but only one validation label and no positive coverage sufficient for evaluation. Held-out-game evaluation is unsupported because only two of three sampled games have category 2–3 candidates.

All labels, audit findings, split assignments, and confidence scores are machine judgments from one session. Confidence is not calibrated. Category 1 is not a positive relevance label. The human inspection queue is marked `not_reviewed` throughout.

## 300-review full-list audit

The user-approved independent audit is complete as run `rv4audit-a60c181629f3cc8195cc4c44`. It sampled 300 unique reviews from the first seven days after Dota 2's July 1, 2026 update and showed each review the same complete, numbered list of 69 extracted changes. The sampler selected from Stage 2 memberships without consulting Stage 3 candidates. All 300 responses passed validation.

The audit returned two findings: one category 1 topical-only crash complaint and one category 2 plausible role-queue match. No category 3 finding or category 2–3 retrieval omission was found. The role-queue pair was already in Stage 3 (BM25 rank 50, fused rank 79). The window was collected only to the page budget and reports 47.28% review coverage; the sample is random within that incomplete pool. Full patch-note completeness is also unverified. These results are a single-patch diagnostic, not a corpus-wide recall estimate.

The standalone audit exporter was made import-compatible by recording its Stage 1/2/3 source IDs and audit-only response counts in the manifest. Stage 3 is used only during import to check whether independently found pairs were retrieved; it does not influence review selection. Stage 4 tests pass (10 tests).

The audit jobs occupy about 16 MB and contain roughly 3.6–5.3 million estimated uncached input tokens. Labeling all 62,548 Stage 3 candidate pairs is estimated at about 198–297 million input tokens plus 6.3–12.5 million output tokens, before any provider prompt-cache discount. These are character-based planning estimates, not exact tokenizer or API usage. No local model inference, embeddings, training, or GPU workload was used. See the audit report for assumptions and time scenarios.

## Files to inspect

- Jobs, sampled-stratum manifest, responses, Parquet datasets, split manifest, queue, and receipt: `data/relevance_v1/processed/stage4/rv4-02c10d1f84099a6d45e2a04a/`
- Readable exact list of all 24 target change ↔ review-claim pairs: `reports/relevance_v1/stage4/rv4-02c10d1f84099a6d45e2a04a/candidate_pairs_for_inspection.md`
- Readiness report: `reports/relevance_v1/stage4/rv4-02c10d1f84099a6d45e2a04a/readiness_report.md`
- 300-review audit jobs, responses, findings, manifest, and receipt: `data/relevance_v1/processed/stage4/independent_audit/rv4audit-a60c181629f3cc8195cc4c44/`
- 300-review audit results and token/runtime estimate: `reports/relevance_v1/stage4/independent_audit/rv4audit-a60c181629f3cc8195cc4c44/readiness_report.md`
- Stage 4 implementation and tests: `src/steam_patch_relevance/stage4/` and `tests/relevance_v1/test_stage4.py`
- Schema/architecture details: this directory's `DATA_CONTRACTS.md` and `ARCHITECTURE.md`

Earlier unannotated Stage 4 exports remain in the ignored data tree as reproducible exploratory artifacts. They are not inputs to this run and contain no labels; use the canonical ID above for the pilot results.

The 300-review full-list audit and candidate-pair labels are separate datasets. The audit is complete; Stage 4 candidate-pair labels remain limited to the original 24-pair pilot. No full-candidate labeling run has been started.

## Commands

To inspect the already-generated outputs, open the paths above. To reproduce the same export from the frozen Stage 3 dataset:

```bash
uv run --all-extras steam-relevance stage4 export \
  --source-dataset rv3-cef79b660029d7d5eb703567 \
  --candidate-pairs 24 --audit-reviews 6 --seed stage4-pilot-v5
```

The matching response-import command is recorded in the run manifest and used the `pilot_responses.jsonl` file inside the run directory. No collection, model training, threshold tuning, or deployment was performed.

Reproduce the 300-review independent audit export:

```bash
uv run --all-extras steam-relevance stage4 audit-export \
  --source-dataset rv2-d52a3f9f1a3de2fe80aa098f \
  --patch-id rv2_patch_1d2cff01840bf8f1810c9f13 \
  --window-segment after_0_7d --reviews 300 \
  --seed stage4-full-list-audit-300-v1
```

Import the completed responses with the independent-audit output roots:

```bash
uv run --all-extras steam-relevance stage4 import \
  --run-id rv4audit-a60c181629f3cc8195cc4c44 \
  --responses data/relevance_v1/processed/stage4/independent_audit/rv4audit-a60c181629f3cc8195cc4c44/responses_gpt6_codex_chat_session.jsonl \
  --output-root data/relevance_v1/processed/stage4/independent_audit \
  --report-root reports/relevance_v1/stage4/independent_audit
```

The imported response file is `responses_gpt6_codex_chat_session.jsonl` in the audit run directory. Full candidate-pair labeling beyond the 24-pair pilot, model training, threshold tuning, and deployment have not been started.
