# Quick Start: Web Page HTML Retrieval API

**Phase**: Phase 1 (Design & Contracts)  
**Date**: 2025-12-14  
**Branch**: `001-web-page-scraper`

## 5-Minute Setup

### 1. Prerequisites

- Docker (20.10+) installed locally
- `curl` or similar HTTP client
- No additional setup required (Docker includes Python, Playwright, Chromium)

### 2. Build & Run Container

```bash
# Build the Docker image
docker build -t browse-local:latest .

# Run the container (port 8000)
docker run -p 8000:8000 browse-local:latest

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 3. Health Check

```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-14T10:30:00Z",
  "browser": {
    "connected": true,
    "version": "Chromium 120.0.0"
  }
}
```

---

## Basic Examples

### Example 1: Simple HTML Retrieval

Fetch HTML content from a static page (no waiting):

```bash
curl "http://localhost:8000/v1/html?url=https://example.com"
```

**Response** (truncated):
```json
{
  "content": "<!DOCTYPE html>\n<html>\n<head>...",
  "metadata": {
    "url": "https://example.com",
    "statusCode": 200,
    "renderTime": 0.567,
    "timestamp": "2025-12-14T10:30:00Z",
    "warnings": []
  }
}
```

**Time**: ~1-2 seconds

---

### Example 2: Wait for Network Idle

Fetch a page that loads content dynamically via JavaScript; wait for all network requests to complete:

```bash
curl "http://localhost:8000/v1/html?url=https://httpbin.org/delay/2&waitFor=network-idle&timeout=15000"
```

**What happens**:
1. Page starts loading at `httpbin.org/delay/2`
2. Browser waits for all network activity to cease
3. After 2 seconds (simulated delay), network becomes idle
4. HTML is captured and returned

**Response** (truncated):
```json
{
  "content": "<!DOCTYPE html>\n<html>...",
  "metadata": {
    "url": "https://httpbin.org/delay/2",
    "statusCode": 200,
    "renderTime": 2.450,
    "timestamp": "2025-12-14T10:30:02Z",
    "warnings": []
  }
}
```

**Time**: ~2-3 seconds (depends on page)

---

### Example 3: Wait for CSS Selector

Wait for a specific element to appear in the DOM before capturing HTML:

```bash
curl "http://localhost:8000/v1/html?url=https://example.com&waitFor=selector&selector=.content&timeout=10000"
```

**What happens**:
1. Page loads at `example.com`
2. Browser waits for an element matching `.content` selector to appear
3. Once found (or timeout), HTML is captured

**Response**:
```json
{
  "content": "<!DOCTYPE html>\n<html>...",
  "metadata": {
    "url": "https://example.com",
    "statusCode": 200,
    "renderTime": 0.789,
    "timestamp": "2025-12-14T10:30:00Z",
    "warnings": []
  }
}
```

**Time**: ~1-2 seconds (or up to 10s timeout)

---

### Example 4: Custom User Agent (Mobile)

Emulate a mobile browser to test responsive design:

```bash
curl "http://localhost:8000/v1/html?url=https://example.com&userAgent=Mozilla/5.0%20(iPhone%3B%20CPU%20iPhone%20OS%2014_7_1%20like%20Mac%20OS%20X)%20AppleWebKit/537.36"
```

**What happens**:
- Page is fetched with iPhone user agent
- Server may return mobile-optimized HTML
- Rendering happens in mobile viewport

**Response**: Same structure, but content may differ (mobile layout)

**Note**: URL-encode special characters (spaces, parentheses, etc.)

---

### Example 5: Timeout Handling

Request a slow-loading page with a short timeout:

```bash
curl "http://localhost:8000/v1/html?url=https://httpbin.org/delay/15&waitFor=network-idle&timeout=5000"
```

**What happens**:
1. Page starts loading
2. Browser waits for network idle
3. After 5 seconds (timeout), rendering stops
4. **Returns HTTP 200 with partial content** (not an error)

**Response**:
```json
{
  "content": "<!DOCTYPE html>\n<html>...",
  "metadata": {
    "url": "https://httpbin.org/delay/15",
    "statusCode": 200,
    "renderTime": 5.001,
    "timestamp": "2025-12-14T10:30:05Z",
    "warnings": ["Timeout reached (5000ms) before network idle; returning partial content"]
  }
}
```

**Time**: ~5 seconds (timeout duration)

---

## Error Examples

### Error 1: Invalid URL

```bash
curl "http://localhost:8000/v1/html?url=not-a-url"
```

**Response** (HTTP 400):
```json
{
  "code": "INVALID_URL",
  "message": "URL must be a valid HTTP or HTTPS URL",
  "details": {
    "url": "not-a-url",
    "reason": "missing scheme (http or https)"
  },
  "timestamp": "2025-12-14T10:30:00Z"
}
```

---

### Error 2: Selector Required

```bash
curl "http://localhost:8000/v1/html?url=https://example.com&waitFor=selector"
```

**Response** (HTTP 400):
```json
{
  "code": "SELECTOR_REQUIRED",
  "message": "selector parameter required when waitFor=selector",
  "details": {
    "parameter": "selector",
    "received": null
  },
  "timestamp": "2025-12-14T10:30:00Z"
}
```

---

### Error 3: 404 Not Found

```bash
curl "http://localhost:8000/v1/html?url=https://example.com/nonexistent-page"
```

**Response** (HTTP 404):
```json
{
  "code": "NOT_FOUND",
  "message": "Target URL returned 404 Not Found",
  "details": {
    "url": "https://example.com/nonexistent-page",
    "targetStatusCode": 404
  },
  "timestamp": "2025-12-14T10:30:00Z"
}
```

---

## Using the API Programmatically

### Python Example (with httpx)

```python
import httpx
import json

async def fetch_page_html(url: str, wait_for: str = "none"):
    """Fetch HTML from a page."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/v1/html",
            params={
                "url": url,
                "waitFor": wait_for,
                "timeout": 30000
            }
        )
        response.raise_for_status()
        return response.json()

# Usage
result = await fetch_page_html("https://example.com", wait_for="network-idle")
print(f"Rendered in {result['metadata']['renderTime']}s")
print(f"HTML length: {len(result['content'])} characters")
```

### JavaScript/Node.js Example (with fetch)

```javascript
async function fetchPageHtml(url, waitFor = "none") {
  const params = new URLSearchParams({
    url: url,
    waitFor: waitFor,
    timeout: 30000
  });

  const response = await fetch(
    `http://localhost:8000/v1/html?${params}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`${error.code}: ${error.message}`);
  }

  return await response.json();
}

// Usage
const result = await fetchPageHtml("https://example.com", "network-idle");
console.log(`Rendered in ${result.metadata.renderTime}s`);
```

### cURL with Piping

Extract just the HTML content using `jq`:

```bash
curl -s "http://localhost:8000/v1/html?url=https://example.com" | jq -r '.content' > page.html
```

---

## Docker Usage

### Environment Variables

Configure via `.env` file (or `-e` flag):

```bash
# .env example
TIMEOUT_MIN=1000          # Minimum timeout (ms)
TIMEOUT_MAX=120000        # Maximum timeout (ms)
TIMEOUT_DEFAULT=30000     # Default timeout (ms)
LOG_LEVEL=INFO            # Log level (DEBUG, INFO, WARN, ERROR)
WORKERS=2                 # Uvicorn worker threads
```

### Run with Custom Env

```bash
docker run -p 8000:8000 \
  -e TIMEOUT_DEFAULT=60000 \
  -e LOG_LEVEL=DEBUG \
  browse-local:latest
```

### Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      TIMEOUT_DEFAULT: 30000
      LOG_LEVEL: INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

Run:
```bash
docker-compose up
```

---

## Performance Tips

1. **Reduce Timeout for Fast Pages**:
   ```bash
   curl "http://localhost:8000/v1/html?url=https://example.com&timeout=3000"
   ```
   → Returns in ~1-3s instead of default 30s

2. **Use network-idle Sparingly**:
   - Best for pages that load data via API calls
   - Slower than `waitFor=none` (may wait 5-30+ seconds)

3. **Cache Results**:
   - In production, cache fetched HTML in Redis or similar
   - Re-fetch only if data is stale

4. **Monitor via Health Check**:
   ```bash
   # Periodic health check
   watch -n 10 'curl -s http://localhost:8000/health | jq .'
   ```

---

## Troubleshooting

### Browser Not Connecting

**Symptom**: `"Browser process exited unexpectedly"`

**Solutions**:
- Increase Docker memory: `docker run -m 1g browse-local:latest`
- Check Docker logs: `docker logs <container-id>`
- Verify Playwright/Chromium installed: `docker run browse-local:latest playwright install-deps`

### Timeout Always Triggered

**Symptom**: `"Timeout reached before..."` even for quick pages

**Solutions**:
- Increase timeout: `&timeout=60000`
- Switch to `waitFor=none`: `&waitFor=none`
- Check target website (may be slow)

### Selector Not Matching

**Symptom**: Selector specified but warnings say not found

**Solutions**:
- Verify selector with browser DevTools: Open page in browser, use DevTools to test selector
- Check JavaScript execution: If selector is added by JS, ensure `waitFor=network-idle` or higher timeout
- Use more generic selector: `.content` instead of `.article-content-loaded-by-js`

---

## Next Steps

1. **Run integration tests**: `pytest tests/integration/`
2. **View OpenAPI docs**: Visit `/docs` on running container (FastAPI auto-generates interactive Swagger UI)
3. **Check logs**: `docker logs -f <container-id>` for structured JSON logs
4. **Deploy to production**: Use Kubernetes, Docker Swarm, or cloud-managed containers (AWS ECS, Google Cloud Run, etc.)

---

## API Reference Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/v1/html` | Fetch and render HTML |
| GET | `/health` | Health check |

**Query Parameters**:
- `url` (required): Target URL
- `waitFor` (optional): `none`, `network-idle`, or `selector`
- `selector` (optional): CSS selector (required if `waitFor=selector`)
- `userAgent` (optional): Custom user agent
- `timeout` (optional): Timeout in ms (1000-120000, default 30000)

See [contracts/openapi.yaml](./contracts/openapi.yaml) for full API specification.

