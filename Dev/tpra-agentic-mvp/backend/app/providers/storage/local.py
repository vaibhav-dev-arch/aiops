"""Local filesystem storage provider."""

from __future__ import annotations

from pathlib import Path

from app.core.exceptions import NotFoundError
from app.providers.base import StorageProvider


class LocalStorageProvider(StorageProvider):
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe = key.lstrip("/").replace("..", "_")
        path = self.root / safe
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def put_bytes(self, key: str, data: bytes, *, content_type: str = "application/octet-stream") -> str:
        path = self._path(key)
        path.write_bytes(data)
        return key

    def get_bytes(self, key: str) -> bytes:
        path = self._path(key)
        if not path.exists():
            raise NotFoundError(f"Object not found: {key}")
        return path.read_bytes()

    def delete(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            path.unlink()

    def exists(self, key: str) -> bool:
        return self._path(key).exists()
