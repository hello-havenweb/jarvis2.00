"""Screenshot tool."""

from datetime import datetime
from pathlib import Path

from tools.base import BaseTool
from core.models import ToolResult
from core.config import Config
from core.logger import get_logger

logger = get_logger("tools.screenshot")


class ScreenshotTool(BaseTool):
    """Take screenshots."""

    def execute(self, **kwargs) -> ToolResult:
        """Take a screenshot."""
        try:
            from PIL import ImageGrab

            config = Config()
            save_dir = config.data_dir / "screenshots"
            save_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = save_dir / filename

            screenshot = ImageGrab.grab()
            screenshot.save(str(filepath))

            logger.info(f"Screenshot saved: {filepath}")
            return ToolResult(
                success=True,
                message=f"📸 Screenshot saved: {filepath}",
                data=str(filepath)
            )
        except ImportError:
            return ToolResult(success=False, error="Pillow library not available for screenshots.")
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return ToolResult(success=False, error=f"Screenshot failed: {e}")
