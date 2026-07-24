"""Provider abstract interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.domain.models import UserContext


class StorageProvider(ABC):
    @abstractmethod
    def put_bytes(self, key: str, data: bytes, *, content_type: str = "application/octet-stream") -> str:
        raise NotImplementedError

    @abstractmethod
    def get_bytes(self, key: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, key: str) -> bool:
        raise NotImplementedError


class MetadataProvider(ABC):
    @abstractmethod
    def upsert(self, collection: str, doc_id: str, body: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, collection: str, doc_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, collection: str, doc_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def list(self, collection: str, *, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, *, system: str, user: str, **kwargs: Any) -> str:
        raise NotImplementedError


class DocIntelligenceProvider(ABC):
    @abstractmethod
    def extract_text(self, data: bytes, *, filename: str, content_type: str = "") -> str:
        raise NotImplementedError


class AuthProvider(ABC):
    @abstractmethod
    def authenticate(self, headers: dict[str, str]) -> UserContext:
        raise NotImplementedError
