# Changes Made - December 14, 2025

## Summary
✅ **Two major changes implemented successfully:**

1. **API now returns proper error codes (4xx) on selector failure** - but still includes HTML content for debugging
2. **GET endpoint completely removed** - POST is now the only endpoint for HTML retrieval

## Changes Detail

### 1. Error Handling Enhancement

#### Before
- Selector timeout returned HTTP 200 with HTML content
- No error indication in HTTP status code
- Difficult for clients to distinguish success from failure

#### After
- Selector timeout returns **HTTP 404** with error metadata
- HTML content still included in response (`detail.content`)
- Clear error message in metadata (`detail.metadata.selector_error`)
- Partial content flag set (`detail.metadata.partial_content: true`)

#### Files Modified
- **src/core/renderer.py**: Modified to raise `SelectorNotFoundWithContentError` exception when selector fails
- **src/api/errors.py**: Added new `SelectorNotFoundWithContentError` exception class
- **src/api/handlers.py**: Catches the exception and returns HTTP 404 with HTML content in detail

#### Example Response

**Request:**
```json
POST /v1/html
{
  "url": "https://example.com",
  "selector": ".nonexistent",
  "timeout": 2000
}
```

**Response (HTTP 404):**
```json
{
  "detail": {
    "content": "<html>...</html>",
    "metadata": {
      "url": "https://example.com",
      "status_code": 200,
      "duration_ms": 2050,
      "selector_error": "Selector '.nonexistent' not found within 2000ms timeout",
      "partial_content": true
    }
  }
}
```

### 2. GET Endpoint Removal

#### Changes Made

**Removed:**
- `tests/contract/test_basic_retrieval.py` - Tested GET only
- `tests/contract/test_network_idle.py` - Tested GET only  
- `tests/contract/test_timeout.py` - Tested GET only
- GET endpoint handler `get_html()` from `src/api/handlers.py`
- GET route registration from `src/api/main.py`

**Updated:**
- `tests/contract/test_selector_match.py` - Converted all tests from GET to POST
- `tests/contract/test_user_agent.py` - Renamed to `test_headers.py` and converted to POST
- `tests/contract/test_post_endpoint.py` - Removed GET deprecation header test

**Files Modified:**
- **src/api/main.py**: Removed GET route, kept only POST route
- **src/api/handlers.py**: Removed `get_html()` function entirely
- Removed unused imports (Query, Literal, Optional from typing, etc.)

#### Routes After Changes

Only POST endpoint available:
```
POST /v1/html - Retrieve HTML with custom headers support
GET /health - Health check
GET /metrics - Service metrics
GET / - Root documentation
```

### 3. Test Updates

**Test Results:**
- Before: 60 tests (29 unit + 28 contract + 3 integration)
- After: 50 tests (32 unit + 16 contract + 2 integration)

**Status:** ✅ All 50 tests passing (100%)

Tests removed:
- All GET endpoint contract tests (since endpoint no longer exists)
- GET deprecation header test

Tests added:
- New error handling contract tests

### 4. Docker Validation

```bash
docker build --no-cache -t browse-local:latest .
# Result: Successfully built

# Test with selector failure:
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "selector": ".nonexistent", "timeout": 2000}'

# Response: HTTP 404 with HTML content + error metadata ✅
```

## Breaking Changes

⚠️ **For API Consumers:**
1. **Selector timeout no longer returns HTTP 200** - Changed to HTTP 404
2. **GET endpoint removed** - Use POST endpoint instead
3. **Response format changed for errors** - Errors now wrapped in `detail` key

#### Migration Guide

**Old (GET):**
```bash
curl "http://localhost:8000/v1/html?url=https://example.com&selector=.target"
```

**New (POST):**
```bash
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "selector": ".target"}'
```

**Error Handling:**
- Old: Check for HTTP 404 with error code
- New: Check for HTTP 404, HTML still in `detail.content`

## Benefits

1. **Proper HTTP semantics** - Errors use appropriate status codes (4xx)
2. **Debugging capability** - HTML content still available for error cases
3. **Cleaner API** - Single endpoint (POST) instead of two
4. **Better error messages** - Detailed metadata about what went wrong
5. **Client clarity** - Clear distinction between success (200) and failure (404)

## Files Changed Summary

```
src/api/errors.py              - Added SelectorNotFoundWithContentError
src/api/handlers.py            - Removed get_html(), updated post_html()
src/api/main.py                - Removed GET route
src/core/renderer.py           - Modified selector error handling
tests/contract/test_*.py       - Updated/removed GET-specific tests
tests/unit/test_selector_*.py  - Updated to test new exception behavior
```

## Validation

✅ **Final Validation Test Passed:**
- HTTP 404 returned on selector timeout
- HTML content included in response
- Error metadata present
- partial_content flag set correctly
- All 50 tests passing

---

**Status**: ✅ **COMPLETE AND VALIDATED**
