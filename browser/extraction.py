"""Web page content extraction."""

from typing import Optional
from core.logger import get_logger

logger = get_logger("browser.extraction")


class ContentExtractor:
    """Extract content from web pages."""

    def extract_text(self, page) -> str:
        """Extract visible text from a page."""
        try:
            return page.inner_text("body")
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""

    def extract_links(self, page) -> list:
        """Extract links from a page."""
        try:
            links = page.eval_on_selector_all(
                "a[href]",
                "elements => elements.map(e => ({text: e.innerText.trim(), href: e.href})).filter(l => l.text && l.href)"
            )
            return links[:50]  # Limit
        except Exception as e:
            logger.error(f"Link extraction failed: {e}")
            return []

    def extract_title(self, page) -> str:
        """Extract page title."""
        try:
            return page.title()
        except Exception:
            return ""
