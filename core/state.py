"""Application state management."""

from core.models import JarvisState
from core.events import event_bus
from core.logger import get_logger

logger = get_logger("state")


class AppState:
    """Manages JARVIS application state."""

    def __init__(self) -> None:
        self._state: JarvisState = JarvisState.IDLE
        self._previous_state: JarvisState = JarvisState.IDLE
        self._language: str = "en"
        self._voice_enabled: bool = False
        self._tts_enabled: bool = False
        self._ollama_connected: bool = False
        self._first_run: bool = False

    @property
    def state(self) -> JarvisState:
        return self._state

    @state.setter
    def state(self, new_state: JarvisState) -> None:
        if new_state != self._state:
            self._previous_state = self._state
            self._state = new_state
            logger.debug(f"State: {self._previous_state.value} -> {new_state.value}")
            event_bus.publish("state_changed", state=new_state, previous=self._previous_state)

    @property
    def language(self) -> str:
        return self._language

    @language.setter
    def language(self, lang: str) -> None:
        self._language = lang
        event_bus.publish("language_changed", language=lang)

    @property
    def voice_enabled(self) -> bool:
        return self._voice_enabled

    @voice_enabled.setter
    def voice_enabled(self, val: bool) -> None:
        self._voice_enabled = val

    @property
    def tts_enabled(self) -> bool:
        return self._tts_enabled

    @tts_enabled.setter
    def tts_enabled(self, val: bool) -> None:
        self._tts_enabled = val

    @property
    def ollama_connected(self) -> bool:
        return self._ollama_connected

    @ollama_connected.setter
    def ollama_connected(self, val: bool) -> None:
        self._ollama_connected = val

    @property
    def first_run(self) -> bool:
        return self._first_run

    @first_run.setter
    def first_run(self, val: bool) -> None:
        self._first_run = val
