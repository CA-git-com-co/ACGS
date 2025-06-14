"""
ACGS-PGP Federated Evaluation Service
Main FastAPI application for federated evaluation framework
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from shared import get_config

# Mock metrics and security middleware for testing
def create_metrics_endpoint(app):
    @app.get("/metrics")
    async def metrics():
        return {"metrics": "mock_metrics"}

async def metrics_middleware(request, call_next):
    return await call_next(request)

class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        return await self.app(scope, receive, send)

from .api.v1.federated_evaluation import router as federated_router
from .api.v1.privacy_metrics import router as privacy_router
from .api.v1.secure_aggregation import router as aggregation_router
from .core.federated_coordinator import federated_coordinator
from .core.secure_aggregation import secure_aggregator
from .dashboard.federated_dashboard import create_dash_app

# Load centralized configuration
config = get_config()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Federated Evaluation Service...")

    # Initialize federated coordinator
    await federated_coordinator.initialize()

    # Initialize secure aggregator
    await secure_aggregator.initialize()

    logger.info("Federated Evaluation Service started successfully")

    yield

    # Cleanup
    logger.info("Shutting down Federated Evaluation Service...")
    await federated_coordinator.shutdown()
    await secure_aggregator.shutdown()
    logger.info("Federated Evaluation Service shutdown complete")


app = FastAPI(
    title="Federated Evaluation (FE) Service",
    version=config.get("api_version", "v1"),
    debug=config.get("debug", False),
    lifespan=lifespan,
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get("cors_origins", ["http://localhost:3000"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add metrics middleware
app.add_middleware(metrics_middleware)

# Include API routers
app.include_router(federated_router, prefix="/api/v1/federated", tags=["federated"])
app.include_router(
    aggregation_router, prefix="/api/v1/aggregation", tags=["aggregation"]
)
app.include_router(privacy_router, prefix="/api/v1/privacy", tags=["privacy"])

# Add metrics endpoint
create_metrics_endpoint(app)

# Create Dash dashboard
dash_app = create_dash_app()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "federated_evaluation",
        "timestamp": datetime.utcnow().isoformat(),
        "version": config.get("api_version", "v1"),
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ACGS-PGP Federated Evaluation Service",
        "version": config.get("api_version", "v1"),
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "dashboard": "/dashboard",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8006, reload=True, log_level="info"
    )
