"""Audio device detection and management."""

from typing import List, Dict, Optional
from core.logger import get_logger

logger = get_logger("devices")


def list_audio_devices() -> List[Dict]:
    """List available audio devices."""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        if not isinstance(devices, list):
            devices = [devices]
        result = []
        for i, d in enumerate(devices):
            result.append({
                "index": i,
                "name": d.get("name", "Unknown"),
                "max_input_channels": d.get("max_input_channels", 0),
                "max_output_channels": d.get("max_output_channels", 0),
                "default_samplerate": d.get("default_samplerate", 0),
            })
        return result
    except Exception as e:
        logger.warning(f"Cannot list audio devices: {e}")
        return []


def get_default_input_device() -> Optional[Dict]:
    """Get the default input device."""
    try:
        import sounddevice as sd
        idx = sd.default.device[0]
        if idx is not None and idx >= 0:
            info = sd.query_devices(idx)
            return {
                "index": idx,
                "name": info.get("name", "Unknown"),
                "max_input_channels": info.get("max_input_channels", 0),
            }
    except Exception as e:
        logger.debug(f"No default input device: {e}")
    return None


def has_microphone() -> bool:
    """Check if a microphone is available."""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        if not isinstance(devices, list):
            devices = [devices]
        return any(d.get("max_input_channels", 0) > 0 for d in devices)
    except Exception:
        return False
