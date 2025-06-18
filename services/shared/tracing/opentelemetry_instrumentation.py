#!/usr/bin/env python3
"""
OpenTelemetry Instrumentation for ACGS-1 Services

Comprehensive distributed tracing implementation with:
- Automatic instrumentation for FastAPI, HTTP clients, databases
- Custom span creation and enrichment
- Performance monitoring with <1% overhead
- Integration with Jaeger and OpenTelemetry Collector
- Constitutional governance operation tracking
"""

import functools
import logging
import os
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.propagators.jaeger import JaegerPropagator
from opentelemetry.propagators.composite import CompositeHTTPPropagator
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.semconv.trace import SpanAttributes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ACGSTracingManager:
    """Comprehensive tracing manager for ACGS-1 services."""

    def __init__(
        self,
        service_name: str,
        service_version: str = "1.0.0",
        environment: str = "production",
        jaeger_endpoint: Optional[str] = None,
        otlp_endpoint: Optional[str] = None,
        sampling_rate: float = 0.1,
        enable_console_export: bool = False
    ):
        """Initialize tracing manager.
        
        Args:
            service_name: Name of the service
            service_version: Version of the service
            environment: Deployment environment
            jaeger_endpoint: Jaeger collector endpoint
            otlp_endpoint: OTLP collector endpoint
            sampling_rate: Trace sampling rate (0.0-1.0)
            enable_console_export: Enable console span export for debugging
        """
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self.sampling_rate = sampling_rate
        self.enable_console_export = enable_console_export
        
        # Default endpoints
        self.jaeger_endpoint = jaeger_endpoint or os.getenv(
            "JAEGER_ENDPOINT", "http://localhost:14268/api/traces"
        )
        self.otlp_endpoint = otlp_endpoint or os.getenv(
            "OTLP_ENDPOINT", "http://localhost:4317"
        )
        
        # Tracing components
        self.tracer_provider: Optional[TracerProvider] = None
        self.tracer: Optional[trace.Tracer] = None
        
        # Performance tracking
        self.instrumentation_overhead = 0.0
        self.span_count = 0
        self.start_time = time.time()

    def initialize_tracing(self) -> bool:
        """Initialize OpenTelemetry tracing infrastructure.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            start_time = time.time()
            
            # Create resource
            resource = Resource.create({
                ResourceAttributes.SERVICE_NAME: self.service_name,
                ResourceAttributes.SERVICE_VERSION: self.service_version,
                ResourceAttributes.DEPLOYMENT_ENVIRONMENT: self.environment,
                ResourceAttributes.SERVICE_NAMESPACE: "acgs-1",
                "service.instance.id": f"{self.service_name}-{int(time.time())}",
                "telemetry.sdk.name": "opentelemetry",
                "telemetry.sdk.language": "python",
                "telemetry.sdk.version": "1.21.0"
            })
            
            # Create tracer provider with sampling
            self.tracer_provider = TracerProvider(
                resource=resource,
                sampler=TraceIdRatioBased(self.sampling_rate)
            )
            
            # Set up exporters
            self._setup_exporters()
            
            # Set global tracer provider
            trace.set_tracer_provider(self.tracer_provider)
            
            # Set up propagators
            self._setup_propagators()
            
            # Get tracer
            self.tracer = trace.get_tracer(
                self.service_name,
                self.service_version
            )
            
            # Set up automatic instrumentation
            self._setup_automatic_instrumentation()
            
            # Track initialization overhead
            self.instrumentation_overhead = time.time() - start_time
            
            logger.info(
                f"✅ OpenTelemetry tracing initialized for {self.service_name} "
                f"(overhead: {self.instrumentation_overhead*1000:.2f}ms, "
                f"sampling: {self.sampling_rate*100:.1f}%)"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize tracing: {e}")
            return False

    def _setup_exporters(self):
        """Set up trace exporters."""
        exporters_added = 0
        
        # OTLP exporter (preferred)
        try:
            otlp_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(
                    otlp_exporter,
                    max_queue_size=2048,
                    max_export_batch_size=512,
                    export_timeout_millis=30000,
                    schedule_delay_millis=1000
                )
            )
            exporters_added += 1
            logger.info(f"✅ OTLP exporter configured: {self.otlp_endpoint}")
        except Exception as e:
            logger.warning(f"⚠️ OTLP exporter failed: {e}")
        
        # Jaeger exporter (fallback)
        try:
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
                collector_endpoint=self.jaeger_endpoint
            )
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(jaeger_exporter)
            )
            exporters_added += 1
            logger.info(f"✅ Jaeger exporter configured: {self.jaeger_endpoint}")
        except Exception as e:
            logger.warning(f"⚠️ Jaeger exporter failed: {e}")
        
        # Console exporter for debugging
        if self.enable_console_export or exporters_added == 0:
            console_exporter = ConsoleSpanExporter()
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(console_exporter)
            )
            logger.info("✅ Console exporter configured")

    def _setup_propagators(self):
        """Set up trace context propagators."""
        # Composite propagator for maximum compatibility
        propagator = CompositeHTTPPropagator([
            JaegerPropagator(),
            B3MultiFormat(),
        ])
        set_global_textmap(propagator)
        logger.info("✅ Trace propagators configured")

    def _setup_automatic_instrumentation(self):
        """Set up automatic instrumentation for common libraries."""
        try:
            # HTTP client instrumentation
            HTTPXClientInstrumentor().instrument()
            RequestsInstrumentor().instrument()
            
            # Database instrumentation
            try:
                Psycopg2Instrumentor().instrument()
                SQLAlchemyInstrumentor().instrument()
            except Exception as e:
                logger.warning(f"⚠️ Database instrumentation failed: {e}")
            
            # Redis instrumentation
            try:
                RedisInstrumentor().instrument()
            except Exception as e:
                logger.warning(f"⚠️ Redis instrumentation failed: {e}")
            
            logger.info("✅ Automatic instrumentation configured")
            
        except Exception as e:
            logger.error(f"❌ Automatic instrumentation failed: {e}")

    def instrument_fastapi_app(self, app):
        """Instrument FastAPI application.
        
        Args:
            app: FastAPI application instance
        """
        try:
            FastAPIInstrumentor.instrument_app(
                app,
                tracer_provider=self.tracer_provider,
                excluded_urls="/health,/metrics,/docs,/openapi.json"
            )
            logger.info(f"✅ FastAPI app instrumented for {self.service_name}")
        except Exception as e:
            logger.error(f"❌ FastAPI instrumentation failed: {e}")

    @contextmanager
    def trace_operation(
        self,
        operation_name: str,
        attributes: Optional[Dict[str, Any]] = None,
        operation_type: Optional[str] = None
    ):
        """Context manager for tracing operations.
        
        Args:
            operation_name: Name of the operation
            attributes: Additional span attributes
            operation_type: Type of operation (constitutional, governance, etc.)
        """
        if not self.tracer:
            yield None
            return
        
        with self.tracer.start_as_current_span(operation_name) as span:
            try:
                # Add basic attributes
                span.set_attribute(SpanAttributes.CODE_FUNCTION, operation_name)
                span.set_attribute("service.name", self.service_name)
                
                if operation_type:
                    span.set_attribute("operation.type", operation_type)
                
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, str(value))
                
                # Track span count
                self.span_count += 1
                
                yield span
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    def trace_constitutional_operation(
        self,
        operation_name: str,
        constitutional_hash: Optional[str] = None,
        policy_id: Optional[str] = None,
        compliance_score: Optional[float] = None
    ):
        """Decorator for tracing constitutional governance operations.
        
        Args:
            operation_name: Name of the constitutional operation
            constitutional_hash: Constitutional hash being validated
            policy_id: Policy ID being processed
            compliance_score: Compliance score if available
        """
        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                attributes = {
                    "operation.category": "constitutional_governance",
                    "operation.name": operation_name
                }
                
                if constitutional_hash:
                    attributes["constitutional.hash"] = constitutional_hash
                if policy_id:
                    attributes["policy.id"] = policy_id
                if compliance_score is not None:
                    attributes["compliance.score"] = compliance_score
                
                with self.trace_operation(
                    f"constitutional.{operation_name}",
                    attributes=attributes,
                    operation_type="constitutional_validation"
                ) as span:
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        
                        # Add result attributes
                        if span and hasattr(result, 'get'):
                            if 'compliance_score' in result:
                                span.set_attribute("result.compliance_score", result['compliance_score'])
                            if 'validation_status' in result:
                                span.set_attribute("result.status", result['validation_status'])
                        
                        return result
                    finally:
                        if span:
                            duration_ms = (time.time() - start_time) * 1000
                            span.set_attribute("operation.duration_ms", duration_ms)
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                attributes = {
                    "operation.category": "constitutional_governance",
                    "operation.name": operation_name
                }
                
                if constitutional_hash:
                    attributes["constitutional.hash"] = constitutional_hash
                if policy_id:
                    attributes["policy.id"] = policy_id
                if compliance_score is not None:
                    attributes["compliance.score"] = compliance_score
                
                with self.trace_operation(
                    f"constitutional.{operation_name}",
                    attributes=attributes,
                    operation_type="constitutional_validation"
                ) as span:
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        
                        # Add result attributes
                        if span and hasattr(result, 'get'):
                            if 'compliance_score' in result:
                                span.set_attribute("result.compliance_score", result['compliance_score'])
                            if 'validation_status' in result:
                                span.set_attribute("result.status", result['validation_status'])
                        
                        return result
                    finally:
                        if span:
                            duration_ms = (time.time() - start_time) * 1000
                            span.set_attribute("operation.duration_ms", duration_ms)
            
            # Return appropriate wrapper based on function type
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator

    def trace_governance_workflow(
        self,
        workflow_name: str,
        workflow_stage: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Decorator for tracing governance workflow operations.
        
        Args:
            workflow_name: Name of the governance workflow
            workflow_stage: Current stage of the workflow
            user_id: User ID initiating the workflow
        """
        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                attributes = {
                    "workflow.name": workflow_name,
                    "workflow.category": "governance"
                }
                
                if workflow_stage:
                    attributes["workflow.stage"] = workflow_stage
                if user_id:
                    attributes["user.id"] = user_id
                
                with self.trace_operation(
                    f"governance.{workflow_name}",
                    attributes=attributes,
                    operation_type="governance_workflow"
                ) as span:
                    return await func(*args, **kwargs)
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                attributes = {
                    "workflow.name": workflow_name,
                    "workflow.category": "governance"
                }
                
                if workflow_stage:
                    attributes["workflow.stage"] = workflow_stage
                if user_id:
                    attributes["user.id"] = user_id
                
                with self.trace_operation(
                    f"governance.{workflow_name}",
                    attributes=attributes,
                    operation_type="governance_workflow"
                ) as span:
                    return func(*args, **kwargs)
            
            # Return appropriate wrapper based on function type
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get tracing performance metrics.
        
        Returns:
            Dictionary containing performance metrics
        """
        uptime = time.time() - self.start_time
        
        return {
            "service_name": self.service_name,
            "uptime_seconds": uptime,
            "total_spans_created": self.span_count,
            "spans_per_second": self.span_count / uptime if uptime > 0 else 0,
            "initialization_overhead_ms": self.instrumentation_overhead * 1000,
            "sampling_rate": self.sampling_rate,
            "tracer_active": self.tracer is not None
        }

    def shutdown(self):
        """Shutdown tracing infrastructure gracefully."""
        try:
            if self.tracer_provider:
                # Force flush all pending spans
                self.tracer_provider.force_flush(timeout_millis=5000)
                
                # Shutdown span processors
                self.tracer_provider.shutdown()
                
            logger.info(f"✅ Tracing shutdown complete for {self.service_name}")
            
        except Exception as e:
            logger.error(f"❌ Tracing shutdown failed: {e}")


# Global tracing manager instance
_tracing_manager: Optional[ACGSTracingManager] = None


def get_tracing_manager(
    service_name: str,
    service_version: str = "1.0.0",
    environment: str = "production",
    **kwargs
) -> ACGSTracingManager:
    """Get or create global tracing manager instance.
    
    Args:
        service_name: Name of the service
        service_version: Version of the service
        environment: Deployment environment
        **kwargs: Additional configuration options
    
    Returns:
        ACGSTracingManager instance
    """
    global _tracing_manager
    
    if _tracing_manager is None:
        _tracing_manager = ACGSTracingManager(
            service_name=service_name,
            service_version=service_version,
            environment=environment,
            **kwargs
        )
        _tracing_manager.initialize_tracing()
    
    return _tracing_manager


def initialize_service_tracing(
    app,
    service_name: str,
    service_version: str = "1.0.0",
    environment: str = "production",
    **kwargs
) -> ACGSTracingManager:
    """Initialize tracing for a FastAPI service.
    
    Args:
        app: FastAPI application instance
        service_name: Name of the service
        service_version: Version of the service
        environment: Deployment environment
        **kwargs: Additional configuration options
    
    Returns:
        ACGSTracingManager instance
    """
    tracing_manager = get_tracing_manager(
        service_name=service_name,
        service_version=service_version,
        environment=environment,
        **kwargs
    )
    
    # Instrument the FastAPI app
    tracing_manager.instrument_fastapi_app(app)
    
    return tracing_manager
