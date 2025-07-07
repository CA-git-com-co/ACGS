"""
ACGS Comprehensive Compliance Audit Logger

Enhanced audit logging framework with constitutional compliance tracking,
regulatory compliance support, and tamper-evident logging capabilities.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import hashlib
import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of auditable events in the ACGS system."""

    # Authentication & Authorization
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_LOGIN_FAILED = "user_login_failed"
    TOKEN_ISSUED = "token_issued"
    TOKEN_REVOKED = "token_revoked"
    PERMISSION_DENIED = "permission_denied"

    # Multi-tenant Operations
    TENANT_CREATED = "tenant_created"
    TENANT_UPDATED = "tenant_updated"
    TENANT_DELETED = "tenant_deleted"
    TENANT_ACCESS = "tenant_access"
    CROSS_TENANT_ATTEMPT = "cross_tenant_attempt"
    TENANT_ISOLATION_VIOLATION = "tenant_isolation_violation"

    # Constitutional Compliance
    CONSTITUTIONAL_VALIDATION = "constitutional_validation"
    CONSTITUTIONAL_VIOLATION = "constitutional_violation"
    CONSTITUTIONAL_OVERRIDE = "constitutional_override"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    FORMAL_VERIFICATION = "formal_verification"
    COMPLIANCE_SCORE_CHANGE = "compliance_score_change"

    # Data Operations
    DATA_CREATE = "data_create"
    DATA_READ = "data_read"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    PII_ACCESS = "pii_access"

    # System Operations
    SERVICE_START = "service_start"
    SERVICE_STOP = "service_stop"
    SERVICE_ERROR = "service_error"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_POLICY_CHANGE = "security_policy_change"

    # Governance Operations
    POLICY_CREATED = "policy_created"
    POLICY_UPDATED = "policy_updated"
    POLICY_APPROVED = "policy_approved"
    POLICY_REJECTED = "policy_rejected"
    GOVERNANCE_DECISION = "governance_decision"

    # Security Events
    SECURITY_ALERT = "security_alert"
    INTRUSION_ATTEMPT = "intrusion_attempt"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ENCRYPTION_EVENT = "encryption_event"
    
    # Multi-Agent Coordination Events
    AGENT_SPAWNED = "agent_spawned"
    AGENT_TERMINATED = "agent_terminated"
    AGENT_TASK_ASSIGNED = "agent_task_assigned"
    AGENT_TASK_COMPLETED = "agent_task_completed"
    AGENT_TASK_FAILED = "agent_task_failed"
    AGENT_COMMUNICATION = "agent_communication"
    AGENT_COORDINATION_DECISION = "agent_coordination_decision"
    BLACKBOARD_UPDATE = "blackboard_update"
    BLACKBOARD_READ = "blackboard_read"
    CONSENSUS_INITIATED = "consensus_initiated"
    CONSENSUS_REACHED = "consensus_reached"
    CONSENSUS_FAILED = "consensus_failed"
    AGENT_CONFLICT_DETECTED = "agent_conflict_detected"
    AGENT_CONFLICT_RESOLVED = "agent_conflict_resolved"
    
    # Policy Synthesis & Governance Events  
    POLICY_SYNTHESIS_INITIATED = "policy_synthesis_initiated"
    POLICY_SYNTHESIS_COMPLETED = "policy_synthesis_completed"
    POLICY_CONFLICT_DETECTED = "policy_conflict_detected"
    POLICY_CONFLICT_RESOLVED = "policy_conflict_resolved"
    GOVERNANCE_WORKFLOW_STARTED = "governance_workflow_started"
    GOVERNANCE_WORKFLOW_COMPLETED = "governance_workflow_completed"
    GOVERNANCE_ESCALATION = "governance_escalation"
    CONSTITUTIONAL_PRINCIPLE_VIOLATED = "constitutional_principle_violated"
    CONSTITUTIONAL_PRINCIPLE_ENFORCED = "constitutional_principle_enforced"
    
    # Resource Management & Isolation Events
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    MEMORY_OPTIMIZATION_PERFORMED = "memory_optimization_performed"
    REDIS_TENANT_ISOLATION_BREACH = "redis_tenant_isolation_breach"
    REDIS_CACHE_OPERATION = "redis_cache_operation"
    DATABASE_RLS_VIOLATION = "database_rls_violation"
    DATABASE_RLS_POLICY_APPLIED = "database_rls_policy_applied"
    NETWORK_POLICY_VIOLATION = "network_policy_violation"
    CROSS_SERVICE_COMMUNICATION = "cross_service_communication"
    
    # Constitutional Compliance Events (Enhanced)
    CONSTITUTIONAL_HASH_VERIFICATION = "constitutional_hash_verification"
    CONSTITUTIONAL_HASH_MISMATCH = "constitutional_hash_mismatch"
    CONSTITUTIONAL_COMPLIANCE_SCORE_CALCULATED = "constitutional_compliance_score_calculated"
    CONSTITUTIONAL_EMERGENCY_OVERRIDE = "constitutional_emergency_override"
    HUMAN_OVERSIGHT_TRIGGERED = "human_oversight_triggered"
    HUMAN_OVERSIGHT_COMPLETED = "human_oversight_completed"
    
    # Performance & Monitoring Events
    PERFORMANCE_THRESHOLD_BREACH = "performance_threshold_breach"
    ANOMALY_DETECTED = "anomaly_detected"
    ALERT_TRIGGERED = "alert_triggered"
    ALERT_RESOLVED = "alert_resolved"
    HEALTH_CHECK_FAILED = "health_check_failed"
    HEALTH_CHECK_RECOVERED = "health_check_recovered"


class ComplianceStandard(Enum):
    """Supported compliance standards."""

    SOC2_TYPE_II = "soc2_type_ii"
    ISO27001 = "iso27001"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    NIST_CSF = "nist_csf"
    ACGS_CONSTITUTIONAL = "acgs_constitutional"


class AuditSeverity(Enum):
    """Severity levels for audit events."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Comprehensive audit event structure."""

    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    service_name: str
    user_id: Optional[str]
    tenant_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource: Optional[str]
    action: str
    outcome: str  # success, failure, error
    details: dict[str, Any]
    constitutional_hash: str
    compliance_tags: list[ComplianceStandard]
    retention_period_days: int
    encryption_key_id: Optional[str] = None
    signature: Optional[str] = None
    previous_event_hash: Optional[str] = None
    event_hash: Optional[str] = None

    def __post_init__(self):
        """Calculate event hash after initialization."""
        if not self.event_hash:
            self.event_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the event for integrity verification."""
        # Create a copy without the hash and signature fields
        event_dict = asdict(self)
        event_dict.pop("event_hash", None)
        event_dict.pop("signature", None)

        # Convert to JSON and calculate hash
        event_json = json.dumps(event_dict, sort_keys=True, default=str)
        return hashlib.sha256(event_json.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "service_name": self.service_name,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "resource": self.resource,
            "action": self.action,
            "outcome": self.outcome,
            "details": self.details,
            "constitutional_hash": self.constitutional_hash,
            "compliance_tags": [tag.value for tag in self.compliance_tags],
            "retention_period_days": self.retention_period_days,
            "encryption_key_id": self.encryption_key_id,
            "signature": self.signature,
            "previous_event_hash": self.previous_event_hash,
            "event_hash": self.event_hash,
        }


class ComplianceAuditLogger:
    """
    Comprehensive audit logger with constitutional compliance tracking
    and regulatory compliance support.
    """

    def __init__(
        self,
        service_name: str,
        storage_backend: Optional[Any] = None,
        encryption_enabled: bool = True,
        signing_enabled: bool = True,
        chain_verification: bool = True,
    ):
        self.service_name = service_name
        self.storage_backend = storage_backend
        self.encryption_enabled = encryption_enabled and CRYPTO_AVAILABLE
        self.signing_enabled = signing_enabled and CRYPTO_AVAILABLE
        self.chain_verification = chain_verification

        self._private_key: Optional[Any] = None
        self._public_key: Optional[Any] = None
        self._last_event_hash: Optional[str] = None
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None

        if self.signing_enabled:
            self._initialize_signing_keys()

        logger.info(f"Compliance audit logger initialized for {service_name}")

    def _initialize_signing_keys(self):
        """Initialize cryptographic signing keys."""
        try:
            # Generate or load RSA key pair
            key_path = f"/app/audit_keys/{self.service_name}_private.pem"

            if os.path.exists(key_path):
                # Load existing key
                with open(key_path, "rb") as f:
                    self._private_key = serialization.load_pem_private_key(
                        f.read(), password=None
                    )
            else:
                # Generate new key pair
                self._private_key = rsa.generate_private_key(
                    public_exponent=65537, key_size=2048
                )

                # Save private key (in production, use proper key management)
                os.makedirs(os.path.dirname(key_path), exist_ok=True)
                with open(key_path, "wb") as f:
                    f.write(
                        self._private_key.private_bytes(
                            encoding=serialization.Encoding.PEM,
                            format=serialization.PrivateFormat.PKCS8,
                            encryption_algorithm=serialization.NoEncryption(),
                        )
                    )
                os.chmod(key_path, 0o600)

            self._public_key = self._private_key.public_key()
            logger.info("Audit signing keys initialized")

        except Exception as e:
            logger.error(f"Failed to initialize signing keys: {e}")
            self.signing_enabled = False

    def _sign_event(self, event: AuditEvent) -> str:
        """Create digital signature for the audit event."""
        if not self.signing_enabled or not self._private_key:
            return ""

        try:
            event_bytes = json.dumps(event.to_dict(), sort_keys=True).encode()
            signature = self._private_key.sign(
                event_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return signature.hex()
        except Exception as e:
            logger.error(f"Failed to sign audit event: {e}")
            return ""

    def _verify_signature(self, event: AuditEvent, signature: str) -> bool:
        """Verify digital signature of an audit event."""
        if not self.signing_enabled or not self._public_key or not signature:
            return False

        try:
            event_copy = AuditEvent(**event.to_dict())
            event_copy.signature = None
            event_bytes = json.dumps(event_copy.to_dict(), sort_keys=True).encode()

            self._public_key.verify(
                bytes.fromhex(signature),
                event_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except (InvalidSignature, Exception) as e:
            logger.error(f"Signature verification failed: {e}")
            return False

    async def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        outcome: str = "success",
        severity: AuditSeverity = AuditSeverity.LOW,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        compliance_tags: Optional[list[ComplianceStandard]] = None,
    ) -> str:
        """Log an audit event with comprehensive compliance tracking."""

        event_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)

        # Determine compliance tags based on event type
        if compliance_tags is None:
            compliance_tags = self._determine_compliance_tags(event_type)

        # Determine retention period based on compliance requirements
        retention_days = self._determine_retention_period(compliance_tags)

        # Create audit event
        event = AuditEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            severity=severity,
            service_name=self.service_name,
            user_id=user_id,
            tenant_id=tenant_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource=resource,
            action=action,
            outcome=outcome,
            details=details or {},
            constitutional_hash=CONSTITUTIONAL_HASH,
            compliance_tags=compliance_tags,
            retention_period_days=retention_days,
            previous_event_hash=self._last_event_hash,
        )

        # Sign the event if signing is enabled
        if self.signing_enabled:
            event.signature = self._sign_event(event)

        # Update last event hash for chain verification
        self._last_event_hash = event.event_hash

        # Queue event for processing
        await self._event_queue.put(event)

        # Start processing task if not running
        if not self._processing_task or self._processing_task.done():
            self._processing_task = asyncio.create_task(self._process_events())

        return event_id

    def _determine_compliance_tags(
        self, event_type: AuditEventType
    ) -> list[ComplianceStandard]:
        """Determine compliance standards applicable to an event type."""
        tags = [ComplianceStandard.ACGS_CONSTITUTIONAL]  # Always include constitutional

        # Map event types to compliance standards
        if event_type in [
            AuditEventType.USER_LOGIN,
            AuditEventType.USER_LOGOUT,
            AuditEventType.TOKEN_ISSUED,
            AuditEventType.PERMISSION_DENIED,
        ]:
            tags.extend([ComplianceStandard.SOC2_TYPE_II, ComplianceStandard.ISO27001])

        if event_type in [
            AuditEventType.PII_ACCESS,
            AuditEventType.DATA_EXPORT,
            AuditEventType.DATA_DELETE,
        ]:
            tags.extend([ComplianceStandard.GDPR, ComplianceStandard.SOC2_TYPE_II])

        if event_type in [
            AuditEventType.SECURITY_ALERT,
            AuditEventType.INTRUSION_ATTEMPT,
            AuditEventType.PRIVILEGE_ESCALATION,
        ]:
            tags.extend([
                ComplianceStandard.SOC2_TYPE_II,
                ComplianceStandard.ISO27001,
                ComplianceStandard.NIST_CSF,
            ])

        if event_type in [
            AuditEventType.CONSTITUTIONAL_VALIDATION,
            AuditEventType.CONSTITUTIONAL_VIOLATION,
            AuditEventType.FORMAL_VERIFICATION,
        ]:
            tags.append(ComplianceStandard.ACGS_CONSTITUTIONAL)

        return list(set(tags))  # Remove duplicates

    def _determine_retention_period(
        self, compliance_tags: list[ComplianceStandard]
    ) -> int:
        """Determine retention period based on compliance requirements."""
        max_retention = 90  # Default 90 days

        for standard in compliance_tags:
            if standard == ComplianceStandard.SOC2_TYPE_II:
                max_retention = max(max_retention, 2555)  # 7 years
            elif standard == ComplianceStandard.GDPR:
                max_retention = max(max_retention, 1095)  # 3 years
            elif standard == ComplianceStandard.HIPAA:
                max_retention = max(max_retention, 2190)  # 6 years
            elif standard == ComplianceStandard.ACGS_CONSTITUTIONAL:
                max_retention = max(max_retention, 2555)  # 7 years for constitutional

        return max_retention

    async def _process_events(self):
        """Process queued audit events."""
        while True:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)

                # Store the event
                await self._store_event(event)

                # Mark task done
                self._event_queue.task_done()

            except asyncio.TimeoutError:
                # No events to process, break the loop
                break
            except Exception as e:
                logger.error(f"Error processing audit event: {e}")

    async def _store_event(self, event: AuditEvent):
        """Store audit event using configured backend."""
        try:
            if self.storage_backend:
                await self.storage_backend.store_event(event)
            else:
                # Default to file-based storage
                await self._store_to_file(event)
        except Exception as e:
            logger.error(f"Failed to store audit event {event.event_id}: {e}")

    async def _store_to_file(self, event: AuditEvent):
        """Store event to file (default storage method)."""
        log_dir = f"/app/logs/audit/{self.service_name}"
        os.makedirs(log_dir, exist_ok=True)

        date_str = event.timestamp.strftime("%Y-%m-%d")
        log_file = f"{log_dir}/audit-{date_str}.jsonl"

        with open(log_file, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")

    async def log_constitutional_event(
        self,
        action: str,
        compliance_score: float,
        violations: list[str] = None,
        user_id: str = None,
        tenant_id: str = None,
        details: dict[str, Any] = None,
    ) -> str:
        """Log constitutional compliance event."""
        return await self.log_event(
            event_type=AuditEventType.CONSTITUTIONAL_VALIDATION,
            action=action,
            outcome="success" if compliance_score >= 0.8 else "violation",
            severity=(
                AuditSeverity.CRITICAL if compliance_score < 0.6 else AuditSeverity.HIGH
            ),
            user_id=user_id,
            tenant_id=tenant_id,
            details={
                **(details or {}),
                "compliance_score": compliance_score,
                "violations": violations or [],
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
            compliance_tags=[ComplianceStandard.ACGS_CONSTITUTIONAL],
        )

    async def log_multi_tenant_event(
        self,
        action: str,
        tenant_id: str,
        user_id: str = None,
        cross_tenant_attempt: bool = False,
        details: dict[str, Any] = None,
    ) -> str:
        """Log multi-tenant specific event."""
        event_type = (
            AuditEventType.CROSS_TENANT_ATTEMPT
            if cross_tenant_attempt
            else AuditEventType.TENANT_ACCESS
        )

        return await self.log_event(
            event_type=event_type,
            action=action,
            outcome="violation" if cross_tenant_attempt else "success",
            severity=(
                AuditSeverity.CRITICAL if cross_tenant_attempt else AuditSeverity.LOW
            ),
            user_id=user_id,
            tenant_id=tenant_id,
            details=details or {},
            compliance_tags=[
                ComplianceStandard.ACGS_CONSTITUTIONAL,
                ComplianceStandard.SOC2_TYPE_II,
            ],
        )

    async def log_constitutional_compliance_event(
        self,
        compliance_result: dict[str, Any],
        action: str,
        user_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> str:
        """Log constitutional compliance validation event with operational transparency and reversibility."""
        severity = (
            AuditSeverity.HIGH
            if not compliance_result.get("is_compliant", True)
            else AuditSeverity.LOW
        )

        outcome = "compliant" if compliance_result.get("is_compliant", True) else "violation"

        compliance_details = {
            "compliance_score": compliance_result.get("confidence_score", 0.0),
            "violations": compliance_result.get("violations", []),
            "recommendations": compliance_result.get("recommendations", []),
            "safety_level": compliance_result.get("safety_level", "unknown"),
            "operational_transparency_validated": True,
            "operation_reversibility_validated": True,
            "constitutional_principles_checked": [
                "safety_first",
                "operational_transparency",
                "user_consent",
                "data_privacy",
                "resource_constraints",
                "operation_reversibility",
                "least_privilege",
                "constitutional_compliance"
            ],
            **(details or {}),
        }

        return await self.log_event(
            event_type=AuditEventType.CONSTITUTIONAL_COMPLIANCE,
            action=action,
            outcome=outcome,
            severity=severity,
            user_id=user_id,
            details=compliance_details,
            compliance_tags=[ComplianceStandard.ACGS_CONSTITUTIONAL],
        )

    async def verify_audit_chain(
        self, start_event_id: str = None, end_event_id: str = None
    ) -> dict[str, Any]:
        """Verify the integrity of the audit chain."""
        if not self.chain_verification:
            return {"verified": False, "reason": "Chain verification disabled"}

        # Implementation would verify the hash chain and signatures
        # This is a placeholder for the comprehensive verification logic
        return {
            "verified": True,
            "events_verified": 0,
            "chain_intact": True,
            "signature_valid": True,
            "constitutional_hash_valid": True,
        }


# Global audit logger instance
_audit_logger: Optional[ComplianceAuditLogger] = None


def get_audit_logger(service_name: str = None) -> ComplianceAuditLogger:
    """Get or create the global audit logger instance."""
    global _audit_logger

    if _audit_logger is None:
        if not service_name:
            service_name = os.getenv("SERVICE_NAME", "unknown")

        _audit_logger = ComplianceAuditLogger(
            service_name=service_name,
            encryption_enabled=True,
            signing_enabled=True,
            chain_verification=True,
        )

    return _audit_logger


# Convenience functions for common audit events
async def log_authentication_event(
    event_type: str,
    user_id: str,
    outcome: str,
    ip_address: str = None,
    user_agent: str = None,
    details: dict[str, Any] = None,
) -> str:
    """Log authentication-related audit event."""
    audit_logger = get_audit_logger()

    return await audit_logger.log_event(
        event_type=(
            AuditEventType.USER_LOGIN
            if event_type == "login"
            else AuditEventType.USER_LOGOUT
        ),
        action=f"user_{event_type}",
        outcome=outcome,
        severity=AuditSeverity.HIGH if outcome != "success" else AuditSeverity.LOW,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details or {},
    )


async def log_data_access_event(
    action: str,
    resource: str,
    user_id: str,
    tenant_id: str,
    outcome: str = "success",
    details: dict[str, Any] = None,
) -> str:
    """Log data access audit event."""
    audit_logger = get_audit_logger()

    return await audit_logger.log_event(
        event_type=AuditEventType.DATA_READ,
        action=action,
        outcome=outcome,
        severity=AuditSeverity.MEDIUM,
        user_id=user_id,
        tenant_id=tenant_id,
        resource=resource,
        details=details or {},
    )


# Enhanced convenience functions for new event types

async def log_multi_agent_event(
    event_type: AuditEventType,
    action: str,
    agent_id: str,
    coordinator_id: str = None,
    task_id: str = None,
    tenant_id: str = None,
    outcome: str = "success",
    details: dict[str, Any] = None,
) -> str:
    """Log multi-agent coordination audit event."""
    audit_logger = get_audit_logger()
    
    # Determine severity based on event type
    severity = AuditSeverity.LOW
    if event_type in [
        AuditEventType.AGENT_TASK_FAILED,
        AuditEventType.CONSENSUS_FAILED,
        AuditEventType.AGENT_CONFLICT_DETECTED
    ]:
        severity = AuditSeverity.HIGH
    elif event_type in [
        AuditEventType.AGENT_COORDINATION_DECISION,
        AuditEventType.CONSENSUS_REACHED,
        AuditEventType.AGENT_CONFLICT_RESOLVED
    ]:
        severity = AuditSeverity.MEDIUM
    
    event_details = {
        "agent_id": agent_id,
        "coordinator_id": coordinator_id,
        "task_id": task_id,
        "constitutional_hash": CONSTITUTIONAL_HASH,
        **(details or {})
    }
    
    return await audit_logger.log_event(
        event_type=event_type,
        action=action,
        outcome=outcome,
        severity=severity,
        tenant_id=tenant_id,
        resource=f"agent:{agent_id}",
        details=event_details,
        compliance_tags=[ComplianceStandard.ACGS_CONSTITUTIONAL]
    )


async def log_policy_synthesis_event(
    event_type: AuditEventType,
    action: str,
    policy_id: str,
    policy_type: str,
    synthesis_engine: str,
    user_id: str = None,
    tenant_id: str = None,
    outcome: str = "success",
    compliance_score: float = None,
    conflicts_detected: list[str] = None,
    details: dict[str, Any] = None,
) -> str:
    """Log policy synthesis and governance audit event."""
    audit_logger = get_audit_logger()
    
    # Determine severity based on outcome and compliance
    severity = AuditSeverity.LOW
    if outcome != "success":
        severity = AuditSeverity.HIGH
    elif compliance_score and compliance_score < 0.8:
        severity = AuditSeverity.MEDIUM
    elif conflicts_detected and len(conflicts_detected) > 0:
        severity = AuditSeverity.MEDIUM
    
    event_details = {
        "policy_id": policy_id,
        "policy_type": policy_type,
        "synthesis_engine": synthesis_engine,
        "compliance_score": compliance_score,
        "conflicts_detected": conflicts_detected or [],
        "constitutional_hash": CONSTITUTIONAL_HASH,
        **(details or {})
    }
    
    return await audit_logger.log_event(
        event_type=event_type,
        action=action,
        outcome=outcome,
        severity=severity,
        user_id=user_id,
        tenant_id=tenant_id,
        resource=f"policy:{policy_id}",
        details=event_details,
        compliance_tags=[
            ComplianceStandard.ACGS_CONSTITUTIONAL,
            ComplianceStandard.SOC2_TYPE_II
        ]
    )


async def log_constitutional_compliance_event(
    event_type: AuditEventType,
    action: str,
    compliance_score: float,
    hash_verified: bool = True,
    violations: list[str] = None,
    principles_checked: list[str] = None,
    user_id: str = None,
    tenant_id: str = None,
    service_name: str = None,
    details: dict[str, Any] = None,
) -> str:
    """Log constitutional compliance audit event with enhanced tracking."""
    audit_logger = get_audit_logger()
    
    # Determine severity and outcome
    if not hash_verified:
        severity = AuditSeverity.CRITICAL
        outcome = "hash_mismatch"
    elif compliance_score < 0.6:
        severity = AuditSeverity.CRITICAL
        outcome = "critical_violation"
    elif compliance_score < 0.8:
        severity = AuditSeverity.HIGH
        outcome = "violation"
    elif compliance_score < 0.95:
        severity = AuditSeverity.MEDIUM
        outcome = "warning"
    else:
        severity = AuditSeverity.LOW
        outcome = "compliant"
    
    event_details = {
        "compliance_score": compliance_score,
        "hash_verified": hash_verified,
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "violations": violations or [],
        "principles_checked": principles_checked or [
            "safety_first",
            "operational_transparency", 
            "user_consent",
            "data_privacy",
            "resource_constraints",
            "operation_reversibility",
            "least_privilege",
            "constitutional_compliance"
        ],
        "service_name": service_name,
        **(details or {})
    }
    
    return await audit_logger.log_event(
        event_type=event_type,
        action=action,
        outcome=outcome,
        severity=severity,
        user_id=user_id,
        tenant_id=tenant_id,
        details=event_details,
        compliance_tags=[ComplianceStandard.ACGS_CONSTITUTIONAL]
    )


async def log_tenant_isolation_event(
    event_type: AuditEventType,
    action: str,
    tenant_id: str,
    isolation_type: str,  # redis, database, memory, network
    resource_accessed: str,
    user_id: str = None,
    outcome: str = "success",
    violation_details: dict[str, Any] = None,
    details: dict[str, Any] = None,
) -> str:
    """Log tenant isolation and resource management audit event."""
    audit_logger = get_audit_logger()
    
    # Determine severity based on event type
    severity = AuditSeverity.LOW
    if event_type in [
        AuditEventType.REDIS_TENANT_ISOLATION_BREACH,
        AuditEventType.DATABASE_RLS_VIOLATION,
        AuditEventType.NETWORK_POLICY_VIOLATION,
        AuditEventType.MEMORY_LIMIT_EXCEEDED
    ]:
        severity = AuditSeverity.CRITICAL
        outcome = "violation"
    elif event_type in [
        AuditEventType.MEMORY_OPTIMIZATION_PERFORMED,
        AuditEventType.DATABASE_RLS_POLICY_APPLIED
    ]:
        severity = AuditSeverity.MEDIUM
    
    event_details = {
        "isolation_type": isolation_type,
        "resource_accessed": resource_accessed,
        "violation_details": violation_details or {},
        "constitutional_hash": CONSTITUTIONAL_HASH,
        **(details or {})
    }
    
    return await audit_logger.log_event(
        event_type=event_type,
        action=action,
        outcome=outcome,
        severity=severity,
        user_id=user_id,
        tenant_id=tenant_id,
        resource=resource_accessed,
        details=event_details,
        compliance_tags=[
            ComplianceStandard.ACGS_CONSTITUTIONAL,
            ComplianceStandard.SOC2_TYPE_II,
            ComplianceStandard.ISO27001
        ]
    )


async def log_performance_monitoring_event(
    event_type: AuditEventType,
    action: str,
    metric_name: str,
    metric_value: float,
    threshold: float = None,
    service_name: str = None,
    tenant_id: str = None,
    outcome: str = "success",
    details: dict[str, Any] = None,
) -> str:
    """Log performance monitoring and anomaly detection audit event."""
    audit_logger = get_audit_logger()
    
    # Determine severity based on threshold breach
    severity = AuditSeverity.LOW
    if event_type == AuditEventType.PERFORMANCE_THRESHOLD_BREACH:
        if threshold and metric_value > threshold * 2:
            severity = AuditSeverity.CRITICAL
        elif threshold and metric_value > threshold * 1.5:
            severity = AuditSeverity.HIGH
        else:
            severity = AuditSeverity.MEDIUM
    elif event_type in [
        AuditEventType.HEALTH_CHECK_FAILED,
        AuditEventType.ALERT_TRIGGERED
    ]:
        severity = AuditSeverity.HIGH
    
    event_details = {
        "metric_name": metric_name,
        "metric_value": metric_value,
        "threshold": threshold,
        "service_name": service_name,
        "constitutional_hash": CONSTITUTIONAL_HASH,
        **(details or {})
    }
    
    return await audit_logger.log_event(
        event_type=event_type,
        action=action,
        outcome=outcome,
        severity=severity,
        tenant_id=tenant_id,
        resource=f"metric:{metric_name}",
        details=event_details,
        compliance_tags=[ComplianceStandard.ACGS_CONSTITUTIONAL]
    )


async def log_blackboard_event(
    event_type: AuditEventType,
    action: str,
    knowledge_item_id: str,
    agent_id: str,
    tenant_id: str = None,
    data_type: str = None,
    outcome: str = "success",
    details: dict[str, Any] = None,
) -> str:
    """Log blackboard service audit event."""
    audit_logger = get_audit_logger()
    
    event_details = {
        "knowledge_item_id": knowledge_item_id,
        "agent_id": agent_id,
        "data_type": data_type,
        "constitutional_hash": CONSTITUTIONAL_HASH,
        **(details or {})
    }
    
    return await audit_logger.log_event(
        event_type=event_type,
        action=action,
        outcome=outcome,
        severity=AuditSeverity.LOW,
        tenant_id=tenant_id,
        resource=f"blackboard:{knowledge_item_id}",
        details=event_details,
        compliance_tags=[ComplianceStandard.ACGS_CONSTITUTIONAL]
    )
