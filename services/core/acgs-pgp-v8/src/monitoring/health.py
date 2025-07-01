"""
Health Monitor for ACGS-PGP v8

Comprehensive health monitoring and alerting for all system components.
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Health check configuration."""

    name: str
    check_function: Callable
    interval_seconds: int
    timeout_seconds: int
    failure_threshold: int
    recovery_threshold: int
    enabled: bool = True


@dataclass
class HealthResult:
    """Health check result."""

    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    duration_ms: float
    details: dict[str, Any]


class HealthMonitor:
    """
    Comprehensive health monitor for ACGS-PGP v8 system.

    Provides continuous health monitoring, alerting, and recovery
    recommendations for all system components.
    """

    def __init__(self, constitutional_hash: str = "cdd01ef066bc6cf2"):
        """Initialize health monitor."""
        self.constitutional_hash = constitutional_hash
        self.health_checks: dict[str, HealthCheck] = {}
        self.health_results: dict[str, HealthResult] = {}
        self.failure_counts: dict[str, int] = {}
        self.recovery_counts: dict[str, int] = {}
        self.monitoring_tasks: dict[str, asyncio.Task] = {}
        self.is_monitoring = False

        # Health thresholds
        self.overall_health_threshold = 0.8  # 80% of checks must be healthy
        self.degraded_threshold = 0.6  # 60% of checks must be healthy for degraded

        # Alert callbacks
        self.alert_callbacks: list[Callable] = []

        logger.info("Health monitor initialized")

    def register_health_check(
        self,
        name: str,
        check_function: Callable,
        interval_seconds: int = 30,
        timeout_seconds: int = 10,
        failure_threshold: int = 3,
        recovery_threshold: int = 2,
    ):
        """Register a health check."""
        health_check = HealthCheck(
            name=name,
            check_function=check_function,
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds,
            failure_threshold=failure_threshold,
            recovery_threshold=recovery_threshold,
        )

        self.health_checks[name] = health_check
        self.failure_counts[name] = 0
        self.recovery_counts[name] = 0

        logger.info(f"Registered health check: {name}")

    def register_alert_callback(self, callback: Callable):
        """Register alert callback function."""
        self.alert_callbacks.append(callback)
        logger.info("Registered alert callback")

    async def start_monitoring(self):
        """Start continuous health monitoring."""
        if self.is_monitoring:
            logger.warning("Health monitoring already started")
            return

        self.is_monitoring = True
        logger.info("Starting health monitoring")

        # Start monitoring tasks for each health check
        for name, health_check in self.health_checks.items():
            if health_check.enabled:
                task = asyncio.create_task(self._monitor_health_check(name))
                self.monitoring_tasks[name] = task

        logger.info(f"Started {len(self.monitoring_tasks)} health monitoring tasks")

    async def stop_monitoring(self):
        """Stop health monitoring."""
        if not self.is_monitoring:
            return

        self.is_monitoring = False
        logger.info("Stopping health monitoring")

        # Cancel all monitoring tasks
        for task in self.monitoring_tasks.values():
            task.cancel()

        # Wait for tasks to complete
        if self.monitoring_tasks:
            await asyncio.gather(
                *self.monitoring_tasks.values(), return_exceptions=True
            )

        self.monitoring_tasks.clear()
        logger.info("Health monitoring stopped")

    async def _monitor_health_check(self, name: str):
        """Monitor a single health check continuously."""
        health_check = self.health_checks[name]

        while self.is_monitoring:
            try:
                # Perform health check
                result = await self._perform_health_check(name)

                # Update failure/recovery counts
                if result.status == HealthStatus.HEALTHY:
                    self.recovery_counts[name] += 1
                    if self.recovery_counts[name] >= health_check.recovery_threshold:
                        self.failure_counts[name] = 0
                        self.recovery_counts[name] = 0
                else:
                    self.failure_counts[name] += 1
                    self.recovery_counts[name] = 0

                # Check for alerts
                await self._check_alerts(name, result)

                # Wait for next check
                await asyncio.sleep(health_check.interval_seconds)

            except asyncio.CancelledError:
                logger.info(f"Health check monitoring cancelled: {name}")
                break
            except Exception as e:
                logger.error(f"Error in health check monitoring {name}: {e}")
                await asyncio.sleep(health_check.interval_seconds)

    async def _perform_health_check(self, name: str) -> HealthResult:
        """Perform a single health check."""
        health_check = self.health_checks[name]
        start_time = datetime.now()

        try:
            # Execute health check with timeout
            result = await asyncio.wait_for(
                health_check.check_function(), timeout=health_check.timeout_seconds
            )

            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            # Parse result
            if isinstance(result, dict):
                status_str = result.get("status", "unknown")
                message = result.get("message", "Health check completed")
                details = result.get("details", {})
            else:
                status_str = "healthy" if result else "unhealthy"
                message = "Health check completed"
                details = {}

            # Convert status string to enum
            try:
                status = HealthStatus(status_str.lower())
            except ValueError:
                status = HealthStatus.UNKNOWN

            health_result = HealthResult(
                name=name,
                status=status,
                message=message,
                timestamp=end_time,
                duration_ms=duration_ms,
                details=details,
            )

            self.health_results[name] = health_result
            return health_result

        except TimeoutError:
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            health_result = HealthResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {health_check.timeout_seconds}s",
                timestamp=end_time,
                duration_ms=duration_ms,
                details={"timeout": True},
            )

            self.health_results[name] = health_result
            return health_result

        except Exception as e:
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            health_result = HealthResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                timestamp=end_time,
                duration_ms=duration_ms,
                details={"error": str(e)},
            )

            self.health_results[name] = health_result
            return health_result

    async def _check_alerts(self, name: str, result: HealthResult):
        """Check if alerts should be triggered."""
        health_check = self.health_checks[name]
        failure_count = self.failure_counts[name]

        # Trigger alert if failure threshold reached
        if (
            result.status != HealthStatus.HEALTHY
            and failure_count >= health_check.failure_threshold
        ):

            alert_data = {
                "type": "health_check_failure",
                "component": name,
                "status": result.status.value,
                "message": result.message,
                "failure_count": failure_count,
                "timestamp": result.timestamp.isoformat(),
                "constitutional_hash": self.constitutional_hash,
            }

            await self._trigger_alerts(alert_data)

    async def _trigger_alerts(self, alert_data: dict[str, Any]):
        """Trigger registered alert callbacks."""
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert_data)
                else:
                    callback(alert_data)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

    async def get_overall_health(self) -> dict[str, Any]:
        """Get overall system health status."""
        if not self.health_results:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": "No health checks performed yet",
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now().isoformat(),
            }

        # Calculate health percentages
        total_checks = len(self.health_results)
        healthy_checks = sum(
            1
            for result in self.health_results.values()
            if result.status == HealthStatus.HEALTHY
        )

        health_percentage = healthy_checks / total_checks if total_checks > 0 else 0

        # Determine overall status
        if health_percentage >= self.overall_health_threshold:
            overall_status = HealthStatus.HEALTHY
            message = f"System healthy ({healthy_checks}/{total_checks} checks passing)"
        elif health_percentage >= self.degraded_threshold:
            overall_status = HealthStatus.DEGRADED
            message = (
                f"System degraded ({healthy_checks}/{total_checks} checks passing)"
            )
        else:
            overall_status = HealthStatus.UNHEALTHY
            message = (
                f"System unhealthy ({healthy_checks}/{total_checks} checks passing)"
            )

        return {
            "status": overall_status.value,
            "message": message,
            "health_percentage": health_percentage * 100,
            "healthy_checks": healthy_checks,
            "total_checks": total_checks,
            "constitutional_hash": self.constitutional_hash,
            "timestamp": datetime.now().isoformat(),
            "component_details": {
                name: {
                    "status": result.status.value,
                    "message": result.message,
                    "last_check": result.timestamp.isoformat(),
                    "duration_ms": result.duration_ms,
                }
                for name, result in self.health_results.items()
            },
        }

    async def get_component_health(self, component_name: str) -> dict[str, Any] | None:
        """Get health status for a specific component."""
        if component_name not in self.health_results:
            return None

        result = self.health_results[component_name]
        return {
            "name": component_name,
            "status": result.status.value,
            "message": result.message,
            "timestamp": result.timestamp.isoformat(),
            "duration_ms": result.duration_ms,
            "details": result.details,
            "failure_count": self.failure_counts.get(component_name, 0),
            "constitutional_hash": self.constitutional_hash,
        }

    async def perform_immediate_check(self, component_name: str) -> HealthResult | None:
        """Perform immediate health check for a component."""
        if component_name not in self.health_checks:
            return None

        return await self._perform_health_check(component_name)

    def get_health_summary(self) -> dict[str, Any]:
        """Get health monitoring summary."""
        return {
            "monitoring_active": self.is_monitoring,
            "registered_checks": len(self.health_checks),
            "active_monitoring_tasks": len(self.monitoring_tasks),
            "alert_callbacks": len(self.alert_callbacks),
            "constitutional_hash": self.constitutional_hash,
            "health_checks": {
                name: {
                    "enabled": check.enabled,
                    "interval_seconds": check.interval_seconds,
                    "timeout_seconds": check.timeout_seconds,
                    "failure_threshold": check.failure_threshold,
                    "current_failures": self.failure_counts.get(name, 0),
                }
                for name, check in self.health_checks.items()
            },
        }
