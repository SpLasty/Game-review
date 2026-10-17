"""Run reusable data stages and publish a completed dataset snapshot."""

from steam_insights.data.io import inventory, write_json
from steam_insights.pipeline.settings import PipelineConfig


def run_pipeline(config: PipelineConfig, stage: str = "all") -> dict:
    config.work_dir.mkdir(parents=True, exist_ok=True)
    result = inventory(config.data)
    write_json(config.work_dir / "source_inventory.json", result)
    if stage != "inventory":
        raise ValueError("Only inventory is implemented in the F0 walking skeleton")
    return {"stage": stage, "output": str(config.work_dir / "source_inventory.json")}
