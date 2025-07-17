"""
Domain Models for Advanced Security & Validation Service
Constitutional Hash: cdd01ef066bc6cf2
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Union
from uuid import UUID, uuid4
import hashlib


# Security Event Types
class SecurityEventType(Enum):
    """Types of security events"""
    AUTHENTICATION_FAILURE = "authentication_failure"
    AUTHORIZATION_VIOLATION = "authorization_violation"
    CONSTITUTIONAL_VIOLATION = "constitutional_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    INJECTION_ATTEMPT = "injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    CSRF_ATTEMPT = "csrf_attempt"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    MALWARE_DETECTION = "malware_detection"
    NETWORK_INTRUSION = "network_intrusion"
    CONFIGURATION_CHANGE = "configuration_change"


class ThreatLevel(Enum):
    """Threat severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SecurityAction(Enum):
    """Security response actions"""
    BLOCK = "block"
    QUARANTINE = "quarantine"
    MONITOR = "monitor"
    ALERT = "alert"
    LOG = "log"
    ESCALATE = "escalate"
    AUTO_REMEDIATE = "auto_remediate"
    REQUIRE_HUMAN_REVIEW = "require_human_review"


class ComplianceFramework(Enum):
    """Compliance frameworks"""
    CONSTITUTIONAL_AI = "constitutional_ai"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    NIST = "nist"
    OWASP = "owasp"


class ValidationResult(Enum):
    """Validation results"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    UNKNOWN = "unknown"
    PENDING = "pending"


class SecurityControlType(Enum):
    """Types of security controls"""
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"
    DETERRENT = "deterrent"
    RECOVERY = "recovery"
    COMPENSATING = "compensating"


# Core Domain Models

@dataclass
class ConstitutionalContext:
    """Constitutional context for security operations"""
    constitutional_hash: str = "cdd01ef066bc6cf2"
    purpose: str = ""
    tenant_id: Optional[str] = None
    compliance_level: str = "high"
    additional_constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: UUID = field(default_factory=uuid4)
    event_type: SecurityEventType = SecurityEventType.SUSPICIOUS_ACTIVITY
    threat_level: ThreatLevel = ThreatLevel.MEDIUM
    source_ip: str = ""
    source_user: Optional[str] = None
    source_service: str = ""
    target_resource: str = ""
    description: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)
    indicators: List[str] = field(default_factory=list)
    attack_vector: Optional[str] = None
    affected_assets: List[str] = field(default_factory=list)
    constitutional_context: ConstitutionalContext = field(default_factory=ConstitutionalContext)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    detection_method: str = ""
    confidence_score: float = 0.0  # 0.0 to 1.0
    false_positive_probability: float = 0.0
    correlation_id: Optional[UUID] = None
    parent_event_id: Optional[UUID] = None
    child_events: List[UUID] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    is_resolved: bool = False
    resolution_timestamp: Optional[datetime] = None
    resolution_notes: str = ""


@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    intel_id: UUID = field(default_factory=uuid4)
    threat_name: str = ""
    threat_type: str = ""
    threat_level: ThreatLevel = ThreatLevel.MEDIUM
    indicators_of_compromise: List[str] = field(default_factory=list)
    attack_patterns: List[str] = field(default_factory=list)
    mitre_tactics: List[str] = field(default_factory=list)
    mitre_techniques: List[str] = field(default_factory=list)
    cve_references: List[str] = field(default_factory=list)
    source: str = ""
    source_reliability: float = 0.0  # 0.0 to 1.0
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None
    kill_chain_phases: List[str] = field(default_factory=list)
    affected_platforms: List[str] = field(default_factory=list)
    countermeasures: List[str] = field(default_factory=list)
    severity_score: float = 0.0  # CVSS-like score
    constitutional_impact: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityRule:
    """Security detection rule"""
    rule_id: UUID = field(default_factory=uuid4)
    rule_name: str = ""
    rule_type: str = ""
    description: str = ""
    severity: ThreatLevel = ThreatLevel.MEDIUM
    enabled: bool = True
    rule_logic: str = ""  # Query or logic expression
    rule_language: str = "sigma"  # sigma, yara, suricata, etc.
    triggers: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    actions: List[SecurityAction] = field(default_factory=list)
    false_positive_rate: float = 0.0
    effectiveness_score: float = 0.0
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    constitutional_compliance: float = 1.0
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)


@dataclass
class SecurityControl:
    """Security control implementation"""
    control_id: UUID = field(default_factory=uuid4)
    control_name: str = ""
    control_type: SecurityControlType = SecurityControlType.PREVENTIVE
    control_family: str = ""
    description: str = ""
    implementation_status: str = "implemented"
    effectiveness: float = 1.0  # 0.0 to 1.0
    coverage: float = 1.0  # 0.0 to 1.0
    test_frequency: str = "daily"
    last_tested: Optional[datetime] = None
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    control_objectives: List[str] = field(default_factory=list)
    responsible_team: str = ""
    constitutional_alignment: float = 1.0
    risk_reduction: float = 0.0
    cost_of_implementation: float = 0.0
    maintenance_requirements: List[str] = field(default_factory=list)
    dependencies: List[UUID] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class VulnerabilityAssessment:
    """Vulnerability assessment result"""
    assessment_id: UUID = field(default_factory=uuid4)
    scan_type: str = ""
    target: str = ""
    scanner: str = ""
    scan_started: datetime = field(default_factory=datetime.utcnow)
    scan_completed: Optional[datetime] = None
    vulnerabilities: List[Dict[str, Any]] = field(default_factory=list)
    total_vulnerabilities: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    risk_score: float = 0.0
    constitutional_impact_score: float = 0.0
    remediation_recommendations: List[str] = field(default_factory=list)
    scan_coverage: float = 1.0
    scan_accuracy: float = 1.0
    false_positive_rate: float = 0.0
    baseline_comparison: Optional[Dict[str, Any]] = None
    remediation_timeline: Dict[str, datetime] = field(default_factory=dict)
    affected_services: List[str] = field(default_factory=list)


@dataclass
class ComplianceAssessment:
    """Compliance assessment result"""
    assessment_id: UUID = field(default_factory=uuid4)
    framework: ComplianceFramework = ComplianceFramework.CONSTITUTIONAL_AI
    assessment_date: datetime = field(default_factory=datetime.utcnow)
    assessor: str = ""
    scope: str = ""
    controls_evaluated: int = 0
    controls_compliant: int = 0
    controls_non_compliant: int = 0
    controls_not_applicable: int = 0
    overall_compliance_score: float = 0.0
    constitutional_compliance_score: float = 0.0
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    risk_rating: ThreatLevel = ThreatLevel.LOW
    remediation_plan: List[Dict[str, Any]] = field(default_factory=list)
    next_assessment_date: Optional[datetime] = None
    evidence_collected: List[str] = field(default_factory=list)
    attestations: List[Dict[str, Any]] = field(default_factory=list)
    exceptions_granted: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SecurityIncident:
    """Security incident record"""
    incident_id: UUID = field(default_factory=uuid4)
    incident_number: str = ""
    title: str = ""
    description: str = ""
    severity: ThreatLevel = ThreatLevel.MEDIUM
    status: str = "open"  # open, investigating, contained, resolved, closed
    category: str = ""
    subcategory: str = ""
    detection_time: datetime = field(default_factory=datetime.utcnow)
    containment_time: Optional[datetime] = None
    resolution_time: Optional[datetime] = None
    affected_systems: List[str] = field(default_factory=list)
    affected_users: List[str] = field(default_factory=list)
    affected_data: List[str] = field(default_factory=list)
    attack_vector: str = ""
    threat_actor: str = ""
    indicators_of_compromise: List[str] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    containment_actions: List[str] = field(default_factory=list)
    eradication_actions: List[str] = field(default_factory=list)
    recovery_actions: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    assigned_to: str = ""
    escalated_to: List[str] = field(default_factory=list)
    constitutional_impact: str = ""
    regulatory_notification_required: bool = False
    customer_notification_required: bool = False
    cost_estimate: float = 0.0
    related_events: List[UUID] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SecurityMetrics:
    """Security metrics and KPIs"""
    metric_id: UUID = field(default_factory=uuid4)
    metric_name: str = ""
    metric_type: str = ""
    value: float = 0.0
    unit: str = ""
    target_value: Optional[float] = None
    threshold_critical: Optional[float] = None
    threshold_warning: Optional[float] = None
    collection_method: str = ""
    collection_frequency: str = ""
    last_collected: datetime = field(default_factory=datetime.utcnow)
    trend: str = "stable"  # improving, stable, degrading
    trend_period: str = "7d"
    historical_values: List[Dict[str, Any]] = field(default_factory=list)
    constitutional_alignment: float = 1.0
    business_impact: str = ""
    related_controls: List[UUID] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    reporting_frequency: str = "daily"
    data_sources: List[str] = field(default_factory=list)


@dataclass
class SecurityConfiguration:
    """Security service configuration"""
    service_name: str = "Advanced Security & Validation Service"
    service_version: str = "1.0.0"
    constitutional_hash: str = "cdd01ef066bc6cf2"
    enable_real_time_monitoring: bool = True
    enable_threat_intelligence: bool = True
    enable_behavioral_analysis: bool = True
    enable_ml_detection: bool = True
    enable_auto_remediation: bool = False
    enable_compliance_monitoring: bool = True
    threat_detection_sensitivity: str = "medium"  # low, medium, high
    false_positive_tolerance: float = 0.05
    incident_auto_escalation_threshold: ThreatLevel = ThreatLevel.HIGH
    retention_period_days: int = 365
    anonymization_enabled: bool = True
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    audit_all_access: bool = True
    require_constitutional_validation: bool = True
    max_concurrent_scans: int = 10
    scan_throttle_rate: float = 100.0  # requests per second
    notification_channels: List[str] = field(default_factory=list)
    integration_endpoints: Dict[str, str] = field(default_factory=dict)


@dataclass
class ZeroTrustPolicy:
    """Zero Trust security policy"""
    policy_id: UUID = field(default_factory=uuid4)
    policy_name: str = ""
    description: str = ""
    enabled: bool = True
    trust_level_required: str = "verified"  # none, basic, verified, high
    verification_methods: List[str] = field(default_factory=list)
    resource_access_rules: List[Dict[str, Any]] = field(default_factory=list)
    continuous_verification: bool = True
    verification_interval: int = 300  # seconds
    risk_assessment_required: bool = True
    device_compliance_required: bool = True
    location_restrictions: List[str] = field(default_factory=list)
    time_restrictions: List[str] = field(default_factory=list)
    conditional_access_rules: List[Dict[str, Any]] = field(default_factory=list)
    constitutional_constraints: List[str] = field(default_factory=list)
    exception_rules: List[Dict[str, Any]] = field(default_factory=list)
    monitoring_requirements: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SecurityAuditEntry:
    """Security audit log entry"""
    audit_id: UUID = field(default_factory=uuid4)
    event_type: str = ""
    actor: str = ""
    resource: str = ""
    action: str = ""
    outcome: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_ip: str = ""
    user_agent: str = ""
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    constitutional_context: ConstitutionalContext = field(default_factory=ConstitutionalContext)
    risk_score: float = 0.0
    anomaly_score: float = 0.0
    compliance_flags: List[str] = field(default_factory=list)
    event_details: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[UUID] = None
    chain_of_custody: List[Dict[str, Any]] = field(default_factory=list)
    retention_policy: str = "365d"
    classification: str = "internal"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit entry to dictionary"""
        return {
            "audit_id": str(self.audit_id),
            "event_type": self.event_type,
            "actor": self.actor,
            "resource": self.resource,
            "action": self.action,
            "outcome": self.outcome,
            "timestamp": self.timestamp.isoformat(),
            "source_ip": self.source_ip,
            "constitutional_hash": self.constitutional_context.constitutional_hash,
            "risk_score": self.risk_score,
            "anomaly_score": self.anomaly_score,
            "compliance_flags": self.compliance_flags,
            "correlation_id": str(self.correlation_id) if self.correlation_id else None
        }


@dataclass
class SecurityCapabilities:
    """Capabilities of the Security & Validation service"""
    real_time_threat_detection: bool = True
    behavioral_analysis: bool = True
    machine_learning_detection: bool = True
    threat_intelligence_integration: bool = True
    vulnerability_scanning: bool = True
    compliance_monitoring: bool = True
    incident_response_automation: bool = True
    zero_trust_enforcement: bool = True
    constitutional_compliance_validation: bool = True
    advanced_audit_logging: bool = True
    security_orchestration: bool = True
    threat_hunting: bool = True
    digital_forensics: bool = True
    security_metrics_reporting: bool = True
    risk_assessment: bool = True
    penetration_testing: bool = False  # Requires special authorization
    red_team_exercises: bool = False  # Requires special authorization
    max_concurrent_scans: int = 10
    supported_scan_types: List[str] = field(default_factory=lambda: [
        "vulnerability", "compliance", "configuration", "behavioral", "threat_intelligence"
    ])
    supported_compliance_frameworks: List[str] = field(default_factory=lambda: [
        "constitutional_ai", "soc2", "iso27001", "gdpr", "ccpa", "nist", "owasp"
    ])
    constitutional_validation: bool = True
    security_certification: str = "ACGS-2-Constitutional-Security-Validated"