"""Dataset publication gates evaluated against actual Parquet files using DuckDB."""

import json

import duckdb
import pyarrow.parquet as pq

from steam_insights.data.io import sha256
from steam_insights.pipeline.storage import SCHEMAS


def validate_snapshot(directory, *, verify_hashes=True) -> dict:
    manifest = json.loads((directory / "manifest.json").read_text())
    checks, failures = [], []
    connection = duckdb.connect()
    connection.execute("SET threads = 4")
    connection.execute("SET TimeZone = 'UTC'")
    connection.execute("SET memory_limit = '512MB'")

    def require(name, passed, detail=None):
        checks.append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            failures.append(name)

    def zero(name, sql):
        count = connection.execute(sql).fetchone()[0]
        require(name, count == 0, int(count))

    for name, contract in SCHEMAS.items():
        path = directory / (name + ".parquet")
        require(name + ":exists", path.exists())
        if not path.exists():
            continue
        schema = pq.read_schema(path)
        require(
            name + ":schema",
            list(schema.names) == list(contract)
            and all(schema.field(k).type == v for k, v in contract.items()),
        )
        metadata = manifest["tables"].get(name, {})
        require(name + ":row_count", pq.read_metadata(path).num_rows == metadata.get("rows"))
        if verify_hashes:
            require(name + ":sha256", sha256(path) == metadata.get("sha256"))
        escaped = str(path.resolve()).replace("'", "''")
        connection.execute(f"CREATE VIEW \"{name}\" AS SELECT * FROM read_parquet('{escaped}')")
    if failures:
        connection.close()
        raise ValueError("Dataset contract failed: " + ", ".join(failures))
    primary_keys = {
        "games": "appid",
        "source_records": "source_record_id",
        "quarantine": "source_record_id",
        "review_revisions": "review_revision_id",
        "reviews": "appid, review_id",
        "review_passages": "passage_id",
        "announcement_revisions": "announcement_revision_id",
        "announcements": "appid, post_id",
        "announcement_blocks": "block_id",
        "announcement_links": "link_id",
        "changes": "change_id",
        "patches": "patch_id",
        "verification_evidence": "evidence_id",
        "patch_windows": "patch_id",
        "candidates": "candidate_id",
        "annotations": "annotation_id",
        "model_review_inputs": "passage_id",
        "model_change_inputs": "change_id",
        "model_pair_inputs": "candidate_id",
        "labeled_pairs": "candidate_id",
        "llm_annotations": "annotation_id",
        "silver_pairs": "candidate_id",
    }
    for table, key in primary_keys.items():
        zero(
            table + ":unique_keys",
            f"SELECT count(*) FROM (SELECT {key} FROM {table} GROUP BY {key} HAVING count(*) > 1)",
        )
        for field in key.split(", "):
            zero(
                table + ":non_null_key:" + field,
                f'SELECT count(*) FROM {table} WHERE "{field}" IS NULL',
            )
    for table in SCHEMAS:
        if "split" in SCHEMAS[table]:
            zero(
                table + ":game_split",
                f"SELECT count(*) FROM {table} t LEFT JOIN games g USING(appid) WHERE t.split IS NULL OR g.appid IS NULL OR t.split <> g.split",
            )
    for child, child_key, parent, parent_key in [
        ("reviews", "review_revision_id", "review_revisions", "review_revision_id"),
        ("review_passages", "review_revision_id", "reviews", "review_revision_id"),
        (
            "announcements",
            "announcement_revision_id",
            "announcement_revisions",
            "announcement_revision_id",
        ),
        (
            "announcement_blocks",
            "announcement_revision_id",
            "announcements",
            "announcement_revision_id",
        ),
        (
            "announcement_links",
            "announcement_revision_id",
            "announcements",
            "announcement_revision_id",
        ),
        ("changes", "block_id", "announcement_blocks", "block_id"),
        ("patches", "announcement_revision_id", "announcements", "announcement_revision_id"),
        (
            "verification_evidence",
            "announcement_revision_id",
            "announcement_revisions",
            "announcement_revision_id",
        ),
        ("patch_windows", "patch_id", "patches", "patch_id"),
        ("candidates", "review_revision_id", "reviews", "review_revision_id"),
        ("candidates", "change_id", "changes", "change_id"),
        ("annotations", "candidate_id", "candidates", "candidate_id"),
        ("model_review_inputs", "passage_id", "review_passages", "passage_id"),
        ("model_change_inputs", "change_id", "changes", "change_id"),
        ("model_pair_inputs", "candidate_id", "candidates", "candidate_id"),
        ("labeled_pairs", "annotation_id", "annotations", "annotation_id"),
        ("llm_annotations", "candidate_id", "candidates", "candidate_id"),
        ("silver_pairs", "annotation_id", "llm_annotations", "annotation_id"),
    ]:
        zero(
            f"{child}:{child_key}:foreign_key",
            f"SELECT count(*) FROM {child} c LEFT JOIN {parent} p ON c.{child_key}=p.{parent_key} WHERE p.{parent_key} IS NULL",
        )
    for table in ("review_revisions", "announcement_revisions"):
        zero(
            table + ":source_lineage",
            f"SELECT count(*) FROM {table} t LEFT JOIN source_records s USING(source_record_id) WHERE s.source_record_id IS NULL",
        )
    for child, parent, link, canonical in [
        ("review_passages", "reviews", "review_revision_id", "review_text"),
        ("announcement_blocks", "announcements", "announcement_revision_id", "canonical_text"),
        ("changes", "announcements", "announcement_revision_id", "canonical_text"),
    ]:
        zero(
            child + ":exact_offsets",
            f"SELECT count(*) FROM {child} c JOIN {parent} p USING({link}) WHERE c.char_start < 0 OR c.char_end <= c.char_start OR c.char_end > length(p.{canonical}) OR c.text <> substr(p.{canonical}, c.char_start + 1, c.char_end - c.char_start)",
        )
    zero(
        "verification:exact_offsets",
        """SELECT count(*) FROM verification_evidence e
        JOIN announcement_revisions d USING(announcement_revision_id)
        WHERE e.char_start < 0 OR e.char_end <= e.char_start OR
        e.evidence_text <> substr(CASE WHEN e.field='title' THEN d.title ELSE d.canonical_text END,
            e.char_start + 1, e.char_end-e.char_start)""",
    )
    zero(
        "patches:verification_has_evidence",
        """SELECT count(*) FROM patches p WHERE p.verified_for_analysis
        AND NOT EXISTS (SELECT 1 FROM verification_evidence e WHERE e.announcement_revision_id=p.announcement_revision_id)""",
    )
    zero(
        "candidates:parent_game_consistency",
        """SELECT count(*) FROM candidates c JOIN reviews r USING(review_revision_id)
        JOIN changes ch USING(change_id) WHERE c.appid <> r.appid OR c.appid <> ch.appid OR c.split <> ch.split""",
    )
    settings = manifest["configuration"]["candidates"]
    zero(
        "candidates:feedback_time",
        f"""SELECT count(*) FROM candidates c JOIN reviews r USING(review_revision_id)
        LEFT JOIN patches p USING(patch_id) JOIN announcements d ON c.announcement_revision_id=d.announcement_revision_id
        WHERE c.task='post_patch_feedback' AND (p.patch_id IS NULL OR d.publication_utc > r.created_utc OR
        r.created_utc < p.anchor_utc OR r.created_utc >= p.anchor_utc + INTERVAL '{settings["feedback_days"]} days')""",
    )
    zero(
        "candidates:resolution_time",
        f"""SELECT count(*) FROM candidates c JOIN reviews r USING(review_revision_id)
        JOIN announcements d ON c.announcement_revision_id=d.announcement_revision_id
        WHERE c.task='retrospective_complaint_resolution' AND (d.publication_utc <= r.created_utc OR
        d.publication_utc > r.created_utc + INTERVAL '{settings["resolution_days"]} days')""",
    )
    zero(
        "candidates:bounded",
        f"SELECT count(*) FROM (SELECT review_revision_id, task FROM candidates GROUP BY ALL HAVING count(*)>{settings['max_per_review_per_task']})",
    )
    zero(
        "model_pairs:exact_review_passage",
        "SELECT count(*) FROM model_pair_inputs WHERE review_passage_text <> substr(review_text, review_char_start+1, review_char_end-review_char_start)",
    )
    zero(
        "model_pairs:exact_change",
        "SELECT count(*) FROM model_pair_inputs m JOIN changes c USING(change_id) WHERE m.change_text<>c.text OR m.change_context<>c.context_text",
    )
    zero(
        "labeled_pairs:human_only",
        "SELECT count(*) FROM labeled_pairs l JOIN annotations a USING(annotation_id) WHERE a.label_source<>'human' OR NOT a.adjudicated",
    )
    zero(
        "labeled_pairs:no_flagged_duplicates",
        "SELECT count(*) FROM labeled_pairs WHERE cross_split_duplicate",
    )
    zero(
        "llm_annotations:machine_only",
        "SELECT count(*) FROM llm_annotations WHERE label_source IS DISTINCT FROM 'llm' OR adjudicated IS DISTINCT FROM false",
    )
    zero(
        "silver_pairs:machine_only",
        "SELECT count(*) FROM silver_pairs WHERE label_source IS DISTINCT FROM 'llm'",
    )
    zero(
        "silver_pairs:no_flagged_duplicates",
        "SELECT count(*) FROM silver_pairs WHERE cross_split_duplicate",
    )
    zero(
        "silver_pairs:accepted_relevance",
        "SELECT count(*) FROM silver_pairs WHERE relevance IS NULL OR relevance NOT IN ('relevant','irrelevant')",
    )
    for prefix, parent, key, canonical in [
        ("review", "reviews", "review_revision_id", "review_text"),
        ("change", "announcements", "announcement_revision_id", "canonical_text"),
    ]:
        zero(
            "llm_annotations:exact_" + prefix + "_evidence",
            f"""SELECT count(*) FROM llm_annotations a
            JOIN candidates c USING(candidate_id) JOIN {parent} p ON c.{key}=p.{key}
            WHERE a.{prefix}_evidence_text IS NOT NULL AND
            (a.{prefix}_evidence_start < 0 OR a.{prefix}_evidence_end <= a.{prefix}_evidence_start OR
            a.{prefix}_evidence_text <> substr(p.{canonical}, a.{prefix}_evidence_start+1, a.{prefix}_evidence_end-a.{prefix}_evidence_start))""",
        )
    for field in ("exact_duplicate_group", "near_duplicate_group"):
        zero(
            "labeled_pairs:no_leakage:" + field,
            f"""SELECT count(*) FROM labeled_pairs l JOIN review_revisions r USING(review_revision_id)
            WHERE r.{field} IN (SELECT {field} FROM review_revisions WHERE {field} IS NOT NULL GROUP BY {field} HAVING count(DISTINCT split)>1)""",
        )
    for dataset in ("reviews", "announcements"):
        stats = manifest["stages"][dataset]
        count = connection.execute(
            "SELECT count(*) FROM source_records WHERE dataset=?", [dataset]
        ).fetchone()[0]
        require(
            dataset + ":source_accounting",
            count == stats["source_rows"] == stats["valid_source_rows"] + stats["quarantined_rows"],
        )
    connection.close()
    if failures:
        raise ValueError(
            "Dataset invariant failed: "
            + ", ".join(
                f"{item['check']} ({item['detail']})" for item in checks if not item["passed"]
            )
        )
    return {"passed": True, "checks": len(checks), "results": checks}
