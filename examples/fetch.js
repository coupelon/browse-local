#!/usr/bin/env node
/**
 * Example: Fetch HTML content using the Browse Local API (Node.js + fetch)
 */

const API_BASE = "http://localhost:8000";

/**
 * Fetch HTML content from a URL using the Browse Local API
 */
async function fetchHtml(url, options = {}) {
  const { waitFor = "none", selector = null, timeout = 30000 } = options;

  const params = new URLSearchParams({
    url,
    waitFor,
    timeout: timeout.toString(),
  });

  if (selector) {
    params.append("selector", selector);
  }

  try {
    const response = await fetch(`${API_BASE}/v1/html?${params}`);

    if (!response.ok) {
      const error = await response.json();
      console.error(`✗ HTTP error: ${response.status}`);
      console.error(`  Error code: ${error.error.code}`);
      console.error(`  Message: ${error.error.message}`);
      return null;
    }

    const data = await response.json();
    console.log(`✓ Successfully fetched ${url}`);
    console.log(`  Status: ${data.metadata.status_code}`);
    console.log(`  Duration: ${data.metadata.duration_ms}ms`);
    console.log(`  Content length: ${data.content.length} characters`);
    console.log(`  Final URL: ${data.metadata.url}`);

    return data.content;
  } catch (error) {
    console.error(`✗ Request failed: ${error.message}`);
    return null;
  }
}

/**
 * Main function - run example requests
 */
async function main() {
  console.log("Browse Local API - Node.js Example\n");

  // Example 1: Basic retrieval
  console.log("1. Basic HTML retrieval:");
  await fetchHtml("https://example.com");
  console.log();

  // Example 2: Wait for network idle
  console.log("2. Wait for network idle:");
  await fetchHtml("https://example.com", { waitFor: "network-idle" });
  console.log();

  // Example 3: Wait for CSS selector
  console.log("3. Wait for CSS selector:");
  await fetchHtml("https://example.com", {
    waitFor: "selector",
    selector: "h1",
  });
  console.log();

  // Example 4: Custom timeout
  console.log("4. With custom timeout:");
  await fetchHtml("https://example.com", { timeout: 5000 });
  console.log();

  // Example 5: Custom user agent
  console.log("5. With custom user agent:");
  const paramsWithUA = new URLSearchParams({
    url: "https://httpbin.org/user-agent",
    userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
  });
  const response = await fetch(`${API_BASE}/v1/html?${paramsWithUA}`);
  const data = await response.json();
  console.log(`✓ Content: ${data.content.substring(0, 200)}...`);
  console.log();
}

// Run main function
main().catch(console.error);
