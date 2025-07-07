"""
Advanced Alert Management System for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive alerting with multiple channels, rules, and escalation policies.
"""

import asyncio
import json
import logging
import smtplib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import aiohttp

from ..resilience.retry import retry_with_exponential_backoff
from .metrics import MetricValue, get_metrics_collector

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status states."""

    PENDING = "pending"
    FIRING = "firing"
    RESOLVED = "resolved"
    SILENCED = "silenced"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class Alert:
    """Represents an alert instance."""

    name: str
    message: str
    severity: AlertSeverity
    source: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    status: AlertStatus = AlertStatus.PENDING
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None

    def __post_init__(self):
        """Initialize alert with constitutional compliance."""
        self.labels["constitutional_hash"] = "cdd01ef066bc6cf2"
        self.labels["alert_id"] = f"{self.name}_{int(self.timestamp.timestamp())}"

    def resolve(self) -> None:
        """Mark alert as resolved."""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.utcnow()

    def acknowledge(self, user: str) -> None:
        """Acknowledge the alert."""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = datetime.utcnow()
        self.acknowledged_by = user

    def silence(self) -> None:
        """Silence the alert."""
        self.status = AlertStatus.SILENCED

    @property
    def is_active(self) -> bool:
        """Check if alert is currently active."""
        return self.status in [AlertStatus.PENDING, AlertStatus.FIRING]

    @property
    def duration(self) -> timedelta:
        """Get alert duration."""
        end_time = self.resolved_at or datetime.utcnow()
        return end_time - self.timestamp

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary representation."""
        return {
            "name": self.name,
            "message": self.message,
            "severity": self.severity.value,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
            "annotations": self.annotations,
            "status": self.status.value,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "acknowledged_at": (
                self.acknowledged_at.isoformat() if self.acknowledged_at else None
            ),
            "acknowledged_by": self.acknowledged_by,
            "duration_seconds": self.duration.total_seconds(),
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


class AlertRule:
    """Rule for generating alerts based on conditions."""

    def __init__(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], bool],
        severity: AlertSeverity,
        message_template: str,
        labels: Dict[str, str] = None,
        annotations: Dict[str, str] = None,
        for_duration: timedelta = None,
        cooldown: timedelta = None,
    ):
        self.name = name
        self.condition = condition
        self.severity = severity
        self.message_template = message_template
        self.labels = labels or {}
        self.annotations = annotations or {}
        self.for_duration = for_duration or timedelta(seconds=0)
        self.cooldown = cooldown or timedelta(minutes=5)

        # Internal state
        self._condition_met_since: Optional[datetime] = None
        self._last_fired: Optional[datetime] = None

    def evaluate(self, context: Dict[str, Any]) -> Optional[Alert]:
        """Evaluate rule and return alert if condition is met."""
        try:
            condition_met = self.condition(context)
            now = datetime.utcnow()

            if condition_met:
                if self._condition_met_since is None:
                    self._condition_met_since = now

                # Check if condition has been met for required duration
                if now - self._condition_met_since >= self.for_duration:
                    # Check cooldown period
                    if (
                        self._last_fired is None
                        or now - self._last_fired >= self.cooldown
                    ):

                        # Generate alert
                        alert = self._create_alert(context)
                        self._last_fired = now
                        return alert
            else:
                # Reset condition timer if condition is no longer met
                self._condition_met_since = None

            return None

        except Exception as e:
            logger.error(f"Error evaluating alert rule '{self.name}': {e}")
            return None

    def _create_alert(self, context: Dict[str, Any]) -> Alert:
        """Create alert from rule."""
        # Format message with context
        try:
            message = self.message_template.format(**context)
        except KeyError as e:
            message = f"{self.message_template} (formatting error: {e})"

        # Merge labels and annotations with context
        labels = self.labels.copy()
        labels.update(context.get("labels", {}))

        annotations = self.annotations.copy()
        annotations.update(context.get("annotations", {}))

        return Alert(
            name=self.name,
            message=message,
            severity=self.severity,
            source=f"rule:{self.name}",
            labels=labels,
            annotations=annotations,
        )


class AlertChannel(ABC):
    """Abstract base class for alert channels."""

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled

    @abstractmethod
    async def send_alert(self, alert: Alert) -> bool:
        """Send alert through this channel."""
        pass

    def should_send(self, alert: Alert) -> bool:
        """Check if alert should be sent through this channel."""
        return self.enabled


class EmailAlertChannel(AlertChannel):
    """Email alert channel."""

    def __init__(
        self,
        name: str,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        recipients: List[str],
        from_email: str = None,
        enabled: bool = True,
        min_severity: AlertSeverity = AlertSeverity.WARNING,
    ):
        super().__init__(name, enabled)
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.recipients = recipients
        self.from_email = from_email or username
        self.min_severity = min_severity

    def should_send(self, alert: Alert) -> bool:
        """Check if alert severity meets minimum threshold."""
        severity_levels = {
            AlertSeverity.INFO: 0,
            AlertSeverity.WARNING: 1,
            AlertSeverity.ERROR: 2,
            AlertSeverity.CRITICAL: 3,
        }

        return (
            super().should_send(alert)
            and severity_levels[alert.severity] >= severity_levels[self.min_severity]
        )

    async def send_alert(self, alert: Alert) -> bool:
        """Send alert via email."""
        if not self.should_send(alert):
            return True

        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.recipients)
            msg["Subject"] = f"[{alert.severity.upper()}] {alert.name}"

            # Create body
            body = f"""
ACGS Alert: {alert.name}

Severity: {alert.severity.upper()}
Message: {alert.message}
Source: {alert.source}
Timestamp: {alert.timestamp.isoformat()}

Labels:
{json.dumps(alert.labels, indent=2)}

Annotations:
{json.dumps(alert.annotations, indent=2)}

Constitutional Hash: cdd01ef066bc6cf2
            """.strip()

            msg.attach(MIMEText(body, "plain"))

            # Send email
            await retry_with_exponential_backoff(
                self._send_email, msg, operation_name="email_alert_send", max_attempts=3
            )

            logger.info(f"Email alert sent for: {alert.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email alert for {alert.name}: {e}")
            return False

    async def _send_email(self, msg: MIMEMultipart) -> None:
        """Send email message."""

        def send_sync():
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, send_sync)


class SlackAlertChannel(AlertChannel):
    """Slack alert channel."""

    def __init__(
        self,
        name: str,
        webhook_url: str,
        channel: str = None,
        username: str = "ACGS Alerts",
        enabled: bool = True,
        min_severity: AlertSeverity = AlertSeverity.WARNING,
    ):
        super().__init__(name, enabled)
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username
        self.min_severity = min_severity

    def should_send(self, alert: Alert) -> bool:
        """Check if alert severity meets minimum threshold."""
        severity_levels = {
            AlertSeverity.INFO: 0,
            AlertSeverity.WARNING: 1,
            AlertSeverity.ERROR: 2,
            AlertSeverity.CRITICAL: 3,
        }

        return (
            super().should_send(alert)
            and severity_levels[alert.severity] >= severity_levels[self.min_severity]
        )

    async def send_alert(self, alert: Alert) -> bool:
        """Send alert to Slack."""
        if not self.should_send(alert):
            return True

        try:
            # Color coding for severity
            colors = {
                AlertSeverity.INFO: "#36a64f",  # Green
                AlertSeverity.WARNING: "#ff9900",  # Orange
                AlertSeverity.ERROR: "#ff0000",  # Red
                AlertSeverity.CRITICAL: "#800080",  # Purple
            }

            # Create Slack message
            payload = {
                "username": self.username,
                "attachments": [
                    {
                        "color": colors.get(alert.severity, "#cccccc"),
                        "title": f"{alert.severity.upper()}: {alert.name}",
                        "text": alert.message,
                        "fields": [
                            {"title": "Source", "value": alert.source, "short": True},
                            {
                                "title": "Timestamp",
                                "value": alert.timestamp.strftime(
                                    "%Y-%m-%d %H:%M:%S UTC"
                                ),
                                "short": True,
                            },
                        ],
                        "footer": f"Constitutional Hash: cdd01ef066bc6cf2",
                        "ts": int(alert.timestamp.timestamp()),
                    }
                ],
            }

            if self.channel:
                payload["channel"] = self.channel

            # Send to Slack
            await retry_with_exponential_backoff(
                self._send_to_slack,
                payload,
                operation_name="slack_alert_send",
                max_attempts=3,
            )

            logger.info(f"Slack alert sent for: {alert.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to send Slack alert for {alert.name}: {e}")
            return False

    async def _send_to_slack(self, payload: Dict[str, Any]) -> None:
        """Send message to Slack webhook."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status != 200:
                    raise Exception(f"Slack webhook returned status {response.status}")


class WebhookAlertChannel(AlertChannel):
    """Generic webhook alert channel."""

    def __init__(
        self,
        name: str,
        webhook_url: str,
        headers: Dict[str, str] = None,
        enabled: bool = True,
    ):
        super().__init__(name, enabled)
        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}

    async def send_alert(self, alert: Alert) -> bool:
        """Send alert to webhook."""
        if not self.should_send(alert):
            return True

        try:
            payload = alert.to_dict()

            await retry_with_exponential_backoff(
                self._send_to_webhook,
                payload,
                operation_name="webhook_alert_send",
                max_attempts=3,
            )

            logger.info(f"Webhook alert sent for: {alert.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to send webhook alert for {alert.name}: {e}")
            return False

    async def _send_to_webhook(self, payload: Dict[str, Any]) -> None:
        """Send payload to webhook."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.webhook_url, json=payload, headers=self.headers
            ) as response:
                if response.status not in [200, 201, 202]:
                    raise Exception(f"Webhook returned status {response.status}")


class AlertManager:
    """Central alert management system."""

    def __init__(self, name: str = "acgs_alerts"):
        self.name = name
        self._rules: List[AlertRule] = []
        self._channels: List[AlertChannel] = []
        self._active_alerts: Dict[str, Alert] = {}
        self._alert_history: List[Alert] = []
        self._evaluation_interval = 30.0  # Evaluate rules every 30 seconds
        self._running = False
        self._evaluation_task: Optional[asyncio.Task] = None

        # Metrics
        self._metrics_collector = get_metrics_collector()
        self._alerts_total = self._metrics_collector.counter(
            "alerts_total", "Total alerts generated"
        )
        self._alerts_by_severity = {}
        for severity in AlertSeverity:
            self._alerts_by_severity[severity] = self._metrics_collector.counter(
                f"alerts_{severity.value}_total", f"Total {severity.value} alerts"
            )

    def add_rule(self, rule: AlertRule) -> None:
        """Add alert rule."""
        self._rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")

    def add_channel(self, channel: AlertChannel) -> None:
        """Add alert channel."""
        self._channels.append(channel)
        logger.info(f"Added alert channel: {channel.name}")

    async def fire_alert(self, alert: Alert) -> None:
        """Fire an alert manually."""
        alert.status = AlertStatus.FIRING
        alert_key = f"{alert.name}_{alert.source}"

        # Track alert
        self._active_alerts[alert_key] = alert
        self._alert_history.append(alert)

        # Update metrics
        self._alerts_total.increment()
        self._alerts_by_severity[alert.severity].increment()

        # Send through channels
        await self._send_alert(alert)

        logger.warning(f"Alert fired: {alert.name} ({alert.severity.value})")

    async def resolve_alert(self, alert_name: str, source: str = None) -> bool:
        """Resolve an active alert."""
        alert_key = f"{alert_name}_{source or 'unknown'}"

        if alert_key in self._active_alerts:
            alert = self._active_alerts[alert_key]
            alert.resolve()
            del self._active_alerts[alert_key]

            logger.info(f"Alert resolved: {alert_name}")
            return True

        return False

    async def acknowledge_alert(
        self, alert_name: str, user: str, source: str = None
    ) -> bool:
        """Acknowledge an active alert."""
        alert_key = f"{alert_name}_{source or 'unknown'}"

        if alert_key in self._active_alerts:
            alert = self._active_alerts[alert_key]
            alert.acknowledge(user)

            logger.info(f"Alert acknowledged by {user}: {alert_name}")
            return True

        return False

    async def _send_alert(self, alert: Alert) -> None:
        """Send alert through all channels."""
        send_tasks = []
        for channel in self._channels:
            if channel.enabled:
                send_tasks.append(channel.send_alert(alert))

        if send_tasks:
            results = await asyncio.gather(*send_tasks, return_exceptions=True)
            failed_channels = [
                channel.name
                for channel, result in zip(self._channels, results)
                if isinstance(result, Exception)
            ]

            if failed_channels:
                logger.error(
                    f"Failed to send alert through channels: {failed_channels}"
                )

    async def _evaluate_rules(self) -> None:
        """Evaluate all alert rules."""
        if not self._rules:
            return

        # Get current metrics for context
        metrics_collector = get_metrics_collector()
        metrics = metrics_collector.collect_all()

        # Build context from metrics
        context = {
            "metrics": {metric.name: metric.value for metric in metrics},
            "timestamp": datetime.utcnow(),
            "labels": {},
            "annotations": {},
        }

        # Evaluate each rule
        for rule in self._rules:
            try:
                alert = rule.evaluate(context)
                if alert:
                    await self.fire_alert(alert)
            except Exception as e:
                logger.error(f"Error evaluating rule '{rule.name}': {e}")

    async def start_evaluation_loop(self) -> None:
        """Start automatic rule evaluation loop."""
        if self._running:
            return

        self._running = True
        logger.info(
            f"Starting alert evaluation loop (interval: {self._evaluation_interval}s)"
        )

        while self._running:
            try:
                await self._evaluate_rules()
                await asyncio.sleep(self._evaluation_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert evaluation loop: {e}")
                await asyncio.sleep(self._evaluation_interval)

    def stop_evaluation_loop(self) -> None:
        """Stop automatic rule evaluation loop."""
        self._running = False
        if self._evaluation_task:
            self._evaluation_task.cancel()

    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return list(self._active_alerts.values())

    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history."""
        return self._alert_history[-limit:]

    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics."""
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = sum(
                1
                for alert in self._active_alerts.values()
                if alert.severity == severity
            )

        return {
            "manager_name": self.name,
            "total_rules": len(self._rules),
            "total_channels": len(self._channels),
            "active_alerts": len(self._active_alerts),
            "total_alerts_generated": len(self._alert_history),
            "alerts_by_severity": severity_counts,
            "evaluation_interval": self._evaluation_interval,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


# Global alert manager
_global_alert_manager = AlertManager()


def get_alert_manager() -> AlertManager:
    """Get the global alert manager."""
    return _global_alert_manager


async def send_alert(
    name: str,
    message: str,
    severity: AlertSeverity,
    source: str = "manual",
    labels: Dict[str, str] = None,
    annotations: Dict[str, str] = None,
) -> None:
    """Convenience function to send an alert."""
    alert = Alert(
        name=name,
        message=message,
        severity=severity,
        source=source,
        labels=labels or {},
        annotations=annotations or {},
    )

    await _global_alert_manager.fire_alert(alert)


# Common alert rules
def create_high_cpu_rule(threshold: float = 90.0) -> AlertRule:
    """Create rule for high CPU usage."""

    def condition(context):
        cpu_usage = context.get("metrics", {}).get("system_cpu_usage", 0)
        return cpu_usage > threshold

    return AlertRule(
        name="high_cpu_usage",
        condition=condition,
        severity=AlertSeverity.WARNING,
        message_template=f"High CPU usage detected: {{metrics[system_cpu_usage]:.1f}}%",
        for_duration=timedelta(minutes=2),
        cooldown=timedelta(minutes=10),
    )


def create_high_memory_rule(threshold: float = 90.0) -> AlertRule:
    """Create rule for high memory usage."""

    def condition(context):
        memory_usage = context.get("metrics", {}).get("system_memory_usage", 0)
        return memory_usage > threshold

    return AlertRule(
        name="high_memory_usage",
        condition=condition,
        severity=AlertSeverity.WARNING,
        message_template=f"High memory usage detected: {{metrics[system_memory_usage]:.1f}}%",
        for_duration=timedelta(minutes=2),
        cooldown=timedelta(minutes=10),
    )


def create_constitutional_violation_rule() -> AlertRule:
    """Create rule for constitutional violations."""

    def condition(context):
        violations = context.get("metrics", {}).get(
            "constitutional_violations_total", 0
        )
        return violations > 0

    return AlertRule(
        name="constitutional_violation",
        condition=condition,
        severity=AlertSeverity.CRITICAL,
        message_template="Constitutional violation detected: {metrics[constitutional_violations_total]} violations",
        for_duration=timedelta(seconds=0),  # Fire immediately
        cooldown=timedelta(minutes=1),
    )


# Setup default alerting
def setup_default_alerting() -> None:
    """Set up default alert rules and channels."""
    alert_manager = get_alert_manager()

    # Add default rules
    alert_manager.add_rule(create_high_cpu_rule())
    alert_manager.add_rule(create_high_memory_rule())
    alert_manager.add_rule(create_constitutional_violation_rule())

    logger.info("Default alerting configured")
