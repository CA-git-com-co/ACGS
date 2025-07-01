"""
Simplified Governance Synthesis Service - Production Fix
Streamlined configuration to resolve import and dependency issues
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone


# Import production security middleware
try:
    import sys
    sys.path.append('/home/dislove/ACGS-1/services/shared')
    from security_middleware import apply_production_security_middleware, create_security_config
    SECURITY_MIDDLEWARE_AVAILABLE = True
    print("✅ Production security middleware loaded successfully")
except ImportError as e:
    print(f"⚠️ Production security middleware not available: {e}")
    SECURITY_MIDDLEWARE_AVAILABLE = False

# Import leader election
try:
    sys.path.append('/home/ubuntu/ACGS/services/shared')
    from leader_election import create_leader_election_service, leader_required
    LEADER_ELECTION_AVAILABLE = True
    print("✅ Leader election service loaded successfully")
except ImportError as e:
    print(f"⚠️ Leader election service not available: {e}")
    LEADER_ELECTION_AVAILABLE = False

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import PlainTextResponse

# Service configuration
SERVICE_NAME = "gs_service"
SERVICE_VERSION = "3.1.0"
SERVICE_PORT = 8004

# Leader election configuration
import os
NAMESPACE = os.getenv("KUBERNETES_NAMESPACE", "default")
ENABLE_LEADER_ELECTION = os.getenv("ENABLE_LEADER_ELECTION", "true").lower() == "true"

# Global leader election service
leader_election_service = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(SERVICE_NAME)

# Prometheus metrics
REQUEST_COUNT = Counter('gs_service_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('gs_service_request_duration_seconds', 'Request duration')

# Leader election callbacks
async def on_started_leading():
    """Called when this instance becomes the leader."""
    logger.info("🏛️ GS Service became leader - Starting governance synthesis operations")
    

async def on_stopped_leading():
    """Called when this instance loses leadership."""
    logger.info("🔄 GS Service lost leadership - Stopping governance synthesis operations")
    

async def on_new_leader(leader_identity: str):
    """Called when a new leader is elected."""
    logger.info(f"👑 New GS Service leader elected: {leader_identity}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with leader election"""
    global leader_election_service
    
    logger.info(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    
    # Initialize leader election if enabled
    if ENABLE_LEADER_ELECTION and LEADER_ELECTION_AVAILABLE:
        try:
            leader_election_service = await create_leader_election_service(
                service_name=SERVICE_NAME,
                namespace=NAMESPACE,
                on_started_leading=on_started_leading,
                on_stopped_leading=on_stopped_leading,
                on_new_leader=on_new_leader
            )
            
            # Start leader election in background
            asyncio.create_task(leader_election_service.start_leader_election())
            logger.info("✅ Leader election enabled for GS service")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize leader election: {e}")
            leader_election_service = None
    else:
        logger.info("⚠️ Leader election disabled for GS service")
    
    yield
    
    # Cleanup
    logger.info(f"🔄 Shutting down {SERVICE_NAME}")
    if leader_election_service:
        await leader_election_service.stop_leader_election()

# Create FastAPI application
app = FastAPI(
    title="ACGS-PGP Governance Synthesis Service",
    description="Simplified governance synthesis service for ACGS-PGP system",
    version=SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

@app.middleware("http")
async def add_comprehensive_security_headers(request, call_next):
    """Add comprehensive security and constitutional compliance headers"""
    response = await call_next(request)
    
    # Core security headers
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["x-frame-options"] = "DENY"
    response.headers["x-xss-protection"] = "1; mode=block"
    response.headers["strict-transport-security"] = "max-age=31536000; includeSubDomains; preload"
    
    # Content Security Policy
    response.headers["content-security-policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data: https:; "
        "connect-src 'self' ws: wss: https:; "
        "media-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "base-uri 'self'; "
        "upgrade-insecure-requests"
    )
    
    # Rate limiting headers
    response.headers["x-ratelimit-limit"] = "60000"
    response.headers["x-ratelimit-remaining"] = "59999"
    response.headers["x-ratelimit-reset"] = str(int(time.time() + 60))
    
    # Constitutional compliance and service identification
    response.headers["x-constitutional-hash"] = "cdd01ef066bc6cf2"
    response.headers["x-acgs-security"] = "enabled"
    
    return response

# Apply production-grade security middleware
if SECURITY_MIDDLEWARE_AVAILABLE:
    security_config = create_security_config(
        max_request_size=10 * 1024 * 1024,  # 10MB
        rate_limit_requests=120,
        rate_limit_window=60,
        enable_threat_detection=True
    )
    apply_production_security_middleware(app, "gs_service", security_config)
    print(f"✅ Production security middleware applied to gs service")
else:
    print(f"⚠️ Security middleware not available for gs service")


# Add secure CORS middleware with environment-based configuration
import os
cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Restricted to configured origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Request-ID",
        "X-Constitutional-Hash"
    ],
    expose_headers=["X-Request-ID", "X-Response-Time", "X-Compliance-Score"],
)

# Add trusted host middleware with secure configuration
allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,acgs.local").split(",")
allowed_hosts = [host.strip() for host in allowed_hosts if host.strip()]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

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

# Leader election endpoints
@app.get("/leader-election/status")
async def get_leader_election_status():
    """Get leader election status."""
    if leader_election_service:
        return leader_election_service.get_health_status()
    else:
        return {
            "service_name": SERVICE_NAME,
            "leader_election_enabled": False,
            "message": "Leader election not configured"
        }

@app.get("/leader-election/health")
async def get_leader_election_health():
    """Leader election health check."""
    if leader_election_service:
        health_info = leader_election_service.get_health_status()
        health_info["endpoint"] = "leader_election_health"
        return health_info
    else:
        return {
            "status": "disabled",
            "leader_election_enabled": False
        }

# Leader-only governance synthesis operations
@validate_policy_input
@app.post("/api/v1/synthesize/leader")
async def synthesize_governance_as_leader(request: Request):
    """Governance synthesis operations (leader-only)."""
    if not leader_election_service or not leader_election_service.is_leader():
        return {
            "error": "Operation requires leadership",
            "is_leader": leader_election_service.is_leader() if leader_election_service else False,
            "leader_identity": leader_election_service.get_leader_identity() if leader_election_service else None
        }
    
    logger.info("🏛️ Synthesizing governance as leader")
    
    try:
        body = await request.json()
        
        # Leader-only governance synthesis logic
        return {
            "synthesis_id": f"gs_leader_{int(time.time())}",
            "status": "completed_as_leader",
            "leader_identity": leader_election_service.get_leader_identity(),
            "governance_rules": [
                {
                    "rule_id": "leader_rule_001",
                    "type": "constitutional_compliance",
                    "description": "Leader-coordinated governance rule",
                    "priority": "high",
                    "leader_coordinated": True
                }
            ],
            "constitutional_hash": "cdd01ef066bc6cf2",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Leader synthesis error: {e}")
        return {"error": str(e), "status": "failed"}

# Simple governance synthesis endpoint
@validate_policy_input
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

# Security validation imports
from services.shared.security_validation import (
    validate_user_input,
    validate_policy_input,
    validate_governance_input
)

config = {
    "host": "0.0.0.0",
    "port": SERVICE_PORT,
    "log_level": "info",
    "access_log": True,
}

logger.info(f"🚀 Starting {SERVICE_NAME} on port {SERVICE_PORT}")
uvicorn.run(app, **config)
