"""
ACGS-PGP v8 Main Application

FastAPI application implementing Quantum-Inspired Semantic Fault Tolerance (QEC-SFT)
architecture with integration to ACGS-1 Constitutional Governance System.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import httpx
import jwt
import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.core.caching.cache_manager import CacheManager, initialize_cache_manager
from services.core.caching.diagnostic_cache import DiagnosticDataCache
from services.core.caching.execution_cache import ExecutionResultCache
from services.core.caching.policy_cache import PolicyGenerationCache
from services.core.generation_engine.engine import (
    GenerationConfig,
    GenerationEngine,
    PolicyGenerationRequest,
    PolicyGenerationResponse,
)
from services.core.monitoring.alerts import AlertManager
from services.core.monitoring.health import HealthMonitor
from services.core.monitoring.metrics import (
    MetricsManager,
    initialize_metrics_manager,
)
from services.core.sde.engine import SyndromeDiagnosticEngine
from services.core.see.environment import StabilizerExecutionEnvironment

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global instances
generation_engine: GenerationEngine | None = None
stabilizer_env: StabilizerExecutionEnvironment | None = None
diagnostic_engine: SyndromeDiagnosticEngine | None = None

# Cache instances
cache_manager: CacheManager | None = None
policy_cache: PolicyGenerationCache | None = None
execution_cache: ExecutionResultCache | None = None
diagnostic_cache: DiagnosticDataCache | None = None

# Monitoring instances
metrics_manager: MetricsManager | None = None
health_monitor: HealthMonitor | None = None
alert_manager: AlertManager | None = None

# Authentication setup
security = HTTPBearer()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "acgs-pgp-v8-secret-key-2024")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global generation_engine, stabilizer_env, diagnostic_engine
    global cache_manager, policy_cache, execution_cache, diagnostic_cache
    global metrics_manager, health_monitor, alert_manager

    logger.info("🚀 Starting ACGS-PGP v8 system initialization...")

    try:
        # Initialize configuration
        config = GenerationConfig(
            gs_service_url=os.getenv("GS_SERVICE_URL", "http://localhost:8004"),
            pgc_service_url=os.getenv("PGC_SERVICE_URL", "http://localhost:8005"),
            constitutional_hash=os.getenv("CONSTITUTIONAL_HASH", "cdd01ef066bc6cf2"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            postgres_url=os.getenv(
                "DATABASE_URL",
                "postgresql://acgs_user:acgs_password@localhost:5432/acgs_db",
            ),
        )

        # Initialize Stabilizer Execution Environment
        stabilizer_env = StabilizerExecutionEnvironment(
            redis_url=config.gs_service_url.replace("8004", "6379").replace(
                "http://", "redis://"
            )
            + "/0",
            postgres_url=os.getenv(
                "DATABASE_URL",
                "postgresql://acgs_user:acgs_password@localhost:5432/acgs_db",
            ),
            constitutional_hash=config.constitutional_hash,
        )
        await stabilizer_env.initialize()
        logger.info("✅ Stabilizer Execution Environment initialized")

        # Initialize Generation Engine
        generation_engine = GenerationEngine(config)
        logger.info("✅ Generation Engine initialized")

        # Initialize Syndrome Diagnostic Engine
        diagnostic_engine = SyndromeDiagnosticEngine(
            stabilizer_env=stabilizer_env,
            constitutional_hash=config.constitutional_hash,
        )
        await diagnostic_engine.initialize()
        logger.info("✅ Syndrome Diagnostic Engine initialized")

        # Initialize Cache Manager and specialized caches
        cache_manager = initialize_cache_manager(
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            constitutional_hash=config.constitutional_hash,
        )
        await cache_manager.initialize()
        logger.info("✅ Cache Manager initialized")

        # Initialize specialized caches
        policy_cache = PolicyGenerationCache(cache_manager)
        execution_cache = ExecutionResultCache(cache_manager)
        diagnostic_cache = DiagnosticDataCache(cache_manager)
        logger.info("✅ Specialized caches initialized")

        # Initialize Monitoring System
        metrics_manager = initialize_metrics_manager(
            constitutional_hash=config.constitutional_hash
        )
        logger.info("✅ Metrics Manager initialized")

        # Initialize Health Monitor
        health_monitor = HealthMonitor(constitutional_hash=config.constitutional_hash)

        # Register health checks for all components
        health_monitor.register_health_check(
            "generation_engine", generation_engine.health_check, interval_seconds=30
        )
        health_monitor.register_health_check(
            "stabilizer_env", stabilizer_env.get_health_status, interval_seconds=30
        )
        health_monitor.register_health_check(
            "diagnostic_engine",
            diagnostic_engine.get_health_status,
            interval_seconds=30,
        )
        health_monitor.register_health_check(
            "cache_manager", cache_manager.health_check, interval_seconds=60
        )

        await health_monitor.start_monitoring()
        logger.info("✅ Health Monitor initialized and started")

        # Initialize Alert Manager
        alert_manager = AlertManager(constitutional_hash=config.constitutional_hash)

        # Register health monitor alerts
        health_monitor.register_alert_callback(alert_manager.process_event)
        logger.info("✅ Alert Manager initialized")

        logger.info("🎉 ACGS-PGP v8 system fully operational")

        yield

    except Exception as e:
        logger.error(f"❌ Failed to initialize ACGS-PGP v8: {e}")
        raise

    finally:
        # Cleanup
        logger.info("🔄 Shutting down ACGS-PGP v8 system...")

        if generation_engine:
            await generation_engine.close()

        if stabilizer_env:
            await stabilizer_env.cleanup()

        if diagnostic_engine:
            await diagnostic_engine.cleanup()

        if cache_manager:
            await cache_manager.close()

        logger.info("✅ ACGS-PGP v8 shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="ACGS-PGP v8: Quantum-Inspired Semantic Fault Tolerance",
    description="Advanced policy generation platform with constitutional governance integration",
    version="8.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security middleware
@app.middleware("http")
async def security_headers_middleware(request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Constitutional compliance header
    response.headers["X-Constitutional-Hash"] = "cdd01ef066bc6cf2"
    response.headers["X-ACGS-Service"] = "acgs-pgp-v8"

    return response


@app.middleware("http")
async def constitutional_compliance_middleware(request, call_next):
    """Validate constitutional compliance for all requests."""
    # Skip compliance check for health endpoints
    if request.url.path in ["/health", "/metrics"]:
        return await call_next(request)

    # Validate constitutional hash in request headers (if provided)
    request_hash = request.headers.get("X-Constitutional-Hash")
    if request_hash and request_hash != "cdd01ef066bc6cf2":
        return JSONResponse(
            status_code=400,
            content={
                "error": "Constitutional compliance violation",
                "detail": "Invalid constitutional hash",
                "expected_hash": "cdd01ef066bc6cf2",
                "provided_hash": request_hash,
            },
        )

    response = await call_next(request)
    return response


# Authentication functions
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict[str, Any]:
    """Verify JWT token and return user information."""
    try:
        # Try to decode JWT token locally first
        payload = jwt.decode(
            credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
        )
        return payload
    except jwt.InvalidTokenError:
        # If local verification fails, try auth service
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{AUTH_SERVICE_URL}/auth/verify",
                    headers={"Authorization": f"Bearer {credentials.credentials}"},
                    timeout=5.0,
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=401, detail="Invalid authentication token"
                    )
        except Exception:
            raise HTTPException(
                status_code=401, detail="Authentication service unavailable"
            )


async def get_current_user(
    token_data: dict[str, Any] = Depends(verify_token),
) -> dict[str, Any]:
    """Get current authenticated user."""
    return token_data


# Dependency injection
async def get_generation_engine() -> GenerationEngine:
    """Get generation engine instance."""
    if not generation_engine:
        raise HTTPException(status_code=503, detail="Generation engine not initialized")
    return generation_engine


async def get_stabilizer_env() -> StabilizerExecutionEnvironment:
    """Get stabilizer execution environment instance."""
    if not stabilizer_env:
        raise HTTPException(
            status_code=503, detail="Stabilizer environment not initialized"
        )
    return stabilizer_env


async def get_diagnostic_engine() -> SyndromeDiagnosticEngine:
    """Get syndrome diagnostic engine instance."""
    if not diagnostic_engine:
        raise HTTPException(status_code=503, detail="Diagnostic engine not initialized")
    return diagnostic_engine


async def get_policy_cache() -> PolicyGenerationCache:
    """Get policy generation cache instance."""
    if not policy_cache:
        raise HTTPException(status_code=503, detail="Policy cache not initialized")
    return policy_cache


async def get_execution_cache() -> ExecutionResultCache:
    """Get execution result cache instance."""
    if not execution_cache:
        raise HTTPException(status_code=503, detail="Execution cache not initialized")
    return execution_cache


async def get_diagnostic_cache() -> DiagnosticDataCache:
    """Get diagnostic data cache instance."""
    if not diagnostic_cache:
        raise HTTPException(status_code=503, detail="Diagnostic cache not initialized")
    return diagnostic_cache


# API Models
class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    service: str
    version: str
    timestamp: str
    constitutional_hash: str
    components: dict[str, Any]


class SystemStatusResponse(BaseModel):
    """System status response model."""

    overall_status: str
    generation_engine: dict[str, Any]
    stabilizer_environment: dict[str, Any]
    diagnostic_engine: dict[str, Any]
    constitutional_hash: str
    timestamp: str


# API Endpoints


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    components = {}

    # Check generation engine
    if generation_engine:
        try:
            gen_health = await generation_engine.health_check()
            components["generation_engine"] = gen_health
        except Exception as e:
            components["generation_engine"] = {"status": "unhealthy", "error": str(e)}
    else:
        components["generation_engine"] = {"status": "not_initialized"}

    # Check stabilizer environment
    if stabilizer_env:
        try:
            stab_health = await stabilizer_env.get_health_status()
            components["stabilizer_environment"] = stab_health
        except Exception as e:
            components["stabilizer_environment"] = {
                "status": "unhealthy",
                "error": str(e),
            }
    else:
        components["stabilizer_environment"] = {"status": "not_initialized"}

    # Check diagnostic engine
    if diagnostic_engine:
        try:
            diag_health = await diagnostic_engine.get_health_status()
            components["diagnostic_engine"] = diag_health
        except Exception as e:
            components["diagnostic_engine"] = {"status": "unhealthy", "error": str(e)}
    else:
        components["diagnostic_engine"] = {"status": "not_initialized"}

    # Check cache manager
    if cache_manager:
        try:
            cache_health = await cache_manager.health_check()
            components["cache_manager"] = cache_health
        except Exception as e:
            components["cache_manager"] = {"status": "unhealthy", "error": str(e)}
    else:
        components["cache_manager"] = {"status": "not_initialized"}

    # Determine overall status
    unhealthy_components = sum(
        1 for comp in components.values() if comp.get("status") != "healthy"
    )

    overall_status = "healthy"
    if unhealthy_components > 0:
        overall_status = (
            "degraded" if unhealthy_components < len(components) else "unhealthy"
        )

    return HealthResponse(
        status=overall_status,
        service="acgs-pgp-v8",
        version="8.0.0",
        timestamp=datetime.now().isoformat(),
        constitutional_hash="cdd01ef066bc6cf2",
        components=components,
    )


@app.get("/api/v1/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get comprehensive system status."""
    gen_status = {}
    stab_status = {}
    diag_status = {}

    if generation_engine:
        gen_status = await generation_engine.get_metrics()

    if stabilizer_env:
        stab_status = stabilizer_env.get_execution_statistics()

    if diagnostic_engine:
        diag_status = await diagnostic_engine.get_metrics()

    # Determine overall status
    all_healthy = all(
        [
            gen_status.get("status") == "healthy" if gen_status else False,
            stab_status.get("status") == "healthy" if stab_status else False,
            diag_status.get("status") == "healthy" if diag_status else False,
        ]
    )

    overall_status = "operational" if all_healthy else "degraded"

    return SystemStatusResponse(
        overall_status=overall_status,
        generation_engine=gen_status,
        stabilizer_environment=stab_status,
        diagnostic_engine=diag_status,
        constitutional_hash="cdd01ef066bc6cf2",
        timestamp=datetime.now().isoformat(),
    )


@app.post("/api/v1/generate-policy", response_model=PolicyGenerationResponse)
async def generate_policy(
    request: PolicyGenerationRequest,
    background_tasks: BackgroundTasks,
    engine: GenerationEngine = Depends(get_generation_engine),
    env: StabilizerExecutionEnvironment = Depends(get_stabilizer_env),
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """Generate policy using quantum-inspired semantic fault tolerance."""
    execution_id = f"policy_gen_{int(datetime.now().timestamp())}"

    # Log authenticated user for audit trail
    user_id = current_user.get("user_id", "unknown")
    logger.info(f"Policy generation requested by user: {user_id}")

    async with env.execute(execution_id, "policy_generation") as execution:
        try:
            execution.add_log("Starting policy generation with QEC-SFT")

            # Generate policy using the generation engine
            response = await engine.generate_policy(
                request, use_quantum_enhancement=True
            )

            execution.add_log(
                f"Policy generated successfully: {response.generation_id}"
            )
            execution.result_data = {
                "generation_id": response.generation_id,
                "constitutional_compliance_score": response.constitutional_compliance_score,
                "confidence_score": response.confidence_score,
                "semantic_hash": response.semantic_hash,
            }

            return response

        except Exception as e:
            execution.add_log(f"Policy generation failed: {str(e)}", "ERROR")
            raise HTTPException(
                status_code=500, detail=f"Policy generation failed: {str(e)}"
            )


@app.post("/api/v1/diagnose")
async def diagnose_system(
    target_system: str = "acgs-pgp-v8",
    current_user: dict[str, Any] = Depends(get_current_user),
    diagnostic_engine: SyndromeDiagnosticEngine = Depends(get_diagnostic_engine),
):
    """Perform system diagnosis with authentication required."""
    try:
        user_id = current_user.get("user_id", "unknown")
        logger.info(f"System diagnosis requested by user: {user_id}")

        result = await diagnostic_engine.diagnose_system(
            target_system=target_system, include_recommendations=True
        )

        return {
            "diagnostic_id": result.diagnostic_id,
            "target_system": result.target_system,
            "overall_health_score": result.overall_health_score,
            "constitutional_compliance_score": result.constitutional_compliance_score,
            "error_count": result.error_count,
            "critical_error_count": result.critical_error_count,
            "recommendations_count": len(result.recommendations),
            "auto_executable_recommendations": result.auto_executable_recommendations,
            "timestamp": result.diagnostic_timestamp.isoformat(),
            "constitutional_hash": result.constitutional_hash,
            "is_system_healthy": result.is_system_healthy(),
            "requires_immediate_attention": result.requires_immediate_attention(),
        }

    except Exception as e:
        logger.error(f"System diagnosis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Diagnosis failed: {str(e)}")


@app.get("/metrics")
async def get_prometheus_metrics():
    """Prometheus metrics endpoint."""
    try:
        if metrics_manager:
            metrics_data = metrics_manager.get_metrics_data()
            return Response(
                content=metrics_data,
                media_type="text/plain; version=0.0.4; charset=utf-8",
            )
        else:
            return Response(
                content="# Metrics manager not initialized\n",
                media_type="text/plain; version=0.0.4; charset=utf-8",
            )
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        return Response(
            content=f"# Error getting metrics: {str(e)}\n",
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )


@app.get("/api/v1/metrics/summary")
async def get_metrics_summary():
    """Get metrics summary for monitoring dashboards."""
    try:
        if metrics_manager:
            summary = metrics_manager.get_metrics_summary()
            return summary
        else:
            return {
                "error": "Metrics manager not initialized",
                "constitutional_hash": "cdd01ef066bc6cf2",
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get metrics summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Metrics summary failed: {str(e)}")


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8010")),
        reload=False,
        log_level="info",
    )
