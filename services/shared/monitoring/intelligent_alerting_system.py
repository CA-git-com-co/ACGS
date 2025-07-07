"""
Intelligent Alerting System for ACGS

This module provides advanced alerting capabilities including:
- Machine learning-based anomaly detection
- Adaptive thresholds based on patterns
- Alert correlation and deduplication
- Intelligent notification routing
- Performance prediction and early warnings
"""

import asyncio
import json
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import structlog

from ..redis_client import ACGSRedisClient
from ..resource_management.enhanced_resource_manager import AlertLevel, ResourceType

logger = structlog.get_logger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class AnomalyType(Enum):
    """Types of anomalies that can be detected."""

    SPIKE = "spike"
    DIP = "dip"
    TREND_CHANGE = "trend_change"
    SEASONAL_DEVIATION = "seasonal_deviation"
    CORRELATION_BREAK = "correlation_break"


class NotificationChannel(Enum):
    """Notification delivery channels."""

    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    LOG = "log"
    DASHBOARD = "dashboard"


@dataclass
class AnomalyPattern:
    """Detected anomaly pattern."""

    timestamp: datetime
    resource_type: ResourceType
    anomaly_type: AnomalyType
    severity: float  # 0.0 to 1.0
    current_value: float
    expected_value: float
    confidence: float
    description: str
    related_metrics: List[str] = field(default_factory=list)


@dataclass
class AlertContext:
    """Context information for an alert."""

    alert_id: str
    resource_type: ResourceType
    level: AlertLevel
    timestamp: datetime
    current_value: float
    threshold: float
    duration_seconds: float
    related_alerts: List[str] = field(default_factory=list)
    root_cause_probability: float = 0.0
    historical_pattern: Optional[str] = None
    recommended_actions: List[str] = field(default_factory=list)


@dataclass
class NotificationRule:
    """Rules for notification routing."""

    resource_types: List[ResourceType]
    alert_levels: List[AlertLevel]
    channels: List[NotificationChannel]
    escalation_time: float = 300.0  # 5 minutes
    rate_limit_window: float = 60.0  # 1 minute
    rate_limit_count: int = 5
    enabled: bool = True
    filters: Dict[str, Any] = field(default_factory=dict)


class AnomalyDetector:
    """Machine learning-based anomaly detector."""

    def __init__(self, window_size: int = 100, sensitivity: float = 2.0):
        self.window_size = window_size
        self.sensitivity = sensitivity
        self.baseline_data: Dict[ResourceType, deque] = defaultdict(
            lambda: deque(maxlen=window_size)
        )
        self.seasonal_patterns: Dict[ResourceType, List[float]] = {}

    def add_data_point(
        self, resource_type: ResourceType, value: float, timestamp: datetime
    ):
        """Add a new data point for analysis."""
        self.baseline_data[resource_type].append(
            {"value": value, "timestamp": timestamp}
        )

        # Update seasonal patterns if we have enough data
        if len(self.baseline_data[resource_type]) >= self.window_size:
            self._update_seasonal_pattern(resource_type)

    def detect_anomalies(
        self, resource_type: ResourceType, current_value: float
    ) -> List[AnomalyPattern]:
        """Detect anomalies in the current value."""
        anomalies = []
        data = self.baseline_data[resource_type]

        if len(data) < 10:  # Need minimum data points
            return anomalies

        # Get historical values
        values = [d["value"] for d in data]
        timestamps = [d["timestamp"] for d in data]

        # Statistical anomaly detection
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0

        # Z-score based detection
        if std_dev > 0:
            z_score = abs(current_value - mean_value) / std_dev

            if z_score > self.sensitivity:
                anomaly_type = (
                    AnomalyType.SPIKE if current_value > mean_value else AnomalyType.DIP
                )
                severity = min(1.0, z_score / (self.sensitivity * 2))
                confidence = min(1.0, (z_score - self.sensitivity) / self.sensitivity)

                anomalies.append(
                    AnomalyPattern(
                        timestamp=datetime.now(),
                        resource_type=resource_type,
                        anomaly_type=anomaly_type,
                        severity=severity,
                        current_value=current_value,
                        expected_value=mean_value,
                        confidence=confidence,
                        description=f"{anomaly_type.value.title()} detected: {current_value:.2f} vs expected {mean_value:.2f}",
                    )
                )

        # Trend change detection
        if len(values) >= 20:
            recent_trend = self._calculate_trend(values[-10:])
            historical_trend = self._calculate_trend(values[-20:-10])

            if abs(recent_trend - historical_trend) > 0.5:  # Significant trend change
                anomalies.append(
                    AnomalyPattern(
                        timestamp=datetime.now(),
                        resource_type=resource_type,
                        anomaly_type=AnomalyType.TREND_CHANGE,
                        severity=min(1.0, abs(recent_trend - historical_trend) / 2.0),
                        current_value=current_value,
                        expected_value=mean_value,
                        confidence=0.7,
                        description=f"Trend change detected: {recent_trend:.2f} vs {historical_trend:.2f}",
                    )
                )

        # Seasonal deviation detection
        if resource_type in self.seasonal_patterns:
            expected_seasonal = self._get_seasonal_expectation(
                resource_type, datetime.now()
            )
            if (
                expected_seasonal
                and abs(current_value - expected_seasonal) > std_dev * 2
            ):
                anomalies.append(
                    AnomalyPattern(
                        timestamp=datetime.now(),
                        resource_type=resource_type,
                        anomaly_type=AnomalyType.SEASONAL_DEVIATION,
                        severity=min(
                            1.0, abs(current_value - expected_seasonal) / (std_dev * 4)
                        ),
                        current_value=current_value,
                        expected_value=expected_seasonal,
                        confidence=0.8,
                        description=f"Seasonal deviation: {current_value:.2f} vs seasonal expectation {expected_seasonal:.2f}",
                    )
                )

        return anomalies

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend (slope) of values."""
        if len(values) < 2:
            return 0.0

        x = list(range(len(values)))
        return np.polyfit(x, values, 1)[0] if len(values) > 1 else 0.0

    def _update_seasonal_pattern(self, resource_type: ResourceType):
        """Update seasonal pattern for a resource type."""
        data = self.baseline_data[resource_type]

        # Group by hour of day to find patterns
        hourly_averages = defaultdict(list)
        for d in data:
            hour = d["timestamp"].hour
            hourly_averages[hour].append(d["value"])

        # Calculate average for each hour
        pattern = []
        for hour in range(24):
            if hour in hourly_averages and hourly_averages[hour]:
                pattern.append(statistics.mean(hourly_averages[hour]))
            else:
                pattern.append(0.0)

        self.seasonal_patterns[resource_type] = pattern

    def _get_seasonal_expectation(
        self, resource_type: ResourceType, timestamp: datetime
    ) -> Optional[float]:
        """Get seasonal expectation for a timestamp."""
        if resource_type not in self.seasonal_patterns:
            return None

        hour = timestamp.hour
        return self.seasonal_patterns[resource_type][hour]


class AlertCorrelator:
    """Correlates related alerts to identify root causes."""

    def __init__(self, correlation_window: float = 300.0):  # 5 minutes
        self.correlation_window = correlation_window
        self.alert_groups: Dict[str, List[AlertContext]] = {}
        self.correlation_rules: List[Callable] = []

        # Initialize default correlation rules
        self._init_correlation_rules()

    def _init_correlation_rules(self):
        """Initialize default correlation rules."""

        def memory_cpu_correlation(alerts: List[AlertContext]) -> bool:
            """High memory usage often correlates with high CPU usage."""
            memory_alerts = [
                a for a in alerts if a.resource_type == ResourceType.MEMORY
            ]
            cpu_alerts = [a for a in alerts if a.resource_type == ResourceType.CPU]
            return len(memory_alerts) > 0 and len(cpu_alerts) > 0

        def db_connection_correlation(alerts: List[AlertContext]) -> bool:
            """Database connection issues often correlate with performance issues."""
            db_alerts = [
                a
                for a in alerts
                if a.resource_type == ResourceType.DATABASE_CONNECTIONS
            ]
            perf_alerts = [
                a
                for a in alerts
                if a.resource_type in [ResourceType.CPU, ResourceType.MEMORY]
            ]
            return len(db_alerts) > 0 and len(perf_alerts) > 0

        self.correlation_rules.extend(
            [memory_cpu_correlation, db_connection_correlation]
        )

    def add_alert(self, alert: AlertContext) -> Optional[str]:
        """Add an alert and return correlation group ID if correlated."""
        current_time = alert.timestamp

        # Find potential correlation groups
        for group_id, group_alerts in self.alert_groups.items():
            # Check if any alert in group is within correlation window
            if any(
                (current_time - existing_alert.timestamp).total_seconds()
                <= self.correlation_window
                for existing_alert in group_alerts
            ):
                # Check correlation rules
                test_group = group_alerts + [alert]
                if any(rule(test_group) for rule in self.correlation_rules):
                    group_alerts.append(alert)
                    alert.related_alerts = [
                        a.alert_id for a in group_alerts if a.alert_id != alert.alert_id
                    ]

                    # Update root cause probabilities
                    self._update_root_cause_probabilities(group_alerts)

                    return group_id

        # Create new correlation group
        group_id = f"group_{int(time.time())}_{alert.alert_id[:8]}"
        self.alert_groups[group_id] = [alert]

        return group_id

    def _update_root_cause_probabilities(self, alerts: List[AlertContext]):
        """Update root cause probabilities for correlated alerts."""
        # Simple heuristic: earlier alerts are more likely to be root causes
        alerts.sort(key=lambda a: a.timestamp)

        for i, alert in enumerate(alerts):
            # Higher probability for earlier, more severe alerts
            time_factor = 1.0 - (i / len(alerts)) * 0.5
            severity_factor = 1.0 if alert.level == AlertLevel.CRITICAL else 0.8
            alert.root_cause_probability = time_factor * severity_factor

    def cleanup_old_groups(self):
        """Clean up old correlation groups."""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=self.correlation_window * 2)

        groups_to_remove = []
        for group_id, alerts in self.alert_groups.items():
            if all(alert.timestamp < cutoff_time for alert in alerts):
                groups_to_remove.append(group_id)

        for group_id in groups_to_remove:
            del self.alert_groups[group_id]


class IntelligentAlertingSystem:
    """Intelligent alerting system with ML-based anomaly detection."""

    def __init__(
        self,
        redis_client: ACGSRedisClient,
        anomaly_sensitivity: float = 2.0,
        correlation_window: float = 300.0,
    ):
        self.redis_client = redis_client

        # Components
        self.anomaly_detector = AnomalyDetector(sensitivity=anomaly_sensitivity)
        self.alert_correlator = AlertCorrelator(correlation_window=correlation_window)

        # Configuration
        self.notification_rules: List[NotificationRule] = []
        self.adaptive_thresholds: Dict[ResourceType, Dict[str, float]] = defaultdict(
            dict
        )

        # State tracking
        self.active_alerts: Dict[str, AlertContext] = {}
        self.alert_history: deque = deque(maxlen=10000)
        self.notification_rate_limits: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )

        # Background tasks
        self._analysis_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

        # Performance metrics
        self.metrics = {
            "total_alerts": 0,
            "anomalies_detected": 0,
            "correlations_found": 0,
            "notifications_sent": 0,
            "false_positives": 0,
            "adaptive_threshold_updates": 0,
        }

    async def start(self):
        """Start the intelligent alerting system."""
        if self._running:
            return

        self._running = True

        # Initialize default notification rules
        self._init_default_notification_rules()

        # Start background tasks
        self._analysis_task = asyncio.create_task(self._analysis_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info(
            "Intelligent alerting system started",
            constitutional_hash=CONSTITUTIONAL_HASH,
        )

    async def stop(self):
        """Stop the intelligent alerting system."""
        self._running = False

        # Cancel background tasks
        for task in [self._analysis_task, self._cleanup_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        logger.info("Intelligent alerting system stopped")

    def _init_default_notification_rules(self):
        """Initialize default notification rules."""
        # Constitutional alerts - highest priority
        self.notification_rules.append(
            NotificationRule(
                resource_types=list(ResourceType),
                alert_levels=[AlertLevel.CRITICAL, AlertLevel.EMERGENCY],
                channels=[
                    NotificationChannel.SLACK,
                    NotificationChannel.EMAIL,
                    NotificationChannel.LOG,
                ],
                escalation_time=120.0,  # 2 minutes
                rate_limit_window=30.0,
                rate_limit_count=3,
            )
        )

        # Warning alerts
        self.notification_rules.append(
            NotificationRule(
                resource_types=list(ResourceType),
                alert_levels=[AlertLevel.WARNING],
                channels=[NotificationChannel.LOG, NotificationChannel.DASHBOARD],
                escalation_time=600.0,  # 10 minutes
                rate_limit_window=120.0,
                rate_limit_count=5,
            )
        )

    async def process_metric_update(
        self,
        resource_type: ResourceType,
        current_value: float,
        timestamp: Optional[datetime] = None,
    ):
        """Process a metric update and detect anomalies."""
        if timestamp is None:
            timestamp = datetime.now()

        # Add to anomaly detector
        self.anomaly_detector.add_data_point(resource_type, current_value, timestamp)

        # Detect anomalies
        anomalies = self.anomaly_detector.detect_anomalies(resource_type, current_value)

        for anomaly in anomalies:
            await self._process_anomaly(anomaly)
            self.metrics["anomalies_detected"] += 1

        # Update adaptive thresholds
        await self._update_adaptive_thresholds(resource_type, current_value, anomalies)

    async def _process_anomaly(self, anomaly: AnomalyPattern):
        """Process a detected anomaly."""
        # Determine alert level based on severity
        if anomaly.severity >= 0.8:
            alert_level = AlertLevel.CRITICAL
        elif anomaly.severity >= 0.6:
            alert_level = AlertLevel.WARNING
        else:
            alert_level = AlertLevel.INFO

        # Create alert context
        alert_context = AlertContext(
            alert_id=f"anomaly_{int(time.time())}_{anomaly.resource_type.value}",
            resource_type=anomaly.resource_type,
            level=alert_level,
            timestamp=anomaly.timestamp,
            current_value=anomaly.current_value,
            threshold=anomaly.expected_value,
            duration_seconds=0.0,  # Anomalies are instant
            recommended_actions=self._get_recommended_actions(anomaly),
        )

        await self._process_alert(alert_context)

    async def process_threshold_alert(
        self,
        resource_type: ResourceType,
        level: AlertLevel,
        current_value: float,
        threshold: float,
        duration: float,
    ):
        """Process a threshold-based alert."""
        alert_context = AlertContext(
            alert_id=f"threshold_{int(time.time())}_{resource_type.value}",
            resource_type=resource_type,
            level=level,
            timestamp=datetime.now(),
            current_value=current_value,
            threshold=threshold,
            duration_seconds=duration,
            recommended_actions=self._get_threshold_recommended_actions(
                resource_type, level
            ),
        )

        await self._process_alert(alert_context)

    async def _process_alert(self, alert_context: AlertContext):
        """Process an alert through the intelligent system."""
        # Add to correlation analysis
        correlation_group = self.alert_correlator.add_alert(alert_context)

        if (
            correlation_group
            and len(self.alert_correlator.alert_groups[correlation_group]) > 1
        ):
            self.metrics["correlations_found"] += 1

        # Store alert
        self.active_alerts[alert_context.alert_id] = alert_context
        self.alert_history.append(
            {
                "alert_id": alert_context.alert_id,
                "resource_type": alert_context.resource_type.value,
                "level": alert_context.level.value,
                "timestamp": alert_context.timestamp.isoformat(),
                "current_value": alert_context.current_value,
                "threshold": alert_context.threshold,
                "root_cause_probability": alert_context.root_cause_probability,
            }
        )

        # Persist to Redis
        await self._persist_alert(alert_context)

        # Send notifications
        await self._send_notifications(alert_context)

        self.metrics["total_alerts"] += 1

        logger.info(
            "Alert processed",
            alert_id=alert_context.alert_id,
            resource_type=alert_context.resource_type.value,
            level=alert_context.level.value,
            correlation_group=correlation_group,
        )

    async def _update_adaptive_thresholds(
        self,
        resource_type: ResourceType,
        current_value: float,
        anomalies: List[AnomalyPattern],
    ):
        """Update adaptive thresholds based on patterns."""
        # Simple adaptive threshold logic
        baseline_data = self.anomaly_detector.baseline_data[resource_type]

        if len(baseline_data) >= 50:  # Need sufficient data
            values = [d["value"] for d in baseline_data]
            mean_val = statistics.mean(values)
            std_dev = statistics.stdev(values) if len(values) > 1 else 0

            # Calculate adaptive thresholds
            warning_threshold = mean_val + (std_dev * 1.5)
            critical_threshold = mean_val + (std_dev * 2.0)
            emergency_threshold = mean_val + (std_dev * 2.5)

            # Update if significantly different from current
            current_thresholds = self.adaptive_thresholds[resource_type]

            if (
                abs(current_thresholds.get("warning", 0) - warning_threshold)
                > std_dev * 0.2
            ):
                current_thresholds["warning"] = warning_threshold
                current_thresholds["critical"] = critical_threshold
                current_thresholds["emergency"] = emergency_threshold

                self.metrics["adaptive_threshold_updates"] += 1

                logger.debug(
                    "Adaptive thresholds updated",
                    resource_type=resource_type.value,
                    warning=warning_threshold,
                    critical=critical_threshold,
                )

    def _get_recommended_actions(self, anomaly: AnomalyPattern) -> List[str]:
        """Get recommended actions for an anomaly."""
        actions = []

        if anomaly.resource_type == ResourceType.MEMORY:
            if anomaly.anomaly_type == AnomalyType.SPIKE:
                actions.extend(
                    [
                        "Check for memory leaks in recent deployments",
                        "Review application memory usage patterns",
                        "Consider increasing memory allocation if trend continues",
                    ]
                )
        elif anomaly.resource_type == ResourceType.CPU:
            if anomaly.anomaly_type == AnomalyType.SPIKE:
                actions.extend(
                    [
                        "Identify processes causing high CPU usage",
                        "Check for inefficient algorithms or loops",
                        "Consider load balancing or scaling",
                    ]
                )
        elif anomaly.resource_type == ResourceType.DATABASE_CONNECTIONS:
            actions.extend(
                [
                    "Review connection pool configuration",
                    "Check for connection leaks",
                    "Monitor query performance",
                ]
            )

        # Constitutional-specific actions
        if CONSTITUTIONAL_HASH in str(anomaly.related_metrics):
            actions.append("Review constitutional compliance processes")

        return actions

    def _get_threshold_recommended_actions(
        self, resource_type: ResourceType, level: AlertLevel
    ) -> List[str]:
        """Get recommended actions for threshold alerts."""
        actions = []

        if level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
            actions.append("Immediate investigation required")

            if resource_type == ResourceType.MEMORY:
                actions.extend(
                    [
                        "Check for memory leaks",
                        "Restart services if necessary",
                        "Scale up memory resources",
                    ]
                )
            elif resource_type == ResourceType.DATABASE_CONNECTIONS:
                actions.extend(
                    [
                        "Check connection pool health",
                        "Restart database proxy if needed",
                        "Scale connection limits",
                    ]
                )

        return actions

    async def _send_notifications(self, alert_context: AlertContext):
        """Send notifications according to rules."""
        for rule in self.notification_rules:
            if not rule.enabled:
                continue

            # Check if rule applies to this alert
            if (
                alert_context.resource_type not in rule.resource_types
                or alert_context.level not in rule.alert_levels
            ):
                continue

            # Check rate limiting
            rule_key = f"{rule.resource_types[0].value}_{rule.alert_levels[0].value}"
            rate_limit_history = self.notification_rate_limits[rule_key]

            # Clean old entries
            cutoff_time = datetime.now() - timedelta(seconds=rule.rate_limit_window)
            while rate_limit_history and rate_limit_history[0] < cutoff_time:
                rate_limit_history.popleft()

            # Check if we've hit rate limit
            if len(rate_limit_history) >= rule.rate_limit_count:
                logger.warning(
                    "Notification rate limit hit",
                    rule_key=rule_key,
                    count=len(rate_limit_history),
                )
                continue

            # Send notifications
            for channel in rule.channels:
                try:
                    await self._send_notification(channel, alert_context, rule)
                    rate_limit_history.append(datetime.now())
                    self.metrics["notifications_sent"] += 1
                except Exception as e:
                    logger.error(
                        "Failed to send notification",
                        channel=channel.value,
                        error=str(e),
                    )

    async def _send_notification(
        self,
        channel: NotificationChannel,
        alert_context: AlertContext,
        rule: NotificationRule,
    ):
        """Send notification to specific channel."""
        if channel == NotificationChannel.LOG:
            logger.warning(
                "ALERT",
                alert_id=alert_context.alert_id,
                resource_type=alert_context.resource_type.value,
                level=alert_context.level.value,
                current_value=alert_context.current_value,
                threshold=alert_context.threshold,
                recommended_actions=alert_context.recommended_actions,
            )

        elif channel == NotificationChannel.DASHBOARD:
            # Store alert for dashboard consumption
            dashboard_key = f"acgs:dashboard:alerts:{alert_context.alert_id}"
            await self.redis_client.set_json(
                dashboard_key,
                {
                    "alert_id": alert_context.alert_id,
                    "resource_type": alert_context.resource_type.value,
                    "level": alert_context.level.value,
                    "timestamp": alert_context.timestamp.isoformat(),
                    "current_value": alert_context.current_value,
                    "threshold": alert_context.threshold,
                    "recommended_actions": alert_context.recommended_actions,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                ttl=3600,  # 1 hour
            )

        # Additional channels (EMAIL, SLACK, etc.) would be implemented here
        # with appropriate service integrations

    async def _persist_alert(self, alert_context: AlertContext):
        """Persist alert to Redis for durability."""
        alert_key = f"acgs:alerts:{alert_context.alert_id}"
        alert_data = {
            "alert_id": alert_context.alert_id,
            "resource_type": alert_context.resource_type.value,
            "level": alert_context.level.value,
            "timestamp": alert_context.timestamp.isoformat(),
            "current_value": alert_context.current_value,
            "threshold": alert_context.threshold,
            "duration_seconds": alert_context.duration_seconds,
            "related_alerts": alert_context.related_alerts,
            "root_cause_probability": alert_context.root_cause_probability,
            "recommended_actions": alert_context.recommended_actions,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        await self.redis_client.set_json(alert_key, alert_data, ttl=86400)  # 24 hours

    async def _analysis_loop(self):
        """Background analysis loop for pattern learning."""
        try:
            while self._running:
                await asyncio.sleep(60)  # Run every minute

                # Update correlation patterns
                self.alert_correlator.cleanup_old_groups()

                # Analyze false positives (simplified)
                await self._analyze_false_positives()

        except asyncio.CancelledError:
            logger.info("Analysis loop cancelled")

    async def _analyze_false_positives(self):
        """Analyze and learn from false positives."""
        # Simple false positive detection based on alert resolution
        # In practice, this would involve more sophisticated ML

        current_time = datetime.now()
        for alert_id, alert_context in list(self.active_alerts.items()):
            # If alert is old and resource is back to normal, mark as resolved
            age = (current_time - alert_context.timestamp).total_seconds()

            if age > 600:  # 10 minutes old
                # In a real implementation, check if resource is back to normal
                # For now, just clean up old alerts
                del self.active_alerts[alert_id]

    async def _cleanup_loop(self):
        """Background cleanup of old data."""
        try:
            while self._running:
                await asyncio.sleep(300)  # Every 5 minutes

                # Clean up old notification rate limit data
                cutoff_time = datetime.now() - timedelta(hours=1)
                for channel_history in self.notification_rate_limits.values():
                    while channel_history and channel_history[0] < cutoff_time:
                        channel_history.popleft()

        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled")

    def get_adaptive_thresholds(self, resource_type: ResourceType) -> Dict[str, float]:
        """Get current adaptive thresholds for a resource type."""
        return self.adaptive_thresholds[resource_type].copy()

    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get comprehensive alert statistics."""
        return {
            "metrics": self.metrics,
            "active_alerts_count": len(self.active_alerts),
            "correlation_groups_count": len(self.alert_correlator.alert_groups),
            "notification_rules_count": len(self.notification_rules),
            "adaptive_thresholds": {
                resource_type.value: thresholds
                for resource_type, thresholds in self.adaptive_thresholds.items()
            },
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Acknowledge an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]

            # Store acknowledgment
            ack_key = f"acgs:alert_ack:{alert_id}"
            await self.redis_client.set_json(
                ack_key,
                {
                    "alert_id": alert_id,
                    "acknowledged_by": acknowledged_by,
                    "acknowledged_at": datetime.now().isoformat(),
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                ttl=86400,
            )

            logger.info(
                "Alert acknowledged", alert_id=alert_id, acknowledged_by=acknowledged_by
            )

    async def resolve_alert(
        self, alert_id: str, resolved_by: str, resolution_notes: str = ""
    ):
        """Resolve an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]

            # Store resolution
            resolution_key = f"acgs:alert_resolution:{alert_id}"
            await self.redis_client.set_json(
                resolution_key,
                {
                    "alert_id": alert_id,
                    "resolved_by": resolved_by,
                    "resolved_at": datetime.now().isoformat(),
                    "resolution_notes": resolution_notes,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                ttl=86400,
            )

            # Remove from active alerts
            del self.active_alerts[alert_id]

            logger.info("Alert resolved", alert_id=alert_id, resolved_by=resolved_by)
