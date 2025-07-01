#!/usr/bin/env python3
"""
ACGS Advanced Observability Stack
Comprehensive observability with OpenTelemetry, distributed tracing, advanced metrics, and constitutional compliance monitoring.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    start_http_server,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ObservabilityLevel(Enum):
    """Observability levels."""

    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    CONSTITUTIONAL = "constitutional"


class TraceType(Enum):
    """Trace types for categorization."""

    REQUEST = "request"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    CONSTITUTIONAL = "constitutional"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class ObservabilityConfig:
    """Observability configuration."""

    service_name: str
    service_version: str
    environment: str = "production"

    # Tracing configuration
    tracing_enabled: bool = True
    sampling_rate: float = 1.0
    jaeger_endpoint: str = "http://localhost:14268/api/traces"

    # Metrics configuration
    metrics_enabled: bool = True
    prometheus_port: int = 8110

    # Logging configuration
    log_level: str = "INFO"
    structured_logging: bool = True

    # Constitutional compliance
    constitutional_monitoring: bool = True
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class ConstitutionalTrace:
    """Constitutional compliance trace."""

    trace_id: str
    span_id: str
    operation: str
    constitutional_hash: str
    compliance_score: float
    validation_time_ms: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AdvancedObservabilityStack:
    """Advanced observability stack for ACGS."""

    def __init__(self, config: ObservabilityConfig):
        self.config = config

        # OpenTelemetry components
        self.tracer_provider = None
        self.meter_provider = None
        self.tracer = None
        self.meter = None

        # Metrics
        self.registry = CollectorRegistry()
        self.setup_custom_metrics()

        # Constitutional compliance tracking
        self.constitutional_traces: list[ConstitutionalTrace] = []
        self.compliance_violations: list[dict] = []

        # Service instrumentation
        self.instrumented_services = set()

        logger.info(
            f"Advanced Observability Stack initialized for {config.service_name}"
        )

    def setup_custom_metrics(self):
        """Setup custom Prometheus metrics."""
        self.constitutional_compliance_score = Gauge(
            "acgs_constitutional_compliance_score",
            "Constitutional compliance score",
            ["service", "operation"],
            registry=self.registry,
        )

        self.constitutional_validation_duration = Histogram(
            "acgs_constitutional_validation_duration_seconds",
            "Constitutional validation duration",
            ["service", "operation"],
            registry=self.registry,
        )

        self.trace_constitutional_operations = Counter(
            "acgs_trace_constitutional_operations_total",
            "Total constitutional operations traced",
            ["service", "operation", "status"],
            registry=self.registry,
        )

        self.observability_health_score = Gauge(
            "acgs_observability_health_score",
            "Overall observability health score",
            ["component"],
            registry=self.registry,
        )

        self.distributed_trace_latency = Histogram(
            "acgs_distributed_trace_latency_seconds",
            "End-to-end distributed trace latency",
            ["service_chain"],
            registry=self.registry,
        )

    async def initialize_observability(self):
        """Initialize the observability stack."""
        logger.info("Initializing Advanced Observability Stack...")

        # Initialize OpenTelemetry
        await self.setup_opentelemetry()

        # Start metrics server
        if self.config.metrics_enabled:
            start_http_server(self.config.prometheus_port, registry=self.registry)
            logger.info(
                f"Observability metrics server started on port {self.config.prometheus_port}"
            )

        # Initialize instrumentation
        await self.setup_instrumentation()

        # Start monitoring tasks
        asyncio.create_task(self.constitutional_monitoring_loop())
        asyncio.create_task(self.observability_health_loop())
        asyncio.create_task(self.trace_analysis_loop())

        logger.info("Advanced Observability Stack initialized")

    async def setup_opentelemetry(self):
        """Setup OpenTelemetry tracing and metrics."""
        try:
            # Create resource
            resource = Resource.create(
                {
                    "service.name": self.config.service_name,
                    "service.version": self.config.service_version,
                    "service.environment": self.config.environment,
                    "constitutional.hash": self.config.constitutional_hash,
                }
            )

            # Setup tracing
            if self.config.tracing_enabled:
                self.tracer_provider = TracerProvider(resource=resource)

                # Jaeger exporter
                jaeger_exporter = JaegerExporter(
                    agent_host_name="localhost",
                    agent_port=6831,
                )

                span_processor = BatchSpanProcessor(jaeger_exporter)
                self.tracer_provider.add_span_processor(span_processor)

                trace.set_tracer_provider(self.tracer_provider)
                self.tracer = trace.get_tracer(__name__)

                logger.info("OpenTelemetry tracing initialized")

            # Setup metrics
            if self.config.metrics_enabled:
                prometheus_reader = PrometheusMetricReader()
                self.meter_provider = MeterProvider(
                    resource=resource, metric_readers=[prometheus_reader]
                )

                metrics.set_meter_provider(self.meter_provider)
                self.meter = metrics.get_meter(__name__)

                logger.info("OpenTelemetry metrics initialized")

        except Exception as e:
            logger.error(f"Error setting up OpenTelemetry: {e}")

    async def setup_instrumentation(self):
        """Setup automatic instrumentation for common libraries."""
        try:
            # FastAPI instrumentation
            FastAPIInstrumentor().instrument()
            self.instrumented_services.add("fastapi")

            # AsyncPG instrumentation
            AsyncPGInstrumentor().instrument()
            self.instrumented_services.add("asyncpg")

            # AioHTTP client instrumentation
            AioHttpClientInstrumentor().instrument()
            self.instrumented_services.add("aiohttp")

            logger.info(
                f"Instrumented services: {', '.join(self.instrumented_services)}"
            )

        except Exception as e:
            logger.error(f"Error setting up instrumentation: {e}")

    def create_constitutional_span(
        self, operation: str, constitutional_hash: str = None
    ) -> trace.Span:
        """Create a span for constitutional operations."""
        if not self.tracer:
            return None

        span = self.tracer.start_span(
            f"constitutional.{operation}",
            attributes={
                "constitutional.hash": constitutional_hash or CONSTITUTIONAL_HASH,
                "constitutional.operation": operation,
                "service.name": self.config.service_name,
                "trace.type": TraceType.CONSTITUTIONAL.value,
            },
        )

        return span

    async def trace_constitutional_operation(
        self, operation: str, func, *args, **kwargs
    ):
        """Trace a constitutional operation with compliance validation."""
        start_time = time.time()

        with self.create_constitutional_span(operation) as span:
            try:
                # Execute the operation
                result = (
                    await func(*args, **kwargs)
                    if asyncio.iscoroutinefunction(func)
                    else func(*args, **kwargs)
                )

                # Validate constitutional compliance
                compliance_score = await self.validate_constitutional_compliance(
                    operation, result
                )

                # Record metrics
                validation_time = (time.time() - start_time) * 1000  # Convert to ms

                self.constitutional_compliance_score.labels(
                    service=self.config.service_name, operation=operation
                ).set(compliance_score)

                self.constitutional_validation_duration.labels(
                    service=self.config.service_name, operation=operation
                ).observe(
                    validation_time / 1000
                )  # Convert back to seconds

                # Add span attributes
                if span:
                    span.set_attribute(
                        "constitutional.compliance_score", compliance_score
                    )
                    span.set_attribute(
                        "constitutional.validation_time_ms", validation_time
                    )
                    span.set_attribute("operation.status", "success")

                # Record constitutional trace
                constitutional_trace = ConstitutionalTrace(
                    trace_id=span.get_span_context().trace_id if span else "unknown",
                    span_id=span.get_span_context().span_id if span else "unknown",
                    operation=operation,
                    constitutional_hash=CONSTITUTIONAL_HASH,
                    compliance_score=compliance_score,
                    validation_time_ms=validation_time,
                )

                self.constitutional_traces.append(constitutional_trace)

                # Keep only last 1000 traces
                if len(self.constitutional_traces) > 1000:
                    self.constitutional_traces = self.constitutional_traces[-1000:]

                # Record counter
                self.trace_constitutional_operations.labels(
                    service=self.config.service_name,
                    operation=operation,
                    status="success",
                ).inc()

                return result

            except Exception as e:
                # Record error
                if span:
                    span.set_attribute("operation.status", "error")
                    span.set_attribute("error.message", str(e))

                self.trace_constitutional_operations.labels(
                    service=self.config.service_name,
                    operation=operation,
                    status="error",
                ).inc()

                logger.error(f"Constitutional operation {operation} failed: {e}")
                raise

    async def validate_constitutional_compliance(
        self, operation: str, result: Any
    ) -> float:
        """Validate constitutional compliance for an operation."""
        try:
            # Basic compliance checks
            compliance_score = 100.0

            # Check if result contains constitutional hash
            if hasattr(result, "get") and callable(result.get):
                result_hash = result.get("constitutional_hash")
                if result_hash != CONSTITUTIONAL_HASH:
                    compliance_score -= 50.0

                    # Record violation
                    violation = {
                        "operation": operation,
                        "expected_hash": CONSTITUTIONAL_HASH,
                        "actual_hash": result_hash,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    self.compliance_violations.append(violation)

            # Additional compliance checks based on operation type
            if operation in ["policy_generation", "constitutional_validation"]:
                # Critical operations require perfect compliance
                if compliance_score < 100.0:
                    compliance_score = 0.0

            return compliance_score

        except Exception as e:
            logger.error(f"Error validating constitutional compliance: {e}")
            return 0.0

    async def create_distributed_trace(
        self, service_chain: list[str], operation: str
    ) -> str:
        """Create a distributed trace across multiple services."""
        if not self.tracer:
            return None

        trace_id = None
        start_time = time.time()

        try:
            with self.tracer.start_as_current_span(
                f"distributed.{operation}"
            ) as root_span:
                trace_id = root_span.get_span_context().trace_id

                # Add trace attributes
                root_span.set_attribute(
                    "distributed.service_chain", ",".join(service_chain)
                )
                root_span.set_attribute("distributed.operation", operation)
                root_span.set_attribute("constitutional.hash", CONSTITUTIONAL_HASH)

                # Simulate service calls (in practice, these would be actual service calls)
                for i, service in enumerate(service_chain):
                    with self.tracer.start_as_current_span(
                        f"{service}.{operation}"
                    ) as service_span:
                        service_span.set_attribute("service.name", service)
                        service_span.set_attribute("service.order", i + 1)

                        # Simulate processing time
                        await asyncio.sleep(0.01)

                # Record distributed trace latency
                total_latency = time.time() - start_time
                self.distributed_trace_latency.labels(
                    service_chain=",".join(service_chain)
                ).observe(total_latency)

                return str(trace_id)

        except Exception as e:
            logger.error(f"Error creating distributed trace: {e}")
            return None

    async def constitutional_monitoring_loop(self):
        """Monitor constitutional compliance continuously."""
        while True:
            try:
                # Analyze recent constitutional traces
                recent_traces = [
                    trace
                    for trace in self.constitutional_traces
                    if (datetime.now(timezone.utc) - trace.timestamp).total_seconds()
                    < 300
                ]

                if recent_traces:
                    # Calculate average compliance score
                    avg_compliance = sum(
                        t.compliance_score for t in recent_traces
                    ) / len(recent_traces)

                    # Update overall constitutional compliance metric
                    self.constitutional_compliance_score.labels(
                        service=self.config.service_name, operation="overall"
                    ).set(avg_compliance)

                    # Check for compliance violations
                    violations = [t for t in recent_traces if t.compliance_score < 95.0]
                    if violations:
                        logger.warning(
                            f"Constitutional compliance violations detected: {len(violations)}"
                        )

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error in constitutional monitoring loop: {e}")
                await asyncio.sleep(120)

    async def observability_health_loop(self):
        """Monitor observability stack health."""
        while True:
            try:
                # Check tracing health
                tracing_health = (
                    100.0 if self.tracer and self.config.tracing_enabled else 0.0
                )
                self.observability_health_score.labels(component="tracing").set(
                    tracing_health
                )

                # Check metrics health
                metrics_health = (
                    100.0 if self.meter and self.config.metrics_enabled else 0.0
                )
                self.observability_health_score.labels(component="metrics").set(
                    metrics_health
                )

                # Check instrumentation health
                instrumentation_health = (
                    len(self.instrumented_services) * 25.0
                )  # Max 4 services = 100%
                self.observability_health_score.labels(component="instrumentation").set(
                    min(100.0, instrumentation_health)
                )

                # Check constitutional monitoring health
                constitutional_health = (
                    100.0 if self.config.constitutional_monitoring else 0.0
                )
                self.observability_health_score.labels(component="constitutional").set(
                    constitutional_health
                )

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error in observability health loop: {e}")
                await asyncio.sleep(60)

    async def trace_analysis_loop(self):
        """Analyze traces for patterns and anomalies."""
        while True:
            try:
                # Analyze constitutional traces for patterns
                if len(self.constitutional_traces) >= 10:
                    await self.analyze_constitutional_patterns()

                # Clean up old traces
                cutoff_time = datetime.now(timezone.utc).timestamp() - 3600  # 1 hour
                self.constitutional_traces = [
                    trace
                    for trace in self.constitutional_traces
                    if trace.timestamp.timestamp() > cutoff_time
                ]

                await asyncio.sleep(300)  # Analyze every 5 minutes

            except Exception as e:
                logger.error(f"Error in trace analysis loop: {e}")
                await asyncio.sleep(600)

    async def analyze_constitutional_patterns(self):
        """Analyze constitutional compliance patterns."""
        try:
            # Group traces by operation
            operation_groups = {}
            for trace in self.constitutional_traces:
                if trace.operation not in operation_groups:
                    operation_groups[trace.operation] = []
                operation_groups[trace.operation].append(trace)

            # Analyze each operation
            for operation, traces in operation_groups.items():
                if len(traces) >= 5:  # Minimum traces for analysis
                    avg_compliance = sum(t.compliance_score for t in traces) / len(
                        traces
                    )
                    avg_validation_time = sum(
                        t.validation_time_ms for t in traces
                    ) / len(traces)

                    # Check for anomalies
                    if avg_compliance < 95.0:
                        logger.warning(
                            f"Low compliance detected for {operation}: {avg_compliance:.1f}%"
                        )

                    if avg_validation_time > 100.0:  # 100ms threshold
                        logger.warning(
                            f"Slow validation detected for {operation}: {avg_validation_time:.1f}ms"
                        )

        except Exception as e:
            logger.error(f"Error analyzing constitutional patterns: {e}")

    def get_observability_status(self) -> dict[str, Any]:
        """Get observability stack status."""
        return {
            "service_name": self.config.service_name,
            "service_version": self.config.service_version,
            "environment": self.config.environment,
            "tracing_enabled": self.config.tracing_enabled,
            "metrics_enabled": self.config.metrics_enabled,
            "constitutional_monitoring": self.config.constitutional_monitoring,
            "instrumented_services": list(self.instrumented_services),
            "constitutional_traces_count": len(self.constitutional_traces),
            "compliance_violations_count": len(self.compliance_violations),
            "constitutional_hash": self.config.constitutional_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global observability stack instance
observability_config = ObservabilityConfig(
    service_name="acgs-platform", service_version="1.0.0", environment="production"
)
observability_stack = AdvancedObservabilityStack(observability_config)

if __name__ == "__main__":

    async def main():
        await observability_stack.initialize_observability()

        try:
            # Keep running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down advanced observability stack...")

    asyncio.run(main())
