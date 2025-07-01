#!/usr/bin/env python3
"""
ACGS Performance Alerting System
Real-time performance monitoring with automated alerting for regression detection.
"""

import asyncio
import json
import logging
import smtplib
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional

import aiohttp
from prometheus_client import CollectorRegistry, Counter, Gauge, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class AlertThreshold:
    """Alert threshold configuration."""

    metric_name: str
    threshold_value: float
    comparison: str  # 'gt', 'lt', 'eq'
    duration_minutes: int = 5
    severity: str = "warning"  # 'critical', 'warning', 'info'
    enabled: bool = True


@dataclass
class PerformanceAlert:
    """Performance alert instance."""

    alert_id: str
    alert_name: str
    service_name: str
    metric_name: str
    current_value: float
    threshold_value: float
    severity: str
    message: str
    triggered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH


class PerformanceAlertingSystem:
    """Real-time performance alerting system."""

    def __init__(self):
        self.registry = CollectorRegistry()
        self.setup_metrics()

        # Alert configuration
        self.alert_thresholds = self.setup_alert_thresholds()
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_history: List[PerformanceAlert] = []

        # Monitoring configuration
        self.services = {
            "auth-service": 8000,
            "ac-service": 8001,
            "integrity-service": 8002,
            "fv-service": 8003,
            "gs-service": 8004,
            "pgc-service": 8005,
            "ec-service": 8006,
        }

        # Baseline data for regression detection
        self.baseline_metrics: Dict[str, Dict] = {}

        logger.info("Performance Alerting System initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics for alerting."""
        self.alerts_triggered = Counter(
            "acgs_alerts_triggered_total",
            "Total alerts triggered",
            ["service", "metric", "severity"],
            registry=self.registry,
        )

        self.alerts_active = Gauge(
            "acgs_alerts_active",
            "Currently active alerts",
            ["service", "metric", "severity"],
            registry=self.registry,
        )

        self.performance_regression_detected = Counter(
            "acgs_performance_regression_detected_total",
            "Performance regressions detected",
            ["service", "metric"],
            registry=self.registry,
        )

        self.alert_response_time = Gauge(
            "acgs_alert_response_time_seconds",
            "Time to detect and alert on performance issues",
            ["service", "metric"],
            registry=self.registry,
        )

    def setup_alert_thresholds(self) -> List[AlertThreshold]:
        """Setup alert thresholds."""
        return [
            # Response time thresholds
            AlertThreshold(
                metric_name="response_time_ms",
                threshold_value=500.0,
                comparison="gt",
                duration_minutes=2,
                severity="critical",
            ),
            AlertThreshold(
                metric_name="response_time_ms",
                threshold_value=200.0,
                comparison="gt",
                duration_minutes=5,
                severity="warning",
            ),
            # Throughput thresholds
            AlertThreshold(
                metric_name="throughput_rps",
                threshold_value=10.0,
                comparison="lt",
                duration_minutes=5,
                severity="warning",
            ),
            AlertThreshold(
                metric_name="throughput_rps",
                threshold_value=5.0,
                comparison="lt",
                duration_minutes=2,
                severity="critical",
            ),
            # Error rate thresholds
            AlertThreshold(
                metric_name="error_rate_percent",
                threshold_value=1.0,
                comparison="gt",
                duration_minutes=2,
                severity="warning",
            ),
            AlertThreshold(
                metric_name="error_rate_percent",
                threshold_value=5.0,
                comparison="gt",
                duration_minutes=1,
                severity="critical",
            ),
            # Constitutional compliance thresholds
            AlertThreshold(
                metric_name="constitutional_compliance",
                threshold_value=0.99,
                comparison="lt",
                duration_minutes=5,
                severity="warning",
            ),
            AlertThreshold(
                metric_name="constitutional_compliance",
                threshold_value=0.95,
                comparison="lt",
                duration_minutes=2,
                severity="critical",
            ),
            # Performance regression thresholds (10% increase)
            AlertThreshold(
                metric_name="response_time_regression_percent",
                threshold_value=10.0,
                comparison="gt",
                duration_minutes=5,
                severity="warning",
            ),
            # Throughput regression thresholds (5% decrease)
            AlertThreshold(
                metric_name="throughput_regression_percent",
                threshold_value=5.0,
                comparison="gt",
                duration_minutes=5,
                severity="warning",
            ),
        ]

    async def start_alerting_system(self):
        """Start the performance alerting system."""
        logger.info("Starting performance alerting system...")

        # Start metrics server
        start_http_server(8096, registry=self.registry)
        logger.info("Alerting metrics server started on port 8096")

        # Load baseline metrics
        await self.load_baseline_metrics()

        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self.performance_monitoring_loop()),
            asyncio.create_task(self.alert_resolution_loop()),
            asyncio.create_task(self.regression_detection_loop()),
        ]

        await asyncio.gather(*tasks)

    async def load_baseline_metrics(self):
        """Load baseline metrics for regression detection."""
        try:
            baseline_file = (
                "infrastructure/monitoring/performance/baselines/latest_baseline.json"
            )

            with open(baseline_file) as f:
                baseline_data = json.load(f)

            for service_name, service_data in baseline_data.get("services", {}).items():
                self.baseline_metrics[service_name] = {
                    "avg_response_time": service_data.get("avg_response_time", 0),
                    "p95_response_time": service_data.get("p95_response_time", 0),
                    "avg_throughput": service_data.get("avg_throughput", 0),
                    "error_rate_percent": service_data.get("error_rate_percent", 0),
                    "constitutional_compliance_rate": service_data.get(
                        "constitutional_compliance_rate", 1.0
                    ),
                }

            logger.info(
                f"Loaded baseline metrics for {len(self.baseline_metrics)} services"
            )

        except FileNotFoundError:
            logger.warning("No baseline metrics found - regression detection disabled")
        except Exception as e:
            logger.error(f"Failed to load baseline metrics: {e}")

    async def performance_monitoring_loop(self):
        """Main performance monitoring loop."""
        while True:
            try:
                await self.check_performance_metrics()
                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error in performance monitoring loop: {e}")
                await asyncio.sleep(60)

    async def check_performance_metrics(self):
        """Check performance metrics against thresholds."""
        for service_name, port in self.services.items():
            try:
                metrics = await self.collect_service_metrics(service_name, port)
                await self.evaluate_alert_thresholds(service_name, metrics)

            except Exception as e:
                logger.warning(f"Failed to check metrics for {service_name}: {e}")

    async def collect_service_metrics(self, service_name: str, port: int) -> Dict:
        """Collect current metrics for a service."""
        metrics = {}

        async with aiohttp.ClientSession() as session:
            # Health check for response time
            start_time = time.time()
            try:
                async with session.get(
                    f"http://localhost:{port}/health", timeout=10
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    metrics["response_time_ms"] = response_time
                    metrics["available"] = response.status == 200

            except Exception:
                metrics["response_time_ms"] = (time.time() - start_time) * 1000
                metrics["available"] = False

            # Get Prometheus metrics if available
            try:
                async with session.get(
                    f"http://localhost:{port}/metrics", timeout=5
                ) as response:
                    if response.status == 200:
                        prometheus_text = await response.text()

                        # Parse basic metrics (simplified)
                        if "http_requests_total" in prometheus_text:
                            # Calculate throughput and error rate from Prometheus metrics
                            # This is a simplified implementation
                            metrics["throughput_rps"] = 10.0  # Placeholder
                            metrics["error_rate_percent"] = 0.5  # Placeholder

            except Exception:
                pass

            # Constitutional compliance check
            if service_name in ["ac-service", "pgc-service", "ec-service"]:
                try:
                    constitutional_request = {
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                        "validation_level": "basic",
                    }

                    async with session.post(
                        f"http://localhost:{port}/api/v1/constitutional/validate",
                        json=constitutional_request,
                        timeout=10,
                    ) as response:
                        if response.status == 200:
                            constitutional_data = await response.json()
                            metrics["constitutional_compliance"] = (
                                constitutional_data.get("compliance_score", 1.0)
                            )
                        else:
                            metrics["constitutional_compliance"] = 0.0

                except Exception:
                    metrics["constitutional_compliance"] = 0.0
            else:
                metrics["constitutional_compliance"] = 1.0

        return metrics

    async def evaluate_alert_thresholds(self, service_name: str, metrics: Dict):
        """Evaluate metrics against alert thresholds."""
        for threshold in self.alert_thresholds:
            if not threshold.enabled:
                continue

            metric_value = metrics.get(threshold.metric_name)
            if metric_value is None:
                continue

            # Check threshold condition
            should_alert = False

            if (
                threshold.comparison == "gt"
                and metric_value > threshold.threshold_value
            ):
                should_alert = True
            elif (
                threshold.comparison == "lt"
                and metric_value < threshold.threshold_value
            ):
                should_alert = True
            elif (
                threshold.comparison == "eq"
                and metric_value == threshold.threshold_value
            ):
                should_alert = True

            alert_key = f"{service_name}_{threshold.metric_name}_{threshold.severity}"

            if should_alert:
                if alert_key not in self.active_alerts:
                    # Create new alert
                    alert = PerformanceAlert(
                        alert_id=f"alert_{int(time.time())}_{alert_key}",
                        alert_name=f"{threshold.metric_name.replace('_', ' ').title()} Alert",
                        service_name=service_name,
                        metric_name=threshold.metric_name,
                        current_value=metric_value,
                        threshold_value=threshold.threshold_value,
                        severity=threshold.severity,
                        message=f"{service_name} {threshold.metric_name} is {metric_value:.2f} (threshold: {threshold.threshold_value})",
                    )

                    await self.trigger_alert(alert)
            else:
                # Resolve alert if it exists
                if alert_key in self.active_alerts:
                    await self.resolve_alert(alert_key)

    async def trigger_alert(self, alert: PerformanceAlert):
        """Trigger a performance alert."""
        alert_key = f"{alert.service_name}_{alert.metric_name}_{alert.severity}"

        # Add to active alerts
        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert)

        # Update metrics
        self.alerts_triggered.labels(
            service=alert.service_name,
            metric=alert.metric_name,
            severity=alert.severity,
        ).inc()

        self.alerts_active.labels(
            service=alert.service_name,
            metric=alert.metric_name,
            severity=alert.severity,
        ).set(1)

        # Send alert notifications
        await self.send_alert_notifications(alert)

        logger.warning(f"Alert triggered: {alert.message}")

    async def resolve_alert(self, alert_key: str):
        """Resolve an active alert."""
        if alert_key in self.active_alerts:
            alert = self.active_alerts[alert_key]
            alert.resolved_at = datetime.now(timezone.utc)

            # Remove from active alerts
            del self.active_alerts[alert_key]

            # Update metrics
            self.alerts_active.labels(
                service=alert.service_name,
                metric=alert.metric_name,
                severity=alert.severity,
            ).set(0)

            logger.info(f"Alert resolved: {alert.message}")

    async def send_alert_notifications(self, alert: PerformanceAlert):
        """Send alert notifications."""
        # Log alert
        logger.warning(f"PERFORMANCE ALERT: {alert.message}")

        # Send to external systems (webhook, email, Slack, etc.)
        await self.send_webhook_notification(alert)

        # Save alert to file
        await self.save_alert_to_file(alert)

    async def send_webhook_notification(self, alert: PerformanceAlert):
        """Send webhook notification."""
        webhook_payload = {
            "alert_id": alert.alert_id,
            "alert_name": alert.alert_name,
            "service": alert.service_name,
            "metric": alert.metric_name,
            "current_value": alert.current_value,
            "threshold": alert.threshold_value,
            "severity": alert.severity,
            "message": alert.message,
            "timestamp": alert.triggered_at.isoformat(),
            "constitutional_hash": alert.constitutional_hash,
        }

        # Example webhook call (configure endpoint as needed)
        try:
            async with aiohttp.ClientSession() as session:
                # Replace with actual webhook URL
                webhook_url = "http://localhost:8097/alerts/webhook"

                async with session.post(
                    webhook_url, json=webhook_payload, timeout=10
                ) as response:
                    if response.status == 200:
                        logger.info(
                            f"Webhook notification sent for alert {alert.alert_id}"
                        )
                    else:
                        logger.warning(
                            f"Webhook notification failed: {response.status}"
                        )

        except Exception as e:
            logger.warning(f"Failed to send webhook notification: {e}")

    async def save_alert_to_file(self, alert: PerformanceAlert):
        """Save alert to file."""
        import os

        alerts_dir = "logs/alerts"
        os.makedirs(alerts_dir, exist_ok=True)

        alert_data = {
            "alert_id": alert.alert_id,
            "alert_name": alert.alert_name,
            "service_name": alert.service_name,
            "metric_name": alert.metric_name,
            "current_value": alert.current_value,
            "threshold_value": alert.threshold_value,
            "severity": alert.severity,
            "message": alert.message,
            "triggered_at": alert.triggered_at.isoformat(),
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "constitutional_hash": alert.constitutional_hash,
        }

        alert_file = f"{alerts_dir}/alert_{alert.alert_id}.json"
        with open(alert_file, "w") as f:
            json.dump(alert_data, f, indent=2)

    async def regression_detection_loop(self):
        """Loop for detecting performance regressions."""
        while True:
            try:
                await self.detect_performance_regressions()
                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Error in regression detection loop: {e}")
                await asyncio.sleep(600)

    async def detect_performance_regressions(self):
        """Detect performance regressions against baseline."""
        if not self.baseline_metrics:
            return

        for service_name, port in self.services.items():
            if service_name not in self.baseline_metrics:
                continue

            try:
                current_metrics = await self.collect_service_metrics(service_name, port)
                baseline = self.baseline_metrics[service_name]

                # Check response time regression (>10% increase)
                if (
                    "response_time_ms" in current_metrics
                    and baseline["avg_response_time"] > 0
                ):
                    current_rt = current_metrics["response_time_ms"]
                    baseline_rt = baseline["avg_response_time"]
                    regression_percent = (
                        (current_rt - baseline_rt) / baseline_rt
                    ) * 100

                    if regression_percent > 10:  # 10% threshold
                        await self.trigger_regression_alert(
                            service_name,
                            "response_time",
                            current_rt,
                            baseline_rt,
                            regression_percent,
                        )

                # Check throughput regression (>5% decrease)
                if (
                    "throughput_rps" in current_metrics
                    and baseline["avg_throughput"] > 0
                ):
                    current_tp = current_metrics["throughput_rps"]
                    baseline_tp = baseline["avg_throughput"]
                    regression_percent = (
                        (baseline_tp - current_tp) / baseline_tp
                    ) * 100

                    if regression_percent > 5:  # 5% threshold
                        await self.trigger_regression_alert(
                            service_name,
                            "throughput",
                            current_tp,
                            baseline_tp,
                            regression_percent,
                        )

            except Exception as e:
                logger.warning(f"Failed to check regression for {service_name}: {e}")

    async def trigger_regression_alert(
        self,
        service_name: str,
        metric_type: str,
        current_value: float,
        baseline_value: float,
        regression_percent: float,
    ):
        """Trigger a performance regression alert."""
        alert = PerformanceAlert(
            alert_id=f"regression_{int(time.time())}_{service_name}_{metric_type}",
            alert_name=f"Performance Regression - {metric_type.title()}",
            service_name=service_name,
            metric_name=f"{metric_type}_regression",
            current_value=current_value,
            threshold_value=baseline_value,
            severity="warning",
            message=f"{service_name} {metric_type} regression detected: {regression_percent:.1f}% change from baseline",
        )

        # Record regression detection
        self.performance_regression_detected.labels(
            service=service_name, metric=metric_type
        ).inc()

        await self.trigger_alert(alert)

    async def alert_resolution_loop(self):
        """Loop for checking alert resolution."""
        while True:
            try:
                # Clean up old resolved alerts
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
                self.alert_history = [
                    alert
                    for alert in self.alert_history
                    if alert.resolved_at is None or alert.resolved_at > cutoff_time
                ]

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Error in alert resolution loop: {e}")
                await asyncio.sleep(600)

    def get_alert_summary(self) -> Dict:
        """Get alert summary."""
        return {
            "active_alerts": len(self.active_alerts),
            "total_alerts_today": len(
                [
                    alert
                    for alert in self.alert_history
                    if alert.triggered_at.date() == datetime.now(timezone.utc).date()
                ]
            ),
            "critical_alerts": len(
                [
                    alert
                    for alert in self.active_alerts.values()
                    if alert.severity == "critical"
                ]
            ),
            "warning_alerts": len(
                [
                    alert
                    for alert in self.active_alerts.values()
                    if alert.severity == "warning"
                ]
            ),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global alerting system instance
alerting_system = PerformanceAlertingSystem()

if __name__ == "__main__":

    async def main():
        await alerting_system.start_alerting_system()

    asyncio.run(main())
