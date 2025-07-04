"""
Sliding Window UCB Algorithm for Non-Stationary Environment Handling

This module implements the Sliding Window Upper Confidence Bound (SW-UCB) algorithm
specifically designed for handling non-stationary environments in AI governance.
It adapts to changing conditions while maintaining safety and constitutional compliance.

Key Features:
- Sliding window for recent reward tracking
- Change detection mechanisms
- Adaptive window sizing
- Constitutional compliance integration
- Performance monitoring and alerting
- Integration with existing ACGS MAB framework

Based on research in non-stationary multi-armed bandits and adaptive algorithms.
"""

import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
from scipy import stats

from .mab_prompt_optimizer import MABAlgorithmBase, MABConfig

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


@dataclass
class SlidingWindowConfig:
    """Configuration for Sliding Window UCB algorithm."""

    # Window parameters
    initial_window_size: int = 1000
    min_window_size: int = 100
    max_window_size: int = 5000
    adaptive_window: bool = True

    # UCB parameters
    alpha: float = 1.0  # Confidence parameter
    exploration_bonus: float = 0.1

    # Change detection
    change_detection_enabled: bool = True
    change_threshold: float = 0.05  # Threshold for detecting changes
    min_samples_for_detection: int = 50
    detection_window_ratio: float = 0.3  # Fraction of window for change detection

    # Adaptation parameters
    adaptation_rate: float = 0.1
    performance_threshold: float = 0.8
    stability_threshold: float = 0.05

    # Constitutional compliance
    constitutional_weight: float = 0.3
    safety_weight: float = 0.4
    performance_weight: float = 0.3

    # Monitoring
    alert_on_change: bool = True
    log_adaptations: bool = True


@dataclass
class ArmWindow:
    """Sliding window data for a single arm."""

    arm_id: str
    rewards: deque = field(default_factory=deque)
    contexts: deque = field(default_factory=deque)
    timestamps: deque = field(default_factory=deque)
    constitutional_scores: deque = field(default_factory=deque)
    safety_scores: deque = field(default_factory=deque)

    # Statistics
    total_pulls: int = 0
    window_mean: float = 0.0
    window_variance: float = 0.0
    last_change_detection: datetime | None = None
    change_detected: bool = False

    # Performance tracking
    recent_performance: float = 0.0
    performance_trend: float = 0.0
    stability_score: float = 1.0


@dataclass
class ChangeDetectionResult:
    """Result of change detection analysis."""

    arm_id: str
    change_detected: bool
    change_magnitude: float
    change_timestamp: datetime
    confidence: float
    detection_method: str
    old_mean: float
    new_mean: float


class SlidingWindowUCB(MABAlgorithmBase):
    """
    Sliding Window UCB algorithm for non-stationary environments.

    Implements adaptive window sizing, change detection, and constitutional
    compliance monitoring for AI governance applications.
    """

    def __init__(self, config: SlidingWindowConfig):
        """Initialize Sliding Window UCB algorithm."""
        super().__init__(MABConfig())  # Initialize base class
        self.config = config
        self.arm_windows: dict[str, ArmWindow] = {}
        self.global_window_size = config.initial_window_size
        self.total_rounds = 0

        # Change detection tracking
        self.change_history: list[ChangeDetectionResult] = []
        self.environment_stability = 1.0
        self.last_adaptation_time = datetime.now(timezone.utc)

        # Performance monitoring
        self.performance_metrics = {
            "total_changes_detected": 0,
            "total_adaptations": 0,
            "average_window_size": config.initial_window_size,
            "environment_stability": 1.0,
            "constitutional_compliance_rate": 1.0,
        }

        logger.info(f"Initialized Sliding Window UCB with config: {config}")

    def select_arm(
        self, context: dict[str, Any] = None, available_arms: list[str] = None
    ) -> str | None:
        """Select arm using Sliding Window UCB algorithm."""
        if not available_arms:
            logger.warning("No available arms for selection")
            return None

        context = context or {}

        # Initialize arms if needed
        for arm_id in available_arms:
            if arm_id not in self.arm_windows:
                self._initialize_arm(arm_id)

        # Perform change detection if enabled
        if self.config.change_detection_enabled:
            self._detect_changes(available_arms)

        # Adapt window sizes if needed
        if self.config.adaptive_window:
            self._adapt_window_sizes()

        # Calculate UCB values for available arms
        ucb_values = {}
        for arm_id in available_arms:
            arm_window = self.arm_windows[arm_id]

            if len(arm_window.rewards) == 0:
                # Unplayed arm gets maximum priority
                ucb_values[arm_id] = float("inf")
            else:
                # Calculate UCB value
                mean_reward = arm_window.window_mean
                n_pulls = len(arm_window.rewards)

                # Confidence bound
                confidence = self.config.alpha * np.sqrt(
                    np.log(self.total_rounds + 1) / n_pulls
                )

                # Constitutional and safety bonuses
                constitutional_bonus = self._calculate_constitutional_bonus(arm_window)
                safety_bonus = self._calculate_safety_bonus(arm_window)

                # Exploration bonus for recently changed arms
                change_bonus = (
                    self.config.exploration_bonus if arm_window.change_detected else 0.0
                )

                ucb_values[arm_id] = (
                    mean_reward
                    + confidence
                    + constitutional_bonus
                    + safety_bonus
                    + change_bonus
                )

        # Select arm with highest UCB value
        if not ucb_values:
            return available_arms[0] if available_arms else None

        selected_arm = max(ucb_values.keys(), key=lambda x: ucb_values[x])

        logger.debug(
            f"Selected arm {selected_arm} with UCB {ucb_values[selected_arm]:.3f}"
        )

        return selected_arm

    def update_reward(self, arm_id: str, reward: float, context: dict[str, Any] = None):
        """Update arm statistics with new reward observation."""
        if arm_id not in self.arm_windows:
            self._initialize_arm(arm_id)

        context = context or {}
        arm_window = self.arm_windows[arm_id]
        current_time = datetime.now(timezone.utc)

        # Add new observation to window
        arm_window.rewards.append(reward)
        arm_window.contexts.append(context)
        arm_window.timestamps.append(current_time)
        arm_window.total_pulls += 1

        # Add constitutional and safety scores
        constitutional_score = context.get("constitutional_compliance", 0.5)
        safety_score = context.get("safety_score", 0.5)
        arm_window.constitutional_scores.append(constitutional_score)
        arm_window.safety_scores.append(safety_score)

        # Maintain window size
        current_window_size = self._get_current_window_size(arm_id)
        while len(arm_window.rewards) > current_window_size:
            arm_window.rewards.popleft()
            arm_window.contexts.popleft()
            arm_window.timestamps.popleft()
            arm_window.constitutional_scores.popleft()
            arm_window.safety_scores.popleft()

        # Update statistics
        self._update_arm_statistics(arm_window)

        # Update global counters
        self.total_rounds += 1

        # Update performance metrics
        self._update_performance_metrics()

        logger.debug(
            f"Updated arm {arm_id}: window_size={len(arm_window.rewards)}, "
            f"mean_reward={arm_window.window_mean:.3f}"
        )

    def _initialize_arm(self, arm_id: str) -> ArmWindow:
        """Initialize window for a new arm."""
        arm_window = ArmWindow(arm_id=arm_id)
        self.arm_windows[arm_id] = arm_window
        logger.debug(f"Initialized new arm window: {arm_id}")
        return arm_window

    def _get_current_window_size(self, arm_id: str) -> int:
        """Get current window size for an arm."""
        if not self.config.adaptive_window:
            return self.config.initial_window_size

        arm_window = self.arm_windows.get(arm_id)
        if not arm_window:
            return self.config.initial_window_size

        # Adapt based on stability and performance
        base_size = self.global_window_size

        # Reduce window size if changes detected
        if arm_window.change_detected:
            base_size = int(base_size * 0.7)

        # Adjust based on stability
        stability_factor = arm_window.stability_score
        adjusted_size = int(base_size * (0.5 + 0.5 * stability_factor))

        # Ensure within bounds
        return max(
            self.config.min_window_size, min(self.config.max_window_size, adjusted_size)
        )

    def _update_arm_statistics(self, arm_window: ArmWindow):
        """Update statistics for an arm window."""
        if not arm_window.rewards:
            return

        rewards = list(arm_window.rewards)

        # Calculate basic statistics
        arm_window.window_mean = np.mean(rewards)
        arm_window.window_variance = np.var(rewards) if len(rewards) > 1 else 0.0

        # Calculate recent performance (last 20% of window)
        recent_size = max(1, len(rewards) // 5)
        recent_rewards = rewards[-recent_size:]
        arm_window.recent_performance = np.mean(recent_rewards)

        # Calculate performance trend
        if len(rewards) >= 10:
            half_point = len(rewards) // 2
            first_half_mean = np.mean(rewards[:half_point])
            second_half_mean = np.mean(rewards[half_point:])
            arm_window.performance_trend = second_half_mean - first_half_mean

        # Calculate stability score (inverse of variance)
        arm_window.stability_score = 1.0 / (1.0 + arm_window.window_variance)

    def _calculate_constitutional_bonus(self, arm_window: ArmWindow) -> float:
        """Calculate constitutional compliance bonus."""
        if not arm_window.constitutional_scores:
            return 0.0

        avg_constitutional = np.mean(list(arm_window.constitutional_scores))
        return self.config.constitutional_weight * avg_constitutional

    def _calculate_safety_bonus(self, arm_window: ArmWindow) -> float:
        """Calculate safety compliance bonus."""
        if not arm_window.safety_scores:
            return 0.0

        avg_safety = np.mean(list(arm_window.safety_scores))
        return self.config.safety_weight * avg_safety

    def _detect_changes(self, available_arms: list[str]):
        """Detect changes in arm performance using statistical tests."""
        for arm_id in available_arms:
            arm_window = self.arm_windows.get(arm_id)
            if (
                not arm_window
                or len(arm_window.rewards) < self.config.min_samples_for_detection
            ):
                continue

            # Perform change detection
            change_result = self._perform_change_detection(arm_window)

            if change_result.change_detected:
                # Update arm state
                arm_window.change_detected = True
                arm_window.last_change_detection = change_result.change_timestamp

                # Log the change
                self.change_history.append(change_result)
                self.performance_metrics["total_changes_detected"] += 1

                if self.config.log_adaptations:
                    logger.info(
                        f"Change detected in arm {arm_id}: "
                        f"magnitude={change_result.change_magnitude:.3f}, "
                        f"method={change_result.detection_method}"
                    )

                # Alert if configured
                if self.config.alert_on_change:
                    self._send_change_alert(change_result)
            # Reset change flag if no recent changes
            elif arm_window.change_detected:
                time_since_change = (
                    datetime.now(timezone.utc) - arm_window.last_change_detection
                ).total_seconds()
                if time_since_change > 300:  # 5 minutes
                    arm_window.change_detected = False

    def _perform_change_detection(self, arm_window: ArmWindow) -> ChangeDetectionResult:
        """Perform statistical change detection on an arm."""
        rewards = list(arm_window.rewards)
        n_rewards = len(rewards)

        # Calculate detection window size
        detection_window = int(n_rewards * self.config.detection_window_ratio)
        detection_window = max(
            self.config.min_samples_for_detection // 2, detection_window
        )

        if detection_window * 2 > n_rewards:
            return ChangeDetectionResult(
                arm_id=arm_window.arm_id,
                change_detected=False,
                change_magnitude=0.0,
                change_timestamp=datetime.now(timezone.utc),
                confidence=0.0,
                detection_method="insufficient_data",
                old_mean=0.0,
                new_mean=0.0,
            )

        # Split into old and new windows
        old_window = rewards[:-detection_window]
        new_window = rewards[-detection_window:]

        old_mean = np.mean(old_window)
        new_mean = np.mean(new_window)

        # Perform t-test for mean change
        try:
            t_stat, p_value = stats.ttest_ind(old_window, new_window)
            change_magnitude = abs(new_mean - old_mean)

            # Determine if change is significant
            change_detected = (
                p_value < 0.05 and change_magnitude > self.config.change_threshold
            )

            confidence = 1.0 - p_value if change_detected else 0.0

        except Exception as e:
            logger.warning(f"Change detection failed for {arm_window.arm_id}: {e}")
            change_detected = False
            change_magnitude = 0.0
            confidence = 0.0

        return ChangeDetectionResult(
            arm_id=arm_window.arm_id,
            change_detected=change_detected,
            change_magnitude=change_magnitude,
            change_timestamp=datetime.now(timezone.utc),
            confidence=confidence,
            detection_method="t_test",
            old_mean=old_mean,
            new_mean=new_mean,
        )

    def _adapt_window_sizes(self):
        """Adapt window sizes based on environment stability."""
        if not self.config.adaptive_window:
            return

        # Calculate overall environment stability
        recent_changes = [
            c
            for c in self.change_history
            if (datetime.now(timezone.utc) - c.change_timestamp).total_seconds() < 3600
        ]

        change_rate = len(recent_changes) / max(1, len(self.arm_windows))
        self.environment_stability = max(0.1, 1.0 - change_rate)

        # Adapt global window size
        if self.environment_stability < 0.5:
            # Unstable environment - reduce window size
            target_size = int(self.config.initial_window_size * 0.7)
        elif self.environment_stability > 0.8:
            # Stable environment - increase window size
            target_size = int(self.config.initial_window_size * 1.3)
        else:
            # Moderate stability - use default size
            target_size = self.config.initial_window_size

        # Apply adaptation rate
        size_diff = target_size - self.global_window_size
        adaptation = size_diff * self.config.adaptation_rate
        self.global_window_size = int(self.global_window_size + adaptation)

        # Ensure within bounds
        self.global_window_size = max(
            self.config.min_window_size,
            min(self.config.max_window_size, self.global_window_size),
        )

        # Update metrics
        self.performance_metrics["average_window_size"] = self.global_window_size
        self.performance_metrics["environment_stability"] = self.environment_stability

    def _send_change_alert(self, change_result: ChangeDetectionResult):
        """Send alert for detected change."""
        # This would integrate with the monitoring/alerting system
        logger.warning(
            f"CHANGE ALERT: {change_result.arm_id} - "
            f"Magnitude: {change_result.change_magnitude:.3f}, "
            f"Confidence: {change_result.confidence:.3f}"
        )

    def _update_performance_metrics(self):
        """Update performance metrics."""
        if not self.arm_windows:
            return

        # Calculate constitutional compliance rate
        total_constitutional = 0.0
        total_samples = 0

        for arm_window in self.arm_windows.values():
            if arm_window.constitutional_scores:
                total_constitutional += sum(arm_window.constitutional_scores)
                total_samples += len(arm_window.constitutional_scores)

        if total_samples > 0:
            compliance_rate = total_constitutional / total_samples
            self.performance_metrics["constitutional_compliance_rate"] = compliance_rate

    def get_arm_statistics(self, arm_id: str) -> dict[str, Any] | None:
        """Get comprehensive statistics for an arm."""
        arm_window = self.arm_windows.get(arm_id)
        if not arm_window:
            return None

        return {
            "arm_id": arm_id,
            "total_pulls": arm_window.total_pulls,
            "window_size": len(arm_window.rewards),
            "window_mean": arm_window.window_mean,
            "window_variance": arm_window.window_variance,
            "recent_performance": arm_window.recent_performance,
            "performance_trend": arm_window.performance_trend,
            "stability_score": arm_window.stability_score,
            "change_detected": arm_window.change_detected,
            "last_change_detection": arm_window.last_change_detection,
            "constitutional_scores": {
                "mean": (
                    np.mean(list(arm_window.constitutional_scores))
                    if arm_window.constitutional_scores
                    else 0.0
                ),
                "count": len(arm_window.constitutional_scores),
            },
            "safety_scores": {
                "mean": (
                    np.mean(list(arm_window.safety_scores))
                    if arm_window.safety_scores
                    else 0.0
                ),
                "count": len(arm_window.safety_scores),
            },
        }

    def get_system_statistics(self) -> dict[str, Any]:
        """Get comprehensive system statistics."""
        return {
            "total_rounds": self.total_rounds,
            "global_window_size": self.global_window_size,
            "environment_stability": self.environment_stability,
            "active_arms": len(self.arm_windows),
            "total_changes_detected": len(self.change_history),
            "recent_changes": len(
                [
                    c
                    for c in self.change_history
                    if (datetime.now(timezone.utc) - c.change_timestamp).total_seconds()
                    < 3600
                ]
            ),
            "performance_metrics": self.performance_metrics,
            "config": {
                "adaptive_window": self.config.adaptive_window,
                "change_detection_enabled": self.config.change_detection_enabled,
                "change_threshold": self.config.change_threshold,
                "alpha": self.config.alpha,
            },
        }

    def reset_change_detection(self, arm_id: str = None):
        """Reset change detection for specific arm or all arms."""
        if arm_id:
            arm_window = self.arm_windows.get(arm_id)
            if arm_window:
                arm_window.change_detected = False
                arm_window.last_change_detection = None
                logger.info(f"Reset change detection for arm {arm_id}")
        else:
            for arm_window in self.arm_windows.values():
                arm_window.change_detected = False
                arm_window.last_change_detection = None
            self.change_history.clear()
            logger.info("Reset change detection for all arms")

    def export_change_history(self) -> list[dict[str, Any]]:
        """Export change detection history for analysis."""
        return [
            {
                "arm_id": change.arm_id,
                "change_detected": change.change_detected,
                "change_magnitude": change.change_magnitude,
                "change_timestamp": change.change_timestamp.isoformat(),
                "confidence": change.confidence,
                "detection_method": change.detection_method,
                "old_mean": change.old_mean,
                "new_mean": change.new_mean,
            }
            for change in self.change_history
        ]
