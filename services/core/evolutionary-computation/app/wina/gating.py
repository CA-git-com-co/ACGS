"""
WINA Gating System

Provides runtime gating and strategy selection for WINA optimization
with constitutional compliance and performance monitoring.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class GatingStrategy(Enum):
    """WINA gating strategies for optimization control."""

    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"
    CONSTITUTIONAL_FIRST = "constitutional_first"


class GatingDecision(Enum):
    """Gating decision outcomes."""

    ALLOW = "allow"
    BLOCK = "block"
    THROTTLE = "throttle"
    FALLBACK = "fallback"


@dataclass
class GatingContext:
    """Context information for gating decisions."""

    operation_type: str
    risk_level: str
    constitutional_score: float
    performance_metrics: dict[str, float]
    historical_success_rate: float
    current_load: float


@dataclass
class GatingResult:
    """Result of a gating decision."""

    decision: GatingDecision
    confidence: float
    reasoning: str
    throttle_factor: float | None = None
    fallback_strategy: str | None = None
    metadata: dict[str, Any] = None


class RuntimeGating:
    """
    Runtime gating system for WINA optimization operations.

    Provides intelligent gating decisions based on constitutional compliance,
    performance metrics, and system health to ensure safe optimization.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize runtime gating system.

        Args:
            config: WINA configuration dictionary
        """
        self.config = config
        self.gating_config = config.get("gating", {})
        self.strategy = GatingStrategy(self.gating_config.get("strategy", "adaptive"))
        self.threshold = self.gating_config.get("threshold", 0.7)
        self.fallback_enabled = self.gating_config.get("fallback_enabled", True)

        # Constitutional requirements
        self.constitutional_threshold = config.get("constitutional", {}).get(
            "compliance_threshold", 0.90
        )

        # Performance thresholds
        self.performance_thresholds = config.get("performance_targets", {})

        # Gating history and metrics
        self.gating_history: list[GatingResult] = []
        self.decision_counts = dict.fromkeys(GatingDecision, 0)
        self.strategy_performance: dict[GatingStrategy, list[float]] = {}

        # Circuit breaker state
        self.circuit_breaker_active = False
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_reset_time = None

        logger.info(f"Runtime gating initialized with {self.strategy.value} strategy")

    async def evaluate_gating_decision(self, context: GatingContext) -> GatingResult:
        """
        Evaluate gating decision based on context and strategy.

        Args:
            context: Gating context with operation details

        Returns:
            GatingResult with decision and reasoning
        """
        try:
            # Check circuit breaker first
            if self.circuit_breaker_active:
                if self._should_reset_circuit_breaker():
                    self.circuit_breaker_active = False
                    self.circuit_breaker_failures = 0
                    logger.info("Circuit breaker reset")
                else:
                    return GatingResult(
                        decision=GatingDecision.BLOCK,
                        confidence=1.0,
                        reasoning="Circuit breaker active due to repeated failures",
                    )

            # Apply strategy-specific gating logic
            if self.strategy == GatingStrategy.CONSERVATIVE:
                result = await self._conservative_gating(context)
            elif self.strategy == GatingStrategy.AGGRESSIVE:
                result = await self._aggressive_gating(context)
            elif self.strategy == GatingStrategy.CONSTITUTIONAL_FIRST:
                result = await self._constitutional_first_gating(context)
            elif self.strategy == GatingStrategy.ADAPTIVE:
                result = await self._adaptive_gating(context)
            else:  # BALANCED
                result = await self._balanced_gating(context)

            # Update gating history and metrics
            self._update_gating_metrics(result)

            # Handle circuit breaker logic
            if result.decision == GatingDecision.BLOCK:
                self.circuit_breaker_failures += 1
                if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
                    self.circuit_breaker_active = True
                    self.circuit_breaker_reset_time = time.time() + 300  # 5 minutes
                    logger.warning("Circuit breaker activated")
            else:
                self.circuit_breaker_failures = max(
                    0, self.circuit_breaker_failures - 1
                )

            return result

        except Exception as e:
            logger.error(f"Gating decision evaluation failed: {e}")
            return GatingResult(
                decision=GatingDecision.BLOCK,
                confidence=0.0,
                reasoning=f"Gating evaluation error: {e!s}",
            )

    async def _conservative_gating(self, context: GatingContext) -> GatingResult:
        """Conservative gating strategy - prioritizes safety over performance."""

        # Very strict constitutional compliance requirement
        if context.constitutional_score < 0.95:
            return GatingResult(
                decision=GatingDecision.BLOCK,
                confidence=0.9,
                reasoning=f"Constitutional score {context.constitutional_score:.3f} below conservative threshold 0.95",
            )

        # Strict performance requirements
        if context.historical_success_rate < 0.9:
            return GatingResult(
                decision=GatingDecision.THROTTLE,
                confidence=0.8,
                reasoning="Historical success rate below conservative threshold",
                throttle_factor=0.5,
            )

        # High load protection
        if context.current_load > 0.7:
            return GatingResult(
                decision=GatingDecision.THROTTLE,
                confidence=0.7,
                reasoning="System load above conservative threshold",
                throttle_factor=0.3,
            )

        return GatingResult(
            decision=GatingDecision.ALLOW,
            confidence=0.9,
            reasoning="Conservative gating criteria met",
        )

    async def _aggressive_gating(self, context: GatingContext) -> GatingResult:
        """Aggressive gating strategy - prioritizes performance over safety."""

        # Relaxed constitutional compliance
        if context.constitutional_score < 0.8:
            return GatingResult(
                decision=GatingDecision.BLOCK,
                confidence=0.8,
                reasoning=f"Constitutional score {context.constitutional_score:.3f} below aggressive threshold 0.8",
            )

        # Allow operations with lower success rates
        if context.historical_success_rate < 0.6:
            return GatingResult(
                decision=GatingDecision.THROTTLE,
                confidence=0.6,
                reasoning="Historical success rate below aggressive threshold",
                throttle_factor=0.8,
            )

        # Higher load tolerance
        if context.current_load > 0.9:
            return GatingResult(
                decision=GatingDecision.THROTTLE,
                confidence=0.5,
                reasoning="System load above aggressive threshold",
                throttle_factor=0.7,
            )

        return GatingResult(
            decision=GatingDecision.ALLOW,
            confidence=0.8,
            reasoning="Aggressive gating criteria met",
        )

    async def _constitutional_first_gating(
        self, context: GatingContext
    ) -> GatingResult:
        """Constitutional-first gating - prioritizes constitutional compliance above all."""

        # Extremely strict constitutional compliance
        if context.constitutional_score < self.constitutional_threshold:
            return GatingResult(
                decision=GatingDecision.BLOCK,
                confidence=1.0,
                reasoning=f"Constitutional score {context.constitutional_score:.3f} below threshold {self.constitutional_threshold:.3f}",
            )

        # Secondary check on risk level
        if context.risk_level == "high":
            return GatingResult(
                decision=GatingDecision.THROTTLE,
                confidence=0.9,
                reasoning="High risk operation requires throttling for constitutional safety",
                throttle_factor=0.4,
            )

        return GatingResult(
            decision=GatingDecision.ALLOW,
            confidence=0.95,
            reasoning="Constitutional compliance verified",
        )

    async def _adaptive_gating(self, context: GatingContext) -> GatingResult:
        """Adaptive gating strategy - adjusts based on current conditions and history."""

        # Calculate adaptive thresholds based on recent performance
        recent_success_rate = self._get_recent_success_rate()
        adaptive_constitutional_threshold = max(
            0.85, self.constitutional_threshold - (1.0 - recent_success_rate) * 0.1
        )

        # Constitutional compliance with adaptive threshold
        if context.constitutional_score < adaptive_constitutional_threshold:
            return GatingResult(
                decision=GatingDecision.BLOCK,
                confidence=0.85,
                reasoning=f"Constitutional score {context.constitutional_score:.3f} below adaptive threshold {adaptive_constitutional_threshold:.3f}",
            )

        # Adaptive performance gating
        performance_score = self._calculate_performance_score(context)
        if performance_score < 0.7:
            throttle_factor = max(0.3, performance_score)
            return GatingResult(
                decision=GatingDecision.THROTTLE,
                confidence=0.7,
                reasoning=f"Performance score {performance_score:.3f} requires throttling",
                throttle_factor=throttle_factor,
            )

        return GatingResult(
            decision=GatingDecision.ALLOW,
            confidence=0.8,
            reasoning="Adaptive gating criteria met",
        )

    async def _balanced_gating(self, context: GatingContext) -> GatingResult:
        """Balanced gating strategy - balances safety and performance."""

        # Standard constitutional compliance
        if context.constitutional_score < 0.88:
            return GatingResult(
                decision=GatingDecision.BLOCK,
                confidence=0.8,
                reasoning=f"Constitutional score {context.constitutional_score:.3f} below balanced threshold 0.88",
            )

        # Balanced performance requirements
        if context.historical_success_rate < 0.75:
            return GatingResult(
                decision=GatingDecision.THROTTLE,
                confidence=0.7,
                reasoning="Historical success rate below balanced threshold",
                throttle_factor=0.6,
            )

        # Moderate load protection
        if context.current_load > 0.8:
            return GatingResult(
                decision=GatingDecision.THROTTLE,
                confidence=0.6,
                reasoning="System load above balanced threshold",
                throttle_factor=0.5,
            )

        return GatingResult(
            decision=GatingDecision.ALLOW,
            confidence=0.8,
            reasoning="Balanced gating criteria met",
        )

    def _calculate_performance_score(self, context: GatingContext) -> float:
        """Calculate overall performance score from context metrics."""
        try:
            weights = {
                "success_rate": 0.4,
                "constitutional_score": 0.3,
                "load_factor": 0.2,
                "risk_factor": 0.1,
            }

            load_score = max(0, 1.0 - context.current_load)
            risk_score = (
                1.0
                if context.risk_level == "low"
                else 0.7 if context.risk_level == "medium" else 0.3
            )

            performance_score = (
                weights["success_rate"] * context.historical_success_rate
                + weights["constitutional_score"] * context.constitutional_score
                + weights["load_factor"] * load_score
                + weights["risk_factor"] * risk_score
            )

            return performance_score

        except Exception as e:
            logger.error(f"Performance score calculation failed: {e}")
            return 0.5  # Default moderate score

    def _get_recent_success_rate(self) -> float:
        """Get recent success rate from gating history."""
        try:
            recent_decisions = self.gating_history[-20:]  # Last 20 decisions
            if not recent_decisions:
                return 0.8  # Default

            successful_decisions = sum(
                1
                for result in recent_decisions
                if result.decision in [GatingDecision.ALLOW, GatingDecision.THROTTLE]
            )

            return successful_decisions / len(recent_decisions)

        except Exception as e:
            logger.error(f"Recent success rate calculation failed: {e}")
            return 0.8

    def _should_reset_circuit_breaker(self) -> bool:
        """Check if circuit breaker should be reset."""
        return (
            self.circuit_breaker_reset_time is not None
            and time.time() >= self.circuit_breaker_reset_time
        )

    def _update_gating_metrics(self, result: GatingResult):
        """Update gating metrics and history."""
        try:
            self.gating_history.append(result)
            if len(self.gating_history) > 1000:  # Keep last 1000 results
                self.gating_history.pop(0)

            self.decision_counts[result.decision] += 1

        except Exception as e:
            logger.error(f"Failed to update gating metrics: {e}")

    def get_gating_summary(self) -> dict[str, Any]:
        """Get summary of gating performance."""
        try:
            total_decisions = sum(self.decision_counts.values())

            return {
                "strategy": self.strategy.value,
                "total_decisions": total_decisions,
                "decision_breakdown": {
                    decision.value: count
                    for decision, count in self.decision_counts.items()
                },
                "allow_rate": (
                    self.decision_counts[GatingDecision.ALLOW] / total_decisions
                    if total_decisions > 0
                    else 0
                ),
                "circuit_breaker_active": self.circuit_breaker_active,
                "circuit_breaker_failures": self.circuit_breaker_failures,
                "recent_success_rate": self._get_recent_success_rate(),
                "threshold": self.threshold,
                "constitutional_threshold": self.constitutional_threshold,
            }

        except Exception as e:
            logger.error(f"Failed to generate gating summary: {e}")
            return {"error": str(e)}
