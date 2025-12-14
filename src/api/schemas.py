"""Pydantic models for API request/response schemas."""
from typing import Optional, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator


class HtmlRequest(BaseModel):
    """Request schema for HTML retrieval."""
    
    url: HttpUrl = Field(..., description="Target URL to retrieve HTML from")
    wait_for: Optional[Literal["none", "network-idle"]] = Field(
        default="none",
        description="Wait strategy: 'none' (immediate), 'network-idle' (wait for network)",
        alias="waitFor"
    )
    selector: Optional[str] = Field(
        default=None,
        description="CSS selector to wait for before returning HTML",
        max_length=500
    )
    user_agent: Optional[str] = Field(
        default=None,
        description="Custom User-Agent header",
        alias="userAgent",
        max_length=1000
    )
    timeout: Optional[int] = Field(
        default=30000,
        description="Request timeout in milliseconds (1000-120000)",
        ge=1000,
        le=120000
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
                "timeout": 30000
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


class ErrorResponse(BaseModel):
    """Response schema for error cases."""
    
    error: "ErrorDetail" = Field(..., description="Error details")


class ErrorDetail(BaseModel):
    """Detailed error information."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for tracing"
    )
    details: Optional[dict] = Field(
        default=None,
        description="Additional error context"
    )


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""
    
    status: Literal["healthy", "unhealthy"] = Field(..., description="Service health status")
    version: str = Field(default="1.0.0", description="API version")
    browser_ready: bool = Field(..., description="Playwright browser readiness")
