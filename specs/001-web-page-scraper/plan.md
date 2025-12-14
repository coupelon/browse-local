# Implementation Plan: Web Page HTML Retrieval API

**Branch**: `001-web-page-scraper` | **Date**: 2025-12-14 | **Spec**: `/specs/001-web-page-scraper/spec.md`
**Input**: Feature specification from `/specs/001-web-page-scraper/spec.md`

**Status**: Phase 0 Planning - API migration from GET query params to POST with JSON body and custom HTTP headers

## Summary

Web Page HTML Retrieval API using Playwright for browser automation and content rendering. Currently implemented as GET endpoint with query parameters; transitioning to POST endpoint with JSON request body to support custom HTTP headers and improved parameter passing. Key change: consolidate all parameters (url, waitFor, selector, headers, timeout) into a single JSON payload; custom HTTP headers replace and supersede the userAgent parameter.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, Playwright (Chromium), Pydantic, httpx
**Storage**: None (stateless API)
**Testing**: pytest + pytest-asyncio, httpx AsyncClient, fixture-based test client
**Target Platform**: Linux Docker container (OCI-compliant)
**Project Type**: Single web service (async HTTP API)
**Performance Goals**: <2s p95 basic retrieval, <10s p95 with network-idle, ≥10 concurrent requests
**Constraints**: Payload unrestricted (FR-012 removed), timeout 1000–120000ms, selector validation per CSS spec
**Scale/Scope**: Single-tenant, stateless, ~50 routes (currently /v1/html, /health, /metrics)

**Current State**:
- Existing endpoint: `GET /v1/html?url=...&waitFor=...&selector=...&userAgent=...&timeout=...`
- **New approach**: `POST /v1/html` with JSON body containing:
  - `url` (string, required): Target URL
  - `waitFor` (string, optional): "none" | "network-idle"
  - `selector` (string, optional): CSS selector to wait for
  - `headers` (object, optional): Custom HTTP headers (replaces userAgent parameter)
  - `timeout` (integer, optional): Timeout in milliseconds, default 30000
- Custom headers are merged with Playwright's default headers; replaces dedicated userAgent parameter
- All parameters validated via Pydantic models
- Structured JSON logging with request IDs
- Docker containerized with health checks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Principle I (Code Quality)**: Readability, naming, DRY, complexity limits, linting configured.  
✅ **Principle II (Test-Driven Development)**: Unit/contract/integration tests; ≥76% coverage (target 80%); pytest with fixtures.  
✅ **Principle III (API Design & Contracts)**: OpenAPI spec in `/contracts/openapi.yaml`; Pydantic models enforce schema.  
✅ **Principle IV (Performance & Scalability)**: Async FastAPI, concurrent test validation; metrics endpoint tracks request times.  
✅ **Principle V (UX Consistency)**: Error responses consistent; metadata in all responses; docs at `/docs`.

**No violations identified. Proceed to Phase 0 research.**

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

**Selected**: Single project structure

```text
src/
├── api/
│   ├── main.py         # FastAPI app, route registration
│   ├── handlers.py     # Endpoint handlers (post_html, get_health, get_metrics)
│   ├── schemas.py      # Pydantic models (HtmlRequest, HtmlResponse, etc.)
│   └── errors.py       # Custom error classes and exception handlers
├── core/
│   ├── browser.py      # Browser session lifecycle (Playwright)
│   ├── renderer.py     # Page rendering logic, selector waiting, header passing
│   ├── logger.py       # Structured JSON logging with request context
│   └── metrics.py      # Request metrics collection and aggregation
└── lib/
    └── validators.py   # URL, selector, timeout, header validation

tests/
├── contract/           # API contract tests (schema validation, error codes)
├── integration/        # End-to-end tests (real browser, real URLs)
└── unit/               # Unit tests (validators, error handling, mocks)
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

No violations identified; standard development practices apply.| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
