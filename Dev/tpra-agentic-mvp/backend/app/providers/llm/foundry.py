"""Azure AI Foundry LLM stub."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import TPRAError
from app.providers.base import LLMProvider


class FoundryLLMProvider(LLMProvider):
    def __init__(self, agent_endpoint: str | None = None):
        self.agent_endpoint = agent_endpoint

    def generate(self, *, system: str, user: str, **kwargs: Any) -> str:
        raise TPRAError(
            "Foundry LLM stub — deploy Foundry agents and wire endpoints for client use.",
            code="azure_stub",
            status_code=501,
        )
