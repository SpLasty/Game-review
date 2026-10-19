# Stage 4 scope

Stage 4 creates a new, provider-neutral LLM-silver labeling workflow for the atomic pair “one specific developer change ↔ one specific review claim.” It uses categories 0–3 for unrelated, topical-only, plausibly related, and clearly attributable; feature polarity is separate. It supplies full original review context, exact target claim/change spans, temporal context, surrounding patch text, and neighboring patch context where available. A category 3 response requires verifiable quote evidence and cannot precede the patch anchor.

The workflow also evaluates missed retrieval pairs with candidate-independent review samples from Stage 3 full-list packets. The model sees the entire numbered patch change list. Candidate and audit responses are stored separately. Exact source evidence, prompt/model provenance, deterministic IDs, and versioned manifests are required.

The bounded pilot must stop before training. It must report label counts, positive coverage, audit discoveries/possible omissions, validation failures, split viability, and a readiness recommendation. Every label remains silver unless an actual person independently reviews it.
