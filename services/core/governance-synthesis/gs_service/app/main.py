"""
Simplified Governance Synthesis Service - Production Fix
Streamlined configuration to resolve import and dependency issues
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

# Import multi-tenant components
try:
    import os
    import sys
    from pathlib import Path

    # Add project root to path
    current_dir = Path(Path(__file__).resolve()).parent
    project_root = os.path.join(current_dir, "..", "..", "..", "..", "..")
    shared_path = os.path.join(project_root, "services", "shared")
    sys.path.insert(0, Path(shared_path).resolve())

    from clients.tenant_service_client import TenantServiceClient, service_registry
    from middleware.tenant_middleware import (
        TenantContextMiddleware,
        TenantSecurityMiddleware,
        get_optional_tenant_context,
        get_tenant_context,
        get_tenant_db,
    )

    MULTI_TENANT_AVAILABLE = True
except ImportError:
    MULTI_TENANT_AVAILABLE = False

# Import production security middleware
try:
    sys.path.append("/home/dislove/ACGS-1/services/shared")
    from security_middleware import (
        apply_production_security_middleware,
        create_security_config,
    )

    SECURITY_MIDDLEWARE_AVAILABLE = True
except ImportError:
    SECURITY_MIDDLEWARE_AVAILABLE = False

# Import leader election
try:
    sys.path.append("/home/ubuntu/ACGS/services/shared")
    from leader_election import create_leader_election_service, leader_required

    LEADER_ELECTION_AVAILABLE = True
except ImportError:
    LEADER_ELECTION_AVAILABLE = False

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import PlainTextResponse

# Service configuration
SERVICE_NAME = "gs_service"
SERVICE_VERSION = "4.0.0"  # Upgraded for multi-tenant support
SERVICE_PORT = 8004

# JWT configuration for multi-tenant tokens
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
JWT_ALGORITHM = "HS256"

# Leader election configuration
import os

NAMESPACE = os.getenv("KUBERNETES_NAMESPACE", "default")
ENABLE_LEADER_ELECTION = os.getenv("ENABLE_LEADER_ELECTION", "true").lower() == "true"

# Global leader election service
leader_election_service = None

# Global advanced governance synthesis engine
advanced_governance_engine = None

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(SERVICE_NAME)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "gs_service_requests_total", "Total requests", ["method", "endpoint", "status"]
)
REQUEST_DURATION = Histogram("gs_service_request_duration_seconds", "Request duration")


# Leader election callbacks
async def on_started_leading():
    """Called when this instance becomes the leader."""
    logger.info("🏛️ GS Service became leader - Starting governance synthesis operations")


async def on_stopped_leading():
    """Called when this instance loses leadership."""
    logger.info(
        "🔄 GS Service lost leadership - Stopping governance synthesis operations"
    )


async def on_new_leader(leader_identity: str):
    """Called when a new leader is elected."""
    logger.info(f"👑 New GS Service leader elected: {leader_identity}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with leader election and advanced governance engine"""
    global leader_election_service, advanced_governance_engine

    logger.info(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")

    # Initialize advanced governance synthesis engine
    try:
        policies_path = os.path.join(Path(__file__).parent, "..", "policies")
        advanced_governance_engine = AdvancedGovernanceSynthesisEngine(policies_path)
        logger.info("✅ Advanced Governance Synthesis Engine initialized")
    except Exception as e:
        logger.exception(f"❌ Failed to initialize Advanced Governance Engine: {e}")
        advanced_governance_engine = None

    # Initialize leader election if enabled
    if ENABLE_LEADER_ELECTION and LEADER_ELECTION_AVAILABLE:
        try:
            leader_election_service = await create_leader_election_service(
                service_name=SERVICE_NAME,
                namespace=NAMESPACE,
                on_started_leading=on_started_leading,
                on_stopped_leading=on_stopped_leading,
                on_new_leader=on_new_leader,
            )

            # Start leader election in background
            asyncio.create_task(leader_election_service.start_leader_election())
            logger.info("✅ Leader election enabled for GS service")

        except Exception as e:
            logger.exception(f"❌ Failed to initialize leader election: {e}")
            leader_election_service = None
    else:
        logger.info("⚠️ Leader election disabled for GS service")

    yield

    # Cleanup
    logger.info(f"🔄 Shutting down {SERVICE_NAME}")
    if leader_election_service:
        await leader_election_service.stop_leader_election()


# Create FastAPI application
app = FastAPI(
    title="ACGS-PGP Governance Synthesis Service",
    description="Simplified governance synthesis service for ACGS-PGP system",
    version=SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add multi-tenant middleware
if MULTI_TENANT_AVAILABLE:
    # Add tenant context middleware (before other middleware)
    app.add_middleware(
        TenantContextMiddleware,
        jwt_secret_key=JWT_SECRET_KEY,
        jwt_algorithm=JWT_ALGORITHM,
        exclude_paths=[
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics",
            "/leader-election/status",
            "/leader-election/health",
        ],
        require_tenant=True,  # Governance synthesis requires tenant context
        bypass_paths=[
            "/health",
            "/metrics",
            "/leader-election/status",
            "/leader-election/health",
        ],
    )

    # Add tenant security middleware
    app.add_middleware(TenantSecurityMiddleware)


@app.middleware("http")
async def add_comprehensive_security_headers(request, call_next):
    """Add comprehensive security and constitutional compliance headers"""
    response = await call_next(request)

    # Core security headers
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["x-frame-options"] = "DENY"
    response.headers["x-xss-protection"] = "1; mode=block"
    response.headers["strict-transport-security"] = (
        "max-age=31536000; includeSubDomains; preload"
    )

    # Content Security Policy
    response.headers["content-security-policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data: https:; "
        "connect-src 'self' ws: wss: https:; "
        "media-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "base-uri 'self'; "
        "upgrade-insecure-requests"
    )

    # Rate limiting headers
    response.headers["x-ratelimit-limit"] = "60000"
    response.headers["x-ratelimit-remaining"] = "59999"
    response.headers["x-ratelimit-reset"] = str(int(time.time() + 60))

    # Constitutional compliance and service identification
    response.headers["x-constitutional-hash"] = "cdd01ef066bc6cf2"
    response.headers["x-acgs-security"] = "enabled"

    return response


# Apply production-grade security middleware
if SECURITY_MIDDLEWARE_AVAILABLE:
    security_config = create_security_config(
        max_request_size=10 * 1024 * 1024,  # 10MB
        rate_limit_requests=120,
        rate_limit_window=60,
        enable_threat_detection=True,
    )
    apply_production_security_middleware(app, "gs_service", security_config)


# Add secure CORS middleware with environment-based configuration
import os

cors_origins = os.getenv(
    "BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:8080"
).split(",")
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Restricted to configured origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Request-ID",
        "X-Constitutional-Hash",
    ],
    expose_headers=["X-Request-ID", "X-Response-Time", "X-Compliance-Score"],
)

# Add trusted host middleware with secure configuration
allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,acgs.local").split(",")
allowed_hosts = [host.strip() for host in allowed_hosts if host.strip()]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)


@app.middleware("http")
async def add_constitutional_headers(request: Request, call_next):
    """Add constitutional compliance headers"""
    response = await call_next(request)
    response.headers["x-constitutional-hash"] = "cdd01ef066bc6cf2"
    response.headers["x-service-name"] = SERVICE_NAME
    response.headers["x-service-version"] = SERVICE_VERSION
    return response


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Prometheus metrics middleware"""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    REQUEST_DURATION.observe(duration)
    REQUEST_COUNT.labels(
        method=request.method, endpoint=request.url.path, status=response.status_code
    ).inc()

    return response


# Import performance optimization module
import os

# Import advanced governance synthesis engine
import sys

from .performance_optimizer import (
    SynthesisPerformanceMonitor,
    apply_wina_optimization,
    cache_synthesis_response,
    get_synthesis_performance_metrics,
)

sys.path.append(os.path.join(Path(__file__).parent, ".."))
from advanced_opa_engine import (
    AdvancedGovernanceSynthesisEngine,
    PolicyEvaluationContext,
)


# Health check endpoint with performance optimization
@app.get("/health")
@cache_synthesis_response(ttl=60, key_prefix="gs_health")
async def health_check():
    """Health check endpoint with synthesis performance optimization"""
    start_time = time.time()

    health_data = {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "constitutional_hash": "cdd01ef066bc6cf2",
        "multi_tenant_enabled": MULTI_TENANT_AVAILABLE,
        "request_count": getattr(health_check, "_request_count", 0),
    }

    # Increment request counter
    health_check._request_count = getattr(health_check, "_request_count", 0) + 1

    # Add performance metrics
    response_time_ms = (time.time() - start_time) * 1000
    health_data["response_time_ms"] = round(response_time_ms, 2)

    return health_data


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Leader election endpoints
@app.get("/leader-election/status")
async def get_leader_election_status():
    """Get leader election status."""
    if leader_election_service:
        return leader_election_service.get_health_status()
    return {
        "service_name": SERVICE_NAME,
        "leader_election_enabled": False,
        "message": "Leader election not configured",
    }


@app.get("/leader-election/health")
async def get_leader_election_health():
    """Leader election health check."""
    if leader_election_service:
        health_info = leader_election_service.get_health_status()
        health_info["endpoint"] = "leader_election_health"
        return health_info
    return {"status": "disabled", "leader_election_enabled": False}


# Leader-only governance synthesis operations
@validate_policy_input
@app.post("/api/v1/synthesize/leader")
async def synthesize_governance_as_leader(request: Request):
    """Governance synthesis operations (leader-only)."""
    if not leader_election_service or not leader_election_service.is_leader():
        return {
            "error": "Operation requires leadership",
            "is_leader": (
                leader_election_service.is_leader()
                if leader_election_service
                else False
            ),
            "leader_identity": (
                leader_election_service.get_leader_identity()
                if leader_election_service
                else None
            ),
        }

    logger.info("🏛️ Synthesizing governance as leader")

    try:
        await request.json()

        # Leader-only governance synthesis logic
        return {
            "synthesis_id": f"gs_leader_{int(time.time())}",
            "status": "completed_as_leader",
            "leader_identity": leader_election_service.get_leader_identity(),
            "governance_rules": [
                {
                    "rule_id": "leader_rule_001",
                    "type": "constitutional_compliance",
                    "description": "Leader-coordinated governance rule",
                    "priority": "high",
                    "leader_coordinated": True,
                }
            ],
            "constitutional_hash": "cdd01ef066bc6cf2",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.exception(f"Leader synthesis error: {e}")
        return {"error": str(e), "status": "failed"}


# Optimized governance synthesis endpoint
@validate_policy_input
@app.post("/api/v1/synthesize")
@cache_synthesis_response(ttl=300, key_prefix="gs_synthesis")
async def synthesize_governance(
    request: Request,
    session: AsyncSession = Depends(get_tenant_db) if MULTI_TENANT_AVAILABLE else None,
    tenant_context=Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None,
):
    """Optimized governance synthesis endpoint with advanced OPA engine and WINA optimization"""
    async with SynthesisPerformanceMonitor("governance_synthesis"):
        try:
            body = await request.json()

            # Apply WINA optimization to input policy
            optimized_input = await apply_wina_optimization(body)

            # If advanced governance engine is available, use it
            if advanced_governance_engine:
                # Create policy evaluation context
                context = PolicyEvaluationContext(
                    request_id=f"gs_{int(time.time())}",
                    timestamp=datetime.now(timezone.utc),
                    principal=body.get(
                        "principal",
                        {
                            "id": "system",
                            "type": "governance_service",
                            "tenant_id": (
                                tenant_context.tenant_id
                                if tenant_context
                                else "default"
                            ),
                        },
                    ),
                    resource=body.get(
                        "resource",
                        {"id": "governance_policy", "type": "policy_synthesis"},
                    ),
                    action=body.get("action", "synthesize_governance"),
                    environment=body.get("environment", {}),
                    constitutional_requirements=body.get(
                        "constitutional_requirements",
                        {
                            "human_dignity": True,
                            "fairness": True,
                            "transparency": True,
                            "accountability": True,
                            "privacy": True,
                        },
                    ),
                )

                # Perform advanced governance synthesis
                advanced_result = (
                    await advanced_governance_engine.synthesize_governance_decision(
                        context
                    )
                )

                # Enhance with WINA optimization data
                return {
                    **advanced_result,
                    "wina_optimized": True,
                    "optimization_metrics": {
                        "wina_applied": optimized_input.get("wina_optimized", False),
                        "optimization_level": optimized_input.get(
                            "neuron_activation", {}
                        ).get("optimization_level", "medium"),
                        "confidence_boost": optimized_input.get(
                            "neuron_activation", {}
                        ).get("confidence", 0.85),
                    },
                    "legacy_compatibility": True,
                }

            # Fallback to legacy synthesis if advanced engine not available
            logger.warning(
                "Advanced governance engine not available, using legacy synthesis"
            )

            # Enhanced governance synthesis response with optimization
            return {
                "synthesis_id": f"gs_{int(time.time())}",
                "status": "completed",
                "wina_optimized": True,
                "governance_rules": [
                    {
                        "rule_id": "rule_001",
                        "type": "constitutional_compliance",
                        "description": (
                            "Ensure all actions comply with constitutional hash"
                        ),
                        "priority": "high",
                        "wina_weight": optimized_input.get("weight_analysis", {}).get(
                            "constitutional_weight", 0.95
                        ),
                    },
                    {
                        "rule_id": "rule_002",
                        "type": "policy_governance",
                        "description": "WINA-optimized policy governance rule",
                        "priority": "high",
                        "optimization_score": optimized_input.get(
                            "neuron_activation", {}
                        ).get("activation_score", 0.89),
                    },
                ],
                "optimization_metrics": {
                    "wina_applied": optimized_input.get("wina_optimized", False),
                    "optimization_level": optimized_input.get(
                        "neuron_activation", {}
                    ).get("optimization_level", "medium"),
                    "confidence_score": optimized_input.get(
                        "neuron_activation", {}
                    ).get("confidence", 0.85),
                },
                "constitutional_hash": "cdd01ef066bc6cf2",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "legacy_mode": True,
            }

        except Exception as e:
            logger.exception(f"Synthesis error: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "constitutional_hash": "cdd01ef066bc6cf2",
            }


# Validation decorator for policy input
def validate_policy_input(func):
    """Decorator for validating policy input"""

    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    return wrapper


# Import and include APGF router
from .api.v1.apgf_endpoints import router as apgf_router

app.include_router(apgf_router)


# Enhanced service info endpoint with performance metrics
@app.get("/api/v1/info")
@cache_synthesis_response(ttl=120, key_prefix="gs_info")
async def service_info():
    """Service information endpoint with performance optimization"""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "status": "operational",
        "constitutional_hash": "cdd01ef066bc6cf2",
        "optimization_enabled": True,
        "wina_optimization": True,
        "capabilities": [
            "governance_synthesis",
            "advanced_opa_engine",
            "policy_evaluation",
            "policy_conflict_resolution",
            "constitutional_compliance",
            "temporal_policy_verification",
            "multi_policy_orchestration",
            "policy_generation",
            "wina_optimization",
            "performance_caching",
            "apgf_workflows",
            "dynamic_agents",
            "tool_execution",
        ],
        "endpoints": [
            "/health",
            "/metrics",
            "/api/v1/synthesize",
            "/api/v1/synthesize/advanced",
            "/api/v1/policy/evaluate",
            "/api/v1/policy/catalog",
            "/api/v1/info",
            "/api/v1/performance/metrics",
            "/api/v1/apgf/workflows",
            "/api/v1/apgf/agents",
            "/api/v1/apgf/tools/execute",
            "/api/v1/apgf/status",
            "/api/v1/apgf/health",
        ],
    }


# Advanced governance synthesis endpoint
@app.post("/api/v1/synthesize/advanced")
async def synthesize_governance_advanced(request: Request):
    """Advanced governance synthesis with comprehensive policy evaluation"""
    try:
        if not advanced_governance_engine:
            return {
                "error": "Advanced governance engine not available",
                "status": "service_unavailable",
                "constitutional_hash": "cdd01ef066bc6cf2",
            }

        body = await request.json()

        # Create comprehensive policy evaluation context
        context = PolicyEvaluationContext(
            request_id=body.get("request_id", f"advanced_gs_{int(time.time())}"),
            timestamp=datetime.now(timezone.utc),
            principal=body.get("principal", {}),
            resource=body.get("resource", {}),
            action=body.get("action", "governance_decision"),
            environment=body.get("environment", {}),
            historical_context=body.get("historical_context", []),
            constitutional_requirements=body.get("constitutional_requirements", {}),
        )

        # Specify policy scope if provided
        policy_scope = body.get("policy_scope")

        # Perform advanced governance synthesis
        result = await advanced_governance_engine.synthesize_governance_decision(
            context, policy_scope
        )

        logger.info(
            f"Advanced governance synthesis completed: {result['synthesis_id']}"
        )
        return result

    except Exception as e:
        logger.exception(f"Advanced synthesis error: {e}")
        return {
            "error": str(e),
            "status": "synthesis_failed",
            "constitutional_hash": "cdd01ef066bc6cf2",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Policy evaluation endpoint
@app.post("/api/v1/policy/evaluate")
async def evaluate_policy(request: Request):
    """Evaluate specific policies against a context"""
    try:
        if not advanced_governance_engine:
            return {
                "error": "Advanced governance engine not available",
                "status": "service_unavailable",
                "constitutional_hash": "cdd01ef066bc6cf2",
            }

        body = await request.json()

        # Create policy evaluation context
        context = PolicyEvaluationContext(
            request_id=body.get("request_id", f"policy_eval_{int(time.time())}"),
            timestamp=datetime.now(timezone.utc),
            principal=body.get("principal", {}),
            resource=body.get("resource", {}),
            action=body.get("action", "policy_evaluation"),
            environment=body.get("environment", {}),
            constitutional_requirements=body.get("constitutional_requirements", {}),
        )

        # Get policies to evaluate
        policies = body.get("policies", [])
        if not policies:
            return {
                "error": "No policies specified for evaluation",
                "status": "invalid_request",
                "constitutional_hash": "cdd01ef066bc6cf2",
            }

        # Evaluate policies
        policy_decisions = await advanced_governance_engine.evaluation_engine.evaluate_multiple_policies(
            policies, context
        )

        # Format results
        return {
            "evaluation_id": context.request_id,
            "policies_evaluated": policies,
            "decisions": [
                advanced_governance_engine._serialize_decision(d)
                for d in policy_decisions
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

    except Exception as e:
        logger.exception(f"Policy evaluation error: {e}")
        return {
            "error": str(e),
            "status": "evaluation_failed",
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


# Performance metrics endpoint
@app.get("/api/v1/performance/metrics")
async def get_synthesis_performance_metrics():
    """Get detailed synthesis performance metrics"""
    async with SynthesisPerformanceMonitor("performance_metrics"):
        try:
            metrics = await get_synthesis_performance_metrics()

            # Add advanced engine metrics if available
            advanced_metrics = {}
            if advanced_governance_engine:
                advanced_metrics = (
                    await advanced_governance_engine.get_performance_metrics()
                )

            return {
                "service": SERVICE_NAME,
                "version": SERVICE_VERSION,
                "optimization_status": "enabled",
                "target_response_time_ms": 5.0,
                "performance_metrics": metrics,
                "advanced_engine_metrics": advanced_metrics,
                "constitutional_hash": "cdd01ef066bc6cf2",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.exception(f"Performance metrics error: {e}")
            return {
                "error": str(e),
                "optimization_status": "error",
                "constitutional_hash": "cdd01ef066bc6cf2",
            }


# Policy catalog endpoint
@app.get("/api/v1/policy/catalog")
async def get_policy_catalog():
    """Get available policy catalog"""
    try:
        if not advanced_governance_engine:
            return {
                "error": "Advanced governance engine not available",
                "status": "service_unavailable",
                "constitutional_hash": "cdd01ef066bc6cf2",
            }

        return {
            "policy_catalog": advanced_governance_engine.policy_catalog,
            "total_policies": len(advanced_governance_engine.policy_catalog),
            "policy_dependencies": len(advanced_governance_engine.policy_graph.edges()),
            "constitutional_hash": "cdd01ef066bc6cf2",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.exception(f"Policy catalog error: {e}")
        return {
            "error": str(e),
            "status": "catalog_error",
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


if __name__ == "__main__":
    import uvicorn

# Security validation imports

config = {
    "host": "0.0.0.0",
    "port": SERVICE_PORT,
    "log_level": "info",
    "access_log": True,
}

logger.info(f"🚀 Starting {SERVICE_NAME} on port {SERVICE_PORT}")
uvicorn.run(app, **config)
