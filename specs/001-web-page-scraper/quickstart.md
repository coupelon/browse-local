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

### Example 1: Simple HTML Retrieval (POST)

Fetch HTML content from a static page (no waiting):

```bash
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","waitFor":"none","timeout":15000}'
```

**Response** (truncated):
```json
{
  "content": "<!DOCTYPE html>\n<html>\n<head>...",
  "metadata": {
    "url": "https://example.com",
    "status_code": 200,
    "duration_ms": 567,
    "wait_strategy": "none",
    "timestamp": "2025-12-14T10:30:00Z"
  }
}
```

**Time**: ~1-2 seconds

---

### Example 2: Wait for Network Idle

Fetch a page that loads content dynamically via JavaScript; wait for all network requests to complete:

```bash
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/delay/2",
    "waitFor": "network-idle",
    "timeout": 15000
  }'
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
    "status_code": 200,
    "duration_ms": 2450,
    "wait_strategy": "network-idle",
    "timestamp": "2025-12-14T10:30:02Z"
  }
}
```

**Time**: ~2-3 seconds (depends on page)

---

### Example 3: Wait for CSS Selector

Wait for a specific element to appear in the DOM before capturing HTML:

```bash
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "waitFor": "none",
    "selector": ".content",
    "timeout": 10000
  }'
```

**What happens**:
1. Page loads at `example.com`
2. Browser waits for an element matching `.content` selector to appear
3. Once found, HTML is captured

**Response**:
```json
{
  "content": "<!DOCTYPE html>\n<html>...",
  "metadata": {
    "url": "https://example.com",
    "status_code": 200,
    "duration_ms": 789,
    "wait_strategy": "none",
    "timestamp": "2025-12-14T10:30:00Z"
  }
}
```

**Time**: ~1-2 seconds (or up to 10s timeout)

---

### Example 4: Custom Headers

Send custom HTTP headers (User-Agent, cookies, authorization, etc.):

```bash
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "waitFor": "none",
    "headers": {
      "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)",
      "Accept-Language": "fr-FR,fr;q=0.9",
      "Cookie": "session_id=abc123"
    },
    "timeout": 15000
  }'
```

**What happens**:
- Page is fetched with custom headers
- Server may return mobile-optimized or localized HTML
- Cookies are sent with the request

**Response**: Same structure, but content may differ based on headers

---

---

## Error Examples

### Error 1: Invalid URL

```bash
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{"url":"not-a-url"}'
```

**Response** (HTTP 422 - Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "url"],
      "msg": "URL must be a valid HTTP or HTTPS URL",
      "input": "not-a-url"
    }
  ]
}
```

---

### Error 2: Selector Not Found (Returns HTML for Debugging)

When a CSS selector times out or is not found, the API **returns HTTP 404** but includes the page HTML for debugging:

```bash
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "selector": ".nonexistent-element",
    "timeout": 2000
  }'
```

**Response** (HTTP 404):
```json
{
  "detail": {
    "content": "<!DOCTYPE html>\n<html>...<full page HTML>...",
    "metadata": {
      "url": "https://example.com/",
      "status_code": 404,
      "duration_ms": 2050,
      "wait_strategy": "none",
      "selector_error": "Selector '.nonexistent-element' not found within 2000ms timeout",
      "partial_content": true,
      "timestamp": "2025-12-14T10:30:00Z"
    }
  }
}
```

**Key Points**:
- HTTP status: **404** (error)
- Response contains full HTML in `detail.content`
- Error details in `detail.metadata.selector_error`
- `partial_content: true` indicates incomplete rendering
- Useful for debugging: analyze HTML structure to refine your selector

---

### Error 3: Blocked Header

```bash
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "headers": {
      "Host": "evil.com"
    }
  }'
```

**Response** (HTTP 422):
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "headers"],
      "msg": "Header 'Host' is not allowed for security reasons",
      "input": {"Host": "evil.com"}
    }
  ]
}
```

---

## Using the API Programmatically

### Python Example (with httpx)

```python
import httpx
import json

async def fetch_page_html(url: str, wait_for: str = "none", selector: str = None):
    """Fetch HTML from a page using POST endpoint."""
    async with httpx.AsyncClient() as client:
        payload = {
            "url": url,
            "waitFor": wait_for,
            "timeout": 30000
        }
        if selector:
            payload["selector"] = selector
        
        response = await client.post(
            "http://localhost:8000/v1/html",
            json=payload
        )
        
        if response.status_code == 404:
            # Selector not found, but HTML is available for debugging
            error_data = response.json()
            print(f"Warning: {error_data['detail']['metadata']['selector_error']}")
            return error_data['detail']['content']
        
        response.raise_for_status()
        return response.json()

# Usage
result = await fetch_page_html("https://example.com", wait_for="network-idle")
print(f"Rendered in {result['metadata']['duration_ms']}ms")
print(f"HTML length: {len(result['content'])} characters")
```

### JavaScript/Node.js Example (with fetch)

```javascript
async function fetchPageHtml(url, waitFor = "none", selector = null) {
  const payload = {
    url: url,
    waitFor: waitFor,
    timeout: 30000
  };
  
  if (selector) {
    payload.selector = selector;
  }

  const response = await fetch("http://localhost:8000/v1/html", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (response.status === 404) {
    // Selector not found, but HTML is available
    const errorData = await response.json();
    console.warn(`Selector error: ${errorData.detail.metadata.selector_error}`);
    return errorData.detail.content;
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API error: ${JSON.stringify(error)}`);
  }

  return await response.json();
}

// Usage
const result = await fetchPageHtml("https://example.com", "network-idle");
console.log(`Rendered in ${result.metadata.duration_ms}ms`);
```

### cURL with Piping

Extract just the HTML content using `jq`:

```bash
curl -s -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}' \
  | jq -r '.content' > page.html
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
   curl -X POST http://localhost:8000/v1/html \
     -H "Content-Type: application/json" \
     -d '{"url":"https://example.com","timeout":3000}'
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

**Symptom**: HTTP 404 returned with `selector_error` in metadata

**Solutions**:
- Verify selector with browser DevTools: Open page in browser, use DevTools to test selector
- Check JavaScript execution: If selector is added by JS, ensure `waitFor=network-idle` or higher timeout
- Use more generic selector: `.content` instead of `.article-content-loaded-by-js`
- Examine returned HTML: The error response includes full HTML in `detail.content` for debugging

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
| POST | `/v1/html` | Fetch and render HTML with custom headers |
| GET | `/health` | Health check |
| GET | `/metrics` | Performance metrics |

**POST Body Parameters**:
- `url` (required): Target URL
- `waitFor` (optional): `none`, `network-idle`, or `selector`
- `selector` (optional): CSS selector to wait for
- `iframe` (optional): Iframe selector for nested content
- `headers` (optional): Custom HTTP headers (object)
- `timeout` (optional): Timeout in ms (1000-120000, default 30000)

See [contracts/openapi.yaml](./contracts/openapi.yaml) for full API specification.

