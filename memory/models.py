"""Memory data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ConversationEntry:
    id: int = 0
    user_message: str = ""
    assistant_message: str = ""
    language: str = "en"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MemoryEntry:
    id: int = 0
    category: str = ""
    key: str = ""
    value: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Preference:
    key: str = ""
    value: str = ""
    updated: datetime = field(default_factory=datetime.now)
