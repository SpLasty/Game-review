"""Small operator-facing actions over a published dataset."""

import json
import os

from steam_insights.pipeline.annotations import (
    export_annotation_queue,
    read_annotation_file,
    validate_annotations,
)
from steam_insights.pipeline.checks import validate_snapshot
from steam_insights.pipeline.loader import latest_dataset
from steam_insights.pipeline.storage import read_table


def annotation_or_validation_command(config, args):
    directory = latest_dataset(config)
    if args.command == "pipeline-validate":
        result = validate_snapshot(directory)
        return {"dataset": directory.name, "passed": result["passed"], "checks": result["checks"]}
    if args.command == "annotations-export":
        if args.sample_size <= 0:
            raise ValueError("sample-size must be positive")
        splits = (
            ("train", "validation")
            if args.split == "development"
            else ("train", "validation", "test")
            if args.split == "all"
            else (args.split,)
        )
        output = args.output or config.root / "data" / "annotations" / "queues" / (
            directory.name + ".jsonl"
        )
        if output.resolve() == config.input("annotations"):
            raise ValueError(
                "Annotation queue output must not overwrite the accepted annotation file"
            )
        return export_annotation_queue(
            directory, output, sample_size=args.sample_size, splits=splits
        )
    if not args.input or not args.input.is_file():
        raise ValueError("annotations-import requires --input path/to/completed.jsonl")
    from steam_insights.pipeline.runner import build_lock

    with build_lock(config):
        path = config.input("annotations")
        existing = read_annotation_file(path)
        rows = validate_annotations(
            existing + read_annotation_file(args.input),
            read_table(directory, "candidates"),
            read_table(directory, "reviews"),
            read_table(directory, "announcements"),
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(
                    json.dumps(row, ensure_ascii=False, sort_keys=True, default=str) + "\n"
                )
        os.replace(temporary, path)
    return {
        "output": str(path),
        "validated_annotation_records": len(rows),
        "next": "Run steam-insights pipeline to publish a new dataset incorporating these annotations.",
    }
