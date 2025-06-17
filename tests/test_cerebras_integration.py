#!/usr/bin/env python3
"""
Test suite for Cerebras AI integration in ACGS-1 constitutional governance system.

This test suite validates:
- Cerebras client initialization and configuration
- Model loading and API connectivity
- Constitutional compliance validation
- Multi-model consensus with Cerebras models
- Performance benchmarks and error handling
"""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, patch

import pytest

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from services.shared.ai_model_service import AIModelService
from services.shared.cerebras_client import (
    CerebrasClient,
    CerebrasConfig,
    CerebrasModel,
    get_cerebras_client,
)
from services.shared.langgraph_config import get_langgraph_config


class TestCerebrasClient:
    """Test Cerebras client functionality."""

    @pytest.fixture
    def cerebras_config(self):
        """Create test Cerebras configuration."""
        return CerebrasConfig(
            api_key="test-api-key",
            base_url="https://api.cerebras.ai/v1",
            timeout_seconds=30,
            max_retries=3,
            default_model=CerebrasModel.LLAMA3_1_8B,
        )

    @pytest.fixture
    def cerebras_client(self, cerebras_config):
        """Create test Cerebras client."""
        return CerebrasClient(cerebras_config)

    def test_cerebras_config_initialization(self, cerebras_config):
        """Test Cerebras configuration initialization."""
        assert cerebras_config.api_key == "test-api-key"
        assert cerebras_config.base_url == "https://api.cerebras.ai/v1"
        assert cerebras_config.default_model == CerebrasModel.LLAMA3_1_8B
        assert cerebras_config.max_tokens == 8192
        assert cerebras_config.temperature == 0.1

    def test_cerebras_client_initialization(self, cerebras_client):
        """Test Cerebras client initialization."""
        assert cerebras_client.config.api_key == "test-api-key"
        assert cerebras_client.request_count == 0
        assert cerebras_client.error_count == 0
        assert cerebras_client.total_response_time == 0.0

    @pytest.mark.asyncio
    async def test_constitutional_analysis_mock(self, cerebras_client):
        """Test constitutional analysis with mocked API response."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Constitutional analysis: This policy aligns with democratic principles and governance requirements."
                    },
                    "finish_reason": "completed",
                }
            ],
            "usage": {"total_tokens": 150},
        }

        with patch.object(cerebras_client.client, "post") as mock_post:
            mock_response_obj = AsyncMock()
            mock_response_obj.status_code = 200
            mock_response_obj.json.return_value = mock_response
            mock_post.return_value.__aenter__.return_value = mock_response_obj

            response = await cerebras_client.generate_constitutional_analysis(
                prompt="Analyze the constitutional implications of AI governance",
                constitution_hash="cdd01ef066bc6cf2",
            )

            assert response.content.startswith("Constitutional analysis:")
            assert response.model == "llama3.1-8b"
            assert response.tokens_used == 150
            assert response.finish_reason == "completed"
            assert response.constitutional_compliance_score > 0.5
            assert response.error is None

    @pytest.mark.asyncio
    async def test_fast_synthesis(self, cerebras_client):
        """Test fast policy synthesis."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Policy synthesis: Rapid constitutional governance framework with democratic oversight."
                    },
                    "finish_reason": "completed",
                }
            ],
            "usage": {"total_tokens": 120},
        }

        with patch.object(cerebras_client.client, "post") as mock_post:
            mock_post.return_value.__aenter__.return_value.status_code = 200
            mock_post.return_value.__aenter__.return_value.json.return_value = (
                mock_response
            )

            response = await cerebras_client.generate_fast_synthesis(
                prompt="Create a governance policy for AI oversight",
                policies=["POL-001", "POL-002"],
                principles=["Democratic Governance", "Transparency"],
            )

            assert "Policy synthesis:" in response.content
            assert response.model == "llama3.1-8b"
            assert response.constitutional_compliance_score > 0.0

    @pytest.mark.asyncio
    async def test_deep_analysis(self, cerebras_client):
        """Test deep constitutional analysis."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Deep constitutional analysis: Comprehensive governance framework evaluation with constitutional fidelity assessment."
                    },
                    "finish_reason": "completed",
                }
            ],
            "usage": {"total_tokens": 200},
        }

        with patch.object(cerebras_client.client, "post") as mock_post:
            mock_post.return_value.__aenter__.return_value.status_code = 200
            mock_post.return_value.__aenter__.return_value.json.return_value = (
                mock_response
            )

            response = await cerebras_client.generate_deep_analysis(
                prompt="Perform deep constitutional analysis of governance framework",
                constitution_hash="cdd01ef066bc6cf2",
            )

            assert "Deep constitutional analysis:" in response.content
            assert response.model == "llama3.1-70b"
            assert response.constitutional_compliance_score > 0.5

    @pytest.mark.asyncio
    async def test_api_error_handling(self, cerebras_client):
        """Test API error handling."""
        with patch.object(cerebras_client.client, "post") as mock_post:
            mock_post.return_value.__aenter__.return_value.status_code = 429
            mock_post.return_value.__aenter__.return_value.text = "Rate limit exceeded"

            response = await cerebras_client.generate_constitutional_analysis(
                prompt="Test error handling"
            )

            assert response.error is not None
            assert "429" in response.error
            assert response.finish_reason == "error"
            assert cerebras_client.error_count == 1

    def test_constitutional_compliance_assessment(self, cerebras_client):
        """Test constitutional compliance scoring."""
        # High compliance content
        high_compliance_content = """
        Constitutional analysis: This governance framework aligns with democratic principles,
        ensures transparency, maintains accountability, and respects fundamental rights.
        The policy demonstrates constitutional compliance and governance best practices.
        """

        score = cerebras_client._assess_constitutional_compliance(
            high_compliance_content
        )
        assert score > 0.7

        # Low compliance content
        low_compliance_content = (
            "Simple response without constitutional considerations."
        )

        score = cerebras_client._assess_constitutional_compliance(
            low_compliance_content
        )
        assert score < 0.3

    def test_confidence_score_calculation(self, cerebras_client):
        """Test confidence score calculation."""
        # High confidence content
        detailed_content = """
        Comprehensive constitutional analysis with multiple considerations.
        This detailed response covers governance implications, constitutional principles,
        and provides structured recommendations for implementation.
        """

        score = cerebras_client._calculate_confidence_score(
            detailed_content, CerebrasModel.LLAMA3_1_70B
        )
        assert score > 0.8

        # Low confidence content
        brief_content = "Short response."

        score = cerebras_client._calculate_confidence_score(
            brief_content, CerebrasModel.LLAMA3_1_8B
        )
        assert score < 0.8

    def test_performance_metrics(self, cerebras_client):
        """Test performance metrics tracking."""
        # Simulate some requests
        cerebras_client.request_count = 10
        cerebras_client.error_count = 2
        cerebras_client.total_response_time = 5000.0  # 5 seconds total

        metrics = cerebras_client.get_performance_metrics()

        assert metrics["total_requests"] == 10
        assert metrics["total_errors"] == 2
        assert metrics["error_rate"] == 0.2
        assert metrics["average_response_time_ms"] == 500.0


class TestCerebrasIntegration:
    """Test Cerebras integration with ACGS-1 services."""

    @pytest.mark.asyncio
    async def test_ai_model_service_cerebras_integration(self):
        """Test Cerebras integration with AI model service."""
        with patch.dict(
            os.environ, {"CEREBRAS_API_KEY": "test-key", "ENABLE_CEREBRAS": "true"}
        ):
            service = AIModelService()

            # Check if Cerebras models are loaded
            available_models = service.get_available_models()

            cerebras_models = [
                name
                for name, config in available_models.items()
                if config["provider"] == "cerebras"
            ]

            assert len(cerebras_models) >= 2  # Should have at least 2 Cerebras models

    @pytest.mark.asyncio
    async def test_langgraph_config_cerebras_support(self):
        """Test LangGraph configuration Cerebras support."""
        with patch.dict(os.environ, {"CEREBRAS_API_KEY": "test-key"}):
            config = get_langgraph_config()

            # Check API key validation
            api_keys = config.validate_api_keys()
            assert "cerebras" in api_keys

    @pytest.mark.asyncio
    async def test_global_cerebras_client(self):
        """Test global Cerebras client initialization."""
        with patch.dict(os.environ, {"CEREBRAS_API_KEY": "test-key"}):
            client = await get_cerebras_client()

            assert client is not None
            assert client.config.api_key == "test-key"

            await client.close()

    @pytest.mark.asyncio
    async def test_cerebras_client_without_api_key(self):
        """Test Cerebras client behavior without API key."""
        with patch.dict(os.environ, {}, clear=True):
            client = await get_cerebras_client()

            assert client is None


class TestCerebrasPerformance:
    """Test Cerebras performance and benchmarks."""

    @pytest.mark.asyncio
    async def test_response_time_benchmark(self):
        """Test Cerebras response time performance."""
        config = CerebrasConfig(api_key="test-key")

        async with CerebrasClient(config) as client:
            mock_response = {
                "choices": [
                    {
                        "message": {"content": "Fast response"},
                        "finish_reason": "completed",
                    }
                ],
                "usage": {"total_tokens": 50},
            }

            with patch.object(client.client, "post") as mock_post:
                mock_post.return_value.__aenter__.return_value.status_code = 200
                mock_post.return_value.__aenter__.return_value.json.return_value = (
                    mock_response
                )

                response = await client.generate_constitutional_analysis("Test prompt")

                # Cerebras should be fast (< 2s for this test)
                assert response.response_time_ms < 2000
                assert response.error is None

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test concurrent Cerebras requests."""
        config = CerebrasConfig(api_key="test-key")

        async with CerebrasClient(config) as client:
            mock_response = {
                "choices": [
                    {
                        "message": {"content": "Concurrent response"},
                        "finish_reason": "completed",
                    }
                ],
                "usage": {"total_tokens": 75},
            }

            with patch.object(client.client, "post") as mock_post:
                mock_post.return_value.__aenter__.return_value.status_code = 200
                mock_post.return_value.__aenter__.return_value.json.return_value = (
                    mock_response
                )

                # Run 5 concurrent requests
                tasks = [
                    client.generate_constitutional_analysis(f"Concurrent test {i}")
                    for i in range(5)
                ]

                responses = await asyncio.gather(*tasks)

                assert len(responses) == 5
                assert all(r.error is None for r in responses)
                assert client.request_count == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
