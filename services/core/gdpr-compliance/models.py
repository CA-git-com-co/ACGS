"""
GDPR Compliance Models
Constitutional Hash: cdd01ef066bc6cf2

Data models for GDPR compliance including data subjects, consent management,
privacy impact assessments, and data breach handling.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
import uuid

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class ConsentStatus(str, Enum):
    """Consent status values"""
    GIVEN = "given"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"
    REFUSED = "refused"
    DELETED = "deleted"

class ProcessingLawfulBasis(str, Enum):
    """GDPR lawful bases for processing"""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTEREST = "legitimate_interest"

class DataCategory(str, Enum):
    """Categories of personal data"""
    IDENTITY = "identity"  # Name, ID numbers, etc.
    CONTACT = "contact"    # Email, phone, address
    DEMOGRAPHIC = "demographic"  # Age, gender, etc.
    FINANCIAL = "financial"      # Payment, billing
    TECHNICAL = "technical"      # IP, cookies, logs
    BEHAVIORAL = "behavioral"    # Usage patterns, preferences
    BIOMETRIC = "biometric"      # Fingerprints, photos
    HEALTH = "health"           # Medical data
    SPECIAL_CATEGORY = "special_category"  # Sensitive data

class RequestType(str, Enum):
    """Data subject request types"""
    ACCESS = "access"                    # Article 15
    RECTIFICATION = "rectification"      # Article 16
    ERASURE = "erasure"                 # Article 17
    RESTRICTION = "restriction"          # Article 18
    PORTABILITY = "portability"         # Article 20
    OBJECTION = "objection"             # Article 21
    AUTOMATED_DECISION = "automated_decision"  # Article 22

class DataSubject(BaseModel):
    """Data subject (individual)"""
    subject_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    country: Optional[str] = None
    language_preference: str = "en"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: Optional[datetime] = None
    anonymized: bool = False
    data_categories: List[DataCategory] = []
    special_categories: List[str] = []
    constitutional_hash: str = CONSTITUTIONAL_HASH

class ConsentRecord(BaseModel):
    """Consent record for data processing"""
    consent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject_id: str
    processing_activity: str
    purpose: str
    lawful_basis: ProcessingLawfulBasis
    consent_method: str  # web_form, email, phone, etc.
    consent_text: str
    status: ConsentStatus = ConsentStatus.GIVEN
    given_at: datetime = Field(default_factory=datetime.utcnow)
    withdrawn_at: Optional[datetime] = None
    withdrawal_reason: Optional[str] = None
    expires_at: Optional[datetime] = None
    renewal_required: bool = False
    data_categories: List[DataCategory] = []
    special_categories: bool = False
    automated_decision_making: bool = False
    profiling: bool = False
    third_party_sharing: bool = False
    international_transfers: bool = False
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DataProcessingActivity(BaseModel):
    """Data processing activity record"""
    activity_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    controller_id: str
    processor_ids: List[str] = []
    purposes: List[str]
    lawful_basis: ProcessingLawfulBasis
    special_category_basis: Optional[str] = None
    data_categories: List[DataCategory]
    special_categories: bool = False
    data_subjects: List[str]  # Categories of data subjects
    recipients: List[str]     # Who receives the data
    retention_period_months: int
    international_transfers: bool = False
    transfer_safeguards: Optional[str] = None
    automated_decision_making: bool = False
    profiling: bool = False
    security_measures: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_reviewed: datetime = Field(default_factory=datetime.utcnow)
    next_review_date: Optional[datetime] = None

class DataRetentionRule(BaseModel):
    """Data retention rule"""
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    data_categories: List[DataCategory]
    retention_period_months: int  # -1 for permanent
    retention_basis: str
    deletion_method: str = "secure_deletion"
    anonymization_method: Optional[str] = None
    exceptions: List[str] = []
    auto_deletion: bool = True
    review_frequency_months: int = 12
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_reviewed: datetime = Field(default_factory=datetime.utcnow)

class PrivacyImpactAssessment(BaseModel):
    """Privacy Impact Assessment (PIA/DPIA)"""
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    processing_activity_id: str
    assessor_name: str
    assessor_email: EmailStr
    risk_level: str = "medium"  # low, medium, high
    necessity_assessment: str
    proportionality_assessment: str
    data_minimization_measures: List[str] = []
    security_measures: List[str] = []
    data_subject_rights_impact: str
    legitimate_interests_assessment: Optional[str] = None
    consultation_required: bool = False
    consultation_details: Optional[str] = None
    mitigation_measures: List[str] = []
    residual_risks: List[str] = []
    approval_status: str = "draft"  # draft, approved, rejected
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    review_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DataBreachIncident(BaseModel):
    """Data breach incident record"""
    incident_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    incident_type: str  # confidentiality, integrity, availability
    severity: str = "medium"  # low, medium, high, critical
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    reported_by: str
    affected_data_categories: List[DataCategory] = []
    affected_data_subjects_count: int = 0
    affected_data_subjects_details: Optional[str] = None
    root_cause: Optional[str] = None
    containment_actions: List[str] = []
    remediation_actions: List[str] = []
    data_subject_notification_required: bool = False
    data_subject_notification_sent: bool = False
    data_subject_notification_date: Optional[datetime] = None
    supervisory_authority_notification_required: bool = False
    supervisory_authority_notification_sent: bool = False
    supervisory_authority_notification_date: Optional[datetime] = None
    status: str = "open"  # open, investigating, contained, resolved
    resolution_date: Optional[datetime] = None
    lessons_learned: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DataSubjectRequest(BaseModel):
    """Data subject request"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject_id: str
    request_type: RequestType
    details: Dict[str, Any] = {}
    verification_method: str = "email"
    verification_completed: bool = False
    legal_basis: Optional[str] = None
    status: str = "pending"  # pending, processing, completed, rejected
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    response_data: Optional[Dict[str, Any]] = None
    rejection_reason: Optional[str] = None
    complexity: str = "standard"  # simple, standard, complex
    fee_required: bool = False
    fee_amount: Optional[float] = None
    extension_granted: bool = False
    extension_reason: Optional[str] = None
    processor_notifications: List[str] = []

class ComplianceReport(BaseModel):
    """GDPR compliance report"""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_type: str
    period_start: datetime
    period_end: datetime
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    total_data_subjects: int = 0
    active_consents: int = 0
    expired_consents: int = 0
    withdrawn_consents: int = 0
    consent_refresh_rate: float = 0.0
    withdrawal_rate: float = 0.0
    subject_requests_received: int = 0
    subject_requests_completed: int = 0
    subject_requests_pending: int = 0
    average_response_time_days: float = 0.0
    breach_incidents: int = 0
    privacy_assessments_completed: int = 0
    compliance_score: float = 100.0
    recommendations: List[str] = []
    action_items: List[str] = []

class PrivacyNotice(BaseModel):
    """Privacy notice/policy"""
    notice_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    version: str
    effective_date: datetime
    language: str = "en"
    data_controller: str
    contact_details: Dict[str, str]
    purposes_of_processing: List[str]
    lawful_bases: List[str]
    data_categories: List[str]
    data_sources: List[str] = []
    recipients: List[str] = []
    retention_periods: Dict[str, str]
    international_transfers: bool = False
    transfer_safeguards: Optional[str] = None
    data_subject_rights: List[str]
    automated_decision_making: bool = False
    profiling: bool = False
    cookies_used: bool = False
    cookie_policy_link: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class DataController(BaseModel):
    """Data controller information"""
    controller_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    organization: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    address: str
    dpo_name: Optional[str] = None
    dpo_email: Optional[EmailStr] = None
    dpo_phone: Optional[str] = None
    lawful_bases: List[ProcessingLawfulBasis] = []
    data_categories: List[DataCategory] = []
    processing_activities: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DataProcessor(BaseModel):
    """Data processor information"""
    processor_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    organization: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    address: str
    processing_agreement_signed: bool = False
    processing_agreement_date: Optional[datetime] = None
    security_certifications: List[str] = []
    processing_activities: List[str] = []
    subprocessors: List[str] = []
    international_transfers: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CrossBorderTransfer(BaseModel):
    """Cross-border data transfer record"""
    transfer_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_country: str
    to_country: str
    adequacy_decision: bool = False
    safeguards_type: Optional[str] = None  # SCCs, BCRs, certification
    safeguards_details: Optional[str] = None
    data_categories: List[DataCategory] = []
    purposes: List[str] = []
    data_subjects_informed: bool = False
    data_importer: str
    data_exporter: str
    transfer_date: datetime = Field(default_factory=datetime.utcnow)
    legal_basis: Optional[str] = None
    derogation_used: Optional[str] = None
    risk_assessment_completed: bool = False
    additional_safeguards: List[str] = []

class ConsentStatistics(BaseModel):
    """Consent statistics"""
    total_consents: int = 0
    active_consents: int = 0
    expired_consents: int = 0
    withdrawn_consents: int = 0
    pending_consents: int = 0
    consent_rate: float = 0.0
    withdrawal_rate: float = 0.0
    expiry_rate: float = 0.0
    average_consent_duration_days: float = 0.0
    consents_by_purpose: Dict[str, int] = {}
    consents_by_category: Dict[str, int] = {}
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class DataSubjectStatistics(BaseModel):
    """Data subject statistics"""
    total_subjects: int = 0
    active_subjects: int = 0
    anonymized_subjects: int = 0
    subjects_by_country: Dict[str, int] = {}
    subjects_by_category: Dict[str, int] = {}
    average_data_age_days: float = 0.0
    subjects_with_requests: int = 0
    subjects_with_consents: int = 0
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class GDPRConfiguration(BaseModel):
    """GDPR service configuration"""
    config_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_name: str = "ACGS-2 Platform"
    default_retention_days: int = 365
    consent_refresh_months: int = 24
    breach_notification_hours: int = 72
    subject_request_response_days: int = 30
    anonymization_enabled: bool = True
    pseudonymization_enabled: bool = True
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    audit_trail_enabled: bool = True
    data_minimization_enforced: bool = True
    purpose_limitation_enforced: bool = True
    storage_limitation_enforced: bool = True
    accuracy_checks_enabled: bool = True
    integrity_checks_enabled: bool = True
    availability_monitoring_enabled: bool = True
    constitutional_hash: str = CONSTITUTIONAL_HASH
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)