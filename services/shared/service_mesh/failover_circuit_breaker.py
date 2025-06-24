"""
Enhanced Circuit Breaker with Automatic Failover for ACGS-1 Load Balancing
Provides intelligent failover capabilities with service degradation handling
"""

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from services.shared.service_mesh.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerState,
)

from .common_types import ServiceInstance, ServiceType

logger = logging.getLogger(__name__)


class FailoverStrategy(Enum):
    """Failover strategies for service instances."""

    IMMEDIATE = "immediate"  # Immediate failover to backup
    GRACEFUL = "graceful"  # Graceful degradation with retry
    CIRCUIT_BREAK = "circuit_break"  # Circuit breaker based
    LOAD_SHED = "load_shed"  # Load shedding with priority


@dataclass
class FailoverConfig:
    """Configuration for failover behavior."""

    strategy: FailoverStrategy = FailoverStrategy.GRACEFUL
    max_retries: int = 3
    retry_delay: float = 1.0
    backup_threshold: float = 0.8  # Use backup when primary at 80% capacity
    degradation_enabled: bool = True
    circuit_breaker_threshold: int = 5
    recovery_timeout: float = 60.0


class FailoverCircuitBreaker:
    """
    Enhanced circuit breaker with automatic failover capabilities.

    Integrates with load balancing to provide intelligent failover
    and service degradation for high availability.
    """

    def __init__(self, service_type: ServiceType, config: FailoverConfig | None = None):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Initialize failover circuit breaker.

        Args:
            service_type: Type of service this breaker protects
            config: Failover configuration
        """
        self.service_type = service_type
        self.config = config or FailoverConfig()

        # Circuit breaker for each instance
        self.instance_breakers: dict[str, CircuitBreaker] = {}

        # Failover state
        self.primary_instances: list[str] = []
        self.backup_instances: list[str] = []
        self.degraded_mode: bool = False

        # Metrics
        self.failover_count: int = 0
        self.last_failover: float | None = None
        self.recovery_attempts: int = 0

        # Callbacks
        self.failover_callbacks: list[Callable[[str, str], None]] = []
        self.recovery_callbacks: list[Callable[[str], None]] = []

    def register_instances(self, instances: list[ServiceInstance]):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Register service instances with the circuit breaker.

        Args:
            instances: List of service instances to register
        """
        # Clear existing state
        self.instance_breakers.clear()
        self.primary_instances.clear()
        self.backup_instances.clear()

        # Categorize instances by priority
        for instance in instances:
            instance_id = instance.instance_id

            # Create circuit breaker for instance
            self.instance_breakers[instance_id] = CircuitBreaker(
                threshold=self.config.circuit_breaker_threshold,
                timeout=self.config.recovery_timeout,
            )

            # Categorize by priority (lower number = higher priority)
            if instance.priority <= 1:
                self.primary_instances.append(instance_id)
            else:
                self.backup_instances.append(instance_id)

        logger.info(
            f"Registered {len(self.primary_instances)} primary and "
            f"{len(self.backup_instances)} backup instances for {self.service_type.value}"
        )

    async def execute_with_failover(
        self, operation: Callable, instance_id: str, *args, **kwargs
    ) -> Any:
        """
        Execute operation with automatic failover.

        Args:
            operation: Async operation to execute
            instance_id: Target instance ID
            *args: Operation arguments
            **kwargs: Operation keyword arguments

        Returns:
            Operation result

        Raises:
            Exception: If all failover attempts fail
        """
        breaker = self.instance_breakers.get(instance_id)
        if not breaker:
            raise ValueError(f"Instance {instance_id} not registered")

        # Try primary instance first
        try:
            async with breaker:
                result = await operation(*args, **kwargs)
                self._record_success(instance_id)
                return result

        except Exception as e:
            self._record_failure(instance_id)

            # Attempt failover based on strategy
            if self.config.strategy == FailoverStrategy.IMMEDIATE:
                return await self._immediate_failover(operation, instance_id, *args, **kwargs)
            elif self.config.strategy == FailoverStrategy.GRACEFUL:
                return await self._graceful_failover(operation, instance_id, *args, **kwargs)
            elif self.config.strategy == FailoverStrategy.CIRCUIT_BREAK:
                return await self._circuit_break_failover(operation, instance_id, *args, **kwargs)
            elif self.config.strategy == FailoverStrategy.LOAD_SHED:
                return await self._load_shed_failover(operation, instance_id, *args, **kwargs)
            else:
                raise e

    async def _immediate_failover(
        self, operation: Callable, failed_instance: str, *args, **kwargs
    ) -> Any:
        """Immediate failover to backup instance."""
        backup_instances = self._get_available_backups(failed_instance)

        if not backup_instances:
            raise Exception(f"No backup instances available for {self.service_type.value}")

        # Try first available backup
        backup_id = backup_instances[0]
        backup_breaker = self.instance_breakers[backup_id]

        try:
            async with backup_breaker:
                result = await operation(*args, **kwargs)
                self._notify_failover(failed_instance, backup_id)
                return result
        except Exception as e:
            logger.error(f"Backup instance {backup_id} also failed: {e}")
            raise

    async def _graceful_failover(
        self, operation: Callable, failed_instance: str, *args, **kwargs
    ) -> Any:
        """Graceful failover with retries and degradation."""
        # Try retries on primary first
        for attempt in range(self.config.max_retries):
            try:
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                breaker = self.instance_breakers[failed_instance]

                if breaker.state != CircuitBreakerState.OPEN:
                    async with breaker:
                        result = await operation(*args, **kwargs)
                        self._record_success(failed_instance)
                        return result
            except Exception:
                continue

        # If retries failed, try backup instances
        backup_instances = self._get_available_backups(failed_instance)

        for backup_id in backup_instances:
            try:
                backup_breaker = self.instance_breakers[backup_id]
                async with backup_breaker:
                    result = await operation(*args, **kwargs)
                    self._notify_failover(failed_instance, backup_id)
                    return result
            except Exception:
                continue

        # Enable degraded mode if configured
        if self.config.degradation_enabled:
            self.degraded_mode = True
            logger.warning(f"Entering degraded mode for {self.service_type.value}")
            return await self._degraded_operation(operation, *args, **kwargs)

        raise Exception(f"All failover attempts failed for {self.service_type.value}")

    async def _circuit_break_failover(
        self, operation: Callable, failed_instance: str, *args, **kwargs
    ) -> Any:
        """Circuit breaker based failover."""
        breaker = self.instance_breakers[failed_instance]

        if breaker.state == CircuitBreakerState.OPEN:
            # Circuit is open, immediately try backup
            return await self._immediate_failover(operation, failed_instance, *args, **kwargs)
        else:
            # Circuit is closed or half-open, allow normal retry logic
            return await self._graceful_failover(operation, failed_instance, *args, **kwargs)

    async def _load_shed_failover(
        self, operation: Callable, failed_instance: str, *args, **kwargs
    ) -> Any:
        """Load shedding based failover."""
        # Check if we should shed this request based on system load
        if self._should_shed_load():
            raise Exception("Request shed due to high system load")

        # Otherwise, proceed with graceful failover
        return await self._graceful_failover(operation, failed_instance, *args, **kwargs)

    async def _degraded_operation(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute operation in degraded mode.

        This could return cached results, simplified responses,
        or trigger alternative workflows.
        """
        # For now, return a degraded response
        # In a real implementation, this would return cached data or simplified results
        logger.warning(f"Returning degraded response for {self.service_type.value}")
        return {"status": "degraded", "message": "Service operating in degraded mode"}

    def _get_available_backups(self, failed_instance: str) -> list[str]:
        """Get list of available backup instances."""
        available_backups = []

        for instance_id in self.backup_instances:
            if instance_id != failed_instance:
                breaker = self.instance_breakers.get(instance_id)
                if breaker and breaker.state != CircuitBreakerState.OPEN:
                    available_backups.append(instance_id)

        return available_backups

    def _should_shed_load(self) -> bool:
        """Determine if load should be shed."""
        # Simple load shedding logic based on circuit breaker states
        open_breakers = sum(
            1
            for breaker in self.instance_breakers.values()
            if breaker.state == CircuitBreakerState.OPEN
        )

        total_breakers = len(self.instance_breakers)
        if total_breakers == 0:
            return False

        # Shed load if more than 50% of instances are down
        failure_rate = open_breakers / total_breakers
        return failure_rate > 0.5

    def _record_success(self, instance_id: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record successful operation."""
        if self.degraded_mode:
            self.degraded_mode = False
            logger.info(f"Exiting degraded mode for {self.service_type.value}")

    def _record_failure(self, instance_id: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record failed operation."""
        logger.warning(f"Operation failed on instance {instance_id}")

    def _notify_failover(self, failed_instance: str, backup_instance: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Notify about failover event."""
        self.failover_count += 1
        self.last_failover = time.time()

        logger.warning(
            f"Failover from {failed_instance} to {backup_instance} "
            f"for {self.service_type.value}"
        )

        for callback in self.failover_callbacks:
            try:
                callback(failed_instance, backup_instance)
            except Exception as e:
                logger.error(f"Error in failover callback: {e}")

    def register_failover_callback(self, callback: Callable[[str, str], None]):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Register callback for failover events."""
        self.failover_callbacks.append(callback)

    def register_recovery_callback(self, callback: Callable[[str], None]):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Register callback for recovery events."""
        self.recovery_callbacks.append(callback)

    def get_status(self) -> dict[str, Any]:
        """Get failover circuit breaker status."""
        return {
            "service_type": self.service_type.value,
            "strategy": self.config.strategy.value,
            "degraded_mode": self.degraded_mode,
            "failover_count": self.failover_count,
            "last_failover": self.last_failover,
            "primary_instances": len(self.primary_instances),
            "backup_instances": len(self.backup_instances),
            "instance_states": {
                instance_id: breaker.get_status()
                for instance_id, breaker in self.instance_breakers.items()
            },
        }


class FailoverManager:
    """
    Manager for failover circuit breakers across all services.

    Provides centralized failover management and coordination
    for the entire ACGS-1 system.
    """

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize failover manager."""
        self.service_breakers: dict[ServiceType, FailoverCircuitBreaker] = {}
        self.global_degraded_mode: bool = False

    def get_failover_breaker(
        self, service_type: ServiceType, config: FailoverConfig | None = None
    ) -> FailoverCircuitBreaker:
        """
        Get or create failover circuit breaker for a service.

        Args:
            service_type: Type of service
            config: Failover configuration

        Returns:
            Failover circuit breaker instance
        """
        if service_type not in self.service_breakers:
            self.service_breakers[service_type] = FailoverCircuitBreaker(service_type, config)

        return self.service_breakers[service_type]

    def register_service_instances(
        self, service_type: ServiceType, instances: list[ServiceInstance]
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Register instances for a service type."""
        breaker = self.get_failover_breaker(service_type)
        breaker.register_instances(instances)

    def get_system_status(self) -> dict[str, Any]:
        """Get overall system failover status."""
        service_statuses = {}
        total_degraded = 0

        for service_type, breaker in self.service_breakers.items():
            status = breaker.get_status()
            service_statuses[service_type.value] = status

            if status["degraded_mode"]:
                total_degraded += 1

        return {
            "global_degraded_mode": self.global_degraded_mode,
            "services_in_degraded_mode": total_degraded,
            "total_services": len(self.service_breakers),
            "services": service_statuses,
        }


# Global failover manager
_failover_manager: FailoverManager | None = None


def get_failover_manager() -> FailoverManager:
    """Get the global failover manager."""
    global _failover_manager

    if _failover_manager is None:
        _failover_manager = FailoverManager()

    return _failover_manager
