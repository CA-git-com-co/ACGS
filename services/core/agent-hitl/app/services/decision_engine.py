"""
Agent HITL Decision Engine

Core decision-making logic for evaluating agent operations.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.config import settings
from ..models.review import (
    AgentConfidenceProfile,
    AgentOperationReview,
    EscalationLevel,
    ReviewStatus,
    RiskLevel,
)

logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    Decision engine for evaluating agent operations.

    Implements multi-factor decision logic combining:
    - Agent confidence scores
    - Operation risk assessment
    - Historical performance
    - Constitutional compliance
    """

    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.operation_risk_weights = settings.OPERATION_RISK_WEIGHTS

    async def evaluate_operation(
        self,
        db: AsyncSession,
        agent_id: str,
        agent_type: str,
        operation_type: str,
        operation_description: str,
        operation_context: dict[str, Any],
        operation_target: str | None = None,
        request_metadata: dict[str, Any] | None = None,
    ) -> AgentOperationReview:
        """
        Evaluate an agent operation and determine if it requires human review.

        Returns:
            AgentOperationReview with decision and escalation level
        """
        start_time = datetime.utcnow()

        # Generate review ID
        review_id = f"review_{agent_id}_{datetime.utcnow().timestamp()}"

        # Get agent confidence profile
        agent_profile = await self._get_or_create_agent_profile(db, agent_id)

        # Parallel evaluation tasks
        confidence_task = self._calculate_confidence_score(
            agent_id, agent_type, operation_type, operation_context, agent_profile
        )
        risk_task = self._assess_operation_risk(
            operation_type, operation_description, operation_context, operation_target
        )
        compliance_task = self._check_constitutional_compliance(
            agent_id, operation_type, operation_context
        )

        # Execute evaluations in parallel
        (confidence_result, risk_result, compliance_result) = await asyncio.gather(
            confidence_task, risk_task, compliance_task
        )

        # Determine escalation level and decision
        escalation_level, decision, reason = self._determine_escalation_and_decision(
            confidence_result["score"],
            risk_result["score"],
            risk_result["level"],
            compliance_result["violations"],
            agent_profile,
        )

        # Create review record
        review = AgentOperationReview(
            review_id=review_id,
            agent_id=agent_id,
            agent_type=agent_type,
            agent_version=operation_context.get("agent_version", "unknown"),
            operation_type=operation_type,
            operation_description=operation_description,
            operation_context=operation_context,
            operation_target=operation_target,
            confidence_score=confidence_result["score"],
            risk_score=risk_result["score"],
            risk_level=risk_result["level"],
            confidence_factors=confidence_result["factors"],
            risk_factors=risk_result["factors"],
            constitutional_hash=settings.CONSTITUTIONAL_HASH,
            policy_violations=compliance_result["violations"],
            applicable_principles=compliance_result["principles"],
            status=decision["status"],
            escalation_level=escalation_level,
            decision=decision["decision"],
            decision_reason=reason,
            decision_metadata={
                "confidence_threshold": self._get_threshold_for_level(escalation_level),
                "risk_tolerance": agent_profile.risk_tolerance_factor,
                "auto_decision": escalation_level == EscalationLevel.LEVEL_1_AUTO,
            },
            request_id=request_metadata.get("request_id") if request_metadata else None,
            session_id=request_metadata.get("session_id") if request_metadata else None,
            client_ip=request_metadata.get("client_ip") if request_metadata else None,
            metadata=request_metadata or {},
        )

        # If auto-approved, set decision timestamp
        if decision["status"] == ReviewStatus.AUTO_APPROVED:
            review.decided_at = datetime.utcnow()
            review.processing_time_ms = int(
                (review.decided_at - start_time).total_seconds() * 1000
            )

        # Save to database
        db.add(review)
        await db.commit()

        # Update agent profile statistics
        await self._update_agent_profile_stats(db, agent_profile, review)

        logger.info(
            f"Operation evaluated for agent {agent_id}: "
            f"confidence={confidence_result['score']:.2f}, "
            f"risk={risk_result['score']:.2f}, "
            f"escalation_level={escalation_level}, "
            f"decision={decision['decision']}"
        )

        return review

    async def _get_or_create_agent_profile(
        self, db: AsyncSession, agent_id: str
    ) -> AgentConfidenceProfile:
        """Get or create agent confidence profile."""
        result = await db.execute(
            select(AgentConfidenceProfile).where(
                AgentConfidenceProfile.agent_id == agent_id
            )
        )
        profile = result.scalar_one_or_none()

        if not profile:
            profile = AgentConfidenceProfile(agent_id=agent_id)
            db.add(profile)
            await db.commit()

        return profile

    async def _calculate_confidence_score(
        self,
        agent_id: str,
        agent_type: str,
        operation_type: str,
        operation_context: dict[str, Any],
        agent_profile: AgentConfidenceProfile,
    ) -> dict[str, Any]:
        """
        Calculate confidence score for the operation.

        Factors:
        - Base agent type confidence
        - Operation-specific confidence
        - Historical performance adjustment
        - Context-specific factors
        """
        factors = {}

        # Base confidence by agent type
        base_confidence = {
            "coding_agent": 0.85,
            "policy_agent": 0.90,
            "monitoring_agent": 0.95,
            "analysis_agent": 0.88,
            "integration_agent": 0.82,
            "custom_agent": 0.80,
        }.get(agent_type, 0.80)
        factors["base_confidence"] = base_confidence

        # Operation-specific adjustment
        operation_adjustments = agent_profile.operation_confidence_adjustments or {}
        operation_adjustment = operation_adjustments.get(operation_type, 0.0)
        factors["operation_adjustment"] = operation_adjustment

        # Historical performance adjustment
        if (
            agent_profile.total_operations
            >= settings.MIN_AGENT_OPERATIONS_FOR_ADAPTATION
        ):
            if agent_profile.total_operations > 0:
                success_rate = agent_profile.correct_auto_approvals / max(
                    agent_profile.auto_approved_operations, 1
                )
                performance_adjustment = (success_rate - 0.5) * 0.2  # ±0.1 max
                factors["performance_adjustment"] = performance_adjustment
            else:
                performance_adjustment = 0.0
        else:
            performance_adjustment = -0.05  # Penalty for new agents
            factors["new_agent_penalty"] = -0.05

        # Context-specific factors
        context_confidence = await self._evaluate_context_confidence(
            operation_context, agent_type
        )
        factors["context_confidence"] = context_confidence

        # Calculate final score
        confidence_score = min(
            1.0,
            max(
                0.0,
                base_confidence
                + operation_adjustment
                + performance_adjustment
                + agent_profile.base_confidence_adjustment
                + context_confidence,
            ),
        )

        return {
            "score": confidence_score,
            "factors": factors,
        }

    async def _assess_operation_risk(
        self,
        operation_type: str,
        operation_description: str,
        operation_context: dict[str, Any],
        operation_target: str | None = None,
    ) -> dict[str, Any]:
        """Assess risk level of the operation."""
        factors = {}

        # Base risk from operation type
        base_risk = self.operation_risk_weights.get(operation_type, 0.5)
        factors["operation_type_risk"] = base_risk

        # Target sensitivity assessment
        target_risk = 0.0
        if operation_target:
            if any(
                sensitive in operation_target.lower()
                for sensitive in [
                    "config",
                    "secret",
                    "credential",
                    "password",
                    "key",
                    "token",
                    "production",
                    "database",
                    "security",
                    "auth",
                ]
            ):
                target_risk = 0.3
                factors["sensitive_target"] = True

        # Scope assessment
        scope_risk = 0.0
        scope = operation_context.get("scope", {})
        if scope.get("affects_multiple_services", False):
            scope_risk += 0.2
        if scope.get("affects_production", False):
            scope_risk += 0.3
        if scope.get("irreversible", False):
            scope_risk += 0.2
        factors["scope_risk"] = scope_risk

        # Calculate total risk score
        risk_score = min(1.0, base_risk + target_risk + scope_risk)

        # Determine risk level
        if risk_score >= 0.8:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 0.3:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        return {
            "score": risk_score,
            "level": risk_level.value,
            "factors": factors,
        }

    async def _check_constitutional_compliance(
        self,
        agent_id: str,
        operation_type: str,
        operation_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Check operation against constitutional principles."""
        try:
            # Call Constitutional AI service
            response = await self.http_client.post(
                f"{settings.CONSTITUTIONAL_AI_URL}/api/v1/evaluate",
                json={
                    "agent_id": agent_id,
                    "operation_type": operation_type,
                    "operation_context": operation_context,
                    "constitutional_hash": settings.CONSTITUTIONAL_HASH,
                },
                timeout=5.0,
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "violations": result.get("violations", []),
                    "principles": result.get("applicable_principles", []),
                    "compliance_score": result.get("compliance_score", 1.0),
                }
        except Exception as e:
            logger.error(f"Constitutional compliance check failed: {e}")

        # Default to no violations if service unavailable
        return {
            "violations": [],
            "principles": [],
            "compliance_score": 1.0,
        }

    async def _evaluate_context_confidence(
        self, operation_context: dict[str, Any], agent_type: str
    ) -> float:
        """Evaluate confidence based on operation context."""
        confidence_adjustment = 0.0

        # Check for explicit confidence indicators
        if "confidence_indicators" in operation_context:
            indicators = operation_context["confidence_indicators"]
            if indicators.get("previous_success", False):
                confidence_adjustment += 0.05
            if indicators.get("similar_operations_approved", 0) > 10:
                confidence_adjustment += 0.03
            if indicators.get("user_requested", False):
                confidence_adjustment += 0.02

        # Check for uncertainty indicators
        if "uncertainty_factors" in operation_context:
            factors = operation_context["uncertainty_factors"]
            if factors.get("ambiguous_intent", False):
                confidence_adjustment -= 0.1
            if factors.get("complex_operation", False):
                confidence_adjustment -= 0.05
            if factors.get("novel_pattern", False):
                confidence_adjustment -= 0.08

        return confidence_adjustment

    def _determine_escalation_and_decision(
        self,
        confidence_score: float,
        risk_score: float,
        risk_level: str,
        policy_violations: list[str],
        agent_profile: AgentConfidenceProfile,
    ) -> tuple[int, dict[str, str], str]:
        """Determine escalation level and decision based on scores."""

        # Check for policy violations - always escalate
        if policy_violations:
            return (
                EscalationLevel.LEVEL_4_CONSTITUTIONAL_COUNCIL,
                {"status": ReviewStatus.ESCALATED.value, "decision": None},
                f"Policy violations detected: {', '.join(policy_violations)}",
            )

        # Adjust confidence threshold based on risk
        risk_adjusted_confidence = confidence_score * (2.0 - risk_score)

        # Check against escalation thresholds
        if risk_adjusted_confidence >= settings.ESCALATION_LEVEL_1_THRESHOLD:
            if risk_level in [RiskLevel.LOW.value, RiskLevel.MEDIUM.value]:
                return (
                    EscalationLevel.LEVEL_1_AUTO,
                    {
                        "status": ReviewStatus.AUTO_APPROVED.value,
                        "decision": "approved",
                    },
                    f"High confidence ({confidence_score:.2f}) with acceptable risk",
                )

        if risk_level == RiskLevel.CRITICAL.value:
            return (
                EscalationLevel.LEVEL_4_CONSTITUTIONAL_COUNCIL,
                {"status": ReviewStatus.ESCALATED.value, "decision": None},
                "Critical risk operation requires Constitutional Council review",
            )

        if risk_adjusted_confidence >= settings.ESCALATION_LEVEL_2_THRESHOLD:
            return (
                EscalationLevel.LEVEL_2_TEAM_LEAD,
                {"status": ReviewStatus.PENDING.value, "decision": None},
                f"Moderate confidence ({confidence_score:.2f}) requires team lead review",
            )

        if risk_adjusted_confidence >= settings.ESCALATION_LEVEL_3_THRESHOLD:
            return (
                EscalationLevel.LEVEL_3_DOMAIN_EXPERT,
                {"status": ReviewStatus.PENDING.value, "decision": None},
                f"Low confidence ({confidence_score:.2f}) requires domain expert review",
            )

        return (
            EscalationLevel.LEVEL_4_CONSTITUTIONAL_COUNCIL,
            {"status": ReviewStatus.ESCALATED.value, "decision": None},
            f"Very low confidence ({confidence_score:.2f}) requires Constitutional Council review",
        )

    def _get_threshold_for_level(self, escalation_level: int) -> float:
        """Get confidence threshold for escalation level."""
        return {
            EscalationLevel.LEVEL_1_AUTO: settings.ESCALATION_LEVEL_1_THRESHOLD,
            EscalationLevel.LEVEL_2_TEAM_LEAD: settings.ESCALATION_LEVEL_2_THRESHOLD,
            EscalationLevel.LEVEL_3_DOMAIN_EXPERT: settings.ESCALATION_LEVEL_3_THRESHOLD,
            EscalationLevel.LEVEL_4_CONSTITUTIONAL_COUNCIL: settings.ESCALATION_LEVEL_4_THRESHOLD,
        }.get(escalation_level, 0.0)

    async def _update_agent_profile_stats(
        self,
        db: AsyncSession,
        profile: AgentConfidenceProfile,
        review: AgentOperationReview,
    ) -> None:
        """Update agent profile statistics after evaluation."""
        profile.total_operations += 1

        if review.status == ReviewStatus.AUTO_APPROVED.value:
            profile.auto_approved_operations += 1

        await db.commit()

    async def close(self):
        """Clean up resources."""
        await self.http_client.aclose()
