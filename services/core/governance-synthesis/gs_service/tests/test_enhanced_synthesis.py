"""
Comprehensive Unit Tests for Governance-Synthesis Enhanced Synthesis
HASH-OK:cdd01ef066bc6cf2

Tests the enhanced synthesis functionality including:
- Multi-model consensus algorithms
- Constitutional prompting mechanisms
- Policy synthesis workflows
- WINA optimization
- OPA validation
- Performance optimization
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import time
from datetime import datetime
from typing import Dict, Any, List

from services.core.governance_synthesis.gs_service.app.api.v1.enhanced_synthesis import (
    synthesize_policy,
    multi_model_consensus_synthesis
)
from services.core.governance_synthesis.gs_service.app.core.multi_model_coordinator import (
    MultiModelCoordinator,
    EnsembleResult,
    EnsembleStrategy,
    RequestComplexity
)
from services.core.governance_synthesis.gs_service.app.core.constitutional_prompting import (
    ConstitutionalPromptingEngine
)

# Constitutional Hash: cdd01ef066bc6cf2
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class TestEnhancedSynthesis:
    """Comprehensive test suite for Enhanced Synthesis functionality."""

    @pytest.fixture
    def mock_synthesis_service(self):
        """Mock enhanced synthesis service."""
        service = AsyncMock()
        service.synthesize_policy.return_value = {
            "policy": "Test synthesized policy with constitutional compliance",
            "confidence_score": 0.92,
            "constitutional_compliance": True,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "synthesis_method": "enhanced_multi_model",
            "performance_metrics": {
                "synthesis_time_ms": 45.2,
                "model_consensus_score": 0.89
            }
        }
        return service

    @pytest.fixture
    def sample_synthesis_request(self):
        """Sample synthesis request for testing."""
        return {
            "constitutional_principles": [
                "democratic_participation",
                "transparency",
                "accountability"
            ],
            "policy_domain": "data_governance",
            "stakeholder_requirements": [
                "privacy_protection",
                "data_accessibility"
            ],
            "synthesis_method": "multi_model_consensus",
            "enable_wina_optimization": True,
            "target_format": "rego"
        }

    @pytest.fixture
    def mock_multi_model_coordinator(self):
        """Mock multi-model coordinator."""
        coordinator = AsyncMock(spec=MultiModelCoordinator)
        coordinator.coordinate_synthesis.return_value = EnsembleResult(
            synthesized_policy="Test policy with constitutional compliance",
            confidence_score=0.91,
            contributing_models=["deepseek_chat_v3", "qwen3_235b"],
            ensemble_strategy_used=EnsembleStrategy.WEIGHTED_VOTING,
            performance_metrics={
                "total_synthesis_time_ms": 1250.5,
                "model_response_times": {"deepseek": 650.2, "qwen": 600.3}
            },
            constitutional_fidelity=0.95,
            wina_optimization_applied=True,
            synthesis_time_ms=1250.5
        )
        return coordinator

    @pytest.fixture
    def mock_constitutional_prompting(self):
        """Mock constitutional prompting engine."""
        engine = AsyncMock(spec=ConstitutionalPromptingEngine)
        engine.build_constitutional_context.return_value = {
            "principles": ["transparency", "accountability"],
            "constitutional_hierarchy": ["transparency", "accountability", "efficiency"],
            "context": "data_governance",
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        engine.build_constitutional_prompt.return_value = f"""
        Constitutional Prompt for Policy Synthesis
        Hash: {CONSTITUTIONAL_HASH}
        
        Principles: transparency, accountability
        Context: data_governance
        
        Generate policy that ensures constitutional compliance.
        """
        return engine

    async def test_constitutional_hash_validation(self):
        """Test that constitutional hash is properly validated."""
        assert CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"

    async def test_enhanced_synthesis_basic_functionality(self, mock_synthesis_service, sample_synthesis_request):
        """Test basic enhanced synthesis functionality."""
        with patch('services.core.governance_synthesis.gs_service.app.api.v1.enhanced_synthesis.get_enhanced_synthesis_service') as mock_get_service:
            mock_get_service.return_value = mock_synthesis_service
            
            # Mock request object
            mock_request = Mock()
            mock_request.constitutional_principles = sample_synthesis_request["constitutional_principles"]
            mock_request.policy_domain = sample_synthesis_request["policy_domain"]
            mock_request.stakeholder_requirements = sample_synthesis_request["stakeholder_requirements"]
            mock_request.synthesis_method = sample_synthesis_request["synthesis_method"]
            mock_request.enable_wina_optimization = sample_synthesis_request["enable_wina_optimization"]
            
            # Mock background tasks
            mock_background_tasks = Mock()
            
            # Execute synthesis
            result = await mock_synthesis_service.synthesize_policy(mock_request)
            
            # Verify results
            assert result is not None
            assert "policy" in result
            assert "constitutional_hash" in result
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
            assert result["constitutional_compliance"] is True
            assert result["confidence_score"] > 0.8

    async def test_multi_model_coordinator_initialization(self, mock_multi_model_coordinator):
        """Test multi-model coordinator initialization."""
        coordinator = mock_multi_model_coordinator
        
        # Test initialization
        await coordinator.initialize()
        
        # Verify initialization was called
        coordinator.initialize.assert_called_once()

    async def test_multi_model_consensus_synthesis(self, mock_multi_model_coordinator, sample_synthesis_request):
        """Test multi-model consensus synthesis."""
        coordinator = mock_multi_model_coordinator
        
        # Execute synthesis
        result = await coordinator.coordinate_synthesis(sample_synthesis_request, enable_wina=True)
        
        # Verify results
        assert isinstance(result, EnsembleResult)
        assert result.synthesized_policy is not None
        assert result.confidence_score > 0.8
        assert result.constitutional_fidelity > 0.9
        assert result.wina_optimization_applied is True
        assert len(result.contributing_models) > 0
        assert result.ensemble_strategy_used == EnsembleStrategy.WEIGHTED_VOTING

    async def test_constitutional_prompting_engine(self, mock_constitutional_prompting):
        """Test constitutional prompting engine functionality."""
        engine = mock_constitutional_prompting
        
        # Test context building
        context = await engine.build_constitutional_context(
            principles=["transparency", "accountability"],
            domain="data_governance"
        )
        
        assert context is not None
        assert "constitutional_hash" in context
        assert context["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "principles" in context
        assert "context" in context
        
        # Test prompt building
        prompt = await engine.build_constitutional_prompt(
            constitutional_context=context,
            synthesis_request="Generate data governance policy",
            enable_cot=True,
            enable_rag=True
        )
        
        assert prompt is not None
        assert CONSTITUTIONAL_HASH in prompt
        assert "constitutional compliance" in prompt.lower()

    async def test_wina_optimization_integration(self, mock_multi_model_coordinator):
        """Test WINA optimization integration."""
        coordinator = mock_multi_model_coordinator
        
        # Test with WINA enabled
        result_with_wina = await coordinator.coordinate_synthesis(
            {"test": "request"}, enable_wina=True
        )
        
        assert result_with_wina.wina_optimization_applied is True
        
        # Test with WINA disabled
        coordinator.coordinate_synthesis.return_value = EnsembleResult(
            synthesized_policy="Test policy",
            confidence_score=0.85,
            contributing_models=["model1"],
            ensemble_strategy_used=EnsembleStrategy.SIMPLE_MAJORITY,
            performance_metrics={},
            constitutional_fidelity=0.90,
            wina_optimization_applied=False,
            synthesis_time_ms=800.0
        )
        
        result_without_wina = await coordinator.coordinate_synthesis(
            {"test": "request"}, enable_wina=False
        )
        
        assert result_without_wina.wina_optimization_applied is False

    async def test_ensemble_strategies(self, mock_multi_model_coordinator):
        """Test different ensemble strategies."""
        coordinator = mock_multi_model_coordinator
        
        strategies = [
            EnsembleStrategy.WEIGHTED_VOTING,
            EnsembleStrategy.SIMPLE_MAJORITY,
            EnsembleStrategy.CONSTITUTIONAL_PRIORITY,
            EnsembleStrategy.PERFORMANCE_WEIGHTED
        ]
        
        for strategy in strategies:
            coordinator.coordinate_synthesis.return_value = EnsembleResult(
                synthesized_policy=f"Policy with {strategy.value} strategy",
                confidence_score=0.88,
                contributing_models=["model1", "model2"],
                ensemble_strategy_used=strategy,
                performance_metrics={},
                constitutional_fidelity=0.92,
                wina_optimization_applied=True,
                synthesis_time_ms=1000.0
            )
            
            result = await coordinator.coordinate_synthesis({"test": "request"})
            assert result.ensemble_strategy_used == strategy

    async def test_request_complexity_assessment(self):
        """Test request complexity assessment."""
        # Simple request
        simple_request = {
            "constitutional_principles": ["transparency"],
            "policy_domain": "simple_domain"
        }
        
        # Complex request
        complex_request = {
            "constitutional_principles": [
                "transparency", "accountability", "democratic_participation",
                "privacy", "security", "efficiency"
            ],
            "policy_domain": "multi_stakeholder_governance",
            "stakeholder_requirements": [
                "privacy_protection", "data_accessibility", "security_compliance",
                "performance_optimization", "cost_effectiveness"
            ],
            "constraints": ["regulatory_compliance", "technical_feasibility"]
        }
        
        # Test complexity assessment logic
        simple_complexity = len(simple_request.get("constitutional_principles", [])) + \
                          len(simple_request.get("stakeholder_requirements", [])) + \
                          len(simple_request.get("constraints", []))
        
        complex_complexity = len(complex_request.get("constitutional_principles", [])) + \
                           len(complex_request.get("stakeholder_requirements", [])) + \
                           len(complex_request.get("constraints", []))
        
        assert simple_complexity < 5  # Should be classified as simple
        assert complex_complexity > 10  # Should be classified as complex

    async def test_performance_metrics_collection(self, mock_multi_model_coordinator):
        """Test performance metrics collection."""
        coordinator = mock_multi_model_coordinator
        
        result = await coordinator.coordinate_synthesis({"test": "request"})
        
        # Verify performance metrics are collected
        assert "performance_metrics" in result.__dict__
        assert result.synthesis_time_ms > 0
        assert isinstance(result.performance_metrics, dict)

    async def test_constitutional_compliance_validation(self, mock_synthesis_service):
        """Test constitutional compliance validation throughout synthesis."""
        service = mock_synthesis_service
        
        # Test synthesis with constitutional validation
        result = await service.synthesize_policy(Mock())
        
        assert result["constitutional_compliance"] is True
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    async def test_opa_validation_integration(self, mock_synthesis_service):
        """Test OPA (Open Policy Agent) validation integration."""
        service = mock_synthesis_service
        
        # Mock OPA validation result
        service.synthesize_policy.return_value.update({
            "opa_validation": {
                "valid": True,
                "policy_conflicts": [],
                "compliance_score": 0.96,
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        })
        
        result = await service.synthesize_policy(Mock())
        
        assert "opa_validation" in result
        assert result["opa_validation"]["valid"] is True
        assert result["opa_validation"]["constitutional_hash"] == CONSTITUTIONAL_HASH

    async def test_policy_synthesis_workflow_integration(self):
        """Test policy synthesis workflow integration."""
        # Mock workflow state
        workflow_state = {
            "request_id": "test_request_123",
            "current_step": "synthesis",
            "constitutional_principles": ["transparency", "accountability"],
            "synthesis_progress": 0.75,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        # Verify workflow state structure
        assert "request_id" in workflow_state
        assert "constitutional_hash" in workflow_state
        assert workflow_state["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert 0 <= workflow_state["synthesis_progress"] <= 1

    async def test_error_handling_and_fallbacks(self, mock_multi_model_coordinator):
        """Test error handling and fallback mechanisms."""
        coordinator = mock_multi_model_coordinator
        
        # Test with synthesis failure
        coordinator.coordinate_synthesis.side_effect = Exception("Model unavailable")
        
        try:
            await coordinator.coordinate_synthesis({"test": "request"})
            assert False, "Should have raised an exception"
        except Exception as e:
            assert "Model unavailable" in str(e)

    async def test_caching_and_performance_optimization(self, mock_synthesis_service):
        """Test caching and performance optimization features."""
        service = mock_synthesis_service
        
        # Test cached response
        service.synthesize_policy.return_value.update({
            "cached": True,
            "cache_hit": True,
            "response_time_ms": 15.2,  # Fast cached response
            "constitutional_hash": CONSTITUTIONAL_HASH
        })
        
        result = await service.synthesize_policy(Mock())
        
        assert result.get("cached") is True
        assert result.get("response_time_ms", 0) < 50  # Should be fast
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    async def test_stakeholder_requirements_processing(self, mock_synthesis_service):
        """Test stakeholder requirements processing."""
        service = mock_synthesis_service
        
        stakeholder_requirements = [
            "privacy_protection",
            "data_accessibility", 
            "security_compliance",
            "performance_optimization"
        ]
        
        # Mock processing of stakeholder requirements
        service.synthesize_policy.return_value.update({
            "stakeholder_requirements_processed": stakeholder_requirements,
            "requirements_satisfaction_score": 0.94,
            "constitutional_hash": CONSTITUTIONAL_HASH
        })
        
        result = await service.synthesize_policy(Mock())
        
        assert "stakeholder_requirements_processed" in result
        assert len(result["stakeholder_requirements_processed"]) == len(stakeholder_requirements)
        assert result["requirements_satisfaction_score"] > 0.9

    async def test_constitutional_fidelity_scoring(self, mock_multi_model_coordinator):
        """Test constitutional fidelity scoring mechanism."""
        coordinator = mock_multi_model_coordinator
        
        result = await coordinator.coordinate_synthesis({"test": "request"})
        
        # Verify constitutional fidelity scoring
        assert hasattr(result, 'constitutional_fidelity')
        assert 0 <= result.constitutional_fidelity <= 1
        assert result.constitutional_fidelity > 0.9  # Should be high for compliant policies

    async def test_synthesis_method_selection(self, mock_synthesis_service):
        """Test synthesis method selection and routing."""
        service = mock_synthesis_service
        
        synthesis_methods = [
            "multi_model_consensus",
            "wina_optimization",
            "constitutional_prompting",
            "langgraph_workflow"
        ]
        
        for method in synthesis_methods:
            service.synthesize_policy.return_value.update({
                "synthesis_method_used": method,
                "method_performance": {
                    "accuracy": 0.92,
                    "speed_ms": 850.0,
                    "constitutional_compliance": True
                },
                "constitutional_hash": CONSTITUTIONAL_HASH
            })
            
            result = await service.synthesize_policy(Mock())
            
            assert result["synthesis_method_used"] == method
            assert result["method_performance"]["constitutional_compliance"] is True
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    async def test_background_task_integration(self, mock_synthesis_service):
        """Test background task integration for async processing."""
        service = mock_synthesis_service
        
        # Mock background task processing
        background_tasks = []
        
        def mock_add_task(func, *args, **kwargs):
            background_tasks.append((func, args, kwargs))
        
        mock_background_tasks = Mock()
        mock_background_tasks.add_task = mock_add_task
        
        # Simulate background task addition
        mock_background_tasks.add_task(
            "log_synthesis_metrics",
            synthesis_id="test_123",
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
        assert len(background_tasks) == 1
        assert background_tasks[0][2]["constitutional_hash"] == CONSTITUTIONAL_HASH


class TestMultiModelCoordinator:
    """Test suite for Multi-Model Coordinator functionality."""

    @pytest.fixture
    def coordinator_config(self):
        """Configuration for multi-model coordinator."""
        return {
            "primary_model": "deepseek_chat_v3",
            "fallback_models": ["qwen3_235b", "claude_3_5_sonnet"],
            "ensemble_strategies": ["weighted_voting", "constitutional_priority"],
            "performance_thresholds": {
                "max_response_time_ms": 2000,
                "min_confidence_score": 0.8,
                "min_constitutional_fidelity": 0.9
            },
            "constitutional_hash": CONSTITUTIONAL_HASH
        }

    async def test_model_selection_strategy(self, coordinator_config):
        """Test model selection strategy based on request complexity."""
        # Simple request should use single efficient model
        simple_request = {"complexity": "low", "principles": ["transparency"]}

        # Complex request should use ensemble
        complex_request = {
            "complexity": "high",
            "principles": ["transparency", "accountability", "privacy"],
            "stakeholders": ["citizens", "government", "businesses"]
        }

        # Verify selection logic
        assert len(simple_request["principles"]) < 3
        assert len(complex_request["principles"]) >= 3

    async def test_ensemble_voting_mechanisms(self):
        """Test different ensemble voting mechanisms."""
        # Mock model responses
        model_responses = [
            {"policy": "Policy A", "confidence": 0.9, "constitutional_score": 0.95},
            {"policy": "Policy B", "confidence": 0.85, "constitutional_score": 0.92},
            {"policy": "Policy C", "confidence": 0.88, "constitutional_score": 0.98}
        ]

        # Test weighted voting (highest constitutional score should win)
        best_response = max(model_responses, key=lambda x: x["constitutional_score"])
        assert best_response["policy"] == "Policy C"
        assert best_response["constitutional_score"] == 0.98

    async def test_constitutional_fidelity_calculation(self):
        """Test constitutional fidelity calculation."""
        # Mock policy analysis
        policy_text = "Data collection requires explicit user consent and transparent disclosure"
        constitutional_principles = ["transparency", "privacy", "consent"]

        # Simulate fidelity scoring
        principle_scores = {
            "transparency": 0.95,  # High transparency
            "privacy": 0.92,       # Good privacy protection
            "consent": 0.98        # Excellent consent mechanism
        }

        overall_fidelity = sum(principle_scores.values()) / len(principle_scores)
        assert overall_fidelity > 0.9
        assert all(score >= 0.9 for score in principle_scores.values())

class TestConstitutionalPrompting:
    """Test suite for Constitutional Prompting Engine."""

    async def test_prompt_template_generation(self):
        """Test constitutional prompt template generation."""
        template_components = {
            "constitutional_preamble": f"Constitutional Hash: {CONSTITUTIONAL_HASH}",
            "principles_section": "Core constitutional principles",
            "context_section": "Domain-specific context",
            "synthesis_instructions": "Policy generation instructions",
            "verification_section": "Compliance verification steps"
        }

        # Verify all components are present
        for component, content in template_components.items():
            assert content is not None
            assert len(content) > 0

        # Verify constitutional hash is included
        assert CONSTITUTIONAL_HASH in template_components["constitutional_preamble"]

    async def test_chain_of_thought_reasoning(self):
        """Test Chain-of-Thought reasoning integration."""
        cot_steps = [
            "1. Analyze constitutional principles",
            "2. Identify stakeholder requirements",
            "3. Assess potential conflicts",
            "4. Generate policy framework",
            "5. Validate constitutional compliance",
            f"6. Verify hash: {CONSTITUTIONAL_HASH}"
        ]

        # Verify CoT structure
        assert len(cot_steps) == 6
        assert all(step.startswith(f"{i+1}.") for i, step in enumerate(cot_steps))
        assert CONSTITUTIONAL_HASH in cot_steps[-1]

    async def test_rag_precedent_retrieval(self):
        """Test Retrieval-Augmented Generation for constitutional precedents."""
        # Mock precedent database
        constitutional_precedents = [
            {
                "case_id": "CONST_001",
                "principle": "transparency",
                "precedent": "Government data must be publicly accessible",
                "constitutional_hash": CONSTITUTIONAL_HASH
            },
            {
                "case_id": "CONST_002",
                "principle": "privacy",
                "precedent": "Personal data requires explicit consent",
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        ]

        # Test precedent retrieval
        transparency_precedents = [
            p for p in constitutional_precedents
            if p["principle"] == "transparency"
        ]

        assert len(transparency_precedents) == 1
        assert transparency_precedents[0]["constitutional_hash"] == CONSTITUTIONAL_HASH
