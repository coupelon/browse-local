"""Integration tests for real website fetching (User Story 1)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRealWebsite:
    """Integration tests with real websites."""

    async def test_fetch_example_com(self, test_client: AsyncClient):
        """Test fetching example.com and verify expected content."""
        response = await test_client.post(
            "/v1/html",
            json={"url": "https://example.com", "waitFor": "none"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify content contains expected text from example.com
        content = data["content"]
        assert "example" in content.lower()

        # Verify HTML structure
        assert "<html" in content.lower() or "<!doctype html>" in content.lower()

    async def test_http_and_https(self, test_client: AsyncClient):
        """Test that both http:// and https:// URLs work.

        Use neverssl.com for HTTP to avoid environments that auto-upgrade or block plain HTTP.
        """
        # Test HTTPS
        https_response = await test_client.post(
            "/v1/html",
            json={"url": "https://example.com", "waitFor": "none"}
        )
        assert https_response.status_code == 200

        # Test HTTP using neverssl.com (intentionally HTTP-only)
        http_response = await test_client.post(
            "/v1/html",
            json={"url": "http://neverssl.com", "waitFor": "none"}
        )
        assert http_response.status_code == 200

        # Both should return valid content
        https_data = https_response.json()
        http_data = http_response.json()

        assert len(https_data["content"]) > 0
        assert len(http_data["content"]) > 0

    async def test_response_metadata_contains_final_url(self, test_client: AsyncClient):
        """Test that metadata URL matches target URL."""
        target_url = "https://example.com"
        response = await test_client.post(
            "/v1/html",
            json={"url": target_url, "waitFor": "none"}
        )

        assert response.status_code == 200
        data = response.json()

        metadata = data["metadata"]
        # URL might have trailing slash or be slightly different due to redirects
        assert target_url in metadata["url"] or metadata["url"].startswith(target_url)
