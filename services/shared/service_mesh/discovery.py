"""
Service discovery for ACGS-PGP microservices.

Provides dynamic service discovery capabilities to eliminate hard-coded
service URLs and enable flexible deployment configurations.
"""

import asyncio
import logging
import time
from collections.abc import Callable
from typing import Any

import httpx

from services.shared.common.error_handling import ServiceUnavailableError
from services.shared.service_mesh.registry import get_service_registry

from .common_types import LoadBalancingStrategy, ServiceInstance, ServiceType

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
from .failover_circuit_breaker import FailoverConfig, FailoverManager
from .governance_session_manager import GovernanceSessionManager, GovernanceWorkflowType
from .infrastructure_integration import (
    InfrastructureIntegrationManager,
    get_infrastructure_manager,
)
from .load_balancer import LoadBalancer, SessionAffinityManager
from .performance_monitor import (
    PerformanceMetrics,
    PerformanceMonitor,
    get_performance_monitor,
)

logger = logging.getLogger(__name__)


class ServiceDiscovery:
    """
    Service discovery implementation for ACGS-PGP microservices.

    Provides dynamic service discovery, health monitoring, and
    advanced load balancing capabilities for high availability.
    """

    def __init__(
        self,
        health_check_interval: float = 30.0,
        default_strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_RESPONSE_TIME,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Initialize service discovery with load balancing.

        Args:
            health_check_interval: Interval between health checks (seconds)
            default_strategy: Default load balancing strategy
        """
        self.health_check_interval = health_check_interval
        self.default_strategy = default_strategy
        self.registry = get_service_registry()

        # Service instances by type
        self.instances: dict[ServiceType, list[ServiceInstance]] = {}

        # Load balancing components
        self.load_balancer = LoadBalancer(default_strategy)
        self.session_manager = SessionAffinityManager()
        self.failover_manager = FailoverManager()
        self.governance_session_manager = GovernanceSessionManager()
        self.infrastructure_manager: InfrastructureIntegrationManager | None = None
        self.performance_monitor: PerformanceMonitor | None = None

        # Health check state
        self._health_check_task: asyncio.Task | None = None
        self._running = False

        # Callbacks for service events
        self._service_up_callbacks: list[Callable[[ServiceInstance], None]] = []
        self._service_down_callbacks: list[Callable[[ServiceInstance], None]] = []

        # HTTP client for health checks
        self._http_client: httpx.AsyncClient | None = None

    async def start(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Start service discovery and health monitoring."""
        if self._running:
            return

        self._running = True
        self._http_client = httpx.AsyncClient(timeout=10.0)

        # Initialize service instances from registry
        await self._initialize_services()

        # Initialize failover circuit breakers
        await self._initialize_failover_breakers()

        # Start governance session manager
        await self.governance_session_manager.start()

        # Initialize infrastructure integration
        self.infrastructure_manager = await get_infrastructure_manager()

        # Initialize performance monitoring
        self.performance_monitor = await get_performance_monitor()

        # Start health check task
        self._health_check_task = asyncio.create_task(self._health_check_loop())

        logger.info("Service discovery started")

    async def stop(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Stop service discovery and health monitoring."""
        if not self._running:
            return

        self._running = False

        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        # Close HTTP client
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

        logger.info("Service discovery stopped")

    async def _initialize_services(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize service instances from registry."""
        for service_type in ServiceType:
            config = self.registry.get_service_config(service_type)
            if config:
                instance = ServiceInstance(
                    service_type=service_type,
                    instance_id=f"{service_type.value}-default",
                    base_url=config.base_url,
                    port=config.port,
                    health_url=config.health_url,
                    metadata={"source": "registry"},
                )

                if service_type not in self.instances:
                    self.instances[service_type] = []

                self.instances[service_type].append(instance)

        logger.info(
            "Initialized"
            f" {sum(len(instances) for instances in self.instances.values())} service"
            " instances"
        )

    async def _initialize_failover_breakers(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize failover circuit breakers for all services."""
        for service_type, instances in self.instances.items():
            if instances:
                # Register instances with failover manager
                self.failover_manager.register_service_instances(
                    service_type, instances
                )

                logger.info(
                    f"Initialized failover circuit breaker for {service_type.value}"
                )

    async def _health_check_loop(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Main health check loop."""
        while self._running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(5.0)  # Short delay before retrying

    async def _perform_health_checks(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Perform health checks on all service instances."""
        tasks = []

        for _service_type, instances in self.instances.items():
            for instance in instances:
                task = asyncio.create_task(self._check_instance_health(instance))
                tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_instance_health(self, instance: ServiceInstance):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Check health of a single service instance.

        Args:
            instance: Service instance to check
        """
        if not self._http_client:
            return

        start_time = time.time()
        old_status = instance.status

        try:
            response = await self._http_client.get(instance.health_url)
            response_time = time.time() - start_time

            if response.status_code == 200:
                instance.status = "healthy"
                instance.response_time = response_time

                # Notify if service came back up
                if old_status != "healthy":
                    self._notify_service_up(instance)

                # Record metrics in infrastructure manager
                if self.infrastructure_manager:
                    await self.infrastructure_manager.record_load_balancing_metrics(
                        instance.service_type, instance
                    )

                # Record performance metrics
                if self.performance_monitor:
                    await self._record_performance_metrics(instance)
            else:
                instance.status = "unhealthy"

                # Notify if service went down
                if old_status == "healthy":
                    self._notify_service_down(instance)

        except Exception as e:
            instance.status = "unhealthy"
            instance.response_time = None

            # Notify if service went down
            if old_status == "healthy":
                self._notify_service_down(instance)

            logger.debug(f"Health check failed for {instance.instance_id}: {e}")

        finally:
            instance.last_check = time.time()

    async def _record_performance_metrics(self, instance: ServiceInstance):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record performance metrics for monitoring."""
        if not self.performance_monitor:
            return

        # Calculate service-level metrics
        service_instances = self.instances.get(instance.service_type, [])
        healthy_instances = [inst for inst in service_instances if inst.is_healthy]

        # Calculate availability percentage
        availability = (len(healthy_instances) / max(len(service_instances), 1)) * 100

        # Calculate error rate
        total_requests = sum(inst.total_requests for inst in service_instances)
        failed_requests = sum(inst.failed_requests for inst in service_instances)
        error_rate = (failed_requests / max(total_requests, 1)) * 100

        # Calculate throughput (simplified)
        current_connections = sum(
            inst.current_connections for inst in service_instances
        )

        # Create performance metrics
        metrics = PerformanceMetrics(
            timestamp=time.time(),
            service_type=instance.service_type.value,
            instance_id=instance.instance_id,
            response_time_ms=instance.response_time or 0.0,
            availability_percent=availability,
            throughput_rps=0.0,  # Would need request rate calculation
            error_rate_percent=error_rate,
            concurrent_connections=current_connections,
            active_instances=len(service_instances),
            healthy_instances=len(healthy_instances),
            total_requests=total_requests,
            failed_requests=failed_requests,
        )

        # Record metrics
        self.performance_monitor.record_metrics(metrics)

    def _notify_service_up(self, instance: ServiceInstance):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Notify callbacks that a service came up."""
        logger.info(f"Service {instance.instance_id} is now healthy")

        for callback in self._service_up_callbacks:
            try:
                callback(instance)
            except Exception as e:
                logger.error(f"Error in service up callback: {e}")

    def _notify_service_down(self, instance: ServiceInstance):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Notify callbacks that a service went down."""
        logger.warning(f"Service {instance.instance_id} is now unhealthy")

        for callback in self._service_down_callbacks:
            try:
                callback(instance)
            except Exception as e:
                logger.error(f"Error in service down callback: {e}")

    def register_service_up_callback(self, callback: Callable[[ServiceInstance], None]):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Register callback for service up events."""
        self._service_up_callbacks.append(callback)

    def register_service_down_callback(
        self, callback: Callable[[ServiceInstance], None]
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Register callback for service down events."""
        self._service_down_callbacks.append(callback)

    def get_healthy_instances(self, service_type: ServiceType) -> list[ServiceInstance]:
        """
        Get all healthy instances of a service type.

        Args:
            service_type: Type of service to get instances for

        Returns:
            List of healthy service instances
        """
        instances = self.instances.get(service_type, [])
        return [instance for instance in instances if instance.is_healthy]

    def get_best_instance(
        self,
        service_type: ServiceType,
        strategy: LoadBalancingStrategy | None = None,
        session_id: str | None = None,
        hash_key: str | None = None,
    ) -> ServiceInstance | None:
        """
        Get the best available instance using load balancing strategy.

        Args:
            service_type: Type of service to get instance for
            strategy: Load balancing strategy to use
            session_id: Session ID for session affinity
            hash_key: Hash key for consistent hashing

        Returns:
            Best available service instance or None
        """
        instances = self.instances.get(service_type, [])

        # Use load balancer to select instance
        selected = self.load_balancer.select_instance(
            instances=instances,
            strategy=strategy,
            session_id=session_id,
            hash_key=hash_key,
        )

        if selected and session_id:
            # Set session affinity for governance workflow continuity
            self.session_manager.set_affinity(
                session_id, service_type, selected.instance_id
            )
            selected.increment_connections()

        return selected

    def get_service_url(self, service_type: ServiceType) -> str | None:
        """
        Get URL for the best available instance of a service.

        Args:
            service_type: Type of service to get URL for

        Returns:
            Service URL or None if no healthy instances
        """
        instance = self.get_best_instance(service_type)
        return instance.base_url if instance else None

    def is_service_available(self, service_type: ServiceType) -> bool:
        """
        Check if a service type has any healthy instances.

        Args:
            service_type: Type of service to check

        Returns:
            True if service has healthy instances
        """
        return len(self.get_healthy_instances(service_type)) > 0

    def get_service_status(self, service_type: ServiceType) -> dict[str, any]:
        """
        Get status information for a service type.

        Args:
            service_type: Type of service to get status for

        Returns:
            Service status information
        """
        instances = self.instances.get(service_type, [])
        healthy_instances = self.get_healthy_instances(service_type)

        if not instances:
            return {
                "service": service_type.value,
                "status": "not_found",
                "instances": 0,
                "healthy_instances": 0,
            }

        # Calculate average response time for healthy instances
        response_times = [
            instance.response_time
            for instance in healthy_instances
            if instance.response_time is not None
        ]
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else None
        )

        return {
            "service": service_type.value,
            "status": "available" if healthy_instances else "unavailable",
            "instances": len(instances),
            "healthy_instances": len(healthy_instances),
            "average_response_time": avg_response_time,
            "last_check": max(
                (instance.last_check for instance in instances if instance.last_check),
                default=None,
            ),
        }

    def get_all_services_status(self) -> dict[str, dict[str, any]]:
        """
        Get status information for all services.

        Returns:
            Status information for all service types
        """
        return {
            service_type.value: self.get_service_status(service_type)
            for service_type in ServiceType
        }

    def add_service_instance(self, instance: ServiceInstance):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Manually add a service instance.

        Args:
            instance: Service instance to add
        """
        if instance.service_type not in self.instances:
            self.instances[instance.service_type] = []

        # Check if instance already exists
        existing = next(
            (
                inst
                for inst in self.instances[instance.service_type]
                if inst.instance_id == instance.instance_id
            ),
            None,
        )

        if existing:
            # Update existing instance
            existing.base_url = instance.base_url
            existing.port = instance.port
            existing.health_url = instance.health_url
            existing.metadata.update(instance.metadata)
        else:
            # Add new instance
            self.instances[instance.service_type].append(instance)

        logger.info(f"Added service instance: {instance.instance_id}")

    def remove_service_instance(self, service_type: ServiceType, instance_id: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Remove a service instance.

        Args:
            service_type: Type of service
            instance_id: ID of instance to remove
        """
        if service_type in self.instances:
            self.instances[service_type] = [
                instance
                for instance in self.instances[service_type]
                if instance.instance_id != instance_id
            ]
            logger.info(f"Removed service instance: {instance_id}")

    def release_instance_connection(self, service_type: ServiceType, instance_id: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Release a connection from a service instance.

        Args:
            service_type: Type of service
            instance_id: ID of instance to release connection from
        """
        instances = self.instances.get(service_type, [])
        for instance in instances:
            if instance.instance_id == instance_id:
                instance.decrement_connections()
                break

    def record_instance_failure(self, service_type: ServiceType, instance_id: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Record a failure for a service instance.

        Args:
            service_type: Type of service
            instance_id: ID of instance that failed
        """
        instances = self.instances.get(service_type, [])
        for instance in instances:
            if instance.instance_id == instance_id:
                instance.record_failure()
                break

    def get_load_balancing_stats(self, service_type: ServiceType) -> dict[str, any]:
        """
        Get load balancing statistics for a service type.

        Args:
            service_type: Type of service

        Returns:
            Load balancing statistics
        """
        instances = self.instances.get(service_type, [])
        return self.load_balancer.get_load_balancing_stats(instances)

    def cleanup_expired_sessions(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Clean up expired session affinities."""
        self.session_manager.cleanup_expired_sessions()

    def get_session_stats(self) -> dict[str, any]:
        """Get session affinity statistics."""
        return self.session_manager.get_session_stats()

    def set_instance_weight(
        self, service_type: ServiceType, instance_id: str, weight: int
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Set weight for a service instance.

        Args:
            service_type: Type of service
            instance_id: ID of instance
            weight: New weight value
        """
        instances = self.instances.get(service_type, [])
        for instance in instances:
            if instance.instance_id == instance_id:
                instance.weight = weight
                logger.info(f"Updated weight for {instance_id} to {weight}")
                break

    async def execute_with_failover(
        self,
        service_type: ServiceType,
        operation: Callable,
        instance_id: str | None = None,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute operation with automatic failover.

        Args:
            service_type: Type of service
            operation: Async operation to execute
            instance_id: Specific instance ID (optional)
            *args: Operation arguments
            **kwargs: Operation keyword arguments

        Returns:
            Operation result
        """
        # Get failover circuit breaker for service
        failover_breaker = self.failover_manager.get_failover_breaker(service_type)

        # If no specific instance, select best available
        if not instance_id:
            instance = self.get_best_instance(service_type)
            if not instance:
                raise ServiceUnavailableError(
                    f"No healthy instances for {service_type.value}"
                )
            instance_id = instance.instance_id

        # Execute with failover protection
        return await failover_breaker.execute_with_failover(
            operation, instance_id, *args, **kwargs
        )

    def get_failover_status(self, service_type: ServiceType) -> dict[str, Any]:
        """Get failover status for a service type."""
        failover_breaker = self.failover_manager.get_failover_breaker(service_type)
        return failover_breaker.get_status()

    def get_system_failover_status(self) -> dict[str, Any]:
        """Get overall system failover status."""
        return self.failover_manager.get_system_status()

    def configure_failover(self, service_type: ServiceType, config: FailoverConfig):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Configure failover settings for a service type."""
        failover_breaker = self.failover_manager.get_failover_breaker(
            service_type, config
        )

        # Re-register instances with new configuration
        instances = self.instances.get(service_type, [])
        if instances:
            failover_breaker.register_instances(instances)

    async def get_instance_for_governance_session(
        self,
        service_type: ServiceType,
        session_id: str,
        workflow_type: GovernanceWorkflowType,
        user_id: str,
    ) -> ServiceInstance | None:
        """
        Get service instance for governance workflow with session affinity.

        Args:
            service_type: Type of service
            session_id: Governance session ID
            workflow_type: Type of governance workflow
            user_id: User identifier

        Returns:
            Service instance with session affinity
        """
        # Check if session already has affinity for this service
        affinity_instance_id = (
            await self.governance_session_manager.get_service_affinity(
                session_id, service_type
            )
        )

        if affinity_instance_id:
            # Find the specific instance
            instances = self.instances.get(service_type, [])
            for instance in instances:
                if instance.instance_id == affinity_instance_id and instance.is_healthy:
                    return instance

        # No existing affinity or instance unhealthy, select new instance
        instance = self.get_best_instance(
            service_type=service_type,
            strategy=LoadBalancingStrategy.CONSISTENT_HASH,
            session_id=session_id,
            hash_key=f"{session_id}:{workflow_type.value}",
        )

        if instance:
            # Set session affinity for governance workflow continuity
            await self.governance_session_manager.set_service_affinity(
                session_id, service_type, instance.instance_id
            )

        return instance

    async def create_governance_session(
        self,
        workflow_type: GovernanceWorkflowType,
        user_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Create a new governance session.

        Args:
            workflow_type: Type of governance workflow
            user_id: User identifier
            metadata: Optional session metadata

        Returns:
            Session ID
        """
        session = await self.governance_session_manager.create_session(
            workflow_type, user_id, metadata
        )
        return session.session_id

    async def advance_governance_workflow(
        self,
        session_id: str,
        step_name: str,
        step_data: dict[str, Any] | None = None,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Advance governance workflow to next step.

        Args:
            session_id: Session identifier
            step_name: Name of the next step
            step_data: Optional step data
        """
        await self.governance_session_manager.advance_workflow_step(
            session_id, step_name, step_data
        )

    async def complete_governance_session(self, session_id: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Complete governance session.

        Args:
            session_id: Session identifier
        """
        await self.governance_session_manager.complete_session(session_id)

    async def get_governance_session_stats(self) -> dict[str, Any]:
        """Get governance session statistics."""
        return await self.governance_session_manager.get_session_stats()


# Global service discovery instance
_service_discovery: ServiceDiscovery | None = None


async def get_service_discovery() -> ServiceDiscovery:
    """
    Get the global service discovery instance.

    Returns:
        Service discovery instance
    """
    global _service_discovery

    if _service_discovery is None:
        _service_discovery = ServiceDiscovery()
        await _service_discovery.start()

    return _service_discovery
