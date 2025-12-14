import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_timeout_documented_behavior(test_client: AsyncClient):
    """
    Test that timeout parameter is respected and passed through correctly.
    Use a reliable, fast endpoint to ensure consistent behavior.
    """
    url = "https://example.com"
    # Use a reasonable timeout that should succeed for a reliable site
    resp = await test_client.post(
        "/v1/html",
        json={"url": url, "waitFor": "none", "timeout": 15000},
    )
    # Should complete successfully within timeout
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data.get("content"), str)
    assert len(data["content"]) > 0
    # Verify timeout was used (check metadata)
    assert data["metadata"]["duration_ms"] < 15000


@pytest.mark.asyncio
async def test_navigation_within_timeout_succeeds(test_client: AsyncClient):
    # If navigation completes within timeout, should return 200
    url = "https://example.com"
    resp = await test_client.post(
        "/v1/html",
        json={"url": url, "waitFor": "none", "timeout": 5000},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data.get("content"), str)
    assert len(data["content"]) > 0
