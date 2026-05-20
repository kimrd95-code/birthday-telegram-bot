from pathlib import Path
from typing import Any

import yaml

from config import MESSAGES_PATH

_cache: dict[str, Any] | None = None


def _load() -> dict[str, Any]:
    global _cache
    if _cache is None:
        with open(MESSAGES_PATH, encoding="utf-8") as f:
            _cache = yaml.safe_load(f)
    return _cache


def get(path: str) -> str:
    """Путь вида 'start.welcome' или 'reminder.week_before'."""
    node: Any = _load()
    for part in path.split("."):
        node = node[part]
    return str(node).strip()


def fmt(path: str, **kwargs: Any) -> str:
    text = get(path)
    return text.format(**kwargs)
