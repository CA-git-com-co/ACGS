"""
Policy Management Value Objects
Constitutional Hash: cdd01ef066bc6cf2

Value objects for policy management domain with immutable data structures
and constitutional compliance validation.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from services.shared.domain.base import CONSTITUTIONAL_HASH, ValueObject


class PolicyStatus(str, Enum):
    """Status of a policy in its lifecycle."""
    
    DRAFT = "draft"
    REVIEW = "review"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ComplianceLevel(str, Enum):
    """Levels of compliance evaluation."""
    
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"


class PolicyType(str, Enum):
    """Types of policies in the system."""
    
    GOVERNANCE = "governance"
    SECURITY = "security"
    OPERATIONAL = "operational"
    CONSTITUTIONAL = "constitutional"
    COMPLIANCE = "compliance"


class ViolationSeverity(str, Enum):
    """Severity levels for policy violations."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass(frozen=True)
class PolicyScope(ValueObject):
    """Defines the scope and applicability of a policy."""
    
    domains: list[str]
    systems: list[str]
    user_groups: list[str]
    geographic_regions: list[str]
    effective_date: datetime
    expiration_date: datetime | None = None
    
    def __post_init__(self):
        """Validate policy scope."""
        if not self.domains:
            raise ValueError("Policy scope must include at least one domain")
        
        if self.expiration_date and self.expiration_date <= self.effective_date:
            raise ValueError("Expiration date must be after effective date")
    
    def is_applicable_to_domain(self, domain: str) -> bool:
        """Check if policy applies to a specific domain."""
        return domain in self.domains or "*" in self.domains
    
    def is_applicable_to_system(self, system: str) -> bool:
        """Check if policy applies to a specific system."""
        return system in self.systems or "*" in self.systems
    
    def is_currently_effective(self) -> bool:
        """Check if policy is currently effective."""
        now = datetime.utcnow()
        if now < self.effective_date:
            return False
        if self.expiration_date and now > self.expiration_date:
            return False
        return True


@dataclass(frozen=True)
class PolicyVersion(ValueObject):
    """Represents a version of a policy."""
    
    version_number: str
    created_at: datetime
    created_by: str
    change_summary: str
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    def __post_init__(self):
        """Validate policy version."""
        if not self.version_number:
            raise ValueError("Version number is required")
        
        if not self.created_by:
            raise ValueError("Creator is required")
        
        if self.constitutional_hash != CONSTITUTIONAL_HASH:
            raise ValueError(f"Invalid constitutional hash: {self.constitutional_hash}")


@dataclass(frozen=True)
class PolicyMetadata(ValueObject):
    """Metadata associated with a policy."""
    
    tags: list[str]
    categories: list[str]
    priority: int
    owner: str
    reviewers: list[str]
    approval_required: bool = True
    review_frequency_days: int = 90
    
    def __post_init__(self):
        """Validate policy metadata."""
        if not 1 <= self.priority <= 10:
            raise ValueError("Priority must be between 1 and 10")
        
        if not self.owner:
            raise ValueError("Policy owner is required")
        
        if self.review_frequency_days < 1:
            raise ValueError("Review frequency must be at least 1 day")


@dataclass(frozen=True)
class ComplianceResult(ValueObject):
    """Result of a compliance evaluation."""
    
    evaluation_id: str
    policy_id: str
    compliance_level: ComplianceLevel
    compliance_score: float
    violations: list[dict[str, Any]]
    recommendations: list[str]
    evaluated_at: datetime
    evaluated_by: str
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    def __post_init__(self):
        """Validate compliance result."""
        if not 0.0 <= self.compliance_score <= 1.0:
            raise ValueError("Compliance score must be between 0.0 and 1.0")
        
        if not self.evaluation_id:
            raise ValueError("Evaluation ID is required")
        
        if not self.policy_id:
            raise ValueError("Policy ID is required")
        
        if self.constitutional_hash != CONSTITUTIONAL_HASH:
            raise ValueError(f"Invalid constitutional hash: {self.constitutional_hash}")
    
    def is_compliant(self) -> bool:
        """Check if the evaluation result is compliant."""
        return self.compliance_level == ComplianceLevel.COMPLIANT
    
    def has_violations(self) -> bool:
        """Check if there are any violations."""
        return len(self.violations) > 0


@dataclass(frozen=True)
class PolicyRule(ValueObject):
    """Represents a single rule within a policy."""
    
    rule_id: str
    rule_type: str
    condition: dict[str, Any]
    action: dict[str, Any]
    priority: int
    is_active: bool = True
    
    def __post_init__(self):
        """Validate policy rule."""
        if not self.rule_id:
            raise ValueError("Rule ID is required")
        
        if not self.rule_type:
            raise ValueError("Rule type is required")
        
        if not self.condition:
            raise ValueError("Rule condition is required")
        
        if not self.action:
            raise ValueError("Rule action is required")
        
        if not 1 <= self.priority <= 100:
            raise ValueError("Rule priority must be between 1 and 100")


@dataclass(frozen=True)
class ViolationDetail(ValueObject):
    """Details of a policy violation."""
    
    violation_id: str
    policy_id: str
    rule_id: str
    severity: ViolationSeverity
    description: str
    context: dict[str, Any]
    detected_at: datetime
    detected_by: str
    evidence: dict[str, Any] | None = None
    
    def __post_init__(self):
        """Validate violation detail."""
        if not self.violation_id:
            raise ValueError("Violation ID is required")
        
        if not self.policy_id:
            raise ValueError("Policy ID is required")
        
        if not self.rule_id:
            raise ValueError("Rule ID is required")
        
        if not self.description:
            raise ValueError("Violation description is required")
        
        if not self.detected_by:
            raise ValueError("Detector is required")


@dataclass(frozen=True)
class PolicyConflict(ValueObject):
    """Represents a conflict between policies."""
    
    conflict_id: str
    policy_ids: list[str]
    conflict_type: str
    description: str
    severity: ViolationSeverity
    resolution_options: list[str]
    detected_at: datetime
    
    def __post_init__(self):
        """Validate policy conflict."""
        if not self.conflict_id:
            raise ValueError("Conflict ID is required")
        
        if len(self.policy_ids) < 2:
            raise ValueError("At least two policies must be involved in a conflict")
        
        if not self.conflict_type:
            raise ValueError("Conflict type is required")
        
        if not self.description:
            raise ValueError("Conflict description is required")


@dataclass(frozen=True)
class PolicyApproval(ValueObject):
    """Represents approval for a policy."""
    
    approval_id: str
    policy_id: str
    approver_id: str
    approval_status: str  # "approved", "rejected", "pending"
    approval_notes: str | None
    approved_at: datetime | None
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    def __post_init__(self):
        """Validate policy approval."""
        if not self.approval_id:
            raise ValueError("Approval ID is required")
        
        if not self.policy_id:
            raise ValueError("Policy ID is required")
        
        if not self.approver_id:
            raise ValueError("Approver ID is required")
        
        if self.approval_status not in ["approved", "rejected", "pending"]:
            raise ValueError("Invalid approval status")
        
        if self.constitutional_hash != CONSTITUTIONAL_HASH:
            raise ValueError(f"Invalid constitutional hash: {self.constitutional_hash}")
    
    def is_approved(self) -> bool:
        """Check if the policy is approved."""
        return self.approval_status == "approved"
    
    def is_rejected(self) -> bool:
        """Check if the policy is rejected."""
        return self.approval_status == "rejected"
    
    def is_pending(self) -> bool:
        """Check if the approval is pending."""
        return self.approval_status == "pending"
