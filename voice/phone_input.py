"""Phone input support — placeholder for future phone-as-microphone feature."""

from core.logger import get_logger

logger = get_logger("phone_input")


class PhoneInput:
    """Handles phone-as-microphone input (future feature)."""

    def __init__(self) -> None:
        self._available = False
        logger.info("Phone input module loaded (not yet implemented in this release).")

    @property
    def available(self) -> bool:
        return self._available

    def start_server(self) -> bool:
        """Start a local server for phone audio streaming."""
        logger.info("Phone input server is not available in this release.")
        return False

    def stop_server(self) -> None:
        """Stop the phone input server."""
        logger.info("Phone input server stopped.")
