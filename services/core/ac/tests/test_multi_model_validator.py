"""
Comprehensive unit tests for Multi-Model Constitutional Compliance Validator
Target: >90% test coverage with accuracy validation

Tests cover:
- Multi-model consensus calculation
- Constitutional hash validation
- Performance metrics tracking
- Fallback mechanisms
- Error handling and edge cases
"""

import asyncio
import os

# Import the module under test
import sys
import time
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "validators"))

from multi_model_validator import (
    ConsensusResult,
    ModelConfig,
    ModelResponse,
    MultiModelValidator,
    ValidationResult,
    get_multi_model_validator,
)


class TestValidationResult:
    """Test ValidationResult enum."""

    def test_validation_result_values(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test validation result enum values."""
        assert ValidationResult.COMPLIANT.value == "compliant"
        assert ValidationResult.NON_COMPLIANT.value == "non_compliant"
        assert ValidationResult.UNCERTAIN.value == "uncertain"


class TestModelResponse:
    """Test ModelResponse dataclass."""

    def test_model_response_creation(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test model response creation."""
        response = ModelResponse(
            model_id="test_model",
            result=ValidationResult.COMPLIANT,
            confidence=0.95,
            reasoning="Policy aligns with constitutional principles",
            latency_ms=150.0,
            constitutional_alignment=0.9,
        )

        assert response.model_id == "test_model"
        assert response.result == ValidationResult.COMPLIANT
        assert response.confidence == 0.95
        assert response.latency_ms == 150.0
        assert response.error is None


class TestModelConfig:
    """Test ModelConfig dataclass."""

    def test_model_config_creation(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test model configuration creation."""
        config = ModelConfig(
            model_id="qwen3_32b",
            model_name="Qwen3-32B",
            weight=0.25,
            timeout_seconds=10,
            enabled=True,
            constitutional_specialization=True,
        )

        assert config.model_id == "qwen3_32b"
        assert config.weight == 0.25
        assert config.enabled is True
        assert config.constitutional_specialization is True


class TestMultiModelValidator:
    """Test MultiModelValidator functionality."""

    @pytest.fixture
    def validator(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Create validator for testing."""
        return MultiModelValidator(
            consensus_threshold=0.6,
            constitutional_hash="cdd01ef066bc6cf2",
            enable_fallback=True,
            max_validation_time=30,
        )

    @pytest.fixture
    def sample_policy_content(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Sample policy content for testing."""
        return """
        Policy POL-001: Constitutional Governance Framework
        
        This policy establishes the framework for constitutional governance
        within the ACGS-1 system, ensuring all governance actions comply
        with established constitutional principles.
        
        Requirements:
        1. All policy proposals must undergo constitutional review
        2. Governance actions require appropriate authorization
        3. Constitutional compliance must be verified before enactment
        """

    @pytest.fixture
    def sample_policy_context(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Sample policy context for testing."""
        return {
            "policy_id": "POL-001",
            "category": "constitutional_governance",
            "priority": "high",
            "proposed_by": "governance_committee",
            "timestamp": time.time(),
        }

    def test_validator_initialization(self, validator):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test validator initialization."""
        assert validator.consensus_threshold == 0.6
        assert validator.constitutional_hash == "cdd01ef066bc6cf2"
        assert validator.enable_fallback is True
        assert len(validator.models) == 5  # Default model count

        # Check model configurations
        model_ids = [m.model_id for m in validator.models]
        assert "qwen3_32b" in model_ids
        assert "deepseek_chat_v3" in model_ids
        assert "fallback_model" in model_ids

    def test_model_weight_distribution(self, validator):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test model weight distribution."""
        total_weight = sum(m.weight for m in validator.models if m.enabled)
        assert abs(total_weight - 1.0) < 0.01  # Should sum to approximately 1.0

        # Check individual weights are reasonable
        for model in validator.models:
            assert 0.0 <= model.weight <= 1.0

    @pytest.mark.asyncio
    async def test_constitutional_hash_validation(self, validator):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test constitutional hash validation."""
        result = await validator._validate_constitutional_hash()
        assert isinstance(result, bool)
        assert result is True  # Should validate reference hash

    def test_validation_prompt_construction(
        self, validator, sample_policy_content, sample_policy_context
    ):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test validation prompt construction."""
        model_config = validator.models[0]
        prompt = validator._construct_validation_prompt(
            sample_policy_content, sample_policy_context, "comprehensive", model_config
        )

        assert "constitutional compliance validator" in prompt.lower()
        assert validator.constitutional_hash in prompt
        assert "comprehensive" in prompt
        assert sample_policy_content in prompt
        assert "json" in prompt.lower()

    def test_model_response_parsing_valid_json(self, validator):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test parsing valid JSON model response."""
        json_response = '{"result": "COMPLIANT", "confidence": 0.95, "reasoning": "Policy aligns well", "constitutional_alignment": 0.9}'

        result, confidence, reasoning, alignment = validator._parse_model_response(
            json_response
        )

        assert result == ValidationResult.COMPLIANT
        assert confidence == 0.95
        assert reasoning == "Policy aligns well"
        assert alignment == 0.9

    def test_model_response_parsing_invalid_json(self, validator):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test parsing invalid JSON with fallback."""
        text_response = "This policy is COMPLIANT with constitutional principles."

        result, confidence, reasoning, alignment = validator._parse_model_response(
            text_response
        )

        assert result == ValidationResult.COMPLIANT
        assert 0.0 <= confidence <= 1.0
        assert len(reasoning) > 0
        assert 0.0 <= alignment <= 1.0

    def test_mock_model_response_compliant(self, validator):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test mock model response for compliant policy."""
        model_config = validator.models[0]
        policy_content = "This is a constitutional governance policy that ensures authorized actions."

        result, confidence, reasoning, alignment = validator._mock_model_response(
            model_config, policy_content
        )

        assert result == ValidationResult.COMPLIANT
        assert confidence > 0.8
        assert "constitutional" in reasoning.lower()
        assert alignment > 0.8

    def test_mock_model_response_non_compliant(self, validator):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test mock model response for non-compliant policy."""
        model_config = validator.models[0]
        policy_content = (
            "This policy allows unsafe and unauthorized bypass of security measures."
        )

        result, confidence, reasoning, alignment = validator._mock_model_response(
            model_config, policy_content
        )

        assert result == ValidationResult.NON_COMPLIANT
        assert confidence > 0.8
        assert "problematic" in reasoning.lower()
        assert alignment < 0.5

    def test_consensus_calculation_unanimous(self, validator):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test consensus calculation with unanimous agreement."""
        model_responses = [
            ModelResponse(
                model_id="model1",
                result=ValidationResult.COMPLIANT,
                confidence=0.9,
                reasoning="Compliant",
                latency_ms=100,
                constitutional_alignment=0.9,
            ),
            ModelResponse(
                model_id="model2",
                result=ValidationResult.COMPLIANT,
                confidence=0.85,
                reasoning="Compliant",
                latency_ms=120,
                constitutional_alignment=0.85,
            ),
            ModelResponse(
                model_id="model3",
                result=ValidationResult.COMPLIANT,
                confidence=0.95,
                reasoning="Compliant",
                latency_ms=90,
                constitutional_alignment=0.95,
            ),
        ]

        consensus = validator._calculate_consensus(model_responses, True)

        assert consensus.final_result == ValidationResult.COMPLIANT
        assert consensus.consensus_threshold_met is True
        assert consensus.agreement_percentage == 100.0
        assert consensus.constitutional_hash_validated is True
        assert len(consensus.model_responses) == 3

    def test_consensus_calculation_split_decision(self, validator):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test consensus calculation with split decision."""
        model_responses = [
            ModelResponse(
                model_id="model1",
                result=ValidationResult.COMPLIANT,
                confidence=0.8,
                reasoning="Compliant",
                latency_ms=100,
                constitutional_alignment=0.8,
            ),
            ModelResponse(
                model_id="model2",
                result=ValidationResult.NON_COMPLIANT,
                confidence=0.9,
                reasoning="Non-compliant",
                latency_ms=120,
                constitutional_alignment=0.3,
            ),
            ModelResponse(
                model_id="model3",
                result=ValidationResult.COMPLIANT,
                confidence=0.85,
                reasoning="Compliant",
                latency_ms=90,
                constitutional_alignment=0.85,
            ),
        ]

        consensus = validator._calculate_consensus(model_responses, True)

        # Should favor COMPLIANT (2 vs 1 votes)
        assert consensus.final_result == ValidationResult.COMPLIANT
        assert consensus.agreement_percentage < 100.0
        assert len(consensus.model_responses) == 3

    def test_consensus_calculation_no_responses(self, validator):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test consensus calculation with no model responses."""
        consensus = validator._calculate_consensus([], False)

        assert consensus.final_result == ValidationResult.UNCERTAIN
        assert consensus.consensus_threshold_met is False
        assert consensus.agreement_percentage == 0.0
        assert consensus.constitutional_hash_validated is False
        assert len(consensus.model_responses) == 0

    @pytest.mark.asyncio
    async def test_validate_with_model_mock(
        self, validator, sample_policy_content, sample_policy_context
    ):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test validation with individual model (mock)."""
        model_config = validator.models[0]

        response = await validator._validate_with_model(
            model_config, sample_policy_content, sample_policy_context, "comprehensive"
        )

        assert isinstance(response, ModelResponse)
        assert response.model_id == model_config.model_id
        assert response.result in [
            ValidationResult.COMPLIANT,
            ValidationResult.NON_COMPLIANT,
            ValidationResult.UNCERTAIN,
        ]
        assert 0.0 <= response.confidence <= 1.0
        assert response.latency_ms >= 0
        assert len(response.reasoning) > 0

    @pytest.mark.asyncio
    async def test_full_validation_process(
        self, validator, sample_policy_content, sample_policy_context
    ):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test complete validation process."""
        result = await validator.validate_constitutional_compliance(
            sample_policy_content, sample_policy_context, "comprehensive"
        )

        assert isinstance(result, ConsensusResult)
        assert result.final_result in [
            ValidationResult.COMPLIANT,
            ValidationResult.NON_COMPLIANT,
            ValidationResult.UNCERTAIN,
        ]
        assert 0.0 <= result.consensus_confidence <= 1.0
        assert result.total_latency_ms >= 0
        assert len(result.model_responses) > 0
        assert result.constitutional_hash_validated is True

    @pytest.mark.asyncio
    async def test_fallback_validation(
        self, validator, sample_policy_content, sample_policy_context
    ):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test fallback validation mechanism."""
        result = await validator._fallback_validation(
            sample_policy_content, sample_policy_context
        )

        assert isinstance(result, ConsensusResult)
        assert len(result.model_responses) == 1  # Single model response
        assert result.agreement_percentage == 100.0  # Single model always agrees
        assert result.total_latency_ms >= 0

    def test_performance_stats_update(self, validator):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test performance statistics update."""
        # Create mock consensus result
        model_responses = [
            ModelResponse(
                model_id="test_model",
                result=ValidationResult.COMPLIANT,
                confidence=0.9,
                reasoning="Test",
                latency_ms=100,
                constitutional_alignment=0.9,
            )
        ]

        consensus_result = ConsensusResult(
            final_result=ValidationResult.COMPLIANT,
            consensus_confidence=0.9,
            model_responses=model_responses,
            consensus_threshold_met=True,
            agreement_percentage=100.0,
            weighted_confidence=0.9,
            constitutional_hash_validated=True,
            validation_timestamp=time.time(),
            total_latency_ms=100.0,
        )

        initial_validations = validator.validation_stats["total_validations"]
        validator._update_performance_stats(consensus_result)

        assert (
            validator.validation_stats["total_validations"] == initial_validations + 1
        )
        assert validator.validation_stats["consensus_achieved"] > 0
        assert len(validator.validation_stats["accuracy_samples"]) > 0
        assert len(validator.validation_stats["latency_samples"]) > 0

    def test_performance_metrics_retrieval(self, validator):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test performance metrics retrieval."""
        metrics = validator.get_performance_metrics()

        required_fields = [
            "total_validations",
            "consensus_rate_percent",
            "average_accuracy",
            "average_latency_ms",
            "consensus_threshold",
            "constitutional_hash",
            "enabled_models",
            "model_performance",
            "target_accuracy_percent",
            "performance_status",
        ]

        for field in required_fields:
            assert field in metrics

        assert metrics["target_accuracy_percent"] == 95.0
        assert metrics["constitutional_hash"] == "cdd01ef066bc6cf2"
        assert metrics["performance_status"] in ["optimal", "needs_optimization"]


class TestMultiModelValidatorIntegration:
    """Integration tests for multi-model validator."""

    @pytest.mark.asyncio
    async def test_global_validator_singleton(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test global validator singleton pattern."""
        validator1 = await get_multi_model_validator()
        validator2 = await get_multi_model_validator()

        # Should return same instance
        assert validator1 is validator2

    @pytest.mark.asyncio
    async def test_custom_configuration(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test validator with custom configuration."""
        validator = await get_multi_model_validator(
            consensus_threshold=0.8, constitutional_hash="custom_hash_123"
        )

        assert validator.consensus_threshold == 0.8
        assert validator.constitutional_hash == "custom_hash_123"

    @pytest.mark.asyncio
    @patch("multi_model_validator.ModelClient")
    async def test_model_client_integration(self, mock_model_client_class):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Test integration with model client."""
        # Setup mock model client
        mock_client = AsyncMock()
        mock_client.generate_response.return_value = '{"result": "COMPLIANT", "confidence": 0.95, "reasoning": "Test response", "constitutional_alignment": 0.9}'
        mock_model_client_class.return_value = mock_client

        validator = MultiModelValidator()
        await validator.initialize_model_client()

        # Test validation with mocked client
        policy_content = "Test policy content"
        policy_context = {"test": "context"}

        result = await validator.validate_constitutional_compliance(
            policy_content, policy_context
        )

        assert isinstance(result, ConsensusResult)
        # Verify model client was called
        assert mock_client.generate_response.called


if __name__ == "__main__":
    pytest.main(
        [__file__, "-v", "--cov=multi_model_validator", "--cov-report=term-missing"]
    )
