"""Load agent definitions from foundry/agents.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.core.config import get_settings


DEFAULT_AGENTS = [
    {
        "id": "uc1_structured_findings",
        "name": "Structured Findings Package Agent",
        "description": "Ingest vendor findings, normalize, validate, and package outputs.",
        "capabilities": ["parse", "normalize", "validate", "package"],
        "required_inputs": ["findings_file"],
        "model": "mock-local",
        "prompt_dir": "prompts/structured_findings/v1",
    },
    {
        "id": "uc2_draft_report",
        "name": "Draft TPRA Report Generation Agent",
        "description": "Generate a draft TPRA Word report from approved findings.",
        "capabilities": ["template_map", "llm_narrative", "docx"],
        "required_inputs": ["approved_findings_package"],
        "model": "mock-local",
        "prompt_dir": "prompts/draft_report/v1",
    },
]


class AgentRegistry:
    def __init__(self, agents_path: Path | None = None):
        self.agents_path = agents_path
        self._agents: list[dict[str, Any]] | None = None

    def _load(self) -> list[dict[str, Any]]:
        if self._agents is not None:
            return self._agents
        path = self.agents_path
        if path is None:
            settings = get_settings()
            path = settings.foundry_agents_path
        if path and Path(path).exists():
            with open(path, encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            agents = data.get("agents") or data.get("items") or []
            if isinstance(agents, list) and agents:
                self._agents = agents
                return self._agents
        self._agents = list(DEFAULT_AGENTS)
        return self._agents

    def list_agents(self) -> list[dict[str, Any]]:
        return list(self._load())

    def get(self, agent_id: str) -> dict[str, Any] | None:
        for agent in self._load():
            if agent.get("id") == agent_id:
                return agent
        return None
