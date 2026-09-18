"""Text-to-speech engine abstraction."""

from typing import Optional
from core.logger import get_logger
from core.config import Config

logger = get_logger("tts")


class TTSEngine:
    """Text-to-speech engine using pyttsx3."""

    def __init__(self) -> None:
        self.config = Config()
        self._engine = None
        self._available = False
        self._speaking = False
        self._initialize()

    def _initialize(self) -> None:
        """Initialize TTS engine."""
        try:
            import pyttsx3
            self._engine = pyttsx3.init()

            # Configure
            rate = self.config.get("tts.rate", 175)
            volume = self.config.get("tts.volume", 0.9)
            self._engine.setProperty('rate', rate)
            self._engine.setProperty('volume', volume)

            self._available = True
            logger.info("TTS engine initialized.")
        except ImportError:
            logger.warning("pyttsx3 not available. TTS disabled.")
        except Exception as e:
            logger.warning(f"TTS initialization failed: {e}")

    @property
    def available(self) -> bool:
        return self._available

    @property
    def speaking(self) -> bool:
        return self._speaking

    def speak(self, text: str, language: str = "en") -> bool:
        """Speak text."""
        if not self._available or not self._engine:
            logger.info(f"TTS unavailable. Text output: {text}")
            return False

        try:
            self._speaking = True
            self._engine.say(text)
            self._engine.runAndWait()
            self._speaking = False
            return True
        except Exception as e:
            logger.error(f"TTS speak error: {e}")
            self._speaking = False
            return False

    def stop(self) -> None:
        """Stop speaking."""
        if self._engine and self._speaking:
            try:
                self._engine.stop()
            except Exception as e:
                logger.error(f"TTS stop error: {e}")
            self._speaking = False

    def set_rate(self, rate: int) -> None:
        """Set speech rate."""
        if self._engine:
            self._engine.setProperty('rate', rate)

    def set_volume(self, volume: float) -> None:
        """Set volume (0.0 to 1.0)."""
        if self._engine:
            self._engine.setProperty('volume', max(0.0, min(1.0, volume)))

    def get_voices(self) -> list:
        """Get available voices."""
        if not self._engine:
            return []
        try:
            voices = self._engine.getProperty('voices')
            return [{"id": v.id, "name": v.name, "languages": v.languages} for v in voices]
        except Exception:
            return []

    def set_voice(self, voice_id: str) -> bool:
        """Set voice by ID."""
        if not self._engine:
            return False
        try:
            self._engine.setProperty('voice', voice_id)
            return True
        except Exception as e:
            logger.error(f"Failed to set voice: {e}")
            return False
