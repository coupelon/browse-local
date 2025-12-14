#!/usr/bin/env python3
"""
Example: Fetch HTML content using the Browse Local API (Python + httpx)
"""
import asyncio
import httpx


async def fetch_html(url: str, wait_for: str = "none", selector: str = None):
    """
    Fetch HTML content from a URL using the Browse Local API.
    
    Args:
        url: Target URL to fetch
        wait_for: Wait strategy ("none", "network-idle")
        selector: CSS selector to wait for (optional)
    """
    api_base = "http://localhost:8000"
    
    params = {
        "url": url,
        "waitFor": wait_for,
    }
    
    if selector:
        params["selector"] = selector
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.get(f"{api_base}/v1/html", params=params)
            response.raise_for_status()
            
            data = response.json()
            print(f"✓ Successfully fetched {url}")
            print(f"  Status: {data['metadata']['status_code']}")
            print(f"  Duration: {data['metadata']['duration_ms']}ms")
            print(f"  Content length: {len(data['content'])} characters")
            print(f"  Final URL: {data['metadata']['url']}")
            
            return data["content"]
            
        except httpx.HTTPStatusError as e:
            print(f"✗ HTTP error: {e.response.status_code}")
            error = e.response.json()
            print(f"  Error code: {error['error']['code']}")
            print(f"  Message: {error['error']['message']}")
            return None
        except Exception as e:
            print(f"✗ Request failed: {e}")
            return None


async def main():
    """Run example requests."""
    print("Browse Local API - Python Example\n")
    
    # Example 1: Basic retrieval
    print("1. Basic HTML retrieval:")
    await fetch_html("https://example.com")
    print()
    
    # Example 2: Wait for network idle
    print("2. Wait for network idle:")
    await fetch_html("https://example.com", wait_for="network-idle")
    print()
    
    # Example 3: Wait for CSS selector
    print("3. Wait for CSS selector:")
    await fetch_html("https://example.com", wait_for="selector", selector="h1")
    print()
    
    # Example 4: Custom timeout
    print("4. With custom timeout:")
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(
            "http://localhost:8000/v1/html",
            params={"url": "https://example.com", "timeout": 5000}
        )
        data = response.json()
        print(f"✓ Fetched with 5s timeout in {data['metadata']['duration_ms']}ms")
    print()


if __name__ == "__main__":
    asyncio.run(main())
