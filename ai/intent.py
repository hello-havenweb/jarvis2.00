"""Intent detection from user input."""

import json
import re
from typing import Optional

from core.models import Intent
from core.logger import get_logger
from core.config import Config

logger = get_logger("intent")


class IntentDetector:
    """Detects user intent — uses pattern matching, with AI fallback."""

    def __init__(self) -> None:
        self.config = Config()

    def detect(self, text: str, language: str = "en") -> Optional[Intent]:
        """Detect intent from text. Returns None if no clear intent is found."""
        text_lower = text.lower().strip()

        # Language change commands
        lang_intent = self._detect_language_change(text_lower)
        if lang_intent:
            return lang_intent

        # Greeting
        if self._is_greeting(text_lower):
            return Intent(
                action="conversation",
                tool="ai_chat",
                parameters={"message": text},
                confidence=0.9,
                language=language
            )

        # Time/date
        if any(w in text_lower for w in ["time", "date", "waqt", "tarikh", "din"]):
            if "time" in text_lower or "waqt" in text_lower:
                return Intent(action="show_time", tool="show_time", confidence=0.9, language=language)
            return Intent(action="show_date", tool="show_date", confidence=0.9, language=language)

        # System status
        if any(phrase in text_lower for phrase in ["system status", "system info", "cpu", "ram", "memory usage", "disk space"]):
            return Intent(action="system_info", tool="system_info", confidence=0.9, language=language)

        # Screenshot
        if "screenshot" in text_lower or "screen capture" in text_lower:
            return Intent(action="screenshot", tool="screenshot", confidence=0.95, language=language)

        # Reminders
        if "reminder" in text_lower or "remind" in text_lower or "yaad" in text_lower:
            if any(w in text_lower for w in ["show", "list", "dikhao", "batao"]):
                return Intent(action="show_reminders", tool="show_reminders", confidence=0.9, language=language)
            if any(w in text_lower for w in ["cancel", "delete", "remove", "hatao"]):
                return Intent(
                    action="cancel_reminder", tool="cancel_reminder",
                    parameters={"text": text}, confidence=0.85, language=language
                )
            return Intent(
                action="set_reminder", tool="set_reminder",
                parameters={"text": text}, confidence=0.85, language=language
            )

        # Progress
        if any(phrase in text_lower for phrase in ["progress", "report", "activity", "what did i do", "aaj kya kiya"]):
            return Intent(action="daily_progress", tool="daily_progress", confidence=0.9, language=language)

        # Memory
        if any(phrase in text_lower for phrase in ["show memory", "memory dikhao"]):
            return Intent(action="show_memory", tool="show_memory", confidence=0.9, language=language)
        if any(phrase in text_lower for phrase in ["clear memory", "memory clear", "memory delete"]):
            return Intent(action="clear_memory", tool="clear_memory", confidence=0.9, language=language)

        # No specific intent detected — return None for AI fallback
        return None

    def _detect_language_change(self, text: str) -> Optional[Intent]:
        """Detect language change commands."""
        patterns = {
            r"speak\s+(in\s+)?english": "en",
            r"speak\s+(in\s+)?urdu": "ur",
            r"speak\s+(in\s+)?hindi": "hi",
            r"speak\s+(in\s+)?arabic": "ar",
            r"speak\s+(in\s+)?spanish": "es",
            r"speak\s+(in\s+)?french": "fr",
            r"speak\s+(in\s+)?german": "de",
            r"auto\s+language": "auto",
            r"angrezi\s+mein\s+bolo": "en",
            r"urdu\s+mein\s+bolo": "ur",
        }
        for pattern, lang in patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    action="change_language",
                    tool="change_language",
                    parameters={"language": lang},
                    confidence=0.95
                )
        return None

    def _is_greeting(self, text: str) -> bool:
        """Check if text is a greeting."""
        greetings = {
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "howdy", "greetings", "salam", "assalam", "namaste", "hola", "bonjour",
            "hallo", "kya haal", "kaise ho", "how are you", "what's up", "sup"
        }
        return text.strip().rstrip("!?.") in greetings or any(text.startswith(g) for g in greetings)
