"""Persistence layers for email storage (In-memory and SQLite)."""

import sqlite3
import json
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from .drafts import Draft, DraftStatus


class StorageError(Exception):
    """Base storage exception."""
    pass


class BaseDraftStorage(ABC):
    """Abstract interface for draft storage."""

    @abstractmethod
    def save(self, draft: Draft) -> None:
        pass

    @abstractmethod
    def get(self, draft_id: str) -> Optional[Draft]:
        pass

    @abstractmethod
    def delete(self, draft_id: str) -> bool:
        pass

    @abstractmethod
    def list_all(self) -> List[Draft]:
        pass


class SQLiteDraftStorage(BaseDraftStorage):
    """SQLite-backed storage for drafts."""

    def __init__(self, db_path: str = "drafts.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS drafts (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
                """
            )
            conn.commit()

    def save(self, draft: Draft) -> None:
        data_json = json.dumps(draft.to_dict())
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO drafts (id, data, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    data = excluded.data,
                    updated_at = excluded.updated_at
                """,
                (draft.id, data_json, draft.updated_at.isoformat()),
            )
            conn.commit()

    def get(self, draft_id: str) -> Optional[Draft]:
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT data FROM drafts WHERE id = ?", (draft_id,))
            row = cursor.fetchone()
            if row:
                return Draft.from_dict(json.loads(row[0]))
        return None

    def delete(self, draft_id: str) -> bool:
        with self._get_conn() as conn:
            cursor = conn.execute("DELETE FROM drafts WHERE id = ?", (draft_id,))
            conn.commit()
            return cursor.rowcount > 0

    def list_all(self) -> List[Draft]:
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT data FROM drafts ORDER BY updated_at DESC")
            return [Draft.from_dict(json.loads(row[0])) for row in cursor.fetchall()]
