import pytest
from fastapi import FastAPI
from starlette.requests import Request
from fastapi.testclient import TestClient

from src.api.errors import (
    InvalidUrlError,
    browse_local_error_handler,
    generic_error_handler,
)


def build_app():
    app = FastAPI()

    @app.exception_handler(Exception)
    async def _generic_handler(request, exc):
        return await generic_error_handler(request, exc)

    @app.exception_handler(InvalidUrlError)
    async def _invalid_url_handler(request, exc: InvalidUrlError):
        return await browse_local_error_handler(request, exc)

    @app.get("/raise-invalid-url")
    async def raise_invalid_url():
        raise InvalidUrlError("not-a-url", reason="Invalid URL")

    @app.get("/raise-generic")
    async def raise_generic():
        # Raise a generic exception to be handled by the Exception handler
        raise Exception("boom")

    return app


def test_error_response_format_invalid_url():
    app = build_app()
    client = TestClient(app)
    r = client.get("/raise-invalid-url")
    assert r.status_code == 400
    data = r.json()
    assert "error" in data
    err = data["error"]
    assert {"code", "message"}.issubset(err.keys())
    assert err["code"] == "INVALID_URL"
    assert isinstance(err.get("details"), dict)


@pytest.mark.asyncio
async def test_generic_error_maps_to_500():
    # Call handler directly to assert mapping
    scope = {"type": "http", "method": "GET", "path": "/raise-generic", "headers": []}
    request = Request(scope)
    from src.api.errors import generic_error_handler

    response = await generic_error_handler(request, Exception("boom"))
    assert response.status_code == 500
    data = response.body
    assert b'"code":"INTERNAL_ERROR"' in data
