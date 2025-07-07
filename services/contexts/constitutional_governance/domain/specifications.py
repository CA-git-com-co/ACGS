"""
Domain Specifications for Constitutional Governance
Constitutional Hash: cdd01ef066bc6cf2

Specifications for complex domain queries and business rules.
"""

from typing import Any, Dict

from services.shared.domain.specifications import Specification

from .entities import AmendmentProposal, Constitution, Principle
from .value_objects import (
    AmendmentStatus,
    ConstitutionStatus,
    PriorityWeight,
    ViolationSeverity,
)


class ActiveConstitutionSpec(Specification[Constitution]):
    """Specification for active constitutions."""

    def is_satisfied_by(self, constitution: Constitution) -> bool:
        """Check if constitution is active."""
        return constitution.status == ConstitutionStatus.ACTIVE


class ApplicablePrincipleSpec(Specification[Principle]):
    """Specification for principles applicable to a specific context."""

    def __init__(self, context: Dict[str, Any]):
        """Initialize with evaluation context."""
        self.context = context

    def is_satisfied_by(self, principle: Principle) -> bool:
        """Check if principle applies to the context."""
        # Check if principle scope applies to context
        if "context" in self.context:
            if not principle.scope.applies_to_context(self.context["context"]):
                return False

        if "domain" in self.context:
            if not principle.scope.applies_to_domain(self.context["domain"]):
                return False

        if "service" in self.context:
            if not principle.scope.applies_to_service(self.context["service"]):
                return False

        # Check if principle is active
        return principle._is_active


class ValidAmendmentSpec(Specification[AmendmentProposal]):
    """Specification for valid amendment proposals."""

    def is_satisfied_by(self, amendment: AmendmentProposal) -> bool:
        """Check if amendment proposal is valid."""
        # Must have at least one amendment
        if not amendment.amendments:
            return False

        # Must have justification
        if not amendment.justification:
            return False

        # Check each amendment is valid
        for amend in amendment.amendments:
            if not self._is_amendment_valid(amend):
                return False

        return True

    def _is_amendment_valid(self, amendment) -> bool:
        """Check if individual amendment is valid."""
        # Must reference a principle
        if not amendment.principle_id:
            return False

        # Must have at least one change
        return any(
            [
                amendment.new_content,
                amendment.new_priority,
                amendment.new_scope,
                amendment.new_validation,
            ]
        )


class ConflictingPrinciplesSpec(Specification[tuple[Principle, Principle]]):
    """Specification for detecting conflicting principles."""

    def is_satisfied_by(self, principle_pair: tuple[Principle, Principle]) -> bool:
        """Check if two principles conflict."""
        principle1, principle2 = principle_pair

        # Check for conflicts
        conflict = principle1.conflicts_with(principle2)

        return conflict is not None


class HighPriorityPrincipleSpec(Specification[Principle]):
    """Specification for high priority principles."""

    def __init__(self, threshold: float = 0.7):
        """Initialize with priority threshold."""
        self.threshold = threshold

    def is_satisfied_by(self, principle: Principle) -> bool:
        """Check if principle has high priority."""
        return principle.priority_weight.value >= self.threshold


class CriticalPriorityPrincipleSpec(Specification[Principle]):
    """Specification for critical priority principles."""

    def is_satisfied_by(self, principle: Principle) -> bool:
        """Check if principle has critical priority."""
        return principle.priority_weight.is_critical()


class PublicConsultationRequiredSpec(Specification[AmendmentProposal]):
    """Specification for amendments requiring public consultation."""

    def is_satisfied_by(self, amendment: AmendmentProposal) -> bool:
        """Check if amendment requires public consultation."""
        # Major constitutional changes require consultation
        if self._affects_fundamental_principles(amendment):
            return True

        # Multiple principle changes require consultation
        if len(amendment.amendments) > 1:
            return True

        # High-impact changes require consultation
        if self._has_high_impact(amendment):
            return True

        return False

    def _affects_fundamental_principles(self, amendment: AmendmentProposal) -> bool:
        """Check if amendment affects fundamental principles."""
        # This would check against a list of fundamental principle categories
        fundamental_categories = {
            "core_rights",
            "system_safety",
            "democratic_participation",
        }

        # For now, simplified check
        return len(amendment.amendments) > 0

    def _has_high_impact(self, amendment: AmendmentProposal) -> bool:
        """Check if amendment has high impact."""
        # Check if affecting high-priority principles
        # This would require access to the principle repository
        # For now, simplified implementation
        return len(amendment.amendments) > 2


class ExpertReviewRequiredSpec(Specification[AmendmentProposal]):
    """Specification for amendments requiring expert review."""

    def is_satisfied_by(self, amendment: AmendmentProposal) -> bool:
        """Check if amendment requires expert review."""
        # Technical amendments require expert review
        if self._is_technical_amendment(amendment):
            return True

        # Safety-related amendments require expert review
        if self._affects_safety_principles(amendment):
            return True

        return False

    def _is_technical_amendment(self, amendment: AmendmentProposal) -> bool:
        """Check if amendment is technical in nature."""
        # Check if any amendment involves formal constraints
        for amend in amendment.amendments:
            if amend.new_validation:
                return True
        return False

    def _affects_safety_principles(self, amendment: AmendmentProposal) -> bool:
        """Check if amendment affects safety principles."""
        # This would check against safety principle categories
        return False  # Simplified for now


class AmendmentInProgressSpec(Specification[AmendmentProposal]):
    """Specification for amendments currently in progress."""

    def is_satisfied_by(self, amendment: AmendmentProposal) -> bool:
        """Check if amendment is in progress."""
        in_progress_statuses = {
            AmendmentStatus.IN_REVIEW,
            AmendmentStatus.IN_CONSULTATION,
        }
        return amendment.status in in_progress_statuses


class CompletedAmendmentSpec(Specification[AmendmentProposal]):
    """Specification for completed amendments."""

    def is_satisfied_by(self, amendment: AmendmentProposal) -> bool:
        """Check if amendment is completed."""
        completed_statuses = {
            AmendmentStatus.APPROVED,
            AmendmentStatus.REJECTED,
            AmendmentStatus.WITHDRAWN,
        }
        return amendment.status in completed_statuses


class UniversalScopePrincipleSpec(Specification[Principle]):
    """Specification for principles with universal scope."""

    def is_satisfied_by(self, principle: Principle) -> bool:
        """Check if principle has universal scope."""
        return principle.scope.is_universal()


class CategoryPrincipleSpec(Specification[Principle]):
    """Specification for principles in a specific category."""

    def __init__(self, category: str):
        """Initialize with category filter."""
        self.category = category

    def is_satisfied_by(self, principle: Principle) -> bool:
        """Check if principle belongs to category."""
        return principle.category == self.category


class KeywordPrincipleSpec(Specification[Principle]):
    """Specification for principles with specific keywords."""

    def __init__(self, keywords: set[str]):
        """Initialize with keyword filter."""
        self.keywords = keywords

    def is_satisfied_by(self, principle: Principle) -> bool:
        """Check if principle has any of the keywords."""
        principle_keywords = set(principle.keywords)
        return bool(principle_keywords & self.keywords)


class RecentlyModifiedPrincipleSpec(Specification[Principle]):
    """Specification for recently modified principles."""

    def __init__(self, days: int = 30):
        """Initialize with recency threshold."""
        from datetime import datetime, timedelta

        self.cutoff_date = datetime.utcnow() - timedelta(days=days)

    def is_satisfied_by(self, principle: Principle) -> bool:
        """Check if principle was recently modified."""
        return principle.updated_at >= self.cutoff_date


class ConsistentConstitutionSpec(Specification[Constitution]):
    """Specification for constitutions without conflicts."""

    def is_satisfied_by(self, constitution: Constitution) -> bool:
        """Check if constitution is internally consistent."""
        conflicts = constitution.validate_consistency()

        # Check for critical conflicts
        critical_conflicts = [
            c for c in conflicts if c.severity == ViolationSeverity.CRITICAL
        ]

        return len(critical_conflicts) == 0


class MinimumPrincipleCountSpec(Specification[Constitution]):
    """Specification for constitutions with minimum principle count."""

    def __init__(self, minimum: int = 1):
        """Initialize with minimum count."""
        self.minimum = minimum

    def is_satisfied_by(self, constitution: Constitution) -> bool:
        """Check if constitution has minimum number of principles."""
        return len(constitution.principles) >= self.minimum


class BalancedPriorityDistributionSpec(Specification[Constitution]):
    """Specification for constitutions with balanced priority distribution."""

    def is_satisfied_by(self, constitution: Constitution) -> bool:
        """Check if constitution has balanced priority distribution."""
        if not constitution.principles:
            return False

        # Calculate priority distribution
        high_priority_count = sum(
            1 for p in constitution.principles if p.priority_weight.is_high_priority()
        )

        total_count = len(constitution.principles)
        high_priority_ratio = high_priority_count / total_count

        # Ensure not all principles are high priority (max 50%)
        return high_priority_ratio <= 0.5


# Composite specifications for common use cases
class ReadyForActivationSpec(Specification[Constitution]):
    """Composite specification for constitutions ready for activation."""

    def __init__(self):
        """Initialize composite specification."""
        self.spec = (
            ConsistentConstitutionSpec()
            & MinimumPrincipleCountSpec(3)  # At least 3 principles
            & BalancedPriorityDistributionSpec()
        )

    def is_satisfied_by(self, constitution: Constitution) -> bool:
        """Check if constitution is ready for activation."""
        return (
            constitution.status == ConstitutionStatus.DRAFT
            and self.spec.is_satisfied_by(constitution)
        )


class ReadyForConsultationSpec(Specification[AmendmentProposal]):
    """Composite specification for amendments ready for consultation."""

    def __init__(self):
        """Initialize composite specification."""
        self.spec = ValidAmendmentSpec() & PublicConsultationRequiredSpec()

    def is_satisfied_by(self, amendment: AmendmentProposal) -> bool:
        """Check if amendment is ready for consultation."""
        return (
            amendment.status == AmendmentStatus.IN_REVIEW
            and self.spec.is_satisfied_by(amendment)
        )
