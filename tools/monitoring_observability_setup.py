#!/usr/bin/env python3
"""
Monitoring & Observability Enhancement for ACGS-1

Implements comprehensive monitoring, alerting, and observability
for constitutional governance operations with Prometheus, Grafana,
and custom metrics collection.
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass
from typing import Any

import aiohttp
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""

    prometheus_port: int = 9090
    grafana_port: int = 3000
    metrics_port: int = 8888
    scrape_interval: int = 15
    alert_threshold_response_time: float = 500.0  # ms
    alert_threshold_error_rate: float = 0.05  # 5%
    alert_threshold_availability: float = 0.995  # 99.5%


@dataclass
class ServiceMetrics:
    """Service metrics data."""

    name: str
    response_time_avg: float = 0.0
    response_time_p95: float = 0.0
    request_count: int = 0
    error_count: int = 0
    availability: float = 1.0
    constitutional_compliance_score: float = 1.0
    last_updated: float = 0.0

    @property
    def error_rate(self) -> float:
        return self.error_count / self.request_count if self.request_count > 0 else 0.0


class MonitoringObservabilityEnhancer:
    """
    Comprehensive monitoring and observability enhancer for ACGS-1.

    Provides Prometheus metrics, Grafana dashboards, alerting,
    and real-time monitoring of constitutional governance operations.
    """

    def __init__(self, config: MonitoringConfig = None):
        """Initialize monitoring enhancer."""
        self.config = config or MonitoringConfig()
        self.registry = CollectorRegistry()
        self.session: aiohttp.ClientSession | None = None

        # Service definitions
        self.services = [
            "auth_service",
            "ac_service",
            "integrity_service",
            "fv_service",
            "gs_service",
            "pgc_service",
            "ec_service",
            "research_service",
        ]

        # Initialize Prometheus metrics
        self._initialize_prometheus_metrics()

        # Service metrics storage
        self.service_metrics: dict[str, ServiceMetrics] = {
            service: ServiceMetrics(service) for service in self.services
        }

    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics."""
        # Response time metrics
        self.response_time_gauge = Gauge(
            "acgs_service_response_time_seconds",
            "Service response time in seconds",
            ["service", "endpoint"],
            registry=self.registry,
        )

        self.response_time_histogram = Histogram(
            "acgs_service_response_time_histogram",
            "Service response time histogram",
            ["service", "endpoint"],
            registry=self.registry,
        )

        # Request metrics
        self.request_counter = Counter(
            "acgs_service_requests_total",
            "Total service requests",
            ["service", "endpoint", "status"],
            registry=self.registry,
        )

        # Error metrics
        self.error_counter = Counter(
            "acgs_service_errors_total",
            "Total service errors",
            ["service", "error_type"],
            registry=self.registry,
        )

        # Availability metrics
        self.availability_gauge = Gauge(
            "acgs_service_availability",
            "Service availability (0-1)",
            ["service"],
            registry=self.registry,
        )

        # Constitutional compliance metrics
        self.constitutional_compliance_gauge = Gauge(
            "acgs_constitutional_compliance_score",
            "Constitutional compliance score (0-1)",
            ["service"],
            registry=self.registry,
        )

        # Governance operation metrics
        self.governance_operations_counter = Counter(
            "acgs_governance_operations_total",
            "Total governance operations",
            ["operation_type", "status"],
            registry=self.registry,
        )

        # System health metrics
        self.system_health_gauge = Gauge(
            "acgs_system_health_score",
            "Overall system health score (0-1)",
            registry=self.registry,
        )

        logger.info("Prometheus metrics initialized")

    async def initialize(self):
        """Initialize monitoring system."""
        connector = aiohttp.TCPConnector(limit=50)
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)

        logger.info("Monitoring observability enhancer initialized")

    async def collect_service_metrics(self):
        """Collect metrics from all ACGS services."""
        logger.info("📊 Collecting service metrics...")

        for service_name in self.services:
            await self._collect_single_service_metrics(service_name)

        # Update system-wide metrics
        await self._update_system_metrics()

    async def _collect_single_service_metrics(self, service_name: str):
        """Collect metrics from a single service."""
        service_port = 8000 + self.services.index(service_name)
        base_url = f"http://localhost:{service_port}"

        metrics = self.service_metrics[service_name]

        try:
            # Health check
            start_time = time.time()
            async with self.session.get(f"{base_url}/health") as response:
                response_time = time.time() - start_time

                if response.status == 200:
                    metrics.availability = 1.0
                    metrics.response_time_avg = response_time

                    # Update Prometheus metrics
                    self.response_time_gauge.labels(
                        service=service_name, endpoint="health"
                    ).set(response_time)

                    self.response_time_histogram.labels(
                        service=service_name, endpoint="health"
                    ).observe(response_time)

                    self.request_counter.labels(
                        service=service_name, endpoint="health", status="200"
                    ).inc()

                    self.availability_gauge.labels(service=service_name).set(1.0)

                else:
                    metrics.availability = 0.0
                    metrics.error_count += 1

                    self.error_counter.labels(
                        service=service_name, error_type="health_check_failed"
                    ).inc()

                    self.availability_gauge.labels(service=service_name).set(0.0)

            # Collect constitutional compliance metrics for relevant services
            if service_name in ["pgc_service", "ac_service", "fv_service"]:
                await self._collect_constitutional_metrics(service_name, base_url)

            metrics.request_count += 1
            metrics.last_updated = time.time()

        except Exception as e:
            logger.warning(f"Failed to collect metrics from {service_name}: {e}")
            metrics.availability = 0.0
            metrics.error_count += 1

            self.error_counter.labels(
                service=service_name, error_type="connection_failed"
            ).inc()

            self.availability_gauge.labels(service=service_name).set(0.0)

    async def _collect_constitutional_metrics(self, service_name: str, base_url: str):
        """Collect constitutional compliance metrics."""
        try:
            if service_name == "pgc_service":
                # Test constitutional validation
                start_time = time.time()
                async with self.session.get(
                    f"{base_url}/api/v1/constitutional/validate"
                ) as response:
                    response_time = time.time() - start_time

                    if response.status == 200:
                        data = await response.json()
                        compliance_score = data.get("validation_result", {}).get(
                            "compliance_score", 1.0
                        )

                        self.constitutional_compliance_gauge.labels(
                            service=service_name
                        ).set(compliance_score)

                        self.service_metrics[
                            service_name
                        ].constitutional_compliance_score = compliance_score

                        # Record governance operation
                        self.governance_operations_counter.labels(
                            operation_type="constitutional_validation", status="success"
                        ).inc()

                        # Update response time metrics
                        self.response_time_gauge.labels(
                            service=service_name, endpoint="constitutional_validate"
                        ).set(response_time)

            elif service_name == "ac_service":
                # Test constitutional council
                start_time = time.time()
                async with self.session.get(
                    f"{base_url}/api/v1/constitutional-council/members"
                ) as response:
                    response_time = time.time() - start_time

                    if response.status == 200:
                        data = await response.json()
                        # Calculate compliance based on council configuration
                        required_sigs = data.get("required_signatures", 0)
                        data.get("total_members", 0)
                        compliance_score = (
                            min(required_sigs / 5, 1.0) if required_sigs > 0 else 0.0
                        )

                        self.constitutional_compliance_gauge.labels(
                            service=service_name
                        ).set(compliance_score)

                        self.service_metrics[
                            service_name
                        ].constitutional_compliance_score = compliance_score

        except Exception as e:
            logger.debug(
                f"Constitutional metrics collection failed for {service_name}: {e}"
            )

    async def _update_system_metrics(self):
        """Update system-wide metrics."""
        # Calculate overall system health
        healthy_services = sum(
            1 for metrics in self.service_metrics.values() if metrics.availability > 0.5
        )
        total_services = len(self.service_metrics)
        system_health = healthy_services / total_services

        self.system_health_gauge.set(system_health)

        # Calculate average constitutional compliance
        constitutional_services = ["pgc_service", "ac_service", "fv_service"]
        compliance_scores = [
            self.service_metrics[service].constitutional_compliance_score
            for service in constitutional_services
            if service in self.service_metrics
        ]

        if compliance_scores:
            avg_compliance = sum(compliance_scores) / len(compliance_scores)
            logger.info(f"Average constitutional compliance: {avg_compliance:.3f}")

    async def generate_monitoring_report(self) -> dict[str, Any]:
        """Generate comprehensive monitoring report."""
        await self.collect_service_metrics()

        # Calculate system-wide statistics
        total_requests = sum(m.request_count for m in self.service_metrics.values())
        total_errors = sum(m.error_count for m in self.service_metrics.values())
        avg_response_time = sum(
            m.response_time_avg for m in self.service_metrics.values()
        ) / len(self.service_metrics)

        healthy_services = [
            name for name, m in self.service_metrics.items() if m.availability > 0.5
        ]

        # Generate alerts
        alerts = self._generate_alerts()

        report = {
            "timestamp": time.time(),
            "system_overview": {
                "total_services": len(self.services),
                "healthy_services": len(healthy_services),
                "availability_percentage": (len(healthy_services) / len(self.services))
                * 100,
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate": (
                    total_errors / total_requests if total_requests > 0 else 0.0
                ),
                "avg_response_time_ms": avg_response_time * 1000,
            },
            "service_metrics": {
                name: asdict(metrics) for name, metrics in self.service_metrics.items()
            },
            "constitutional_governance": {
                "pgc_compliance": self.service_metrics[
                    "pgc_service"
                ].constitutional_compliance_score,
                "ac_compliance": self.service_metrics[
                    "ac_service"
                ].constitutional_compliance_score,
                "fv_compliance": self.service_metrics.get(
                    "fv_service", ServiceMetrics("fv_service")
                ).constitutional_compliance_score,
                "overall_compliance": sum(
                    self.service_metrics[s].constitutional_compliance_score
                    for s in ["pgc_service", "ac_service", "fv_service"]
                    if s in self.service_metrics
                )
                / 3,
            },
            "alerts": alerts,
            "performance_targets": {
                "response_time_target_ms": self.config.alert_threshold_response_time,
                "error_rate_target": self.config.alert_threshold_error_rate,
                "availability_target": self.config.alert_threshold_availability,
                "targets_met": len(alerts) == 0,
            },
        }

        return report

    def _generate_alerts(self) -> list[dict[str, Any]]:
        """Generate alerts based on thresholds."""
        alerts = []

        for service_name, metrics in self.service_metrics.items():
            # Response time alerts
            if (
                metrics.response_time_avg * 1000
                > self.config.alert_threshold_response_time
            ):
                alerts.append(
                    {
                        "severity": "warning",
                        "service": service_name,
                        "metric": "response_time",
                        "value": metrics.response_time_avg * 1000,
                        "threshold": self.config.alert_threshold_response_time,
                        "message": f"{service_name} response time {metrics.response_time_avg * 1000:.1f}ms exceeds threshold",
                    }
                )

            # Error rate alerts
            if metrics.error_rate > self.config.alert_threshold_error_rate:
                alerts.append(
                    {
                        "severity": "critical",
                        "service": service_name,
                        "metric": "error_rate",
                        "value": metrics.error_rate,
                        "threshold": self.config.alert_threshold_error_rate,
                        "message": f"{service_name} error rate {metrics.error_rate:.3f} exceeds threshold",
                    }
                )

            # Availability alerts
            if metrics.availability < self.config.alert_threshold_availability:
                alerts.append(
                    {
                        "severity": "critical",
                        "service": service_name,
                        "metric": "availability",
                        "value": metrics.availability,
                        "threshold": self.config.alert_threshold_availability,
                        "message": f"{service_name} availability {metrics.availability:.3f} below threshold",
                    }
                )

        return alerts

    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        return generate_latest(self.registry).decode("utf-8")

    async def setup_grafana_dashboard(self):
        """Setup Grafana dashboard configuration."""
        dashboard_config = {
            "dashboard": {
                "title": "ACGS-1 Constitutional Governance System",
                "tags": ["acgs", "constitutional", "governance"],
                "timezone": "browser",
                "panels": [
                    {
                        "title": "Service Availability",
                        "type": "stat",
                        "targets": [{"expr": "acgs_service_availability"}],
                        "fieldConfig": {
                            "defaults": {
                                "min": 0,
                                "max": 1,
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "yellow", "value": 0.95},
                                        {"color": "green", "value": 0.995},
                                    ]
                                },
                            }
                        },
                    },
                    {
                        "title": "Response Times",
                        "type": "graph",
                        "targets": [{"expr": "acgs_service_response_time_seconds"}],
                        "yAxes": [{"unit": "s"}],
                    },
                    {
                        "title": "Constitutional Compliance",
                        "type": "stat",
                        "targets": [{"expr": "acgs_constitutional_compliance_score"}],
                        "fieldConfig": {
                            "defaults": {
                                "min": 0,
                                "max": 1,
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "yellow", "value": 0.9},
                                        {"color": "green", "value": 0.95},
                                    ]
                                },
                            }
                        },
                    },
                ],
            }
        }

        # Save dashboard configuration
        with open("grafana_dashboard.json", "w") as f:
            json.dump(dashboard_config, f, indent=2)

        logger.info("Grafana dashboard configuration saved")

    async def close(self):
        """Close monitoring enhancer."""
        if self.session:
            await self.session.close()
        logger.info("Monitoring observability enhancer closed")


async def main():
    """Main monitoring setup execution."""
    logger.info("🚀 Starting ACGS-1 Monitoring & Observability Enhancement")

    enhancer = MonitoringObservabilityEnhancer()

    try:
        await enhancer.initialize()

        # Generate monitoring report
        report = await enhancer.generate_monitoring_report()

        # Save report
        with open("monitoring_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)

        # Setup Grafana dashboard
        await enhancer.setup_grafana_dashboard()

        # Save Prometheus metrics
        with open("prometheus_metrics.txt", "w") as f:
            f.write(enhancer.get_prometheus_metrics())

        # Display results
        print("\n" + "=" * 80)
        print("🏁 ACGS-1 Monitoring & Observability Enhancement Results")
        print("=" * 80)

        overview = report["system_overview"]
        print(
            f"System Availability: {overview['availability_percentage']:.1f}% ({overview['healthy_services']}/{overview['total_services']} services)"
        )
        print(f"Average Response Time: {overview['avg_response_time_ms']:.1f}ms")
        print(f"Error Rate: {overview['error_rate']:.3f}")

        constitutional = report["constitutional_governance"]
        print("\n🏛️ Constitutional Governance:")
        print(f"   PGC Compliance: {constitutional['pgc_compliance']:.3f}")
        print(f"   AC Compliance: {constitutional['ac_compliance']:.3f}")
        print(f"   Overall Compliance: {constitutional['overall_compliance']:.3f}")

        alerts = report["alerts"]
        if alerts:
            print(f"\n⚠️ Active Alerts ({len(alerts)}):")
            for alert in alerts[:5]:  # Show first 5 alerts
                print(f"   {alert['severity'].upper()}: {alert['message']}")
        else:
            print("\n✅ No active alerts - all targets met!")

        targets = report["performance_targets"]
        print("\n📊 Performance Targets:")
        print(f"   Response Time: <{targets['response_time_target_ms']}ms")
        print(f"   Error Rate: <{targets['error_rate_target']:.1%}")
        print(f"   Availability: >{targets['availability_target']:.1%}")
        print(f"   Targets Met: {'✅ YES' if targets['targets_met'] else '❌ NO'}")

        print("\n📄 Reports saved:")
        print("   - monitoring_report.json")
        print("   - grafana_dashboard.json")
        print("   - prometheus_metrics.txt")
        print("=" * 80)

    except Exception as e:
        logger.error(f"Monitoring enhancement failed: {e}")
        raise
    finally:
        await enhancer.close()


if __name__ == "__main__":
    asyncio.run(main())
