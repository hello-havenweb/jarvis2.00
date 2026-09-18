"""Web search tool."""

import subprocess
import webbrowser
from tools.base import BaseTool
from core.models import ToolResult
from core.logger import get_logger

logger = get_logger("browser.search")


class WebSearchTool(BaseTool):
    """Web search — opens browser with search query."""

    def execute(self, query: str = "", **kwargs) -> ToolResult:
        """Search the web."""
        if not query:
            return ToolResult(success=False, error="No search query provided.")

        try:
            import urllib.parse
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"

            # Try webbrowser module first (works without Playwright)
            webbrowser.open(search_url)
            logger.info(f"Web search: {query}")
            return ToolResult(success=True, message=f"🔍 Searching Google for: {query}")
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return ToolResult(success=False, error=f"Web search failed: {e}")
