"""Speech-to-text using faster-whisper."""

from typing import Optional
from core.logger import get_logger
from core.config import Config

logger = get_logger("stt")


class SpeechToText:
    """Speech-to-text engine using faster-whisper."""

    def __init__(self) -> None:
        self.config = Config()
        self._model = None
        self._available = False
        self._initialize()

    def _initialize(self) -> None:
        """Try to initialize faster-whisper."""
        try:
            from faster_whisper import WhisperModel
            model_size = self.config.stt_model
            logger.info(f"Loading Whisper model: {model_size}")
            self._model = WhisperModel(model_size, device="cpu", compute_type="int8")
            self._available = True
            logger.info("Speech-to-text initialized successfully.")
        except ImportError:
            logger.warning("faster-whisper not available. Voice input disabled.")
            self._available = False
        except Exception as e:
            logger.warning(f"Failed to initialize STT: {e}")
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    def transcribe(self, audio_path: str) -> Optional[str]:
        """Transcribe audio file to text."""
        if not self._available or self._model is None:
            logger.warning("STT not available.")
            return None

        try:
            segments, info = self._model.transcribe(audio_path, beam_size=5)
            text = " ".join(seg.text for seg in segments).strip()
            logger.info(f"Transcribed ({info.language}): {text[:100]}")
            return text
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None

    def transcribe_array(self, audio_array, sample_rate: int = 16000) -> Optional[str]:
        """Transcribe numpy audio array to text."""
        if not self._available or self._model is None:
            return None

        try:
            segments, info = self._model.transcribe(audio_array, beam_size=5)
            text = " ".join(seg.text for seg in segments).strip()
            return text
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
