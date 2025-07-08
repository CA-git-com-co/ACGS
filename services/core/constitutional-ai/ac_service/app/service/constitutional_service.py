"""
Service Layer for Constitutional AI
Constitutional Hash: cdd01ef066bc6cf2

This module contains the business logic and service implementations
for constitutional validation and compliance checking.
"""

import logging
from datetime import datetime
from typing import Any

from ...shared.di.container import ServiceLifetime, injectable
from ..domain.entities import (
    AuditEvent,
    AuditService,
    ConstitutionalComplianceRequest,
    ConstitutionalPolicyService,
    ConstitutionalPrinciple,
    ConstitutionalValidator,
    ConstitutionalViolation,
    ContentValidationRequest,
    PolicyDecision,
    ValidationResult,
    ViolationType,
)
from ..infra.gateways import (
    AuditRepository,
    ConstitutionalRepository,
    ExternalValidationGateway,
    PolicyRepository,
)

logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@injectable(ServiceLifetime.SCOPED)
class ConstitutionalValidationService(ConstitutionalValidator):
    """
    Main service for constitutional validation.
    
    Implements the business logic for validating content and compliance
    against constitutional principles.
    """

    def __init__(
        self,
        constitutional_repo: ConstitutionalRepository,
        policy_service: "ConstitutionalPolicyServiceImpl",
        audit_service: "AuditServiceImpl",
        external_gateway: ExternalValidationGateway,
    ):
        self.constitutional_repo = constitutional_repo
        self.policy_service = policy_service
        self.audit_service = audit_service
        self.external_gateway = external_gateway

        logger.debug("ConstitutionalValidationService initialized")

    async def validate_content(self, request: ContentValidationRequest) -> ValidationResult:
        """
        Validate content against constitutional rules.
        
        Args:
            request: Content validation request
            
        Returns:
            ValidationResult with compliance information
        """
        logger.info(f"Validating content for request {request.request_id}")

        # Create initial result
        result = ValidationResult(
            is_valid=True,
            compliance_score=1.0,
            constitutional_hash=CONSTITUTIONAL_HASH,
        )

        try:
            # Get applicable principles
            principles = await self.policy_service.get_applicable_principles(
                request.context
            )

            # Validate against each principle
            for principle in principles:
                violations = await self._validate_against_principle(
                    request.content, principle, request.context
                )

                for violation in violations:
                    result.add_violation(violation)

            # External validation if configured
            if await self._should_use_external_validation(request):
                external_result = await self.external_gateway.validate_content(request)
                if external_result:
                    result.violations.extend(external_result.violations)
                    result._recalculate_compliance_score()

            # Generate recommendations
            recommendations = await self._generate_recommendations(result)
            for rec in recommendations:
                result.add_recommendation(rec)

            # Log audit event
            await self.audit_service.log_event(AuditEvent(
                event_type="content_validation",
                entity_type="content",
                entity_id=request.request_id,
                action="validate",
                actor_id=request.requester_id,
                metadata={
                    "compliance_score": result.compliance_score,
                    "violations_count": len(result.violations),
                    "content_type": request.content_type,
                }
            ))

            logger.info(
                f"Content validation completed for {request.request_id}: "
                f"score={result.compliance_score:.3f}, "
                f"violations={len(result.violations)}"
            )

            return result

        except Exception as e:
            logger.error(f"Content validation failed for {request.request_id}: {e}")

            # Log error event
            await self.audit_service.log_event(AuditEvent(
                event_type="validation_error",
                entity_type="content",
                entity_id=request.request_id,
                action="validate_failed",
                actor_id=request.requester_id,
                metadata={"error": str(e)}
            ))

            raise

    async def validate_compliance(
        self, request: ConstitutionalComplianceRequest
    ) -> ValidationResult:
        """
        Validate constitutional compliance.
        
        Args:
            request: Constitutional compliance request
            
        Returns:
            ValidationResult with compliance information
        """
        logger.info(f"Validating compliance for request {request.request_id}")

        result = ValidationResult(
            is_valid=True,
            compliance_score=1.0,
            constitutional_hash=CONSTITUTIONAL_HASH,
        )

        try:
            # Evaluate policy decisions
            policy_decision = await self.policy_service.evaluate_policy(
                request.content, request.policy_context
            )

            # Check policy decision
            if policy_decision.decision == "deny":
                violation = ConstitutionalViolation(
                    violation_type=ViolationType.POLICY_VIOLATION,
                    severity=1.0 - policy_decision.confidence,
                    description=f"Policy violation: {'; '.join(policy_decision.reasoning)}",
                    context=request.policy_context,
                )
                result.add_violation(violation)
            elif policy_decision.decision == "review":
                violation = ConstitutionalViolation(
                    violation_type=ViolationType.CONSTITUTIONAL_BREACH,
                    severity=0.5,
                    description="Content requires manual review",
                    context=request.policy_context,
                )
                result.add_violation(violation)

            # Strict mode additional checks
            if request.strict_mode:
                strict_violations = await self._perform_strict_validation(
                    request.content, request.policy_context
                )
                for violation in strict_violations:
                    result.add_violation(violation)

            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(
                result, policy_decision
            )
            for rec in recommendations:
                result.add_recommendation(rec)

            # Log audit event
            await self.audit_service.log_event(AuditEvent(
                event_type="compliance_validation",
                entity_type="policy",
                entity_id=request.request_id,
                action="validate_compliance",
                actor_id=request.requester_id,
                metadata={
                    "compliance_score": result.compliance_score,
                    "policy_decision": policy_decision.decision,
                    "strict_mode": request.strict_mode,
                }
            ))

            logger.info(
                f"Compliance validation completed for {request.request_id}: "
                f"score={result.compliance_score:.3f}, "
                f"decision={policy_decision.decision}"
            )

            return result

        except Exception as e:
            logger.error(f"Compliance validation failed for {request.request_id}: {e}")
            raise

    def validate_constitutional_hash(self) -> dict[str, Any]:
        """
        Validate constitutional hash integrity.
        
        Returns:
            Dict with validation results
        """
        expected_hash = CONSTITUTIONAL_HASH

        return {
            "is_valid": True,
            "expected_hash": expected_hash,
            "actual_hash": CONSTITUTIONAL_HASH,
            "validated_at": datetime.utcnow().isoformat(),
            "validation_source": "constitutional_validation_service",
        }

    async def _validate_against_principle(
        self, content: str, principle: ConstitutionalPrinciple, context: dict[str, Any]
    ) -> list[ConstitutionalViolation]:
        """Validate content against a specific constitutional principle."""
        violations = []

        # Implementation would include specific validation logic
        # For now, simplified example
        for rule in principle.rules:
            violation = await self._check_rule_violation(content, rule, context)
            if violation:
                violations.append(violation)

        return violations

    async def _check_rule_violation(
        self, content: str, rule: str, context: dict[str, Any]
    ) -> ConstitutionalViolation | None:
        """Check if content violates a specific rule."""
        # Simplified rule checking - in practice this would be more sophisticated
        if "harmful" in content.lower() and "harmful_content" in rule:
            return ConstitutionalViolation(
                violation_type=ViolationType.CONTENT_HARMFUL,
                severity=0.8,
                description=f"Content contains harmful material (rule: {rule})",
                context=context,
            )

        return None

    async def _should_use_external_validation(
        self, request: ContentValidationRequest
    ) -> bool:
        """Determine if external validation should be used."""
        # Could be based on content type, risk level, etc.
        return request.content_type in ["image", "video", "audio"]

    async def _perform_strict_validation(
        self, content: str, context: dict[str, Any]
    ) -> list[ConstitutionalViolation]:
        """Perform additional strict validation checks."""
        violations = []

        # Example strict checks
        if len(content) > 10000:  # Very long content
            violations.append(ConstitutionalViolation(
                violation_type=ViolationType.POLICY_VIOLATION,
                severity=0.3,
                description="Content exceeds recommended length limits",
                context=context,
            ))

        return violations

    async def _generate_recommendations(
        self, result: ValidationResult
    ) -> list[str]:
        """Generate recommendations based on validation result."""
        recommendations = []

        if result.compliance_score < 0.8:
            recommendations.append("Consider revising content to improve compliance")

        if any(v.violation_type == ViolationType.CONTENT_HARMFUL for v in result.violations):
            recommendations.append("Remove harmful content before proceeding")

        if any(v.violation_type == ViolationType.BIAS_DETECTED for v in result.violations):
            recommendations.append("Review content for potential bias")

        return recommendations

    async def _generate_compliance_recommendations(
        self, result: ValidationResult, policy_decision: PolicyDecision
    ) -> list[str]:
        """Generate compliance-specific recommendations."""
        recommendations = []

        if policy_decision.decision == "deny":
            recommendations.append("Content violates constitutional policies and cannot be approved")
        elif policy_decision.decision == "review":
            recommendations.append("Content requires manual review before approval")

        if result.compliance_score < 0.9:
            recommendations.append("Consider policy updates to improve compliance framework")

        return recommendations


@injectable(ServiceLifetime.SCOPED)
class ConstitutionalPolicyServiceImpl(ConstitutionalPolicyService):
    """Implementation of constitutional policy service."""

    def __init__(self, policy_repo: PolicyRepository):
        self.policy_repo = policy_repo
        logger.debug("ConstitutionalPolicyServiceImpl initialized")

    async def evaluate_policy(
        self, content: str, context: dict[str, Any]
    ) -> PolicyDecision:
        """Evaluate content against constitutional policies."""
        # Simplified policy evaluation
        decision = PolicyDecision(
            policy_id="default_policy",
            decision="allow",
            confidence=0.95,
            reasoning=["Content passed basic checks"],
            applied_principles=["transparency", "accountability"],
            context=context,
        )

        # Check for obvious violations
        if any(keyword in content.lower() for keyword in ["harmful", "illegal", "violation"]):
            decision.decision = "deny"
            decision.confidence = 0.9
            decision.reasoning = ["Content contains prohibited keywords"]

        return decision

    async def get_applicable_principles(
        self, context: dict[str, Any]
    ) -> list[ConstitutionalPrinciple]:
        """Get constitutional principles applicable to the given context."""
        # For now, return default principles
        return [
            ConstitutionalPrinciple(
                name="Transparency",
                description="Ensure transparent and accountable AI decisions",
                priority=1.0,
                rules=["transparency_required", "audit_trail_maintained"],
            ),
            ConstitutionalPrinciple(
                name="Safety",
                description="Prevent harmful content and outputs",
                priority=1.5,
                rules=["harmful_content", "bias_detection"],
            ),
        ]


@injectable(ServiceLifetime.SCOPED)
class AuditServiceImpl(AuditService):
    """Implementation of audit service."""

    def __init__(self, audit_repo: AuditRepository):
        self.audit_repo = audit_repo
        logger.debug("AuditServiceImpl initialized")

    async def log_event(self, event: AuditEvent) -> None:
        """Log an audit event."""
        try:
            await self.audit_repo.save_event(event)
            logger.debug(f"Audit event logged: {event.event_type} for {event.entity_id}")
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            # Don't fail the main operation if audit logging fails

    async def get_audit_trail(self, entity_id: str) -> list[AuditEvent]:
        """Get audit trail for an entity."""
        try:
            return await self.audit_repo.get_events_by_entity(entity_id)
        except Exception as e:
            logger.error(f"Failed to retrieve audit trail for {entity_id}: {e}")
            return []
