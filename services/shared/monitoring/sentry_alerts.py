"""
Sentry Alert Configuration for ACGS-2 Constitutional Monitoring

Defines alert rules and thresholds for constitutional compliance,
performance targets, and multi-agent coordination issues.

Constitutional Hash: cdd01ef066bc6cf2
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

import sentry_sdk

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class AlertSeverity(Enum):
    """Alert severity levels for constitutional governance"""

    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"  # Urgent attention needed
    MEDIUM = "medium"  # Should be addressed soon
    LOW = "low"  # Informational


class AlertCategory(Enum):
    """Categories of alerts in ACGS-2"""

    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SECURITY_VIOLATION = "security_violation"
    AGENT_COORDINATION_FAILURE = "agent_coordination_failure"
    SERVICE_HEALTH = "service_health"
    DATA_INTEGRITY = "data_integrity"


@dataclass
class AlertThreshold:
    """Define thresholds for different alert types"""

    metric_name: str
    critical_threshold: float
    high_threshold: float
    medium_threshold: float
    low_threshold: float
    unit: str
    description: str


# Define ACGS-2 specific alert thresholds
ALERT_THRESHOLDS = {
    "constitutional_compliance_rate": AlertThreshold(
        metric_name="constitutional_compliance_rate",
        critical_threshold=0.95,  # <95% is critical
        high_threshold=0.97,  # <97% is high priority
        medium_threshold=0.99,  # <99% is medium
        low_threshold=1.0,  # <100% is low
        unit="percentage",
        description="Constitutional compliance validation success rate",
    ),
    "p99_latency": AlertThreshold(
        metric_name="p99_latency",
        critical_threshold=10.0,  # >10ms is critical
        high_threshold=7.5,  # >7.5ms is high
        medium_threshold=5.0,  # >5ms is medium (target)
        low_threshold=3.0,  # >3ms is low
        unit="ms",
        description="99th percentile request latency",
    ),
    "error_rate": AlertThreshold(
        metric_name="error_rate",
        critical_threshold=0.05,  # >5% error rate is critical
        high_threshold=0.02,  # >2% is high
        medium_threshold=0.01,  # >1% is medium
        low_threshold=0.005,  # >0.5% is low
        unit="percentage",
        description="Overall service error rate",
    ),
    "cache_hit_rate": AlertThreshold(
        metric_name="cache_hit_rate",
        critical_threshold=0.70,  # <70% is critical
        high_threshold=0.80,  # <80% is high
        medium_threshold=0.85,  # <85% is medium (target)
        low_threshold=0.90,  # <90% is low
        unit="percentage",
        description="Constitutional validation cache hit rate",
    ),
    "agent_consensus_rate": AlertThreshold(
        metric_name="agent_consensus_rate",
        critical_threshold=0.80,  # <80% consensus is critical
        high_threshold=0.85,  # <85% is high
        medium_threshold=0.90,  # <90% is medium
        low_threshold=0.95,  # <95% is low
        unit="percentage",
        description="Multi-agent consensus achievement rate",
    ),
    "memory_usage": AlertThreshold(
        metric_name="memory_usage",
        critical_threshold=0.95,  # >95% memory is critical
        high_threshold=0.90,  # >90% is high
        medium_threshold=0.85,  # >85% is medium
        low_threshold=0.80,  # >80% is low
        unit="percentage",
        description="Service memory utilization",
    ),
}


class ConstitutionalAlertManager:
    """Manages alerts for constitutional compliance and governance"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.alert_history: list[dict[str, Any]] = []

    def check_threshold(
        self,
        metric_name: str,
        current_value: float,
        metadata: dict[str, Any] | None = None,
    ) -> AlertSeverity | None:
        """Check if a metric breaches defined thresholds"""
        if metric_name not in ALERT_THRESHOLDS:
            return None

        threshold = ALERT_THRESHOLDS[metric_name]
        severity = None

        # Determine severity based on threshold direction
        if metric_name in {
            "constitutional_compliance_rate",
            "cache_hit_rate",
            "agent_consensus_rate",
        }:
            # Lower values are worse
            if current_value < threshold.critical_threshold:
                severity = AlertSeverity.CRITICAL
            elif current_value < threshold.high_threshold:
                severity = AlertSeverity.HIGH
            elif current_value < threshold.medium_threshold:
                severity = AlertSeverity.MEDIUM
            elif current_value < threshold.low_threshold:
                severity = AlertSeverity.LOW
        # Higher values are worse
        elif current_value > threshold.critical_threshold:
            severity = AlertSeverity.CRITICAL
        elif current_value > threshold.high_threshold:
            severity = AlertSeverity.HIGH
        elif current_value > threshold.medium_threshold:
            severity = AlertSeverity.MEDIUM
        elif current_value > threshold.low_threshold:
            severity = AlertSeverity.LOW

        if severity:
            self._trigger_alert(
                metric_name=metric_name,
                current_value=current_value,
                threshold=threshold,
                severity=severity,
                metadata=metadata,
            )

        return severity

    def _trigger_alert(
        self,
        metric_name: str,
        current_value: float,
        threshold: AlertThreshold,
        severity: AlertSeverity,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Trigger an alert in Sentry"""
        alert_data = {
            "metric_name": metric_name,
            "current_value": f"{current_value}{threshold.unit}",
            "severity": severity.value,
            "service": self.service_name,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "threshold_breached": self._get_breached_threshold(severity, threshold),
            "metadata": metadata or {},
        }

        # Record in history
        self.alert_history.append(alert_data)

        # Send to Sentry with appropriate level
        sentry_level = self._severity_to_sentry_level(severity)

        sentry_sdk.capture_message(
            f"Alert: {threshold.description} breach",
            level=sentry_level,
            tags={
                "alert_severity": severity.value,
                "metric_name": metric_name,
                "service": self.service_name,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
            extra=alert_data,
        )

        # For critical alerts, add additional context
        if severity == AlertSeverity.CRITICAL:
            sentry_sdk.set_context(
                "critical_alert",
                {
                    "metric": metric_name,
                    "value": current_value,
                    "threshold": threshold.critical_threshold,
                    "requires_immediate_action": True,
                },
            )

    def _get_breached_threshold(
        self, severity: AlertSeverity, threshold: AlertThreshold
    ) -> float:
        """Get the specific threshold that was breached"""
        mapping = {
            AlertSeverity.CRITICAL: threshold.critical_threshold,
            AlertSeverity.HIGH: threshold.high_threshold,
            AlertSeverity.MEDIUM: threshold.medium_threshold,
            AlertSeverity.LOW: threshold.low_threshold,
        }
        return mapping[severity]

    def _severity_to_sentry_level(self, severity: AlertSeverity) -> str:
        """Convert alert severity to Sentry level"""
        mapping = {
            AlertSeverity.CRITICAL: "fatal",
            AlertSeverity.HIGH: "error",
            AlertSeverity.MEDIUM: "warning",
            AlertSeverity.LOW: "info",
        }
        return mapping[severity]

    def trigger_constitutional_violation(
        self,
        violation_type: str,
        description: str,
        affected_services: list[str],
        remediation_steps: list[str] | None = None,
    ) -> None:
        """Trigger a constitutional compliance violation alert"""
        sentry_sdk.capture_message(
            f"Constitutional Violation: {violation_type}",
            level="error",
            tags={
                "constitutional_violation": True,
                "violation_type": violation_type,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "alert_category": AlertCategory.CONSTITUTIONAL_COMPLIANCE.value,
            },
            extra={
                "description": description,
                "affected_services": affected_services,
                "remediation_steps": remediation_steps or [],
                "service": self.service_name,
            },
        )

    def trigger_security_alert(
        self,
        security_event: str,
        risk_level: str,
        details: dict[str, Any],
        immediate_action_required: bool = False,
    ) -> None:
        """Trigger a security-related alert"""
        level = "fatal" if immediate_action_required else "error"

        sentry_sdk.capture_message(
            f"Security Alert: {security_event}",
            level=level,
            tags={
                "security_alert": True,
                "security_event": security_event,
                "risk_level": risk_level,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "alert_category": AlertCategory.SECURITY_VIOLATION.value,
            },
            extra={
                "details": details,
                "service": self.service_name,
                "immediate_action_required": immediate_action_required,
            },
        )

    def trigger_agent_coordination_failure(
        self,
        agents_involved: list[str],
        task_type: str,
        failure_reason: str,
        consensus_score: float | None = None,
    ) -> None:
        """Trigger alert for multi-agent coordination failures"""
        sentry_sdk.capture_message(
            f"Agent Coordination Failure: {task_type}",
            level="error",
            tags={
                "agent_failure": True,
                "task_type": task_type,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "alert_category": AlertCategory.AGENT_COORDINATION_FAILURE.value,
            },
            extra={
                "agents_involved": agents_involved,
                "failure_reason": failure_reason,
                "consensus_score": consensus_score,
                "service": self.service_name,
            },
        )


# Predefined alert rules for common scenarios
class AlertRules:
    """Predefined alert rules for ACGS-2 monitoring"""

    @staticmethod
    def check_constitutional_compliance(
        compliance_rate: float, service_name: str
    ) -> None:
        """Check and alert on constitutional compliance rate"""
        manager = ConstitutionalAlertManager(service_name)
        severity = manager.check_threshold(
            "constitutional_compliance_rate",
            compliance_rate,
            metadata={"check_type": "periodic_validation"},
        )

        # Additional actions for critical compliance failures
        if severity == AlertSeverity.CRITICAL:
            sentry_sdk.capture_message(
                "CRITICAL: Constitutional compliance breach - Human oversight required",
                level="fatal",
                tags={
                    "requires_human_oversight": True,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            )

    @staticmethod
    def check_performance_sla(p99_latency: float, service_name: str) -> None:
        """Check and alert on performance SLA breaches"""
        manager = ConstitutionalAlertManager(service_name)
        manager.check_threshold(
            "p99_latency", p99_latency, metadata={"sla_target": "5ms"}
        )

    @staticmethod
    def check_multi_agent_consensus(
        consensus_rate: float, task_type: str, service_name: str
    ) -> None:
        """Check and alert on multi-agent consensus rates"""
        manager = ConstitutionalAlertManager(service_name)
        severity = manager.check_threshold(
            "agent_consensus_rate",
            consensus_rate,
            metadata={"task_type": task_type, "agent_coordination": True},
        )

        # Log pattern for repeated consensus failures
        if severity in {AlertSeverity.CRITICAL, AlertSeverity.HIGH}:
            sentry_sdk.add_breadcrumb(
                message=f"Low consensus rate detected: {consensus_rate:.2%}",
                category="agent.consensus",
                level="warning",
                data={"task_type": task_type, "consensus_rate": consensus_rate},
            )
