#!/usr/bin/env python3
"""
Test server for ACGS Code Analysis Engine - Minimal version for testing
"""

import logging
import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Add the service directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.constitutional import CONSTITUTIONAL_HASH
from config.settings import get_settings

# Initialize settings with environment variables
os.environ.setdefault("POSTGRESQL_PASSWORD", "test_password")
os.environ.setdefault("JWT_SECRET_KEY", "test_jwt_secret_key_for_development_only")
os.environ.setdefault("REDIS_PASSWORD", "")

settings = get_settings()

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Minimal lifespan management for testing"""
    logger.info("Starting ACGS Code Analysis Engine (Test Mode)...")

    # Store minimal state
    app.state.test_mode = True
    app.state.constitutional_hash = CONSTITUTIONAL_HASH

    logger.info("ACGS Code Analysis Engine startup completed (Test Mode)")

    yield

    logger.info("ACGS Code Analysis Engine shutdown completed (Test Mode)")


# Create minimal FastAPI application
app = FastAPI(
    title="ACGS Code Analysis Engine (Test)",
    description="Test version of the ACGS Code Analysis Engine",
    version="1.0.0-test",
    lifespan=lifespan,
)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Service health check endpoint for testing.
    """
    try:
        health_status = {
            "status": "healthy",
            "service": "acgs-code-analysis-engine",
            "version": "1.0.0-test",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "test_mode": True,
            "checks": {
                "database": "not_tested",
                "cache": "not_tested",
                "service_registry": "not_tested",
                "file_watcher": "not_tested",
            },
        }

        return JSONResponse(status_code=200, content=health_status)

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "acgs-code-analysis-engine",
                "error": str(e),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "test_mode": True,
            },
        )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "ACGS Code Analysis Engine (Test Mode)",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "version": "1.0.0-test",
    }


def main():
    """Main entry point for the test application"""
    logger.info(
        f"Starting ACGS Code Analysis Engine (Test) on {settings.host}:{settings.port}"
    )
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

    # Start the server
    uvicorn.run(
        app, host=settings.host, port=settings.port, log_level="info", access_log=True
    )


if __name__ == "__main__":
    main()
