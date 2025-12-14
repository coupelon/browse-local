"""Integration tests for custom user agent (User Story 4)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUserAgentIntegration:
    """Integration tests for custom user agent functionality."""

    async def test_mobile_user_agent(self, test_client: AsyncClient):
        """Test with mobile (iPhone) user agent."""
        mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        response = await test_client.post(
            "/v1/html", json={"url": "https://example.com", "headers": {"User-Agent": mobile_ua}}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify content is returned
        assert len(data["content"]) > 0
        assert "example" in data["content"].lower()

    async def test_custom_user_agent_different_from_default(self, test_client: AsyncClient):
        """Test that custom and default user agents both work."""
        # Request with custom UA
        custom_ua = "CustomBot/2.0"
        response_custom = await test_client.post(
            "/v1/html", json={"url": "https://example.com", "headers": {"User-Agent": custom_ua}}
        )

        # Request without custom UA (default)
        response_default = await test_client.post("/v1/html", json={"url": "https://example.com"})

        # Both should succeed
        assert response_custom.status_code == 200
        assert response_default.status_code == 200

        data_custom = response_custom.json()
        data_default = response_default.json()

        # Both should return valid content
        assert len(data_custom["content"]) > 0
        assert len(data_default["content"]) > 0
