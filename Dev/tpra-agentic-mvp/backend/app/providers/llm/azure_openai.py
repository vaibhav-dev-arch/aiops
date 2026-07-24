"""Azure OpenAI LLM stub."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import TPRAError
from app.providers.base import LLMProvider


class AzureOpenAILLMProvider(LLMProvider):
    def __init__(self, endpoint: str, api_key: str, deployment: str):
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment = deployment

    def generate(self, *, system: str, user: str, **kwargs: Any) -> str:
        raise TPRAError(
            "Azure OpenAI stub — configure AZURE_OPENAI_* for client deploy.",
            code="azure_stub",
            status_code=501,
        )
