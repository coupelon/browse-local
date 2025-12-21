<!--
SYNC IMPACT REPORT
==================

Version Change: INITIAL → 1.0.0 (MAJOR baseline adoption)

New Principles:
- I. Code Quality & Maintainability (NEW)
- II. Test-Driven Development (NEW)
- III. API Design & Clear Contracts (NEW)
- IV. Performance & Scalability Standards (NEW)
- V. User Experience Consistency (NEW)

Added Sections:
- Development Standards (Observability & Logging, Documentation)
- Governance (Constitution Authority, Amendment Process, Compliance Verification)

Templates Updated:
- ✅ plan-template.md: Constitution Check section now references Code Quality, Testing, and Performance principles
- ✅ spec-template.md: User Scenarios section aligns with Principle II (Test-First Workflow)
- ✅ tasks-template.md: Task organization aligns with testing standards from Principle II
- ✅ agent-file-template.md: No updates required (generic template)
- ✅ checklist-template.md: No updates required (generic checklist)

Follow-up TODOs:
- None - all principles are concrete and defined

Next Steps:
1. All new features MUST verify compliance against these 5 core principles
2. Code reviews MUST explicitly call out principle violations
3. CI/CD pipeline should enforce linting, testing baselines per Principle II

-->

# Browse Local HTTP API Constitution

## Core Principles

### I. Code Quality & Maintainability

Every contribution MUST meet explicit quality standards to ensure the codebase remains clear, consistent, and maintainable.

- **Readability First**: Code MUST be self-documenting; variable names, function names, and logic flow MUST be immediately understandable to another engineer without extensive comments.
- **Naming Conventions**: Adopt consistent naming patterns across the codebase; domain-specific terminology MUST be used correctly and uniformly.
- **DRY Principle**: Duplicated logic MUST be refactored into reusable functions or utilities; exceptions require explicit justification in code review.
- **Code Complexity**: Cyclomatic complexity MUST not exceed 10 per function; functions exceeding 50 lines MUST be decomposed unless explicitly justified.
- **Linting & Formatting**: All code MUST pass configured linters; formatting MUST be automatically enforced via pre-commit hooks—manual formatting is forbidden.

### II. Test-Driven Development (NON-NEGOTIABLE)

Testing is not an afterthought—it is the specification of the feature.

- **TDD Mandate**: Tests MUST be written and approved by review BEFORE any implementation begins; they define the contract between the feature and the system.
- **Test-First Workflow**: Red → Green → Refactor cycle strictly enforced; if code is implemented without failing tests first, the PR MUST be rejected.
- **Coverage Baseline**: Minimum 50% code coverage MUST be achieved on all new code; coverage MUST be tracked and reported in CI/CD.
- **Test Types Required**:
  - **Unit Tests**: For all business logic, utilities, and service functions.
  - **Integration Tests**: For API endpoints, database interactions, and inter-service communication.
  - **Contract Tests**: For all API endpoints and message schemas; contracts MUST be versioned alongside code.
- **Test Clarity**: Test names MUST clearly describe the behavior being tested using the pattern: `test_[given_condition]_[when_action]_[then_expected_outcome]`.

### III. API Design & Clear Contracts

The API MUST be explicitly specified and consistently implemented.

- **OpenAPI/Swagger**: All endpoints MUST be documented in OpenAPI 3.0+ format; the specification MUST be generated from code or maintained in sync with code (NOT manual).
- **Request/Response Schemas**: Every endpoint MUST define JSON schema for request and response bodies; validation MUST be enforced before business logic executes.
- **Versioning Strategy**: API MUST use path-based versioning (`/v1/`, `/v2/`) or header versioning; breaking changes MUST increment the major version and include a migration guide.
- **Error Handling Consistency**:
  - All errors MUST return HTTP status codes per RFC 7231 standards.
  - Error responses MUST include a consistent structure: `{ "code": "ERROR_CODE", "message": "human-readable message", "details": {...} }`.
  - Error codes MUST be domain-specific and reusable (e.g., `RESOURCE_NOT_FOUND`, `VALIDATION_FAILED`, `RATE_LIMIT_EXCEEDED`).
- **Backward Compatibility**: Deprecations MUST be announced 2 minor versions in advance; deprecated endpoints MUST log usage and include a `Deprecation` header.

### IV. Performance & Scalability Standards

Performance is measurable and non-negotiable.

- **Latency Targets**: All endpoints MUST meet defined p95/p99 latency targets; targets MUST be documented in the API specification and enforced via load testing.
  - Default target: p95 < 500ms, p99 < 1000ms (adjust per endpoint if justified).
- **Benchmarking**: Every feature that touches hot paths MUST include before/after benchmarks; regressions > 10% MUST be justified or reverted.
- **Database Query Optimization**: N+1 queries are forbidden; all queries MUST be analyzed with EXPLAIN plans before merge; indexing strategy MUST be documented.
- **Caching Strategy**: Cache invalidation patterns MUST be explicit and testable; cache headers MUST be set correctly for each endpoint type.
- **Resource Limits**: Request size limits, pagination defaults, and timeout values MUST be set explicitly; any endpoint accepting bulk operations MUST have strict batch size limits.

### V. User Experience Consistency

Users MUST experience predictable, coherent behavior throughout the API.

- **Response Consistency**: All successful responses MUST follow a consistent envelope structure; metadata (pagination, timestamps) MUST use ISO 8601 formats.
- **Input Validation**: Validation errors MUST be detailed and actionable; users MUST understand what failed and why.
- **Pagination Standards**: All list endpoints MUST support limit/offset OR cursor-based pagination; default page size MUST be reasonable (e.g., 20–100 items).
- **Rate Limiting**: Rate limit headers MUST be consistent across all endpoints; users MUST receive `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers.
- **Idempotency**: Endpoints that modify state MUST support idempotency keys for safe retries; idempotency MUST be documented.

## Development Standards

### Observability & Logging

- **Structured Logging**: All logs MUST be in JSON format with consistent field names; request IDs MUST be included in all logs for traceability.
- **Log Levels**: Use `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL` correctly; business events use `INFO`, operational issues use `WARN/ERROR`.
- **Metrics**: All endpoints MUST expose Prometheus-compatible metrics; metrics MUST include request counts, latencies, and error rates.

### Documentation Requirements

- **Inline Comments**: Comment the "why," not the "what"; code that requires comment explanation is a refactoring candidate.
- **API Documentation**: Every endpoint MUST have examples of successful and error responses; authentication requirements MUST be explicit.
- **Runbook**: Deployment, troubleshooting, and incident response procedures MUST be documented and kept current.

## Governance

**Constitution Authority**: This constitution supersedes all other development guidance; amendments MUST be documented, reviewed, and approved before implementation.

**Amendment Process**: Proposed changes MUST include:
1. Rationale: Why the change is necessary
2. Impact Analysis: Which areas of the codebase are affected
3. Migration Plan: How existing code will be brought into compliance (if needed)
4. Deprecation Timeline: Any phases of transition (if applicable)

**Compliance Verification**: All PRs MUST verify compliance against applicable principles; code reviews MUST explicitly call out constitution violations.

**Version Policy**: Versions follow MAJOR.MINOR.PATCH semantic versioning:
- **MAJOR**: Principle removals or redefinitions (backward-incompatible)
- **MINOR**: New principles or expanded guidance
- **PATCH**: Clarifications, wording, or typo fixes

**Version**: 1.0.0 | **Ratified**: 2025-12-14 | **Last Amended**: 2025-12-14
