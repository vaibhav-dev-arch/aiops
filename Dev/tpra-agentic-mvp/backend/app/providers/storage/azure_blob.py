"""Azure Blob Storage stub — raises until configured."""

from __future__ import annotations

from app.core.exceptions import TPRAError
from app.providers.base import StorageProvider


class AzureBlobStorageProvider(StorageProvider):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        if not connection_string:
            # Stub is instantiable but operations fail clearly
            pass

    def _ensure(self) -> None:
        if not self.connection_string:
            raise TPRAError(
                "Azure Blob Storage is not configured. Set AZURE_STORAGE_CONNECTION_STRING.",
                code="azure_not_configured",
                status_code=501,
            )
        raise TPRAError(
            "Azure Blob Storage stub — install azure-storage-blob and implement for client deploy.",
            code="azure_stub",
            status_code=501,
        )

    def put_bytes(self, key: str, data: bytes, *, content_type: str = "application/octet-stream") -> str:
        self._ensure()
        return key

    def get_bytes(self, key: str) -> bytes:
        self._ensure()
        return b""

    def delete(self, key: str) -> None:
        self._ensure()

    def exists(self, key: str) -> bool:
        self._ensure()
        return False
