"""Small wrapper over the shared annotations-import command."""

import sys

from steam_insights.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["annotations-import"] + sys.argv[1:]))
