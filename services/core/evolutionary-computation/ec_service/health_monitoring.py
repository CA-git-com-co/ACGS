"""
Comprehensive Health Monitoring for ACGS Evolutionary Computation Service
Implements advanced health checks, monitoring, and alerting capabilities.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional

import aiohttp
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    start_http_server,
)

logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class ComponentType(Enum):
    """Types of components to monitor."""

    API_ENDPOINT = "api_endpoint"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    SECURITY_LAYER = "security_layer"
    EVOLUTION_ENGINE = "evolution_engine"
    HUMAN_WORKFLOW = "human_workflow"


@dataclass
class HealthCheck:
    """Individual health check definition."""

    check_id: str
    name: str
    component_type: ComponentType
    check_function: str
    interval_seconds: int = 30
    timeout_seconds: int = 10
    critical: bool = False

    # Thresholds
    warning_threshold: float = 0.8
    critical_threshold: float = 0.5

    # State tracking
    last_check_time: Optional[datetime] = None
    last_status: Optional[HealthStatus] = None
    consecutive_failures: int = 0


@dataclass
class HealthMetrics:
    """Health metrics for a component."""

    component_id: str
    status: HealthStatus
    response_time_ms: float
    availability_percent: float
    error_rate_percent: float
    constitutional_compliance_score: float
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class HealthMonitor:
    """Comprehensive health monitoring system."""

    def __init__(self):
        self.registry = CollectorRegistry()
        self.setup_metrics()

        # Health tracking
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_metrics: Dict[str, HealthMetrics] = {}
        self.alert_history: List[Dict] = []

        # Service endpoints
        self.service_endpoints = {
            "auth-service": "http://localhost:8000",
            "ac-service": "http://localhost:8001",
            "integrity-service": "http://localhost:8002",
            "fv-service": "http://localhost:8003",
            "gs-service": "http://localhost:8004",
            "pgc-service": "http://localhost:8005",
            "ec-service": "http://localhost:8006",
        }

        # Initialize health checks
        self.initialize_health_checks()

        logger.info("Health Monitor initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics for health monitoring."""
        self.health_status_gauge = Gauge(
            "acgs_ec_health_status",
            "Health status of components (0=critical, 1=unhealthy, 2=degraded, 3=healthy)",
            ["component_id", "component_type"],
            registry=self.registry,
        )

        self.health_check_duration = Histogram(
            "acgs_ec_health_check_duration_seconds",
            "Duration of health checks",
            ["check_id"],
            registry=self.registry,
        )

        self.health_check_failures_total = Counter(
            "acgs_ec_health_check_failures_total",
            "Total health check failures",
            ["check_id", "component_type"],
            registry=self.registry,
        )

        self.constitutional_compliance_health = Gauge(
            "acgs_ec_constitutional_compliance_health",
            "Constitutional compliance score for health checks",
            ["component_id"],
            registry=self.registry,
        )

    def initialize_health_checks(self):
        """Initialize all health checks."""
        health_checks = [
            # API endpoint checks
            HealthCheck(
                check_id="api_root",
                name="API Root Endpoint",
                component_type=ComponentType.API_ENDPOINT,
                check_function="check_api_endpoint",
                interval_seconds=30,
                critical=True,
            ),
            HealthCheck(
                check_id="api_health",
                name="API Health Endpoint",
                component_type=ComponentType.API_ENDPOINT,
                check_function="check_health_endpoint",
                interval_seconds=15,
                critical=True,
            ),
            HealthCheck(
                check_id="api_evolution_submit",
                name="Evolution Submit API",
                component_type=ComponentType.API_ENDPOINT,
                check_function="check_evolution_api",
                interval_seconds=60,
                critical=False,
            ),
            # External service checks
            HealthCheck(
                check_id="ac_service_integration",
                name="AC Service Integration",
                component_type=ComponentType.EXTERNAL_SERVICE,
                check_function="check_ac_service",
                interval_seconds=60,
                critical=True,
            ),
            HealthCheck(
                check_id="pgc_service_integration",
                name="PGC Service Integration",
                component_type=ComponentType.EXTERNAL_SERVICE,
                check_function="check_pgc_service",
                interval_seconds=60,
                critical=False,
            ),
            # Security layer checks
            HealthCheck(
                check_id="security_architecture",
                name="4-Layer Security Architecture",
                component_type=ComponentType.SECURITY_LAYER,
                check_function="check_security_layers",
                interval_seconds=120,
                critical=True,
            ),
            # Evolution engine checks
            HealthCheck(
                check_id="evolution_engine",
                name="Evolution Engine",
                component_type=ComponentType.EVOLUTION_ENGINE,
                check_function="check_evolution_engine",
                interval_seconds=90,
                critical=True,
            ),
            # Human workflow checks
            HealthCheck(
                check_id="human_approval_workflow",
                name="Human Approval Workflow",
                component_type=ComponentType.HUMAN_WORKFLOW,
                check_function="check_human_workflow",
                interval_seconds=180,
                critical=False,
            ),
        ]

        for check in health_checks:
            self.health_checks[check.check_id] = check

    async def start_health_monitoring(self):
        """Start the health monitoring system."""
        logger.info("Starting health monitoring system...")

        # Start Prometheus metrics server
        start_http_server(8092, registry=self.registry)
        logger.info("Health monitoring metrics server started on port 8092")

        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self.health_check_loop()),
            asyncio.create_task(self.alert_manager()),
            asyncio.create_task(self.metrics_updater()),
        ]

        await asyncio.gather(*tasks)

    async def health_check_loop(self):
        """Main health check loop."""
        while True:
            try:
                current_time = datetime.now(timezone.utc)

                for check_id, health_check in self.health_checks.items():
                    # Check if it's time to run this health check
                    if (
                        health_check.last_check_time is None
                        or (current_time - health_check.last_check_time).total_seconds()
                        >= health_check.interval_seconds
                    ):

                        await self.run_health_check(health_check)

                await asyncio.sleep(5)  # Check every 5 seconds for due health checks

            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(10)

    async def run_health_check(self, health_check: HealthCheck):
        """Run a specific health check."""
        start_time = time.time()

        try:
            # Get the check function
            check_function = getattr(self, health_check.check_function)

            # Run the health check
            result = await asyncio.wait_for(
                check_function(health_check), timeout=health_check.timeout_seconds
            )

            # Update health check state
            health_check.last_check_time = datetime.now(timezone.utc)
            health_check.last_status = result["status"]

            if result["status"] == HealthStatus.HEALTHY:
                health_check.consecutive_failures = 0
            else:
                health_check.consecutive_failures += 1

            # Record metrics
            duration = time.time() - start_time
            self.health_check_duration.labels(check_id=health_check.check_id).observe(
                duration
            )

            if result["status"] != HealthStatus.HEALTHY:
                self.health_check_failures_total.labels(
                    check_id=health_check.check_id,
                    component_type=health_check.component_type.value,
                ).inc()

            # Update health metrics
            self.update_health_metrics(health_check.check_id, result)

            logger.debug(
                f"Health check {health_check.check_id}: {result['status'].value}"
            )

        except asyncio.TimeoutError:
            logger.warning(f"Health check {health_check.check_id} timed out")
            await self.handle_health_check_failure(health_check, "timeout")

        except Exception as e:
            logger.error(f"Health check {health_check.check_id} failed: {e}")
            await self.handle_health_check_failure(health_check, str(e))

    async def check_api_endpoint(self, health_check: HealthCheck) -> Dict:
        """Check API endpoint health."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()

            try:
                async with session.get("http://localhost:8006/", timeout=5) as response:
                    response_time = (time.time() - start_time) * 1000

                    if response.status == 200:
                        data = await response.json()

                        return {
                            "status": HealthStatus.HEALTHY,
                            "response_time_ms": response_time,
                            "details": {"status_code": response.status},
                        }
                    else:
                        return {
                            "status": HealthStatus.DEGRADED,
                            "response_time_ms": response_time,
                            "details": {"status_code": response.status},
                        }

            except Exception as e:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "details": {"error": str(e)},
                }

    async def check_health_endpoint(self, health_check: HealthCheck) -> Dict:
        """Check dedicated health endpoint."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()

            try:
                async with session.get(
                    "http://localhost:8006/health", timeout=5
                ) as response:
                    response_time = (time.time() - start_time) * 1000

                    if response.status == 200:
                        data = await response.json()

                        if data.get("status") in ["healthy", "operational"]:
                            return {
                                "status": HealthStatus.HEALTHY,
                                "response_time_ms": response_time,
                                "details": data,
                            }
                        else:
                            return {
                                "status": HealthStatus.DEGRADED,
                                "response_time_ms": response_time,
                                "details": data,
                            }
                    else:
                        return {
                            "status": HealthStatus.UNHEALTHY,
                            "response_time_ms": response_time,
                            "details": {"status_code": response.status},
                        }

            except Exception as e:
                return {
                    "status": HealthStatus.CRITICAL,
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "details": {"error": str(e)},
                }

    async def check_evolution_api(self, health_check: HealthCheck) -> Dict:
        """Check evolution API functionality."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()

            try:
                # Test evolution status endpoint with fake ID
                fake_id = "health-check-test"
                async with session.get(
                    f"http://localhost:8006/api/v1/evolution/{fake_id}/status",
                    timeout=5,
                ) as response:
                    response_time = (time.time() - start_time) * 1000

                    # Should return 404 for non-existent evolution
                    if response.status == 404:
                        return {
                            "status": HealthStatus.HEALTHY,
                            "response_time_ms": response_time,
                            "details": {"api_functional": True},
                        }
                    else:
                        return {
                            "status": HealthStatus.DEGRADED,
                            "response_time_ms": response_time,
                            "details": {"unexpected_status": response.status},
                        }

            except Exception as e:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "details": {"error": str(e)},
                }

    async def check_ac_service(self, health_check: HealthCheck) -> Dict:
        """Check AC Service integration."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()

            try:
                async with session.get(
                    "http://localhost:8001/health", timeout=5
                ) as response:
                    response_time = (time.time() - start_time) * 1000

                    if response.status == 200:
                        return {
                            "status": HealthStatus.HEALTHY,
                            "response_time_ms": response_time,
                            "details": {"ac_service_available": True},
                        }
                    else:
                        return {
                            "status": HealthStatus.DEGRADED,
                            "response_time_ms": response_time,
                            "details": {"ac_service_status": response.status},
                        }

            except Exception as e:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "details": {"error": str(e)},
                }

    async def check_pgc_service(self, health_check: HealthCheck) -> Dict:
        """Check PGC Service integration."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()

            try:
                async with session.get(
                    "http://localhost:8005/health", timeout=5
                ) as response:
                    response_time = (time.time() - start_time) * 1000

                    if response.status == 200:
                        return {
                            "status": HealthStatus.HEALTHY,
                            "response_time_ms": response_time,
                            "details": {"pgc_service_available": True},
                        }
                    else:
                        return {
                            "status": HealthStatus.DEGRADED,
                            "response_time_ms": response_time,
                            "details": {"pgc_service_status": response.status},
                        }

            except Exception as e:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "details": {"error": str(e)},
                }

    async def check_security_layers(self, health_check: HealthCheck) -> Dict:
        """Check 4-layer security architecture."""
        start_time = time.time()

        try:
            # Check if security configuration files exist
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent.parent.parent

            security_files = [
                "infrastructure/security/sandbox_configs/default.json",
                "infrastructure/security/policies/evolution.rego",
                "infrastructure/security/auth/jwt_config.json",
                "infrastructure/security/audit/config.json",
            ]

            layers_healthy = 0
            total_layers = len(security_files)

            for file_path in security_files:
                full_path = project_root / file_path
                if full_path.exists():
                    layers_healthy += 1

            response_time = (time.time() - start_time) * 1000
            health_ratio = layers_healthy / total_layers

            if health_ratio >= 1.0:
                status = HealthStatus.HEALTHY
            elif health_ratio >= 0.75:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY

            return {
                "status": status,
                "response_time_ms": response_time,
                "details": {
                    "layers_healthy": layers_healthy,
                    "total_layers": total_layers,
                    "health_ratio": health_ratio,
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "response_time_ms": (time.time() - start_time) * 1000,
                "details": {"error": str(e)},
            }

    async def check_evolution_engine(self, health_check: HealthCheck) -> Dict:
        """Check evolution engine health."""
        start_time = time.time()

        try:
            # Import and check evolution engine
            from .evolution_engine import evolution_engine

            # Check if evolution engine is responsive
            active_evolutions = len(evolution_engine.active_evolutions)

            response_time = (time.time() - start_time) * 1000

            return {
                "status": HealthStatus.HEALTHY,
                "response_time_ms": response_time,
                "details": {
                    "active_evolutions": active_evolutions,
                    "engine_responsive": True,
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "response_time_ms": (time.time() - start_time) * 1000,
                "details": {"error": str(e)},
            }

    async def check_human_workflow(self, health_check: HealthCheck) -> Dict:
        """Check human approval workflow health."""
        start_time = time.time()

        try:
            # Import and check human workflow
            from .human_approval_workflow import human_approval_workflow

            # Check if workflow is responsive
            pending_reviews = len(human_approval_workflow.pending_tasks)

            response_time = (time.time() - start_time) * 1000

            return {
                "status": HealthStatus.HEALTHY,
                "response_time_ms": response_time,
                "details": {
                    "pending_reviews": pending_reviews,
                    "workflow_responsive": True,
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.DEGRADED,
                "response_time_ms": (time.time() - start_time) * 1000,
                "details": {"error": str(e)},
            }

    def update_health_metrics(self, check_id: str, result: Dict):
        """Update health metrics for a component."""
        status = result["status"]
        response_time = result.get("response_time_ms", 0.0)

        # Update health metrics
        self.health_metrics[check_id] = HealthMetrics(
            component_id=check_id,
            status=status,
            response_time_ms=response_time,
            availability_percent=100.0 if status == HealthStatus.HEALTHY else 50.0,
            error_rate_percent=0.0 if status == HealthStatus.HEALTHY else 10.0,
            constitutional_compliance_score=1.0,  # Simplified for now
        )

        # Update Prometheus metrics
        status_values = {
            HealthStatus.CRITICAL: 0,
            HealthStatus.UNHEALTHY: 1,
            HealthStatus.DEGRADED: 2,
            HealthStatus.HEALTHY: 3,
        }

        health_check = self.health_checks[check_id]
        self.health_status_gauge.labels(
            component_id=check_id, component_type=health_check.component_type.value
        ).set(status_values[status])

        self.constitutional_compliance_health.labels(component_id=check_id).set(1.0)

    async def handle_health_check_failure(self, health_check: HealthCheck, error: str):
        """Handle health check failure."""
        health_check.last_check_time = datetime.now(timezone.utc)
        health_check.last_status = HealthStatus.CRITICAL
        health_check.consecutive_failures += 1

        # Record failure metrics
        self.health_check_failures_total.labels(
            check_id=health_check.check_id,
            component_type=health_check.component_type.value,
        ).inc()

        # Create alert if critical
        if health_check.critical or health_check.consecutive_failures >= 3:
            await self.create_alert(health_check, error)

    async def create_alert(self, health_check: HealthCheck, error: str):
        """Create health alert."""
        alert = {
            "alert_id": f"health_{health_check.check_id}_{int(time.time())}",
            "check_id": health_check.check_id,
            "component_type": health_check.component_type.value,
            "severity": "critical" if health_check.critical else "warning",
            "message": f"Health check {health_check.name} failed: {error}",
            "consecutive_failures": health_check.consecutive_failures,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        self.alert_history.append(alert)

        # Keep only last 100 alerts
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]

        logger.warning(f"Health alert created: {alert['message']}")

    async def alert_manager(self):
        """Manage health alerts."""
        while True:
            try:
                # Process alerts (in production, would integrate with alerting system)
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Error in alert manager: {e}")

    async def metrics_updater(self):
        """Update aggregated metrics."""
        while True:
            try:
                await asyncio.sleep(30)

                # Update overall health status
                # Implementation would aggregate component health

            except Exception as e:
                logger.error(f"Error in metrics updater: {e}")

    def get_overall_health(self) -> Dict:
        """Get overall health status."""
        if not self.health_metrics:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": "No health data available",
            }

        # Calculate overall health
        healthy_components = sum(
            1
            for metrics in self.health_metrics.values()
            if metrics.status == HealthStatus.HEALTHY
        )
        total_components = len(self.health_metrics)

        health_ratio = (
            healthy_components / total_components if total_components > 0 else 0
        )

        if health_ratio >= 0.9:
            overall_status = HealthStatus.HEALTHY
        elif health_ratio >= 0.7:
            overall_status = HealthStatus.DEGRADED
        elif health_ratio >= 0.5:
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.CRITICAL

        return {
            "status": overall_status.value,
            "healthy_components": healthy_components,
            "total_components": total_components,
            "health_ratio": health_ratio,
            "component_details": {
                check_id: {
                    "status": metrics.status.value,
                    "response_time_ms": metrics.response_time_ms,
                    "last_updated": metrics.last_updated.isoformat(),
                }
                for check_id, metrics in self.health_metrics.items()
            },
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }


# Global health monitor instance
health_monitor = HealthMonitor()
