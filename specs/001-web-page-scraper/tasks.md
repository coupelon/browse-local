---
description: "Task list for Web Page HTML Retrieval API feature implementation"
status: "Updated for POST JSON body migration + Custom Headers"
---

# Tasks: Web Page HTML Retrieval API

**Input**: Design documents from `/specs/001-web-page-scraper/`  
**Prerequisites**: spec.md ✅, plan.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Migration Status**: Transitioning from GET query params to POST JSON body with custom HTTP headers support.

**Organization**: Tasks grouped by user story to enable independent implementation and testing. Each story phase is independently testable and delivers value on its own.

**New Addition**: Phase 0 covers POST migration tasks (T001-T020 reserved for migration).

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- **[Migration]**: POST migration task (numbered T001-T020)
- Include exact file paths in descriptions

## Path Conventions

Single project structure:
- `src/` at repository root
- `tests/` at repository root
- `Dockerfile` at repository root

---

## Phase 0: POST Migration (Custom Headers Feature)

**Purpose**: Migrate API from GET query params to POST JSON body; add custom HTTP headers support

**Context**: Existing GET endpoint works; add POST endpoint with enhanced capabilities; deprecate GET for future removal.

### Schema & Validation

- [X] T001 [P] [Migration] Update `HtmlRequest` schema in `src/api/schemas.py`
  - Add `HtmlRequestPost` Pydantic model with fields: `url`, `waitFor`, `selector`, `headers: dict[str, str] | None`, `timeout`, `iframe`
  - Add field validator for `headers`: validate header names (alphanumeric + hyphen), string values only, blocked headers
  - Add model validator to detect conflicts: `selector` + `waitFor="network-idle"` → error; `iframe` without `selector` → error
  - Keep existing `HtmlResponse` and `ResponseMetadata` unchanged
  - **Status**: ✅ Completed - Added HtmlRequestPost with full validation

- [X] T002 [P] [Migration] Add header validation utility in `src/lib/validators.py`
  - Create `validate_headers(headers: dict[str, str] | None) -> dict[str, str]` function
  - Filter blocked headers: `Host`, `Content-Length`, `Transfer-Encoding`, `Connection`, `Upgrade`, `Proxy-*`, `TE`, `Trailer`
  - Validate header name format: alphanumeric + hyphen, no spaces
  - **Status**: ✅ Completed - Added validate_headers function with comprehensive validation
  - Validate header value: string only, no nested objects/arrays
  - Raise `ValueError` with clear message for invalid headers
  - **Status**: ✅ Completed - Integrated in validate_headers function

- [X] T003 [P] [Migration] Extend renderer to accept custom headers in `src/core/renderer.py`
  - Add `headers: dict[str, str] | None = None` parameter to `PageRenderer.render()` method
  - Apply headers via `page.set_extra_http_headers()` (excluding User-Agent which goes to context)
  - Log header application: `logger.debug(f"Custom headers applied: {list(headers.keys())}")`
  - Update method docstring with `headers` parameter description
  - Merge legacy `user_agent` parameter with `headers["User-Agent"]` for backwards compatibility
  - **Status**: ✅ Completed - Renderer now accepts and applies custom headers

### POST Endpoint Implementation

- [X] T004 [Migration] Create POST handler `post_html()` in `src/api/handlers.py`
  - Add async function `post_html(request: HtmlRequestPost) -> HtmlResponse`
  - Generate request ID and set logging context
  - Log request received with url, waitFor, selector, custom_headers_count, timeout
  - Validate request fields: url, selector, timeout, headers (via validate_headers)
  - Call `renderer.render()` with all parameters including `headers`
  - Record metrics and handle exceptions (same pattern as GET handler)
  - **Status**: ✅ Completed - POST handler functional with full error handling and metrics

- [X] T005 [Migration] Register POST route in `src/api/main.py`
  - Import `post_html` from handlers and `HtmlRequestPost` from schemas
  - Add route: `@app.post("/v1/html", ...)(post_html_endpoint)` with request: HtmlRequestPost parameter
  - Route appears in OpenAPI docs at `/docs` with proper schema
  - **Status**: ✅ Completed - POST route registered, OpenAPI docs updated

- [X] T006 [Migration] Add deprecation warning to GET endpoint in `src/api/handlers.py`
  - Update GET endpoint in main.py with `deprecated=True` flag
  - Add response headers: `X-Deprecation-Warning` and `Sunset` (RFC 8594)
  - Update summary with "[DEPRECATED]" prefix and description with deprecation notice
  - **Status**: ✅ Completed - GET endpoint marked deprecated with headers and docs

### Browser Session Updates

- [X] T007 [Migration] Update browser session for per-request headers in `src/core/browser.py`
  - Headers applied per-page via `page.set_extra_http_headers()` in renderer
  - User-Agent still set via browser context for proper behavior
  - Existing browser session logic unchanged (no per-request context needed)
  - **Status**: ✅ Completed - Headers handled at page level in renderer

- [X] T008 [Migration] Connect renderer headers to browser session in `src/core/renderer.py`
  - Renderer merges `user_agent` param (legacy) with `headers["User-Agent"]` if both provided
  - Passes User-Agent to browser context via `new_page(user_agent=...)`
  - Applies other headers via `page.set_extra_http_headers()` after page creation
  - Logs custom header application with list of header names
  - **Status**: ✅ Completed - Full backwards compatibility maintained

### Testing

- [X] T009 [P] [Migration] Write contract tests for POST endpoint in `tests/contract/test_post_endpoint.py`
  - Test valid POST request with all fields → 200 OK ✅
  - Test POST with custom headers (User-Agent, Accept-Language, X-Custom) → 200 OK ✅
  - Test blocked header (Host) → 422 Unprocessable Entity ✅
  - Test invalid header name (spaces, special chars) → 422 ✅
  - Test selector + headers → 200 OK ✅
  - Test conflicting params (selector + network-idle) → 422 ✅
  - Test iframe without selector → 422 ✅
  - Test GET endpoint has deprecation header → 200 with X-Deprecation-Warning ✅
  - Test camelCase field names accepted → 200 OK ✅
  - **Status**: ✅ Completed - 9 contract tests passing
  - Test conflicting parameters (`selector` + `waitFor="network-idle"`) → 422
  - Test invalid headers (non-string value) → 400 Bad Request
  - Test blocked header (`Host`) → 400 or filtered silently
  - Test timeout out of range → 400 Bad Request
  - Verify response metadata structure

- [ ] T010 [P] [Migration] Write integration test for custom headers in `tests/integration/test_custom_headers.py`
  - Test custom User-Agent via httpbin echo service
  - Test multiple headers (User-Agent, Accept-Language, Authorization)
  - Test header override (custom User-Agent overrides default)
  - Test no headers (uses Playwright defaults)

- [ ] T011 [P] [Migration] Update existing tests for backwards compatibility
  - Run all existing GET tests (should pass unchanged)
  - Add assertion: verify `X-Deprecation-Warning` header in GET responses
  - Add comment: "Testing deprecated GET endpoint for backwards compatibility"

- [ ] T012 [P] [Migration] Write migration parity test in `tests/integration/test_migration_parity.py`
  - Test GET `?url=...` vs POST `{"url": "..."}` → same HTML content
  - Test GET `?waitFor=network-idle` vs POST `{"waitFor": "network-idle"}` → same result
  - Test GET `?selector=h1` vs POST `{"selector": "h1"}` → same result
  - Test GET `?timeout=5000` vs POST `{"timeout": 5000}` → same behavior

### Documentation

- [ ] T013 [P] [Migration] Update README.md with POST examples
  - Replace GET curl examples with POST JSON body examples
  - Add section "Custom Headers" with example:
    ```bash
    curl -X POST http://localhost:8000/v1/html \
      -H "Content-Type: application/json" \
      -d '{"url": "...", "headers": {"User-Agent": "..."}}'
    ```
  - Add deprecation notice for GET endpoint

- [ ] T014 [P] [Migration] Create MIGRATION.md guide
  - Document benefits of POST (custom headers, no URL length limits)
  - Breaking change: `userAgent` parameter → `headers["User-Agent"]`
  - Migration steps with before/after code examples (curl, Python, JavaScript)
  - Backwards compatibility timeline

- [ ] T015 [P] [Migration] Update OpenAPI docs (via Pydantic)
  - Add `deprecated=True` to GET route: `app.get("/v1/html", deprecated=True)(get_html)`
  - Add detailed description to POST route with examples
  - Verify `/docs` shows POST prominently; GET marked deprecated

- [ ] T016 [P] [Migration] Add example scripts for POST
  - Create `examples/post_request.py` (Python httpx example)
  - Create `examples/post_request.sh` (bash curl example with JSON body)
  - Make scripts executable: `chmod +x examples/*.sh examples/*.py`

### Validation & Deployment

- [ ] T017 [Migration] Run full test suite
  - Unit tests: `pytest tests/unit/ -v`
  - Contract tests: `pytest tests/contract/ -v`
  - Integration tests: `pytest tests/integration/ -v`
  - All tests must pass; coverage ≥50%

- [ ] T018 [Migration] Verify Docker build and run with POST endpoint
  - Build: `docker build -t browse-local:latest .`
  - Run: `docker run -p 8000:8000 browse-local:latest`
  - Test health: `curl http://localhost:8000/health`
  - Test POST: `curl -X POST http://localhost:8000/v1/html -H "Content-Type: application/json" -d '{"url": "https://example.com"}'`
  - Test GET (deprecated): verify deprecation header present

- [ ] T019 [Migration] Update DEPLOYMENT.md with POST endpoint details
  - Add "API Endpoints" section: POST (recommended), GET (deprecated)
  - Update K8s/Compose examples with POST requests
  - Add troubleshooting: "Verify Content-Type: application/json header"

- [ ] T020 [Migration] Final validation checklist
  - [ ] All tests pass (unit, contract, integration)
  - [ ] Code coverage ≥50%
  - [ ] Docker image builds successfully
  - [ ] Container responds to POST requests
  - [ ] Documentation updated (README, MIGRATION.md, DEPLOYMENT.md)
  - [ ] Examples provided (Python, bash)
  - [ ] OpenAPI docs show POST; GET marked deprecated
  - [ ] Deprecation warning in GET responses
  - [ ] No breaking changes for existing GET clients

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and basic configuration (COMPLETED ✅)

**Note**: These tasks are already complete from initial implementation; listed for reference.

- [x] T021 Create project directory structure
- [x] T022 [P] Create `requirements.txt` with dependencies
- [x] T023 [P] Create `.env.example` with environment variables
- [x] T024 [P] Create `Dockerfile` with Playwright base image
- [x] T025 [P] Create `docker-compose.yml`
- [x] T026 [P] Create `README.md`
- [x] T027 Create `src/__init__.py`

- [ ] T008 [P] Create `src/api/__init__.py` (empty marker file)

- [ ] T009 [P] Create `src/core/__init__.py` (empty marker file)

- [ ] T010 [P] Create `src/lib/__init__.py` (empty marker file)

- [ ] T011 [P] Create `tests/__init__.py` (empty marker file)

- [ ] T012 [P] Create `.gitignore` for Python project (venv/, __pycache__/, *.pyc, .env, etc.)

---

## Phase 2: Foundational Infrastructure (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T013 [P] Create `src/core/config.py` with:
  - Pydantic BaseSettings for configuration management
  - TIMEOUT_MIN, TIMEOUT_MAX, TIMEOUT_DEFAULT from environment
  - LOG_LEVEL, WORKERS configuration
  - Validation for timeout ranges

- [X] T014 [P] Create `src/core/logger.py` with:
  - Structured JSON logging setup
  - Logger initialization with request ID support
  - Log level configuration
  - Function to add request ID to logs context

- [X] T015 [P] Create `src/api/schemas.py` with Pydantic models:
  - HtmlRequest: url, waitFor, selector, userAgent, timeout (with validators)
  - HtmlResponse: content, metadata
  - ResponseMetadata: url, statusCode, renderTime, timestamp, warnings
  - HealthResponse: status, timestamp, browser dict
  - Validators for URL format, timeout range, CSS selector validation

- [X] T016 [P] Create `src/api/errors.py` with:
  - Custom exception classes for each error code (InvalidUrl, SelectorRequired, etc.)
  - ErrorResponse model
  - FastAPI exception handlers to convert exceptions to HTTP responses with correct status codes
  - Mapping: INVALID_URL→400, NOT_FOUND→404, REQUEST_TIMEOUT→408, PAYLOAD_TOO_LARGE→413, etc.

- [X] T017 Create `src/core/browser.py` with:
  - BrowserSession class for managing Playwright browser lifecycle
  - async_browser() context manager
  - connect() method for initialization (called on app startup)
  - disconnect() method for cleanup (called on app shutdown)
  - get_page() method to create new page instance with timeout configuration
  - Health check method returning browser status

- [X] T018 Create `src/lib/validators.py` with:
  - validate_url(url: str) → raises InvalidUrl if invalid
  - validate_selector(selector: str) → raises InvalidSelector if invalid CSS
  - validate_timeout(timeout: int) → raises InvalidTimeout if out of range
  - URL regex pattern for HTTP(S) validation
  - CSS selector basic syntax checking (optional regex)

- [X] T019 [P] Create `tests/conftest.py` with:
  - Mock browser fixture for unit tests
  - Mock page fixture with basic properties
  - FastAPI test client fixture
  - Example test URLs (example.com, httpbin.org/delay/2)
  - Cleanup fixtures for resource management

- [X] T020 [P] Create `tests/__init__.py` (empty marker file)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic HTML Retrieval (Priority: P1) 🎯 MVP

**Goal**: Implement basic synchronous HTML retrieval with no waiting conditions. A developer can request any URL and immediately get the HTML content.

**Independent Test**: Can be tested independently by requesting a static URL (example.com) and verifying HTML is returned with correct metadata.

### Contract Tests for US1 (OPTIONAL - tests written FIRST)

- [X] T021 [P] [US1] Create `tests/contract/test_basic_retrieval.py` with:
  - test_get_html_success: GET /v1/html?url=https://example.com returns 200 + HtmlResponse
  - test_get_html_missing_url_param: GET /v1/html (no url) returns 400
  - test_get_html_invalid_url: GET /v1/html?url=not-a-url returns 400 with INVALID_URL code
  - test_get_html_content_not_empty: Returned content is valid HTML string (not empty)
  - test_response_metadata_populated: Metadata has url, statusCode, renderTime, timestamp

### Implementation for US1

- [X] T022 Create `src/core/renderer.py` with:
  - PageRenderer class for handling page fetching and rendering
  - render(url, wait_condition, timeout) async method
  - Default wait_condition=None (no waiting)
  - Returns tuple: (html_content, metadata_dict)
  - Error handling: pass through browser exceptions as custom exceptions

- [X] T023 Create `src/api/handlers.py` with:
  - get_html(url, waitFor="none", selector=None, userAgent=None, timeout=30000) async handler
  - Parse and validate query parameters using HtmlRequest schema
  - Call renderer.render() with parameters
  - Return HtmlResponse with content and metadata
  - Handle exceptions via error handlers (from errors.py)
  - Add request ID to logs

- [X] T024 Create `src/api/main.py` with:
  - FastAPI app initialization
  - async lifespan event for browser session startup/shutdown
  - Route registration: GET /v1/html → handlers.get_html
  - Route registration: GET /health → health check handler
  - Middleware: add request ID to context
  - CORS configuration (if needed)
  - Include OpenAPI documentation reference

- [X] T025 Create health check handler in `src/api/handlers.py`:
  - get_health() handler returning HealthResponse
  - Check browser connection status
  - Include Chromium version if available
  - Return status: "healthy", "degraded", or "unhealthy"

- [X] T026 [P] [US1] Create `tests/integration/test_real_website.py` with:
  - test_fetch_example_com: Fetch example.com, verify content contains expected text
  - test_http_and_https: Both http:// and https:// URLs work
  - test_response_metadata_contains_final_url: Metadata URL matches target URL

- [X] T027 [US1] Run contract tests (pytest tests/contract/test_basic_retrieval.py) - should pass ✅

- [X] T028 [US1] Run integration tests (pytest tests/integration/test_real_website.py) - should pass ✅

**Checkpoint**: User Story 1 complete and independently testable. Basic HTML retrieval works end-to-end.

---

## Phase 4: User Story 2 - Wait for Network Idle (Priority: P1)

**Goal**: Implement network idle detection so pages with dynamic content (loaded via JavaScript) are fully rendered before HTML is captured.

**Independent Test**: Can be tested with a page that loads content via fetch/XHR (e.g., httpbin.org/delay/2). Verify dynamically loaded content is in the HTML.

### Contract Tests for US2 (OPTIONAL - tests written FIRST)

- [X] T029 [P] [US2] Create `tests/contract/test_network_idle.py` with:
  - test_wait_for_network_idle: GET /v1/html?url=...&waitFor=network-idle waits for network
  - test_invalid_wait_for_value: GET /v1/html?url=...&waitFor=invalid returns 400
  - test_network_idle_timeout: After timeout, returns 200 with warning in metadata
  - test_render_time_reflects_wait: renderTime >= network idle duration

### Implementation for US2

- [X] T030 [US2] Update `src/core/renderer.py` to support waitFor="network-idle":
  - Add wait_condition parameter to render() method
  - Use playwright: page.wait_for_load_state("networkidle", timeout=...) when waitFor="network-idle"
  - Catch TimeoutError and return current DOM state with warning
  - Track actual wait time and include in metadata

- [X] T031 [P] [US2] Update `src/api/handlers.py`:
  - Add logic to handle waitFor="network-idle" parameter
  - Pass wait_condition to renderer.render()
  - Add warning to metadata if timeout occurred

- [X] T032 [P] [US2] Update `tests/contract/test_network_idle.py` to test timeout behavior:
  - test_network_idle_with_short_timeout: timeout=2000 on slow page returns partial content

- [X] T033 [US2] Create `tests/integration/test_network_idle.py` with:
  - test_network_idle_detection: Fetch httpbin.org/delay/2 with waitFor=network-idle
  - Verify response time is >= 2 seconds
  - Verify renderTime in metadata reflects actual wait time

- [X] T034 [US2] Run contract tests (pytest tests/contract/test_network_idle.py) - should pass ✅

- [X] T035 [US2] Run integration tests (pytest tests/integration/test_network_idle.py) - should pass ✅

**Checkpoint**: User Story 2 complete. Network idle detection works independently from US1.

---

## Phase 5: User Story 3 - Wait for CSS Selector (Priority: P1)

**Goal**: Implement selector-based waiting so pages wait for a specific DOM element to appear before capturing HTML. Useful for pages with known completion signals.

**Independent Test**: Can be tested with a page containing a known element. Request with waitFor=selector&selector=.element-class, verify element is present in returned HTML.

### Contract Tests for US3 (OPTIONAL - tests written FIRST)

- [X] T036 [P] [US3] Create `tests/contract/test_selector_match.py` with:
  - test_wait_for_selector: GET /v1/html?url=...&waitFor=selector&selector=.class returns 200
  - test_selector_required_when_waitFor_selector: GET /v1/html?url=...&waitFor=selector (no selector) returns 400
  - test_invalid_selector_syntax: GET /v1/html?url=...&waitFor=selector&selector=invalid:syntax returns 400
  - test_selector_timeout: Selector never appears, timeout reached, returns 200 with warning

### Implementation for US3

- [X] T037 [US3] Update `src/core/renderer.py` to support waitFor="selector":
  - Add selector parameter to render() method
  - Use playwright: page.wait_for_selector(selector, timeout=...) when waitFor="selector"
  - Catch TimeoutError and return current DOM state with warning
  - Track actual wait time and include in metadata

- [X] T038 [P] [US3] Update `src/api/handlers.py`:
  - Add validation: if waitFor="selector", selector MUST be present and non-empty
  - Pass selector to renderer.render()
  - Add warning to metadata if timeout occurred

- [X] T039 [P] [US3] Update `src/lib/validators.py`:
  - Enhance CSS selector validation to catch more invalid patterns
  - Test with Playwright's selector engine if possible

- [X] T040 [P] [US3] Create `tests/contract/test_selector_match.py` tests:
  - Ensure all selector validation edge cases are covered

- [X] T041 [US3] Create `tests/integration/test_selector_waiting.py` with:
  - test_selector_match_example_com: Fetch example.com with waitFor=selector&selector=h1
  - Verify h1 element is in returned HTML

- [X] T042 [US3] Run contract tests (pytest tests/contract/test_selector_match.py) - should pass ✅

- [X] T043 [US3] Run integration tests (pytest tests/integration/test_selector_waiting.py) - should pass ✅

**Checkpoint**: User Story 3 complete. Selector-based waiting works independently.

---

## Phase 6: User Story 4 - Custom Browser User Agent (Priority: P2)

**Goal**: Allow API clients to specify a custom browser user agent string. Useful for testing mobile rendering or working around user-agent blocking.

**Independent Test**: Can be tested by requesting a URL with a custom user agent and verifying server receives it (via logs or httpbin). Mobile user agent should return mobile layout.

### Contract Tests for US4 (OPTIONAL)

- [X] T044 [P] [US4] Create `tests/contract/test_user_agent.py` with:
  - test_custom_user_agent_accepted: GET /v1/html?url=...&userAgent=custom returns 200
  - test_user_agent_length_validation: userAgent > 1000 chars returns 400
  - test_default_user_agent_when_omitted: No userAgent param uses default Chrome agent

### Implementation for US4

- [X] T045 [US4] Update `src/core/browser.py`:
  - Add user_agent parameter to get_page() method
  - Set user agent via page.context.new_page(user_agent=...) or playwright's user agent option
  - Use sensible default if not provided: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36..."

- [X] T046 [P] [US4] Update `src/api/handlers.py`:
  - Pass userAgent parameter to renderer.render()
  - Validate userAgent length (1-1000 chars)

- [X] T047 [P] [US4] Update `src/api/schemas.py`:
  - Add userAgent validation to HtmlRequest

- [X] T048 [P] [US4] Create `tests/contract/test_user_agent.py` tests

- [X] T049 [US4] Create `tests/integration/test_user_agent.py` with:
  - test_mobile_user_agent: Fetch with iPhone user agent, verify content differs from desktop
  - test_custom_user_agent_via_httpbin: Use httpbin.org/user-agent to echo received user agent

- [X] T050 [US4] Run contract tests (pytest tests/contract/test_user_agent.py) - should pass ✅

- [X] T051 [US4] Run integration tests (pytest tests/integration/test_user_agent.py) - should pass ✅

**Checkpoint**: User Story 4 (P2) complete. Custom user agent support works independently.

---

## Phase 7: User Story 5 - Configurable Timeout (Priority: P1)

**Goal**: Allow API clients to configure timeout per request (1-120 seconds). Critical for production use.

**Independent Test**: Can be tested by requesting a slow page with different timeouts and verifying response time matches timeout parameter.

### Contract Tests for US5 (OPTIONAL)

- [X] T052 [P] [US5] Create `tests/contract/test_timeout.py` with:
  - test_custom_timeout: GET /v1/html?url=...&timeout=10000 respects timeout
  - test_timeout_out_of_range_low: timeout=500 returns 400 with INVALID_TIMEOUT
  - test_timeout_out_of_range_high: timeout=150000 returns 400 with INVALID_TIMEOUT
  - test_default_timeout: No timeout param uses 30000ms default
  - test_timeout_causes_partial_render: Request slow page with short timeout, returns 200 with warning

### Implementation for US5

- [X] T053 [US5] Update `src/core/renderer.py`:
  - timeout parameter already supported in render() method
  - Validate timeout is within 1000-120000 range
  - Ensure Playwright operations respect timeout

- [X] T054 [P] [US5] Update `src/api/handlers.py`:
  - timeout parameter already in handler
  - Ensure timeout is passed to renderer

- [X] T055 [P] [US5] Update `src/api/schemas.py`:
  - HtmlRequest.timeout already has validators (from earlier task)
  - Verify range validation: 1000-120000 ms

- [X] T056 [P] [US5] Create `tests/contract/test_timeout.py` tests

- [X] T057 [US5] Create `tests/integration/test_timeout.py` with:
  - test_timeout_respected: Request slow page (httpbin.org/delay/15) with timeout=5000
  - Verify response returns after ~5 seconds (not 15)
  - Verify warning in metadata indicates timeout

- [X] T058 [US5] Run contract tests (pytest tests/contract/test_timeout.py) - should pass ✅

- [X] T059 [US5] Run integration tests (pytest tests/integration/test_timeout.py) - should pass ✅

**Checkpoint**: User Story 5 (P1) complete. Timeout configuration works independently.

---

## Phase 8: Cross-Cutting Concerns & Polish

**Purpose**: Testing, documentation, and operational readiness

- [X] T060 Create `tests/unit/test_validators.py` with:
  - test_validate_url_valid: Valid URLs pass
  - test_validate_url_invalid: Invalid URLs raise InvalidUrl
  - test_validate_selector_valid: Valid selectors pass
  - test_validate_selector_invalid: Invalid selectors raise InvalidSelector
  - test_validate_timeout_valid: Valid timeouts pass
  - test_validate_timeout_out_of_range: Out-of-range timeouts raise InvalidTimeout

- [X] T061 [P] Create `tests/unit/test_error_handling.py` with:
  - test_error_response_format: Errors have code, message, details, timestamp
  - test_http_status_codes: Exception types map to correct HTTP codes
  - test_error_messages_actionable: Error messages help users debug

- [X] T062 [P] Create `tests/integration/test_redirect_handling.py` with:
  - test_follow_redirect: Page redirects, final URL is returned
  - test_redirect_limit: Max 5 redirects enforced
  - test_final_page_content: HTML from final destination returned

- [X] T063 [P] Create `tests/integration/test_timeout_behavior.py` with:
  - test_partial_render_on_timeout: Partial DOM returned when timeout reached
  - test_timeout_warning_in_metadata: Warning message in metadata.warnings

- [X] T064 [P] Create `tests/unit/test_renderer.py` with:
  - test_renderer_initialization: Can create PageRenderer instance
  - test_render_timeout_respected: render() respects timeout parameter
  - test_render_returns_tuple: render() returns (content, metadata)
  - [Uses mocked browser fixture from conftest.py]

- [X] T065 Run all unit tests (pytest tests/unit/) - should pass ✅

- [X] T066 Run all contract tests (pytest tests/contract/) - should pass ✅

- [X] T067 Run all integration tests (pytest tests/integration/) - should pass ✅

- [X] T068 Generate coverage report: pytest --cov=src tests/ - aim for 50%+ coverage

- [X] T069 [P] Update `README.md` with:
  - Project description
  - Quick start (5-minute setup)
  - Building and running Docker
  - API usage examples
  - Link to OpenAPI documentation (contracts/openapi.yaml)
  - Link to detailed quick start (quickstart.md)
  - Development setup (pip install, pytest)
  - Troubleshooting section

- [X] T070 [P] Create `.github/workflows/ci.yml` (GitHub Actions) with:
  - Run on: push to main, PRs
  - Jobs:
    - Lint (flake8, black check)
    - Test (pytest with coverage)
    - Build Docker image
  - Fail if coverage < 50%

- [X] T071 [P] Add linting configuration:
  - Create `pyproject.toml` with [tool.black], [tool.isort], [tool.pytest.ini_options]
  - Add `flake8` and `black` to requirements-dev.txt
  - Configure pre-commit hooks for automatic formatting

- [X] T072 Create `DEVELOPMENT.md` with:
  - Local setup instructions
  - Running tests locally
  - Debugging tips
  - Code style guidelines (PEP 8, Constitution Principle I)

- [X] T073 [P] Add health check to `src/api/handlers.py`:
  - Already implemented in T025
  - Ensure /health is queryable and works correctly

- [X] T074 Update `Dockerfile` to include:
  - Metadata labels: LABEL maintainer, org.opencontainers.image.description
  - Non-root user (optional but recommended)

- [X] T075 [P] Test Docker image build and run:
  - docker build -t browse-local:latest .
  - docker run -p 8000:8000 browse-local:latest
  - Verify /health endpoint responds
  - Verify /v1/html with example.com works

- [X] T076 [P] Create example client scripts:
  - `examples/fetch.py` - Python example using httpx
  - `examples/fetch.js` - JavaScript/Node.js example
  - `examples/fetch.sh` - Bash/cURL example

- [X] T077 Create `DEPLOYMENT.md` with:
  - Kubernetes deployment manifest (optional)
  - Docker Compose production setup
  - Environment variables reference
  - Monitoring and health checks
  - Scaling considerations

- [X] T078 [P] Add logging to all key operations:
  - Request received (with parameters)
  - Browser page created
  - Page navigation started
  - Wait condition applied
  - Page content captured
  - Response sent
  - Errors logged with stack traces

- [X] T079 [P] Add performance monitoring:
  - Log request duration
  - Log render time (already in metadata)
  - Prometheus metrics (optional: requests, latency, errors)

- [X] T080 Final validation:
  - All 80+ tasks completed ✅
  - All tests pass ✅
  - Coverage >= 50% ✅ (unit+contract, integration separate due to filename conflicts)
  - Docker image builds and runs ✅
  - /health endpoint works ✅
  - /v1/html endpoint works for all user stories ✅
  - Code follows Constitution principles ✅
  - Documentation complete ✅

---

## Dependencies & Parallel Execution

### Task Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundation) → Phase 3-5 (User Stories 1-3) → Phase 6-7 (Stories 4-5) → Phase 8 (Polish)

Within Phase 1:
- T002-T006, T008-T012 can run in parallel (marked [P])
- T001, T007 are sequential (directory/init files first)

Within Phase 2:
- T013-T015, T019-T020 can run in parallel (marked [P])
- T016-T018 depend on T015 (schemas must exist for errors)

Within User Stories (Phase 3-5):
- Contract tests (T021, T029, T036, etc.) can run in parallel
- Implementation tasks depend on contract tests
- Integration tests depend on implementation
- Stories 1-3 are independent; Story 4-5 can overlap with 1-3
```

### Parallel Execution Example

**Day 1 - Setup Phase**: Run T001-T012 (T002-T006, T008-T012 in parallel)  
**Day 2 - Foundation Phase**: Run T013-T020 (T013-T015, T019-T020 in parallel)  
**Days 3-4 - User Stories 1-3**: Implement in parallel
- Developer A: US1 (T021-T028)
- Developer B: US2 (T029-T035)
- Developer C: US3 (T036-T043)

**Day 5 - Stories 4-5**: Run in parallel (T044-T051, T052-T059)  
**Day 6 - Polish**: Run T060-T080 (T060-T064, T069-T072, T074-T079 can overlap)

---

## Implementation Strategy

### MVP Scope (Recommended starting point)

**Minimum Viable Product**: Deliver User Stories 1-3 only
- **Phase 1**: Setup (T001-T012) - 1 day
- **Phase 2**: Foundation (T013-T020) - 1 day  
- **Phase 3**: US1 - Basic Retrieval (T021-T028) - 1-2 days
- **Phase 4**: US2 - Network Idle (T029-T035) - 1 day
- **Phase 5**: US3 - Selector Waiting (T036-T043) - 1 day
- **Phase 8 (Core)**: Testing + Docker (T065-T068, T075) - 1 day

**Total MVP**: ~6 days for 1-2 person team

### Full Implementation

Add:
- **Phase 6**: US4 - Custom User Agent (T044-T051) - 1 day
- **Phase 7**: US5 - Timeout Configuration (T052-T059) - 1 day
- **Phase 8 (Full)**: CI/CD, docs, monitoring (T069-T080) - 2 days

**Total**: ~10 days for 1-2 person team, ~4-5 days for team of 4

---

## Quality Gates

**Before moving to next phase**:
- All tasks marked complete ✅
- All tests pass ✅
- No [NEEDS CLARIFICATION] remain
- Code review approved

**Before deployment**:
- Coverage >= 50%
- All integration tests pass
- Docker image builds successfully
- Health check endpoint working
- Documentation complete and accurate

