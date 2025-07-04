#!/usr/bin/env python3
"""
Start PGC Service with OpenTelemetry distributed tracing enabled.
"""

import os
import sys
from pathlib import Path

import uvicorn

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))


def main():
    """Start the PGC service with tracing enabled."""

    # Set environment variables for OpenTelemetry
    os.environ.setdefault("OTEL_SERVICE_NAME", "pgc_service")
    os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    os.environ.setdefault("OTEL_EXPORTER_OTLP_PROTOCOL", "grpc")
    os.environ.setdefault("OTEL_TRACES_SAMPLER", "traceidratio")
    os.environ.setdefault("OTEL_TRACES_SAMPLER_ARG", "0.1")
    os.environ.setdefault(
        "OTEL_RESOURCE_ATTRIBUTES",
        "service.name=pgc_service,service.version=3.0.0,deployment.environment=production",
    )

    # Enable telemetry
    os.environ.setdefault("TELEMETRY_ENABLED", "true")

    print("🚀 Starting PGC Service with OpenTelemetry distributed tracing")
    print(f"📊 OTLP Endpoint: {os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT')}")
    print(f"🎯 Service Name: {os.environ.get('OTEL_SERVICE_NAME')}")
    print(f"📈 Sampling Rate: {os.environ.get('OTEL_TRACES_SAMPLER_ARG')}")

    # Import and run a minimal FastAPI app for tracing demonstration
    try:
        from fastapi import FastAPI
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.semconv.resource import ResourceAttributes

        # Set up OpenTelemetry
        resource = Resource.create(
            {
                ResourceAttributes.SERVICE_NAME: "pgc_service",
                ResourceAttributes.SERVICE_VERSION: "3.0.0",
                ResourceAttributes.DEPLOYMENT_ENVIRONMENT: "production",
            }
        )

        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)

        # Add OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint="http://localhost:4317", insecure=True
        )
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)

        # Create minimal FastAPI app
        app = FastAPI(
            title="ACGS-1 PGC Service with Distributed Tracing",
            description="Policy Governance Compliance Service with OpenTelemetry tracing",
            version="3.0.0",
        )

        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)

        @app.get("/health")
        async def health_check():
            """Health check endpoint with tracing."""
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span("health_check") as span:
                span.set_attribute("service.name", "pgc_service")
                span.set_attribute("health.status", "healthy")
                return {
                    "status": "healthy",
                    "service": "pgc_service",
                    "tracing": "enabled",
                }

        @app.get("/api/v1/governance/validate")
        async def validate_governance():
            """Sample governance validation endpoint with tracing."""
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span("governance_validation") as span:
                span.set_attribute("operation.type", "constitutional_validation")
                span.set_attribute("service.name", "pgc_service")
                return {"validation": "passed", "constitutional_compliance": True}

        # Production-grade server configuration
        config = {
            "host": "0.0.0.0",
            "port": 8005,
            "log_level": "info",
            "access_log": True,
            "workers": 1,
        }

        print(f"🌐 Starting server on port {config['port']}")
        print("✅ OpenTelemetry distributed tracing enabled")
        uvicorn.run(app, **config)

    except Exception as e:
        print(f"❌ Failed to start PGC service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
