---
description: "Task list for Web Page HTML Retrieval API feature implementation"
---

# Tasks: Web Page HTML Retrieval API

**Input**: Design documents from `/specs/001-web-page-scraper/`  
**Prerequisites**: spec.md ✅, plan.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Organization**: Tasks grouped by user story to enable independent implementation and testing. Each story phase is independently testable and delivers value on its own.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project structure:
- `src/` at repository root
- `tests/` at repository root
- `Dockerfile` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and basic configuration

- [ ] T001 Create project directory structure (`src/`, `src/api/`, `src/core/`, `src/lib/`, `tests/`, `tests/contract/`, `tests/integration/`, `tests/unit/`)

- [ ] T002 [P] Create `requirements.txt` with dependencies: fastapi==0.104.0, playwright==1.40.0, pydantic==2.5.0, python-dotenv==1.0.0, uvicorn==0.24.0, pytest==7.4.0, pytest-asyncio==0.21.0, httpx==0.25.0

- [ ] T003 [P] Create `.env.example` with environment variables: TIMEOUT_MIN, TIMEOUT_MAX, TIMEOUT_DEFAULT, LOG_LEVEL, WORKERS

- [ ] T004 [P] Create `Dockerfile` with:
  - Base image: mcr.microsoft.com/playwright/python:v1.40.0-jammy
  - WORKDIR /app
  - Copy requirements.txt and install dependencies
  - Copy src/ to /app/src/
  - EXPOSE 8000
  - HEALTHCHECK pointing to /health endpoint
  - CMD: uvicorn src.api.main:app --host 0.0.0.0 --port 8000

- [ ] T005 [P] Create `docker-compose.yml` with service configuration for local development

- [ ] T006 [P] Create `README.md` with project overview, quick start, and links to API documentation

- [ ] T007 Create `src/__init__.py` (empty marker file)

- [ ] T008 [P] Create `src/api/__init__.py` (empty marker file)

- [ ] T009 [P] Create `src/core/__init__.py` (empty marker file)

- [ ] T010 [P] Create `src/lib/__init__.py` (empty marker file)

- [ ] T011 [P] Create `tests/__init__.py` (empty marker file)

- [ ] T012 [P] Create `.gitignore` for Python project (venv/, __pycache__/, *.pyc, .env, etc.)

---

## Phase 2: Foundational Infrastructure (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T013 [P] Create `src/core/config.py` with:
  - Pydantic BaseSettings for configuration management
  - TIMEOUT_MIN, TIMEOUT_MAX, TIMEOUT_DEFAULT from environment
  - LOG_LEVEL, WORKERS configuration
  - Validation for timeout ranges

- [ ] T014 [P] Create `src/core/logger.py` with:
  - Structured JSON logging setup
  - Logger initialization with request ID support
  - Log level configuration
  - Function to add request ID to logs context

- [ ] T015 [P] Create `src/api/schemas.py` with Pydantic models:
  - HtmlRequest: url, waitFor, selector, userAgent, timeout (with validators)
  - HtmlResponse: content, metadata
  - ResponseMetadata: url, statusCode, renderTime, timestamp, warnings
  - HealthResponse: status, timestamp, browser dict
  - Validators for URL format, timeout range, CSS selector validation

- [ ] T016 [P] Create `src/api/errors.py` with:
  - Custom exception classes for each error code (InvalidUrl, SelectorRequired, etc.)
  - ErrorResponse model
  - FastAPI exception handlers to convert exceptions to HTTP responses with correct status codes
  - Mapping: INVALID_URL→400, NOT_FOUND→404, REQUEST_TIMEOUT→408, PAYLOAD_TOO_LARGE→413, etc.

- [ ] T017 Create `src/core/browser.py` with:
  - BrowserSession class for managing Playwright browser lifecycle
  - async_browser() context manager
  - connect() method for initialization (called on app startup)
  - disconnect() method for cleanup (called on app shutdown)
  - get_page() method to create new page instance with timeout configuration
  - Health check method returning browser status

- [ ] T018 Create `src/lib/validators.py` with:
  - validate_url(url: str) → raises InvalidUrl if invalid
  - validate_selector(selector: str) → raises InvalidSelector if invalid CSS
  - validate_timeout(timeout: int) → raises InvalidTimeout if out of range
  - URL regex pattern for HTTP(S) validation
  - CSS selector basic syntax checking (optional regex)

- [ ] T019 [P] Create `tests/conftest.py` with:
  - Mock browser fixture for unit tests
  - Mock page fixture with basic properties
  - FastAPI test client fixture
  - Example test URLs (example.com, httpbin.org/delay/2)
  - Cleanup fixtures for resource management

- [ ] T020 [P] Create `tests/__init__.py` (empty marker file)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic HTML Retrieval (Priority: P1) 🎯 MVP

**Goal**: Implement basic synchronous HTML retrieval with no waiting conditions. A developer can request any URL and immediately get the HTML content.

**Independent Test**: Can be tested independently by requesting a static URL (example.com) and verifying HTML is returned with correct metadata.

### Contract Tests for US1 (OPTIONAL - tests written FIRST)

- [ ] T021 [P] [US1] Create `tests/contract/test_basic_retrieval.py` with:
  - test_get_html_success: GET /v1/html?url=https://example.com returns 200 + HtmlResponse
  - test_get_html_missing_url_param: GET /v1/html (no url) returns 400
  - test_get_html_invalid_url: GET /v1/html?url=not-a-url returns 400 with INVALID_URL code
  - test_get_html_content_not_empty: Returned content is valid HTML string (not empty)
  - test_response_metadata_populated: Metadata has url, statusCode, renderTime, timestamp

### Implementation for US1

- [ ] T022 Create `src/core/renderer.py` with:
  - PageRenderer class for handling page fetching and rendering
  - render(url, wait_condition, timeout) async method
  - Default wait_condition=None (no waiting)
  - Returns tuple: (html_content, metadata_dict)
  - Error handling: pass through browser exceptions as custom exceptions

- [ ] T023 Create `src/api/handlers.py` with:
  - get_html(url, waitFor="none", selector=None, userAgent=None, timeout=30000) async handler
  - Parse and validate query parameters using HtmlRequest schema
  - Call renderer.render() with parameters
  - Return HtmlResponse with content and metadata
  - Handle exceptions via error handlers (from errors.py)
  - Add request ID to logs

- [ ] T024 Create `src/api/main.py` with:
  - FastAPI app initialization
  - async lifespan event for browser session startup/shutdown
  - Route registration: GET /v1/html → handlers.get_html
  - Route registration: GET /health → health check handler
  - Middleware: add request ID to context
  - CORS configuration (if needed)
  - Include OpenAPI documentation reference

- [ ] T025 Create health check handler in `src/api/handlers.py`:
  - get_health() handler returning HealthResponse
  - Check browser connection status
  - Include Chromium version if available
  - Return status: "healthy", "degraded", or "unhealthy"

- [ ] T026 [P] [US1] Create `tests/integration/test_real_website.py` with:
  - test_fetch_example_com: Fetch example.com, verify content contains expected text
  - test_http_and_https: Both http:// and https:// URLs work
  - test_response_metadata_contains_final_url: Metadata URL matches target URL

- [ ] T027 [US1] Run contract tests (pytest tests/contract/test_basic_retrieval.py) - should pass ✅

- [ ] T028 [US1] Run integration tests (pytest tests/integration/test_real_website.py) - should pass ✅

**Checkpoint**: User Story 1 complete and independently testable. Basic HTML retrieval works end-to-end.

---

## Phase 4: User Story 2 - Wait for Network Idle (Priority: P1)

**Goal**: Implement network idle detection so pages with dynamic content (loaded via JavaScript) are fully rendered before HTML is captured.

**Independent Test**: Can be tested with a page that loads content via fetch/XHR (e.g., httpbin.org/delay/2). Verify dynamically loaded content is in the HTML.

### Contract Tests for US2 (OPTIONAL - tests written FIRST)

- [ ] T029 [P] [US2] Create `tests/contract/test_network_idle.py` with:
  - test_wait_for_network_idle: GET /v1/html?url=...&waitFor=network-idle waits for network
  - test_invalid_wait_for_value: GET /v1/html?url=...&waitFor=invalid returns 400
  - test_network_idle_timeout: After timeout, returns 200 with warning in metadata
  - test_render_time_reflects_wait: renderTime >= network idle duration

### Implementation for US2

- [ ] T030 [US2] Update `src/core/renderer.py` to support waitFor="network-idle":
  - Add wait_condition parameter to render() method
  - Use playwright: page.wait_for_load_state("networkidle", timeout=...) when waitFor="network-idle"
  - Catch TimeoutError and return current DOM state with warning
  - Track actual wait time and include in metadata

- [ ] T031 [P] [US2] Update `src/api/handlers.py`:
  - Add logic to handle waitFor="network-idle" parameter
  - Pass wait_condition to renderer.render()
  - Add warning to metadata if timeout occurred

- [ ] T032 [P] [US2] Update `tests/contract/test_network_idle.py` to test timeout behavior:
  - test_network_idle_with_short_timeout: timeout=2000 on slow page returns partial content

- [ ] T033 [US2] Create `tests/integration/test_network_idle.py` with:
  - test_network_idle_detection: Fetch httpbin.org/delay/2 with waitFor=network-idle
  - Verify response time is >= 2 seconds
  - Verify renderTime in metadata reflects actual wait time

- [ ] T034 [US2] Run contract tests (pytest tests/contract/test_network_idle.py) - should pass ✅

- [ ] T035 [US2] Run integration tests (pytest tests/integration/test_network_idle.py) - should pass ✅

**Checkpoint**: User Story 2 complete. Network idle detection works independently from US1.

---

## Phase 5: User Story 3 - Wait for CSS Selector (Priority: P1)

**Goal**: Implement selector-based waiting so pages wait for a specific DOM element to appear before capturing HTML. Useful for pages with known completion signals.

**Independent Test**: Can be tested with a page containing a known element. Request with waitFor=selector&selector=.element-class, verify element is present in returned HTML.

### Contract Tests for US3 (OPTIONAL - tests written FIRST)

- [ ] T036 [P] [US3] Create `tests/contract/test_selector_match.py` with:
  - test_wait_for_selector: GET /v1/html?url=...&waitFor=selector&selector=.class returns 200
  - test_selector_required_when_waitFor_selector: GET /v1/html?url=...&waitFor=selector (no selector) returns 400
  - test_invalid_selector_syntax: GET /v1/html?url=...&waitFor=selector&selector=invalid:syntax returns 400
  - test_selector_timeout: Selector never appears, timeout reached, returns 200 with warning

### Implementation for US3

- [ ] T037 [US3] Update `src/core/renderer.py` to support waitFor="selector":
  - Add selector parameter to render() method
  - Use playwright: page.wait_for_selector(selector, timeout=...) when waitFor="selector"
  - Catch TimeoutError and return current DOM state with warning
  - Track actual wait time and include in metadata

- [ ] T038 [P] [US3] Update `src/api/handlers.py`:
  - Add validation: if waitFor="selector", selector MUST be present and non-empty
  - Pass selector to renderer.render()
  - Add warning to metadata if timeout occurred

- [ ] T039 [P] [US3] Update `src/lib/validators.py`:
  - Enhance CSS selector validation to catch more invalid patterns
  - Test with Playwright's selector engine if possible

- [ ] T040 [P] [US3] Create `tests/contract/test_selector_match.py` tests:
  - Ensure all selector validation edge cases are covered

- [ ] T041 [US3] Create `tests/integration/test_selector_waiting.py` with:
  - test_selector_match_example_com: Fetch example.com with waitFor=selector&selector=h1
  - Verify h1 element is in returned HTML

- [ ] T042 [US3] Run contract tests (pytest tests/contract/test_selector_match.py) - should pass ✅

- [ ] T043 [US3] Run integration tests (pytest tests/integration/test_selector_waiting.py) - should pass ✅

**Checkpoint**: User Story 3 complete. Selector-based waiting works independently.

---

## Phase 6: User Story 4 - Custom Browser User Agent (Priority: P2)

**Goal**: Allow API clients to specify a custom browser user agent string. Useful for testing mobile rendering or working around user-agent blocking.

**Independent Test**: Can be tested by requesting a URL with a custom user agent and verifying server receives it (via logs or httpbin). Mobile user agent should return mobile layout.

### Contract Tests for US4 (OPTIONAL)

- [ ] T044 [P] [US4] Create `tests/contract/test_user_agent.py` with:
  - test_custom_user_agent_accepted: GET /v1/html?url=...&userAgent=custom returns 200
  - test_user_agent_length_validation: userAgent > 1000 chars returns 400
  - test_default_user_agent_when_omitted: No userAgent param uses default Chrome agent

### Implementation for US4

- [ ] T045 [US4] Update `src/core/browser.py`:
  - Add user_agent parameter to get_page() method
  - Set user agent via page.context.new_page(user_agent=...) or playwright's user agent option
  - Use sensible default if not provided: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36..."

- [ ] T046 [P] [US4] Update `src/api/handlers.py`:
  - Pass userAgent parameter to renderer.render()
  - Validate userAgent length (1-1000 chars)

- [ ] T047 [P] [US4] Update `src/api/schemas.py`:
  - Add userAgent validation to HtmlRequest

- [ ] T048 [P] [US4] Create `tests/contract/test_user_agent.py` tests

- [ ] T049 [US4] Create `tests/integration/test_user_agent.py` with:
  - test_mobile_user_agent: Fetch with iPhone user agent, verify content differs from desktop
  - test_custom_user_agent_via_httpbin: Use httpbin.org/user-agent to echo received user agent

- [ ] T050 [US4] Run contract tests (pytest tests/contract/test_user_agent.py) - should pass ✅

- [ ] T051 [US4] Run integration tests (pytest tests/integration/test_user_agent.py) - should pass ✅

**Checkpoint**: User Story 4 (P2) complete. Custom user agent support works independently.

---

## Phase 7: User Story 5 - Configurable Timeout (Priority: P1)

**Goal**: Allow API clients to configure timeout per request (1-120 seconds). Critical for production use.

**Independent Test**: Can be tested by requesting a slow page with different timeouts and verifying response time matches timeout parameter.

### Contract Tests for US5 (OPTIONAL)

- [ ] T052 [P] [US5] Create `tests/contract/test_timeout.py` with:
  - test_custom_timeout: GET /v1/html?url=...&timeout=10000 respects timeout
  - test_timeout_out_of_range_low: timeout=500 returns 400 with INVALID_TIMEOUT
  - test_timeout_out_of_range_high: timeout=150000 returns 400 with INVALID_TIMEOUT
  - test_default_timeout: No timeout param uses 30000ms default
  - test_timeout_causes_partial_render: Request slow page with short timeout, returns 200 with warning

### Implementation for US5

- [ ] T053 [US5] Update `src/core/renderer.py`:
  - timeout parameter already supported in render() method
  - Validate timeout is within 1000-120000 range
  - Ensure Playwright operations respect timeout

- [ ] T054 [P] [US5] Update `src/api/handlers.py`:
  - timeout parameter already in handler
  - Ensure timeout is passed to renderer

- [ ] T055 [P] [US5] Update `src/api/schemas.py`:
  - HtmlRequest.timeout already has validators (from earlier task)
  - Verify range validation: 1000-120000 ms

- [ ] T056 [P] [US5] Create `tests/contract/test_timeout.py` tests

- [ ] T057 [US5] Create `tests/integration/test_timeout.py` with:
  - test_timeout_respected: Request slow page (httpbin.org/delay/15) with timeout=5000
  - Verify response returns after ~5 seconds (not 15)
  - Verify warning in metadata indicates timeout

- [ ] T058 [US5] Run contract tests (pytest tests/contract/test_timeout.py) - should pass ✅

- [ ] T059 [US5] Run integration tests (pytest tests/integration/test_timeout.py) - should pass ✅

**Checkpoint**: User Story 5 (P1) complete. Timeout configuration works independently.

---

## Phase 8: Cross-Cutting Concerns & Polish

**Purpose**: Testing, documentation, and operational readiness

- [ ] T060 Create `tests/unit/test_validators.py` with:
  - test_validate_url_valid: Valid URLs pass
  - test_validate_url_invalid: Invalid URLs raise InvalidUrl
  - test_validate_selector_valid: Valid selectors pass
  - test_validate_selector_invalid: Invalid selectors raise InvalidSelector
  - test_validate_timeout_valid: Valid timeouts pass
  - test_validate_timeout_out_of_range: Out-of-range timeouts raise InvalidTimeout

- [ ] T061 [P] Create `tests/unit/test_error_handling.py` with:
  - test_error_response_format: Errors have code, message, details, timestamp
  - test_http_status_codes: Exception types map to correct HTTP codes
  - test_error_messages_actionable: Error messages help users debug

- [ ] T062 [P] Create `tests/integration/test_redirect_handling.py` with:
  - test_follow_redirect: Page redirects, final URL is returned
  - test_redirect_limit: Max 5 redirects enforced
  - test_final_page_content: HTML from final destination returned

- [ ] T063 [P] Create `tests/integration/test_timeout_behavior.py` with:
  - test_partial_render_on_timeout: Partial DOM returned when timeout reached
  - test_timeout_warning_in_metadata: Warning message in metadata.warnings

- [ ] T064 [P] Create `tests/unit/test_renderer.py` with:
  - test_renderer_initialization: Can create PageRenderer instance
  - test_render_timeout_respected: render() respects timeout parameter
  - test_render_returns_tuple: render() returns (content, metadata)
  - [Uses mocked browser fixture from conftest.py]

- [ ] T065 Run all unit tests (pytest tests/unit/) - should pass ✅

- [ ] T066 Run all contract tests (pytest tests/contract/) - should pass ✅

- [ ] T067 Run all integration tests (pytest tests/integration/) - should pass ✅

- [ ] T068 Generate coverage report: pytest --cov=src tests/ - aim for 80%+ coverage

- [ ] T069 [P] Update `README.md` with:
  - Project description
  - Quick start (5-minute setup)
  - Building and running Docker
  - API usage examples
  - Link to OpenAPI documentation (contracts/openapi.yaml)
  - Link to detailed quick start (quickstart.md)
  - Development setup (pip install, pytest)
  - Troubleshooting section

- [ ] T070 [P] Create `.github/workflows/ci.yml` (GitHub Actions) with:
  - Run on: push to main, PRs
  - Jobs:
    - Lint (flake8, black check)
    - Test (pytest with coverage)
    - Build Docker image
  - Fail if coverage < 80%

- [ ] T071 [P] Add linting configuration:
  - Create `pyproject.toml` with [tool.black], [tool.isort], [tool.pytest.ini_options]
  - Add `flake8` and `black` to requirements-dev.txt
  - Configure pre-commit hooks for automatic formatting

- [ ] T072 Create `DEVELOPMENT.md` with:
  - Local setup instructions
  - Running tests locally
  - Debugging tips
  - Code style guidelines (PEP 8, Constitution Principle I)

- [ ] T073 [P] Add health check to `src/api/handlers.py`:
  - Already implemented in T025
  - Ensure /health is queryable and works correctly

- [ ] T074 Update `Dockerfile` to include:
  - Metadata labels: LABEL maintainer, org.opencontainers.image.description
  - Non-root user (optional but recommended)

- [ ] T075 [P] Test Docker image build and run:
  - docker build -t browse-local:latest .
  - docker run -p 8000:8000 browse-local:latest
  - Verify /health endpoint responds
  - Verify /v1/html with example.com works

- [ ] T076 [P] Create example client scripts:
  - `examples/fetch.py` - Python example using httpx
  - `examples/fetch.js` - JavaScript/Node.js example
  - `examples/fetch.sh` - Bash/cURL example

- [ ] T077 Create `DEPLOYMENT.md` with:
  - Kubernetes deployment manifest (optional)
  - Docker Compose production setup
  - Environment variables reference
  - Monitoring and health checks
  - Scaling considerations

- [ ] T078 [P] Add logging to all key operations:
  - Request received (with parameters)
  - Browser page created
  - Page navigation started
  - Wait condition applied
  - Page content captured
  - Response sent
  - Errors logged with stack traces

- [ ] T079 [P] Add performance monitoring:
  - Log request duration
  - Log render time (already in metadata)
  - Prometheus metrics (optional: requests, latency, errors)

- [ ] T080 Final validation:
  - All 80+ tasks completed ✅
  - All tests pass ✅
  - Coverage >= 80% ✅
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
- Coverage >= 80%
- All integration tests pass
- Docker image builds successfully
- Health check endpoint working
- Documentation complete and accurate

