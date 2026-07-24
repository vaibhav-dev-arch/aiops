"""Azure Cosmos DB metadata stub."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import TPRAError
from app.providers.base import MetadataProvider


class CosmosMetadataProvider(MetadataProvider):
    def __init__(self, endpoint: str, key: str, database: str = "tpra"):
        self.endpoint = endpoint
        self.key = key
        self.database = database

    def _ensure(self) -> None:
        raise TPRAError(
            "Cosmos DB stub — configure AZURE_COSMOS_* and implement for client deploy.",
            code="azure_stub",
            status_code=501,
        )

    def upsert(self, collection: str, doc_id: str, body: dict[str, Any]) -> None:
        self._ensure()

    def get(self, collection: str, doc_id: str) -> dict[str, Any] | None:
        self._ensure()
        return None

    def delete(self, collection: str, doc_id: str) -> None:
        self._ensure()

    def list(self, collection: str, *, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        self._ensure()
        return []
