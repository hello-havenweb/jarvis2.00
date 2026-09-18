"""Audio recording utilities."""

import io
import wave
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np

from core.logger import get_logger

logger = get_logger("audio")


class AudioRecorder:
    """Records audio from microphone."""

    def __init__(self, sample_rate: int = 16000, channels: int = 1) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self._available = False
        self._sd = None

        try:
            import sounddevice as sd
            self._sd = sd
            # Test if any input device exists
            devices = sd.query_devices()
            input_devices = [d for d in (devices if isinstance(devices, list) else [devices]) if d.get('max_input_channels', 0) > 0]
            if input_devices:
                self._available = True
                logger.info(f"Audio input available. Devices: {len(input_devices)}")
            else:
                logger.warning("No audio input devices found.")
        except Exception as e:
            logger.warning(f"Audio subsystem not available: {e}")

    @property
    def available(self) -> bool:
        return self._available

    def record(self, duration: float = 5.0) -> Optional[np.ndarray]:
        """Record audio for specified duration."""
        if not self._available or self._sd is None:
            logger.warning("Cannot record — no audio input available.")
            return None

        try:
            logger.info(f"Recording {duration}s of audio...")
            audio = self._sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32'
            )
            self._sd.wait()
            logger.info("Recording complete.")
            return audio.flatten()
        except Exception as e:
            logger.error(f"Recording failed: {e}")
            return None

    def save_wav(self, audio: np.ndarray, path: Optional[Path] = None) -> Optional[Path]:
        """Save audio array to WAV file."""
        if path is None:
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            path = Path(tmp.name)
            tmp.close()

        try:
            audio_int16 = (audio * 32767).astype(np.int16)
            with wave.open(str(path), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_int16.tobytes())
            return path
        except Exception as e:
            logger.error(f"Failed to save WAV: {e}")
            return None
