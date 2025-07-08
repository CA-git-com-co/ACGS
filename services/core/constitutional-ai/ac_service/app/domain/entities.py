"""
Domain Entities for Constitutional AI Service
Constitutional Hash: cdd01ef066bc6cf2

This module contains the core domain entities that represent the business logic
and rules of the constitutional AI system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ViolationType(Enum):
    """Types of constitutional violations."""
    CONTENT_HARMFUL = "content_harmful"
    BIAS_DETECTED = "bias_detected"
    PRIVACY_VIOLATION = "privacy_violation"
    CONSTITUTIONAL_BREACH = "constitutional_breach"
    ETHICAL_VIOLATION = "ethical_violation"
    POLICY_VIOLATION = "policy_violation"


class ComplianceLevel(Enum):
    """Levels of constitutional compliance."""
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_REVIEW = "requires_review"


@dataclass
class ConstitutionalViolation:
    """Represents a constitutional violation."""

    violation_id: str = field(default_factory=lambda: str(uuid4()))
    violation_type: ViolationType = ViolationType.CONSTITUTIONAL_BREACH
    severity: float = 0.0  # 0.0 to 1.0
    description: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.utcnow)
    constitutional_hash: str = CONSTITUTIONAL_HASH

    def __post_init__(self):
        """Validate violation data."""
        if not 0.0 <= self.severity <= 1.0:
            raise ValueError("Severity must be between 0.0 and 1.0")
        if not self.description:
            raise ValueError("Description cannot be empty")


@dataclass
class ValidationResult:
    """Result of constitutional validation."""

    result_id: str = field(default_factory=lambda: str(uuid4()))
    is_valid: bool = False
    compliance_score: float = 0.0  # 0.0 to 1.0
    compliance_level: ComplianceLevel = ComplianceLevel.NON_COMPLIANT
    violations: list[ConstitutionalViolation] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    validated_at: datetime = field(default_factory=datetime.utcnow)
    constitutional_hash: str = CONSTITUTIONAL_HASH

    def __post_init__(self):
        """Validate result data."""
        if not 0.0 <= self.compliance_score <= 1.0:
            raise ValueError("Compliance score must be between 0.0 and 1.0")

        # Auto-determine compliance level based on score
        if self.compliance_score >= 0.95:
            self.compliance_level = ComplianceLevel.COMPLIANT
        elif self.compliance_score >= 0.75:
            self.compliance_level = ComplianceLevel.PARTIALLY_COMPLIANT
        elif self.compliance_score >= 0.50:
            self.compliance_level = ComplianceLevel.REQUIRES_REVIEW
        else:
            self.compliance_level = ComplianceLevel.NON_COMPLIANT

    def add_violation(self, violation: ConstitutionalViolation):
        """Add a violation to the result."""
        self.violations.append(violation)
        self.is_valid = False
        # Recalculate compliance score
        self._recalculate_compliance_score()

    def add_recommendation(self, recommendation: str):
        """Add a recommendation to the result."""
        if recommendation and recommendation not in self.recommendations:
            self.recommendations.append(recommendation)

    def _recalculate_compliance_score(self):
        """Recalculate compliance score based on violations."""
        if not self.violations:
            self.compliance_score = 1.0
            return

        # Calculate weighted penalty based on violation severity
        total_penalty = sum(v.severity for v in self.violations)
        max_penalty = len(self.violations)  # If all violations were severity 1.0

        if max_penalty > 0:
            penalty_ratio = min(total_penalty / max_penalty, 1.0)
            self.compliance_score = max(0.0, 1.0 - penalty_ratio)
        else:
            self.compliance_score = 1.0


@dataclass
class ContentValidationRequest:
    """Request for content validation."""

    request_id: str = field(default_factory=lambda: str(uuid4()))
    content: str = ""
    content_type: str = "text"
    validation_rules: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    requester_id: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    constitutional_hash: str = CONSTITUTIONAL_HASH

    def __post_init__(self):
        """Validate request data."""
        if not self.content.strip():
            raise ValueError("Content cannot be empty")
        if not self.content_type:
            raise ValueError("Content type must be specified")


@dataclass
class ConstitutionalComplianceRequest:
    """Request for constitutional compliance validation."""

    request_id: str = field(default_factory=lambda: str(uuid4()))
    content: str = ""
    policy_context: dict[str, Any] = field(default_factory=dict)
    validation_scope: list[str] = field(default_factory=list)
    strict_mode: bool = True
    requester_id: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    constitutional_hash: str = CONSTITUTIONAL_HASH

    def __post_init__(self):
        """Validate request data."""
        if not self.content.strip():
            raise ValueError("Content cannot be empty")


class ConstitutionalValidator(ABC):
    """Abstract base class for constitutional validators."""

    @abstractmethod
    async def validate_content(self, request: ContentValidationRequest) -> ValidationResult:
        """Validate content against constitutional rules."""

    @abstractmethod
    async def validate_compliance(self, request: ConstitutionalComplianceRequest) -> ValidationResult:
        """Validate constitutional compliance."""

    @abstractmethod
    def validate_constitutional_hash(self) -> dict[str, Any]:
        """Validate constitutional hash integrity."""


@dataclass
class ConstitutionalPrinciple:
    """Represents a constitutional principle."""

    principle_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    priority: float = 1.0  # Higher values = higher priority
    rules: list[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    constitutional_hash: str = CONSTITUTIONAL_HASH

    def __post_init__(self):
        """Validate principle data."""
        if not self.name.strip():
            raise ValueError("Principle name cannot be empty")
        if not self.description.strip():
            raise ValueError("Principle description cannot be empty")
        if self.priority <= 0:
            raise ValueError("Priority must be positive")


@dataclass
class AuditEvent:
    """Represents an audit event in the constitutional system."""

    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: str = ""
    entity_type: str = ""
    entity_id: str = ""
    action: str = ""
    actor_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    constitutional_hash: str = CONSTITUTIONAL_HASH

    def __post_init__(self):
        """Validate audit event data."""
        if not self.event_type:
            raise ValueError("Event type cannot be empty")
        if not self.entity_type:
            raise ValueError("Entity type cannot be empty")
        if not self.action:
            raise ValueError("Action cannot be empty")


@dataclass
class PolicyDecision:
    """Represents a policy decision made by the constitutional system."""

    decision_id: str = field(default_factory=lambda: str(uuid4()))
    policy_id: str = ""
    decision: str = ""  # "allow", "deny", "review"
    confidence: float = 0.0  # 0.0 to 1.0
    reasoning: list[str] = field(default_factory=list)
    applied_principles: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    decided_at: datetime = field(default_factory=datetime.utcnow)
    constitutional_hash: str = CONSTITUTIONAL_HASH

    def __post_init__(self):
        """Validate policy decision data."""
        if not self.policy_id:
            raise ValueError("Policy ID cannot be empty")
        if self.decision not in ["allow", "deny", "review"]:
            raise ValueError("Decision must be 'allow', 'deny', or 'review'")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


# Domain Services (interfaces)
class ConstitutionalPolicyService(ABC):
    """Abstract service for constitutional policy management."""

    @abstractmethod
    async def evaluate_policy(self, content: str, context: dict[str, Any]) -> PolicyDecision:
        """Evaluate content against constitutional policies."""

    @abstractmethod
    async def get_applicable_principles(self, context: dict[str, Any]) -> list[ConstitutionalPrinciple]:
        """Get constitutional principles applicable to the given context."""


class AuditService(ABC):
    """Abstract service for audit logging."""

    @abstractmethod
    async def log_event(self, event: AuditEvent) -> None:
        """Log an audit event."""

    @abstractmethod
    async def get_audit_trail(self, entity_id: str) -> list[AuditEvent]:
        """Get audit trail for an entity."""
