"""Human label import, evidence validation, and explicit adjudication handling."""

import json
from collections import defaultdict

from steam_insights.pipeline.storage import parse_time, stable_id

RELEVANCE = {"relevant", "irrelevant", "uncertain"}
SENTIMENT = {
    "positive",
    "negative",
    "mixed",
    "neutral",
    "not_expressed",
    "unknown",
    "not_applicable",
}
FIX_STATUS = {
    "acknowledged",
    "planned",
    "workaround",
    "partial_fix",
    "limited_fix",
    "released_fix",
    "unknown",
    "not_applicable",
}


def read_annotation_file(path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def validate_annotations(
    records: list[dict], candidates, reviews, announcements, *, expected_source="human"
) -> list[dict]:
    by_candidate = {r["candidate_id"]: r for r in candidates}
    by_review = {r["review_revision_id"]: r for r in reviews}
    by_doc = {r["announcement_revision_id"]: r for r in announcements}
    validated = {}
    for record in records:
        required = {
            "candidate_id",
            "annotator_id",
            "label_source",
            "adjudicated",
            "created_at",
            "relevance",
            "sentiment",
            "fix_status",
        }
        if missing := required - record.keys():
            raise ValueError(f"Annotation missing fields: {sorted(missing)}")
        candidate = by_candidate.get(record["candidate_id"])
        if candidate is None:
            raise ValueError(
                f"Annotation references an unknown/stale candidate: {record['candidate_id']}"
            )
        if (
            record["label_source"] != expected_source
            or type(record["adjudicated"]) is not bool
            or not str(record["annotator_id"]).strip()
        ):
            raise ValueError(
                f"Labels require a named {expected_source} annotator and an explicit adjudicated boolean"
            )
        if (
            record["relevance"] not in RELEVANCE
            or record["sentiment"] not in SENTIMENT
            or record["fix_status"] not in FIX_STATUS
        ):
            raise ValueError("Invalid relevance, sentiment, or fix_status label")
        if record["relevance"] == "irrelevant" and (
            record["sentiment"] != "not_applicable" or record["fix_status"] != "not_applicable"
        ):
            raise ValueError("Irrelevant pairs require sentiment/fix_status=not_applicable")
        created = parse_time(record["created_at"])
        if created is None:
            raise ValueError("Annotation created_at is required")
        row = {key: record[key] for key in required}
        row["created_at"] = created
        for prefix, canonical in (
            ("review", by_review[candidate["review_revision_id"]]["review_text"]),
            ("change", by_doc[candidate["announcement_revision_id"]]["canonical_text"]),
        ):
            evidence = record.get(prefix + "_evidence")
            if evidence is None:
                if (
                    prefix + "_evidence_text" in record
                    and record[prefix + "_evidence_text"] is not None
                ):
                    evidence = {
                        "start": record[prefix + "_evidence_start"],
                        "end": record[prefix + "_evidence_end"],
                        "text": record[prefix + "_evidence_text"],
                    }
            if evidence:
                begin, end, text = evidence.get("start"), evidence.get("end"), evidence.get("text")
                if (
                    type(begin) is not int
                    or type(end) is not int
                    or not isinstance(text, str)
                    or not text
                    or not 0 <= begin < end <= len(canonical)
                    or canonical[begin:end] != text
                ):
                    raise ValueError(
                        f"Annotation {prefix} evidence offsets/text do not match canonical source"
                    )
            else:
                begin, end, text = None, None, None
            if record["relevance"] == "relevant" and not text:
                raise ValueError(f"Relevant pairs need exact {prefix} evidence")
            row.update(
                {
                    prefix + "_evidence_start": begin,
                    prefix + "_evidence_end": end,
                    prefix + "_evidence_text": text,
                }
            )
        if (
            record["sentiment"] not in {"unknown", "not_expressed", "not_applicable"}
            and row["review_evidence_text"] is None
        ):
            raise ValueError("A sentiment label requires review evidence")
        if (
            record["fix_status"] not in {"unknown", "not_applicable"}
            and row["change_evidence_text"] is None
        ):
            raise ValueError("A fix-status label requires announcement evidence")
        row["supersedes"] = sorted(set(record.get("supersedes", [])))
        identifier_payload = {**row, "created_at": created.isoformat()}
        row["annotation_id"] = stable_id(f"{expected_source}_annotation_v1", identifier_payload)
        if record.get("annotation_id") and record["annotation_id"] != row["annotation_id"]:
            raise ValueError("Annotation ID disagrees with its contents")
        validated[row["annotation_id"]] = row
    for row in validated.values():
        for old_id in row["supersedes"]:
            old = validated.get(old_id)
            if (
                old is None
                or old["candidate_id"] != row["candidate_id"]
                or old["created_at"] >= row["created_at"]
            ):
                raise ValueError(
                    "supersedes must reference an older annotation for the same candidate"
                )
    return sorted(
        validated.values(), key=lambda r: (r["candidate_id"], r["created_at"], r["annotation_id"])
    )


def labeled_exports(
    model_pairs: list[dict], annotations: list[dict], *, require_adjudicated=True
) -> tuple[list[dict], dict]:
    superseded = {identifier for row in annotations for identifier in row["supersedes"]}
    active = defaultdict(list)
    for row in annotations:
        if (row["adjudicated"] or not require_adjudicated) and row[
            "annotation_id"
        ] not in superseded:
            active[row["candidate_id"]].append(row)
    labels, conflicts = {}, 0
    for candidate_id, rows in active.items():
        decisions = {(row["relevance"], row["sentiment"], row["fix_status"]) for row in rows}
        if len(decisions) == 1 and rows[0]["relevance"] != "uncertain":
            labels[candidate_id] = min(rows, key=lambda r: r["annotation_id"])
        else:
            conflicts += 1
    result = []
    excluded_duplicates = 0
    for pair in model_pairs:
        label = labels.get(pair["candidate_id"])
        if label is None:
            continue
        if pair["cross_split_duplicate"]:
            excluded_duplicates += 1
            continue
        result.append(
            {
                **pair,
                "annotation_id": label["annotation_id"],
                "relevance": label["relevance"],
                "sentiment": label["sentiment"],
                "fix_status": label["fix_status"],
            }
        )
    return result, {
        "human_annotations": len(annotations),
        "unresolved_or_uncertain_candidates": conflicts,
        "labeled_pairs": len(result),
        "labeled_pairs_excluded_for_duplicate_leakage": excluded_duplicates,
        "supervised_training_ready": bool(any(r["split"] == "train" for r in result)),
    }


def sample_annotation_pairs(
    directory,
    *,
    sample_size=100,
    splits=("train", "validation"),
    patch_id=None,
    exclude_annotated=False,
):
    from steam_insights.pipeline.storage import read_table

    pairs = read_table(directory, "model_pair_inputs")
    candidate_by_id = {}
    if patch_id is not None:
        candidate_by_id = {row["candidate_id"]: row for row in read_table(directory, "candidates")}
        pairs = [
            row
            for row in pairs
            if candidate_by_id.get(row["candidate_id"], {}).get("patch_id") == patch_id
        ]
        if not pairs:
            raise ValueError(f"No review/change candidates found for patch {patch_id}")
    if exclude_annotated:
        labeled_ids = {row["candidate_id"] for row in read_table(directory, "llm_annotations")}
        pairs = [row for row in pairs if row["candidate_id"] not in labeled_ids]
    groups = defaultdict(list)
    for row in pairs:
        if row["split"] in splits and not row["cross_split_duplicate"]:
            key = (
                (row["appid"], row["task"], row["split"], row["change_id"])
                if patch_id is not None
                else (row["appid"], row["task"], row["split"])
            )
            groups[key].append(row)
    if patch_id is not None and not groups:
        raise ValueError(
            f"No eligible review/change candidates found for patch {patch_id} in splits {splits}"
        )
    for group in groups.values():
        if patch_id is not None:
            group.sort(
                key=lambda row: (
                    -candidate_by_id[row["candidate_id"]]["lexical_score"],
                    stable_id("annotation_sample_v1", row["candidate_id"]),
                )
            )
        else:
            group.sort(key=lambda r: stable_id("annotation_sample_v1", r["candidate_id"]))
    selected = []
    while len(selected) < sample_size and any(groups.values()):
        for key in sorted(groups):
            if groups[key] and len(selected) < sample_size:
                selected.append(groups[key].pop(0))
    return selected


def export_annotation_queue(
    directory, output, *, sample_size=100, splits=("train", "validation")
) -> dict:
    from steam_insights.pipeline.storage import read_table

    if output.exists():
        return {
            "output": str(output),
            "status": "existing_queue_preserved",
            "note": "An existing queue may contain human work; use a new output filename for another sample.",
        }
    selected = sample_annotation_pairs(directory, sample_size=sample_size, splits=splits)
    candidate_map = {r["candidate_id"]: r for r in read_table(directory, "candidates")}
    documents = {r["announcement_revision_id"]: r for r in read_table(directory, "announcements")}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in selected:
            candidate = candidate_map[row["candidate_id"]]
            document = documents[candidate["announcement_revision_id"]]
            template = {
                **row,
                "announcement_revision_id": document["announcement_revision_id"],
                "announcement_text": document["canonical_text"],
                "post_id": document["post_id"],
                "source_url": document["source_url"],
                "annotator_id": "",
                "label_source": "human",
                "adjudicated": False,
                "created_at": None,
                "relevance": None,
                "sentiment": None,
                "fix_status": None,
                "review_evidence": None,
                "change_evidence": None,
                "supersedes": [],
            }
            handle.write(json.dumps(template, ensure_ascii=False) + "\n")
    return {
        "output": str(output),
        "examples": len(selected),
        "splits": list(splits),
        "note": "Blank label fields are templates, not annotations; test games excluded by default.",
    }
