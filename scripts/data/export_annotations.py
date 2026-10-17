"""Small wrapper over the shared annotations-export command."""

import sys

from steam_insights.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["annotations-export"] + sys.argv[1:]))
