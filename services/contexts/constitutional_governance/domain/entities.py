"""
Entities for Constitutional Governance Domain
Constitutional Hash: cdd01ef066bc6cf2

Core entities representing constitutional concepts.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set
from uuid import UUID

from services.shared.domain.base import (
    Entity, 
    AggregateRoot, 
    EntityId,
    TenantId,
    MultiTenantAggregateRoot,
    InvalidEntityStateException,
    CONSTITUTIONAL_HASH
)

from .value_objects import (
    ConstitutionalHash,
    PriorityWeight,
    ComplianceScore,
    ApplicationScope,
    ValidationCriteria,
    FormalConstraints,
    VersionNumber,
    ConstitutionStatus,
    AmendmentStatus,
    ViolationSeverity,
    AmendmentJustification,
    ConflictAnalysis,
    ConsultationSummary,
    ApprovalStep,
    ViolationDetail
)

from .events import (
    ConstitutionAmended,
    PrincipleViolationDetected,
    AmendmentProposed,
    PublicConsultationCompleted,
    AmendmentApproved,
    AmendmentRejected
)


class Principle(Entity):
    """Entity representing a constitutional principle."""
    
    def __init__(
        self,
        principle_id: Optional[EntityId],
        name: str,
        content: str,
        priority_weight: PriorityWeight,
        scope: ApplicationScope,
        validation_criteria: ValidationCriteria,
        constraints: Optional[FormalConstraints] = None,
        category: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        rationale: Optional[str] = None
    ):
        """Initialize a principle."""
        super().__init__(principle_id)
        self.name = name
        self.content = content
        self.priority_weight = priority_weight
        self.scope = scope
        self.validation_criteria = validation_criteria
        self.constraints = constraints
        self.category = category or "general"
        self.keywords = keywords or []
        self.rationale = rationale
        self._is_active = True
    
    def evaluate_compliance(self, context: Dict[str, any]) -> ComplianceScore:
        """Evaluate compliance with this principle in a given context."""
        # This would contain actual evaluation logic
        # For now, return a mock score
        return ComplianceScore(
            overall_score=0.9,
            principle_scores={str(self.id): 0.9},
            violations=[],
            confidence_interval=(0.85, 0.95),
            calculated_at=datetime.utcnow()
        )
    
    def conflicts_with(self, other: 'Principle') -> Optional[ConflictAnalysis]:
        """Check if this principle conflicts with another."""
        # Check for logical conflicts
        if self._has_logical_conflict(other):
            return ConflictAnalysis(
                conflicting_principles=[(str(self.id), str(other.id))],
                conflict_type="logical",
                severity=ViolationSeverity.HIGH,
                resolution_options=[
                    "Apply meta-rule precedence",
                    "Scope-based resolution",
                    "Priority-based resolution"
                ]
            )
        
        # Check for scope overlap with different requirements
        if self._has_scope_conflict(other):
            return ConflictAnalysis(
                conflicting_principles=[(str(self.id), str(other.id))],
                conflict_type="scope",
                severity=ViolationSeverity.MEDIUM,
                resolution_options=[
                    "Narrow scope of one principle",
                    "Create context-specific rules",
                    "Merge principles with conditions"
                ]
            )
        
        return None
    
    def _has_logical_conflict(self, other: 'Principle') -> bool:
        """Check for logical conflicts between principles."""
        # Simplified logic - in production would use formal verification
        return False
    
    def _has_scope_conflict(self, other: 'Principle') -> bool:
        """Check for scope conflicts between principles."""
        # Check if scopes overlap
        context_overlap = bool(
            set(self.scope.contexts) & set(other.scope.contexts)
        )
        domain_overlap = bool(
            set(self.scope.domains) & set(other.scope.domains)
        )
        service_overlap = bool(
            set(self.scope.services) & set(other.scope.services)
        )
        
        return context_overlap or domain_overlap or service_overlap
    
    def deactivate(self) -> None:
        """Deactivate this principle."""
        self._is_active = False
        self.increment_version()
    
    def validate_invariants(self) -> None:
        """Validate principle invariants."""
        if not self.name:
            raise InvalidEntityStateException("Principle must have a name")
        if not self.content:
            raise InvalidEntityStateException("Principle must have content")
        if self.priority_weight.value < 0 or self.priority_weight.value > 1:
            raise InvalidEntityStateException("Priority weight must be between 0 and 1")


class MetaRule(Entity):
    """Entity representing rules that govern how principles work."""
    
    def __init__(
        self,
        meta_rule_id: Optional[EntityId],
        name: str,
        rule_logic: str,
        precedence_level: int,
        applicable_principles: Set[str],
        conflict_resolution_strategy: str
    ):
        """Initialize a meta-rule."""
        super().__init__(meta_rule_id)
        self.name = name
        self.rule_logic = rule_logic
        self.precedence_level = precedence_level
        self.applicable_principles = applicable_principles
        self.conflict_resolution_strategy = conflict_resolution_strategy
    
    def apply_to_conflict(self, conflict: ConflictAnalysis) -> str:
        """Apply this meta-rule to resolve a conflict."""
        # Implement conflict resolution logic
        if self.conflict_resolution_strategy == "precedence":
            return f"Apply precedence level {self.precedence_level}"
        elif self.conflict_resolution_strategy == "scope":
            return "Narrow scope to eliminate conflict"
        else:
            return "Escalate to human oversight"
    
    def validate_invariants(self) -> None:
        """Validate meta-rule invariants."""
        if not self.name:
            raise InvalidEntityStateException("Meta-rule must have a name")
        if self.precedence_level < 0:
            raise InvalidEntityStateException("Precedence level must be non-negative")


class Constitution(MultiTenantAggregateRoot):
    """Aggregate root representing the complete constitutional framework."""
    
    def __init__(
        self,
        constitution_id: Optional[EntityId],
        tenant_id: TenantId,
        version: VersionNumber,
        principles: Optional[List[Principle]] = None,
        meta_rules: Optional[List[MetaRule]] = None
    ):
        """Initialize a constitution."""
        super().__init__(constitution_id, tenant_id)
        self.version = version
        self.principles = principles or []
        self.meta_rules = meta_rules or []
        self.status = ConstitutionStatus.DRAFT
        self.constitutional_hash = ConstitutionalHash()
        self._principle_index = {str(p.id): p for p in self.principles}
        self._meta_rule_index = {str(mr.id): mr for mr in self.meta_rules}
    
    def add_principle(self, principle: Principle) -> None:
        """Add a new principle to the constitution."""
        # Check for conflicts with existing principles
        for existing in self.principles:
            conflict = existing.conflicts_with(principle)
            if conflict and conflict.severity == ViolationSeverity.CRITICAL:
                raise InvalidEntityStateException(
                    f"Cannot add principle {principle.name}: "
                    f"Critical conflict with {existing.name}"
                )
        
        self.principles.append(principle)
        self._principle_index[str(principle.id)] = principle
        self.increment_version()
        
        # Add domain event
        self.add_domain_event(
            ConstitutionAmended(
                aggregate_id=self.id,
                constitution_version=str(self.version),
                amended_principles=[str(principle.id)],
                new_hash=self.constitutional_hash.value,
                effective_date=datetime.utcnow(),
                approved_by=[]  # Would be populated from context
            )
        )
    
    def amend_principle(
        self, 
        principle_id: str, 
        amendment: 'Amendment'
    ) -> None:
        """Amend an existing principle."""
        if principle_id not in self._principle_index:
            raise InvalidEntityStateException(
                f"Principle {principle_id} not found in constitution"
            )
        
        principle = self._principle_index[principle_id]
        
        # Apply amendment changes
        if amendment.new_content:
            principle.content = amendment.new_content
        if amendment.new_priority:
            principle.priority_weight = amendment.new_priority
        if amendment.new_scope:
            principle.scope = amendment.new_scope
        
        principle.increment_version()
        self.increment_version()
        
        # Add domain event
        self.add_domain_event(
            ConstitutionAmended(
                aggregate_id=self.id,
                constitution_version=str(self.version),
                amended_principles=[principle_id],
                new_hash=self.constitutional_hash.value,
                effective_date=datetime.utcnow(),
                approved_by=[]
            )
        )
    
    def activate(self) -> None:
        """Activate this constitution version."""
        if self.status != ConstitutionStatus.DRAFT:
            raise InvalidEntityStateException(
                f"Cannot activate constitution in status {self.status}"
            )
        
        self.status = ConstitutionStatus.ACTIVE
        self.increment_version()
    
    def supersede(self) -> None:
        """Mark this constitution as superseded by a newer version."""
        if self.status != ConstitutionStatus.ACTIVE:
            raise InvalidEntityStateException(
                f"Cannot supersede constitution in status {self.status}"
            )
        
        self.status = ConstitutionStatus.SUPERSEDED
        self.increment_version()
    
    def validate_consistency(self) -> List[ConflictAnalysis]:
        """Validate internal consistency of all principles."""
        conflicts = []
        
        # Check all principle pairs for conflicts
        for i, principle1 in enumerate(self.principles):
            for principle2 in self.principles[i+1:]:
                conflict = principle1.conflicts_with(principle2)
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    def calculate_compliance_score(
        self, 
        action: Dict[str, any],
        context: Dict[str, any]
    ) -> ComplianceScore:
        """Calculate overall compliance score for an action."""
        applicable_principles = self._get_applicable_principles(action, context)
        
        if not applicable_principles:
            # No applicable principles means full compliance
            return ComplianceScore(
                overall_score=1.0,
                principle_scores={},
                violations=[],
                confidence_interval=(1.0, 1.0),
                calculated_at=datetime.utcnow()
            )
        
        # Evaluate each applicable principle
        principle_scores = {}
        violations = []
        
        for principle in applicable_principles:
            score = principle.evaluate_compliance(context)
            principle_scores[str(principle.id)] = score.overall_score
            violations.extend(score.violations)
        
        # Calculate weighted average based on priority
        total_weight = sum(p.priority_weight.value for p in applicable_principles)
        if total_weight == 0:
            overall_score = sum(principle_scores.values()) / len(principle_scores)
        else:
            weighted_sum = sum(
                score * p.priority_weight.value 
                for p, score in zip(applicable_principles, principle_scores.values())
            )
            overall_score = weighted_sum / total_weight
        
        return ComplianceScore(
            overall_score=overall_score,
            principle_scores=principle_scores,
            violations=violations,
            confidence_interval=(overall_score - 0.05, overall_score + 0.05),
            calculated_at=datetime.utcnow()
        )
    
    def _get_applicable_principles(
        self,
        action: Dict[str, any],
        context: Dict[str, any]
    ) -> List[Principle]:
        """Get principles applicable to an action in a context."""
        applicable = []
        
        for principle in self.principles:
            if self._is_principle_applicable(principle, action, context):
                applicable.append(principle)
        
        return applicable
    
    def _is_principle_applicable(
        self,
        principle: Principle,
        action: Dict[str, any],
        context: Dict[str, any]
    ) -> bool:
        """Check if a principle applies to an action/context."""
        # Check scope applicability
        if "context" in context:
            if not principle.scope.applies_to_context(context["context"]):
                return False
        
        if "domain" in context:
            if not principle.scope.applies_to_domain(context["domain"]):
                return False
        
        if "service" in context:
            if not principle.scope.applies_to_service(context["service"]):
                return False
        
        return True
    
    def validate_invariants(self) -> None:
        """Validate constitution invariants."""
        if not self.version:
            raise InvalidEntityStateException("Constitution must have a version")
        
        if self.constitutional_hash.value != CONSTITUTIONAL_HASH:
            raise InvalidEntityStateException(
                f"Invalid constitutional hash: {self.constitutional_hash.value}"
            )
        
        # Validate all principles
        for principle in self.principles:
            principle.validate_invariants()
        
        # Validate all meta-rules
        for meta_rule in self.meta_rules:
            meta_rule.validate_invariants()
        
        # Check for critical conflicts
        conflicts = self.validate_consistency()
        critical_conflicts = [
            c for c in conflicts 
            if c.severity == ViolationSeverity.CRITICAL
        ]
        
        if critical_conflicts:
            raise InvalidEntityStateException(
                f"Constitution has {len(critical_conflicts)} critical conflicts"
            )


class Amendment(Entity):
    """Entity representing a change to a principle."""
    
    def __init__(
        self,
        amendment_id: Optional[EntityId],
        principle_id: str,
        new_content: Optional[str] = None,
        new_priority: Optional[PriorityWeight] = None,
        new_scope: Optional[ApplicationScope] = None,
        new_validation: Optional[ValidationCriteria] = None,
        justification: Optional[AmendmentJustification] = None
    ):
        """Initialize an amendment."""
        super().__init__(amendment_id)
        self.principle_id = principle_id
        self.new_content = new_content
        self.new_priority = new_priority
        self.new_scope = new_scope
        self.new_validation = new_validation
        self.justification = justification
    
    def validate_invariants(self) -> None:
        """Validate amendment invariants."""
        if not self.principle_id:
            raise InvalidEntityStateException("Amendment must reference a principle")
        
        # At least one change must be specified
        if not any([
            self.new_content,
            self.new_priority,
            self.new_scope,
            self.new_validation
        ]):
            raise InvalidEntityStateException(
                "Amendment must specify at least one change"
            )


class PublicConsultation(Entity):
    """Entity representing a public consultation process."""
    
    def __init__(
        self,
        consultation_id: Optional[EntityId],
        amendment_id: str,
        start_date: datetime,
        end_date: datetime,
        required_participants: int = 100
    ):
        """Initialize public consultation."""
        super().__init__(consultation_id)
        self.amendment_id = amendment_id
        self.start_date = start_date
        self.end_date = end_date
        self.required_participants = required_participants
        self.stakeholder_inputs: List[StakeholderInput] = []
        self.public_comments: List[Dict[str, any]] = []
        self.expert_reviews: List[Dict[str, any]] = []
    
    def add_stakeholder_input(self, input: 'StakeholderInput') -> None:
        """Add stakeholder input to the consultation."""
        self.stakeholder_inputs.append(input)
        self.increment_version()
    
    def is_complete(self) -> bool:
        """Check if consultation period is complete."""
        return (
            datetime.utcnow() >= self.end_date and
            len(self.stakeholder_inputs) >= self.required_participants
        )
    
    def generate_summary(self) -> ConsultationSummary:
        """Generate summary of consultation results."""
        total = len(self.stakeholder_inputs)
        support = sum(1 for i in self.stakeholder_inputs if i.supports_amendment)
        oppose = total - support
        
        return ConsultationSummary(
            total_participants=total,
            support_percentage=(support / total * 100) if total > 0 else 0,
            oppose_percentage=(oppose / total * 100) if total > 0 else 0,
            key_concerns=[],  # Would aggregate from inputs
            suggested_modifications=[],  # Would aggregate from inputs
            expert_opinions={}  # Would aggregate from expert reviews
        )
    
    def validate_invariants(self) -> None:
        """Validate consultation invariants."""
        if self.end_date <= self.start_date:
            raise InvalidEntityStateException(
                "Consultation end date must be after start date"
            )
        
        if self.required_participants < 1:
            raise InvalidEntityStateException(
                "Must require at least one participant"
            )


class StakeholderInput(Entity):
    """Entity representing input from a stakeholder."""
    
    def __init__(
        self,
        input_id: Optional[EntityId],
        stakeholder_id: str,
        stakeholder_type: str,  # "citizen", "expert", "organization"
        supports_amendment: bool,
        concerns: List[str],
        suggestions: List[str],
        submitted_at: Optional[datetime] = None
    ):
        """Initialize stakeholder input."""
        super().__init__(input_id)
        self.stakeholder_id = stakeholder_id
        self.stakeholder_type = stakeholder_type
        self.supports_amendment = supports_amendment
        self.concerns = concerns
        self.suggestions = suggestions
        self.submitted_at = submitted_at or datetime.utcnow()
    
    def validate_invariants(self) -> None:
        """Validate stakeholder input invariants."""
        valid_types = {"citizen", "expert", "organization", "government"}
        if self.stakeholder_type not in valid_types:
            raise InvalidEntityStateException(
                f"Invalid stakeholder type: {self.stakeholder_type}"
            )


class AmendmentProposal(MultiTenantAggregateRoot):
    """Aggregate root for the amendment proposal process."""
    
    def __init__(
        self,
        proposal_id: Optional[EntityId],
        tenant_id: TenantId,
        proposer_id: str,
        amendments: List[Amendment],
        justification: AmendmentJustification
    ):
        """Initialize amendment proposal."""
        super().__init__(proposal_id, tenant_id)
        self.proposer_id = proposer_id
        self.amendments = amendments
        self.justification = justification
        self.status = AmendmentStatus.PROPOSED
        self.public_consultation: Optional[PublicConsultation] = None
        self.approval_workflow: Optional[ApprovalWorkflow] = None
        self.submitted_at = datetime.utcnow()
        self.decided_at: Optional[datetime] = None
    
    def start_public_consultation(
        self,
        start_date: datetime,
        end_date: datetime,
        required_participants: int = 100
    ) -> None:
        """Start public consultation for the amendment."""
        if self.status != AmendmentStatus.IN_REVIEW:
            raise InvalidEntityStateException(
                f"Cannot start consultation in status {self.status}"
            )
        
        self.public_consultation = PublicConsultation(
            consultation_id=None,
            amendment_id=str(self.id),
            start_date=start_date,
            end_date=end_date,
            required_participants=required_participants
        )
        
        self.status = AmendmentStatus.IN_CONSULTATION
        self.increment_version()
    
    def record_stakeholder_input(self, input: StakeholderInput) -> None:
        """Record stakeholder input during consultation."""
        if not self.public_consultation:
            raise InvalidEntityStateException("No active consultation")
        
        if self.status != AmendmentStatus.IN_CONSULTATION:
            raise InvalidEntityStateException(
                f"Cannot record input in status {self.status}"
            )
        
        self.public_consultation.add_stakeholder_input(input)
        
        # Check if consultation is complete
        if self.public_consultation.is_complete():
            self._complete_consultation()
    
    def _complete_consultation(self) -> None:
        """Complete the consultation phase."""
        summary = self.public_consultation.generate_summary()
        
        # Add domain event
        self.add_domain_event(
            PublicConsultationCompleted(
                aggregate_id=self.id,
                amendment_id=self.id,
                consultation_id=self.public_consultation.id,
                stakeholder_input_count=summary.total_participants,
                public_comment_count=len(self.public_consultation.public_comments),
                expert_review_count=len(self.public_consultation.expert_reviews),
                consultation_summary=summary
            )
        )
        
        # Move to next phase based on results
        if summary.has_strong_support():
            self.status = AmendmentStatus.APPROVED
            self._approve_amendment()
        elif summary.has_majority_support():
            # Needs further review
            self.status = AmendmentStatus.IN_REVIEW
        else:
            self.status = AmendmentStatus.REJECTED
            self._reject_amendment()
    
    def _approve_amendment(self) -> None:
        """Approve the amendment."""
        self.decided_at = datetime.utcnow()
        
        self.add_domain_event(
            AmendmentApproved(
                aggregate_id=self.id,
                amendment_id=self.id,
                approved_at=self.decided_at,
                approval_details={}
            )
        )
    
    def _reject_amendment(self) -> None:
        """Reject the amendment."""
        self.decided_at = datetime.utcnow()
        
        self.add_domain_event(
            AmendmentRejected(
                aggregate_id=self.id,
                amendment_id=self.id,
                rejected_at=self.decided_at,
                rejection_reason="Insufficient public support"
            )
        )
    
    def withdraw(self, reason: str) -> None:
        """Withdraw the amendment proposal."""
        if self.status in [AmendmentStatus.APPROVED, AmendmentStatus.REJECTED]:
            raise InvalidEntityStateException(
                f"Cannot withdraw amendment in status {self.status}"
            )
        
        self.status = AmendmentStatus.WITHDRAWN
        self.decided_at = datetime.utcnow()
        self.increment_version()
    
    def validate_invariants(self) -> None:
        """Validate amendment proposal invariants."""
        if not self.proposer_id:
            raise InvalidEntityStateException("Amendment must have a proposer")
        
        if not self.amendments:
            raise InvalidEntityStateException("Must propose at least one amendment")
        
        # Validate all amendments
        for amendment in self.amendments:
            amendment.validate_invariants()
        
        # Validate justification
        self.justification._validate()
        
        # Status transitions
        valid_transitions = {
            AmendmentStatus.PROPOSED: [
                AmendmentStatus.IN_REVIEW,
                AmendmentStatus.WITHDRAWN
            ],
            AmendmentStatus.IN_REVIEW: [
                AmendmentStatus.IN_CONSULTATION,
                AmendmentStatus.APPROVED,
                AmendmentStatus.REJECTED,
                AmendmentStatus.WITHDRAWN
            ],
            AmendmentStatus.IN_CONSULTATION: [
                AmendmentStatus.IN_REVIEW,
                AmendmentStatus.APPROVED,
                AmendmentStatus.REJECTED,
                AmendmentStatus.WITHDRAWN
            ],
            AmendmentStatus.APPROVED: [],
            AmendmentStatus.REJECTED: [],
            AmendmentStatus.WITHDRAWN: []
        }
        
        # This check would be used during status transitions
        # Currently just validates the status is valid
        if self.status not in AmendmentStatus:
            raise InvalidEntityStateException(f"Invalid status: {self.status}")


class ApprovalWorkflow(Entity):
    """Entity representing the approval workflow for an amendment."""
    
    def __init__(
        self,
        workflow_id: Optional[EntityId],
        amendment_id: str,
        required_steps: List[ApprovalStep]
    ):
        """Initialize approval workflow."""
        super().__init__(workflow_id)
        self.amendment_id = amendment_id
        self.required_steps = required_steps
        self.completed_steps: Dict[ApprovalStep, datetime] = {}
        self.current_step: Optional[ApprovalStep] = required_steps[0] if required_steps else None
    
    def complete_step(
        self,
        step: ApprovalStep,
        result: Dict[str, any]
    ) -> None:
        """Mark a step as completed."""
        if step != self.current_step:
            raise InvalidEntityStateException(
                f"Cannot complete step {step}, current step is {self.current_step}"
            )
        
        self.completed_steps[step] = datetime.utcnow()
        
        # Move to next step
        current_index = self.required_steps.index(step)
        if current_index < len(self.required_steps) - 1:
            self.current_step = self.required_steps[current_index + 1]
        else:
            self.current_step = None  # Workflow complete
        
        self.increment_version()
    
    def is_complete(self) -> bool:
        """Check if all required steps are complete."""
        return len(self.completed_steps) == len(self.required_steps)
    
    def validate_invariants(self) -> None:
        """Validate workflow invariants."""
        if not self.amendment_id:
            raise InvalidEntityStateException("Workflow must reference an amendment")
        
        if not self.required_steps:
            raise InvalidEntityStateException("Workflow must have at least one step")