"""Performance metrics and monitoring."""

import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RequestMetrics:
    """Metrics for a single request."""

    request_id: str
    url: str
    duration_ms: int
    render_time_ms: int
    status_code: int
    content_size: int
    wait_strategy: str
    error: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class MetricsCollector:
    """Collects and tracks request metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self._request_metrics: Dict[str, RequestMetrics] = {}
        self._total_requests = 0
        self._total_errors = 0
        self._total_duration_ms = 0

    def record_request(self, metrics: RequestMetrics) -> None:
        """Record request metrics."""
        self._request_metrics[metrics.request_id] = metrics
        self._total_requests += 1
        self._total_duration_ms += metrics.duration_ms

        if metrics.error:
            self._total_errors += 1

        # Log metrics
        logger.info(
            "Request metrics recorded",
            extra={
                "request_id": metrics.request_id,
                "url": metrics.url,
                "duration_ms": metrics.duration_ms,
                "render_time_ms": metrics.render_time_ms,
                "status_code": metrics.status_code,
                "content_size": metrics.content_size,
                "error": metrics.error,
            },
        )

    def get_average_duration_ms(self) -> float:
        """Get average request duration in milliseconds."""
        if self._total_requests == 0:
            return 0.0
        return self._total_duration_ms / self._total_requests

    def get_error_rate(self) -> float:
        """Get error rate as percentage."""
        if self._total_requests == 0:
            return 0.0
        return (self._total_errors / self._total_requests) * 100

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        return {
            "total_requests": self._total_requests,
            "total_errors": self._total_errors,
            "average_duration_ms": self.get_average_duration_ms(),
            "error_rate_percent": self.get_error_rate(),
            "total_duration_ms": self._total_duration_ms,
        }

    def get_recent_metrics(self, limit: int = 100) -> list:
        """Get recent request metrics."""
        recent = list(self._request_metrics.values())[-limit:]
        return [m.to_dict() for m in recent]


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
        logger.info("Metrics collector initialized")
    return _metrics_collector


# Optional Prometheus metrics (if prometheus-client is installed)
try:
    from prometheus_client import Counter, Histogram, Gauge

    PROMETHEUS_AVAILABLE = True

    # Request counter
    request_count = Counter("browse_local_requests_total", "Total number of requests", ["method", "status"])

    # Request latency histogram
    request_latency = Histogram(
        "browse_local_request_duration_seconds", "Request latency in seconds", buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
    )

    # Active requests gauge
    active_requests = Gauge("browse_local_active_requests", "Number of active requests")

    # Error counter
    request_errors = Counter("browse_local_request_errors_total", "Total number of request errors", ["error_type"])

    # Content size histogram
    content_size = Histogram("browse_local_content_size_bytes", "Content size in bytes", buckets=(1024, 5120, 10240))

    # Render time histogram
    render_time = Histogram(
        "browse_local_render_time_seconds", "Page render time in seconds", buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 30.0)
    )

    def record_prometheus_metrics(metrics: RequestMetrics) -> None:
        """Record metrics to Prometheus."""
        try:
            method = "GET"  # All requests are GET
            status = metrics.status_code if not metrics.error else 500

            request_count.labels(method=method, status=status).inc()
            request_latency.observe(metrics.duration_ms / 1000)
            content_size.observe(metrics.content_size)
            render_time.observe(metrics.render_time_ms / 1000)

            if metrics.error:
                request_errors.labels(error_type=metrics.error).inc()

            logger.debug("Prometheus metrics recorded", extra={"request_id": metrics.request_id, "status": status})
        except Exception as e:
            logger.warning(f"Failed to record Prometheus metrics: {e}")

except ImportError:
    PROMETHEUS_AVAILABLE = False

    def record_prometheus_metrics(metrics: RequestMetrics) -> None:
        """Prometheus not available - no-op."""
        pass


class MetricsContextManager:
    """Context manager for tracking request metrics."""

    def __init__(self, request_id: str, url: str, wait_strategy: str = "none"):
        """Initialize metrics context."""
        self.request_id = request_id
        self.url = url
        self.wait_strategy = wait_strategy
        self.start_time = time.time()
        self.metrics: Optional[RequestMetrics] = None

    def __enter__(self) -> "MetricsContextManager":
        """Enter context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context and record metrics."""
        duration_ms = int((time.time() - self.start_time) * 1000)

        error = None
        if exc_type is not None:
            error = exc_type.__name__

        # For now, we need to pass render_time manually
        # This will be set by the renderer
        self.metrics = RequestMetrics(
            request_id=self.request_id,
            url=self.url,
            duration_ms=duration_ms,
            render_time_ms=duration_ms,  # Will be overridden by renderer
            status_code=500 if error else 200,
            content_size=0,  # Will be overridden by renderer
            wait_strategy=self.wait_strategy,
            error=error,
        )

        collector = get_metrics_collector()
        collector.record_request(self.metrics)

        if PROMETHEUS_AVAILABLE:
            record_prometheus_metrics(self.metrics)

    def set_response(self, status_code: int, content_size: int, render_time_ms: int) -> None:
        """Set response details (called by handler after successful response)."""
        if self.metrics:
            self.metrics.status_code = status_code
            self.metrics.content_size = content_size
            self.metrics.render_time_ms = render_time_ms
