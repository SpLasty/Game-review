"""Small wrapper over the shared prepare-data command."""

import sys

from steam_insights.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["prepare-data"] + sys.argv[1:]))
