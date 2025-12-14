"""Contract tests for custom user agent (User Story 4)."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUserAgent:
    """Test custom user agent functionality."""
    
    async def test_custom_user_agent_accepted(self, test_client: AsyncClient):
        """Test that custom user agent is accepted."""
        custom_ua = "MyCustomBot/1.0"
        response = await test_client.get(
            f"/v1/html?url=https://example.com&userAgent={custom_ua}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "content" in data
        assert "metadata" in data
    
    async def test_user_agent_length_validation(self, test_client: AsyncClient):
        """Test that userAgent over 1000 chars returns 400."""
        long_ua = "A" * 1001
        response = await test_client.get(
            f"/v1/html?url=https://example.com&userAgent={long_ua}"
        )
        
        # Should return 400 for invalid user agent
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    async def test_default_user_agent_when_omitted(self, test_client: AsyncClient):
        """Test that no userAgent param works fine (uses default)."""
        response = await test_client.get(
            "/v1/html?url=https://example.com"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["content"]) > 0
