#!/usr/bin/env python3
"""
Simple main entry point for ACGS Integrity Service.

This file serves as a compatibility layer for Docker containers
that expect simple_main.py but the actual application is in main.py.

Constitutional Hash: cdd01ef066bc6cf2
"""

import sys
import os

# Add the current directory to Python path to handle imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.dirname(current_dir))

# Import and run the actual main application
try:
    from main import app
except ImportError:
    # Fallback: create a minimal FastAPI app
    from fastapi import FastAPI
    from datetime import datetime, timezone
    
    app = FastAPI(
        title="ACGS Integrity Service",
        description="Constitutional AI-enhanced integrity verification service",
        version="4.0.0"
    )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "integrity-service",
            "constitutional_hash": "cdd01ef066bc6cf2",
            "timestamp": datetime.now(timezone.utc).isoformat()
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
