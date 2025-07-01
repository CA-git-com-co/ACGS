#!/usr/bin/env python3
"""
Enterprise High Availability Manager for ACGS-1
Implements intelligent routing, circuit breakers, auto failover, and service discovery
Target: >99.9% uptime, <500ms response times for 95% of requests
"""

import asyncio
import hashlib
import json
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service health status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"


class RoutingStrategy(Enum):
    """Load balancing routing strategies"""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    CONSISTENT_HASH = "consistent_hash"
    RESPONSE_TIME_BASED = "response_time_based"
    RESOURCE_BASED = "resource_based"


@dataclass
class ServiceInstance:
    """Service instance configuration"""

    id: str
    host: str
    port: int
    weight: int = 100
    max_connections: int = 1000
    current_connections: int = 0
    avg_response_time: float = 0.0
    status: ServiceStatus = ServiceStatus.HEALTHY
    last_health_check: datetime = field(default_factory=datetime.now)
    failure_count: int = 0
    circuit_breaker_open: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ServicePool:
    """Pool of service instances"""

    name: str
    instances: list[ServiceInstance] = field(default_factory=list)
    routing_strategy: RoutingStrategy = RoutingStrategy.LEAST_CONNECTIONS
    health_check_interval: int = 10
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    session_affinity: bool = False
    sticky_sessions: dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    uptime_percentage: float = 100.0
    last_updated: datetime = field(default_factory=datetime.now)


class EnterpriseHAManager:
    """
    Enterprise High Availability Manager
    Provides intelligent routing, circuit breakers, auto failover, and service discovery
    """

    def __init__(self):
        self.service_pools: dict[str, ServicePool] = {}
        self.performance_metrics: dict[str, PerformanceMetrics] = {}
        self.response_time_history: dict[str, list[float]] = {}
        self.health_check_tasks: dict[str, asyncio.Task] = {}
        self.running = False

        # Initialize ACGS service pools
        self._initialize_acgs_services()

    def _initialize_acgs_services(self):
        """Initialize ACGS service pools with enterprise configuration"""
        acgs_services = [
            ("auth_service", 8000, 2),
            ("ac_service", 8001, 2),
            ("integrity_service", 8002, 2),
            ("fv_service", 8003, 2),
            ("gs_service", 8004, 3),  # Higher capacity for LLM operations
            ("pgc_service", 8005, 2),
            ("ec_service", 8006, 2),
        ]

        for service_name, base_port, instance_count in acgs_services:
            instances = []
            for i in range(instance_count):
                instance = ServiceInstance(
                    id=f"{service_name}_{i + 1}",
                    host=f"{service_name}_{i + 1}" if i > 0 else service_name,
                    port=base_port,
                    weight=100 if i == 0 else 80,  # Primary instance gets higher weight
                    max_connections=1000,
                )
                instances.append(instance)

            # Special configuration for GS service (LLM operations)
            routing_strategy = (
                RoutingStrategy.RESPONSE_TIME_BASED
                if service_name == "gs_service"
                else RoutingStrategy.LEAST_CONNECTIONS
            )

            pool = ServicePool(
                name=service_name,
                instances=instances,
                routing_strategy=routing_strategy,
                health_check_interval=10,
                circuit_breaker_threshold=5,
                circuit_breaker_timeout=60,
                session_affinity=(service_name in ["auth_service", "ac_service"]),
            )

            self.service_pools[service_name] = pool
            self.performance_metrics[service_name] = PerformanceMetrics()
            self.response_time_history[service_name] = []

    async def start(self):
        """Start the HA manager and health checking"""
        if self.running:
            return

        self.running = True
        logger.info("Starting Enterprise HA Manager")

        # Start health check tasks for each service pool
        for service_name, _pool in self.service_pools.items():
            task = asyncio.create_task(self._health_check_loop(service_name))
            self.health_check_tasks[service_name] = task

        # Start metrics collection task
        asyncio.create_task(self._metrics_collection_loop())

        logger.info("Enterprise HA Manager started successfully")

    async def stop(self):
        """Stop the HA manager"""
        if not self.running:
            return

        self.running = False
        logger.info("Stopping Enterprise HA Manager")

        # Cancel all health check tasks
        for task in self.health_check_tasks.values():
            task.cancel()

        await asyncio.gather(*self.health_check_tasks.values(), return_exceptions=True)
        self.health_check_tasks.clear()

        logger.info("Enterprise HA Manager stopped")

    async def get_service_instance(
        self, service_name: str, session_id: str | None = None
    ) -> ServiceInstance | None:
        """
        Get the best available service instance using intelligent routing
        """
        pool = self.service_pools.get(service_name)
        if not pool:
            logger.error(f"Service pool {service_name} not found")
            return None

        # Check for session affinity
        if pool.session_affinity and session_id:
            if session_id in pool.sticky_sessions:
                instance_id = pool.sticky_sessions[session_id]
                instance = next(
                    (i for i in pool.instances if i.id == instance_id), None
                )
                if (
                    instance
                    and instance.status == ServiceStatus.HEALTHY
                    and not instance.circuit_breaker_open
                ):
                    return instance

        # Get healthy instances
        healthy_instances = [
            i
            for i in pool.instances
            if i.status == ServiceStatus.HEALTHY and not i.circuit_breaker_open
        ]

        if not healthy_instances:
            # Try degraded instances as fallback
            healthy_instances = [
                i
                for i in pool.instances
                if i.status == ServiceStatus.DEGRADED and not i.circuit_breaker_open
            ]

        if not healthy_instances:
            logger.error(f"No healthy instances available for {service_name}")
            return None

        # Apply routing strategy
        selected_instance = await self._apply_routing_strategy(pool, healthy_instances)

        # Set session affinity if enabled
        if pool.session_affinity and session_id and selected_instance:
            pool.sticky_sessions[session_id] = selected_instance.id

        return selected_instance

    async def _apply_routing_strategy(
        self, pool: ServicePool, instances: list[ServiceInstance]
    ) -> ServiceInstance | None:
        """Apply the configured routing strategy"""
        if not instances:
            return None

        if pool.routing_strategy == RoutingStrategy.ROUND_ROBIN:
            return self._round_robin_selection(instances)
        if pool.routing_strategy == RoutingStrategy.LEAST_CONNECTIONS:
            return min(instances, key=lambda i: i.current_connections)
        if pool.routing_strategy == RoutingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(instances)
        if pool.routing_strategy == RoutingStrategy.CONSISTENT_HASH:
            return self._consistent_hash_selection(instances, pool.name)
        if pool.routing_strategy == RoutingStrategy.RESPONSE_TIME_BASED:
            return min(instances, key=lambda i: i.avg_response_time)
        if pool.routing_strategy == RoutingStrategy.RESOURCE_BASED:
            return self._resource_based_selection(instances)
        return instances[0]  # Default to first instance

    def _round_robin_selection(
        self, instances: list[ServiceInstance]
    ) -> ServiceInstance:
        """Simple round-robin selection"""
        if not hasattr(self, "_round_robin_counter"):
            self._round_robin_counter = {}

        pool_key = instances[0].id.split("_")[0]  # Extract service name
        counter = self._round_robin_counter.get(pool_key, 0)
        selected = instances[counter % len(instances)]
        self._round_robin_counter[pool_key] = counter + 1
        return selected

    def _weighted_round_robin_selection(
        self, instances: list[ServiceInstance]
    ) -> ServiceInstance:
        """Weighted round-robin selection based on instance weights"""
        total_weight = sum(i.weight for i in instances)
        if total_weight == 0:
            return instances[0]

        random_weight = random.randint(1, total_weight)
        current_weight = 0

        for instance in instances:
            current_weight += instance.weight
            if random_weight <= current_weight:
                return instance

        return instances[-1]  # Fallback

    def _consistent_hash_selection(
        self, instances: list[ServiceInstance], key: str
    ) -> ServiceInstance:
        """Consistent hash selection for session affinity"""
        hash_value = int(hashlib.sha256(key.encode()).hexdigest(), 16)
        return instances[hash_value % len(instances)]

    def _resource_based_selection(
        self, instances: list[ServiceInstance]
    ) -> ServiceInstance:
        """Resource-based selection considering connections and response time"""

        def score(instance: ServiceInstance) -> float:
            connection_ratio = instance.current_connections / instance.max_connections
            response_time_factor = min(
                instance.avg_response_time / 1000.0, 1.0
            )  # Normalize to 1s
            return connection_ratio * 0.6 + response_time_factor * 0.4

        return min(instances, key=score)

    async def _health_check_loop(self, service_name: str):
        """Continuous health checking for a service pool"""
        pool = self.service_pools[service_name]

        while self.running:
            try:
                for instance in pool.instances:
                    await self._check_instance_health(instance)

                await asyncio.sleep(pool.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error for {service_name}: {e}")
                await asyncio.sleep(5)  # Brief pause on error

    async def _check_instance_health(self, instance: ServiceInstance):
        """Check health of a single service instance"""
        try:
            # Simulate health check (replace with actual HTTP health check)
            start_time = time.time()

            # Mock health check - replace with actual implementation
            health_check_success = random.random() > 0.05  # 95% success rate

            response_time = (time.time() - start_time) * 1000  # Convert to ms

            if health_check_success:
                instance.status = ServiceStatus.HEALTHY
                instance.failure_count = 0
                instance.circuit_breaker_open = False
                instance.avg_response_time = (instance.avg_response_time * 0.8) + (
                    response_time * 0.2
                )
            else:
                instance.failure_count += 1
                if (
                    instance.failure_count
                    >= self.service_pools[
                        instance.id.split("_")[0]
                    ].circuit_breaker_threshold
                ):
                    instance.circuit_breaker_open = True
                    instance.status = ServiceStatus.UNHEALTHY
                    logger.warning(f"Circuit breaker opened for {instance.id}")

            instance.last_health_check = datetime.now()

        except Exception as e:
            logger.error(f"Health check failed for {instance.id}: {e}")
            instance.failure_count += 1
            instance.status = ServiceStatus.UNHEALTHY

    async def _metrics_collection_loop(self):
        """Collect and update performance metrics"""
        while self.running:
            try:
                for service_name, pool in self.service_pools.items():
                    metrics = self.performance_metrics[service_name]

                    # Calculate uptime percentage
                    healthy_instances = sum(
                        1 for i in pool.instances if i.status == ServiceStatus.HEALTHY
                    )
                    total_instances = len(pool.instances)
                    metrics.uptime_percentage = (
                        (healthy_instances / total_instances) * 100
                        if total_instances > 0
                        else 0
                    )

                    # Calculate average response time
                    response_times = self.response_time_history.get(service_name, [])
                    if response_times:
                        metrics.avg_response_time = sum(response_times) / len(
                            response_times
                        )
                        response_times.sort()
                        if (
                            len(response_times) >= 20
                        ):  # Need sufficient data for percentiles
                            metrics.p95_response_time = response_times[
                                int(len(response_times) * 0.95)
                            ]
                            metrics.p99_response_time = response_times[
                                int(len(response_times) * 0.99)
                            ]

                    metrics.last_updated = datetime.now()

                await asyncio.sleep(30)  # Update metrics every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(10)

    async def record_request_metrics(
        self, service_name: str, response_time: float, success: bool
    ):
        """Record request metrics for performance monitoring"""
        metrics = self.performance_metrics.get(service_name)
        if not metrics:
            return

        metrics.total_requests += 1
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1

        # Store response time for percentile calculations
        response_times = self.response_time_history.get(service_name, [])
        response_times.append(response_time)

        # Keep only last 1000 response times
        if len(response_times) > 1000:
            response_times = response_times[-1000:]

        self.response_time_history[service_name] = response_times

    async def get_service_status(self) -> dict[str, Any]:
        """Get comprehensive service status report"""
        status_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "healthy",
            "services": {},
            "summary": {
                "total_services": len(self.service_pools),
                "healthy_services": 0,
                "degraded_services": 0,
                "unhealthy_services": 0,
            },
        }

        for service_name, pool in self.service_pools.items():
            healthy_instances = sum(
                1 for i in pool.instances if i.status == ServiceStatus.HEALTHY
            )
            total_instances = len(pool.instances)

            service_health = "healthy"
            if healthy_instances == 0:
                service_health = "unhealthy"
                status_report["summary"]["unhealthy_services"] += 1
            elif healthy_instances < total_instances:
                service_health = "degraded"
                status_report["summary"]["degraded_services"] += 1
            else:
                status_report["summary"]["healthy_services"] += 1

            metrics = self.performance_metrics[service_name]

            status_report["services"][service_name] = {
                "health": service_health,
                "instances": {
                    "total": total_instances,
                    "healthy": healthy_instances,
                    "unhealthy": total_instances - healthy_instances,
                },
                "metrics": {
                    "uptime_percentage": metrics.uptime_percentage,
                    "avg_response_time": metrics.avg_response_time,
                    "p95_response_time": metrics.p95_response_time,
                    "total_requests": metrics.total_requests,
                    "success_rate": (
                        (metrics.successful_requests / metrics.total_requests * 100)
                        if metrics.total_requests > 0
                        else 100
                    ),
                },
                "routing_strategy": pool.routing_strategy.value,
                "session_affinity": pool.session_affinity,
            }

        # Determine overall health
        if status_report["summary"]["unhealthy_services"] > 0:
            status_report["overall_health"] = "unhealthy"
        elif status_report["summary"]["degraded_services"] > 0:
            status_report["overall_health"] = "degraded"

        return status_report


# Global HA manager instance
ha_manager = EnterpriseHAManager()


async def main():
    """Main function for testing the HA manager"""
    logger.info("Starting Enterprise HA Manager Test")

    await ha_manager.start()

    # Simulate some requests
    for _i in range(10):
        for service_name in ["auth_service", "ac_service", "gs_service"]:
            instance = await ha_manager.get_service_instance(service_name)
            if instance:
                # Simulate request processing
                response_time = random.uniform(50, 500)  # 50-500ms
                success = random.random() > 0.05  # 95% success rate

                await ha_manager.record_request_metrics(
                    service_name, response_time, success
                )
                logger.info(
                    f"Request to {instance.id}: {response_time:.1f}ms, Success: {success}"
                )

        await asyncio.sleep(1)

    # Get status report
    status = await ha_manager.get_service_status()
    logger.info(f"Service Status Report: {json.dumps(status, indent=2)}")

    await ha_manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
