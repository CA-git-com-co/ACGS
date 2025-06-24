#!/usr/bin/env python3
"""
Minimal GS Service Startup Script
Starts the GS service with minimal security for health check compatibility
"""

import os
import sys

import uvicorn

# Add the service directory to Python path
sys.path.insert(0, "/home/dislove/ACGS-1/services/core/governance-synthesis/gs_service")
sys.path.insert(0, "/home/dislove/ACGS-1/services/shared")

# Set environment variables to disable problematic security features
os.environ["DISABLE_SECURITY_MIDDLEWARE"] = "true"
os.environ["ENABLE_HTTPS_ONLY"] = "false"
os.environ["ENVIRONMENT"] = "development"
os.environ["SECURITY_LEVEL"] = "minimal"

# Import the app
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting GS Service with minimal security configuration...")
    print("⚠️ This configuration is for health check compatibility only")

    # Start with minimal configuration
    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="info", access_log=True, reload=False)
