#!/usr/bin/env python3
"""Create/update Azure AI Foundry agents (stub)."""

from __future__ import annotations

from pathlib import Path

import yaml


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    for path in sorted((root / "foundry").glob("*-agent.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        print(f"[stub] would upsert Foundry agent from {path.name}: {data.get('name')}")


if __name__ == "__main__":
    main()
