"""
Blockchain Audit Service - Main Application
Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time

from .api.routes import router
from .services.audit_manager import AuditManager
from .services.blockchain_service import BlockchainService
from .models.schemas import CONSTITUTIONAL_HASH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'blockchain_audit_requests_total',
    'Total blockchain audit requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'blockchain_audit_request_duration_seconds',
    'Blockchain audit request latency',
    ['method', 'endpoint']
)

AUDIT_EVENTS_TOTAL = Counter(
    'blockchain_audit_events_total',
    'Total audit events processed',
    ['event_type', 'service_name']
)

BLOCKCHAIN_TRANSACTIONS_TOTAL = Counter(
    'blockchain_transactions_total',
    'Total blockchain transactions',
    ['network', 'status']
)

# Global service instances
audit_manager = None
blockchain_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global audit_manager, blockchain_service
    
    # Startup
    logger.info("Starting Blockchain Audit Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    try:
        # Initialize services
        audit_manager = AuditManager()
        blockchain_service = BlockchainService()
        
        # Initialize database
        await audit_manager.initialize_database()
        
        # Store references in app state
        app.state.audit_manager = audit_manager
        app.state.blockchain_service = blockchain_service
        
        logger.info("Blockchain Audit Service initialized successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize Blockchain Audit Service: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Blockchain Audit Service")

# Create FastAPI application
app = FastAPI(
    title="Blockchain Audit Service",
    description="ACGS-2 Blockchain Audit and Logging Service",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for metrics and constitutional compliance
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware for request metrics and constitutional compliance."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate metrics
    process_time = time.time() - start_time
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    
    # Add constitutional compliance headers
    response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
    response.headers["X-Service-Name"] = "blockchain-audit"
    response.headers["X-Response-Time"] = str(process_time)
    
    return response

# Constitutional compliance middleware
@app.middleware("http")
async def constitutional_compliance_middleware(request: Request, call_next):
    """Ensure constitutional compliance for all requests."""
    # Check for constitutional hash in request headers (optional)
    client_hash = request.headers.get("X-Constitutional-Hash")
    
    if client_hash and client_hash != CONSTITUTIONAL_HASH:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid constitutional hash",
                "expected": CONSTITUTIONAL_HASH,
                "received": client_hash
            }
        )
    
    response = await call_next(request)
    return response

# Include API routes
app.include_router(router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database health
        db_healthy = await audit_manager.health_check() if audit_manager else False
        
        # Check blockchain service
        blockchain_healthy = blockchain_service.is_available() if blockchain_service else False
        
        status = "healthy" if db_healthy else "unhealthy"
        
        return {
            "status": status,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": time.time(),
            "services": {
                "database": "healthy" if db_healthy else "unhealthy",
                "blockchain": "healthy" if blockchain_healthy else "unavailable"
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        )

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "ACGS-2 Blockchain Audit Service",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "api": "/api/v1",
            "docs": "/docs"
        }
    }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception in {request.method} {request.url.path}: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    )

# Background task for cleanup
async def cleanup_old_records():
    """Background task to clean up old audit records."""
    try:
        if audit_manager:
            deleted_count = await audit_manager.cleanup_old_records(days_old=90)
            logger.info(f"Cleaned up {deleted_count} old records")
    except Exception as e:
        logger.error(f"Failed to cleanup old records: {e}")

# Development server
if __name__ == "__main__":
    # Load environment variables
    port = int(os.getenv("PORT", 8024))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting Blockchain Audit Service on {host}:{port}")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )