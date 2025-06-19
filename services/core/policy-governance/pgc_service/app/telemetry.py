"""
OpenTelemetry integration for PGC Service.

Implements OpenTelemetry instrumentation for the PGC service to provide
distributed tracing, metrics, and logging with the specified version (v1.37.0).
"""

import logging
import time
from collections.abc import Callable
from typing import Any

from fastapi import FastAPI, Request, Response
from opentelemetry import metrics, trace

# Set up logger first
logger = logging.getLogger(__name__)

try:
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
        OTLPMetricExporter,
    )
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import (
        ConsoleMetricExporter,
        PeriodicExportingMetricReader,
    )
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.semconv.resource import ResourceAttributes
    from opentelemetry.trace.propagation.tracecontext import (
        TraceContextTextMapPropagator,
    )

    TELEMETRY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"OpenTelemetry components not available: {e}")
    TELEMETRY_AVAILABLE = False

    # Create fallback classes
    class NoOpTelemetry:
        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, *args, **kwargs):
            return self

        def __getattr__(self, name):
            return self

    OTLPMetricExporter = NoOpTelemetry
    OTLPSpanExporter = NoOpTelemetry
    FastAPIInstrumentor = NoOpTelemetry
    HTTPXClientInstrumentor = NoOpTelemetry
    MeterProvider = NoOpTelemetry
    ConsoleMetricExporter = NoOpTelemetry
    PeriodicExportingMetricReader = NoOpTelemetry
    Resource = NoOpTelemetry
    TracerProvider = NoOpTelemetry
    BatchSpanProcessor = NoOpTelemetry
    ConsoleSpanExporter = NoOpTelemetry
    ResourceAttributes = NoOpTelemetry
    TraceContextTextMapPropagator = NoOpTelemetry

from .config.service_config import get_service_config

logger = logging.getLogger(__name__)


class TelemetryManager:
    """Manages OpenTelemetry instrumentation for the PGC service."""

    def __init__(self):
        """Initialize telemetry manager."""
        self.config = get_service_config()
        self.telemetry_config = self.config.get_section("telemetry")

        self.enabled = self.telemetry_config.get("enabled", True)
        self.otlp_endpoint = self.telemetry_config.get(
            "otlp_endpoint", "http://otel-collector:4317"
        )
        self.otlp_version = self.telemetry_config.get("otlp_version", "v1.37.0")
        self.service_name = self.telemetry_config.get("service_name", "pgc_service")
        self.environment = self.telemetry_config.get("environment", "production")
        self.trace_sample_rate = self.telemetry_config.get("traces_sample_rate", 0.1)

        self.meter_provider = None
        self.tracer_provider = None
        self.tracer = None

        # Metrics
        self.request_counter = None
        self.request_duration_histogram = None
        self.active_requests_gauge = None
        self.validation_counter = None
        self.validation_duration_histogram = None
        self.cache_hit_counter = None
        self.cache_miss_counter = None

        # Performance targets from config
        self.performance_config = self.config.get_section("performance")
        self.p99_latency_target_ms = self.performance_config.get("p99_latency_target_ms", 500)
        self.p95_latency_target_ms = self.performance_config.get("p95_latency_target_ms", 25)

    def setup(self) -> None:
        """Set up OpenTelemetry instrumentation."""
        if not self.enabled:
            logger.info("Telemetry is disabled. Skipping setup.")
            return

        if not TELEMETRY_AVAILABLE:
            logger.warning("OpenTelemetry not available. Running without telemetry.")
            return

        logger.info(
            f"Setting up OpenTelemetry instrumentation (version {self.otlp_version}) "
            f"for {self.service_name} in {self.environment} environment"
        )

        try:
            # Create resource
            resource = Resource.create(
                {
                    ResourceAttributes.SERVICE_NAME: self.service_name,
                    ResourceAttributes.SERVICE_VERSION: self.otlp_version,
                    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: self.environment,
                }
            )

            # Set up tracing
            self._setup_tracing(resource)

            # Set up metrics
            self._setup_metrics(resource)

            # Initialize HTTP instrumentation
            HTTPXClientInstrumentor().instrument()

            logger.info("OpenTelemetry instrumentation setup complete")

        except Exception as e:
            logger.error(f"Failed to set up OpenTelemetry instrumentation: {e}")

    def _setup_tracing(self, resource: Resource) -> None:
        """Set up OpenTelemetry tracing.

        Args:
            resource: OpenTelemetry resource
        """
        # Create tracer provider
        self.tracer_provider = TracerProvider(
            resource=resource,
            # TODO: Use TraceIdRatioBased sampler with configurable rate
        )
        trace.set_tracer_provider(self.tracer_provider)

        # Add OTLP exporter if available
        if OTLP_AVAILABLE and OTLPSpanExporter:
            otlp_span_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
            self.tracer_provider.add_span_processor(BatchSpanProcessor(otlp_span_exporter))

        # Add console exporter in development or as fallback
        if self.environment == "development" or not OTLP_AVAILABLE:
            self.tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        # Get tracer
        self.tracer = trace.get_tracer(self.service_name, self.otlp_version)

    def _setup_metrics(self, resource: Resource) -> None:
        """Set up OpenTelemetry metrics.

        Args:
            resource: OpenTelemetry resource
        """
        # Create exporters
        metric_readers = []

        if OTLP_AVAILABLE and OTLPMetricExporter:
            otlp_metric_exporter = OTLPMetricExporter(endpoint=self.otlp_endpoint)
            metric_readers.append(PeriodicExportingMetricReader(otlp_metric_exporter))

        # Add console exporter in development or as fallback
        if self.environment == "development" or not OTLP_AVAILABLE:
            metric_readers.append(PeriodicExportingMetricReader(ConsoleMetricExporter()))

        # Create meter provider
        self.meter_provider = MeterProvider(
            resource=resource,
            metric_readers=metric_readers,
        )
        metrics.set_meter_provider(self.meter_provider)

        # Get meter
        meter = metrics.get_meter(self.service_name, self.otlp_version)

        # Create metrics
        self.request_counter = meter.create_counter(
            name="pgc.http.requests",
            description="Number of HTTP requests",
            unit="1",
        )

        self.request_duration_histogram = meter.create_histogram(
            name="pgc.http.duration",
            description="HTTP request duration",
            unit="ms",
        )

        self.active_requests_gauge = meter.create_up_down_counter(
            name="pgc.http.active_requests",
            description="Number of active HTTP requests",
            unit="1",
        )

        self.validation_counter = meter.create_counter(
            name="pgc.policy.validations",
            description="Number of policy validations",
            unit="1",
        )

        self.validation_duration_histogram = meter.create_histogram(
            name="pgc.policy.validation_duration",
            description="Policy validation duration",
            unit="ms",
        )

        self.cache_hit_counter = meter.create_counter(
            name="pgc.cache.hits",
            description="Number of cache hits",
            unit="1",
        )

        self.cache_miss_counter = meter.create_counter(
            name="pgc.cache.misses",
            description="Number of cache misses",
            unit="1",
        )

    def instrument_app(self, app: FastAPI) -> None:
        """Instrument FastAPI application.

        Args:
            app: FastAPI application
        """
        if not self.enabled or not TELEMETRY_AVAILABLE:
            return

        try:
            # Instrument FastAPI
            FastAPIInstrumentor.instrument_app(
                app,
                tracer_provider=self.tracer_provider,
                meter_provider=self.meter_provider,
            )

            # Add middleware for latency SLO monitoring
            @app.middleware("http")
            async def latency_slo_middleware(request: Request, call_next: Callable) -> Response:
                # Record start time
                start_time = time.time()

                # Increment active requests
                if self.active_requests_gauge:
                    self.active_requests_gauge.add(1, {"service": self.service_name})

                try:
                    # Process request
                    response = await call_next(request)

                    # Record request duration
                    duration_ms = (time.time() - start_time) * 1000
                    path = request.url.path
                    method = request.method
                    status_code = response.status_code

                    # Record metrics
                    if self.request_counter and self.request_duration_histogram:
                        attributes = {
                            "service": self.service_name,
                            "path": path,
                            "method": method,
                            "status_code": status_code,
                        }

                        self.request_counter.add(1, attributes)
                        self.request_duration_histogram.record(duration_ms, attributes)

                        # Check SLO targets
                        if path.startswith("/api/v1/enforcement"):
                            # Add SLO target info to response headers
                            response.headers["X-PGC-P99-Latency-Target"] = str(
                                self.p99_latency_target_ms
                            )
                            response.headers["X-PGC-P95-Latency-Target"] = str(
                                self.p95_latency_target_ms
                            )
                            response.headers["X-PGC-Request-Duration"] = f"{duration_ms:.2f}"

                            # Check if request exceeded targets
                            if duration_ms > self.p99_latency_target_ms:
                                logger.warning(
                                    f"Request to {path} exceeded p99 latency target: "
                                    f"{duration_ms:.2f}ms > {self.p99_latency_target_ms}ms"
                                )

                    return response

                finally:
                    # Decrement active requests
                    if self.active_requests_gauge:
                        self.active_requests_gauge.add(-1, {"service": self.service_name})

            logger.info("FastAPI application instrumentation complete")

        except Exception as e:
            logger.error(f"Failed to instrument FastAPI application: {e}")

    def record_cache_result(self, hit: bool, cache_name: str) -> None:
        """Record cache hit or miss.

        Args:
            hit: Whether cache hit or miss
            cache_name: Name of cache
        """
        if not self.enabled:
            return

        attributes = {
            "service": self.service_name,
            "cache_name": cache_name,
        }

        if hit and self.cache_hit_counter:
            self.cache_hit_counter.add(1, attributes)
        elif not hit and self.cache_miss_counter:
            self.cache_miss_counter.add(1, attributes)

    def record_validation(
        self, policy_id: str, validation_type: str, duration_ms: float, success: bool
    ) -> None:
        """Record policy validation.

        Args:
            policy_id: Policy ID
            validation_type: Type of validation
            duration_ms: Validation duration in milliseconds
            success: Whether validation was successful
        """
        if not self.enabled:
            return

        attributes = {
            "service": self.service_name,
            "policy_id": policy_id,
            "validation_type": validation_type,
            "success": success,
        }

        if self.validation_counter:
            self.validation_counter.add(1, attributes)

        if self.validation_duration_histogram:
            self.validation_duration_histogram.record(duration_ms, attributes)

    def create_span(self, name: str, attributes: dict[str, Any] | None = None) -> Any:
        """Create a new span.

        Args:
            name: Span name
            attributes: Span attributes

        Returns:
            Span context manager
        """
        if not self.enabled or not self.tracer:
            # Return no-op context manager
            class NoOpSpan:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc_val, exc_tb):
                    pass

                def set_attribute(self, key, value):
                    pass

                def add_event(self, name, attributes=None):
                    pass

                def record_exception(self, exception):
                    pass

            return NoOpSpan()

        return self.tracer.start_as_current_span(name, attributes=attributes or {})

    def inject_trace_context(self, headers: dict[str, str]) -> None:
        """Inject trace context into headers for distributed tracing.

        Args:
            headers: Request headers to inject context into
        """
        if not self.enabled:
            return

        TraceContextTextMapPropagator().inject(headers)

    def shutdown(self) -> None:
        """Shut down OpenTelemetry instrumentation."""
        if not self.enabled:
            return

        if self.tracer_provider:
            self.tracer_provider.shutdown()

        if self.meter_provider:
            self.meter_provider.shutdown()


# Singleton instance
_telemetry_manager = None


def get_telemetry_manager() -> TelemetryManager:
    """Get or create telemetry manager singleton.

    Returns:
        TelemetryManager instance
    """
    global _telemetry_manager
    if _telemetry_manager is None:
        _telemetry_manager = TelemetryManager()
        _telemetry_manager.setup()

    return _telemetry_manager
