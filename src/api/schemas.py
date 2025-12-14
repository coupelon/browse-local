"""Pydantic models for API request/response schemas."""

import re
from typing import Optional, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


class HtmlRequest(BaseModel):
    """Request schema for HTML retrieval (GET endpoint - DEPRECATED)."""

    url: HttpUrl = Field(..., description="Target URL to retrieve HTML from")
    wait_for: Optional[Literal["none", "network-idle"]] = Field(
        default="none",
        description="Wait strategy: 'none' (immediate), 'network-idle' (wait for network)",
        alias="waitFor",
    )
    selector: Optional[str] = Field(
        default=None, description="CSS selector to wait for before returning HTML", max_length=500
    )
    user_agent: Optional[str] = Field(
        default=None, description="Custom User-Agent header", alias="userAgent", max_length=1000
    )
    timeout: Optional[int] = Field(
        default=30000, description="Request timeout in milliseconds (1000-120000)", ge=1000, le=120000
    )
    iframe: Optional[str] = Field(
        default=None, description="Optional iframe selector to wait for element inside iframe", max_length=500
    )

    class Config:
        """Pydantic configuration."""

        populate_by_name = True  # Allow both camelCase and snake_case
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "waitFor": "network-idle",
                "selector": "div.content",
                "userAgent": "Mozilla/5.0",
                "timeout": 30000,
            }
        }


class HtmlRequestPost(BaseModel):
    """Request schema for HTML retrieval (POST endpoint)."""

    url: HttpUrl = Field(..., description="Target URL to retrieve HTML from")
    wait_for: Optional[Literal["none", "network-idle"]] = Field(
        default="none",
        description="Wait strategy: 'none' (immediate), 'network-idle' (wait for network)",
        alias="waitFor",
    )
    selector: Optional[str] = Field(
        default=None, description="CSS selector to wait for before returning HTML", max_length=500
    )
    headers: Optional[dict[str, str]] = Field(
        default=None,
        description="Custom HTTP headers (e.g., User-Agent, Cookie, Authorization). Dangerous headers are blocked.",
        json_schema_extra={
            "example": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "fr-FR,fr;q=0.9",
                "Cookie": "session=abc123",
            }
        },
    )
    timeout: Optional[int] = Field(
        default=30000, description="Request timeout in milliseconds (1000-120000)", ge=1000, le=120000
    )
    iframe: Optional[str] = Field(
        default=None, description="Optional iframe selector to wait for element inside iframe", max_length=500
    )

    @field_validator("headers")
    @classmethod
    def validate_headers_format(cls, v: Optional[dict[str, str]]) -> Optional[dict[str, str]]:
        """Validate header names and values."""
        if v is None:
            return None

        # Blocked headers (dangerous or auto-managed)
        blocked_headers = {
            "host",
            "content-length",
            "transfer-encoding",
            "connection",
            "upgrade",
            "te",
            "trailer",
            "proxy-authorization",
            "proxy-authenticate",
        }

        validated = {}
        for name, value in v.items():
            # Check header name format
            if not re.match(r"^[a-zA-Z0-9\-]+$", name):
                raise ValueError(f"Invalid header name format: {name}. Only alphanumeric and hyphen allowed.")

            # Check if blocked
            if name.lower() in blocked_headers or name.lower().startswith("proxy-"):
                raise ValueError(f"Header '{name}' is blocked for security reasons.")

            # Check value is string
            if not isinstance(value, str):
                raise ValueError(f"Header value for '{name}' must be a string, got {type(value).__name__}")

            # Check for control characters in value (except tab)
            if any(ord(c) < 32 and c != "\t" or ord(c) == 127 for c in value):
                raise ValueError(f"Header value for '{name}' contains invalid control characters")

            validated[name] = value

        return validated

    @model_validator(mode="after")
    def validate_conflicts(self) -> "HtmlRequestPost":
        """Validate no conflicting parameters."""
        if self.selector and self.wait_for == "network-idle":
            raise ValueError(
                "Cannot use selector with waitFor='network-idle'. " "Use waitFor='none' when using a selector."
            )

        if self.iframe and not self.selector:
            raise ValueError(
                "iframe parameter requires a selector to specify which element to wait for inside the iframe."
            )

        return self

    class Config:
        """Pydantic configuration."""

        populate_by_name = True  # Allow both camelCase and snake_case
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "waitFor": "none",
                "selector": "#content",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Accept-Language": "fr-FR,fr;q=0.9",
                },
                "timeout": 30000,
            }
        }


class HtmlResponse(BaseModel):
    """Response schema for successful HTML retrieval."""

    content: str = Field(..., description="Retrieved HTML content")
    metadata: "ResponseMetadata" = Field(..., description="Response metadata")


class ResponseMetadata(BaseModel):
    """Metadata about the HTML retrieval operation."""

    url: str = Field(..., description="Final URL after redirects")
    status_code: int = Field(..., description="HTTP status code")
    duration_ms: int = Field(..., description="Total operation duration in milliseconds")
    wait_strategy: str = Field(..., description="Wait strategy used")
    timestamp: str = Field(..., description="ISO 8601 timestamp of retrieval")
    selector_error: Optional[str] = Field(
        default=None, description="Error message if selector was not found (content still returned for debugging)"
    )
    partial_content: Optional[bool] = Field(
        default=None, description="True if content may be incomplete due to selector/timeout error"
    )


class ErrorResponse(BaseModel):
    """Response schema for error cases."""

    error: "ErrorDetail" = Field(..., description="Error details")


class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracing")
    details: Optional[dict] = Field(default=None, description="Additional error context")


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: Literal["healthy", "unhealthy"] = Field(..., description="Service health status")
    version: str = Field(default="1.0.0", description="API version")
    browser_ready: bool = Field(..., description="Playwright browser readiness")
