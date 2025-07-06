"""
ACGS API Gateway Service

Constitutional AI-enhanced API gateway providing unified entry point,
authentication, authorization, rate limiting, and security policy enforcement.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import httpx

# ACGS imports
from .core.gateway_config import GatewayConfig
from .middleware.authentication import AuthenticationMiddleware
from .middleware.rate_limiting import RateLimitingMiddleware
from .middleware.constitutional_compliance import ConstitutionalComplianceMiddleware
from .middleware.security_headers import SecurityHeadersMiddleware
from .middleware.request_logging import RequestLoggingMiddleware
from .routing.service_router import ServiceRouter
from .security.policy_engine import SecurityPolicyEngine
from .monitoring.metrics_collector import MetricsCollector

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ACGS API Gateway",
    description="Constitutional AI-enhanced API gateway for secure microservices access",
    version="4.0.0",
    docs_url="/gateway/docs" if GatewayConfig.ENABLE_DOCS else None,
    redoc_url="/gateway/redoc" if GatewayConfig.ENABLE_DOCS else None
)

# Initialize core components
gateway_config = GatewayConfig()
service_router = ServiceRouter()
security_policy_engine = SecurityPolicyEngine()
metrics_collector = MetricsCollector()


@app.on_event("startup")
async def startup_event():
    """Initialize gateway components on startup."""
    
    logger.info(f"Starting ACGS API Gateway with constitutional hash: {CONSTITUTIONAL_HASH}")
    
    # Initialize service router
    await service_router.initialize()
    
    # Initialize security policy engine
    await security_policy_engine.initialize()
    
    # Initialize metrics collector
    await metrics_collector.initialize()
    
    # Verify constitutional compliance
    constitutional_status = await verify_constitutional_compliance()
    if not constitutional_status["is_compliant"]:
        logger.critical("Constitutional compliance verification failed!")
        raise RuntimeError("Constitutional compliance check failed")
    
    logger.info("ACGS API Gateway startup completed successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    
    logger.info("Shutting down ACGS API Gateway")
    
    # Cleanup components
    await metrics_collector.cleanup()
    await service_router.cleanup()
    await security_policy_engine.cleanup()
    
    logger.info("ACGS API Gateway shutdown completed")


# Add middleware stack (order is important)
app.add_middleware(
    RequestLoggingMiddleware,
    constitutional_hash=CONSTITUTIONAL_HASH
)

app.add_middleware(
    SecurityHeadersMiddleware,
    constitutional_compliance=True
)

app.add_middleware(
    ConstitutionalComplianceMiddleware,
    constitutional_hash=CONSTITUTIONAL_HASH,
    policy_engine=security_policy_engine
)

app.add_middleware(
    RateLimitingMiddleware,
    requests_per_minute=gateway_config.RATE_LIMIT_REQUESTS_PER_MINUTE,
    burst_limit=gateway_config.RATE_LIMIT_BURST
)

app.add_middleware(
    AuthenticationMiddleware,
    constitutional_verification=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=gateway_config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"]
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=gateway_config.ALLOWED_HOSTS
)


# Constitutional compliance verification endpoint
async def verify_constitutional_compliance() -> Dict[str, Any]:
    """Verify constitutional compliance of the gateway."""
    
    try:
        # Verify constitutional hash
        current_hash = CONSTITUTIONAL_HASH
        expected_hash = "cdd01ef066bc6cf2"
        
        hash_valid = current_hash == expected_hash
        
        # Verify policy engine compliance
        policy_compliance = await security_policy_engine.verify_constitutional_compliance()
        
        # Verify service routing compliance
        routing_compliance = await service_router.verify_constitutional_compliance()
        
        overall_compliance = hash_valid and policy_compliance and routing_compliance
        
        return {
            "is_compliant": overall_compliance,
            "constitutional_hash": current_hash,
            "hash_valid": hash_valid,
            "policy_compliance": policy_compliance,
            "routing_compliance": routing_compliance,
            "verified_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Constitutional compliance verification failed: {e}")
        return {
            "is_compliant": False,
            "error": str(e),
            "verified_at": datetime.now(timezone.utc).isoformat()
        }


# Health check endpoints
@app.get("/gateway/health")
async def health_check():
    """Gateway health check endpoint."""
    
    return {
        "status": "healthy",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "4.0.0"
    }


@app.get("/gateway/health/detailed")
async def detailed_health_check():
    """Detailed health check with component status."""
    
    # Check component health
    components_health = {
        "service_router": await service_router.health_check(),
        "security_policy_engine": await security_policy_engine.health_check(),
        "metrics_collector": await metrics_collector.health_check()
    }
    
    # Check constitutional compliance
    constitutional_status = await verify_constitutional_compliance()
    
    overall_healthy = (
        all(health["healthy"] for health in components_health.values()) and
        constitutional_status["is_compliant"]
    )
    
    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "constitutional_compliance": constitutional_status,
        "components": components_health,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# Gateway configuration endpoint
@app.get("/gateway/config")
async def get_gateway_config():
    """Get gateway configuration (filtered for security)."""
    
    return {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "version": "4.0.0",
        "rate_limiting": {
            "requests_per_minute": gateway_config.RATE_LIMIT_REQUESTS_PER_MINUTE,
            "burst_limit": gateway_config.RATE_LIMIT_BURST
        },
        "security": {
            "constitutional_compliance_enabled": True,
            "multi_tenant_isolation": True,
            "formal_verification": True
        },
        "services": await service_router.get_registered_services()
    }


# Metrics endpoint
@app.get("/gateway/metrics")
async def get_gateway_metrics():
    """Get gateway metrics."""
    
    return await metrics_collector.get_metrics()


# Main proxy handler for all service requests
@app.api_route("/api/{service_name:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_to_service(
    service_name: str,
    request: Request,
    response: Response
):
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
            user_context=user_context
        )
        
        # Record metrics
        await metrics_collector.record_request(
            service_name=service_name,
            method=request.method,
            status_code=service_response.status_code,
            response_time=getattr(request.state, "response_time", 0),
            tenant_id=tenant_context.get("tenant_id") if tenant_context else None
        )
        
        # Return service response
        response.status_code = service_response.status_code
        
        # Copy response headers (filtered for security)
        safe_headers = [
            "content-type", "content-length", "cache-control",
            "x-constitutional-hash", "x-request-id"
        ]
        
        for header_name, header_value in service_response.headers.items():
            if header_name.lower() in safe_headers:
                response.headers[header_name] = header_value
        
        # Add constitutional compliance header
        response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
        response.headers["X-Gateway-Version"] = "4.0.0"
        
        return service_response.json() if service_response.headers.get("content-type", "").startswith("application/json") else service_response.content
        
    except HTTPException:
        # Re-raise HTTP exceptions (they contain proper status codes)
        raise
        
    except Exception as e:
        logger.error(f"Error proxying request to {service_name}: {e}")
        
        # Record error metrics
        await metrics_collector.record_error(
            service_name=service_name,
            error_type=type(e).__name__,
            tenant_id=getattr(request.state, "tenant_context", {}).get("tenant_id")
        )
        
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "Service unavailable",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with constitutional compliance."""
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with constitutional compliance."""
    
    logger.error(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


# Administrative endpoints
@app.post("/gateway/admin/reload-policies")
async def reload_security_policies():
    """Reload security policies (admin only)."""
    
    try:
        await security_policy_engine.reload_policies()
        
        return {
            "status": "success",
            "message": "Security policies reloaded",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to reload security policies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reload security policies"
        )


@app.post("/gateway/admin/refresh-services")
async def refresh_service_registry():
    """Refresh service registry (admin only)."""
    
    try:
        await service_router.refresh_services()
        
        return {
            "status": "success", 
            "message": "Service registry refreshed",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to refresh service registry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh service registry"
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
        date_header=False     # Security: hide date header
    )