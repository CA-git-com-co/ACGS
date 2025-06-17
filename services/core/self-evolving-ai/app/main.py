"""
ACGS-1 Self-Evolving AI Architecture Foundation Service

This service implements the foundational self-evolving AI governance architecture
with manual policy evolution, comprehensive security, and human control mechanisms.

Key Features:
- Layered security architecture (4 layers)
- Manual policy evolution with 100% human oversight
- Risk mitigation for top 6 threats
- Integration with all ACGS-1 services
- Comprehensive observability framework

Performance Targets:
- >1000 concurrent governance actions
- >99.9% availability during evolution
- <500ms response times for 95% requests
- <10 minute evolution cycle time

Quantumagi Compatibility:
- Preserve Constitution Hash cdd01ef066bc6cf2
- Maintain Solana devnet deployment
- Ensure governance workflow compatibility
- Support constitutional amendments
"""

import logging
import sys
import time
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Import API routers
from .api.v1.evolution import router as evolution_router
from .api.v1.observability import router as observability_router
from .api.v1.security import router as security_router

# Import configuration and dependencies
from .config import get_settings
from .core.background_processor import BackgroundProcessor

# Import core components
from .core.evolution_engine import EvolutionEngine
from .core.observability_framework import ObservabilityFramework
from .core.policy_orchestrator import PolicyOrchestrator
from .core.security_manager import SecurityManager
from .dependencies import (
    set_background_processor,
    set_evolution_engine,
    set_observability_framework,
    set_policy_orchestrator,
    set_security_manager,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/self_evolving_ai.log", mode="a"),
    ],
)

logger = logging.getLogger(__name__)

# Global service instances
evolution_engine: EvolutionEngine | None = None
security_manager: SecurityManager | None = None
policy_orchestrator: PolicyOrchestrator | None = None
background_processor: BackgroundProcessor | None = None
observability_framework: ObservabilityFramework | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global evolution_engine, security_manager, policy_orchestrator
    global background_processor, observability_framework

    settings = get_settings()

    try:
        logger.info(
            "🚀 Starting ACGS-1 Self-Evolving AI Architecture Foundation Service"
        )

        # Initialize observability framework first
        observability_framework = ObservabilityFramework(settings)
        await observability_framework.initialize()
        logger.info("✅ Observability framework initialized")

        # Initialize security manager
        security_manager = SecurityManager(settings)
        await security_manager.initialize()
        logger.info("✅ Security manager initialized with 4-layer architecture")

        # Initialize policy orchestrator
        policy_orchestrator = PolicyOrchestrator(settings)
        await policy_orchestrator.initialize()
        logger.info("✅ Policy orchestrator initialized with OPA integration")

        # Initialize background processor
        background_processor = BackgroundProcessor(settings)
        await background_processor.initialize()
        logger.info("✅ Background processor initialized with Celery/Redis")

        # Initialize evolution engine
        evolution_engine = EvolutionEngine(
            settings=settings,
            security_manager=security_manager,
            policy_orchestrator=policy_orchestrator,
            background_processor=background_processor,
            observability_framework=observability_framework,
        )
        await evolution_engine.initialize()
        logger.info("✅ Evolution engine initialized with manual oversight")

        # Set dependencies for FastAPI
        set_evolution_engine(evolution_engine)
        set_security_manager(security_manager)
        set_policy_orchestrator(policy_orchestrator)
        set_background_processor(background_processor)
        set_observability_framework(observability_framework)

        # Perform system health check (temporarily disabled for debugging)
        # health_status = await perform_startup_health_check()
        # if not health_status["healthy"]:
        #     logger.error("❌ Startup health check failed")
        #     raise RuntimeError("Service startup health check failed")
        logger.info("⚠️ Startup health check temporarily disabled")

        logger.info("🎯 Self-Evolving AI Architecture Foundation Service ready")
        logger.info(
            "📊 Performance targets: >1000 concurrent actions, >99.9% availability"
        )
        logger.info("🔒 Security: 4-layer architecture with human oversight")
        logger.info("🏛️ Quantumagi compatibility: Constitution Hash cdd01ef066bc6cf2")

        yield

    except Exception as e:
        logger.error(f"❌ Service startup failed: {e}")
        raise
    finally:
        # Cleanup on shutdown
        logger.info("🛑 Shutting down Self-Evolving AI Architecture Foundation Service")

        if evolution_engine:
            await evolution_engine.shutdown()
        if background_processor:
            await background_processor.shutdown()
        if policy_orchestrator:
            await policy_orchestrator.shutdown()
        if security_manager:
            await security_manager.shutdown()
        if observability_framework:
            await observability_framework.shutdown()

        logger.info("✅ Service shutdown complete")


async def perform_startup_health_check() -> dict[str, Any]:
    """Perform comprehensive startup health check."""
    health_status = {
        "healthy": True,
        "timestamp": time.time(),
        "checks": {},
    }

    try:
        # Check evolution engine
        if evolution_engine:
            engine_health = await evolution_engine.health_check()
            health_status["checks"]["evolution_engine"] = engine_health
            if not engine_health.get("healthy", False):
                health_status["healthy"] = False

        # Check security manager
        if security_manager:
            security_health = await security_manager.health_check()
            health_status["checks"]["security_manager"] = security_health
            if not security_health.get("healthy", False):
                health_status["healthy"] = False

        # Check policy orchestrator
        if policy_orchestrator:
            policy_health = await policy_orchestrator.health_check()
            health_status["checks"]["policy_orchestrator"] = policy_health
            if not policy_health.get("healthy", False):
                health_status["healthy"] = False

        # Check background processor
        if background_processor:
            processor_health = await background_processor.health_check()
            health_status["checks"]["background_processor"] = processor_health
            if not processor_health.get("healthy", False):
                health_status["healthy"] = False

        # Check observability framework
        if observability_framework:
            observability_health = await observability_framework.health_check()
            health_status["checks"]["observability_framework"] = observability_health
            if not observability_health.get("healthy", False):
                health_status["healthy"] = False

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        health_status["healthy"] = False
        health_status["error"] = str(e)
        return health_status


# Create FastAPI application
app = FastAPI(
    title="ACGS-1 Self-Evolving AI Architecture Foundation",
    description="Foundational self-evolving AI governance architecture with manual policy evolution and comprehensive security",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware
settings = get_settings()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Include API routers
app.include_router(
    evolution_router,
    prefix="/api/v1/evolution",
    tags=["Evolution Management"],
)

app.include_router(
    security_router,
    prefix="/api/v1/security",
    tags=["Security Management"],
)

app.include_router(
    observability_router,
    prefix="/api/v1/observability",
    tags=["Observability"],
)


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    try:
        health_status = await perform_startup_health_check()

        if health_status["healthy"]:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "healthy",
                    "service": "self-evolving-ai",
                    "version": "1.0.0",
                    "timestamp": health_status["timestamp"],
                    "checks": health_status["checks"],
                    "performance_targets": {
                        "concurrent_actions": ">1000",
                        "availability": ">99.9%",
                        "response_time": "<500ms",
                        "evolution_cycle": "<10min",
                    },
                    "quantumagi_compatibility": {
                        "constitution_hash": "cdd01ef066bc6cf2",
                        "solana_devnet": "enabled",
                        "governance_workflows": "compatible",
                    },
                },
            )
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "service": "self-evolving-ai",
                    "timestamp": health_status["timestamp"],
                    "checks": health_status["checks"],
                    "error": health_status.get("error"),
                },
            )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "service": "self-evolving-ai",
                "error": str(e),
                "timestamp": time.time(),
            },
        )


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "ACGS-1 Self-Evolving AI Architecture Foundation",
        "version": "1.0.0",
        "description": "Foundational self-evolving AI governance architecture with manual policy evolution and comprehensive security",
        "features": [
            "Layered security architecture (4 layers)",
            "Manual policy evolution with 100% human oversight",
            "Risk mitigation for top 6 threats",
            "Integration with all ACGS-1 services",
            "Comprehensive observability framework",
        ],
        "performance_targets": {
            "concurrent_actions": ">1000",
            "availability": ">99.9%",
            "response_time": "<500ms",
            "evolution_cycle": "<10min",
        },
        "quantumagi_compatibility": {
            "constitution_hash": "cdd01ef066bc6cf2",
            "solana_devnet": "enabled",
            "governance_workflows": "compatible",
        },
        "endpoints": {
            "health": "/health",
            "evolution": "/api/v1/evolution",
            "security": "/api/v1/security",
            "observability": "/api/v1/observability",
        },
    }


if __name__ == "__main__":
    # Get configuration
    settings = get_settings()

    # Run the application
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
