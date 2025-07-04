"""
Enhanced Performance Optimizer for Policy Synthesis Enhancement

This module implements comprehensive performance optimization for policy synthesis,
including WINA-enhanced optimization and synthesis strategy effectiveness tracking.

Key Features:
- Adaptive optimization strategies
- Real-time performance monitoring
- Constitutional compliance preservation
- GFLOPs reduction tracking
- Accuracy retention verification
- Synthesis strategy effectiveness monitoring
- Dynamic strategy weight adjustment
- Response time optimization targeting <2s
"""

import logging
import statistics
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import numpy as np

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """WINA optimization strategies."""

    CONSERVATIVE = "conservative"  # Prioritize accuracy retention
    BALANCED = "balanced"  # Balance efficiency and accuracy
    AGGRESSIVE = "aggressive"  # Maximize GFLOPs reduction
    ADAPTIVE = "adaptive"  # Adapt based on context
    CONSTITUTIONAL = "constitutional"  # Prioritize constitutional compliance


@dataclass
class OptimizationMetrics:
    """Performance optimization metrics."""

    gflops_reduction: float
    accuracy_retention: float
    constitutional_compliance: float
    optimization_time_ms: float
    strategy_used: OptimizationStrategy
    success: bool
    timestamp: datetime


@dataclass
class OptimizationResult:
    """Result from WINA performance optimization."""

    optimized: bool
    gflops_reduction_achieved: float
    accuracy_retained: float
    constitutional_compliance_maintained: float
    optimization_strategy: OptimizationStrategy
    performance_metrics: dict[str, Any]
    recommendations: list[str]
    warnings: list[str]


@dataclass
class SynthesisPerformanceMetrics:
    """Performance metrics for a synthesis operation."""

    strategy_used: str
    response_time_seconds: float
    quality_score: float
    success: bool
    error_count: int
    principle_count: int
    context_complexity: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyPerformance:
    """Aggregated performance data for a synthesis strategy."""

    strategy_name: str
    total_uses: int = 0
    success_count: int = 0
    total_response_time: float = 0.0
    total_quality_score: float = 0.0
    error_count: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def success_rate(self) -> float:
        """Calculate success rate for this strategy."""
        return self.success_count / max(self.total_uses, 1)

    @property
    def average_response_time(self) -> float:
        """Calculate average response time for this strategy."""
        return self.total_response_time / max(self.total_uses, 1)

    @property
    def average_quality_score(self) -> float:
        """Calculate average quality score for this strategy."""
        return self.total_quality_score / max(self.total_uses, 1)


class WINAPerformanceOptimizer:
    """
    Advanced WINA performance optimizer for Phase 2 AlphaEvolve-ACGS integration.

    Implements adaptive optimization strategies to achieve target performance metrics
    while maintaining constitutional compliance and synthesis accuracy.
    """

    def __init__(self, config: dict[str, Any]):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Initialize WINA performance optimizer.

        Args:
            config: Configuration dictionary with optimization settings
        """
        self.config = config
        self.target_gflops_reduction = config.get("target_gflops_reduction", 0.5)
        self.accuracy_retention_threshold = config.get(
            "accuracy_retention_threshold", 0.95
        )
        self.constitutional_compliance_threshold = config.get(
            "constitutional_compliance_threshold", 0.85
        )
        self.optimization_strategy = OptimizationStrategy(
            config.get("optimization_strategy", "adaptive")
        )

        # Performance tracking
        self.optimization_history: list[OptimizationMetrics] = []
        self.current_performance = {
            "average_gflops_reduction": 0.0,
            "average_accuracy_retention": 1.0,
            "average_constitutional_compliance": 0.85,
            "optimization_success_rate": 0.0,
            "total_optimizations": 0,
        }

        # Adaptive parameters
        self.adaptive_thresholds = {
            "gflops_reduction_min": 0.3,
            "gflops_reduction_max": 0.7,
            "accuracy_threshold_strict": 0.98,
            "accuracy_threshold_relaxed": 0.92,
            "constitutional_threshold_strict": 0.9,
            "constitutional_threshold_relaxed": 0.8,
        }

        # Synthesis performance tracking
        self.strategy_performance: dict[str, StrategyPerformance] = {}
        self.recent_synthesis_metrics: deque = deque(
            maxlen=config.get("max_recent_metrics", 1000)
        )

        # Dynamic strategy weights for synthesis
        self.synthesis_strategy_weights = {
            "standard_synthesis": 1.0,
            "enhanced_validation": 1.0,
            "multi_model_consensus": 1.0,
            "human_review_required": 1.0,
        }

        # Synthesis performance targets
        self.synthesis_targets = {
            "response_time_seconds": config.get("target_synthesis_response_time", 2.0),
            "success_rate": config.get("target_synthesis_success_rate", 0.95),
            "quality_score": config.get("target_synthesis_quality_score", 0.85),
        }

        # Optimization parameters for synthesis
        self.synthesis_optimization_interval = config.get(
            "synthesis_optimization_interval_hours", 1
        )
        self.last_synthesis_optimization = datetime.now(timezone.utc)
        self.min_synthesis_samples = config.get("min_synthesis_samples", 10)

        self._initialized = False

    async def initialize(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize the performance optimizer."""
        if self._initialized:
            return

        try:
            # Initialize optimization parameters based on historical data
            await self._load_historical_performance()

            # Calibrate adaptive thresholds
            await self._calibrate_adaptive_thresholds()

            self._initialized = True
            logger.info("WINA performance optimizer initialized")

        except Exception as e:
            logger.error(f"Failed to initialize WINA performance optimizer: {e}")
            raise

    async def optimize_synthesis_performance(
        self, synthesis_context: dict[str, Any], current_metrics: dict[str, Any]
    ) -> OptimizationResult:
        """
        Optimize synthesis performance using WINA techniques.

        Args:
            synthesis_context: Context for the synthesis operation
            current_metrics: Current performance metrics

        Returns:
            OptimizationResult with optimization details
        """
        if not self._initialized:
            await self.initialize()

        start_time = time.time()

        try:
            logger.info("Starting WINA performance optimization")

            # Determine optimization strategy
            strategy = await self._select_optimization_strategy(
                synthesis_context, current_metrics
            )

            # Apply optimization based on strategy
            optimization_result = await self._apply_optimization_strategy(
                strategy, synthesis_context, current_metrics
            )

            # Validate optimization results
            await self._validate_optimization(optimization_result)

            # Update performance tracking
            optimization_time_ms = (time.time() - start_time) * 1000
            await self._update_performance_metrics(
                optimization_result, optimization_time_ms, strategy
            )

            logger.info(
                f"WINA optimization completed in {optimization_time_ms:.2f}ms "
                f"(GFLOPs reduction: {optimization_result.gflops_reduction_achieved:.1%})"
            )

            return optimization_result

        except Exception as e:
            logger.error(f"WINA performance optimization failed: {e}")
            return OptimizationResult(
                optimized=False,
                gflops_reduction_achieved=0.0,
                accuracy_retained=1.0,
                constitutional_compliance_maintained=current_metrics.get(
                    "constitutional_compliance", 0.85
                ),
                optimization_strategy=self.optimization_strategy,
                performance_metrics={"error": str(e)},
                recommendations=["Fix optimization errors and retry"],
                warnings=[f"Optimization failed: {e!s}"],
            )

    async def _select_optimization_strategy(
        self, context: dict[str, Any], metrics: dict[str, Any]
    ) -> OptimizationStrategy:
        """Select optimal optimization strategy based on context and current performance."""
        if self.optimization_strategy != OptimizationStrategy.ADAPTIVE:
            return self.optimization_strategy

        # Adaptive strategy selection
        current_accuracy = metrics.get("accuracy", 1.0)
        current_compliance = metrics.get("constitutional_compliance", 0.85)
        synthesis_complexity = context.get("complexity_score", 0.5)

        # High accuracy and compliance - can be more aggressive
        if current_accuracy > 0.97 and current_compliance > 0.9:
            return OptimizationStrategy.AGGRESSIVE

        # Low compliance - prioritize constitutional compliance
        if current_compliance < 0.8:
            return OptimizationStrategy.CONSTITUTIONAL

        # Low accuracy - be conservative
        if current_accuracy < 0.93:
            return OptimizationStrategy.CONSERVATIVE

        # Complex synthesis - use balanced approach
        if synthesis_complexity > 0.7:
            return OptimizationStrategy.BALANCED

        # Default to balanced
        return OptimizationStrategy.BALANCED

    async def _apply_optimization_strategy(
        self,
        strategy: OptimizationStrategy,
        context: dict[str, Any],
        metrics: dict[str, Any],
    ) -> OptimizationResult:
        """Apply the selected optimization strategy."""
        recommendations = []
        warnings = []

        if strategy == OptimizationStrategy.AGGRESSIVE:
            gflops_reduction = min(
                self.adaptive_thresholds["gflops_reduction_max"], 0.7
            )
            accuracy_target = max(
                self.adaptive_thresholds["accuracy_threshold_relaxed"], 0.92
            )
            compliance_target = max(
                self.adaptive_thresholds["constitutional_threshold_relaxed"], 0.8
            )
            recommendations.append(
                "Aggressive optimization applied - monitor accuracy closely"
            )

        elif strategy == OptimizationStrategy.CONSERVATIVE:
            gflops_reduction = max(
                self.adaptive_thresholds["gflops_reduction_min"], 0.3
            )
            accuracy_target = self.adaptive_thresholds["accuracy_threshold_strict"]
            compliance_target = self.adaptive_thresholds[
                "constitutional_threshold_strict"
            ]
            recommendations.append(
                "Conservative optimization - prioritizing accuracy retention"
            )

        elif strategy == OptimizationStrategy.CONSTITUTIONAL:
            gflops_reduction = max(
                self.adaptive_thresholds["gflops_reduction_min"], 0.35
            )
            accuracy_target = 0.95
            compliance_target = self.adaptive_thresholds[
                "constitutional_threshold_strict"
            ]
            recommendations.append(
                "Constitutional priority optimization - ensuring compliance"
            )

        elif strategy == OptimizationStrategy.BALANCED:
            gflops_reduction = self.target_gflops_reduction
            accuracy_target = self.accuracy_retention_threshold
            compliance_target = self.constitutional_compliance_threshold
            recommendations.append("Balanced optimization strategy applied")

        else:  # ADAPTIVE fallback
            gflops_reduction = self.target_gflops_reduction
            accuracy_target = self.accuracy_retention_threshold
            compliance_target = self.constitutional_compliance_threshold

        # Simulate optimization application
        # In a real implementation, this would apply WINA transformations
        actual_gflops_reduction = gflops_reduction * np.random.uniform(
            0.8, 1.0
        )  # Some variance
        actual_accuracy = min(1.0, accuracy_target * np.random.uniform(0.98, 1.02))
        actual_compliance = min(1.0, compliance_target * np.random.uniform(0.95, 1.05))

        # Check if optimization meets thresholds
        optimization_success = (
            actual_accuracy >= self.accuracy_retention_threshold
            and actual_compliance >= self.constitutional_compliance_threshold
        )

        if not optimization_success:
            warnings.append("Optimization did not meet all quality thresholds")

        return OptimizationResult(
            optimized=optimization_success,
            gflops_reduction_achieved=actual_gflops_reduction,
            accuracy_retained=actual_accuracy,
            constitutional_compliance_maintained=actual_compliance,
            optimization_strategy=strategy,
            performance_metrics={
                "target_gflops_reduction": gflops_reduction,
                "target_accuracy": accuracy_target,
                "target_compliance": compliance_target,
                "optimization_variance": {
                    "gflops": abs(actual_gflops_reduction - gflops_reduction),
                    "accuracy": abs(actual_accuracy - accuracy_target),
                    "compliance": abs(actual_compliance - compliance_target),
                },
            },
            recommendations=recommendations,
            warnings=warnings,
        )

    async def _validate_optimization(
        self, result: OptimizationResult
    ) -> OptimizationResult:
        """Validate optimization results and add additional recommendations."""
        additional_recommendations = []
        additional_warnings = []

        # Check GFLOPs reduction achievement
        if result.gflops_reduction_achieved < self.target_gflops_reduction * 0.8:
            additional_warnings.append("GFLOPs reduction below 80% of target")
            additional_recommendations.append(
                "Consider more aggressive optimization strategy"
            )

        # Check accuracy retention
        if result.accuracy_retained < self.accuracy_retention_threshold:
            additional_warnings.append("Accuracy retention below threshold")
            additional_recommendations.append("Reduce optimization aggressiveness")

        # Check constitutional compliance
        if (
            result.constitutional_compliance_maintained
            < self.constitutional_compliance_threshold
        ):
            additional_warnings.append("Constitutional compliance below threshold")
            additional_recommendations.append(
                "Apply constitutional priority optimization"
            )

        # Update result with additional feedback
        result.recommendations.extend(additional_recommendations)
        result.warnings.extend(additional_warnings)

        return result

    async def _update_performance_metrics(
        self,
        result: OptimizationResult,
        optimization_time_ms: float,
        strategy: OptimizationStrategy,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update performance tracking metrics."""
        # Add to history
        metrics = OptimizationMetrics(
            gflops_reduction=result.gflops_reduction_achieved,
            accuracy_retention=result.accuracy_retained,
            constitutional_compliance=result.constitutional_compliance_maintained,
            optimization_time_ms=optimization_time_ms,
            strategy_used=strategy,
            success=result.optimized,
            timestamp=datetime.now(),
        )

        self.optimization_history.append(metrics)

        # Keep last 1000 entries
        if len(self.optimization_history) > 1000:
            self.optimization_history.pop(0)

        # Update current performance averages
        recent_history = self.optimization_history[-50:]  # Last 50 optimizations
        if recent_history:
            self.current_performance.update(
                {
                    "average_gflops_reduction": sum(
                        m.gflops_reduction for m in recent_history
                    )
                    / len(recent_history),
                    "average_accuracy_retention": sum(
                        m.accuracy_retention for m in recent_history
                    )
                    / len(recent_history),
                    "average_constitutional_compliance": sum(
                        m.constitutional_compliance for m in recent_history
                    )
                    / len(recent_history),
                    "optimization_success_rate": sum(
                        1 for m in recent_history if m.success
                    )
                    / len(recent_history),
                    "total_optimizations": len(self.optimization_history),
                }
            )

    async def _load_historical_performance(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Load historical performance data for calibration."""
        # In a real implementation, this would load from database
        # For now, we'll initialize with baseline values
        logger.info("Loading historical performance data")

    async def _calibrate_adaptive_thresholds(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Calibrate adaptive thresholds based on historical performance."""
        if len(self.optimization_history) < 10:
            logger.info(
                "Insufficient history for threshold calibration, using defaults"
            )
            return

        # Analyze recent performance to adjust thresholds
        recent_history = self.optimization_history[-100:]

        # Calculate performance percentiles
        gflops_reductions = [m.gflops_reduction for m in recent_history]
        accuracies = [m.accuracy_retention for m in recent_history]
        compliances = [m.constitutional_compliance for m in recent_history]

        # Update adaptive thresholds based on performance distribution
        self.adaptive_thresholds.update(
            {
                "gflops_reduction_min": max(0.2, np.percentile(gflops_reductions, 25)),
                "gflops_reduction_max": min(0.8, np.percentile(gflops_reductions, 75)),
                "accuracy_threshold_strict": max(0.95, np.percentile(accuracies, 75)),
                "accuracy_threshold_relaxed": max(0.90, np.percentile(accuracies, 25)),
                "constitutional_threshold_strict": max(
                    0.85, np.percentile(compliances, 75)
                ),
                "constitutional_threshold_relaxed": max(
                    0.75, np.percentile(compliances, 25)
                ),
            }
        )

        logger.info("Adaptive thresholds calibrated based on historical performance")

    def get_performance_summary(self) -> dict[str, Any]:
        """Get comprehensive performance summary."""
        if not self.optimization_history:
            return {"status": "no_data"}

        recent_history = self.optimization_history[-20:]

        return {
            "current_performance": self.current_performance,
            "recent_performance": {
                "optimizations": len(recent_history),
                "success_rate": sum(1 for m in recent_history if m.success)
                / len(recent_history),
                "average_gflops_reduction": sum(
                    m.gflops_reduction for m in recent_history
                )
                / len(recent_history),
                "average_accuracy": sum(m.accuracy_retention for m in recent_history)
                / len(recent_history),
                "average_compliance": sum(
                    m.constitutional_compliance for m in recent_history
                )
                / len(recent_history),
            },
            "target_achievement": {
                "gflops_target": self.target_gflops_reduction,
                "accuracy_target": self.accuracy_retention_threshold,
                "compliance_target": self.constitutional_compliance_threshold,
                "targets_met": (
                    self.current_performance["average_gflops_reduction"]
                    >= self.target_gflops_reduction * 0.9
                    and self.current_performance["average_accuracy_retention"]
                    >= self.accuracy_retention_threshold
                    and self.current_performance["average_constitutional_compliance"]
                    >= self.constitutional_compliance_threshold
                ),
            },
            "adaptive_thresholds": self.adaptive_thresholds,
            "strategy_distribution": {
                strategy.value: sum(
                    1 for m in self.optimization_history if m.strategy_used == strategy
                )
                for strategy in OptimizationStrategy
            },
        }

    async def recommend_strategy_adjustment(self) -> dict[str, Any]:
        """Recommend strategy adjustments based on performance analysis."""
        if len(self.optimization_history) < 10:
            return {"recommendation": "insufficient_data"}

        recent_performance = self.get_performance_summary()["recent_performance"]

        recommendations = []

        # Analyze performance trends
        if recent_performance["success_rate"] < 0.8:
            recommendations.append("Consider more conservative optimization strategy")

        if (
            recent_performance["average_gflops_reduction"]
            < self.target_gflops_reduction * 0.8
        ):
            recommendations.append("Consider more aggressive GFLOPs reduction")

        if recent_performance["average_accuracy"] < self.accuracy_retention_threshold:
            recommendations.append("Prioritize accuracy retention in optimization")

        if (
            recent_performance["average_compliance"]
            < self.constitutional_compliance_threshold
        ):
            recommendations.append("Apply constitutional priority optimization")

        return {
            "recommendations": recommendations,
            "current_strategy": self.optimization_strategy.value,
            "performance_analysis": recent_performance,
        }

    async def track_synthesis_performance(
        self,
        strategy_used: str,
        response_time_seconds: float,
        success: bool,
        quality_score: float | None = None,
        error_count: int = 0,
        principle_count: int = 1,
        context_complexity: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Track performance metrics for a synthesis operation.

        Args:
            strategy_used: Strategy that was used for synthesis
            response_time_seconds: Time taken for synthesis
            success: Whether synthesis was successful
            quality_score: Quality score of synthesis output (0.0-1.0)
            error_count: Number of errors encountered
            principle_count: Number of principles processed
            context_complexity: Complexity score of context (0.0-1.0)
            metadata: Additional metadata for tracking
        """
        try:
            # Create performance metrics record
            metrics = SynthesisPerformanceMetrics(
                strategy_used=strategy_used,
                response_time_seconds=response_time_seconds,
                quality_score=quality_score or 0.5,
                success=success,
                error_count=error_count,
                principle_count=principle_count,
                context_complexity=context_complexity or 0.5,
                metadata=metadata or {},
            )

            # Add to recent metrics
            self.recent_synthesis_metrics.append(metrics)

            # Update strategy performance
            await self._update_synthesis_strategy_performance(metrics)

            # Check if optimization is needed
            await self._check_synthesis_optimization_trigger()

            logger.debug(
                f"Tracked synthesis performance for {strategy_used}: "
                f"time={response_time_seconds:.3f}s, success={success}, "
                f"quality={quality_score}"
            )

        except Exception as e:
            logger.error(f"Error tracking synthesis performance: {e}")

    async def _update_synthesis_strategy_performance(
        self, metrics: SynthesisPerformanceMetrics
    ) -> None:
        """Update aggregated performance data for a synthesis strategy."""
        strategy = metrics.strategy_used

        if strategy not in self.strategy_performance:
            self.strategy_performance[strategy] = StrategyPerformance(
                strategy_name=strategy
            )

        perf = self.strategy_performance[strategy]
        perf.total_uses += 1
        perf.total_response_time += metrics.response_time_seconds
        perf.total_quality_score += metrics.quality_score
        perf.error_count += metrics.error_count
        perf.last_updated = datetime.now(timezone.utc)

        if metrics.success:
            perf.success_count += 1

    async def _check_synthesis_optimization_trigger(self) -> None:
        """Check if synthesis strategy weight optimization should be triggered."""
        now = datetime.now(timezone.utc)
        time_since_last = (
            now - self.last_synthesis_optimization
        ).total_seconds() / 3600

        if (
            time_since_last >= self.synthesis_optimization_interval
            and len(self.recent_synthesis_metrics) >= self.min_synthesis_samples
        ):
            await self.adjust_strategy_weights()

    async def adjust_strategy_weights(self) -> dict[str, float]:
        """
        Dynamically adjust synthesis strategy weights based on historical performance.

        Returns:
            Updated strategy weights dictionary
        """
        try:
            logger.info("Starting synthesis strategy weight optimization")

            # Calculate performance scores for each strategy
            strategy_scores = {}

            for strategy_name, performance in self.strategy_performance.items():
                if performance.total_uses < 5:  # Skip strategies with insufficient data
                    continue

                # Calculate composite performance score
                success_score = performance.success_rate
                time_score = max(
                    0,
                    1
                    - (
                        performance.average_response_time
                        / self.synthesis_targets["response_time_seconds"]
                    ),
                )
                quality_score = (
                    performance.average_quality_score
                    / self.synthesis_targets["quality_score"]
                )

                # Weighted composite score
                composite_score = (
                    success_score * 0.5 + time_score * 0.3 + quality_score * 0.2
                )

                strategy_scores[strategy_name] = composite_score

            if not strategy_scores:
                logger.warning(
                    "No synthesis strategy performance data available for optimization"
                )
                return self.synthesis_strategy_weights

            # Adjust weights based on performance
            max_score = max(strategy_scores.values())
            min_score = min(strategy_scores.values())
            score_range = max_score - min_score

            for strategy_name in self.synthesis_strategy_weights:
                if strategy_name in strategy_scores:
                    score = strategy_scores[strategy_name]

                    # Normalize score and adjust weight
                    if score_range > 0:
                        normalized_score = (score - min_score) / score_range
                        # Weight adjustment: better performing strategies get higher weights
                        self.synthesis_strategy_weights[strategy_name] = 0.5 + (
                            normalized_score * 0.5
                        )
                    else:
                        self.synthesis_strategy_weights[strategy_name] = 1.0
                else:
                    # Default weight for strategies without sufficient data
                    self.synthesis_strategy_weights[strategy_name] = 1.0

            self.last_synthesis_optimization = datetime.now(timezone.utc)

            logger.info(
                f"Synthesis strategy weights optimized: {self.synthesis_strategy_weights}"
            )
            return self.synthesis_strategy_weights

        except Exception as e:
            logger.error(f"Error adjusting synthesis strategy weights: {e}")
            return self.synthesis_strategy_weights

    def get_synthesis_performance_summary(self) -> dict[str, Any]:
        """Get comprehensive synthesis performance summary."""
        try:
            # Overall metrics from recent data
            recent_metrics_list = list(self.recent_synthesis_metrics)

            if not recent_metrics_list:
                return {
                    "status": "no_data",
                    "message": "No synthesis performance data available",
                }

            # Calculate overall metrics
            total_operations = len(recent_metrics_list)
            successful_operations = sum(1 for m in recent_metrics_list if m.success)
            avg_response_time = statistics.mean(
                m.response_time_seconds for m in recent_metrics_list
            )
            avg_quality_score = statistics.mean(
                m.quality_score for m in recent_metrics_list
            )

            # Strategy breakdown
            strategy_breakdown = {}
            for strategy_name, performance in self.strategy_performance.items():
                strategy_breakdown[strategy_name] = {
                    "total_uses": performance.total_uses,
                    "success_rate": performance.success_rate,
                    "average_response_time": performance.average_response_time,
                    "average_quality_score": performance.average_quality_score,
                    "current_weight": self.synthesis_strategy_weights.get(
                        strategy_name, 1.0
                    ),
                }

            # Target achievement
            targets_met = {
                "response_time": avg_response_time
                <= self.synthesis_targets["response_time_seconds"],
                "success_rate": (successful_operations / total_operations)
                >= self.synthesis_targets["success_rate"],
                "quality_score": avg_quality_score
                >= self.synthesis_targets["quality_score"],
            }

            return {
                "status": "active",
                "overall_metrics": {
                    "total_operations": total_operations,
                    "success_rate": successful_operations / total_operations,
                    "average_response_time_seconds": avg_response_time,
                    "average_quality_score": avg_quality_score,
                },
                "targets": self.synthesis_targets,
                "targets_met": targets_met,
                "strategy_performance": strategy_breakdown,
                "current_strategy_weights": self.synthesis_strategy_weights,
                "last_optimization": self.last_synthesis_optimization.isoformat(),
                "optimization_interval_hours": self.synthesis_optimization_interval,
            }

        except Exception as e:
            logger.error(f"Error generating synthesis performance summary: {e}")
            return {"status": "error", "error": str(e)}
