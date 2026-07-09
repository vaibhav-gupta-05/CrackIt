import asyncio
import logging
from typing import AsyncGenerator

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from config import get_settings

logger = logging.getLogger(__name__)


class BrowserManager:
    """
    Manages the lifecycle of a Playwright headless browser session.
    Implements anti-detection strategies to improve scraping reliability.
    Designed to be used as an async context manager.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    async def __aenter__(self) -> "BrowserManager":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()

    async def start(self) -> None:
        """Launches the browser with stealth configurations."""
        logger.debug("Starting Playwright browser instance...")
        self._playwright = await async_playwright().start()
        
        self._browser = await self._playwright.chromium.launch(
            headless=self.settings.scraper_headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ]
        )
        
        # Create a context that looks like a real user
        self._context = await self._browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1,
            has_touch=False,
            is_mobile=False,
            locale="en-US",
            timezone_id="America/New_York",
        )
        
        # Mask webdriver flag
        await self._context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        logger.debug("Browser context initialized successfully.")

    async def stop(self) -> None:
        """Cleanly shuts down all browser resources."""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.debug("Browser resources cleaned up.")

    async def new_page(self) -> Page:
        """Returns a new tab within the configured context."""
        if not self._context:
            raise RuntimeError("Browser context not started. Use 'async with BrowserManager():' or call start()")
        return await self._context.new_page()

    async def fetch_html(self, url: str) -> str:
        """Helper to simply fetch HTML if you don't need to interact."""
        page = await self.new_page()
        try:
            # Wait for network to be idle to ensure dynamic content loads
            await page.goto(url, wait_until="networkidle")
            # Wait an additional configured delay just to be safe from rate limits
            await asyncio.sleep(self.settings.scraper_delay_ms / 1000.0)
            return await page.content()
        except Exception as e:
            logger.error(f"Failed to fetch HTML for {url}: {e}")
            raise
        finally:
            await page.close()
