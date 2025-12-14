# Quick Fix Checklist - Pre-Implementation

**Status**: ⚠️ **2 BLOCKING ISSUES TO FIX BEFORE PHASE 1**

---

## Issue #1: FR-012 Payload Validation Missing

**Severity**: 🔴 **HIGH**

**Requirement** (spec.md, line 140):
> System MUST reject requests with extremely large payloads (URL + parameters > 10KB) with HTTP 413.

**Current State**:
- FR-012 exists in spec
- Not explicitly mapped to any task
- Will be missed during implementation

**Fix Location**: 
- Option A: T016 `src/api/errors.py`
- Option B: T023 `src/api/handlers.py`

**Recommended Implementation**:

```python
# T016: src/api/errors.py
class PayloadTooLargeError(Exception):
    """Raised when request payload exceeds maximum allowed size."""
    code = "PAYLOAD_TOO_LARGE"
    http_status = 413

# T023: src/api/handlers.py
MAX_PAYLOAD_SIZE = 10240  # 10KB in bytes

@app.get("/v1/html")
async def get_html(request: Request):
    # Check payload size
    query_string = str(request.url.query)
    if len(query_string) > MAX_PAYLOAD_SIZE:
        raise PayloadTooLargeError("Request payload exceeds 10KB limit")
    # ... rest of handler
```

**Contract Test** (add to T021):

```python
# tests/contract/test_basic_retrieval.py
def test_get_html_payload_too_large():
    """GET /v1/html with > 10KB payload returns 413"""
    large_url = "https://example.com/" + ("a" * 15000)
    response = client.get(f"/v1/html?url={large_url}")
    assert response.status_code == 413
    assert response.json()["code"] == "PAYLOAD_TOO_LARGE"
```

**Time to Fix**: ⏱️ **10 minutes**

**Action**: Add to T016 task description before Phase 1 begins

---

## Issue #2: Multiple Wait Conditions Rejection

**Severity**: 🟠 **MEDIUM**

**Context** (spec.md, edge cases section):
> What happens when multiple wait conditions are provided (e.g., both `network-idle` and a `selector`)?

**Current State**:
- Spec mentions as edge case
- No explicit rejection behavior specified
- Tasks don't clarify how to handle conflicting parameters
- Could lead to implementation disagreement

**Fix Location**:
- T038: `src/api/handlers.py` (add validation)
- T040: `tests/contract/test_selector_match.py` (add contract test)

**Recommended Implementation**:

```python
# T038: src/api/handlers.py
def validate_wait_conditions(waitFor: str, selector: Optional[str]) -> None:
    """Validate wait condition parameters are not conflicting."""
    if waitFor == "network-idle" and selector:
        raise ConflictingParametersError(
            "Cannot specify both waitFor=network-idle and selector parameter"
        )
    if waitFor == "none" and selector:
        raise ConflictingParametersError(
            "Selector parameter requires waitFor=selector"
        )

# In handler:
validate_wait_conditions(request.waitFor, request.selector)
```

**Contract Test** (add to T040):

```python
# tests/contract/test_selector_match.py

def test_multiple_wait_conditions_rejected():
    """GET /v1/html with both waitFor=network-idle and selector returns 400"""
    response = client.get(
        "/v1/html?url=https://example.com&waitFor=network-idle&selector=.content"
    )
    assert response.status_code == 400
    assert response.json()["code"] == "CONFLICTING_WAIT_CONDITIONS"

def test_selector_ignored_when_waitFor_none():
    """Selector parameter is ignored (or rejected) when waitFor=none"""
    # Option 1: Silently ignore
    response = client.get(
        "/v1/html?url=https://example.com&waitFor=none&selector=.content"
    )
    # Should succeed and ignore selector
    assert response.status_code == 200
    
    # Option 2: Reject (more explicit)
    # assert response.status_code == 400
```

**Error Response** (add to data-model.md if not present):

```json
{
  "code": "CONFLICTING_WAIT_CONDITIONS",
  "message": "Cannot specify both waitFor=network-idle and selector parameter",
  "details": {
    "waitFor": "network-idle",
    "selector": ".content",
    "hint": "If you need selector matching, use waitFor=selector"
  },
  "timestamp": "2025-12-14T10:00:00Z"
}
```

**Time to Fix**: ⏱️ **20 minutes**

**Action**: Add validation to T038 and tests to T040 before Phase 3 begins

---

## Checklist Before Starting Phase 1

- [ ] **Issue #1 Fixed**: FR-012 payload validation added to T016
  - [ ] Validation code written (max 10KB check)
  - [ ] HTTP 413 response generated
  - [ ] Contract test added to T021
  - [ ] Task T016 description updated

- [ ] **Issue #2 Fixed**: Multiple wait conditions handling clarified
  - [ ] Validation logic added to T038 (handlers.py)
  - [ ] ConflictingParametersError exception created
  - [ ] Contract tests added to T040
  - [ ] Error response structure documented
  - [ ] Decision made: ignore or reject conflicting params

- [ ] **Verification**: Run analysis again
  ```bash
  grep "FR-012" specs/001-web-page-scraper/tasks.md
  grep "CONFLICTING" specs/001-web-page-scraper/tasks.md
  ```

---

## How to Apply Fixes

### Option 1: Direct File Edits (Quick)

1. Open `tasks.md`
2. Find T016 (src/api/errors.py)
3. Add payload validation to description:
   ```
   - [ ] T016 [P] Create `src/api/errors.py` with:
     - Custom exception classes for each error code
     - PayloadTooLargeError for > 10KB requests ← ADD THIS
     - ErrorResponse model
     - FastAPI exception handlers
     - HTTP status code mapping
   ```

4. Find T038 (handlers.py update)
5. Add conflict validation note:
   ```
   - [ ] T038 [P] [US3] Update `src/api/handlers.py`:
     - Add validation: if waitFor=selector, selector MUST be present
     - Add conflict detection: reject if both network-idle and selector
     - Pass selector to renderer.render()
     - Add warning if timeout occurred
   ```

6. Find T040 (contract tests)
7. Add test for conflicts:
   ```
   - [ ] T040 [P] [US3] Create/Update tests:
     - Ensure selector validation covers edge cases
     - Add test for conflicting parameters (waitFor + selector)
     - Add test for selector ignored when waitFor != selector
   ```

### Option 2: Update Report & Commit

After fixes:
```bash
git add -A
git commit -m "fix: FR-012 payload validation and wait-condition conflict detection

- Added FR-012 payload validation (max 10KB) to T016 description
- Added PayloadTooLargeError exception (HTTP 413)
- Added CONFLICTING_WAIT_CONDITIONS validation to T038
- Added contract tests to T040 for conflict scenarios
- Resolves: Issue #1 and #2 from ANALYSIS_REPORT.md

Status: All blocking issues resolved, ready for Phase 1"
```

---

## Verification Commands

After making fixes, verify completeness:

```bash
# Check if FR-012 is mapped
grep -n "FR-012\|PayloadTooLarge\|10KB" specs/001-web-page-scraper/tasks.md

# Check if conflict handling is mentioned
grep -n "conflict\|ConflictingWaitConditions\|network-idle.*selector" specs/001-web-page-scraper/tasks.md

# Count tasks for completeness
grep "^\- \[ \] T[0-9]" specs/001-web-page-scraper/tasks.md | wc -l
# Should still be 80
```

---

## Timeline Impact

- **Time Required**: 30 minutes total (10 + 20)
- **Blocks**: Phase 1 start (T001-T012 can't be truly blocked, but fixes needed before T016-T023)
- **Impact**: Prevents implementation gaps, ensures spec compliance

---

## Next Steps

1. ✅ Read this checklist
2. ⏳ Implement fixes (30 minutes)
3. ✅ Verify with grep commands
4. ✅ Commit changes
5. 🚀 Begin Phase 1: Setup (T001-T012)

---

**Report**: See `ANALYSIS_REPORT.md` for full analysis context

**Generated**: 2025-12-14  
**Priority**: MUST COMPLETE before T016 and T038 implementation

