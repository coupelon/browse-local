"""Contract tests for custom headers (User Story 4) - Headers are POST-only feature."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHeaders:
    """Test custom header functionality via POST endpoint."""
    
    async def test_custom_header_accepted(self, test_client: AsyncClient):
        """Test that custom User-Agent header is accepted."""
        response = await test_client.post(
            "/v1/html",
            json={
                "url": "https://example.com",
                "headers": {
                    "User-Agent": "MyCustomBot/1.0"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "content" in data
        assert "metadata" in data
    
    async def test_multiple_headers_accepted(self, test_client: AsyncClient):
        """Test that multiple custom headers are accepted."""
        response = await test_client.post(
            "/v1/html",
            json={
                "url": "https://example.com",
                "headers": {
                    "User-Agent": "MyCustomBot/1.0",
                    "Cookie": "session=xyz",
                    "Authorization": "Bearer token123"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["content"]) > 0
    
    async def test_blocked_header_rejected(self, test_client: AsyncClient):
        """Test that blocked headers are rejected."""
        response = await test_client.post(
            "/v1/html",
            json={
                "url": "https://example.com",
                "headers": {
                    "Host": "example.com"  # Blocked header
                }
            }
        )
        
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "detail" in data
    
    async def test_no_headers_default(self, test_client: AsyncClient):
        """Test that requests work without custom headers."""
        response = await test_client.post(
            "/v1/html",
            json={
                "url": "https://example.com"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["content"]) > 0
