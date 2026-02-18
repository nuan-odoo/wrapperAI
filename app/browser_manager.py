import asyncio
from playwright.async_api import async_playwright, Page, Browser
from app.config import CHATBOT_CONFIGS


class BrowserManager:
    def __init__(self):
        self.playwright  = None
        self.browser: Browser = None
        self.page: Page  = None
        self.lock        = asyncio.Lock()
        self.is_ready    = False
        self.active_bot  = None

    async def start(self, target: str, cookies: list = None, email: str = None, password: str = None):
        """
        Launch the browser and authenticate using either cookies or email/password.
        Called once from the /setup endpoint after the user completes the GUI form.
        """
        config = CHATBOT_CONFIGS[target]
        self.active_bot = target

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await self.browser.new_context()

        # Inject cookies before navigating (cookie-based auth like Claude)
if config["auth"] == "cookie" and cookies:
    # Sanitize sameSite values — Playwright only accepts Strict, Lax, or None
    sameSite_map = {
        "no_restriction": "None",
        "unspecified":    "None",
        "strict":         "Strict",
        "lax":            "Lax",
        "none":           "None",
    }
    cleaned = []
    for cookie in cookies:
        c = dict(cookie)
        raw = str(c.get("sameSite", "Lax")).lower()
        c["sameSite"] = sameSite_map.get(raw, "Lax")
        # Remove keys Playwright doesn't accept
        for key in ["storeId", "hostOnly", "session"]:
            c.pop(key, None)
        cleaned.append(c)
    await context.add_cookies(cleaned)

        self.page = await context.new_page()
        await self.page.goto(config["url"])

        # Password-based auth (ChatGPT, Gemini)
        if config["auth"] == "password" and email and password:
            await self._login(config, email, password)

        # Wait for the chat input to confirm we're logged in
        await self.page.wait_for_selector(config["input_box"], timeout=20000)
        self.is_ready = True

    async def _login(self, config: dict, email: str, password: str):
        """Handle email/password login flow."""
        login = config["login"]
        try:
            await self.page.wait_for_selector(login["email_field"], timeout=5000)
            await self.page.fill(login["email_field"], email)
            await self.page.click(login["submit_button"])

            await self.page.wait_for_selector(login["password_field"], timeout=5000)
            await self.page.fill(login["password_field"], password)
            await self.page.click(login["submit_button"])
        except Exception:
            pass

    async def send_message(self, message: str) -> str:
        """
        Core shadow API method — types into the GUI and captures the response.
        """
        if not self.is_ready:
            raise RuntimeError("Browser session not ready. Complete setup first.")

        config = CHATBOT_CONFIGS[self.active_bot]

        async with self.lock:
            input_box = self.page.locator(config["input_box"])
            await input_box.click()
            await input_box.fill(message)
            await self.page.click(config["send_button"])

            last_text    = ""
            stable_count = 0

            while stable_count < 3:
                await asyncio.sleep(1)
                try:
                    elements     = self.page.locator(config["response"])
                    count        = await elements.count()
                    if count == 0:
                        continue
                    current_text = await elements.last.inner_text()
                    if current_text == last_text and current_text != "":
                        stable_count += 1
                    else:
                        stable_count = 0
                        last_text    = current_text
                except Exception:
                    continue

            return last_text

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
