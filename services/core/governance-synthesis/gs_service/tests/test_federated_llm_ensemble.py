"""
ACGS-2 Federated LLM Ensemble Test Suite

Comprehensive test suite for the federated LLM ensemble with bias detection,
democratic legitimacy validation, and WINA optimization testing.

Constitutional Hash: cdd01ef066bc6cf2

Test Coverage:
- 200 input test cases for bias reduction validation
- SHAP explanation accuracy testing
- Democratic legitimacy scoring validation
- WINA optimization reliability testing
- Correlation handling per Theorem 3.3
- <2% bias target achievement validation
"""

import asyncio
import json
import logging
import pytest
import random
import statistics
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

# Import modules under test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app', 'core'))

from federated_llm_ensemble import (
    FederatedLLMEnsemble, MockLLMModel, WINAOptimizer, 
    ModelPrediction, EnsembleResult, CONSTITUTIONAL_HASH
)
from bias_detection_mitigation import (
    SHAPBiasExplainer, DemocraticLegitimacyValidator,
    BiasAnalysis, DemocraticLegitimacyMetrics
)

logger = logging.getLogger(__name__)


class TestFederatedLLMEnsemble:
    """Test suite for FederatedLLMEnsemble class."""
    
    @pytest.fixture
    def ensemble(self):
        """Create a test ensemble instance."""
        return FederatedLLMEnsemble()
    
    @pytest.fixture
    def test_principles(self):
        """Generate test constitutional principles."""
        principles = []
        
        # Generate diverse test principles
        principle_templates = [
            "Ensure {aspect} compliance with {framework} standards while maintaining {quality}",
            "Implement {aspect} controls that provide {quality} and {framework} alignment",
            "Establish {aspect} governance with {framework} oversight and {quality} assurance",
            "Maintain {aspect} integrity through {framework} validation and {quality} monitoring"
        ]
        
        aspects = ["data privacy", "algorithmic fairness", "security", "transparency", "accountability"]
        frameworks = ["constitutional", "regulatory", "ethical", "legal", "democratic"]
        qualities = ["reliability", "accuracy", "fairness", "transparency", "legitimacy"]
        
        for i in range(200):  # Generate 200 test cases
            template = random.choice(principle_templates)
            aspect = random.choice(aspects)
            framework = random.choice(frameworks)
            quality = random.choice(qualities)
            
            principle = template.format(aspect=aspect, framework=framework, quality=quality)
            principles.append(principle)
        
        return principles
    
    def test_constitutional_hash_validation(self, ensemble):
        """Test constitutional hash validation."""
        assert ensemble.constitutional_hash == CONSTITUTIONAL_HASH
        assert CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"
    
    def test_ensemble_initialization(self, ensemble):
        """Test ensemble initialization."""
        assert len(ensemble.models) == 3
        assert "gpt4" in ensemble.models
        assert "claude" in ensemble.models
        assert "llama3" in ensemble.models
        assert isinstance(ensemble.wina_optimizer, WINAOptimizer)
        assert ensemble.wina_optimizer.target_reliability == 0.9992
    
    @pytest.mark.asyncio
    async def test_single_policy_synthesis(self, ensemble):
        """Test single policy synthesis."""
        principle = "Ensure data privacy compliance with constitutional standards"
        
        result = await ensemble.synthesize_policy(principle)
        
        assert isinstance(result, EnsembleResult)
        assert result.constitutional_hash == CONSTITUTIONAL_HASH
        assert len(result.individual_predictions) == 3
        assert result.ensemble_confidence > 0.0
        assert result.wina_reliability_score >= 0.0
        assert result.democratic_legitimacy_score >= 0.0
        
        # Validate individual predictions
        for prediction in result.individual_predictions:
            assert isinstance(prediction, ModelPrediction)
            assert prediction.model_name in ["gpt4", "claude", "llama3"]
            assert 0.0 <= prediction.confidence <= 1.0
            assert 0.0 <= prediction.bias_score <= 1.0
            assert 0.0 <= prediction.constitutional_compliance <= 1.0
    
    @pytest.mark.asyncio
    async def test_bias_reduction_200_inputs(self, ensemble, test_principles):
        """Test bias reduction across 200 input cases."""
        bias_scores = []
        synthesis_results = []
        
        logger.info("Testing bias reduction across 200 input cases...")
        
        for i, principle in enumerate(test_principles):
            try:
                result = await ensemble.synthesize_policy(principle)
                synthesis_results.append(result)
                
                # Extract bias score from analysis
                overall_bias = result.bias_analysis.get('overall_bias_score', 0.0)
                bias_scores.append(overall_bias)
                
                if (i + 1) % 50 == 0:
                    logger.info(f"Processed {i + 1}/200 test cases")
                
            except Exception as e:
                logger.error(f"Test case {i} failed: {e}")
                bias_scores.append(1.0)  # Worst case bias score
        
        # Calculate bias statistics
        average_bias = statistics.mean(bias_scores)
        max_bias = max(bias_scores)
        bias_violations = len([b for b in bias_scores if b > 0.02])  # >2% bias
        
        logger.info(f"Bias test results - Average: {average_bias:.4f}, Max: {max_bias:.4f}, Violations: {bias_violations}/200")
        
        # Validate <2% bias target
        assert average_bias < 0.02, f"Average bias {average_bias:.4f} exceeds 2% target"
        assert bias_violations < 10, f"Too many bias violations: {bias_violations}/200"  # Allow some tolerance
        
        # Validate constitutional compliance
        compliance_scores = [
            result.individual_predictions[0].constitutional_compliance 
            for result in synthesis_results
        ]
        average_compliance = statistics.mean(compliance_scores)
        assert average_compliance > 0.95, f"Constitutional compliance {average_compliance:.3f} below 95%"
    
    @pytest.mark.asyncio
    async def test_wina_reliability_target(self, ensemble, test_principles):
        """Test WINA optimization achieves 99.92% reliability target."""
        reliability_scores = []
        
        # Test with subset of principles for performance
        test_subset = test_principles[:50]
        
        for principle in test_subset:
            result = await ensemble.synthesize_policy(principle)
            reliability_scores.append(result.wina_reliability_score)
        
        average_reliability = statistics.mean(reliability_scores)
        min_reliability = min(reliability_scores)
        
        logger.info(f"WINA reliability - Average: {average_reliability:.6f}, Min: {min_reliability:.6f}")
        
        # Validate 99.92% reliability target
        assert average_reliability >= 0.9992, f"Average reliability {average_reliability:.6f} below 99.92% target"
        assert min_reliability >= 0.995, f"Minimum reliability {min_reliability:.6f} too low"
    
    @pytest.mark.asyncio
    async def test_democratic_legitimacy_scoring(self, ensemble):
        """Test democratic legitimacy scoring mechanism."""
        principle = "Implement transparent governance with democratic oversight and stakeholder inclusion"
        
        result = await ensemble.synthesize_policy(principle)
        
        # Validate democratic legitimacy components
        assert result.democratic_legitimacy_score >= 0.0
        assert result.democratic_legitimacy_score <= 1.0
        
        # Check that high-legitimacy keywords improve score
        high_legitimacy_principle = (
            "Establish transparent, accountable, and inclusive governance framework "
            "with democratic participation, stakeholder representation, and "
            "constitutional compliance oversight mechanisms"
        )
        
        high_legitimacy_result = await ensemble.synthesize_policy(high_legitimacy_principle)
        
        # High legitimacy principle should score better
        assert high_legitimacy_result.democratic_legitimacy_score >= result.democratic_legitimacy_score
    
    @pytest.mark.asyncio
    async def test_correlation_handling_theorem_3_3(self, ensemble):
        """Test correlation handling per Theorem 3.3."""
        # Test with correlated principles
        correlated_principles = [
            "Ensure data privacy with encryption standards",
            "Implement data protection using cryptographic methods",
            "Establish secure data handling with encryption protocols"
        ]
        
        results = []
        for principle in correlated_principles:
            result = await ensemble.synthesize_policy(principle)
            results.append(result)
        
        # Validate correlation analysis
        for result in results:
            assert "correlation_analysis" in result.correlation_analysis
            correlation_data = result.correlation_analysis
            
            # Should detect correlations in similar principles
            assert isinstance(correlation_data, dict)
            
        # Check that correlated principles have similar confidence patterns
        confidences = [
            [pred.confidence for pred in result.individual_predictions]
            for result in results
        ]
        
        # Calculate correlation between confidence patterns
        gpt4_confidences = [conf[0] for conf in confidences]
        claude_confidences = [conf[1] for conf in confidences]
        
        # Correlated principles should have similar confidence patterns
        gpt4_variance = statistics.variance(gpt4_confidences) if len(gpt4_confidences) > 1 else 0
        claude_variance = statistics.variance(claude_confidences) if len(claude_confidences) > 1 else 0
        
        # Low variance indicates consistent behavior on correlated inputs
        assert gpt4_variance < 0.1, f"High variance in GPT-4 confidence: {gpt4_variance}"
        assert claude_variance < 0.1, f"High variance in Claude confidence: {claude_variance}"
    
    def test_performance_benchmarks(self, ensemble):
        """Test performance benchmarks for ensemble operations."""
        principle = "Test performance with standard governance principle"
        
        # Measure synthesis time
        start_time = time.time()
        
        # Run synthesis synchronously for timing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(ensemble.synthesize_policy(principle))
        loop.close()
        
        synthesis_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Validate performance targets
        assert synthesis_time < 5000, f"Synthesis time {synthesis_time:.1f}ms exceeds 5s limit"
        assert result.ensemble_confidence > 0.1, "Ensemble confidence too low"
        
        logger.info(f"Synthesis performance: {synthesis_time:.1f}ms")


class TestSHAPBiasExplainer:
    """Test suite for SHAP bias explanation system."""
    
    @pytest.fixture
    def bias_explainer(self):
        """Create a test bias explainer instance."""
        return SHAPBiasExplainer()
    
    @pytest.fixture
    def mock_predictions(self):
        """Create mock predictions for testing."""
        return [
            ModelPrediction(
                model_name="gpt4",
                prediction="Implement comprehensive data protection with strong encryption and access controls",
                confidence=0.85,
                latency_ms=120.0,
                token_count=15,
                bias_score=0.05,
                constitutional_compliance=0.95
            ),
            ModelPrediction(
                model_name="claude",
                prediction="Establish secure data handling with appropriate safeguards and oversight",
                confidence=0.80,
                latency_ms=110.0,
                token_count=12,
                bias_score=0.03,
                constitutional_compliance=0.97
            ),
            ModelPrediction(
                model_name="llama3",
                prediction="Deploy technical data security measures with monitoring and compliance",
                confidence=0.78,
                latency_ms=95.0,
                token_count=11,
                bias_score=0.08,
                constitutional_compliance=0.92
            )
        ]
    
    def test_bias_explainer_initialization(self, bias_explainer):
        """Test bias explainer initialization."""
        assert len(bias_explainer.bias_dimensions) == 10
        assert "gender" in bias_explainer.bias_dimensions
        assert "technical" in bias_explainer.bias_dimensions
        assert len(bias_explainer.bias_patterns) == 10
    
    @pytest.mark.asyncio
    async def test_bias_explanation_generation(self, bias_explainer, mock_predictions):
        """Test SHAP bias explanation generation."""
        principle = "Ensure fair and unbiased algorithmic decision making"
        
        explanations = await bias_explainer.explain_bias(mock_predictions, principle)
        
        assert "dimensional_analysis" in explanations
        assert "feature_importance" in explanations
        assert "bias_sources" in explanations
        assert "attribution_scores" in explanations
        assert explanations["constitutional_hash"] == CONSTITUTIONAL_HASH
        
        # Validate dimensional analysis
        dimensional_analysis = explanations["dimensional_analysis"]
        assert isinstance(dimensional_analysis, dict)
        assert len(dimensional_analysis) == 10  # All bias dimensions
        
        # Validate feature importance
        feature_importance = explanations["feature_importance"]
        assert isinstance(feature_importance, dict)
        assert "bias_indicators" in feature_importance
        assert "constitutional_compliance" in feature_importance
    
    @pytest.mark.asyncio
    async def test_bias_detection_accuracy(self, bias_explainer):
        """Test bias detection accuracy with known biased inputs."""
        # Create intentionally biased predictions
        biased_predictions = [
            ModelPrediction(
                model_name="test",
                prediction="Only men should lead technical teams because they are naturally better at it",
                confidence=0.6,
                latency_ms=100.0,
                token_count=15,
                bias_score=0.9,  # High bias
                constitutional_compliance=0.3
            )
        ]
        
        explanations = await bias_explainer.explain_bias(
            biased_predictions, 
            "Ensure fair hiring practices"
        )
        
        # Should detect gender bias
        dimensional_analysis = explanations["dimensional_analysis"]
        assert dimensional_analysis.get("gender", 0.0) > 0.1, "Failed to detect gender bias"
        
        # Should identify bias sources
        bias_sources = explanations["bias_sources"]
        assert len(bias_sources) > 0, "Failed to identify bias sources"


class TestDemocraticLegitimacyValidator:
    """Test suite for democratic legitimacy validation."""
    
    @pytest.fixture
    def legitimacy_validator(self):
        """Create a test legitimacy validator instance."""
        return DemocraticLegitimacyValidator()
    
    def test_validator_initialization(self, legitimacy_validator):
        """Test validator initialization."""
        assert len(legitimacy_validator.legitimacy_criteria) == 5
        assert "consensus" in legitimacy_validator.legitimacy_criteria
        assert "representation" in legitimacy_validator.legitimacy_criteria
        assert sum(legitimacy_validator.legitimacy_criteria.values()) == 1.0  # Weights sum to 1
    
    def test_democratic_legitimacy_calculation(self, legitimacy_validator):
        """Test democratic legitimacy calculation."""
        # Create test predictions with high legitimacy indicators
        high_legitimacy_predictions = [
            ModelPrediction(
                model_name="gpt4",
                prediction="Establish transparent and accountable governance with stakeholder participation",
                confidence=0.85,
                latency_ms=120.0,
                token_count=12,
                bias_score=0.02,
                constitutional_compliance=0.95
            ),
            ModelPrediction(
                model_name="claude",
                prediction="Implement inclusive democratic processes with community representation",
                confidence=0.83,
                latency_ms=110.0,
                token_count=10,
                bias_score=0.01,
                constitutional_compliance=0.97
            )
        ]
        
        ensemble_weights = {"gpt4": 0.5, "claude": 0.5}
        
        metrics = legitimacy_validator.calculate_democratic_legitimacy(
            high_legitimacy_predictions, ensemble_weights
        )
        
        assert isinstance(metrics, DemocraticLegitimacyMetrics)
        assert metrics.overall_legitimacy > 0.5, "High legitimacy content should score well"
        assert metrics.consensus_score >= 0.0
        assert metrics.representation_fairness >= 0.0
        assert metrics.transparency_score >= 0.0
        assert metrics.accountability_score >= 0.0
        assert metrics.stakeholder_inclusion >= 0.0
        assert metrics.constitutional_hash == CONSTITUTIONAL_HASH


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
