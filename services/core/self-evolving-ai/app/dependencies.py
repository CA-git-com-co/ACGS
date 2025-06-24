"""
Dependencies for ACGS-1 Self-Evolving AI Architecture Foundation Service.

This module provides dependency injection for FastAPI endpoints,
ensuring proper initialization and access to core components.
"""

import logging

from fastapi import HTTPException

from .core.background_processor import BackgroundProcessor
from .core.evolution_engine import EvolutionEngine
from .core.observability_framework import ObservabilityFramework
from .core.policy_orchestrator import PolicyOrchestrator
from .core.security_manager import SecurityManager

logger = logging.getLogger(__name__)

# Global instances (initialized in main.py)
_evolution_engine: EvolutionEngine | None = None
_security_manager: SecurityManager | None = None
_policy_orchestrator: PolicyOrchestrator | None = None
_background_processor: BackgroundProcessor | None = None
_observability_framework: ObservabilityFramework | None = None


def set_evolution_engine(engine: EvolutionEngine):
    """Set the global evolution engine instance."""
    global _evolution_engine
    _evolution_engine = engine


def set_security_manager(manager: SecurityManager):
    """Set the global security manager instance."""
    global _security_manager
    _security_manager = manager


def set_policy_orchestrator(orchestrator: PolicyOrchestrator):
    """Set the global policy orchestrator instance."""
    global _policy_orchestrator
    _policy_orchestrator = orchestrator


def set_background_processor(processor: BackgroundProcessor):
    """Set the global background processor instance."""
    global _background_processor
    _background_processor = processor


def set_observability_framework(framework: ObservabilityFramework):
    """Set the global observability framework instance."""
    global _observability_framework
    _observability_framework = framework


async def get_evolution_engine() -> EvolutionEngine:
    """
    Dependency to get the evolution engine instance.

    Returns:
        EvolutionEngine instance

    Raises:
        HTTPException: If evolution engine is not initialized
    """
    if _evolution_engine is None:
        logger.error("Evolution engine not initialized")
        raise HTTPException(status_code=503, detail="Evolution engine service unavailable")
    return _evolution_engine


async def get_security_manager() -> SecurityManager:
    """
    Dependency to get the security manager instance.

    Returns:
        SecurityManager instance

    Raises:
        HTTPException: If security manager is not initialized
    """
    if _security_manager is None:
        logger.error("Security manager not initialized")
        raise HTTPException(status_code=503, detail="Security manager service unavailable")
    return _security_manager


async def get_policy_orchestrator() -> PolicyOrchestrator:
    """
    Dependency to get the policy orchestrator instance.

    Returns:
        PolicyOrchestrator instance

    Raises:
        HTTPException: If policy orchestrator is not initialized
    """
    if _policy_orchestrator is None:
        logger.error("Policy orchestrator not initialized")
        raise HTTPException(status_code=503, detail="Policy orchestrator service unavailable")
    return _policy_orchestrator


async def get_background_processor() -> BackgroundProcessor:
    """
    Dependency to get the background processor instance.

    Returns:
        BackgroundProcessor instance

    Raises:
        HTTPException: If background processor is not initialized
    """
    if _background_processor is None:
        logger.error("Background processor not initialized")
        raise HTTPException(status_code=503, detail="Background processor service unavailable")
    return _background_processor


async def get_observability_framework() -> ObservabilityFramework:
    """
    Dependency to get the observability framework instance.

    Returns:
        ObservabilityFramework instance

    Raises:
        HTTPException: If observability framework is not initialized
    """
    if _observability_framework is None:
        logger.error("Observability framework not initialized")
        raise HTTPException(status_code=503, detail="Observability framework service unavailable")
    return _observability_framework


# Health check dependencies
async def check_all_services_healthy() -> bool:
    """
    Check if all core services are healthy.

    Returns:
        True if all services are healthy, False otherwise
    """
    try:
        services_healthy = True

        # Check evolution engine
        if _evolution_engine:
            engine_health = await _evolution_engine.health_check()
            if not engine_health.get("healthy", False):
                services_healthy = False
                logger.warning("Evolution engine is unhealthy")
        else:
            services_healthy = False
            logger.warning("Evolution engine not initialized")

        # Check security manager
        if _security_manager:
            security_health = await _security_manager.health_check()
            if not security_health.get("healthy", False):
                services_healthy = False
                logger.warning("Security manager is unhealthy")
        else:
            services_healthy = False
            logger.warning("Security manager not initialized")

        # Check policy orchestrator
        if _policy_orchestrator:
            policy_health = await _policy_orchestrator.health_check()
            if not policy_health.get("healthy", False):
                services_healthy = False
                logger.warning("Policy orchestrator is unhealthy")
        else:
            services_healthy = False
            logger.warning("Policy orchestrator not initialized")

        # Check background processor
        if _background_processor:
            processor_health = await _background_processor.health_check()
            if not processor_health.get("healthy", False):
                services_healthy = False
                logger.warning("Background processor is unhealthy")
        else:
            services_healthy = False
            logger.warning("Background processor not initialized")

        # Check observability framework
        if _observability_framework:
            observability_health = await _observability_framework.health_check()
            if not observability_health.get("healthy", False):
                services_healthy = False
                logger.warning("Observability framework is unhealthy")
        else:
            services_healthy = False
            logger.warning("Observability framework not initialized")

        return services_healthy

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False


async def get_service_status() -> dict:
    """
    Get comprehensive status of all services.

    Returns:
        Dictionary with status information for all services
    """
    try:
        status = {
            "evolution_engine": {
                "initialized": _evolution_engine is not None,
                "healthy": False,
                "details": None,
            },
            "security_manager": {
                "initialized": _security_manager is not None,
                "healthy": False,
                "details": None,
            },
            "policy_orchestrator": {
                "initialized": _policy_orchestrator is not None,
                "healthy": False,
                "details": None,
            },
            "background_processor": {
                "initialized": _background_processor is not None,
                "healthy": False,
                "details": None,
            },
            "observability_framework": {
                "initialized": _observability_framework is not None,
                "healthy": False,
                "details": None,
            },
        }

        # Get detailed status for each service
        if _evolution_engine:
            engine_health = await _evolution_engine.health_check()
            status["evolution_engine"]["healthy"] = engine_health.get("healthy", False)
            status["evolution_engine"]["details"] = engine_health

        if _security_manager:
            security_health = await _security_manager.health_check()
            status["security_manager"]["healthy"] = security_health.get("healthy", False)
            status["security_manager"]["details"] = security_health

        if _policy_orchestrator:
            policy_health = await _policy_orchestrator.health_check()
            status["policy_orchestrator"]["healthy"] = policy_health.get("healthy", False)
            status["policy_orchestrator"]["details"] = policy_health

        if _background_processor:
            processor_health = await _background_processor.health_check()
            status["background_processor"]["healthy"] = processor_health.get("healthy", False)
            status["background_processor"]["details"] = processor_health

        if _observability_framework:
            observability_health = await _observability_framework.health_check()
            status["observability_framework"]["healthy"] = observability_health.get(
                "healthy", False
            )
            status["observability_framework"]["details"] = observability_health

        return status

    except Exception as e:
        logger.error(f"Get service status failed: {e}")
        return {"error": str(e)}


# Utility functions for service management
def are_all_services_initialized() -> bool:
    """Check if all core services are initialized."""
    return all(
        [
            _evolution_engine is not None,
            _security_manager is not None,
            _policy_orchestrator is not None,
            _background_processor is not None,
            _observability_framework is not None,
        ]
    )


def get_initialized_services() -> list[str]:
    """Get list of initialized service names."""
    initialized = []

    if _evolution_engine is not None:
        initialized.append("evolution_engine")
    if _security_manager is not None:
        initialized.append("security_manager")
    if _policy_orchestrator is not None:
        initialized.append("policy_orchestrator")
    if _background_processor is not None:
        initialized.append("background_processor")
    if _observability_framework is not None:
        initialized.append("observability_framework")

    return initialized


def get_uninitialized_services() -> list[str]:
    """Get list of uninitialized service names."""
    all_services = [
        "evolution_engine",
        "security_manager",
        "policy_orchestrator",
        "background_processor",
        "observability_framework",
    ]

    initialized = get_initialized_services()
    return [service for service in all_services if service not in initialized]
