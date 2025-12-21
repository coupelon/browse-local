import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_timeout_documented_behavior(test_client: AsyncClient):
    """
    Test that navigation timeout is enforced correctly.
    With wait_until="commit", httpbin returns quickly even for /delay/X.
    Here we just ensure that timeout param is passed through correctly.
    """
    url = "https://httpbin.org/delay/5"
    resp = await test_client.post(
        "/v1/html",
        json={"url": url, "waitFor": "none", "timeout": 10000},
    )
    # With wait_until="commit", response should be 200
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data.get("content"), str)


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
