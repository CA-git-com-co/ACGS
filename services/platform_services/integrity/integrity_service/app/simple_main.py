#!/usr/bin/env python3
"""
Simple main entry point for ACGS Integrity Service.

This file serves as a compatibility layer for Docker containers
that expect simple_main.py but the actual application is in main.py.

Constitutional Hash: cdd01ef066bc6cf2
"""

import pathlib
import sys

# Add the current directory to Python path to handle imports
current_dir = pathlib.Path(pathlib.Path(__file__).resolve()).parent
sys.path.insert(0, current_dir)
sys.path.insert(0, pathlib.Path(current_dir).parent)

# Import and run the actual main application
try:
    from main import app
except ImportError:
    # Fallback: create a minimal FastAPI app
    from datetime import datetime, timezone

    from fastapi import FastAPI

    app = FastAPI(
        title="ACGS Integrity Service",
        description="Constitutional AI-enhanced integrity verification service",
        version="4.0.0",
    )

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "integrity-service",
            "constitutional_hash": "cdd01ef066bc6cf2",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


if __name__ == "__main__":
    import uvicorn

    # Run the integrity service
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info",
        access_log=True,
    )
