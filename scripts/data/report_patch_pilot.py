"""Summarize an LLM-labeled patch pilot against its lexical retrieval audit."""

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def _read_response_file(path):
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("```") and text.endswith("```"):
        text = "\n".join(text.splitlines()[1:-1]).strip()
    if text.startswith("["):
        rows = json.loads(text)
    else:
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"Expected JSON objects in {path}")
    return rows


def _read_responses(path):
    files = (
        sorted(path.rglob("*.jsonl")) + sorted(path.rglob("*.json")) if path.is_dir() else [path]
    )
    if not files:
        raise ValueError(f"No JSON/JSONL response files found in {path}")
    rows = [row for file in files for row in _read_response_file(file)]
    by_id = {}
    for row in rows:
        candidate_id = row.get("candidate_id")
        if not isinstance(candidate_id, str) or candidate_id in by_id:
            raise ValueError("Responses must have unique string candidate_id values")
        by_id[candidate_id] = row
    return by_id


def _rank_band(rank):
    value = int(rank)
    return str(value) if value <= 2 else "3+"


def build_report(job, responses):
    manifest = json.loads((job / "manifest.json").read_text(encoding="utf-8"))
    audit_path = job / "retrieval_audit.csv"
    with audit_path.open(encoding="utf-8", newline="") as handle:
        audit = list(csv.DictReader(handle))

    sample = [row for row in audit if row["sampled_for_labeling"].lower() == "true"]
    labels = _read_responses(responses)
    selected_ids = {row["candidate_id"] for row in sample}
    outside = sorted(set(labels) - selected_ids)
    joined = [(row, labels[row["candidate_id"]]) for row in sample if row["candidate_id"] in labels]
    relevance = Counter(label.get("relevance", "missing") for _, label in joined)
    by_task = defaultdict(Counter)
    by_rank = defaultdict(Counter)
    shared_terms = Counter(
        term for row in sample for term in row["shared_terms"].split("|") if term
    )
    for audit_row, label in joined:
        value = label.get("relevance", "missing")
        by_task[audit_row["task"]][value] += 1
        by_rank[_rank_band(audit_row["lexical_rank_within_change"])][value] += 1

    def counter_table(items, heading, first_column):
        present = {key for counts in items.values() for key in counts}
        values = ["relevant", "irrelevant", "uncertain"]
        values.extend(sorted(present - set(values)))
        lines = [
            f"| {first_column} | " + " | ".join(values) + " |",
            "|---|" + "|".join("---:" for _ in values) + "|",
        ]
        for name in sorted(items):
            lines.append(
                f"| {name} | " + " | ".join(str(items[name][key]) for key in values) + " |"
            )
        return [f"### {heading}", "", *lines]

    lines = [
        "# Patch Pilot Retrieval Audit",
        "",
        f"- Dataset: `{manifest['dataset_id']}`",
        f"- Patch: `{manifest.get('patch_id')}`",
        f"- Sampling: {manifest.get('sampling_strategy')}",
        f"- Lexical candidate pool in audited splits: {len(audit)}",
        f"- Labeled sample: {len(sample)}",
        f"- Responses received for sample: {len(joined)}",
        f"- Responses missing: {len(sample) - len(joined)}",
        f"- Responses outside this sampled job: {len(outside)}",
        "",
        "## Relevance labels",
        "",
        "| Label | Count |",
        "|---|---:|",
        *[f"| {name} | {relevance[name]} |" for name in ("relevant", "irrelevant", "uncertain")],
        "",
    ]
    if by_task:
        lines.extend(counter_table(by_task, "Relevance by task", "Task"))
        lines.append("")
    if by_rank:
        lines.extend(
            counter_table(by_rank, "Relevance by lexical rank within change/task", "Lexical rank")
        )
        lines.append("")
    if shared_terms:
        lines.extend(
            [
                "### Most common shared lexical terms in the sample",
                "",
                "| Term | Candidate pairs |",
                "|---|---:|",
                *[f"| {term} | {count} |" for term, count in shared_terms.most_common(20)],
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation",
            "",
            "These labels are a single-model silver pass and have not been independently verified. The importer validates IDs, label structure, provenance and exact evidence, but cannot verify semantic relevance. Review every pair individually against its full announcement context before using label rates to tune retrieval. This is a descriptive audit of the stratified, lexical-retriever sample; it is not a probability estimate of precision, does not measure missed-pair recall, and does not establish patch causality. Unlabeled sampled rows are excluded from relevance counts.",
            "",
        ]
    )
    if outside:
        lines.append(
            "Response IDs outside the sampled audit rows: "
            + ", ".join(f"`{value}`" for value in outside)
        )
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", type=Path, required=True, help="Patch-scoped LLM job directory")
    parser.add_argument("--responses", type=Path, required=True, help="Response file or directory")
    parser.add_argument("--output", type=Path, help="Markdown destination; defaults inside the job")
    args = parser.parse_args(argv)
    output = args.output or args.job / "retrieval_audit_report.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_report(args.job, args.responses), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
