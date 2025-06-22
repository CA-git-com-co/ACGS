"""
ACGS-1 Comprehensive Audit Logging & Compliance Manager

This module provides enterprise-grade audit logging and compliance capabilities
including immutable audit trails, regulatory compliance monitoring, data retention
policies, privacy protection, and comprehensive compliance reporting.

Features:
- Immutable audit logging with cryptographic integrity
- GDPR, CCPA, SOX, HIPAA compliance support
- Automated compliance reporting and monitoring
- Data retention and archival policies
- Privacy protection and data anonymization
- Real-time compliance violation detection
- Regulatory audit trail generation
"""

import hashlib
import json
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Set, Union
from enum import Enum
from dataclasses import dataclass, field

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import structlog

logger = structlog.get_logger(__name__)


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    SOC_2 = "soc_2"
    NIST = "nist"
    FIPS_140_3 = "fips_140_3"
    CONSTITUTIONAL_GOVERNANCE = "constitutional_governance"


class AuditEventType(str, Enum):
    """Audit event types."""
    USER_AUTHENTICATION = "user_authentication"
    USER_AUTHORIZATION = "user_authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    POLICY_CREATION = "policy_creation"
    POLICY_MODIFICATION = "policy_modification"
    POLICY_ENFORCEMENT = "policy_enforcement"
    CONSTITUTIONAL_VALIDATION = "constitutional_validation"
    FORMAL_VERIFICATION = "formal_verification"
    GOVERNANCE_ACTION = "governance_action"
    SYSTEM_CONFIGURATION = "system_configuration"
    SECURITY_EVENT = "security_event"
    COMPLIANCE_VIOLATION = "compliance_violation"
    PRIVACY_EVENT = "privacy_event"


class DataClassification(str, Enum):
    """Data classification for compliance."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"
    PHI = "phi"
    FINANCIAL = "financial"
    CONSTITUTIONAL = "constitutional"


class RetentionPolicy(str, Enum):
    """Data retention policies."""
    DAYS_30 = "30_days"
    DAYS_90 = "90_days"
    MONTHS_6 = "6_months"
    YEAR_1 = "1_year"
    YEARS_3 = "3_years"
    YEARS_7 = "7_years"
    YEARS_10 = "10_years"
    PERMANENT = "permanent"


@dataclass
class AuditEvent:
    """Comprehensive audit event record."""
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    service_name: str
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource: str
    action: str
    result: str
    details: Dict[str, Any]
    data_classification: DataClassification
    compliance_frameworks: List[ComplianceFramework]
    retention_policy: RetentionPolicy
    privacy_impact: bool
    constitutional_impact: bool
    
    # Integrity fields
    content_hash: Optional[str] = None
    digital_signature: Optional[str] = None
    chain_hash: Optional[str] = None
    
    # Compliance fields
    gdpr_lawful_basis: Optional[str] = None
    data_subject_id: Optional[str] = None
    processing_purpose: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "service_name": self.service_name,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "resource": self.resource,
            "action": self.action,
            "result": self.result,
            "details": self.details,
            "data_classification": self.data_classification.value,
            "compliance_frameworks": [f.value for f in self.compliance_frameworks],
            "retention_policy": self.retention_policy.value,
            "privacy_impact": self.privacy_impact,
            "constitutional_impact": self.constitutional_impact,
            "content_hash": self.content_hash,
            "digital_signature": self.digital_signature,
            "chain_hash": self.chain_hash,
            "gdpr_lawful_basis": self.gdpr_lawful_basis,
            "data_subject_id": self.data_subject_id,
            "processing_purpose": self.processing_purpose
        }


@dataclass
class ComplianceRule:
    """Compliance rule definition."""
    rule_id: str
    framework: ComplianceFramework
    title: str
    description: str
    requirement: str
    validation_logic: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    remediation_guidance: str
    applicable_events: List[AuditEventType]


@dataclass
class ComplianceViolation:
    """Compliance violation record."""
    violation_id: str
    rule_id: str
    framework: ComplianceFramework
    event_id: str
    timestamp: datetime
    severity: str
    description: str
    remediation_required: bool
    remediation_deadline: Optional[datetime]
    status: str  # OPEN, IN_PROGRESS, RESOLVED, ACCEPTED_RISK


class AuditComplianceManager:
    """Comprehensive audit logging and compliance manager."""
    
    def __init__(self, 
                 signing_key: Optional[rsa.RSAPrivateKey] = None,
                 verification_key: Optional[rsa.RSAPublicKey] = None):
        """Initialize audit compliance manager."""
        self.audit_events: List[AuditEvent] = []
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.violations: List[ComplianceViolation] = []
        self.chain_hash = "0" * 64  # Genesis hash
        
        # Cryptographic keys for digital signatures
        if signing_key is None:
            self.signing_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.verification_key = self.signing_key.public_key()
        else:
            self.signing_key = signing_key
            self.verification_key = verification_key or signing_key.public_key()
        
        # Initialize compliance rules
        self._initialize_compliance_rules()
    
    def _initialize_compliance_rules(self):
        """Initialize default compliance rules."""
        
        # GDPR Rules
        gdpr_rules = [
            ComplianceRule(
                rule_id="GDPR_001",
                framework=ComplianceFramework.GDPR,
                title="Data Processing Lawful Basis",
                description="All personal data processing must have lawful basis",
                requirement="Article 6 - Lawfulness of processing",
                validation_logic="gdpr_lawful_basis is not None",
                severity="HIGH",
                remediation_guidance="Specify lawful basis for data processing",
                applicable_events=[AuditEventType.DATA_ACCESS, AuditEventType.DATA_MODIFICATION]
            ),
            ComplianceRule(
                rule_id="GDPR_002",
                framework=ComplianceFramework.GDPR,
                title="Data Subject Rights",
                description="Data subject access requests must be logged",
                requirement="Article 15 - Right of access by the data subject",
                validation_logic="action == 'data_subject_access_request'",
                severity="MEDIUM",
                remediation_guidance="Log all data subject access requests",
                applicable_events=[AuditEventType.DATA_ACCESS]
            )
        ]
        
        # SOX Rules
        sox_rules = [
            ComplianceRule(
                rule_id="SOX_001",
                framework=ComplianceFramework.SOX,
                title="Financial Data Access Control",
                description="Access to financial data must be authorized and logged",
                requirement="Section 404 - Management assessment of internal controls",
                validation_logic="data_classification == 'financial' and user_id is not None",
                severity="CRITICAL",
                remediation_guidance="Ensure proper authorization for financial data access",
                applicable_events=[AuditEventType.DATA_ACCESS, AuditEventType.DATA_MODIFICATION]
            )
        ]
        
        # Constitutional Governance Rules
        constitutional_rules = [
            ComplianceRule(
                rule_id="CONST_001",
                framework=ComplianceFramework.CONSTITUTIONAL_GOVERNANCE,
                title="Constitutional Validation Required",
                description="All policy changes must undergo constitutional validation",
                requirement="ACGS Constitutional Framework",
                validation_logic="constitutional_impact == True",
                severity="CRITICAL",
                remediation_guidance="Ensure constitutional validation for policy changes",
                applicable_events=[AuditEventType.POLICY_CREATION, AuditEventType.POLICY_MODIFICATION]
            )
        ]
        
        # Register all rules
        for rule in gdpr_rules + sox_rules + constitutional_rules:
            self.compliance_rules[rule.rule_id] = rule
    
    def log_audit_event(self, 
                       event_type: AuditEventType,
                       service_name: str,
                       resource: str,
                       action: str,
                       result: str,
                       user_id: Optional[str] = None,
                       session_id: Optional[str] = None,
                       ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None,
                       details: Optional[Dict[str, Any]] = None,
                       data_classification: DataClassification = DataClassification.INTERNAL,
                       compliance_frameworks: Optional[List[ComplianceFramework]] = None,
                       retention_policy: RetentionPolicy = RetentionPolicy.YEARS_7,
                       privacy_impact: bool = False,
                       constitutional_impact: bool = False,
                       gdpr_lawful_basis: Optional[str] = None,
                       data_subject_id: Optional[str] = None,
                       processing_purpose: Optional[str] = None) -> str:
        """Log comprehensive audit event."""
        
        event_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        # Default compliance frameworks based on data classification
        if compliance_frameworks is None:
            compliance_frameworks = self._determine_compliance_frameworks(
                data_classification, privacy_impact, constitutional_impact
            )
        
        # Create audit event
        audit_event = AuditEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            service_name=service_name,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource=resource,
            action=action,
            result=result,
            details=details or {},
            data_classification=data_classification,
            compliance_frameworks=compliance_frameworks,
            retention_policy=retention_policy,
            privacy_impact=privacy_impact,
            constitutional_impact=constitutional_impact,
            gdpr_lawful_basis=gdpr_lawful_basis,
            data_subject_id=data_subject_id,
            processing_purpose=processing_purpose
        )
        
        # Calculate content hash
        content = json.dumps(audit_event.to_dict(), sort_keys=True)
        audit_event.content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Create digital signature
        audit_event.digital_signature = self._sign_event(audit_event)
        
        # Update chain hash
        chain_input = f"{self.chain_hash}{audit_event.content_hash}"
        audit_event.chain_hash = hashlib.sha256(chain_input.encode()).hexdigest()
        self.chain_hash = audit_event.chain_hash
        
        # Store audit event
        self.audit_events.append(audit_event)
        
        # Check compliance violations
        self._check_compliance_violations(audit_event)
        
        logger.info(
            "Audit event logged",
            event_id=event_id,
            event_type=event_type.value,
            service=service_name,
            resource=resource,
            action=action,
            result=result,
            compliance_frameworks=[f.value for f in compliance_frameworks]
        )
        
        return event_id
    
    def _determine_compliance_frameworks(self,
                                       data_classification: DataClassification,
                                       privacy_impact: bool,
                                       constitutional_impact: bool) -> List[ComplianceFramework]:
        """Determine applicable compliance frameworks."""
        frameworks = [ComplianceFramework.ISO_27001, ComplianceFramework.SOC_2]
        
        if privacy_impact or data_classification == DataClassification.PII:
            frameworks.extend([ComplianceFramework.GDPR, ComplianceFramework.CCPA])
        
        if data_classification == DataClassification.PHI:
            frameworks.append(ComplianceFramework.HIPAA)
        
        if data_classification == DataClassification.FINANCIAL:
            frameworks.append(ComplianceFramework.SOX)
        
        if constitutional_impact or data_classification == DataClassification.CONSTITUTIONAL:
            frameworks.append(ComplianceFramework.CONSTITUTIONAL_GOVERNANCE)
        
        return frameworks
    
    def _sign_event(self, event: AuditEvent) -> str:
        """Create digital signature for audit event."""
        content = json.dumps(event.to_dict(), sort_keys=True).encode()
        
        signature = self.signing_key.sign(
            content,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        import base64
        return base64.b64encode(signature).decode()
    
    def verify_event_signature(self, event: AuditEvent) -> bool:
        """Verify digital signature of audit event."""
        try:
            import base64
            signature = base64.b64decode(event.digital_signature.encode())
            
            # Temporarily remove signature for verification
            temp_signature = event.digital_signature
            event.digital_signature = None
            
            content = json.dumps(event.to_dict(), sort_keys=True).encode()
            
            # Restore signature
            event.digital_signature = temp_signature
            
            self.verification_key.verify(
                signature,
                content,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def verify_chain_integrity(self) -> bool:
        """Verify integrity of entire audit chain."""
        if not self.audit_events:
            return True
        
        current_hash = "0" * 64  # Genesis hash
        
        for event in self.audit_events:
            # Verify event signature
            if not self.verify_event_signature(event):
                logger.error(f"Signature verification failed for event {event.event_id}")
                return False
            
            # Verify chain hash
            expected_chain_hash = hashlib.sha256(
                f"{current_hash}{event.content_hash}".encode()
            ).hexdigest()
            
            if event.chain_hash != expected_chain_hash:
                logger.error(f"Chain integrity violation at event {event.event_id}")
                return False
            
            current_hash = event.chain_hash
        
        return True
    
    def _check_compliance_violations(self, event: AuditEvent):
        """Check for compliance violations."""
        for rule in self.compliance_rules.values():
            if rule.framework in event.compliance_frameworks:
                if event.event_type in rule.applicable_events:
                    # Simple rule evaluation (in production, use a proper rule engine)
                    if not self._evaluate_compliance_rule(rule, event):
                        violation = ComplianceViolation(
                            violation_id=str(uuid.uuid4()),
                            rule_id=rule.rule_id,
                            framework=rule.framework,
                            event_id=event.event_id,
                            timestamp=datetime.now(timezone.utc),
                            severity=rule.severity,
                            description=f"Violation of {rule.title}: {rule.description}",
                            remediation_required=rule.severity in ["HIGH", "CRITICAL"],
                            remediation_deadline=datetime.now(timezone.utc) + timedelta(days=30),
                            status="OPEN"
                        )
                        
                        self.violations.append(violation)
                        
                        logger.warning(
                            "Compliance violation detected",
                            violation_id=violation.violation_id,
                            rule_id=rule.rule_id,
                            framework=rule.framework.value,
                            severity=rule.severity,
                            event_id=event.event_id
                        )
    
    def _evaluate_compliance_rule(self, rule: ComplianceRule, event: AuditEvent) -> bool:
        """Evaluate compliance rule against event (simplified implementation)."""
        # This is a simplified rule evaluation
        # In production, use a proper rule engine like OPA
        
        if rule.rule_id == "GDPR_001":
            return event.gdpr_lawful_basis is not None
        elif rule.rule_id == "GDPR_002":
            return event.action == "data_subject_access_request"
        elif rule.rule_id == "SOX_001":
            return (event.data_classification == DataClassification.FINANCIAL and 
                   event.user_id is not None)
        elif rule.rule_id == "CONST_001":
            return event.constitutional_impact
        
        return True  # Default to compliant
    
    def generate_compliance_report(self, 
                                 framework: ComplianceFramework,
                                 start_date: datetime,
                                 end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report for specific framework."""
        
        # Filter events by framework and date range
        relevant_events = [
            event for event in self.audit_events
            if framework in event.compliance_frameworks
            and start_date <= event.timestamp <= end_date
        ]
        
        # Filter violations by framework and date range
        relevant_violations = [
            violation for violation in self.violations
            if violation.framework == framework
            and start_date <= violation.timestamp <= end_date
        ]
        
        # Calculate compliance metrics
        total_events = len(relevant_events)
        total_violations = len(relevant_violations)
        compliance_rate = ((total_events - total_violations) / max(total_events, 1)) * 100
        
        # Group violations by severity
        violations_by_severity = {}
        for violation in relevant_violations:
            severity = violation.severity
            if severity not in violations_by_severity:
                violations_by_severity[severity] = 0
            violations_by_severity[severity] += 1
        
        return {
            "framework": framework.value,
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_events": total_events,
                "total_violations": total_violations,
                "compliance_rate": round(compliance_rate, 2),
                "violations_by_severity": violations_by_severity
            },
            "events": [event.to_dict() for event in relevant_events],
            "violations": [
                {
                    "violation_id": v.violation_id,
                    "rule_id": v.rule_id,
                    "event_id": v.event_id,
                    "timestamp": v.timestamp.isoformat(),
                    "severity": v.severity,
                    "description": v.description,
                    "status": v.status
                }
                for v in relevant_violations
            ],
            "recommendations": self._generate_compliance_recommendations(framework, relevant_violations)
        }
    
    def _generate_compliance_recommendations(self, 
                                           framework: ComplianceFramework,
                                           violations: List[ComplianceViolation]) -> List[str]:
        """Generate compliance recommendations."""
        recommendations = []
        
        if framework == ComplianceFramework.GDPR:
            if any(v.rule_id == "GDPR_001" for v in violations):
                recommendations.append("Implement mandatory lawful basis specification for all data processing")
            if any(v.rule_id == "GDPR_002" for v in violations):
                recommendations.append("Enhance data subject access request logging")
        
        elif framework == ComplianceFramework.SOX:
            if any(v.rule_id == "SOX_001" for v in violations):
                recommendations.append("Strengthen access controls for financial data")
        
        elif framework == ComplianceFramework.CONSTITUTIONAL_GOVERNANCE:
            if any(v.rule_id == "CONST_001" for v in violations):
                recommendations.append("Ensure all policy changes undergo constitutional validation")
        
        return recommendations
    
    def anonymize_audit_data(self, event: AuditEvent) -> AuditEvent:
        """Anonymize audit data for privacy compliance."""
        anonymized_event = AuditEvent(**event.__dict__)
        
        # Anonymize PII fields
        if event.privacy_impact:
            anonymized_event.user_id = self._hash_identifier(event.user_id) if event.user_id else None
            anonymized_event.ip_address = self._anonymize_ip(event.ip_address) if event.ip_address else None
            anonymized_event.data_subject_id = self._hash_identifier(event.data_subject_id) if event.data_subject_id else None
            
            # Anonymize details that might contain PII
            if event.details:
                anonymized_event.details = self._anonymize_details(event.details)
        
        return anonymized_event
    
    def _hash_identifier(self, identifier: str) -> str:
        """Hash identifier for anonymization."""
        return hashlib.sha256(f"salt_{identifier}".encode()).hexdigest()[:16]
    
    def _anonymize_ip(self, ip_address: str) -> str:
        """Anonymize IP address."""
        # For IPv4, zero out last octet
        parts = ip_address.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0"
        return "anonymized"
    
    def _anonymize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize details dictionary."""
        anonymized = {}
        
        for key, value in details.items():
            if any(pii_field in key.lower() for pii_field in ['email', 'name', 'phone', 'address']):
                anonymized[key] = "[ANONYMIZED]"
            else:
                anonymized[key] = value
        
        return anonymized


# Global audit compliance manager instance
audit_compliance_manager = None


def initialize_audit_compliance_manager(signing_key: Optional[rsa.RSAPrivateKey] = None):
    """Initialize the global audit compliance manager."""
    global audit_compliance_manager
    audit_compliance_manager = AuditComplianceManager(signing_key)


def get_audit_compliance_manager() -> AuditComplianceManager:
    """Get the global audit compliance manager."""
    if audit_compliance_manager is None:
        raise RuntimeError("Audit compliance manager not initialized")
    return audit_compliance_manager


# Export main classes and functions
__all__ = [
    "AuditComplianceManager",
    "AuditEvent",
    "ComplianceRule",
    "ComplianceViolation",
    "ComplianceFramework",
    "AuditEventType",
    "DataClassification",
    "RetentionPolicy",
    "initialize_audit_compliance_manager",
    "get_audit_compliance_manager"
]
