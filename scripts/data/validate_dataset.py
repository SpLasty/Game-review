"""Small wrapper over the shared pipeline-validate command."""

import sys

from steam_insights.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["pipeline-validate"] + sys.argv[1:]))
