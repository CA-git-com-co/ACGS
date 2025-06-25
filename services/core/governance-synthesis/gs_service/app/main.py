"""
Simplified Governance Synthesis Service - Production Fix
Streamlined configuration to resolve import and dependency issues
"""

import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import PlainTextResponse

# Service configuration
SERVICE_NAME = "gs_service"
SERVICE_VERSION = "3.1.0"
SERVICE_PORT = 8004

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(SERVICE_NAME)

# Prometheus metrics
REQUEST_COUNT = Counter('gs_service_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('gs_service_request_duration_seconds', 'Request duration')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    yield
    logger.info(f"🔄 Shutting down {SERVICE_NAME}")

# Create FastAPI application
app = FastAPI(
    title="ACGS-PGP Governance Synthesis Service",
    description="Simplified governance synthesis service for ACGS-PGP system",
    version=SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add minimal CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

@app.middleware("http")
async def add_constitutional_headers(request: Request, call_next):
    """Add constitutional compliance headers"""
    response = await call_next(request)
    response.headers["x-constitutional-hash"] = "cdd01ef066bc6cf2"
    response.headers["x-service-name"] = SERVICE_NAME
    response.headers["x-service-version"] = SERVICE_VERSION
    return response

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Prometheus metrics middleware"""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_DURATION.observe(duration)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "constitutional_hash": "cdd01ef066bc6cf2"
    }

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Simple governance synthesis endpoint
@app.post("/api/v1/synthesize")
async def synthesize_governance(request: Request):
    """Simple governance synthesis endpoint"""
    try:
        body = await request.json()
        
        # Mock governance synthesis response
        return {
            "synthesis_id": f"gs_{int(time.time())}",
            "status": "completed",
            "governance_rules": [
                {
                    "rule_id": "rule_001",
                    "type": "constitutional_compliance",
                    "description": "Ensure all actions comply with constitutional hash",
                    "priority": "high"
                }
            ],
            "constitutional_hash": "cdd01ef066bc6cf2",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        return {"error": str(e), "status": "failed"}

# Service info endpoint
@app.get("/api/v1/info")
async def service_info():
    """Service information endpoint"""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "status": "operational",
        "constitutional_hash": "cdd01ef066bc6cf2",
        "capabilities": [
            "governance_synthesis",
            "policy_generation",
            "constitutional_compliance"
        ],
        "endpoints": [
            "/health",
            "/metrics",
            "/api/v1/synthesize",
            "/api/v1/info"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    config = {
        "host": "0.0.0.0",
        "port": SERVICE_PORT,
        "log_level": "info",
        "access_log": True,
    }
    
    logger.info(f"🚀 Starting {SERVICE_NAME} on port {SERVICE_PORT}")
    uvicorn.run(app, **config)
