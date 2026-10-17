"""One resumable operator command for collection through validated model inputs."""

import json

from steam_insights.data.io import write_json
from steam_insights.pipeline.checks import validate_snapshot
from steam_insights.pipeline.llm_annotations import export_llm_job
from steam_insights.pipeline.loader import latest_dataset
from steam_insights.pipeline.runner import run_pipeline
from steam_insights.pipeline.sources import PublicSteamClient, backfill_reviews, recover_sources
from steam_insights.pipeline.storage import utc_now


def prepare_data(config, *, online=False, refresh=False, sample_size=100):
    if sample_size <= 0:
        raise ValueError("sample_size must be positive")
    state = {"started_utc": utc_now(), "online": online, "status": "running", "steps": []}
    journal = config.output("datasets_dir") / "orchestration.json"

    def step(name, operation):
        item = {"step": name, "started_utc": utc_now(), "status": "running"}
        state["steps"].append(item)
        write_json(journal, state)
        print(f"[{name}] running", flush=True)
        try:
            result = operation()
        except Exception as exc:
            item.update(status="failed", error=f"{type(exc).__name__}: {exc}")
            state["status"] = "failed_resumable"
            write_json(journal, state)
            raise
        item.update(status="completed", finished_utc=utc_now(), result=result)
        write_json(journal, state)
        return result

    if online:
        client = PublicSteamClient(config, refresh=refresh)
        step(
            "recover_announcements", lambda: recover_sources(config, refresh=refresh, client=client)
        )
        step("prepare_reviews_for_collection_plan", lambda: run_pipeline(config, "reviews"))
        step(
            "prepare_announcements_for_collection_plan",
            lambda: run_pipeline(config, "announcements"),
        )
        step(
            "backfill_review_windows",
            lambda: backfill_reviews(config, refresh=refresh, client=client),
        )
    build = step("build_model_dataset", lambda: run_pipeline(config))
    directory = latest_dataset(config)
    checked = step(
        "validate_published_dataset",
        lambda: {
            key: value for key, value in validate_snapshot(directory).items() if key != "results"
        },
    )

    def annotation_handoff():
        output = config.root / "data/annotations/llm_jobs" / directory.name
        if (output / "manifest.json").exists():
            job = json.loads((output / "manifest.json").read_text())
            if job["dataset_id"] != directory.name:
                raise ValueError("LLM handoff job disagrees with the published dataset")
            return {"output": str(output), "status": "existing_job_preserved"}
        return export_llm_job(directory, output, sample_size=sample_size)

    queue = step("export_development_llm_job", annotation_handoff)
    from steam_insights.data.quality_report import generate_quality_report

    step(
        "refresh_source_quality_report",
        lambda: {
            key: str(value) if hasattr(value, "as_posix") else value
            for key, value in generate_quality_report(config.data).items()
        },
    )
    state.update(
        status="processing_complete",
        finished_utc=utc_now(),
        dataset_id=build["dataset_id"],
        validation_checks=checked["checks"],
        llm_annotation_job=queue["output"],
        next="Give batch Markdown files to an LLM, import responses, then rerun prepare-data. Human annotation is optional.",
    )
    write_json(journal, state)
    return {
        "status": state["status"],
        "dataset_id": build["dataset_id"],
        "output": str(directory),
        "report": str(config.output("reports_dir") / "report.md"),
        "llm_annotation_job": queue["output"],
        "journal": str(journal),
        "validation_checks": checked["checks"],
        "note": "Processing completion does not imply complete collection or labeled training data. LLM response import requires no human annotation.",
    }
