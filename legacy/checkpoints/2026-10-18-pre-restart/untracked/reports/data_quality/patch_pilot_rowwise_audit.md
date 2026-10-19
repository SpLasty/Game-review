# Sea of Thieves 3.8.1 rowwise relevance audit

Updated: 2026-10-18

## Scope and method

This audit covers the 200 train pairs in `data/annotations/llm_jobs/sot-381-pilot`, frozen against dataset `5c8a356cb9aa33235617e46eb2b6597db40ed77ee1967ed71be2ec0b65f633c7`. The candidate pool contains 348 pairs from the lexical retriever. The sample is stratified over change/task groups and prioritizes lexical rank; it is not a probability sample.

Each full Steam review was compared with its candidate's specific change text and the available announcement title, heading, and surrounding passage. A same-game opinion, a Steam Recommended vote, or broad word overlap such as “ship,” “players,” “visual,” or “loot” was not accepted as evidence that the review discusses a change. A review had to identify the change or the specific issue it addresses. When the announcement extraction contained only a section heading, or a symptom overlapped while the described trigger differed, the pair remained uncertain.

The corrected responses use model label `GPT-6`, run ID `codex-gpt6-sot381-row-audit-2026-10-18`. They explicitly supersede the first run's decision for each of the 200 candidates. This is an LLM-only correction pass; it is not human adjudication or an independent accuracy check.

## Results

| Task | Pairs | Relevant | Irrelevant | Uncertain |
|---|---:|---:|---:|---:|
| Post-patch feedback | 126 | 0 | 118 | 8 |
| Retrospective complaint resolution | 74 | 0 | 72 | 2 |
| **Total** | **200** | **0** | **190** | **10** |

| Lexical rank within change/task | Relevant | Irrelevant | Uncertain |
|---|---:|---:|---:|
| 1 | 0 | 147 | 8 |
| 2 | 0 | 43 | 2 |

The 10 uncertain cases are:

| Candidate ID | Why it remains uncertain |
|---|---|
| `9d826c4a801826c7b852d88a194f7fdf268e1e9ed2cf70ab9b7ee2f017ce8609` | The review reports both audio and visual bugs, while the candidate contains only the “Visual and Audio” section heading, not an atomic change. |
| `53574d7668084f7172b192f8458d4abe63328446c7bf90eb2a326920b50ad935` | A boat is launched skyward by storm waves in the review; the patch concerns ships blocking spawn points at Legendary Locations. The symptom overlaps, but the trigger differs. |
| `9038f1e1dce18999f75145f70d8aa304ba4f69e93d5ad9d2b9917c8ef35c3681` | The review criticizes Custom Seas broadly; the candidate is only the “Custom Seas – Legendary Locations” heading. |
| `544681e16a6475f0b7cf438a210d858236fcd63e38515af56008f77d6bb53ccb` | The review objects to Custom Seas as a mode; the change adds a particular practice preset, which the review does not mention. |
| `32980cd43d4303589c104523d0173b82148a3b3f31bc9fecbbb2c03e7355487f` | Both sources mention a black loading screen, but the review describes a connection interruption while sailing and the patch describes matchmaking at battle start. |
| `418f0d49a1f374ecea7c20c93617f8f29325f840dccb63bcec1e78db22d0ef5a` | The review criticizes Custom Seas generally; the candidate contains only a “Custom Seas” heading without a specific change. |
| `0580a1ebea2136d74ecfc50cfdaefb92e404fa80103bd6e8e3018f2a93244abe` | The review's shipwreck treasure disappears before recovery; the patch resets the timer only after treasure is retrieved and dropped into the sea again. |
| `7a49bede7010160aaf9433c0b6bbc45c5c3dac35f5b9b61b2647324fa59bbcbd` | The review praises Custom Seas broadly; it does not identify the specific new official practice preset. |
| `b425f3710d0f4a49f5d7016401464f6194a5b6a7f60b95297ddf20074ebef9ac` | The review reports unrecovered shipwreck treasure sinking; the patch describes resetting the timer only when previously retrieved treasure is dropped again. |
| `caad4bdf64e756912bd8deddf34c85566b58649c0cee1c57e967edaa38117f72` | The review says server issues are annoying but does not identify unexpected exits or session disconnections, which are the patch's stated stability cases. |

## Pipeline effect and artifacts

The previous 200 decisions are retained in `data/annotations/llm_labels.jsonl` as superseded history. The current snapshot is `cfa34941257d2905d8a2f2681de931909e1904d97bc220e9d121f3c855b4cf56`; all 196 publication checks pass. It contains 500 stored annotation records (200 superseded), 300 active decisions, 289 silver rows, and no human annotations. Active corpus-wide decisions are 6 relevant, 283 irrelevant, and 11 uncertain. Across all 202 currently labeled candidates for this patch, there are 192 irrelevant and 10 uncertain decisions, with no relevant decision.

The machine-readable rowwise responses and individual rationales are in the local, Git-ignored file `data/annotations/llm_jobs/sot-381-pilot/rowwise-audit/responses-0001.jsonl`. The corrected task/rank report is `data/annotations/llm_jobs/sot-381-pilot/retrieval_audit_report.md`; the earlier report is retained at `data/annotations/llm_jobs/sot-381-pilot/rowwise-audit/first_pass_retrieval_audit_report.md`. The full 348-pair lexical sidecar is `data/annotations/llm_jobs/sot-381-pilot/retrieval_audit.csv`.

The absence of relevant rows in this sample suggests that generic lexical overlap is surfacing many unrelated review/change pairs for this patch. It is not a corpus precision estimate, it cannot reveal relevant pairs omitted by the retriever, and it does not show whether patch 3.8.1 caused a change in sentiment. The next retrieval evaluation should include a separately sampled set of noncandidate pairs and should inspect announcement blocks where extraction produced only headings.

## Follow-up input-consistency check

On 2026-10-18, the uncertain-row rationales were checked against the frozen `model_pair_inputs.parquet` rows. Two rationales do not describe their stored review input:

| Candidate ID | Stored review/change pair | Audit rationale issue |
|---|---|---|
| `0580a1ebea2136d74ecfc50cfdaefb92e404fa80103bd6e8e3018f2a93244abe` | “Sea of thieves is a good time to play with friends” vs. the sink-timer reset after retrieved treasure is dropped into the sea again. | The rationale claims the review describes shipwreck treasure disappearing before recovery; that complaint is absent from the stored review. This pair appears irrelevant and should be corrected in a new annotation run. |
| `caad4bdf64e756912bd8deddf34c85566b58649c0cee1c57e967edaa38117f72` | A broadly positive review that mentions losing treasure to another crew vs. a stability change for unexpected exits/session disconnects. | The rationale says the review complains about server issues; the stored review does not. This pair appears irrelevant and should be corrected in a new annotation run. |

The stored rowwise counts above remain 190 irrelevant and 10 uncertain until these two annotation records are superseded and the snapshot is rebuilt. If both are corrected to irrelevant, the audited sample would be 192 irrelevant and 8 uncertain, still with no relevant pair. This is an input/rationale consistency problem in the LLM audit, not evidence that the retriever found relevant matches. The rationale for candidate `b425f3710d0f4a49f5d7016401464f6194a5b6a7f60b95297ddf20074ebef9ac` also describes more detail than the stored review states; the review says another crew sinks the player's ship and haul, but does not describe the patch's retrieved-then-redropped treasure sequence. Keep that pair uncertain pending a corrected, source-grounded rationale.
