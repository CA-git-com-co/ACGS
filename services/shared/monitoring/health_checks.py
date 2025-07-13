"""
Comprehensive Health Check System for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Production-grade health monitoring for all system components.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import psutil
from shared.performance.caching import get_cache_manager
from shared.performance.connection_pool import get_connection_pool_registry
from shared.resilience.circuit_breaker import get_circuit_breaker_registry

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check operation."""

    name: str
    status: HealthStatus
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "details": self.details,
            "error": self.error,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

    @property
    def is_healthy(self) -> bool:
        """Check if the health check passed."""
        return self.status == HealthStatus.HEALTHY


class HealthCheck(ABC):
    """Abstract base class for health checks."""

    def __init__(
        self,
        name: str,
        description: str | None = None,
        timeout: float = 30.0,
        critical: bool = False,
    ):
        self.name = name
        self.description = description or name
        self.timeout = timeout
        self.critical = critical
        self._last_result: HealthCheckResult | None = None
        self._check_count = 0
        self._failure_count = 0

    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """Perform the health check."""

    async def run_check(self) -> HealthCheckResult:
        """Run the health check with timeout and error handling."""
        start_time = time.time()
        self._check_count += 1

        try:
            # Run check with timeout
            result = await asyncio.wait_for(self.check(), timeout=self.timeout)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            result.duration_ms = duration_ms

            # Update failure count
            if not result.is_healthy:
                self._failure_count += 1

            self._last_result = result
            return result

        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            self._failure_count += 1

            result = HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {self.timeout}s",
                duration_ms=duration_ms,
                error="timeout",
            )

            self._last_result = result
            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._failure_count += 1

            logger.exception(f"Health check '{self.name}' failed: {e}")

            result = HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {e!s}",
                duration_ms=duration_ms,
                error=str(e),
            )

            self._last_result = result
            return result

    def get_stats(self) -> dict[str, Any]:
        """Get health check statistics."""
        failure_rate = self._failure_count / max(self._check_count, 1)

        return {
            "name": self.name,
            "description": self.description,
            "critical": self.critical,
            "check_count": self._check_count,
            "failure_count": self._failure_count,
            "failure_rate": failure_rate,
            "last_result": self._last_result.to_dict() if self._last_result else None,
        }


class SystemHealthCheck(HealthCheck):
    """Health check for system resources (CPU, memory, disk)."""

    def __init__(
        self,
        cpu_threshold: float = 90.0,
        memory_threshold: float = 90.0,
        disk_threshold: float = 90.0,
        **kwargs,
    ):
        super().__init__(
            "system_resources", "System CPU, memory, and disk usage", **kwargs
        )
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold

    async def check(self) -> HealthCheckResult:
        """Check system resource usage."""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Calculate usage percentages
            memory_percent = memory.percent
            disk_percent = disk.percent

            # Determine status
            issues = []
            status = HealthStatus.HEALTHY

            if cpu_percent > self.cpu_threshold:
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
                status = HealthStatus.UNHEALTHY
            elif cpu_percent > self.cpu_threshold * 0.8:
                issues.append(f"Elevated CPU usage: {cpu_percent:.1f}%")
                status = HealthStatus.DEGRADED

            if memory_percent > self.memory_threshold:
                issues.append(f"High memory usage: {memory_percent:.1f}%")
                status = HealthStatus.UNHEALTHY
            elif memory_percent > self.memory_threshold * 0.8:
                issues.append(f"Elevated memory usage: {memory_percent:.1f}%")
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.DEGRADED

            if disk_percent > self.disk_threshold:
                issues.append(f"High disk usage: {disk_percent:.1f}%")
                status = HealthStatus.UNHEALTHY
            elif disk_percent > self.disk_threshold * 0.8:
                issues.append(f"Elevated disk usage: {disk_percent:.1f}%")
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.DEGRADED

            message = "System resources healthy"
            if issues:
                message = "; ".join(issues)

            return HealthCheckResult(
                name=self.name,
                status=status,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "disk_percent": disk_percent,
                    "memory_total_gb": memory.total / (1024**3),
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_total_gb": disk.total / (1024**3),
                    "disk_free_gb": disk.free / (1024**3),
                },
            )

        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check system resources: {e}",
                error=str(e),
            )


class DatabaseHealthCheck(HealthCheck):
    """Health check for database connectivity and performance."""

    def __init__(self, pool_name: str, **kwargs):
        super().__init__(
            f"database_{pool_name}", f"Database connectivity for {pool_name}", **kwargs
        )
        self.pool_name = pool_name

    async def check(self) -> HealthCheckResult:
        """Check database health."""
        try:
            pool_registry = get_connection_pool_registry()
            pool = pool_registry.get_pool(self.pool_name)

            if not pool:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Database pool '{self.pool_name}' not found",
                    error="pool_not_found",
                )

            # Get pool status
            pool_status = await pool.get_pool_status()

            if pool_status.get("status") != "active":
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Database pool is not active: {pool_status.get('status')}",
                    details=pool_status,
                )

            # Check pool metrics
            metrics = pool_status.get("metrics", {})
            utilization = metrics.get("utilization_rate", 0)
            success_rate = metrics.get("success_rate", 1)

            status = HealthStatus.HEALTHY
            message = "Database connectivity healthy"

            if success_rate < 0.95:
                status = HealthStatus.UNHEALTHY
                message = f"Low database success rate: {success_rate:.2%}"
            elif success_rate < 0.99:
                status = HealthStatus.DEGRADED
                message = f"Reduced database success rate: {success_rate:.2%}"
            elif utilization > 0.9:
                status = HealthStatus.DEGRADED
                message = f"High database pool utilization: {utilization:.2%}"

            return HealthCheckResult(
                name=self.name, status=status, message=message, details=pool_status
            )

        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database health check failed: {e}",
                error=str(e),
            )


class CacheHealthCheck(HealthCheck):
    """Health check for cache connectivity and performance."""

    def __init__(self, cache_name: str | None = None, **kwargs):
        cache_label = cache_name or "default"
        super().__init__(
            f"cache_{cache_label}", f"Cache health for {cache_label}", **kwargs
        )
        self.cache_name = cache_name

    async def check(self) -> HealthCheckResult:
        """Check cache health."""
        try:
            cache_manager = get_cache_manager()
            cache = cache_manager.get_cache(self.cache_name)

            if not cache:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Cache '{self.cache_name or 'default'}' not found",
                    error="cache_not_found",
                )

            # Test cache operation
            test_key = f"health_check_{int(time.time())}"
            test_value = "health_check_value"

            # Set test value
            set_success = await cache.set(test_key, test_value, ttl=60)
            if not set_success:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message="Cache set operation failed",
                    error="set_failed",
                )

            # Get test value
            retrieved_value = await cache.get(test_key)
            if retrieved_value != test_value:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message="Cache get operation failed or value mismatch",
                    error="get_failed",
                )

            # Clean up test key
            await cache.delete(test_key)

            # Get cache statistics
            stats = await cache.get_stats()
            hit_rate = stats.get("hit_rate", 0)

            status = HealthStatus.HEALTHY
            message = "Cache connectivity healthy"

            if hit_rate < 0.5:
                status = HealthStatus.DEGRADED
                message = f"Low cache hit rate: {hit_rate:.2%}"

            return HealthCheckResult(
                name=self.name, status=status, message=message, details=stats
            )

        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Cache health check failed: {e}",
                error=str(e),
            )


class ExternalServiceHealthCheck(HealthCheck):
    """Health check for external service connectivity."""

    def __init__(self, service_name: str, check_function: Callable, **kwargs):
        super().__init__(
            f"external_{service_name}", f"External service {service_name}", **kwargs
        )
        self.service_name = service_name
        self.check_function = check_function

    async def check(self) -> HealthCheckResult:
        """Check external service health."""
        try:
            result = await self.check_function()

            if isinstance(result, bool):
                if result:
                    return HealthCheckResult(
                        name=self.name,
                        status=HealthStatus.HEALTHY,
                        message=f"External service {self.service_name} is healthy",
                    )
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"External service {self.service_name} is unhealthy",
                )

            if isinstance(result, dict):
                status = result.get("status", HealthStatus.UNKNOWN)
                message = result.get(
                    "message", f"External service {self.service_name} status: {status}"
                )
                details = result.get("details", {})

                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus(status) if isinstance(status, str) else status,
                    message=message,
                    details=details,
                )

            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message=f"External service {self.service_name} responded",
                details={"response": str(result)},
            )

        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"External service {self.service_name} check failed: {e}",
                error=str(e),
            )


class CircuitBreakerHealthCheck(HealthCheck):
    """Health check for circuit breaker status."""

    def __init__(self, **kwargs):
        super().__init__("circuit_breakers", "Circuit breaker status", **kwargs)

    async def check(self) -> HealthCheckResult:
        """Check circuit breaker health."""
        try:
            cb_registry = get_circuit_breaker_registry()
            cb_health = await cb_registry.health_check()

            status_map = {
                "healthy": HealthStatus.HEALTHY,
                "degraded": HealthStatus.DEGRADED,
                "unhealthy": HealthStatus.UNHEALTHY,
            }

            status = status_map.get(cb_health["status"], HealthStatus.UNKNOWN)

            open_breakers = cb_health["open_breakers"]
            total_breakers = cb_health["total_breakers"]

            if open_breakers == 0:
                message = f"All {total_breakers} circuit breakers are closed"
            else:
                message = f"{open_breakers}/{total_breakers} circuit breakers are open"

            return HealthCheckResult(
                name=self.name, status=status, message=message, details=cb_health
            )

        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Circuit breaker health check failed: {e}",
                error=str(e),
            )


class HealthCheckRegistry:
    """Registry for managing and executing health checks."""

    def __init__(self):
        self._health_checks: list[HealthCheck] = []
        self._last_run: datetime | None = None
        self._last_results: list[HealthCheckResult] = []

    def register(self, health_check: HealthCheck) -> None:
        """Register a health check."""
        self._health_checks.append(health_check)
        logger.info(f"Registered health check: {health_check.name}")

    async def run_all_checks(self, parallel: bool = True) -> list[HealthCheckResult]:
        """Run all registered health checks."""
        if not self._health_checks:
            return []

        self._last_run = datetime.utcnow()

        if parallel:
            # Run all checks in parallel
            tasks = [check.run_check() for check in self._health_checks]
            self._last_results = await asyncio.gather(*tasks, return_exceptions=False)
        else:
            # Run checks sequentially
            self._last_results = []
            for check in self._health_checks:
                result = await check.run_check()
                self._last_results.append(result)

        return self._last_results

    async def get_overall_health(self) -> dict[str, Any]:
        """Get overall system health status."""
        if not self._last_results:
            await self.run_all_checks()

        if not self._last_results:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": "No health checks configured",
                "timestamp": datetime.utcnow().isoformat(),
                "constitutional_hash": "cdd01ef066bc6cf2",
            }

        # Categorize results
        healthy_count = sum(
            1 for r in self._last_results if r.status == HealthStatus.HEALTHY
        )
        degraded_count = sum(
            1 for r in self._last_results if r.status == HealthStatus.DEGRADED
        )
        unhealthy_count = sum(
            1 for r in self._last_results if r.status == HealthStatus.UNHEALTHY
        )
        unknown_count = sum(
            1 for r in self._last_results if r.status == HealthStatus.UNKNOWN
        )

        total_checks = len(self._last_results)

        # Determine overall status
        if unhealthy_count > 0:
            # Check if any critical checks failed
            critical_failures = [
                r
                for r in self._last_results
                if r.status == HealthStatus.UNHEALTHY
                and any(hc.critical for hc in self._health_checks if hc.name == r.name)
            ]

            if critical_failures:
                overall_status = HealthStatus.UNHEALTHY
                message = f"Critical health checks failed: {len(critical_failures)}"
            else:
                overall_status = HealthStatus.DEGRADED
                message = f"Non-critical health checks failed: {unhealthy_count}"
        elif degraded_count > 0:
            overall_status = HealthStatus.DEGRADED
            message = f"Some health checks degraded: {degraded_count}"
        elif unknown_count > 0:
            overall_status = HealthStatus.UNKNOWN
            message = f"Some health checks status unknown: {unknown_count}"
        else:
            overall_status = HealthStatus.HEALTHY
            message = "All health checks passed"

        return {
            "status": overall_status.value,
            "message": message,
            "timestamp": self._last_run.isoformat() if self._last_run else None,
            "summary": {
                "total_checks": total_checks,
                "healthy": healthy_count,
                "degraded": degraded_count,
                "unhealthy": unhealthy_count,
                "unknown": unknown_count,
            },
            "checks": [result.to_dict() for result in self._last_results],
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

    def get_health_check_stats(self) -> dict[str, Any]:
        """Get statistics for all health checks."""
        return {
            "total_checks": len(self._health_checks),
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "checks": [check.get_stats() for check in self._health_checks],
        }


# Global health check registry
_health_registry = HealthCheckRegistry()


def get_health_registry() -> HealthCheckRegistry:
    """Get the global health check registry."""
    return _health_registry


def setup_default_health_checks(
    database_pools: list[str] | None = None,
    cache_names: list[str] | None = None,
    external_services: dict[str, Callable] | None = None,
) -> None:
    """Set up default health checks for common components."""
    registry = get_health_registry()

    # System resources check
    registry.register(SystemHealthCheck(critical=True))

    # Circuit breaker check
    registry.register(CircuitBreakerHealthCheck())

    # Database checks
    if database_pools:
        for pool_name in database_pools:
            registry.register(DatabaseHealthCheck(pool_name, critical=True))

    # Cache checks
    if cache_names:
        for cache_name in cache_names:
            registry.register(CacheHealthCheck(cache_name))

    # External service checks
    if external_services:
        for service_name, check_func in external_services.items():
            registry.register(ExternalServiceHealthCheck(service_name, check_func))

    logger.info("Default health checks configured")
