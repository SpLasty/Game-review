"""Small wrapper over the shared recover-sources command."""

import sys

from steam_insights.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["recover-sources"] + sys.argv[1:]))
