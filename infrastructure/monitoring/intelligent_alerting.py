#!/usr/bin/env python3
"""
ACGS-1 Intelligent Alerting with Automated Remediation
Enterprise-grade alerting system with ML-based anomaly detection and automated response
"""

import asyncio
import json
import logging
import time
import subprocess
import os
import hashlib
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
import httpx
import yaml
from dataclasses import dataclass, asdict
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram
from prometheus_client.gateway import push_to_gateway

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"


class RemediationStatus(Enum):
    """Remediation status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class Alert:
    """Alert data structure"""
    id: str
    name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    source: str
    timestamp: datetime
    labels: Dict[str, str]
    annotations: Dict[str, str]
    remediation_attempted: bool = False
    remediation_success: bool = False
    escalation_level: int = 0
    last_notification: Optional[datetime] = None
    acknowledgment_time: Optional[datetime] = None
    resolution_time: Optional[datetime] = None


@dataclass
class RemediationAction:
    """Remediation action definition"""
    name: str
    command: str
    timeout: int = 300
    retry_count: int = 3
    conditions: List[str] = None
    escalation_delay: int = 300
    requires_approval: bool = False
    impact_level: str = "low"  # low, medium, high, critical


@dataclass
class RemediationResult:
    """Remediation execution result"""
    action_name: str
    status: RemediationStatus
    start_time: datetime
    end_time: Optional[datetime]
    output: str
    error: Optional[str]
    exit_code: Optional[int]


class IntelligentAlertManager:
    """
    Intelligent Alert Manager with automated remediation capabilities
    """

    def __init__(self, config_path: str = "config/intelligent_alerting.json"):
        self.config = self._load_config(config_path)
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.remediation_actions: Dict[str, RemediationAction] = {}
        self.notification_channels: Dict[str, Dict] = {}
        self.escalation_policies: Dict[str, Dict] = {}
        self.remediation_history: List[RemediationResult] = []
        
        # State tracking
        self.last_notification_times: Dict[str, datetime] = {}
        self.suppressed_alerts: Dict[str, datetime] = {}
        self.running_remediations: Dict[str, asyncio.Task] = {}
        
        # Metrics
        self.registry = CollectorRegistry()
        self.alert_counter = Counter(
            'acgs_alerts_total',
            'Total number of alerts generated',
            ['severity', 'source', 'alert_name'],
            registry=self.registry
        )
        self.remediation_counter = Counter(
            'acgs_remediations_total',
            'Total number of automated remediations attempted',
            ['action', 'success'],
            registry=self.registry
        )
        self.alert_duration = Histogram(
            'acgs_alert_duration_seconds',
            'Duration of alerts from creation to resolution',
            ['severity', 'alert_name'],
            registry=self.registry
        )
        self.notification_counter = Counter(
            'acgs_notifications_total',
            'Total notifications sent',
            ['channel', 'severity'],
            registry=self.registry
        )
        
        self._initialize_remediation_actions()
        self._initialize_notification_channels()
        self._initialize_escalation_policies()
        
        logger.info("Intelligent Alert Manager initialized")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "alert_retention_days": 30,
            "max_escalation_level": 3,
            "remediation_timeout": 300,
            "notification_cooldown": 300,
            "enable_automated_remediation": True,
            "enable_ml_anomaly_detection": True,
            "prometheus_pushgateway": "http://localhost:9091",
            "webhook_endpoints": {
                "slack": os.getenv("SLACK_WEBHOOK_URL", ""),
                "pagerduty": os.getenv("PAGERDUTY_WEBHOOK_URL", ""),
                "custom": os.getenv("CUSTOM_WEBHOOK_URL", "")
            },
            "notification_channels": {
                "email": {
                    "enabled": True,
                    "smtp_server": "localhost",
                    "smtp_port": 587,
                    "from_address": "acgs-alerts@acgs.ai"
                },
                "slack": {
                    "enabled": True,
                    "webhook_url": os.getenv("SLACK_WEBHOOK_URL", ""),
                    "channel": "#acgs-alerts"
                },
                "pagerduty": {
                    "enabled": False,
                    "integration_key": os.getenv("PAGERDUTY_INTEGRATION_KEY", "")
                }
            }
        }

    def _initialize_remediation_actions(self):
        """Initialize automated remediation actions"""
        self.remediation_actions = {
            "service_restart": RemediationAction(
                name="service_restart",
                command="python3 /home/dislove/ACGS-1/scripts/emergency_rollback_procedures.py restart",
                timeout=120,
                retry_count=2,
                impact_level="medium"
            ),
            "service_isolation": RemediationAction(
                name="service_isolation",
                command="python3 /home/dislove/ACGS-1/scripts/emergency_rollback_procedures.py isolate --service {service}",
                timeout=60,
                retry_count=1,
                impact_level="high"
            ),
            "health_check": RemediationAction(
                name="health_check",
                command="python3 /home/dislove/ACGS-1/scripts/emergency_rollback_procedures.py health",
                timeout=30,
                retry_count=3,
                impact_level="low"
            ),
            "clear_cache": RemediationAction(
                name="clear_cache",
                command="redis-cli FLUSHALL",
                timeout=30,
                retry_count=1,
                impact_level="medium"
            ),
            "restart_database": RemediationAction(
                name="restart_database",
                command="sudo systemctl restart postgresql",
                timeout=60,
                retry_count=1,
                requires_approval=True,
                impact_level="critical"
            ),
            "scale_service": RemediationAction(
                name="scale_service",
                command="docker-compose up --scale {service}=2",
                timeout=120,
                retry_count=1,
                impact_level="medium"
            )
        }

    def _initialize_notification_channels(self):
        """Initialize notification channels"""
        self.notification_channels = self.config.get("notification_channels", {})

    def _initialize_escalation_policies(self):
        """Initialize escalation policies"""
        self.escalation_policies = {
            "critical": {
                "immediate": ["slack", "pagerduty"],
                "5_minutes": ["email"],
                "15_minutes": ["phone"],
                "30_minutes": ["escalation_team"]
            },
            "high": {
                "immediate": ["slack"],
                "10_minutes": ["email"],
                "30_minutes": ["pagerduty"]
            },
            "medium": {
                "immediate": ["slack"],
                "1_hour": ["email"]
            },
            "low": {
                "immediate": ["slack"]
            }
        }

    async def generate_alert_id(self, alert_name: str, source: str) -> str:
        """Generate unique alert ID using SHA-256 (upgraded from MD5 for security)"""
        timestamp = str(int(time.time()))
        content = f"{alert_name}:{source}:{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    async def create_alert(
        self,
        name: str,
        severity: AlertSeverity,
        message: str,
        source: str,
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None
    ) -> Alert:
        """Create a new alert"""
        alert_id = await self.generate_alert_id(name, source)

        alert = Alert(
            id=alert_id,
            name=name,
            severity=severity,
            status=AlertStatus.ACTIVE,
            message=message,
            source=source,
            timestamp=datetime.now(),
            labels=labels or {},
            annotations=annotations or {}
        )

        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)

        # Update metrics
        self.alert_counter.labels(
            severity=severity.value,
            source=source,
            alert_name=name
        ).inc()

        logger.info(f"Alert created: {alert_id} - {name} ({severity.value})")

        # Trigger automated response
        await self._handle_new_alert(alert)

        return alert

    async def _handle_new_alert(self, alert: Alert):
        """Handle new alert with automated response"""
        try:
            # Check if alert should be suppressed
            if await self._should_suppress_alert(alert):
                alert.status = AlertStatus.SUPPRESSED
                logger.info(f"Alert {alert.id} suppressed due to cooldown or duplicate")
                return

            # Send notifications
            await self._send_notifications(alert)

            # Attempt automated remediation if enabled
            if self.config.get("enable_automated_remediation", True):
                await self._attempt_automated_remediation(alert)

            # Schedule escalation if needed
            await self._schedule_escalation(alert)

        except Exception as e:
            logger.error(f"Error handling alert {alert.id}: {e}")

    async def _should_suppress_alert(self, alert: Alert) -> bool:
        """Check if alert should be suppressed"""
        # Check cooldown period
        cooldown = self.config.get("notification_cooldown", 300)
        alert_key = f"{alert.name}:{alert.source}"

        if alert_key in self.last_notification_times:
            last_time = self.last_notification_times[alert_key]
            if (datetime.now() - last_time).total_seconds() < cooldown:
                return True

        # Check if similar alert is already active
        for active_alert in self.active_alerts.values():
            if (active_alert.name == alert.name and
                active_alert.source == alert.source and
                active_alert.status == AlertStatus.ACTIVE):
                return True

        return False

    async def _send_notifications(self, alert: Alert):
        """Send notifications through configured channels"""
        severity_policy = self.escalation_policies.get(alert.severity.value, {})
        immediate_channels = severity_policy.get("immediate", [])

        for channel in immediate_channels:
            try:
                await self._send_notification_to_channel(alert, channel)
                self.notification_counter.labels(
                    channel=channel,
                    severity=alert.severity.value
                ).inc()
            except Exception as e:
                logger.error(f"Failed to send notification to {channel}: {e}")

        # Update last notification time
        alert_key = f"{alert.name}:{alert.source}"
        self.last_notification_times[alert_key] = datetime.now()
        alert.last_notification = datetime.now()

    async def _send_notification_to_channel(self, alert: Alert, channel: str):
        """Send notification to specific channel"""
        if channel == "slack":
            await self._send_slack_notification(alert)
        elif channel == "pagerduty":
            await self._send_pagerduty_notification(alert)
        elif channel == "email":
            await self._send_email_notification(alert)
        elif channel == "webhook":
            await self._send_webhook_notification(alert)

    async def _send_slack_notification(self, alert: Alert):
        """Send Slack notification"""
        webhook_url = self.config["webhook_endpoints"].get("slack")
        if not webhook_url:
            logger.warning("Slack webhook URL not configured")
            return

        color_map = {
            AlertSeverity.CRITICAL: "danger",
            AlertSeverity.HIGH: "warning",
            AlertSeverity.MEDIUM: "warning",
            AlertSeverity.LOW: "good",
            AlertSeverity.INFO: "good"
        }

        payload = {
            "attachments": [{
                "color": color_map.get(alert.severity, "warning"),
                "title": f"🚨 ACGS-1 Alert: {alert.name}",
                "text": alert.message,
                "fields": [
                    {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                    {"title": "Source", "value": alert.source, "short": True},
                    {"title": "Time", "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "short": True},
                    {"title": "Alert ID", "value": alert.id, "short": True}
                ],
                "footer": "ACGS-1 Constitutional Governance System",
                "ts": int(alert.timestamp.timestamp())
            }]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()

    async def _send_pagerduty_notification(self, alert: Alert):
        """Send PagerDuty notification"""
        integration_key = self.notification_channels.get("pagerduty", {}).get("integration_key")
        if not integration_key:
            logger.warning("PagerDuty integration key not configured")
            return

        payload = {
            "routing_key": integration_key,
            "event_action": "trigger",
            "dedup_key": alert.id,
            "payload": {
                "summary": f"ACGS-1 Alert: {alert.name}",
                "source": alert.source,
                "severity": alert.severity.value,
                "component": alert.labels.get("component", "unknown"),
                "group": alert.labels.get("service", "acgs"),
                "class": "constitutional_governance",
                "custom_details": {
                    "message": alert.message,
                    "labels": alert.labels,
                    "annotations": alert.annotations
                }
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=payload,
                timeout=10
            )
            response.raise_for_status()

    async def _send_webhook_notification(self, alert: Alert):
        """Send generic webhook notification"""
        webhook_url = self.config["webhook_endpoints"].get("custom")
        if not webhook_url:
            return

        payload = {
            "alert_id": alert.id,
            "name": alert.name,
            "severity": alert.severity.value,
            "status": alert.status.value,
            "message": alert.message,
            "source": alert.source,
            "timestamp": alert.timestamp.isoformat(),
            "labels": alert.labels,
            "annotations": alert.annotations
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()

    async def _attempt_automated_remediation(self, alert: Alert):
        """Attempt automated remediation for the alert"""
        remediation_action = self._get_remediation_action(alert)
        if not remediation_action:
            logger.info(f"No automated remediation available for alert {alert.id}")
            return

        # Check if remediation requires approval for high-impact actions
        if remediation_action.requires_approval:
            logger.warning(f"Remediation {remediation_action.name} requires manual approval")
            await self._request_remediation_approval(alert, remediation_action)
            return

        # Execute remediation
        alert.remediation_attempted = True
        remediation_task = asyncio.create_task(
            self._execute_remediation(alert, remediation_action)
        )
        self.running_remediations[alert.id] = remediation_task

        try:
            result = await remediation_task
            alert.remediation_success = result.status == RemediationStatus.SUCCESS
            self.remediation_history.append(result)

            # Update metrics
            self.remediation_counter.labels(
                action=remediation_action.name,
                success=str(alert.remediation_success).lower()
            ).inc()

            if alert.remediation_success:
                logger.info(f"Automated remediation successful for alert {alert.id}")
                await self._resolve_alert(alert.id, "Automated remediation successful")
            else:
                logger.error(f"Automated remediation failed for alert {alert.id}")
                await self._escalate_alert(alert)

        except Exception as e:
            logger.error(f"Error during automated remediation for alert {alert.id}: {e}")
            alert.remediation_success = False
        finally:
            if alert.id in self.running_remediations:
                del self.running_remediations[alert.id]

    def _get_remediation_action(self, alert: Alert) -> Optional[RemediationAction]:
        """Get appropriate remediation action for alert"""
        # Map alert types to remediation actions
        action_mapping = {
            "ServiceDown": "service_restart",
            "ACGSServiceDown": "service_restart",
            "HighResponseTime": "health_check",
            "DatabaseConnectionIssues": "restart_database",
            "HighMemoryUsage": "clear_cache",
            "HighCPUUsage": "scale_service",
            "GovernanceWorkflowFailure": "service_restart"
        }

        action_name = action_mapping.get(alert.name)
        if action_name:
            return self.remediation_actions.get(action_name)

        # Default action based on severity
        if alert.severity == AlertSeverity.CRITICAL:
            return self.remediation_actions.get("service_restart")
        elif alert.severity == AlertSeverity.HIGH:
            return self.remediation_actions.get("health_check")

        return None

    async def _execute_remediation(self, alert: Alert, action: RemediationAction) -> RemediationResult:
        """Execute remediation action"""
        start_time = datetime.now()
        result = RemediationResult(
            action_name=action.name,
            status=RemediationStatus.RUNNING,
            start_time=start_time,
            end_time=None,
            output="",
            error=None,
            exit_code=None
        )

        try:
            # Format command with alert context
            command = action.command.format(
                service=alert.labels.get("service", "unknown"),
                alert_id=alert.id,
                severity=alert.severity.value
            )

            logger.info(f"Executing remediation: {command}")

            # Execute command with timeout
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/home/dislove/ACGS-1"
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=action.timeout
                )

                result.output = stdout.decode() if stdout else ""
                result.error = stderr.decode() if stderr else None
                result.exit_code = process.returncode
                result.end_time = datetime.now()

                if process.returncode == 0:
                    result.status = RemediationStatus.SUCCESS
                    logger.info(f"Remediation {action.name} completed successfully")
                else:
                    result.status = RemediationStatus.FAILED
                    logger.error(f"Remediation {action.name} failed with exit code {process.returncode}")

            except asyncio.TimeoutError:
                result.status = RemediationStatus.TIMEOUT
                result.error = f"Command timed out after {action.timeout} seconds"
                result.end_time = datetime.now()
                process.kill()
                logger.error(f"Remediation {action.name} timed out")

        except Exception as e:
            result.status = RemediationStatus.FAILED
            result.error = str(e)
            result.end_time = datetime.now()
            logger.error(f"Error executing remediation {action.name}: {e}")

        return result

    async def _request_remediation_approval(self, alert: Alert, action: RemediationAction):
        """Request manual approval for high-impact remediation"""
        approval_message = {
            "type": "remediation_approval_request",
            "alert_id": alert.id,
            "alert_name": alert.name,
            "severity": alert.severity.value,
            "action": action.name,
            "impact_level": action.impact_level,
            "command": action.command,
            "message": f"High-impact remediation requested for alert {alert.name}. Manual approval required."
        }

        # Send approval request through notification channels
        await self._send_slack_notification_with_payload(approval_message)
        logger.info(f"Remediation approval requested for alert {alert.id}")

    async def _send_slack_notification_with_payload(self, payload: Dict[str, Any]):
        """Send custom Slack notification"""
        webhook_url = self.config["webhook_endpoints"].get("slack")
        if not webhook_url:
            return

        slack_payload = {
            "text": f"🔧 Remediation Approval Required",
            "attachments": [{
                "color": "warning",
                "title": "High-Impact Remediation Request",
                "fields": [
                    {"title": "Alert", "value": payload["alert_name"], "short": True},
                    {"title": "Severity", "value": payload["severity"].upper(), "short": True},
                    {"title": "Action", "value": payload["action"], "short": True},
                    {"title": "Impact", "value": payload["impact_level"].upper(), "short": True}
                ],
                "text": payload["message"],
                "footer": "React with ✅ to approve or ❌ to deny"
            }]
        }

        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json=slack_payload, timeout=10)

    async def _resolve_alert(self, alert_id: str, resolution_reason: str = ""):
        """Resolve an alert"""
        if alert_id not in self.active_alerts:
            logger.warning(f"Alert {alert_id} not found in active alerts")
            return

        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolution_time = datetime.now()

        # Calculate alert duration
        duration = (alert.resolution_time - alert.timestamp).total_seconds()
        self.alert_duration.labels(
            severity=alert.severity.value,
            alert_name=alert.name
        ).observe(duration)

        # Remove from active alerts
        del self.active_alerts[alert_id]

        logger.info(f"Alert {alert_id} resolved: {resolution_reason}")

        # Send resolution notification
        await self._send_resolution_notification(alert, resolution_reason)

    async def _escalate_alert(self, alert: Alert):
        """Escalate alert to next level"""
        alert.escalation_level += 1
        max_escalation = self.config.get("max_escalation_level", 3)

        if alert.escalation_level > max_escalation:
            logger.error(f"Alert {alert.id} reached maximum escalation level")
            return

        logger.warning(f"Escalating alert {alert.id} to level {alert.escalation_level}")

        # Send escalation notification
        escalation_message = f"Alert escalated to level {alert.escalation_level}: {alert.message}"
        await self._send_escalation_notification(alert, escalation_message)

    async def _schedule_escalation(self, alert: Alert):
        """Schedule automatic escalation if alert is not resolved"""
        severity_policy = self.escalation_policies.get(alert.severity.value, {})

        for time_key, channels in severity_policy.items():
            if time_key == "immediate":
                continue

            # Parse time (e.g., "5_minutes", "1_hour")
            if "_minutes" in time_key:
                delay = int(time_key.split("_")[0]) * 60
            elif "_hour" in time_key:
                delay = int(time_key.split("_")[0]) * 3600
            else:
                continue

            # Schedule escalation
            asyncio.create_task(self._delayed_escalation(alert, delay, channels))

    async def _delayed_escalation(self, alert: Alert, delay: int, channels: List[str]):
        """Execute delayed escalation"""
        await asyncio.sleep(delay)

        # Check if alert is still active
        if alert.id in self.active_alerts and alert.status == AlertStatus.ACTIVE:
            alert.escalation_level += 1
            logger.warning(f"Auto-escalating alert {alert.id} after {delay} seconds")

            for channel in channels:
                try:
                    await self._send_notification_to_channel(alert, channel)
                except Exception as e:
                    logger.error(f"Failed to send escalation notification to {channel}: {e}")

    async def _send_resolution_notification(self, alert: Alert, reason: str):
        """Send alert resolution notification"""
        if not self.config["webhook_endpoints"].get("slack"):
            return

        duration = ""
        if alert.resolution_time:
            duration_seconds = (alert.resolution_time - alert.timestamp).total_seconds()
            duration = f" (Duration: {duration_seconds:.1f}s)"

        payload = {
            "attachments": [{
                "color": "good",
                "title": f"✅ ACGS-1 Alert Resolved: {alert.name}",
                "text": f"Alert has been resolved: {reason}",
                "fields": [
                    {"title": "Alert ID", "value": alert.id, "short": True},
                    {"title": "Duration", "value": duration, "short": True},
                    {"title": "Remediation", "value": "Success" if alert.remediation_success else "Manual", "short": True}
                ],
                "footer": "ACGS-1 Constitutional Governance System"
            }]
        }

        webhook_url = self.config["webhook_endpoints"]["slack"]
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json=payload, timeout=10)

    async def _send_escalation_notification(self, alert: Alert, message: str):
        """Send alert escalation notification"""
        if not self.config["webhook_endpoints"].get("slack"):
            return

        payload = {
            "attachments": [{
                "color": "danger",
                "title": f"🚨 ESCALATED: {alert.name}",
                "text": message,
                "fields": [
                    {"title": "Escalation Level", "value": str(alert.escalation_level), "short": True},
                    {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                    {"title": "Duration", "value": f"{(datetime.now() - alert.timestamp).total_seconds():.1f}s", "short": True}
                ],
                "footer": "ACGS-1 Constitutional Governance System - ESCALATED ALERT"
            }]
        }

        webhook_url = self.config["webhook_endpoints"]["slack"]
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json=payload, timeout=10)

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system") -> bool:
        """Acknowledge an alert"""
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledgment_time = datetime.now()

        logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
        return True

    async def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())

    async def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.timestamp >= cutoff_time]

    async def get_remediation_history(self, hours: int = 24) -> List[RemediationResult]:
        """Get remediation history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [result for result in self.remediation_history if result.start_time >= cutoff_time]

    async def push_metrics(self):
        """Push metrics to Prometheus pushgateway"""
        try:
            pushgateway_url = self.config.get("prometheus_pushgateway")
            if pushgateway_url:
                push_to_gateway(
                    pushgateway_url,
                    job='acgs_intelligent_alerting',
                    registry=self.registry
                )
        except Exception as e:
            logger.error(f"Failed to push metrics: {e}")

    async def cleanup_old_alerts(self):
        """Clean up old alerts and history"""
        retention_days = self.config.get("alert_retention_days", 30)
        cutoff_time = datetime.now() - timedelta(days=retention_days)

        # Clean up alert history
        self.alert_history = [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]

        # Clean up remediation history
        self.remediation_history = [
            result for result in self.remediation_history
            if result.start_time >= cutoff_time
        ]

        logger.info(f"Cleaned up alerts older than {retention_days} days")


async def main():
    """Main function for testing and CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description="ACGS-1 Intelligent Alerting System")
    parser.add_argument("action", choices=["test", "monitor", "status", "cleanup"],
                       help="Action to perform")
    parser.add_argument("--config", default="config/intelligent_alerting.json",
                       help="Configuration file path")
    parser.add_argument("--alert-name", help="Alert name for testing")
    parser.add_argument("--severity", choices=["critical", "high", "medium", "low", "info"],
                       default="medium", help="Alert severity for testing")
    parser.add_argument("--message", help="Alert message for testing")
    parser.add_argument("--source", default="test", help="Alert source for testing")

    args = parser.parse_args()

    # Initialize alert manager
    alert_manager = IntelligentAlertManager(args.config)

    try:
        if args.action == "test":
            # Create test alert
            if not args.alert_name or not args.message:
                print("Error: --alert-name and --message required for test action")
                return

            severity = AlertSeverity(args.severity)
            alert = await alert_manager.create_alert(
                name=args.alert_name,
                severity=severity,
                message=args.message,
                source=args.source,
                labels={"component": "test", "service": "test_service"}
            )

            print(f"Test alert created: {alert.id}")

            # Wait a bit to see remediation results
            await asyncio.sleep(5)

            # Show alert status
            if alert.id in alert_manager.active_alerts:
                print(f"Alert status: {alert_manager.active_alerts[alert.id].status.value}")
                print(f"Remediation attempted: {alert_manager.active_alerts[alert.id].remediation_attempted}")
                print(f"Remediation success: {alert_manager.active_alerts[alert.id].remediation_success}")

        elif args.action == "monitor":
            print("Starting intelligent alerting monitor...")
            print("Press Ctrl+C to stop")

            # Start monitoring loop
            while True:
                await alert_manager.push_metrics()
                await asyncio.sleep(30)

        elif args.action == "status":
            # Show system status
            active_alerts = await alert_manager.get_active_alerts()
            recent_history = await alert_manager.get_alert_history(hours=24)
            recent_remediations = await alert_manager.get_remediation_history(hours=24)

            print(f"Active alerts: {len(active_alerts)}")
            print(f"Alerts in last 24h: {len(recent_history)}")
            print(f"Remediations in last 24h: {len(recent_remediations)}")

            if active_alerts:
                print("\nActive Alerts:")
                for alert in active_alerts:
                    print(f"  {alert.id}: {alert.name} ({alert.severity.value}) - {alert.message}")

            if recent_remediations:
                print("\nRecent Remediations:")
                for remediation in recent_remediations[-5:]:  # Show last 5
                    print(f"  {remediation.action_name}: {remediation.status.value}")

        elif args.action == "cleanup":
            await alert_manager.cleanup_old_alerts()
            print("Cleanup completed")

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
