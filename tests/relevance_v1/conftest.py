from __future__ import annotations

from pathlib import Path

import pytest

from steam_patch_relevance.config import load_config

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def config():
    return load_config(REPO_ROOT / "configs" / "relevance_v1.toml")
