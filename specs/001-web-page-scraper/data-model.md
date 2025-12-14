# Data Model: Web Page HTML Retrieval API

**Phase**: Phase 1 (Design & Contracts)  
**Date**: 2025-12-14  
**Branch**: `001-web-page-scraper`  
**Status**: Updated for POST JSON + Custom Headers

## Overview

This document defines the data entities, their relationships, and validation rules for the Web Page HTML Retrieval API. All entities are derived from the feature specification requirements.

**Architecture Change**: The API has transitioned from `GET /v1/html?params` to `POST /v1/html` with JSON body, enabling support for custom HTTP headers and improved parameter passing.

---

## Entity: HtmlRequest (POST Body)

**Purpose**: Encapsulates all parameters for fetching and rendering a web page

**Endpoint**: `POST /v1/html`

**Content-Type**: `application/json`

**Fields**:

| Field | Type | Required | Default | Constraints | Purpose |
|-------|------|----------|---------|-------------|---------|
| `url` | string (URI) | Yes | — | Valid HTTP(S) URL, max 2048 chars | Target web page URL |
| `waitFor` | enum | No | `"none"` | `"none"` \| `"network-idle"` | Rendering wait strategy |
| `selector` | string | Conditional | null | Valid CSS selector, max 500 chars | Element to wait for (if applicable) |
| `headers` | object | No | {} | dict[str, str]; blocked headers filtered | Custom HTTP headers to include in request |
| `timeout` | integer | No | 30000 | 1000-120000 (milliseconds) | Maximum wait time before returning result |

**Validation Rules**:

1. **URL Validation**:
   - MUST be a valid HTTP or HTTPS URL (RFC 3986)
   - MUST be reachable (checked at request time)
   - Localhost URLs (e.g., `http://localhost:3000`) are allowed
   - Maximum length: 2048 characters
   - Examples:
     - ✅ `https://www.seloger.com/classified-search?...`
     - ✅ `https://example.com/path?query=value#fragment`
     - ✅ `http://localhost:8000`
     - ❌ `not-a-url` (error: INVALID_URL)
     - ❌ `ftp://example.com` (error: UNSUPPORTED_SCHEME)

2. **WaitFor Validation**:
   - MUST be one of: `"none"`, `"network-idle"`
   - Default: `"none"` (capture immediately)
   - Examples:
     - ✅ `"none"` or omitted (no wait)
     - ✅ `"network-idle"` (wait for network idle)
     - ❌ `"selector"` (deprecated syntax; use `selector` field instead)

3. **Selector Validation**:
   - OPTIONAL; if provided, MUST be a valid CSS selector
   - MUST NOT be combined with `waitFor="network-idle"` (error: CONFLICTING_PARAMETERS)
   - Maximum length: 500 characters
   - Examples:
     - ✅ `.article-content`
     - ✅ `a[title][data-testid]`
     - ✅ `div#main > p:first-child`
     - ❌ `` (empty; error: INVALID_SELECTOR)
     - ❌ `[invalid:selector` (error: INVALID_SELECTOR_SYNTAX)

4. **Headers Validation** (NEW):
   - OPTIONAL; if provided, MUST be `dict[str, str]`
   - Keys: Valid HTTP header names (alphanumeric, hyphen).
   - Values: Strings (no nested objects/arrays).
   - Blocked headers (security): `Host`, `Content-Length`, `Transfer-Encoding`, `Connection`, `Upgrade`, `Proxy-*`, `TE`, `Trailer`
   - Allowed: Standard headers (User-Agent, Accept-Language, Authorization, Cookie, etc.) + custom `X-*` headers
   - Merging: User headers override Playwright defaults.
   - Examples:
     - ✅ `{"User-Agent": "Mozilla/5.0 (iPhone...)", "Accept-Language": "fr-FR"}`
     - ✅ `{"Authorization": "Bearer token123"}`
     - ✅ `{"X-Custom-Header": "value"}`
     - ❌ `{"Host": "example.com"}` (error: BLOCKED_HEADER or silently ignored)
     - ❌ `{"User-Agent": 123}` (error: INVALID_HEADER_VALUE, must be string)

5. **Timeout Validation**:
   - OPTIONAL; default: 30000 milliseconds (30 seconds)
   - MUST be an integer
   - Range: 1000-120000 milliseconds (1-120 seconds)
   - Examples:
     - ✅ 2000 (2 seconds for fast pages)
     - ✅ 30000 (default)
     - ✅ 60000 (1 minute for heavy pages)
     - ❌ 500 (error: TIMEOUT_TOO_SHORT)
     - ❌ 200000 (error: TIMEOUT_TOO_LONG)

6. **Conflict Detection**:
   - IF `selector` is present AND `waitFor="network-idle"` THEN error: CONFLICTING_PARAMETERS (422 Unprocessable Entity)
   - IF `selector` is present THEN wait for selector in DOM
   - IF `waitFor="network-idle"` THEN wait for network idle
   - IF both absent THEN capture immediately

---

## Example HtmlRequest Payloads

**Basic Request** (no wait):
```json
{
  "url": "https://example.com"
}
```

**With Network Idle**:
```json
{
  "url": "https://www.seloger.com/classified-search",
  "waitFor": "network-idle",
  "timeout": 15000
}
```

**With CSS Selector**:
```json
{
  "url": "https://www.seloger.com/classified-search",
  "selector": "a[title][data-testid]",
  "timeout": 20000
}
```

**With Custom Headers**:
```json
{
  "url": "https://www.seloger.com/classified-search",
  "waitFor": "network-idle",
  "headers": {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Authorization": "Bearer token123"
  },
  "timeout": 15000
}
```

---

## Entity: HtmlResponse

**Purpose**: Encapsulates the result of a page fetch/render operation

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | Raw HTML content of the rendered page (UTF-8 encoded) |
| `metadata` | object | Metadata about the fetch operation (see ResponseMetadata below) |

**Notes**:
- `content` is never null; even on partial renders (timeout), it contains the current DOM
- `content` max size: 50MB (enforced by HTTP response size limit)
- Example response:
```json
{
  "content": "<!DOCTYPE html>\n<html>\n<head>\n<title>Example</title>\n</head>\n<body>...",
  "metadata": { ... }
}
```

---

## Entity: ResponseMetadata

**Purpose**: Provides transparency and debugging information about the render operation

**Fields**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `url` | string | Yes | Final URL after redirects | `"https://example.com"` |
| `statusCode` | integer | Yes | HTTP status of fetched page | 200 |
| `renderTime` | number | Yes | Time spent rendering (seconds) | 2.345 |
| `timestamp` | string (ISO 8601) | Yes | UTC time of response | `"2025-12-14T10:30:00Z"` |
| `warnings` | array[string] | No | Non-blocking issues during render | `["Timeout reached before selector matched"]` |

**Examples**:

**Example 1: Successful Basic Retrieval**
```json
{
  "url": "https://example.com",
  "statusCode": 200,
  "renderTime": 0.456,
  "timestamp": "2025-12-14T10:30:00Z",
  "warnings": []
}
```

**Example 2: Network-Idle with Timeout**
```json
{
  "url": "https://slow-api.example.com",
  "statusCode": 200,
  "renderTime": 30.001,
  "timestamp": "2025-12-14T10:30:30Z",
  "warnings": ["Timeout reached (30s) before network idle; returning partial content"]
}
```

**Example 3: Selector Not Matched**
```json
{
  "url": "https://example.com",
  "statusCode": 200,
  "renderTime": 10.0,
  "timestamp": "2025-12-14T10:30:10Z",
  "warnings": ["Selector '.nonexistent-element' not found; timeout reached"]
}
```

---

## Entity: ErrorResponse

**Purpose**: Standardized error response for all error scenarios

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | Yes | Error code (e.g., `"VALIDATION_ERROR"`) |
| `message` | string | Yes | Human-readable error message |
| `details` | object | No | Additional context (varies by error type) |
| `timestamp` | string (ISO 8601) | Yes | UTC time of error response |

**Error Codes & Status Codes**:

| Code | HTTP Status | Scenario | Details |
|------|------------|----------|---------|
| `INVALID_URL` | 400 | URL format invalid | `{ "url": "provided_value", "reason": "not a valid HTTP(S) URL" }` |
| `UNSUPPORTED_SCHEME` | 400 | URL scheme not HTTP(S) | `{ "scheme": "ftp" }` |
| `INVALID_WAIT_STRATEGY` | 400 | `waitFor` not in enum | `{ "waitFor": "invalid", "allowed": ["none", "network-idle", "selector"] }` |
| `SELECTOR_REQUIRED` | 400 | `waitFor="selector"` but selector missing | `{ "message": "selector parameter required when waitFor=selector" }` |
| `INVALID_SELECTOR_SYNTAX` | 400 | CSS selector invalid | `{ "selector": "provided_value", "error": "Playwright parse error" }` |
| `INVALID_TIMEOUT` | 400 | Timeout out of range | `{ "timeout": 500, "min": 1000, "max": 120000 }` |
| `PAYLOAD_TOO_LARGE` | 413 | URL + params exceed 10KB | `{ "size": 12000, "max": 10000 }` |
| `NOT_FOUND` | 404 | Target URL returns 404 | `{ "url": "https://example.com/missing", "targetStatusCode": 404 }` |
| `REQUEST_TIMEOUT` | 408 | Timeout reached during render | `{ "timeout": 30000, "reason": "wait condition not met" }` |
| `BROWSER_ERROR` | 500 | Browser crash or internal error | `{ "error": "Browser process exited unexpectedly" }` |
| `NETWORK_ERROR` | 500 | Network failure (DNS, connection, etc.) | `{ "url": "...", "error": "Connection refused" }` |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected server error | `{ "message": "Internal server error; request ID: ..." }` |

**Example Error Responses**:

**Example 1: Invalid URL**
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

**Example 2: Missing Required Selector**
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

**Example 3: Timeout**
```json
{
  "code": "REQUEST_TIMEOUT",
  "message": "Request timeout: wait condition not met within 30000ms",
  "details": {
    "timeout": 30000,
    "waitCondition": "network-idle"
  },
  "timestamp": "2025-12-14T10:30:00Z"
}
```

---

## Entity: BrowserSession (Internal)

**Purpose**: Manages Playwright browser lifecycle; not exposed to API clients

**Attributes**:
- `browser`: Playwright Browser instance
- `context`: Playwright BrowserContext (maintains cookies, storage)
- `isConnected`: Boolean indicating if browser is responsive
- `createdAt`: Timestamp of session creation

**Lifecycle**:
1. **Startup**: Created when FastAPI app starts (lifespan event)
2. **Per-Request**: Reused for multiple requests; new page created per request
3. **Cleanup**: Closed when FastAPI app shuts down (lifespan event)

**Note**: Singleton pattern; one instance per container.

---

## Relationships

```
HtmlRequest
    ↓
BrowserSession (internal)
    ↓
Page (Playwright)
    ↓ fetch & render
    ↓
HtmlResponse (on success)
  or
ErrorResponse (on failure)
```

---

## Constraints & Rules Summary

| Aspect | Constraint | Rationale |
|--------|------------|-----------|
| URL | Valid HTTP(S), max 2048 chars | Security (FR-006) |
| Selector | Valid CSS, max 500 chars, required if `waitFor="selector"` | Prevent invalid queries (FR-011) |
| Timeout | 1-120 seconds (integer ms) | Production safety (FR-005) |
| Content Size | Max 50MB | Memory & network efficiency |
| Response Format | Consistent envelope, ISO 8601 timestamps | API consistency (Constitution V) |
| Error Codes | Domain-specific, reusable | User experience (Constitution V) |
| Logging | Structured JSON, request ID correlation | Observability (Constitution II) |

---

## Implementation Mapping

**Where These Entities Are Used**:

- `HtmlRequest` → `src/api/schemas.py` (Pydantic model)
- `HtmlResponse` → `src/api/schemas.py` (Pydantic model)
- `ResponseMetadata` → `src/api/schemas.py` (Pydantic model)
- `ErrorResponse` → `src/api/errors.py` (Custom FastAPI exception handlers)
- `BrowserSession` → `src/core/browser.py` (Class managing Playwright)

---

## Testing Notes

**Unit Tests** (validates data model rules):
- `tests/unit/test_validators.py`: URL, selector, timeout validation
- `tests/unit/test_error_handling.py`: Error response formatting

**Contract Tests** (validates API contracts with these entities):
- `tests/contract/test_basic_retrieval.py`: HtmlResponse schema
- `tests/contract/test_error_responses.py`: ErrorResponse schema

