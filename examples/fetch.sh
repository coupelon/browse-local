#!/bin/bash
# Example: Fetch HTML content using the Browse Local API (Bash + curl)

API_BASE="http://localhost:8000"

echo "Browse Local API - Bash Example"
echo ""

# Example 1: Basic retrieval
echo "1. Basic HTML retrieval:"
curl -s "${API_BASE}/v1/html?url=https://example.com" | \
  jq -r '"✓ Status: \(.metadata.status_code) | Duration: \(.metadata.duration_ms)ms | Content: \(.content | length) chars"'
echo ""

# Example 2: Wait for network idle
echo "2. Wait for network idle:"
curl -s "${API_BASE}/v1/html?url=https://example.com&waitFor=network-idle" | \
  jq -r '"✓ Duration: \(.metadata.duration_ms)ms | Wait strategy: \(.metadata.wait_strategy)"'
echo ""

# Example 3: Wait for CSS selector
echo "3. Wait for CSS selector:"
curl -s "${API_BASE}/v1/html?url=https://example.com&waitFor=selector&selector=h1" | \
  jq -r '"✓ Selector matched | Content length: \(.content | length) chars"'
echo ""

# Example 4: Custom timeout
echo "4. With custom timeout (5 seconds):"
curl -s "${API_BASE}/v1/html?url=https://example.com&timeout=5000" | \
  jq -r '"✓ Duration: \(.metadata.duration_ms)ms"'
echo ""

# Example 5: Custom user agent
echo "5. With custom user agent:"
USER_AGENT="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
curl -s "${API_BASE}/v1/html?url=https://httpbin.org/user-agent&userAgent=${USER_AGENT}" | \
  jq -r '.content' | head -n 5
echo ""

# Example 6: Error handling
echo "6. Error handling (invalid URL):"
curl -s "${API_BASE}/v1/html?url=not-a-valid-url" | \
  jq -r '"✗ Error: \(.error.code) - \(.error.message)"'
echo ""

# Example 7: Health check
echo "7. Health check:"
curl -s "${API_BASE}/health" | \
  jq -r '"Status: \(.status) | Browser ready: \(.browser_ready) | Version: \(.version)"'
echo ""
