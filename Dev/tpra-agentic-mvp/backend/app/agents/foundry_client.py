"""Generic Azure AI Foundry client stub."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import TPRAError


class FoundryClient:
    def __init__(self, endpoint: str | None = None, api_key: str | None = None):
        self.endpoint = endpoint
        self.api_key = api_key

    def invoke_agent(self, agent_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise TPRAError(
            f"Foundry client stub — cannot invoke '{agent_name}' until Azure Foundry is configured.",
            code="azure_stub",
            status_code=501,
        )
