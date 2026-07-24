"""SQLite-backed metadata store."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.providers.base import MetadataProvider


class SqliteMetadataProvider(MetadataProvider):
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    collection TEXT NOT NULL,
                    id TEXT NOT NULL,
                    body TEXT NOT NULL,
                    PRIMARY KEY (collection, id)
                )
                """
            )
            conn.commit()

    def upsert(self, collection: str, doc_id: str, body: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO documents (collection, id, body) VALUES (?, ?, ?)
                ON CONFLICT(collection, id) DO UPDATE SET body=excluded.body
                """,
                (collection, doc_id, json.dumps(body, default=str)),
            )
            conn.commit()

    def get(self, collection: str, doc_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT body FROM documents WHERE collection=? AND id=?",
                (collection, doc_id),
            ).fetchone()
        if not row:
            return None
        return json.loads(row["body"])

    def delete(self, collection: str, doc_id: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM documents WHERE collection=? AND id=?",
                (collection, doc_id),
            )
            conn.commit()

    def list(self, collection: str, *, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT body FROM documents WHERE collection=?",
                (collection,),
            ).fetchall()
        docs = [json.loads(r["body"]) for r in rows]
        if not filters:
            return docs
        out = []
        for doc in docs:
            if all(doc.get(k) == v for k, v in filters.items()):
                out.append(doc)
        return out
