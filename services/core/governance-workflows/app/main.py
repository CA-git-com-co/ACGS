"""
ACGS-1 Advanced Governance Workflows Implementation

This service implements the 5 core governance workflows with enterprise-grade
capabilities, performance optimization, and comprehensive monitoring.

Core Workflows:
1. Policy Creation - Draft → Review → Voting → Implementation
2. Constitutional Compliance - Validation → Assessment → Enforcement
3. Policy Enforcement - Monitoring → Violation Detection → Remediation
4. WINA Oversight - Performance Monitoring → Optimization → Reporting
5. Audit/Transparency - Data Collection → Analysis → Public Reporting

Performance Targets:
- >1000 concurrent governance actions
- >99.9% availability
- <500ms response times for 95% requests
- >95% constitutional compliance accuracy
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

from .api.v1.audit_transparency import router as audit_transparency_router
from .api.v1.constitutional_compliance import router as constitutional_compliance_router

# Import API routers
from .api.v1.policy_creation import router as policy_creation_router
from .api.v1.policy_enforcement import router as policy_enforcement_router
from .api.v1.wina_oversight import router as wina_oversight_router

# Import configuration
from .config import get_settings
from .core.metrics_collector import MetricsCollector
from .core.performance_monitor import PerformanceMonitor
from .core.service_integrator import ServiceIntegrator

# Import core components
from .core.workflow_orchestrator import WorkflowOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/governance_workflows.log", mode="a"),
    ],
)

logger = logging.getLogger(__name__)

# Global service instances
workflow_orchestrator: WorkflowOrchestrator | None = None
performance_monitor: PerformanceMonitor | None = None
service_integrator: ServiceIntegrator | None = None
metrics_collector: MetricsCollector | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global workflow_orchestrator, performance_monitor, service_integrator, metrics_collector

    settings = get_settings()

    try:
        logger.info("🚀 Starting ACGS-1 Advanced Governance Workflows Service")

        # Initialize performance monitor first
        performance_monitor = PerformanceMonitor(settings)
        await performance_monitor.initialize()
        logger.info("✅ Performance monitor initialized")

        # Initialize service integrator
        service_integrator = ServiceIntegrator(settings)
        await service_integrator.initialize()
        logger.info("✅ Service integrator initialized")

        # Initialize metrics collector
        metrics_collector = MetricsCollector(settings)
        await metrics_collector.initialize()
        logger.info("✅ Metrics collector initialized")

        # Initialize workflow orchestrator
        workflow_orchestrator = WorkflowOrchestrator(
            settings=settings,
            performance_monitor=performance_monitor,
            service_integrator=service_integrator,
            metrics_collector=metrics_collector,
        )
        await workflow_orchestrator.initialize()
        logger.info("✅ Workflow orchestrator initialized")

        # Perform system health check
        health_status = await perform_startup_health_check()
        if not health_status["healthy"]:
            logger.error("❌ Startup health check failed")
            raise RuntimeError("Service startup health check failed")

        logger.info("🎯 Advanced Governance Workflows Service ready")
        logger.info(
            "📊 Performance targets: >1000 concurrent actions, >99.9% availability"
        )
        logger.info("🏛️ Quantumagi compatibility: Constitution Hash cdd01ef066bc6cf2")
        logger.info("🔄 5 core workflows operational")

        yield

    except Exception as e:
        logger.error(f"❌ Service startup failed: {e}")
        raise
    finally:
        # Cleanup on shutdown
        logger.info("🛑 Shutting down Advanced Governance Workflows Service")

        if workflow_orchestrator:
            await workflow_orchestrator.shutdown()
        if metrics_collector:
            await metrics_collector.shutdown()
        if service_integrator:
            await service_integrator.shutdown()
        if performance_monitor:
            await performance_monitor.shutdown()

        logger.info("✅ Service shutdown complete")


async def perform_startup_health_check() -> dict[str, Any]:
    """Perform comprehensive startup health check."""
    health_status = {
        "healthy": True,
        "timestamp": time.time(),
        "checks": {},
    }

    try:
        # Check workflow orchestrator
        if workflow_orchestrator:
            orchestrator_health = await workflow_orchestrator.health_check()
            health_status["checks"]["workflow_orchestrator"] = orchestrator_health
            if not orchestrator_health.get("healthy", False):
                health_status["healthy"] = False

        # Check performance monitor
        if performance_monitor:
            monitor_health = await performance_monitor.health_check()
            health_status["checks"]["performance_monitor"] = monitor_health
            if not monitor_health.get("healthy", False):
                health_status["healthy"] = False

        # Check service integrator
        if service_integrator:
            integrator_health = await service_integrator.health_check()
            health_status["checks"]["service_integrator"] = integrator_health
            if not integrator_health.get("healthy", False):
                health_status["healthy"] = False

        # Check metrics collector
        if metrics_collector:
            collector_health = await metrics_collector.health_check()
            health_status["checks"]["metrics_collector"] = collector_health
            if not collector_health.get("healthy", False):
                health_status["healthy"] = False

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        health_status["healthy"] = False
        health_status["error"] = str(e)
        return health_status


# Create FastAPI application
app = FastAPI(
    title="ACGS-1 Advanced Governance Workflows",
    description="Enterprise-grade governance workflows with performance optimization and comprehensive monitoring",
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
    policy_creation_router,
    prefix="/api/v1/workflows/policy-creation",
    tags=["Policy Creation"],
)

app.include_router(
    constitutional_compliance_router,
    prefix="/api/v1/workflows/constitutional-compliance",
    tags=["Constitutional Compliance"],
)

app.include_router(
    policy_enforcement_router,
    prefix="/api/v1/workflows/policy-enforcement",
    tags=["Policy Enforcement"],
)

app.include_router(
    wina_oversight_router,
    prefix="/api/v1/workflows/wina-oversight",
    tags=["WINA Oversight"],
)

app.include_router(
    audit_transparency_router,
    prefix="/api/v1/workflows/audit-transparency",
    tags=["Audit/Transparency"],
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
                    "service": "governance-workflows",
                    "version": "1.0.0",
                    "timestamp": health_status["timestamp"],
                    "checks": health_status["checks"],
                    "performance_targets": {
                        "concurrent_actions": ">1000",
                        "availability": ">99.9%",
                        "response_time": "<500ms",
                        "compliance_accuracy": ">95%",
                    },
                    "workflows": {
                        "policy_creation": "operational",
                        "constitutional_compliance": "operational",
                        "policy_enforcement": "operational",
                        "wina_oversight": "operational",
                        "audit_transparency": "operational",
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
                    "service": "governance-workflows",
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
                "service": "governance-workflows",
                "error": str(e),
                "timestamp": time.time(),
            },
        )


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "ACGS-1 Advanced Governance Workflows",
        "version": "1.0.0",
        "description": "Enterprise-grade governance workflows with performance optimization and comprehensive monitoring",
        "workflows": [
            "Policy Creation - Draft → Review → Voting → Implementation",
            "Constitutional Compliance - Validation → Assessment → Enforcement",
            "Policy Enforcement - Monitoring → Violation Detection → Remediation",
            "WINA Oversight - Performance Monitoring → Optimization → Reporting",
            "Audit/Transparency - Data Collection → Analysis → Public Reporting",
        ],
        "performance_targets": {
            "concurrent_actions": ">1000",
            "availability": ">99.9%",
            "response_time": "<500ms",
            "compliance_accuracy": ">95%",
        },
        "quantumagi_compatibility": {
            "constitution_hash": "cdd01ef066bc6cf2",
            "solana_devnet": "enabled",
            "governance_workflows": "compatible",
        },
        "endpoints": {
            "health": "/health",
            "policy_creation": "/api/v1/workflows/policy-creation",
            "constitutional_compliance": "/api/v1/workflows/constitutional-compliance",
            "policy_enforcement": "/api/v1/workflows/policy-enforcement",
            "wina_oversight": "/api/v1/workflows/wina-oversight",
            "audit_transparency": "/api/v1/workflows/audit-transparency",
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
