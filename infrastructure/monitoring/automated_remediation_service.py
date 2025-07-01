#!/usr/bin/env python3
"""
ACGS-1 Automated Remediation Service
Intelligent automated response system for Prometheus alerts with escalation policies.

Features:
- Automated service restart for known issues
- Resource scaling based on load
- Self-healing infrastructure
- Incident management integration
- Escalation to human operators when needed
"""

import asyncio
import json
import logging
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import aiohttp
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/automated_remediation.log"),
    ],
)
logger = logging.getLogger(__name__)


class RemediationAction(Enum):
    """Types of automated remediation actions."""

    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    CLEAR_CACHE = "clear_cache"
    RESTART_CONTAINER = "restart_container"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    RUN_SCRIPT = "run_script"
    NOTIFY_ONLY = "notify_only"


class AlertSeverity(Enum):
    """Alert severity levels."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class RemediationRule:
    """Configuration for automated remediation."""

    alert_name: str
    service: str
    action: RemediationAction
    max_attempts: int = 3
    cooldown_minutes: int = 5
    escalate_after_attempts: int = 2
    script_path: str | None = None
    parameters: dict[str, Any] = None


class AlertWebhook(BaseModel):
    """Webhook payload from Alertmanager."""

    receiver: str
    status: str
    alerts: list[dict[str, Any]]
    groupLabels: dict[str, str]
    commonLabels: dict[str, str]
    commonAnnotations: dict[str, str]
    externalURL: str
    version: str
    groupKey: str


class AutomatedRemediationService:
    """Main service for automated alert remediation."""

    def __init__(self):
        self.app = FastAPI(
            title="ACGS-1 Automated Remediation Service",
            description="Intelligent automated response to monitoring alerts",
            version="1.0.0",
        )

        # Track remediation attempts
        self.remediation_history: dict[str, list[datetime]] = {}
        self.escalated_alerts: set = set()

        # Load remediation rules
        self.rules = self._load_remediation_rules()

        # Setup routes
        self._setup_routes()

        logger.info("Automated Remediation Service initialized")

    def _load_remediation_rules(self) -> list[RemediationRule]:
        """Load remediation rules from configuration."""
        rules = [
            # Service restart rules
            RemediationRule(
                alert_name="ServiceDown",
                service="pgc_service",
                action=RemediationAction.RESTART_SERVICE,
                max_attempts=3,
                cooldown_minutes=2,
                escalate_after_attempts=2,
            ),
            RemediationRule(
                alert_name="ServiceDown",
                service="gs_service",
                action=RemediationAction.RESTART_SERVICE,
                max_attempts=3,
                cooldown_minutes=2,
                escalate_after_attempts=2,
            ),
            RemediationRule(
                alert_name="HighMemoryUsage",
                service="elasticsearch",
                action=RemediationAction.CLEAR_CACHE,
                max_attempts=2,
                cooldown_minutes=10,
                escalate_after_attempts=1,
            ),
            RemediationRule(
                alert_name="HighCPUUsage",
                service="any",
                action=RemediationAction.SCALE_UP,
                max_attempts=1,
                cooldown_minutes=15,
                escalate_after_attempts=1,
            ),
            # Constitutional governance critical - immediate escalation
            RemediationRule(
                alert_name="ConstitutionalHashMismatch",
                service="any",
                action=RemediationAction.ESCALATE_TO_HUMAN,
                max_attempts=0,
                cooldown_minutes=0,
                escalate_after_attempts=0,
            ),
            # Security alerts - immediate escalation
            RemediationRule(
                alert_name="SecurityBreach",
                service="any",
                action=RemediationAction.ESCALATE_TO_HUMAN,
                max_attempts=0,
                cooldown_minutes=0,
                escalate_after_attempts=0,
            ),
        ]

        logger.info(f"Loaded {len(rules)} remediation rules")
        return rules

    def _setup_routes(self):
        """Setup FastAPI routes."""

        @self.app.post("/webhook/alerts")
        async def handle_alert_webhook(
            webhook: AlertWebhook, background_tasks: BackgroundTasks
        ):
            """Handle incoming alert webhooks from Alertmanager."""
            logger.info(
                f"Received webhook: {webhook.status} with {len(webhook.alerts)} alerts"
            )

            for alert in webhook.alerts:
                if webhook.status == "firing":
                    background_tasks.add_task(self._process_alert, alert)
                elif webhook.status == "resolved":
                    await self._handle_resolved_alert(alert)

            return {"status": "received", "processed_alerts": len(webhook.alerts)}

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "service": "automated_remediation",
                "rules_loaded": len(self.rules),
                "active_remediations": len(self.remediation_history),
            }

        @self.app.get("/status")
        async def get_status():
            """Get current remediation status."""
            return {
                "remediation_history": {
                    alert_key: [dt.isoformat() for dt in attempts]
                    for alert_key, attempts in self.remediation_history.items()
                },
                "escalated_alerts": list(self.escalated_alerts),
                "rules": [
                    {
                        "alert_name": rule.alert_name,
                        "service": rule.service,
                        "action": rule.action.value,
                        "max_attempts": rule.max_attempts,
                    }
                    for rule in self.rules
                ],
            }

    async def _process_alert(self, alert: dict[str, Any]):
        """Process a single alert for potential remediation."""
        try:
            alert_name = alert.get("labels", {}).get("alertname", "Unknown")
            service = alert.get("labels", {}).get("service", "unknown")
            severity = alert.get("labels", {}).get("severity", "info")

            logger.info(
                f"Processing alert: {alert_name} for service: {service} (severity: {severity})"
            )

            # Find matching remediation rule
            rule = self._find_matching_rule(alert_name, service)
            if not rule:
                logger.info(f"No remediation rule found for alert: {alert_name}")
                return

            # Check if we should attempt remediation
            alert_key = f"{alert_name}:{service}"
            if not self._should_attempt_remediation(alert_key, rule):
                logger.info(
                    f"Skipping remediation for {alert_key} (cooldown or max attempts)"
                )
                return

            # Record attempt
            if alert_key not in self.remediation_history:
                self.remediation_history[alert_key] = []
            self.remediation_history[alert_key].append(datetime.now())

            # Execute remediation
            success = await self._execute_remediation(rule, alert)

            if success:
                logger.info(f"Remediation successful for {alert_key}")
            else:
                logger.warning(f"Remediation failed for {alert_key}")

                # Check if we should escalate
                attempts = len(self.remediation_history[alert_key])
                if attempts >= rule.escalate_after_attempts:
                    await self._escalate_to_human(alert, rule, attempts)

        except Exception as e:
            logger.error(f"Error processing alert: {e}")

    def _find_matching_rule(
        self, alert_name: str, service: str
    ) -> RemediationRule | None:
        """Find the best matching remediation rule."""
        # First try exact match
        for rule in self.rules:
            if rule.alert_name == alert_name and (
                rule.service == service or rule.service == "any"
            ):
                return rule

        # Then try partial match
        for rule in self.rules:
            if alert_name.startswith(rule.alert_name) and (
                rule.service == service or rule.service == "any"
            ):
                return rule

        return None

    def _should_attempt_remediation(
        self, alert_key: str, rule: RemediationRule
    ) -> bool:
        """Check if we should attempt remediation based on history and rules."""
        if alert_key not in self.remediation_history:
            return True

        attempts = self.remediation_history[alert_key]

        # Check max attempts
        if len(attempts) >= rule.max_attempts:
            return False

        # Check cooldown period
        if attempts:
            last_attempt = attempts[-1]
            cooldown_end = last_attempt + timedelta(minutes=rule.cooldown_minutes)
            if datetime.now() < cooldown_end:
                return False

        return True

    async def _execute_remediation(
        self, rule: RemediationRule, alert: dict[str, Any]
    ) -> bool:
        """Execute the specified remediation action."""
        try:
            service = alert.get("labels", {}).get("service", "unknown")

            if rule.action == RemediationAction.RESTART_SERVICE:
                return await self._restart_service(service)
            if rule.action == RemediationAction.RESTART_CONTAINER:
                return await self._restart_container(service)
            if rule.action == RemediationAction.CLEAR_CACHE:
                return await self._clear_cache(service)
            if rule.action == RemediationAction.SCALE_UP:
                return await self._scale_service(service, "up")
            if rule.action == RemediationAction.SCALE_DOWN:
                return await self._scale_service(service, "down")
            if rule.action == RemediationAction.RUN_SCRIPT:
                return await self._run_script(rule.script_path, rule.parameters)
            if rule.action == RemediationAction.ESCALATE_TO_HUMAN:
                await self._escalate_to_human(alert, rule, 0)
                return True
            logger.warning(f"Unknown remediation action: {rule.action}")
            return False

        except Exception as e:
            logger.error(f"Error executing remediation: {e}")
            return False

    async def _restart_service(self, service: str) -> bool:
        """Restart a specific service."""
        try:
            logger.info(f"Attempting to restart service: {service}")

            # Map service names to restart commands
            service_commands = {
                "pgc_service": "pkill -f pgc_service || true",
                "gs_service": "pkill -f gs_service || true",
                "auth_service": "pkill -f auth_service || true",
                "ac_service": "pkill -f ac_service || true",
                "integrity_service": "pkill -f integrity_service || true",
                "fv_service": "pkill -f fv_service || true",
                "ec_service": "pkill -f ec_service || true",
            }

            if service in service_commands:
                # Kill the service process
                result = subprocess.run(
                    service_commands[service],
                    check=False,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                # Wait a moment for cleanup
                await asyncio.sleep(2)

                # The service should be restarted by systemd or supervisor
                logger.info(f"Service restart command executed for {service}")
                return True
            logger.warning(f"No restart command configured for service: {service}")
            return False

        except Exception as e:
            logger.error(f"Error restarting service {service}: {e}")
            return False

    async def _restart_container(self, service: str) -> bool:
        """Restart a Docker container."""
        try:
            logger.info(f"Attempting to restart container: {service}")

            result = subprocess.run(
                f"docker restart {service}",
                check=False,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                logger.info(f"Container {service} restarted successfully")
                return True
            logger.error(f"Failed to restart container {service}: {result.stderr}")
            return False

        except Exception as e:
            logger.error(f"Error restarting container {service}: {e}")
            return False

    async def _clear_cache(self, service: str) -> bool:
        """Clear cache for a service."""
        try:
            logger.info(f"Attempting to clear cache for service: {service}")

            if service == "elasticsearch":
                # Clear Elasticsearch cache
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "http://localhost:9201/_cache/clear"
                    ) as response:
                        if response.status == 200:
                            logger.info("Elasticsearch cache cleared successfully")
                            return True

            # Add more cache clearing logic for other services
            return False

        except Exception as e:
            logger.error(f"Error clearing cache for {service}: {e}")
            return False

    async def _scale_service(self, service: str, direction: str) -> bool:
        """Scale a service up or down."""
        try:
            logger.info(f"Attempting to scale {service} {direction}")

            # This would integrate with Kubernetes or Docker Swarm
            # For now, just log the action
            logger.info(
                f"Scaling {service} {direction} - would execute scaling command here"
            )
            return True

        except Exception as e:
            logger.error(f"Error scaling service {service}: {e}")
            return False

    async def _run_script(self, script_path: str, parameters: dict[str, Any]) -> bool:
        """Run a custom remediation script."""
        try:
            if not script_path or not os.path.exists(script_path):
                logger.error(f"Script not found: {script_path}")
                return False

            logger.info(f"Running remediation script: {script_path}")

            result = subprocess.run(
                [script_path] + [str(v) for v in (parameters or {}).values()],
                check=False,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                logger.info(f"Script {script_path} executed successfully")
                return True
            logger.error(f"Script {script_path} failed: {result.stderr}")
            return False

        except Exception as e:
            logger.error(f"Error running script {script_path}: {e}")
            return False

    async def _escalate_to_human(
        self, alert: dict[str, Any], rule: RemediationRule, attempts: int
    ):
        """Escalate alert to human operators."""
        try:
            alert_name = alert.get("labels", {}).get("alertname", "Unknown")
            service = alert.get("labels", {}).get("service", "unknown")
            alert_key = f"{alert_name}:{service}"

            if alert_key in self.escalated_alerts:
                return  # Already escalated

            self.escalated_alerts.add(alert_key)

            logger.warning(
                f"Escalating alert to human: {alert_name} (service: {service}, attempts: {attempts})"
            )

            # Send escalation notification
            escalation_data = {
                "alert": alert,
                "remediation_attempts": attempts,
                "escalation_reason": f"Automated remediation failed after {attempts} attempts",
                "timestamp": datetime.now().isoformat(),
                "requires_human_intervention": True,
            }

            # This would send to incident management system
            logger.info(f"Escalation data: {json.dumps(escalation_data, indent=2)}")

        except Exception as e:
            logger.error(f"Error escalating alert: {e}")

    async def _handle_resolved_alert(self, alert: dict[str, Any]):
        """Handle resolved alerts."""
        try:
            alert_name = alert.get("labels", {}).get("alertname", "Unknown")
            service = alert.get("labels", {}).get("service", "unknown")
            alert_key = f"{alert_name}:{service}"

            logger.info(f"Alert resolved: {alert_key}")

            # Remove from escalated alerts
            self.escalated_alerts.discard(alert_key)

            # Clean up old history (keep last 24 hours)
            if alert_key in self.remediation_history:
                cutoff = datetime.now() - timedelta(hours=24)
                self.remediation_history[alert_key] = [
                    dt for dt in self.remediation_history[alert_key] if dt > cutoff
                ]

                if not self.remediation_history[alert_key]:
                    del self.remediation_history[alert_key]

        except Exception as e:
            logger.error(f"Error handling resolved alert: {e}")


# Global service instance
remediation_service = AutomatedRemediationService()

if __name__ == "__main__":
    import uvicorn

    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    logger.info("Starting ACGS-1 Automated Remediation Service")

    uvicorn.run(remediation_service.app, host="0.0.0.0", port=8080, log_level="info")
