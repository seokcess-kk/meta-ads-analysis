import asyncio
import logging
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

# Local storage path for screenshots
SCREENSHOT_DIR = Path("/app/static/screenshots")


class ScreenshotService:
    """Service for capturing screenshots of ad pages."""

    def __init__(self):
        self._browser = None
        self._playwright = None

    async def _ensure_browser(self):
        """Ensure browser is initialized."""
        if self._browser is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

    async def capture_ad_screenshot(
        self,
        render_url: str,
        ad_id: str,
        width: int = 400,
        height: int = 400,
    ) -> Optional[str]:
        """
        Capture screenshot of an ad render page.

        Args:
            render_url: The render_ad URL from Meta
            ad_id: Ad ID for filename
            width: Screenshot width
            height: Screenshot height

        Returns:
            Local path to the screenshot or None if failed
        """
        try:
            await self._ensure_browser()

            # Create screenshot directory if not exists
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

            # Create new page
            page = await self._browser.new_page(
                viewport={'width': width, 'height': height}
            )

            try:
                # Navigate to the render URL
                await page.goto(render_url, wait_until='networkidle', timeout=30000)

                # Wait a bit for any animations
                await asyncio.sleep(1)

                # Generate filename
                filename = f"{ad_id}.png"
                filepath = SCREENSHOT_DIR / filename

                # Take screenshot
                await page.screenshot(path=str(filepath), full_page=False)

                logger.info(f"Screenshot captured for ad {ad_id}")
                return f"/static/screenshots/{filename}"

            finally:
                await page.close()

        except Exception as e:
            logger.error(f"Failed to capture screenshot for ad {ad_id}: {e}")
            return None

    async def close(self):
        """Close browser instance."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None


# Singleton instance
screenshot_service = ScreenshotService()


async def capture_screenshot(render_url: str, ad_id: str) -> Optional[str]:
    """Convenience function to capture screenshot."""
    return await screenshot_service.capture_ad_screenshot(render_url, ad_id)
