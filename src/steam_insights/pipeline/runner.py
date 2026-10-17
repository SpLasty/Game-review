"""Orchestrate independent stages and atomically publish immutable dataset versions."""

import json
import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path

from steam_insights.data.io import inventory, sha256, write_json
from steam_insights.pipeline import PIPELINE_VERSION
from steam_insights.pipeline.annotations import (
    labeled_exports,
    read_annotation_file,
    validate_annotations,
)
from steam_insights.pipeline.announcements import prepare_announcement_observations
from steam_insights.pipeline.checks import validate_snapshot
from steam_insights.pipeline.datasets import (
    assign_splits,
    build_candidates,
    build_windows,
    model_exports,
)
from steam_insights.pipeline.ingestion import load_observations, source_files
from steam_insights.pipeline.reporting import write_readiness_report
from steam_insights.pipeline.reviews import prepare_review_observations
from steam_insights.pipeline.settings import PipelineConfig
from steam_insights.pipeline.storage import SCHEMAS, create_catalog, stable_id, utc_now, write_table

REVIEW_TABLES = (
    "reviews",
    "review_revisions",
    "review_passages",
    "source_records",
    "quarantine",
    "duplicate_pairs",
)
ANNOUNCEMENT_TABLES = (
    "announcements",
    "announcement_revisions",
    "announcement_blocks",
    "announcement_links",
    "changes",
    "patches",
    "verification_evidence",
    "source_records",
    "quarantine",
)


@contextmanager
def build_lock(config):
    root = config.output("datasets_dir")
    root.mkdir(parents=True, exist_ok=True)
    path = root / ".build.lock"
    try:
        path.mkdir()
    except FileExistsError as exc:
        raise ValueError(
            f"Pipeline writer already running, or interrupted lock needs inspection: {path}"
        ) from exc
    try:
        write_json(path / "owner.json", {"pid": os.getpid(), "started_utc": utc_now()})
        yield
    finally:
        shutil.rmtree(path)


def fingerprint(config):
    def info(path):
        try:
            name = path.relative_to(config.root).as_posix()
        except ValueError:
            name = str(path)
        return {"path": name, "sha256": sha256(path), "bytes": path.stat().st_size}

    inputs = [info(path) for path in source_files(config)]
    implementation = [
        info(path) for path in sorted((config.root / "src" / "steam_insights").rglob("*.py"))
    ]
    for path in (config.path, config.input("data_config"), config.root / "uv.lock"):
        if path.exists():
            implementation.append(info(path))
    value = {
        "inputs": inputs,
        "implementation": implementation,
        "configuration": config.values,
        "pipeline_version": PIPELINE_VERSION,
    }
    return stable_id("steam_model_dataset_v1", value), value


def _stage(config, name, result, tables):
    directory = config.work_dir / name
    for table in tables:
        write_table(directory, table, result[table], config.values["storage"])
    write_json(directory / "stage_report.json", result["stats"])
    create_catalog(directory)
    return {"stage": name, "output": str(directory), "stats": result["stats"]}


def _publish_pointer(config, snapshot, dataset_id):
    root = config.output("datasets_dir")
    pointer = root / "latest.tmp.json"
    write_json(pointer, {"dataset_id": dataset_id, "path": snapshot.relative_to(root).as_posix()})
    os.replace(pointer, root / "latest.json")
    report_root = config.output("reports_dir")
    report_root.mkdir(parents=True, exist_ok=True)
    for name in (
        "report.md",
        "readiness.json",
        "game_quality_summary.csv",
        "patch_window_quality.csv",
        "validation.json",
    ):
        shutil.copy2(snapshot / name, report_root / name)


def run_pipeline(config: PipelineConfig, stage: str = "all") -> dict:
    if stage not in {"inventory", "reviews", "announcements", "all"}:
        raise ValueError("Unknown pipeline stage")
    with build_lock(config):
        config.work_dir.mkdir(parents=True, exist_ok=True)
        source_inventory = inventory(config.data)
        write_json(config.work_dir / "source_inventory.json", source_inventory)
        if stage == "inventory":
            return {"stage": stage, "output": str(config.work_dir / "source_inventory.json")}
        if stage == "reviews":
            result = prepare_review_observations(load_observations(config, "reviews"), config)
            return _stage(config, "reviews", result, REVIEW_TABLES)
        if stage == "announcements":
            result = prepare_announcement_observations(
                load_observations(config, "announcements"), config
            )
            return _stage(config, "announcements", result, ANNOUNCEMENT_TABLES)

        dataset_id, provenance = fingerprint(config)
        snapshots = config.output("datasets_dir") / "snapshots"
        snapshot = snapshots / dataset_id
        if (snapshot / "manifest.json").exists():
            checked = validate_snapshot(snapshot)
            create_catalog(snapshot)
            _publish_pointer(config, snapshot, dataset_id)
            return {
                "dataset_id": dataset_id,
                "output": str(snapshot),
                "reused": True,
                "validation_checks": checked["checks"],
            }
        review_result = prepare_review_observations(load_observations(config, "reviews"), config)
        doc_result = prepare_announcement_observations(
            load_observations(config, "announcements"), config
        )
        games, split_stats = assign_splits(review_result, doc_result, config)
        collection_path = config.input("recovery_dir") / "review_backfill_report.json"
        collection = json.loads(collection_path.read_text()) if collection_path.exists() else {}
        windows = build_windows(review_result["reviews"], doc_result["patches"], config, collection)
        candidates = build_candidates(
            review_result["reviews"],
            doc_result["announcements"],
            doc_result["changes"],
            doc_result["patches"],
            config,
        )
        exports = model_exports(review_result, doc_result["changes"], candidates)
        annotations = validate_annotations(
            read_annotation_file(config.input("annotations")),
            candidates,
            review_result["reviews"],
            doc_result["announcements"],
        )
        labeled, label_stats = labeled_exports(exports["model_pair_inputs"], annotations)
        tables = {
            **{name: review_result[name] for name in REVIEW_TABLES},
            **{name: doc_result[name] for name in ANNOUNCEMENT_TABLES},
            **exports,
            "games": games,
            "patch_windows": windows,
            "candidates": candidates,
            "annotations": annotations,
            "labeled_pairs": labeled,
            "source_records": review_result["source_records"] + doc_result["source_records"],
            "quarantine": review_result["quarantine"] + doc_result["quarantine"],
        }
        snapshots.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".building-", dir=snapshots))
        try:
            metadata = {}
            for name in SCHEMAS:
                metadata[name] = write_table(staging, name, tables[name], config.values["storage"])
                metadata[name]["sha256"] = sha256(staging / f"{name}.parquet")
            try:
                commit = subprocess.check_output(
                    ["git", "rev-parse", "HEAD"],
                    cwd=config.root,
                    text=True,
                    stderr=subprocess.DEVNULL,
                ).strip()
            except (OSError, subprocess.CalledProcessError):
                commit = None
            manifest = {
                "schema_version": 1,
                "pipeline_version": PIPELINE_VERSION,
                "dataset_id": dataset_id,
                "created_utc": utc_now(),
                "git_commit": commit,
                "configuration": config.values,
                "provenance": provenance,
                "source_inventory": source_inventory,
                "stages": {
                    "reviews": review_result["stats"],
                    "announcements": doc_result["stats"],
                    "splits": split_stats,
                    "annotations": label_stats,
                },
                "tables": metadata,
                "readiness": {
                    **label_stats,
                    **split_stats,
                    "inference_inputs_ready": bool(
                        exports["model_review_inputs"] and exports["model_change_inputs"]
                    ),
                    "pair_inference_inputs_ready": bool(candidates),
                    "language_warnings": review_result["stats"]["language_warnings"],
                    "flattened_or_plain_posts": sum(
                        not d["structure_available"] for d in doc_result["announcements"]
                    ),
                    "unknown_release_times": sum(
                        p["release_utc"] is None for p in doc_result["patches"]
                    ),
                },
            }
            write_json(staging / "manifest.json", manifest)
            validation = validate_snapshot(staging)
            write_json(staging / "validation.json", validation)
            write_readiness_report(
                staging,
                manifest,
                review_result["reviews"],
                doc_result["announcements"],
                games,
                windows,
            )
            if fingerprint(config)[0] != dataset_id:
                raise ValueError(
                    "Inputs/config/code changed during build; refused mixed-snapshot publication"
                )
            os.rename(staging, snapshot)
            create_catalog(snapshot)
            _publish_pointer(config, snapshot, dataset_id)
            _stage(config, "reviews", review_result, REVIEW_TABLES)
            _stage(config, "announcements", doc_result, ANNOUNCEMENT_TABLES)
            result = {
                "dataset_id": dataset_id,
                "output": str(snapshot),
                "reused": False,
                "validation_checks": validation["checks"],
                "rows": {name: item["rows"] for name, item in metadata.items()},
                "readiness": manifest["readiness"],
            }
            write_json(config.output("datasets_dir") / "last_run.json", result)
            return result
        finally:
            if staging.exists():
                shutil.rmtree(staging)
