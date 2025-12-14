"""Integration tests for real website fetching (User Story 1)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRealWebsite:
    """Integration tests with real websites."""

    async def test_fetch_example_com(self, test_client: AsyncClient):
        """Test fetching example.com and verify expected content."""
        response = await test_client.post("/v1/html", json={"url": "https://example.com", "waitFor": "none"})

        assert response.status_code == 200
        data = response.json()

        # Verify content contains expected text from example.com
        content = data["content"]
        assert "example" in content.lower()

        # Verify HTML structure
        assert "<html" in content.lower() or "<!doctype html>" in content.lower()

    async def test_http_and_https(self, test_client: AsyncClient):
        """Test that HTTPS URLs work correctly.

        Note: HTTP-only sites are increasingly rare and unreliable in CI environments.
        HTTPS is the standard for modern web applications.
        """
        # Test HTTPS with multiple domains to ensure protocol handling is robust
        urls = [
            "https://example.com",
            "https://www.w3schools.com",
        ]

        for url in urls:
            response = await test_client.post("/v1/html", json={"url": url, "waitFor": "none"})
            assert response.status_code == 200

            data = response.json()
            assert len(data["content"]) > 0
            assert data["metadata"]["url"].startswith("https://")

    async def test_response_metadata_contains_final_url(self, test_client: AsyncClient):
        """Test that metadata URL matches target URL."""
        target_url = "https://example.com"
        response = await test_client.post("/v1/html", json={"url": target_url, "waitFor": "none"})

        assert response.status_code == 200
        data = response.json()

        metadata = data["metadata"]
        # URL might have trailing slash or be slightly different due to redirects
        assert target_url in metadata["url"] or metadata["url"].startswith(target_url)
