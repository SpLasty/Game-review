"""Import legacy CSVs, original collector archives, and new source observations."""

import json
from pathlib import Path

from steam_insights.data.io import read_csv, sha256
from steam_insights.pipeline.settings import PipelineConfig
from steam_insights.pipeline.storage import stable_id


def api_review_row(record: dict, appid: int, game: str) -> dict:
    author = record.get("author", {})

    def hours(key):
        value = author.get(key)
        return None if value is None else float(value) / 60

    return {
        "appid": str(appid),
        "game": game,
        "review_id": str(record.get("recommendationid", "")),
        "review_text": record.get("review", ""),
        "language": record.get("language", "unknown"),
        "timestamp_created": record.get("timestamp_created"),
        "timestamp_updated": record.get("timestamp_updated"),
        "recommended": record.get("voted_up"),
        "author_hash": author.get("author_hash"),
        "author_hash_namespace": record.get("author_hash_namespace", "legacy_collector"),
        "playtime_at_review_hours": hours("playtime_at_review"),
        "lifetime_playtime_hours": hours("playtime_forever"),
        "source_url": record.get("source_url", f"https://store.steampowered.com/app/{appid}/"),
        "observed_at": record.get("fetched_utc"),
        **{
            key: record.get(key)
            for key in (
                "steam_purchase",
                "received_for_free",
                "refunded",
                "primarily_steam_deck",
                "written_during_early_access",
            )
        },
    }


def api_news_row(record: dict, appid: int, game: str) -> dict:
    return {
        "appid": str(appid),
        "game": game,
        "gid": str(record.get("gid", "")),
        "title": record.get("title", ""),
        "timestamp": record.get("date"),
        "text": record.get("text", record.get("contents", "")),
        "contents": record.get("contents"),
        "source_url": record.get("url", ""),
        "feed": record.get("feedname", ""),
        "observed_at": record.get("fetched_utc"),
        "event_type": record.get("event_type"),
    }


def source_files(config: PipelineConfig) -> list[Path]:
    paths = [config.data.source(kind) for kind in ("reviews", "balanced", "announcements")]
    archive = config.input("raw_archive")
    paths.extend(archive.glob("*/reviews.jsonl"))
    paths.extend(archive.glob("*/news.json"))
    paths.extend(config.input("recovery_dir").glob("records/**/*.json"))
    for filename in ("announcement_recovery_report.json", "review_backfill_report.json"):
        report = config.input("recovery_dir") / filename
        if report.exists():
            paths.append(report)
    for name in ("annotations", "patch_verification"):
        if config.input(name).exists():
            paths.append(config.input(name))
    return sorted(set(paths))


def load_observations(config: PipelineConfig, dataset: str) -> list[dict]:
    frame = read_csv(config.data.source(dataset))
    required = (
        {
            "appid",
            "game",
            "review_id",
            "review_text",
            "language",
            "timestamp_created",
            "timestamp_updated",
            "recommended",
        }
        if dataset == "reviews"
        else {"appid", "game", "gid", "title", "text", "timestamp", "source_url"}
    )
    if missing := required - set(frame.columns):
        raise ValueError(f"{dataset}: required columns missing: {sorted(missing)}")
    observations = []

    def add(path, records, kind, offset=1):
        file_hash = sha256(path)
        try:
            display = path.relative_to(config.root).as_posix()
        except ValueError:
            display = str(path)
        for index, record in enumerate(records, offset):
            row = dict(record)
            row["_source"] = {
                "source_record_id": stable_id(dataset, file_hash, index, display),
                "dataset": dataset,
                "source_path": display,
                "source_sha256": file_hash,
                "source_row": index,
                "source_kind": kind,
                "source_url": str(row.get("source_url", "")),
            }
            observations.append(row)

    add(config.data.source(dataset), frame.to_dict("records"), "csv_export", 2)
    archive = config.input("raw_archive")
    if dataset == "reviews":
        for path in sorted(archive.glob("*/reviews.jsonl")):
            raw = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
            add(
                path, [api_review_row(r, int(r["appid"]), r["game"]) for r in raw], "collector_json"
            )
    else:
        for path in sorted(archive.glob("*/news.json")):
            raw = json.loads(path.read_text())
            add(path, [api_news_row(r, int(r["appid"]), r["game"]) for r in raw], "collector_json")
    for path in sorted(config.input("recovery_dir").glob(f"records/{dataset}/**/*.json")):
        envelope = json.loads(path.read_text())
        record = envelope["record"]
        record["observed_at"] = envelope["fetched_utc"]
        add(path, [record], "public_api_snapshot")
    return observations
