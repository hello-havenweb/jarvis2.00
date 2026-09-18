"""Wake word detection for JARVIS."""

import re
from typing import Optional
from core.logger import get_logger

logger = get_logger("wakeword")


class WakeWordDetector:
    """Simple wake word detection from transcribed text."""

    def __init__(self, wake_words: Optional[list] = None) -> None:
        self.wake_words = wake_words or ["jarvis", "hey jarvis"]
        self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, val: bool) -> None:
        self._enabled = val

    def check(self, text: str) -> Optional[str]:
        """Check if wake word is present and return the command after it.

        Returns the command text (without wake word) if detected, else None.
        """
        if not self._enabled:
            return text  # If disabled, all text is a command

        text_lower = text.lower().strip()

        for ww in sorted(self.wake_words, key=len, reverse=True):
            pattern = re.compile(rf"^{re.escape(ww)}[\s,!.]*(.*)$", re.IGNORECASE)
            match = pattern.match(text_lower)
            if match:
                command = match.group(1).strip()
                if command:
                    logger.info(f"Wake word '{ww}' detected. Command: {command}")
                    return command
                else:
                    logger.info(f"Wake word '{ww}' detected but no command followed.")
                    return ""

        return None  # Wake word not found
