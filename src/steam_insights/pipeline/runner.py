"""Run reusable data stages and publish a completed dataset snapshot."""

from steam_insights.data.io import inventory, write_json
from steam_insights.pipeline.settings import PipelineConfig
from steam_insights.pipeline.ingestion import load_observations
from steam_insights.pipeline.reviews import prepare_review_observations
from steam_insights.pipeline.storage import create_catalog, write_table


def run_pipeline(config: PipelineConfig, stage: str = "all") -> dict:
    config.work_dir.mkdir(parents=True, exist_ok=True)
    result = inventory(config.data)
    write_json(config.work_dir / "source_inventory.json", result)
    if stage == "inventory":
        return {"stage": stage, "output": str(config.work_dir / "source_inventory.json")}
    reviews = prepare_review_observations(load_observations(config, "reviews"), config)
    directory = config.work_dir / "reviews"
    for name in ("reviews", "review_revisions", "review_passages", "source_records", "quarantine", "duplicate_pairs"):
        write_table(directory, name, reviews[name], config.values["storage"])
    write_json(directory / "stage_report.json", reviews["stats"])
    create_catalog(directory)
    if stage != "reviews":
        raise ValueError("Announcement and export stages follow after the F1 review stage")
    return {"stage": stage, "output": str(directory), "stats": reviews["stats"]}
