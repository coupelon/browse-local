"""Integration test for POST endpoint with custom headers."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_post_with_custom_headers_integration(test_client: AsyncClient):
    """
    Integration test: POST endpoint with custom headers.
    Verifies that custom headers are properly applied during page rendering.
    """
    response = await test_client.post(
        "/v1/html",
        json={
            "url": "https://example.com",
            "waitFor": "none",
            "headers": {"User-Agent": "Mozilla/5.0 (Test Agent)", "Accept-Language": "fr-FR,fr;q=0.9"},
            "timeout": 15000,
        },
    )

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
    assert metadata["status_code"] == 200
    assert metadata["url"] == "https://example.com/"
    assert "duration_ms" in metadata
    assert "timestamp" in metadata


@pytest.mark.asyncio
async def test_post_with_selector_and_headers(test_client: AsyncClient):
    """
    Integration test: POST endpoint with selector and custom headers.
    """
    response = await test_client.post(
        "/v1/html",
        json={
            "url": "https://example.com",
            "waitFor": "none",
            "selector": "h1",
            "headers": {"User-Agent": "Mozilla/5.0 (Integration Test)", "X-Test-Header": "integration-test-value"},
            "timeout": 15000,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert "<h1>" in data["content"].lower()
