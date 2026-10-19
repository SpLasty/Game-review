# Stage 4 architecture

Stage 4 turns Stage 3 retrieval candidates into a small, versioned LLM-silver dataset and separately probes retrieval misses using candidate-independent full-list audit packets. It is a local file workflow in `steam_patch_relevance.stage4`; it makes no provider API calls and imports no legacy labels or annotation jobs.

```text
Stage 1 original reviews + Stage 2 claims/changes + Stage 3 candidate pairs
                           │
              bounded, seeded candidate sample
          (hard / semantic-only / lexical / fused)
                           │
       full review + target claim + one atomic change
       + surrounding note + neighboring-patch context
                           │
                 external LLM judgment
                           │
       JSONL response import and quote/schema checks
                           │
       silver labels + grouped split/readiness report

Stage 3 candidate-free full-list audit packets
                           │
    full review + every numbered change in that patch
                           │
          independent-of-candidates LLM search
                           │
       separate audit findings and omission checks
```

`steam-relevance stage4 export` creates stable `rv4-` run IDs and `rv4_input_` job IDs. Each job carries a prompt version and SHA-256. Candidate jobs contain the complete review, extracted target claim, full announcement text, target atomic change with provenance, same-note context, and potentially competing nearby patch context. Full-list audit jobs contain the entire review and every numbered change; they omit candidate IDs, retrieval scores, and ranks. The selection manifest holds sampling strata and source IDs separately from the prompt payload.

The current pilot samples 24 candidates, balanced across the three games and four retrieval strata, and six candidate-independent audit reviews. Every candidate review revision is excluded from the audit sample. Audit selection targets one early post-patch and one pre-patch review per game. A fixed seed makes the job population reproducible against the frozen Stage 3 dataset.

Responses are provider-neutral JSONL files. Import checks input identity, prompt version and hash, model provenance, category/polarity schema, exact quote containment, original-source offsets, full-list completion counts, and category 3 temporal/source-span requirements. Invalid responses are rejected; missing responses remain visible as partial. Candidate labels and audit findings are stored separately. This assistant-generated pilot records OpenAI / GPT-6 Codex and notes that the immutable serving revision is not exposed by the session.

The importer builds chronological splits that keep review IDs and overlapping patch episodes together. It reports when the pilot is too small for held-out-game evaluation. Split assignments are diagnostic only at this scale and do not authorize model training.

## Boundaries

- Stage 4 reads only the declared Stage 1–3 `relevance_v1` artifacts.
- It does not collect Steam data, parse new patch changes, create retrieval candidates, train a model, or make an API call.
- All imported judgments are silver LLM judgments. Multiple labels from this one session are not independent agreement and are not gold labels.
- The full-list audit is independent of candidate membership and ranking, but its tiny sample does not estimate corpus-wide recall.
- No Stage 5 training work is authorized by this pilot.
