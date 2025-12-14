"""Unit tests for selector error handling - HTML should be returned via exception."""

import asyncio
import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from src.core.renderer import PageRenderer
from src.core.browser import BrowserSession
from src.api.errors import SelectorNotFoundWithContentError


class MockPageWithTimeout:
    """Mock page that simulates selector timeout."""

    def __init__(self, html_content="<html><body><h1>Page Content</h1></body></html>"):
        self._content = html_content
        self.url = "https://example.com"

    async def goto(self, url, timeout=None, wait_until=None):
        await asyncio.sleep(0)

        class Response:
            status = 200

        return Response()

    async def wait_for_load_state(self, state, timeout=None):
        await asyncio.sleep(0)

    async def wait_for_selector(self, selector, timeout=None):
        """Simulate selector timeout."""
        await asyncio.sleep(0)
        raise PlaywrightTimeoutError(f"Timeout {timeout}ms exceeded")

    async def content(self):
        return self._content


class MockPageSuccess:
    """Mock page with successful selector."""

    def __init__(self, html_content="<html><body><div class='target'>Found</div></body></html>"):
        self._content = html_content
        self.url = "https://example.com"

    async def goto(self, url, timeout=None, wait_until=None):
        await asyncio.sleep(0)

        class Response:
            status = 200

        return Response()

    async def wait_for_load_state(self, state, timeout=None):
        await asyncio.sleep(0)

    async def wait_for_selector(self, selector, timeout=None):
        """Selector found successfully."""
        await asyncio.sleep(0)
        return None

    async def content(self):
        return self._content


class MockBrowserSession(BrowserSession):
    """Mock browser session for testing."""

    def __init__(self, page_mock):
        # Don't call super().__init__() to avoid real browser initialization
        self._page_mock = page_mock

    def new_page(self, user_agent=None):
        class _Page:
            def __init__(self_inner, page):
                self_inner._page = page

            async def __aenter__(self_inner):
                return self_inner._page

            async def __aexit__(self_inner, exc_type, exc, tb):
                return False

        return _Page(self._page_mock)


@pytest.mark.asyncio
async def test_render_returns_html_when_selector_not_found():
    """Test that SelectorNotFoundWithContentError is raised with HTML content when selector times out."""
    # Setup
    mock_page = MockPageWithTimeout("<html><body><h1>Debug Content</h1></body></html>")
    mock_session = MockBrowserSession(mock_page)
    renderer = PageRenderer(mock_session)

    # Execute and expect exception
    with pytest.raises(SelectorNotFoundWithContentError) as exc_info:
        await renderer.render(url="https://example.com", selector=".non-existent-selector", timeout=5000)

    # Assert: Exception should contain HTML content
    exception = exc_info.value
    assert exception.html_content == "<html><body><h1>Debug Content</h1></body></html>"

    # Assert: Metadata should indicate selector error
    assert "selector_error" in exception.metadata
    assert ".non-existent-selector" in exception.metadata["selector_error"]

    # Assert: Partial content flag should be set
    assert exception.metadata["partial_content"] is True


@pytest.mark.asyncio
async def test_render_successful_with_selector():
    """Test that normal selector behavior still works."""
    # Setup
    mock_page = MockPageSuccess("<html><body><div class='target'>Found</div></body></html>")
    mock_session = MockBrowserSession(mock_page)
    renderer = PageRenderer(mock_session)

    # Execute
    html_content, metadata = await renderer.render(url="https://example.com", selector=".target", timeout=5000)

    # Assert: HTML content returned
    assert html_content == "<html><body><div class='target'>Found</div></body></html>"

    # Assert: No selector error in metadata
    assert "selector_error" not in metadata
    assert "partial_content" not in metadata


@pytest.mark.asyncio
async def test_render_without_selector():
    """Test render without selector (no wait condition)."""
    # Setup
    mock_page = MockPageSuccess("<html><body><p>Simple page</p></body></html>")
    mock_session = MockBrowserSession(mock_page)
    renderer = PageRenderer(mock_session)

    # Execute
    html_content, metadata = await renderer.render(url="https://example.com", selector=None)

    # Assert: HTML content returned
    assert html_content == "<html><body><p>Simple page</p></body></html>"

    # Assert: No selector-related metadata
    assert "selector_error" not in metadata
    assert "partial_content" not in metadata
    assert metadata["wait_strategy"] == "none"
