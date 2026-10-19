# Initial Steam data exploration

## Review populations

- **reviews**: 73,336 reviews; 18.95% negative votes out of 73,336 valid votes; 42,548 below 10 words.
- **balanced**: 30,000 reviews; 25.06% negative votes out of 30,000 valid votes; 0 below 10 words.

## Validation

- **reviews**: passed
  - warning: empty_text (291) — Retained for vote counts; has no usable text
  - warning: repeated_review_text (13,560) — Repeated wording is retained; inspect for memes or duplicate families
- **balanced**: passed
  - warning: repeated_review_text (89) — Repeated wording is retained; inspect for memes or duplicate families
- **announcements**: passed
  - warning: empty_text (2) — Source coverage needs inspection

## Interpretation limits

- The balanced file overlaps the full file: never concatenate them as new reviews.
- A negative recommendation is not sentiment toward every patch change.
- Short reviews remain in recommendation statistics; text filtering changes the population.
- Coverage tables describe observed dates, not a proof that a patch window is complete.
- Edited text and votes are the latest exported state, not their original historical values.
- Patch/keyword flags are heuristics; no gold labels or causal patch effects are produced.
- Original announcement heading markup is absent from these CSVs.

See profile.json for source fingerprints and validation details, CSV tables for aggregate inspection, and figures/ for plots.
