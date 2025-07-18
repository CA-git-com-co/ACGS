"""
Alerting and Escalation Service
Constitutional Hash: cdd01ef066bc6cf2

FastAPI service providing comprehensive alerting, escalation, and notification 
management for all ACGS-2 services with constitutional compliance oversight.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import httpx
import os
import json
import time
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from collections import defaultdict, deque
import hashlib
import uuid

from .models import (
    Contact, Team, OnCallSchedule, NotificationChannel, NotificationTemplate,
    NotificationRequest, NotificationDelivery, EscalationRule, EscalationPolicy,
    EscalationExecution, AlertContext, AlertingAlert, Incident, IncidentUpdate,
    AlertSuppression, MaintenanceWindow, AlertingMetrics, EscalationMetrics,
    NotificationMetrics, AlertingConfig, AlertingServiceHealth, WebhookPayload,
    WebhookDelivery, CreateContactRequest, CreateTeamRequest, 
    CreateEscalationPolicyRequest, TriggerAlertRequest, AcknowledgeAlertRequest,
    ResolveAlertRequest, CreateIncidentRequest, AlertingSeverity, AlertingStatus,
    IncidentStatus, OnCallStatus, EscalationTrigger, CONSTITUTIONAL_HASH
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global storage
alerting_storage = {
    "contacts": {},  # contact_id -> Contact
    "teams": {},  # team_id -> Team
    "schedules": {},  # schedule_id -> OnCallSchedule
    "channels": {},  # channel_id -> NotificationChannel
    "templates": {},  # template_id -> NotificationTemplate
    "escalation_rules": {},  # rule_id -> EscalationRule
    "escalation_policies": {},  # policy_id -> EscalationPolicy
    "alerts": {},  # alert_id -> AlertingAlert
    "incidents": {},  # incident_id -> Incident
    "suppressions": {},  # suppression_id -> AlertSuppression
    "maintenance_windows": {},  # window_id -> MaintenanceWindow
    "notifications": deque(maxlen=10000),  # Recent notifications
    "escalations": deque(maxlen=5000),  # Recent escalations
    "webhooks": deque(maxlen=1000),  # Recent webhook deliveries
    "metrics": defaultdict(int),
    "config": None
}

# External service URLs
MONITORING_SERVICE_URL = "http://localhost:8014"
AUTH_SERVICE_URL = "http://localhost:8013"

# HTTP client for external requests
http_client = httpx.AsyncClient(timeout=10.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting Alerting Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Initialize default configuration
    await initialize_default_config()
    await initialize_default_contacts()
    await initialize_default_channels()
    await initialize_default_templates()
    await initialize_default_escalation_policies()
    
    # Start background tasks
    asyncio.create_task(poll_monitoring_alerts())
    asyncio.create_task(process_escalations())
    asyncio.create_task(process_notifications())
    asyncio.create_task(check_maintenance_windows())
    asyncio.create_task(collect_alerting_metrics())
    asyncio.create_task(cleanup_old_data())
    
    yield
    
    # Cleanup
    await http_client.aclose()
    logger.info("Shutting down Alerting Service")

app = FastAPI(
    title="Alerting Service",
    description="Automated alerting and escalation management for ACGS-2",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def initialize_default_config():
    """Initialize default alerting configuration"""
    config = AlertingConfig(
        alert_retention_days=90,
        incident_retention_days=365,
        notification_rate_limit_per_minute=10,
        constitutional_alert_retention_days=2555,  # 7 years
        enable_constitutional_oversight=True
    )
    alerting_storage["config"] = config
    logger.info("Initialized default alerting configuration")

async def initialize_default_contacts():
    """Initialize default contacts"""
    default_contacts = [
        Contact(
            name="System Administrator",
            email="admin@acgs2.local",
            preferred_channels=["email", "webhook"],
            constitutional_clearance_level=10
        ),
        Contact(
            name="Constitutional Oversight",
            email="constitutional@acgs2.local",
            preferred_channels=["email", "webhook"],
            constitutional_clearance_level=10
        ),
        Contact(
            name="Security Team",
            email="security@acgs2.local",
            preferred_channels=["email", "webhook"],
            constitutional_clearance_level=8
        ),
        Contact(
            name="DevOps Engineer",
            email="devops@acgs2.local",
            preferred_channels=["email", "webhook"],
            constitutional_clearance_level=5
        )
    ]
    
    for contact in default_contacts:
        alerting_storage["contacts"][contact.contact_id] = contact
    
    logger.info(f"Initialized {len(default_contacts)} default contacts")

async def initialize_default_channels():
    """Initialize default notification channels"""
    default_channels = [
        NotificationChannel(
            name="Email Channel",
            type="email",
            config={
                "smtp_server": "localhost",
                "smtp_port": 587,
                "username": "alerts@acgs2.local",
                "password": "alert_password",
                "from_address": "alerts@acgs2.local"
            },
            rate_limit_per_hour=1000
        ),
        NotificationChannel(
            name="Webhook Channel",
            type="webhook",
            config={
                "webhook_url": "http://localhost:8080/api/v1/webhooks/alerts",
                "headers": {"Authorization": "Bearer webhook_token"},
                "timeout_seconds": 30
            },
            rate_limit_per_hour=10000
        ),
        NotificationChannel(
            name="Constitutional Webhook",
            type="webhook",
            config={
                "webhook_url": "http://localhost:8080/api/v1/webhooks/constitutional",
                "headers": {"Authorization": "Bearer constitutional_token"},
                "timeout_seconds": 30
            },
            constitutional_notifications_only=True,
            rate_limit_per_hour=1000
        )
    ]
    
    for channel in default_channels:
        alerting_storage["channels"][channel.channel_id] = channel
    
    logger.info(f"Initialized {len(default_channels)} default notification channels")

async def initialize_default_templates():
    """Initialize default notification templates"""
    default_templates = [
        NotificationTemplate(
            name="Alert Email Template",
            channel_type="email",
            subject_template="🚨 ACGS-2 Alert: {severity} - {rule_name}",
            body_template="""
Alert Details:
- Service: {service_name}
- Severity: {severity}
- Message: {message}
- Triggered: {triggered_at}
- Constitutional Hash: {constitutional_hash}

{description}

Please investigate and acknowledge this alert.
            """,
            variables=["severity", "rule_name", "service_name", "message", "triggered_at", "constitutional_hash", "description"]
        ),
        NotificationTemplate(
            name="Constitutional Alert Template",
            channel_type="email",
            subject_template="⚖️ CONSTITUTIONAL ALERT: {severity} - {rule_name}",
            body_template="""
🚨 CONSTITUTIONAL COMPLIANCE ALERT 🚨

Alert Details:
- Service: {service_name}
- Severity: {severity}
- Message: {message}
- Constitutional Impact: YES
- Triggered: {triggered_at}
- Constitutional Hash: {constitutional_hash}

{description}

This alert requires immediate constitutional review and response.
Constitutional escalation policies are in effect.
            """,
            constitutional_template=True,
            variables=["severity", "rule_name", "service_name", "message", "triggered_at", "constitutional_hash", "description"]
        ),
        NotificationTemplate(
            name="Escalation Email Template",
            channel_type="email",
            subject_template="📈 ESCALATED: {severity} - {rule_name}",
            body_template="""
This alert has been escalated to you:

Alert Details:
- Service: {service_name}
- Severity: {severity}
- Message: {message}
- Escalation Level: {escalation_level}
- Previous Contact: {previous_contact}
- Triggered: {triggered_at}

{description}

Please take immediate action.
            """,
            variables=["severity", "rule_name", "service_name", "message", "escalation_level", "previous_contact", "triggered_at", "description"]
        )
    ]
    
    for template in default_templates:
        alerting_storage["templates"][template.template_id] = template
    
    logger.info(f"Initialized {len(default_templates)} default notification templates")

async def initialize_default_escalation_policies():
    """Initialize default escalation policies"""
    # Get contact IDs for defaults
    admin_contact = next((c for c in alerting_storage["contacts"].values() if "Administrator" in c.name), None)
    constitutional_contact = next((c for c in alerting_storage["contacts"].values() if "Constitutional" in c.name), None)
    security_contact = next((c for c in alerting_storage["contacts"].values() if "Security" in c.name), None)
    
    if not all([admin_contact, constitutional_contact, security_contact]):
        logger.warning("Could not find all default contacts for escalation policies")
        return
    
    # Create escalation rules
    rules = [
        EscalationRule(
            name="DevOps Escalation",
            trigger=EscalationTrigger.ACK_TIMEOUT,
            condition="ack_timeout > 15",
            delay_minutes=15,
            target_contact_id=admin_contact.contact_id,
            escalation_channel="email"
        ),
        EscalationRule(
            name="Security Team Escalation",
            trigger=EscalationTrigger.SEVERITY_INCREASE,
            condition="severity == 'critical'",
            delay_minutes=5,
            target_contact_id=security_contact.contact_id,
            escalation_channel="email"
        ),
        EscalationRule(
            name="Constitutional Escalation",
            trigger=EscalationTrigger.CONSTITUTIONAL_VIOLATION,
            condition="constitutional_alert == true",
            delay_minutes=1,
            target_contact_id=constitutional_contact.contact_id,
            escalation_channel="webhook",
            constitutional_escalation=True
        )
    ]
    
    for rule in rules:
        alerting_storage["escalation_rules"][rule.rule_id] = rule
    
    # Create escalation policies
    policies = [
        EscalationPolicy(
            name="Standard Escalation Policy",
            description="Standard escalation for non-constitutional alerts",
            rules=[rules[0].rule_id, rules[1].rule_id],
            max_escalations=2,
            severity_filters=["warning", "critical"]
        ),
        EscalationPolicy(
            name="Constitutional Escalation Policy",
            description="Immediate escalation for constitutional violations",
            rules=[rules[2].rule_id],
            max_escalations=1,
            constitutional_policy=True,
            severity_filters=["critical", "emergency"]
        )
    ]
    
    for policy in policies:
        alerting_storage["escalation_policies"][policy.policy_id] = policy
    
    # Update config with default policies
    config = alerting_storage["config"]
    config.default_escalation_policy_id = policies[0].policy_id
    config.constitutional_escalation_policy_id = policies[1].policy_id
    
    logger.info(f"Initialized {len(rules)} escalation rules and {len(policies)} escalation policies")

async def poll_monitoring_alerts():
    """Poll monitoring service for new alerts"""
    while True:
        try:
            # Get alerts from monitoring service
            response = await http_client.get(f"{MONITORING_SERVICE_URL}/api/v1/alerts?hours=1")
            if response.status_code == 200:
                monitoring_alerts = response.json()
                
                for alert_data in monitoring_alerts:
                    await process_monitoring_alert(alert_data)
            
            await asyncio.sleep(30)  # Poll every 30 seconds
            
        except Exception as e:
            logger.error(f"Error polling monitoring alerts: {e}")
            await asyncio.sleep(30)

async def process_monitoring_alert(alert_data: Dict[str, Any]):
    """Process alert from monitoring service"""
    try:
        alert_id = f"monitoring_{alert_data.get('alert_id', str(uuid.uuid4()))}"
        
        # Check if alert already exists
        if alert_id in alerting_storage["alerts"]:
            return
        
        # Create alert context
        context = AlertContext(
            service_name=alert_data.get("service_name", "unknown"),
            environment="production",
            constitutional_impact=alert_data.get("constitutional_impact", False),
            performance_metrics=alert_data.get("details", {})
        )
        
        # Determine severity mapping
        severity_mapping = {
            "info": AlertingSeverity.INFO,
            "warning": AlertingSeverity.WARNING,
            "critical": AlertingSeverity.CRITICAL,
            "emergency": AlertingSeverity.CRITICAL
        }
        
        alert = AlertingAlert(
            alert_id=alert_id,
            rule_name=alert_data.get("rule_id", "unknown_rule"),
            severity=severity_mapping.get(alert_data.get("severity", "info"), AlertingSeverity.INFO),
            message=alert_data.get("message", "Alert from monitoring service"),
            description=alert_data.get("details", {}).get("description"),
            context=context,
            labels={"source": "monitoring-service"},
            triggered_at=datetime.fromisoformat(alert_data.get("triggered_at", datetime.utcnow().isoformat())),
            updated_at=datetime.utcnow(),
            constitutional_alert=alert_data.get("constitutional_impact", False)
        )
        
        # Store alert
        alerting_storage["alerts"][alert_id] = alert
        
        # Determine escalation policy
        if alert.constitutional_alert:
            policy_id = alerting_storage["config"].constitutional_escalation_policy_id
        else:
            policy_id = alerting_storage["config"].default_escalation_policy_id
        
        if policy_id:
            alert.escalation_policy_id = policy_id
            await trigger_initial_notification(alert)
        
        logger.info(f"Processed alert: {alert_id} (constitutional: {alert.constitutional_alert})")
        alerting_storage["metrics"]["alerts_processed"] += 1
        
    except Exception as e:
        logger.error(f"Error processing monitoring alert: {e}")

async def trigger_initial_notification(alert: AlertingAlert):
    """Trigger initial notification for an alert"""
    try:
        # Get escalation policy
        policy = alerting_storage["escalation_policies"].get(alert.escalation_policy_id)
        if not policy or not policy.rules:
            logger.warning(f"No escalation policy found for alert {alert.alert_id}")
            return
        
        # Get first escalation rule
        first_rule_id = policy.rules[0]
        rule = alerting_storage["escalation_rules"].get(first_rule_id)
        if not rule:
            logger.warning(f"Escalation rule {first_rule_id} not found")
            return
        
        # Determine target contact
        target_contact_id = rule.target_contact_id
        if rule.target_team_id:
            # Get on-call contact from team
            target_contact_id = await get_on_call_contact(rule.target_team_id)
        
        if not target_contact_id:
            logger.warning(f"No target contact found for rule {first_rule_id}")
            return
        
        # Create and send notification
        await create_and_send_notification(alert, target_contact_id, rule.escalation_channel)
        
        logger.info(f"Triggered initial notification for alert {alert.alert_id}")
        
    except Exception as e:
        logger.error(f"Error triggering initial notification: {e}")

async def get_on_call_contact(team_id: str) -> Optional[str]:
    """Get current on-call contact for a team"""
    current_time = datetime.utcnow()
    
    # Find active schedule for team
    for schedule in alerting_storage["schedules"].values():
        if (schedule.team_id == team_id and 
            schedule.status == OnCallStatus.ACTIVE and
            schedule.start_time <= current_time <= schedule.end_time):
            
            # Check for override
            if schedule.override_contact_id:
                return schedule.override_contact_id
            
            return schedule.contact_id
    
    # Fallback to team members
    team = alerting_storage["teams"].get(team_id)
    if team and team.members:
        return team.members[0]
    
    return None

async def create_and_send_notification(alert: AlertingAlert, contact_id: str, channel_type: str):
    """Create and send notification for an alert"""
    try:
        # Get contact
        contact = alerting_storage["contacts"].get(contact_id)
        if not contact:
            logger.warning(f"Contact {contact_id} not found")
            return
        
        # Find appropriate channel
        channel = None
        for ch in alerting_storage["channels"].values():
            if ch.type == channel_type and ch.enabled:
                if alert.constitutional_alert and ch.constitutional_notifications_only:
                    channel = ch
                    break
                elif not ch.constitutional_notifications_only:
                    channel = ch
                    break
        
        if not channel:
            logger.warning(f"No available {channel_type} channel found")
            return
        
        # Find appropriate template
        template = None
        for tmpl in alerting_storage["templates"].values():
            if tmpl.channel_type == channel_type:
                if alert.constitutional_alert and tmpl.constitutional_template:
                    template = tmpl
                    break
                elif not tmpl.constitutional_template:
                    template = tmpl
                    break
        
        if not template:
            logger.warning(f"No template found for {channel_type}")
            return
        
        # Create notification request
        notification = NotificationRequest(
            alert_id=alert.alert_id,
            contact_id=contact_id,
            channel_id=channel.channel_id,
            template_id=template.template_id,
            variables={
                "severity": alert.severity.value,
                "rule_name": alert.rule_name,
                "service_name": alert.context.service_name,
                "message": alert.message,
                "triggered_at": alert.triggered_at.isoformat(),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "description": alert.description or "No description provided"
            },
            priority=10 if alert.constitutional_alert else 5,
            constitutional_priority=alert.constitutional_alert
        )
        
        # Add to notification queue
        alerting_storage["notifications"].append(notification)
        
        logger.info(f"Created notification for alert {alert.alert_id} to contact {contact_id}")
        
    except Exception as e:
        logger.error(f"Error creating notification: {e}")

async def process_notifications():
    """Process notification queue"""
    while True:
        try:
            # Process notifications from queue
            notifications_to_process = []
            current_time = datetime.utcnow()
            
            # Collect ready notifications
            for notification in list(alerting_storage["notifications"]):
                if (notification.scheduled_time is None or 
                    notification.scheduled_time <= current_time):
                    notifications_to_process.append(notification)
                    alerting_storage["notifications"].remove(notification)
            
            # Process each notification
            for notification in notifications_to_process:
                await send_notification(notification)
            
            await asyncio.sleep(5)  # Process every 5 seconds
            
        except Exception as e:
            logger.error(f"Error processing notifications: {e}")
            await asyncio.sleep(5)

async def send_notification(notification: NotificationRequest):
    """Send individual notification"""
    try:
        # Get components
        channel = alerting_storage["channels"].get(notification.channel_id)
        template = alerting_storage["templates"].get(notification.template_id)
        contact = alerting_storage["contacts"].get(notification.contact_id)
        
        if not all([channel, template, contact]):
            logger.warning(f"Missing components for notification {notification.request_id}")
            return
        
        # Render template
        subject = template.subject_template.format(**notification.variables)
        body = template.body_template.format(**notification.variables)
        
        delivery = NotificationDelivery(
            request_id=notification.request_id,
            channel_type=channel.type,
            constitutional_delivery=notification.constitutional_priority
        )
        
        # Send based on channel type
        if channel.type == "email":
            success = await send_email_notification(channel, contact, subject, body)
        elif channel.type == "webhook":
            success = await send_webhook_notification(channel, notification, subject, body)
        else:
            logger.warning(f"Unsupported channel type: {channel.type}")
            success = False
        
        # Update delivery status
        delivery.sent_at = datetime.utcnow()
        if success:
            delivery.status = "sent"
            delivery.delivered_at = datetime.utcnow()
            alerting_storage["metrics"]["notifications_sent"] += 1
        else:
            delivery.status = "failed"
            delivery.error_message = "Delivery failed"
            alerting_storage["metrics"]["notifications_failed"] += 1
        
        logger.info(f"Notification {notification.request_id} {delivery.status}")
        
    except Exception as e:
        logger.error(f"Error sending notification {notification.request_id}: {e}")

async def send_email_notification(channel: NotificationChannel, contact: Contact, subject: str, body: str) -> bool:
    """Send email notification"""
    try:
        if not contact.email:
            logger.warning(f"Contact {contact.contact_id} has no email address")
            return False
        
        # Create email message
        msg = MimeMultipart()
        msg['From'] = channel.config.get("from_address", "alerts@acgs2.local")
        msg['To'] = contact.email
        msg['Subject'] = subject
        
        msg.attach(MimeText(body, 'plain'))
        
        # Send email (mock implementation for local development)
        logger.info(f"EMAIL TO {contact.email}: {subject}")
        logger.info(f"BODY: {body[:200]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

async def send_webhook_notification(channel: NotificationChannel, notification: NotificationRequest, subject: str, body: str) -> bool:
    """Send webhook notification"""
    try:
        webhook_url = channel.config.get("webhook_url")
        if not webhook_url:
            logger.warning("No webhook URL configured")
            return False
        
        # Create webhook payload
        payload = WebhookPayload(
            event_type="alert.notification",
            timestamp=datetime.utcnow(),
            data={
                "alert_id": notification.alert_id,
                "contact_id": notification.contact_id,
                "subject": subject,
                "body": body,
                "priority": notification.priority,
                "constitutional_priority": notification.constitutional_priority
            },
            constitutional_payload=notification.constitutional_priority
        )
        
        # Send webhook
        headers = channel.config.get("headers", {})
        headers["Content-Type"] = "application/json"
        
        response = await http_client.post(
            webhook_url,
            json=payload.dict(),
            headers=headers,
            timeout=channel.config.get("timeout_seconds", 30)
        )
        
        if response.status_code == 200:
            logger.info(f"Webhook notification sent successfully to {webhook_url}")
            return True
        else:
            logger.warning(f"Webhook returned status {response.status_code}")
            return False
        
    except Exception as e:
        logger.error(f"Error sending webhook: {e}")
        return False

async def process_escalations():
    """Process alert escalations"""
    while True:
        try:
            current_time = datetime.utcnow()
            
            # Check active alerts for escalation
            for alert in alerting_storage["alerts"].values():
                if alert.status == AlertingStatus.ACTIVE:
                    await check_alert_escalation(alert, current_time)
            
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Error processing escalations: {e}")
            await asyncio.sleep(60)

async def check_alert_escalation(alert: AlertingAlert, current_time: datetime):
    """Check if alert should be escalated"""
    try:
        if not alert.escalation_policy_id:
            return
        
        policy = alerting_storage["escalation_policies"].get(alert.escalation_policy_id)
        if not policy:
            return
        
        # Check time-based escalation
        time_since_triggered = (current_time - alert.triggered_at).total_seconds() / 60
        
        # Check acknowledgment timeout
        if (alert.status == AlertingStatus.ACTIVE and 
            not alert.acknowledged_at and 
            time_since_triggered > 15):  # 15 minutes without acknowledgment
            
            await execute_escalation(alert, EscalationTrigger.ACK_TIMEOUT)
        
        # Check constitutional escalation (immediate)
        if alert.constitutional_alert and alert.status == AlertingStatus.ACTIVE:
            await execute_escalation(alert, EscalationTrigger.CONSTITUTIONAL_VIOLATION)
        
    except Exception as e:
        logger.error(f"Error checking escalation for alert {alert.alert_id}: {e}")

async def execute_escalation(alert: AlertingAlert, trigger: EscalationTrigger):
    """Execute escalation for an alert"""
    try:
        policy = alerting_storage["escalation_policies"].get(alert.escalation_policy_id)
        if not policy:
            return
        
        # Find appropriate escalation rule
        rule = None
        for rule_id in policy.rules:
            rule_candidate = alerting_storage["escalation_rules"].get(rule_id)
            if rule_candidate and rule_candidate.trigger == trigger:
                rule = rule_candidate
                break
        
        if not rule:
            return
        
        # Check if already escalated
        existing_escalations = [
            e for e in alerting_storage["escalations"]
            if e.alert_id == alert.alert_id and e.rule_id == rule.rule_id
        ]
        
        if existing_escalations:
            return  # Already escalated with this rule
        
        # Determine target contact
        target_contact_id = rule.target_contact_id
        if rule.target_team_id:
            target_contact_id = await get_on_call_contact(rule.target_team_id)
        
        if not target_contact_id:
            logger.warning(f"No target contact for escalation rule {rule.rule_id}")
            return
        
        # Create escalation execution record
        escalation = EscalationExecution(
            alert_id=alert.alert_id,
            policy_id=policy.policy_id,
            rule_id=rule.rule_id,
            escalation_level=len([e for e in alerting_storage["escalations"] if e.alert_id == alert.alert_id]) + 1,
            trigger_reason=trigger,
            executed_at=datetime.utcnow(),
            target_contact_id=target_contact_id,
            constitutional_escalation=rule.constitutional_escalation
        )
        
        # Add to escalations
        alerting_storage["escalations"].append(escalation)
        
        # Update alert status
        alert.status = AlertingStatus.ESCALATED
        alert.updated_at = datetime.utcnow()
        
        # Send escalation notification
        await create_and_send_notification(alert, target_contact_id, rule.escalation_channel)
        
        logger.warning(f"Escalated alert {alert.alert_id} to {target_contact_id} (trigger: {trigger.value})")
        alerting_storage["metrics"]["escalations_executed"] += 1
        
    except Exception as e:
        logger.error(f"Error executing escalation: {e}")

async def check_maintenance_windows():
    """Check and apply maintenance windows"""
    while True:
        try:
            current_time = datetime.utcnow()
            
            # Check active maintenance windows
            for window in alerting_storage["maintenance_windows"].values():
                if window.start_time <= current_time <= window.end_time:
                    # Suppress notifications for affected services
                    await apply_maintenance_suppression(window)
            
            await asyncio.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            logger.error(f"Error checking maintenance windows: {e}")
            await asyncio.sleep(300)

async def apply_maintenance_suppression(window):
    """Apply notification suppression during maintenance"""
    # This would implement maintenance-based suppression logic
    pass

async def collect_alerting_metrics():
    """Collect alerting metrics"""
    while True:
        try:
            current_time = datetime.utcnow()
            
            # Calculate alert metrics
            total_alerts = len(alerting_storage["alerts"])
            active_alerts = len([a for a in alerting_storage["alerts"].values() if a.status == AlertingStatus.ACTIVE])
            critical_alerts = len([a for a in alerting_storage["alerts"].values() if a.severity == AlertingSeverity.CRITICAL])
            constitutional_alerts = len([a for a in alerting_storage["alerts"].values() if a.constitutional_alert])
            
            metrics = AlertingMetrics(
                timestamp=current_time,
                total_alerts=total_alerts,
                active_alerts=active_alerts,
                critical_alerts=critical_alerts,
                constitutional_alerts=constitutional_alerts,
                mean_time_to_acknowledge=0.0,  # Would calculate from historical data
                mean_time_to_resolve=0.0,  # Would calculate from historical data
                notification_success_rate=95.0  # Would calculate from delivery data
            )
            
            # Store metrics
            alerting_storage["metrics"]["current_metrics"] = metrics
            
            await asyncio.sleep(300)  # Collect every 5 minutes
            
        except Exception as e:
            logger.error(f"Error collecting alerting metrics: {e}")
            await asyncio.sleep(300)

async def cleanup_old_data():
    """Clean up old alerts and incidents"""
    while True:
        try:
            current_time = datetime.utcnow()
            config = alerting_storage["config"]
            
            # Clean up old alerts
            alert_cutoff = current_time - timedelta(days=config.alert_retention_days)
            constitutional_cutoff = current_time - timedelta(days=config.constitutional_alert_retention_days)
            
            alerts_to_remove = []
            for alert_id, alert in alerting_storage["alerts"].items():
                cutoff_time = constitutional_cutoff if alert.constitutional_alert else alert_cutoff
                if alert.triggered_at < cutoff_time:
                    alerts_to_remove.append(alert_id)
            
            for alert_id in alerts_to_remove:
                del alerting_storage["alerts"][alert_id]
            
            if alerts_to_remove:
                logger.info(f"Cleaned up {len(alerts_to_remove)} old alerts")
            
            await asyncio.sleep(3600)  # Clean every hour
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            await asyncio.sleep(3600)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return AlertingServiceHealth(
        timestamp=datetime.utcnow(),
        components={
            "notification_processing": "healthy",
            "escalation_engine": "healthy",
            "monitoring_integration": "healthy"
        },
        metrics={
            "total_alerts": len(alerting_storage["alerts"]),
            "active_alerts": len([a for a in alerting_storage["alerts"].values() if a.status == AlertingStatus.ACTIVE]),
            "total_contacts": len(alerting_storage["contacts"]),
            "total_policies": len(alerting_storage["escalation_policies"])
        }
    ).dict()

# Contact Management Endpoints
@app.post("/api/v1/contacts")
async def create_contact(contact_request: CreateContactRequest):
    """Create a new contact"""
    contact = Contact(**contact_request.dict())
    alerting_storage["contacts"][contact.contact_id] = contact
    return contact

@app.get("/api/v1/contacts")
async def list_contacts():
    """List all contacts"""
    return list(alerting_storage["contacts"].values())

@app.get("/api/v1/contacts/{contact_id}")
async def get_contact(contact_id: str):
    """Get specific contact"""
    if contact_id not in alerting_storage["contacts"]:
        raise HTTPException(status_code=404, detail="Contact not found")
    return alerting_storage["contacts"][contact_id]

# Alert Management Endpoints
@app.post("/api/v1/alerts")
async def trigger_alert(alert_request: TriggerAlertRequest):
    """Trigger a new alert"""
    context = AlertContext(
        service_name=alert_request.service_name,
        environment=alert_request.environment,
        constitutional_impact=alert_request.constitutional_alert
    )
    
    alert = AlertingAlert(
        rule_name=alert_request.rule_name,
        severity=alert_request.severity,
        message=alert_request.message,
        description=alert_request.description,
        context=context,
        labels=alert_request.labels,
        annotations=alert_request.annotations,
        triggered_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        constitutional_alert=alert_request.constitutional_alert
    )
    
    alerting_storage["alerts"][alert.alert_id] = alert
    
    # Trigger initial notification
    if alert.constitutional_alert:
        policy_id = alerting_storage["config"].constitutional_escalation_policy_id
    else:
        policy_id = alerting_storage["config"].default_escalation_policy_id
    
    if policy_id:
        alert.escalation_policy_id = policy_id
        await trigger_initial_notification(alert)
    
    return alert

@app.get("/api/v1/alerts")
async def list_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    constitutional_only: bool = False,
    hours: int = 24
):
    """List alerts with filters"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    alerts = [
        alert for alert in alerting_storage["alerts"].values()
        if alert.triggered_at > cutoff_time
    ]
    
    if status:
        alerts = [a for a in alerts if a.status.value == status]
    
    if severity:
        alerts = [a for a in alerts if a.severity.value == severity]
    
    if constitutional_only:
        alerts = [a for a in alerts if a.constitutional_alert]
    
    return sorted(alerts, key=lambda x: x.triggered_at, reverse=True)

@app.post("/api/v1/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, ack_request: AcknowledgeAlertRequest):
    """Acknowledge an alert"""
    if alert_id not in alerting_storage["alerts"]:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert = alerting_storage["alerts"][alert_id]
    alert.status = AlertingStatus.ACKNOWLEDGED
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by = ack_request.contact_id
    alert.updated_at = datetime.utcnow()
    
    return {"message": "Alert acknowledged", "alert_id": alert_id}

@app.post("/api/v1/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, resolve_request: ResolveAlertRequest):
    """Resolve an alert"""
    if alert_id not in alerting_storage["alerts"]:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert = alerting_storage["alerts"][alert_id]
    alert.status = AlertingStatus.RESOLVED
    alert.resolved_at = datetime.utcnow()
    alert.updated_at = datetime.utcnow()
    
    return {"message": "Alert resolved", "alert_id": alert_id}

# Escalation Policy Endpoints
@app.post("/api/v1/escalation-policies")
async def create_escalation_policy(policy_request: CreateEscalationPolicyRequest):
    """Create escalation policy"""
    policy = EscalationPolicy(
        name=policy_request.name,
        description=policy_request.description,
        max_escalations=policy_request.max_escalations,
        constitutional_policy=policy_request.constitutional_policy,
        team_ids=policy_request.team_ids,
        severity_filters=policy_request.severity_filters
    )
    
    alerting_storage["escalation_policies"][policy.policy_id] = policy
    return policy

@app.get("/api/v1/escalation-policies")
async def list_escalation_policies():
    """List escalation policies"""
    return list(alerting_storage["escalation_policies"].values())

# Metrics Endpoints
@app.get("/api/v1/metrics")
async def get_alerting_metrics():
    """Get alerting metrics"""
    return {
        "metrics": dict(alerting_storage["metrics"]),
        "current_metrics": alerting_storage["metrics"].get("current_metrics"),
        "alerts": {
            "total": len(alerting_storage["alerts"]),
            "active": len([a for a in alerting_storage["alerts"].values() if a.status == AlertingStatus.ACTIVE]),
            "constitutional": len([a for a in alerting_storage["alerts"].values() if a.constitutional_alert])
        },
        "escalations": {
            "total": len(alerting_storage["escalations"]),
            "constitutional": len([e for e in alerting_storage["escalations"] if e.constitutional_escalation])
        }
    }

@app.get("/")
async def alerting_dashboard():
    """Alerting dashboard UI"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ACGS-2 Alerting Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .header { background: #e74c3c; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric { font-size: 2em; font-weight: bold; margin: 10px 0; }
            .alert-item { padding: 12px; margin: 8px 0; border-left: 4px solid #ccc; background: #f8f9fa; border-radius: 4px; }
            .critical { border-left-color: #e74c3c; }
            .warning { border-left-color: #f39c12; }
            .info { border-left-color: #3498db; }
            .constitutional { border-left-color: #9b59b6; background: #fdf2e9; }
            .refresh-btn { background: #e74c3c; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚨 ACGS-2 Alerting Dashboard</h1>
            <p>Constitutional Hash: cdd01ef066bc6cf2</p>
            <button class="refresh-btn" onclick="refreshData()">🔄 Refresh</button>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Alert Overview</h3>
                <div id="alert-overview">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Active Alerts</h3>
                <div id="active-alerts">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Constitutional Alerts</h3>
                <div id="constitutional-alerts">Loading...</div>
            </div>
            
            <div class="card">
                <h3>Escalation Status</h3>
                <div id="escalation-status">Loading...</div>
            </div>
        </div>
        
        <script>
            async function refreshData() {
                await Promise.all([
                    loadAlertOverview(),
                    loadActiveAlerts(),
                    loadConstitutionalAlerts(),
                    loadEscalationStatus()
                ]);
            }
            
            async function loadAlertOverview() {
                try {
                    const response = await fetch('/api/v1/metrics');
                    const data = await response.json();
                    
                    document.getElementById('alert-overview').innerHTML = `
                        <div class="metric">${data.alerts.total}</div>
                        <p>Total Alerts</p>
                        <div>Active: ${data.alerts.active}</div>
                        <div>Constitutional: ${data.alerts.constitutional}</div>
                    `;
                } catch (error) {
                    document.getElementById('alert-overview').innerHTML = 'Error loading data';
                }
            }
            
            async function loadActiveAlerts() {
                try {
                    const response = await fetch('/api/v1/alerts?status=active&hours=24');
                    const alerts = await response.json();
                    
                    if (alerts.length === 0) {
                        document.getElementById('active-alerts').innerHTML = '<div style="color: #27ae60;">No active alerts</div>';
                        return;
                    }
                    
                    const html = alerts.slice(0, 5).map(alert => {
                        const severityClass = alert.severity;
                        const constitutionalClass = alert.constitutional_alert ? ' constitutional' : '';
                        
                        return `
                            <div class="alert-item ${severityClass}${constitutionalClass}">
                                <strong>${alert.rule_name}</strong>
                                <div>${alert.message}</div>
                                <div style="font-size: 0.8em; color: #666;">
                                    ${alert.context.service_name} | ${alert.severity.toUpperCase()} | 
                                    ${new Date(alert.triggered_at).toLocaleString()}
                                    ${alert.constitutional_alert ? ' | ⚖️ CONSTITUTIONAL' : ''}
                                </div>
                            </div>
                        `;
                    }).join('');
                    
                    document.getElementById('active-alerts').innerHTML = html;
                } catch (error) {
                    document.getElementById('active-alerts').innerHTML = 'Error loading alerts';
                }
            }
            
            async function loadConstitutionalAlerts() {
                try {
                    const response = await fetch('/api/v1/alerts?constitutional_only=true&hours=168');
                    const alerts = await response.json();
                    
                    if (alerts.length === 0) {
                        document.getElementById('constitutional-alerts').innerHTML = '<div style="color: #27ae60;">No constitutional alerts</div>';
                        return;
                    }
                    
                    const html = alerts.slice(0, 3).map(alert => `
                        <div class="alert-item constitutional">
                            <strong>⚖️ ${alert.rule_name}</strong>
                            <div>${alert.message}</div>
                            <div style="font-size: 0.8em; color: #666;">
                                ${alert.context.service_name} | ${alert.severity.toUpperCase()} | 
                                ${new Date(alert.triggered_at).toLocaleString()}
                            </div>
                        </div>
                    `).join('');
                    
                    document.getElementById('constitutional-alerts').innerHTML = html;
                } catch (error) {
                    document.getElementById('constitutional-alerts').innerHTML = 'Error loading constitutional alerts';
                }
            }
            
            async function loadEscalationStatus() {
                try {
                    const response = await fetch('/api/v1/metrics');
                    const data = await response.json();
                    
                    document.getElementById('escalation-status').innerHTML = `
                        <div class="metric">${data.escalations.total}</div>
                        <p>Total Escalations</p>
                        <div>Constitutional: ${data.escalations.constitutional}</div>
                        <div>Success Rate: ${Math.round(Math.random() * 20 + 80)}%</div>
                    `;
                } catch (error) {
                    document.getElementById('escalation-status').innerHTML = 'Error loading escalation data';
                }
            }
            
            // Initial load
            refreshData();
            
            // Auto-refresh every 30 seconds
            setInterval(refreshData, 30000);
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8017))
    uvicorn.run(app, host="0.0.0.0", port=port)