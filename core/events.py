"""Simple event bus for JARVIS subsystem communication."""

from typing import Callable, Dict, List, Any
from core.logger import get_logger

logger = get_logger("events")


class EventBus:
    """Publish/subscribe event system."""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable]] = {}

    def subscribe(self, event: str, handler: Callable) -> None:
        """Register a handler for an event."""
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)
        logger.debug(f"Subscribed to event '{event}': {handler.__name__}")

    def unsubscribe(self, event: str, handler: Callable) -> None:
        """Remove a handler for an event."""
        if event in self._handlers:
            self._handlers[event] = [h for h in self._handlers[event] if h != handler]

    def publish(self, event: str, **kwargs: Any) -> None:
        """Publish an event, calling all handlers."""
        handlers = self._handlers.get(event, [])
        for handler in handlers:
            try:
                handler(**kwargs)
            except Exception as e:
                logger.error(f"Error in event handler '{handler.__name__}' for '{event}': {e}")

    def clear(self) -> None:
        """Remove all handlers."""
        self._handlers.clear()


# Global event bus instance
event_bus = EventBus()
