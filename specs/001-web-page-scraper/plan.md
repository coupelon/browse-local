# Implementation Plan: Web Page HTML Retrieval API

**Branch**: `001-web-page-scraper` | **Date**: 2025-12-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-web-page-scraper/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a containerized HTTP API that retrieves HTML content from web pages with advanced rendering support. The API accepts a URL and optional wait conditions (network idle, CSS selector match) and returns the rendered HTML. The entire application must run in a Docker container using Playwright with embedded Chromium, auto-starting the API on container startup. MVP includes basic retrieval, network-idle waiting, and selector-based waiting; P2 enhancements add custom user agents and fine-grained timeout control.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Playwright, Pydantic, python-dotenv  
**Storage**: N/A (stateless API, optional file-based logging)  
**Testing**: pytest, pytest-asyncio  
**Target Platform**: Docker container (Linux-based, x86_64)  
**Project Type**: Single backend API service  
**Performance Goals**: Basic retrieval p95 < 2s, network-idle p95 < 10s, support ≥10 concurrent requests  
**Constraints**: Timeout ranges 1-120 seconds (configurable), max HTML response 50MB, single-threaded async (uvicorn workers configurable)  
**Scale/Scope**: Initial scope is MVP (P1 features); supports eventual horizontal scaling via container orchestration

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle I - Code Quality & Maintainability**: ✅ PASS
- Clear API endpoints with explicit parameters
- Linting and formatting enforced via pre-commit hooks (to be configured)
- Complexity targets: functions < 50 lines, cyclomatic complexity < 10

**Principle II - Test-Driven Development (NON-NEGOTIABLE)**: ✅ PASS - WITH NOTE
- TDD mandatory: All tasks include contract tests, integration tests, and unit tests
- Coverage target: 80% minimum on handlers and core logic (explicitly in SC-008)
- Test types: Contract tests for API endpoints, integration tests for browser rendering, unit tests for utilities
- **Note**: Playwright browser instances add complexity; test infrastructure documented in research.md Phase 0

**Principle III - API Design & Clear Contracts**: ✅ PASS
- OpenAPI 3.0 documentation required (Phase 1 output: contracts/openapi.yaml)
- Request/Response schemas defined in JSON Schema format
- Consistent error response structure with code, message, details
- Versioning: path-based `/v1/html`
- No breaking changes planned for MVP

**Principle IV - Performance & Scalability Standards**: ✅ PASS
- Latency targets defined: basic < 2s (p95), network-idle < 10s (p95) (SC-001, SC-002)
- Timeout limits: 1-120 seconds configurable
- Resource limits: max 50MB HTML response
- No database queries (N/A), caching via browser memory (Playwright handles)

**Principle V - User Experience Consistency**: ✅ PASS
- Response envelope: ISO 8601 timestamps, consistent metadata
- Error responses: standard format with actionable messages
- Default timeout: 30 seconds (reasonable middle ground)
- Pagination: N/A (not a list endpoint)

**Overall Status**: ✅ GATE PASSED - No violations. Proceed to Phase 0.

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

```text
src/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization and startup
│   ├── handlers.py          # HTTP GET /v1/html handler
│   ├── schemas.py           # Pydantic request/response models
│   └── errors.py            # Custom exception classes and error handling
├── core/
│   ├── __init__.py
│   ├── browser.py           # Playwright browser session management
│   ├── renderer.py          # Page rendering logic (wait conditions, timeouts)
│   ├── config.py            # Configuration from environment variables
│   └── logger.py            # Structured JSON logging setup
├── lib/
│   ├── __init__.py
│   └── validators.py        # URL validation, CSS selector validation

tests/
├── conftest.py              # pytest fixtures (mock Playwright, test fixtures)
├── contract/
│   ├── test_basic_retrieval.py         # Contract: GET /v1/html returns HTML
│   ├── test_network_idle.py            # Contract: waitFor=network-idle
│   └── test_selector_match.py          # Contract: waitFor=selector with selector param
├── integration/
│   ├── test_real_website.py            # Integration: test against real websites
│   ├── test_timeout_behavior.py        # Integration: timeout handling
│   └── test_redirect_handling.py       # Integration: redirect following
└── unit/
    ├── test_validators.py              # Unit: URL/selector validation
    ├── test_renderer.py                # Unit: rendering logic with mocked browser
    └── test_error_handling.py          # Unit: error response formatting

Dockerfile                   # Docker image with Playwright + Chromium
docker-compose.yml          # Local development orchestration (optional)
requirements.txt            # Python dependencies
.env.example                # Environment variables template
README.md                   # Project overview and quick start
```

**Structure Decision**: Single backend API service using async FastAPI. All rendering logic encapsulated in `core/renderer.py`. Browser session management (Playwright) isolated in `core/browser.py` for testability. Tests organized by type (contract, integration, unit) per Constitution Principle II requirements. Dockerfile ensures 100% containerization with embedded Chromium and auto-startup.

## Complexity Tracking

> **No Constitution violations—this section is empty.**

All decisions align with Constitution principles. No complex patterns or workarounds required. FastAPI + Playwright are standard, well-supported choices for this use case.
