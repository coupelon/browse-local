# Use official Playwright image with embedded Chromium
FROM mcr.microsoft.com/playwright/python:v1.65.2-noble

# Metadata labels
LABEL maintainer="Browse Local Team"
LABEL org.opencontainers.image.description="Web Page HTML Retrieval API with Playwright"
LABEL org.opencontainers.image.source="https://github.com/your-org/browse-local"
LABEL org.opencontainers.image.version="1.0.0"

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src/

# Create non-root user (optional but recommended)
# Note: UIDs 1000 (ubuntu) and 1001 (pwuser) already exist in the noble base image
RUN useradd -m -u 1002 appuser && chown -R appuser:appuser /app
USER appuser

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start API server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
