"""Execute starter notebook cells and verify outputs against the real source snapshot.

This is a Python-cell smoke check, not a Jupyter browser/kernel integration test.
Run from the project root after installing the package.
"""

import json
import os
import warnings
from pathlib import Path

import pandas as pd

from steam_insights.config import load_config
from steam_insights.data.io import read_csv, sha256
from steam_insights.data.validation import boolean_values


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    os.environ.setdefault("MPLBACKEND", "Agg")
    config = load_config()
    original_hashes = {
        kind: sha256(config.source(kind)) for kind in ("reviews", "balanced", "announcements")
    }
    for name in ("01_data_exploration.ipynb", "02_preprocessing.ipynb"):
        notebook = json.loads((root / "notebooks" / name).read_text(encoding="utf-8"))
        namespace = {"__name__": "__main__", "display": lambda *_: None}
        for index, cell in enumerate(notebook["cells"]):
            if cell["cell_type"] != "code":
                continue
            assert cell["outputs"] == [] and cell["execution_count"] is None, (
                "Clear committed notebook outputs"
            )
            source = "".join(cell["source"])
            with warnings.catch_warnings():
                # The smoke check intentionally has no interactive display server.
                warnings.filterwarnings("ignore", message="FigureCanvasAgg is non-interactive.*")
                exec(compile(source, f"{name}:cell-{index}", "exec"), namespace)
        print(f"Executed Python cells: {name}")
    prepared = pd.read_parquet(config.interim_dir / "reviews.parquet")
    source = read_csv(config.source("reviews"))
    source["appid"] = source["appid"].astype("int64")
    keys = ["appid", "review_id"]
    expected = source.set_index(keys).sort_index()
    actual = prepared.set_index(keys).sort_index()
    pd.testing.assert_series_equal(
        actual["review_text"].astype("string"), expected["review_text"].astype("string")
    )
    pd.testing.assert_series_equal(actual["recommended"], boolean_values(expected["recommended"]))
    text_view = pd.read_parquet(config.interim_dir / "reviews_text.parquet")
    pd.testing.assert_frame_equal(
        text_view, prepared.loc[prepared["analysis_text_eligible"]].reset_index(drop=True)
    )
    notes = pd.read_parquet(config.interim_dir / "announcements.parquet")
    original_notes = read_csv(config.source("announcements"))
    original_notes["appid"] = original_notes["appid"].astype("int64")
    pd.testing.assert_series_equal(
        notes.set_index(["appid", "gid"])["text"].sort_index().astype("string"),
        original_notes.set_index(["appid", "gid"])["text"].sort_index().astype("string"),
    )
    for kind, digest in original_hashes.items():
        assert sha256(config.source(kind)) == digest, f"Source file changed: {kind}"
    print(
        f"Verified {len(prepared):,} reviews, {len(text_view):,} text-view rows and {len(notes):,} posts"
    )
    print("Original review/announcement text and votes preserved; source files unchanged.")


if __name__ == "__main__":
    main()
