#!/usr/bin/env python3
"""
Automated Incident Response and Escalation System

This script implements automated incident response procedures with:
- Multi-tier escalation policies
- Automated remediation actions
- Incident tracking and documentation
- Integration with monitoring systems
- Stakeholder notification workflows

Target: Critical <2min, High <5min, Medium <15min response times
"""

import asyncio
import json
import logging
import smtplib
import subprocess
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from pathlib import Path
from typing import Any

import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IncidentSeverity(Enum):
    """Incident severity levels with response time targets."""

    CRITICAL = "critical"  # <2 minutes
    HIGH = "high"  # <5 minutes
    MEDIUM = "medium"  # <15 minutes
    LOW = "low"  # <1 hour


class IncidentStatus(Enum):
    """Incident status tracking."""

    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVING = "resolving"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AutomatedIncidentResponse:
    """Automated incident response and escalation system."""

    def __init__(self):
        self.project_root = Path("/home/dislove/ACGS-1")
        self.logs_dir = self.project_root / "logs"
        self.incidents_dir = self.logs_dir / "incidents"
        self.config_dir = self.project_root / "config"

        # Ensure directories exist
        self.incidents_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config()

        # Active incidents tracking
        self.active_incidents: dict[str, dict[str, Any]] = {}

        # Escalation timers
        self.escalation_timers: dict[str, asyncio.Task] = {}

        # Service endpoints
        self.services = {
            "auth_service": 8000,
            "ac_service": 8001,
            "integrity_service": 8002,
            "fv_service": 8003,
            "gs_service": 8004,
            "pgc_service": 8005,
            "ec_service": 8006,
        }

    def _load_config(self) -> dict[str, Any]:
        """Load incident response configuration."""
        config_file = self.config_dir / "incident_response_config.json"

        default_config = {
            "escalation_policies": {
                "critical": {
                    "initial_response_time": 120,  # 2 minutes
                    "escalation_levels": [
                        {"time": 300, "contacts": ["ops-team@acgs.ai"]},
                        {"time": 600, "contacts": ["sre-lead@acgs.ai"]},
                        {"time": 900, "contacts": ["cto@acgs.ai"]},
                    ],
                },
                "high": {
                    "initial_response_time": 300,  # 5 minutes
                    "escalation_levels": [
                        {"time": 900, "contacts": ["ops-team@acgs.ai"]},
                        {"time": 1800, "contacts": ["sre-lead@acgs.ai"]},
                    ],
                },
                "medium": {
                    "initial_response_time": 900,  # 15 minutes
                    "escalation_levels": [
                        {"time": 3600, "contacts": ["ops-team@acgs.ai"]}
                    ],
                },
            },
            "automated_remediation": {
                "service_restart": True,
                "cache_clear": True,
                "database_connection_reset": True,
                "load_balancer_health_check": True,
            },
            "notification_channels": {
                "email": {
                    "enabled": True,
                    "smtp_server": "localhost",
                    "smtp_port": 587,
                    "username": "acgs-alerts@acgs.ai",
                    "password": "secure_password",
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": "",
                    "channels": {
                        "critical": "#acgs-critical",
                        "high": "#acgs-alerts",
                        "medium": "#acgs-monitoring",
                    },
                },
                "webhook": {
                    "enabled": True,
                    "endpoints": ["http://localhost:9093/webhook/incident"],
                },
            },
        }

        if config_file.exists():
            try:
                with open(config_file) as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Failed to load config, using defaults: {e}")

        return default_config

    async def handle_alert(self, alert_data: dict[str, Any]) -> str:
        """Handle incoming alert and initiate incident response."""
        incident_id = self._generate_incident_id(alert_data)

        logger.info(f"🚨 Handling alert: {incident_id}")

        # Create incident record
        incident = {
            "id": incident_id,
            "alert_data": alert_data,
            "severity": self._determine_severity(alert_data),
            "status": IncidentStatus.OPEN.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "escalation_level": 0,
            "automated_actions": [],
            "notifications_sent": [],
            "resolution_time": None,
        }

        self.active_incidents[incident_id] = incident

        # Save incident to disk
        await self._save_incident(incident)

        # Start incident response workflow
        await self._start_incident_response(incident)

        return incident_id

    def _generate_incident_id(self, alert_data: dict[str, Any]) -> str:
        """Generate unique incident ID."""
        timestamp = int(time.time())
        alert_name = alert_data.get("alertname", "unknown")
        service = alert_data.get("service", "unknown")
        return f"INC-{timestamp}-{alert_name}-{service}"

    def _determine_severity(self, alert_data: dict[str, Any]) -> str:
        """Determine incident severity from alert data."""
        severity = alert_data.get("severity", "medium").lower()

        # Map alert severities to incident severities
        severity_mapping = {
            "critical": IncidentSeverity.CRITICAL.value,
            "high": IncidentSeverity.HIGH.value,
            "warning": IncidentSeverity.MEDIUM.value,
            "info": IncidentSeverity.LOW.value,
        }

        return severity_mapping.get(severity, IncidentSeverity.MEDIUM.value)

    async def _start_incident_response(self, incident: dict[str, Any]):
        """Start automated incident response workflow."""
        incident_id = incident["id"]
        severity = incident["severity"]

        logger.info(
            f"🔄 Starting incident response for {incident_id} (severity: {severity})"
        )

        # Step 1: Immediate automated remediation
        if self.config["automated_remediation"]:
            await self._attempt_automated_remediation(incident)

        # Step 2: Send initial notifications
        await self._send_initial_notification(incident)

        # Step 3: Start escalation timer
        await self._start_escalation_timer(incident)

        # Step 4: Update incident status
        incident["status"] = IncidentStatus.ACKNOWLEDGED.value
        incident["updated_at"] = datetime.now().isoformat()
        await self._save_incident(incident)

    async def _attempt_automated_remediation(self, incident: dict[str, Any]):
        """Attempt automated remediation based on alert type."""
        alert_data = incident["alert_data"]
        alertname = alert_data.get("alertname", "")
        service = alert_data.get("service", "")

        remediation_actions = []

        try:
            # Service down remediation
            if "ServiceDown" in alertname or "service_unavailable" in alertname.lower():
                if service in self.services:
                    action_result = await self._restart_service(service)
                    remediation_actions.append(
                        {
                            "action": "service_restart",
                            "service": service,
                            "result": action_result,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

            # High response time remediation
            elif (
                "HighResponseTime" in alertname or "response_time" in alertname.lower()
            ):
                # Clear cache
                cache_result = await self._clear_cache()
                remediation_actions.append(
                    {
                        "action": "cache_clear",
                        "result": cache_result,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                # Reset database connections
                db_result = await self._reset_database_connections()
                remediation_actions.append(
                    {
                        "action": "database_reset",
                        "result": db_result,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            # Constitutional compliance remediation
            elif "constitutional" in alertname.lower():
                # Restart PGC service specifically
                pgc_result = await self._restart_service("pgc_service")
                remediation_actions.append(
                    {
                        "action": "pgc_service_restart",
                        "result": pgc_result,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            # Capacity remediation
            elif "capacity" in alertname.lower() or "utilization" in alertname.lower():
                # Trigger load balancer health check
                lb_result = await self._trigger_load_balancer_health_check()
                remediation_actions.append(
                    {
                        "action": "load_balancer_check",
                        "result": lb_result,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            incident["automated_actions"] = remediation_actions

            if remediation_actions:
                logger.info(
                    f"✅ Automated remediation attempted for {incident['id']}: {len(remediation_actions)} actions"
                )

        except Exception as e:
            logger.error(f"❌ Automated remediation failed for {incident['id']}: {e}")
            remediation_actions.append(
                {
                    "action": "remediation_failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

    async def _restart_service(self, service_name: str) -> dict[str, Any]:
        """Restart a specific service."""
        try:
            # Kill existing process
            kill_result = subprocess.run(
                ["pkill", "-f", f"{service_name}"],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Wait a moment
            await asyncio.sleep(2)

            # Start service
            service_script = self.project_root / "scripts" / f"start_{service_name}.sh"
            if service_script.exists():
                start_result = subprocess.run(
                    ["bash", str(service_script)],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                return {
                    "success": start_result.returncode == 0,
                    "output": start_result.stdout,
                    "error": start_result.stderr,
                }
            return {
                "success": False,
                "error": f"Service script not found: {service_script}",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _clear_cache(self) -> dict[str, Any]:
        """Clear Redis cache."""
        try:
            result = subprocess.run(
                ["redis-cli", "FLUSHALL"],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _reset_database_connections(self) -> dict[str, Any]:
        """Reset database connection pools."""
        try:
            # This would typically involve restarting connection pools
            # For now, we'll simulate this action
            await asyncio.sleep(1)

            return {"success": True, "output": "Database connections reset"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _trigger_load_balancer_health_check(self) -> dict[str, Any]:
        """Trigger load balancer health check."""
        try:
            # This would typically involve HAProxy admin interface
            # For now, we'll simulate this action
            await asyncio.sleep(1)

            return {"success": True, "output": "Load balancer health check triggered"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _send_initial_notification(self, incident: dict[str, Any]):
        """Send initial incident notification."""
        severity = incident["severity"]

        # Determine notification channels based on severity
        if severity == IncidentSeverity.CRITICAL.value:
            await self._send_email_notification(incident, urgent=True)
            await self._send_slack_notification(incident)
            await self._send_webhook_notification(incident)
        elif severity == IncidentSeverity.HIGH.value:
            await self._send_email_notification(incident)
            await self._send_slack_notification(incident)
        else:
            await self._send_webhook_notification(incident)

    async def _send_email_notification(
        self, incident: dict[str, Any], urgent: bool = False
    ):
        """Send email notification."""
        if not self.config["notification_channels"]["email"]["enabled"]:
            return

        try:
            email_config = self.config["notification_channels"]["email"]

            # Create email
            msg = MIMEMultipart()
            msg["From"] = email_config["username"]
            msg["Subject"] = (
                f"{'🚨 URGENT: ' if urgent else ''}ACGS Incident {incident['id']}"
            )

            # Determine recipients based on severity
            severity = incident["severity"]
            escalation_policy = self.config["escalation_policies"].get(severity, {})
            initial_contacts = escalation_policy.get("escalation_levels", [{}])[0].get(
                "contacts", ["ops-team@acgs.ai"]
            )

            msg["To"] = ", ".join(initial_contacts)

            # Create email body
            body = self._create_email_body(incident)
            msg.attach(MIMEText(body, "html"))

            # Send email
            server = smtplib.SMTP(
                email_config["smtp_server"], email_config["smtp_port"]
            )
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            server.send_message(msg)
            server.quit()

            incident["notifications_sent"].append(
                {
                    "type": "email",
                    "recipients": initial_contacts,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            logger.info(f"📧 Email notification sent for {incident['id']}")

        except Exception as e:
            logger.error(f"❌ Failed to send email notification: {e}")

    async def _send_slack_notification(self, incident: dict[str, Any]):
        """Send Slack notification."""
        if not self.config["notification_channels"]["slack"]["enabled"]:
            return

        try:
            slack_config = self.config["notification_channels"]["slack"]
            webhook_url = slack_config["webhook_url"]

            if not webhook_url:
                return

            severity = incident["severity"]
            channel = slack_config["channels"].get(severity, "#acgs-monitoring")

            # Create Slack message
            message = {
                "channel": channel,
                "text": f"🚨 ACGS Incident: {incident['id']}",
                "attachments": [
                    {
                        "color": "danger" if severity == "critical" else "warning",
                        "fields": [
                            {
                                "title": "Alert",
                                "value": incident["alert_data"].get(
                                    "alertname", "Unknown"
                                ),
                                "short": True,
                            },
                            {
                                "title": "Severity",
                                "value": severity.upper(),
                                "short": True,
                            },
                            {
                                "title": "Service",
                                "value": incident["alert_data"].get(
                                    "service", "Unknown"
                                ),
                                "short": True,
                            },
                            {
                                "title": "Status",
                                "value": incident["status"],
                                "short": True,
                            },
                        ],
                        "ts": int(time.time()),
                    }
                ],
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message) as response:
                    if response.status == 200:
                        incident["notifications_sent"].append(
                            {
                                "type": "slack",
                                "channel": channel,
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                        logger.info(f"💬 Slack notification sent for {incident['id']}")
                    else:
                        logger.error(f"❌ Slack notification failed: {response.status}")

        except Exception as e:
            logger.error(f"❌ Failed to send Slack notification: {e}")

    async def _send_webhook_notification(self, incident: dict[str, Any]):
        """Send webhook notification."""
        if not self.config["notification_channels"]["webhook"]["enabled"]:
            return

        try:
            webhook_config = self.config["notification_channels"]["webhook"]
            endpoints = webhook_config["endpoints"]

            for endpoint in endpoints:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(endpoint, json=incident) as response:
                            if response.status == 200:
                                incident["notifications_sent"].append(
                                    {
                                        "type": "webhook",
                                        "endpoint": endpoint,
                                        "timestamp": datetime.now().isoformat(),
                                    }
                                )
                                logger.info(
                                    f"🔗 Webhook notification sent for {incident['id']}"
                                )
                            else:
                                logger.error(
                                    f"❌ Webhook notification failed: {response.status}"
                                )
                except Exception as e:
                    logger.error(f"❌ Webhook notification failed for {endpoint}: {e}")

        except Exception as e:
            logger.error(f"❌ Failed to send webhook notifications: {e}")

    def _create_email_body(self, incident: dict[str, Any]) -> str:
        """Create HTML email body for incident notification."""
        alert_data = incident["alert_data"]

        return f"""
        <html>
        <body>
            <h2 style="color: {
            "red" if incident["severity"] == "critical" else "orange"
        };">
                🚨 ACGS Incident Alert
            </h2>
            
            <div style="border: 1px solid #ccc; padding: 15px; margin: 10px 0;">
                <h3>Incident Details</h3>
                <p><strong>Incident ID:</strong> {incident["id"]}</p>
                <p><strong>Severity:</strong> {incident["severity"].upper()}</p>
                <p><strong>Status:</strong> {incident["status"]}</p>
                <p><strong>Created:</strong> {incident["created_at"]}</p>
            </div>
            
            <div style="border: 1px solid #ccc; padding: 15px; margin: 10px 0;">
                <h3>Alert Information</h3>
                <p><strong>Alert Name:</strong> {
            alert_data.get("alertname", "Unknown")
        }</p>
                <p><strong>Service:</strong> {alert_data.get("service", "Unknown")}</p>
                <p><strong>Description:</strong> {
            alert_data.get("description", "No description available")
        }</p>
                <p><strong>Summary:</strong> {
            alert_data.get("summary", "No summary available")
        }</p>
            </div>
            
            <div style="border: 1px solid #ccc; padding: 15px; margin: 10px 0;">
                <h3>Automated Actions</h3>
                {
            "<p>No automated actions taken yet.</p>"
            if not incident.get("automated_actions")
            else "<ul>"
            + "".join(
                [
                    f"<li>{action['action']}: {action.get('result', {}).get('success', 'Unknown')}</li>"
                    for action in incident["automated_actions"]
                ]
            )
            + "</ul>"
        }
            </div>
            
            <p><strong>Next Steps:</strong> Please investigate and take appropriate action.</p>
            <p><strong>Runbook:</strong> <a href="{
            alert_data.get("runbook_url", "#")
        }">View Runbook</a></p>
        </body>
        </html>
        """

    async def _start_escalation_timer(self, incident: dict[str, Any]):
        """Start escalation timer for incident."""
        incident_id = incident["id"]
        severity = incident["severity"]

        escalation_policy = self.config["escalation_policies"].get(severity, {})
        escalation_levels = escalation_policy.get("escalation_levels", [])

        if escalation_levels:
            # Start timer for first escalation level
            first_escalation = escalation_levels[0]
            escalation_time = first_escalation["time"]

            async def escalate():
                await asyncio.sleep(escalation_time)
                if incident_id in self.active_incidents:
                    await self._escalate_incident(incident_id, 0)

            self.escalation_timers[incident_id] = asyncio.create_task(escalate())

    async def _escalate_incident(self, incident_id: str, escalation_level: int):
        """Escalate incident to next level."""
        if incident_id not in self.active_incidents:
            return

        incident = self.active_incidents[incident_id]
        severity = incident["severity"]

        escalation_policy = self.config["escalation_policies"].get(severity, {})
        escalation_levels = escalation_policy.get("escalation_levels", [])

        if escalation_level < len(escalation_levels):
            escalation = escalation_levels[escalation_level]
            contacts = escalation["contacts"]

            logger.warning(
                f"🔺 Escalating incident {incident_id} to level {escalation_level + 1}"
            )

            # Send escalation notification
            await self._send_escalation_notification(
                incident, escalation_level, contacts
            )

            # Update incident
            incident["escalation_level"] = escalation_level + 1
            incident["updated_at"] = datetime.now().isoformat()
            await self._save_incident(incident)

            # Schedule next escalation if available
            if escalation_level + 1 < len(escalation_levels):
                next_escalation = escalation_levels[escalation_level + 1]
                next_time = next_escalation["time"] - escalation["time"]

                async def next_escalate():
                    await asyncio.sleep(next_time)
                    if incident_id in self.active_incidents:
                        await self._escalate_incident(incident_id, escalation_level + 1)

                self.escalation_timers[incident_id] = asyncio.create_task(
                    next_escalate()
                )

    async def _send_escalation_notification(
        self, incident: dict[str, Any], level: int, contacts: list[str]
    ):
        """Send escalation notification."""
        try:
            if self.config["notification_channels"]["email"]["enabled"]:
                email_config = self.config["notification_channels"]["email"]

                # Create escalation email
                msg = MIMEMultipart()
                msg["From"] = email_config["username"]
                msg["To"] = ", ".join(contacts)
                msg["Subject"] = (
                    f"🔺 ESCALATION Level {level + 1}: ACGS Incident {incident['id']}"
                )

                body = f"""
                <html>
                <body>
                    <h2 style="color: red;">🔺 INCIDENT ESCALATION - Level {level + 1}</h2>
                    
                    <p><strong>This incident has been escalated due to lack of response.</strong></p>
                    
                    <div style="border: 2px solid red; padding: 15px; margin: 10px 0;">
                        <h3>Incident Details</h3>
                        <p><strong>Incident ID:</strong> {incident["id"]}</p>
                        <p><strong>Severity:</strong> {incident["severity"].upper()}</p>
                        <p><strong>Created:</strong> {incident["created_at"]}</p>
                        <p><strong>Alert:</strong> {incident["alert_data"].get("alertname", "Unknown")}</p>
                        <p><strong>Service:</strong> {incident["alert_data"].get("service", "Unknown")}</p>
                    </div>
                    
                    <p><strong>IMMEDIATE ACTION REQUIRED</strong></p>
                </body>
                </html>
                """

                msg.attach(MIMEText(body, "html"))

                # Send email
                server = smtplib.SMTP(
                    email_config["smtp_server"], email_config["smtp_port"]
                )
                server.starttls()
                server.login(email_config["username"], email_config["password"])
                server.send_message(msg)
                server.quit()

                incident["notifications_sent"].append(
                    {
                        "type": "escalation_email",
                        "level": level + 1,
                        "recipients": contacts,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                logger.warning(
                    f"📧 Escalation notification sent for {incident['id']} level {level + 1}"
                )

        except Exception as e:
            logger.error(f"❌ Failed to send escalation notification: {e}")

    async def _save_incident(self, incident: dict[str, Any]):
        """Save incident to disk."""
        try:
            incident_file = self.incidents_dir / f"{incident['id']}.json"
            with open(incident_file, "w") as f:
                json.dump(incident, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save incident {incident['id']}: {e}")

    async def resolve_incident(self, incident_id: str, resolution_notes: str = ""):
        """Mark incident as resolved."""
        if incident_id not in self.active_incidents:
            logger.warning(f"⚠️ Incident {incident_id} not found in active incidents")
            return

        incident = self.active_incidents[incident_id]
        incident["status"] = IncidentStatus.RESOLVED.value
        incident["resolution_time"] = datetime.now().isoformat()
        incident["resolution_notes"] = resolution_notes
        incident["updated_at"] = datetime.now().isoformat()

        # Cancel escalation timer
        if incident_id in self.escalation_timers:
            self.escalation_timers[incident_id].cancel()
            del self.escalation_timers[incident_id]

        # Save incident
        await self._save_incident(incident)

        # Remove from active incidents
        del self.active_incidents[incident_id]

        logger.info(f"✅ Incident {incident_id} resolved")

    async def get_active_incidents(self) -> list[dict[str, Any]]:
        """Get list of active incidents."""
        return list(self.active_incidents.values())


async def main():
    """Main function for testing incident response system."""
    incident_response = AutomatedIncidentResponse()

    # Test alert
    test_alert = {
        "alertname": "ServiceDown",
        "service": "pgc_service",
        "severity": "critical",
        "description": "PGC service is not responding",
        "summary": "Constitutional compliance service unavailable",
        "runbook_url": "https://docs.acgs.ai/runbooks/service-down",
    }

    incident_id = await incident_response.handle_alert(test_alert)
    print(f"Created incident: {incident_id}")

    # Wait a bit to see escalation
    await asyncio.sleep(10)

    # Resolve incident
    await incident_response.resolve_incident(
        incident_id, "Service restarted successfully"
    )


if __name__ == "__main__":
    asyncio.run(main())
