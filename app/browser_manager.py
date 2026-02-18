import asyncio
from playwright.async_api import async_playwright, Page, Browser
from app.config import CHATBOT_URL, CHATBOT_EMAIL, CHATBOT_PASSWORD, SELECTORS, CHATBOT_TARGET


class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.page: Page = None
        self.lock = asyncio.Lock()

    async def start(self):
        """Launch the headless browser and log in once when the server starts."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await self.browser.new_context()
        self.page = await context.new_page()

        await self.page.goto(CHATBOT_URL)
        await self._login()

    async def _login(self):
        """Log in using the selectors defined for the active chatbot."""
        login = SELECTORS["login"]
        try:
            await self.page.wait_for_selector(login["email_field"], timeout=5000)
            await self.page.fill(login["email_field"], CHATBOT_EMAIL)
            await self.page.click(login["submit_button"])

            await self.page.wait_for_selector(login["password_field"], timeout=5000)
            await self.page.fill(login["password_field"], CHATBOT_PASSWORD)
            await self.page.click(login["submit_button"])

            await self.page.wait_for_selector(SELECTORS["input_box"], timeout=15000)
        except Exception:
            # Already logged in, or no login page appeared
            pass

    async def send_message(self, message: str) -> str:
        """Type a message into the chatbot UI and return the response."""
        async with self.lock:
            input_box = self.page.locator(SELECTORS["input_box"])
            await input_box.click()
            await input_box.fill(message)
            await self.page.click(SELECTORS["send_button"])

            # Wait for response to finish streaming
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
        await self.browser.close()
        await self.playwright.stop()
