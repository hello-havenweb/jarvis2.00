"""Clipboard operations."""

from tools.base import BaseTool
from core.models import ToolResult
from core.logger import get_logger

logger = get_logger("tools.clipboard")


class ClipboardTool(BaseTool):
    """Clipboard read/write tool."""

    def execute(self, **kwargs) -> ToolResult:
        """Route to read or write."""
        action = kwargs.get("_action", "clipboard_read")
        if action == "clipboard_write":
            return self.write(kwargs.get("text", ""))
        return self.read()

    def read(self) -> ToolResult:
        """Read clipboard contents."""
        try:
            import pyperclip
            content = pyperclip.paste()
            if content:
                preview = content[:500]
                return ToolResult(success=True, message=f"📋 Clipboard: {preview}", data=content)
            return ToolResult(success=True, message="📋 Clipboard is empty.")
        except ImportError:
            return ToolResult(success=False, error="Clipboard library not available.")
        except Exception as e:
            return ToolResult(success=False, error=f"Clipboard error: {e}")

    def write(self, text: str) -> ToolResult:
        """Write to clipboard."""
        if not text:
            return ToolResult(success=False, error="No text to copy.")
        try:
            import pyperclip
            pyperclip.copy(text)
            return ToolResult(success=True, message=f"📋 Copied to clipboard: {text[:100]}...")
        except ImportError:
            return ToolResult(success=False, error="Clipboard library not available.")
        except Exception as e:
            return ToolResult(success=False, error=f"Clipboard error: {e}")
