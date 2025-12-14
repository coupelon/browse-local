#!/bin/bash

# Test script for selector error handling
# Should return HTML content even when selector fails

# Start container
echo "Starting Docker container..."
docker run -d -p 8000:8000 --name browse-local-test browse-local:latest
sleep 5

echo ""
echo "Testing selector error handling with dynamic web page..."
echo "========================================================"

# Test with invalid selector (should return HTML + selector_error metadata)
response=$(curl -s -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.w3schools.com/html/",
    "selector": "article[data-id-nonexistent]",
    "timeout": 15000
  }')

# Check if response contains content
content_length=$(echo "$response" | jq -r '.content' | wc -c)
selector_error=$(echo "$response" | jq -r '.metadata.selector_error // "null"')
partial_content=$(echo "$response" | jq -r '.metadata.partial_content // "null"')
status_code=$(echo "$response" | jq -r '.status // "null"')

echo "Response analysis:"
echo "- Content length: $content_length bytes"
echo "- Selector error: $selector_error"
echo "- Partial content flag: $partial_content"
echo "- Status: $status_code"

echo ""
if [ "$content_length" -gt 1000 ] && [ "$selector_error" != "null" ] && [ "$partial_content" == "true" ]; then
    echo "✅ SUCCESS: HTML content returned with selector error metadata"
else
    echo "❌ FAILED: Expected HTML content with selector_error metadata"
    echo ""
    echo "Full response (first 500 chars):"
    echo "$response" | head -c 500
fi

# Cleanup
echo ""
echo "Stopping container..."
docker stop browse-local-test
docker rm browse-local-test
