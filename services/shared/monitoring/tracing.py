"""
Distributed Tracing System for ACGS
Constitutional Hash: cdd01ef066bc6cf2

OpenTelemetry-compatible distributed tracing for request flow monitoring.
"""

import asyncio
import logging
import threading
import uuid
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class SpanStatus(str, Enum):
    """Span status levels."""

    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class SpanKind(str, Enum):
    """Span kinds for different operation types."""

    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


@dataclass
class SpanContext:
    """Context information for tracing spans."""

    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    baggage: dict[str, str] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if span context is valid."""
        return bool(self.trace_id and self.span_id)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "baggage": self.baggage,
        }


@dataclass
class SpanEvent:
    """Event within a span."""

    name: str
    timestamp: datetime
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "timestamp": self.timestamp.isoformat(),
            "attributes": self.attributes,
        }


@dataclass
class Span:
    """Represents a single span in distributed tracing."""

    operation_name: str
    span_context: SpanContext
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime | None = None
    status: SpanStatus = SpanStatus.OK
    kind: SpanKind = SpanKind.INTERNAL
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[SpanEvent] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)
    tags: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize span with constitutional compliance."""
        self.attributes["constitutional_hash"] = "cdd01ef066bc6cf2"
        self.attributes["span_id"] = self.span_context.span_id
        self.attributes["trace_id"] = self.span_context.trace_id

    def set_attribute(self, key: str, value: Any) -> "Span":
        """Set span attribute."""
        self.attributes[key] = value
        return self

    def set_tag(self, key: str, value: str) -> "Span":
        """Set span tag."""
        self.tags[key] = value
        return self

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> "Span":
        """Add event to span."""
        event = SpanEvent(
            name=name, timestamp=datetime.utcnow(), attributes=attributes or {}
        )
        self.events.append(event)
        return self

    def log(self, message: str) -> "Span":
        """Add log message to span."""
        self.logs.append(f"{datetime.utcnow().isoformat()}: {message}")
        return self

    def set_status(self, status: SpanStatus, description: str | None = None) -> "Span":
        """Set span status."""
        self.status = status
        if description:
            self.attributes["status_description"] = description
        return self

    def record_exception(self, exception: Exception) -> "Span":
        """Record exception in span."""
        self.set_status(SpanStatus.ERROR, str(exception))
        self.attributes["exception.type"] = type(exception).__name__
        self.attributes["exception.message"] = str(exception)
        self.add_event(
            "exception",
            {
                "exception.type": type(exception).__name__,
                "exception.message": str(exception),
            },
        )
        return self

    def finish(self) -> None:
        """Finish the span."""
        if self.end_time is None:
            self.end_time = datetime.utcnow()
            self.attributes["duration_ms"] = (
                self.end_time - self.start_time
            ).total_seconds() * 1000

    @property
    def is_finished(self) -> bool:
        """Check if span is finished."""
        return self.end_time is not None

    @property
    def duration_ms(self) -> float | None:
        """Get span duration in milliseconds."""
        if not self.is_finished:
            return None
        return (self.end_time - self.start_time).total_seconds() * 1000

    def to_dict(self) -> dict[str, Any]:
        """Convert span to dictionary representation."""
        return {
            "operation_name": self.operation_name,
            "span_context": self.span_context.to_dict(),
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "kind": self.kind.value,
            "attributes": self.attributes,
            "events": [event.to_dict() for event in self.events],
            "logs": self.logs,
            "tags": self.tags,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


class TraceExporter(ABC):
    """Abstract base class for trace exporters."""

    @abstractmethod
    async def export(self, spans: list[Span]) -> None:
        """Export spans to external system."""


class ConsoleTraceExporter(TraceExporter):
    """Console trace exporter for development."""

    async def export(self, spans: list[Span]) -> None:
        """Export spans to console."""
        for span in spans:
            logger.info(
                f"Trace Export: {span.operation_name} "
                f"({span.span_context.trace_id[:8]}...{span.span_context.span_id[:8]}) "
                f"- {span.duration_ms:.2f}ms - {span.status.value}"
            )


class JaegerTraceExporter(TraceExporter):
    """Jaeger trace exporter."""

    def __init__(self, endpoint: str = "http://localhost:14268/api/traces"):
        self.endpoint = endpoint

    async def export(self, spans: list[Span]) -> None:
        """Export spans to Jaeger."""
        # In production, use jaeger-client or opentelemetry-exporter-jaeger
        logger.info(f"Would export {len(spans)} spans to Jaeger at {self.endpoint}")
        for span in spans:
            logger.debug(f"Jaeger span: {span.to_dict()}")


class TracingManager:
    """Central tracing management system."""

    def __init__(self, service_name: str = "acgs_service"):
        self.service_name = service_name
        self._exporters: list[TraceExporter] = []
        self._active_spans: dict[str, Span] = {}
        self._finished_spans: list[Span] = []
        self._export_batch_size = 100
        self._export_timeout = 30.0
        self._export_interval = 10.0
        self._running = False
        self._export_task: asyncio.Task | None = None
        self._lock = threading.Lock()

    def add_exporter(self, exporter: TraceExporter) -> None:
        """Add trace exporter."""
        self._exporters.append(exporter)
        logger.info(f"Added trace exporter: {type(exporter).__name__}")

    def create_span(
        self,
        operation_name: str,
        parent_context: SpanContext | None = None,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: dict[str, Any] | None = None,
    ) -> Span:
        """Create a new span."""

        # Generate IDs
        trace_id = (
            parent_context.trace_id
            if parent_context
            else str(uuid.uuid4()).replace("-", "")
        )
        span_id = str(uuid.uuid4()).replace("-", "")[:16]
        parent_span_id = parent_context.span_id if parent_context else None

        # Create span context
        span_context = SpanContext(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            baggage=parent_context.baggage.copy() if parent_context else {},
        )

        # Create span
        span = Span(
            operation_name=operation_name,
            span_context=span_context,
            kind=kind,
            attributes=attributes or {},
        )

        # Add service information
        span.set_attribute("service.name", self.service_name)
        span.set_attribute("service.version", "1.0.0")

        # Track active span
        with self._lock:
            self._active_spans[span_id] = span

        logger.debug(f"Created span: {operation_name} ({trace_id[:8]}...{span_id[:8]})")
        return span

    def finish_span(self, span: Span) -> None:
        """Finish and record span."""
        if span.is_finished:
            return

        span.finish()

        with self._lock:
            # Remove from active spans
            self._active_spans.pop(span.span_context.span_id, None)

            # Add to finished spans
            self._finished_spans.append(span)

            # Export if batch is full
            if len(self._finished_spans) >= self._export_batch_size:
                asyncio.create_task(self._export_batch())

        logger.debug(f"Finished span: {span.operation_name} - {span.duration_ms:.2f}ms")

    async def _export_batch(self) -> None:
        """Export batch of finished spans."""
        with self._lock:
            spans_to_export = self._finished_spans.copy()
            self._finished_spans.clear()

        if not spans_to_export or not self._exporters:
            return

        for exporter in self._exporters:
            try:
                await asyncio.wait_for(
                    exporter.export(spans_to_export), timeout=self._export_timeout
                )
            except Exception as e:
                logger.exception(
                    f"Error exporting spans with {type(exporter).__name__}: {e}"
                )

    async def start_export_loop(self) -> None:
        """Start automatic span export loop."""
        if self._running:
            return

        self._running = True
        logger.info(f"Starting trace export loop (interval: {self._export_interval}s)")

        while self._running:
            try:
                await self._export_batch()
                await asyncio.sleep(self._export_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in trace export loop: {e}")
                await asyncio.sleep(self._export_interval)

    def stop_export_loop(self) -> None:
        """Stop automatic span export loop."""
        self._running = False
        if self._export_task:
            self._export_task.cancel()

    async def flush(self) -> None:
        """Flush all pending spans."""
        await self._export_batch()

    def get_active_spans(self) -> list[Span]:
        """Get all active spans."""
        with self._lock:
            return list(self._active_spans.values())

    def get_trace_stats(self) -> dict[str, Any]:
        """Get tracing statistics."""
        with self._lock:
            return {
                "service_name": self.service_name,
                "active_spans": len(self._active_spans),
                "finished_spans": len(self._finished_spans),
                "exporters_count": len(self._exporters),
                "export_batch_size": self._export_batch_size,
                "constitutional_hash": "cdd01ef066bc6cf2",
            }


# Context variable for current span
_current_span: ContextVar[Span | None] = ContextVar("current_span", default=None)

# Global tracing manager
_global_tracer = TracingManager()


def get_tracer() -> TracingManager:
    """Get the global tracing manager."""
    return _global_tracer


def get_current_span() -> Span | None:
    """Get the current active span."""
    return _current_span.get()


def set_current_span(span: Span | None) -> None:
    """Set the current active span."""
    _current_span.set(span)


@asynccontextmanager
async def trace_operation(
    operation_name: str,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes: dict[str, Any] | None = None,
    parent_context: SpanContext | None = None,
) -> AsyncGenerator[Span, None]:
    """Context manager for tracing operations."""
    tracer = get_tracer()

    # Use current span as parent if no parent provided
    if parent_context is None:
        current_span = get_current_span()
        if current_span:
            parent_context = current_span.span_context

    # Create new span
    span = tracer.create_span(
        operation_name=operation_name,
        parent_context=parent_context,
        kind=kind,
        attributes=attributes,
    )

    # Set as current span
    previous_span = get_current_span()
    set_current_span(span)

    try:
        yield span
    except Exception as e:
        span.record_exception(e)
        raise
    finally:
        # Restore previous span
        set_current_span(previous_span)
        # Finish current span
        tracer.finish_span(span)


class TraceLogger:
    """Logger that includes trace information."""

    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)

    def _add_trace_info(self, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        """Add trace information to log extra."""
        if extra is None:
            extra = {}

        current_span = get_current_span()
        if current_span:
            extra.update(
                {
                    "trace_id": current_span.span_context.trace_id,
                    "span_id": current_span.span_context.span_id,
                    "operation_name": current_span.operation_name,
                }
            )

        extra["constitutional_hash"] = "cdd01ef066bc6cf2"
        return extra

    def debug(self, msg: str, *args, extra: dict[str, Any] | None = None, **kwargs):
        """Log debug with trace info."""
        self.logger.debug(msg, *args, extra=self._add_trace_info(extra), **kwargs)

    def info(self, msg: str, *args, extra: dict[str, Any] | None = None, **kwargs):
        """Log info with trace info."""
        self.logger.info(msg, *args, extra=self._add_trace_info(extra), **kwargs)

    def warning(self, msg: str, *args, extra: dict[str, Any] | None = None, **kwargs):
        """Log warning with trace info."""
        self.logger.warning(msg, *args, extra=self._add_trace_info(extra), **kwargs)

    def error(self, msg: str, *args, extra: dict[str, Any] | None = None, **kwargs):
        """Log error with trace info."""
        self.logger.error(msg, *args, extra=self._add_trace_info(extra), **kwargs)

    def critical(self, msg: str, *args, extra: dict[str, Any] | None = None, **kwargs):
        """Log critical with trace info."""
        self.logger.critical(msg, *args, extra=self._add_trace_info(extra), **kwargs)


# Decorator for automatic tracing
def traced(operation_name: str | None = None, kind: SpanKind = SpanKind.INTERNAL):
    """Decorator for automatic function tracing."""

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            async def async_wrapper(*args, **kwargs):
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                async with trace_operation(op_name, kind) as span:
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    return await func(*args, **kwargs)

            return async_wrapper

        def sync_wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            # For sync functions, we'll use a simple approach
            tracer = get_tracer()
            span = tracer.create_span(op_name, kind=kind)
            span.set_attribute("function.name", func.__name__)
            span.set_attribute("function.module", func.__module__)

            try:
                return func(*args, **kwargs)
            except Exception as e:
                span.record_exception(e)
                raise
            finally:
                tracer.finish_span(span)

        return sync_wrapper

    return decorator


# Setup default tracing
def setup_default_tracing(service_name: str = "acgs_service") -> None:
    """Set up default tracing configuration."""
    global _global_tracer
    _global_tracer = TracingManager(service_name)

    # Add console exporter for development
    _global_tracer.add_exporter(ConsoleTraceExporter())

    # Add Jaeger exporter if endpoint is available
    try:
        jaeger_exporter = JaegerTraceExporter()
        _global_tracer.add_exporter(jaeger_exporter)
    except Exception as e:
        logger.warning(f"Failed to setup Jaeger exporter: {e}")

    logger.info(f"Default tracing configured for service: {service_name}")
