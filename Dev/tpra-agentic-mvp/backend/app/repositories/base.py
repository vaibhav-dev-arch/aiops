"""Repository base helpers."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from app.providers.base import MetadataProvider

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    collection: str
    model: type[T]

    def __init__(self, metadata: MetadataProvider):
        self.metadata = metadata

    def save(self, entity: T) -> T:
        data = entity.model_dump(mode="json")
        self.metadata.upsert(self.collection, data["id"], data)
        return entity

    def get(self, entity_id: str) -> T | None:
        raw = self.metadata.get(self.collection, entity_id)
        if raw is None:
            return None
        return self.model.model_validate(raw)

    def delete(self, entity_id: str) -> None:
        self.metadata.delete(self.collection, entity_id)

    def list(self, *, filters: dict[str, Any] | None = None) -> list[T]:
        rows = self.metadata.list(self.collection, filters=filters)
        return [self.model.model_validate(r) for r in rows]
