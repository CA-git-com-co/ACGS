"""
Test suite for Constitutional Hash Validation in ACGS-1 PGC Service

Tests the enterprise-grade constitutional hash validation implementation,
ensuring 100% constitutional compliance and <5ms validation latency.

# requires: constitutional_hash = "cdd01ef066bc6cf2", pytest framework
# ensures: test_coverage >= 80.0 AND all_tests_pass
# sha256: constitutional_hash_validation_tests_v1.0_acgs1
"""

import asyncio
import time

import pytest

from .core.constitutional_hash_validator import (
    ConstitutionalContext,
    ConstitutionalHashStatus,
    ConstitutionalHashValidator,
    ConstitutionalValidationLevel,
)


class TestConstitutionalHashValidator:
    """Test suite for Constitutional Hash Validator."""

    @pytest.fixture
    def validator(self):
        """Create a constitutional hash validator for testing."""
        return ConstitutionalHashValidator(
            constitutional_hash="cdd01ef066bc6cf2",
            performance_target_ms=5.0,
        )

    @pytest.fixture
    def basic_context(self):
        """Create a basic validation context."""
        return ConstitutionalContext(
            operation_type="test_operation",
            validation_level=ConstitutionalValidationLevel.STANDARD,
        )

    @pytest.fixture
    def policy_data(self):
        """Create sample policy data for testing."""
        return {
            "id": "POL-TEST-001",
            "title": "Test Policy",
            "description": "A test policy for constitutional validation",
            "constitutional_principles": ["CP-001", "CP-002"],
            "constitutional_hash": "cdd01ef066bc6cf2",
            "content": "This is a test policy content that meets constitutional requirements.",
            "governance_context": {
                "scope": "test",
                "target_system": "acgs-1",
            },
        }

    @pytest.mark.asyncio
    async def test_valid_constitutional_hash(self, validator, basic_context):
        """Test validation with correct constitutional hash."""
        result = await validator.validate_constitutional_hash(
            "cdd01ef066bc6cf2", basic_context
        )

        assert result.status == ConstitutionalHashStatus.VALID
        assert result.hash_valid is True
        assert result.compliance_score >= 0.95
        assert len(result.violations) == 0
        assert result.constitutional_hash == "cdd01ef066bc6cf2"

    @pytest.mark.asyncio
    async def test_invalid_constitutional_hash(self, validator, basic_context):
        """Test validation with incorrect constitutional hash."""
        result = await validator.validate_constitutional_hash(
            "invalid_hash_123", basic_context
        )

        assert result.status == ConstitutionalHashStatus.MISMATCH
        assert result.hash_valid is False
        assert result.compliance_score == 0.0
        assert len(result.violations) > 0
        assert "Constitutional hash mismatch" in result.violations[0]

    @pytest.mark.asyncio
    async def test_missing_constitutional_hash_standard_level(self, validator):
        """Test validation with missing hash at standard level."""
        context = ConstitutionalContext(
            operation_type="test_operation",
            validation_level=ConstitutionalValidationLevel.STANDARD,
        )

        result = await validator.validate_constitutional_hash(None, context)

        assert result.status == ConstitutionalHashStatus.VALID
        assert result.hash_valid is False
        assert result.compliance_score >= 0.7  # Should still pass at standard level
        assert len(result.recommendations) > 0

    @pytest.mark.asyncio
    async def test_missing_constitutional_hash_critical_level(self, validator):
        """Test validation with missing hash at critical level."""
        context = ConstitutionalContext(
            operation_type="test_operation",
            validation_level=ConstitutionalValidationLevel.CRITICAL,
        )

        result = await validator.validate_constitutional_hash(None, context)

        assert result.status in [
            ConstitutionalHashStatus.INVALID,
            ConstitutionalHashStatus.MISMATCH,
        ]
        assert result.hash_valid is False
        assert result.compliance_score < 0.7
        assert len(result.violations) > 0

    @pytest.mark.asyncio
    async def test_policy_constitutional_compliance_valid(
        self, validator, basic_context, policy_data
    ):
        """Test policy constitutional compliance with valid data."""
        result = await validator.validate_policy_constitutional_compliance(
            policy_data, basic_context
        )

        assert result.status == ConstitutionalHashStatus.VALID
        assert result.hash_valid is True
        assert result.compliance_score >= 0.8
        assert result.constitutional_hash == "cdd01ef066bc6cf2"

    @pytest.mark.asyncio
    async def test_policy_constitutional_compliance_missing_elements(
        self, validator, basic_context
    ):
        """Test policy constitutional compliance with missing required elements."""
        incomplete_policy = {
            "id": "POL-TEST-002",
            # Missing title, description, constitutional_principles
        }

        result = await validator.validate_policy_constitutional_compliance(
            incomplete_policy, basic_context
        )

        assert result.compliance_score < 1.0
        assert len(result.violations) > 0
        assert any("title" in violation.lower() for violation in result.violations)

    @pytest.mark.asyncio
    async def test_performance_target_compliance(self, validator, basic_context):
        """Test that validation meets performance targets."""
        start_time = time.time()

        result = await validator.validate_constitutional_hash(
            "cdd01ef066bc6cf2", basic_context
        )

        validation_time_ms = (time.time() - start_time) * 1000

        # Should meet the 5ms performance target
        assert (
            validation_time_ms <= validator.performance_target_ms * 2
        )  # Allow some margin for test environment
        assert "validation_time_ms" in result.performance_metrics

    @pytest.mark.asyncio
    async def test_constitutional_state_retrieval(self, validator):
        """Test constitutional state retrieval."""
        state = await validator.get_constitutional_state()

        assert "constitutional_hash" in state
        assert state["constitutional_hash"] == "cdd01ef066bc6cf2"
        assert "validation_status" in state
        assert "timestamp" in state

    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self, validator, basic_context):
        """Test circuit breaker functionality under failure conditions."""
        # Simulate multiple failures to trigger circuit breaker
        validator._circuit_breaker_failures = validator._circuit_breaker_threshold

        result = await validator.validate_constitutional_hash(
            "cdd01ef066bc6cf2", basic_context
        )

        assert result.status == ConstitutionalHashStatus.UNKNOWN
        assert "temporarily unavailable" in result.violations[0].lower()
        assert "circuit_breaker_open" in result.performance_metrics

    def test_integrity_signature_generation(self, validator):
        """Test HMAC integrity signature generation."""
        signature1 = validator._generate_integrity_signature(
            "test_data", "test_operation"
        )
        signature2 = validator._generate_integrity_signature(
            "test_data", "test_operation"
        )
        signature3 = validator._generate_integrity_signature(
            "different_data", "test_operation"
        )

        # Same input should produce same signature
        assert signature1 == signature2
        # Different input should produce different signature
        assert signature1 != signature3
        # Signature should be non-empty
        assert len(signature1) > 0

    @pytest.mark.asyncio
    async def test_enhanced_validation_comprehensive_level(
        self, validator, policy_data
    ):
        """Test enhanced validation at comprehensive level."""
        context = ConstitutionalContext(
            operation_type="policy_creation",
            validation_level=ConstitutionalValidationLevel.COMPREHENSIVE,
        )

        result = await validator.validate_policy_constitutional_compliance(
            policy_data, context
        )

        assert result.validation_level == ConstitutionalValidationLevel.COMPREHENSIVE
        assert result.integrity_signature is not None
        assert len(result.integrity_signature) > 0

    @pytest.mark.asyncio
    async def test_constitutional_hash_format_validation(
        self, validator, basic_context
    ):
        """Test constitutional hash format validation."""
        # Test invalid length
        result1 = await validator.validate_constitutional_hash("short", basic_context)
        assert result1.compliance_score < 1.0

        # Test invalid characters
        result2 = await validator.validate_constitutional_hash(
            "gggggggggggggggg", basic_context
        )
        assert result2.compliance_score < 1.0

        # Test valid format
        result3 = await validator.validate_constitutional_hash(
            "cdd01ef066bc6cf2", basic_context
        )
        assert result3.compliance_score >= 0.95

    @pytest.mark.asyncio
    async def test_cache_key_generation(self, validator, basic_context):
        """Test cache key generation for validation results."""
        key1 = validator._generate_cache_key("test_hash", basic_context)
        key2 = validator._generate_cache_key("test_hash", basic_context)
        key3 = validator._generate_cache_key("different_hash", basic_context)

        # Same input should produce same key
        assert key1 == key2
        # Different input should produce different key
        assert key1 != key3
        # Key should be reasonable length
        assert len(key1) == 16  # Truncated SHA256


class TestConstitutionalValidationIntegration:
    """Integration tests for constitutional validation."""

    @pytest.mark.asyncio
    async def test_end_to_end_policy_validation(self):
        """Test end-to-end policy validation workflow."""
        validator = ConstitutionalHashValidator(
            constitutional_hash="cdd01ef066bc6cf2",
        )

        policy_data = {
            "id": "POL-E2E-001",
            "title": "End-to-End Test Policy",
            "description": "A comprehensive test policy for end-to-end validation",
            "constitutional_principles": ["CP-001", "CP-002", "CP-003"],
            "constitutional_hash": "cdd01ef066bc6cf2",
            "content": "This policy demonstrates comprehensive constitutional compliance.",
            "governance_context": {
                "scope": "global",
                "target_system": "acgs-1",
                "governance_type": "constitutional",
            },
        }

        context = ConstitutionalContext(
            operation_type="policy_creation",
            policy_id=policy_data["id"],
            validation_level=ConstitutionalValidationLevel.COMPREHENSIVE,
        )

        result = await validator.validate_policy_constitutional_compliance(
            policy_data, context
        )

        # Comprehensive validation should pass
        assert result.status == ConstitutionalHashStatus.VALID
        assert result.hash_valid is True
        assert result.compliance_score >= 0.9
        assert result.constitutional_hash == "cdd01ef066bc6cf2"
        assert result.integrity_signature is not None

    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test performance under simulated load."""
        validator = ConstitutionalHashValidator(
            constitutional_hash="cdd01ef066bc6cf2",
            performance_target_ms=5.0,
        )

        context = ConstitutionalContext(
            operation_type="load_test",
            validation_level=ConstitutionalValidationLevel.STANDARD,
        )

        # Simulate multiple concurrent validations
        tasks = []
        for _i in range(10):
            task = validator.validate_constitutional_hash("cdd01ef066bc6cf2", context)
            tasks.append(task)

        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # All validations should succeed
        assert all(
            result.status == ConstitutionalHashStatus.VALID for result in results
        )
        assert all(result.hash_valid for result in results)

        # Average time per validation should be reasonable
        avg_time_ms = (total_time / len(results)) * 1000
        assert (
            avg_time_ms <= validator.performance_target_ms * 2
        )  # Allow margin for test environment


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
