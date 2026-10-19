"""Command-line entry point for the versioned Steam relevance workflow."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Sequence

import pyarrow as pa

from steam_patch_relevance import __version__
from steam_patch_relevance.api import RequestBudget, SteamAPI, SteamAPIError
from steam_patch_relevance.collect import materialize_from_checkpoints, run_collection
from steam_patch_relevance.config import load_config
from steam_patch_relevance.stage2.pipeline import run_stage2
from steam_patch_relevance.stage3.pipeline import (
    DEFAULT_DENSE_MODEL,
    DEFAULT_DENSE_REVISION,
    run_stage3,
)
from steam_patch_relevance.stage3.pipeline import (
    DEFAULT_OUTPUT_ROOT as DEFAULT_STAGE3_OUTPUT_ROOT,
)
from steam_patch_relevance.stage3.pipeline import (
    DEFAULT_REPORT_ROOT as DEFAULT_STAGE3_REPORT_ROOT,
)
from steam_patch_relevance.stage3.pipeline import (
    DEFAULT_SOURCE_DATASET as DEFAULT_STAGE2_DATASET,
)
from steam_patch_relevance.stage4.pipeline import (
    DEFAULT_OUTPUT_ROOT as DEFAULT_STAGE4_OUTPUT_ROOT,
)
from steam_patch_relevance.stage4.pipeline import (
    DEFAULT_REPORT_ROOT as DEFAULT_STAGE4_REPORT_ROOT,
)
from steam_patch_relevance.stage4.pipeline import (
    DEFAULT_STAGE3_DATASET as DEFAULT_STAGE3_DATASET,
)
from steam_patch_relevance.stage4.pipeline import (
    export_annotation_pilot,
    export_full_list_review_audit,
    import_annotation_responses,
)
from steam_patch_relevance.storage import LocalStore, write_json

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "relevance_v1.toml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="steam-relevance",
        description="Collect and inspect raw Steam source data for relevance_v1.",
    )
    parser.add_argument("--version", action="version", version=f"steam-relevance {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    collect = commands.add_parser("collect", help="collect news and bounded patch review windows")
    collect.add_argument(
        "--online", action="store_true", help="required acknowledgement for live requests"
    )
    collect.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    collect.add_argument(
        "--max-requests", type=int, help="override the configured HTTP attempt budget"
    )
    collect.add_argument("--refresh", action="store_true", help="re-fetch completed checkpoints")

    materialize = commands.add_parser(
        "materialize",
        help="rebuild Parquet tables and coverage reports offline from raw checkpoints",
    )
    materialize.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    materialize.add_argument(
        "--run-id", help="collection run to materialize; defaults to newest run"
    )

    inspect = commands.add_parser(
        "inspect", help="inspect the latest local Parquet coverage with DuckDB"
    )
    inspect.add_argument(
        "--root", type=Path, default=REPO_ROOT / "data" / "relevance_v1" / "normalized"
    )
    inspect.add_argument(
        "--reports", type=Path, default=REPO_ROOT / "reports" / "relevance_v1" / "stage1"
    )

    catalog = commands.add_parser(
        "catalog", help="page through the authenticated Steam Store app catalog"
    )
    catalog.add_argument("--max-pages", type=int, default=1)
    catalog.add_argument("--max-results", type=int, default=1000)
    catalog.add_argument("--root", type=Path, default=REPO_ROOT / "data" / "relevance_v1")
    catalog.add_argument(
        "--online", action="store_true", help="required acknowledgement for live requests"
    )

    stage2 = commands.add_parser(
        "stage2", help="build atomic patch-change, review-claim, and temporal datasets offline"
    )
    stage2_commands = stage2.add_subparsers(dest="stage2_command", required=True)
    extract = stage2_commands.add_parser(
        "extract", help="classify announcements and extract versioned Stage 2 datasets"
    )
    extract.add_argument("--source-run", help="Stage 1 normalized run ID; defaults to latest")
    extract.add_argument("--review-batch-size", type=int, default=2048)
    extract.add_argument(
        "--limit-reviews",
        type=int,
        help="bounded smoke run only; output is marked partial and is not a complete dataset",
    )
    extract.add_argument("--sample-per-stratum", type=int, default=2)

    stage3 = commands.add_parser(
        "stage3", help="rank review claims for patch changes using hybrid retrieval"
    )
    stage3_commands = stage3.add_subparsers(dest="stage3_command", required=True)
    retrieve = stage3_commands.add_parser(
        "retrieve", help="build candidate pairs and an independent full-list audit sample"
    )
    retrieve.add_argument("--source-dataset", default=DEFAULT_STAGE2_DATASET)
    retrieve.add_argument("--budgets", type=int, nargs="+", default=[10, 25, 50, 100])
    retrieve.add_argument("--before-days", type=int, default=14)
    retrieve.add_argument("--after-days", type=int, default=14)
    retrieve.add_argument("--rrf-k", type=int, default=60)
    retrieve.add_argument(
        "--no-dense",
        action="store_true",
        help="run lexical/entity signals only for a bounded smoke test",
    )
    retrieve.add_argument("--dense-model", default=DEFAULT_DENSE_MODEL)
    retrieve.add_argument("--dense-revision", default=DEFAULT_DENSE_REVISION)
    retrieve.add_argument("--dense-batch-size", type=int, default=64)
    retrieve.add_argument("--audit-per-segment", type=int, default=5)
    retrieve.add_argument("--audit-seed", default="stage3-full-list-audit-v1")
    retrieve.add_argument(
        "--patch-id", action="append", help="limit retrieval to this Stage 2 patch ID; repeatable"
    )
    retrieve.add_argument(
        "--game-id",
        action="append",
        type=int,
        help="limit retrieval to this Steam app ID; repeatable",
    )
    retrieve.add_argument("--output-root", type=Path, default=DEFAULT_STAGE3_OUTPUT_ROOT)
    retrieve.add_argument("--report-root", type=Path, default=DEFAULT_STAGE3_REPORT_ROOT)

    stage4 = commands.add_parser(
        "stage4", help="export, validate, and assess patch/review silver annotation jobs"
    )
    stage4_commands = stage4.add_subparsers(dest="stage4_command", required=True)
    export = stage4_commands.add_parser(
        "export", help="create a bounded provider-neutral candidate and full-list audit batch"
    )
    export.add_argument("--source-dataset", default=DEFAULT_STAGE3_DATASET)
    export.add_argument("--candidate-pairs", type=int, default=24)
    export.add_argument("--audit-reviews", type=int, default=6)
    export.add_argument("--seed", default="stage4-pilot-v1")
    export.add_argument("--output-root", type=Path, default=DEFAULT_STAGE4_OUTPUT_ROOT)
    export.add_argument("--report-root", type=Path, default=DEFAULT_STAGE4_REPORT_ROOT)

    audit_export = stage4_commands.add_parser(
        "audit-export",
        help="sample reviews independently from a Stage 2 patch window and include every change",
    )
    audit_export.add_argument("--source-dataset", default="rv2-d52a3f9f1a3de2fe80aa098f")
    audit_export.add_argument("--patch-id", required=True)
    audit_export.add_argument(
        "--window-segment", choices=("after_0_7d", "after_8_14d"), default="after_0_7d"
    )
    audit_export.add_argument("--reviews", type=int, default=300)
    audit_export.add_argument("--seed", default="stage4-full-list-audit-300-v1")
    audit_export.add_argument(
        "--output-root", type=Path, default=DEFAULT_STAGE4_OUTPUT_ROOT / "independent_audit"
    )
    audit_export.add_argument(
        "--report-root", type=Path, default=DEFAULT_STAGE4_REPORT_ROOT / "independent_audit"
    )

    stage4_import = stage4_commands.add_parser(
        "import", help="validate JSONL responses and build silver labels and readiness outputs"
    )
    stage4_import.add_argument("--run-id", required=True)
    stage4_import.add_argument("--responses", type=Path, required=True)
    stage4_import.add_argument("--output-root", type=Path, default=DEFAULT_STAGE4_OUTPUT_ROOT)
    stage4_import.add_argument("--report-root", type=Path, default=DEFAULT_STAGE4_REPORT_ROOT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "collect":
            if not args.online:
                parser.error("collect requires --online because it contacts Steam")
            config = load_config(args.config, max_requests=args.max_requests)
            result = run_collection(config, repo_root=REPO_ROOT, refresh=args.refresh)
            return 0 if result.get("status") == "complete" else 2
        if args.command == "inspect":
            return _inspect(args.root, args.reports)
        if args.command == "materialize":
            config = load_config(args.config)
            materialize_from_checkpoints(config, repo_root=REPO_ROOT, run_id=args.run_id)
            return 0
        if args.command == "catalog":
            if not args.online:
                parser.error("catalog requires --online because it contacts Steam")
            return _catalog(args)
        if args.command == "stage2" and args.stage2_command == "extract":
            if args.review_batch_size < 1 or args.sample_per_stratum < 1:
                raise ValueError("review-batch-size and sample-per-stratum must be positive")
            if args.limit_reviews is not None and args.limit_reviews < 1:
                raise ValueError("limit-reviews must be positive when supplied")
            result = run_stage2(
                repo_root=REPO_ROOT,
                source_run=args.source_run,
                review_batch_size=args.review_batch_size,
                limit_reviews=args.limit_reviews,
                sample_per_stratum=args.sample_per_stratum,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
            return 0
        if args.command == "stage3" and args.stage3_command == "retrieve":
            if not args.budgets or any(budget < 1 for budget in args.budgets):
                raise ValueError("budgets must be positive integers")
            if args.before_days < 0 or args.after_days < 0:
                raise ValueError("temporal windows cannot be negative")
            result = run_stage3(
                repo_root=REPO_ROOT,
                source_dataset=args.source_dataset,
                output_root=args.output_root,
                report_root=args.report_root,
                budgets=args.budgets,
                before_days=args.before_days,
                after_days=args.after_days,
                rrf_k=args.rrf_k,
                dense=not args.no_dense,
                dense_model=args.dense_model,
                dense_revision=args.dense_revision,
                dense_batch_size=args.dense_batch_size,
                audit_per_segment=args.audit_per_segment,
                audit_seed=args.audit_seed,
                patch_ids=args.patch_id,
                game_ids=args.game_id,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
            return 0
        if args.command == "stage4" and args.stage4_command == "export":
            result = export_annotation_pilot(
                repo_root=REPO_ROOT,
                source_dataset=args.source_dataset,
                candidate_pairs=args.candidate_pairs,
                audit_reviews=args.audit_reviews,
                seed=args.seed,
                output_root=args.output_root,
                report_root=args.report_root,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
            return 0
        if args.command == "stage4" and args.stage4_command == "audit-export":
            result = export_full_list_review_audit(
                repo_root=REPO_ROOT,
                source_dataset=args.source_dataset,
                patch_id=args.patch_id,
                window_segment=args.window_segment,
                review_count=args.reviews,
                seed=args.seed,
                output_root=args.output_root,
                report_root=args.report_root,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
            return 0
        if args.command == "stage4" and args.stage4_command == "import":
            result = import_annotation_responses(
                repo_root=REPO_ROOT,
                run_id=args.run_id,
                responses_path=args.responses,
                output_root=args.output_root,
                report_root=args.report_root,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
            return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"steam-relevance: {exc}", file=sys.stderr)
        return 1
    return 1


def _inspect(normalized_root: Path, report_root: Path) -> int:
    try:
        import duckdb
    except ImportError as exc:
        raise RuntimeError("DuckDB is required for inspect") from exc
    runs = (
        sorted(
            (
                path
                for path in normalized_root.iterdir()
                if path.is_dir() and _is_collection_run_name(path.name)
            ),
            key=lambda path: path.name,
            reverse=True,
        )
        if normalized_root.exists()
        else []
    )
    if not runs:
        raise FileNotFoundError(f"No normalized collection runs under {normalized_root}")
    latest = runs[0]
    db = duckdb.connect(database=":memory:")
    tables = [
        "games",
        "announcements",
        "patch_candidates",
        "review_revisions",
        "review_window_memberships",
        "review_windows",
    ]
    counts: dict[str, int] = {}
    for table in tables:
        path = latest / f"{table}.parquet"
        if path.exists():
            counts[table] = db.execute(
                "SELECT count(*) FROM read_parquet(?)", [str(path)]
            ).fetchone()[0]
    coverage = report_root / "latest" / "game_coverage.csv"
    games = []
    if coverage.exists():
        games = (
            db.execute("SELECT * FROM read_csv_auto(?)", [str(coverage)])
            .fetchdf()
            .to_dict("records")
        )
    print(
        json.dumps(
            {
                "latest_run": latest.name,
                "normalized_path": str(latest),
                "row_counts": counts,
                "game_coverage": games,
            },
            indent=2,
            default=str,
        )
    )
    db.close()
    return 0


def _catalog(args: argparse.Namespace) -> int:
    api_key = os.environ.get("STEAM_WEB_API_KEY")
    if not api_key:
        raise ValueError("Set STEAM_WEB_API_KEY in the environment; the key is never saved to disk")
    if not 1 <= args.max_results <= 50_000 or args.max_pages < 1:
        raise ValueError("max-results must be 1..50000 and max-pages must be positive")
    run_id = f"rv1-catalog-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    store = LocalStore(args.root, run_id)
    budget = RequestBudget(args.max_pages * 4)
    checkpoint_key = f"catalog_{args.max_results}"
    previous = store.load_checkpoint(checkpoint_key)
    if previous and previous.get("status") != "complete":
        last_appid = previous.get("last_appid")
        refs = list(previous.get("page_refs", []))
        pages_total = int(previous.get("page_count", 0))
    else:
        last_appid = None
        refs = []
        pages_total = 0
    pages_this_run = 0
    complete = False
    observations = []
    try:
        with SteamAPI(budget=budget, retries=3) as api:
            while pages_this_run < args.max_pages:
                response = api.get_app_list(
                    api_key=api_key, last_appid=last_appid, max_results=args.max_results
                )
                pages_total += 1
                pages_this_run += 1
                observation = store.save_response(response, page_number=pages_total)
                observations.append(observation)
                refs.append(observation)
                wrapper = response.payload.get("response")
                if not isinstance(wrapper, dict) or not isinstance(wrapper.get("apps"), list):
                    store.save_checkpoint(
                        checkpoint_key,
                        {
                            "source_kind": "app_list",
                            "status": "invalid_response",
                            "last_appid": last_appid,
                            "page_count": pages_total,
                            "page_refs": refs,
                        },
                    )
                    write_json(
                        store.run_root / "manifest.json",
                        {
                            "run_id": run_id,
                            "source": "IStoreService/GetAppList",
                            "status": "invalid_response",
                            "error": "response.apps list missing; raw response preserved",
                            "credential_source": "STEAM_WEB_API_KEY",
                            "credential_recorded": False,
                            "observations": observations,
                        },
                    )
                    raise RuntimeError(
                        "GetAppList response shape is not the documented/expected "
                        "response.apps array; raw payload was preserved for inspection"
                    )
                apps = wrapper["apps"]
                if not apps:
                    complete = True
                    break
                try:
                    last_appid = int(apps[-1]["appid"])
                except (KeyError, TypeError, ValueError) as exc:
                    store.save_checkpoint(
                        checkpoint_key,
                        {
                            "source_kind": "app_list",
                            "status": "invalid_response",
                            "last_appid": last_appid,
                            "page_count": pages_total,
                            "page_refs": refs,
                        },
                    )
                    raise RuntimeError("GetAppList returned an app without a valid appid") from exc
                store.save_checkpoint(
                    checkpoint_key,
                    {
                        "source_kind": "app_list",
                        "status": "partial",
                        "last_appid": last_appid,
                        "page_count": pages_total,
                        "page_refs": refs,
                    },
                )
                if len(apps) < args.max_results:
                    complete = True
                    break
    except SteamAPIError as exc:
        write_json(
            store.run_root / "manifest.json",
            {
                "run_id": run_id,
                "source": "IStoreService/GetAppList",
                "status": "request_error",
                "error": str(exc),
                "request_attempts_used": budget.used,
                "credential_source": "STEAM_WEB_API_KEY",
                "credential_recorded": False,
                "observations": observations,
            },
        )
        raise

    app_rows = _catalog_rows(store, refs)
    catalog_schema = pa.schema(
        [
            ("appid", pa.int64()),
            ("name", pa.string()),
            ("last_modified", pa.int64()),
            ("price_change_number", pa.int64()),
            ("source_observation_id", pa.string()),
            ("payload_sha256", pa.string()),
        ]
    )
    catalog_table = store.write_table("catalog_apps", app_rows, catalog_schema)
    store.save_checkpoint(
        checkpoint_key,
        {
            "source_kind": "app_list",
            "status": "complete" if complete else "page_budget_reached",
            "last_appid": last_appid,
            "page_count": pages_total,
            "page_refs": refs,
        },
    )
    manifest = {
        "run_id": run_id,
        "source": "IStoreService/GetAppList",
        "status": "complete" if complete else "partial",
        "page_budget_status": "complete" if complete else "page_budget_reached",
        "request_attempts_used": budget.used,
        "page_count_this_run": len(observations),
        "page_count_total": pages_total,
        "last_appid": last_appid,
        "app_count": len(app_rows),
        "observations_this_run": observations,
        "page_observations": refs,
        "outputs": {"catalog_apps": str(catalog_table)},
        "credential_source": "STEAM_WEB_API_KEY",
        "credential_recorded": False,
    }
    write_json(store.run_root / "manifest.json", manifest)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "run_id": run_id,
                "pages_this_run": len(observations),
                "pages_total": pages_total,
                "request_attempts_used": budget.used,
                "last_appid": last_appid,
                "app_count": len(app_rows),
                "normalized_path": str(catalog_table),
            },
            indent=2,
        )
    )
    return 0 if complete else 2


def _catalog_rows(store: LocalStore, page_refs: list[dict[str, object]]) -> list[dict[str, object]]:
    """Normalize catalog identity fields while keeping exact pages in raw storage."""
    apps_by_id: dict[int, dict[str, object]] = {}
    for ref in page_refs:
        payload = store.payload_for(ref)
        wrapper = payload.get("response")
        apps = wrapper.get("apps") if isinstance(wrapper, dict) else None
        if not isinstance(apps, list):
            continue
        for app in apps:
            if not isinstance(app, dict):
                continue
            try:
                appid = int(app["appid"])
            except (KeyError, TypeError, ValueError):
                continue
            if appid <= 0:
                continue
            apps_by_id[appid] = {
                "appid": appid,
                "name": str(app.get("name") or ""),
                "last_modified": _catalog_optional_int(app.get("last_modified")),
                "price_change_number": _catalog_optional_int(app.get("price_change_number")),
                "source_observation_id": str(ref["observation_id"]),
                "payload_sha256": str(ref["payload_sha256"]),
            }
    return [apps_by_id[appid] for appid in sorted(apps_by_id)]


def _catalog_optional_int(value: object) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError, OverflowError):
        return None


def _is_collection_run_name(name: str) -> bool:
    return name.startswith("rv1-") and len(name) > 4 and name[4].isdigit()


if __name__ == "__main__":
    raise SystemExit(main())
