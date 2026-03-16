from playwright_stealth import Stealth
import urllib.parse

REAL_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

_stealth = Stealth()

class BrowserSession:
    def __init__(self):
        self._pw_ctx = None
        self._playwright = None
        self._browser = None
        self._page = None

    async def start(self):
        # use_async wraps the playwright context manager so stealth
        # evasions are applied to every page opened in this session
        from playwright.async_api import async_playwright
        self._pw_ctx = _stealth.use_async(async_playwright())
        self._playwright = await self._pw_ctx.__aenter__()
        self._browser = await self._playwright.chromium.launch(headless=True)
        self._page = await self._browser.new_page(user_agent=REAL_USER_AGENT)

    async def stop(self):
        if self._browser:
            await self._browser.close()
        if self._pw_ctx:
            await self._pw_ctx.__aexit__(None, None, None)

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
