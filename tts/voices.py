"""Voice management for TTS."""

from typing import List, Dict, Optional
from core.logger import get_logger

logger = get_logger("voices")


def get_available_voices() -> List[Dict]:
    """Get list of available TTS voices."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        result = []
        for v in voices:
            result.append({
                "id": v.id,
                "name": v.name,
                "languages": getattr(v, 'languages', []),
                "gender": getattr(v, 'gender', 'unknown'),
            })
        engine.stop()
        return result
    except Exception as e:
        logger.warning(f"Cannot get voices: {e}")
        return []


def find_voice_for_language(language: str) -> Optional[str]:
    """Find a suitable voice for the given language."""
    voices = get_available_voices()
    if not voices:
        return None

    language_lower = language.lower()

    # Language code mapping
    lang_map = {
        "en": ["english", "en-us", "en-gb", "en_us", "en_gb"],
        "ur": ["urdu", "ur"],
        "hi": ["hindi", "hi"],
        "ar": ["arabic", "ar"],
        "es": ["spanish", "es"],
        "fr": ["french", "fr"],
        "de": ["german", "de"],
        "zh": ["chinese", "zh"],
        "ja": ["japanese", "ja"],
    }

    search_terms = lang_map.get(language_lower, [language_lower])

    for voice in voices:
        voice_name = voice["name"].lower()
        for term in search_terms:
            if term in voice_name:
                return voice["id"]

    # Default to first available voice
    if voices:
        return voices[0]["id"]

    return None
