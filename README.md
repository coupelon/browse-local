# Browse Local - Web Page HTML Retrieval API

A containerized HTTP API that retrieves HTML content from web pages with advanced rendering support using Playwright and embedded Chromium.

## Features

- **Basic HTML Retrieval**: Fetch HTML content from any public URL
- **Network Idle Detection**: Wait for dynamic content to load via JavaScript
- **CSS Selector Matching**: Wait for specific DOM elements before capturing
- **Custom User Agent**: Emulate different browsers and devices
- **Configurable Timeout**: Control wait times (1-120 seconds)
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

### Basic Retrieval

```bash
curl "http://localhost:8000/v1/html?url=https://example.com"
```

### Wait for Network Idle

```bash
curl "http://localhost:8000/v1/html?url=https://example.com&waitFor=network-idle&timeout=15000"
```

### Wait for CSS Selector

```bash
curl "http://localhost:8000/v1/html?url=https://example.com&waitFor=selector&selector=.content"
```

### Custom User Agent

```bash
curl "http://localhost:8000/v1/html?url=https://example.com&userAgent=Mozilla/5.0%20(iPhone...)"
```

## API Documentation

- **OpenAPI Specification**: See `specs/001-web-page-scraper/contracts/openapi.yaml`
- **Detailed Guide**: See `specs/001-web-page-scraper/quickstart.md`
- **Interactive Docs**: Visit `http://localhost:8000/docs` (when running)

## Development Setup

### Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test type
pytest tests/unit/
pytest tests/contract/
pytest tests/integration/
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
- **Validation**: Pydantic models
- **Testing**: pytest + httpx
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
- Code coverage: ≥80%

## Troubleshooting

### Browser fails to start

Ensure you're using the official Playwright Docker image:
```bash
docker pull mcr.microsoft.com/playwright/python:v1.40.0-jammy
```

### Timeout issues

Increase the timeout parameter:
```bash
curl "http://localhost:8000/v1/html?url=<URL>&timeout=60000"
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
