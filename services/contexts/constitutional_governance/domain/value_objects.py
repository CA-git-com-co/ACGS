"""
Value Objects for Constitutional Governance Domain
Constitutional Hash: cdd01ef066bc6cf2

Immutable value objects representing domain concepts.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set
from uuid import UUID

from services.shared.domain.base import CONSTITUTIONAL_HASH, ValueObject


class ConstitutionStatus(str, Enum):
    """Status of a constitution."""

    DRAFT = "draft"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class AmendmentStatus(str, Enum):
    """Status of an amendment proposal."""

    PROPOSED = "proposed"
    IN_REVIEW = "in_review"
    IN_CONSULTATION = "in_consultation"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ViolationSeverity(str, Enum):
    """Severity levels for principle violations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalStep(str, Enum):
    """Steps in the amendment approval workflow."""

    PROPOSED = "proposed"
    IMPACT_ANALYSIS = "impact_analysis"
    PUBLIC_CONSULTATION = "public_consultation"
    EXPERT_REVIEW = "expert_review"
    FORMAL_VERIFICATION = "formal_verification"
    CONSENSUS_BUILDING = "consensus_building"
    RATIFICATION = "ratification"


@dataclass(frozen=True)
class ConstitutionalHash(ValueObject):
    """Immutable cryptographic hash ensuring constitutional integrity."""

    value: str = CONSTITUTIONAL_HASH
    algorithm: str = "SHA-256"

    def _validate(self) -> None:
        """Validate the constitutional hash."""
        if self.value != CONSTITUTIONAL_HASH:
            raise ValueError(
                f"Invalid constitutional hash. Expected {CONSTITUTIONAL_HASH}, "
                f"got {self.value}"
            )

    def verify_integrity(self, content: str) -> bool:
        """Verify content integrity against the hash."""
        # In production, would compute hash of content and compare
        return self.value == CONSTITUTIONAL_HASH


@dataclass(frozen=True)
class PriorityWeight(ValueObject):
    """Priority weighting for principle importance (0.0 to 1.0)."""

    value: float

    def _validate(self) -> None:
        """Validate priority weight is in valid range."""
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(
                f"Priority weight must be between 0.0 and 1.0, got {self.value}"
            )

    def is_high_priority(self) -> bool:
        """Check if this is a high priority (>= 0.7)."""
        return self.value >= 0.7

    def is_critical(self) -> bool:
        """Check if this is critical priority (>= 0.9)."""
        return self.value >= 0.9


@dataclass(frozen=True)
class VersionNumber(ValueObject):
    """Semantic version number for constitutions."""

    major: int
    minor: int
    patch: int

    def _validate(self) -> None:
        """Validate version components."""
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            raise ValueError("Version components must be non-negative")

    def __str__(self) -> str:
        """String representation of version."""
        return f"{self.major}.{self.minor}.{self.patch}"

    def increment_major(self) -> "VersionNumber":
        """Create new version with incremented major number."""
        return VersionNumber(self.major + 1, 0, 0)

    def increment_minor(self) -> "VersionNumber":
        """Create new version with incremented minor number."""
        return VersionNumber(self.major, self.minor + 1, 0)

    def increment_patch(self) -> "VersionNumber":
        """Create new version with incremented patch number."""
        return VersionNumber(self.major, self.minor, self.patch + 1)

    def is_newer_than(self, other: "VersionNumber") -> bool:
        """Check if this version is newer than another."""
        return (self.major, self.minor, self.patch) > (
            other.major,
            other.minor,
            other.patch,
        )


@dataclass(frozen=True)
class ApplicationScope(ValueObject):
    """Scope where a principle applies."""

    contexts: Set[str]
    domains: Set[str]
    services: Set[str]

    def _validate(self) -> None:
        """Validate scope components."""
        if not (self.contexts or self.domains or self.services):
            raise ValueError("ApplicationScope must have at least one scope defined")

    def applies_to_context(self, context: str) -> bool:
        """Check if scope applies to a specific context."""
        return context in self.contexts or "*" in self.contexts

    def applies_to_domain(self, domain: str) -> bool:
        """Check if scope applies to a specific domain."""
        return domain in self.domains or "*" in self.domains

    def applies_to_service(self, service: str) -> bool:
        """Check if scope applies to a specific service."""
        return service in self.services or "*" in self.services

    def is_universal(self) -> bool:
        """Check if this scope applies universally."""
        return "*" in self.contexts and "*" in self.domains and "*" in self.services


@dataclass(frozen=True)
class ValidationCriteria(ValueObject):
    """Criteria for validating compliance with a principle."""

    criteria_type: str  # "logical", "quantitative", "qualitative"
    expression: str
    threshold: Optional[float] = None
    metadata: Optional[Dict[str, any]] = None

    def _validate(self) -> None:
        """Validate criteria configuration."""
        valid_types = {"logical", "quantitative", "qualitative"}
        if self.criteria_type not in valid_types:
            raise ValueError(f"Invalid criteria type: {self.criteria_type}")

        if self.criteria_type == "quantitative" and self.threshold is None:
            raise ValueError("Quantitative criteria must have a threshold")


@dataclass(frozen=True)
class FormalConstraints(ValueObject):
    """Machine-readable formal constraints for a principle."""

    constraint_language: str  # "z3", "opa", "datalog"
    constraints: List[str]
    variables: Dict[str, str]

    def _validate(self) -> None:
        """Validate formal constraints."""
        valid_languages = {"z3", "opa", "datalog", "prolog"}
        if self.constraint_language not in valid_languages:
            raise ValueError(f"Invalid constraint language: {self.constraint_language}")

        if not self.constraints:
            raise ValueError("Must have at least one constraint")


@dataclass(frozen=True)
class ComplianceScore(ValueObject):
    """Quantitative measure of constitutional adherence."""

    overall_score: float
    principle_scores: Dict[str, float]
    violations: List["ViolationDetail"]
    confidence_interval: tuple[float, float]
    calculated_at: datetime

    def _validate(self) -> None:
        """Validate compliance score."""
        if not 0.0 <= self.overall_score <= 1.0:
            raise ValueError(f"Overall score must be between 0.0 and 1.0")

        for principle_id, score in self.principle_scores.items():
            if not 0.0 <= score <= 1.0:
                raise ValueError(
                    f"Principle score for {principle_id} must be between 0.0 and 1.0"
                )

        lower, upper = self.confidence_interval
        if not (0.0 <= lower <= upper <= 1.0):
            raise ValueError("Invalid confidence interval")

    def is_compliant(self, threshold: float = 0.8) -> bool:
        """Check if score meets compliance threshold."""
        return self.overall_score >= threshold

    def has_violations(self) -> bool:
        """Check if there are any violations."""
        return len(self.violations) > 0

    def has_critical_violations(self) -> bool:
        """Check if there are any critical violations."""
        return any(v.severity == ViolationSeverity.CRITICAL for v in self.violations)


@dataclass(frozen=True)
class ViolationDetail(ValueObject):
    """Details of a principle violation."""

    principle_id: str
    violation_type: str
    severity: ViolationSeverity
    description: str
    evidence: Dict[str, any]
    detected_at: datetime

    def _validate(self) -> None:
        """Validate violation details."""
        if not self.principle_id:
            raise ValueError("Principle ID is required")
        if not self.description:
            raise ValueError("Violation description is required")


@dataclass(frozen=True)
class AmendmentJustification(ValueObject):
    """Justification for a constitutional amendment."""

    rationale: str
    problem_statement: str
    proposed_solution: str
    expected_benefits: List[str]
    potential_risks: List[str]
    evidence_links: List[str]

    def _validate(self) -> None:
        """Validate justification completeness."""
        if not self.rationale:
            raise ValueError("Amendment rationale is required")
        if not self.problem_statement:
            raise ValueError("Problem statement is required")
        if not self.proposed_solution:
            raise ValueError("Proposed solution is required")
        if not self.expected_benefits:
            raise ValueError("At least one expected benefit is required")


@dataclass(frozen=True)
class ConflictAnalysis(ValueObject):
    """Analysis of conflicts between principles."""

    conflicting_principles: List[tuple[str, str]]
    conflict_type: str  # "logical", "priority", "scope"
    severity: ViolationSeverity
    resolution_options: List[str]

    def _validate(self) -> None:
        """Validate conflict analysis."""
        valid_types = {"logical", "priority", "scope", "temporal"}
        if self.conflict_type not in valid_types:
            raise ValueError(f"Invalid conflict type: {self.conflict_type}")

        if not self.conflicting_principles:
            raise ValueError("Must have at least one conflict")

        if not self.resolution_options:
            raise ValueError("Must provide at least one resolution option")


@dataclass(frozen=True)
class ConsultationSummary(ValueObject):
    """Summary of public consultation results."""

    total_participants: int
    support_percentage: float
    oppose_percentage: float
    key_concerns: List[str]
    suggested_modifications: List[str]
    expert_opinions: Dict[str, str]

    def _validate(self) -> None:
        """Validate consultation summary."""
        if self.total_participants < 0:
            raise ValueError("Participant count cannot be negative")

        if not 0.0 <= self.support_percentage <= 100.0:
            raise ValueError("Support percentage must be between 0 and 100")

        if not 0.0 <= self.oppose_percentage <= 100.0:
            raise ValueError("Oppose percentage must be between 0 and 100")

        total_percentage = self.support_percentage + self.oppose_percentage
        if total_percentage > 100.0:
            raise ValueError("Support + oppose percentages cannot exceed 100")

    def has_majority_support(self) -> bool:
        """Check if amendment has majority support."""
        return self.support_percentage > 50.0

    def has_strong_support(self) -> bool:
        """Check if amendment has strong support (>= 75%)."""
        return self.support_percentage >= 75.0
