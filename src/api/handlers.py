"""Request handlers for API endpoints."""

import uuid
from typing import Optional, Dict, Any

from fastapi import HTTPException, status

from src.core.renderer import PageRenderer
from src.core.browser import BrowserSession
from src.core.logger import get_logger, set_request_id
from src.core.metrics import get_metrics_collector, RequestMetrics
from src.api.schemas import HtmlResponse, ResponseMetadata, HealthResponse, HtmlRequestPost
from src.api.errors import SelectorNotFoundWithContentError
from src.lib.validators import validate_url, validate_selector, validate_timeout, validate_headers

logger = get_logger(__name__)


async def post_html(request: HtmlRequestPost) -> HtmlResponse:
    """
    Retrieve HTML content from a web page (POST endpoint with custom headers support).

    Args:
        request: HtmlRequestPost with url, waitFor, selector, headers, timeout, iframe

    Returns:
        HtmlResponse with content and metadata
    """
    # Generate and set request ID
    request_id = str(uuid.uuid4())
    set_request_id(request_id)

    # Log request received with all parameters
    logger.info(
        "HTML POST request received",
        extra={
            "request_id": request_id,
            "url": str(request.url),
            "waitFor": request.wait_for,
            "selector": request.selector,
            "iframe": request.iframe,
            "custom_headers_count": len(request.headers) if request.headers else 0,
            "timeout_ms": request.timeout,
        },
    )

    # Validate parameters (headers already validated by Pydantic)
    validated_url = validate_url(str(request.url))
    validated_selector = validate_selector(request.selector)
    validated_iframe = validate_selector(request.iframe)
    validated_timeout = validate_timeout(request.timeout)
    validated_headers = validate_headers(request.headers)  # Returns empty dict if None

    # Conflicts are already checked by model_validator in HtmlRequestPost

    # Get browser session and renderer
    browser_session = await BrowserSession.get_instance()
    renderer = PageRenderer(browser_session)

    # Determine wait condition
    wait_condition = None
    if request.wait_for == "network-idle":
        wait_condition = "network-idle"
    elif validated_selector:
        wait_condition = None  # selector is handled separately

    logger.debug(
        f"Processing POST request {request_id}",
        extra={
            "wait_condition": wait_condition,
            "selector": validated_selector,
            "custom_headers": list(validated_headers.keys()) if validated_headers else [],
        },
    )

    try:
        # Render page with custom headers
        html_content, metadata = await renderer.render(
            url=validated_url,
            wait_condition=wait_condition,
            selector=validated_selector,
            iframe_selector=validated_iframe,
            headers=validated_headers if validated_headers else None,
            timeout=validated_timeout,
            request_id=request_id,
        )

        # Build response
        response_metadata = ResponseMetadata(**metadata)

        # Record metrics
        metrics = RequestMetrics(
            request_id=request_id,
            url=metadata.get("url", validated_url),
            duration_ms=metadata.get("duration_ms", 0),
            render_time_ms=metadata.get("duration_ms", 0),
            status_code=metadata.get("status_code", 200),
            content_size=len(html_content),
            wait_strategy=metadata.get("wait_strategy", "none"),
        )
        metrics_collector = get_metrics_collector()
        metrics_collector.record_request(metrics)

        # Log successful response
        logger.info(
            f"POST response sent for request {request_id}",
            extra={
                "request_id": request_id,
                "url": metadata.get("url"),
                "duration_ms": metadata.get("duration_ms"),
                "status_code": metadata.get("status_code"),
                "content_size": len(html_content),
            },
        )

        return HtmlResponse(content=html_content, metadata=response_metadata)
    except SelectorNotFoundWithContentError as e:
        # Return HTML with error metadata and proper HTTP status code
        response_metadata = ResponseMetadata(**e.metadata)

        # Record metrics
        metrics = RequestMetrics(
            request_id=request_id,
            url=e.metadata.get("url", validated_url),
            duration_ms=e.metadata.get("duration_ms", 0),
            render_time_ms=e.metadata.get("duration_ms", 0),
            status_code=404,
            content_size=len(e.html_content),
            wait_strategy=e.metadata.get("wait_strategy", "none"),
            error="SELECTOR_NOT_FOUND",
        )
        metrics_collector = get_metrics_collector()
        metrics_collector.record_request(metrics)

        logger.warning(
            f"POST request {request_id} failed with selector error",
            extra={
                "request_id": request_id,
                "selector_error": e.metadata.get("selector_error"),
                "status_code": 404,
                "content_size": len(e.html_content),
            },
        )

        from fastapi import HTTPException

        raise HTTPException(
            status_code=404, detail={"content": e.html_content, "metadata": response_metadata.model_dump()}
        )
    except Exception as e:
        # Record error metrics
        metrics = RequestMetrics(
            request_id=request_id,
            url=validated_url,
            duration_ms=0,
            render_time_ms=0,
            status_code=500,
            content_size=0,
            wait_strategy=request.wait_for or "none",
            error=type(e).__name__,
        )
        metrics_collector = get_metrics_collector()
        metrics_collector.record_request(metrics)

        logger.error(
            f"Error processing POST request {request_id}: {str(e)}",
            extra={"request_id": request_id, "url": validated_url, "error_type": type(e).__name__},
            exc_info=True,
        )
        raise


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

        return HealthResponse(status=status, version="1.0.0", browser_ready=browser_ready)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(status="unhealthy", version="1.0.0", browser_ready=False)


async def get_metrics() -> Dict[str, Any]:
    """
    Get performance metrics endpoint.

    Returns:
        Dictionary with request statistics and recent metrics
    """
    collector = get_metrics_collector()
    stats = collector.get_stats()

    logger.info(
        "Metrics requested",
        extra={
            "total_requests": stats["total_requests"],
            "average_duration_ms": stats["average_duration_ms"],
            "error_rate_percent": stats["error_rate_percent"],
        },
    )

    return {"stats": stats, "recent_requests": collector.get_recent_metrics(limit=50)}
