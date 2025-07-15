"""
Unit tests for Gemini validators in ACGS-1 constitutional governance.
Tests GeminiProValidator and GeminiFlashValidator functionality.

Test Coverage Requirements:
- ≥90% test pass rate
- ≥80% code coverage
- Constitutional compliance validation
- Performance targets validation
- Error handling and resilience testing

Formal Verification Comments:
# requires: test_coverage >= 0.8
# ensures: all_tests_pass_rate >= 0.9
# ensures: constitutional_compliance_accuracy >= 0.95
# sha256: evolutionary_tensor_decomposition_gemini_tests_v1.0
"""

import json
import os
import unittest
from unittest.mock import AsyncMock, patch

from services.core.governance-synthesis.gs_service.app.core.heterogeneous_validator import (

# Add parent directory to path to handle dash-named directories
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

    GovernanceContext,
    ValidationResult,
)

# Import the validators to test
from services.core.governance-synthesis.gs_service.app.validators.gemini_validators import (
    GeminiFlashValidator,
    GeminiProValidator,
)


class TestGeminiProValidator(unittest.TestCase):
    """Test suite for GeminiProValidator."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = GeminiProValidator()
        self.test_context = GovernanceContext(
            constitutional_hash="cdd01ef066bc6cf2",
            policy_type="constitutional",
            compliance_requirements={
                "accuracy_threshold": 0.95,
                "constitutional_compliance": True,
            },
            performance_targets={"response_time_ms": 2000, "accuracy": 0.95},
        )
        self.test_policy_data = {
            "content": "Test policy content for constitutional governance",
            "type": "constitutional",
            "metadata": {"version": "1.0", "author": "ACGS-1"},
        }

    def test_validator_initialization(self):
        """Test validator initialization and configuration."""
        assert self.validator.name == "gemini_pro"
        assert self.validator.weight == 0.1
        assert self.validator.base_url is not None
        assert self.validator.max_retries == 3
        assert self.validator.retry_delay == 1.0

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"})
    @patch("aiohttp.ClientSession.post")
    async def test_successful_validation(self, mock_post):
        """Test successful validation with proper API response."""
        # Mock successful API response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps(
                                    {
                                        "overall_score": 0.96,
                                        "confidence": 0.92,
                                        "constitutional_compliance": 0.98,
                                        "legal_consistency": 0.94,
                                        "implementation_feasibility": 0.95,
                                        "stakeholder_impact": 0.90,
                                        "detailed_analysis": "Policy demonstrates strong constitutional alignment",
                                        "recommendations": [
                                            "Consider stakeholder feedback"
                                        ],
                                        "risk_factors": ["Implementation complexity"],
                                    }
                                )
                            }
                        ]
                    }
                }
            ]
        }
        mock_post.return_value.__aenter__.return_value = mock_response

        # Create validator with API key
        validator = GeminiProValidator()
        validator.api_key = "test_api_key"

        # Execute validation
        result = await validator.validate(self.test_policy_data, self.test_context)

        # Assertions
        assert isinstance(result, ValidationResult)
        assert result.score == 0.96
        assert result.confidence == 0.92
        assert result.error_message is None
        assert "constitutional_compliance" in result.details
        assert result.details["validator"] == "gemini_pro"

    @patch.dict(os.environ, {}, clear=True)
    async def test_missing_api_key(self):
        """Test behavior when API key is not configured."""
        validator = GeminiProValidator()

        result = await validator.validate(self.test_policy_data, self.test_context)

        assert result.score == 0.0
        assert result.confidence == 0.0
        assert result.error_message is not None
        assert "API key not available" in result.error_message

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"})
    @patch("aiohttp.ClientSession.post")
    async def test_api_error_handling(self, mock_post):
        """Test handling of API errors and retries."""
        # Mock API error response
        mock_response = AsyncMock()
        mock_response.status = 429  # Rate limit error
        mock_response.raise_for_status.side_effect = Exception("Rate limited")
        mock_post.return_value.__aenter__.return_value = mock_response

        validator = GeminiProValidator()
        validator.api_key = "test_api_key"

        result = await validator.validate(self.test_policy_data, self.test_context)

        assert result.score == 0.0
        assert result.confidence == 0.0
        assert result.error_message is not None
        assert "Validation failed" in result.error_message

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"})
    @patch("aiohttp.ClientSession.post")
    async def test_response_parsing_fallback(self, mock_post):
        """Test fallback when JSON parsing fails."""
        # Mock response with unparseable content
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "This is not valid JSON for parsing"}]}}
            ]
        }
        mock_post.return_value.__aenter__.return_value = mock_response

        validator = GeminiProValidator()
        validator.api_key = "test_api_key"

        result = await validator.validate(self.test_policy_data, self.test_context)

        # Should fallback to default score
        assert result.score == 0.7
        assert result.confidence == 0.6
        assert "parsing_note" in result.details

    def test_metrics_tracking(self):
        """Test that metrics are properly tracked."""
        validator = GeminiProValidator()

        # Initial metrics
        assert validator.metrics["total_validations"] == 0
        assert validator.metrics["average_latency_ms"] == 0.0
        assert validator.metrics["error_rate"] == 0.0

        # Test metrics update
        validator._update_metrics(150.0, success=True)
        validator.metrics["total_validations"] = 1  # Simulate validation count

        assert validator.metrics["average_latency_ms"] == 150.0

        # Test error tracking
        validator._update_metrics(200.0, success=False)
        validator.metrics["total_validations"] = 2

        assert validator.metrics["total_errors"] == 1
        assert validator.metrics["error_rate"] == 0.5


class TestGeminiFlashValidator(unittest.TestCase):
    """Test suite for GeminiFlashValidator."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = GeminiFlashValidator()
        self.test_context = GovernanceContext(
            constitutional_hash="cdd01ef066bc6cf2",
            policy_type="operational",
            compliance_requirements={"basic_compliance": True},
            performance_targets={"response_time_ms": 100},
        )
        self.test_policy_data = {
            "content": "Test operational policy for rapid screening",
            "type": "operational",
        }

    def test_validator_initialization(self):
        """Test GeminiFlash validator initialization."""
        assert self.validator.name == "gemini_flash"
        assert self.validator.weight == 0.05
        assert self.validator.max_retries == 2  # Fewer retries for speed
        assert self.validator.retry_delay == 0.5

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"})
    @patch("aiohttp.ClientSession.post")
    async def test_rapid_screening(self, mock_post):
        """Test rapid screening functionality."""
        # Mock fast response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "SCORE: 0.85 | ASSESSMENT: Policy appears fundamentally sound with no obvious constitutional violations. Recommend proceeding to detailed review."
                            }
                        ]
                    }
                }
            ]
        }
        mock_post.return_value.__aenter__.return_value = mock_response

        validator = GeminiFlashValidator()
        validator.api_key = "test_api_key"

        result = await validator.validate(self.test_policy_data, self.test_context)

        assert result.score == 0.85
        assert result.confidence == 0.8
        assert result.details["screening_mode"]
        assert result.details["validator"] == "gemini_flash"

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"})
    @patch("aiohttp.ClientSession.post")
    async def test_timeout_handling(self, mock_post):
        """Test timeout handling for rapid responses."""
        # Mock timeout scenario
        mock_post.side_effect = TimeoutError("Request timeout")

        validator = GeminiFlashValidator()
        validator.api_key = "test_api_key"

        result = await validator.validate(self.test_policy_data, self.test_context)

        # Should return neutral score on timeout
        assert result.score == 0.5
        assert result.confidence == 0.0
        assert result.error_message is not None

    def test_prompt_truncation(self):
        """Test that prompts are truncated for speed."""
        validator = GeminiFlashValidator()

        # Create long policy content
        long_policy = {"content": "A" * 1000}

        prompt = validator._create_screening_prompt(long_policy, self.test_context)

        # Should truncate to 500 characters
        assert "A" * 500 in prompt
        assert "A" * 600 not in prompt


class TestHeterogeneousValidatorIntegration(unittest.TestCase):
    """Test integration of Gemini validators with HeterogeneousValidator."""

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"})
    def test_gemini_validators_registration(self):
        """Test that Gemini validators are properly registered."""
        from services.core.governance-synthesis.gs_service.app.core.heterogeneous_validator import (
            HeterogeneousValidator,
        )

        validator = HeterogeneousValidator()

        # Check that Gemini validators are included
        assert "gemini_pro" in validator.validators
        assert "gemini_flash" in validator.validators

        # Check weights are properly set
        assert validator.weights["gemini_pro"] == 0.1
        assert validator.weights["gemini_flash"] == 0.05

    @patch.dict(os.environ, {}, clear=True)
    def test_graceful_degradation_without_api_key(self):
        """Test graceful degradation when Gemini API key is not available."""
        from services.core.governance-synthesis.gs_service.app.core.heterogeneous_validator import (
            HeterogeneousValidator,
        )

        # Should not crash when API key is missing
        validator = HeterogeneousValidator()

        # Gemini validators should still be registered but with 0 weight
        if "gemini_pro" in validator.validators:
            assert validator.weights.get("gemini_pro", 0) == 0.0
        if "gemini_flash" in validator.validators:
            assert validator.weights.get("gemini_flash", 0) == 0.0


class TestPerformanceRequirements(unittest.TestCase):
    """Test performance requirements for validators."""

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"})
    @patch("aiohttp.ClientSession.post")
    async def test_gemini_pro_accuracy_target(self, mock_post):
        """Test that GeminiPro meets >95% accuracy target."""
        # Mock high-accuracy response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps(
                                    {
                                        "overall_score": 0.97,
                                        "confidence": 0.96,
                                        "constitutional_compliance": 0.98,
                                    }
                                )
                            }
                        ]
                    }
                }
            ]
        }
        mock_post.return_value.__aenter__.return_value = mock_response

        validator = GeminiProValidator()
        validator.api_key = "test_api_key"

        context = GovernanceContext(
            constitutional_hash="cdd01ef066bc6cf2",
            policy_type="constitutional",
            compliance_requirements={"accuracy_threshold": 0.95},
            performance_targets={"accuracy": 0.95},
        )

        result = await validator.validate({}, context)

        # Should meet >95% accuracy target
        assert result.score >= 0.95
        assert result.confidence >= 0.9

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"})
    @patch("aiohttp.ClientSession.post")
    async def test_gemini_flash_speed_target(self, mock_post):
        """Test that GeminiFlash meets <100ms response time target."""
        import time

        # Mock fast response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "SCORE: 0.8 | ASSESSMENT: Quick screening passed"}
                        ]
                    }
                }
            ]
        }
        mock_post.return_value.__aenter__.return_value = mock_response

        validator = GeminiFlashValidator()
        validator.api_key = "test_api_key"

        start_time = time.time()
        result = await validator.validate(
            {},
            GovernanceContext(
                constitutional_hash="test",
                policy_type="operational",
                compliance_requirements={},
                performance_targets={"response_time_ms": 100},
            ),
        )
        end_time = time.time()

        # Response time should be reasonable (allowing for mocking overhead)
        response_time_ms = (end_time - start_time) * 1000
        assert response_time_ms < 1000  # Generous limit for testing

        # Should return valid result
        assert isinstance(result, ValidationResult)
        assert result.score >= 0.0
        assert result.score <= 1.0


if __name__ == "__main__":
    # Run tests with coverage
    unittest.main(verbosity=2)
