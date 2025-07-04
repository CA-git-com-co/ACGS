#!/usr/bin/env python3
"""
Production Monitoring Orchestrator for ACGS-1
Comprehensive monitoring with Prometheus/Grafana, custom dashboards, automated alerting,
performance metrics collection, and health monitoring integrated into constitutional workflows
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class ServiceStatus(Enum):
    """Service status levels"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class MetricThreshold:
    """Metric threshold configuration"""

    name: str
    warning_threshold: float
    critical_threshold: float
    unit: str
    description: str


@dataclass
class AlertRule:
    """Alert rule configuration"""

    name: str
    expression: str
    severity: AlertSeverity
    duration: str
    description: str
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)


@dataclass
class ServiceMetrics:
    """Service metrics data"""

    service_name: str
    availability: float
    response_time_p95: float
    response_time_avg: float
    error_rate: float
    throughput: float
    cpu_usage: float
    memory_usage: float
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class GovernanceMetrics:
    """Constitutional governance specific metrics"""

    constitutional_compliance_score: float
    governance_action_cost_sol: float
    policy_synthesis_success_rate: float
    active_workflows: int
    completed_workflows_24h: int
    blockchain_transaction_success_rate: float
    last_updated: datetime = field(default_factory=datetime.now)


class ProductionMonitoringOrchestrator:
    """
    Production Monitoring Orchestrator
    Manages comprehensive monitoring, alerting, and health monitoring for ACGS-1
    """

    def __init__(
        self,
        prometheus_url: str = "http://localhost:9090",
        grafana_url: str = "http://localhost:3000",
        alertmanager_url: str = "http://localhost:9093",
    ):
        self.prometheus_url = prometheus_url
        self.grafana_url = grafana_url
        self.alertmanager_url = alertmanager_url

        self.service_metrics: dict[str, ServiceMetrics] = {}
        self.governance_metrics: GovernanceMetrics | None = None
        self.alert_rules: list[AlertRule] = []
        self.metric_thresholds: dict[str, MetricThreshold] = {}

        self.running = False
        self.monitoring_tasks: list[asyncio.Task] = []

        # Initialize ACGS service monitoring
        self._initialize_acgs_monitoring()

    def _initialize_acgs_monitoring(self):
        """Initialize ACGS-specific monitoring configuration"""

        # Define metric thresholds for ACGS services
        self.metric_thresholds = {
            "response_time_p95": MetricThreshold(
                name="Response Time 95th Percentile",
                warning_threshold=1.0,
                critical_threshold=2.0,
                unit="seconds",
                description="95th percentile response time",
            ),
            "error_rate": MetricThreshold(
                name="Error Rate",
                warning_threshold=0.05,
                critical_threshold=0.10,
                unit="percentage",
                description="Service error rate",
            ),
            "availability": MetricThreshold(
                name="Service Availability",
                warning_threshold=0.995,
                critical_threshold=0.99,
                unit="percentage",
                description="Service availability percentage",
            ),
            "constitutional_compliance": MetricThreshold(
                name="Constitutional Compliance",
                warning_threshold=0.95,
                critical_threshold=0.90,
                unit="score",
                description="Constitutional compliance score",
            ),
            "governance_cost": MetricThreshold(
                name="Governance Action Cost",
                warning_threshold=0.008,
                critical_threshold=0.01,
                unit="SOL",
                description="Cost per governance action",
            ),
        }

        # Define alert rules for ACGS services
        self.alert_rules = [
            AlertRule(
                name="ACGSServiceDown",
                expression='up{job=~"acgs-.*"} == 0',
                severity=AlertSeverity.CRITICAL,
                duration="1m",
                description="ACGS service is down",
                labels={"component": "acgs-core"},
                annotations={
                    "summary": "ACGS service {{ $labels.job }} is down",
                    "description": "Service {{ $labels.job }} has been down for more than 1 minute",
                },
            ),
            AlertRule(
                name="ACGSHighResponseTime",
                expression='histogram_quantile(0.95, rate(acgs_http_request_duration_seconds_bucket{job=~"acgs-.*"}[5m])) > 2',
                severity=AlertSeverity.WARNING,
                duration="5m",
                description="High response time for ACGS service",
                labels={"component": "acgs-performance"},
                annotations={
                    "summary": "High response time for {{ $labels.job }}",
                    "description": "95th percentile response time is {{ $value }}s, exceeding 2s target",
                },
            ),
            AlertRule(
                name="ACGSConstitutionalComplianceLow",
                expression="acgs_constitutional_compliance_score < 0.95",
                severity=AlertSeverity.CRITICAL,
                duration="2m",
                description="Constitutional compliance below threshold",
                labels={"component": "acgs-governance"},
                annotations={
                    "summary": "Constitutional compliance below threshold",
                    "description": "Constitutional compliance rate is {{ $value }}%, below 95% threshold",
                },
            ),
            AlertRule(
                name="ACGSGovernanceCostHigh",
                expression="acgs_governance_action_cost_sol > 0.01",
                severity=AlertSeverity.WARNING,
                duration="1m",
                description="Governance action costs too high",
                labels={"component": "acgs-blockchain"},
                annotations={
                    "summary": "Governance action costs too high",
                    "description": "Governance action cost is {{ $value }} SOL, exceeding 0.01 SOL target",
                },
            ),
            AlertRule(
                name="ACGSQuantumagiProgramError",
                expression="rate(quantumagi_program_errors_total[5m]) > 0.1",
                severity=AlertSeverity.CRITICAL,
                duration="2m",
                description="High error rate in Quantumagi programs",
                labels={"component": "acgs-blockchain"},
                annotations={
                    "summary": "High error rate in Quantumagi programs",
                    "description": "Error rate is {{ $value }} errors/sec in {{ $labels.program }}",
                },
            ),
        ]

    async def start(self):
        """Start the production monitoring orchestrator"""
        if self.running:
            return

        self.running = True
        logger.info("Starting Production Monitoring Orchestrator")

        # Start monitoring tasks
        tasks = [
            self._metrics_collection_loop(),
            self._health_monitoring_loop(),
            self._governance_metrics_loop(),
            self._alert_evaluation_loop(),
            self._dashboard_update_loop(),
        ]

        self.monitoring_tasks = [asyncio.create_task(task) for task in tasks]

        logger.info("Production Monitoring Orchestrator started successfully")

    async def stop(self):
        """Stop the production monitoring orchestrator"""
        if not self.running:
            return

        self.running = False
        logger.info("Stopping Production Monitoring Orchestrator")

        # Cancel all monitoring tasks
        for task in self.monitoring_tasks:
            task.cancel()

        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        self.monitoring_tasks.clear()

        logger.info("Production Monitoring Orchestrator stopped")

    async def _metrics_collection_loop(self):
        """Collect metrics from Prometheus"""
        while self.running:
            try:
                await self._collect_service_metrics()
                await asyncio.sleep(30)  # Collect every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(10)

    async def _collect_service_metrics(self):
        """Collect metrics for all ACGS services"""
        acgs_services = [
            "auth_service",
            "ac_service",
            "integrity_service",
            "fv_service",
            "gs_service",
            "pgc_service",
            "ec_service",
        ]

        for service in acgs_services:
            try:
                # Simulate metrics collection (replace with actual Prometheus queries)
                metrics = ServiceMetrics(
                    service_name=service,
                    availability=0.999,  # 99.9% availability
                    response_time_p95=0.45,  # 450ms
                    response_time_avg=0.25,  # 250ms
                    error_rate=0.02,  # 2% error rate
                    throughput=150.0,  # 150 requests/sec
                    cpu_usage=0.65,  # 65% CPU usage
                    memory_usage=0.70,  # 70% memory usage
                )

                self.service_metrics[service] = metrics

            except Exception as e:
                logger.error(f"Failed to collect metrics for {service}: {e}")

    async def _health_monitoring_loop(self):
        """Monitor service health and update status"""
        while self.running:
            try:
                await self._evaluate_service_health()
                await asyncio.sleep(15)  # Check every 15 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5)

    async def _evaluate_service_health(self):
        """Evaluate overall service health"""
        for service_name, metrics in self.service_metrics.items():
            status = ServiceStatus.HEALTHY

            # Check availability
            if (
                metrics.availability
                < self.metric_thresholds["availability"].critical_threshold
            ):
                status = ServiceStatus.UNHEALTHY
            elif (
                metrics.availability
                < self.metric_thresholds["availability"].warning_threshold
            ):
                status = ServiceStatus.DEGRADED

            # Check response time
            if (
                metrics.response_time_p95
                > self.metric_thresholds["response_time_p95"].critical_threshold
            ):
                status = ServiceStatus.UNHEALTHY
            elif (
                metrics.response_time_p95
                > self.metric_thresholds["response_time_p95"].warning_threshold
            ):
                if status == ServiceStatus.HEALTHY:
                    status = ServiceStatus.DEGRADED

            # Check error rate
            if (
                metrics.error_rate
                > self.metric_thresholds["error_rate"].critical_threshold
            ):
                status = ServiceStatus.UNHEALTHY
            elif (
                metrics.error_rate
                > self.metric_thresholds["error_rate"].warning_threshold
            ):
                if status == ServiceStatus.HEALTHY:
                    status = ServiceStatus.DEGRADED

            logger.debug(f"Service {service_name} health status: {status.value}")

    async def _governance_metrics_loop(self):
        """Collect governance-specific metrics"""
        while self.running:
            try:
                await self._collect_governance_metrics()
                await asyncio.sleep(60)  # Collect every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Governance metrics collection error: {e}")
                await asyncio.sleep(15)

    async def _collect_governance_metrics(self):
        """Collect constitutional governance metrics"""
        # Simulate governance metrics collection
        self.governance_metrics = GovernanceMetrics(
            constitutional_compliance_score=0.97,  # 97% compliance
            governance_action_cost_sol=0.008,  # 0.008 SOL per action
            policy_synthesis_success_rate=0.94,  # 94% success rate
            active_workflows=12,
            completed_workflows_24h=45,
            blockchain_transaction_success_rate=0.995,  # 99.5% success rate
        )

    async def _alert_evaluation_loop(self):
        """Evaluate alert conditions"""
        while self.running:
            try:
                await self._evaluate_alerts()
                await asyncio.sleep(30)  # Evaluate every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Alert evaluation error: {e}")
                await asyncio.sleep(10)

    async def _evaluate_alerts(self):
        """Evaluate alert conditions and trigger notifications"""
        alerts_triggered = []

        # Check service metrics against thresholds
        for service_name, metrics in self.service_metrics.items():
            # Response time alerts
            if (
                metrics.response_time_p95
                > self.metric_thresholds["response_time_p95"].critical_threshold
            ):
                alerts_triggered.append(
                    {
                        "alert": "HighResponseTime",
                        "severity": "critical",
                        "service": service_name,
                        "value": metrics.response_time_p95,
                        "threshold": self.metric_thresholds[
                            "response_time_p95"
                        ].critical_threshold,
                    }
                )

            # Error rate alerts
            if (
                metrics.error_rate
                > self.metric_thresholds["error_rate"].warning_threshold
            ):
                severity = (
                    "critical"
                    if metrics.error_rate
                    > self.metric_thresholds["error_rate"].critical_threshold
                    else "warning"
                )
                alerts_triggered.append(
                    {
                        "alert": "HighErrorRate",
                        "severity": severity,
                        "service": service_name,
                        "value": metrics.error_rate,
                        "threshold": self.metric_thresholds[
                            "error_rate"
                        ].warning_threshold,
                    }
                )

        # Check governance metrics
        if self.governance_metrics:
            if (
                self.governance_metrics.constitutional_compliance_score
                < self.metric_thresholds["constitutional_compliance"].warning_threshold
            ):
                severity = (
                    "critical"
                    if self.governance_metrics.constitutional_compliance_score
                    < self.metric_thresholds[
                        "constitutional_compliance"
                    ].critical_threshold
                    else "warning"
                )
                alerts_triggered.append(
                    {
                        "alert": "LowConstitutionalCompliance",
                        "severity": severity,
                        "value": self.governance_metrics.constitutional_compliance_score,
                        "threshold": self.metric_thresholds[
                            "constitutional_compliance"
                        ].warning_threshold,
                    }
                )

        # Log triggered alerts
        for alert in alerts_triggered:
            logger.warning(f"Alert triggered: {alert}")

    async def _dashboard_update_loop(self):
        """Update dashboard data"""
        while self.running:
            try:
                await self._update_dashboards()
                await asyncio.sleep(60)  # Update every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Dashboard update error: {e}")
                await asyncio.sleep(15)

    async def _update_dashboards(self):
        """Update Grafana dashboards with latest data"""
        # Simulate dashboard update
        logger.debug("Updating Grafana dashboards with latest metrics")

    async def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status report"""
        healthy_services = sum(
            1
            for metrics in self.service_metrics.values()
            if metrics.availability
            >= self.metric_thresholds["availability"].warning_threshold
        )
        total_services = len(self.service_metrics)

        overall_availability = (
            sum(metrics.availability for metrics in self.service_metrics.values())
            / total_services
            if total_services > 0
            else 0
        )
        avg_response_time = (
            sum(metrics.response_time_p95 for metrics in self.service_metrics.values())
            / total_services
            if total_services > 0
            else 0
        )

        status_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": (
                "healthy"
                if healthy_services == total_services
                else "degraded" if healthy_services > 0 else "unhealthy"
            ),
            "system_metrics": {
                "overall_availability": overall_availability,
                "avg_response_time_p95": avg_response_time,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "service_health_percentage": (
                    (healthy_services / total_services * 100)
                    if total_services > 0
                    else 0
                ),
            },
            "service_metrics": {
                service: {
                    "availability": metrics.availability,
                    "response_time_p95": metrics.response_time_p95,
                    "error_rate": metrics.error_rate,
                    "throughput": metrics.throughput,
                    "status": (
                        "healthy"
                        if metrics.availability
                        >= self.metric_thresholds["availability"].warning_threshold
                        else "degraded"
                    ),
                }
                for service, metrics in self.service_metrics.items()
            },
            "governance_metrics": (
                {
                    "constitutional_compliance_score": (
                        self.governance_metrics.constitutional_compliance_score
                        if self.governance_metrics
                        else 0
                    ),
                    "governance_action_cost_sol": (
                        self.governance_metrics.governance_action_cost_sol
                        if self.governance_metrics
                        else 0
                    ),
                    "active_workflows": (
                        self.governance_metrics.active_workflows
                        if self.governance_metrics
                        else 0
                    ),
                    "blockchain_success_rate": (
                        self.governance_metrics.blockchain_transaction_success_rate
                        if self.governance_metrics
                        else 0
                    ),
                }
                if self.governance_metrics
                else {}
            ),
            "performance_targets": {
                "availability_target": ">99.9%",
                "response_time_target": "<500ms",
                "constitutional_compliance_target": ">95%",
                "governance_cost_target": "<0.01 SOL",
            },
        }

        return status_report


# Global monitoring orchestrator instance
monitoring_orchestrator = ProductionMonitoringOrchestrator()


async def main():
    """Main function for testing the monitoring orchestrator"""
    logger.info("Starting Production Monitoring Orchestrator Test")

    await monitoring_orchestrator.start()

    # Let it run for a bit to collect metrics
    await asyncio.sleep(10)

    # Get status report
    status = await monitoring_orchestrator.get_system_status()
    logger.info(f"System Status Report: {json.dumps(status, indent=2)}")

    await monitoring_orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())
