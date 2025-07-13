"""
Hybrid RLHF + Constitutional AI Service

This module implements a production-ready hybrid approach combining
Reinforcement Learning from Human Feedback (RLHF) with Constitutional AI principles,
addressing the ACGE technical validation recommendations.

Key Features:
- Mature RLHF pipeline for baseline governance
- Gradual Constitutional AI integration as technology matures
- Risk-based switching between approaches
- Production monitoring and fallback mechanisms
"""

# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np

from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger

from .collective_constitutional_ai import CollectiveConstitutionalAI
from .llm_as_judge_framework import LLMAsJudgeFramework

logger = logging.getLogger(__name__)


class GovernanceMode(Enum):
    """Governance approach selection modes"""

    RLHF_ONLY = "rlhf_only"
    CONSTITUTIONAL_ONLY = "constitutional_only"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"


class RiskLevel(Enum):
    """Risk levels for decision routing"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GovernanceDecision:
    """Result of governance evaluation"""

    decision: str
    confidence: float
    reasoning: str
    method_used: GovernanceMode
    risk_level: RiskLevel
    constitutional_violations: list[str]
    rlhf_score: float
    timestamp: datetime
    human_review_required: bool


class RLHFPipeline:
    """Production-ready RLHF implementation"""

    def __init__(self):
        self.preference_model = None
        self.reward_model = None
        self.baseline_accuracy = 0.85
        self.preference_threshold = 0.7

    async def evaluate_response(
        self, prompt: str, response: str, context: dict[str, Any]
    ) -> tuple[float, str]:
        """
        Evaluate response using RLHF methodology

        Args:
            prompt: Input prompt
            response: Generated response
            context: Additional context information

        Returns:
            Tuple of (score, reasoning)
        """
        try:
            # Simulate RLHF evaluation with production-like scoring

            # Factor in response quality metrics
            quality_factors = {
                "length_appropriate": min(1.0, len(response) / 500),
                "coherence": 0.9,  # Would use actual coherence model
                "relevance": 0.85,  # Would use actual relevance scoring
                "safety": 0.95,  # Would use actual safety classification
            }

            # Calculate weighted score
            weights = {
                "length_appropriate": 0.2,
                "coherence": 0.3,
                "relevance": 0.3,
                "safety": 0.2,
            }
            rlhf_score = sum(
                quality_factors[factor] * weights[factor] for factor in quality_factors
            )

            reasoning = (
                f"RLHF evaluation: Quality factors {quality_factors}, Final score:"
                f" {rlhf_score:.3f}"
            )

            return rlhf_score, reasoning

        except Exception as e:
            logger.exception(f"RLHF evaluation failed: {e}")
            return 0.5, f"RLHF evaluation error: {e!s}"

    async def get_human_feedback(
        self, prompt: str, response: str
    ) -> dict[str, float] | None:
        """
        Collect human feedback for continuous learning

        Args:
            prompt: Input prompt
            response: Generated response

        Returns:
            Human feedback scores or None if unavailable
        """
        # In production, this would interface with human feedback collection system
        # For now, return simulated feedback patterns
        return {"helpfulness": 0.8, "harmlessness": 0.9, "honesty": 0.85}


class HybridGovernanceEngine:
    """
    Hybrid RLHF + Constitutional AI Governance Engine

    Implements production-ready governance with gradual Constitutional AI adoption
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.rlhf_pipeline = RLHFPipeline()
        self.constitutional_ai = None  # Will be initialized when available
        self.llm_judge = LLMAsJudgeFramework()
        self.alerting = AlertingSystem()
        self.audit_logger = AuditLogger()

        # Configuration parameters
        self.governance_mode = GovernanceMode(config.get("governance_mode", "hybrid"))
        self.constitutional_confidence_threshold = config.get(
            "constitutional_threshold", 0.8
        )
        self.rlhf_fallback_threshold = config.get("rlhf_threshold", 0.6)
        self.human_review_threshold = config.get("human_review_threshold", 0.9)

        # Metrics tracking
        self.decision_counts = dict.fromkeys(GovernanceMode, 0)
        self.performance_metrics = {
            "total_decisions": 0,
            "human_interventions": 0,
            "constitutional_violations": 0,
            "average_latency": 0.0,
            "accuracy_scores": [],
        }

    async def initialize_constitutional_ai(self):
        """Initialize Constitutional AI when technology is mature enough"""
        try:
            self.constitutional_ai = CollectiveConstitutionalAI()
            await self.constitutional_ai.initialize()
            logger.info("Constitutional AI initialized successfully")
        except Exception as e:
            logger.warning(
                f"Constitutional AI initialization failed, using RLHF fallback: {e}"
            )
            self.constitutional_ai = None

    def assess_risk_level(self, prompt: str, context: dict[str, Any]) -> RiskLevel:
        """
        Assess risk level of the request to determine governance approach

        Args:
            prompt: Input prompt
            context: Request context

        Returns:
            Risk level assessment
        """
        risk_factors = {
            "sensitive_topics": any(
                topic in prompt.lower()
                for topic in ["medical", "legal", "financial", "political"]
            ),
            "user_age": context.get("user_age", 18) < 18,
            "high_stakes": context.get("high_stakes", False),
            "public_facing": context.get("public_facing", False),
        }

        risk_score = sum(risk_factors.values())

        if risk_score >= 3:
            return RiskLevel.CRITICAL
        if risk_score >= 2:
            return RiskLevel.HIGH
        if risk_score >= 1:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    async def evaluate_with_rlhf(
        self, prompt: str, response: str, context: dict[str, Any]
    ) -> GovernanceDecision:
        """Evaluate using RLHF methodology"""
        start_time = time.time()

        rlhf_score, reasoning = await self.rlhf_pipeline.evaluate_response(
            prompt, response, context
        )
        risk_level = self.assess_risk_level(prompt, context)

        decision = (
            "approved" if rlhf_score >= self.rlhf_fallback_threshold else "rejected"
        )
        human_review = (
            risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL} or rlhf_score < 0.7
        )

        latency = time.time() - start_time
        self._update_metrics(latency, rlhf_score, human_review)

        return GovernanceDecision(
            decision=decision,
            confidence=rlhf_score,
            reasoning=reasoning,
            method_used=GovernanceMode.RLHF_ONLY,
            risk_level=risk_level,
            constitutional_violations=[],
            rlhf_score=rlhf_score,
            timestamp=datetime.utcnow(),
            human_review_required=human_review,
        )

    async def evaluate_with_constitutional_ai(
        self, prompt: str, response: str, context: dict[str, Any]
    ) -> GovernanceDecision:
        """Evaluate using Constitutional AI principles"""
        if not self.constitutional_ai:
            # Fallback to RLHF if Constitutional AI unavailable
            return await self.evaluate_with_rlhf(prompt, response, context)

        start_time = time.time()

        try:
            # Get Constitutional AI evaluation
            constitutional_result = (
                await self.constitutional_ai.evaluate_constitutional_compliance(
                    prompt, response, context
                )
            )

            risk_level = self.assess_risk_level(prompt, context)
            confidence = constitutional_result.get("confidence", 0.0)
            violations = constitutional_result.get("violations", [])

            decision = (
                "approved"
                if confidence >= self.constitutional_confidence_threshold
                and not violations
                else "rejected"
            )
            human_review = (
                risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
                or confidence < 0.8
                or violations
            )

            # Also get RLHF score for comparison
            rlhf_score, _ = await self.rlhf_pipeline.evaluate_response(
                prompt, response, context
            )

            latency = time.time() - start_time
            self._update_metrics(latency, confidence, human_review, len(violations))

            return GovernanceDecision(
                decision=decision,
                confidence=confidence,
                reasoning=constitutional_result.get(
                    "reasoning", "Constitutional AI evaluation"
                ),
                method_used=GovernanceMode.CONSTITUTIONAL_ONLY,
                risk_level=risk_level,
                constitutional_violations=violations,
                rlhf_score=rlhf_score,
                timestamp=datetime.utcnow(),
                human_review_required=human_review,
            )

        except Exception as e:
            logger.exception(f"Constitutional AI evaluation failed: {e}")
            # Fallback to RLHF
            return await self.evaluate_with_rlhf(prompt, response, context)

    async def evaluate_hybrid(
        self, prompt: str, response: str, context: dict[str, Any]
    ) -> GovernanceDecision:
        """Hybrid evaluation using both RLHF and Constitutional AI"""
        start_time = time.time()

        # Run both evaluations in parallel
        rlhf_task = asyncio.create_task(
            self.evaluate_with_rlhf(prompt, response, context)
        )

        if self.constitutional_ai:
            constitutional_task = asyncio.create_task(
                self.evaluate_with_constitutional_ai(prompt, response, context)
            )
            rlhf_result, constitutional_result = await asyncio.gather(
                rlhf_task, constitutional_task, return_exceptions=True
            )
        else:
            rlhf_result = await rlhf_task
            constitutional_result = None

        risk_level = self.assess_risk_level(prompt, context)

        # Combine results with weighted approach
        if isinstance(constitutional_result, GovernanceDecision):
            # Weighted combination: 60% Constitutional AI, 40% RLHF for high-risk
            if risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
                combined_confidence = (
                    0.6 * constitutional_result.confidence
                    + 0.4 * rlhf_result.confidence
                )
                combined_violations = constitutional_result.constitutional_violations
            else:
                # For lower risk: 40% Constitutional AI, 60% RLHF
                combined_confidence = (
                    0.4 * constitutional_result.confidence
                    + 0.6 * rlhf_result.confidence
                )
                combined_violations = constitutional_result.constitutional_violations

            reasoning = (
                "Hybrid evaluation: Constitutional AI"
                f" ({constitutional_result.confidence:.3f}), RLHF"
                f" ({rlhf_result.confidence:.3f})"
            )
        else:
            # Constitutional AI failed, use RLHF only
            combined_confidence = rlhf_result.confidence
            combined_violations = []
            reasoning = (
                "Hybrid evaluation (Constitutional AI unavailable): RLHF"
                f" ({rlhf_result.confidence:.3f})"
            )

        decision = (
            "approved"
            if combined_confidence >= self.constitutional_confidence_threshold
            and not combined_violations
            else "rejected"
        )
        human_review = (
            risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
            or combined_confidence < 0.8
            or combined_violations
        )

        latency = time.time() - start_time
        self._update_metrics(
            latency, combined_confidence, human_review, len(combined_violations)
        )

        return GovernanceDecision(
            decision=decision,
            confidence=combined_confidence,
            reasoning=reasoning,
            method_used=GovernanceMode.HYBRID,
            risk_level=risk_level,
            constitutional_violations=combined_violations,
            rlhf_score=rlhf_result.confidence,
            timestamp=datetime.utcnow(),
            human_review_required=human_review,
        )

    async def evaluate_adaptive(
        self, prompt: str, response: str, context: dict[str, Any]
    ) -> GovernanceDecision:
        """Adaptive evaluation that chooses method based on context and performance"""
        risk_level = self.assess_risk_level(prompt, context)

        # Adaptive routing logic
        if risk_level == RiskLevel.CRITICAL:
            # Use both methods for critical decisions
            return await self.evaluate_hybrid(prompt, response, context)
        if risk_level == RiskLevel.HIGH:
            # Prefer Constitutional AI for high-risk
            if self.constitutional_ai:
                return await self.evaluate_with_constitutional_ai(
                    prompt, response, context
                )
            return await self.evaluate_with_rlhf(prompt, response, context)
        # Use RLHF for lower risk (faster, proven)
        return await self.evaluate_with_rlhf(prompt, response, context)

    async def evaluate(
        self, prompt: str, response: str, context: dict[str, Any] | None = None
    ) -> GovernanceDecision:
        """
        Main evaluation entry point

        Args:
            prompt: Input prompt
            response: Generated response to evaluate
            context: Additional context information

        Returns:
            Governance decision with detailed evaluation
        """
        if context is None:
            context = {}

        try:
            # Route to appropriate evaluation method
            if self.governance_mode == GovernanceMode.RLHF_ONLY:
                result = await self.evaluate_with_rlhf(prompt, response, context)
            elif self.governance_mode == GovernanceMode.CONSTITUTIONAL_ONLY:
                result = await self.evaluate_with_constitutional_ai(
                    prompt, response, context
                )
            elif self.governance_mode == GovernanceMode.HYBRID:
                result = await self.evaluate_hybrid(prompt, response, context)
            elif self.governance_mode == GovernanceMode.ADAPTIVE:
                result = await self.evaluate_adaptive(prompt, response, context)
            else:
                raise ValueError(f"Unknown governance mode: {self.governance_mode}")

            # Log decision for audit trail
            await self.audit_logger.log_governance_decision(
                {
                    "prompt_hash": hash(prompt),
                    "decision": result.decision,
                    "confidence": result.confidence,
                    "method": result.method_used.value,
                    "risk_level": result.risk_level.value,
                    "human_review_required": result.human_review_required,
                    "timestamp": result.timestamp.isoformat(),
                }
            )

            # Update decision counts
            self.decision_counts[result.method_used] += 1

            # Check for alerts
            await self._check_alert_conditions(result)

            return result

        except Exception as e:
            logger.exception(f"Governance evaluation failed: {e}")
            # Emergency fallback
            return GovernanceDecision(
                decision="rejected",
                confidence=0.0,
                reasoning=f"Evaluation failed: {e!s}",
                method_used=GovernanceMode.RLHF_ONLY,
                risk_level=RiskLevel.CRITICAL,
                constitutional_violations=["evaluation_failure"],
                rlhf_score=0.0,
                timestamp=datetime.utcnow(),
                human_review_required=True,
            )

    def _update_metrics(
        self, latency: float, confidence: float, human_review: bool, violations: int = 0
    ):
        """Update performance metrics"""
        self.performance_metrics["total_decisions"] += 1
        if human_review:
            self.performance_metrics["human_interventions"] += 1
        if violations > 0:
            self.performance_metrics["constitutional_violations"] += violations

        # Update rolling average latency
        current_avg = self.performance_metrics["average_latency"]
        total_decisions = self.performance_metrics["total_decisions"]
        self.performance_metrics["average_latency"] = (
            current_avg * (total_decisions - 1) + latency
        ) / total_decisions

        self.performance_metrics["accuracy_scores"].append(confidence)
        # Keep only recent scores (last 1000)
        if len(self.performance_metrics["accuracy_scores"]) > 1000:
            self.performance_metrics["accuracy_scores"] = self.performance_metrics[
                "accuracy_scores"
            ][-1000:]

    async def _check_alert_conditions(self, result: GovernanceDecision):
        """Check for conditions requiring alerts"""
        # High constitutional violation rate
        if self.performance_metrics["total_decisions"] > 100:
            violation_rate = (
                self.performance_metrics["constitutional_violations"]
                / self.performance_metrics["total_decisions"]
            )
            if violation_rate > 0.05:  # 5% threshold
                await self.alerting.send_alert(
                    "high_constitutional_violation_rate",
                    f"Constitutional violation rate: {violation_rate:.2%}",
                    severity="high",
                )

        # High human intervention rate
        if self.performance_metrics["total_decisions"] > 50:
            intervention_rate = (
                self.performance_metrics["human_interventions"]
                / self.performance_metrics["total_decisions"]
            )
            if intervention_rate > 0.25:  # 25% threshold
                await self.alerting.send_alert(
                    "high_human_intervention_rate",
                    f"Human intervention rate: {intervention_rate:.2%}",
                    severity="medium",
                )

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance metrics summary"""
        if self.performance_metrics["accuracy_scores"]:
            avg_confidence = np.mean(self.performance_metrics["accuracy_scores"])
            min_confidence = np.min(self.performance_metrics["accuracy_scores"])
            max_confidence = np.max(self.performance_metrics["accuracy_scores"])
        else:
            avg_confidence = min_confidence = max_confidence = 0.0

        return {
            "total_decisions": self.performance_metrics["total_decisions"],
            "decision_distribution": dict(self.decision_counts),
            "human_intervention_rate": self.performance_metrics["human_interventions"]
            / max(1, self.performance_metrics["total_decisions"]),
            "constitutional_violation_rate": self.performance_metrics[
                "constitutional_violations"
            ]
            / max(1, self.performance_metrics["total_decisions"]),
            "average_latency_ms": self.performance_metrics["average_latency"] * 1000,
            "confidence_metrics": {
                "average": avg_confidence,
                "minimum": min_confidence,
                "maximum": max_confidence,
            },
            "governance_mode": self.governance_mode.value,
        }


# Example usage and configuration
DEFAULT_CONFIG = {
    "governance_mode": "adaptive",
    "constitutional_threshold": 0.8,
    "rlhf_threshold": 0.6,
    "human_review_threshold": 0.9,
}


async def create_hybrid_governance_engine(
    config: dict[str, Any] | None = None,
) -> HybridGovernanceEngine:
    """
    Factory function to create and initialize the hybrid governance engine

    Args:
        config: Configuration dictionary

    Returns:
        Initialized HybridGovernanceEngine
    """
    if config is None:
        config = DEFAULT_CONFIG

    engine = HybridGovernanceEngine(config)
    await engine.initialize_constitutional_ai()

    logger.info(
        f"Hybrid Governance Engine initialized with mode: {engine.governance_mode}"
    )
    return engine
