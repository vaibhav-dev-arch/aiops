"""Azure Document Intelligence stub."""

from __future__ import annotations

from app.core.exceptions import TPRAError
from app.providers.base import DocIntelligenceProvider


class AzureDocIntelligenceProvider(DocIntelligenceProvider):
    def __init__(self, endpoint: str, key: str):
        self.endpoint = endpoint
        self.key = key

    def extract_text(self, data: bytes, *, filename: str, content_type: str = "") -> str:
        raise TPRAError(
            "Azure Document Intelligence stub — configure endpoints for client deploy.",
            code="azure_stub",
            status_code=501,
        )
