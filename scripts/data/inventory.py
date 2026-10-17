"""Small wrapper over the shared pipeline --stage inventory command."""

import sys

from steam_insights.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["pipeline", "--stage", "inventory"] + sys.argv[1:]))
