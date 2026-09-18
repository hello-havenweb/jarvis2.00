"""Core data models for JARVIS."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class PermissionLevel(Enum):
    SAFE = "SAFE"
    CONFIRM = "CONFIRM"
    DANGEROUS = "DANGEROUS"
    BLOCKED = "BLOCKED"


class JarvisState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    EXECUTING = "executing"
    SPEAKING = "speaking"
    ERROR = "error"


@dataclass
class UserCommand:
    text: str
    language: str = "en"
    source: str = "text"  # "text" or "voice"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Intent:
    action: str
    tool: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    raw_text: str = ""
    language: str = "en"


@dataclass
class ActionPlan:
    steps: List[Intent] = field(default_factory=list)
    requires_confirmation: bool = False
    permission_level: PermissionLevel = PermissionLevel.SAFE
    description: str = ""


@dataclass
class ToolResult:
    success: bool
    message: str = ""
    data: Any = None
    error: str = ""


@dataclass
class JarvisResponse:
    text: str
    speak: bool = True
    language: str = "en"
    tool_results: List[ToolResult] = field(default_factory=list)
    state: JarvisState = JarvisState.IDLE


@dataclass
class ActivityEntry:
    timestamp: datetime
    category: str
    action: str
    details: str = ""
    success: bool = True
