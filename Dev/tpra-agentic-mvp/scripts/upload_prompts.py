#!/usr/bin/env python3
"""Publish prompts/ to Azure Blob (stub)."""

from __future__ import annotations

from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1] / "prompts"
    files = list(root.rglob("*"))
    print(f"[stub] would upload {sum(1 for f in files if f.is_file())} prompt files from {root}")


if __name__ == "__main__":
    main()
