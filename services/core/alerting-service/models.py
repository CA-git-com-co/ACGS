"""
Alerting Service Data Models
Constitutional Hash: cdd01ef066bc6cf2

Data models for alerting, escalation, and notification management.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Core Enums
class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"
    PAGERDUTY = "pagerduty"
    DISCORD = "discord"

class EscalationTrigger(str, Enum):
    TIME_BASED = "time_based"
    ACK_TIMEOUT = "ack_timeout"
    SEVERITY_INCREASE = "severity_increase"
    NO_RESPONSE = "no_response"
    CONSTITUTIONAL_VIOLATION = "constitutional_violation"

class AlertingSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertingStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"

class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"

class OnCallStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OVERRIDE = "override"
    ESCALATED = "escalated"

# Contact and Team Models
class Contact(BaseModel):
    contact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    slack_user_id: Optional[str] = None
    teams_user_id: Optional[str] = None
    timezone: str = "UTC"
    preferred_channels: List[NotificationChannel] = [NotificationChannel.EMAIL]
    constitutional_clearance_level: int = Field(ge=1, le=10, default=1)
    
    class Config:
        use_enum_values = True

class Team(BaseModel):
    team_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    members: List[str] = []  # contact_ids
    escalation_policy_id: Optional[str] = None
    constitutional_oversight: bool = False
    
class OnCallSchedule(BaseModel):
    schedule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    team_id: str
    contact_id: str
    start_time: datetime
    end_time: datetime
    timezone: str = "UTC"
    status: OnCallStatus = OnCallStatus.ACTIVE
    override_contact_id: Optional[str] = None
    rotation_frequency_hours: int = Field(default=168, ge=1)  # Default weekly

# Notification Models
class NotificationChannel(BaseModel):
    channel_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: NotificationChannel
    config: Dict[str, Any] = {}
    enabled: bool = True
    rate_limit_per_hour: int = Field(default=100, ge=1)
    constitutional_notifications_only: bool = False

class NotificationTemplate(BaseModel):
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    channel_type: NotificationChannel
    subject_template: str
    body_template: str
    constitutional_template: bool = False
    variables: List[str] = []

class NotificationRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str
    contact_id: str
    channel_id: str
    template_id: str
    variables: Dict[str, str] = {}
    priority: int = Field(ge=1, le=10, default=5)
    constitutional_priority: bool = False
    scheduled_time: Optional[datetime] = None

class NotificationDelivery(BaseModel):
    delivery_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    channel_type: NotificationChannel
    status: str  # sent, delivered, failed, bounced
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    constitutional_delivery: bool = False

# Escalation Models
class EscalationRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    trigger: EscalationTrigger
    condition: str  # JSON or expression for when to escalate
    delay_minutes: int = Field(default=15, ge=1)
    target_contact_id: Optional[str] = None
    target_team_id: Optional[str] = None
    escalation_channel: NotificationChannel = NotificationChannel.EMAIL
    constitutional_escalation: bool = False
    active: bool = True

class EscalationPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    rules: List[str] = []  # escalation_rule_ids in order
    max_escalations: int = Field(default=3, ge=1)
    constitutional_policy: bool = False
    team_ids: List[str] = []
    severity_filters: List[AlertingSeverity] = []

class EscalationExecution(BaseModel):
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str
    policy_id: str
    rule_id: str
    escalation_level: int = Field(ge=1)
    trigger_reason: EscalationTrigger
    executed_at: datetime
    target_contact_id: Optional[str] = None
    target_team_id: Optional[str] = None
    notification_sent: bool = False
    constitutional_escalation: bool = False

# Alert Models
class AlertContext(BaseModel):
    service_name: str
    environment: str = "production"
    region: Optional[str] = None
    cluster: Optional[str] = None
    namespace: Optional[str] = None
    constitutional_impact: bool = False
    performance_metrics: Dict[str, float] = {}

class AlertingAlert(BaseModel):
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_name: str
    severity: AlertingSeverity
    status: AlertingStatus = AlertingStatus.ACTIVE
    message: str
    description: Optional[str] = None
    context: AlertContext
    labels: Dict[str, str] = {}
    annotations: Dict[str, str] = {}
    triggered_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None  # contact_id
    escalation_policy_id: Optional[str] = None
    incident_id: Optional[str] = None
    constitutional_alert: bool = False
    hash_validation: str = CONSTITUTIONAL_HASH

# Incident Models
class Incident(BaseModel):
    incident_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    status: IncidentStatus = IncidentStatus.OPEN
    severity: AlertingSeverity
    priority: int = Field(ge=1, le=10, default=5)
    affected_services: List[str] = []
    assigned_team_id: Optional[str] = None
    assigned_contact_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    alert_ids: List[str] = []  # Related alerts
    constitutional_incident: bool = False
    timeline: List[Dict[str, Any]] = []

class IncidentUpdate(BaseModel):
    update_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    contact_id: str
    status: Optional[IncidentStatus] = None
    message: str
    timestamp: datetime
    constitutional_update: bool = False

# Suppression and Maintenance Models
class AlertSuppression(BaseModel):
    suppression_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    filter_expression: str  # JSON or expression to match alerts
    start_time: datetime
    end_time: datetime
    created_by: str  # contact_id
    constitutional_suppression: bool = False
    active: bool = True

class MaintenanceWindow(BaseModel):
    window_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    affected_services: List[str] = []
    start_time: datetime
    end_time: datetime
    created_by: str  # contact_id
    notifications_suppressed: bool = True
    constitutional_maintenance: bool = False
    recurring: bool = False
    recurrence_pattern: Optional[str] = None  # cron expression

# Metrics and Reporting Models
class AlertingMetrics(BaseModel):
    timestamp: datetime
    total_alerts: int = 0
    active_alerts: int = 0
    critical_alerts: int = 0
    acknowledged_alerts: int = 0
    resolved_alerts: int = 0
    escalated_alerts: int = 0
    constitutional_alerts: int = 0
    mean_time_to_acknowledge: float = 0.0  # minutes
    mean_time_to_resolve: float = 0.0  # minutes
    notification_success_rate: float = 0.0  # percentage

class EscalationMetrics(BaseModel):
    timestamp: datetime
    total_escalations: int = 0
    successful_escalations: int = 0
    failed_escalations: int = 0
    constitutional_escalations: int = 0
    average_escalation_time: float = 0.0  # minutes
    escalation_success_rate: float = 0.0  # percentage

class NotificationMetrics(BaseModel):
    timestamp: datetime
    channel_type: NotificationChannel
    total_sent: int = 0
    total_delivered: int = 0
    total_failed: int = 0
    delivery_rate: float = 0.0  # percentage
    average_delivery_time: float = 0.0  # seconds
    constitutional_notifications: int = 0

# System Configuration Models
class AlertingConfig(BaseModel):
    config_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    default_escalation_policy_id: Optional[str] = None
    constitutional_escalation_policy_id: Optional[str] = None
    default_notification_channels: List[str] = []  # channel_ids
    alert_retention_days: int = Field(default=90, ge=1)
    incident_retention_days: int = Field(default=365, ge=1)
    notification_rate_limit_per_minute: int = Field(default=10, ge=1)
    constitutional_alert_retention_days: int = Field(default=2555, ge=365)  # 7 years
    enable_constitutional_oversight: bool = True
    hash_validation: str = CONSTITUTIONAL_HASH

# Health and Status Models
class AlertingServiceHealth(BaseModel):
    service_name: str = "alerting-service"
    status: str = "healthy"
    version: str = "1.0.0"
    constitutional_hash: str = CONSTITUTIONAL_HASH
    timestamp: datetime
    components: Dict[str, str] = {}  # component_name -> status
    metrics: Dict[str, Any] = {}

# API Request/Response Models
class CreateContactRequest(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    slack_user_id: Optional[str] = None
    teams_user_id: Optional[str] = None
    timezone: str = "UTC"
    preferred_channels: List[NotificationChannel] = [NotificationChannel.EMAIL]
    constitutional_clearance_level: int = Field(ge=1, le=10, default=1)

class CreateTeamRequest(BaseModel):
    name: str
    description: Optional[str] = None
    member_contact_ids: List[str] = []
    constitutional_oversight: bool = False

class CreateEscalationPolicyRequest(BaseModel):
    name: str
    description: Optional[str] = None
    escalation_rules: List[Dict[str, Any]] = []
    max_escalations: int = Field(default=3, ge=1)
    constitutional_policy: bool = False
    team_ids: List[str] = []
    severity_filters: List[AlertingSeverity] = []

class TriggerAlertRequest(BaseModel):
    rule_name: str
    severity: AlertingSeverity
    message: str
    description: Optional[str] = None
    service_name: str
    environment: str = "production"
    labels: Dict[str, str] = {}
    annotations: Dict[str, str] = {}
    constitutional_alert: bool = False

class AcknowledgeAlertRequest(BaseModel):
    contact_id: str
    acknowledgment_message: Optional[str] = None
    constitutional_acknowledgment: bool = False

class ResolveAlertRequest(BaseModel):
    contact_id: str
    resolution_message: Optional[str] = None
    constitutional_resolution: bool = False

class CreateIncidentRequest(BaseModel):
    title: str
    description: str
    severity: AlertingSeverity
    priority: int = Field(ge=1, le=10, default=5)
    affected_services: List[str] = []
    assigned_team_id: Optional[str] = None
    assigned_contact_id: Optional[str] = None
    alert_ids: List[str] = []
    constitutional_incident: bool = False

# Webhook Models
class WebhookPayload(BaseModel):
    webhook_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str  # alert.triggered, alert.acknowledged, alert.resolved, etc.
    timestamp: datetime
    data: Dict[str, Any]
    constitutional_payload: bool = False
    hash_validation: str = CONSTITUTIONAL_HASH

class WebhookDelivery(BaseModel):
    delivery_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    webhook_url: str
    payload: WebhookPayload
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    constitutional_delivery: bool = False