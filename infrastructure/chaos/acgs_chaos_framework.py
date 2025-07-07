#!/usr/bin/env python3
"""
ACGS Chaos Engineering Framework
Comprehensive chaos engineering and fault injection testing for ACGS microservices.
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import aiohttp
import docker
import psutil
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    start_http_server,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ChaosType(Enum):
    """Types of chaos experiments."""

    SERVICE_FAILURE = "service_failure"
    NETWORK_LATENCY = "network_latency"
    NETWORK_PARTITION = "network_partition"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DATABASE_FAILURE = "database_failure"
    MESSAGE_BROKER_FAILURE = "message_broker_failure"
    CONSTITUTIONAL_VALIDATION_FAILURE = "constitutional_validation_failure"
    DISK_FAILURE = "disk_failure"
    MEMORY_PRESSURE = "memory_pressure"
    CPU_STRESS = "cpu_stress"


class ExperimentStatus(Enum):
    """Experiment execution status."""

    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class ChaosExperiment:
    """Chaos experiment definition."""

    experiment_id: str
    name: str
    chaos_type: ChaosType
    target_services: list[str]

    # Experiment parameters
    duration_seconds: int = 300  # 5 minutes default
    intensity: float = 0.5  # 0.0 to 1.0

    # Conditions
    steady_state_hypothesis: dict[str, Any] = field(default_factory=dict)
    rollback_conditions: list[str] = field(default_factory=list)

    # Safety measures
    blast_radius: str = "single_service"  # single_service, service_group, system_wide
    max_impact_threshold: float = 0.1  # Max 10% impact on system performance

    # Execution metadata
    status: ExperimentStatus = ExperimentStatus.PLANNED
    start_time: datetime | None = None
    end_time: datetime | None = None
    results: dict[str, Any] = field(default_factory=dict)

    # Constitutional compliance
    constitutional_hash: str = CONSTITUTIONAL_HASH
    constitutional_compliance_required: bool = True


@dataclass
class SystemMetrics:
    """System metrics for chaos experiment monitoring."""

    timestamp: datetime

    # Service metrics
    service_response_times: dict[str, float] = field(default_factory=dict)
    service_error_rates: dict[str, float] = field(default_factory=dict)
    service_availability: dict[str, bool] = field(default_factory=dict)

    # Infrastructure metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_latency: float = 0.0

    # Constitutional compliance
    constitutional_compliance_rate: float = 1.0
    constitutional_validation_time: float = 0.0


class ACGSChaosFramework:
    """ACGS Chaos Engineering Framework."""

    def __init__(self):
        self.docker_client = docker.from_env()

        # Metrics
        self.registry = CollectorRegistry()
        self.setup_metrics()

        # ACGS services configuration
        self.services = {
            "auth-service": {"port": 8000, "critical": True},
            "ac-service": {"port": 8001, "critical": True},
            "integrity-service": {"port": 8002, "critical": False},
            "fv-service": {"port": 8003, "critical": False},
            "gs-service": {"port": 8004, "critical": False},
            "pgc-service": {"port": 8005, "critical": True},
            "ec-service": {"port": 8006, "critical": True},
        }

        # Infrastructure services
        self.infrastructure = {
            "postgres": {"port": 5432, "critical": True},
            "redis": {"port": 6379, "critical": False},
            "nats": {"port": 4222, "critical": True},
        }

        # Active experiments
        self.active_experiments: dict[str, ChaosExperiment] = {}
        self.experiment_history: list[ChaosExperiment] = []

        # Safety mechanisms
        self.safety_enabled = True
        self.max_concurrent_experiments = 2
        self.emergency_stop_conditions = [
            "constitutional_compliance_below_95_percent",
            "critical_service_unavailable",
            "error_rate_above_10_percent",
        ]

        logger.info("ACGS Chaos Framework initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics for chaos experiments."""
        self.experiments_total = Counter(
            "acgs_chaos_experiments_total",
            "Total chaos experiments executed",
            ["chaos_type", "target_service", "status"],
            registry=self.registry,
        )

        self.experiment_duration = Histogram(
            "acgs_chaos_experiment_duration_seconds",
            "Duration of chaos experiments",
            ["chaos_type", "target_service"],
            registry=self.registry,
        )

        self.system_impact = Gauge(
            "acgs_chaos_system_impact",
            "System impact during chaos experiments",
            ["metric_type"],
            registry=self.registry,
        )

        self.constitutional_compliance_during_chaos = Gauge(
            "acgs_chaos_constitutional_compliance",
            "Constitutional compliance rate during chaos experiments",
            ["experiment_id"],
            registry=self.registry,
        )

        self.recovery_time = Histogram(
            "acgs_chaos_recovery_time_seconds",
            "Time to recover from chaos experiments",
            ["chaos_type", "target_service"],
            registry=self.registry,
        )

    async def start_framework(self):
        """Start the chaos engineering framework."""
        logger.info("Starting ACGS Chaos Engineering Framework...")

        # Start metrics server
        start_http_server(8100, registry=self.registry)
        logger.info("Chaos framework metrics server started on port 8100")

        # Start monitoring tasks
        asyncio.create_task(self.system_monitoring_loop())
        asyncio.create_task(self.safety_monitoring_loop())

        logger.info("ACGS Chaos Engineering Framework started")

    async def create_experiment(
        self, experiment_config: dict[str, Any]
    ) -> ChaosExperiment:
        """Create a new chaos experiment."""
        experiment = ChaosExperiment(
            experiment_id=str(uuid.uuid4()),
            name=experiment_config["name"],
            chaos_type=ChaosType(experiment_config["chaos_type"]),
            target_services=experiment_config["target_services"],
            duration_seconds=experiment_config.get("duration_seconds", 300),
            intensity=experiment_config.get("intensity", 0.5),
            steady_state_hypothesis=experiment_config.get(
                "steady_state_hypothesis", {}
            ),
            rollback_conditions=experiment_config.get("rollback_conditions", []),
            blast_radius=experiment_config.get("blast_radius", "single_service"),
            max_impact_threshold=experiment_config.get("max_impact_threshold", 0.1),
        )

        logger.info(
            f"Created chaos experiment: {experiment.name} ({experiment.experiment_id})"
        )
        return experiment

    async def execute_experiment(self, experiment: ChaosExperiment) -> bool:
        """Execute a chaos experiment."""
        logger.info(f"Executing chaos experiment: {experiment.name}")

        try:
            # Safety checks
            if not await self.pre_experiment_safety_check(experiment):
                logger.error(f"Safety check failed for experiment {experiment.name}")
                experiment.status = ExperimentStatus.ABORTED
                return False

            # Check concurrent experiments limit
            if len(self.active_experiments) >= self.max_concurrent_experiments:
                logger.error("Maximum concurrent experiments limit reached")
                return False

            # Validate steady state
            if not await self.validate_steady_state(experiment):
                logger.error(
                    f"Steady state validation failed for experiment {experiment.name}"
                )
                experiment.status = ExperimentStatus.FAILED
                return False

            # Start experiment
            experiment.status = ExperimentStatus.RUNNING
            experiment.start_time = datetime.now(timezone.utc)
            self.active_experiments[experiment.experiment_id] = experiment

            # Execute chaos action
            await self.execute_chaos_action(experiment)

            # Monitor experiment
            await self.monitor_experiment(experiment)

            # Cleanup and recovery
            await self.cleanup_experiment(experiment)

            experiment.status = ExperimentStatus.COMPLETED
            experiment.end_time = datetime.now(timezone.utc)

            # Record metrics
            self.experiments_total.labels(
                chaos_type=experiment.chaos_type.value,
                target_service=",".join(experiment.target_services),
                status=experiment.status.value,
            ).inc()

            duration = (experiment.end_time - experiment.start_time).total_seconds()
            self.experiment_duration.labels(
                chaos_type=experiment.chaos_type.value,
                target_service=",".join(experiment.target_services),
            ).observe(duration)

            logger.info(f"Completed chaos experiment: {experiment.name}")
            return True

        except Exception as e:
            logger.error(f"Experiment {experiment.name} failed: {e}")
            experiment.status = ExperimentStatus.FAILED
            experiment.end_time = datetime.now(timezone.utc)
            await self.emergency_cleanup(experiment)
            return False

        finally:
            # Remove from active experiments
            if experiment.experiment_id in self.active_experiments:
                del self.active_experiments[experiment.experiment_id]

            # Add to history
            self.experiment_history.append(experiment)

    async def execute_chaos_action(self, experiment: ChaosExperiment):
        """Execute the specific chaos action."""
        logger.info(
            f"Executing {experiment.chaos_type.value} on {experiment.target_services}"
        )

        if experiment.chaos_type == ChaosType.SERVICE_FAILURE:
            await self.inject_service_failure(experiment)
        elif experiment.chaos_type == ChaosType.NETWORK_LATENCY:
            await self.inject_network_latency(experiment)
        elif experiment.chaos_type == ChaosType.NETWORK_PARTITION:
            await self.inject_network_partition(experiment)
        elif experiment.chaos_type == ChaosType.RESOURCE_EXHAUSTION:
            await self.inject_resource_exhaustion(experiment)
        elif experiment.chaos_type == ChaosType.DATABASE_FAILURE:
            await self.inject_database_failure(experiment)
        elif experiment.chaos_type == ChaosType.MESSAGE_BROKER_FAILURE:
            await self.inject_message_broker_failure(experiment)
        elif experiment.chaos_type == ChaosType.CONSTITUTIONAL_VALIDATION_FAILURE:
            await self.inject_constitutional_validation_failure(experiment)
        elif experiment.chaos_type == ChaosType.MEMORY_PRESSURE:
            await self.inject_memory_pressure(experiment)
        elif experiment.chaos_type == ChaosType.CPU_STRESS:
            await self.inject_cpu_stress(experiment)
        else:
            raise ValueError(f"Unsupported chaos type: {experiment.chaos_type}")

    async def inject_service_failure(self, experiment: ChaosExperiment):
        """Inject service failure by stopping containers."""
        for service_name in experiment.target_services:
            try:
                # Find container
                containers = self.docker_client.containers.list(
                    filters={"name": service_name}
                )

                if containers:
                    container = containers[0]

                    # Stop container
                    container.stop()
                    logger.info(f"Stopped container: {service_name}")

                    # Wait for experiment duration
                    await asyncio.sleep(experiment.duration_seconds)

                    # Restart container
                    container.start()
                    logger.info(f"Restarted container: {service_name}")

                    # Wait for service to be ready
                    await self.wait_for_service_ready(service_name)

            except Exception as e:
                logger.error(
                    f"Failed to inject service failure for {service_name}: {e}"
                )

    async def inject_network_latency(self, experiment: ChaosExperiment):
        """Inject network latency using tc (traffic control)."""
        latency_ms = int(experiment.intensity * 1000)  # Convert to milliseconds

        for service_name in experiment.target_services:
            try:
                # Add network latency using tc
                # This is a simplified implementation - in practice, you'd use tools like Pumba or Chaos Mesh
                logger.info(f"Injecting {latency_ms}ms latency for {service_name}")

                # Simulate latency injection
                await asyncio.sleep(experiment.duration_seconds)

                logger.info(f"Removed latency injection for {service_name}")

            except Exception as e:
                logger.error(
                    f"Failed to inject network latency for {service_name}: {e}"
                )

    async def inject_network_partition(self, experiment: ChaosExperiment):
        """Inject network partition between services."""
        logger.info(f"Injecting network partition for {experiment.target_services}")

        try:
            # Simulate network partition
            # In practice, you'd use iptables rules or network policies
            await asyncio.sleep(experiment.duration_seconds)

            logger.info(f"Removed network partition for {experiment.target_services}")

        except Exception as e:
            logger.error(f"Failed to inject network partition: {e}")

    async def inject_resource_exhaustion(self, experiment: ChaosExperiment):
        """Inject resource exhaustion (CPU/Memory)."""
        for service_name in experiment.target_services:
            try:
                # Find container
                containers = self.docker_client.containers.list(
                    filters={"name": service_name}
                )

                if containers:
                    container = containers[0]

                    # Update container resources to create pressure
                    memory_limit = int(100 * 1024 * 1024 * experiment.intensity)  # MB
                    cpu_limit = int(0.5 * experiment.intensity * 1000000)  # CPU units

                    container.update(mem_limit=memory_limit, cpu_quota=cpu_limit)

                    logger.info(f"Applied resource constraints to {service_name}")

                    # Wait for experiment duration
                    await asyncio.sleep(experiment.duration_seconds)

                    # Remove constraints
                    container.update(mem_limit=0, cpu_quota=0)
                    logger.info(f"Removed resource constraints from {service_name}")

            except Exception as e:
                logger.error(
                    f"Failed to inject resource exhaustion for {service_name}: {e}"
                )

    async def inject_database_failure(self, experiment: ChaosExperiment):
        """Inject database failure."""
        try:
            # Stop PostgreSQL container
            postgres_containers = self.docker_client.containers.list(
                filters={"name": "postgres"}
            )

            if postgres_containers:
                postgres_container = postgres_containers[0]
                postgres_container.stop()
                logger.info("Stopped PostgreSQL container")

                # Wait for experiment duration
                await asyncio.sleep(experiment.duration_seconds)

                # Restart PostgreSQL
                postgres_container.start()
                logger.info("Restarted PostgreSQL container")

                # Wait for database to be ready
                await asyncio.sleep(30)

        except Exception as e:
            logger.error(f"Failed to inject database failure: {e}")

    async def inject_message_broker_failure(self, experiment: ChaosExperiment):
        """Inject NATS message broker failure."""
        try:
            # Stop NATS container
            nats_containers = self.docker_client.containers.list(
                filters={"name": "nats"}
            )

            if nats_containers:
                nats_container = nats_containers[0]
                nats_container.stop()
                logger.info("Stopped NATS container")

                # Wait for experiment duration
                await asyncio.sleep(experiment.duration_seconds)

                # Restart NATS
                nats_container.start()
                logger.info("Restarted NATS container")

                # Wait for NATS to be ready
                await asyncio.sleep(10)

        except Exception as e:
            logger.error(f"Failed to inject message broker failure: {e}")

    async def inject_constitutional_validation_failure(
        self, experiment: ChaosExperiment
    ):
        """Inject constitutional validation failure by corrupting the hash temporarily."""
        logger.info("Injecting constitutional validation failure")

        try:
            # This would temporarily modify the constitutional hash validation
            # In practice, you'd modify the validation service or inject invalid hashes

            # Simulate constitutional validation failure
            await asyncio.sleep(experiment.duration_seconds)

            logger.info("Restored constitutional validation")

        except Exception as e:
            logger.error(f"Failed to inject constitutional validation failure: {e}")

    async def inject_memory_pressure(self, experiment: ChaosExperiment):
        """Inject memory pressure on the system."""
        logger.info("Injecting memory pressure")

        try:
            # Allocate memory to create pressure
            memory_to_allocate = int(
                psutil.virtual_memory().total * experiment.intensity * 0.1
            )

            # Simulate memory pressure
            await asyncio.sleep(experiment.duration_seconds)

            logger.info("Released memory pressure")

        except Exception as e:
            logger.error(f"Failed to inject memory pressure: {e}")

    async def inject_cpu_stress(self, experiment: ChaosExperiment):
        """Inject CPU stress on the system."""
        logger.info("Injecting CPU stress")

        try:
            # Create CPU stress
            # In practice, you'd use stress-ng or similar tools

            # Simulate CPU stress
            await asyncio.sleep(experiment.duration_seconds)

            logger.info("Released CPU stress")

        except Exception as e:
            logger.error(f"Failed to inject CPU stress: {e}")

    async def monitor_experiment(self, experiment: ChaosExperiment):
        """Monitor experiment progress and system health."""
        logger.info(f"Monitoring experiment: {experiment.name}")

        start_time = time.time()

        while time.time() - start_time < experiment.duration_seconds:
            # Collect system metrics
            metrics = await self.collect_system_metrics()

            # Check safety conditions
            if await self.check_emergency_stop_conditions(experiment, metrics):
                logger.warning(
                    f"Emergency stop triggered for experiment {experiment.name}"
                )
                await self.emergency_cleanup(experiment)
                break

            # Update metrics
            self.system_impact.labels(metric_type="response_time").set(
                sum(metrics.service_response_times.values())
                / len(metrics.service_response_times)
                if metrics.service_response_times
                else 0
            )

            self.constitutional_compliance_during_chaos.labels(
                experiment_id=experiment.experiment_id
            ).set(metrics.constitutional_compliance_rate)

            # Wait before next check
            await asyncio.sleep(10)

    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        metrics = SystemMetrics(timestamp=datetime.now(timezone.utc))

        # Collect service metrics
        for service_name, config in self.services.items():
            try:
                async with aiohttp.ClientSession() as session:
                    start_time = time.time()
                    async with session.get(
                        f"http://localhost:{config['port']}/health", timeout=5
                    ) as response:
                        response_time = (time.time() - start_time) * 1000

                        metrics.service_response_times[service_name] = response_time
                        metrics.service_availability[service_name] = (
                            response.status == 200
                        )

                        if response.status >= 400:
                            metrics.service_error_rates[service_name] = 1.0
                        else:
                            metrics.service_error_rates[service_name] = 0.0

            except Exception:
                metrics.service_availability[service_name] = False
                metrics.service_error_rates[service_name] = 1.0
                metrics.service_response_times[service_name] = 5000  # Timeout

        # Collect system metrics
        metrics.cpu_usage = psutil.cpu_percent()
        metrics.memory_usage = psutil.virtual_memory().percent
        metrics.disk_usage = psutil.disk_usage("/").percent

        # Check constitutional compliance
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://localhost:8001/api/v1/constitutional/validate",
                    json={"constitutional_hash": CONSTITUTIONAL_HASH},
                    timeout=5,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        metrics.constitutional_compliance_rate = data.get(
                            "compliance_score", 0.0
                        )
                    else:
                        metrics.constitutional_compliance_rate = 0.0
        except Exception:
            metrics.constitutional_compliance_rate = 0.0

        return metrics

    async def validate_steady_state(self, experiment: ChaosExperiment) -> bool:
        """Validate system is in steady state before experiment."""
        logger.info(f"Validating steady state for experiment: {experiment.name}")

        metrics = await self.collect_system_metrics()

        # Check service availability
        for service_name in experiment.target_services:
            if not metrics.service_availability.get(service_name, False):
                logger.error(f"Service {service_name} is not available")
                return False

        # Check constitutional compliance
        if metrics.constitutional_compliance_rate < 0.95:
            logger.error(
                f"Constitutional compliance too low: {metrics.constitutional_compliance_rate}"
            )
            return False

        # Check error rates
        avg_error_rate = sum(metrics.service_error_rates.values()) / len(
            metrics.service_error_rates
        )
        if avg_error_rate > 0.05:  # 5% threshold
            logger.error(f"Error rate too high: {avg_error_rate}")
            return False

        logger.info("Steady state validation passed")
        return True

    async def pre_experiment_safety_check(self, experiment: ChaosExperiment) -> bool:
        """Perform safety checks before experiment."""
        logger.info(f"Performing safety check for experiment: {experiment.name}")

        # Check if safety is enabled
        if not self.safety_enabled:
            logger.warning("Safety checks disabled")
            return True

        # Check blast radius
        if experiment.blast_radius == "system_wide" and experiment.intensity > 0.3:
            logger.error("System-wide experiment with high intensity not allowed")
            return False

        # Check critical services
        critical_services = [
            name for name, config in self.services.items() if config["critical"]
        ]
        if any(service in critical_services for service in experiment.target_services):
            if experiment.intensity > 0.5:
                logger.error(
                    "High intensity experiment on critical services not allowed"
                )
                return False

        # Check constitutional compliance requirement
        if experiment.constitutional_compliance_required:
            metrics = await self.collect_system_metrics()
            if metrics.constitutional_compliance_rate < 0.99:
                logger.error("Constitutional compliance too low for experiment")
                return False

        logger.info("Safety check passed")
        return True

    async def check_emergency_stop_conditions(
        self, experiment: ChaosExperiment, metrics: SystemMetrics
    ) -> bool:
        """Check if emergency stop conditions are met."""

        # Constitutional compliance check
        if metrics.constitutional_compliance_rate < 0.95:
            logger.warning("Constitutional compliance below 95%")
            return True

        # Critical service availability check
        critical_services = [
            name for name, config in self.services.items() if config["critical"]
        ]
        for service in critical_services:
            if not metrics.service_availability.get(service, False):
                logger.warning(f"Critical service {service} unavailable")
                return True

        # Error rate check
        avg_error_rate = sum(metrics.service_error_rates.values()) / len(
            metrics.service_error_rates
        )
        if avg_error_rate > 0.1:  # 10% threshold
            logger.warning(f"Error rate above 10%: {avg_error_rate}")
            return True

        return False

    async def emergency_cleanup(self, experiment: ChaosExperiment):
        """Perform emergency cleanup and recovery."""
        logger.warning(
            f"Performing emergency cleanup for experiment: {experiment.name}"
        )

        try:
            # Stop all chaos actions immediately
            await self.cleanup_experiment(experiment)

            # Restart all affected services
            for service_name in experiment.target_services:
                await self.restart_service(service_name)

            # Wait for services to recover
            await asyncio.sleep(30)

            # Validate recovery
            metrics = await self.collect_system_metrics()
            recovery_successful = all(
                metrics.service_availability.get(service, False)
                for service in experiment.target_services
            )

            if recovery_successful:
                logger.info("Emergency recovery successful")
            else:
                logger.error("Emergency recovery failed")

        except Exception as e:
            logger.error(f"Emergency cleanup failed: {e}")

    async def cleanup_experiment(self, experiment: ChaosExperiment):
        """Clean up after experiment completion."""
        logger.info(f"Cleaning up experiment: {experiment.name}")

        # Restore all services to normal state
        for service_name in experiment.target_services:
            try:
                # Remove any resource constraints
                containers = self.docker_client.containers.list(
                    filters={"name": service_name}
                )

                if containers:
                    container = containers[0]
                    container.update(mem_limit=0, cpu_quota=0)

            except Exception as e:
                logger.warning(f"Failed to cleanup {service_name}: {e}")

    async def restart_service(self, service_name: str):
        """Restart a specific service."""
        try:
            containers = self.docker_client.containers.list(
                filters={"name": service_name}
            )

            if containers:
                container = containers[0]
                container.restart()
                logger.info(f"Restarted service: {service_name}")

                # Wait for service to be ready
                await self.wait_for_service_ready(service_name)

        except Exception as e:
            logger.error(f"Failed to restart service {service_name}: {e}")

    async def wait_for_service_ready(self, service_name: str, timeout: int = 60):
        """Wait for a service to be ready."""
        port = self.services.get(service_name, {}).get("port")
        if not port:
            return

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"http://localhost:{port}/health", timeout=5
                    ) as response:
                        if response.status == 200:
                            logger.info(f"Service {service_name} is ready")
                            return
            except Exception:
                pass

            await asyncio.sleep(2)

        logger.warning(f"Service {service_name} not ready after {timeout} seconds")

    async def system_monitoring_loop(self):
        """Continuous system monitoring loop."""
        while True:
            try:
                metrics = await self.collect_system_metrics()

                # Update system metrics
                self.system_impact.labels(metric_type="cpu_usage").set(
                    metrics.cpu_usage
                )
                self.system_impact.labels(metric_type="memory_usage").set(
                    metrics.memory_usage
                )
                self.system_impact.labels(metric_type="constitutional_compliance").set(
                    metrics.constitutional_compliance_rate
                )

                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Error in system monitoring loop: {e}")
                await asyncio.sleep(60)

    async def safety_monitoring_loop(self):
        """Continuous safety monitoring loop."""
        while True:
            try:
                # Check all active experiments
                for experiment in list(self.active_experiments.values()):
                    metrics = await self.collect_system_metrics()

                    if await self.check_emergency_stop_conditions(experiment, metrics):
                        logger.warning(
                            f"Emergency stop triggered for {experiment.name}"
                        )
                        await self.emergency_cleanup(experiment)
                        experiment.status = ExperimentStatus.ABORTED

                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"Error in safety monitoring loop: {e}")
                await asyncio.sleep(30)

    def get_framework_status(self) -> dict[str, Any]:
        """Get chaos framework status."""
        return {
            "active_experiments": len(self.active_experiments),
            "total_experiments": len(self.experiment_history),
            "safety_enabled": self.safety_enabled,
            "max_concurrent_experiments": self.max_concurrent_experiments,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "services_monitored": len(self.services),
            "infrastructure_monitored": len(self.infrastructure),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global chaos framework instance
chaos_framework = ACGSChaosFramework()

if __name__ == "__main__":

    async def main():
        await chaos_framework.start_framework()

        try:
            # Keep running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down chaos framework...")

    asyncio.run(main())
