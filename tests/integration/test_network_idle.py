"""Integration tests for network idle wait (User Story 2)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestNetworkIdleIntegration:
    """Integration tests for network idle functionality."""

    async def test_network_idle_detection(self, test_client: AsyncClient):
        """Test network idle wait with a page that loads content."""
        # Use example.com as a simple test (actual delay sites may be flaky)
        response = await test_client.post(
            "/v1/html",
            json={"url": "https://example.com", "waitFor": "network-idle", "timeout": 10000}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify content is present
        assert len(data["content"]) > 0
        assert "example" in data["content"].lower()

        # Verify wait strategy
        metadata = data["metadata"]
        assert metadata["wait_strategy"] == "network-idle"
        assert metadata["duration_ms"] > 0

    async def test_network_idle_vs_basic(self, test_client: AsyncClient):
        """Compare network-idle wait vs basic retrieval."""
        # Basic retrieval
        response_basic = await test_client.post(
            "/v1/html",
            json={"url": "https://example.com", "waitFor": "none"}
        )
        assert response_basic.status_code == 200
        data_basic = response_basic.json()

        # Network-idle retrieval
        response_idle = await test_client.post(
            "/v1/html",
            json={"url": "https://example.com", "waitFor": "network-idle"}
        )
        assert response_idle.status_code == 200
        data_idle = response_idle.json()

        # Both should succeed
        assert len(data_basic["content"]) > 0
        assert len(data_idle["content"]) > 0

        # Verify wait strategies
        assert data_basic["metadata"]["wait_strategy"] == "none"
        assert data_idle["metadata"]["wait_strategy"] == "network-idle"
