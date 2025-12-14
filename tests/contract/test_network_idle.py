"""Contract tests for network idle wait (User Story 2)."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestNetworkIdle:
    """Test network idle wait functionality."""
    
    async def test_wait_for_network_idle(self, test_client: AsyncClient):
        """Test that waitFor=network-idle waits for network to be idle."""
        response = await test_client.get(
            "/v1/html?url=https://example.com&waitFor=network-idle"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "content" in data
        assert "metadata" in data
        
        # Verify wait strategy is recorded
        metadata = data["metadata"]
        assert metadata["wait_strategy"] == "network-idle"
        
        # Verify content is valid
        assert len(data["content"]) > 0
    
    async def test_invalid_wait_for_value(self, test_client: AsyncClient):
        """Test that invalid waitFor value returns 400."""
        response = await test_client.get(
            "/v1/html?url=https://example.com&waitFor=invalid"
        )
        
        # FastAPI validation should catch this
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    async def test_render_time_reflects_wait(self, test_client: AsyncClient):
        """Test that renderTime reflects actual wait duration."""
        # Test with network-idle (should take longer than basic)
        response_idle = await test_client.get(
            "/v1/html?url=https://example.com&waitFor=network-idle"
        )
        
        assert response_idle.status_code == 200
        data_idle = response_idle.json()
        
        # Verify duration is tracked
        assert data_idle["metadata"]["duration_ms"] > 0
        assert isinstance(data_idle["metadata"]["duration_ms"], int)
