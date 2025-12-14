"""Contract tests for basic HTML retrieval (User Story 1)."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestBasicRetrieval:
    """Test basic HTML retrieval without wait conditions."""
    
    async def test_get_html_success(self, test_client: AsyncClient):
        """Test successful HTML retrieval from valid URL."""
        response = await test_client.get("/v1/html?url=https://example.com")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "content" in data
        assert "metadata" in data
        
        # Validate content
        assert isinstance(data["content"], str)
        assert len(data["content"]) > 0
        assert "<html" in data["content"].lower()
        
        # Validate metadata
        metadata = data["metadata"]
        assert "url" in metadata
        assert "status_code" in metadata
        assert "duration_ms" in metadata
        assert "wait_strategy" in metadata
        assert "timestamp" in metadata
        
        assert metadata["status_code"] == 200
        assert metadata["wait_strategy"] == "none"
    
    async def test_get_html_missing_url_param(self, test_client: AsyncClient):
        """Test that missing URL parameter returns 400."""
        response = await test_client.get("/v1/html")
        
        assert response.status_code == 422  # FastAPI validation error
        data = response.json()
        assert "detail" in data
    
    async def test_get_html_invalid_url(self, test_client: AsyncClient):
        """Test that invalid URL returns 400 with INVALID_URL code."""
        response = await test_client.get("/v1/html?url=not-a-url")
        
        assert response.status_code == 400
        data = response.json()
        
        assert "error" in data
        assert data["error"]["code"] == "INVALID_URL"
        assert "message" in data["error"]
    
    async def test_get_html_content_not_empty(self, test_client: AsyncClient):
        """Test that returned content is valid HTML string (not empty)."""
        response = await test_client.get("/v1/html?url=https://example.com")
        
        assert response.status_code == 200
        data = response.json()
        
        content = data["content"]
        assert content is not None
        assert isinstance(content, str)
        assert len(content) > 0
        
        # Verify it's HTML
        assert "<html" in content.lower() or "<!doctype html>" in content.lower()
    
    async def test_response_metadata_populated(self, test_client: AsyncClient):
        """Test that metadata has all required fields populated."""
        response = await test_client.get("/v1/html?url=https://example.com")
        
        assert response.status_code == 200
        data = response.json()
        
        metadata = data["metadata"]
        
        # Check all required fields exist and are populated
        assert metadata["url"] == "https://example.com" or metadata["url"].startswith("https://example.com")
        assert isinstance(metadata["status_code"], int)
        assert metadata["status_code"] > 0
        assert isinstance(metadata["duration_ms"], int)
        assert metadata["duration_ms"] >= 0
        assert isinstance(metadata["timestamp"], str)
        assert len(metadata["timestamp"]) > 0
        assert metadata["wait_strategy"] in ["none", "network-idle", "selector"]
