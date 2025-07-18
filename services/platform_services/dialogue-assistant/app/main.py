"""
Dialogue Assistant Service - Main FastAPI Application
Constitutional Hash: cdd01ef066bc6cf2

Provides AI-powered conversational assistant with constitutional compliance
validation and multi-turn conversation support.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .api.routes import router
from .models.schemas import CONSTITUTIONAL_HASH

# Try to import shared middleware
try:
    from services.shared.middleware.tenant_middleware import TenantContextMiddleware
    from services.shared.middleware.error_handling import setup_error_handlers
    from services.shared.security.enhanced_security_middleware import (
        EnhancedSecurityMiddleware,
    )

    SHARED_MIDDLEWARE_AVAILABLE = True
except ImportError:
    SHARED_MIDDLEWARE_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Dialogue Assistant Service",
    description="AI-powered conversational assistant with constitutional compliance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add shared middleware if available
if SHARED_MIDDLEWARE_AVAILABLE:
    # Enhanced security middleware
    app.add_middleware(
        EnhancedSecurityMiddleware,
        max_requests=100,  # Rate limit: 100 requests per 60 seconds
        window_seconds=60,
        max_request_size=1 * 1024 * 1024,  # 1MB for text content
    )

    # Multi-tenant middleware
    app.add_middleware(TenantContextMiddleware)

    # Error handling
    setup_error_handlers(app)

    logger.info("Shared middleware loaded successfully")
else:
    logger.warning("Shared middleware not available, running in standalone mode")


# Constitutional compliance middleware
@app.middleware("http")
async def constitutional_compliance_middleware(request: Request, call_next):
    """Ensure all requests include constitutional compliance validation."""

    # Add constitutional hash to response headers
    response = await call_next(request)
    response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
    response.headers["X-Service-Name"] = "dialogue-assistant"
    response.headers["X-Service-Version"] = "1.0.0"

    return response


# Include API routes
app.include_router(router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Dialogue Assistant Service",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "description": "AI-powered conversational assistant with constitutional compliance",
        "endpoints": {
            "health": "/api/v1/chat/health",
            "message": "/api/v1/chat/message",
            "stream": "/api/v1/chat/stream",
            "conversation": "/api/v1/chat/conversation/{conversation_id}",
            "search": "/api/v1/chat/conversation/search",
            "analytics": "/api/v1/chat/analytics/{user_id}",
            "docs": "/docs",
        },
    }


# Health check endpoint at root level
@app.get("/health")
async def health():
    """Service health check."""
    return {
        "status": "healthy",
        "service": "dialogue-assistant",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": "2025-07-16T00:00:00Z",
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    logger.info("Starting Dialogue Assistant Service...")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    logger.info("Service initialization complete")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down Dialogue Assistant Service...")
    # TODO: Clean up AI models and Redis connections
    logger.info("Service shutdown complete")


if __name__ == "__main__":
    import uvicorn

    # Run the service
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8021,  # Use port 8021 for dialogue assistant service
        reload=True,
        log_level="info",
    )
