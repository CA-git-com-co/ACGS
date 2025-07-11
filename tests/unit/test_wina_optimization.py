"""
Unit tests for WINA Optimization Module

Tests WINA optimization insights, risk threshold management (0.25-0.55),
and explainable comments for policy decisions.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import pytest
from unittest.mock import Mock, patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from services.core.policy_governance.pgc_service.app.core.wina_optimization import (
    WINAOptimizer,
    WINAWeights,
    RiskThresholdConfig,
    WINAOptimizationStrategy,
    RiskLevel,
    WINAOptimizationResult,
    ExplainablePolicyDecision,
    CONSTITUTIONAL_HASH
)


class TestWINAWeights:
    """Test WINA weights functionality."""
    
    def test_wina_weights_creation(self):
        """Test WINA weights creation and normalization."""
        weights = WINAWeights(
            constitutional_compliance_weight=0.5,
            rule_quality_weight=0.3,
            performance_weight=0.15,
            explainability_weight=0.05
        )
        
        # Should sum to 1.0
        total = (weights.constitutional_compliance_weight + 
                weights.rule_quality_weight + 
                weights.performance_weight + 
                weights.explainability_weight)
        assert abs(total - 1.0) < 0.001
    
    def test_weights_normalization(self):
        """Test weights normalization."""
        weights = WINAWeights(
            constitutional_compliance_weight=2.0,
            rule_quality_weight=1.0,
            performance_weight=1.0,
            explainability_weight=0.5
        )
        
        weights.normalize()
        
        # Should sum to 1.0 after normalization
        total = (weights.constitutional_compliance_weight + 
                weights.rule_quality_weight + 
                weights.performance_weight + 
                weights.explainability_weight)
        assert abs(total - 1.0) < 0.001
        
        # Constitutional compliance should have highest weight
        assert weights.constitutional_compliance_weight > weights.rule_quality_weight


class TestRiskThresholdConfig:
    """Test risk threshold configuration."""
    
    def test_risk_threshold_config_creation(self):
        """Test risk threshold configuration creation."""
        config = RiskThresholdConfig(
            min_threshold=0.25,
            max_threshold=0.55,
            default_threshold=0.4
        )
        
        assert config.min_threshold == 0.25
        assert config.max_threshold == 0.55
        assert config.default_threshold == 0.4
        assert config.constitutional_hash == CONSTITUTIONAL_HASH
    
    def test_risk_threshold_validation(self):
        """Test risk threshold validation."""
        # Valid configuration
        valid_config = RiskThresholdConfig(
            min_threshold=0.25,
            max_threshold=0.55,
            default_threshold=0.4
        )
        assert valid_config.validate() == True
        
        # Invalid configuration - default outside range
        invalid_config = RiskThresholdConfig(
            min_threshold=0.25,
            max_threshold=0.55,
            default_threshold=0.6
        )
        assert invalid_config.validate() == False
        
        # Invalid configuration - min > max
        invalid_config2 = RiskThresholdConfig(
            min_threshold=0.6,
            max_threshold=0.4,
            default_threshold=0.5
        )
        assert invalid_config2.validate() == False


class TestWINAOptimizer:
    """Test WINA optimizer functionality."""
    
    @pytest.fixture
    def optimizer_conservative(self):
        return WINAOptimizer(strategy=WINAOptimizationStrategy.CONSERVATIVE)
    
    @pytest.fixture
    def optimizer_balanced(self):
        return WINAOptimizer(strategy=WINAOptimizationStrategy.BALANCED)
    
    @pytest.fixture
    def optimizer_aggressive(self):
        return WINAOptimizer(strategy=WINAOptimizationStrategy.AGGRESSIVE)
    
    @pytest.fixture
    def sample_rule_content(self):
        return f"""package test.policy

default allow = false

allow {{
    input.constitutional_hash == "{CONSTITUTIONAL_HASH}"
    input.test_validated == true
    # Generated rule for testing
}}"""
    
    def test_optimizer_initialization(self, optimizer_balanced):
        """Test WINA optimizer initialization."""
        assert optimizer_balanced.strategy == WINAOptimizationStrategy.BALANCED
        assert optimizer_balanced.risk_config.validate() == True
        assert optimizer_balanced.performance_metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert len(optimizer_balanced.optimization_history) == 0
    
    def test_risk_threshold_calculation_strategies(self):
        """Test risk threshold calculation for different strategies."""
        conservative = WINAOptimizer(strategy=WINAOptimizationStrategy.CONSERVATIVE)
        balanced = WINAOptimizer(strategy=WINAOptimizationStrategy.BALANCED)
        aggressive = WINAOptimizer(strategy=WINAOptimizationStrategy.AGGRESSIVE)
        
        conservative_threshold = conservative._calculate_risk_threshold()
        balanced_threshold = balanced._calculate_risk_threshold()
        aggressive_threshold = aggressive._calculate_risk_threshold()
        
        # Conservative should have lowest threshold
        assert conservative_threshold < balanced_threshold < aggressive_threshold
        
        # All should be within valid range
        assert 0.25 <= conservative_threshold <= 0.55
        assert 0.25 <= balanced_threshold <= 0.55
        assert 0.25 <= aggressive_threshold <= 0.55
    
    def test_risk_level_assessment(self, optimizer_balanced):
        """Test risk level assessment."""
        assert optimizer_balanced._assess_risk_level(0.2) == RiskLevel.LOW
        assert optimizer_balanced._assess_risk_level(0.4) == RiskLevel.MEDIUM
        assert optimizer_balanced._assess_risk_level(0.6) == RiskLevel.HIGH
        assert optimizer_balanced._assess_risk_level(0.8) == RiskLevel.CRITICAL
    
    def test_rule_quality_assessment(self, optimizer_balanced, sample_rule_content):
        """Test rule quality assessment."""
        quality_score = optimizer_balanced._assess_rule_quality(sample_rule_content)
        
        # Should have high quality score due to proper structure
        assert quality_score >= 0.8
        assert quality_score <= 1.0
        
        # Test with poor quality rule
        poor_rule = "# This is not a proper rule"
        poor_quality = optimizer_balanced._assess_rule_quality(poor_rule)
        assert poor_quality < 0.5
    
    def test_performance_impact_assessment(self, optimizer_balanced, sample_rule_content):
        """Test performance impact assessment."""
        context = {"domain": "test", "complexity": "medium"}
        performance_score = optimizer_balanced._assess_performance_impact(
            sample_rule_content, context
        )
        
        assert 0.0 <= performance_score <= 1.0
        
        # Test with very long rule (should have lower performance)
        long_rule = sample_rule_content + "\n" + "# " + "x" * 1000
        long_performance = optimizer_balanced._assess_performance_impact(long_rule, context)
        assert long_performance < performance_score
    
    def test_explainability_assessment(self, optimizer_balanced, sample_rule_content):
        """Test explainability assessment."""
        context = {"domain": "test"}
        explainability_score = optimizer_balanced._assess_explainability(
            sample_rule_content, context
        )
        
        # Should have good explainability due to comments and structure
        assert explainability_score >= 0.7
        assert explainability_score <= 1.0
        
        # Test with rule without comments
        no_comment_rule = sample_rule_content.replace("# Generated rule for testing", "")
        no_comment_explainability = optimizer_balanced._assess_explainability(
            no_comment_rule, context
        )
        assert no_comment_explainability < explainability_score
    
    @pytest.mark.asyncio
    async def test_optimize_rule_generation(self, optimizer_balanced, sample_rule_content):
        """Test rule generation optimization."""
        principle_context = {
            "category": "test",
            "complexity": "medium",
            "domain": "testing"
        }
        
        result = await optimizer_balanced.optimize_rule_generation(
            sample_rule_content, principle_context, 0.8
        )
        
        assert isinstance(result, WINAOptimizationResult)
        assert result.constitutional_compliance == True
        assert result.constitutional_hash == CONSTITUTIONAL_HASH
        assert 0.25 <= result.risk_threshold <= 0.55
        assert result.optimized_score >= result.original_score  # Should improve or maintain
        assert len(result.explanation) > 0
        
        # Check that optimization was recorded
        assert len(optimizer_balanced.optimization_history) == 1
        assert optimizer_balanced.performance_metrics["total_optimizations"] == 1
    
    @pytest.mark.asyncio
    async def test_multiple_optimizations_tracking(self, optimizer_balanced, sample_rule_content):
        """Test tracking of multiple optimizations."""
        principle_context = {"category": "test"}
        
        # Run multiple optimizations
        for i in range(5):
            await optimizer_balanced.optimize_rule_generation(
                sample_rule_content, principle_context, 0.7 + i * 0.05
            )
        
        # Check tracking
        assert len(optimizer_balanced.optimization_history) == 5
        assert optimizer_balanced.performance_metrics["total_optimizations"] == 5
        assert optimizer_balanced.performance_metrics["reliability_score"] > 0
        assert optimizer_balanced.performance_metrics["constitutional_compliance_rate"] == 1.0
    
    @pytest.mark.asyncio
    async def test_create_explainable_decision(self, optimizer_balanced, sample_rule_content):
        """Test creation of explainable policy decisions."""
        principle_context = {"category": "test"}
        
        # First optimize a rule
        optimization_result = await optimizer_balanced.optimize_rule_generation(
            sample_rule_content, principle_context, 0.8
        )
        
        # Create explainable decision
        decision = await optimizer_balanced.create_explainable_decision(
            sample_rule_content, optimization_result, principle_context
        )
        
        assert isinstance(decision, ExplainablePolicyDecision)
        assert decision.constitutional_hash == CONSTITUTIONAL_HASH
        assert decision.policy_content == sample_rule_content
        assert len(decision.decision_rationale) > 0
        assert len(decision.constitutional_compliance_explanation) > 0
        
        # Check WINA factors
        assert "constitutional_compliance" in decision.wina_factors
        assert "rule_quality" in decision.wina_factors
        assert "performance" in decision.wina_factors
        assert "explainability" in decision.wina_factors
        assert "overall_score" in decision.wina_factors
        
        # Check risk assessment
        assert "risk_level" in decision.risk_assessment
        assert "risk_threshold" in decision.risk_assessment
        assert "constitutional_hash_verified" in decision.risk_assessment
        assert decision.risk_assessment["constitutional_hash_verified"] == True
    
    def test_optimization_metrics(self, optimizer_balanced):
        """Test optimization metrics collection."""
        metrics = optimizer_balanced.get_optimization_metrics()
        
        assert "constitutional_hash" in metrics
        assert metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "optimization_strategy" in metrics
        assert metrics["optimization_strategy"] == WINAOptimizationStrategy.BALANCED.value
        assert "risk_threshold_config" in metrics
        assert "weights_configuration" in metrics
        
        # Check risk threshold config
        threshold_config = metrics["risk_threshold_config"]
        assert threshold_config["min"] == 0.25
        assert threshold_config["max"] == 0.55
        
        # Check weights configuration
        weights_config = metrics["weights_configuration"]
        assert "constitutional_compliance" in weights_config
        assert "rule_quality" in weights_config
        assert "performance" in weights_config
        assert "explainability" in weights_config
    
    @pytest.mark.asyncio
    async def test_adaptive_threshold_calculation(self):
        """Test adaptive threshold calculation."""
        adaptive_optimizer = WINAOptimizer(strategy=WINAOptimizationStrategy.ADAPTIVE)
        
        # Initially should use default threshold
        initial_threshold = adaptive_optimizer._calculate_risk_threshold()
        assert initial_threshold == adaptive_optimizer.risk_config.default_threshold
        
        # Add some history
        adaptive_optimizer.adaptive_threshold_history = [
            (0.3, 0.8),  # threshold, performance
            (0.35, 0.85),
            (0.4, 0.9),
            (0.45, 0.88)
        ]
        
        # Should calculate based on history
        adaptive_threshold = adaptive_optimizer._adaptive_threshold_calculation()
        assert 0.25 <= adaptive_threshold <= 0.55
    
    @pytest.mark.asyncio
    async def test_constitutional_compliance_enforcement(self, optimizer_balanced):
        """Test that constitutional compliance is enforced."""
        # Rule without constitutional hash
        non_compliant_rule = """package test.policy

default allow = false

allow {
    input.test_validated == true
}"""
        
        principle_context = {"category": "test"}
        
        result = await optimizer_balanced.optimize_rule_generation(
            non_compliant_rule, principle_context, 0.8
        )
        
        # Should still maintain constitutional compliance in result
        assert result.constitutional_compliance == True
        assert result.constitutional_hash == CONSTITUTIONAL_HASH
        
        # Performance metrics should reflect the optimization
        assert "constitutional_compliance" in result.performance_metrics
    
    def test_wina_score_calculation(self, optimizer_balanced):
        """Test WINA score calculation."""
        # Test with perfect scores
        perfect_score = optimizer_balanced._calculate_wina_score(1.0, 1.0, 1.0, 1.0)
        assert perfect_score == 1.0
        
        # Test with zero scores
        zero_score = optimizer_balanced._calculate_wina_score(0.0, 0.0, 0.0, 0.0)
        assert zero_score == 0.0
        
        # Test with mixed scores
        mixed_score = optimizer_balanced._calculate_wina_score(1.0, 0.8, 0.6, 0.4)
        assert 0.0 < mixed_score < 1.0
        
        # Constitutional compliance should have highest weight
        high_compliance_score = optimizer_balanced._calculate_wina_score(1.0, 0.5, 0.5, 0.5)
        low_compliance_score = optimizer_balanced._calculate_wina_score(0.5, 1.0, 1.0, 1.0)
        assert high_compliance_score > low_compliance_score


@pytest.mark.integration
class TestWINAIntegration:
    """Integration tests for WINA optimization."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_optimization_workflow(self):
        """Test complete WINA optimization workflow."""
        optimizer = WINAOptimizer(strategy=WINAOptimizationStrategy.BALANCED)
        
        rule_content = f"""package integration.test

default allow = false

allow {{
    input.constitutional_hash == "{CONSTITUTIONAL_HASH}"
    input.integration_test == true
}}"""
        
        principle_context = {
            "category": "integration",
            "domain": "testing",
            "complexity": "low"
        }
        
        # Run optimization
        optimization_result = await optimizer.optimize_rule_generation(
            rule_content, principle_context, 0.75
        )
        
        # Create explainable decision
        decision = await optimizer.create_explainable_decision(
            rule_content, optimization_result, principle_context
        )
        
        # Get metrics
        metrics = optimizer.get_optimization_metrics()
        
        # Validate end-to-end results
        assert optimization_result.constitutional_hash == CONSTITUTIONAL_HASH
        assert decision.constitutional_hash == CONSTITUTIONAL_HASH
        assert metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
        
        assert optimization_result.optimized_score > 0.5
        assert decision.confidence_score > 0.5
        assert metrics["constitutional_compliance_rate"] == 1.0
        
        print("✅ End-to-end WINA optimization workflow completed successfully")
        print(f"Optimization score: {optimization_result.original_score:.3f} → {optimization_result.optimized_score:.3f}")
        print(f"Risk level: {optimization_result.risk_level.value}")
        print(f"Constitutional compliance: {optimization_result.constitutional_compliance}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
