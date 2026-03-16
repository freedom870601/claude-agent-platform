import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_page():
    page = AsyncMock()
    page.title = AsyncMock(return_value="Test Page")
    page.inner_text = AsyncMock(return_value="Hello world " * 1000)
    page.click = AsyncMock()
    page.fill = AsyncMock()
    page.goto = AsyncMock()
    return page

@pytest.fixture
def mock_browser(mock_page):
    browser = AsyncMock()
    browser.new_page = AsyncMock(return_value=mock_page)
    return browser

@pytest.fixture
def mock_playwright(mock_browser):
    playwright = AsyncMock()
    playwright.chromium.launch = AsyncMock(return_value=mock_browser)
    return playwright

@pytest.fixture
async def session(mock_playwright, mock_page, mock_browser):
    from app.browser import BrowserSession
    # Mock _stealth.use_async to return an async context manager yielding mock_playwright
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_playwright)
    mock_ctx.__aexit__ = AsyncMock(return_value=None)
    with patch("app.browser._stealth.use_async", return_value=mock_ctx):
        s = BrowserSession()
        s._playwright = mock_playwright
        s._browser = mock_browser
        s._page = mock_page
        yield s

@pytest.mark.asyncio
async def test_navigate(session):
    result = await session.navigate("https://example.com")
    assert "https://example.com" in result
    assert "Test Page" in result

@pytest.mark.asyncio
async def test_extract_text_truncated(session):
    result = await session.extract_text()
    assert len(result) <= 8000

@pytest.mark.asyncio
async def test_click(session):
    result = await session.click("#button")
    assert "#button" in result

@pytest.mark.asyncio
async def test_type_text(session):
    result = await session.type_text("#input", "hello")
    assert "#input" in result

@pytest.mark.asyncio
async def test_search(session):
    result = await session.search("python version")
    assert isinstance(result, str)
    assert len(result) <= 8000
