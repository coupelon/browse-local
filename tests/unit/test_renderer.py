import asyncio
import pytest

from src.core.renderer import PageRenderer
from src.core.browser import BrowserSession


class DummyPage:
    def __init__(self):
        self._content = "<!DOCTYPE html><html><body><h1>Hi</h1></body></html>"
        self.url = "https://example.com"

    async def goto(self, url, timeout=None, wait_until=None):
        await asyncio.sleep(0)

        class Resp:
            status = 200

        return Resp()

    async def wait_for_load_state(self, state, timeout=None):
        await asyncio.sleep(0)
        return None

    async def wait_for_selector(self, selector, timeout=None):
        await asyncio.sleep(0)
        return None

    async def content(self):
        return self._content


class DummyContext:
    async def close(self):
        return None


class DummySession(BrowserSession):
    async def new_context(self, user_agent=None):
        class _Ctx:
            async def __aenter__(self_inner):
                return DummyContext()

            async def __aexit__(self_inner, exc_type, exc, tb):
                return False

        return _Ctx()

    def new_page(self, user_agent=None):
        class _Page:
            async def __aenter__(self_inner):
                return DummyPage()

            async def __aexit__(self_inner, exc_type, exc, tb):
                return False

        return _Page()


@pytest.mark.asyncio
async def test_renderer_returns_tuple():
    renderer = PageRenderer(DummySession())
    html, meta = await renderer.render(
        url="https://example.com",
        wait_condition=None,
        selector=None,
        user_agent=None,
        timeout=3000,
    )
    assert isinstance(html, str)
    assert isinstance(meta, dict)
    assert meta.get("status_code") == 200


@pytest.mark.asyncio
async def test_renderer_respects_timeout():
    renderer = PageRenderer(DummySession())
    html, meta = await renderer.render(
        url="https://example.com",
        wait_condition="network-idle",
        selector=None,
        user_agent=None,
        timeout=1000,
    )
    assert meta.get("duration_ms") is not None
