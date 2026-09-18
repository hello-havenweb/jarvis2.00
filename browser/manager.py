"""Browser automation manager using Playwright."""

from typing import Optional
from core.logger import get_logger
from core.config import Config
from core.exceptions import BrowserError

logger = get_logger("browser")


class BrowserManager:
    """Manages browser automation via Playwright."""

    def __init__(self) -> None:
        self.config = Config()
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._available = False

    def is_available(self) -> bool:
        """Check if Playwright is available."""
        try:
            from playwright.sync_api import sync_playwright
            return True
        except ImportError:
            return False

    def start(self) -> bool:
        """Start the browser."""
        try:
            from playwright.sync_api import sync_playwright

            self._playwright = sync_playwright().start()
            headless = self.config.get("browser.headless", False)
            self._browser = self._playwright.chromium.launch(headless=headless)
            self._context = self._browser.new_context()
            self._page = self._context.new_page()
            self._available = True
            logger.info("Browser started successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            self._available = False
            return False

    def stop(self) -> None:
        """Stop the browser."""
        try:
            if self._page:
                self._page.close()
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")
        finally:
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None
            self._available = False

    @property
    def page(self):
        """Get current page."""
        return self._page

    @property
    def available(self) -> bool:
        return self._available

    def navigate(self, url: str) -> bool:
        """Navigate to a URL."""
        if not self._available or not self._page:
            if not self.start():
                return False

        try:
            self._page.goto(url, wait_until="domcontentloaded", timeout=30000)
            logger.info(f"Navigated to: {url}")
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False

    def get_text(self) -> str:
        """Get page text content."""
        if not self._page:
            return ""
        try:
            return self._page.inner_text("body")
        except Exception:
            return ""

    def screenshot(self, path: str) -> bool:
        """Take a screenshot of the current page."""
        if not self._page:
            return False
        try:
            self._page.screenshot(path=path)
            return True
        except Exception as e:
            logger.error(f"Browser screenshot failed: {e}")
            return False
