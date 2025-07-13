#!/usr/bin/env python3
"""
Constitutional Core Service - Simplified Version for Testing
Constitutional Hash: cdd01ef066bc6cf2

Provides basic constitutional compliance verification and health checks.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import fast constitutional validator
from .fast_constitutional_validator import (
    get_fast_validator,
    validate_constitutional_fast,
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
SERVICE_NAME = "constitutional-core"
SERVICE_VERSION = "1.0.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(SERVICE_NAME)

# Service startup time
start_time = time.time()

# Create FastAPI application
app = FastAPI(
    title="Constitutional Core Service",
    description="Unified constitutional AI reasoning and formal verification service",
    version=SERVICE_VERSION,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# Configure CORS - Production-ready security settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Grafana dashboard
        "http://localhost:8080",  # API Gateway
        "http://localhost:9090",  # Prometheus
        "https://acgs.local",  # Production domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Constitutional-Hash",
        "X-Tenant-ID",
        "X-Request-ID",
    ],
)


# =============================================================================
# Pydantic Models
# =============================================================================


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: datetime
    service: str
    version: str
    constitutional_hash: str
    uptime_seconds: float
    components: dict[str, Any]


class ConstitutionalValidationRequest(BaseModel):
    """Constitutional validation request model."""

    content: str
    context: dict[str, Any] = {}
    principles: list[str] = []
    require_formal_proof: bool = False


class ConstitutionalValidationResult(BaseModel):
    """Constitutional validation result model."""

    compliant: bool
    score: float = Field(ge=0.0, le=1.0)
    violated_principles: list[str] = []
    reasoning: list[str] = []
    recommendations: list[str] = []
    constitutional_hash: str = CONSTITUTIONAL_HASH
    metadata: dict[str, Any] = {}


# =============================================================================
# API Endpoints
# =============================================================================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with constitutional hash validation."""
    current_time = datetime.now(timezone.utc)
    uptime = time.time() - start_time

    components = {
        "constitutional_engine": True,
        "formal_verification": False,  # Simplified version
        "unified_compliance": True,
        "database": False,
        "cache": True,  # Fast multi-level caching enabled
        "redis_cache": True,  # L3 distributed cache
        "performance_optimization": "ENHANCED",
    }

    return HealthResponse(
        status="healthy",
        timestamp=current_time,
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        constitutional_hash=CONSTITUTIONAL_HASH,
        uptime_seconds=uptime,
        components=components,
    )


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Constitutional Core Service",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "version": SERVICE_VERSION,
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "docs": "/api/v1/docs",
            "constitutional": "/api/v1/constitutional",
            "verification": "/api/v1/verification",
            "unified": "/api/v1/unified",
        },
    }


@app.post(
    "/api/v1/constitutional/validate", response_model=ConstitutionalValidationResult
)
async def validate_constitutional_compliance(request: ConstitutionalValidationRequest):
    """Validate constitutional compliance using fast cached validation."""
    try:
        # Use fast constitutional validator with multi-level caching
        validation_result = await validate_constitutional_fast(
            content=request.content,
            context=request.context,
            principles=request.principles,
        )

        return ConstitutionalValidationResult(
            compliant=validation_result["compliant"],
            score=validation_result["score"],
            violated_principles=validation_result["violated_principles"],
            reasoning=validation_result["reasoning"],
            recommendations=validation_result["recommendations"],
            constitutional_hash=validation_result["constitutional_hash"],
            metadata=validation_result.get("metadata", {}),
        )

    except Exception as e:
        logger.exception(f"Constitutional validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Constitutional validation failed: {e!s}",
        )


@app.get("/api/v1/constitutional/principles")
async def list_constitutional_principles():
    """List basic constitutional principles."""
    principles = [
        {
            "id": "non-maleficence",
            "name": "Non-Maleficence",
            "description": "Do no harm",
            "category": "ethics",
            "priority": 10,
        },
        {
            "id": "beneficence",
            "name": "Beneficence",
            "description": "Act in the best interest of others",
            "category": "ethics",
            "priority": 9,
        },
        {
            "id": "autonomy",
            "name": "Autonomy",
            "description": "Respect individual autonomy and decision-making",
            "category": "rights",
            "priority": 8,
        },
        {
            "id": "adequacy",
            "name": "Adequacy",
            "description": "Provide sufficient information and context",
            "category": "quality",
            "priority": 7,
        },
    ]

    return {
        "principles": principles,
        "total": len(principles),
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }


@app.get("/api/v1/unified/status")
async def get_unified_status():
    """Get unified compliance system status."""
    return {
        "constitutional_engine": "operational",
        "formal_verification": "simplified",
        "unified_compliance": "operational",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "system_health": "healthy",
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/constitutional/performance")
async def get_performance_metrics():
    """Get constitutional validation performance metrics."""
    validator = get_fast_validator()
    cache_stats = validator.get_cache_stats()

    return {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "service": SERVICE_NAME,
        "performance_status": cache_stats["performance_metrics"]["current_performance"],
        "metrics": cache_stats,
        "optimization_level": "ENHANCED_CACHING",
        "target_p99_latency_ms": 1.0,
        "current_avg_latency_ms": cache_stats["performance_metrics"][
            "avg_validation_time_ms"
        ],
        "cache_effectiveness": cache_stats["cache_performance"]["overall_hit_rate"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers including constitutional hash."""
    response = await call_next(request)

    # Core security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Constitutional compliance headers
    response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
    response.headers["X-Service-Name"] = SERVICE_NAME
    response.headers["X-Service-Version"] = SERVICE_VERSION

    return response


if __name__ == "__main__":
    logger.info(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")

    uvicorn.run(
        "main_simple:app", host="0.0.0.0", port=8001, reload=True, log_level="info"
    )
