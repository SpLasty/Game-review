"""Small wrapper over the shared backfill-reviews command."""

import sys

from steam_insights.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["backfill-reviews"] + sys.argv[1:]))
