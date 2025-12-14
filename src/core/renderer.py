"""Page rendering logic using Playwright."""

import time
from typing import Optional, Tuple, Dict, Any
from datetime import datetime

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from src.core.browser import BrowserSession
from src.core.logger import get_logger
from src.api.errors import (
    InvalidUrlError,
    TimeoutError,
    SelectorNotFoundError,
    SelectorNotFoundWithContentError,
    BrowserError,
)

logger = get_logger(__name__)

# No payload size limit (FR-012 removed)


class PageRenderer:
    """Handles page fetching and rendering using Playwright."""

    def __init__(self, browser_session: BrowserSession):
        """Initialize renderer with browser session."""
        self.browser_session = browser_session

    async def render(
        self,
        url: str,
        wait_condition: Optional[str] = None,
        selector: Optional[str] = None,
        iframe_selector: Optional[str] = None,
        user_agent: Optional[str] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: int = 30000,
        request_id: Optional[str] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Render a web page and return HTML content with metadata.

        Args:
            url: Target URL to render
            wait_condition: Wait strategy ("none", "network-idle", or None)
            selector: CSS selector to wait for (if specified)
            iframe_selector: CSS selector for the target iframe; when provided,
                waits for `selector` inside the matched iframe
            user_agent: Custom User-Agent header (legacy, prefer headers dict)
            headers: Custom HTTP headers (replaces user_agent for POST endpoint)
            timeout: Request timeout in milliseconds
            request_id: Unique request identifier for logging

        Returns:
            Tuple of (html_content, metadata_dict)

        Raises:
            InvalidUrlError: If URL is invalid or unreachable
            TimeoutError: If operation exceeds timeout
            SelectorNotFoundError: If selector not found within timeout
            BrowserError: If browser operation fails
        """
        start_time = time.time()

        try:
            # Merge headers if both user_agent and headers provided (legacy support)
            effective_headers = headers.copy() if headers else {}
            if user_agent and "User-Agent" not in effective_headers:
                effective_headers["User-Agent"] = user_agent

            logger.debug(
                f"Creating new browser page for request {request_id}",
                extra={
                    "request_id": request_id,
                    "user_agent_set": bool(user_agent),
                    "custom_headers_count": len(effective_headers),
                },
            )

            # Use User-Agent from headers if available, otherwise use legacy user_agent
            ua_for_context = effective_headers.get("User-Agent", user_agent)

            async with self.browser_session.new_page(user_agent=ua_for_context) as page:
                # Set custom headers (excluding User-Agent which is set via context)
                if effective_headers:
                    headers_to_set = {k: v for k, v in effective_headers.items() if k != "User-Agent"}
                    if headers_to_set:
                        await page.set_extra_http_headers(headers_to_set)
                        logger.debug(
                            f"Custom headers applied: {list(headers_to_set.keys())}",
                            extra={"request_id": request_id, "headers": list(headers_to_set.keys())},
                        )
                # Navigate to URL
                logger.info(f"Navigation started to {url}", extra={"request_id": request_id, "url": url})
                try:
                    response = await page.goto(url, timeout=timeout, wait_until="commit")
                except PlaywrightTimeoutError:
                    logger.error(
                        f"Navigation timeout for {url}",
                        extra={"request_id": request_id, "url": url, "timeout_ms": timeout},
                        exc_info=True,
                    )
                    raise TimeoutError(timeout, f"page navigation to {url}")
                except Exception as e:
                    logger.error(
                        f"Navigation failed for {url}: {str(e)}",
                        extra={"request_id": request_id, "url": url, "error_type": type(e).__name__},
                        exc_info=True,
                    )
                    raise InvalidUrlError(url, f"Failed to navigate: {str(e)}")

                if response is None:
                    logger.error(f"No response received from {url}", extra={"request_id": request_id, "url": url})
                    raise InvalidUrlError(url, "No response received")

                logger.info(
                    f"Navigation completed for {url}",
                    extra={"request_id": request_id, "url": url, "status_code": response.status},
                )

                # Apply wait condition
                if wait_condition == "network-idle":
                    logger.info("Wait condition applied: network-idle", extra={"request_id": request_id})
                    try:
                        await page.wait_for_load_state("networkidle", timeout=timeout)
                        logger.debug("Network idle reached", extra={"request_id": request_id})
                    except PlaywrightTimeoutError:
                        logger.error(
                            "Network idle timeout",
                            extra={"request_id": request_id, "timeout_ms": timeout},
                            exc_info=True,
                        )
                        raise TimeoutError(timeout, "network idle wait")

                # Wait for selector if specified
                selector_error = None
                if selector:
                    logger.info(
                        f"Wait condition applied: selector={selector}",
                        extra={"request_id": request_id, "selector": selector},
                    )
                    try:
                        if iframe_selector:
                            # Wait for iframe, then wait for selector inside iframe
                            logger.debug(
                                "Iframe selector provided; waiting for iframe",
                                extra={"request_id": request_id, "iframe_selector": iframe_selector},
                            )
                            await page.wait_for_selector(iframe_selector, timeout=timeout)

                            frame_locator = page.frame_locator(iframe_selector)
                            await frame_locator.locator(selector).wait_for(timeout=timeout)
                            logger.debug(
                                "Selector found inside iframe",
                                extra={
                                    "request_id": request_id,
                                    "selector": selector,
                                    "iframe_selector": iframe_selector,
                                },
                            )
                        else:
                            await page.wait_for_selector(selector, timeout=timeout)
                            logger.debug(
                                f"Selector found: {selector}", extra={"request_id": request_id, "selector": selector}
                            )
                    except PlaywrightTimeoutError:
                        # Capture error but continue to get HTML content for debugging
                        selector_error = f"Selector '{selector}' not found within {timeout}ms timeout"
                        logger.warning(
                            f"Selector not found within timeout: {selector} - will return HTML with error",
                            extra={"request_id": request_id, "selector": selector, "timeout_ms": timeout},
                            exc_info=True,
                        )
                    except Exception as e:
                        # Capture error but continue to get HTML content for debugging
                        selector_error = f"Selector wait failed: {str(e)}"
                        logger.error(
                            f"Selector wait failed: {str(e)} - will return HTML with error",
                            extra={"request_id": request_id, "selector": selector, "error_type": type(e).__name__},
                            exc_info=True,
                        )

                # Get HTML content (handle transient navigation updates)
                logger.debug("Capturing page content", extra={"request_id": request_id})
                try:
                    html_content = await page.content()
                except Exception:
                    try:
                        await page.wait_for_load_state("load", timeout=timeout)
                        html_content = await page.content()
                    except Exception as e:
                        logger.error(
                            f"Failed to retrieve content: {str(e)}",
                            extra={"request_id": request_id, "error_type": type(e).__name__},
                            exc_info=True,
                        )
                        raise BrowserError(f"Failed to retrieve content: {str(e)}")

                logger.debug(
                    "Page content captured", extra={"request_id": request_id, "content_size": len(html_content)}
                )

                # Payload size is unrestricted per updated requirements
                content_size = len(html_content.encode("utf-8"))

                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)

                # Build metadata
                metadata = {
                    "url": page.url,  # Final URL after redirects
                    "status_code": response.status,
                    "duration_ms": duration_ms,
                    "wait_strategy": wait_condition or "none",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }

                # If selector error occurred, raise exception with HTML content
                if selector_error:
                    metadata["selector_error"] = selector_error
                    metadata["partial_content"] = True
                    logger.warning(
                        "Selector error occurred, raising exception with HTML content",
                        extra={"request_id": request_id, "selector_error": selector_error},
                    )
                    raise SelectorNotFoundWithContentError(
                        selector=selector, timeout_ms=timeout, html_content=html_content, metadata=metadata
                    )

                logger.info(
                    "Page rendered successfully",
                    extra={
                        "request_id": request_id,
                        "url": page.url,
                        "duration_ms": duration_ms,
                        "content_size": content_size,
                    },
                )
                return html_content, metadata

        except (InvalidUrlError, TimeoutError, SelectorNotFoundError, SelectorNotFoundWithContentError, BrowserError):
            # Re-raise application errors
            raise
        except Exception as e:
            logger.exception(
                f"Unexpected error rendering {url}",
                extra={"request_id": request_id, "url": url, "error_type": type(e).__name__},
            )
            raise BrowserError(f"Unexpected error: {str(e)}")
