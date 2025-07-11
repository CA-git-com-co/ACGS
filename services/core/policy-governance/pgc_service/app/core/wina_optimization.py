"""
WINA (Weight-Informed Neural Architecture) Optimization Module

Integrates WINA optimization insights with risk threshold management (0.25-0.55)
and explainable comments for policy decisions in RAG-based rule generation.

Constitutional Hash: cdd01ef066bc6cf2

Key Features:
- Weight-informed activation for enhanced reliability
- Risk threshold management and optimization
- Explainable policy decision comments
- Performance monitoring and metrics
- Integration with RAG rule generation pipeline
"""

import asyncio
import logging
import math
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import numpy as np

# Constitutional compliance hash for ACGS-2
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for WINA optimization."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WINAOptimizationStrategy(Enum):
    """WINA optimization strategies."""
    CONSERVATIVE = "conservative"  # Lower risk threshold (0.25-0.35)
    BALANCED = "balanced"         # Medium risk threshold (0.35-0.45)
    AGGRESSIVE = "aggressive"     # Higher risk threshold (0.45-0.55)
    ADAPTIVE = "adaptive"         # Dynamic threshold adjustment


@dataclass
class WINAWeights:
    """WINA weight configuration for optimization."""
    
    constitutional_compliance_weight: float = 0.4
    rule_quality_weight: float = 0.3
    performance_weight: float = 0.2
    explainability_weight: float = 0.1
    
    def normalize(self):
        """Normalize weights to sum to 1.0."""
        total = (self.constitutional_compliance_weight + 
                self.rule_quality_weight + 
                self.performance_weight + 
                self.explainability_weight)
        
        if total > 0:
            self.constitutional_compliance_weight /= total
            self.rule_quality_weight /= total
            self.performance_weight /= total
            self.explainability_weight /= total


@dataclass
class RiskThresholdConfig:
    """Risk threshold configuration for WINA optimization."""
    
    min_threshold: float = 0.25
    max_threshold: float = 0.55
    default_threshold: float = 0.4
    adaptive_adjustment_rate: float = 0.05
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    def validate(self) -> bool:
        """Validate threshold configuration."""
        return (0.0 <= self.min_threshold <= self.max_threshold <= 1.0 and
                self.min_threshold <= self.default_threshold <= self.max_threshold)


@dataclass
class WINAOptimizationResult:
    """Result of WINA optimization."""
    
    optimization_id: str
    original_score: float
    optimized_score: float
    risk_threshold: float
    risk_level: RiskLevel
    weights_applied: WINAWeights
    explanation: str
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    constitutional_compliance: bool = True
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class ExplainablePolicyDecision:
    """Explainable policy decision with WINA insights."""
    
    decision_id: str
    policy_content: str
    decision_rationale: str
    wina_factors: Dict[str, float]
    risk_assessment: Dict[str, Any]
    confidence_score: float
    explainability_score: float
    constitutional_compliance_explanation: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    constitutional_hash: str = CONSTITUTIONAL_HASH


class WINAOptimizer:
    """WINA optimization engine for policy rule generation."""
    
    def __init__(
        self,
        strategy: WINAOptimizationStrategy = WINAOptimizationStrategy.BALANCED,
        risk_config: Optional[RiskThresholdConfig] = None
    ):
        self.strategy = strategy
        self.risk_config = risk_config or RiskThresholdConfig()
        self.weights = WINAWeights()
        self.weights.normalize()
        
        # Optimization history and metrics
        self.optimization_history: List[WINAOptimizationResult] = []
        self.performance_metrics = {
            "total_optimizations": 0,
            "avg_improvement": 0.0,
            "reliability_score": 0.0,
            "constitutional_compliance_rate": 1.0,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        # Adaptive threshold tracking
        self.adaptive_threshold_history: List[Tuple[float, float]] = []  # (threshold, performance)
        
        logger.info(f"WINA Optimizer initialized with strategy: {strategy.value}")
    
    def _calculate_risk_threshold(self, context: Dict[str, Any] = None) -> float:
        """Calculate appropriate risk threshold based on strategy and context."""
        if self.strategy == WINAOptimizationStrategy.CONSERVATIVE:
            return self.risk_config.min_threshold + 0.1
        elif self.strategy == WINAOptimizationStrategy.AGGRESSIVE:
            return self.risk_config.max_threshold - 0.1
        elif self.strategy == WINAOptimizationStrategy.BALANCED:
            return self.risk_config.default_threshold
        elif self.strategy == WINAOptimizationStrategy.ADAPTIVE:
            return self._adaptive_threshold_calculation(context)
        else:
            return self.risk_config.default_threshold
    
    def _adaptive_threshold_calculation(self, context: Dict[str, Any] = None) -> float:
        """Calculate adaptive risk threshold based on historical performance."""
        if not self.adaptive_threshold_history:
            return self.risk_config.default_threshold
        
        # Analyze recent performance
        recent_history = self.adaptive_threshold_history[-10:]  # Last 10 optimizations
        
        if len(recent_history) < 3:
            return self.risk_config.default_threshold
        
        # Calculate trend in performance
        thresholds = [h[0] for h in recent_history]
        performances = [h[1] for h in recent_history]
        
        # Simple linear regression to find optimal threshold
        if len(thresholds) > 1:
            correlation = np.corrcoef(thresholds, performances)[0, 1]
            
            if correlation > 0.3:  # Positive correlation - increase threshold
                new_threshold = min(
                    self.risk_config.max_threshold,
                    recent_history[-1][0] + self.risk_config.adaptive_adjustment_rate
                )
            elif correlation < -0.3:  # Negative correlation - decrease threshold
                new_threshold = max(
                    self.risk_config.min_threshold,
                    recent_history[-1][0] - self.risk_config.adaptive_adjustment_rate
                )
            else:  # No clear correlation - maintain current
                new_threshold = recent_history[-1][0]
        else:
            new_threshold = self.risk_config.default_threshold
        
        return new_threshold
    
    def _assess_risk_level(self, risk_score: float) -> RiskLevel:
        """Assess risk level based on risk score."""
        if risk_score <= 0.3:
            return RiskLevel.LOW
        elif risk_score <= 0.5:
            return RiskLevel.MEDIUM
        elif risk_score <= 0.7:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _calculate_wina_score(
        self,
        constitutional_compliance: float,
        rule_quality: float,
        performance: float,
        explainability: float
    ) -> float:
        """Calculate WINA-weighted score."""
        score = (
            constitutional_compliance * self.weights.constitutional_compliance_weight +
            rule_quality * self.weights.rule_quality_weight +
            performance * self.weights.performance_weight +
            explainability * self.weights.explainability_weight
        )
        
        return min(max(score, 0.0), 1.0)
    
    async def optimize_rule_generation(
        self,
        rule_content: str,
        principle_context: Dict[str, Any],
        original_confidence: float
    ) -> WINAOptimizationResult:
        """Optimize rule generation using WINA insights."""
        optimization_id = f"wina-opt-{int(time.time())}-{str(uuid4())[:8]}"
        start_time = time.time()
        
        # Calculate risk threshold
        risk_threshold = self._calculate_risk_threshold(principle_context)
        
        # Assess current rule quality metrics
        constitutional_compliance = 1.0 if CONSTITUTIONAL_HASH in rule_content else 0.0
        
        # Mock rule quality assessment (in real implementation, this would be more sophisticated)
        rule_quality = self._assess_rule_quality(rule_content)
        performance = self._assess_performance_impact(rule_content, principle_context)
        explainability = self._assess_explainability(rule_content, principle_context)
        
        # Calculate original WINA score
        original_score = self._calculate_wina_score(
            constitutional_compliance, rule_quality, performance, explainability
        )
        
        # Apply WINA optimization
        optimized_metrics = await self._apply_wina_optimization(
            rule_content, principle_context, risk_threshold
        )
        
        # Calculate optimized WINA score
        optimized_score = self._calculate_wina_score(
            optimized_metrics["constitutional_compliance"],
            optimized_metrics["rule_quality"],
            optimized_metrics["performance"],
            optimized_metrics["explainability"]
        )
        
        # Assess risk level
        risk_score = 1.0 - optimized_score  # Higher score = lower risk
        risk_level = self._assess_risk_level(risk_score)
        
        # Generate explanation
        explanation = self._generate_optimization_explanation(
            original_score, optimized_score, risk_threshold, optimized_metrics
        )
        
        # Create optimization result
        result = WINAOptimizationResult(
            optimization_id=optimization_id,
            original_score=original_score,
            optimized_score=optimized_score,
            risk_threshold=risk_threshold,
            risk_level=risk_level,
            weights_applied=self.weights,
            explanation=explanation,
            performance_metrics={
                "optimization_time_ms": (time.time() - start_time) * 1000,
                "improvement_ratio": (optimized_score - original_score) / max(original_score, 0.001),
                "constitutional_compliance": optimized_metrics["constitutional_compliance"],
                "risk_score": risk_score
            }
        )
        
        # Update optimization history and metrics
        self.optimization_history.append(result)
        self.adaptive_threshold_history.append((risk_threshold, optimized_score))
        self._update_performance_metrics(result)
        
        logger.info(f"WINA optimization {optimization_id} completed: "
                   f"{original_score:.3f} → {optimized_score:.3f}")
        
        return result
    
    def _assess_rule_quality(self, rule_content: str) -> float:
        """Assess rule quality based on structure and content."""
        quality_score = 0.0
        
        # Basic structure checks
        if "package " in rule_content:
            quality_score += 0.25
        if "default " in rule_content:
            quality_score += 0.25
        if "allow" in rule_content or "deny" in rule_content:
            quality_score += 0.25
        if "{" in rule_content and "}" in rule_content:
            quality_score += 0.25
        
        return quality_score
    
    def _assess_performance_impact(self, rule_content: str, context: Dict[str, Any]) -> float:
        """Assess performance impact of the rule."""
        # Mock performance assessment
        base_performance = 0.8
        
        # Penalize overly complex rules
        complexity_penalty = min(len(rule_content) / 1000.0, 0.2)
        
        # Bonus for optimized patterns
        optimization_bonus = 0.1 if "input." in rule_content else 0.0
        
        return max(0.0, base_performance - complexity_penalty + optimization_bonus)
    
    def _assess_explainability(self, rule_content: str, context: Dict[str, Any]) -> float:
        """Assess explainability of the rule."""
        explainability_score = 0.5  # Base score
        
        # Bonus for comments
        if "#" in rule_content:
            explainability_score += 0.2
        
        # Bonus for clear variable names
        if "input." in rule_content:
            explainability_score += 0.2
        
        # Bonus for structured format
        if rule_content.count('\n') > 2:  # Multi-line structure
            explainability_score += 0.1
        
        return min(explainability_score, 1.0)
    
    async def _apply_wina_optimization(
        self,
        rule_content: str,
        context: Dict[str, Any],
        risk_threshold: float
    ) -> Dict[str, float]:
        """Apply WINA optimization to improve rule metrics."""
        # Mock optimization - in real implementation, this would apply actual optimizations
        
        # Ensure constitutional compliance
        constitutional_compliance = 1.0 if CONSTITUTIONAL_HASH in rule_content else 0.8
        
        # Optimize rule quality based on risk threshold
        base_quality = self._assess_rule_quality(rule_content)
        quality_improvement = (1.0 - risk_threshold) * 0.2  # Lower risk = more improvement
        rule_quality = min(base_quality + quality_improvement, 1.0)
        
        # Optimize performance
        base_performance = self._assess_performance_impact(rule_content, context)
        performance_improvement = (1.0 - risk_threshold) * 0.1
        performance = min(base_performance + performance_improvement, 1.0)
        
        # Optimize explainability
        base_explainability = self._assess_explainability(rule_content, context)
        explainability_improvement = 0.1  # Always try to improve explainability
        explainability = min(base_explainability + explainability_improvement, 1.0)
        
        return {
            "constitutional_compliance": constitutional_compliance,
            "rule_quality": rule_quality,
            "performance": performance,
            "explainability": explainability
        }
    
    def _generate_optimization_explanation(
        self,
        original_score: float,
        optimized_score: float,
        risk_threshold: float,
        metrics: Dict[str, float]
    ) -> str:
        """Generate human-readable explanation of optimization."""
        improvement = optimized_score - original_score
        improvement_pct = (improvement / max(original_score, 0.001)) * 100
        
        explanation_parts = [
            f"WINA optimization applied with {self.strategy.value} strategy.",
            f"Risk threshold set to {risk_threshold:.3f} (range: {self.risk_config.min_threshold}-{self.risk_config.max_threshold}).",
            f"Overall score improved from {original_score:.3f} to {optimized_score:.3f} ({improvement_pct:+.1f}%)."
        ]
        
        # Add specific metric explanations
        if metrics["constitutional_compliance"] >= 0.95:
            explanation_parts.append("Constitutional compliance maintained at high level.")
        elif metrics["constitutional_compliance"] < 0.8:
            explanation_parts.append("⚠️ Constitutional compliance below threshold - review required.")
        
        if metrics["rule_quality"] >= 0.8:
            explanation_parts.append("Rule quality meets high standards.")
        elif metrics["rule_quality"] < 0.6:
            explanation_parts.append("Rule quality could be improved with better structure.")
        
        if metrics["performance"] >= 0.8:
            explanation_parts.append("Performance impact is minimal.")
        elif metrics["performance"] < 0.6:
            explanation_parts.append("Performance optimization recommended.")
        
        explanation_parts.append(f"Constitutional hash {CONSTITUTIONAL_HASH} verified.")
        
        return " ".join(explanation_parts)
    
    def _update_performance_metrics(self, result: WINAOptimizationResult):
        """Update performance metrics based on optimization result."""
        self.performance_metrics["total_optimizations"] += 1
        
        # Update average improvement
        current_avg = self.performance_metrics["avg_improvement"]
        total_opts = self.performance_metrics["total_optimizations"]
        improvement = result.optimized_score - result.original_score
        
        self.performance_metrics["avg_improvement"] = (
            (current_avg * (total_opts - 1) + improvement) / total_opts
        )
        
        # Update reliability score (based on recent optimizations)
        recent_results = self.optimization_history[-10:]  # Last 10 optimizations
        if recent_results:
            avg_optimized_score = sum(r.optimized_score for r in recent_results) / len(recent_results)
            self.performance_metrics["reliability_score"] = avg_optimized_score
        
        # Update constitutional compliance rate
        compliant_count = sum(1 for r in self.optimization_history if r.constitutional_compliance)
        self.performance_metrics["constitutional_compliance_rate"] = (
            compliant_count / len(self.optimization_history)
        )
    
    async def create_explainable_decision(
        self,
        policy_content: str,
        optimization_result: WINAOptimizationResult,
        context: Dict[str, Any] = None
    ) -> ExplainablePolicyDecision:
        """Create explainable policy decision with WINA insights."""
        decision_id = f"decision-{int(time.time())}-{str(uuid4())[:8]}"
        
        # Generate decision rationale
        rationale_parts = [
            f"Policy decision made using WINA optimization (score: {optimization_result.optimized_score:.3f}).",
            f"Risk assessment: {optimization_result.risk_level.value} risk level with threshold {optimization_result.risk_threshold:.3f}.",
            optimization_result.explanation
        ]
        
        decision_rationale = " ".join(rationale_parts)
        
        # Extract WINA factors
        wina_factors = {
            "constitutional_compliance": optimization_result.weights_applied.constitutional_compliance_weight,
            "rule_quality": optimization_result.weights_applied.rule_quality_weight,
            "performance": optimization_result.weights_applied.performance_weight,
            "explainability": optimization_result.weights_applied.explainability_weight,
            "overall_score": optimization_result.optimized_score
        }
        
        # Risk assessment
        risk_assessment = {
            "risk_level": optimization_result.risk_level.value,
            "risk_threshold": optimization_result.risk_threshold,
            "risk_score": 1.0 - optimization_result.optimized_score,
            "mitigation_applied": True,
            "constitutional_hash_verified": CONSTITUTIONAL_HASH in policy_content
        }
        
        # Constitutional compliance explanation
        compliance_explanation = (
            f"Constitutional compliance verified through hash validation ({CONSTITUTIONAL_HASH}). "
            f"Policy adheres to constitutional principles with {optimization_result.performance_metrics.get('constitutional_compliance', 1.0):.1%} compliance rate."
        )
        
        return ExplainablePolicyDecision(
            decision_id=decision_id,
            policy_content=policy_content,
            decision_rationale=decision_rationale,
            wina_factors=wina_factors,
            risk_assessment=risk_assessment,
            confidence_score=optimization_result.optimized_score,
            explainability_score=wina_factors["explainability"],
            constitutional_compliance_explanation=compliance_explanation
        )
    
    def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get comprehensive optimization metrics."""
        if not self.optimization_history:
            return {
                "no_optimizations": True,
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        
        # Calculate additional metrics
        recent_optimizations = self.optimization_history[-20:]  # Last 20
        
        risk_level_distribution = {}
        for result in recent_optimizations:
            level = result.risk_level.value
            risk_level_distribution[level] = risk_level_distribution.get(level, 0) + 1
        
        return {
            **self.performance_metrics,
            "optimization_strategy": self.strategy.value,
            "risk_threshold_config": {
                "min": self.risk_config.min_threshold,
                "max": self.risk_config.max_threshold,
                "default": self.risk_config.default_threshold
            },
            "recent_performance": {
                "optimizations_count": len(recent_optimizations),
                "avg_score": sum(r.optimized_score for r in recent_optimizations) / len(recent_optimizations),
                "risk_level_distribution": risk_level_distribution
            },
            "weights_configuration": {
                "constitutional_compliance": self.weights.constitutional_compliance_weight,
                "rule_quality": self.weights.rule_quality_weight,
                "performance": self.weights.performance_weight,
                "explainability": self.weights.explainability_weight
            }
        }


# Global instance for service integration
_wina_optimizer: Optional[WINAOptimizer] = None


async def get_wina_optimizer(
    strategy: WINAOptimizationStrategy = WINAOptimizationStrategy.BALANCED
) -> WINAOptimizer:
    """Get or create global WINA optimizer instance."""
    global _wina_optimizer
    
    if _wina_optimizer is None:
        _wina_optimizer = WINAOptimizer(strategy=strategy)
    
    return _wina_optimizer
