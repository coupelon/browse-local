"""Contract tests for timeout configuration (User Story 5)."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestTimeout:
    """Test timeout configuration functionality."""
    
    async def test_custom_timeout(self, test_client: AsyncClient):
        """Test that custom timeout is respected."""
        response = await test_client.get(
            "/v1/html?url=https://example.com&timeout=10000"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response
        assert "content" in data
        assert "metadata" in data
        assert data["metadata"]["duration_ms"] <= 10000 + 1000  # Allow 1s margin
    
    async def test_timeout_out_of_range_low(self, test_client: AsyncClient):
        """Test that timeout below 1000ms returns 422."""
        response = await test_client.get(
            "/v1/html?url=https://example.com&timeout=500"
        )
        
        # FastAPI validation should catch this
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    async def test_timeout_out_of_range_high(self, test_client: AsyncClient):
        """Test that timeout above 120000ms returns 422."""
        response = await test_client.get(
            "/v1/html?url=https://example.com&timeout=150000"
        )
        
        # FastAPI validation should catch this
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    async def test_default_timeout(self, test_client: AsyncClient):
        """Test that no timeout param uses default (30000ms)."""
        response = await test_client.get(
            "/v1/html?url=https://example.com"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should complete successfully with default timeout
        assert "content" in data
        assert len(data["content"]) > 0
