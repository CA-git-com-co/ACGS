#!/usr/bin/env python3
"""
Weighted Consensus Engine for ACGS-1 Phase 2 Multi-Model Integration

This module implements a sophisticated weighted voting mechanism for 4+ model consensus
in constitutional governance decisions. It provides multiple consensus strategies,
tie-breaking mechanisms, and confidence scoring for robust decision-making.

Key Features:
- Multiple consensus strategies (weighted_average, majority_vote, confidence_weighted)
- Tie-breaking mechanisms with fallback strategies
- Constitutional compliance scoring integration
- Performance monitoring and metrics collection
- Configurable model weights and thresholds
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class ConsensusStrategy(str, Enum):
    """Available consensus strategies for multi-model voting."""

    WEIGHTED_AVERAGE = "weighted_average"
    MAJORITY_VOTE = "majority_vote"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    UNANIMOUS_REQUIRED = "unanimous_required"
    SUPERMAJORITY = "supermajority"  # Requires 2/3 agreement


class TieBreakingStrategy(str, Enum):
    """Tie-breaking strategies when models disagree."""

    HIGHEST_CONFIDENCE = "highest_confidence"
    HIGHEST_WEIGHT = "highest_weight"
    MOST_RECENT = "most_recent"
    CONSTITUTIONAL_PRIORITY = "constitutional_priority"
    HUMAN_REVIEW = "human_review"


@dataclass
class ModelVote:
    """Individual model vote with metadata."""

    model_id: str
    decision: str
    confidence: float
    weight: float
    reasoning: str | None = None
    constitutional_score: float | None = None
    response_time_ms: float | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class ConsensusResult:
    """Result from weighted consensus calculation."""

    final_decision: str
    confidence_score: float
    consensus_strategy: ConsensusStrategy
    agreement_score: float
    participating_models: list[str]
    model_votes: list[ModelVote]
    tie_broken: bool = False
    tie_breaking_strategy: TieBreakingStrategy | None = None
    processing_time_ms: float = 0.0
    metadata: dict[str, Any] | None = None


class WeightedConsensusEngine:
    """
    Advanced weighted consensus engine for multi-model decision making.

    Implements sophisticated voting mechanisms with multiple strategies,
    tie-breaking, and constitutional governance integration.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize weighted consensus engine."""
        self.config = config or {}

        # Default model weights for Phase 2 enhanced models
        self.default_weights = {
            "embedding": 0.25,
            "qwen3_32b": 0.20,
            "qwen3_235b": 0.25,
            "deepseek_chat_v3": 0.20,
            "deepseek_r1": 0.10,
        }

        # Consensus thresholds
        self.majority_threshold = self.config.get("majority_threshold", 0.5)
        self.supermajority_threshold = self.config.get("supermajority_threshold", 0.67)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.7)

        # Performance tracking
        self.total_consensus_calculations = 0
        self.successful_consensus = 0
        self.tie_breaking_events = 0

    def calculate_consensus(
        self,
        model_responses: dict[str, dict[str, Any]],
        strategy: ConsensusStrategy = ConsensusStrategy.WEIGHTED_AVERAGE,
        custom_weights: dict[str, float] | None = None,
        tie_breaking: TieBreakingStrategy = TieBreakingStrategy.HIGHEST_CONFIDENCE,
    ) -> ConsensusResult:
        """
        Calculate weighted consensus from multiple model responses.

        Args:
            model_responses: Dictionary of model responses
            strategy: Consensus strategy to use
            custom_weights: Optional custom model weights
            tie_breaking: Tie-breaking strategy

        Returns:
            ConsensusResult with final decision and metadata
        """
        start_time = time.time()
        self.total_consensus_calculations += 1

        try:
            # Parse model votes
            model_votes = self._parse_model_votes(model_responses, custom_weights)

            if not model_votes:
                return self._create_error_result("No valid model votes", start_time)

            # Apply consensus strategy
            if strategy == ConsensusStrategy.WEIGHTED_AVERAGE:
                result = self._weighted_average_consensus(model_votes)
            elif strategy == ConsensusStrategy.MAJORITY_VOTE:
                result = self._majority_vote_consensus(model_votes)
            elif strategy == ConsensusStrategy.CONFIDENCE_WEIGHTED:
                result = self._confidence_weighted_consensus(model_votes)
            elif strategy == ConsensusStrategy.UNANIMOUS_REQUIRED:
                result = self._unanimous_consensus(model_votes)
            elif strategy == ConsensusStrategy.SUPERMAJORITY:
                result = self._supermajority_consensus(model_votes)
            else:
                return self._create_error_result(
                    f"Unknown strategy: {strategy}", start_time
                )

            # Apply tie-breaking if needed
            if self._is_tie(result, model_votes):
                result = self._apply_tie_breaking(result, model_votes, tie_breaking)
                result.tie_broken = True
                result.tie_breaking_strategy = tie_breaking
                self.tie_breaking_events += 1

            # Calculate final metrics
            result.consensus_strategy = strategy
            result.processing_time_ms = (time.time() - start_time) * 1000
            result.agreement_score = self._calculate_agreement_score(
                model_votes, result.final_decision
            )
            result.participating_models = [vote.model_id for vote in model_votes]
            result.model_votes = model_votes

            self.successful_consensus += 1

            logger.info(
                "Consensus calculation completed",
                strategy=strategy.value,
                final_decision=result.final_decision,
                confidence=result.confidence_score,
                agreement_score=result.agreement_score,
                tie_broken=result.tie_broken,
                processing_time_ms=result.processing_time_ms,
            )

            return result

        except Exception as e:
            logger.error(f"Consensus calculation failed: {e}")
            return self._create_error_result(str(e), start_time)

    def _parse_model_votes(
        self,
        model_responses: dict[str, dict[str, Any]],
        custom_weights: dict[str, float] | None = None,
    ) -> list[ModelVote]:
        """Parse model responses into structured votes."""
        votes = []
        weights = custom_weights or self.default_weights

        for model_id, response in model_responses.items():
            if not isinstance(response, dict):
                continue

            # Extract decision and confidence
            decision = response.get("decision", response.get("choice", "unknown"))
            confidence = float(response.get("confidence", response.get("score", 0.5)))

            # Get model weight
            weight = weights.get(model_id, 0.1)  # Default weight for unknown models

            # Extract additional metadata
            reasoning = response.get("reasoning", response.get("explanation"))
            constitutional_score = response.get(
                "constitutional_score", response.get("compliance_score")
            )
            response_time = response.get("response_time_ms", response.get("latency_ms"))

            vote = ModelVote(
                model_id=model_id,
                decision=str(decision),
                confidence=confidence,
                weight=weight,
                reasoning=reasoning,
                constitutional_score=constitutional_score,
                response_time_ms=response_time,
                metadata=response.get("metadata", {}),
            )

            votes.append(vote)

        return votes

    def _weighted_average_consensus(self, votes: list[ModelVote]) -> ConsensusResult:
        """Calculate consensus using weighted average of decisions."""
        decision_scores = {}
        total_weight = 0.0
        confidence_sum = 0.0

        for vote in votes:
            decision = vote.decision
            weight = vote.weight
            confidence = vote.confidence

            if decision not in decision_scores:
                decision_scores[decision] = 0.0

            decision_scores[decision] += weight * confidence
            total_weight += weight
            confidence_sum += weight * confidence

        if not decision_scores:
            return ConsensusResult(
                "unknown", 0.0, ConsensusStrategy.WEIGHTED_AVERAGE, 0.0, [], []
            )

        # Normalize scores
        if total_weight > 0:
            decision_scores = {k: v / total_weight for k, v in decision_scores.items()}
            final_confidence = confidence_sum / total_weight
        else:
            final_confidence = 0.0

        # Get highest scoring decision
        best_decision = max(decision_scores.items(), key=lambda x: x[1])

        return ConsensusResult(
            final_decision=best_decision[0],
            confidence_score=final_confidence,
            consensus_strategy=ConsensusStrategy.WEIGHTED_AVERAGE,
            agreement_score=0.0,  # Will be calculated later
            participating_models=[],  # Will be filled later
            model_votes=[],  # Will be filled later
        )

    def _majority_vote_consensus(self, votes: list[ModelVote]) -> ConsensusResult:
        """Calculate consensus using majority vote."""
        decision_counts = {}
        total_votes = len(votes)

        for vote in votes:
            decision = vote.decision
            decision_counts[decision] = decision_counts.get(decision, 0) + 1

        if not decision_counts:
            return ConsensusResult(
                "unknown", 0.0, ConsensusStrategy.MAJORITY_VOTE, 0.0, [], []
            )

        # Find majority decision
        max_count = max(decision_counts.values())
        majority_decisions = [d for d, c in decision_counts.items() if c == max_count]

        # Check if we have a clear majority
        if (
            max_count > total_votes * self.majority_threshold
            and len(majority_decisions) == 1
        ):
            final_decision = majority_decisions[0]
            confidence = max_count / total_votes
        else:
            # No clear majority, use most voted option
            final_decision = majority_decisions[0] if majority_decisions else "unknown"
            confidence = max_count / total_votes if total_votes > 0 else 0.0

        return ConsensusResult(
            final_decision=final_decision,
            confidence_score=confidence,
            consensus_strategy=ConsensusStrategy.MAJORITY_VOTE,
            agreement_score=0.0,
            participating_models=[],
            model_votes=[],
        )

    def _confidence_weighted_consensus(self, votes: list[ModelVote]) -> ConsensusResult:
        """Calculate consensus weighted by model confidence scores."""
        decision_scores = {}
        total_confidence = 0.0

        for vote in votes:
            decision = vote.decision
            confidence = vote.confidence
            weight = vote.weight

            # Weight by both model weight and confidence
            weighted_confidence = (
                weight * confidence * confidence
            )  # Square confidence for emphasis

            if decision not in decision_scores:
                decision_scores[decision] = 0.0

            decision_scores[decision] += weighted_confidence
            total_confidence += weighted_confidence

        if not decision_scores or total_confidence == 0:
            return ConsensusResult(
                "unknown", 0.0, ConsensusStrategy.CONFIDENCE_WEIGHTED, 0.0, [], []
            )

        # Normalize and find best decision
        normalized_scores = {
            k: v / total_confidence for k, v in decision_scores.items()
        }
        best_decision = max(normalized_scores.items(), key=lambda x: x[1])

        return ConsensusResult(
            final_decision=best_decision[0],
            confidence_score=best_decision[1],
            consensus_strategy=ConsensusStrategy.CONFIDENCE_WEIGHTED,
            agreement_score=0.0,
            participating_models=[],
            model_votes=[],
        )

    def _unanimous_consensus(self, votes: list[ModelVote]) -> ConsensusResult:
        """Require unanimous agreement from all models."""
        if not votes:
            return ConsensusResult(
                "unknown", 0.0, ConsensusStrategy.UNANIMOUS_REQUIRED, 0.0, [], []
            )

        first_decision = votes[0].decision
        unanimous = all(vote.decision == first_decision for vote in votes)

        if unanimous:
            avg_confidence = sum(vote.confidence for vote in votes) / len(votes)
            return ConsensusResult(
                final_decision=first_decision,
                confidence_score=avg_confidence,
                consensus_strategy=ConsensusStrategy.UNANIMOUS_REQUIRED,
                agreement_score=1.0,
                participating_models=[],
                model_votes=[],
            )
        else:
            return ConsensusResult(
                final_decision="no_consensus",
                confidence_score=0.0,
                consensus_strategy=ConsensusStrategy.UNANIMOUS_REQUIRED,
                agreement_score=0.0,
                participating_models=[],
                model_votes=[],
            )

    def _supermajority_consensus(self, votes: list[ModelVote]) -> ConsensusResult:
        """Require supermajority (2/3) agreement."""
        decision_counts = {}
        total_votes = len(votes)

        for vote in votes:
            decision = vote.decision
            decision_counts[decision] = decision_counts.get(decision, 0) + 1

        if not decision_counts:
            return ConsensusResult(
                "unknown", 0.0, ConsensusStrategy.SUPERMAJORITY, 0.0, [], []
            )

        # Check for supermajority
        for decision, count in decision_counts.items():
            if count >= total_votes * self.supermajority_threshold:
                confidence = count / total_votes
                return ConsensusResult(
                    final_decision=decision,
                    confidence_score=confidence,
                    consensus_strategy=ConsensusStrategy.SUPERMAJORITY,
                    agreement_score=confidence,
                    participating_models=[],
                    model_votes=[],
                )

        # No supermajority found
        return ConsensusResult(
            final_decision="no_supermajority",
            confidence_score=0.0,
            consensus_strategy=ConsensusStrategy.SUPERMAJORITY,
            agreement_score=0.0,
            participating_models=[],
            model_votes=[],
        )

    def _is_tie(self, result: ConsensusResult, votes: list[ModelVote]) -> bool:
        """Check if the result represents a tie that needs breaking."""
        if result.confidence_score < self.confidence_threshold:
            return True

        if result.final_decision in ["unknown", "no_consensus", "no_supermajority"]:
            return True

        return False

    def _apply_tie_breaking(
        self,
        result: ConsensusResult,
        votes: list[ModelVote],
        strategy: TieBreakingStrategy,
    ) -> ConsensusResult:
        """Apply tie-breaking strategy to resolve conflicts."""

        if strategy == TieBreakingStrategy.HIGHEST_CONFIDENCE:
            # Choose decision from model with highest confidence
            highest_confidence_vote = max(votes, key=lambda v: v.confidence)
            result.final_decision = highest_confidence_vote.decision
            result.confidence_score = highest_confidence_vote.confidence

        elif strategy == TieBreakingStrategy.HIGHEST_WEIGHT:
            # Choose decision from model with highest weight
            highest_weight_vote = max(votes, key=lambda v: v.weight)
            result.final_decision = highest_weight_vote.decision
            result.confidence_score = highest_weight_vote.confidence

        elif strategy == TieBreakingStrategy.CONSTITUTIONAL_PRIORITY:
            # Choose decision with highest constitutional score
            constitutional_votes = [
                v for v in votes if v.constitutional_score is not None
            ]
            if constitutional_votes:
                best_constitutional_vote = max(
                    constitutional_votes, key=lambda v: v.constitutional_score
                )
                result.final_decision = best_constitutional_vote.decision
                result.confidence_score = best_constitutional_vote.confidence

        return result

    def _calculate_agreement_score(
        self, votes: list[ModelVote], final_decision: str
    ) -> float:
        """Calculate agreement score for the final decision."""
        if not votes:
            return 0.0

        agreeing_votes = sum(1 for vote in votes if vote.decision == final_decision)
        return agreeing_votes / len(votes)

    def _create_error_result(
        self, error_message: str, start_time: float
    ) -> ConsensusResult:
        """Create error result for failed consensus calculations."""
        return ConsensusResult(
            final_decision="error",
            confidence_score=0.0,
            consensus_strategy=ConsensusStrategy.WEIGHTED_AVERAGE,
            agreement_score=0.0,
            participating_models=[],
            model_votes=[],
            processing_time_ms=(time.time() - start_time) * 1000,
            metadata={"error": error_message},
        )

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get consensus engine performance metrics."""
        success_rate = (
            self.successful_consensus / max(1, self.total_consensus_calculations)
        ) * 100
        tie_breaking_rate = (
            self.tie_breaking_events / max(1, self.total_consensus_calculations)
        ) * 100

        return {
            "total_consensus_calculations": self.total_consensus_calculations,
            "successful_consensus": self.successful_consensus,
            "tie_breaking_events": self.tie_breaking_events,
            "success_rate_percentage": success_rate,
            "tie_breaking_rate_percentage": tie_breaking_rate,
            "supported_strategies": [strategy.value for strategy in ConsensusStrategy],
            "supported_tie_breaking": [
                strategy.value for strategy in TieBreakingStrategy
            ],
        }


# Global consensus engine instance
_consensus_engine: WeightedConsensusEngine | None = None


def get_consensus_engine() -> WeightedConsensusEngine:
    """Get global weighted consensus engine instance."""
    global _consensus_engine

    if _consensus_engine is None:
        _consensus_engine = WeightedConsensusEngine()

    return _consensus_engine
