"""
Integration Tests for Constitutional Trainer Service
Tests ACGS-1 Lite integration and constitutional compliance validation.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from constitutional_trainer import ConstitutionalConfig, ConstitutionalTrainer
from fastapi.testclient import TestClient
from main import app
from privacy_engine import ConstitutionalPrivacyEngine
from validators import ACGSConstitutionalValidator

# Test configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
TEST_CONFIG = {
    "constitutional_hash": CONSTITUTIONAL_HASH,
    "compliance_threshold": 0.95,
    "policy_engine_url": "http://test-policy-engine:8001",
    "audit_engine_url": "http://test-audit-engine:8003",
    "max_critique_iterations": 3,
}


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_auth_token():
    """Mock authentication token."""
    return "Bearer test-constitutional-trainer-token"


@pytest.fixture
def constitutional_config():
    """Constitutional configuration for testing."""
    return ConstitutionalConfig(**TEST_CONFIG)


@pytest.fixture
def sample_training_request():
    """Sample training request for testing."""
    return {
        "model_name": "microsoft/DialoGPT-small",
        "training_data": [
            {
                "prompt": "What are the principles of ethical AI?",
                "response": "Ethical AI should be fair, transparent, accountable, and respect human rights.",
            },
            {
                "prompt": "How should AI handle personal data?",
                "response": "AI systems must protect privacy and handle personal data with strict security measures.",
            },
        ],
        "model_id": "test-constitutional-model-001",
        "constitutional_constraints": {
            "harmlessness_weight": 0.3,
            "helpfulness_weight": 0.25,
            "honesty_weight": 0.25,
            "privacy_weight": 0.2,
        },
        "lora_config": {"r": 8, "lora_alpha": 16, "lora_dropout": 0.1},
        "privacy_config": {"noise_multiplier": 1.1, "max_grad_norm": 1.0},
    }


class TestConstitutionalTrainerAPI:
    """Test Constitutional Trainer API endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "constitutional-trainer"
        assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "timestamp" in data

    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "constitutional_training_requests_total" in response.text
        assert "constitutional_compliance_score" in response.text

    @patch("main.verify_token")
    def test_start_training_unauthorized(
        self, mock_verify_token, client, sample_training_request
    ):
        """Test training start with invalid authentication."""
        mock_verify_token.side_effect = Exception("Invalid token")

        response = client.post(
            "/api/v1/train",
            json=sample_training_request,
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401

    @patch("main.verify_token")
    @patch("main.execute_constitutional_training")
    def test_start_training_success(
        self, mock_execute_training, mock_verify_token, client, sample_training_request
    ):
        """Test successful training start."""
        mock_verify_token.return_value = {
            "user_id": "test-user",
            "groups": ["constitutional-ai-users"],
            "permissions": ["model_training", "constitutional_validation"],
        }

        response = client.post(
            "/api/v1/train",
            json=sample_training_request,
            headers={"Authorization": "Bearer valid-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        assert "training_id" in data
        assert data["message"] == "Constitutional training initiated successfully"

    @patch("main.verify_token")
    def test_start_training_insufficient_permissions(
        self, mock_verify_token, client, sample_training_request
    ):
        """Test training start with insufficient permissions."""
        mock_verify_token.return_value = {
            "user_id": "test-user",
            "groups": ["basic-users"],
            "permissions": ["read_only"],
        }

        response = client.post(
            "/api/v1/train",
            json=sample_training_request,
            headers={"Authorization": "Bearer valid-token"},
        )

        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    def test_start_training_invalid_data(self, client):
        """Test training start with invalid data."""
        invalid_request = {
            "model_name": "",  # Invalid empty model name
            "training_data": [],  # Invalid empty training data
        }

        response = client.post(
            "/api/v1/train",
            json=invalid_request,
            headers={"Authorization": "Bearer valid-token"},
        )

        assert response.status_code == 422  # Validation error


class TestConstitutionalValidator:
    """Test Constitutional Validator integration."""

    @pytest.fixture
    def validator(self, constitutional_config):
        """Constitutional validator instance."""
        return ACGSConstitutionalValidator(constitutional_config)

    @pytest.mark.asyncio
    async def test_validator_initialization(self, validator):
        """Test validator initialization."""
        await validator.initialize()
        assert validator.constitutional_hash == CONSTITUTIONAL_HASH
        assert validator.config.compliance_threshold == 0.95

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_policy_engine_integration(self, mock_post, validator):
        """Test Policy Engine integration."""
        # Mock Policy Engine response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "allow": True,
            "confidence_score": 0.96,
            "violations": [],
            "reason": "Constitutional compliance validated",
        }
        mock_post.return_value.__aenter__.return_value = mock_response

        await validator.initialize()

        is_compliant, score, violations = await validator.validate_response(
            "AI should be developed ethically and responsibly.",
            {"prompt": "What are AI ethics?", "test": True},
        )

        assert is_compliant is True
        assert score >= 0.95
        assert len(violations) == 0

        # Verify Policy Engine was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "constitutional_evaluation" in str(call_args)

    @pytest.mark.asyncio
    async def test_local_validation_fallback(self, validator):
        """Test local validation when Policy Engine is unavailable."""
        await validator.initialize()

        # Test with content that should pass local validation
        is_compliant, score, violations = await validator._validate_locally(
            "This is a helpful and harmless response about AI ethics.",
            {"prompt": "Test prompt"},
        )

        assert isinstance(is_compliant, bool)
        assert 0.0 <= score <= 1.0
        assert isinstance(violations, list)

    @pytest.mark.asyncio
    async def test_batch_validation(self, validator):
        """Test batch validation functionality."""
        await validator.initialize()

        responses = [
            "AI should be developed ethically.",
            "Machine learning requires careful consideration.",
            "Privacy protection is essential in AI systems.",
        ]
        contexts = [{"prompt": f"Test prompt {i}"} for i in range(len(responses))]

        with patch.object(validator, "validate_response") as mock_validate:
            mock_validate.return_value = (True, 0.96, [])

            results = await validator.batch_validate(responses, contexts)

            assert len(results) == len(responses)
            assert all(
                isinstance(result, tuple) and len(result) == 3 for result in results
            )
            assert mock_validate.call_count == len(responses)

    @pytest.mark.asyncio
    async def test_health_check(self, validator):
        """Test validator health check."""
        await validator.initialize()

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_get.return_value.__aenter__.return_value = mock_response

            health_status = await validator.health_check()

            assert "validator_status" in health_status
            assert health_status["constitutional_hash"] == CONSTITUTIONAL_HASH
            assert "policy_engine_status" in health_status
            assert "audit_engine_status" in health_status


class TestConstitutionalTrainer:
    """Test Constitutional Trainer core functionality."""

    @pytest.fixture
    def trainer(self, constitutional_config):
        """Constitutional trainer instance."""
        with patch("constitutional_trainer.AutoModelForCausalLM.from_pretrained"):
            with patch("constitutional_trainer.AutoTokenizer.from_pretrained"):
                return ConstitutionalTrainer(
                    "microsoft/DialoGPT-small", constitutional_config
                )

    @pytest.mark.asyncio
    async def test_critique_revision_cycle(self, trainer):
        """Test critique-revision cycle functionality."""
        with patch.object(trainer.validator, "validate_response") as mock_validate:
            # First call: low compliance, second call: high compliance
            mock_validate.side_effect = [
                (False, 0.85, ["harmlessness_violation"]),
                (True, 0.96, []),
            ]

            with patch.object(trainer, "_generate_response") as mock_generate:
                mock_generate.side_effect = [
                    "Critique of the response",
                    "Improved constitutional response",
                ]

                improved_response, score = await trainer._critique_revision_cycle(
                    "Test prompt", "Original response"
                )

                assert score >= 0.95
                assert improved_response == "Improved constitutional response"
                assert mock_validate.call_count == 2

    @pytest.mark.asyncio
    async def test_preprocess_training_data(self, trainer):
        """Test training data preprocessing with constitutional validation."""
        training_data = [
            {"prompt": "What is AI?", "response": "AI is artificial intelligence."},
            {"prompt": "How to hack?", "response": "I cannot help with hacking."},
        ]

        with patch.object(trainer, "_critique_revision_cycle") as mock_cycle:
            mock_cycle.side_effect = [
                ("AI is artificial intelligence with ethical considerations.", 0.96),
                ("I cannot help with hacking as it violates ethical guidelines.", 0.97),
            ]

            processed_data = await trainer._preprocess_training_data(training_data)

            assert len(processed_data) == 2
            assert all(item["compliance_score"] >= 0.95 for item in processed_data)
            assert all("improved" in item for item in processed_data)


class TestPrivacyEngine:
    """Test Constitutional Privacy Engine."""

    @pytest.fixture
    def privacy_engine(self, constitutional_config):
        """Privacy engine instance."""
        mock_model = MagicMock()
        return ConstitutionalPrivacyEngine(mock_model, constitutional_config)

    def test_privacy_engine_initialization(self, privacy_engine):
        """Test privacy engine initialization."""
        assert privacy_engine.constitutional_hash == CONSTITUTIONAL_HASH
        assert privacy_engine.target_epsilon == 8.0
        assert privacy_engine.target_delta == 1e-5

    def test_privacy_budget_tracking(self, privacy_engine):
        """Test privacy budget tracking."""
        with patch.object(
            privacy_engine.privacy_engine, "get_epsilon", return_value=4.0
        ):
            privacy_spent = privacy_engine.get_privacy_spent()

            assert privacy_spent["epsilon"] == 4.0
            assert privacy_spent["target_epsilon"] == 8.0
            assert privacy_spent["remaining_budget"] == 4.0
            assert privacy_spent["budget_utilization"] == 0.5
            assert privacy_spent["constitutional_hash"] == CONSTITUTIONAL_HASH

    def test_privacy_budget_check(self, privacy_engine):
        """Test privacy budget status checking."""
        with patch.object(privacy_engine, "get_privacy_spent") as mock_spent:
            mock_spent.return_value = {
                "epsilon": 7.6,
                "target_epsilon": 8.0,
                "budget_utilization": 0.95,
                "remaining_budget": 0.4,
            }

            budget_status = privacy_engine.check_privacy_budget()

            assert budget_status["status"] == "critical"
            assert budget_status["budget_utilization"] == 0.95
            assert "critically low" in budget_status["message"]

    def test_constitutional_privacy_compliance(self, privacy_engine):
        """Test constitutional privacy compliance validation."""
        compliance_check = privacy_engine.validate_constitutional_privacy_compliance(
            None
        )

        assert "constitutional_hash" in compliance_check
        assert compliance_check["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "privacy_compliant" in compliance_check
        assert "violations" in compliance_check
        assert "recommendations" in compliance_check


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    @patch("main.ConstitutionalTrainer")
    @patch("main.verify_token")
    async def test_complete_training_workflow(
        self, mock_verify_token, mock_trainer_class, client, sample_training_request
    ):
        """Test complete training workflow from API to completion."""
        # Setup mocks
        mock_verify_token.return_value = {
            "user_id": "test-user",
            "groups": ["constitutional-ai-users"],
            "permissions": ["model_training"],
        }

        mock_trainer = AsyncMock()
        mock_trainer.train_with_constitutional_constraints.return_value = {
            "constitutional_compliance_score": 0.96,
            "training_loss": 0.15,
            "privacy_epsilon_used": 6.5,
        }
        mock_trainer_class.return_value = mock_trainer

        # Start training
        response = client.post(
            "/api/v1/train",
            json=sample_training_request,
            headers={"Authorization": "Bearer valid-token"},
        )

        assert response.status_code == 200
        training_id = response.json()["training_id"]

        # Allow background task to complete
        await asyncio.sleep(0.1)

        # Check training status
        with patch("main.session_manager.get_session") as mock_get_session:
            mock_get_session.return_value = {
                "status": "completed",
                "user_id": "test-user",
                "progress": 1.0,
                "compliance_score": 0.96,
                "current_phase": "finished",
            }

            status_response = client.get(
                f"/api/v1/train/{training_id}/status",
                headers={"Authorization": "Bearer valid-token"},
            )

            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["status"] == "completed"
            assert status_data["constitutional_compliance_score"] == 0.96

    @pytest.mark.asyncio
    async def test_constitutional_compliance_enforcement(self):
        """Test that constitutional compliance is enforced throughout the system."""
        config = ConstitutionalConfig(**TEST_CONFIG)

        # Test that all components use the same constitutional hash
        validator = ACGSConstitutionalValidator(config)
        await validator.initialize()

        mock_model = MagicMock()
        privacy_engine = ConstitutionalPrivacyEngine(mock_model, config)

        assert validator.constitutional_hash == CONSTITUTIONAL_HASH
        assert privacy_engine.constitutional_hash == CONSTITUTIONAL_HASH
        assert config.constitutional_hash == CONSTITUTIONAL_HASH

    def test_security_headers_and_cors(self, client):
        """Test security headers and CORS configuration."""
        response = client.get("/health")

        # Check that response doesn't expose sensitive information
        assert "X-Powered-By" not in response.headers
        assert response.status_code == 200

        # Test CORS preflight
        options_response = client.options(
            "/api/v1/train",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )

        # Should handle CORS appropriately
        assert options_response.status_code in [200, 204]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
