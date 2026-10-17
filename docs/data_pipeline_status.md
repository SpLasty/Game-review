# Processing implementation and handoff

**Updated labeling route:** [LLM-only annotation](llm_annotation_workflow.md) is implemented and is now the default preparation handoff. No human annotation is required. Machine labels are published as separate silver data; human gold is optional. The original completion record below predates this extension.

## Run the remaining automated work

From `Game-review/`:

```bash
uv sync --locked --all-extras
uv run --all-extras steam-insights prepare-data --online
```

The second command recovers original announcement content, prepares the review collection plan, backfills insufficient fully elapsed patch windows, publishes model-input Parquet tables, validates them, refreshes both quality reports and exports a development LLM annotation job. It shares 60 HTTP requests per invocation by default. Repeat it to resume saved cursors and advance through more windows. A completed run does not imply Steam has enough reviews for every window.

Use `uv run --all-extras steam-insights prepare-data` for local processing without network requests. Small independent commands are in `scripts/data/`; their logic is shared with the main workflow.

## Implemented scope

| Item | Delivered |
| --- | --- |
| 1. Input inventory and contracts | String-safe imports, source checksums, explicit Arrow types and invalid-record quarantine. |
| 2. Source preservation | Immutable recovered observations, retrieval timestamps and source-row lineage; original CSVs preserved. |
| 3. Efficient storage/exploration | Zstandard Parquet, sorted row groups, DuckDB catalog/views, Pandas queries, notebook and examples. |
| 4. Reviews | Conservative normalization, revisions, language inspection, word counts, edit flags and exact canonical passages. |
| 5. Duplication | Exact/approximate duplicate evidence, bounded comparisons and supervised split-leakage exclusions. |
| 6. Developer documents | HTML/Steam BBCode headings, nested lists, tables, canonical offsets and outgoing references. |
| 7. Patch evidence | Official-source confirmation plus a quote-bound review registry; legacy assertions and release-time uncertainty preserved separately. |
| 8. Individual changes | Structural candidates with inherited headings, status/scope/entity/version hints and ambiguity flags. |
| 9. Patch windows | Before/after counts, dates, edits, overlap, deficits, coverage evidence and resumable date-bounded backfill. |
| 10. Candidate pairs/splits | Bounded lexical retrieval, explicit feedback/retrospective tasks, fixed 8/2/20 game allocation. |
| 11. Model/annotation contracts | Arrow batch loader, inference exports, human annotation queues/import validation and adjudicated supervised exports. |
| 12. Orchestration/assurance | Single command, bounded requests, cursor/cache resume, execution journal, atomic snapshot publication, validation gates and regression tests. |

No implementation placeholders remain. Model training, embedding generation, deployment, DVC and MLflow service setup are later lifecycle stages outside this processing request. The dataset/manifests and frozen contracts support adding those later.

## Work already executed versus work to run

Public announcement recovery was executed: 12 requests recovered all 35 prioritized post IDs and saved 1,200 observations. This provided 1,107 current structured documents. Six remaining legacy post assertions were inspected against their recovered official source and recorded as assistant `source_review` decisions, not human training labels.

The actual local dataset `f6ed010d3a378a5a12a4d9e502a41aae540c77b863356eae972189164cec0240` has been built and passed 175 publication checks. It contains 73,336 reviews, 3,638 current announcements, 32,759 structural change candidates and 27,684 review/change candidates. Of 255 source-confirmed/reviewed patch posts, 15 windows pass the availability screen. Historical review backfill has **not** been executed against Steam in this handoff; it is implemented and exercised with deterministic simulated pagination. Run the online command above for that remaining collection. Missing source content and labels remain explicit rather than being manufactured.

Latest row counts, source-confirmed post counts, games and passing periods are in [the generated readiness report](../reports/data_quality/pipeline/report.md). That report will be regenerated after each run; [the original CSV quality report](../reports/data_quality/data_quality_report.md) remains linked for comparison.

## Data still needed before supervised modeling

1. LLM relevance, change-specific sentiment and fix-status responses with exact evidence. Human gold labels are optional; without independent reference labels, evaluation measures teacher agreement.
2. More date-bounded reviews around the selected patch periods. Exhausted sparse periods remain unsuitable when minimum counts/date coverage are unmet.
3. Original heading/list markup for the remaining flattened announcements, from the collection archive or official sources.
4. Supported effective release times and platform/branch scope where analysis requires them. Current publication times are proxies when deployment evidence is missing.
5. Historical text/vote revisions if strictly historical evaluation is needed. Current API responses cannot recreate past states.

Follow [the annotation guide](../data/annotations/README.md), [pipeline guide](data_pipeline.md), [schema dictionary](data_dictionary.md), and [build record](../implement-stage/data-pipeline/BUILD_NOTE.md).

## Consequential semantic defaults

ASK mode is `never`: approved implementation proceeds with explicit defaults recorded before dependent code. These choices define what downstream results mean; they are not model findings.

| ID | Underdetermined choice | Chosen | Class | Source |
| --- | --- | --- | --- | --- |
| P01 | Review population | Full English export plus optional collected revisions; balanced export is inventory-only and never concatenated. | semantic | user |
| P04 | Review eligibility and language | Preserve all structurally valid reviews for votes; text eligibility >=10 Unicode word runs and Steam English; seeded language detector is an independent warning, not automatic deletion. | semantic | default |
| P05 | Normalization and evidence | NFC/whitespace only; preserve original text, negation, versions and emoji. Span offsets address the versioned canonical document, not the original markup. | semantic | user |
| P06 | Invalid data | Missing required columns or ambiguous conflicting revisions fail publication; defective records quarantine with reasons; exact repeated source records deduplicate with explicit row accounting. | semantic | default |
| P07 | Verification semantics | Separate post type, source confirmation, legacy human flag, release status and effective release time. Automatic source confirmation requires recovered official content and explicit patch evidence; legacy hard-coded flags remain legacy assertions until audited. | semantic | default |
| P08 | Change extraction | Deterministic structural fragments are change candidates; inherited title/heading context retained. Planned/known-issue/workaround scope overrides isolated fix wording; ambiguous or flattened fragments require review. | semantic | default |
| P09 | Release times and events | Publication timestamp is only a proxy unless an explicit release timestamp with zone is supported. Keep posts/events distinct; report overlapping windows and known branch/platform scopes. | semantic | default |
| P10 | Window screen | Default +/-14 days; >=30 eligible reviews and >=7 distinct UTC dates each side, with observed range covering full window; stronger screen >=100. Screen is sample availability, not power or causal validity. | semantic | user |
| P11 | Candidate matching | Per-game lexical shortlist, >=2 informative shared terms, at most 5 changes/review/task; feedback uses preceding 14 days, retrospective complaint-resolution uses subsequent 90 days. Record candidates, temporal direction and unknown scope; no inferred relevance labels. | semantic | default |
| P12 | Dataset splits | Seed 42, 10 development games (8 train/2 validation) and 20 held-out games for current 30-game corpus; configurable for other datasets. Keep revisions/derived records in same split, exclude cross-split exact/high-similarity duplicate families from supervised eligible exports. | semantic | default |
| P13 | Annotation and training readiness | Gold labels only from explicit validated adjudicated human annotation imports. Preserve disagreement; no automatic gold labels or random negatives. Empty labeled exports are valid and reported as not training-ready. | semantic | user |
| P14 | Duplicate similarity | Exact casefolded whitespace-normalized families plus bounded SimHash/sequence-similarity near-duplicate inspection; flag saturated buckets and avoid claiming exhaustive paraphrase detection. | semantic | default |
| P16 | Raw privacy | Retain source text and relevant API fields; pseudonymize author IDs with a local ignored salt before persistence; no SteamID/profile data in model exports. Different legacy hash namespaces are not assumed joinable. | semantic | default |
| P17 | Revisions and raw source recovery | Import original archives when present. Re-fetched content is a new observation with retrieval time; it never substitutes silently for a historical CSV revision. No fabricated historical edits. | semantic | user |
| P19 | Model input contract | Tokenizer-independent full passages and context; model-specific tokenization/truncation handled by loader adapter, never destructive preprocessing. Recommendation is not change-specific sentiment. | semantic | user |
| P20 | Label resolution | Relevant human labels require exact review/change evidence; irrelevant labels require sentiment/fix status not_applicable. Only consistent active adjudicated labels enter supervised exports. Explicit same-candidate supersedes IDs resolve older decisions; conflicts remain excluded. | semantic | default |
| P22 | Retrospective vs feedback candidates | Complaint-resolution candidates can use any subsequent announcement change; feedback candidates require a preceding patch post. Publication availability is enforced in feedback matching; historical edits remain an explicit current-snapshot limitation. | semantic | default |
| P25 | Stronger window coverage evidence | A fully exhausted dated API query on both sides can establish window coverage even without observations outside the interval. Counts/date thresholds stay unchanged; expose API evidence separately from the weaker observed-date-range proxy. | semantic | default |
| P27 | Document-title status scope | Include the document title alongside inherited headings when assigning weak change-status hints; known-issue/planned/workaround context overrides isolated fix language. Hints remain reviewable candidates. | semantic | sweep |
| P29 | Ambiguous announcement observation order | Conflicting announcement bodies/titles at the same observation time and structural-quality tier fail publication, including ties with unknown retrieval times. Supply trustworthy observation provenance or resolve the input conflict rather than choosing a revision hash as chronology. | semantic | sweep |
| P30 | Annotation sampling population | Deterministically hash-order candidates within game/task/split groups, then sample round-robin across groups. The queue is balanced for annotation coverage rather than proportional to candidate frequency. | semantic | sweep |
| P31 | Default paired passage | Choose the review passage with the most shared retrieval terms for each pair, with earliest-passage tie-breaking. Preserve full review text alongside it so models/annotators can inspect all context. | semantic | sweep |
| P32 | Promotional/event change population | Posts classified as promotion or event produce no change candidates, even if a mixed post contains a substantive change. Preserve their documents for inspection; revise classification or add reviewed support before treating such changes as candidates. | semantic | sweep |
| P33 | Supervised readiness threshold | supervised_training_ready means at least one accepted train pair exists. It is an availability flag only; label volume, class coverage and annotation quality require separate assessment. | semantic | sweep |

## Interface choices

| ID | Underdetermined choice | Chosen | Class | Source |
| --- | --- | --- | --- | --- |
| P02 | Storage and publication | Versioned Parquet snapshots, zstd level 3, sorted rows, 65,536-row groups, no per-game tiny-file partitions at current scale; rebuildable DuckDB views; publish by directory rename then atomic latest pointer. | interface | default |
| P03 | Identifiers and missingness | App ID int64; Steam source IDs strings; UTC microsecond timestamps; absent metadata null; source/revision IDs and hashes stable. | interface | default |
| P15 | Collection budget | Separate explicit online commands; cached/resumable public Steam news and date-bounded review collection, configurable request/page budgets, retries and delay. Prioritize known patch IDs and 25 well-covered candidate windows. Capped/failed/future-ended windows remain incomplete. | interface | default |
| P18 | Orchestration and reproducibility | Reusable stage functions and small wrappers with one offline build command; content snapshot identity covers config, sources, annotation inputs and implementation; logs/time outside deterministic payload comparisons. | interface | default |
| P21 | Publication coordination | Portable exclusive directory lock, removed on normal exit; interrupted-run lock requires operator inspection/removal. Refuse publication if source/config/code fingerprint changes during the build. | interface | default |
| P23 | External changelog references | Preserve outgoing link targets and Steam redirect destinations; external domains require confirmation before adding a fetch adapter. No automatic broad web crawl. | interface | default |
| P24 | One-command preparation | prepare-data is offline by default; --online shares the configured total HTTP request budget across recovery/backfill. Page caps apply per invocation so later runs resume. Backfill prioritizes insufficient fully elapsed windows, retaining future periods as gaps. | interface | default |
| P26 | Exhausted sparse windows during resume | Skip fully exhausted exact-bound queries when scheduling subsequent online runs, even if review counts remain inadequate; retain those deficits in the quality report. This lets the bounded scheduler advance to other patches. Explicit --refresh revisits exhausted sources. | interface | default |
| P28 | Collection evidence in snapshot identity | Only sorted fully completed exact-bound query evidence changes the dataset identity; collection report generation times, request counts and progress diagnostics remain operational metadata. Raw recovered observations still retain their source hashes and retrieval times. | interface | sweep |

## Verification record

The regression suite passes 62 tests, Ruff passes, and the final actual snapshot passes 175 publication gates. Repeating the offline orchestration reused the same snapshot and preserved the existing annotation queue. Original CSV checksums are unchanged. Examples and notebook code executed against actual published tables.

All five implementation rungs passed. The fresh assumption review found four undeclared semantic defaults and three stale ledger rows in round one; these were documented/corrected. Round two found zero remaining gaps. This is a same-family, provisional review, recorded separately from deterministic checks in [the build note](../implement-stage/data-pipeline/BUILD_NOTE.md) and its adjacent raw audit artifacts. No live stubs remain.

## LLM-only extension (pipeline 1.1.0)

The user requested operation without human annotators. `prepare-data` now exports a self-contained LLM job instead of requiring a human queue. `llm-annotations-export` produces Markdown batches, JSONL inputs, instructions, a response schema and frozen membership metadata. `llm-annotations-import` accepts file/directory responses, validates exact canonical quotes and machine provenance, and writes separate `llm_labels.jsonl`. Repeated imports are idempotent.

The pipeline publishes `llm_annotations.parquet` and `silver_pairs.parquet`; the model loader supports `labeled=True, label_source="llm"`. No human adjudication or human labels are required to train on this route. Uncertain/conflicting machine decisions and cross-split duplicates are excluded. Model/run/prompt identity, evidence, rationale and self-reported confidence remain auditable. No model API is called by these file tools.

Evaluation using silver references measures agreement with their labeling process, not independently validated human accuracy. Current export covers the lexical candidate population. See [the full commands and interpretation guide](llm_annotation_workflow.md).

A full run encountered a real CSV/API whitespace-only review difference under the same review/update ID. Both raw observations are now retained, equivalent canonical text/vote is accepted, and the latest observed metadata wins. Real canonical-text or vote conflicts still fail. This has a dedicated regression test.

### Extension decisions

Verification: 70 unit tests, Ruff and 196 actual publication gates passed. The actual snapshot has 76,861 reviews and 29,183 candidate pairs. A 20-example pilot in four Markdown batches exists at `data/annotations/llm_jobs/pilot`; no real LLM responses have been imported yet. The default prepare-data job exports up to 100 examples. Earlier review results above describe version 1.0; this extension is executor/test verified.

| ID | Underdetermined choice | Chosen | Class | Source |
| --- | --- | --- | --- | --- |
| P34 | LLM-only supervision | Human labeling is optional. Preserve machine-generated annotations and training pairs in separate llm_annotations/silver_pairs tables; human gold tables remain human-only. Models can explicitly load silver pairs without any human labels. | semantic | user |
| P35 | File transport | Export self-contained Markdown batches, response schema and manifest; import JSONL/JSON responses with an operator-supplied model/run identity. No provider API calls, credentials or paid inference are invoked. Default export covers development games only. | interface | default |
| P36 | LLM evidence and trust | Require exact canonical source quotes; compute offsets for unique quotes, require explicit start for repeated quotes. Treat all source text as untrusted task data. Record prompt version, model, run, rationale and self-reported confidence, which is not a calibrated probability. | semantic | default |
| P37 | Machine acceptance | Accept structurally valid relevant/irrelevant decisions as silver only. Exclude uncertain relevance, cross-split duplicates and candidates with conflicting active machine decisions. A single run can qualify; multiple agreeing runs improve auditability but do not establish ground truth. | semantic | default |
| P38 | Label lifetime | Import against the frozen exported snapshot and exact job membership. Preserve earlier runs; current pipeline rejects stale machine candidate IDs rather than transferring them to changed text. To correct a machine run use a new job and explicitly supersede older same-candidate machine annotation IDs. | interface | default |
| P39 | LLM-only readiness/evaluation | Expose silver training availability separately from human-supervised readiness. Evaluation against machine labels measures agreement with the labeling process; no independently validated accuracy is claimed without independent reference labels. | semantic | default |
| P40 | Bounded file batches | Default batches contain at most ten examples and 100,000 source JSON characters; never truncate evidence. Oversized individual examples remain intact in a separately flagged batch. Limit defaults are transport heuristics, not provider token limits. | interface | default |
| P41 | Default annotation handoff | prepare-data exports/preserves a dataset-specific LLM job by default and reports llm_annotation_job. Human queues remain available through their explicit export command. Job generation makes no model call; returning model response files is a separate operator step. | interface | user |
| P42 | Export/API whitespace differences | Actual online backfill returned whitespace-only differences from the CSV for identical review/update IDs. Preserve both raw revisions but accept them when canonical NFC/whitespace text and recommendation agree; use latest observed metadata for equal-update equivalent revisions. Differing canonical text or votes still fail. | semantic | default |
