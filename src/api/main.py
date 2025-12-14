"""FastAPI application initialization and configuration."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.browser import BrowserSession
from src.core.logger import setup_logging, get_logger
from src.api.handlers import get_html, get_health
from src.api.schemas import HealthResponse
from src.api.errors import BrowseLocalError, browse_local_error_handler, generic_error_handler

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle (startup/shutdown).
    
    Handles browser session initialization and cleanup.
    """
    # Startup
    logger.info("Starting Browse Local API")
    try:
        browser_session = await BrowserSession.get_instance()
        logger.info("Browser session initialized")
    except Exception as e:
        logger.error(f"Failed to initialize browser session: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Browse Local API")
    try:
        if browser_session:
            await browser_session.shutdown()
        logger.info("Browser session shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Browse Local - Web Page HTML Retrieval API",
    description="Retrieve HTML content from web pages with optional wait conditions",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(BrowseLocalError, browse_local_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# Register routes
app.get(
    "/v1/html",
    response_model=None,  # Allow raw dict response
    tags=["HTML Retrieval"],
    summary="Retrieve HTML content from a web page",
    description="Fetch and return the HTML content of a web page with optional wait conditions"
)(get_html)

app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check endpoint",
    description="Check the health status of the API and browser session"
)(get_health)


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint redirecting to documentation."""
    return {
        "message": "Browse Local API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
