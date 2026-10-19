# Stage 4 data contracts

The schema version is `4.0.0`; the pilot prompt version is `patch-review-silver-v1`. All source text remains unchanged Unicode text from the frozen Stage 1/2 artifacts. Stage 4 outputs use new `rv4-` run, `rv4_input_` job, `rv4_label_` label, and `rv4_audit_finding_` finding IDs.

## Job JSONL

`annotation_jobs.jsonl` has one object per candidate pair or full-list audit review:

- Common provenance: `input_id`, `schema_version`, `prompt_version`, `prompt`, `prompt_sha256`, and `task_type`.
- Candidate payload: game, patch publication/anchor time and source, temporal relation, full announcement, target change and exact note span, surrounding changes, neighboring patch information, full review, and exact Stage 2 claim span.
- Audit payload: game, patch/time/window coverage, `full_change_count`, the complete `full_change_list` numbered from 1, full review, and extracted claim spans. It contains no retrieval ranking metadata.
- `response` is `null` in exported jobs. The sampling manifest, not the prompt, records the source candidate/audit IDs and selection stratum.

## Response JSONL

Each response has `input_id`, `provider`, `model_name`, `model_version`, `prompt_version`, `prompt_sha256`, and `output`.

Candidate output fields are `status` (`labeled` or `abstain`), `relevance_category` (`0`–`3`, or null for abstention), confidence in `[0,1]`, exact `review_evidence`, exact `announcement_evidence`, explanation, feature polarity, and ambiguity reason. Empty evidence is allowed when the response makes no relevance claim. Category 3 requires nonempty exact evidence from both the target claim and verified source span, and is rejected for pre-patch reviews.

Audit output attests that the full change list was examined and gives the exact number examined. Every discovered pair points to a change in the supplied list and an extracted claim (or null), includes exact review and change-note evidence, and uses categories 1–3. An empty result requires `no_matches_reason`.

## Derived tables

`silver_labels.parquet` contains one accepted candidate judgment with source Stage 3 candidate ID, Stage 1 review/revision IDs, Stage 2 patch/change/claim IDs, exact quote offsets into the original review and announcement, category, separate polarity, ambiguity, labeler provenance, prompt hash, and temporal context.

`independent_audit_findings.parquet` stores audit discoveries separately. Category 2–3 findings absent from Stage 3 candidate pairs have `retrieval_omission=true`; category 1 topical findings are not counted as retrieval misses. These remain model judgments, not reference truth.

`split_manifest.json` groups by Steam review ID and Stage 2 overlapping patch episodes, then assigns chronological groups. It includes an explicit held-out-game support reason. `human_inspection_queue.csv` marks every row `not_reviewed`; it is a future review aid, not evidence that a person inspected any item.

The run `manifest.json` records source dataset IDs, source manifest hashes, prompt/schema/workflow versions, sample seed and counts, output paths, and the machine-only labeling boundary. `import_receipt.json` records the response file hash, validation failures, unanswered jobs, and source manifest hashes. The readiness report states label counts, positive coverage, audit discoveries/omissions, split status, and whether fine-tuning is justified.

A completed run is immutable with respect to response content: importing the same response-file hash is idempotent; a different response hash is rejected and requires a new exported run ID. This prevents silently replacing silver judgments under an existing dataset identifier.
