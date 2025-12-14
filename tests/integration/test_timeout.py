"""Integration tests for timeout configuration (User Story 5)."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestTimeoutIntegration:
    """Integration tests for timeout functionality."""
    
    async def test_short_timeout_completes(self, test_client: AsyncClient):
        """Test that requests complete within short timeout."""
        response = await test_client.get(
            "/v1/html?url=https://example.com&timeout=5000"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify completed within timeout
        assert data["metadata"]["duration_ms"] <= 5000 + 500  # Small margin
        assert len(data["content"]) > 0
    
    async def test_timeout_values_range(self, test_client: AsyncClient):
        """Test different timeout values work correctly."""
        timeouts = [2000, 5000, 10000, 30000]
        
        for timeout in timeouts:
            response = await test_client.get(
                f"/v1/html?url=https://example.com&timeout={timeout}"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Each should complete successfully
            assert len(data["content"]) > 0
            
            # Duration should be reasonable
            assert data["metadata"]["duration_ms"] > 0
            assert data["metadata"]["duration_ms"] <= timeout + 1000
