# Development Guide

## Local Setup

### Prerequisites

- Python 3.11+
- Git
- Docker (optional, for container testing)

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd browse-local
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   playwright install chromium
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env as needed
   ```

## Running Tests

### All Tests
```bash
pytest
```

### By Test Type
```bash
# Unit tests only
pytest tests/unit/ -v

# Contract tests
pytest tests/contract/ -v

# Integration tests
pytest tests/integration/ -v
```

### With Coverage
```bash
# Generate coverage report
pytest --cov=src tests/unit tests/contract -q

# HTML coverage report
pytest --cov=src --cov-report=html tests/unit tests/contract
open htmlcov/index.html
```

### Specific Test
```bash
pytest tests/unit/test_validators.py::test_validate_url_valid -v
```

## Code Style

### Formatting with Black

```bash
# Format all code
black src/ tests/

# Check formatting without changes
black --check src/ tests/
```

### Linting with Flake8

```bash
# Lint code
flake8 src/ tests/

# With specific line length
flake8 src/ tests/ --max-line-length=120
```

### Import Sorting with isort

```bash
# Sort imports
isort src/ tests/

# Check import order
isort --check-only src/ tests/
```

## Code Style Guidelines

### PEP 8 Compliance

- **Line length**: 120 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Naming conventions**:
  - `snake_case` for functions, variables, modules
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

### Function Complexity

- **Function length**: < 50 lines preferred
- **Cyclomatic complexity**: < 10
- **Parameters**: ≤ 5 per function

### Type Hints

Always use type hints for function signatures:

```python
def validate_url(url: str) -> str:
    """Validate URL format."""
    ...

async def render(
    url: str,
    timeout: int = 30000
) -> Tuple[str, Dict[str, Any]]:
    """Render page and return content."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
    """
    ...
```

## Debugging Tips

### Running the API Locally

```bash
# Start dev server with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# With debug logging
LOG_LEVEL=DEBUG uvicorn src.api.main:app --reload
```

### Interactive Testing

```bash
# Start Python REPL with imports
python -i -c "from src.core.browser import BrowserSession; from src.core.renderer import PageRenderer"
```

### Debug Logging

Enable debug logs in `.env`:
```
LOG_LEVEL=DEBUG
```

### VS Code Debug Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v"],
      "console": "integratedTerminal"
    },
    {
      "name": "Run API",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["src.api.main:app", "--reload"],
      "console": "integratedTerminal"
    }
  ]
}
```

## Git Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `test/description` - Test additions/fixes

### Commit Messages

Follow Conventional Commits format:

```
type(scope): brief description

Longer description if needed.

Fixes #123
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Docker Development

### Build and Test

```bash
# Build image
docker build -t browse-local:dev .

# Run container
docker run -p 8000:8000 --name browse-local-dev browse-local:dev

# Check logs
docker logs -f browse-local-dev

# Stop and remove
docker stop browse-local-dev && docker rm browse-local-dev
```

### Docker Compose

```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Restart service
docker-compose restart

# Rebuild and start
docker-compose up --build -d
```

## Performance Profiling

### Basic Timing

```python
import time

start = time.time()
# ... code to profile
duration = time.time() - start
print(f"Duration: {duration:.2f}s")
```

### Memory Profiling

```bash
pip install memory-profiler

# Add @profile decorator to function
python -m memory_profiler script.py
```

## Troubleshooting

### Playwright Issues

```bash
# Reinstall browsers
playwright install --force chromium

# Check installation
playwright install --help
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Dependencies Out of Sync

```bash
# Clean and reinstall
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
playwright install chromium
```

## CI/CD

See `.github/workflows/ci.yml` for the continuous integration pipeline.

The CI runs:
1. **Lint**: Black formatting + Flake8 linting
2. **Test**: Unit, contract, and integration tests with coverage
3. **Build**: Docker image build and health check

## API Endpoints

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/v1/html` | POST | ✅ Active | Retrieve HTML with custom headers (recommended) |
| `/health` | GET | ✅ Active | Health check |
| `/metrics` | GET | ✅ Active | Performance metrics |

## Error Handling

- Selector timeout or not found returns **HTTP 404**, with HTML content included in `detail.content` and diagnostics in `detail.metadata` (`selector_error`, `partial_content`).

## Test Totals

- Total tests: 50 (100% passing)

## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Playwright for Python**: https://playwright.dev/python/
- **Pydantic**: https://docs.pydantic.dev/
- **pytest**: https://docs.pytest.org/

## Constitution Principles

All code must follow the Constitution principles defined in `.specify/constitution/`:

1. **Code Quality & Maintainability**: Clean, well-documented, linted code
2. **Test-Driven Development**: 50%+ coverage, tests before implementation
3. **API Design**: Clear contracts, versioning, error handling
4. **Performance**: Meet latency targets (< 2s basic, < 10s network-idle)
5. **User Experience**: Consistent responses, actionable error messages
