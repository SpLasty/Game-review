"""Command-line entry points for the initial offline data workflow."""

import argparse
import sys
from pathlib import Path

from steam_insights.config import load_config
from steam_insights.data.io import inventory, write_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["inventory"])
    parser.add_argument("--config", type=Path, default=Path("configs/data.toml"))
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        result = inventory(config)
        output = config.reports_dir / "source_inventory.json"
        write_json(output, result)
        print(f"Source inventory: {output}")
        for name, source in result["sources"].items():
            print(f"  {name}: {source['rows']:,} rows")
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"Data workflow failed: {exc}", file=sys.stderr)
        return 1
