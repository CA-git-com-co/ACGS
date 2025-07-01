"""
Agent HITL Decision Engine

High-performance decision engine for agent oversight with sub-5ms latency.
Implements confidence-based escalation with caching and pre-compiled patterns.
"""

import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.hitl_models import (
    AgentConfidenceProfile,
    AgentOperationRequest,
    DecisionStatus,
    EscalationLevel,
    HITLDecision,
    OperationRiskLevel,
)
from ..schemas.hitl_schemas import (
    AgentOperationRequestCreate,
    HITLDecisionResponse,
)

logger = logging.getLogger(__name__)


class DecisionCache:
    """Redis-based caching for HITL decisions."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_pool = redis.ConnectionPool.from_url(redis_url)
        self.redis_client = redis.Redis(connection_pool=self.redis_pool)

        # Cache TTLs
        self.confidence_ttl = 3600  # 1 hour
        self.pattern_ttl = 86400  # 24 hours
        self.decision_ttl = 604800  # 7 days

    async def get_agent_confidence(self, agent_id: str) -> dict[str, Any] | None:
        """Get cached agent confidence profile."""
        try:
            key = f"agent_confidence:{agent_id}"
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.warning(f"Cache get failed for agent confidence {agent_id}: {e}")
            return None

    async def set_agent_confidence(
        self, agent_id: str, confidence_data: dict[str, Any]
    ) -> None:
        """Cache agent confidence profile."""
        try:
            key = f"agent_confidence:{agent_id}"
            await self.redis_client.setex(
                key, self.confidence_ttl, json.dumps(confidence_data, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache set failed for agent confidence {agent_id}: {e}")

    async def get_decision_pattern(self, pattern_hash: str) -> dict[str, Any] | None:
        """Get cached decision pattern."""
        try:
            key = f"decision_pattern:{pattern_hash}"
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.warning(f"Cache get failed for decision pattern {pattern_hash}: {e}")
            return None

    async def set_decision_pattern(
        self, pattern_hash: str, decision_data: dict[str, Any]
    ) -> None:
        """Cache decision pattern."""
        try:
            key = f"decision_pattern:{pattern_hash}"
            await self.redis_client.setex(
                key, self.pattern_ttl, json.dumps(decision_data, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache set failed for decision pattern {pattern_hash}: {e}")

    async def increment_metric(self, metric_name: str, value: int = 1) -> None:
        """Increment a metric counter."""
        try:
            key = f"metric:{metric_name}"
            await self.redis_client.incrby(key, value)
            await self.redis_client.expire(key, 86400)  # 24 hours
        except Exception as e:
            logger.warning(f"Metric increment failed for {metric_name}: {e}")


class HITLDecisionEngine:
    """
    High-performance HITL decision engine with sub-5ms latency for automated decisions.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.cache = DecisionCache(redis_url)
        self.constitutional_hash = "cdd01ef066bc6cf2"

        # Performance configuration
        self.max_decision_time_ms = 5.0  # Target for Level 1 decisions
        self.cache_enabled = True

        # Escalation thresholds
        self.escalation_thresholds = {
            "level_1_confidence": 0.9,  # Automated approval
            "level_2_confidence": 0.7,  # Automated with notification
            "level_3_confidence": 0.5,  # Human approval required
        }

        # Risk weights
        self.operation_risk_weights = {
            "code_generation": 0.3,
            "code_modification": 0.5,
            "deployment": 0.8,
            "security_change": 0.9,
            "policy_change": 1.0,
            "constitutional_change": 1.0,
        }

        # Agent compliance weights
        self.compliance_weights = {
            "standard": 1.0,
            "high": 0.8,
            "critical": 0.6,
        }

    async def evaluate_operation(
        self,
        db: AsyncSession,
        operation_request: AgentOperationRequestCreate,
        force_escalation_level: EscalationLevel | None = None,
        bypass_cache: bool = False,
    ) -> HITLDecisionResponse:
        """
        Evaluate an agent operation request and make HITL decision.

        Target: <5ms P99 latency for Level 1 decisions.
        """
        start_time = time.time()

        try:
            # Create operation request record
            db_request = AgentOperationRequest(
                request_id=f"req_{int(time.time() * 1000)}_{operation_request.agent_id}",
                agent_id=operation_request.agent_id,
                operation_type=operation_request.operation_type,
                operation_data=operation_request.operation_data,
                operation_context=operation_request.operation_context,
                risk_level=operation_request.risk_level.value,
                risk_factors=operation_request.risk_factors,
                constitutional_hash=self.constitutional_hash,
                constitutional_principles=operation_request.constitutional_principles,
                requires_constitutional_review=operation_request.requires_constitutional_review,
                expires_at=operation_request.expires_at,
                client_ip=operation_request.client_ip,
                user_agent=operation_request.user_agent,
            )

            db.add(db_request)
            await db.flush()

            # Check cache for similar decision patterns (if not bypassed)
            cache_hit = False
            cached_decision = None

            if self.cache_enabled and not bypass_cache:
                pattern_hash = self._generate_pattern_hash(operation_request)
                cached_decision = await self.cache.get_decision_pattern(pattern_hash)
                cache_hit = cached_decision is not None

            # Get agent confidence profile
            agent_confidence = await self._get_agent_confidence(
                db, operation_request.agent_id
            )

            # Calculate decision if not cached
            if cached_decision:
                escalation_level = EscalationLevel(cached_decision["escalation_level"])
                confidence_score = cached_decision["confidence_score"]
                decision_reasoning = cached_decision["reasoning"]
                risk_assessment = cached_decision["risk_assessment"]
                constitutional_compliance_score = cached_decision[
                    "constitutional_compliance_score"
                ]
            else:
                # Perform real-time decision calculation
                (
                    escalation_level,
                    confidence_score,
                    decision_reasoning,
                    risk_assessment,
                    constitutional_compliance_score,
                ) = await self._calculate_decision(
                    operation_request, agent_confidence, force_escalation_level
                )

                # Cache the decision pattern for future use
                if self.cache_enabled:
                    pattern_hash = self._generate_pattern_hash(operation_request)
                    await self.cache.set_decision_pattern(
                        pattern_hash,
                        {
                            "escalation_level": escalation_level.value,
                            "confidence_score": confidence_score,
                            "reasoning": decision_reasoning,
                            "risk_assessment": risk_assessment,
                            "constitutional_compliance_score": constitutional_compliance_score,
                        },
                    )

            # Determine decision status
            decision_status = (
                DecisionStatus.APPROVED
                if escalation_level == EscalationLevel.LEVEL_1_AUTO_APPROVE
                else DecisionStatus.PENDING
            )
            requires_human_review = escalation_level in [
                EscalationLevel.LEVEL_3_HUMAN_REVIEW,
                EscalationLevel.LEVEL_4_COUNCIL_REVIEW,
            ]

            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000

            # Create decision record
            decision = HITLDecision(
                decision_id=f"dec_{int(time.time() * 1000)}_{operation_request.agent_id}",
                operation_request_id=db_request.id,
                escalation_level=escalation_level.value,
                decision_status=decision_status.value,
                confidence_score=confidence_score,
                decision_reasoning=decision_reasoning,
                risk_assessment=risk_assessment,
                constitutional_compliance_score=constitutional_compliance_score,
                processing_time_ms=processing_time_ms,
                cache_hit=cache_hit,
                decision_algorithm="hitl_v1",
                requires_human_review=requires_human_review,
                constitutional_hash=self.constitutional_hash,
                compliance_verified=constitutional_compliance_score >= 0.8,
                completed_at=(
                    datetime.now(timezone.utc)
                    if decision_status == DecisionStatus.APPROVED
                    else None
                ),
            )

            db.add(decision)
            await db.commit()

            # Update metrics
            await self.cache.increment_metric("decisions_total")
            await self.cache.increment_metric(f"decisions_{escalation_level.value}")
            if cache_hit:
                await self.cache.increment_metric("cache_hits")

            # Log performance warning if too slow
            if processing_time_ms > self.max_decision_time_ms:
                logger.warning(
                    f"Decision took {processing_time_ms:.2f}ms (target: {self.max_decision_time_ms}ms)"
                )

            return HITLDecisionResponse(
                decision_id=decision.decision_id,
                operation_request_id=str(db_request.id),
                escalation_level=escalation_level,
                decision_status=decision_status,
                confidence_score=confidence_score,
                decision_reasoning=decision_reasoning,
                risk_assessment=risk_assessment,
                constitutional_compliance_score=constitutional_compliance_score,
                processing_time_ms=processing_time_ms,
                cache_hit=cache_hit,
                decision_algorithm="hitl_v1",
                requires_human_review=requires_human_review,
                created_at=decision.created_at,
                completed_at=decision.completed_at,
                constitutional_hash=self.constitutional_hash,
                compliance_verified=decision.compliance_verified,
            )

        except Exception as e:
            logger.error(f"Decision evaluation failed: {e}")
            await db.rollback()
            raise

    async def _get_agent_confidence(
        self, db: AsyncSession, agent_id: str
    ) -> dict[str, Any]:
        """Get agent confidence profile with caching."""
        # Try cache first
        if self.cache_enabled:
            cached_confidence = await self.cache.get_agent_confidence(agent_id)
            if cached_confidence:
                return cached_confidence

        # Query database
        result = await db.execute(
            select(AgentConfidenceProfile).where(
                AgentConfidenceProfile.agent_id == agent_id
            )
        )
        profile = result.scalar_one_or_none()

        if profile:
            confidence_data = {
                "overall_confidence_score": profile.overall_confidence_score,
                "operation_type_scores": profile.operation_type_scores,
                "risk_level_scores": profile.risk_level_scores,
                "constitutional_compliance_score": profile.constitutional_compliance_score,
                "total_operations": profile.total_operations,
                "successful_operations": profile.successful_operations,
                "failed_operations": profile.failed_operations,
            }
        else:
            # Default confidence for new agents
            confidence_data = {
                "overall_confidence_score": 0.5,
                "operation_type_scores": {},
                "risk_level_scores": {},
                "constitutional_compliance_score": 0.8,
                "total_operations": 0,
                "successful_operations": 0,
                "failed_operations": 0,
            }

        # Cache the result
        if self.cache_enabled:
            await self.cache.set_agent_confidence(agent_id, confidence_data)

        return confidence_data

    async def _calculate_decision(
        self,
        operation_request: AgentOperationRequestCreate,
        agent_confidence: dict[str, Any],
        force_escalation_level: EscalationLevel | None = None,
    ) -> tuple[EscalationLevel, float, str, dict[str, Any], float]:
        """Calculate HITL decision based on confidence and risk factors."""

        if force_escalation_level:
            return force_escalation_level, 0.5, "Forced escalation level", {}, 0.8

        # Get operation-specific confidence
        operation_confidence = agent_confidence["operation_type_scores"].get(
            operation_request.operation_type,
            agent_confidence["overall_confidence_score"],
        )

        # Calculate risk factor
        operation_risk_weight = self.operation_risk_weights.get(
            operation_request.operation_type, 0.5
        )
        risk_level_weight = {
            OperationRiskLevel.LOW.value: 0.2,
            OperationRiskLevel.MEDIUM.value: 0.5,
            OperationRiskLevel.HIGH.value: 0.8,
            OperationRiskLevel.CRITICAL.value: 1.0,
        }.get(operation_request.risk_level.value, 0.5)

        # Adjust confidence based on risk
        risk_adjusted_confidence = operation_confidence * (
            1.0 - (operation_risk_weight * risk_level_weight * 0.3)
        )

        # Constitutional compliance factor
        constitutional_compliance_score = agent_confidence[
            "constitutional_compliance_score"
        ]
        final_confidence = risk_adjusted_confidence * constitutional_compliance_score

        # Determine escalation level
        if final_confidence >= self.escalation_thresholds["level_1_confidence"]:
            escalation_level = EscalationLevel.LEVEL_1_AUTO_APPROVE
            reasoning = "High confidence automated approval"
        elif final_confidence >= self.escalation_thresholds["level_2_confidence"]:
            escalation_level = EscalationLevel.LEVEL_2_AUTO_NOTIFY
            reasoning = "Medium confidence automated approval with notification"
        elif final_confidence >= self.escalation_thresholds["level_3_confidence"]:
            escalation_level = EscalationLevel.LEVEL_3_HUMAN_REVIEW
            reasoning = "Low confidence requires human review"
        else:
            escalation_level = EscalationLevel.LEVEL_4_COUNCIL_REVIEW
            reasoning = "Very low confidence or critical operation requires Constitutional Council review"

        # Check for constitutional review requirement
        if operation_request.requires_constitutional_review:
            escalation_level = EscalationLevel.LEVEL_4_COUNCIL_REVIEW
            reasoning = "Constitutional review explicitly required"

        # Build risk assessment
        risk_assessment = {
            "operation_risk_weight": operation_risk_weight,
            "risk_level_weight": risk_level_weight,
            "operation_confidence": operation_confidence,
            "risk_adjusted_confidence": risk_adjusted_confidence,
            "final_confidence": final_confidence,
            "constitutional_compliance_score": constitutional_compliance_score,
        }

        return (
            escalation_level,
            final_confidence,
            reasoning,
            risk_assessment,
            constitutional_compliance_score,
        )

    def _generate_pattern_hash(
        self, operation_request: AgentOperationRequestCreate
    ) -> str:
        """Generate hash for decision pattern caching."""
        pattern_data = {
            "operation_type": operation_request.operation_type,
            "risk_level": operation_request.risk_level.value,
            "requires_constitutional_review": operation_request.requires_constitutional_review,
            "constitutional_principles": sorted(
                operation_request.constitutional_principles or []
            ),
        }

        pattern_str = json.dumps(pattern_data, sort_keys=True)
        return hashlib.sha256(pattern_str.encode()).hexdigest()[:16]
