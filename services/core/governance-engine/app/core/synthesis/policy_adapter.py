"""
Dynamic Policy Adapter for Constitutional AI Governance
Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import time

import numpy as np
from sklearn.tree import DecisionTreeRegressor

logger = logging.getLogger(__name__)


class DynamicPolicyAdapter:
    """Lightweight ML-based policy adaptation with constitutional compliance."""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"

        # Use lightweight scikit-learn model for better performance
        self.model = DecisionTreeRegressor(max_depth=5, random_state=42)

        # Pre-train with baseline adaptation patterns
        self._train_baseline_model()

        # Adaptation thresholds for rule-based decisions
        self.compliance_threshold = 0.95
        self.latency_threshold = 5.0  # ms
        self.throughput_threshold = 100  # RPS

    def _train_baseline_model(self):
        """Pre-train model with baseline adaptation patterns."""
        # Training data: [compliance, latency, throughput, cache_hit_rate] -> adjustment_factor
        training_data = np.array(
            [
                [0.90, 3.0, 150, 0.85, 1.1],  # Low compliance -> increase strictness
                [0.85, 4.0, 120, 0.80, 1.2],  # Lower compliance -> more strictness
                [0.98, 2.0, 200, 0.90, 0.9],  # High compliance -> relax slightly
                [0.94, 6.0, 80, 0.75, 1.15],  # High latency -> increase efficiency
                [0.92, 1.5, 300, 0.95, 1.05],  # Good performance -> minor adjustment
            ]
        )

        X = training_data[:, :4]  # Features
        y = training_data[:, 4]  # Target adjustment factors

        self.model.fit(X, y)

    def adapt_policy(self, current_policy: dict, metrics: dict) -> dict:
        """Adapt policy based on current metrics with constitutional compliance."""
        start_time = time.time()

        try:
            # Extract metrics
            compliance = metrics.get("compliance", 1.0)
            latency = metrics.get("latency", 0.0)
            throughput = metrics.get("throughput", 100)
            cache_hit_rate = metrics.get("cache_hit_rate", 0.85)

            # Create adapted policy copy
            adapted = current_policy.copy()

            # Ensure constitutional compliance is maintained
            if adapted.get("constitutional_hash") != self.constitutional_hash:
                adapted["constitutional_hash"] = self.constitutional_hash

            # Fast rule-based adaptation for extreme cases
            if compliance < 0.90:
                # Urgent compliance issue - apply strict rules
                adapted["rules"] = self._apply_strict_rules(adapted.get("rules", []))
                adapted["adaptation_reason"] = "urgent_compliance_adjustment"
                adapted["adaptation_factor"] = 1.3

            elif latency > self.latency_threshold:
                # High latency - optimize for performance
                adapted["rules"] = self._apply_performance_rules(
                    adapted.get("rules", [])
                )
                adapted["adaptation_reason"] = "performance_optimization"
                adapted["adaptation_factor"] = 1.1

            elif throughput < self.throughput_threshold:
                # Low throughput - reduce overhead
                adapted["rules"] = self._apply_throughput_rules(
                    adapted.get("rules", [])
                )
                adapted["adaptation_reason"] = "throughput_optimization"
                adapted["adaptation_factor"] = 1.05

            else:
                # Use ML model for fine-tuning
                input_data = np.array(
                    [[compliance, latency, throughput, cache_hit_rate]]
                )
                adjustment_factor = self.model.predict(input_data)[0]

                adapted["rules"] = self._apply_ml_adjustment(
                    adapted.get("rules", []), adjustment_factor
                )
                adapted["adaptation_reason"] = "ml_fine_tuning"
                adapted["adaptation_factor"] = float(adjustment_factor)

            # Add adaptation metadata
            adapted["adapted_at"] = time.time()
            adapted["adaptation_latency_ms"] = (time.time() - start_time) * 1000
            adapted["source_metrics"] = metrics

            # Validate constitutional compliance
            if not self._validate_adaptation(adapted):
                logger.warning(
                    "Adapted policy failed validation, reverting to original"
                )
                return current_policy

            return adapted

        except Exception as e:
            logger.exception(f"Policy adaptation failed: {e}")
            return current_policy

    def _apply_strict_rules(self, rules: list[str]) -> list[str]:
        """Apply strict rules for compliance issues."""
        strict_rules = rules.copy()

        # Add strict validation rules
        strict_rules.extend(
            [
                "REQUIRE constitutional_hash_verification == 'passed'",
                "REQUIRE audit_trail == 'complete'",
                "REQUIRE compliance_score >= 0.98",
                "DENY IF suspicious_activity_detected == true",
            ]
        )

        return strict_rules

    def _apply_performance_rules(self, rules: list[str]) -> list[str]:
        """Apply performance-optimized rules."""
        perf_rules = rules.copy()

        # Add performance-focused rules
        perf_rules.extend(
            [
                "CACHE policy_evaluations FOR 300 seconds",
                "SKIP non_critical_validations IF latency > 3ms",
                "BATCH audit_entries FOR efficiency",
            ]
        )

        return perf_rules

    def _apply_throughput_rules(self, rules: list[str]) -> list[str]:
        """Apply throughput-optimized rules."""
        throughput_rules = rules.copy()

        # Add throughput-focused rules
        throughput_rules.extend(
            [
                "PARALLEL process_requests WHERE safe",
                "ASYNC log_audit_events",
                "OPTIMIZE query_patterns FOR batch_processing",
            ]
        )

        return throughput_rules

    def _apply_ml_adjustment(self, rules: list[str], factor: float) -> list[str]:
        """Apply ML-based fine-tuning adjustment."""
        adjusted_rules = rules.copy()

        # Add ML-suggested adjustments
        if factor > 1.1:
            adjusted_rules.append("INCREASE validation_strictness")
        elif factor < 0.9:
            adjusted_rules.append("DECREASE validation_overhead")
        else:
            adjusted_rules.append("MAINTAIN current_validation_level")

        return adjusted_rules

    def _validate_adaptation(self, adapted_policy: dict) -> bool:
        """Validate that adaptation maintains constitutional compliance."""
        try:
            # Check constitutional hash
            if adapted_policy.get("constitutional_hash") != self.constitutional_hash:
                return False

            # Check required fields are present
            required_fields = ["id", "type", "rules", "constitutional_hash"]
            if not all(field in adapted_policy for field in required_fields):
                return False

            # Check rules are valid
            rules = adapted_policy.get("rules", [])
            if not isinstance(rules, list) or len(rules) == 0:
                return False

            # Check adaptation metadata
            return "adaptation_reason" in adapted_policy

        except Exception as e:
            logger.exception(f"Adaptation validation failed: {e}")
            return False

    def get_adaptation_metrics(self) -> dict:
        """Get metrics about policy adaptations."""
        return {
            "constitutional_hash": self.constitutional_hash,
            "model_type": "DecisionTreeRegressor",
            "adaptation_latency_target_ms": 1.0,
            "compliance_threshold": self.compliance_threshold,
            "supported_metrics": [
                "compliance",
                "latency",
                "throughput",
                "cache_hit_rate",
            ],
        }
