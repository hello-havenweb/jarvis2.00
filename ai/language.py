"""Language detection for multilingual support."""

import re
from typing import Optional

from core.logger import get_logger

logger = get_logger("language")

# Unicode ranges for script detection
_ARABIC_RANGE = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
_DEVANAGARI_RANGE = re.compile(r'[\u0900-\u097F]')
_CJK_RANGE = re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF]')
_JAPANESE_RANGE = re.compile(r'[\u3040-\u309F\u30A0-\u30FF]')
_GURMUKHI_RANGE = re.compile(r'[\u0A00-\u0A7F]')

# Common Urdu/Hindi words in Roman script
_ROMAN_URDU_WORDS = {
    'karo', 'kholo', 'dikhao', 'bhejna', 'karna', 'hai', 'hain', 'mein', 'ko',
    'ka', 'ki', 'ke', 'se', 'par', 'aur', 'ya', 'nahi', 'haan', 'theek',
    'bolo', 'suno', 'dekho', 'chalo', 'ruko', 'band', 'khatam', 'shuru',
    'kal', 'aaj', 'abhi', 'yahan', 'wahan', 'kya', 'kaun', 'kahan',
    'kaise', 'kitna', 'bohot', 'zyada', 'kam', 'accha', 'bura', 'message',
    'bhejo', 'padho', 'likho', 'file', 'folder', 'ye', 'wo', 'woh',
    'bata', 'batao', 'samjha', 'samjhao', 'mujhe', 'tum', 'ap', 'aap',
}

_SPANISH_WORDS = {'hola', 'gracias', 'por', 'favor', 'como', 'estas', 'que', 'el', 'la', 'los', 'las', 'un', 'una'}
_FRENCH_WORDS = {'bonjour', 'merci', 'oui', 'non', 'je', 'tu', 'nous', 'vous', 'les', 'des', 'est', 'sont'}
_GERMAN_WORDS = {'hallo', 'danke', 'bitte', 'ich', 'du', 'wir', 'sie', 'ist', 'sind', 'das', 'ein', 'eine'}


class LanguageDetector:
    """Detect language of user input."""

    def detect(self, text: str) -> str:
        """Detect the language of the input text.

        Returns language code: en, ur, hi, ar, zh, ja, pa, es, fr, de, roman_urdu, mixed
        """
        if not text or not text.strip():
            return "en"

        text_stripped = text.strip()

        # Check for Arabic/Urdu script
        arabic_count = len(_ARABIC_RANGE.findall(text_stripped))
        if arabic_count > len(text_stripped) * 0.3:
            # Could be Arabic or Urdu — both use Arabic script
            return "ur"  # Default to Urdu for this project's context

        # Check for Devanagari (Hindi)
        if len(_DEVANAGARI_RANGE.findall(text_stripped)) > len(text_stripped) * 0.3:
            return "hi"

        # Check for CJK (Chinese)
        if len(_CJK_RANGE.findall(text_stripped)) > len(text_stripped) * 0.2:
            return "zh"

        # Check for Japanese
        if len(_JAPANESE_RANGE.findall(text_stripped)) > len(text_stripped) * 0.2:
            return "ja"

        # Check for Gurmukhi (Punjabi)
        if len(_GURMUKHI_RANGE.findall(text_stripped)) > len(text_stripped) * 0.3:
            return "pa"

        # Latin script — check for Roman Urdu/Hindi
        words = set(text_stripped.lower().split())
        roman_urdu_hits = words & _ROMAN_URDU_WORDS
        if len(roman_urdu_hits) >= 2 or (len(roman_urdu_hits) >= 1 and len(words) <= 3):
            return "roman_urdu"

        # Check other Latin-script languages
        spanish_hits = words & _SPANISH_WORDS
        if len(spanish_hits) >= 2:
            return "es"

        french_hits = words & _FRENCH_WORDS
        if len(french_hits) >= 2:
            return "fr"

        german_hits = words & _GERMAN_WORDS
        if len(german_hits) >= 2:
            return "de"

        # Check for mixed language
        if roman_urdu_hits and len(words - _ROMAN_URDU_WORDS) > 0:
            english_looking = sum(1 for w in words if w.isascii() and w not in _ROMAN_URDU_WORDS)
            if english_looking > 0 and len(roman_urdu_hits) > 0:
                return "mixed"

        return "en"
