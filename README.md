# Browse Local - Web Page HTML Retrieval API

A containerized HTTP API that retrieves HTML content from web pages with advanced rendering support using Playwright and embedded Chromium.

## Features

- **Basic HTML Retrieval**: Fetch HTML content from any public URL
- **Custom HTTP Headers**: Add User-Agent, Cookie, Authorization, and any custom headers
- **Network Idle Detection**: Wait for dynamic content to load via JavaScript
- **CSS Selector Matching**: Wait for specific DOM elements before capturing
- **Iframe Support**: Wait for elements inside iframes
- **Configurable Timeout**: Control wait times (1-120 seconds)
- **JSON POST API**: Modern REST API with comprehensive validation
- **100% Dockerized**: No external dependencies, embedded Chromium

## Quick Start (5 minutes)

### Prerequisites

- Docker installed and running
- curl or httpx for testing

### Build and Run

```bash
# Build the Docker image
docker build -t browse-local:latest .

# Run the container
docker run -p 8000:8000 browse-local:latest

# Check health
curl http://localhost:8000/health
```

**Note**: After code changes, rebuild the image with `--no-cache` to ensure updates are applied:
```bash
docker build --no-cache -t browse-local:latest .
```

### Using Docker Compose

```bash
# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

## API Usage

### 🆕 POST Endpoint (Only)

The POST endpoint provides the most powerful and flexible way to retrieve HTML with custom headers support.

#### Basic POST Request

```bash
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","waitFor":"none","timeout":15000}'
```

Or with formatted JSON (requires `jq` or multiline support):

```bash
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{
  "url": "https://example.com",
  "waitFor": "none",
  "timeout": 15000
}'
```

#### POST with Custom Headers

```bash
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "waitFor": "none",
    "headers": {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "Accept-Language": "fr-FR,fr;q=0.9",
      "Cookie": "session_id=abc123; preferences=dark_mode"
    },
    "timeout": 15000
  }'
```

#### POST with Authentication

```bash
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://api.example.com/protected",
    "headers": {
      "Authorization": "Bearer your-token-here",
      "User-Agent": "MyApp/1.0"
    }
  }'
```

#### POST with Selector

```bash
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "waitFor": "none",
    "selector": "#content",
    "timeout": 15000
  }'
```

#### POST with Iframe Support

```bash
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.w3schools.com/html/html_iframe.asp",
    "waitFor": "none",
    "iframe": "iframe[src*=\"default.asp\"]",
    "selector": "#getdiploma",
    "timeout": 15000
  }'
```

#### Real-World Example: Scraping with Complex Headers

```bash
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.w3schools.com/html/",
    "waitFor": "none",
    "selector": ".examples",
    "headers": {
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
      "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8",
      "Cookie": "session=xyz; preferences=dark_mode",
      "Referer": "https://www.w3schools.com/",
      "X-Requested-With": "XMLHttpRequest"
    },
    "timeout": 30000
  }'
```

### Supported Custom Headers

**Allowed Headers:**
- `User-Agent` - Custom browser identification
- `Cookie` - Session cookies and preferences
- `Authorization` - Bearer tokens, Basic auth, etc.
- `Accept-Language` - Language preferences
- `Referer` - Referrer URL
- `X-*` - Any custom headers starting with X-
- Most standard HTTP headers

**Blocked Headers (for security):**
- `Host`, `Content-Length`, `Transfer-Encoding`
- `Connection`, `Upgrade`, `Proxy-*`
- `TE`, `Trailer`

### 📦 Response Format

```json
{
  "content": "<html>...</html>",
  "metadata": {
    "url": "https://example.com/",
    "status_code": 200,
    "duration_ms": 1234,
    "wait_strategy": "none",
    "timestamp": "2025-12-14T12:00:00.000Z"
  }
}
```

### 🐛 Error Handling & Debugging

#### Selector Not Found (Returns HTML for Debugging)

When a CSS selector times out or is not found, the API **returns HTTP 404** but still includes the HTML content and error metadata in the response payload:

```json
{
  "content": "<html>...</html>",
  "metadata": {
    "url": "https://example.com/",
    "status_code": 404,
    "duration_ms": 15234,
    "wait_strategy": "none",
    "selector_error": "Selector '.article-content' not found within 15000ms timeout",
    "partial_content": true,
    "timestamp": "2025-12-14T12:00:00.000Z"
  }
}
```

**Key fields for error detection:**
- `selector_error` (Optional[string]) - Error message when selector was not found
- `partial_content` (Optional[bool]) - True if content may be incomplete

This behavior enables **debugging** of complex web pages where selectors might fail but HTML structure analysis is needed to refine your selector.

#### Example: Scraping Dynamic Sites with Complex Selectors

```bash
# Request with a selector that might not exist immediately
curl -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.w3schools.com/html/",
    "selector": "article[data-id]",
    "timeout": 15000,
    "headers": {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
  }'

# If selector doesn't exist, you still get HTTP 200 with HTML to analyze
# Check metadata.partial_content flag to detect this situation
```

---

## API Documentation

- **Interactive Docs**: Visit `http://localhost:8000/docs` (when running) - Auto-generated OpenAPI documentation
- **POST Migration Guide**: See `IMPLEMENTATION_SUMMARY.md` for migration details
- **OpenAPI Specification**: See `specs/001-web-page-scraper/contracts/openapi.yaml`
- **Detailed Guide**: See `specs/001-web-page-scraper/quickstart.md`

### API Endpoints

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/v1/html` | POST | ✅ Active | Retrieve HTML with custom headers |
| `/health` | GET | ✅ Active | Health check |
| `/metrics` | GET | ✅ Active | Performance metrics |

## Development Setup

### Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage (all tests)
pytest tests/ --cov=src -q

# Run specific test type
pytest tests/unit/ -v
pytest tests/contract/ -v
pytest tests/integration/ -v
```

### Linting & Formatting

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/

# Lint
flake8 src/ tests/
```

### Environment Variables

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```

Available variables:
- `TIMEOUT_MIN`: Minimum timeout in milliseconds (default: 1000)
- `TIMEOUT_MAX`: Maximum timeout in milliseconds (default: 120000)
- `TIMEOUT_DEFAULT`: Default timeout in milliseconds (default: 30000)
- `LOG_LEVEL`: Logging level (default: INFO)
- `WORKERS`: Number of Uvicorn workers (default: 1)

## Architecture

- **Language**: Python 3.11
- **Framework**: FastAPI (async)
- **Browser Automation**: Playwright with embedded Chromium
- **Validation**: Pydantic v2 with field validators
- **Security**: Header validation, blocked headers filtering
- **Testing**: pytest + httpx (unit, contract, integration; ~68 tests)
- **Containerization**: Docker + Docker Compose

## Project Structure

```
browse-local/
├── src/
│   ├── api/          # HTTP endpoints and handlers
│   ├── core/         # Business logic (browser, renderer, config)
│   └── lib/          # Utilities (validators)
├── tests/
│   ├── contract/     # API contract tests
│   ├── integration/  # End-to-end tests
│   └── unit/         # Unit tests
├── specs/            # Feature specifications
├── Dockerfile        # Docker image definition
├── docker-compose.yml
└── requirements.txt
```

## Performance Targets

- Basic retrieval: < 2s (p95)
- Network idle: < 10s (p95)
- Concurrent requests: ≥10 simultaneous
- Code coverage: ≥80% (target)

## Troubleshooting

### Browser fails to start

Ensure you're using the official Playwright Docker image:
```bash
docker pull mcr.microsoft.com/playwright/python:v1.40.0-jammy
```

### Timeout issues

Increase the timeout parameter (POST example):
```bash
curl -X POST "http://localhost:8000/v1/html" \
  -H "Content-Type: application/json" \
  -d '{"url":"<URL>","timeout":60000}'
```

### Health check fails

Check logs:
```bash
docker-compose logs browse-local
```

## Contributing

See `DEVELOPMENT.md` for development guidelines and `specs/` for feature specifications.

## License

Proprietary

## Support

For issues and questions, see the specification documents in `specs/001-web-page-scraper/`.
