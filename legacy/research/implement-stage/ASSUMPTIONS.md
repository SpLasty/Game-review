# Assumption ledger — initial data foundation

ASK mode: never. Effort: lite. Assurance: draft.

| ID | Under-determined by request | Chosen | Class | Source |
|---|---|---|---|---|
| A-001 | Which dataset is authoritative for initial counting? | All English review CSV; balanced export is compared separately and never concatenated as additional observations. | semantic | default |
| A-002 | How much text cleaning? | Preserve source text, case, negation, numbers and emoji; add NFC/whitespace-normalized text separately. No stop-word removal, stemming or inferred headings. | semantic | default |
| A-003 | Which reviews survive preprocessing? | Keep all valid rows, including short, edited and negative reviews. Add a configurable minimum-word eligibility flag and a separate long-text view; no sentiment balancing. | semantic | default |
| A-004 | What do existing keyword and patch flags mean? | Preserve them as unverified heuristics, not training labels or confirmed patches. Recommendation remains an observed Steam vote, not target sentiment. | semantic | default |
| A-005 | Invalid rows and duplicates? | Profiling reports them; preprocessing fails on invalid required fields, duplicate keys or conflicting timestamp representations instead of silently dropping or repairing records. Missing optional fields stay nullable. | semantic | default |
| A-006 | How are edited reviews interpreted? | Creation/update times describe the exported latest snapshot; equality is a proxy for no recorded edit. No historical state reconstruction or patch-effect claims. | semantic | default |
| A-007 | Entry points and configuration? | Python >=3.11 src package, `steam-insights profile/preprocess` CLI, TOML config relative to the project root, uv dependency environment/lock. | interface | default |
| A-008 | Generated artifacts? | Aggregate reports under `reports/data_exploration/`; new Parquet under `data/interim/steam_30_games/`; deterministic ordering and a manifest. Never overwrite source CSVs or write outputs inside their directory. | interface | default |
| A-009 | Exploration notebook behavior? | Notebooks call tested package functions, with a documented repository-root cell; unexecuted tracked notebooks carry no copied review outputs. | interface | default |
| A-010 | Existing collector default rejects its own path? | Accept safe relative snapshot paths including the current `raw/steam_30_games` default; still reject absolute paths, traversal components and backslashes. This preserves existing archive paths. | interface | default |
| A-011 | What counts as a word? | Use Python Unicode `re` word runs, matching the collector, for both validation and eligibility. Do not use the Arrow-backed string-regex engine, which differs for Unicode text. | semantic | default |

## Notes

- A-003: the ten-word view is useful for detailed text work but changes the recommendation distribution; it cannot replace the all-review population for trend summaries.
- A-005: do not manufacture revision history from duplicate keys. If future live ingestion supplies revisions, that needs an explicit separate schema.
- A-008: content digests in the manifest identify the actual input snapshot; they do not assert that it is representative, complete, or a complete historical archive.
