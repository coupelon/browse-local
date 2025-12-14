import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_iframe_contains_selector(test_client: AsyncClient):
    """Ensure selector inside iframe is available before content capture."""
    url = "https://www.w3schools.com/html/html_iframe.asp"
    payload = {
        "url": url,
        "selector": "#getdiploma",
        "iframe": 'iframe[src*="default.asp"]',
        "waitFor": "none",
    }
    resp = await test_client.post("/v1/html", json=payload)

    assert resp.status_code == 200
    body = resp.json()
    content = body["content"]
    metadata = body["metadata"]

    assert "<iframe" in content or "<IFRAME" in content
    assert isinstance(metadata["duration_ms"], int) and metadata["duration_ms"] >= 0
    assert metadata["status_code"] == 200
    assert "w3schools.com" in metadata["url"]
