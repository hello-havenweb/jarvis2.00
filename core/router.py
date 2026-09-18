"""Command router — maps user input to intents and tool execution."""

import re
from typing import Optional

from core.logger import get_logger
from core.models import UserCommand, Intent, PermissionLevel
from core.config import Config
from ai.intent import IntentDetector

logger = get_logger("router")


class CommandRouter:
    """Routes user commands to appropriate tools."""

    def __init__(self) -> None:
        self.config = Config()
        self.intent_detector = IntentDetector()
        self._quick_commands = self._build_quick_commands()

    def _build_quick_commands(self) -> dict:
        """Build quick-match commands for common operations."""
        return {
            r"^(open|launch|start)\s+(.+)$": ("open_application", "app_name"),
            r"^(close|exit|quit)\s+(.+)$": ("close_application", "app_name"),
            r"^(show|display)\s+system\s+(status|info|information)$": ("system_info", None),
            r"^take\s+(a\s+)?screenshot$": ("screenshot", None),
            r"^(show|open)\s+(desktop|downloads?|documents?)$": ("open_folder", "folder"),
            r"^create\s+folder\s+(.+)$": ("create_folder", "name"),
            r"^(show|list)\s+(my\s+)?reminders?$": ("show_reminders", None),
            r"^(show|what)\s+(is\s+)?(today'?s?\s+)?(progress|report|activity).*$": ("daily_progress", None),
            r"^(what\s+)?(time|date)\s*(is\s+it)?$": ("show_time", None),
            r"^(search|find|google)\s+(.+)$": ("web_search", "query"),
            r"^(show|display)\s+memory$": ("show_memory", None),
            r"^(clear|wipe)\s+memory(\s+(.+))?$": ("clear_memory", "category"),
        }

    def route(self, command: UserCommand) -> Intent:
        """Determine intent from user command."""
        text = command.text.strip()

        # Try quick pattern matching first
        intent = self._match_quick(text)
        if intent:
            intent.language = command.language
            intent.raw_text = text
            logger.info(f"Quick-matched intent: {intent.action}")
            return intent

        # Fall through to AI-based intent detection
        intent = self.intent_detector.detect(text, command.language)
        if intent:
            intent.raw_text = text
            logger.info(f"AI-detected intent: {intent.action}")
            return intent

        # Default: conversation
        return Intent(
            action="conversation",
            tool="ai_chat",
            parameters={"message": text},
            raw_text=text,
            language=command.language,
            confidence=0.5
        )

    def _match_quick(self, text: str) -> Optional[Intent]:
        """Try pattern-based matching for common commands."""
        text_lower = text.lower().strip()

        for pattern, (action, param_name) in self._quick_commands.items():
            match = re.match(pattern, text_lower, re.IGNORECASE)
            if match:
                params = {}
                if param_name:
                    groups = match.groups()
                    # Find the last non-None group as the parameter
                    val = groups[-1] if groups else ""
                    if val:
                        params[param_name] = val.strip()
                return Intent(
                    action=action,
                    tool=action,
                    parameters=params,
                    confidence=0.9
                )

        # Reminder pattern
        reminder_match = re.match(
            r"^(set\s+)?(remind|reminder)\s*(me\s+)?(to\s+)?(.+)$",
            text_lower, re.IGNORECASE
        )
        if reminder_match:
            return Intent(
                action="set_reminder",
                tool="set_reminder",
                parameters={"text": reminder_match.group(5).strip()},
                confidence=0.85
            )

        # Batch processing
        batch_match = re.match(
            r"^process\s+(.+)\s+in\s+batches?\s+of\s+(\d+)$",
            text_lower, re.IGNORECASE
        )
        if batch_match:
            return Intent(
                action="batch_process",
                tool="batch_process",
                parameters={
                    "path": batch_match.group(1).strip(),
                    "size": int(batch_match.group(2))
                },
                confidence=0.9
            )

        return None
