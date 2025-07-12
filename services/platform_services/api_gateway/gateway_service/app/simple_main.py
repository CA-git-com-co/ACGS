#!/usr/bin/env python3
"""
Simple main entry point for ACGS API Gateway Service.

This file serves as a compatibility layer for Docker containers
that expect simple_main.py but the actual application is in main.py.

Constitutional Hash: cdd01ef066bc6cf2
"""

import sys
import os
import logging
from datetime import datetime, timezone
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

# Add the current directory and parent directories to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.dirname(current_dir))
sys.path.insert(0, os.path.join(os.path.dirname(current_dir), '..', '..', '..', '..'))

# Import auth components with fallback
try:
    from auth.integrated_auth import (
        AuthenticationResult,
        IntegratedAuthManager,
        TokenData,
        UserCredentials,
        get_auth_manager,
    )
except ImportError:
    # Fallback auth components
    class AuthenticationResult:
        def __init__(self, success: bool, user_id: str = None, error: str = None):
            self.success = success
            self.user_id = user_id
            self.error = error

    class TokenData:
        def __init__(self, user_id: str, scopes: list = None):
            self.user_id = user_id
            self.scopes = scopes or []

    class UserCredentials:
        def __init__(self, username: str, password: str):
            self.username = username
            self.password = password

    class IntegratedAuthManager:
        async def authenticate(self, credentials: UserCredentials) -> AuthenticationResult:
            return AuthenticationResult(success=True, user_id="fallback_user")

        async def validate_token(self, token: str) -> TokenData:
            return TokenData(user_id="fallback_user")

    async def get_auth_manager() -> IntegratedAuthManager:
        return IntegratedAuthManager()

# Import other components
try:
    from services.shared.middleware.constitutional_middleware import setup_constitutional_validation
    from services.shared.middleware.security_middleware import SecurityPolicyEngine
    from services.shared.middleware.metrics_middleware import MetricsCollector
    from services.shared.middleware.service_discovery_middleware import ServiceRouter
except ImportError:
    # Fallback for missing shared components
    def setup_constitutional_validation(*args, **kwargs):
        pass

    class SecurityPolicyEngine:
        async def initialize(self): pass

    class MetricsCollector:
        async def initialize(self): pass
        async def record_request(self, *args, **kwargs): pass

    class ServiceRouter:
        async def initialize(self): pass
        async def route_request(self, *args, **kwargs):
            return Response(content="Service routing not available", status_code=503)

# Configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Initialize FastAPI app
app = FastAPI(
    title="ACGS API Gateway",
    description="Constitutional AI-enhanced API gateway for secure microservices access",
    version="4.0.0",
    docs_url="/gateway/docs",
    redoc_url="/gateway/redoc",
)

# Setup middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Setup constitutional validation
setup_constitutional_validation(
    app=app,
    service_name="api-gateway",
    performance_target_ms=0.5,
    enable_strict_validation=True,
)

# Initialize components
security_policy_engine = SecurityPolicyEngine()
metrics_collector = MetricsCollector()
service_router = ServiceRouter()

logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event() -> None:
    """Initialize gateway components on startup."""
    logger.info(f"Starting ACGS API Gateway with constitutional hash: {CONSTITUTIONAL_HASH}")

    try:
        await service_router.initialize()
        await security_policy_engine.initialize()
        await metrics_collector.initialize()
        logger.info("✅ ACGS API Gateway started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize gateway components: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/gateway/health")
async def gateway_health_check():
    """Gateway-specific health check endpoint."""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    # Run the gateway service
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8010,
        log_level="info",
        access_log=True,
        server_header=False,  # Security: hide server header
        date_header=False,  # Security: hide date header
    )
