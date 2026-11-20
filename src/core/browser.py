"""Playwright browser session management."""

import asyncio
from typing import Optional
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from src.core.logger import get_logger
from src.api.errors import BrowserError

logger = get_logger(__name__)


def build_default_user_agent(browser_version: str) -> str:
    """Build a desktop Chrome on Linux User-Agent for the given Chromium version.

    Chrome's reduced UA only exposes the major version (e.g. "Chrome/140.0.0.0").
    """
    major = browser_version.split(".")[0]
    return (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        f"(KHTML, like Gecko) Chrome/{major}.0.0.0 Safari/537.36"
    )


class BrowserSession:
    """Singleton browser session manager using Playwright."""

    _instance: Optional["BrowserSession"] = None
    _lock = asyncio.Lock()

    def __init__(self):
        """Initialize browser session (use get_instance instead)."""
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._default_user_agent: Optional[str] = None
        self._initialized = False

    @classmethod
    async def get_instance(cls) -> "BrowserSession":
        """Get singleton instance (thread-safe)."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance.initialize()
        return cls._instance

    async def initialize(self) -> None:
        """Initialize Playwright and launch browser."""
        if self._initialized:
            return

        try:
            logger.info("Initializing Playwright browser session")
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                # Full Chromium in new headless mode instead of the stripped-down
                # headless shell: client hints then report "Chromium" brands,
                # consistent with the default User-Agent below.
                channel="chromium",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                ],
            )
            self._default_user_agent = build_default_user_agent(self._browser.version)
            self._initialized = True
            logger.info(
                f"Browser session initialized successfully "
                f"(Chromium {self._browser.version}, default UA: {self._default_user_agent})"
            )
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise BrowserError(f"Failed to initialize browser: {e}")

    async def shutdown(self) -> None:
        """Shutdown browser and Playwright."""
        if not self._initialized:
            return

        try:
            logger.info("Shutting down browser session")
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            self._initialized = False
            logger.info("Browser session shutdown complete")
        except Exception as e:
            logger.error(f"Error during browser shutdown: {e}")

    @asynccontextmanager
    async def new_context(self, user_agent: Optional[str] = None):
        """Create a new browser context (isolated session)."""
        if not self._initialized or not self._browser:
            logger.error("Browser not initialized")
            raise BrowserError("Browser not initialized")

        context: Optional[BrowserContext] = None
        try:
            logger.debug(f"Creating new browser context (user_agent={bool(user_agent)})")
            # Without an explicit UA, use a regular desktop Chrome/Linux UA
            # matching the embedded Chromium version (the built-in one
            # advertises "HeadlessChrome").
            context_options = {"user_agent": user_agent or self._default_user_agent}
            if user_agent:
                logger.debug("Custom user agent set in context")

            context = await self._browser.new_context(**context_options)
            logger.debug("Browser context created successfully")
            yield context
        finally:
            if context:
                try:
                    await context.close()
                    logger.debug("Browser context closed")
                except Exception as e:
                    logger.error(f"Error closing context: {e}", exc_info=True)

    @asynccontextmanager
    async def new_page(self, user_agent: Optional[str] = None):
        """Create a new page in a new context."""
        logger.debug(f"Creating new browser page (user_agent={bool(user_agent)})")
        async with self.new_context(user_agent=user_agent) as context:
            page: Optional[Page] = None
            try:
                page = await context.new_page()
                logger.debug("Browser page created successfully")
                yield page
            finally:
                if page:
                    try:
                        await page.close()
                        logger.debug("Browser page closed")
                    except Exception as e:
                        logger.error(f"Error closing page: {e}", exc_info=True)

    def is_ready(self) -> bool:
        """Check if browser is ready."""
        return self._initialized and self._browser is not None
