"""Small wrapper over the shared pipeline command."""

import sys

from steam_insights.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["pipeline"] + sys.argv[1:]))
