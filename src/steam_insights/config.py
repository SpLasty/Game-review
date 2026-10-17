"""Explicit filesystem and data-policy configuration for offline commands."""

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataConfig:
    root: Path
    source_dir: Path
    interim_dir: Path
    reports_dir: Path
    reviews_file: str
    balanced_file: str
    announcements_file: str
    minimum_words: int = 10
    language: str = "english"
    quality_dir: Path | None = None

    def source(self, kind: str) -> Path:
        names = {
            "reviews": self.reviews_file,
            "balanced": self.balanced_file,
            "announcements": self.announcements_file,
        }
        return self.source_dir / names[kind]


def load_config(path: str | Path = "configs/data.toml") -> DataConfig:
    path = Path(path).resolve()
    with path.open("rb") as handle:
        values = tomllib.load(handle)
    root = (path.parent / values["project"]["root"]).resolve()
    paths = {key: (root / value).resolve() for key, value in values["paths"].items()}
    output_paths = [paths["interim_dir"], paths["reports_dir"]]
    quality_dir = paths.get("quality_dir", root / "reports" / "data_quality")
    output_paths.append(quality_dir)
    for output in output_paths:
        source = paths["source_dir"]
        if output.is_relative_to(source) or source.is_relative_to(output):
            raise ValueError("Output directories must be separate from the source directory")
    for index, output in enumerate(output_paths):
        if any(
            output.is_relative_to(other) or other.is_relative_to(output)
            for other in output_paths[index + 1 :]
        ):
            raise ValueError(
                "Interim, exploration, and data-quality output directories must be separate"
            )
    policy = values.get("preprocessing", {})
    minimum = policy.get("minimum_words", 10)
    if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 1:
        raise ValueError("minimum_words must be a positive integer")
    for name in values["files"].values():
        if not isinstance(name, str) or Path(name).name != name or not name.endswith(".csv"):
            raise ValueError("Input filenames must be plain CSV filenames")
    return DataConfig(
        root=root,
        **paths,
        reviews_file=values["files"]["reviews"],
        balanced_file=values["files"]["balanced"],
        announcements_file=values["files"]["announcements"],
        minimum_words=minimum,
        language=policy.get("language", "english"),
    )
