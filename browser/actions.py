"""Browser action helpers."""

from core.logger import get_logger
from core.models import ToolResult

logger = get_logger("browser.actions")


class BrowserActions:
    """Browser interaction actions."""

    def __init__(self, manager) -> None:
        self.manager = manager

    def click(self, selector: str) -> ToolResult:
        """Click an element."""
        if not self.manager.page:
            return ToolResult(success=False, error="Browser not open.")
        try:
            self.manager.page.click(selector, timeout=10000)
            return ToolResult(success=True, message=f"Clicked: {selector}")
        except Exception as e:
            return ToolResult(success=False, error=f"Click failed: {e}")

    def fill(self, selector: str, value: str) -> ToolResult:
        """Fill a form field."""
        if not self.manager.page:
            return ToolResult(success=False, error="Browser not open.")
        try:
            self.manager.page.fill(selector, value, timeout=10000)
            return ToolResult(success=True, message=f"Filled: {selector}")
        except Exception as e:
            return ToolResult(success=False, error=f"Fill failed: {e}")

    def get_page_title(self) -> str:
        """Get current page title."""
        if not self.manager.page:
            return ""
        try:
            return self.manager.page.title()
        except Exception:
            return ""
