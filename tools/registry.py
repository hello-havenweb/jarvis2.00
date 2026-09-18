"""Tool registry — central registry for all available tools."""

from typing import Optional, Dict
from core.logger import get_logger
from core.models import ToolResult

logger = get_logger("registry")


class ToolRegistry:
    """Central registry for all JARVIS tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, object] = {}

    def register(self, name: str, tool: object) -> None:
        """Register a tool with a name."""
        self._tools[name] = tool
        logger.debug(f"Registered tool: {name}")

    def get(self, name: str) -> Optional[object]:
        """Get a tool by name."""
        return self._tools.get(name)

    def has(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools

    def list_tools(self) -> list:
        """List all registered tool names."""
        return list(self._tools.keys())

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools
