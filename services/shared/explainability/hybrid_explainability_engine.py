"""
Hybrid Explainability Engine

Comprehensive explainability framework combining SHAP and LIME,
implementing the ACGE technical validation recommendations for
industry-standard explainability with production optimization.

Key Features:
- Intelligent selection between SHAP and LIME based on context
- Combined explanations with consensus analysis
- Explanation validation and quality assessment
- Production-ready caching and optimization
- Integration with constitutional AI for explanation compliance
"""

# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import numpy as np

from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger

from .lime_integration import LIMEExplainer, LIMEExplanation
from .shap_integration import ExplainerType as SHAPExplainerType
from .shap_integration import SHAPExplainer, SHAPExplanation

logger = logging.getLogger(__name__)


class ExplanationStrategy(Enum):
    """Explanation generation strategies"""

    SHAP_ONLY = "shap_only"
    LIME_ONLY = "lime_only"
    BOTH_CONSENSUS = "both_consensus"
    ADAPTIVE = "adaptive"
    CONSTITUTIONAL_GUIDED = "constitutional_guided"


class ExplanationContext(Enum):
    """Context for explanation generation"""

    HIGH_STAKES = "high_stakes"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    ROUTINE_OPERATION = "routine_operation"
    DEBUGGING = "debugging"
    BIAS_INVESTIGATION = "bias_investigation"


@dataclass
class HybridExplanation:
    """Combined explanation result from multiple methods"""

    shap_explanation: Optional[SHAPExplanation]
    lime_explanation: Optional[LIMEExplanation]
    consensus_features: dict[str, float]
    explanation_agreement: float
    primary_method: str
    confidence: float
    context: ExplanationContext
    strategy_used: ExplanationStrategy
    computational_cost: float
    timestamp: datetime
    instance_id: str


@dataclass
class ExplanationValidation:
    """Validation result for explanation quality and compliance"""

    is_valid: bool
    constitutional_compliance: bool
    explanation_stability: float
    feature_consistency: float
    prediction_fidelity: float
    validation_issues: list[str]
    recommendations: list[str]
    timestamp: datetime


class HybridExplainabilityEngine:
    """
    Production-ready hybrid explainability engine
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

        # Initialize component explainers
        self.shap_explainer = SHAPExplainer(config.get("shap_config", {}))
        self.lime_explainer = LIMEExplainer(config.get("lime_config", {}))

        # Framework configuration
        self.default_strategy = ExplanationStrategy(
            config.get("default_strategy", "adaptive")
        )
        self.consensus_threshold = config.get("consensus_threshold", 0.7)
        self.max_computation_time = config.get("max_computation_time_seconds", 30.0)

        # Constitutional compliance configuration
        self.constitutional_principles = config.get(
            "constitutional_principles",
            ["transparency", "accountability", "fairness", "non_discrimination"],
        )

        # Monitoring and alerting
        self.alerting = AlertingSystem()
        self.audit_logger = AuditLogger()

        # Performance optimization
        self.explanation_cache = {}
        self.cache_ttl_hours = config.get("cache_ttl_hours", 6)
        self.adaptive_thresholds = {
            "high_stakes_confidence_min": 0.9,
            "routine_confidence_min": 0.7,
            "agreement_threshold_high": 0.8,
            "agreement_threshold_low": 0.5,
        }

        # Metrics tracking
        self.metrics = {
            "total_explanations": 0,
            "strategy_usage": {strategy: 0 for strategy in ExplanationStrategy},
            "avg_computation_time": 0.0,
            "avg_agreement_score": 0.0,
            "constitutional_violations": 0,
            "cache_hit_rate": 0.0,
        }

    async def initialize_explainers(
        self,
        model: Any,
        training_data: np.ndarray,
        feature_names: list[str],
        class_names: Optional[list[str]] = None,
    ) -> bool:
        """
        Initialize both SHAP and LIME explainers

        Args:
            model: ML model to explain
            training_data: Training data
            feature_names: Names of features
            class_names: Names of classes (for classification)

        Returns:
            Success status
        """
        try:
            # Initialize SHAP explainer
            shap_type = self._determine_optimal_shap_explainer(model, training_data)
            shap_success = await self.shap_explainer.initialize_explainer(
                model, shap_type, training_data, feature_names
            )

            # Initialize LIME explainer
            lime_success = await self.lime_explainer.initialize_tabular_explainer(
                training_data, feature_names, class_names
            )

            initialization_success = shap_success and lime_success

            # Log initialization
            await self.audit_logger.log_explainer_event(
                {
                    "event_type": "hybrid_explainer_initialized",
                    "shap_success": shap_success,
                    "lime_success": lime_success,
                    "shap_type": shap_type.value,
                    "num_features": len(feature_names),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            if not initialization_success:
                logger.warning(
                    "Some explainers failed to initialize - hybrid mode may be limited"
                )

            return initialization_success

        except Exception as e:
            logger.error(f"Hybrid explainer initialization failed: {e}")
            return False

    def _determine_optimal_shap_explainer(
        self, model: Any, training_data: np.ndarray
    ) -> SHAPExplainerType:
        """Determine the optimal SHAP explainer type based on model characteristics"""
        try:
            # Check for tree-based models
            tree_model_types = (
                "xgboost",
                "lightgbm",
                "catboost",
                "randomforest",
                "extratrees",
                "gradientboosting",
            )
            model_name = str(type(model)).lower()

            if any(tree_type in model_name for tree_type in tree_model_types):
                return SHAPExplainerType.TREE

            # Check for linear models
            linear_model_types = ("linear", "logistic", "ridge", "lasso", "elastic")
            if any(linear_type in model_name for linear_type in linear_model_types):
                return SHAPExplainerType.LINEAR

            # Check for deep learning models
            deep_model_types = ("neural", "keras", "tensorflow", "pytorch", "torch")
            if any(deep_type in model_name for deep_type in deep_model_types):
                return SHAPExplainerType.DEEP

            # Default to kernel explainer (model-agnostic but slower)
            return SHAPExplainerType.KERNEL

        except Exception:
            return SHAPExplainerType.KERNEL

    async def explain_instance(
        self,
        model: Any,
        instance: np.ndarray,
        predict_fn: Optional[Callable] = None,
        context: ExplanationContext = ExplanationContext.ROUTINE_OPERATION,
        strategy: Optional[ExplanationStrategy] = None,
    ) -> HybridExplanation:
        """
        Generate hybrid explanation for a single instance

        Args:
            model: ML model
            instance: Instance to explain
            predict_fn: Optional prediction function (for LIME)
            context: Context for explanation generation
            strategy: Explanation strategy to use

        Returns:
            Hybrid explanation result
        """
        start_time = datetime.utcnow()
        instance_id = f"hybrid_{hash(instance.tobytes()) % 1000000}"

        if strategy is None:
            strategy = self._determine_strategy(context, model, instance)

        if predict_fn is None:
            predict_fn = lambda x: (
                model.predict(x)
                if hasattr(model, "predict")
                else np.random.random(len(x))
            )

        try:
            # Check cache first
            cache_key = self._get_cache_key(instance, strategy, context)
            if cache_key in self.explanation_cache:
                cached_explanation = self.explanation_cache[cache_key]
                if self._is_cache_valid(cache_key):
                    logger.debug(f"Cache hit for explanation: {cache_key}")
                    return cached_explanation

            shap_explanation = None
            lime_explanation = None

            # Generate explanations based on strategy
            if strategy in [
                ExplanationStrategy.SHAP_ONLY,
                ExplanationStrategy.BOTH_CONSENSUS,
                ExplanationStrategy.ADAPTIVE,
                ExplanationStrategy.CONSTITUTIONAL_GUIDED,
            ]:
                try:
                    # Determine SHAP explainer type
                    shap_type = self._determine_optimal_shap_explainer(
                        model, instance.reshape(1, -1)
                    )
                    shap_explanation = await self.shap_explainer.explain_instance(
                        model, instance, shap_type
                    )
                except Exception as e:
                    logger.warning(f"SHAP explanation failed: {e}")

            if strategy in [
                ExplanationStrategy.LIME_ONLY,
                ExplanationStrategy.BOTH_CONSENSUS,
                ExplanationStrategy.ADAPTIVE,
                ExplanationStrategy.CONSTITUTIONAL_GUIDED,
            ]:
                try:
                    lime_explanation = (
                        await self.lime_explainer.explain_tabular_instance(
                            instance, predict_fn
                        )
                    )
                except Exception as e:
                    logger.warning(f"LIME explanation failed: {e}")

            # Create hybrid explanation
            hybrid_explanation = await self._create_hybrid_explanation(
                shap_explanation, lime_explanation, strategy, context, instance_id
            )

            # Validate explanation
            validation = await self._validate_explanation(
                hybrid_explanation, model, instance, predict_fn
            )

            # Update metrics
            computation_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_metrics(
                strategy,
                computation_time,
                hybrid_explanation.explanation_agreement,
                validation,
            )

            # Cache the explanation
            self._cache_explanation(cache_key, hybrid_explanation)

            # Log explanation generation
            await self.audit_logger.log_explainer_event(
                {
                    "event_type": "hybrid_explanation_generated",
                    "strategy": strategy.value,
                    "context": context.value,
                    "computation_time": computation_time,
                    "agreement_score": hybrid_explanation.explanation_agreement,
                    "confidence": hybrid_explanation.confidence,
                    "constitutional_compliant": validation.constitutional_compliance,
                    "timestamp": hybrid_explanation.timestamp.isoformat(),
                }
            )

            # Send alerts for concerning explanations
            if not validation.constitutional_compliance:
                await self.alerting.send_alert(
                    "constitutional_violation_explanation",
                    "Explanation violates constitutional principles:"
                    f" {validation.validation_issues}",
                    severity="high",
                )

            if hybrid_explanation.explanation_agreement < 0.5:
                await self.alerting.send_alert(
                    "low_explanation_agreement",
                    "Low agreement between explanation methods:"
                    f" {hybrid_explanation.explanation_agreement:.3f}",
                    severity="medium",
                )

            return hybrid_explanation

        except Exception as e:
            logger.error(f"Hybrid explanation failed: {e}")
            computation_time = (datetime.utcnow() - start_time).total_seconds()

            return HybridExplanation(
                shap_explanation=None,
                lime_explanation=None,
                consensus_features={"error": 1.0},
                explanation_agreement=0.0,
                primary_method="error",
                confidence=0.0,
                context=context,
                strategy_used=strategy,
                computational_cost=computation_time,
                timestamp=datetime.utcnow(),
                instance_id=instance_id,
            )

    def _determine_strategy(
        self, context: ExplanationContext, model: Any, instance: np.ndarray
    ) -> ExplanationStrategy:
        """Determine optimal explanation strategy based on context"""
        try:
            if context == ExplanationContext.HIGH_STAKES:
                # Use both methods for high-stakes decisions
                return ExplanationStrategy.BOTH_CONSENSUS

            elif context == ExplanationContext.REGULATORY_COMPLIANCE:
                # Use constitutional-guided approach for compliance
                return ExplanationStrategy.CONSTITUTIONAL_GUIDED

            elif context == ExplanationContext.BIAS_INVESTIGATION:
                # Use both methods to investigate bias thoroughly
                return ExplanationStrategy.BOTH_CONSENSUS

            elif context == ExplanationContext.DEBUGGING:
                # Use SHAP for faster debugging
                return ExplanationStrategy.SHAP_ONLY

            else:  # ROUTINE_OPERATION
                # Use adaptive strategy for routine operations
                return ExplanationStrategy.ADAPTIVE

        except Exception:
            return self.default_strategy

    async def _create_hybrid_explanation(
        self,
        shap_explanation: Optional[SHAPExplanation],
        lime_explanation: Optional[LIMEExplanation],
        strategy: ExplanationStrategy,
        context: ExplanationContext,
        instance_id: str,
    ) -> HybridExplanation:
        """Create hybrid explanation from individual explanations"""
        try:
            # Determine primary method
            if shap_explanation and lime_explanation:
                primary_method = "consensus"
            elif shap_explanation:
                primary_method = "shap"
            elif lime_explanation:
                primary_method = "lime"
            else:
                primary_method = "none"

            # Create consensus features
            consensus_features = {}
            explanation_agreement = 0.0

            if shap_explanation and lime_explanation:
                # Combine feature importance from both methods
                shap_features = shap_explanation.feature_importance
                lime_features = lime_explanation.feature_importance

                # Find common features
                common_features = set(shap_features.keys()) & set(lime_features.keys())

                if common_features:
                    agreements = []
                    for feature in common_features:
                        shap_importance = shap_features[feature]
                        lime_importance = lime_features[feature]

                        # Weighted average (can be configured)
                        consensus_importance = (
                            0.6 * shap_importance + 0.4 * lime_importance
                        )
                        consensus_features[feature] = consensus_importance

                        # Calculate agreement (normalized correlation)
                        if abs(shap_importance) + abs(lime_importance) > 1e-8:
                            agreement = 1.0 - abs(shap_importance - lime_importance) / (
                                abs(shap_importance) + abs(lime_importance)
                            )
                            agreements.append(agreement)

                    explanation_agreement = np.mean(agreements) if agreements else 0.0
                else:
                    # No common features
                    consensus_features = {**shap_features, **lime_features}
                    explanation_agreement = 0.0

            elif shap_explanation:
                consensus_features = shap_explanation.feature_importance
                explanation_agreement = 1.0  # Perfect agreement with itself

            elif lime_explanation:
                consensus_features = lime_explanation.feature_importance
                explanation_agreement = 1.0  # Perfect agreement with itself

            # Calculate confidence based on available explanations and agreement
            confidence = self._calculate_hybrid_confidence(
                shap_explanation, lime_explanation, explanation_agreement, context
            )

            # Calculate computational cost
            computational_cost = 0.0
            if shap_explanation:
                computational_cost += shap_explanation.computation_time
            if lime_explanation:
                computational_cost += lime_explanation.computation_time

            return HybridExplanation(
                shap_explanation=shap_explanation,
                lime_explanation=lime_explanation,
                consensus_features=consensus_features,
                explanation_agreement=explanation_agreement,
                primary_method=primary_method,
                confidence=confidence,
                context=context,
                strategy_used=strategy,
                computational_cost=computational_cost,
                timestamp=datetime.utcnow(),
                instance_id=instance_id,
            )

        except Exception as e:
            logger.error(f"Hybrid explanation creation failed: {e}")
            return HybridExplanation(
                shap_explanation=shap_explanation,
                lime_explanation=lime_explanation,
                consensus_features={"creation_error": 1.0},
                explanation_agreement=0.0,
                primary_method="error",
                confidence=0.0,
                context=context,
                strategy_used=strategy,
                computational_cost=0.0,
                timestamp=datetime.utcnow(),
                instance_id=instance_id,
            )

    def _calculate_hybrid_confidence(
        self,
        shap_explanation: Optional[SHAPExplanation],
        lime_explanation: Optional[LIMEExplanation],
        agreement: float,
        context: ExplanationContext,
    ) -> float:
        """Calculate confidence score for hybrid explanation"""
        try:
            base_confidence = 0.5

            # Base confidence from individual explanations
            if shap_explanation and lime_explanation:
                base_confidence = (
                    shap_explanation.confidence + lime_explanation.confidence
                ) / 2
            elif shap_explanation:
                base_confidence = (
                    shap_explanation.confidence * 0.9
                )  # Slight penalty for single method
            elif lime_explanation:
                base_confidence = lime_explanation.confidence * 0.9

            # Adjust based on agreement
            agreement_bonus = agreement * 0.2  # Up to 20% bonus for high agreement

            # Adjust based on context requirements
            context_multiplier = {
                ExplanationContext.HIGH_STAKES: 0.9,  # Higher standards
                ExplanationContext.REGULATORY_COMPLIANCE: 0.9,
                ExplanationContext.BIAS_INVESTIGATION: 0.95,
                ExplanationContext.ROUTINE_OPERATION: 1.0,
                ExplanationContext.DEBUGGING: 1.1,  # More lenient
            }.get(context, 1.0)

            final_confidence = (base_confidence + agreement_bonus) * context_multiplier
            return max(0.1, min(1.0, final_confidence))

        except Exception:
            return 0.5

    async def _validate_explanation(
        self,
        explanation: HybridExplanation,
        model: Any,
        instance: np.ndarray,
        predict_fn: Callable,
    ) -> ExplanationValidation:
        """Validate explanation quality and constitutional compliance"""
        try:
            validation_issues = []
            recommendations = []

            # Check constitutional compliance
            constitutional_compliance = await self._check_constitutional_compliance(
                explanation
            )
            if not constitutional_compliance:
                validation_issues.append("Constitutional compliance violation")
                recommendations.append("Review explanation generation methodology")
                self.metrics["constitutional_violations"] += 1

            # Check explanation stability (feature consistency)
            feature_consistency = self._assess_feature_consistency(explanation)
            if feature_consistency < 0.7:
                validation_issues.append(
                    f"Low feature consistency: {feature_consistency:.3f}"
                )
                recommendations.append("Consider using ensemble of explanations")

            # Check prediction fidelity
            prediction_fidelity = await self._assess_prediction_fidelity(
                explanation, model, instance, predict_fn
            )
            if prediction_fidelity < 0.8:
                validation_issues.append(
                    f"Low prediction fidelity: {prediction_fidelity:.3f}"
                )
                recommendations.append("Verify model-explainer compatibility")

            # Overall validation
            is_valid = (
                constitutional_compliance
                and feature_consistency >= 0.6
                and prediction_fidelity >= 0.7
                and explanation.confidence >= 0.5
            )

            return ExplanationValidation(
                is_valid=is_valid,
                constitutional_compliance=constitutional_compliance,
                explanation_stability=explanation.explanation_agreement,
                feature_consistency=feature_consistency,
                prediction_fidelity=prediction_fidelity,
                validation_issues=validation_issues,
                recommendations=recommendations,
                timestamp=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Explanation validation failed: {e}")
            return ExplanationValidation(
                is_valid=False,
                constitutional_compliance=False,
                explanation_stability=0.0,
                feature_consistency=0.0,
                prediction_fidelity=0.0,
                validation_issues=[f"Validation failed: {e!s}"],
                recommendations=["Manual review required"],
                timestamp=datetime.utcnow(),
            )

    async def _check_constitutional_compliance(
        self, explanation: HybridExplanation
    ) -> bool:
        """Check if explanation complies with constitutional principles"""
        try:
            # Check for transparency (explanation should have interpretable features)
            has_interpretable_features = len(explanation.consensus_features) > 0

            # Check for accountability (explanation should be traceable)
            is_traceable = (
                explanation.instance_id is not None
                and explanation.timestamp is not None
            )

            # Check for fairness (no obviously biased features)
            protected_attributes = ["race", "gender", "age", "religion", "ethnicity"]
            has_biased_features = any(
                attr in feature.lower()
                for feature in explanation.consensus_features.keys()
                for attr in protected_attributes
            )

            # Basic compliance check
            constitutional_compliance = (
                has_interpretable_features
                and is_traceable
                and not has_biased_features
                and explanation.confidence > 0.3
            )

            return constitutional_compliance

        except Exception as e:
            logger.error(f"Constitutional compliance check failed: {e}")
            return False

    def _assess_feature_consistency(self, explanation: HybridExplanation) -> float:
        """Assess consistency of feature importance across methods"""
        try:
            if not explanation.shap_explanation or not explanation.lime_explanation:
                return 1.0  # Single method is perfectly consistent with itself

            shap_features = explanation.shap_explanation.feature_importance
            lime_features = explanation.lime_explanation.feature_importance

            common_features = set(shap_features.keys()) & set(lime_features.keys())

            if not common_features:
                return 0.0

            correlations = []
            for feature in common_features:
                shap_val = shap_features[feature]
                lime_val = lime_features[feature]

                # Calculate normalized correlation
                if abs(shap_val) + abs(lime_val) > 1e-8:
                    correlation = 1.0 - abs(shap_val - lime_val) / (
                        abs(shap_val) + abs(lime_val)
                    )
                    correlations.append(correlation)

            return np.mean(correlations) if correlations else 0.0

        except Exception:
            return 0.5

    async def _assess_prediction_fidelity(
        self,
        explanation: HybridExplanation,
        model: Any,
        instance: np.ndarray,
        predict_fn: Callable,
    ) -> float:
        """Assess how well explanation matches actual model predictions"""
        try:
            # Get actual model prediction
            actual_prediction = predict_fn(instance.reshape(1, -1))[0]

            # Compare with explanation predictions
            fidelities = []

            if explanation.shap_explanation:
                # SHAP base value + sum of SHAP values should approximate prediction
                shap_prediction = explanation.shap_explanation.base_value + np.sum(
                    explanation.shap_explanation.shap_values
                )
                fidelity = 1.0 - min(
                    1.0,
                    abs(actual_prediction - shap_prediction)
                    / (abs(actual_prediction) + 1e-8),
                )
                fidelities.append(fidelity)

            if explanation.lime_explanation:
                lime_prediction = explanation.lime_explanation.local_prediction
                fidelity = 1.0 - min(
                    1.0,
                    abs(actual_prediction - lime_prediction)
                    / (abs(actual_prediction) + 1e-8),
                )
                fidelities.append(fidelity)

            return np.mean(fidelities) if fidelities else 0.5

        except Exception:
            return 0.5

    def _get_cache_key(
        self,
        instance: np.ndarray,
        strategy: ExplanationStrategy,
        context: ExplanationContext,
    ) -> str:
        """Generate cache key for explanation"""
        import hashlib

        instance_hash = hashlib.md5(instance.tobytes()).hexdigest()
        return f"hybrid_{strategy.value}_{context.value}_{instance_hash}"

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached explanation is still valid"""
        if cache_key not in self.explanation_cache:
            return False

        explanation = self.explanation_cache[cache_key]
        age_hours = (datetime.utcnow() - explanation.timestamp).total_seconds() / 3600

        return age_hours < self.cache_ttl_hours

    def _cache_explanation(self, cache_key: str, explanation: HybridExplanation):
        """Cache explanation result"""
        try:
            self.explanation_cache[cache_key] = explanation

            # Clean old cache entries periodically
            if len(self.explanation_cache) > 1000:
                self._cleanup_cache()

        except Exception as e:
            logger.warning(f"Explanation caching failed: {e}")

    def _cleanup_cache(self):
        """Clean up old cache entries"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.cache_ttl_hours)

            keys_to_remove = [
                key
                for key, explanation in self.explanation_cache.items()
                if explanation.timestamp < cutoff_time
            ]

            for key in keys_to_remove:
                del self.explanation_cache[key]

            logger.info(f"Cleaned up {len(keys_to_remove)} expired cache entries")

        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")

    def _update_metrics(
        self,
        strategy: ExplanationStrategy,
        computation_time: float,
        agreement_score: float,
        validation: ExplanationValidation,
    ):
        """Update performance metrics"""
        self.metrics["total_explanations"] += 1
        self.metrics["strategy_usage"][strategy] += 1

        # Update rolling averages
        total_explanations = self.metrics["total_explanations"]

        current_avg_time = self.metrics["avg_computation_time"]
        self.metrics["avg_computation_time"] = (
            current_avg_time * (total_explanations - 1) + computation_time
        ) / total_explanations

        current_avg_agreement = self.metrics["avg_agreement_score"]
        self.metrics["avg_agreement_score"] = (
            current_avg_agreement * (total_explanations - 1) + agreement_score
        ) / total_explanations

    def get_performance_summary(self) -> dict[str, Any]:
        """Get comprehensive performance summary"""
        total_explanations = self.metrics["total_explanations"]

        return {
            "total_explanations": total_explanations,
            "strategy_distribution": {
                strategy.value: count
                for strategy, count in self.metrics["strategy_usage"].items()
            },
            "avg_computation_time": self.metrics["avg_computation_time"],
            "avg_agreement_score": self.metrics["avg_agreement_score"],
            "constitutional_violation_rate": self.metrics["constitutional_violations"]
            / max(1, total_explanations),
            "cache_size": len(self.explanation_cache),
            "shap_performance": self.shap_explainer.get_performance_summary(),
            "lime_performance": self.lime_explainer.get_performance_summary(),
        }


# Factory function and example usage
async def create_hybrid_explainability_engine(
    config: Optional[dict[str, Any]] = None,
) -> HybridExplainabilityEngine:
    """
    Factory function to create and initialize the hybrid explainability engine

    Args:
        config: Configuration dictionary

    Returns:
        Initialized HybridExplainabilityEngine
    """
    engine = HybridExplainabilityEngine(config)

    logger.info(
        "Hybrid Explainability Engine initialized with strategy:"
        f" {engine.default_strategy}"
    )

    return engine


# Default configuration
DEFAULT_EXPLAINABILITY_CONFIG = {
    "default_strategy": "adaptive",
    "consensus_threshold": 0.7,
    "max_computation_time_seconds": 30.0,
    "cache_ttl_hours": 6,
    "constitutional_principles": [
        "transparency",
        "accountability",
        "fairness",
        "non_discrimination",
    ],
    "shap_config": {"cache_enabled": True, "cache_ttl_hours": 24, "batch_size": 100},
    "lime_config": {"num_features": 10, "num_samples": 1000},
}


# Example usage
async def example_usage():
    """Example of how to use the hybrid explainability engine"""
    # Initialize engine
    engine = await create_hybrid_explainability_engine(DEFAULT_EXPLAINABILITY_CONFIG)

    # Mock data and model
    training_data = np.random.randn(100, 10)
    feature_names = [f"feature_{i}" for i in range(10)]
    class_names = ["class_0", "class_1"]

    class MockModel:
        def predict(self, X):
            return np.random.random(len(X))

    model = MockModel()

    # Initialize explainers
    success = await engine.initialize_explainers(
        model, training_data, feature_names, class_names
    )

    if success:
        # Generate hybrid explanation
        test_instance = np.random.randn(10)
        explanation = await engine.explain_instance(
            model,
            test_instance,
            context=ExplanationContext.HIGH_STAKES,
            strategy=ExplanationStrategy.BOTH_CONSENSUS,
        )

        print(f"Consensus features: {explanation.consensus_features}")
        print(f"Agreement score: {explanation.explanation_agreement}")
        print(f"Confidence: {explanation.confidence}")

        # Get performance summary
        summary = engine.get_performance_summary()
        print(f"Performance: {summary}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
