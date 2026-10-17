"""Configuration shared by independent preprocessing stages."""

import tomllib
from dataclasses import dataclass
from pathlib import Path

from steam_insights.config import DataConfig, load_config


@dataclass(frozen=True)
class PipelineConfig:
    path: Path
    root: Path
    data: DataConfig
    values: dict

    def input(self, name: str) -> Path:
        return (self.root / self.values["inputs"][name]).resolve()

    def output(self, name: str) -> Path:
        return (self.root / self.values["outputs"][name]).resolve()

    @property
    def work_dir(self) -> Path:
        return self.output("datasets_dir") / "work"


def load_pipeline_config(path: str | Path = "configs/pipeline.toml") -> PipelineConfig:
    path = Path(path).resolve()
    with path.open("rb") as handle:
        values = tomllib.load(handle)
    root = (path.parent / values["project"]["root"]).resolve()
    config = PipelineConfig(path, root, load_config(root / values["inputs"]["data_config"]), values)
    inputs = [config.data.source_dir, config.input("raw_archive"), config.input("recovery_dir")]
    outputs = [config.output("datasets_dir"), config.output("reports_dir")]
    for output in outputs:
        if any(output.is_relative_to(source) or source.is_relative_to(output) for source in inputs):
            raise ValueError("Pipeline outputs must be separate from source inputs")
    if outputs[0].is_relative_to(outputs[1]) or outputs[1].is_relative_to(outputs[0]):
        raise ValueError("Dataset and quality outputs must be separate")
    for section, names in {
        "reviews": ["minimum_words", "passage_max_chars", "near_duplicate_bucket_limit"],
        "windows": [
            "days_before",
            "days_after",
            "minimum_reviews",
            "minimum_review_dates",
            "stronger_minimum_reviews",
        ],
        "candidates": [
            "feedback_days",
            "resolution_days",
            "minimum_shared_terms",
            "max_per_review_per_task",
        ],
        "storage": ["row_group_size"],
        "collection": [
            "max_requests",
            "news_pages_per_game",
            "review_pages_per_window",
            "max_patch_windows",
            "timeout_seconds",
        ],
    }.items():
        for name in names:
            value = values[section][name]
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{section}.{name} must be a positive integer")
    for key in ("validation_games", "test_games", "seed"):
        if not isinstance(values["splits"][key], int) or values["splits"][key] < 0:
            raise ValueError(f"splits.{key} must be a nonnegative integer")
    return config
