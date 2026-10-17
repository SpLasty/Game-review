# Patch Pilot Specification

Target: create a reproducible, patch-scoped LLM labeling pilot for Sea of Thieves 3.8.1 using existing review/change candidates. Inputs are immutable dataset `5c8a356cb9aa33235617e46eb2b6597db40ed77ee1967ed71be2ec0b65f633c7`, patch ID `9593c96b043f323204b6db3437497a9b4972e5986d637dd7e21ce7b908946839`, and existing LLM labels. Outputs are a frozen 200-example train job, imported evidence-backed labels, a refreshed Parquet snapshot, retrieval audit report, and updated `docs/PROJECT_HANDOFF.md`.

Success: the patch filter emits only the requested patch's candidates, excludes already labeled candidates, keeps change/task/split representation balanced, imports all responses, and `prepare-data` publishes a snapshot passing validation. Base commit: `4dcbe2a8cf6214d22f5abf9c5162402030a2a76a`. Scope cuts: do not claim retrieval recall, add an embedding dependency, train a classifier, or deploy a service in this rung.

## Outcome

The exporter created a 200-example train job from a 348-pair lexical pool and excluded two previously labeled IDs. All request IDs were patch-scoped. The GPT-6 pass returned 200/200 labels: 198 irrelevant, 2 uncertain, 0 relevant. Most irrelevant responses used a shared rationale and were not individually checked against all full announcement context, so the zero-relevant result is provisional pending row-by-row audit. Import and rebuild produced snapshot `5eb4842f3daaf8125a9daaaeef18c9e9f0c304dcd8703c5b100a5cfd39c77c9f` with 300 machine decisions, 297 silver rows, no human rows, and 196 passing validation checks. This says nothing about candidate recall.
