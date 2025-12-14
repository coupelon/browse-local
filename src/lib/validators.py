"""Validation utilities for URL, CSS selectors, and timeouts."""
import re
from typing import Optional
from urllib.parse import urlparse

from src.api.errors import InvalidUrlError, InvalidSelectorError, InvalidUserAgentError
from src.core.config import settings


def validate_url(url: str) -> str:
    """
    Validate URL format and scheme.
    
    Args:
        url: URL string to validate
        
    Returns:
        Validated URL string
        
    Raises:
        InvalidUrlError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise InvalidUrlError(url, "URL cannot be empty")
    
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ("http", "https"):
            raise InvalidUrlError(url, "URL must use http or https scheme")
        
        # Check netloc (domain)
        if not parsed.netloc:
            raise InvalidUrlError(url, "URL must include a valid domain")
        
        return url
    except Exception as e:
        if isinstance(e, InvalidUrlError):
            raise
        raise InvalidUrlError(url, f"Invalid URL format: {str(e)}")


def validate_selector(selector: Optional[str]) -> Optional[str]:
    """
    Validate CSS selector syntax.
    
    Args:
        selector: CSS selector string to validate
        
    Returns:
        Validated selector or None
        
    Raises:
        InvalidSelectorError: If selector syntax is invalid
    """
    if selector is None or selector == "":
        return None
    
    if not isinstance(selector, str):
        raise InvalidSelectorError(str(selector), "Selector must be a string")
    
    # Check length
    if len(selector) > 500:
        raise InvalidSelectorError(selector, "Selector exceeds maximum length of 500 characters")
    
    # Basic syntax validation
    # Check for empty or whitespace-only selector
    if not selector.strip():
        raise InvalidSelectorError(selector, "Selector cannot be empty or whitespace only")
    
    # Check for obvious syntax errors
    if selector.count("(") != selector.count(")"):
        raise InvalidSelectorError(selector, "Mismatched parentheses")
    
    if selector.count("[") != selector.count("]"):
        raise InvalidSelectorError(selector, "Mismatched brackets")
    
    # Check for invalid characters at start
    if re.match(r'^[0-9]', selector):
        raise InvalidSelectorError(selector, "Selector cannot start with a digit")
    
    return selector


def validate_timeout(timeout: Optional[int]) -> int:
    """
    Validate timeout value is within acceptable range.
    
    Args:
        timeout: Timeout in milliseconds
        
    Returns:
        Validated timeout value
        
    Raises:
        ValueError: If timeout is out of range
    """
    if timeout is None:
        return settings.timeout_default
    
    if not isinstance(timeout, int):
        raise ValueError("Timeout must be an integer")
    
    if timeout < settings.timeout_min:
        raise ValueError(f"Timeout must be at least {settings.timeout_min}ms")
    
    if timeout > settings.timeout_max:
        raise ValueError(f"Timeout cannot exceed {settings.timeout_max}ms")
    
    return timeout


def validate_user_agent(user_agent: Optional[str]) -> Optional[str]:
    """
    Validate User-Agent string.
    
    Args:
        user_agent: User-Agent string to validate
        
    Returns:
        Validated User-Agent or None
        
    Raises:
        InvalidUserAgentError: If User-Agent is invalid
    """
    if user_agent is None or user_agent == "":
        return None
    
    if not isinstance(user_agent, str):
        raise InvalidUserAgentError(str(user_agent), "User-Agent must be a string")
    
    # Check length
    if len(user_agent) > 1000:
        raise InvalidUserAgentError(user_agent, "User-Agent exceeds maximum length of 1000 characters")
    
    # Check for control characters
    if any(ord(c) < 32 or ord(c) == 127 for c in user_agent):
        raise InvalidUserAgentError(user_agent, "User-Agent contains invalid control characters")
    
    return user_agent
