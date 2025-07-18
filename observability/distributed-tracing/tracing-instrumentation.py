#!/usr/bin/env python3
"""
ACGS-2 Distributed Tracing Instrumentation
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive tracing instrumentation for ACGS-2 services with constitutional compliance.
"""

import asyncio
import functools
import json
import logging
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import os
import sys
from datetime import datetime

# OpenTelemetry imports
from opentelemetry import trace, context, baggage, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.propagators.jaeger import JaegerPropagator
from opentelemetry.propagators.textmap import TextMapPropagator
from opentelemetry.context.context import Context
from opentelemetry.trace.span import Span

class ConstitutionalComplianceLevel(Enum):
    """Constitutional compliance levels for tracing"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"
    PENDING = "pending"

class TraceCategory(Enum):
    """Trace categories for ACGS-2 system"""
    CONSTITUTIONAL = "constitutional"
    CONSENSUS = "consensus"
    AGENT_COORDINATION = "agent_coordination"
    POLICY_EVALUATION = "policy_evaluation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"
    MONITORING = "monitoring"
    ADMIN = "admin"

@dataclass
class ConstitutionalTraceContext:
    """Constitutional trace context for ACGS-2"""
    constitutional_hash: str
    service_name: str
    operation_name: str
    compliance_level: ConstitutionalComplianceLevel
    category: TraceCategory
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    performance_tier: str = "standard"
    security_level: str = "standard"
    
    def to_attributes(self) -> Dict[str, Any]:
        """Convert to OpenTelemetry attributes"""
        attributes = {
            "constitutional_hash": self.constitutional_hash,
            "service.name": self.service_name,
            "operation.name": self.operation_name,
            "constitutional.compliance_level": self.compliance_level.value,
            "trace.category": self.category.value,
            "performance.tier": self.performance_tier,
            "security.level": self.security_level,
            "acgs.version": "v1.0.0",
            "environment": "production"
        }
        
        if self.user_id:
            attributes["user.id"] = self.user_id
        if self.session_id:
            attributes["session.id"] = self.session_id
        if self.request_id:
            attributes["request.id"] = self.request_id
            
        return attributes

class ACGSTracingInstrumentation:
    """
    ACGS-2 Distributed Tracing Instrumentation
    Constitutional Hash: cdd01ef066bc6cf2
    
    Provides comprehensive tracing instrumentation for ACGS-2 services
    with constitutional compliance monitoring and performance tracking.
    """
    
    def __init__(self, 
                 service_name: str,
                 service_version: str = "v1.0.0",
                 jaeger_endpoint: str = "http://jaeger-collector.jaeger-system.svc.cluster.local:14268/api/traces",
                 otlp_endpoint: str = "http://otel-collector.acgs-system.svc.cluster.local:4317",
                 constitutional_hash: str = "cdd01ef066bc6cf2"):
        
        self.service_name = service_name
        self.service_version = service_version
        self.jaeger_endpoint = jaeger_endpoint
        self.otlp_endpoint = otlp_endpoint
        self.constitutional_hash = constitutional_hash
        
        # Initialize OpenTelemetry components
        self.tracer_provider = None
        self.meter_provider = None
        self.tracer = None
        self.meter = None
        self.logger = self._setup_logging()
        
        # Performance tracking
        self.performance_metrics = {
            "traces_created": 0,
            "spans_created": 0,
            "constitutional_violations": 0,
            "high_latency_spans": 0,
            "error_spans": 0
        }
        
        # Initialize instrumentation
        self._setup_tracing()
        self._setup_metrics()
        self._setup_instrumentors()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for tracing instrumentation"""
        logger = logging.getLogger(f"acgs_tracing_{self.service_name}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - CONSTITUTIONAL_HASH:{self.constitutional_hash} - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _setup_tracing(self):
        """Setup OpenTelemetry tracing"""
        # Create resource with constitutional attributes
        resource = Resource.create({
            ResourceAttributes.SERVICE_NAME: self.service_name,
            ResourceAttributes.SERVICE_VERSION: self.service_version,
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT: "production",
            "constitutional_hash": self.constitutional_hash,
            "acgs.version": "v1.0.0",
            "k8s.cluster.name": "acgs-cluster",
            "k8s.namespace.name": "acgs-system"
        })
        
        # Create tracer provider
        self.tracer_provider = TracerProvider(resource=resource)
        
        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name="jaeger-agent.jaeger-system.svc.cluster.local",
            agent_port=6831,
            collector_endpoint=self.jaeger_endpoint,
            username=None,
            password=None,
            max_tag_value_length=None
        )
        
        # Configure OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=self.otlp_endpoint,
            headers={"constitutional-hash": self.constitutional_hash}
        )
        
        # Add span processors
        self.tracer_provider.add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
        self.tracer_provider.add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )
        
        # Set global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        
        # Get tracer
        self.tracer = trace.get_tracer(
            self.service_name,
            self.service_version,
            schema_url="https://opentelemetry.io/schemas/1.20.0"
        )
        
        self.logger.info(f"✅ Tracing initialized for {self.service_name}")
    
    def _setup_metrics(self):
        """Setup OpenTelemetry metrics"""
        # Create metrics exporter
        metrics_exporter = OTLPMetricExporter(
            endpoint=self.otlp_endpoint,
            headers={"constitutional-hash": self.constitutional_hash}
        )
        
        # Create metric reader
        metric_reader = PeriodicExportingMetricReader(
            exporter=metrics_exporter,
            export_interval_millis=30000
        )
        
        # Create meter provider
        self.meter_provider = MeterProvider(
            resource=Resource.create({
                ResourceAttributes.SERVICE_NAME: self.service_name,
                ResourceAttributes.SERVICE_VERSION: self.service_version,
                "constitutional_hash": self.constitutional_hash
            }),
            metric_readers=[metric_reader]
        )
        
        # Set global meter provider
        metrics.set_meter_provider(self.meter_provider)
        
        # Get meter
        self.meter = metrics.get_meter(self.service_name, self.service_version)
        
        # Create performance metrics
        self.trace_counter = self.meter.create_counter(
            "acgs_traces_total",
            description="Total number of traces created",
            unit="1"
        )
        
        self.span_counter = self.meter.create_counter(
            "acgs_spans_total",
            description="Total number of spans created",
            unit="1"
        )
        
        self.constitutional_violation_counter = self.meter.create_counter(
            "acgs_constitutional_violations_total",
            description="Total number of constitutional violations detected",
            unit="1"
        )
        
        self.span_duration_histogram = self.meter.create_histogram(
            "acgs_span_duration_ms",
            description="Span duration in milliseconds",
            unit="ms"
        )
        
        self.logger.info(f"✅ Metrics initialized for {self.service_name}")
    
    def _setup_instrumentors(self):
        """Setup automatic instrumentation"""
        # FastAPI instrumentation
        FastAPIInstrumentor().instrument(
            tracer_provider=self.tracer_provider,
            meter_provider=self.meter_provider
        )
        
        # Requests instrumentation
        RequestsInstrumentor().instrument(
            tracer_provider=self.tracer_provider
        )
        
        # HTTPX instrumentation
        HTTPXClientInstrumentor().instrument(
            tracer_provider=self.tracer_provider
        )
        
        # Redis instrumentation
        RedisInstrumentor().instrument(
            tracer_provider=self.tracer_provider
        )
        
        # PostgreSQL instrumentation
        Psycopg2Instrumentor().instrument(
            tracer_provider=self.tracer_provider
        )
        
        # Logging instrumentation
        LoggingInstrumentor().instrument(
            tracer_provider=self.tracer_provider
        )
        
        self.logger.info("✅ Automatic instrumentation enabled")
    
    @contextmanager
    def trace_constitutional_operation(self, 
                                     operation_name: str,
                                     category: TraceCategory,
                                     compliance_level: ConstitutionalComplianceLevel = ConstitutionalComplianceLevel.COMPLIANT,
                                     user_id: Optional[str] = None,
                                     additional_attributes: Optional[Dict[str, Any]] = None):
        """
        Context manager for tracing constitutional operations
        
        Args:
            operation_name: Name of the operation
            category: Trace category
            compliance_level: Constitutional compliance level
            user_id: User ID if applicable
            additional_attributes: Additional trace attributes
        """
        # Create constitutional trace context
        trace_context = ConstitutionalTraceContext(
            constitutional_hash=self.constitutional_hash,
            service_name=self.service_name,
            operation_name=operation_name,
            compliance_level=compliance_level,
            category=category,
            user_id=user_id,
            request_id=self._generate_request_id(),
            performance_tier="constitutional",
            security_level="high"
        )
        
        # Create span
        with self.tracer.start_as_current_span(
            operation_name,
            kind=trace.SpanKind.SERVER
        ) as span:
            
            start_time = time.time()
            
            try:
                # Add constitutional attributes
                attributes = trace_context.to_attributes()
                if additional_attributes:
                    attributes.update(additional_attributes)
                
                span.set_attributes(attributes)
                
                # Add baggage for cross-service propagation
                baggage.set_baggage("constitutional_hash", self.constitutional_hash)
                baggage.set_baggage("operation_category", category.value)
                baggage.set_baggage("compliance_level", compliance_level.value)
                
                # Record metrics
                self.span_counter.add(1, {
                    "service": self.service_name,
                    "operation": operation_name,
                    "category": category.value,
                    "constitutional_hash": self.constitutional_hash
                })
                
                self.performance_metrics["spans_created"] += 1
                
                yield span
                
                # Mark as successful
                span.set_status(Status(StatusCode.OK))
                
            except Exception as e:
                # Record error
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                span.set_attribute("error", True)
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
                
                self.performance_metrics["error_spans"] += 1
                raise
                
            finally:
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000
                span.set_attribute("duration_ms", duration_ms)
                
                # Record duration metric
                self.span_duration_histogram.record(duration_ms, {
                    "service": self.service_name,
                    "operation": operation_name,
                    "category": category.value
                })
                
                # Check for high latency (P99 > 5ms)
                if duration_ms > 5:
                    span.set_attribute("performance_warning", "high_latency")
                    self.performance_metrics["high_latency_spans"] += 1
                
                # Validate constitutional compliance
                if compliance_level == ConstitutionalComplianceLevel.NON_COMPLIANT:
                    span.set_attribute("constitutional_violation", True)
                    self.constitutional_violation_counter.add(1, {
                        "service": self.service_name,
                        "operation": operation_name
                    })
                    self.performance_metrics["constitutional_violations"] += 1
                    
                    self.logger.warning(f"Constitutional violation detected in {operation_name}")
    
    def trace_function(self, 
                      operation_name: Optional[str] = None,
                      category: TraceCategory = TraceCategory.CONSTITUTIONAL,
                      compliance_level: ConstitutionalComplianceLevel = ConstitutionalComplianceLevel.COMPLIANT,
                      record_args: bool = False,
                      record_result: bool = False):
        """
        Decorator for tracing functions
        
        Args:
            operation_name: Name of the operation (defaults to function name)
            category: Trace category
            compliance_level: Constitutional compliance level
            record_args: Whether to record function arguments
            record_result: Whether to record function result
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                
                with self.trace_constitutional_operation(
                    op_name, category, compliance_level
                ) as span:
                    
                    # Record function arguments if requested
                    if record_args:
                        span.set_attribute("function.args", str(args))
                        span.set_attribute("function.kwargs", str(kwargs))
                    
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # Record result if requested
                    if record_result and result is not None:
                        span.set_attribute("function.result", str(result))
                    
                    return result
                    
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                
                with self.trace_constitutional_operation(
                    op_name, category, compliance_level
                ) as span:
                    
                    # Record function arguments if requested
                    if record_args:
                        span.set_attribute("function.args", str(args))
                        span.set_attribute("function.kwargs", str(kwargs))
                    
                    # Execute async function
                    result = await func(*args, **kwargs)
                    
                    # Record result if requested
                    if record_result and result is not None:
                        span.set_attribute("function.result", str(result))
                    
                    return result
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def trace_database_operation(self, 
                               operation_name: str,
                               table_name: str,
                               query: Optional[str] = None,
                               constitutional_data: bool = False):
        """
        Trace database operations with constitutional compliance
        
        Args:
            operation_name: Database operation name
            table_name: Database table name
            query: SQL query (optional)
            constitutional_data: Whether operation involves constitutional data
        """
        compliance_level = ConstitutionalComplianceLevel.COMPLIANT if constitutional_data else ConstitutionalComplianceLevel.UNKNOWN
        
        additional_attributes = {
            "db.table": table_name,
            "db.operation": operation_name,
            "constitutional_data": constitutional_data
        }
        
        if query:
            additional_attributes["db.query"] = query
            
        return self.trace_constitutional_operation(
            f"db.{operation_name}",
            TraceCategory.DATABASE,
            compliance_level,
            additional_attributes=additional_attributes
        )
    
    def trace_external_api_call(self, 
                              api_name: str,
                              endpoint: str,
                              method: str = "GET",
                              constitutional_headers: bool = True):
        """
        Trace external API calls with constitutional compliance
        
        Args:
            api_name: API name (e.g., "groq", "openai")
            endpoint: API endpoint
            method: HTTP method
            constitutional_headers: Whether constitutional headers are included
        """
        compliance_level = ConstitutionalComplianceLevel.COMPLIANT if constitutional_headers else ConstitutionalComplianceLevel.NON_COMPLIANT
        
        additional_attributes = {
            "http.method": method,
            "http.url": endpoint,
            "api.name": api_name,
            "constitutional_headers": constitutional_headers
        }
        
        return self.trace_constitutional_operation(
            f"api.{api_name}",
            TraceCategory.EXTERNAL_API,
            compliance_level,
            additional_attributes=additional_attributes
        )
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return f"acgs-{int(time.time() * 1000000)}"
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "service": self.service_name,
            "constitutional_hash": self.constitutional_hash,
            "metrics": self.performance_metrics.copy()
        }
    
    def shutdown(self):
        """Shutdown tracing instrumentation"""
        if self.tracer_provider:
            self.tracer_provider.shutdown()
        if self.meter_provider:
            self.meter_provider.shutdown()
        
        self.logger.info(f"✅ Tracing shutdown for {self.service_name}")

# Global instrumentation instance
_instrumentation_instance: Optional[ACGSTracingInstrumentation] = None

def initialize_tracing(service_name: str, **kwargs) -> ACGSTracingInstrumentation:
    """
    Initialize global tracing instrumentation
    
    Args:
        service_name: Service name
        **kwargs: Additional configuration options
    
    Returns:
        ACGSTracingInstrumentation instance
    """
    global _instrumentation_instance
    
    if _instrumentation_instance is None:
        _instrumentation_instance = ACGSTracingInstrumentation(service_name, **kwargs)
    
    return _instrumentation_instance

def get_tracer() -> ACGSTracingInstrumentation:
    """Get global tracing instrumentation instance"""
    if _instrumentation_instance is None:
        raise RuntimeError("Tracing not initialized. Call initialize_tracing() first.")
    
    return _instrumentation_instance

# Convenience decorators
def trace_constitutional(operation_name: Optional[str] = None, 
                        category: TraceCategory = TraceCategory.CONSTITUTIONAL,
                        compliance_level: ConstitutionalComplianceLevel = ConstitutionalComplianceLevel.COMPLIANT):
    """Convenience decorator for constitutional operations"""
    def decorator(func):
        return get_tracer().trace_function(operation_name, category, compliance_level)(func)
    return decorator

def trace_consensus(operation_name: Optional[str] = None):
    """Convenience decorator for consensus operations"""
    return trace_constitutional(operation_name, TraceCategory.CONSENSUS)

def trace_agent_coordination(operation_name: Optional[str] = None):
    """Convenience decorator for agent coordination operations"""
    return trace_constitutional(operation_name, TraceCategory.AGENT_COORDINATION)

def trace_policy_evaluation(operation_name: Optional[str] = None):
    """Convenience decorator for policy evaluation operations"""
    return trace_constitutional(operation_name, TraceCategory.POLICY_EVALUATION)

def trace_authentication(operation_name: Optional[str] = None):
    """Convenience decorator for authentication operations"""
    return trace_constitutional(operation_name, TraceCategory.AUTHENTICATION)

def trace_authorization(operation_name: Optional[str] = None):
    """Convenience decorator for authorization operations"""
    return trace_constitutional(operation_name, TraceCategory.AUTHORIZATION)

if __name__ == "__main__":
    # Example usage
    async def main():
        # Initialize tracing
        tracing = initialize_tracing("example-service")
        
        # Example traced operation
        @trace_constitutional("example_operation")
        async def example_operation():
            await asyncio.sleep(0.001)  # Simulate work
            return "Constitutional operation completed"
        
        # Execute traced operation
        result = await example_operation()
        print(f"Result: {result}")
        
        # Get performance metrics
        metrics = tracing.get_performance_metrics()
        print(f"Metrics: {json.dumps(metrics, indent=2)}")
        
        # Shutdown
        tracing.shutdown()
    
    asyncio.run(main())