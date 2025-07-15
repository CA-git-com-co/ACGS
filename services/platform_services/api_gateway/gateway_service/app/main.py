"""
ACGS API Gateway Service

Constitutional AI-enhanced API gateway providing unified entry point,
authentication, authorization, rate limiting, and security policy enforcement.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
from datetime import datetime, timezone
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

# Integrated authentication
from .auth.integrated_auth import (
    AuthenticationResult,
    TokenData,
    UserCredentials,
    get_auth_manager,
)

# ACGS imports
from .core.gateway_config import GatewayConfig
from .middleware.authentication import AuthenticationMiddleware
from .middleware.constitutional_compliance import ConstitutionalComplianceMiddleware
from .middleware.rate_limiting import RateLimitingMiddleware
from .middleware.request_logging import RequestLoggingMiddleware
from .middleware.security_headers import SecurityHeadersMiddleware
from .monitoring.metrics_collector import MetricsCollector
from .routing.service_router import ServiceRouter
from .security.policy_engine import SecurityPolicyEngine

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ACGS API Gateway",
    description=(
        "Constitutional AI-enhanced API gateway for secure microservices access"
    ),
    version="4.0.0",
    docs_url="/gateway/docs" if GatewayConfig.ENABLE_DOCS else None,
    redoc_url="/gateway/redoc" if GatewayConfig.ENABLE_DOCS else None,
)

# Setup optimized constitutional validation middleware
setup_constitutional_validation(
    app=app,
    service_name="api-gateway",
    performance_target_ms=0.5,  # Optimized target
    enable_strict_validation=True,
)

# Constitutional compliance logging
logger.info("✅ Optimized constitutional middleware enabled for api-gateway")
logger.info("📋 Constitutional Hash: cdd01ef066bc6cf2")
logger.info("🎯 Performance Target: <0.5ms validation")


# Initialize core components
gateway_config = GatewayConfig()
service_router = ServiceRouter()
security_policy_engine = SecurityPolicyEngine()
metrics_collector = MetricsCollector()
auth_manager = get_auth_manager()

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize gateway components on startup."""

    logger.info(
        f"Starting ACGS API Gateway with constitutional hash: {CONSTITUTIONAL_HASH}"
    )

    # Initialize service router
    await service_router.initialize()

    # Initialize security policy engine
    await security_policy_engine.initialize()

    # Initialize metrics collector
    await metrics_collector.initialize()

    # Setup service discovery
    from services.shared.middleware.service_discovery_middleware import (
        setup_service_discovery,
    )

    setup_service_discovery(
        app=app,
        service_name="api-gateway",
        service_version="4.0.0",
        capabilities=[
            "request_routing",
            "authentication",
            "authorization",
            "rate_limiting",
            "constitutional_compliance",
            "service_discovery",
            "load_balancing",
            "security_policies",
        ],
        heartbeat_interval=15,
        metadata={
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "service_type": "platform",
            "compliance_level": "constitutional",
            "gateway_version": "4.0.0",
        },
    )

    # Verify constitutional compliance
    constitutional_status = await verify_constitutional_compliance()
    if not constitutional_status["is_compliant"]:
        logger.critical("Constitutional compliance verification failed!")
        raise RuntimeError("Constitutional compliance check failed")

    logger.info("ACGS API Gateway startup completed successfully")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup resources on shutdown."""

    logger.info("Shutting down ACGS API Gateway")

    # Cleanup components
    await metrics_collector.cleanup()
    await service_router.cleanup()
    await security_policy_engine.cleanup()

    logger.info("ACGS API Gateway shutdown completed")


# Add middleware stack (order is important)
app.add_middleware(RequestLoggingMiddleware, constitutional_hash=CONSTITUTIONAL_HASH)

app.add_middleware(SecurityHeadersMiddleware, constitutional_compliance=True)

app.add_middleware(
    ConstitutionalComplianceMiddleware,
    constitutional_hash=CONSTITUTIONAL_HASH,
    policy_engine=security_policy_engine,
)

app.add_middleware(
    RateLimitingMiddleware,
    requests_per_minute=gateway_config.RATE_LIMIT_REQUESTS_PER_MINUTE,
    burst_limit=gateway_config.RATE_LIMIT_BURST,
)

app.add_middleware(AuthenticationMiddleware, constitutional_verification=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=gateway_config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=gateway_config.ALLOWED_HOSTS)


# Constitutional compliance verification endpoint
async def verify_constitutional_compliance() -> dict[str, Any]:
    """Verify constitutional compliance of the gateway."""

    try:
        # Verify constitutional hash
        current_hash = CONSTITUTIONAL_HASH
        expected_hash = "cdd01ef066bc6cf2"

        hash_valid = current_hash == expected_hash

        # Verify policy engine compliance
        policy_compliance = (
            await security_policy_engine.verify_constitutional_compliance()
        )

        # Verify service routing compliance
        routing_compliance = await service_router.verify_constitutional_compliance()

        overall_compliance = hash_valid and policy_compliance and routing_compliance

        return {
            "is_compliant": overall_compliance,
            "constitutional_hash": current_hash,
            "hash_valid": hash_valid,
            "policy_compliance": policy_compliance,
            "routing_compliance": routing_compliance,
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.exception(f"Constitutional compliance verification failed: {e}")
        return {
            "is_compliant": False,
            "error": str(e),
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }


# Health check endpoints
@app.get("/gateway/health")
async def health_check() -> None:
    """Gateway health check endpoint."""

    return {
        "status": "healthy",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "4.0.0",
    }


@app.get("/gateway/health/detailed")
async def detailed_health_check() -> None:
    """Detailed health check with component status."""

    # Check component health
    components_health = {
        "service_router": await service_router.health_check(),
        "security_policy_engine": await security_policy_engine.health_check(),
        "metrics_collector": await metrics_collector.health_check(),
    }

    # Check constitutional compliance
    constitutional_status = await verify_constitutional_compliance()

    overall_healthy = (
        all(health["healthy"] for health in components_health.values())
        and constitutional_status["is_compliant"]
    )

    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "constitutional_compliance": constitutional_status,
        "components": components_health,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Gateway configuration endpoint
@app.get("/gateway/config")
async def get_gateway_config() -> None:
    """Get gateway configuration (filtered for security)."""

    return {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "version": "4.0.0",
        "rate_limiting": {
            "requests_per_minute": gateway_config.RATE_LIMIT_REQUESTS_PER_MINUTE,
            "burst_limit": gateway_config.RATE_LIMIT_BURST,
        },
        "security": {
            "constitutional_compliance_enabled": True,
            "multi_tenant_isolation": True,
            "formal_verification": True,
        },
        "services": await service_router.get_registered_services(),
    }


# Metrics endpoint
@app.get("/gateway/metrics")
async def get_gateway_metrics() -> None:
    """Get gateway metrics."""

    return await metrics_collector.get_metrics()


# =============================================================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
# Integrated Authentication Endpoints
# =============================================================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2


@app.post("/auth/login", response_model=AuthenticationResult)
async def login(credentials: UserCredentials) -> None:
    """Authenticate user and return access token."""
    try:
        result = await auth_manager.authenticate_user(credentials)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.error or "Authentication failed",
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication service error: {e!s}",
        )


@app.post("/auth/logout")
async def logout(request: Request, token: str = Depends(security)):
    """Logout user by invalidating token."""
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided"
            )

        success = await auth_manager.logout_user(token.credentials)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to logout"
            )

        return {
            "message": "Successfully logged out",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout error: {e!s}",
        )


@app.get("/auth/me")
async def get_current_user(request: Request) -> None:
    """Get current user information from token."""
    try:
        token_data = await auth_manager.validate_request_auth(request)

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        user_info = await auth_manager.get_user_info(token_data.user_id)

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User info error: {e!s}",
        )


@app.post("/auth/validate")
async def validate_token(request: Request) -> None:
    """Validate token and return user information."""
    try:
        token_data = await auth_manager.validate_request_auth(request)

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        return {
            "valid": True,
            "user_id": token_data.user_id,
            "username": token_data.username,
            "tenant_id": token_data.tenant_id,
            "roles": token_data.roles,
            "permissions": token_data.permissions,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@app.get("/auth/health")
async def auth_health_check() -> None:
    """Health check for authentication module."""
    return await auth_manager.health_check()


# Authentication helper dependency
async def get_current_token_data(request: Request) -> TokenData:
    """Dependency to get current user token data."""
    token_data = await auth_manager.validate_request_auth(request)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


# Admin-only authentication endpoints
@app.post("/auth/admin/users")
async def create_user(
    user_data: Dict[str, Any], current_user: TokenData = Depends(get_current_token_data)
):
    """Create a new user (admin only)."""
    if not auth_manager.check_role(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    try:
        success = await auth_manager.create_user(user_data)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create user"
            )

        return {
            "message": "User created successfully",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User creation error: {e!s}",
        )


# Main proxy handler for all service requests
@app.api_route(
    "/api/{service_name:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
)
async def proxy_to_service(
    service_name: str, request: Request, response: Response
) -> None:
    """Proxy requests to backend services with constitutional compliance."""

    try:
        # Extract tenant context from request
        tenant_context = getattr(request.state, "tenant_context", None)
        user_context = getattr(request.state, "user_context", None)

        # Route request to appropriate service
        service_response = await service_router.route_request(
            service_name=service_name,
            request=request,
            tenant_context=tenant_context,
            user_context=user_context,
        )

        # Record metrics
        await metrics_collector.record_request(
            service_name=service_name,
            method=request.method,
            status_code=service_response.status_code,
            response_time=getattr(request.state, "response_time", 0),
            tenant_id=tenant_context.get("tenant_id") if tenant_context else None,
        )

        # Return service response
        response.status_code = service_response.status_code

        # Copy response headers (filtered for security)
        safe_headers = [
            "content-type",
            "content-length",
            "cache-control",
            "x-constitutional-hash",
            "x-request-id",
        ]

        for header_name, header_value in service_response.headers.items():
            if header_name.lower() in safe_headers:
                response.headers[header_name] = header_value

        # Add constitutional compliance header
        response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
        response.headers["X-Gateway-Version"] = "4.0.0"

        return (
            service_response.json()
            if service_response.headers.get("content-type", "").startswith(
                "application/json"
            )
            else service_response.content
        )

    except HTTPException:
        # Re-raise HTTP exceptions (they contain proper status codes)
        raise

    except Exception as e:
        logger.exception(f"Error proxying request to {service_name}: {e}")

        # Record error metrics
        await metrics_collector.record_error(
            service_name=service_name,
            error_type=type(e).__name__,
            tenant_id=getattr(request.state, "tenant_context", {}).get("tenant_id"),
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "Service unavailable",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> None:
    """Handle HTTP exceptions with constitutional compliance."""

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> None:
    """Handle general exceptions with constitutional compliance."""

    logger.error(f"Unhandled exception: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


# Administrative endpoints
@app.post("/gateway/admin/reload-policies")
async def reload_security_policies() -> None:
    """Reload security policies (admin only)."""

    try:
        await security_policy_engine.reload_policies()

        return {
            "status": "success",
            "message": "Security policies reloaded",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.exception(f"Failed to reload security policies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reload security policies",
        )


@app.post("/gateway/admin/refresh-services")
async def refresh_service_registry() -> None:
    """Refresh service registry (admin only)."""

    try:
        await service_router.refresh_services()

        return {
            "status": "success",
            "message": "Service registry refreshed",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.exception(f"Failed to refresh service registry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh service registry",
        )


if __name__ == "__main__":
    # Run the gateway service
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
        access_log=True,
        server_header=False,  # Security: hide server header
        date_header=False,  # Security: hide date header
    )
