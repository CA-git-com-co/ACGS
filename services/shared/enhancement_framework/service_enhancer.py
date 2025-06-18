"""
Main Service Enhancer for ACGS-1 Services

Orchestrates all enhancement components to create production-ready ACGS services.
Provides the main interface for applying the enhancement framework.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import FastAPI

from .service_template import ACGSServiceTemplate

logger = logging.getLogger(__name__)


class ACGSServiceEnhancer:
    """
    Main service enhancer that orchestrates all enhancement components.

    This is the primary interface for applying the ACGS-1 enhancement framework
    to any service. It provides a simple, consistent API for creating enhanced
    services with all optimizations applied.

    Usage:
        enhancer = ACGSServiceEnhancer("pgc_service", port=8005)
        app = await enhancer.create_enhanced_service()
    """

    def __init__(
        self,
        service_name: str,
        port: int,
        version: str = "3.0.0",
        description: Optional[str] = None,
    ):
        """
        Initialize the service enhancer.

        Args:
            service_name: Name of the service (e.g., "pgc_service")
            port: Port number for the service (e.g., 8005)
            version: Service version (default: "3.0.0")
            description: Service description (auto-generated if not provided)
        """
        self.service_name = service_name
        self.port = port
        self.version = version
        self.description = description

        # Create service template
        self.template = ACGSServiceTemplate(
            service_name=service_name,
            port=port,
            version=version,
            description=description,
        )

        # Enhancement components (accessible for advanced configuration)
        self.constitutional_validator = self.template.cache_enhancer
        self.performance_enhancer = self.template.performance_enhancer
        self.monitoring_integrator = self.template.monitoring_integrator
        self.cache_enhancer = self.template.cache_enhancer

        logger.info(f"ACGS Service Enhancer initialized for {service_name}")

    async def create_enhanced_service(self) -> FastAPI:
        """
        Create a fully enhanced FastAPI service with all optimizations applied.

        This method creates a production-ready service with:
        - Constitutional compliance validation (cdd01ef066bc6cf2)
        - Performance optimization (<500ms response times)
        - Prometheus metrics integration
        - Redis caching
        - Circuit breaker protection
        - Standardized middleware stack

        Returns:
            FastAPI application instance with all enhancements applied
        """
        logger.info(f"Creating enhanced service: {self.service_name}")

        # Create enhanced FastAPI application
        app = await self.template.create_enhanced_app()

        logger.info(f"✅ Enhanced service created: {self.service_name}")
        logger.info(f"🔧 Enhancements applied:")
        logger.info(
            f"   - Constitutional Validation: {self.template.enable_constitutional_validation}"
        )
        logger.info(
            f"   - Performance Optimization: {self.template.enable_performance_optimization}"
        )
        logger.info(f"   - Monitoring Integration: {self.template.enable_monitoring}")
        logger.info(f"   - Redis Caching: {self.template.enable_caching}")

        return app

    def configure_constitutional_compliance(
        self,
        enabled: bool = True,
        strict_mode: bool = True,
        bypass_paths: Optional[List[str]] = None,
        performance_target_ms: float = 5.0,
    ):
        """
        Configure constitutional compliance validation.

        Args:
            enabled: Enable/disable constitutional validation
            strict_mode: Enable strict validation mode
            bypass_paths: Additional paths to bypass validation
            performance_target_ms: Target validation time in milliseconds
        """
        self.template.configure_constitutional_validation(
            enabled=enabled,
            strict_mode=strict_mode,
            bypass_paths=bypass_paths,
        )

        logger.info(f"Constitutional compliance configured for {self.service_name}")

    def configure_performance_optimization(
        self,
        enabled: bool = True,
        response_time_target: float = 0.5,  # 500ms
        availability_target: float = 0.995,  # 99.5%
        circuit_breaker_threshold: int = 5,
    ):
        """
        Configure performance optimization settings.

        Args:
            enabled: Enable/disable performance optimization
            response_time_target: Target response time in seconds
            availability_target: Target availability percentage
            circuit_breaker_threshold: Circuit breaker failure threshold
        """
        self.template.configure_performance_optimization(
            enabled=enabled,
            response_time_target=response_time_target,
            availability_target=availability_target,
        )

        # Configure circuit breaker
        if enabled:
            self.performance_enhancer.circuit_breaker_threshold = (
                circuit_breaker_threshold
            )

        logger.info(f"Performance optimization configured for {self.service_name}")

    def configure_monitoring(
        self,
        enabled: bool = True,
        prometheus_enabled: bool = True,
        health_check_enabled: bool = True,
    ):
        """
        Configure monitoring and observability.

        Args:
            enabled: Enable/disable monitoring
            prometheus_enabled: Enable Prometheus metrics
            health_check_enabled: Enable health check endpoints
        """
        self.template.enable_monitoring = enabled

        logger.info(f"Monitoring configured for {self.service_name}")

    def configure_caching(
        self,
        enabled: bool = True,
        redis_url: str = "redis://localhost:6379/0",
        default_ttl: int = 300,  # 5 minutes
        constitutional_cache_ttl: int = 300,
    ):
        """
        Configure Redis caching integration.

        Args:
            enabled: Enable/disable caching
            redis_url: Redis connection URL
            default_ttl: Default cache TTL in seconds
            constitutional_cache_ttl: Constitutional validation cache TTL
        """
        self.template.configure_caching(
            enabled=enabled,
            redis_url=redis_url,
            default_ttl=default_ttl,
        )

        logger.info(f"Caching configured for {self.service_name}")

    def get_service_info(self) -> Dict[str, Any]:
        """
        Get comprehensive service information and configuration.

        Returns:
            Dictionary containing service configuration and status
        """
        return {
            "service_name": self.service_name,
            "port": self.port,
            "version": self.version,
            "description": self.description,
            "constitutional_hash": self.template.constitutional_hash,
            "enhancements": {
                "constitutional_validation": self.template.enable_constitutional_validation,
                "performance_optimization": self.template.enable_performance_optimization,
                "monitoring": self.template.enable_monitoring,
                "caching": self.template.enable_caching,
            },
            "performance_targets": self.performance_enhancer.performance_targets,
            "capabilities": [
                "Constitutional Compliance Validation (cdd01ef066bc6cf2)",
                "Performance Optimization (<500ms response times)",
                "Prometheus Metrics Integration",
                "Redis Caching with Fallback",
                "Circuit Breaker Protection",
                "Standardized Middleware Stack",
                "Health Check Endpoints",
                "Service Registry Integration",
            ],
        }

    async def validate_service_health(self) -> Dict[str, Any]:
        """
        Validate service health and return comprehensive status.

        Returns:
            Dictionary containing health status and metrics
        """
        health_status = {
            "service": self.service_name,
            "status": "healthy",
            "timestamp": time.time(),
            "enhancements_status": {},
        }

        # Check performance enhancer
        if self.template.enable_performance_optimization:
            perf_metrics = self.performance_enhancer.get_performance_metrics()
            health_status["enhancements_status"]["performance"] = {
                "enabled": True,
                "circuit_breaker_open": perf_metrics["circuit_breaker_open"],
                "availability": perf_metrics["availability"],
                "avg_response_time": perf_metrics["avg_response_time"],
            }

        # Check cache enhancer
        if self.template.enable_caching:
            cache_stats = self.cache_enhancer.get_cache_stats()
            health_status["enhancements_status"]["cache"] = {
                "enabled": True,
                "redis_available": cache_stats["redis_available"],
                "hit_rate": cache_stats["hit_rate"],
            }

        # Check monitoring
        if self.template.enable_monitoring:
            health_status["enhancements_status"]["monitoring"] = {
                "enabled": True,
                "prometheus_available": self.monitoring_integrator.metrics_enabled,
            }

        return health_status


# Convenience function for quick service creation
async def create_enhanced_acgs_service(
    service_name: str, port: int, version: str = "3.0.0", **kwargs
) -> FastAPI:
    """
    Convenience function to quickly create an enhanced ACGS service.

    Args:
        service_name: Name of the service
        port: Port number for the service
        version: Service version
        **kwargs: Additional configuration options

    Returns:
        Enhanced FastAPI application
    """
    enhancer = ACGSServiceEnhancer(service_name, port, version)

    # Apply any additional configuration
    if "constitutional_config" in kwargs:
        enhancer.configure_constitutional_compliance(**kwargs["constitutional_config"])

    if "performance_config" in kwargs:
        enhancer.configure_performance_optimization(**kwargs["performance_config"])

    if "monitoring_config" in kwargs:
        enhancer.configure_monitoring(**kwargs["monitoring_config"])

    if "cache_config" in kwargs:
        enhancer.configure_caching(**kwargs["cache_config"])

    return await enhancer.create_enhanced_service()
