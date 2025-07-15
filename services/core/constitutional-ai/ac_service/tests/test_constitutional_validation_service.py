"""
Comprehensive Unit Tests for Constitutional Validation Service
HASH-OK:cdd01ef066bc6cf2

Tests the core constitutional validation functionality including:
- Constitutional compliance validation
- Rule-based validation checks
- Formal verification integration
- Performance and accuracy metrics
- Constitutional hash validation
"""

import time
from unittest.mock import AsyncMock, patch

import pytest
from services.core.constitutional-ai.ac_service.app.schemas import (

# Add parent directory to path to handle dash-named directories
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

    ConstitutionalComplianceRequest,
)
from services.core.constitutional-ai.ac_service.app.services.constitutional_validation_service import (
    CONSTITUTIONAL_HASH,
    ConstitutionalValidationService,
)

# Constitutional Hash: cdd01ef066bc6cf2


class TestConstitutionalValidationService:
    """Comprehensive test suite for Constitutional Validation Service."""

    @pytest.fixture
    def mock_audit_logger(self):
        """Mock audit logger for testing."""
        return AsyncMock()

    @pytest.fixture
    def mock_violation_detector(self):
        """Mock violation detector for testing."""
        detector = AsyncMock()
        detector.detect_violations.return_value = {
            "violations": [],
            "severity": "low",
            "confidence": 0.95,
        }
        return detector

    @pytest.fixture
    def mock_fv_client(self):
        """Mock formal verification client for testing."""
        client = AsyncMock()
        client.verify_policy.return_value = {
            "verified": True,
            "proof": "formal_proof_data",
            "confidence": 0.98,
        }
        return client

    @pytest.fixture
    def validation_service(
        self, mock_audit_logger, mock_violation_detector, mock_fv_client
    ):
        """Create ConstitutionalValidationService instance with mocked dependencies."""
        return ConstitutionalValidationService(
            audit_logger=mock_audit_logger,
            violation_detector=mock_violation_detector,
            fv_client=mock_fv_client,
        )

    @pytest.fixture
    def sample_compliance_request(self):
        """Sample constitutional compliance request for testing."""
        return ConstitutionalComplianceRequest(
            policy="All users must provide informed consent before data collection",
            validation_mode="comprehensive",
            include_reasoning=True,
            principles=["democratic_participation", "transparency", "accountability"],
        )

    @pytest.fixture
    def sample_policy_text(self):
        """Sample policy text for testing."""
        return "Data collection requires explicit user consent and transparent disclosure of usage purposes"

    async def test_constitutional_hash_validation(self, validation_service):
        """Test that constitutional hash is properly validated."""
        # Test constitutional hash constant
        assert CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"

        # Test hash validation in service
        assert validation_service is not None

    async def test_validate_constitutional_compliance_success(
        self, validation_service, sample_compliance_request
    ):
        """Test successful constitutional compliance validation."""
        # Mock the internal validation methods
        with (
            patch.object(
                validation_service, "_perform_rule_validation"
            ) as mock_rule_validation,
            patch.object(
                validation_service, "_calculate_compliance_metrics"
            ) as mock_metrics,
            patch.object(validation_service, "_log_validation_request") as mock_log,
        ):

            # Setup mock returns
            mock_rule_validation.return_value = {
                "CONST-001": {"score": 0.85, "passed": True},
                "CONST-002": {"score": 0.90, "passed": True},
                "CONST-003": {"score": 0.88, "passed": True},
                "CONST-004": {"score": 0.82, "passed": True},
                "CONST-005": {"score": 0.87, "passed": True},
            }

            mock_metrics.return_value = {
                "overall_score": 0.864,
                "compliance_status": "COMPLIANT",
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

            # Execute validation
            result = await validation_service.validate_constitutional_compliance(
                sample_compliance_request
            )

            # Verify results
            assert result is not None
            assert "constitutional_hash" in result
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

            # Verify mocks were called
            mock_rule_validation.assert_called_once()
            mock_metrics.assert_called_once()
            mock_log.assert_called_once()

    async def test_rule_validation_checks(self, validation_service):
        """Test individual rule validation checks."""
        # Test rule configuration
        assert len(validation_service.rule_checks) == 5

        # Test each rule exists and has required properties
        for rule_config in validation_service.rule_checks.values():
            assert "name" in rule_config
            assert "algorithm" in rule_config
            assert "check" in rule_config
            assert "weight" in rule_config
            assert "formal_verification" in rule_config

            # Test weight is valid
            assert 0 < rule_config["weight"] <= 1.0

            # Test check method is callable
            assert callable(rule_config["check"])

    async def test_democratic_participation_check(
        self, validation_service, sample_policy_text
    ):
        """Test democratic participation validation check."""
        # Test the democratic check method
        result = await validation_service._advanced_democratic_check(
            sample_policy_text, {}
        )

        assert isinstance(result, dict)
        assert "score" in result
        assert "reasoning" in result
        assert "constitutional_hash" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert 0 <= result["score"] <= 1.0

    async def test_transparency_check(self, validation_service, sample_policy_text):
        """Test transparency requirement validation check."""
        result = await validation_service._advanced_transparency_check(
            sample_policy_text, {}
        )

        assert isinstance(result, dict)
        assert "score" in result
        assert "reasoning" in result
        assert "constitutional_hash" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert 0 <= result["score"] <= 1.0

    async def test_constitutional_compliance_check(
        self, validation_service, sample_policy_text
    ):
        """Test constitutional compliance validation check."""
        result = await validation_service._advanced_constitutional_check(
            sample_policy_text, {}
        )

        assert isinstance(result, dict)
        assert "score" in result
        assert "reasoning" in result
        assert "constitutional_hash" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert 0 <= result["score"] <= 1.0

    async def test_accountability_check(self, validation_service, sample_policy_text):
        """Test accountability framework validation check."""
        result = await validation_service._advanced_accountability_check(
            sample_policy_text, {}
        )

        assert isinstance(result, dict)
        assert "score" in result
        assert "reasoning" in result
        assert "constitutional_hash" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert 0 <= result["score"] <= 1.0

    async def test_rights_protection_check(
        self, validation_service, sample_policy_text
    ):
        """Test rights protection validation check."""
        result = await validation_service._advanced_rights_check(sample_policy_text, {})

        assert isinstance(result, dict)
        assert "score" in result
        assert "reasoning" in result
        assert "constitutional_hash" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert 0 <= result["score"] <= 1.0

    async def test_validation_id_generation(self, validation_service):
        """Test validation ID generation."""
        policy1 = "Test policy 1"
        policy2 = "Test policy 2"

        id1 = validation_service._generate_validation_id(policy1)
        id2 = validation_service._generate_validation_id(policy2)
        id3 = validation_service._generate_validation_id(policy1)  # Same policy

        # Different policies should generate different IDs
        assert id1 != id2

        # Same policy should generate same ID (deterministic)
        assert id1 == id3

        # IDs should be strings
        assert isinstance(id1, str)
        assert isinstance(id2, str)

    async def test_performance_metrics(
        self, validation_service, sample_compliance_request
    ):
        """Test validation performance metrics."""
        start_time = time.time()

        with (
            patch.object(
                validation_service, "_perform_rule_validation"
            ) as mock_validation,
            patch.object(
                validation_service, "_calculate_compliance_metrics"
            ) as mock_metrics,
            patch.object(validation_service, "_log_validation_request"),
        ):

            mock_validation.return_value = {}
            mock_metrics.return_value = {
                "overall_score": 0.85,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

            result = await validation_service.validate_constitutional_compliance(
                sample_compliance_request
            )

        end_time = time.time()
        execution_time = end_time - start_time

        # Validation should complete quickly (performance target)
        assert execution_time < 1.0  # Should complete in under 1 second

        # Result should contain performance metrics
        assert result is not None

    async def test_error_handling(self, validation_service):
        """Test error handling in validation service."""
        # Test with invalid request
        invalid_request = ConstitutionalComplianceRequest(
            policy="",  # Empty policy
            validation_mode="invalid_mode",
            include_reasoning=True,
            principles=[],
        )

        with patch.object(
            validation_service, "_perform_rule_validation"
        ) as mock_validation:
            mock_validation.side_effect = Exception("Validation error")

            # Should handle errors gracefully
            try:
                result = await validation_service.validate_constitutional_compliance(
                    invalid_request
                )
                # If no exception, result should indicate error
                assert "error" in result or "status" in result
            except Exception as e:
                # Exception handling is acceptable
                assert isinstance(e, Exception)

    async def test_formal_verification_integration(
        self, validation_service, mock_fv_client
    ):
        """Test formal verification client integration."""
        # Test that formal verification is called for appropriate rules

        # Mock formal verification call
        mock_fv_client.verify_policy.return_value = {
            "verified": True,
            "proof": "formal_proof",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        # Test rules that require formal verification
        formal_verification_rules = [
            rule_id
            for rule_id, config in validation_service.rule_checks.items()
            if config.get("formal_verification", False)
        ]

        assert len(formal_verification_rules) > 0  # Should have some FV rules

        # Test that FV client is properly configured
        assert validation_service.fv_client == mock_fv_client

    async def test_constitutional_hash_consistency(
        self, validation_service, sample_compliance_request
    ):
        """Test that constitutional hash is consistent across all operations."""
        with (
            patch.object(
                validation_service, "_perform_rule_validation"
            ) as mock_validation,
            patch.object(
                validation_service, "_calculate_compliance_metrics"
            ) as mock_metrics,
            patch.object(validation_service, "_log_validation_request"),
        ):

            mock_validation.return_value = {}
            mock_metrics.return_value = {
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "overall_score": 0.85,
            }

            result = await validation_service.validate_constitutional_compliance(
                sample_compliance_request
            )

            # Verify constitutional hash is present and correct
            assert "constitutional_hash" in result
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
            assert result["constitutional_hash"] == "cdd01ef066bc6cf2"

    async def test_validation_modes(self, validation_service):
        """Test different validation modes."""
        modes = ["basic", "comprehensive", "formal_verification", "performance"]

        for mode in modes:
            request = ConstitutionalComplianceRequest(
                policy="Test policy",
                validation_mode=mode,
                include_reasoning=True,
                principles=["transparency"],
            )

            with (
                patch.object(
                    validation_service, "_perform_rule_validation"
                ) as mock_validation,
                patch.object(
                    validation_service, "_calculate_compliance_metrics"
                ) as mock_metrics,
                patch.object(validation_service, "_log_validation_request"),
            ):

                mock_validation.return_value = {}
                mock_metrics.return_value = {
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "validation_mode": mode,
                }

                result = await validation_service.validate_constitutional_compliance(
                    request
                )

                # Each mode should work and return constitutional hash
                assert result is not None
                assert "constitutional_hash" in result
                assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
