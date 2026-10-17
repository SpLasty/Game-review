"""Small wrapper over the shared pipeline --stage reviews command."""

import sys

from steam_insights.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["pipeline", "--stage", "reviews"] + sys.argv[1:]))
