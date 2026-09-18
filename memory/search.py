"""Memory search functionality."""

from typing import List
from core.logger import get_logger
from memory.database import DatabaseManager

logger = get_logger("memory_search")


class MemorySearch:
    """Search through JARVIS memory and conversations."""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def search_conversations(self, query: str, limit: int = 20) -> List[dict]:
        """Search conversation history."""
        try:
            rows = self.db.fetchall(
                "SELECT * FROM conversations WHERE "
                "user_message LIKE ? OR assistant_message LIKE ? "
                "ORDER BY timestamp DESC LIMIT ?",
                (f"%{query}%", f"%{query}%", limit)
            )
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Conversation search error: {e}")
            return []

    def search_memories(self, query: str, limit: int = 20) -> List[dict]:
        """Search memory entries."""
        try:
            rows = self.db.fetchall(
                "SELECT * FROM memory WHERE "
                "key LIKE ? OR value LIKE ? OR category LIKE ? "
                "ORDER BY timestamp DESC LIMIT ?",
                (f"%{query}%", f"%{query}%", f"%{query}%", limit)
            )
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Memory search error: {e}")
            return []

    def search_all(self, query: str, limit: int = 20) -> dict:
        """Search all memory stores."""
        return {
            "conversations": self.search_conversations(query, limit),
            "memories": self.search_memories(query, limit),
        }
