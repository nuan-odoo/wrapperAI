import asyncio
from playwright.async_api import async_playwright, Page, Browser
from app.config import CHATBOT_URL, CHATBOT_EMAIL, CHATBOT_PASSWORD, SELECTORS


class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.page: Page = None
        # Lock prevents two requests from typing at the same time
        self.lock = asyncio.Lock()

    async def start(self):
        """Launch the headless browser and log in once when the server starts."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]  # Required inside Docker
        )
        context = await self.browser.new_context()
        self.page = await context.new_page()

        await self.page.goto(CHATBOT_URL)
        await self._login()

    async def _login(self):
        """Log in to the chatbot. Skips gracefully if already logged in."""
        try:
            await self.page.wait_for_selector('input[type="email"]', timeout=5000)
            await self.page.fill('input[type="email"]', CHATBOT_EMAIL)
            await self.page.fill('input[type="password"]', CHATBOT_PASSWORD)
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_selector(SELECTORS["input_box"], timeout=15000)
        except Exception:
            # Already logged in via saved session, or no login page appeared
            pass

    async def send_message(self, message: str) -> str:
        """
        The core of WrapperAI:
        1. Types your message into the chatbot UI
        2. Clicks send
        3. Waits for the response to finish streaming
        4. Returns the response text
        """
        async with self.lock:
            # Type the message
            input_box = self.page.locator(SELECTORS["input_box"])
            await input_box.click()
            await input_box.fill(message)

            # Click send
            await self.page.click(SELECTORS["send_button"])

            # Wait for the response to appear and stop changing (streaming finished)
            last_text = ""
            stable_count = 0

            while stable_count < 3:
                await asyncio.sleep(1)
                try:
                    elements = self.page.locator(SELECTORS["response"])
                    count = await elements.count()
                    if count == 0:
                        continue
                    current_text = await elements.last.inner_text()
                    if current_text == last_text and current_text != "":
                        stable_count += 1
                    else:
                        stable_count = 0
                        last_text = current_text
                except Exception:
                    continue

            return last_text

    async def stop(self):
        """Clean up the browser when the server shuts down."""
        await self.browser.close()
        await self.playwright.stop()
