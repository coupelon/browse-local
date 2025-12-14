import pytest

from src.lib.validators import (
    validate_url,
    validate_selector,
    validate_timeout,
    validate_user_agent,
)
from src.api.errors import (
    InvalidUrlError,
    InvalidSelectorError,
    InvalidUserAgentError,
)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "http://localhost:8000",
        "https://example.com/path?query=value#fragment",
    ],
)
def test_validate_url_valid(url):
    assert validate_url(url) == url


@pytest.mark.parametrize("url", ["not-a-url", "ftp://example.com", "", "http:/bad"])
def test_validate_url_invalid(url):
    with pytest.raises(InvalidUrlError):
        validate_url(url)


@pytest.mark.parametrize(
    "selector",
    [
        "h1",
        ".article",
        "div#main > p:first-child",
        "[data-test=btn]",
    ],
)
def test_validate_selector_valid(selector):
    assert validate_selector(selector) == selector


@pytest.mark.parametrize(
    "selector",
    [
        "[invalid:selector",
        "[missing",
        "1bad",
    ],
)
def test_validate_selector_invalid(selector):
    with pytest.raises(InvalidSelectorError):
        validate_selector(selector)


@pytest.mark.parametrize("timeout", [1000, 30000, 120000])
def test_validate_timeout_valid(timeout):
    assert validate_timeout(timeout) == timeout


@pytest.mark.parametrize("timeout", [0, 999, 120001, 999999])
def test_validate_timeout_out_of_range(timeout):
    with pytest.raises(ValueError):
        validate_timeout(timeout)


@pytest.mark.parametrize(
    "ua",
    [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)",
    ],
)
def test_validate_user_agent_valid(ua):
    assert validate_user_agent(ua) == ua


@pytest.mark.parametrize("ua", ["x" * 1001, "Mozilla\x07Bad"])
def test_validate_user_agent_invalid(ua):
    with pytest.raises(InvalidUserAgentError):
        validate_user_agent(ua)
