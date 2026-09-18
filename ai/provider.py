"""Abstract AI provider interface."""

from abc import ABC, abstractmethod
from typing import List, Dict


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        ...

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send messages and get a response."""
        ...

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text from a single prompt."""
        ...
