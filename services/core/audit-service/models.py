"""
Audit Service Models
Constitutional Hash: cdd01ef066bc6cf2

Data models for audit logging, compliance reporting, and regulatory tracking.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
import uuid

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class EventType(str, Enum):
    """Audit event types"""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_CONFIGURATION = "system_configuration"
    CONSTITUTIONAL_EVENT = "constitutional_event"
    CONSENSUS_DECISION = "consensus_decision"
    SECURITY_INCIDENT = "security_incident"
    PERFORMANCE_ALERT = "performance_alert"
    COMPLIANCE_CHECK = "compliance_check"
    USER_ACTION = "user_action"
    SYSTEM_ERROR = "system_error"
    AUDIT_ALERT = "audit_alert"
    DATA_PROCESSING = "data_processing"
    PRIVACY_EVENT = "privacy_event"


class ComplianceStatus(str, Enum):
    """Compliance status values"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL_COMPLIANCE = "partial_compliance"
    UNDER_REVIEW = "under_review"
    EXEMPTED = "exempted"


class ExportFormat(str, Enum):
    """Export format options"""

    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    XML = "xml"


class AuditEntry(BaseModel):
    """Core audit entry"""

    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str
    source_service: str
    user_id: Optional[str] = None
    action: str
    resource: str
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    constitutional_impact: bool = False
    compliance_relevant: bool = True
    retention_category: str = "default"
    integrity_hash: Optional[str] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH


class AuditQuery(BaseModel):
    """Query parameters for audit entries"""

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: Optional[List[str]] = None
    source_services: Optional[List[str]] = None
    user_id: Optional[str] = None
    resource: Optional[str] = None
    constitutional_impact_only: bool = False
    compliance_relevant_only: bool = False
    success_only: Optional[bool] = None
    limit: Optional[int] = Field(None, le=10000)
    offset: Optional[int] = 0


class ComplianceReport(BaseModel):
    """Compliance assessment report"""

    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    framework_name: str
    status: ComplianceStatus
    compliance_score: float = Field(ge=0.0, le=100.0)
    violations: List[str] = []
    remediation_actions: List[str] = []
    recommendations: List[str] = []
    report_period_start: datetime
    report_period_end: datetime
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: Optional[str] = None
    total_events_reviewed: int = 0
    constitutional_events: int = 0
    security_events: int = 0
    data_processing_events: int = 0
    executive_summary: Optional[str] = None
    detailed_findings: Dict[str, Any] = {}
    risk_assessment: Dict[str, str] = {}


class RegulatoryFramework(BaseModel):
    """Regulatory framework definition"""

    framework_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    version: str = "1.0"
    requirements: List[str] = []
    retention_requirements: str
    audit_requirements: str
    jurisdiction: str
    effective_date: datetime
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    compliance_scoring: Dict[str, float] = {}
    mandatory_fields: List[str] = []
    optional_fields: List[str] = []


class DataRetentionPolicy(BaseModel):
    """Data retention policy"""

    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    retention_days: int  # -1 for permanent retention
    data_types: List[str] = []
    regulatory_basis: List[str] = []
    auto_deletion: bool = True
    deletion_method: str = "secure_delete"
    archive_before_deletion: bool = True
    archive_location: Optional[str] = None
    exceptions: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_reviewed: datetime = Field(default_factory=datetime.utcnow)


class AuditTrail(BaseModel):
    """Audit trail for specific resource"""

    resource_id: str
    resource_type: str
    entries: List[AuditEntry] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    integrity_verified: bool = True
    chain_hash: Optional[str] = None


class SystemActivity(BaseModel):
    """System-wide activity summary"""

    activity_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    period_start: datetime
    period_end: datetime
    total_events: int = 0
    events_by_type: Dict[str, int] = {}
    events_by_service: Dict[str, int] = {}
    constitutional_events: int = 0
    security_events: int = 0
    compliance_violations: int = 0
    unique_users: int = 0
    peak_activity_hour: Optional[int] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ConstitutionalEvent(BaseModel):
    """Constitutional governance event"""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    description: str
    impact_level: str  # low, medium, high, critical
    consensus_required: bool = False
    consensus_achieved: Optional[bool] = None
    human_oversight_required: bool = False
    human_oversight_completed: Optional[bool] = None
    related_audit_entry: Optional[str] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH
    compliance_impact: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ComplianceMetrics(BaseModel):
    """Compliance performance metrics"""

    total_audit_entries: int = 0
    constitutional_events: int = 0
    compliance_violations_last_30_days: int = 0
    data_retention_compliance_rate: float = Field(ge=0.0, le=100.0, default=100.0)
    regulatory_framework_coverage: int = 0
    audit_trail_integrity_score: float = Field(ge=0.0, le=100.0, default=100.0)
    average_incident_response_time_hours: float = 0.0
    privacy_compliance_score: float = Field(ge=0.0, le=100.0, default=100.0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class AuditAlert(BaseModel):
    """Audit system alert"""

    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: str
    severity: str  # low, medium, high, critical
    message: str
    details: Dict[str, Any] = {}
    source_entry_id: Optional[str] = None
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    requires_action: bool = False
    escalated: bool = False
    escalated_at: Optional[datetime] = None
    processed: bool = False
    processed_at: Optional[datetime] = None


class AuditConfiguration(BaseModel):
    """Audit system configuration"""

    config_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    real_time_monitoring: bool = True
    constitutional_tracking: bool = True
    performance_monitoring: bool = True
    security_monitoring: bool = True
    compliance_monitoring: bool = True
    pii_anonymization: bool = True
    encryption_enabled: bool = True
    integrity_verification: bool = True
    regulatory_compliance_checking: bool = True
    alert_thresholds: Dict[str, float] = {}
    retention_defaults: Dict[str, int] = {}
    export_formats: List[str] = ["json", "csv"]
    notification_channels: List[str] = []
    audit_storage_backend: str = "local"
    backup_enabled: bool = True
    backup_frequency_hours: int = 24
    retention_enforcement: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)


class ReportTemplate(BaseModel):
    """Compliance report template"""

    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    sections: List[str] = []
    data_sources: List[str] = []
    filters: Dict[str, Any] = {}
    frequency: str = "monthly"  # daily, weekly, monthly, quarterly, annually
    regulatory_frameworks: List[str] = []
    output_formats: List[str] = ["pdf", "json"]
    recipients: List[str] = []
    auto_generate: bool = False
    next_generation_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)


class PrivacyEvent(BaseModel):
    """Privacy-related event"""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str  # consent_given, consent_withdrawn, data_accessed, data_deleted
    data_subject_id: Optional[str] = None
    data_categories: List[str] = []
    processing_purpose: Optional[str] = None
    legal_basis: Optional[str] = None
    consent_source: Optional[str] = None
    retention_period: Optional[int] = None
    third_party_sharing: bool = False
    cross_border_transfer: bool = False
    anonymization_applied: bool = False
    related_audit_entry: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DataLineage(BaseModel):
    """Data lineage tracking"""

    lineage_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    data_id: str
    data_type: str
    source_system: str
    transformations: List[Dict[str, Any]] = []
    destinations: List[str] = []
    processing_purposes: List[str] = []
    retention_applied: bool = True
    anonymization_applied: bool = False
    encryption_applied: bool = True
    access_controls: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class AuditDashboardWidget(BaseModel):
    """Dashboard widget configuration"""

    widget_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    widget_type: str  # chart, table, metric, alert_list, compliance_status
    data_source: str
    query_parameters: Dict[str, Any] = {}
    visualization_config: Dict[str, Any] = {}
    refresh_interval_seconds: int = 60
    position: Dict[str, int] = {"x": 0, "y": 0, "width": 1, "height": 1}
    visible: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditStatistics(BaseModel):
    """Audit system statistics"""

    total_entries: int = 0
    entries_by_type: Dict[str, int] = {}
    entries_by_service: Dict[str, int] = {}
    entries_by_hour: Dict[int, int] = {}
    constitutional_events_count: int = 0
    compliance_violations_count: int = 0
    security_incidents_count: int = 0
    data_retention_stats: Dict[str, int] = {}
    integrity_check_stats: Dict[str, int] = {}
    export_stats: Dict[str, int] = {}
    alert_stats: Dict[str, int] = {}
    generated_at: datetime = Field(default_factory=datetime.utcnow)
