"""Unit tests for input parsers."""

from __future__ import annotations

import json
from pathlib import Path

from app.agents.structured_findings.parsers import parse_bytes


def test_parse_csv(fixtures_dir: Path):
    data = (fixtures_dir / "sample_approved_findings.csv").read_bytes()
    rows = parse_bytes(data, "sample.csv")
    assert len(rows) == 3
    assert rows[0]["title"] == "MFA Gap"
    assert rows[1]["severity"] == "critical"


def test_parse_json(fixtures_dir: Path):
    data = (fixtures_dir / "sample_approved_findings.json").read_bytes()
    rows = parse_bytes(data, "sample.json")
    assert len(rows) == 3
    assert rows[2]["category"] == "logging"


def test_parse_json_array():
    payload = [{"title": "A", "severity": "low", "category": "general"}]
    rows = parse_bytes(json.dumps(payload).encode(), "arr.json")
    assert len(rows) == 1
    assert rows[0]["title"] == "A"
