"""Small wrapper over the shared llm-annotations-import command."""

import sys

from steam_insights.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["llm-annotations-import"] + sys.argv[1:]))
