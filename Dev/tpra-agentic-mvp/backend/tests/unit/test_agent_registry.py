"""Unit tests for agent registry."""

from pathlib import Path

from app.agents.agent_registry import AgentRegistry


def test_agent_registry_loads_yaml():
    root = Path(__file__).resolve().parents[3]
    reg = AgentRegistry(root / "foundry" / "agents.yaml")
    agents = reg.list_agents()
    ids = {a["id"] for a in agents}
    assert "uc1_structured_findings" in ids
    assert "uc2_draft_report" in ids
    assert reg.get("uc1_structured_findings")["name"]
