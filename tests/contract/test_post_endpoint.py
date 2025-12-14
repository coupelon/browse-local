"""Contract tests for POST /v1/html endpoint with custom headers."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestPostEndpoint:
    """Test POST endpoint with custom headers support."""
    
    async def test_post_html_basic(self, test_client: AsyncClient):
        """Test POST endpoint with basic payload."""
        response = await test_client.post(
            "/v1/html",
            json={
                "url": "https://example.com",
                "waitFor": "none",
                "timeout": 15000
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "metadata" in data
        assert data["metadata"]["url"] == "https://example.com/"


    async def test_post_html_with_custom_headers(self, test_client: AsyncClient):
        """Test POST endpoint with custom HTTP headers."""
        # Use example.com instead of httpbin.org (which may be unavailable)
        response = await test_client.post(
            "/v1/html",
            json={
                "url": "https://example.com",
                "waitFor": "none",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Custom Agent)",
                    "Accept-Language": "fr-FR,fr;q=0.9",
                    "X-Custom-Header": "test-value"
                },
                "timeout": 15000
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "<html" in data["content"].lower()  # Valid HTML response


    async def test_post_html_blocked_header(self, test_client: AsyncClient):
        """Test POST endpoint rejects blocked headers."""
        response = await test_client.post(
            "/v1/html",
            json={
                "url": "https://example.com",
                "headers": {
                    "Host": "malicious.com"  # Blocked header
                }
            }
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data


    async def test_post_html_invalid_header_name(self, test_client: AsyncClient):
        """Test POST endpoint rejects invalid header names."""
        response = await test_client.post(
            "/v1/html",
            json={
                "url": "https://example.com",
                "headers": {
                    "Invalid Header Name!": "value"  # Invalid characters
                }
            }
        )
        
        assert response.status_code == 422  # Validation error


    async def test_post_html_with_selector(self, test_client: AsyncClient):
        """Test POST endpoint with selector."""
        response = await test_client.post(
            "/v1/html",
            json={
                "url": "https://example.com",
                "waitFor": "none",
                "selector": "h1",
                "timeout": 15000
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data


    async def test_post_html_conflicting_params(self, test_client: AsyncClient):
        """Test POST endpoint rejects conflicting parameters."""
        response = await test_client.post(
            "/v1/html",
            json={
                "url": "https://example.com",
                "waitFor": "network-idle",
                "selector": "h1"  # Conflict: selector + network-idle
            }
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data


    async def test_post_html_iframe_without_selector(self, test_client: AsyncClient):
        """Test POST endpoint rejects iframe without selector."""
        response = await test_client.post(
            "/v1/html",
            json={
                "url": "https://example.com",
                "iframe": "iframe#test"  # iframe requires selector
            }
        )
        
        assert response.status_code == 422  # Validation error


    async def test_post_html_camel_case_field_names(self, test_client: AsyncClient):
        """Test POST endpoint accepts camelCase field names."""
        response = await test_client.post(
            "/v1/html",
            json={
                "url": "https://example.com",
                "waitFor": "none",  # camelCase
                "timeout": 15000
            }
        )
        
        assert response.status_code == 200
