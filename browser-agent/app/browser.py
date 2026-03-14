from playwright.async_api import async_playwright
import urllib.parse

class BrowserSession:
    def __init__(self):
        self._playwright = None
        self._browser = None
        self._page = None

    async def start(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        self._page = await self._browser.new_page()

    async def stop(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def navigate(self, url: str) -> str:
        await self._page.goto(url)
        title = await self._page.title()
        return f"Navigated to {url}. Page title: {title}"

    async def extract_text(self) -> str:
        text = await self._page.inner_text("body")
        return text[:8000]

    async def click(self, selector: str) -> str:
        await self._page.click(selector)
        return f"Clicked {selector}"

    async def type_text(self, selector: str, text: str) -> str:
        await self._page.fill(selector, text)
        return f"Typed into {selector}"

    async def search(self, query: str) -> str:
        encoded = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        await self._page.goto(url)
        text = await self._page.inner_text("body")
        return text[:8000]
