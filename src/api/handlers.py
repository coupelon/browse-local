"""Request handlers for API endpoints."""
import uuid
from typing import Optional, Literal

from fastapi import Query, HTTPException, status
from pydantic import HttpUrl

from src.core.renderer import PageRenderer
from src.core.browser import BrowserSession
from src.core.logger import get_logger, set_request_id
from src.api.schemas import HtmlResponse, ResponseMetadata, HealthResponse
from src.api.errors import ConflictingParametersError
from src.lib.validators import validate_url, validate_selector, validate_timeout, validate_user_agent

logger = get_logger(__name__)


async def get_html(
    url: str = Query(..., description="Target URL to retrieve HTML from"),
    waitFor: Optional[Literal["none", "network-idle"]] = Query(None, description="Wait strategy: 'none' or 'network-idle'"),
    selector: Optional[str] = Query(None, description="CSS selector to wait for"),
    userAgent: Optional[str] = Query(None, description="Custom User-Agent header"),
    timeout: Optional[int] = Query(30000, ge=1000, le=120000, description="Timeout in milliseconds")
) -> HtmlResponse:
    """
    Retrieve HTML content from a web page.
    
    Args:
        url: Target URL to retrieve HTML from
        waitFor: Wait strategy ("none" or "network-idle")
        selector: CSS selector to wait for before returning HTML
        userAgent: Custom User-Agent header
        timeout: Request timeout in milliseconds
        
    Returns:
        HtmlResponse with content and metadata
    """
    # Generate and set request ID
    request_id = str(uuid.uuid4())
    set_request_id(request_id)
    
    logger.info(f"Processing HTML request for {url}")
    
    # Validate parameters
    validated_url = validate_url(url)
    validated_selector = validate_selector(selector)
    validated_timeout = validate_timeout(timeout)
    validated_user_agent = validate_user_agent(userAgent)
    
    # Check for conflicting parameters (Quick Fix #2)
    conflicts = []
    if waitFor and waitFor != "none" and validated_selector:
        conflicts.append("waitFor and selector cannot be used together")
    
    if conflicts:
        raise ConflictingParametersError(conflicts)
    
    # Get browser session and renderer
    browser_session = await BrowserSession.get_instance()
    renderer = PageRenderer(browser_session)
    
    # Determine wait condition
    wait_condition = None
    if waitFor == "network-idle":
        wait_condition = "network-idle"
    elif validated_selector:
        wait_condition = None  # selector is handled separately
    
    # Render page
    html_content, metadata = await renderer.render(
        url=validated_url,
        wait_condition=wait_condition,
        selector=validated_selector,
        user_agent=validated_user_agent,
        timeout=validated_timeout
    )
    
    # Build response
    response_metadata = ResponseMetadata(**metadata)
    
    return HtmlResponse(
        content=html_content,
        metadata=response_metadata
    )


async def get_health() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        HealthResponse with service status
    """
    try:
        browser_session = await BrowserSession.get_instance()
        browser_ready = browser_session.is_ready()
        
        status = "healthy" if browser_ready else "unhealthy"
        
        return HealthResponse(
            status=status,
            version="1.0.0",
            browser_ready=browser_ready
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            browser_ready=False
        )
