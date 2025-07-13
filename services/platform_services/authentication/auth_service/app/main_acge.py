"""
ACGE Phase 2 Enhanced Authentication Service
Constitutional compliance integration with ACGE single model architecture
"""

import logging
import os

# Import ACGE integration
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import PlainTextResponse

sys.path.append("..")
from acge_integration import (
    ACGEAuthIntegration,
    ConstitutionalAuthMiddleware,
    add_constitutional_headers,
    constitutional_auth_dependency,
    create_constitutional_jwt_claims,
)

# Import API routers
from .api.agents import router as agents_router

# Service configuration
SERVICE_NAME = "acgs-auth-service-acge"
SERVICE_VERSION = "2.0.0-phase2"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8000"))

# ACGE configuration
ACGE_MODEL_ENDPOINT = os.getenv(
    "ACGE_MODEL_ENDPOINT",
    "http://acge-model-service.acgs-shared.svc.cluster.local:8080",
)
CONSTITUTIONAL_HASH = os.getenv("CONSTITUTIONAL_HASH", "cdd01ef066bc6cf2")
ACGE_ENABLED = os.getenv("ACGE_ENABLED", "true").lower() == "true"
PHASE = os.getenv("PHASE", "phase-2")
ENVIRONMENT = os.getenv("ENVIRONMENT", "green")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(SERVICE_NAME)

# Enhanced Prometheus metrics for ACGE
REQUEST_COUNT = Counter(
    "auth_service_requests_total",
    "Total requests",
    ["method", "endpoint", "status", "environment"],
)
REQUEST_DURATION = Histogram(
    "auth_service_request_duration_seconds",
    "Request duration",
    ["endpoint", "environment"],
)
CONSTITUTIONAL_COMPLIANCE_SCORE = Histogram(
    "auth_constitutional_compliance_score",
    "Constitutional compliance score",
    ["operation"],
)
ACGE_MODEL_REQUESTS = Counter(
    "auth_acge_model_requests_total", "ACGE model requests", ["operation", "status"]
)
CONSTITUTIONAL_VIOLATIONS = Counter(
    "auth_constitutional_violations_total",
    "Constitutional violations",
    ["type", "severity"],
)

# Initialize ACGE integration
acge_integration = None
constitutional_middleware = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with ACGE initialization"""
    global acge_integration, constitutional_middleware

    logger.info(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info(f"🏛️ Constitutional Hash: {CONSTITUTIONAL_HASH}")
    logger.info(f"🤖 ACGE Enabled: {ACGE_ENABLED}")
    logger.info(f"🌍 Environment: {ENVIRONMENT}")
    logger.info(f"📍 Phase: {PHASE}")

    if ACGE_ENABLED:
        try:
            # Initialize ACGE integration
            acge_integration = ACGEAuthIntegration(
                ACGE_MODEL_ENDPOINT, CONSTITUTIONAL_HASH
            )
            constitutional_middleware = ConstitutionalAuthMiddleware(acge_integration)
            logger.info(f"✅ ACGE integration initialized: {ACGE_MODEL_ENDPOINT}")
        except Exception as e:
            logger.exception(f"❌ Failed to initialize ACGE integration: {e}")
            acge_integration = None
            constitutional_middleware = None

    yield

    logger.info(f"🔄 Shutting down {SERVICE_NAME}")
    if acge_integration and hasattr(acge_integration, "client"):
        await acge_integration.client.aclose()


# Create FastAPI application
app = FastAPI(
    title="ACGS-PGP Authentication Service - ACGE Phase 2",
    description="Constitutional compliance authentication service with ACGE integration",
    version=SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Include API routers
app.include_router(agents_router, prefix="/api/v1")

# Security scheme
security = HTTPBearer()


@app.middleware("http")
async def constitutional_compliance_middleware(request: Request, call_next):
    """Constitutional compliance middleware for all requests"""
    start_time = time.time()

    # Add constitutional headers to request context
    request.state.constitutional_hash = CONSTITUTIONAL_HASH
    request.state.acge_enabled = ACGE_ENABLED
    request.state.environment = ENVIRONMENT
    request.state.phase = PHASE

    try:
        response = await call_next(request)

        # Add constitutional headers to response
        response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
        response.headers["X-Service-Name"] = SERVICE_NAME
        response.headers["X-Service-Version"] = SERVICE_VERSION
        response.headers["X-ACGE-Enabled"] = str(ACGE_ENABLED)
        response.headers["X-Environment"] = ENVIRONMENT
        response.headers["X-Phase"] = PHASE

        # Record metrics
        duration = time.time() - start_time
        REQUEST_DURATION.labels(
            endpoint=request.url.path, environment=ENVIRONMENT
        ).observe(duration)

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            environment=ENVIRONMENT,
        ).inc()

        return response

    except Exception as e:
        logger.exception(f"Constitutional middleware error: {e}")
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=500,
            environment=ENVIRONMENT,
        ).inc()
        raise


# Health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check with constitutional compliance status"""
    health_status = {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "acge_enabled": ACGE_ENABLED,
        "environment": ENVIRONMENT,
        "phase": PHASE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Check ACGE model connectivity if enabled
    if ACGE_ENABLED and acge_integration:
        try:
            # Quick health check to ACGE model
            response = await acge_integration.client.get(
                f"{ACGE_MODEL_ENDPOINT}/health", timeout=1.0
            )
            health_status["acge_model_status"] = (
                "connected" if response.status_code == 200 else "error"
            )
        except Exception as e:
            health_status["acge_model_status"] = "disconnected"
            health_status["acge_model_error"] = str(e)

    return health_status


# Constitutional health check
@app.get("/health/constitutional")
async def constitutional_health_check():
    """Constitutional compliance health check"""
    if not ACGE_ENABLED or not constitutional_middleware:
        return {
            "constitutional_compliance": "disabled",
            "acge_enabled": False,
            "fallback_mode": True,
        }

    try:
        # Test constitutional validation
        test_validation = (
            await constitutional_middleware.acge.validate_constitutional_compliance(
                operation="health_check",
                user_data={"username": "system", "role": "system"},
                context={"test": True},
            )
        )

        return {
            "constitutional_compliance": "active",
            "compliance_score": test_validation.get("compliance_score", 0.0),
            "acge_enabled": True,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.exception(f"Constitutional health check failed: {e}")
        return {
            "constitutional_compliance": "error",
            "error": str(e),
            "acge_enabled": True,
            "fallback_mode": True,
        }


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Enhanced login endpoint with ACGE integration
@app.post("/api/v1/auth/login")
async def login_with_constitutional_validation(
    request: Request, response: Response, username: str, password: str
):
    """Enhanced login with constitutional compliance validation"""

    # Mock user validation (replace with actual user service)
    if username == "admin" and password == "admin123":
        user_data = {
            "username": username,
            "user_id": 1,
            "role": "admin",
            "is_active": True,
            "permissions": ["read", "write", "admin"],
        }
    elif username == "user" and password == "user123":
        user_data = {
            "username": username,
            "user_id": 2,
            "role": "user",
            "is_active": True,
            "permissions": ["read"],
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # Constitutional compliance validation
    compliance_result = {"compliance_score": 1.0, "compliant": True}

    if ACGE_ENABLED and constitutional_middleware:
        try:
            request_context = {
                "ip_address": request.client.host,
                "user_agent": request.headers.get("user-agent"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            compliance_result = await constitutional_middleware.validate_login_attempt(
                username=username, user_data=user_data, request_context=request_context
            )

            # Check compliance threshold
            if compliance_result.get("compliance_score", 0.0) < 0.95:
                CONSTITUTIONAL_VIOLATIONS.labels(
                    type="login_compliance_low", severity="warning"
                ).inc()

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Constitutional compliance threshold not met for login",
                    headers={
                        "X-Constitutional-Violation": "true",
                        "X-Compliance-Score": str(
                            compliance_result.get("compliance_score", 0.0)
                        ),
                    },
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Constitutional validation error during login: {e}")
            # Continue with fallback mode
            compliance_result = {
                "compliance_score": 0.5,
                "compliant": False,
                "fallback": True,
            }

    # Create JWT token with constitutional claims
    constitutional_claims = create_constitutional_jwt_claims(
        user_data, compliance_result
    )

    # Mock JWT token creation (replace with actual JWT service)
    token_data = {
        "access_token": f"mock_jwt_token_for_{username}",
        "token_type": "bearer",
        "expires_in": 3600,
        "constitutional": constitutional_claims,
    }

    # Add constitutional headers to response
    add_constitutional_headers(response, compliance_result)

    # Record compliance metrics
    CONSTITUTIONAL_COMPLIANCE_SCORE.labels(operation="login").observe(
        compliance_result.get("compliance_score", 0.0)
    )

    return token_data


# Token validation endpoint
@app.post("/api/v1/auth/validate")
async def validate_token_with_constitutional_check(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Enhanced token validation with constitutional compliance"""

    if not ACGE_ENABLED or not acge_integration:
        # Fallback validation
        return {
            "valid": True,
            "username": "mock_user",
            "constitutional_compliance": "disabled",
        }

    try:
        # Use constitutional auth dependency
        payload = await constitutional_auth_dependency(
            request, credentials, acge_integration
        )

        return {
            "valid": True,
            "username": payload.get("sub"),
            "user_id": payload.get("user_id"),
            "roles": payload.get("roles", []),
            "constitutional": payload.get("constitutional", {}),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token validation error",
        )


# Service info endpoint
@app.get("/api/v1/auth/info")
async def service_info():
    """Enhanced service information with ACGE details"""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "status": "operational",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "acge_enabled": ACGE_ENABLED,
        "environment": ENVIRONMENT,
        "phase": PHASE,
        "acge_model_endpoint": ACGE_MODEL_ENDPOINT if ACGE_ENABLED else None,
        "endpoints": [
            "/health",
            "/health/constitutional",
            "/metrics",
            "/api/v1/auth/login",
            "/api/v1/auth/validate",
            "/api/v1/auth/info",
            "/api/v1/agents",
            "/api/v1/agents/{agent_id}",
            "/api/v1/agents/{agent_id}/status",
            "/api/v1/agents/{agent_id}/audit-logs",
        ],
        "constitutional_features": [
            "acge_model_integration",
            "constitutional_compliance_validation",
            "constitutional_jwt_claims",
            "compliance_monitoring",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    config = {
        "host": "0.0.0.0",
        "port": SERVICE_PORT,
        "log_level": "info",
        "access_log": True,
    }

    logger.info(f"🚀 Starting {SERVICE_NAME} on port {SERVICE_PORT}")
    logger.info(f"🏛️ Constitutional Hash: {CONSTITUTIONAL_HASH}")
    logger.info(f"🤖 ACGE Integration: {'Enabled' if ACGE_ENABLED else 'Disabled'}")

    uvicorn.run(app, **config)
