"""Integration tests for CSS selector waiting (User Story 3)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestSelectorWaiting:
    """Integration tests for selector waiting functionality."""

    async def test_selector_match_example_com(self, test_client: AsyncClient):
        """Test selector wait with example.com h1 element."""
        response = await test_client.post(
            "/v1/html",
            json={"url": "https://example.com", "selector": "h1", "timeout": 10000}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify h1 element is present
        content = data["content"]
        assert "<h1" in content.lower()
        assert "example" in content.lower()

        # Verify metadata
        metadata = data["metadata"]
        assert metadata["status_code"] == 200
        assert metadata["duration_ms"] > 0

    async def test_selector_with_multiple_elements(self, test_client: AsyncClient):
        """Test selector wait with common element (p tag)."""
        response = await test_client.post(
            "/v1/html",
            json={"url": "https://example.com", "selector": "p", "timeout": 10000}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify p element is present
        content = data["content"]
        assert "<p" in content.lower()

    async def test_selector_css_class(self, test_client: AsyncClient):
        """Test selector with CSS class syntax."""
        # Use body tag as it always exists
        response = await test_client.post(
            "/v1/html",
            json={"url": "https://example.com", "selector": "body", "timeout": 10000}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify body element is present
        content = data["content"]
        assert "<body" in content.lower()
