"""Memory management for JARVIS."""

from typing import List, Tuple, Optional
from datetime import datetime

from core.logger import get_logger
from core.models import ToolResult
from memory.database import DatabaseManager

logger = get_logger("memory")


class MemoryManager:
    """Manages JARVIS memory — conversations, facts, preferences."""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def add_conversation(self, user_message: str, assistant_message: str,
                         language: str = "en") -> None:
        """Store a conversation exchange."""
        try:
            self.db.execute(
                "INSERT INTO conversations (user_message, assistant_message, language) VALUES (?, ?, ?)",
                (user_message, assistant_message, language)
            )
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")

    def get_recent_conversation(self, limit: int = 10) -> List[Tuple[str, str]]:
        """Get recent conversation history."""
        try:
            rows = self.db.fetchall(
                "SELECT user_message, assistant_message FROM conversations "
                "ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            result = [(r["user_message"], r["assistant_message"]) for r in rows]
            result.reverse()
            return result
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []

    def remember(self, category: str = "general", key: str = "",
                 value: str = "", **kwargs) -> ToolResult:
        """Store a memory entry."""
        if not key and not value:
            text = kwargs.get("text", "")
            if text:
                key = "note"
                value = text
            else:
                return ToolResult(success=False, error="Nothing to remember.")

        try:
            self.db.execute(
                "INSERT INTO memory (category, key, value) VALUES (?, ?, ?)",
                (category, key, value)
            )
            return ToolResult(success=True, message=f"Remembered: {key} = {value}")
        except Exception as e:
            return ToolResult(success=False, error=f"Failed to remember: {e}")

    def get_memories(self, category: Optional[str] = None, limit: int = 20) -> List[dict]:
        """Retrieve memories."""
        try:
            if category:
                rows = self.db.fetchall(
                    "SELECT * FROM memory WHERE category = ? ORDER BY timestamp DESC LIMIT ?",
                    (category, limit)
                )
            else:
                rows = self.db.fetchall(
                    "SELECT * FROM memory ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Failed to get memories: {e}")
            return []

    def execute(self, **kwargs) -> ToolResult:
        """Tool interface — dispatches based on the registered tool name."""
        action = kwargs.get("_action", "show_memory")
        if action == "show_memory":
            return self.show_memory(**kwargs)
        elif action == "clear_memory":
            return self.clear_memory(**kwargs)
        elif action == "remember":
            return self.remember(**kwargs)
        return self.show_memory(**kwargs)

    def show_memory(self, **kwargs) -> ToolResult:
        """Show stored memories."""
        category = kwargs.get("category")
        memories = self.get_memories(category=category)
        if not memories:
            return ToolResult(success=True, message="No memories stored yet.")

        lines = ["📝 Stored Memories:"]
        for m in memories:
            lines.append(f"  [{m.get('category', '')}] {m.get('key', '')}: {m.get('value', '')}")
        return ToolResult(success=True, message="\n".join(lines))

    def clear_memory(self, category: Optional[str] = None, **kwargs) -> ToolResult:
        """Clear memories."""
        try:
            if category:
                self.db.execute("DELETE FROM memory WHERE category = ?", (category,))
                return ToolResult(success=True, message=f"Cleared memories in category: {category}")
            else:
                self.db.execute("DELETE FROM memory")
                return ToolResult(success=True, message="All memories cleared.")
        except Exception as e:
            return ToolResult(success=False, error=f"Failed to clear memory: {e}")

    def set_preference(self, key: str, value: str) -> None:
        """Set a user preference."""
        try:
            self.db.execute(
                "INSERT OR REPLACE INTO preferences (key, value, updated) VALUES (?, ?, ?)",
                (key, value, datetime.now().isoformat())
            )
        except Exception as e:
            logger.error(f"Failed to set preference: {e}")

    def get_preference(self, key: str, default: str = "") -> str:
        """Get a user preference."""
        try:
            row = self.db.fetchone("SELECT value FROM preferences WHERE key = ?", (key,))
            return row["value"] if row else default
        except Exception:
            return default
