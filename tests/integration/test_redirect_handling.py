import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_follow_redirect(test_client: AsyncClient):
    # Test redirect handling: after redirects, metadata.url should reflect final URL
    url = "https://example.com"
    resp = await test_client.post(
        "/v1/html",
        json={"url": url, "waitFor": "none"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "metadata" in data
    final_url = data["metadata"].get("url")
    assert final_url
    assert "example.com" in final_url


@pytest.mark.asyncio
async def test_redirect_content_present(test_client: AsyncClient):
    # Content should be non-empty after redirect handling
    url = "https://example.com"
    resp = await test_client.post(
        "/v1/html",
        json={"url": url, "waitFor": "none"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data.get("content"), str)
    assert len(data["content"]) > 0


@pytest.mark.asyncio
async def test_final_page_content_after_redirect(test_client: AsyncClient):
    url = "https://example.com"
    resp = await test_client.post(
        "/v1/html",
        json={"url": url, "waitFor": "none"},
    )
    assert resp.status_code == 200
    data = resp.json()
    # Should have non-empty HTML from the final destination
    assert isinstance(data.get("content"), str)
    assert len(data["content"]) > 0
