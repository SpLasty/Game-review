# Annotation and patch-verification guide

**Human annotation is optional.** The default `prepare-data` handoff now exports self-contained LLM batch files. Use [the LLM-only workflow](../../docs/llm_annotation_workflow.md) to generate, import and train on separate machine silver labels with no human adjudication. The human-specific commands below remain available if reference annotations are obtained later.

Run `steam-insights annotations-export` after preparing a dataset. The printed file under `queues/` contains development examples with blank human fields. Existing queue files are preserved. Never use recommendation votes or rule-derived status hints as gold labels.

## Review/change annotations

Complete these fields in each selected queue record:

| Field | Values / requirement |
| --- | --- |
| `candidate_id` | Keep the exact exported ID. |
| `annotator_id` | Named/pseudonymous human annotator identifier. |
| `label_source` | `human`. |
| `adjudicated` | Boolean. True only when the decision has been finalized under the annotation procedure. |
| `created_at` | Explicit ISO-8601 timestamp with timezone. |
| `relevance` | `relevant`, `irrelevant`, `uncertain`. |
| `sentiment` | `positive`, `negative`, `mixed`, `neutral`, `not_expressed`, `unknown`, `not_applicable`. Refers to this change/target, not the whole game. |
| `fix_status` | `acknowledged`, `planned`, `workaround`, `partial_fix`, `limited_fix`, `released_fix`, `unknown`, `not_applicable`. Describes what the announcement supports, not whether the fix actually succeeded. |
| `review_evidence` | `{ "start": integer, "end": integer, "text": exact quote }` in canonical `review_text`. |
| `change_evidence` | Same structure in canonical `announcement_text`, whose heading context must be read. |
| `supersedes` | List of older annotation IDs for the same candidate when explicitly resolving prior decisions. |

Offsets are zero-based Unicode character indices, with exclusive ends. Relevant pairs require both evidence spans. A substantive sentiment requires review evidence; a substantive fix-status decision requires announcement evidence. An irrelevant pair requires both sentiment and fix status to be `not_applicable`. Use uncertainty rather than inferring absent branch/platform/release evidence.

Read surrounding paragraphs and headings: a sentence under “Known Issues” or “Planned” does not support a released fix just because it contains “fixed.” Negative game recommendation does not imply negative sentiment toward every change. A review can praise one change and criticize another. Broad game complaints without a link to the specific target should not be forced into a match.

Annotate a small common pilot independently, compare disagreements, refine the guide on development examples, then adjudicate. Keep annotator decisions separate. Consistent active adjudicated decisions are eligible for supervised export; disagreements and `uncertain` relevance remain excluded. The pipeline checks schema/evidence integrity; it cannot establish inter-annotator agreement or annotation correctness on its own.

```bash
uv run --all-extras steam-insights annotations-import --input path/to/completed.jsonl
uv run --all-extras steam-insights prepare-data
```

Import writes validated records to `labels.jsonl`, without silently resolving disagreements. Labels are tied to the exact candidate/revision; source refreshes may make them stale. Keep the annotated dataset snapshot and resolve stale IDs explicitly.

## Patch-post verification registry

`patch_verification.jsonl` is a separate, source-evidence registry. A record has:

```json
{
  "announcement_revision_id": "exact exported revision ID",
  "decision": "confirm_patch",
  "actor_type": "human",
  "checked_by": "verifier identifier",
  "checked_at": "ISO timestamp with timezone",
  "evidence_field": "canonical_text",
  "evidence_text": "exact source quote"
}
```

Decisions are `confirm_patch`, `non_patch`, or `uncertain`; evidence fields are `title` or `canonical_text`. `actor_type=source_review` records an auditable source inspection separately from human verification. The committed initial source-review records were made by the assistant after reading recovered official posts; they are not human training annotations.

Optional `release_utc` requires `release_evidence_text` in the canonical announcement and a timezone-qualified time. Publication timestamps alone do not establish effective release time. Conflicting registry decisions for the same revision fail until explicitly reconciled. Re-run preparation to validate and apply registry changes.

Full announcement text is available in Parquet/DuckDB. Recovery keeps outgoing references in `announcement_links`; verify an external site's relationship to the developer before relying on an external changelog. Confirmation of a patch-note post does not verify actual fix effectiveness.
