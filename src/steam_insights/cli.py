"""Command-line entry points for the initial offline data workflow."""

import argparse
import json
import sys
from pathlib import Path

from steam_insights.config import load_config
from steam_insights.data.io import inventory, write_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "inventory",
            "profile",
            "preprocess",
            "quality",
            "pipeline",
            "prepare-data",
            "recover-sources",
            "backfill-reviews",
            "pipeline-validate",
            "annotations-export",
            "annotations-import",
            "llm-annotations-export",
            "llm-annotations-import",
        ],
    )
    parser.add_argument("--config", type=Path)
    parser.add_argument(
        "--stage", choices=["inventory", "reviews", "announcements", "all"], default="all"
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Fetch new public observations instead of cached responses",
    )
    parser.add_argument(
        "--online",
        action="store_true",
        help="Recover public sources and backfill reviews before processing",
    )
    parser.add_argument(
        "--max-requests", type=int, help="Override the bounded online request budget"
    )
    parser.add_argument("--input", type=Path, help="Completed annotation JSONL/JSON")
    parser.add_argument("--output", type=Path, help="Queue file or LLM job directory")
    parser.add_argument("--job", type=Path, help="Frozen LLM export job directory")
    parser.add_argument("--model", help="Model/version used for LLM labeling (operator supplied)")
    parser.add_argument("--run-id", help="Distinct LLM labeling pass identifier")
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--max-batch-chars", type=int, default=100_000)
    parser.add_argument("--sample-size", type=int, default=100)
    parser.add_argument(
        "--split",
        choices=["development", "train", "validation", "test", "all"],
        default="development",
    )
    args = parser.parse_args(argv)
    try:
        if args.command in {
            "pipeline",
            "prepare-data",
            "recover-sources",
            "backfill-reviews",
            "pipeline-validate",
            "annotations-export",
            "annotations-import",
            "llm-annotations-export",
            "llm-annotations-import",
        }:
            from steam_insights.pipeline.runner import run_pipeline
            from steam_insights.pipeline.settings import load_pipeline_config

            pipeline_config = load_pipeline_config(args.config or "configs/pipeline.toml")
            if args.max_requests is not None:
                if args.max_requests <= 0:
                    raise ValueError("max-requests must be positive")
                pipeline_config.values["collection"]["max_requests"] = args.max_requests
            if args.command == "prepare-data":
                from steam_insights.pipeline.orchestration import prepare_data

                result = prepare_data(
                    pipeline_config,
                    online=args.online,
                    refresh=args.refresh,
                    sample_size=args.sample_size,
                )
            elif args.command == "pipeline":
                result = run_pipeline(pipeline_config, args.stage)
            elif args.command in {"recover-sources", "backfill-reviews"}:
                from steam_insights.pipeline.sources import backfill_reviews, recover_sources

                operation = (
                    recover_sources if args.command == "recover-sources" else backfill_reviews
                )
                result = operation(pipeline_config, refresh=args.refresh)
            else:
                from steam_insights.pipeline.commands import annotation_or_validation_command

                result = annotation_or_validation_command(pipeline_config, args)
            print(json.dumps(result, indent=2, default=str))
            return 0
        config = load_config(args.config or "configs/data.toml")
        if args.command == "inventory":
            result = inventory(config)
            output = config.reports_dir / "source_inventory.json"
            write_json(output, result)
            print(f"Source inventory: {output}")
            for name, source in result["sources"].items():
                print(f"  {name}: {source['rows']:,} rows")
        elif args.command == "profile":
            from steam_insights.data.exploration import profile

            result = profile(config)
            print(f"Exploration report: {config.reports_dir / 'README.md'}")
            return 0 if all(item["valid"] for item in result["validation"]) else 1
        elif args.command == "quality":
            from steam_insights.data.quality_report import generate_quality_report

            result = generate_quality_report(config)
            print(f"Data-quality report: {result['report']}")
            print(
                f"Patch-window table: {result['patch_windows']} ({result['patch_window_count']:,} rows)"
            )
            validation = json.loads(
                (config.reports_dir / "profile.json").read_text(encoding="utf-8")
            )["validation"]
            return 0 if all(item["valid"] for item in validation) else 1
        else:
            from steam_insights.data.pipeline import preprocess

            result = preprocess(config)
            print(f"Prepared data: {config.interim_dir}")
            for name, count in result["outputs"].items():
                print(f"  {name}: {count:,} rows")
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"Data workflow failed: {exc}", file=sys.stderr)
        return 1
