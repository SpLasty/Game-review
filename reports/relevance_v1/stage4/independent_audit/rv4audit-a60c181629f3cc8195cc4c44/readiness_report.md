# Independent full-list audit — `rv4audit-a60c181629f3cc8195cc4c44`

## Result

The LLM examined the complete 69-change list for 300 deterministically sampled post-patch reviews. All 300 responses passed schema and exact-quote validation. It returned two topical pairs: one category 1 and one category 2. It found no category 3 pair and no category 2–3 retrieval omission.

These are silver judgments from one ChatGPT session, not human-verified labels or calibrated probabilities. The audit is a one-patch diagnostic; it does not estimate corpus-wide recall.

## Sampling scope

- Game and patch: Dota 2, **Dota 2 Update - 7/1/2026** (`rv2_patch_1d2cff01840bf8f1810c9f13`).
- Review window: `after_0_7d`; sample seed: `stage4-full-list-audit-300-v1`.
- Population available to the sampler: 1,996 unique Steam review IDs with non-empty text; 300 distinct reviews were selected by seeded SHA-256 ranking, keeping the latest collected revision per review ID.
- Patch list: 69 source-span-verified implemented changes, numbered in source order; 20,700 review/change exposures.
- Steam review-window collection was `page_budget_reached`, with reported coverage of **47.28%**. The review sample is random within the collected pool, not a random sample of every review Steam received.
- The extracted list comes from the announcement body. Completeness of the developer's full patch notes is **unverified**.
- Sample language counts: Russian 217, English 50, Simplified Chinese 8, Ukrainian 8, Brazilian Portuguese 6, Spanish 4, Latin American Spanish 2, and one each in Czech, Indonesian, Italian, Traditional Chinese, and Thai.
- Candidate independence: reviews were selected from Stage 2 window memberships without consulting Stage 3 candidate rows or ranks.

## Findings

| Category | Review | Change | Finding |
|---|---|---|---|
| 1 — topical only | `229907060` — “стабильно раз в 20 каток игра вылетает” | “Fixed various server and client crashes” | A recurring crash complaint is topically related to the broad crash-fix note, but the review gives no crash signature or update-specific link. This is not a positive relevance label. |
| 2 — plausibly related | `229940924` — “this new system we are forced to play another role” | The solo Ranked Roles high-demand-role selection rule | “New system” and forced role selection plausibly refer to this change, but the review does not mention the high-demand-role or Role Queue Game requirement. The patch may have been confused with another role-assignment or drafting rule. |

Stage 3 already retrieved the category 2 role-queue pair (`rv3_candidate_27efe1482618f1bf0d58f0cf`): BM25 rank 50, fused rank 79. Thus the independent audit found **zero plausible retrieval omissions** in this sample. The category 1 crash complaint was not a category 2–3 retrieval miss.

## Token and runtime estimates

Exact tokenizer counts are unavailable in this chat runtime. The estimates below use serialized prompt characters divided by 3–4.5 characters per token; multilingual reviews and JSON formatting make this approximate.

| Scope | Estimated input | Estimated output | Approximate single-stream inference time* |
|---|---:|---:|---:|
| 300 full-list reviews | 3.6–5.3M tokens uncached | 15–60K tokens | About 1–2 hours |
| All 62,548 Stage 3 candidate pairs | 198–297M tokens uncached | 6.3–12.5M tokens | About 4–6 days |

\*Illustrative only: about 1,000 input tokens/sec and 50 output tokens/sec, without retries or queueing. At 5,000 input and 100 output tokens/sec, the 62,548-pair pass would still take roughly 1–2 days on one stream. Actual wall time depends on the remote model service, concurrency, and rate limits. The estimates do not include human verification.

The candidate estimate extrapolates the mean prompt size of the 24 Stage 4 candidate-pair pilot jobs to the full 62,548-row Stage 3 candidate table. That pilot is stratified and small, so this is a planning range rather than a measured bill. Stage 4's full candidate scope is 62,548 retrieved pairs, not the 3,656,475 possible change/claim combinations.

The output estimate assumes about 50–200 generated tokens per full-list audit review and 100–200 tokens per candidate-pair response. Longer explanations or multiple findings per review increase output usage.

The 300-job JSONL repeats the same 69-change payload in each job (about 50,250 characters per review). A provider with prompt-prefix caching could discount much of that repeated input if the runner submits an identical prefix; the provider-neutral export does not itself enable caching. Repeated announcement bodies across the 62,548 candidate jobs amount to about 494M characters. Caching may lower billable uncached input substantially, while total context processed remains large.

## Local resource use

The sampler and importer ran as ordinary Python/Parquet file operations and completed in a few seconds. The audit export is about 16 MB. No local LLM, GPU inference, embedding generation, model training, Steam API request, or other compute-intensive job ran on the PC. The labels were generated by the ChatGPT model in this session; exact session token accounting is not exposed.

## Artifacts

- Inputs: `data/relevance_v1/processed/stage4/independent_audit/rv4audit-a60c181629f3cc8195cc4c44/annotation_jobs.jsonl`
- Responses: `data/relevance_v1/processed/stage4/independent_audit/rv4audit-a60c181629f3cc8195cc4c44/responses_gpt6_codex_chat_session.jsonl`
- Findings: `data/relevance_v1/processed/stage4/independent_audit/rv4audit-a60c181629f3cc8195cc4c44/independent_audit_findings.parquet`
- Manifest and validation receipt are in the same run directory. The run contains 300/300 accepted responses and is complete; the `human_inspection_queue.csv` remains marked unreviewed.
