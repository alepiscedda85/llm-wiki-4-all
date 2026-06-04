"""Minimal workspace config reader for llm-wiki-4-all."""

from __future__ import annotations

from pathlib import Path


def parse_simple_yaml(path: Path) -> dict[str, str]:
    """Parse the flat key/value subset used by workspace config.yaml.

    This intentionally avoids adding a YAML dependency for the MVP. Supported
    lines look like `key: value`; comments and blank lines are ignored.
    """
    if not path.exists():
        return {}

    config: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip().strip("'\"")
        if key:
            config[key] = value
    return config
