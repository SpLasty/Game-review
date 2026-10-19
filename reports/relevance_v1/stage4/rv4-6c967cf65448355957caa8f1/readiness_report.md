# Stage 4 silver-label pilot — `rv4-6c967cf65448355957caa8f1`

This is a bounded pilot. All judgments are LLM-generated silver labels from a single assistant session; no person reviewed or verified them. Do not treat confidence as calibrated probability.

## Scope

- Candidate-pair responses accepted: 24; candidate labels accepted: 24.
- Independent full-list audit jobs selected: 6; audit findings: 2.
- Candidate relevance counts: {"0": 14, "1": 8, "2": 1, "3": 1}.
- Category 2–3 candidate positives: 2; category 3: 1; games: 2; patch episodes: 2.
- Independent-audit category 2–3 findings: 0; retrieval omissions among those: 0.
- Evidence/schema validation failures: 0.

## Interpretation

Readiness recommendation: **not ready for relevance-model fine-tuning**. This pilot is too small and machine-only to establish a reliable evaluation set. The audit is a tiny stratified probe, not a corpus-wide recall estimate.
Category 0/1/2/3 describes change-specific relevance only. Feature polarity is stored separately. Stage 1 review recommendation was not used.
The full-list audit job and its findings remain separate from candidate labels; category 2–3 omissions are a machine-discovered retrieval-miss signal, not verified ground truth.

## Positive coverage by game and patch

- Counter-Strike 2 — Counter-Strike 2 Update: 1 category 2–3 labels (1 category 3).
- HELLDIVERS 2 — Patch Notes 01.002.200: 1 category 2–3 labels (0 category 3).

## Audited examples

### Counter-Strike 2 — category 3 (0.91)

Change: Added damage prediction settings. Damage prediction allows clients to immediately play the audio/visual effects of inflicting damage without waiting for confirmation from the server. Damage prediction can make shooting feel significantly more responsive, but comes with the risk of occasionally being wrong (e.g. due to aim punch, tagging, or a death that your client isn't yet aware of).
Claim: It basically means your shots will feel more responsive, and headshots will be delivered with a satisfying thud—unless, of course, you’re me, at which point the game seems to assume your enemies are made of marshmallows and your bullets are tickling them.
Evidence: review `It basically means your shots will feel more responsive, and headshots will be delivered with a satisfying thud—unless, of course, you’re me, at which point the game seems to assume your enemies are made of marshmallows and your bullets are tickling them.`; note `Added damage prediction settings. Damage prediction allows clients to immediately play the audio/visual effects of inflicting damage without waiting for confirmation from the server. Damage prediction can make shooting feel significantly more responsive, but comes with the risk of occasionally being wrong (e.g. due to aim punch, tagging, or a death that your client isn't yet aware of).`.
Reason: The review explicitly refers to an update and paraphrases the note's distinctive claim that shots feel more responsive. It calls the technology 'Tickrate', so the underlying terminology is imprecise, but the specific responsiveness claim closely tracks this damage-prediction change. The claim also jokes that its effects feel weak, giving mixed feature sentiment.

### HELLDIVERS 2 — category 2 (0.84)

Change: Fixed an issue where players could be blocked from completing objectives requiring called-down equipment due to the required stratagem being unavailable
Claim: Some bugs made the game less fun: not being able to call down mission stratagems resulting in wasted time, extraction soft-lock etc.
Evidence: review `not being able to call down mission stratagems resulting in wasted time, extraction soft-lock`; note `Fixed an issue where players could be blocked from completing objectives requiring called-down equipment due to the required stratagem being unavailable`.
Reason: The review names the same concrete failure symptom as the patch note: mission stratagems cannot be called down, causing a soft-lock. The review does not say this particular fix resolved it, so attribution remains plausible rather than clear.

## Split and evaluation status

- Split status: `created_grouped_chronological_partitions`; groups: 6; partitions: {"test": 6, "train": 17, "validation": 1}.
- Whole connected review/patch groups kept together.
- Held-out-game evaluation: not_supported — Only 3 games have non-abstained candidate silver labels; a held-out-game test needs more independent game coverage.
- No training, threshold calibration, or model selection should use these pilot labels.

## Limitations and next action

The candidate sample is intentionally stratified across hard cases, semantic-only discoveries, specific lexical overlap, and top fused ranks; its label distribution does not estimate corpus prevalence. The independent audit samples complete patch lists but only a few reviews. A category 3 label requires quote-span validation, but exact quotes alone do not prove causal attribution.
Review the human-inspection queue before scaling. Human reviewers should independently inspect likely category 2/3 cases, low-confidence disagreements, and any candidate-independent omissions. The queue is explicitly marked unreviewed.
