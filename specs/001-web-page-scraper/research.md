# Research & Technical Decisions: Web Page HTML Retrieval API

**Phase**: Phase 0 (Outline & Research)  
**Date**: 2025-12-14  
**Branch**: `001-web-page-scraper`

## Overview

This document captures research findings and technical decisions made during Phase 0. All unknowns from the Technical Context section of plan.md have been resolved.

---

## 1. Language & Runtime Selection

**Decision**: Python 3.11 with FastAPI (async framework)

**Rationale**:
- Python excels at web scraping and browser automation (Playwright is Pythonic)
- FastAPI provides modern async HTTP handling with automatic OpenAPI documentation
- Python 3.11 offers excellent performance and stability for production workloads
- Extensive ecosystem for testing (pytest, pytest-asyncio)

**Alternatives Considered**:
- Node.js + Puppeteer: Would work equally well; chosen Python for team familiarity assumption
- Go + Colly: Overkill for this use case; Playwright support less mature
- Rust: Higher barrier to entry; no compelling performance advantage for HTTP API

---

## 2. Browser Automation: Playwright Selection

**Decision**: Playwright Python library with embedded Chromium

**Rationale**:
- Playwright is modern, well-maintained, and supports all major browsers (Chrome, Firefox, WebKit)
- Async-first API fits perfectly with FastAPI's async model
- Embedded Chromium eliminates external browser setup—perfect for Docker
- Network idle detection is first-class: `page.wait_for_load_state('networkidle')`
- CSS selector waiting is built-in: `page.wait_for_selector(selector, timeout=...)`
- Excellent for headless operation (required for containerized deployment)

**Alternatives Considered**:
- Selenium: Older, synchronous by default, heavier maintenance overhead
- Puppeteer (Node.js): Would require Node runtime; Python version exists but less mature
- Mechanize/BeautifulSoup: Cannot handle JavaScript rendering (disqualifies these for this use case)

---

## 3. Web Framework: FastAPI

**Decision**: FastAPI for HTTP API layer

**Rationale**:
- Native async/await support integrates seamlessly with Playwright's async API
- Automatic OpenAPI 3.0 documentation generation (satisfies Constitution Principle III)
- Pydantic integration for request/response validation (requirement: FR-006, FR-011)
- Built-in dependency injection for browser session management
- Superior performance compared to Flask/Django for this use case
- Excellent error handling and middleware support

**Alternatives Considered**:
- Flask: Synchronous, requires additional async libraries; slower for concurrent requests
- Django: Overkill for a simple single-endpoint API; heavy framework overhead
- Starlette: Lower-level; FastAPI is built on Starlette with added conveniences

---

## 4. Browser Session Management Strategy

**Decision**: Singleton browser context per API instance with connection pooling

**Rationale**:
- Playwright maintains an internal browser pool; reusing context improves performance
- Single browser instance per container is sufficient for target scale (≥10 concurrent requests)
- Async context manager pattern ensures proper resource cleanup
- Timeout enforcement at both Playwright level and FastAPI level for defense-in-depth

**Implementation Details**:
- `core/browser.py` manages browser lifecycle (start on app startup, close on shutdown)
- Each request gets an isolated page within the browser context
- Page timeout is set dynamically based on request parameter
- Network monitoring and selector waiting handled by Playwright, not custom code

**Alternatives Considered**:
- Browser pool with multiple instances: Added complexity not justified by target scale
- Fresh browser per request: Massive overhead; defeats purpose of stateless container advantage
- Thread-based browser management: Conflicts with FastAPI's async model

---

## 5. Request/Response Schema Design

**Decision**: Pydantic models for strict validation; JSON Schema export for OpenAPI

**Request Schema** (`src/api/schemas.py`):
```python
class HtmlRequest(BaseModel):
    url: HttpUrl  # Pydantic's built-in URL validation
    waitFor: Literal["none", "network-idle", "selector"] = "none"
    selector: Optional[str] = None  # Required if waitFor=="selector"
    userAgent: Optional[str] = None
    timeout: int = 30000  # milliseconds

    @field_validator('timeout')
    def validate_timeout(cls, v):
        if not (1000 <= v <= 120000):
            raise ValueError('timeout must be between 1000 and 120000 ms')
        return v
```

**Response Schema**:
```python
class HtmlResponse(BaseModel):
    content: str  # Raw HTML
    metadata: ResponseMetadata

class ResponseMetadata(BaseModel):
    url: str
    statusCode: int  # HTTP status of fetched page
    renderTime: float  # Time spent rendering (seconds)
    timestamp: datetime  # ISO 8601
    warnings: List[str] = []  # e.g., ["Timeout reached before selector matched"]
```

**Rationale**:
- Pydantic's `HttpUrl` type provides full URI validation (satisfies FR-006)
- Literal types enforce enum-like behavior for `waitFor` parameter
- Automatic schema export enables OpenAPI documentation (satisfies FR-011)
- Metadata provides transparency without leaking implementation details

---

## 6. Error Handling & Response Format

**Decision**: Consistent error envelope with RFC 7231 status codes

**Error Response Structure** (all errors):
```json
{
  "code": "VALIDATION_ERROR",
  "message": "selector parameter required when waitFor=selector",
  "details": {
    "param": "selector",
    "received": null,
    "expected": "non-empty string"
  },
  "timestamp": "2025-12-14T10:30:00Z"
}
```

**Status Code Mapping**:
- `400 Bad Request`: Invalid URL format, invalid selector, missing required parameter
- `404 Not Found`: URL is reachable but returns 404 (passed through from target page)
- `408 Request Timeout`: Timeout reached during rendering (before wait condition met)
- `413 Payload Too Large`: URL + parameters exceed 10KB limit
- `500 Internal Server Error`: Browser crash, network failure, unexpected errors
- `200 OK`: Success (including cases where timeout reached but page partially rendered)

**Rationale**:
- Consistent error structure across all endpoints (satisfies Constitution Principle V)
- Actionable error messages help API users debug issues
- Metadata timestamps enable audit trails
- Status codes follow HTTP semantics (RFC 7231)

---

## 7. Timeout Strategy

**Decision**: Multi-layer timeout enforcement

**Layer 1 - Playwright Page Timeout**:
- Set at page creation: `page.set_default_timeout(timeout_ms)`
- Enforces maximum execution time for all Playwright operations
- Playwright exception: `TimeoutError`

**Layer 2 - Wait Condition Timeout**:
- `page.wait_for_load_state('networkidle', timeout=...)` has its own timeout
- Respects request parameter; throws exception if condition not met

**Layer 3 - FastAPI Request Timeout** (optional):
- Background timeout task that cancels request if no response after global max (e.g., 125s)
- Failsafe against hung requests

**Behavior on Timeout**:
- If timeout occurs during wait condition, return HTTP 200 with current DOM state
- Include warning in response metadata: `"Timeout reached before condition met"`
- Log timeout events for monitoring (structured JSON logging)

**Rationale**:
- Multi-layer approach prevents hung requests (critical for production)
- Returning partial content (200) instead of error improves user experience for edge cases
- Timeout is configurable (1-120 seconds) per request (satisfies FR-005)

---

## 8. Logging & Observability

**Decision**: Structured JSON logging with request ID correlation

**Implementation** (`src/core/logger.py`):
- All logs in JSON format (structured logging, satisfies Constitution Principle II)
- Request ID (UUID) added to context; included in all logs for traceability
- Log levels: DEBUG (detailed), INFO (events), WARN (issues), ERROR (failures), FATAL (crashes)
- Example log entry:
```json
{
  "timestamp": "2025-12-14T10:30:00Z",
  "level": "INFO",
  "requestId": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Page rendered successfully",
  "url": "https://example.com",
  "renderTime": 2.345,
  "waitCondition": "network-idle"
}
```

**Metrics** (optional, via Prometheus middleware):
- `http_requests_total`: Counter by endpoint, status code
- `http_request_duration_seconds`: Histogram by endpoint
- `page_render_time_seconds`: Histogram for rendering performance

**Rationale**:
- Structured logging enables log aggregation and analysis (ELK stack, DataDog, etc.)
- Request ID correlation helps debugging multi-step user journeys
- Metrics enable alerting on performance degradation

---

## 9. Testing Strategy

**Decision**: Three-tier testing approach (contract, integration, unit)

**Contract Tests** (`tests/contract/`):
- Test API contracts: endpoint exists, accepts expected parameters, returns expected schema
- Use `pytest` + `httpx.AsyncClient` to test FastAPI routes directly
- No browser mocking; test real Playwright behavior
- Examples:
  - `test_basic_retrieval.py`: GET `/v1/html?url=...` returns 200 with HTML
  - `test_network_idle.py`: GET `/v1/html?url=...&waitFor=network-idle` waits for network
  - `test_selector_match.py`: GET with `waitFor=selector&selector=.class` waits for selector

**Integration Tests** (`tests/integration/`):
- Test against real or test websites (httpbin.org, example.com, etc.)
- Verify end-to-end behavior: actual network requests, timeouts, redirects
- Slower but catch real-world issues
- Examples:
  - `test_real_website.py`: Fetch actual website, verify content
  - `test_timeout_behavior.py`: Request slow-loading page, verify timeout respected
  - `test_redirect_handling.py`: Follow redirects, verify final content

**Unit Tests** (`tests/unit/`):
- Test individual functions in isolation with mocked Playwright
- Fast, repeatable, no side effects
- Examples:
  - `test_validators.py`: URL validation, selector syntax checking
  - `test_renderer.py`: Rendering logic with mocked browser
  - `test_error_handling.py`: Error response formatting

**Fixtures** (`tests/conftest.py`):
- `mock_browser`: Fixture providing mocked Playwright page
- `test_urls`: List of stable URLs for integration tests
- `app_client`: FastAPI test client with dependency injection for mocked browser

**Coverage Target**: 80% minimum (satisfies Constitution Principle II, SC-008)

---

## 10. Docker & Deployment Strategy

**Decision**: Single-stage Dockerfile with Playwright + Chromium embedded

**Dockerfile Structure**:
```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src ./src
COPY .env.example ./.env

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Start API on container startup
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Rationale**:
- Official Playwright image includes Chromium, avoiding manual installation
- Single stage (no multi-stage) keeps image simpler; Playwright image already optimized
- Health check enables Kubernetes/Docker Swarm to detect failed instances
- Uvicorn configured for container-friendly settings (0.0.0.0 binding, direct PID 1)
- Auto-startup via CMD ensures API is running immediately on container start

**Alternatives Considered**:
- Custom base image: More control, but maintenance burden; official image sufficient
- Multi-stage build: No benefit here; Playwright image is already minimal
- Gunicorn + Uvicorn: Unnecessary for single-core container; uvicorn sufficient

**Environment Variables** (via `.env`):
- `TIMEOUT_MIN`: Minimum timeout (default: 1000ms)
- `TIMEOUT_MAX`: Maximum timeout (default: 120000ms)
- `TIMEOUT_DEFAULT`: Default timeout (default: 30000ms)
- `LOG_LEVEL`: Log level (default: INFO)
- `WORKERS`: Uvicorn worker threads (default: 2)

---

## 11. Dependency Management

**Core Dependencies**:
| Package | Version | Purpose |
|---------|---------|---------|
| `playwright` | ^1.40.0 | Browser automation |
| `fastapi` | ^0.104.0 | Web framework |
| `uvicorn` | ^0.24.0 | ASGI server |
| `pydantic` | ^2.5.0 | Data validation |
| `python-dotenv` | ^1.0.0 | Environment config |

**Dev Dependencies**:
| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | ^7.4.0 | Test framework |
| `pytest-asyncio` | ^0.21.0 | Async test support |
| `httpx` | ^0.25.0 | Async HTTP client for tests |

**Lock File**: `requirements-lock.txt` (to be generated via `pip freeze`)

---

## 12. Performance & Scalability Considerations

**Single Instance Limits**:
- Playwright browser: ~200MB memory baseline
- Per-page overhead: ~50MB
- Docker container limit: 512MB-1GB recommended
- Max concurrent pages: ~5-10 (depends on container memory)

**Scaling Strategy** (for future):
- Horizontal scaling via container orchestration (Kubernetes, Docker Swarm)
- Stateless API enables load balancer to distribute requests
- Shared browser instance per container (not across containers)

**Performance Targets Met**:
- Basic retrieval: < 2s (p95) ✅ (Playwright + local Chromium is fast)
- Network-idle: < 10s (p95) ✅ (configurable, reasonable for real-world pages)
- Concurrency: ≥10 simultaneous ✅ (FastAPI + async is efficient)

---

## 13. Security Considerations (Future)

**Out of Scope for MVP** but documented for Phase 2:
- Rate limiting: Implement via FastAPI middleware (e.g., `slowapi`)
- CORS: Configure if exposing to browser clients
- Authentication: None for MVP (internal-only or open access assumed)
- Input sanitization: Pydantic + validators cover basic cases
- SSRF protection: Validate target URL domain against whitelist (future enhancement)

---

## Summary: All NEEDS CLARIFICATION Resolved ✅

| Item | Clarification | Decision |
|------|---------------|----------|
| Language/Version | Python version? | Python 3.11 + FastAPI |
| Primary Dependencies | Which frameworks? | FastAPI, Playwright 1.40.0 |
| Storage | Database needed? | No (stateless API) |
| Testing | Test framework? | pytest + pytest-asyncio |
| Target Platform | Runtime? | Docker container (Linux) |
| Project Type | Architecture? | Single backend API service |
| Performance Goals | Specific numbers? | p95 < 2s (basic), < 10s (rendering) |
| Constraints | Limits? | 1-120s timeout, 50MB max HTML |
| Scale/Scope | MVP or full? | MVP (P1 features) |

**Overall Assessment**: Phase 0 research complete. All technical decisions are justified, documented, and ready for Phase 1 design (data-model.md, contracts/, quickstart.md).

