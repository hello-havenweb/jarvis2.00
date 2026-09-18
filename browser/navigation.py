"""Browser navigation utilities."""

from core.logger import get_logger
from core.models import ToolResult
from browser.manager import BrowserManager

logger = get_logger("browser.navigation")


class BrowserNavigator:
    """Navigate browser to URLs."""

    def __init__(self, manager: Optional["BrowserManager"] = None) -> None:
        from browser.manager import BrowserManager as BM
        self.manager = manager or BM()

    def open_url(self, url: str) -> ToolResult:
        """Open a URL in the browser."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            if self.manager.navigate(url):
                return ToolResult(success=True, message=f"🌐 Opened: {url}")
            return ToolResult(success=False, error=f"Failed to open: {url}")
        except Exception as e:
            return ToolResult(success=False, error=f"Navigation error: {e}")
