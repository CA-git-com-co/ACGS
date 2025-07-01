#!/usr/bin/env python3
"""
Error Rate Validation and SLA Compliance Testing for ACGS
Implements automated monitoring and validation of error rate SLA targets.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

import aiohttp
import numpy as np
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


@dataclass
class SLATarget:
    """SLA target definition."""

    metric_name: str
    target_value: float
    operator: str  # '<', '>', '<=', '>='
    unit: str
    description: str


@dataclass
class ValidationResult:
    """Result of SLA validation."""

    timestamp: datetime
    service_name: str
    metric_name: str
    current_value: float
    target_value: float
    compliant: bool
    deviation_percentage: float
    constitutional_compliance_score: float | None = None


@dataclass
class ContinuousMonitoringSession:
    """Continuous monitoring session data."""

    session_id: str
    start_time: datetime
    duration_hours: int
    services: list[str]
    sla_targets: list[SLATarget]
    results: list[ValidationResult] = field(default_factory=list)
    alerts_triggered: int = 0
    compliance_rate: float = 0.0


class ErrorRateValidator:
    """Automated error rate validation and SLA compliance testing."""

    def __init__(self):
        self.registry = CollectorRegistry()
        self.setup_metrics()

        # SLA targets for ACGS
        self.sla_targets = {
            "error_rate": SLATarget(
                metric_name="error_rate",
                target_value=0.01,  # 1%
                operator="<",
                unit="percentage",
                description="Service error rate must be less than 1%",
            ),
            "response_time_p95": SLATarget(
                metric_name="response_time_p95",
                target_value=0.5,  # 500ms
                operator="<",
                unit="seconds",
                description="95th percentile response time must be less than 500ms",
            ),
            "constitutional_compliance": SLATarget(
                metric_name="constitutional_compliance",
                target_value=0.95,  # 95%
                operator=">=",
                unit="percentage",
                description="Constitutional compliance must be at least 95%",
            ),
            "availability": SLATarget(
                metric_name="availability",
                target_value=0.999,  # 99.9%
                operator=">=",
                unit="percentage",
                description="Service availability must be at least 99.9%",
            ),
        }

        # ACGS services
        self.services = {
            "auth-service": 8000,
            "ac-service": 8001,
            "integrity-service": 8002,
            "fv-service": 8003,
            "gs-service": 8004,
            "pgc-service": 8005,
            "ec-service": 8006,
        }

        # Monitoring sessions
        self.active_sessions: dict[str, ContinuousMonitoringSession] = {}

        logger.info("Error Rate Validator initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics."""
        self.sla_compliance_gauge = Gauge(
            "acgs_sla_compliance",
            "SLA compliance status (1=compliant, 0=non-compliant)",
            ["service", "metric"],
            registry=self.registry,
        )

        self.sla_violations_total = Counter(
            "acgs_sla_violations_total",
            "Total SLA violations",
            ["service", "metric"],
            registry=self.registry,
        )

        self.validation_duration = Histogram(
            "acgs_sla_validation_duration_seconds",
            "Duration of SLA validation checks",
            ["service"],
            registry=self.registry,
        )

        self.constitutional_hash_validation = Gauge(
            "acgs_constitutional_hash_validation",
            "Constitutional hash validation status",
            ["service", "hash"],
            registry=self.registry,
        )

    async def start_validator(self):
        """Start the error rate validator."""
        logger.info("Starting error rate validator...")

        # Start Prometheus metrics server
        start_http_server(8091, registry=self.registry)
        logger.info("SLA validation metrics server started on port 8091")

        # Start validation tasks
        tasks = [
            asyncio.create_task(self.continuous_validation_loop()),
            asyncio.create_task(self.constitutional_hash_monitor()),
            asyncio.create_task(self.session_manager()),
        ]

        await asyncio.gather(*tasks)

    async def continuous_validation_loop(self):
        """Continuous SLA validation loop."""
        while True:
            try:
                await asyncio.sleep(30)  # Validate every 30 seconds

                for service_name in self.services.keys():
                    await self.validate_service_sla(service_name)

            except Exception as e:
                logger.error(f"Error in validation loop: {e}")

    async def validate_service_sla(self, service_name: str):
        """Validate SLA compliance for a specific service."""
        start_time = time.time()

        try:
            # Get current metrics for the service
            metrics = await self.collect_service_metrics(service_name)

            # Validate each SLA target
            for target_name, target in self.sla_targets.items():
                if target_name in metrics:
                    result = self.evaluate_sla_compliance(
                        service_name, target, metrics[target_name]
                    )

                    # Update metrics
                    compliance_value = 1.0 if result.compliant else 0.0
                    self.sla_compliance_gauge.labels(
                        service=service_name, metric=target_name
                    ).set(compliance_value)

                    if not result.compliant:
                        self.sla_violations_total.labels(
                            service=service_name, metric=target_name
                        ).inc()

                        logger.warning(
                            f"SLA violation: {service_name} {target_name} "
                            f"current={result.current_value:.4f} "
                            f"target={result.target_value:.4f}"
                        )

                    # Add to active monitoring sessions
                    for session in self.active_sessions.values():
                        if service_name in session.services:
                            session.results.append(result)

            # Record validation duration
            duration = time.time() - start_time
            self.validation_duration.labels(service=service_name).observe(duration)

        except Exception as e:
            logger.error(f"Failed to validate SLA for {service_name}: {e}")

    async def collect_service_metrics(self, service_name: str) -> dict[str, float]:
        """Collect current metrics for a service."""
        metrics = {}

        try:
            async with aiohttp.ClientSession() as session:
                # Get error rate from Prometheus
                error_rate = await self.get_prometheus_metric(
                    session, f'acgs_error_rate_by_service{{service="{service_name}"}}'
                )
                if error_rate is not None:
                    metrics["error_rate"] = error_rate

                # Get response time P95
                response_time_p95 = await self.get_prometheus_metric(
                    session,
                    f"histogram_quantile(0.95, "
                    f'rate(acgs_http_request_duration_seconds_bucket{{service="{service_name}"}}[5m]))',
                )
                if response_time_p95 is not None:
                    metrics["response_time_p95"] = response_time_p95

                # Get constitutional compliance
                compliance = await self.get_constitutional_compliance(
                    session, service_name
                )
                if compliance is not None:
                    metrics["constitutional_compliance"] = compliance

                # Get availability
                availability = await self.get_service_availability(
                    session, service_name
                )
                if availability is not None:
                    metrics["availability"] = availability

        except Exception as e:
            logger.error(f"Failed to collect metrics for {service_name}: {e}")

        return metrics

    async def get_prometheus_metric(
        self, session: aiohttp.ClientSession, query: str
    ) -> float | None:
        """Get a metric value from Prometheus."""
        try:
            url = "http://localhost:9090/api/v1/query"
            async with session.get(url, params={"query": query}, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["data"]["result"]:
                        return float(data["data"]["result"][0]["value"][1])
        except Exception as e:
            logger.debug(f"Failed to get Prometheus metric: {e}")

        return None

    async def get_constitutional_compliance(
        self, session: aiohttp.ClientSession, service_name: str
    ) -> float | None:
        """Get constitutional compliance score for a service."""
        if service_name not in ["ac-service", "pgc-service"]:
            return (
                1.0  # Services without constitutional validation default to compliant
            )

        try:
            port = self.services[service_name]
            url = f"http://localhost:{port}/api/v1/metrics/constitutional"

            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("compliance_score", 1.0)

        except Exception as e:
            logger.debug(
                f"Failed to get constitutional compliance for {service_name}: {e}"
            )

        return None

    async def get_service_availability(
        self, session: aiohttp.ClientSession, service_name: str
    ) -> float | None:
        """Get service availability."""
        try:
            port = self.services[service_name]
            url = f"http://localhost:{port}/health"

            async with session.get(url, timeout=5) as response:
                return 1.0 if response.status == 200 else 0.0

        except Exception:
            return 0.0

    def evaluate_sla_compliance(
        self, service_name: str, target: SLATarget, current_value: float
    ) -> ValidationResult:
        """Evaluate SLA compliance for a metric."""
        compliant = False

        if target.operator == "<":
            compliant = current_value < target.target_value
        elif target.operator == ">":
            compliant = current_value > target.target_value
        elif target.operator == "<=":
            compliant = current_value <= target.target_value
        elif target.operator == ">=":
            compliant = current_value >= target.target_value

        # Calculate deviation percentage
        if target.target_value != 0:
            deviation_percentage = (
                abs(current_value - target.target_value) / target.target_value * 100
            )
        else:
            deviation_percentage = 0.0

        return ValidationResult(
            timestamp=datetime.now(timezone.utc),
            service_name=service_name,
            metric_name=target.metric_name,
            current_value=current_value,
            target_value=target.target_value,
            compliant=compliant,
            deviation_percentage=deviation_percentage,
        )

    async def constitutional_hash_monitor(self):
        """Monitor constitutional hash validation across services."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                for service_name in ["ac-service", "pgc-service"]:
                    await self.validate_constitutional_hash(service_name)

            except Exception as e:
                logger.error(f"Error in constitutional hash monitoring: {e}")

    async def validate_constitutional_hash(self, service_name: str):
        """Validate constitutional hash for a service."""
        try:
            port = self.services[service_name]
            async with aiohttp.ClientSession() as session:
                url = f"http://localhost:{port}/api/v1/constitutional/hash"

                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        current_hash = data.get("constitutional_hash", "")

                        # Validate hash
                        hash_valid = current_hash == CONSTITUTIONAL_HASH

                        self.constitutional_hash_validation.labels(
                            service=service_name, hash=CONSTITUTIONAL_HASH
                        ).set(1.0 if hash_valid else 0.0)

                        if not hash_valid:
                            logger.error(
                                f"Constitutional hash mismatch in {service_name}: "
                                f"expected {CONSTITUTIONAL_HASH}, got {current_hash}"
                            )
                    else:
                        self.constitutional_hash_validation.labels(
                            service=service_name, hash=CONSTITUTIONAL_HASH
                        ).set(0.0)

        except Exception as e:
            logger.debug(
                f"Failed to validate constitutional hash for {service_name}: {e}"
            )
            self.constitutional_hash_validation.labels(
                service=service_name, hash=CONSTITUTIONAL_HASH
            ).set(0.0)

    async def start_72_hour_monitoring(self, services: list[str] | None = None) -> str:
        """Start a 72-hour continuous monitoring session."""
        session_id = f"72h_monitor_{int(time.time())}"

        if services is None:
            services = list(self.services.keys())

        session = ContinuousMonitoringSession(
            session_id=session_id,
            start_time=datetime.now(timezone.utc),
            duration_hours=72,
            services=services,
            sla_targets=list(self.sla_targets.values()),
        )

        self.active_sessions[session_id] = session

        logger.info(f"Started 72-hour monitoring session: {session_id}")
        return session_id

    async def session_manager(self):
        """Manage monitoring sessions."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                current_time = datetime.now(timezone.utc)
                sessions_to_remove = []

                for session_id, session in self.active_sessions.items():
                    # Check if session has expired
                    session_duration = current_time - session.start_time
                    if (
                        session_duration.total_seconds()
                        >= session.duration_hours * 3600
                    ):
                        # Generate final report
                        await self.generate_session_report(session)
                        sessions_to_remove.append(session_id)
                    else:
                        # Update session statistics
                        await self.update_session_stats(session)

                # Remove expired sessions
                for session_id in sessions_to_remove:
                    del self.active_sessions[session_id]
                    logger.info(f"Completed monitoring session: {session_id}")

            except Exception as e:
                logger.error(f"Error in session management: {e}")

    async def update_session_stats(self, session: ContinuousMonitoringSession):
        """Update statistics for a monitoring session."""
        if not session.results:
            return

        # Calculate compliance rate
        total_checks = len(session.results)
        compliant_checks = sum(1 for result in session.results if result.compliant)
        session.compliance_rate = (
            compliant_checks / total_checks if total_checks > 0 else 0.0
        )

        # Count alerts (non-compliant results)
        session.alerts_triggered = total_checks - compliant_checks

    async def generate_session_report(self, session: ContinuousMonitoringSession):
        """Generate a final report for a monitoring session."""
        await self.update_session_stats(session)

        # Calculate detailed statistics
        service_stats = {}
        metric_stats = {}

        for result in session.results:
            # Service statistics
            if result.service_name not in service_stats:
                service_stats[result.service_name] = {
                    "total_checks": 0,
                    "compliant_checks": 0,
                    "violations": [],
                }

            service_stats[result.service_name]["total_checks"] += 1
            if result.compliant:
                service_stats[result.service_name]["compliant_checks"] += 1
            else:
                service_stats[result.service_name]["violations"].append(result)

            # Metric statistics
            if result.metric_name not in metric_stats:
                metric_stats[result.metric_name] = {
                    "total_checks": 0,
                    "compliant_checks": 0,
                    "values": [],
                }

            metric_stats[result.metric_name]["total_checks"] += 1
            if result.compliant:
                metric_stats[result.metric_name]["compliant_checks"] += 1
            metric_stats[result.metric_name]["values"].append(result.current_value)

        # Generate report
        report = {
            "session_id": session.session_id,
            "start_time": session.start_time.isoformat(),
            "duration_hours": session.duration_hours,
            "services_monitored": session.services,
            "overall_compliance_rate": session.compliance_rate,
            "total_alerts": session.alerts_triggered,
            "service_statistics": {
                service: {
                    "compliance_rate": stats["compliant_checks"]
                    / stats["total_checks"],
                    "total_violations": len(stats["violations"]),
                    "violation_details": [
                        {
                            "metric": v.metric_name,
                            "timestamp": v.timestamp.isoformat(),
                            "current_value": v.current_value,
                            "target_value": v.target_value,
                            "deviation_percentage": v.deviation_percentage,
                        }
                        for v in stats["violations"][:10]  # Limit to first 10
                    ],
                }
                for service, stats in service_stats.items()
            },
            "metric_statistics": {
                metric: {
                    "compliance_rate": stats["compliant_checks"]
                    / stats["total_checks"],
                    "average_value": np.mean(stats["values"]),
                    "min_value": np.min(stats["values"]),
                    "max_value": np.max(stats["values"]),
                    "std_deviation": np.std(stats["values"]),
                }
                for metric, stats in metric_stats.items()
            },
        }

        # Save report
        await self.save_session_report(report)

        # Log summary
        logger.info(
            f"Session {session.session_id} completed: "
            f"{session.compliance_rate:.2%} compliance rate, "
            f"{session.alerts_triggered} alerts triggered"
        )

    async def save_session_report(self, report: dict):
        """Save session report to file."""
        try:
            import os

            report_dir = "infrastructure/monitoring/sla_validation/reports"
            os.makedirs(report_dir, exist_ok=True)

            filename = f"{report_dir}/sla_validation_{report['session_id']}.json"
            with open(filename, "w") as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"Session report saved: {filename}")

        except Exception as e:
            logger.error(f"Failed to save session report: {e}")

    def get_active_sessions(self) -> dict[str, dict]:
        """Get information about active monitoring sessions."""
        return {
            session_id: {
                "start_time": session.start_time.isoformat(),
                "duration_hours": session.duration_hours,
                "services": session.services,
                "compliance_rate": session.compliance_rate,
                "alerts_triggered": session.alerts_triggered,
                "results_count": len(session.results),
            }
            for session_id, session in self.active_sessions.items()
        }


if __name__ == "__main__":
    validator = ErrorRateValidator()
    asyncio.run(validator.start_validator())
