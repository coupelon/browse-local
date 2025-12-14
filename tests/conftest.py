"""Pytest configuration and shared fixtures."""

import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock

from src.core.browser import BrowserSession


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_client():
    """Fixture providing HTTP test client with session-scoped browser."""
    # Import here to ensure proper initialization
    from src.api.main import app

    # Start browser session once for all tests
    browser = await BrowserSession.get_instance()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        timeout=60.0,  # Increase timeout for browser operations
    ) as client:
        yield client

    # Cleanup browser after all tests
    await browser.shutdown()


@pytest.fixture
def mock_browser_session():
    """Fixture providing mock BrowserSession."""
    mock_session = MagicMock(spec=BrowserSession)
    mock_session.is_ready.return_value = True

    # Mock new_page context manager
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_load_state = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()
    mock_page.content = AsyncMock(return_value="<html><body>Test content</body></html>")

    # Setup context manager behavior
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_page)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)
    mock_session.new_page.return_value = mock_context_manager

    return mock_session


@pytest.fixture
def mock_page():
    """Fixture providing mock Playwright Page."""
    page = AsyncMock()
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.wait_for_selector = AsyncMock()
    page.content = AsyncMock(return_value="<html><body>Test content</body></html>")
    page.url = "https://example.com"

    # Mock response
    mock_response = MagicMock()
    mock_response.status = 200
    page.goto.return_value = mock_response

    return page


@pytest.fixture
def sample_html() -> str:
    """Fixture providing sample HTML content."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Page</title>
</head>
<body>
    <div class="content">
        <h1>Hello World</h1>
        <p>This is a test page.</p>
    </div>
</body>
</html>
""".strip()


@pytest.fixture
def valid_url() -> str:
    """Fixture providing valid test URL."""
    return "https://example.com"


@pytest.fixture
def valid_html_request() -> dict:
    """Fixture providing valid HtmlRequest data."""
    return {"url": "https://example.com", "waitFor": "none", "timeout": 30000}
