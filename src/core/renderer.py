"""Page rendering logic using Playwright."""
import time
from typing import Optional, Tuple, Dict, Any
from datetime import datetime

from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from src.core.browser import BrowserSession
from src.core.logger import get_logger
from src.api.errors import (
    InvalidUrlError,
    TimeoutError,
    SelectorNotFoundError,
    BrowserError,
    PayloadTooLargeError
)

logger = get_logger(__name__)

# Maximum payload size (10KB as per FR-012)
MAX_PAYLOAD_SIZE = 10240


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
        user_agent: Optional[str] = None,
        timeout: int = 30000
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Render a web page and return HTML content with metadata.
        
        Args:
            url: Target URL to render
            wait_condition: Wait strategy ("none", "network-idle", or None)
            selector: CSS selector to wait for (if specified)
            user_agent: Custom User-Agent header
            timeout: Request timeout in milliseconds
            
        Returns:
            Tuple of (html_content, metadata_dict)
            
        Raises:
            InvalidUrlError: If URL is invalid or unreachable
            TimeoutError: If operation exceeds timeout
            SelectorNotFoundError: If selector not found within timeout
            BrowserError: If browser operation fails
            PayloadTooLargeError: If HTML content exceeds max size
        """
        start_time = time.time()
        
        try:
            async with self.browser_session.new_page(user_agent=user_agent) as page:
                # Navigate to URL
                logger.info(f"Navigating to {url}")
                try:
                    response = await page.goto(url, timeout=timeout, wait_until="commit")
                except PlaywrightTimeoutError:
                    raise TimeoutError(timeout, f"page navigation to {url}")
                except Exception as e:
                    raise InvalidUrlError(url, f"Failed to navigate: {str(e)}")
                
                if response is None:
                    raise InvalidUrlError(url, "No response received")
                
                # Apply wait condition
                if wait_condition == "network-idle":
                    logger.info("Waiting for network idle")
                    try:
                        await page.wait_for_load_state("networkidle", timeout=timeout)
                    except PlaywrightTimeoutError:
                        raise TimeoutError(timeout, "network idle wait")
                
                # Wait for selector if specified
                if selector:
                    logger.info(f"Waiting for selector: {selector}")
                    try:
                        await page.wait_for_selector(selector, timeout=timeout)
                    except PlaywrightTimeoutError:
                        raise SelectorNotFoundError(selector, timeout)
                    except Exception as e:
                        raise BrowserError(f"Selector wait failed: {str(e)}")
                
                # Get HTML content
                html_content = await page.content()
                
                # Check payload size (FR-012)
                content_size = len(html_content.encode('utf-8'))
                if content_size > MAX_PAYLOAD_SIZE:
                    raise PayloadTooLargeError(content_size, MAX_PAYLOAD_SIZE)
                
                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Build metadata
                metadata = {
                    "url": page.url,  # Final URL after redirects
                    "status_code": response.status,
                    "duration_ms": duration_ms,
                    "wait_strategy": wait_condition or "none",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                
                logger.info(f"Successfully rendered {url} in {duration_ms}ms")
                return html_content, metadata
                
        except (InvalidUrlError, TimeoutError, SelectorNotFoundError, BrowserError, PayloadTooLargeError):
            # Re-raise application errors
            raise
        except Exception as e:
            logger.exception(f"Unexpected error rendering {url}")
            raise BrowserError(f"Unexpected error: {str(e)}")
