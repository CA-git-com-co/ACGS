"""
Alert Manager for ACGS-PGP v8

Intelligent alerting system with constitutional compliance monitoring.
"""

import asyncio
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(Enum):
    """Alert status."""

    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class AlertRule:
    """Alert rule configuration."""

    name: str
    condition: Callable[[dict[str, Any]], bool]
    severity: AlertSeverity
    message_template: str
    cooldown_minutes: int = 15
    auto_resolve: bool = True
    enabled: bool = True


@dataclass
class Alert:
    """Alert instance."""

    id: str
    rule_name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    status: AlertStatus
    data: dict[str, Any]
    resolved_at: datetime | None = None


class AlertManager:
    """
    Intelligent alert manager for ACGS-PGP v8 system.

    Provides rule-based alerting with constitutional compliance
    monitoring and intelligent alert suppression.
    """

    def __init__(self, constitutional_hash: str = "cdd01ef066bc6cf2"):
        """Initialize alert manager."""
        self.constitutional_hash = constitutional_hash
        self.alert_rules: dict[str, AlertRule] = {}
        self.active_alerts: dict[str, Alert] = {}
        self.alert_history: list[Alert] = []
        self.last_alert_times: dict[str, datetime] = {}

        # Alert handlers
        self.alert_handlers: list[Callable] = []

        # Initialize default alert rules
        self._initialize_default_rules()

        logger.info("Alert manager initialized")

    def _initialize_default_rules(self):
        """Initialize default alert rules for ACGS-PGP v8."""

        # Constitutional compliance alerts
        self.register_alert_rule(
            name="constitutional_hash_mismatch",
            condition=lambda data: data.get("type") == "constitutional_violation",
            severity=AlertSeverity.CRITICAL,
            message_template="Constitutional hash mismatch detected: {message}",
            cooldown_minutes=5,
        )

        # Performance alerts
        self.register_alert_rule(
            name="high_response_time",
            condition=lambda data: (
                data.get("type") == "performance" and data.get("response_time_ms", 0) > 500
            ),
            severity=AlertSeverity.HIGH,
            message_template="High response time detected: {response_time_ms}ms on {endpoint}",
            cooldown_minutes=10,
        )

        # Health check alerts
        self.register_alert_rule(
            name="component_unhealthy",
            condition=lambda data: (
                data.get("type") == "health_check_failure" and data.get("status") == "unhealthy"
            ),
            severity=AlertSeverity.HIGH,
            message_template="Component {component} is unhealthy: {message}",
            cooldown_minutes=15,
        )

        # Cache performance alerts
        self.register_alert_rule(
            name="low_cache_hit_rate",
            condition=lambda data: (
                data.get("type") == "cache_performance" and data.get("hit_rate", 100) < 70
            ),
            severity=AlertSeverity.MEDIUM,
            message_template="Low cache hit rate: {hit_rate}% for {cache_type}",
            cooldown_minutes=30,
        )

        # Error rate alerts
        self.register_alert_rule(
            name="high_error_rate",
            condition=lambda data: (
                data.get("type") == "error_rate"
                and data.get("error_rate", 0) > 0.05  # 5% error rate
            ),
            severity=AlertSeverity.HIGH,
            message_template="High error rate detected: {error_rate:.1%} in {component}",
            cooldown_minutes=10,
        )

        # Policy generation alerts
        self.register_alert_rule(
            name="low_compliance_score",
            condition=lambda data: (
                data.get("type") == "policy_generation" and data.get("compliance_score", 1.0) < 0.8
            ),
            severity=AlertSeverity.MEDIUM,
            message_template="Low constitutional compliance score: {compliance_score:.2f}",
            cooldown_minutes=20,
        )

        # System resource alerts
        self.register_alert_rule(
            name="high_memory_usage",
            condition=lambda data: (
                data.get("type") == "resource_usage" and data.get("memory_usage_percent", 0) > 85
            ),
            severity=AlertSeverity.HIGH,
            message_template="High memory usage: {memory_usage_percent}%",
            cooldown_minutes=15,
        )

        # Circuit breaker alerts
        self.register_alert_rule(
            name="circuit_breaker_open",
            condition=lambda data: (
                data.get("type") == "circuit_breaker" and data.get("state") == "open"
            ),
            severity=AlertSeverity.HIGH,
            message_template="Circuit breaker opened for {service}",
            cooldown_minutes=5,
        )

    def register_alert_rule(
        self,
        name: str,
        condition: Callable[[dict[str, Any]], bool],
        severity: AlertSeverity,
        message_template: str,
        cooldown_minutes: int = 15,
        auto_resolve: bool = True,
    ):
        """Register a new alert rule."""
        rule = AlertRule(
            name=name,
            condition=condition,
            severity=severity,
            message_template=message_template,
            cooldown_minutes=cooldown_minutes,
            auto_resolve=auto_resolve,
        )

        self.alert_rules[name] = rule
        logger.info(f"Registered alert rule: {name}")

    def register_alert_handler(self, handler: Callable[[Alert], None]):
        """Register alert handler function."""
        self.alert_handlers.append(handler)
        logger.info("Registered alert handler")

    async def process_event(self, event_data: dict[str, Any]):
        """Process an event and check for alert conditions."""
        triggered_alerts = []

        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue

            try:
                # Check if rule condition is met
                if rule.condition(event_data):
                    # Check cooldown period
                    if self._is_in_cooldown(rule_name):
                        continue

                    # Create alert
                    alert = await self._create_alert(rule, event_data)
                    triggered_alerts.append(alert)

                    # Update last alert time
                    self.last_alert_times[rule_name] = datetime.now()

            except Exception as e:
                logger.error(f"Error processing alert rule {rule_name}: {e}")

        return triggered_alerts

    def _is_in_cooldown(self, rule_name: str) -> bool:
        """Check if alert rule is in cooldown period."""
        if rule_name not in self.last_alert_times:
            return False

        rule = self.alert_rules[rule_name]
        last_alert_time = self.last_alert_times[rule_name]
        cooldown_period = timedelta(minutes=rule.cooldown_minutes)

        return datetime.now() - last_alert_time < cooldown_period

    async def _create_alert(self, rule: AlertRule, event_data: dict[str, Any]) -> Alert:
        """Create a new alert instance."""
        alert_id = f"{rule.name}_{int(datetime.now().timestamp())}"

        # Format message using template
        try:
            message = rule.message_template.format(**event_data)
        except KeyError as e:
            message = f"{rule.message_template} (missing data: {e})"

        alert = Alert(
            id=alert_id,
            rule_name=rule.name,
            severity=rule.severity,
            message=message,
            timestamp=datetime.now(),
            status=AlertStatus.ACTIVE,
            data=event_data.copy(),
        )

        # Add constitutional hash to alert data
        alert.data["constitutional_hash"] = self.constitutional_hash

        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)

        # Trigger alert handlers
        await self._trigger_alert_handlers(alert)

        logger.warning(f"Alert triggered: {rule.name} - {message}")
        return alert

    async def _trigger_alert_handlers(self, alert: Alert):
        """Trigger all registered alert handlers."""
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")

    async def resolve_alert(self, alert_id: str, reason: str = "Manual resolution"):
        """Resolve an active alert."""
        if alert_id not in self.active_alerts:
            logger.warning(f"Alert {alert_id} not found in active alerts")
            return

        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()
        alert.data["resolution_reason"] = reason

        # Remove from active alerts
        del self.active_alerts[alert_id]

        logger.info(f"Alert resolved: {alert_id} - {reason}")

    async def suppress_alert(self, alert_id: str, duration_minutes: int = 60):
        """Suppress an alert for a specified duration."""
        if alert_id not in self.active_alerts:
            logger.warning(f"Alert {alert_id} not found in active alerts")
            return

        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.SUPPRESSED
        alert.data["suppressed_until"] = (
            datetime.now() + timedelta(minutes=duration_minutes)
        ).isoformat()

        logger.info(f"Alert suppressed: {alert_id} for {duration_minutes} minutes")

    def get_active_alerts(self, severity: AlertSeverity | None = None) -> list[Alert]:
        """Get list of active alerts, optionally filtered by severity."""
        alerts = list(self.active_alerts.values())

        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]

        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)

    def get_alert_summary(self) -> dict[str, Any]:
        """Get alert summary statistics."""
        active_alerts = list(self.active_alerts.values())

        # Count by severity
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = sum(
                1 for alert in active_alerts if alert.severity == severity
            )

        # Recent alerts (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_alerts = [alert for alert in self.alert_history if alert.timestamp >= recent_cutoff]

        return {
            "active_alerts_count": len(active_alerts),
            "severity_breakdown": severity_counts,
            "recent_alerts_24h": len(recent_alerts),
            "total_rules": len(self.alert_rules),
            "enabled_rules": sum(1 for rule in self.alert_rules.values() if rule.enabled),
            "constitutional_hash": self.constitutional_hash,
            "timestamp": datetime.now().isoformat(),
        }

    def get_alert_details(self, alert_id: str) -> dict[str, Any] | None:
        """Get detailed information about a specific alert."""
        # Check active alerts first
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
        else:
            # Search in history
            alert = next((a for a in self.alert_history if a.id == alert_id), None)

        if not alert:
            return None

        return {
            "id": alert.id,
            "rule_name": alert.rule_name,
            "severity": alert.severity.value,
            "message": alert.message,
            "status": alert.status.value,
            "timestamp": alert.timestamp.isoformat(),
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "data": alert.data,
            "constitutional_hash": self.constitutional_hash,
        }

    async def cleanup_old_alerts(self, retention_days: int = 30):
        """Clean up old alerts from history."""
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        original_count = len(self.alert_history)
        self.alert_history = [
            alert for alert in self.alert_history if alert.timestamp >= cutoff_date
        ]

        cleaned_count = original_count - len(self.alert_history)
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old alerts")

    def export_alerts(self, start_date: datetime, end_date: datetime) -> str:
        """Export alerts in JSON format for the specified date range."""
        filtered_alerts = [
            alert for alert in self.alert_history if start_date <= alert.timestamp <= end_date
        ]

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "constitutional_hash": self.constitutional_hash,
            "alert_count": len(filtered_alerts),
            "alerts": [
                {
                    "id": alert.id,
                    "rule_name": alert.rule_name,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "status": alert.status.value,
                    "timestamp": alert.timestamp.isoformat(),
                    "resolved_at": (alert.resolved_at.isoformat() if alert.resolved_at else None),
                    "data": alert.data,
                }
                for alert in filtered_alerts
            ],
        }

        return json.dumps(export_data, indent=2)
