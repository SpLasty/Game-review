"""Model-independent Arrow batch loading with explicit task/split selection."""

import json

import pyarrow.dataset as ds


def latest_dataset(config):
    root = config.output("datasets_dir")
    pointer = root / "latest.json"
    if not pointer.exists():
        raise ValueError("No published dataset; run steam-insights pipeline first")
    relative = json.loads(pointer.read_text())["path"]
    directory = (root / relative).resolve()
    if (
        not directory.is_relative_to((root / "snapshots").resolve())
        or not (directory / "manifest.json").exists()
    ):
        raise ValueError("Invalid dataset pointer")
    return directory


def iter_model_batches(
    directory,
    *,
    kind="pairs",
    split=None,
    task=None,
    labeled=False,
    label_source="human",
    batch_size=512,
):
    table_names = {
        "reviews": "model_review_inputs",
        "changes": "model_change_inputs",
        "pairs": "model_pair_inputs",
    }
    if kind not in table_names or batch_size <= 0:
        raise ValueError("Invalid model kind or batch size")
    if labeled and kind != "pairs":
        raise ValueError("Supervised exports currently use review-change pairs")
    if label_source not in {"human", "llm"} or (label_source == "llm" and not labeled):
        raise ValueError("label_source must be human or llm; llm requires labeled=True")
    dataset = ds.dataset(
        directory
        / (
            (
                ("silver_pairs" if label_source == "llm" else "labeled_pairs")
                if labeled
                else table_names[kind]
            )
            + ".parquet"
        ),
        format="parquet",
    )
    predicate = None
    if split:
        if split not in {"train", "validation", "test"}:
            raise ValueError("Unknown split")
        predicate = ds.field("split") == split
    if task:
        if kind != "pairs" or task not in {
            "post_patch_feedback",
            "retrospective_complaint_resolution",
        }:
            raise ValueError("Unknown task or task used with unpaired data")
        rule = ds.field("task") == task
        predicate = rule if predicate is None else predicate & rule
    for batch in dataset.scanner(filter=predicate, batch_size=batch_size).to_batches():
        if batch.num_rows:
            yield batch
