"""Pytest configuration and shared fixtures."""
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock

from src.api.main import app
from src.core.browser import BrowserSession


@pytest.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """Fixture providing HTTP test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


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
    return {
        "url": "https://example.com",
        "waitFor": "none",
        "timeout": 30000
    }
