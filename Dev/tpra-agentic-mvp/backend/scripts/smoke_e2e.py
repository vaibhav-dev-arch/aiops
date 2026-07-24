#!/usr/bin/env python3
"""Smoke test: UC1→UC2 via HTTP against a running API (or TestClient)."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import reset_settings_cache  # noqa: E402
from app.main import create_app  # noqa: E402
from app.providers.registry import reset_registry  # noqa: E402


def main() -> int:
    reset_settings_cache()
    reset_registry()
    app = create_app()
    client = TestClient(app)
    client.headers.update({"x-user-id": "smoke", "x-user-role": "admin", "x-user-name": "Smoke"})
    ws = client.post("/api/workspaces", json={"name": "Smoke"}).json()
    csv_path = ROOT / "backend/tests/fixtures/sample_approved_findings.csv"
    up = client.post(
        f"/api/workspaces/{ws['id']}/files",
        files={"upload": ("findings.csv", csv_path.read_bytes(), "text/csv")},
    )
    up.raise_for_status()
    run1 = client.post(
        f"/api/workspaces/{ws['id']}/agents/runs",
        json={"agent_id": "uc1", "input_file_ids": [up.json()["id"]]},
    )
    run1.raise_for_status()
    files = client.get(f"/api/workspaces/{ws['id']}/files").json()
    structured = next(f for f in files if f["filename"] == "structured_findings.csv")
    run2 = client.post(
        f"/api/workspaces/{ws['id']}/agents/runs",
        json={"agent_id": "uc2", "input_file_ids": [structured["id"]]},
    )
    run2.raise_for_status()
    print("SMOKE OK", run1.json()["status"], run2.json()["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
