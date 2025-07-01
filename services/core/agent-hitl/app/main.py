"""
Agent HITL Service Main Application

FastAPI application for Agent Human-in-the-Loop service.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .api.review import router as review_router
from .services.decision_engine import DecisionEngine

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
)
logger = logging.getLogger(__name__)

# Global decision engine instance
decision_engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global decision_engine

    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    decision_engine = DecisionEngine()

    yield

    # Shutdown
    if decision_engine:
        await decision_engine.close()
    logger.info("Agent HITL Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Agent HITL Service",
    description="Human-in-the-Loop oversight and decision service for autonomous agents",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": (
                str(request.state.timestamp)
                if hasattr(request.state, "timestamp")
                else None
            ),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
        },
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    import time

    start_time = time.time()
    request.state.timestamp = start_time

    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Include routers
app.include_router(review_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "healthy",
        "constitutional_hash": settings.CONSTITUTIONAL_HASH,
        "endpoints": {
            "evaluate": "/api/v1/reviews/evaluate",
            "list_reviews": "/api/v1/reviews",
            "get_review": "/api/v1/reviews/{review_id}",
            "make_decision": "/api/v1/reviews/{review_id}/decide",
            "provide_feedback": "/api/v1/reviews/{review_id}/feedback",
            "agent_profile": "/api/v1/reviews/agents/{agent_id}/profile",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # TODO: Add actual health checks (database connectivity, etc.)
    return {
        "status": "healthy",
        "timestamp": str(time.time()),
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "constitutional_hash": settings.CONSTITUTIONAL_HASH,
    }


@app.get("/metrics")
async def get_metrics():
    """Get service metrics (placeholder)."""
    # TODO: Implement actual metrics collection
    return {
        "service": settings.SERVICE_NAME,
        "metrics": {
            "total_evaluations": 0,
            "auto_approved": 0,
            "human_reviewed": 0,
            "rejected": 0,
            "avg_processing_time_ms": 0.0,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
