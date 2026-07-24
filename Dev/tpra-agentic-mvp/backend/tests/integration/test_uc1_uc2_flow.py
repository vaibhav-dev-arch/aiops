"""Integration test: full UC1 → UC2 pipeline."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_uc1_uc2_flow(client: TestClient, fixtures_dir: Path):
    # Create workspace
    ws = client.post("/api/workspaces", json={"name": "Vendor A TPRA", "description": "test"}).json()
    assert "id" in ws
    workspace_id = ws["id"]

    # Upload findings CSV
    csv_bytes = (fixtures_dir / "sample_approved_findings.csv").read_bytes()
    up = client.post(
        f"/api/workspaces/{workspace_id}/files",
        files={"upload": ("findings.csv", csv_bytes, "text/csv")},
    )
    assert up.status_code == 201, up.text
    file_id = up.json()["id"]

    # Run UC1
    run1 = client.post(
        f"/api/workspaces/{workspace_id}/agents/runs",
        json={"agent_id": "uc1_structured_findings", "input_file_ids": [file_id]},
    )
    assert run1.status_code == 201, run1.text
    body1 = run1.json()
    assert body1["status"] == "succeeded"
    assert body1["output_file_ids"]
    assert body1["result"]["summary"]["finding_count"] == 3

    # Find structured_findings.csv output
    files = client.get(f"/api/workspaces/{workspace_id}/files").json()
    structured = next(f for f in files if f["filename"] == "structured_findings.csv")

    # Reviewer decision
    finding_id = body1["result"]["findings"][0]["id"]
    client.headers["x-user-role"] = "reviewer"
    decision = client.post(
        f"/api/workspaces/{workspace_id}/reviewer-log",
        json={"finding_id": finding_id, "decision": "approve", "comment": "looks good"},
    )
    assert decision.status_code == 201, decision.text

    # Run UC2
    client.headers["x-user-role"] = "admin"
    run2 = client.post(
        f"/api/workspaces/{workspace_id}/agents/runs",
        json={"agent_id": "uc2_draft_report", "input_file_ids": [structured["id"]]},
    )
    assert run2.status_code == 201, run2.text
    body2 = run2.json()
    assert body2["status"] == "succeeded"
    assert body2["result"]["summary"]["approved_count"] == 3

    files2 = client.get(f"/api/workspaces/{workspace_id}/files").json()
    assert any(f["filename"] == "draft_tpra_report.docx" for f in files2)
    assert any(f["filename"] == "missing_inputs.txt" for f in files2)

    # Audit trail
    audit = client.get(f"/api/workspaces/{workspace_id}/audit").json()
    actions = {e["action"] for e in audit}
    assert "workspace.create" in actions
    assert "uc1.complete" in actions
    assert "uc2.complete" in actions

    # Catalog + health
    catalog = client.get("/api/catalog/agents").json()
    assert len(catalog) >= 2
    health = client.get("/api/health").json()
    assert health["status"] == "ok"
