"""Contract tests for CSS selector wait (User Story 3)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestSelectorMatch:
    """Test CSS selector wait functionality via POST endpoint."""

    async def test_wait_for_selector(self, test_client: AsyncClient):
        """Test that selector parameter waits for element to appear."""
        response = await test_client.post("/v1/html", json={"url": "https://example.com", "selector": "h1"})

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "content" in data
        assert "metadata" in data

        # Verify content contains the selector
        assert "<h1" in data["content"].lower()

    async def test_invalid_selector_syntax(self, test_client: AsyncClient):
        """Test that invalid CSS selector syntax returns 400."""
        response = await test_client.post("/v1/html", json={"url": "https://example.com", "selector": "123invalid"})

        assert response.status_code == 400
        data = response.json()

        assert "error" in data
        assert data["error"]["code"] == "INVALID_SELECTOR"

    async def test_selector_timeout_handling(self, test_client: AsyncClient):
        """Test behavior when selector never appears (timeout) - returns 404 with HTML content and error metadata."""
        response = await test_client.post(
            "/v1/html", json={"url": "https://example.com", "selector": ".nonexistent-class", "timeout": 2000}
        )

        # Should return 404 with HTML content and selector error metadata
        assert response.status_code == 404
        data = response.json()

        # Extract content and metadata from detail or direct structure
        if "detail" in data:
            detail = data["detail"]
            content = detail.get("content", "")
            metadata = detail.get("metadata", {})
        else:
            content = data.get("content", "")
            metadata = data.get("metadata", {})

        # Should have content
        assert len(content) > 0

        # Should have selector error in metadata
        assert "selector_error" in metadata
        assert ".nonexistent-class" in metadata["selector_error"]

        # Partial content flag should be set
        assert metadata.get("partial_content") is True

    async def test_conflicting_waitFor_and_selector(self, test_client: AsyncClient):
        """Test that using both waitFor=network-idle and selector returns error."""
        response = await test_client.post(
            "/v1/html", json={"url": "https://example.com", "waitFor": "network-idle", "selector": "h1"}
        )

        # Should return 422 for conflicting parameters (Pydantic validation error)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
