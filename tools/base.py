"""Base tool interface."""

from abc import ABC, abstractmethod
from core.models import ToolResult


class BaseTool(ABC):
    """Abstract base class for all JARVIS tools."""

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def description(self) -> str:
        return self.__doc__ or "No description"

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        ...
