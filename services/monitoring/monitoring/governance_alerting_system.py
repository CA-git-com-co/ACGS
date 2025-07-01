"""
Composite Alerting System for AI Governance

This module implements a sophisticated alerting system specifically designed
for AI governance monitoring. It provides composite alerting, pattern detection,
and intelligent alert correlation for constitutional AI and multi-armed bandits.

Key Features:
- Composite alerting across multiple metrics
- Pattern detection for governance anomalies
- Alert correlation and deduplication
- Severity escalation and routing
- Integration with existing ACGS monitoring
- Constitutional compliance monitoring
- Performance threshold management

Based on modern observability practices and AI governance requirements.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

import numpy as np
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    """Alert status."""

    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"


class AlertCategory(Enum):
    """Alert categories for governance."""

    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    SAFETY_VIOLATION = "safety_violation"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SYSTEM_HEALTH = "system_health"
    SECURITY_INCIDENT = "security_incident"
    GOVERNANCE_WORKFLOW = "governance_workflow"


@dataclass
class Alert:
    """Individual alert with metadata."""

    alert_id: str
    name: str
    description: str
    severity: AlertSeverity
    category: AlertCategory
    status: AlertStatus = AlertStatus.ACTIVE

    # Metrics and context
    metric_name: str = ""
    metric_value: float = 0.0
    threshold: float = 0.0
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)

    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: datetime | None = None

    # Correlation
    correlation_id: str | None = None
    parent_alert_id: str | None = None
    related_alerts: set[str] = field(default_factory=set)

    # Escalation
    escalation_level: int = 0
    escalated_at: datetime | None = None
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None


@dataclass
class AlertRule:
    """Alert rule configuration."""

    rule_id: str
    name: str
    description: str
    category: AlertCategory
    severity: AlertSeverity

    # Condition
    metric_query: str
    threshold: float
    comparison: str  # >, <, >=, <=, ==, !=
    duration: int  # seconds

    # Composite conditions
    composite_conditions: list[dict[str, Any]] = field(default_factory=list)
    correlation_window: int = 300  # seconds

    # Routing
    notification_channels: list[str] = field(default_factory=list)
    escalation_rules: list[dict[str, Any]] = field(default_factory=list)

    # Suppression
    suppression_rules: list[dict[str, Any]] = field(default_factory=list)
    cooldown_period: int = 300  # seconds

    # Metadata
    enabled: bool = True
    tags: set[str] = field(default_factory=set)


@dataclass
class GovernanceAlertingConfig:
    """Configuration for governance alerting system."""

    # Thresholds
    constitutional_compliance_threshold: float = 0.7
    safety_violation_threshold: float = 0.1
    performance_degradation_threshold: float = 0.2

    # Timing
    evaluation_interval: int = 30  # seconds
    correlation_window: int = 300  # seconds
    escalation_timeout: int = 900  # 15 minutes

    # Composite alerting
    enable_composite_alerts: bool = True
    pattern_detection_enabled: bool = True
    alert_correlation_enabled: bool = True

    # Performance
    max_active_alerts: int = 1000
    alert_retention_days: int = 30

    # Notification
    default_notification_channels: list[str] = field(
        default_factory=lambda: ["slack", "email"]
    )
    emergency_notification_channels: list[str] = field(
        default_factory=lambda: ["pagerduty", "sms"]
    )


class GovernanceAlertingSystem:
    """
    Composite Alerting System for AI Governance.

    Provides sophisticated alerting capabilities with pattern detection,
    correlation, and governance-specific monitoring for ACGS.
    """

    def __init__(self, config: GovernanceAlertingConfig):
        """Initialize governance alerting system."""
        self.config = config

        # Alert storage
        self.active_alerts: dict[str, Alert] = {}
        self.alert_history: list[Alert] = []
        self.alert_rules: dict[str, AlertRule] = {}

        # Correlation tracking
        self.correlation_groups: dict[str, set[str]] = {}
        self.pattern_cache: dict[str, Any] = {}

        # Performance metrics
        self.registry = CollectorRegistry()
        self.metrics = {
            "alerts_total": Counter(
                "governance_alerts_total",
                "Total number of alerts generated",
                ["severity", "category"],
                registry=self.registry,
            ),
            "alerts_active": Gauge(
                "governance_alerts_active",
                "Number of active alerts",
                ["severity", "category"],
                registry=self.registry,
            ),
            "alert_evaluation_duration": Histogram(
                "governance_alert_evaluation_duration_seconds",
                "Time spent evaluating alert rules",
                registry=self.registry,
            ),
            "composite_alerts_detected": Counter(
                "governance_composite_alerts_detected_total",
                "Number of composite alerts detected",
                ["pattern"],
                registry=self.registry,
            ),
        }

        # State tracking
        self.last_evaluation = datetime.now(timezone.utc)
        self.evaluation_count = 0

        # Initialize default rules
        self._initialize_default_rules()

        logger.info("Initialized Governance Alerting System")

    def _initialize_default_rules(self):
        """Initialize default alert rules for AI governance."""

        # Constitutional compliance rule
        constitutional_rule = AlertRule(
            rule_id="constitutional_compliance_low",
            name="Low Constitutional Compliance",
            description="Constitutional compliance score below threshold",
            category=AlertCategory.CONSTITUTIONAL_COMPLIANCE,
            severity=AlertSeverity.CRITICAL,
            metric_query="constitutional_compliance_score",
            threshold=self.config.constitutional_compliance_threshold,
            comparison="<",
            duration=120,
            notification_channels=["slack", "email"],
            escalation_rules=[
                {"timeout": 300, "channels": ["pagerduty"]},
                {"timeout": 900, "channels": ["sms", "phone"]},
            ],
        )
        self.alert_rules[constitutional_rule.rule_id] = constitutional_rule

        # Safety violation rule
        safety_rule = AlertRule(
            rule_id="safety_violations_high",
            name="High Safety Violation Rate",
            description="Safety violation rate exceeds threshold",
            category=AlertCategory.SAFETY_VIOLATION,
            severity=AlertSeverity.EMERGENCY,
            metric_query="rate(safety_violations_total[5m])",
            threshold=self.config.safety_violation_threshold,
            comparison=">",
            duration=60,
            notification_channels=["pagerduty", "sms"],
            escalation_rules=[
                {"timeout": 180, "channels": ["phone", "emergency_contact"]}
            ],
        )
        self.alert_rules[safety_rule.rule_id] = safety_rule

        # MAB performance rule
        mab_performance_rule = AlertRule(
            rule_id="mab_performance_degradation",
            name="Multi-Armed Bandit Performance Degradation",
            description="MAB algorithm performance below baseline",
            category=AlertCategory.PERFORMANCE_DEGRADATION,
            severity=AlertSeverity.WARNING,
            metric_query="(mab_current_performance - mab_baseline_performance) / mab_baseline_performance",
            threshold=-self.config.performance_degradation_threshold,
            comparison="<",
            duration=300,
            composite_conditions=[
                {"metric": "mab_exploration_rate", "threshold": 0.8, "comparison": ">"},
                {"metric": "mab_reward_variance", "threshold": 0.5, "comparison": ">"},
            ],
        )
        self.alert_rules[mab_performance_rule.rule_id] = mab_performance_rule

        # System health composite rule
        system_health_rule = AlertRule(
            rule_id="system_health_degraded",
            name="System Health Degraded",
            description="Multiple system health indicators showing degradation",
            category=AlertCategory.SYSTEM_HEALTH,
            severity=AlertSeverity.WARNING,
            metric_query="",  # Composite rule
            threshold=0.0,
            comparison="",
            duration=180,
            composite_conditions=[
                {"metric": "cpu_usage_percent", "threshold": 80, "comparison": ">"},
                {"metric": "memory_usage_percent", "threshold": 85, "comparison": ">"},
                {"metric": "response_time_p95", "threshold": 2.0, "comparison": ">"},
            ],
        )
        self.alert_rules[system_health_rule.rule_id] = system_health_rule

    async def start(self):
        """Start the alerting system."""
        # Start evaluation loop
        asyncio.create_task(self._evaluation_loop())

        # Start correlation engine
        if self.config.alert_correlation_enabled:
            asyncio.create_task(self._correlation_loop())

        # Start cleanup task
        asyncio.create_task(self._cleanup_loop())

        logger.info("Started Governance Alerting System")

    async def _evaluation_loop(self):
        """Main alert evaluation loop."""
        while True:
            try:
                start_time = time.time()

                await self._evaluate_alert_rules()

                # Update metrics
                evaluation_time = time.time() - start_time
                self.metrics["alert_evaluation_duration"].observe(evaluation_time)

                self.evaluation_count += 1
                self.last_evaluation = datetime.now(timezone.utc)

                await asyncio.sleep(self.config.evaluation_interval)

            except Exception as e:
                logger.error(f"Error in alert evaluation loop: {e}")
                await asyncio.sleep(10)

    async def _evaluate_alert_rules(self):
        """Evaluate all alert rules."""
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue

            try:
                await self._evaluate_single_rule(rule)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {e}")

    async def _evaluate_single_rule(self, rule: AlertRule):
        """Evaluate a single alert rule."""
        # Check if rule has composite conditions
        if rule.composite_conditions:
            await self._evaluate_composite_rule(rule)
        else:
            await self._evaluate_simple_rule(rule)

    async def _evaluate_simple_rule(self, rule: AlertRule):
        """Evaluate a simple (single metric) alert rule."""
        # This would integrate with Prometheus or other metrics source
        # For now, simulate metric evaluation
        metric_value = await self._get_metric_value(rule.metric_query)

        if metric_value is None:
            return

        # Check threshold
        condition_met = self._check_threshold(
            metric_value, rule.threshold, rule.comparison
        )

        if condition_met:
            await self._trigger_alert(rule, metric_value)
        else:
            await self._resolve_alert_if_exists(rule.rule_id)

    async def _evaluate_composite_rule(self, rule: AlertRule):
        """Evaluate a composite alert rule with multiple conditions."""
        conditions_met = []

        for condition in rule.composite_conditions:
            metric_value = await self._get_metric_value(condition["metric"])
            if metric_value is not None:
                condition_met = self._check_threshold(
                    metric_value, condition["threshold"], condition["comparison"]
                )
                conditions_met.append(condition_met)

        # Check if all conditions are met
        if all(conditions_met) and len(conditions_met) == len(
            rule.composite_conditions
        ):
            await self._trigger_composite_alert(rule, conditions_met)

            # Update composite alert metrics
            pattern_name = f"composite_{rule.category.value}"
            self.metrics["composite_alerts_detected"].labels(pattern=pattern_name).inc()
        else:
            await self._resolve_alert_if_exists(rule.rule_id)

    async def _get_metric_value(self, metric_query: str) -> float | None:
        """Get metric value from monitoring system."""
        # This would integrate with Prometheus API
        # For demonstration, return simulated values

        if "constitutional_compliance_score" in metric_query:
            return np.random.uniform(0.6, 0.95)
        if "safety_violations" in metric_query:
            return np.random.uniform(0.0, 0.15)
        if "mab_performance" in metric_query:
            return np.random.uniform(-0.3, 0.1)
        if "cpu_usage" in metric_query:
            return np.random.uniform(60, 95)
        if "memory_usage" in metric_query:
            return np.random.uniform(70, 90)
        if "response_time" in metric_query:
            return np.random.uniform(0.5, 3.0)

        return None

    def _check_threshold(self, value: float, threshold: float, comparison: str) -> bool:
        """Check if value meets threshold condition."""
        if comparison == ">":
            return value > threshold
        if comparison == "<":
            return value < threshold
        if comparison == ">=":
            return value >= threshold
        if comparison == "<=":
            return value <= threshold
        if comparison == "==":
            return abs(value - threshold) < 1e-6
        if comparison == "!=":
            return abs(value - threshold) >= 1e-6

        return False

    async def _trigger_alert(self, rule: AlertRule, metric_value: float):
        """Trigger an alert for a rule."""
        alert_id = f"{rule.rule_id}_{int(time.time())}"

        # Check if alert already exists for this rule
        existing_alert = self._find_active_alert_for_rule(rule.rule_id)

        if existing_alert:
            # Update existing alert
            existing_alert.metric_value = metric_value
            existing_alert.updated_at = datetime.now(timezone.utc)
            return

        # Create new alert
        alert = Alert(
            alert_id=alert_id,
            name=rule.name,
            description=rule.description,
            severity=rule.severity,
            category=rule.category,
            metric_name=rule.metric_query,
            metric_value=metric_value,
            threshold=rule.threshold,
            labels={"rule_id": rule.rule_id},
            annotations={
                "metric_query": rule.metric_query,
                "threshold": str(rule.threshold),
                "comparison": rule.comparison,
            },
        )

        # Add to active alerts
        self.active_alerts[alert_id] = alert

        # Update metrics
        self.metrics["alerts_total"].labels(
            severity=alert.severity.value, category=alert.category.value
        ).inc()

        self.metrics["alerts_active"].labels(
            severity=alert.severity.value, category=alert.category.value
        ).inc()

        # Send notifications
        await self._send_alert_notifications(alert, rule)

        logger.warning(f"Alert triggered: {alert.name} (ID: {alert_id})")

    async def _trigger_composite_alert(
        self, rule: AlertRule, conditions_met: list[bool]
    ):
        """Trigger a composite alert."""
        alert_id = f"composite_{rule.rule_id}_{int(time.time())}"

        # Check for existing composite alert
        existing_alert = self._find_active_alert_for_rule(rule.rule_id)

        if existing_alert:
            existing_alert.updated_at = datetime.now(timezone.utc)
            return

        # Create composite alert
        alert = Alert(
            alert_id=alert_id,
            name=f"Composite: {rule.name}",
            description=f"Multiple conditions met: {rule.description}",
            severity=rule.severity,
            category=rule.category,
            labels={"rule_id": rule.rule_id, "type": "composite"},
            annotations={
                "conditions_met": str(len([c for c in conditions_met if c])),
                "total_conditions": str(len(conditions_met)),
            },
        )

        self.active_alerts[alert_id] = alert

        # Update metrics
        self.metrics["alerts_total"].labels(
            severity=alert.severity.value, category=alert.category.value
        ).inc()

        await self._send_alert_notifications(alert, rule)

        logger.warning(f"Composite alert triggered: {alert.name} (ID: {alert_id})")

    async def _resolve_alert_if_exists(self, rule_id: str):
        """Resolve alert if it exists for a rule."""
        alert = self._find_active_alert_for_rule(rule_id)

        if alert:
            await self._resolve_alert(alert.alert_id)

    def _find_active_alert_for_rule(self, rule_id: str) -> Alert | None:
        """Find active alert for a specific rule."""
        for alert in self.active_alerts.values():
            if (
                alert.labels.get("rule_id") == rule_id
                and alert.status == AlertStatus.ACTIVE
            ):
                return alert
        return None

    async def _resolve_alert(self, alert_id: str):
        """Resolve an active alert."""
        alert = self.active_alerts.get(alert_id)

        if not alert:
            return

        # Update alert status
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now(timezone.utc)
        alert.updated_at = datetime.now(timezone.utc)

        # Move to history
        self.alert_history.append(alert)
        del self.active_alerts[alert_id]

        # Update metrics
        self.metrics["alerts_active"].labels(
            severity=alert.severity.value, category=alert.category.value
        ).dec()

        logger.info(f"Alert resolved: {alert.name} (ID: {alert_id})")

    async def _send_alert_notifications(self, alert: Alert, rule: AlertRule):
        """Send alert notifications through configured channels."""
        # This would integrate with notification systems
        # For now, just log the notification

        channels = (
            rule.notification_channels or self.config.default_notification_channels
        )

        if alert.severity == AlertSeverity.EMERGENCY:
            channels.extend(self.config.emergency_notification_channels)

        for channel in channels:
            await self._send_notification(alert, channel)

    async def _send_notification(self, alert: Alert, channel: str):
        """Send notification to a specific channel."""
        # This would integrate with actual notification services
        logger.info(f"Sending alert notification to {channel}: {alert.name}")

        # Simulate notification sending
        await asyncio.sleep(0.1)

    async def _correlation_loop(self):
        """Alert correlation loop."""
        while True:
            try:
                await self._correlate_alerts()
                await asyncio.sleep(60)  # Run correlation every minute

            except Exception as e:
                logger.error(f"Error in correlation loop: {e}")
                await asyncio.sleep(30)

    async def _correlate_alerts(self):
        """Correlate related alerts."""
        if not self.config.alert_correlation_enabled:
            return

        # Group alerts by category and time window
        correlation_window = timedelta(seconds=self.config.correlation_window)
        current_time = datetime.now(timezone.utc)

        # Find alerts within correlation window
        recent_alerts = [
            alert
            for alert in self.active_alerts.values()
            if (current_time - alert.created_at) <= correlation_window
        ]

        # Group by category
        category_groups = {}
        for alert in recent_alerts:
            category = alert.category
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(alert)

        # Correlate alerts within each category
        for category, alerts in category_groups.items():
            if len(alerts) >= 2:
                await self._create_correlation_group(alerts)

    async def _create_correlation_group(self, alerts: list[Alert]):
        """Create correlation group for related alerts."""
        correlation_id = f"corr_{int(time.time())}_{len(alerts)}"

        # Update alerts with correlation ID
        for alert in alerts:
            alert.correlation_id = correlation_id

            # Add related alerts
            for other_alert in alerts:
                if other_alert.alert_id != alert.alert_id:
                    alert.related_alerts.add(other_alert.alert_id)

        # Store correlation group
        self.correlation_groups[correlation_id] = {alert.alert_id for alert in alerts}

        logger.info(
            f"Created correlation group {correlation_id} with {len(alerts)} alerts"
        )

    async def _cleanup_loop(self):
        """Cleanup old alerts and data."""
        while True:
            try:
                await self._cleanup_old_alerts()
                await asyncio.sleep(3600)  # Run cleanup every hour

            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(1800)  # Retry in 30 minutes

    async def _cleanup_old_alerts(self):
        """Clean up old resolved alerts."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(
            days=self.config.alert_retention_days
        )

        # Remove old alerts from history
        self.alert_history = [
            alert
            for alert in self.alert_history
            if alert.resolved_at and alert.resolved_at > cutoff_time
        ]

        # Clean up old correlation groups
        old_correlations = []
        for corr_id, alert_ids in self.correlation_groups.items():
            # Check if any alerts in the group are still active
            active_alerts_in_group = any(
                alert_id in self.active_alerts for alert_id in alert_ids
            )

            if not active_alerts_in_group:
                old_correlations.append(corr_id)

        for corr_id in old_correlations:
            del self.correlation_groups[corr_id]

        logger.info(f"Cleaned up {len(old_correlations)} old correlation groups")

    def get_alert_statistics(self) -> dict[str, Any]:
        """Get comprehensive alert statistics."""
        active_by_severity = {}
        active_by_category = {}

        for alert in self.active_alerts.values():
            # Count by severity
            severity = alert.severity.value
            active_by_severity[severity] = active_by_severity.get(severity, 0) + 1

            # Count by category
            category = alert.category.value
            active_by_category[category] = active_by_category.get(category, 0) + 1

        return {
            "active_alerts": len(self.active_alerts),
            "total_rules": len(self.alert_rules),
            "enabled_rules": sum(
                1 for rule in self.alert_rules.values() if rule.enabled
            ),
            "correlation_groups": len(self.correlation_groups),
            "evaluation_count": self.evaluation_count,
            "last_evaluation": self.last_evaluation.isoformat(),
            "active_by_severity": active_by_severity,
            "active_by_category": active_by_category,
            "alert_history_size": len(self.alert_history),
        }

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        alert = self.active_alerts.get(alert_id)

        if not alert:
            return False

        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.now(timezone.utc)
        alert.updated_at = datetime.now(timezone.utc)

        logger.info(f"Alert acknowledged: {alert.name} by {acknowledged_by}")
        return True

    def add_alert_rule(self, rule: AlertRule) -> bool:
        """Add a new alert rule."""
        if rule.rule_id in self.alert_rules:
            logger.warning(f"Alert rule {rule.rule_id} already exists")
            return False

        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.name}")
        return True

    def remove_alert_rule(self, rule_id: str) -> bool:
        """Remove an alert rule."""
        if rule_id not in self.alert_rules:
            return False

        del self.alert_rules[rule_id]
        logger.info(f"Removed alert rule: {rule_id}")
        return True
