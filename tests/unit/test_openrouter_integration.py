"""
Test OpenRouter integration in AI Model Service.
"""

# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from services.shared.ai_model_service import (
    AIModelService,
    ModelProvider,
    ModelRequest,
    ModelType,
)


class TestOpenRouterIntegration:
    """Test OpenRouter integration functionality"""

    @pytest.fixture
    def ai_service(self):
        """Create AI Model Service instance"""
        return AIModelService()

    @pytest.fixture
    def mock_openrouter_response(self):
        """Mock OpenRouter API response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = (
            "Constitutional compliance analysis: The content appears compliant with ACGS principles. No violations detected."
        )
        return mock_response

    def test_openrouter_provider_in_configs(self, ai_service):
        """Test that Groq provider is properly configured (replacing OpenRouter)"""
        assert ModelProvider.GROQ in ai_service.model_configs
        groq_config = ai_service.model_configs[ModelProvider.GROQ]

        # Check that constitutional validation models are available
        assert "constitutional_validation" in groq_config
        assert (
            "llama-3.3-70b-versatile"
            in groq_config["constitutional_validation"]
        )

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"})
    @patch("services.shared.ai_model_service.OpenAI")
    def test_openrouter_client_initialization(self, mock_openai, ai_service):
        """Test OpenRouter client initialization with API key"""
        # Reinitialize to pick up the environment variable
        ai_service._initialize_openrouter_client()

        # Verify OpenAI client was called with correct parameters
        mock_openai.assert_called_once_with(
            base_url="https://openrouter.ai/api/v1", api_key="test-key"
        )

    @patch.dict("os.environ", {}, clear=True)  # Clear all environment variables
    @patch("os.getenv")
    def test_openrouter_client_initialization_no_key(self, mock_getenv):
        """Test OpenRouter client initialization without API key"""
        # Mock getenv to return None for OPENROUTER_API_KEY
        mock_getenv.return_value = None

        # Create a fresh service instance without API key
        ai_service = AIModelService()
        assert ai_service.openrouter_client is None

    @pytest.mark.asyncio
    async def test_constitutional_compliance_validation(
        self, ai_service, mock_openrouter_response
    ):
        """Test constitutional compliance validation using Groq"""
        with patch.object(ai_service, "_call_groq", return_value="Constitutional compliance analysis: The content appears compliant with ACGS principles. No violations detected."):
            response = await ai_service.validate_constitutional_compliance(
                content="Agent decision to process user data",
                context={"agent_id": "test-agent", "action": "data_processing"},
            )

            assert (
                response.content
                == "Constitutional compliance analysis: The content appears compliant with ACGS principles. No violations detected."
            )
            assert response.metadata["provider"] == ModelProvider.GROQ

            # Verify the API was called with correct parameters
            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args

            assert call_args[1]["model"] == "openrouter/cypher-alpha:free"
            assert "constitutional compliance" in call_args[1]["messages"][1]["content"]

    @pytest.mark.asyncio
    async def test_governance_decision_analysis(
        self, ai_service, mock_openrouter_response
    ):
        """Test governance decision analysis using Groq"""
        with patch.object(ai_service, "_call_groq", return_value="Constitutional compliance analysis: The content appears compliant with ACGS principles. No violations detected."):
            decision = {
                "type": "policy_update",
                "description": "Update data retention policy",
                "impact": "all_agents",
            }
            stakeholders = ["users", "agents", "administrators"]

            response = await ai_service.analyze_governance_decision(
                decision, stakeholders
            )

            assert (
                response.content
                == "Constitutional compliance analysis: The content appears compliant with ACGS principles. No violations detected."
            )
            assert response.metadata["provider"] == ModelProvider.GROQ

    @pytest.mark.asyncio
    async def test_agent_behavior_evaluation(
        self, ai_service, mock_openrouter_response
    ):
        """Test agent behavior evaluation"""
        with patch.object(ai_service, "openrouter_client") as mock_client:
            mock_client.chat.completions.create.return_value = mock_openrouter_response

            behavior_log = [
                {
                    "timestamp": "2024-01-01T10:00:00",
                    "action": "data_access",
                    "result": "success",
                },
                {
                    "timestamp": "2024-01-01T10:05:00",
                    "action": "decision_made",
                    "result": "approved",
                },
            ]

            response = await ai_service.evaluate_agent_behavior(
                "test-agent", behavior_log
            )

            assert (
                response.content
                == "Constitutional compliance analysis: The content appears compliant with ACGS principles. No violations detected."
            )
            assert response.metadata["provider"] == ModelProvider.OPENROUTER

            # Verify the API was called
            mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_openrouter_content_generation_error_handling(self, ai_service):
        """Test error handling in OpenRouter content generation"""
        # Test with authentication error (no valid API key)
        request = ModelRequest(
            model_type=ModelType.CHAT,
            provider=ModelProvider.OPENROUTER,
            model_name="openrouter/cypher-alpha:free",
            prompt="Test prompt",
        )

        response = await ai_service.generate_response(request)
        # Check for OpenRouter API error format
        assert "OpenRouter error:" in response.content
        assert (
            "No auth credentials found" in response.content
            or "OpenRouter client not initialized" in response.content
        )
        assert response.metadata.get("provider") == ModelProvider.OPENROUTER

    @pytest.mark.asyncio
    async def test_openrouter_api_error_handling(self, ai_service):
        """Test API error handling"""
        with patch.object(ai_service, "openrouter_client") as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            request = ModelRequest(
                model_type=ModelType.CHAT,
                provider=ModelProvider.OPENROUTER,
                model_name="openrouter/cypher-alpha:free",
                prompt="Test prompt",
            )

            content = await ai_service._generate_openrouter_content(request)
            assert "OpenRouter error: API Error" in content

    def test_model_availability_check(self, ai_service):
        """Test model availability checking for OpenRouter"""
        # Test valid model
        assert ai_service._is_model_available(
            ModelProvider.OPENROUTER, ModelType.CHAT, "openrouter/cypher-alpha:free"
        )

        # Test invalid model
        assert not ai_service._is_model_available(
            ModelProvider.OPENROUTER, ModelType.CHAT, "invalid-model"
        )

        # Test constitutional validation models
        assert ai_service._is_model_available(
            ModelProvider.OPENROUTER,
            "constitutional_validation",
            "openrouter/cypher-alpha:free",
        )

    @pytest.mark.asyncio
    async def test_constitutional_system_prompt_injection(self, ai_service):
        """Test that constitutional validation gets proper system prompt"""
        with patch.object(ai_service, "openrouter_client") as mock_client:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Analysis complete"
            mock_client.chat.completions.create.return_value = mock_response

            request = ModelRequest(
                model_type=ModelType.ANALYSIS,
                provider=ModelProvider.OPENROUTER,
                model_name="openrouter/cypher-alpha:free",
                prompt="constitutional compliance check for agent behavior",
            )

            await ai_service._generate_openrouter_content(request)

            # Verify system prompt was added
            call_args = mock_client.chat.completions.create.call_args
            messages = call_args[1]["messages"]

            assert len(messages) == 2  # system + user message
            assert messages[0]["role"] == "system"
            assert "constitutional AI validator" in messages[0]["content"]
            assert "ACGS system" in messages[0]["content"]
