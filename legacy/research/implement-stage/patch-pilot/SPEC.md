# Patch Pilot Specification

Target: create a reproducible, patch-scoped LLM labeling pilot for Sea of Thieves 3.8.1 using existing review/change candidates. Inputs are immutable dataset `5c8a356cb9aa33235617e46eb2b6597db40ed77ee1967ed71be2ec0b65f633c7`, patch ID `9593c96b043f323204b6db3437497a9b4972e5986d637dd7e21ce7b908946839`, and existing LLM labels. Outputs are a frozen 200-example train job, imported evidence-backed labels, a refreshed Parquet snapshot, retrieval audit report, and updated `docs/PROJECT_HANDOFF.md`.

Success: the patch filter emits only the requested patch's candidates, excludes already labeled candidates, keeps change/task/split representation balanced, imports all responses, and `prepare-data` publishes a snapshot passing validation. Base commit: `4dcbe2a8cf6214d22f5abf9c5162402030a2a76a`. Scope cuts: do not claim retrieval recall, add an embedding dependency, train a classifier, or deploy a service in this rung.

## Outcome

The exporter created a 200-example train job from a 348-pair lexical pool and excluded two previously labeled IDs. All request IDs were patch-scoped. The first GPT-6 pass returned 198 irrelevant and 2 uncertain labels; these are preserved but superseded because most used a shared rationale and did not verify each complete context.

A rowwise GPT-6 correction pass (`codex-gpt6-sot381-row-audit-2026-10-18`) checked all 200 full reviews against their exact announcement passages and superseded every first-pass decision. It returned 190 irrelevant, 10 uncertain, and 0 relevant labels. The refreshed snapshot is `cfa34941257d2905d8a2f2681de931909e1904d97bc220e9d121f3c855b4cf56`: 500 stored annotations including 200 superseded records, 300 active decisions, 289 silver rows, no human annotations, and 196 passing validation checks. The rowwise review remains machine-generated silver labeling, not independent or human adjudication. This does not measure candidate recall or unbiased corpus precision.
