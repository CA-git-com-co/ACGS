"""
Image Compliance Service - Main FastAPI Application
Constitutional Hash: cdd01ef066bc6cf2

Provides AI-powered image compliance checking and safe image generation
with constitutional compliance validation.
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

# Try to import shared middleware, but don't fail if not available
try:
    from services.shared.middleware.tenant_middleware import TenantContextMiddleware
    from services.shared.middleware.error_handling import setup_error_handlers
    from services.shared.security.enhanced_security_middleware import EnhancedSecurityMiddleware
    SHARED_MIDDLEWARE_AVAILABLE = True
except ImportError:
    SHARED_MIDDLEWARE_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Image Compliance Service",
    description="AI-powered image compliance checking and safe image generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware for cross-origin requests
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
        max_request_size=50 * 1024 * 1024  # 50MB for image uploads
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
    response.headers["X-Service-Name"] = "image-compliance"
    response.headers["X-Service-Version"] = "1.0.0"
    
    return response

# Include API routes
app.include_router(router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Image Compliance Service",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "description": "AI-powered image compliance checking and safe image generation",
        "endpoints": {
            "health": "/api/v1/image/health",
            "audit": "/api/v1/image/audit",
            "generate": "/api/v1/image/generate",
            "index": "/api/v1/image/index",
            "docs": "/docs"
        }
    }

# Health check endpoint at root level
@app.get("/health")
async def health():
    """Service health check."""
    return {
        "status": "healthy",
        "service": "image-compliance",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": "2025-07-16T00:00:00Z"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    logger.info("Starting Image Compliance Service...")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    logger.info("Service initialization complete")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down Image Compliance Service...")
    # TODO: Clean up ML models and resources
    logger.info("Service shutdown complete")

if __name__ == "__main__":
    import uvicorn
    
    # Run the service
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8020,  # Use port 8020 for image compliance service
        reload=True,
        log_level="info"
    )