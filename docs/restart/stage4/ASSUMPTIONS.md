# Stage 4 assumptions and decisions

- **Pilot size:** 24 candidate pairs, eight per game, plus six full-list audit reviews. This is small enough to label in one bounded session and large enough to exercise each game and retrieval stratum; it does not estimate candidate prevalence.
- **Candidate strata:** Two hard cases, two dense-only discoveries, two specific lexical overlaps, and two high-fused-rank pairs per game where available. The deterministic sampler fills short strata from the remaining ranked pool and records actual counts.
- **Audit sampling:** Two candidate-independent reviews per game, one early post-patch and one pre-patch when available. Candidate-sampled review revisions are excluded. This deliberately tests different temporal contexts but is far too small for recall estimation.
- **Judgment source:** One in-session GPT-6 Codex labeling pass. The exact immutable serving revision is unavailable, so that limitation is recorded. There is no second independent model and no human-verified gold data.
- **Topical category:** Category 1 includes same-feature/mechanic overlap without a reliable link to the particular change. Same-game or same-entity mentions alone are insufficient.
- **Change 3:** Category 3 is accepted only for post-anchor reviews, verified developer source spans, and exact review/change evidence. An update reference plus a specific paraphrase may support category 3 even if terminology is imprecise; the explanation must preserve that ambiguity.
- **Audit interpretation:** Category 1 findings are topical discoveries, not retrieval misses. Only category 2–3 audit pairs absent from candidates count as possible retrieval omissions.
- **Readiness:** A grouped split is emitted for inspection but is not a meaningful model evaluation at this pilot size. No model training is allowed.

The fixed seed is `stage4-pilot-v5`. Full-scale counts remain undecided and require the user's next approval.
