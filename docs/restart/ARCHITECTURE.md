# Proposed patch-grounded relevance architecture

Status: Stages 1–4 now have separate implementations under `src/steam_patch_relevance/`. Stage 4 is a bounded LLM-silver pilot; full-scale labeling and model training are not authorized by that pilot. See the [Stage 4 handoff](stage4/HANDOFF.md) for current results.

## Scope and guiding decision

The unit of analysis is **one review revision against one atomic change in one specific patch**. A review can mention zero, one, or several changes; a Steam Recommended vote is not a per-change sentiment label. Patch publication time and effective release time are separate fields. A Steam announcement is not automatically a patch, and a publisher's Major Update or Small Update category is evidence about the post, not proof of a build or a precise release time.

The first relevance pilot will sample reviews independently of lexical retrieval and show the model the entire numbered change list for the patch. This directly tests whether specific changes are discussed and avoids the earlier five-candidate cap. Retrieval may be added later for scale only after a full-list reference sample exposes its misses. Machine judgments remain silver labels; without independent adjudication they cannot be presented as human ground truth.

## Proposed repository and storage boundary

```text
src/steam_patch_relevance/           New package; no imports from steam_insights
  cli.py                              One CLI dispatcher
  sources/                            Steam clients, cursors, immutable response records
  normalize/                          Review revisions and announcement documents
  patches/                            Patch classification and atomic change extraction
  labeling/                           Full-list prompts, parsing, quote validation
  evaluation/                         Audits, coverage, disagreement and baseline metrics
  storage/                            Schemas, IDs, manifests, Parquet read/write
configs/relevance_v1.toml            New paths, budgets, sampling and schema versions
data/relevance_v1/raw/               Immutable fetched payloads plus provenance
data/relevance_v1/normalized/        Validated reviews, announcements, patches, changes
data/relevance_v1/labels/            Versioned machine decisions and audit samples
data/relevance_v1/runs/              Run manifests and derived Parquet tables
reports/relevance_v1/                New quality and evaluation reports only
tests/relevance_v1/                  Synthetic contract and bounded integration tests
docs/restart/                        Design, decisions, handoff and status
legacy/                              Historical handoffs, reports and checkpoint
```

The namespace and storage prefix prevent old snapshot IDs, silver labels, candidate tables, or reports from being resolved by default. A deliberate `import-legacy-source` operation could be designed later, with a source hash and explicit transformation record; it is not part of the first implementation. Existing `data/` directories and `steam_insights` are read-only historical inputs for the new system.

## Proposed data contracts

All timestamps are UTC, source identifiers are strings, and every derived row records source IDs, version, and run ID. Original text and raw response hashes are preserved. Invalid or ambiguous records are retained with a reason rather than silently dropped.

| Table | Required core fields | Rule |
| --- | --- | --- |
| `source_observations` | `source_id`, `appid`, `source_kind`, `url_or_endpoint`, `fetched_at_utc`, `payload_sha256`, `cursor`, `status` | Immutable acquisition record; repeated fetches create observations, not overwritten truth. |
| `announcements` | `announcement_id`, `appid`, `published_at_utc`, `title`, `body_original`, `publisher_category`, `category_provenance`, `source_id` | Preserve publisher tags if observed; classify post type separately. `release_at_utc` may be null. |
| `patches` | `patch_id`, `announcement_id`, `patch_status`, `published_at_utc`, `release_at_utc`, `platform`, `branch`, `verification_evidence` | Distinguish patch note, other update, promotion, event, and uncertain; never infer release time from publication alone. |
| `changes` | `change_id`, `patch_id`, `ordinal`, `heading_path`, `change_text`, `source_span_start`, `source_span_end`, `atomicity_status` | Each numbered item must point to exact source text; headings alone are not atomic changes. |
| `review_revisions` | `review_id`, `appid`, `updated_at_utc`, `created_at_utc`, `text_original`, `recommended`, `language`, `source_id` | Keep edited revision provenance; review vote stays separate from change sentiment. |
| `review_patch_samples` | `sample_id`, `patch_id`, `review_revision_id`, `selection_rule`, `seed`, `eligible_population`, `window_rule` | Random full-list samples must be reproducible and independent of retrieval. |
| `relevance_decisions` | `decision_id`, `sample_id`, `change_id` nullable, `label`, `review_quote`, `change_quote`, `rationale`, `model_id`, `prompt_version`, `run_id` | Labels: `relevant`, `no_match`, `uncertain`. Exact quote/source-span validation is required for relevant decisions. No-match is review-level; multiple relevant change IDs are allowed. |

Identifiers use a new `rv1_` prefix and deterministic hashes of typed, canonical keys. They must never be copied from old dataset IDs. Every run manifest records source hashes, schema/parser/prompt versions, sampling seed, model identity, and output hashes. Parquet is the derived-table format; JSONL stores immutable raw payloads and label responses. DuckDB is for local inspection and validation, not a service or source of truth.

## Proposed data flow

```text
app IDs / public Steam responses
    -> immutable source observations and coverage ledger
    -> announcement type review and exact patch/change extraction
    -> normalized review revisions
    -> reproducible post-patch full-list review sample
    -> LLM relevance decisions with exact evidence + uncertainty
    -> validation, disagreement audit, quality report
    -> optional relevance baseline after enough positives exist
```

Coverage is reported per app, patch, language, time interval, pagination status, and announcement source. A bounded request budget and persisted cursor make collection resumable; no `event_type=12/13` filter is assumed for the documented public `GetNewsForApp` API. When available, publisher category is stored with provenance and checked against the actual post content. For matching, full-list judgments are primary pilot evidence; future retrieval is evaluated against random full-list samples and cannot silently exclude candidate pairs.

## Multilingual strategy for later stages

Steam's review API defaults to English when `languages` is empty; this collector explicitly requests `['all']` by default. The source text and Steam API language code remain unchanged. `detected_language` and `detected_language_confidence` are separate nullable derived fields, and announcement-language metadata has its own field because the news feed may omit it. No translation or language detector runs during ingestion.

| Stage | Multilingual requirements |
| --- | --- |
| 2 — normalization and extraction | Use Unicode-safe, language-aware claim extraction; preserve exact original-language evidence spans; retain game-specific terminology and mixed-language terms. |
| 3 — relevance retrieval | Benchmark multilingual embeddings alongside lexical and entity-based retrieval; include matching non-English reviews to English patch changes; report retrieval quality separately by review language and for cross-language pairs. Translate only when a specific error analysis shows it is needed, rather than translating the full corpus. |
| 4 — LLM decisions | Use multilingual labeling where supported; require exact quotations from original-language review text; retain model-generated labels as a separate machine-evidence layer, distinct from any independently verified judgments. |
| 5 — evaluation | Report relevance performance by review language, patch/change language, and cross-language pair, including sample sizes and uncertainty. |

Language coverage is part of collection quality, not an inference about relevance or sentiment. Sampling and retrieval must not silently discard lower-volume language groups.

The `steam-relevance` CLI includes `collect`, offline `materialize`, `inspect`, optional keyed `catalog`, `stage2 extract`, `stage3 retrieve`, and `stage4 export/import`. Stage 4's file-based workflow and current boundaries are documented in [`stage4/ARCHITECTURE.md`](stage4/ARCHITECTURE.md) and [`stage4/DATA_CONTRACTS.md`](stage4/DATA_CONTRACTS.md).

## Deliberate exclusions

Stage 1 will be a local, modular workflow. There are no microservices, orchestration framework, model registry, DVC, MLflow, deployment, or scheduled job in this design. Those choices would add maintenance before source coverage, change granularity, and relevance evidence are established.
