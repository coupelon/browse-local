"""Contract tests for CSS selector wait (User Story 3)."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestSelectorMatch:
    """Test CSS selector wait functionality."""
    
    async def test_wait_for_selector(self, test_client: AsyncClient):
        """Test that selector parameter waits for element to appear."""
        response = await test_client.get(
            "/v1/html?url=https://example.com&selector=h1"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "content" in data
        assert "metadata" in data
        
        # Verify content contains the selector
        assert "<h1" in data["content"].lower()
    
    async def test_invalid_selector_syntax(self, test_client: AsyncClient):
        """Test that invalid CSS selector syntax returns 400."""
        response = await test_client.get(
            "/v1/html?url=https://example.com&selector=123invalid"
        )
        
        assert response.status_code == 400
        data = response.json()
        
        assert "error" in data
        assert data["error"]["code"] == "INVALID_SELECTOR"
    
    async def test_selector_timeout_handling(self, test_client: AsyncClient):
        """Test behavior when selector never appears (timeout)."""
        response = await test_client.get(
            "/v1/html?url=https://example.com&selector=.nonexistent-class&timeout=2000"
        )
        
        # Should return 404 when selector not found
        assert response.status_code == 404
        data = response.json()
        
        assert "error" in data
        assert data["error"]["code"] == "SELECTOR_NOT_FOUND"
    
    async def test_conflicting_waitFor_and_selector(self, test_client: AsyncClient):
        """Test that using both waitFor=network-idle and selector returns error."""
        response = await test_client.get(
            "/v1/html?url=https://example.com&waitFor=network-idle&selector=h1"
        )
        
        # Should return 400 for conflicting parameters
        assert response.status_code == 400
        data = response.json()
        
        assert "error" in data
        assert data["error"]["code"] == "CONFLICTING_PARAMETERS"
