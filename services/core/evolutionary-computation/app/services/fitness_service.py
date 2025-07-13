"""
Fitness Service Module

Specialized service for fitness evaluation with constitutional compliance,
performance optimization, and automated scoring for evolutionary computation.
"""

import asyncio
import logging
import statistics
import time
from datetime import datetime, timedelta
from typing import Any, NamedTuple

import numpy as np
import redis.asyncio as aioredis
from prometheus_client import Counter, Gauge, Histogram

from ..core.constitutional_validator import ConstitutionalValidator
from ..models.evolution import FitnessMetrics, Individual

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class RegressionAlert(NamedTuple):
    """Regression detection alert."""

    metric_name: str
    current_value: float
    historical_mean: float
    severity: str  # "warning", "critical"
    threshold_violated: float
    timestamp: datetime


class RegressionDetector:
    """
    Advanced regression detection for policy evolution fitness metrics.

    Monitors fitness trends and alerts on significant degradations.
    """

    def __init__(self, lookback_days: int = 30, alert_threshold: float = 0.15):
        """
        Initialize regression detector.

        Args:
            lookback_days: Days of history to consider for baseline
            alert_threshold: Threshold for triggering alerts (15% degradation default)
        """
        self.lookback_days = lookback_days
        self.alert_threshold = alert_threshold
        self.fitness_history: dict[str, list[tuple[datetime, float]]] = {}
        self.alerts: list[RegressionAlert] = []

        logger.info(
            f"RegressionDetector initialized with {lookback_days}d lookback, {alert_threshold} threshold"
        )

    def record_fitness_metric(self, metric_name: str, value: float) -> None:
        """Record a fitness metric for regression analysis."""
        timestamp = datetime.utcnow()

        if metric_name not in self.fitness_history:
            self.fitness_history[metric_name] = []

        self.fitness_history[metric_name].append((timestamp, value))

        # Cleanup old data
        cutoff = timestamp - timedelta(days=self.lookback_days)
        self.fitness_history[metric_name] = [
            (ts, val) for ts, val in self.fitness_history[metric_name] if ts > cutoff
        ]

    def detect_regression(
        self, metric_name: str, current_value: float
    ) -> RegressionAlert | None:
        """
        Detect regression in fitness metrics.

        Args:
            metric_name: Name of the metric to check
            current_value: Current value to compare against historical data

        Returns:
            RegressionAlert if regression detected, None otherwise
        """
        if metric_name not in self.fitness_history:
            # No history to compare against
            return None

        history = self.fitness_history[metric_name]
        if len(history) < 10:  # Need at least 10 data points
            return None

        # Calculate historical statistics
        historical_values = [val for _, val in history]
        historical_mean = statistics.mean(historical_values)
        (statistics.stdev(historical_values) if len(historical_values) > 1 else 0)

        # Check for regression
        degradation = (
            (historical_mean - current_value) / historical_mean
            if historical_mean > 0
            else 0
        )

        if degradation > self.alert_threshold:
            severity = "critical" if degradation > 0.25 else "warning"

            alert = RegressionAlert(
                metric_name=metric_name,
                current_value=current_value,
                historical_mean=historical_mean,
                severity=severity,
                threshold_violated=degradation,
                timestamp=datetime.utcnow(),
            )

            self.alerts.append(alert)
            logger.warning(
                f"Regression detected in {metric_name}: {degradation:.2%} degradation"
            )

            return alert

        return None

    def get_recent_alerts(self, hours: int = 24) -> list[RegressionAlert]:
        """Get alerts from the last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert.timestamp > cutoff]


class MLFitnessPredictor:
    """
    Machine Learning-based fitness prediction for policy evolution.

    Uses historical data to predict and recommend fitness improvements.
    """

    def __init__(self):
        """Initialize ML fitness predictor."""
        self.training_data: list[tuple[dict[str, Any], float]] = []
        self.model_weights: dict[str, float] = {}
        self.is_trained = False

        logger.info("MLFitnessPredictor initialized")

    def add_training_data(self, genotype: dict[str, Any], fitness: float) -> None:
        """Add training data for the ML model."""
        self.training_data.append((genotype.copy(), fitness))

        # Keep only recent data (last 1000 samples)
        if len(self.training_data) > 1000:
            self.training_data = self.training_data[-1000:]

    def train_simple_model(self) -> None:
        """Train a simple linear model for fitness prediction."""
        if len(self.training_data) < 50:
            logger.warning("Insufficient training data for ML model")
            return

        # Extract features and targets
        all_features = set()
        for genotype, _ in self.training_data:
            all_features.update(genotype.keys())

        feature_list = sorted(all_features)

        # Create feature matrix
        X = []
        y = []

        for genotype, fitness in self.training_data:
            features = [genotype.get(feat, 0.0) for feat in feature_list]
            X.append(features)
            y.append(fitness)

        X = np.array(X)
        y = np.array(y)

        # Simple linear regression using normal equation
        try:
            # Add bias term
            X_with_bias = np.column_stack([np.ones(X.shape[0]), X])

            # Normal equation: w = (X^T X)^(-1) X^T y
            XtX = X_with_bias.T @ X_with_bias
            Xty = X_with_bias.T @ y

            weights = np.linalg.solve(XtX, Xty)

            # Store weights
            self.model_weights = {"bias": weights[0]}
            for i, feature in enumerate(feature_list):
                self.model_weights[feature] = weights[i + 1]

            self.is_trained = True
            logger.info(f"ML model trained with {len(self.training_data)} samples")

        except np.linalg.LinAlgError:
            logger.exception("Failed to train ML model - singular matrix")

    def predict_fitness(self, genotype: dict[str, Any]) -> float | None:
        """Predict fitness score using the trained model."""
        if not self.is_trained:
            return None

        # Calculate prediction
        prediction = self.model_weights.get("bias", 0.0)

        for feature, weight in self.model_weights.items():
            if feature != "bias":
                feature_value = genotype.get(feature, 0.0)
                prediction += weight * feature_value

        # Clamp to valid range
        return min(1.0, max(0.0, prediction))

    def suggest_improvements(self, genotype: dict[str, Any]) -> dict[str, float]:
        """Suggest improvements to genotype for better fitness."""
        if not self.is_trained:
            return {}

        suggestions = {}

        for feature, weight in self.model_weights.items():
            if feature != "bias" and weight > 0:
                current_value = genotype.get(feature, 0.0)
                # Suggest increasing positive-weight features
                if current_value < 0.9:
                    improvement = min(0.1, 1.0 - current_value)
                    suggestions[feature] = current_value + improvement

        return suggestions


class FitnessService:
    """
    Specialized fitness evaluation service with constitutional compliance.

    Provides automated fitness scoring with O(1) lookup patterns and
    sub-5ms P99 latency targets for optimal ACGS performance.
    """

    def __init__(self, redis_client: aioredis.Redis | None = None):
        """Initialize fitness service."""
        self.redis = redis_client
        self.constitutional_validator = ConstitutionalValidator()

        # Initialize advanced components
        self.regression_detector = RegressionDetector()
        self.ml_predictor = MLFitnessPredictor()

        self.setup_metrics()

        # Fitness evaluation cache for O(1) lookups
        self.fitness_cache: dict[str, FitnessMetrics] = {}
        self.evaluation_cache: dict[str, dict[str, float]] = {}

        # Fitness evaluation weights (configurable)
        self.fitness_weights = {
            "constitutional_compliance": 0.30,
            "performance_score": 0.20,
            "safety_score": 0.10,
            "fairness_score": 0.10,
            "efficiency_score": 0.10,
            "robustness_score": 0.10,
            "transparency_score": 0.05,
            "user_satisfaction": 0.05,
        }

        logger.info(
            "FitnessService initialized with constitutional compliance, regression detection, and ML prediction"
        )

    def setup_metrics(self) -> None:
        """Setup Prometheus metrics."""
        self.fitness_evaluations_total = Counter(
            "fitness_evaluations_total",
            "Total fitness evaluations",
            ["evaluation_type", "status"],
        )

        self.fitness_evaluation_duration = Histogram(
            "fitness_evaluation_duration_ms",
            "Fitness evaluation duration in milliseconds",
            ["evaluation_component"],
        )

        self.fitness_score_histogram = Histogram(
            "fitness_score_distribution",
            "Distribution of fitness scores",
            ["score_type"],
            buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        )

        # Regression detection metrics
        self.regression_alerts_total = Counter(
            "regression_alerts_total",
            "Total regression alerts generated",
            ["metric_name", "severity"],
        )

        self.fitness_regression_gauge = Gauge(
            "fitness_regression_degradation",
            "Current fitness metric degradation percentage",
            ["metric_name"],
        )

        # ML prediction metrics
        self.ml_predictions_total = Counter(
            "ml_fitness_predictions_total", "Total ML fitness predictions", ["status"]
        )

        self.ml_training_samples = Gauge(
            "ml_fitness_training_samples", "Number of samples in ML training dataset"
        )

    async def evaluate_comprehensive_fitness(
        self, individual: Individual
    ) -> FitnessMetrics:
        """
        Perform comprehensive fitness evaluation with constitutional compliance.

        Args:
            individual: Individual to evaluate

        Returns:
            Comprehensive fitness metrics
        """
        start_time = time.time()

        try:
            # Check cache first for O(1) performance
            cache_key = self._get_fitness_cache_key(individual.genotype)
            if cache_key in self.fitness_cache:
                cached_metrics = self.fitness_cache[cache_key]
                self.fitness_evaluations_total.labels(
                    evaluation_type="comprehensive", status="cached"
                ).inc()
                return cached_metrics

            # Perform parallel evaluation of all fitness components
            evaluation_tasks = [
                self._evaluate_constitutional_compliance(individual),
                self._evaluate_performance(individual),
                self._evaluate_safety(individual),
                self._evaluate_fairness(individual),
                self._evaluate_efficiency(individual),
                self._evaluate_robustness(individual),
                self._evaluate_transparency(individual),
                self._evaluate_user_satisfaction(individual),
            ]

            # Execute evaluations in parallel for optimal performance
            results = await asyncio.gather(*evaluation_tasks, return_exceptions=True)

            # Extract scores (handle exceptions)
            scores = {}
            component_names = [
                "constitutional_compliance",
                "performance_score",
                "safety_score",
                "fairness_score",
                "efficiency_score",
                "robustness_score",
                "transparency_score",
                "user_satisfaction",
            ]

            for _i, (component, result) in enumerate(
                zip(component_names, results, strict=False)
            ):
                if isinstance(result, Exception):
                    logger.warning(
                        f"Fitness evaluation failed for {component}: {result}"
                    )
                    scores[component] = 0.0  # Fail-safe score
                else:
                    scores[component] = min(1.0, max(0.0, result))  # Clamp to [0,1]

            # Calculate weighted overall fitness
            overall_fitness = sum(
                scores[component] * self.fitness_weights[component]
                for component in component_names
            )

            # Create fitness metrics
            fitness_metrics = FitnessMetrics(
                constitutional_compliance=scores["constitutional_compliance"],
                performance_score=scores["performance_score"],
                safety_score=scores["safety_score"],
                fairness_score=scores["fairness_score"],
                efficiency_score=scores["efficiency_score"],
                robustness_score=scores["robustness_score"],
                transparency_score=scores["transparency_score"],
                user_satisfaction=scores["user_satisfaction"],
                overall_fitness=overall_fitness,
                constitutional_hash=CONSTITUTIONAL_HASH,
            )

            # Cache result for future O(1) lookups
            self.fitness_cache[cache_key] = fitness_metrics

            # Cache in Redis if available
            if self.redis:
                await self.redis.setex(
                    f"fitness:{cache_key}",
                    1800,  # 30 minute TTL
                    fitness_metrics.json(),
                )

            # Record metrics
            self.fitness_evaluations_total.labels(
                evaluation_type="comprehensive", status="success"
            ).inc()

            for component, score in scores.items():
                self.fitness_score_histogram.labels(score_type=component).observe(score)

            self.fitness_score_histogram.labels(score_type="overall").observe(
                overall_fitness
            )

            # Record fitness metrics for regression detection
            for component, score in scores.items():
                self.regression_detector.record_fitness_metric(component, score)

                # Check for regressions
                regression_alert = self.regression_detector.detect_regression(
                    component, score
                )
                if regression_alert:
                    self.regression_alerts_total.labels(
                        metric_name=component, severity=regression_alert.severity
                    ).inc()

                    self.fitness_regression_gauge.labels(metric_name=component).set(
                        regression_alert.threshold_violated
                    )

            # Record overall fitness for regression detection
            self.regression_detector.record_fitness_metric(
                "overall_fitness", overall_fitness
            )
            overall_regression = self.regression_detector.detect_regression(
                "overall_fitness", overall_fitness
            )
            if overall_regression:
                self.regression_alerts_total.labels(
                    metric_name="overall_fitness", severity=overall_regression.severity
                ).inc()

            # Add to ML training data
            self.ml_predictor.add_training_data(individual.genotype, overall_fitness)
            self.ml_training_samples.set(len(self.ml_predictor.training_data))

            # Periodically retrain ML model
            if len(self.ml_predictor.training_data) % 100 == 0:
                self.ml_predictor.train_simple_model()

            return fitness_metrics

        except Exception as e:
            logger.exception(f"Comprehensive fitness evaluation failed: {e}")
            self.fitness_evaluations_total.labels(
                evaluation_type="comprehensive", status="error"
            ).inc()

            # Return fail-safe fitness metrics
            return FitnessMetrics(
                constitutional_compliance=0.0,
                performance_score=0.0,
                safety_score=0.0,
                fairness_score=0.0,
                efficiency_score=0.0,
                robustness_score=0.0,
                transparency_score=0.0,
                user_satisfaction=0.0,
                overall_fitness=0.0,
                constitutional_hash=CONSTITUTIONAL_HASH,
            )

        finally:
            duration = (time.time() - start_time) * 1000
            self.fitness_evaluation_duration.labels(
                evaluation_component="comprehensive"
            ).observe(duration)

            # Ensure sub-5ms P99 latency target
            if duration > 5:
                logger.warning(
                    f"Comprehensive fitness evaluation took {duration:.2f}ms (>5ms target)"
                )

    async def evaluate_quick_fitness(self, individual: Individual) -> float:
        """
        Perform quick fitness evaluation for performance-critical scenarios.

        Args:
            individual: Individual to evaluate

        Returns:
            Quick fitness score (0.0 to 1.0)
        """
        start_time = time.time()

        try:
            # Quick evaluation focusing on key metrics
            constitutional_score = (
                await self.constitutional_validator.validate_individual(individual)
            )
            performance_score = await self._evaluate_performance_quick(individual)
            safety_score = await self._evaluate_safety_quick(individual)

            # Weighted quick score
            quick_fitness = (
                constitutional_score * 0.5
                + performance_score * 0.3
                + safety_score * 0.2
            )

            self.fitness_evaluations_total.labels(
                evaluation_type="quick", status="success"
            ).inc()

            return quick_fitness

        except Exception as e:
            logger.exception(f"Quick fitness evaluation failed: {e}")
            self.fitness_evaluations_total.labels(
                evaluation_type="quick", status="error"
            ).inc()
            return 0.0

        finally:
            duration = (time.time() - start_time) * 1000
            self.fitness_evaluation_duration.labels(
                evaluation_component="quick"
            ).observe(duration)

    async def _evaluate_constitutional_compliance(
        self, individual: Individual
    ) -> float:
        """Evaluate constitutional compliance score."""
        start_time = time.time()

        try:
            return await self.constitutional_validator.validate_individual(individual)

        finally:
            duration = (time.time() - start_time) * 1000
            self.fitness_evaluation_duration.labels(
                evaluation_component="constitutional"
            ).observe(duration)

    async def _evaluate_performance(self, individual: Individual) -> float:
        """Evaluate performance score."""
        # Simplified performance evaluation
        genotype = individual.genotype

        # Performance indicators
        efficiency = genotype.get("efficiency", 0.8)
        speed = genotype.get("speed", 0.85)
        accuracy = genotype.get("accuracy", 0.9)
        scalability = genotype.get("scalability", 0.75)

        # Weighted performance score
        performance_score = (
            efficiency * 0.3 + speed * 0.3 + accuracy * 0.3 + scalability * 0.1
        )

        return min(1.0, max(0.0, performance_score))

    async def _evaluate_performance_quick(self, individual: Individual) -> float:
        """Quick performance evaluation."""
        genotype = individual.genotype
        return genotype.get("performance_score", 0.8)

    async def _evaluate_safety(self, individual: Individual) -> float:
        """Evaluate safety score."""
        genotype = individual.genotype

        # Safety indicators
        harm_prevention = 1.0 - genotype.get("harm_potential", 0.1)
        risk_mitigation = genotype.get("risk_mitigation", 0.9)
        fail_safe = genotype.get("fail_safe", 0.85)

        safety_score = (harm_prevention + risk_mitigation + fail_safe) / 3
        return min(1.0, max(0.0, safety_score))

    async def _evaluate_safety_quick(self, individual: Individual) -> float:
        """Quick safety evaluation."""
        genotype = individual.genotype
        return genotype.get("safety_score", 0.9)

    async def _evaluate_fairness(self, individual: Individual) -> float:
        """Evaluate fairness score."""
        genotype = individual.genotype

        bias_score = 1.0 - genotype.get("bias_level", 0.1)
        equal_treatment = genotype.get("equal_treatment", 0.9)
        non_discrimination = genotype.get("non_discrimination", 0.95)

        fairness_score = (bias_score + equal_treatment + non_discrimination) / 3
        return min(1.0, max(0.0, fairness_score))

    async def _evaluate_efficiency(self, individual: Individual) -> float:
        """Evaluate efficiency score."""
        genotype = individual.genotype

        resource_usage = 1.0 - genotype.get("resource_consumption", 0.3)
        time_efficiency = genotype.get("time_efficiency", 0.8)
        energy_efficiency = genotype.get("energy_efficiency", 0.85)

        efficiency_score = (resource_usage + time_efficiency + energy_efficiency) / 3
        return min(1.0, max(0.0, efficiency_score))

    async def _evaluate_robustness(self, individual: Individual) -> float:
        """Evaluate robustness score."""
        genotype = individual.genotype

        error_handling = genotype.get("error_handling", 0.8)
        fault_tolerance = genotype.get("fault_tolerance", 0.85)
        adaptability = genotype.get("adaptability", 0.75)

        robustness_score = (error_handling + fault_tolerance + adaptability) / 3
        return min(1.0, max(0.0, robustness_score))

    async def _evaluate_transparency(self, individual: Individual) -> float:
        """Evaluate transparency score."""
        genotype = individual.genotype

        explainability = genotype.get("explainability", 0.7)
        auditability = genotype.get("auditability", 0.8)
        interpretability = genotype.get("interpretability", 0.75)

        transparency_score = (explainability + auditability + interpretability) / 3
        return min(1.0, max(0.0, transparency_score))

    async def _evaluate_user_satisfaction(self, individual: Individual) -> float:
        """Evaluate user satisfaction score."""
        genotype = individual.genotype

        # Placeholder for user satisfaction - would integrate with feedback systems
        usability = genotype.get("usability", 0.8)
        user_experience = genotype.get("user_experience", 0.85)

        satisfaction_score = (usability + user_experience) / 2
        return min(1.0, max(0.0, satisfaction_score))

    def _get_fitness_cache_key(self, genotype: dict[str, Any]) -> str:
        """Generate cache key for fitness evaluation."""
        import hashlib
        import json

        genotype_str = json.dumps(genotype, sort_keys=True)
        return hashlib.md5(genotype_str.encode()).hexdigest()

    async def predict_fitness_ml(self, individual: Individual) -> float | None:
        """
        Predict fitness using ML model.

        Args:
            individual: Individual to predict fitness for

        Returns:
            Predicted fitness score or None if model not trained
        """
        try:
            prediction = self.ml_predictor.predict_fitness(individual.genotype)

            if prediction is not None:
                self.ml_predictions_total.labels(status="success").inc()
            else:
                self.ml_predictions_total.labels(status="no_model").inc()

            return prediction

        except Exception as e:
            logger.exception(f"ML fitness prediction failed: {e}")
            self.ml_predictions_total.labels(status="error").inc()
            return None

    def get_fitness_improvement_suggestions(
        self, individual: Individual
    ) -> dict[str, float]:
        """
        Get suggestions for improving individual fitness.

        Args:
            individual: Individual to suggest improvements for

        Returns:
            Dictionary of suggested genotype improvements
        """
        try:
            return self.ml_predictor.suggest_improvements(individual.genotype)
        except Exception as e:
            logger.exception(f"Failed to generate improvement suggestions: {e}")
            return {}

    def get_regression_alerts(self, hours: int = 24) -> list[RegressionAlert]:
        """
        Get recent regression alerts.

        Args:
            hours: Hours of history to consider

        Returns:
            List of recent regression alerts
        """
        return self.regression_detector.get_recent_alerts(hours)

    def get_fitness_trends(self, metric_name: str, days: int = 7) -> dict[str, Any]:
        """
        Get fitness trends for a specific metric.

        Args:
            metric_name: Name of the fitness metric
            days: Days of history to analyze

        Returns:
            Dictionary containing trend analysis
        """
        try:
            history = self.regression_detector.fitness_history.get(metric_name, [])

            if not history:
                return {"status": "no_data"}

            # Filter by time range
            cutoff = datetime.utcnow() - timedelta(days=days)
            recent_history = [(ts, val) for ts, val in history if ts > cutoff]

            if len(recent_history) < 2:
                return {"status": "insufficient_data"}

            values = [val for _, val in recent_history]
            timestamps = [ts for ts, _ in recent_history]

            # Calculate trend statistics
            mean_value = statistics.mean(values)
            std_dev = statistics.stdev(values) if len(values) > 1 else 0
            min_value = min(values)
            max_value = max(values)

            # Simple trend calculation (slope)
            if len(values) >= 2:
                # Convert timestamps to numeric values (days since earliest)
                time_diffs = [
                    (ts - timestamps[0]).total_seconds() / 86400 for ts in timestamps
                ]

                # Calculate simple linear trend
                n = len(values)
                sum_x = sum(time_diffs)
                sum_y = sum(values)
                sum_xy = sum(x * y for x, y in zip(time_diffs, values, strict=False))
                sum_x2 = sum(x * x for x in time_diffs)

                if n * sum_x2 - sum_x * sum_x != 0:
                    trend_slope = (n * sum_xy - sum_x * sum_y) / (
                        n * sum_x2 - sum_x * sum_x
                    )
                else:
                    trend_slope = 0
            else:
                trend_slope = 0

            return {
                "status": "success",
                "metric_name": metric_name,
                "days_analyzed": days,
                "data_points": len(recent_history),
                "mean": mean_value,
                "std_dev": std_dev,
                "min": min_value,
                "max": max_value,
                "trend_slope": trend_slope,
                "trend_direction": (
                    "improving"
                    if trend_slope > 0.01
                    else "declining" if trend_slope < -0.01 else "stable"
                ),
            }

        except Exception as e:
            logger.exception(f"Failed to analyze fitness trends for {metric_name}: {e}")
            return {"status": "error", "error": str(e)}

    async def evaluate_with_prediction_comparison(
        self, individual: Individual
    ) -> dict[str, Any]:
        """
        Evaluate fitness and compare with ML prediction for model validation.

        Args:
            individual: Individual to evaluate

        Returns:
            Dictionary with actual fitness, prediction, and accuracy metrics
        """
        try:
            # Get ML prediction first
            predicted_fitness = await self.predict_fitness_ml(individual)

            # Get actual fitness
            actual_metrics = await self.evaluate_comprehensive_fitness(individual)
            actual_fitness = actual_metrics.overall_fitness

            result = {
                "actual_fitness": actual_fitness,
                "predicted_fitness": predicted_fitness,
                "fitness_metrics": actual_metrics,
            }

            # Calculate prediction accuracy if we have a prediction
            if predicted_fitness is not None:
                prediction_error = abs(actual_fitness - predicted_fitness)
                prediction_accuracy = 1.0 - prediction_error

                result.update(
                    {
                        "prediction_error": prediction_error,
                        "prediction_accuracy": prediction_accuracy,
                        "has_prediction": True,
                    }
                )
            else:
                result.update(
                    {
                        "prediction_error": None,
                        "prediction_accuracy": None,
                        "has_prediction": False,
                    }
                )

            return result

        except Exception as e:
            logger.exception(f"Failed to evaluate with prediction comparison: {e}")
            return {"status": "error", "error": str(e)}
