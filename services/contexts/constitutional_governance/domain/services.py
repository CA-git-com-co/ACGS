"""
Domain Services for Constitutional Governance
Constitutional Hash: cdd01ef066bc6cf2

Domain services encapsulating complex business logic that doesn't belong to entities.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from services.shared.domain.base import EntityId, TenantId

from .entities import (
    Amendment,
    AmendmentProposal,
    Constitution,
    Principle,
    PublicConsultation,
    StakeholderInput,
)
from .specifications import (
    ApplicablePrincipleSpec,
    ConflictingPrinciplesSpec,
    ExpertReviewRequiredSpec,
    HighPriorityPrincipleSpec,
    PublicConsultationRequiredSpec,
)
from .value_objects import (
    AmendmentJustification,
    ComplianceScore,
    ConflictAnalysis,
    ConsultationSummary,
    PriorityWeight,
    ViolationDetail,
    ViolationSeverity,
)

logger = logging.getLogger(__name__)


class ConstitutionalComplianceService:
    """
    Domain service for comprehensive constitutional compliance evaluation.

    Handles complex compliance validation logic that requires coordination
    across multiple principles and meta-rules.
    """

    def __init__(
        self,
        principle_repository: "PrincipleRepository",
        meta_rule_repository: "MetaRuleRepository",
        formal_verification_service: Optional["FormalVerificationService"] = None,
    ):
        """Initialize compliance service with dependencies."""
        self.principle_repo = principle_repository
        self.meta_rule_repo = meta_rule_repository
        self.formal_verification = formal_verification_service

    async def evaluate_comprehensive_compliance(
        self, action: Dict[str, Any], context: Dict[str, Any], tenant_id: TenantId
    ) -> ComplianceScore:
        """
        Evaluate action against all applicable constitutional principles.

        This is the core compliance evaluation logic that:
        1. Identifies applicable principles
        2. Evaluates each principle
        3. Detects and resolves conflicts
        4. Calculates weighted compliance score
        5. Integrates formal verification if needed
        """
        logger.info(f"Evaluating compliance for action in tenant {tenant_id}")

        # 1. Identify applicable principles
        applicable_principles = await self._identify_applicable_principles(
            action, context, tenant_id
        )

        if not applicable_principles:
            logger.info("No applicable principles found - full compliance")
            return ComplianceScore(
                overall_score=1.0,
                principle_scores={},
                violations=[],
                confidence_interval=(1.0, 1.0),
                calculated_at=datetime.utcnow(),
            )

        # 2. Evaluate each principle
        principle_evaluations = {}
        all_violations = []

        for principle in applicable_principles:
            logger.debug(f"Evaluating principle: {principle.name}")
            evaluation = principle.evaluate_compliance(context)
            principle_evaluations[str(principle.id)] = evaluation.overall_score
            all_violations.extend(evaluation.violations)

        # 3. Detect and resolve conflicts using meta-rules
        conflicts = await self._detect_and_resolve_conflicts(
            applicable_principles, context, tenant_id
        )

        # Adjust scores based on conflict resolutions
        adjusted_scores = self._apply_conflict_resolutions(
            principle_evaluations, conflicts
        )

        # 4. Calculate final weighted compliance score
        final_score = self._calculate_weighted_score(
            applicable_principles, adjusted_scores
        )

        # 5. Integrate formal verification if required
        if self._requires_formal_verification(action, context):
            verification_adjustment = await self._perform_formal_verification(
                action, context, applicable_principles
            )
            final_score = min(final_score, verification_adjustment)

        # Calculate confidence interval based on principle agreement
        confidence = self._calculate_confidence_interval(adjusted_scores)

        logger.info(f"Compliance evaluation complete. Score: {final_score}")

        return ComplianceScore(
            overall_score=final_score,
            principle_scores=adjusted_scores,
            violations=all_violations,
            confidence_interval=confidence,
            calculated_at=datetime.utcnow(),
        )

    async def _identify_applicable_principles(
        self, action: Dict[str, Any], context: Dict[str, Any], tenant_id: TenantId
    ) -> List[Principle]:
        """Identify which principles apply to this action in this context."""

        # Get all principles for the tenant
        all_principles = await self.principle_repo.find_by_tenant(tenant_id)

        # Filter using specification
        applicable_spec = ApplicablePrincipleSpec(context)
        applicable_principles = [
            p for p in all_principles if applicable_spec.is_satisfied_by(p)
        ]

        logger.debug(f"Found {len(applicable_principles)} applicable principles")
        return applicable_principles

    async def _detect_and_resolve_conflicts(
        self, principles: List[Principle], context: Dict[str, Any], tenant_id: TenantId
    ) -> List[ConflictAnalysis]:
        """Detect conflicts between principles and resolve using meta-rules."""

        conflicts = []
        conflict_spec = ConflictingPrinciplesSpec()

        # Check all principle pairs for conflicts
        for i, principle1 in enumerate(principles):
            for principle2 in principles[i + 1 :]:
                if conflict_spec.is_satisfied_by((principle1, principle2)):
                    conflict = principle1.conflicts_with(principle2)
                    if conflict:
                        conflicts.append(conflict)

        if conflicts:
            logger.info(f"Detected {len(conflicts)} conflicts")
            # Apply meta-rules to resolve conflicts
            resolved_conflicts = await self._apply_meta_rules(conflicts, tenant_id)
            return resolved_conflicts

        return []

    async def _apply_meta_rules(
        self, conflicts: List[ConflictAnalysis], tenant_id: TenantId
    ) -> List[ConflictAnalysis]:
        """Apply meta-rules to resolve conflicts."""

        meta_rules = await self.meta_rule_repo.find_by_tenant(tenant_id)
        resolved_conflicts = []

        for conflict in conflicts:
            # Find applicable meta-rules for this conflict
            applicable_meta_rules = [
                mr
                for mr in meta_rules
                if self._meta_rule_applies_to_conflict(mr, conflict)
            ]

            if applicable_meta_rules:
                # Apply highest precedence meta-rule
                highest_precedence = max(
                    applicable_meta_rules, key=lambda mr: mr.precedence_level
                )

                resolution = highest_precedence.apply_to_conflict(conflict)
                conflict.resolution_strategy = resolution

            resolved_conflicts.append(conflict)

        return resolved_conflicts

    def _meta_rule_applies_to_conflict(
        self, meta_rule, conflict: ConflictAnalysis
    ) -> bool:
        """Check if a meta-rule applies to a specific conflict."""
        # Check if any conflicting principles are in the meta-rule's scope
        conflicting_principle_ids = {
            principle_id
            for pair in conflict.conflicting_principles
            for principle_id in pair
        }

        return bool(conflicting_principle_ids & meta_rule.applicable_principles)

    def _apply_conflict_resolutions(
        self, principle_scores: Dict[str, float], conflicts: List[ConflictAnalysis]
    ) -> Dict[str, float]:
        """Apply conflict resolution adjustments to principle scores."""

        adjusted_scores = principle_scores.copy()

        for conflict in conflicts:
            if hasattr(conflict, "resolution_strategy"):
                # Apply resolution strategy adjustments
                if "precedence" in conflict.resolution_strategy:
                    # Lower-precedence principles get reduced weight
                    for pair in conflict.conflicting_principles:
                        # Simplified: reduce score of second principle
                        if pair[1] in adjusted_scores:
                            adjusted_scores[pair[1]] *= 0.8

        return adjusted_scores

    def _calculate_weighted_score(
        self, principles: List[Principle], scores: Dict[str, float]
    ) -> float:
        """Calculate weighted average compliance score."""

        total_weight = 0.0
        weighted_sum = 0.0

        for principle in principles:
            principle_id = str(principle.id)
            if principle_id in scores:
                weight = principle.priority_weight.value
                score = scores[principle_id]

                weighted_sum += weight * score
                total_weight += weight

        if total_weight == 0:
            return 1.0  # No weighted principles means full compliance

        return weighted_sum / total_weight

    def _requires_formal_verification(
        self, action: Dict[str, Any], context: Dict[str, Any]
    ) -> bool:
        """Check if action requires formal verification."""

        # Require formal verification for critical operations
        if context.get("criticality") == "high":
            return True

        # Require for safety-related operations
        if "safety" in action.get("tags", []):
            return True

        return False

    async def _perform_formal_verification(
        self,
        action: Dict[str, Any],
        context: Dict[str, Any],
        principles: List[Principle],
    ) -> float:
        """Perform formal verification and return adjustment factor."""

        if not self.formal_verification:
            logger.warning("Formal verification requested but service not available")
            return 1.0

        try:
            # Extract formal constraints from principles
            constraints = []
            for principle in principles:
                if principle.constraints:
                    constraints.extend(principle.constraints.constraints)

            if not constraints:
                return 1.0

            # Perform formal verification
            verification_result = await self.formal_verification.verify(
                action, context, constraints
            )

            return 1.0 if verification_result.is_valid else 0.0

        except Exception as e:
            logger.error(f"Formal verification failed: {e}")
            return 0.5  # Conservative score when verification fails

    def _calculate_confidence_interval(
        self, scores: Dict[str, float]
    ) -> tuple[float, float]:
        """Calculate confidence interval for the compliance score."""

        if not scores:
            return (1.0, 1.0)

        score_values = list(scores.values())
        avg_score = sum(score_values) / len(score_values)

        # Calculate standard deviation
        variance = sum((score - avg_score) ** 2 for score in score_values) / len(
            score_values
        )
        std_dev = variance**0.5

        # 95% confidence interval (approximately 2 standard deviations)
        margin = 2 * std_dev
        lower = max(0.0, avg_score - margin)
        upper = min(1.0, avg_score + margin)

        return (lower, upper)


class AmendmentOrchestrationService:
    """
    Domain service for orchestrating complex amendment workflows.

    Manages the multi-step democratic amendment process including
    public consultation, expert review, and approval workflows.
    """

    def __init__(
        self,
        amendment_repository: "AmendmentRepository",
        consultation_service: "ConsultationService",
        notification_service: "NotificationService",
    ):
        """Initialize orchestration service with dependencies."""
        self.amendment_repo = amendment_repository
        self.consultation_service = consultation_service
        self.notification_service = notification_service

    async def orchestrate_amendment_process(
        self, proposal: AmendmentProposal
    ) -> "AmendmentWorkflow":
        """
        Orchestrate the complete democratic amendment process.

        This coordinates the multi-step workflow:
        1. Impact analysis
        2. Public consultation (if required)
        3. Expert review (if required)
        4. Formal verification
        5. Final approval
        """
        logger.info(f"Starting amendment orchestration for {proposal.id}")

        workflow = AmendmentWorkflow(proposal)

        # Determine required steps based on amendment characteristics
        required_steps = self._determine_required_steps(proposal)
        workflow.set_required_steps(required_steps)

        # Start with impact analysis
        await self._initiate_impact_analysis(proposal, workflow)

        return workflow

    def _determine_required_steps(self, proposal: AmendmentProposal) -> List[str]:
        """Determine which steps are required for this amendment."""

        steps = ["impact_analysis"]  # Always required

        # Check if public consultation is required
        consultation_spec = PublicConsultationRequiredSpec()
        if consultation_spec.is_satisfied_by(proposal):
            steps.append("public_consultation")

        # Check if expert review is required
        expert_review_spec = ExpertReviewRequiredSpec()
        if expert_review_spec.is_satisfied_by(proposal):
            steps.append("expert_review")

        # Always include formal verification and approval
        steps.extend(["formal_verification", "approval"])

        return steps

    async def _initiate_impact_analysis(
        self, proposal: AmendmentProposal, workflow: "AmendmentWorkflow"
    ) -> None:
        """Initiate impact analysis for the amendment."""

        logger.info(f"Initiating impact analysis for amendment {proposal.id}")

        # This would trigger a request to the Multi-Agent Coordination context
        # For now, we'll simulate the impact analysis

        # Analyze affected principles
        affected_principles = [
            amendment.principle_id for amendment in proposal.amendments
        ]

        # Estimate impact scope
        impact_scope = self._estimate_impact_scope(proposal)

        # Create impact analysis result
        analysis_result = {
            "affected_principles": affected_principles,
            "impact_scope": impact_scope,
            "risk_assessment": self._assess_risks(proposal),
            "stakeholder_groups": self._identify_stakeholders(proposal),
        }

        workflow.complete_step("impact_analysis", analysis_result)

        # Move to next step
        await self._proceed_to_next_step(proposal, workflow)

    def _estimate_impact_scope(self, proposal: AmendmentProposal) -> str:
        """Estimate the scope of impact for the amendment."""

        if len(proposal.amendments) == 1:
            return "limited"
        elif len(proposal.amendments) <= 3:
            return "moderate"
        else:
            return "extensive"

    def _assess_risks(self, proposal: AmendmentProposal) -> List[str]:
        """Assess potential risks of the amendment."""

        risks = []

        # Check for high-priority principle modifications
        high_priority_spec = HighPriorityPrincipleSpec()
        for amendment in proposal.amendments:
            if amendment.new_priority and amendment.new_priority.is_high_priority():
                risks.append("Modification of high-priority principle")

        # Check for scope expansions
        for amendment in proposal.amendments:
            if amendment.new_scope and amendment.new_scope.is_universal():
                risks.append("Scope expansion to universal application")

        return risks

    def _identify_stakeholders(self, proposal: AmendmentProposal) -> List[str]:
        """Identify relevant stakeholder groups for the amendment."""

        stakeholders = ["general_public"]  # Always include general public

        # Add domain-specific stakeholders based on amendment scope
        # This would analyze the amendment content and scope

        return stakeholders

    async def _proceed_to_next_step(
        self, proposal: AmendmentProposal, workflow: "AmendmentWorkflow"
    ) -> None:
        """Proceed to the next step in the workflow."""

        next_step = workflow.get_next_step()

        if next_step == "public_consultation":
            await self._initiate_public_consultation(proposal, workflow)
        elif next_step == "expert_review":
            await self._initiate_expert_review(proposal, workflow)
        elif next_step == "formal_verification":
            await self._initiate_formal_verification(proposal, workflow)
        elif next_step == "approval":
            await self._initiate_approval_process(proposal, workflow)

    async def _initiate_public_consultation(
        self, proposal: AmendmentProposal, workflow: "AmendmentWorkflow"
    ) -> None:
        """Initiate public consultation process."""

        logger.info(f"Initiating public consultation for amendment {proposal.id}")

        # Start consultation period
        from datetime import timedelta

        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)  # 30-day consultation

        proposal.start_public_consultation(
            start_date=start_date, end_date=end_date, required_participants=100
        )

        # Notify stakeholders
        await self.notification_service.notify_consultation_start(proposal)

        workflow.complete_step(
            "public_consultation",
            {"start_date": start_date, "end_date": end_date, "notification_sent": True},
        )

    async def _initiate_expert_review(
        self, proposal: AmendmentProposal, workflow: "AmendmentWorkflow"
    ) -> None:
        """Initiate expert review process."""

        logger.info(f"Initiating expert review for amendment {proposal.id}")

        # This would coordinate with external expert systems
        # For now, simulate expert review

        expert_review_result = {
            "technical_feasibility": "high",
            "legal_compliance": "verified",
            "implementation_complexity": "medium",
            "recommendations": ["Consider phased implementation"],
        }

        workflow.complete_step("expert_review", expert_review_result)

        await self._proceed_to_next_step(proposal, workflow)

    async def _initiate_formal_verification(
        self, proposal: AmendmentProposal, workflow: "AmendmentWorkflow"
    ) -> None:
        """Initiate formal verification process."""

        logger.info(f"Initiating formal verification for amendment {proposal.id}")

        # This would integrate with the Formal Verification context
        # For now, simulate verification

        verification_result = {
            "logical_consistency": True,
            "safety_properties": "maintained",
            "formal_proof": "valid",
        }

        workflow.complete_step("formal_verification", verification_result)

        await self._proceed_to_next_step(proposal, workflow)

    async def _initiate_approval_process(
        self, proposal: AmendmentProposal, workflow: "AmendmentWorkflow"
    ) -> None:
        """Initiate final approval process."""

        logger.info(f"Initiating approval process for amendment {proposal.id}")

        # Compile all workflow results for final decision
        approval_package = workflow.compile_approval_package()

        # Make approval decision based on all evidence
        approval_decision = self._make_approval_decision(approval_package)

        workflow.complete_step(
            "approval",
            {"decision": approval_decision, "approval_package": approval_package},
        )

        if approval_decision == "approved":
            # Process the approved amendment
            await self._process_approved_amendment(proposal)

        logger.info(f"Amendment {proposal.id} process completed: {approval_decision}")

    def _make_approval_decision(self, approval_package: Dict[str, Any]) -> str:
        """Make final approval decision based on workflow results."""

        # Check public consultation results
        if "public_consultation" in approval_package:
            consultation = approval_package["public_consultation"]
            if not consultation.get("majority_support", False):
                return "rejected"

        # Check formal verification results
        if "formal_verification" in approval_package:
            verification = approval_package["formal_verification"]
            if not verification.get("logical_consistency", False):
                return "rejected"

        # Check expert review
        if "expert_review" in approval_package:
            review = approval_package["expert_review"]
            if review.get("technical_feasibility") == "low":
                return "rejected"

        return "approved"

    async def _process_approved_amendment(self, proposal: AmendmentProposal) -> None:
        """Process an approved amendment."""

        # This would integrate with the Constitution aggregate
        # to actually apply the amendments

        logger.info(f"Processing approved amendment {proposal.id}")

        # Save the approved proposal
        await self.amendment_repo.save(proposal)

        # Notify stakeholders of approval
        await self.notification_service.notify_amendment_approved(proposal)


class ConflictResolutionService:
    """
    Domain service for resolving conflicts between constitutional principles.

    Provides sophisticated conflict detection and resolution algorithms
    that consider precedence, scope, and meta-rule applications.
    """

    def __init__(self, meta_rule_repository: "MetaRuleRepository"):
        """Initialize conflict resolution service."""
        self.meta_rule_repo = meta_rule_repository

    async def resolve_principle_conflict(
        self, conflict: ConflictAnalysis, tenant_id: TenantId
    ) -> str:
        """
        Resolve a conflict between principles using meta-rules and precedence.

        Returns a resolution strategy that can be applied.
        """
        logger.info(f"Resolving principle conflict: {conflict.conflict_type}")

        # Get applicable meta-rules
        meta_rules = await self.meta_rule_repo.find_applicable_to_conflict(
            conflict, tenant_id
        )

        if meta_rules:
            # Apply highest precedence meta-rule
            highest_precedence = max(meta_rules, key=lambda mr: mr.precedence_level)
            resolution = highest_precedence.apply_to_conflict(conflict)

            logger.info(f"Conflict resolved using meta-rule: {highest_precedence.name}")
            return resolution

        # Fallback to built-in resolution strategies
        if conflict.conflict_type == "priority":
            return self._resolve_priority_conflict(conflict)
        elif conflict.conflict_type == "scope":
            return self._resolve_scope_conflict(conflict)
        elif conflict.conflict_type == "logical":
            return self._resolve_logical_conflict(conflict)
        else:
            return "escalate_to_human_oversight"

    def _resolve_priority_conflict(self, conflict: ConflictAnalysis) -> str:
        """Resolve conflicts based on principle priorities."""
        return "apply_higher_priority_principle"

    def _resolve_scope_conflict(self, conflict: ConflictAnalysis) -> str:
        """Resolve conflicts by narrowing principle scopes."""
        return "narrow_scope_to_eliminate_overlap"

    def _resolve_logical_conflict(self, conflict: ConflictAnalysis) -> str:
        """Resolve logical contradictions between principles."""
        if conflict.severity == ViolationSeverity.CRITICAL:
            return "escalate_to_constitutional_council"
        else:
            return "apply_temporal_precedence"


class PrincipleEvaluationService:
    """
    Domain service for evaluating individual principles.

    Provides standardized evaluation logic for assessing how well
    actions comply with specific constitutional principles.
    """

    def evaluate_principle_compliance(
        self, principle: Principle, action: Dict[str, Any], context: Dict[str, Any]
    ) -> ComplianceScore:
        """
        Evaluate compliance of an action with a specific principle.

        This uses the principle's validation criteria to assess compliance.
        """
        logger.debug(f"Evaluating compliance with principle: {principle.name}")

        # Check if principle applies to this context
        if not self._principle_applies(principle, action, context):
            return ComplianceScore(
                overall_score=1.0,
                principle_scores={str(principle.id): 1.0},
                violations=[],
                confidence_interval=(1.0, 1.0),
                calculated_at=datetime.utcnow(),
            )

        # Evaluate based on validation criteria type
        if principle.validation_criteria.criteria_type == "logical":
            score = self._evaluate_logical_criteria(principle, action, context)
        elif principle.validation_criteria.criteria_type == "quantitative":
            score = self._evaluate_quantitative_criteria(principle, action, context)
        elif principle.validation_criteria.criteria_type == "qualitative":
            score = self._evaluate_qualitative_criteria(principle, action, context)
        else:
            logger.warning(
                f"Unknown criteria type: {principle.validation_criteria.criteria_type}"
            )
            score = 0.5  # Conservative default

        violations = []
        if score < 0.8:  # Threshold for violation
            violations.append(
                ViolationDetail(
                    principle_id=str(principle.id),
                    violation_type="compliance_threshold",
                    severity=(
                        ViolationSeverity.MEDIUM
                        if score > 0.5
                        else ViolationSeverity.HIGH
                    ),
                    description=f"Action scored {score} against principle {principle.name}",
                    evidence={"action": action, "context": context, "score": score},
                    detected_at=datetime.utcnow(),
                )
            )

        return ComplianceScore(
            overall_score=score,
            principle_scores={str(principle.id): score},
            violations=violations,
            confidence_interval=(max(0.0, score - 0.1), min(1.0, score + 0.1)),
            calculated_at=datetime.utcnow(),
        )

    def _principle_applies(
        self, principle: Principle, action: Dict[str, Any], context: Dict[str, Any]
    ) -> bool:
        """Check if principle applies to the given action and context."""
        spec = ApplicablePrincipleSpec(context)
        return spec.is_satisfied_by(principle)

    def _evaluate_logical_criteria(
        self, principle: Principle, action: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """Evaluate logical validation criteria."""
        # This would parse and evaluate the logical expression
        # For now, return a simplified evaluation
        expression = principle.validation_criteria.expression

        # Simple keyword-based evaluation
        if "privacy" in expression.lower():
            return 1.0 if action.get("preserves_privacy", True) else 0.0
        elif "fairness" in expression.lower():
            return 1.0 if action.get("is_fair", True) else 0.0
        elif "transparency" in expression.lower():
            return 1.0 if action.get("is_transparent", True) else 0.0

        return 0.8  # Default reasonable compliance

    def _evaluate_quantitative_criteria(
        self, principle: Principle, action: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """Evaluate quantitative validation criteria."""
        threshold = principle.validation_criteria.threshold
        if threshold is None:
            return 0.8

        # Extract numeric value from action based on expression
        expression = principle.validation_criteria.expression

        # Simple metric evaluation
        if "accuracy" in expression:
            accuracy = action.get("accuracy", 0.8)
            return 1.0 if accuracy >= threshold else accuracy / threshold
        elif "latency" in expression:
            latency = action.get("latency_ms", 100)
            return 1.0 if latency <= threshold else threshold / latency

        return 0.8

    def _evaluate_qualitative_criteria(
        self, principle: Principle, action: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """Evaluate qualitative validation criteria."""
        # This would use NLP or other qualitative assessment methods
        # For now, return a simplified evaluation

        expression = principle.validation_criteria.expression

        # Simple sentiment-based evaluation
        if "positive" in expression:
            return 0.9
        elif "negative" in expression:
            return 0.3

        return 0.7  # Neutral default


# Mock classes for type hints (these would be defined in the infrastructure layer)
class AmendmentWorkflow:
    """Mock workflow class for type hints."""

    def __init__(self, proposal: AmendmentProposal):
        self.proposal = proposal
        self.steps = []
        self.completed_steps = {}

    def set_required_steps(self, steps: List[str]) -> None:
        self.steps = steps

    def complete_step(self, step: str, result: Dict[str, Any]) -> None:
        self.completed_steps[step] = result

    def get_next_step(self) -> Optional[str]:
        for step in self.steps:
            if step not in self.completed_steps:
                return step
        return None

    def compile_approval_package(self) -> Dict[str, Any]:
        return self.completed_steps
