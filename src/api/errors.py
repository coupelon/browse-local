"""Custom exceptions and error handling for the API."""
from typing import Optional, Dict, Any
from fastapi import Request, status
from fastapi.responses import JSONResponse
from src.core.logger import get_logger

logger = get_logger(__name__)


class BrowseLocalError(Exception):
    """Base exception for all application errors."""
    
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class InvalidUrlError(BrowseLocalError):
    """Raised when URL is invalid or unreachable."""
    
    def __init__(self, url: str, reason: str = "Invalid or unreachable URL"):
        super().__init__(
            message=f"{reason}: {url}",
            code="INVALID_URL",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"url": url, "reason": reason}
        )


class TimeoutError(BrowseLocalError):
    """Raised when operation exceeds timeout limit."""
    
    def __init__(self, timeout_ms: int, operation: str = "page load"):
        super().__init__(
            message=f"Operation timed out after {timeout_ms}ms: {operation}",
            code="TIMEOUT",
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            details={"timeout_ms": timeout_ms, "operation": operation}
        )


class SelectorNotFoundError(BrowseLocalError):
    """Raised when CSS selector does not match any element."""
    
    def __init__(self, selector: str, timeout_ms: int):
        super().__init__(
            message=f"Selector '{selector}' not found within {timeout_ms}ms",
            code="SELECTOR_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"selector": selector, "timeout_ms": timeout_ms}
        )


class InvalidSelectorError(BrowseLocalError):
    """Raised when CSS selector syntax is invalid."""
    
    def __init__(self, selector: str, reason: str = "Invalid CSS selector syntax"):
        super().__init__(
            message=f"{reason}: {selector}",
            code="INVALID_SELECTOR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"selector": selector, "reason": reason}
        )


class InvalidUserAgentError(BrowseLocalError):
    """Raised when User-Agent string is invalid."""
    
    def __init__(self, user_agent: str, reason: str = "Invalid User-Agent"):
        super().__init__(
            message=f"{reason}: {user_agent[:100]}...",  # Truncate for display
            code="INVALID_USER_AGENT",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"reason": reason}
        )


class BrowserError(BrowseLocalError):
    """Raised when browser operation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Browser error: {message}",
            code="BROWSER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class PayloadTooLargeError(BrowseLocalError):
    """Raised when HTML content exceeds maximum allowed size."""
    
    def __init__(self, size_bytes: int, max_size_bytes: int = 10240):
        super().__init__(
            message=f"HTML content size ({size_bytes} bytes) exceeds maximum allowed size ({max_size_bytes} bytes)",
            code="PAYLOAD_TOO_LARGE",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            details={"size_bytes": size_bytes, "max_size_bytes": max_size_bytes}
        )


class ConflictingParametersError(BrowseLocalError):
    """Raised when multiple conflicting wait conditions are specified."""
    
    def __init__(self, conflicts: list[str]):
        super().__init__(
            message=f"Conflicting wait parameters specified: {', '.join(conflicts)}",
            code="CONFLICTING_PARAMETERS",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"conflicts": conflicts}
        )


async def browse_local_error_handler(
    request: Request,
    exc: BrowseLocalError
) -> JSONResponse:
    """Handle BrowseLocalError exceptions."""
    from src.core.logger import get_request_id
    
    request_id = get_request_id()
    
    logger.error(
        f"Error processing request: {exc.code}",
        extra={
            "error_code": exc.code,
            "error_message": exc.message,
            "error_details": exc.details,
            "request_id": request_id,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": request_id,
                "details": exc.details
            }
        }
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    from src.core.logger import get_request_id
    
    request_id = get_request_id()
    
    logger.exception(
        "Unexpected error processing request",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "exception_type": type(exc).__name__
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "request_id": request_id
            }
        }
    )
