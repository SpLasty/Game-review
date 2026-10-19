# Stage 4 implementation plan

## Bounded pilot — complete

1. Read the Stage 4 requirements and frozen Stage 3 contracts. Do not import the retired annotation mechanism.
2. Implement a new provider-neutral export/import workflow with a four-level relevance taxonomy, separate feature polarity, abstention, exact evidence, provenance, and stable `rv4-` IDs.
3. Sample candidate pairs across hard cases, semantic-only retrieval, lexical overlap, and fused ranks. Keep strata and candidate IDs out of the labeling prompt.
4. Independently sample full-list audit reviews from Stage 3 packets, exclude candidate-labeled review revisions, and expose every numbered patch change.
5. Validate exact quote spans, prompt hashes, response schemas, complete audit coverage, review/patch grouping, and readiness diagnostics.
6. Label and inspect only the bounded 24-pair / 6-review pilot. Record all judgments as silver.

## Scale-up — awaiting user approval

After approval, choose the full labeling budget and add more balanced windows only if the pilot's failure analysis justifies the expense. Preserve frozen source IDs, explicit sample strata, bounded job counts, response hashes, and prompt/model provenance. Re-run the candidate-free audit at a sample size that can support useful uncertainty estimates. If feasible, compare a second model on disagreements, while retaining model-specific responses rather than forcing agreement. Do not convert machine agreement to gold labels.

Completion criteria for an approved scale-up:

- All planned job counts are accounted for as accepted, rejected, or unanswered.
- No evidence-validation failures remain unexplained.
- Candidate and independent audit findings remain separate and reproducible.
- Category 2–3 coverage spans enough games, patches, and change types to justify the intended evaluation design.
- Grouped chronological partitions do not split review identities or overlapping patch episodes; held-out-game evaluation is created only if game coverage supports it.
- Readiness report explicitly distinguishes machine-only findings from independently verified labels and recommends against training when positive coverage or evaluation evidence is weak.

## Later work — not authorized in Stage 4

Only after the scale-up results are reviewed should a separate stage define a model baseline, label adjudication policy, evaluation metrics, and training threshold. This pilot does not train, tune, calibrate, or deploy a relevance model.
