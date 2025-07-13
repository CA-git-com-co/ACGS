"""
WINA Continuous Learning System

Provides continuous learning and adaptation capabilities for WINA optimization
with feedback integration and constitutional compliance learning.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback for WINA learning system."""

    PERFORMANCE = "performance"
    CONSTITUTIONAL = "constitutional"
    USER = "user"
    SYSTEM = "system"
    OPTIMIZATION = "optimization"


class LearningStrategy(Enum):
    """Learning strategies for WINA adaptation."""

    REINFORCEMENT = "reinforcement"
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    CONSTITUTIONAL_GUIDED = "constitutional_guided"


@dataclass
class FeedbackSignal:
    """Feedback signal for WINA learning system."""

    signal_id: str
    feedback_type: FeedbackType
    source: str
    value: float
    context: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    processed: bool = False


@dataclass
class LearningUpdate:
    """Learning update result from feedback processing."""

    update_id: str
    strategy_used: LearningStrategy
    parameters_updated: list[str]
    improvement_score: float
    constitutional_impact: float
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


class WINALearningSystem:
    """
    Continuous learning system for WINA optimization.

    Processes feedback signals to continuously improve WINA performance
    while maintaining constitutional compliance constraints.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize WINA learning system.

        Args:
            config: WINA configuration dictionary
        """
        self.config = config
        self.learning_rate = config.get("learning_rate", 0.01)
        self.constitutional_weight = config.get("constitutional", {}).get(
            "learning_weight", 0.4
        )

        # Learning state
        self.feedback_queue: list[FeedbackSignal] = []
        self.learning_history: list[LearningUpdate] = []
        self.adaptation_parameters: dict[str, float] = {}

        # Performance tracking
        self.total_feedback_processed = 0
        self.successful_adaptations = 0
        self.constitutional_violations_prevented = 0

        # Learning strategies
        self.active_strategies = [
            LearningStrategy.CONSTITUTIONAL_GUIDED,
            LearningStrategy.REINFORCEMENT,
        ]

        logger.info("WINA Learning System initialized")

    async def process_feedback_signal(
        self, feedback: FeedbackSignal
    ) -> LearningUpdate | None:
        """
        Process a feedback signal and generate learning updates.

        Args:
            feedback: Feedback signal to process

        Returns:
            LearningUpdate if adaptation was made, None otherwise
        """
        try:
            self.feedback_queue.append(feedback)
            self.total_feedback_processed += 1

            # Determine learning strategy based on feedback type
            strategy = self._select_learning_strategy(feedback)

            # Process feedback based on strategy
            if strategy == LearningStrategy.CONSTITUTIONAL_GUIDED:
                update = await self._constitutional_guided_learning(feedback)
            elif strategy == LearningStrategy.REINFORCEMENT:
                update = await self._reinforcement_learning(feedback)
            else:
                update = await self._default_learning(feedback)

            if update:
                self.learning_history.append(update)
                self.successful_adaptations += 1

                # Apply parameter updates
                await self._apply_learning_update(update)

                logger.info(f"Learning update applied: {update.update_id}")

            feedback.processed = True
            return update

        except Exception as e:
            logger.exception(f"Failed to process feedback signal: {e}")
            return None

    async def _constitutional_guided_learning(
        self, feedback: FeedbackSignal
    ) -> LearningUpdate | None:
        """Constitutional-guided learning strategy."""
        try:
            # Prioritize constitutional compliance in learning
            constitutional_score = feedback.context.get(
                "constitutional_compliance", 0.0
            )

            if constitutional_score < 0.85:
                # Strong constitutional guidance needed
                parameters_to_update = ["constitutional_weight", "compliance_threshold"]
                improvement_score = 0.8
                constitutional_impact = 0.9
                confidence = 0.9
            else:
                # Moderate constitutional guidance
                parameters_to_update = ["optimization_aggressiveness"]
                improvement_score = 0.6
                constitutional_impact = 0.7
                confidence = 0.7

            return LearningUpdate(
                update_id=f"const_learn_{int(time.time())}",
                strategy_used=LearningStrategy.CONSTITUTIONAL_GUIDED,
                parameters_updated=parameters_to_update,
                improvement_score=improvement_score,
                constitutional_impact=constitutional_impact,
                confidence=confidence,
            )

        except Exception as e:
            logger.exception(f"Constitutional guided learning failed: {e}")
            return None

    async def _reinforcement_learning(
        self, feedback: FeedbackSignal
    ) -> LearningUpdate | None:
        """Reinforcement learning strategy."""
        try:
            # Use feedback value as reward signal
            reward = feedback.value

            if reward > 0.8:
                # Positive reinforcement - strengthen current parameters
                parameters_to_update = ["learning_rate", "optimization_strength"]
                improvement_score = reward
                constitutional_impact = 0.5
                confidence = 0.8
            elif reward < 0.3:
                # Negative reinforcement - adjust parameters
                parameters_to_update = ["learning_rate", "constitutional_weight"]
                improvement_score = 1.0 - reward
                constitutional_impact = 0.8
                confidence = 0.6
            else:
                # Neutral - minor adjustments
                parameters_to_update = ["learning_rate"]
                improvement_score = 0.5
                constitutional_impact = 0.3
                confidence = 0.5

            return LearningUpdate(
                update_id=f"rl_learn_{int(time.time())}",
                strategy_used=LearningStrategy.REINFORCEMENT,
                parameters_updated=parameters_to_update,
                improvement_score=improvement_score,
                constitutional_impact=constitutional_impact,
                confidence=confidence,
            )

        except Exception as e:
            logger.exception(f"Reinforcement learning failed: {e}")
            return None

    async def _default_learning(
        self, feedback: FeedbackSignal
    ) -> LearningUpdate | None:
        """Default learning strategy."""
        try:
            # Simple adaptive learning
            parameters_to_update = ["learning_rate"]
            improvement_score = 0.5
            constitutional_impact = 0.5
            confidence = 0.5

            return LearningUpdate(
                update_id=f"default_learn_{int(time.time())}",
                strategy_used=LearningStrategy.SUPERVISED,
                parameters_updated=parameters_to_update,
                improvement_score=improvement_score,
                constitutional_impact=constitutional_impact,
                confidence=confidence,
            )

        except Exception as e:
            logger.exception(f"Default learning failed: {e}")
            return None

    def _select_learning_strategy(self, feedback: FeedbackSignal) -> LearningStrategy:
        """Select appropriate learning strategy for feedback."""
        try:
            if feedback.feedback_type == FeedbackType.CONSTITUTIONAL:
                return LearningStrategy.CONSTITUTIONAL_GUIDED
            if feedback.feedback_type == FeedbackType.PERFORMANCE:
                return LearningStrategy.REINFORCEMENT
            return LearningStrategy.SUPERVISED

        except Exception as e:
            logger.exception(f"Learning strategy selection failed: {e}")
            return LearningStrategy.SUPERVISED

    async def _apply_learning_update(self, update: LearningUpdate):
        """Apply learning update to adaptation parameters."""
        try:
            for param in update.parameters_updated:
                if param == "learning_rate":
                    # Adjust learning rate based on improvement score
                    adjustment = (update.improvement_score - 0.5) * 0.001
                    self.learning_rate = max(
                        0.001, min(0.1, self.learning_rate + adjustment)
                    )
                    self.adaptation_parameters["learning_rate"] = self.learning_rate

                elif param == "constitutional_weight":
                    # Adjust constitutional weight based on constitutional impact
                    adjustment = update.constitutional_impact * 0.05
                    new_weight = max(
                        0.2, min(0.8, self.constitutional_weight + adjustment)
                    )
                    self.constitutional_weight = new_weight
                    self.adaptation_parameters["constitutional_weight"] = new_weight

                elif param == "optimization_aggressiveness":
                    # Adjust optimization aggressiveness
                    current_aggressiveness = self.adaptation_parameters.get(
                        "optimization_aggressiveness", 0.5
                    )
                    adjustment = (update.improvement_score - 0.5) * 0.1
                    new_aggressiveness = max(
                        0.1, min(0.9, current_aggressiveness + adjustment)
                    )
                    self.adaptation_parameters["optimization_aggressiveness"] = (
                        new_aggressiveness
                    )

            logger.info(f"Applied learning update: {update.update_id}")

        except Exception as e:
            logger.exception(f"Failed to apply learning update: {e}")

    def get_learning_summary(self) -> dict[str, Any]:
        """Get summary of learning system performance."""
        try:
            adaptation_rate = (
                self.successful_adaptations / self.total_feedback_processed
                if self.total_feedback_processed > 0
                else 0.0
            )

            recent_updates = self.learning_history[-10:]  # Last 10 updates
            avg_improvement = (
                sum(u.improvement_score for u in recent_updates) / len(recent_updates)
                if recent_updates
                else 0.0
            )

            return {
                "total_feedback_processed": self.total_feedback_processed,
                "successful_adaptations": self.successful_adaptations,
                "adaptation_rate": adaptation_rate,
                "constitutional_violations_prevented": self.constitutional_violations_prevented,
                "current_learning_rate": self.learning_rate,
                "current_constitutional_weight": self.constitutional_weight,
                "recent_average_improvement": avg_improvement,
                "active_strategies": [s.value for s in self.active_strategies],
                "adaptation_parameters": self.adaptation_parameters.copy(),
            }

        except Exception as e:
            logger.exception(f"Failed to generate learning summary: {e}")
            return {"error": str(e)}

    async def batch_process_feedback(
        self, feedback_batch: list[FeedbackSignal]
    ) -> list[LearningUpdate]:
        """Process multiple feedback signals in batch."""
        try:
            updates = []

            for feedback in feedback_batch:
                update = await self.process_feedback_signal(feedback)
                if update:
                    updates.append(update)

            logger.info(
                f"Batch processed {len(feedback_batch)} feedback signals, generated {len(updates)} updates"
            )
            return updates

        except Exception as e:
            logger.exception(f"Batch feedback processing failed: {e}")
            return []

    def create_feedback_signal(
        self,
        signal_id: str,
        feedback_type: FeedbackType,
        source: str,
        value: float,
        context: dict[str, Any] | None = None,
    ) -> FeedbackSignal:
        """Create a new feedback signal."""
        return FeedbackSignal(
            signal_id=signal_id,
            feedback_type=feedback_type,
            source=source,
            value=value,
            context=context or {},
        )


# Global learning system instance
_learning_system_instance = None


async def get_wina_learning_system(
    config: dict[str, Any] | None = None
) -> WINALearningSystem:
    """
    Get or create the global WINA learning system instance.

    Args:
        config: WINA configuration (used only for first initialization)

    Returns:
        WINALearningSystem instance
    """
    global _learning_system_instance

    if _learning_system_instance is None:
        if config is None:
            # Use default configuration
            config = {"learning_rate": 0.01, "constitutional": {"learning_weight": 0.4}}

        _learning_system_instance = WINALearningSystem(config)
        logger.info("Global WINA learning system created")

    return _learning_system_instance


def reset_wina_learning_system():
    """Reset the global learning system instance (for testing)."""
    global _learning_system_instance
    _learning_system_instance = None
