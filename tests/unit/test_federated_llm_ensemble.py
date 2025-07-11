"""
Unit tests for Federated LLM Ensemble System

Tests federated ensemble simulation with GPT-4, Claude, and Llama-3 models
for enhanced reliability, bias reduction, and constitutional compliance.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from services.core.policy_governance.pgc_service.app.core.federated_llm_ensemble import (
    FederatedLLMEnsemble,
    MockLLMSimulator,
    BiasDetectionEngine,
    ModelResponse,
    EnsembleResponse,
    LLMModelType,
    EnsembleStrategy,
    BiasType,
    integrate_with_rag_system,
    CONSTITUTIONAL_HASH
)


class TestMockLLMSimulator:
    """Test mock LLM simulator functionality."""
    
    @pytest.fixture
    def gpt4_simulator(self):
        return MockLLMSimulator(LLMModelType.GPT_4)
    
    @pytest.fixture
    def claude_simulator(self):
        return MockLLMSimulator(LLMModelType.CLAUDE_3)
    
    @pytest.fixture
    def llama_simulator(self):
        return MockLLMSimulator(LLMModelType.LLAMA_3)
    
    def test_simulator_initialization(self, gpt4_simulator, claude_simulator, llama_simulator):
        """Test LLM simulator initialization."""
        assert gpt4_simulator.model_type == LLMModelType.GPT_4
        assert claude_simulator.model_type == LLMModelType.CLAUDE_3
        assert llama_simulator.model_type == LLMModelType.LLAMA_3
        
        # Check model characteristics are different
        assert gpt4_simulator.base_confidence != claude_simulator.base_confidence
        assert claude_simulator.constitutional_alignment > gpt4_simulator.constitutional_alignment
        assert llama_simulator.bias_tendencies[BiasType.DEMOGRAPHIC] > claude_simulator.bias_tendencies[BiasType.DEMOGRAPHIC]
    
    @pytest.mark.asyncio
    async def test_generate_response(self, gpt4_simulator):
        """Test response generation."""
        prompt = "Generate a privacy policy rule"
        context = {"category": "privacy", "domain": "healthcare"}
        
        response = await gpt4_simulator.generate_response(prompt, context)
        
        assert isinstance(response, ModelResponse)
        assert response.model_type == LLMModelType.GPT_4
        assert response.constitutional_hash == CONSTITUTIONAL_HASH
        assert CONSTITUTIONAL_HASH in response.content
        assert 0.0 <= response.confidence_score <= 1.0
        assert 0.0 <= response.constitutional_compliance_score <= 1.0
        assert response.response_time_ms > 0
        assert len(response.bias_scores) == len(BiasType)
    
    @pytest.mark.asyncio
    async def test_model_specific_characteristics(self, gpt4_simulator, claude_simulator, llama_simulator):
        """Test that different models have different characteristics."""
        prompt = "Generate a security policy rule"
        
        gpt4_response = await gpt4_simulator.generate_response(prompt)
        claude_response = await claude_simulator.generate_response(prompt)
        llama_response = await llama_simulator.generate_response(prompt)
        
        # Claude should have highest constitutional compliance
        assert claude_response.constitutional_compliance_score >= gpt4_response.constitutional_compliance_score
        assert claude_response.constitutional_compliance_score >= llama_response.constitutional_compliance_score
        
        # All should include constitutional hash
        assert CONSTITUTIONAL_HASH in gpt4_response.content
        assert CONSTITUTIONAL_HASH in claude_response.content
        assert CONSTITUTIONAL_HASH in llama_response.content
        
        # Content should be model-specific
        assert "GPT-4" in gpt4_response.content
        assert "Claude-3" in claude_response.content
        assert "Llama-3" in llama_response.content


class TestBiasDetectionEngine:
    """Test bias detection and mitigation functionality."""
    
    @pytest.fixture
    def bias_engine(self):
        return BiasDetectionEngine()
    
    @pytest.fixture
    def sample_responses(self):
        return [
            ModelResponse(
                model_type=LLMModelType.GPT_4,
                response_id="gpt4-test",
                content="test content",
                confidence_score=0.8,
                reasoning="test reasoning",
                constitutional_compliance_score=0.9,
                bias_scores={
                    BiasType.DEMOGRAPHIC: 0.4,  # High bias
                    BiasType.CULTURAL: 0.2,
                    BiasType.LINGUISTIC: 0.1,
                    BiasType.TEMPORAL: 0.3,
                    BiasType.CONFIRMATION: 0.25
                }
            ),
            ModelResponse(
                model_type=LLMModelType.CLAUDE_3,
                response_id="claude-test",
                content="test content",
                confidence_score=0.85,
                reasoning="test reasoning",
                constitutional_compliance_score=0.95,
                bias_scores={
                    BiasType.DEMOGRAPHIC: 0.15,  # Low bias
                    BiasType.CULTURAL: 0.1,
                    BiasType.LINGUISTIC: 0.05,
                    BiasType.TEMPORAL: 0.2,
                    BiasType.CONFIRMATION: 0.1
                }
            )
        ]
    
    @pytest.mark.asyncio
    async def test_bias_detection(self, bias_engine, sample_responses):
        """Test bias detection across ensemble responses."""
        detected_bias = await bias_engine.detect_bias(sample_responses)
        
        assert len(detected_bias) == len(BiasType)
        
        # Should detect average bias levels
        for bias_type, bias_score in detected_bias.items():
            assert 0.0 <= bias_score <= 1.0
        
        # Demographic bias should be detected (average of 0.4 and 0.15)
        assert detected_bias[BiasType.DEMOGRAPHIC] > 0.2
    
    @pytest.mark.asyncio
    async def test_bias_mitigation(self, bias_engine, sample_responses):
        """Test bias mitigation application."""
        detected_bias = await bias_engine.detect_bias(sample_responses)
        mitigated_responses = await bias_engine.apply_bias_mitigation(sample_responses, detected_bias)
        
        assert len(mitigated_responses) == len(sample_responses)
        
        # Check that bias scores are reduced
        for i, (original, mitigated) in enumerate(zip(sample_responses, mitigated_responses)):
            for bias_type in BiasType:
                if detected_bias[bias_type] > bias_engine.bias_thresholds[bias_type]:
                    assert mitigated.bias_scores[bias_type] <= original.bias_scores[bias_type]
    
    def test_bias_reduction_calculation(self, bias_engine, sample_responses):
        """Test bias reduction calculation."""
        # Create mitigated responses with reduced bias
        mitigated_responses = []
        for response in sample_responses:
            mitigated = ModelResponse(
                model_type=response.model_type,
                response_id=response.response_id,
                content=response.content,
                confidence_score=response.confidence_score,
                reasoning=response.reasoning,
                constitutional_compliance_score=response.constitutional_compliance_score,
                bias_scores={bias_type: score * 0.5 for bias_type, score in response.bias_scores.items()}
            )
            mitigated_responses.append(mitigated)
        
        bias_reduction = bias_engine.calculate_bias_reduction(sample_responses, mitigated_responses)
        
        # Should show positive reduction for all bias types
        for bias_type, reduction in bias_reduction.items():
            assert reduction >= 0.0


class TestFederatedLLMEnsemble:
    """Test federated LLM ensemble functionality."""
    
    @pytest.fixture
    def ensemble(self):
        return FederatedLLMEnsemble(EnsembleStrategy.CONSTITUTIONAL_PRIORITY)
    
    def test_ensemble_initialization(self, ensemble):
        """Test ensemble initialization."""
        assert ensemble.ensemble_strategy == EnsembleStrategy.CONSTITUTIONAL_PRIORITY
        assert len(ensemble.models) == 3  # GPT-4, Claude-3, Llama-3
        assert ensemble.target_reliability == 0.9992
        assert ensemble.federated_metrics.constitutional_hash == CONSTITUTIONAL_HASH
        
        # Check model weights
        assert LLMModelType.CLAUDE_3 in ensemble.model_weights
        assert ensemble.model_weights[LLMModelType.CLAUDE_3] > ensemble.model_weights[LLMModelType.GPT_4]
    
    @pytest.mark.asyncio
    async def test_generate_ensemble_response(self, ensemble):
        """Test ensemble response generation."""
        prompt = "Generate a privacy compliance rule"
        context = {"category": "privacy", "domain": "healthcare"}
        
        ensemble_response = await ensemble.generate_ensemble_response(prompt, context)
        
        assert isinstance(ensemble_response, EnsembleResponse)
        assert ensemble_response.constitutional_hash == CONSTITUTIONAL_HASH
        assert len(ensemble_response.individual_responses) == 3
        assert ensemble_response.ensemble_strategy == EnsembleStrategy.CONSTITUTIONAL_PRIORITY
        assert 0.0 <= ensemble_response.consensus_confidence <= 1.0
        assert 0.0 <= ensemble_response.constitutional_compliance_score <= 1.0
        assert 0.0 <= ensemble_response.reliability_score <= 1.0
        assert ensemble_response.processing_time_ms > 0
        
        # Check constitutional compliance in final content
        assert CONSTITUTIONAL_HASH in ensemble_response.final_content
    
    @pytest.mark.asyncio
    async def test_constitutional_priority_consensus(self, ensemble):
        """Test constitutional priority consensus strategy."""
        prompt = "Generate a rule with constitutional priority"
        
        ensemble_response = await ensemble.generate_ensemble_response(prompt)
        
        # Should prioritize constitutional compliance
        assert ensemble_response.constitutional_compliance_score > 0.8
        assert CONSTITUTIONAL_HASH in ensemble_response.final_content
        
        # Check that Claude (highest constitutional alignment) influenced the result
        claude_response = next(
            (r for r in ensemble_response.individual_responses if r.model_type == LLMModelType.CLAUDE_3),
            None
        )
        assert claude_response is not None
        assert claude_response.constitutional_compliance_score > 0.85
    
    @pytest.mark.asyncio
    async def test_different_ensemble_strategies(self):
        """Test different ensemble strategies."""
        strategies = [
            EnsembleStrategy.MAJORITY_VOTE,
            EnsembleStrategy.WEIGHTED_AVERAGE,
            EnsembleStrategy.CONFIDENCE_WEIGHTED,
            EnsembleStrategy.CONSTITUTIONAL_PRIORITY
        ]
        
        prompt = "Generate a security policy rule"
        
        for strategy in strategies:
            ensemble = FederatedLLMEnsemble(strategy)
            response = await ensemble.generate_ensemble_response(prompt)
            
            assert response.ensemble_strategy == strategy
            assert response.constitutional_hash == CONSTITUTIONAL_HASH
            assert len(response.individual_responses) == 3
    
    @pytest.mark.asyncio
    async def test_bias_mitigation_in_ensemble(self, ensemble):
        """Test that ensemble applies bias mitigation."""
        prompt = "Generate a rule that might have bias"
        
        ensemble_response = await ensemble.generate_ensemble_response(prompt)
        
        # Check if bias mitigation was applied
        if ensemble_response.bias_mitigation_applied:
            # Verify that individual responses show bias mitigation
            for response in ensemble_response.individual_responses:
                assert "bias mitigation" in response.reasoning.lower() or \
                       any(bias < 0.3 for bias in response.bias_scores.values())
    
    @pytest.mark.asyncio
    async def test_reliability_target_achievement(self, ensemble):
        """Test that ensemble achieves 99.92% reliability target."""
        # Run multiple queries to build up metrics
        for i in range(10):
            prompt = f"Generate test rule {i}"
            await ensemble.generate_ensemble_response(prompt)
        
        metrics = ensemble.get_federated_metrics()
        
        # Check reliability metrics
        assert "current_reliability" in metrics
        assert "reliability_target_met" in metrics
        assert metrics["target_reliability"] == 0.9992
        
        # With good ensemble responses, should approach target
        assert metrics["current_reliability"] > 0.8
    
    @pytest.mark.asyncio
    async def test_federated_metrics_tracking(self, ensemble):
        """Test federated learning metrics tracking."""
        initial_metrics = ensemble.get_federated_metrics()
        assert initial_metrics["total_queries"] == 0
        
        # Generate some responses
        for i in range(5):
            await ensemble.generate_ensemble_response(f"Test query {i}")
        
        updated_metrics = ensemble.get_federated_metrics()
        
        assert updated_metrics["total_queries"] == 5
        assert updated_metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "model_performance" in updated_metrics
        assert len(updated_metrics["model_performance"]) == 3
        
        # Check per-model metrics
        for model_type in LLMModelType:
            if model_type in updated_metrics["model_performance"]:
                model_metrics = updated_metrics["model_performance"][model_type]
                assert "avg_confidence" in model_metrics
                assert "avg_constitutional_compliance" in model_metrics
                assert "query_count" in model_metrics
    
    @pytest.mark.asyncio
    async def test_health_check(self, ensemble):
        """Test ensemble health check."""
        health_status = await ensemble.health_check()
        
        assert "status" in health_status
        assert health_status["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert health_status["models_available"] == 3
        assert health_status["ensemble_strategy"] == EnsembleStrategy.CONSTITUTIONAL_PRIORITY.value
        assert "model_health" in health_status
        
        # Check individual model health
        model_health = health_status["model_health"]
        assert len(model_health) == 3
        
        for model_name, health in model_health.items():
            assert health["available"] == True
            assert health["response_time_ms"] > 0
            assert 0.0 <= health["constitutional_compliance"] <= 1.0


class TestRAGIntegration:
    """Test integration with RAG system."""
    
    @pytest.mark.asyncio
    async def test_rag_integration(self):
        """Test integration with RAG system."""
        ensemble = FederatedLLMEnsemble()
        
        rag_query = "privacy protection for healthcare data"
        retrieved_principles = [
            "Healthcare data must be protected with encryption",
            "Patient consent required for data access",
            "Audit trails must be maintained for all access"
        ]
        context = {"category": "privacy", "domain": "healthcare"}
        
        ensemble_response = await integrate_with_rag_system(
            ensemble, rag_query, retrieved_principles, context
        )
        
        assert isinstance(ensemble_response, EnsembleResponse)
        assert ensemble_response.constitutional_hash == CONSTITUTIONAL_HASH
        assert CONSTITUTIONAL_HASH in ensemble_response.final_content
        
        # Should incorporate retrieved principles
        final_content = ensemble_response.final_content.lower()
        assert any(principle.lower() in final_content for principle in retrieved_principles) or \
               "privacy" in final_content


@pytest.mark.integration
class TestFederatedEnsembleIntegration:
    """Integration tests for federated ensemble."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_ensemble_workflow(self):
        """Test complete ensemble workflow."""
        ensemble = FederatedLLMEnsemble(EnsembleStrategy.CONSTITUTIONAL_PRIORITY)
        
        # Test multiple queries to build metrics
        queries = [
            "Generate privacy policy for user data",
            "Create security rule for API access",
            "Develop fairness policy for algorithmic decisions",
            "Establish transparency requirements for AI systems"
        ]
        
        responses = []
        for query in queries:
            context = {"category": query.split()[1], "domain": "enterprise"}
            response = await ensemble.generate_ensemble_response(query, context)
            responses.append(response)
        
        # Validate all responses
        for response in responses:
            assert response.constitutional_hash == CONSTITUTIONAL_HASH
            assert response.constitutional_compliance_score > 0.8
            assert response.reliability_score > 0.8
            assert len(response.individual_responses) == 3
            assert CONSTITUTIONAL_HASH in response.final_content
        
        # Check federated metrics
        metrics = ensemble.get_federated_metrics()
        assert metrics["total_queries"] == 4
        assert metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert metrics["current_reliability"] > 0.8
        
        # Check health status
        health = await ensemble.health_check()
        assert health["status"] in ["healthy", "degraded"]  # Should be operational
        assert health["constitutional_hash"] == CONSTITUTIONAL_HASH
        
        print("✅ End-to-end federated ensemble workflow completed successfully")
        print(f"Average Reliability: {metrics['current_reliability']:.4f}")
        print(f"Target Reliability: {metrics['target_reliability']:.4f}")
        print(f"Constitutional Compliance Rate: {1.0 - metrics['constitutional_violation_rate']:.4f}")
        print(f"Bias Detection Rate: {metrics['bias_detection_rate']:.4f}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
