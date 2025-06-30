#!/usr/bin/env python3
"""
Distributed Tracing Instrumentation for ACGS-2
Implements OpenTelemetry tracing across all services.
"""

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

class DistributedTracingManager:
    """Manages distributed tracing for ACGS-2 services."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.tracer_provider = None
        self.tracer = None
    
    def initialize_tracing(self):
        """Initialize distributed tracing for the service."""
        # Set up tracer provider
        trace.set_tracer_provider(TracerProvider())
        self.tracer_provider = trace.get_tracer_provider()
        
        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
        )
        
        # Add span processor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        self.tracer_provider.add_span_processor(span_processor)
        
        # Get tracer
        self.tracer = trace.get_tracer(self.service_name)
        
        # Instrument frameworks
        self._instrument_frameworks()
    
    def _instrument_frameworks(self):
        """Instrument common frameworks and libraries."""
        # FastAPI instrumentation
        FastAPIInstrumentor.instrument()
        
        # HTTP requests instrumentation
        RequestsInstrumentor.instrument()
        
        # Database instrumentation
        Psycopg2Instrumentor.instrument()
        
        # Redis instrumentation
        RedisInstrumentor.instrument()
    
    def create_span(self, operation_name: str, **attributes):
        """Create a new span for tracing."""
        return self.tracer.start_span(operation_name, attributes=attributes)
    
    def add_span_attributes(self, span, **attributes):
        """Add attributes to an existing span."""
        for key, value in attributes.items():
            span.set_attribute(key, value)
    
    def record_exception(self, span, exception):
        """Record an exception in the span."""
        span.record_exception(exception)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(exception)))

# Global tracing manager instance
tracing_manager = None

def initialize_service_tracing(service_name: str):
    """Initialize tracing for a service."""
    global tracing_manager
    tracing_manager = DistributedTracingManager(service_name)
    tracing_manager.initialize_tracing()
    return tracing_manager

def get_tracer():
    """Get the current tracer instance."""
    return tracing_manager.tracer if tracing_manager else None

def trace_operation(operation_name: str):
    """Decorator for tracing operations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if tracing_manager:
                with tracing_manager.create_span(operation_name) as span:
                    try:
                        result = func(*args, **kwargs)
                        span.set_attribute("operation.success", True)
                        return result
                    except Exception as e:
                        tracing_manager.record_exception(span, e)
                        raise
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator
