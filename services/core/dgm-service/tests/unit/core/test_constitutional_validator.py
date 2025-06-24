"""
Unit tests for Constitutional Validator.

Comprehensive test suite for constitutional compliance validation,
governance principle enforcement, and safety constraint checking.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from dgm_service.core.constitutional_validator import ConstitutionalValidator
from dgm_service.models.compliance import ComplianceLevel, ConstitutionalComplianceLog


@pytest.mark.unit
@pytest.mark.constitutional
class TestConstitutionalValidator:
    """Test suite for Constitutional Validator."""

    @pytest.fixture
    def validator(self):
        """Create constitutional validator instance."""
        with patch("dgm_service.core.constitutional_validator.ACGSServiceClient"):
            validator = ConstitutionalValidator()
            validator.ac_service_client = AsyncMock()
            return validator

    @pytest.fixture
    def sample_proposal(self):
        """Sample improvement proposal for testing."""
        return {
            "strategy": "performance_optimization",
            "target_services": ["gs-service"],
            "proposed_changes": {
                "type": "algorithm_optimization",
                "parameters": {"learning_rate": 0.01},
                "affected_components": ["neural_network", "optimizer"],
            },
            "expected_improvement": 0.15,
            "risk_assessment": {"risk_level": "low", "confidence": 0.85},
        }

    @pytest.fixture
    def sample_execution_result(self):
        """Sample execution result for testing."""
        return {
            "improvement_id": str(uuid4()),
            "strategy": "performance_optimization",
            "execution_time": 45.2,
            "changes_applied": ["updated_learning_rate", "optimized_batch_size"],
            "performance_metrics": {
                "before": {"response_time": 150.0},
                "after": {"response_time": 125.0},
            },
        }

    async def test_validate_proposal_compliant(self, validator, sample_proposal):
        """Test validation of compliant proposal."""
        # Mock AC service response
        validator.ac_service_client.validate_governance_compliance.return_value = {
            "is_compliant": True,
            "compliance_score": 0.95,
            "violations": [],
            "recommendations": [],
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

        result = await validator.validate_proposal(sample_proposal)

        assert result["is_compliant"] is True
        assert result["compliance_score"] == 0.95
        assert len(result["violations"]) == 0
        assert "constitutional_hash" in result

        # Verify AC service was called
        validator.ac_service_client.validate_governance_compliance.assert_called_once()

    async def test_validate_proposal_non_compliant(self, validator, sample_proposal):
        """Test validation of non-compliant proposal."""
        # Mock AC service response with violations
        validator.ac_service_client.validate_governance_compliance.return_value = {
            "is_compliant": False,
            "compliance_score": 0.45,
            "violations": [
                {
                    "type": "unsafe_modification",
                    "severity": "high",
                    "description": "Proposed changes may affect system stability",
                    "affected_principles": ["safety", "stability"],
                }
            ],
            "recommendations": [
                "Add safety checks before implementation",
                "Implement gradual rollout strategy",
            ],
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

        result = await validator.validate_proposal(sample_proposal)

        assert result["is_compliant"] is False
        assert result["compliance_score"] == 0.45
        assert len(result["violations"]) == 1
        assert len(result["recommendations"]) == 2

        violation = result["violations"][0]
        assert violation["type"] == "unsafe_modification"
        assert violation["severity"] == "high"

    async def test_validate_execution_success(self, validator, sample_execution_result):
        """Test validation of successful execution."""
        # Mock AC service response
        validator.ac_service_client.validate_execution_compliance.return_value = {
            "is_compliant": True,
            "compliance_score": 0.92,
            "constitutional_hash": "cdd01ef066bc6cf2",
            "audit_trail": {
                "validation_timestamp": datetime.utcnow().isoformat(),
                "validator_version": "1.0.0",
                "checks_performed": 15,
            },
        }

        result = await validator.validate_execution(sample_execution_result)

        assert result["is_compliant"] is True
        assert result["compliance_score"] == 0.92
        assert "constitutional_hash" in result
        assert "audit_trail" in result

    async def test_validate_execution_compliance_failure(self, validator, sample_execution_result):
        """Test validation of execution with compliance failure."""
        # Mock AC service response with compliance failure
        validator.ac_service_client.validate_execution_compliance.return_value = {
            "is_compliant": False,
            "compliance_score": 0.35,
            "constitutional_hash": "cdd01ef066bc6cf2",
            "violations": [
                {
                    "type": "unauthorized_change",
                    "severity": "critical",
                    "description": "Execution modified protected system components",
                }
            ],
        }

        result = await validator.validate_execution(sample_execution_result)

        assert result["is_compliant"] is False
        assert result["compliance_score"] == 0.35
        assert len(result["violations"]) == 1

    async def test_check_safety_constraints_pass(self, validator):
        """Test safety constraints checking - passing case."""
        proposal = {
            "strategy": "safe_optimization",
            "risk_assessment": {"risk_level": "low", "confidence": 0.90},
            "target_services": ["non-critical-service"],
        }

        result = await validator.check_safety_constraints(proposal)

        assert result["constraints_satisfied"] is True
        assert result["safety_score"] >= 0.8
        assert len(result["constraint_violations"]) == 0

    async def test_check_safety_constraints_fail(self, validator):
        """Test safety constraints checking - failing case."""
        proposal = {
            "strategy": "risky_modification",
            "risk_assessment": {"risk_level": "critical", "confidence": 0.95},
            "target_services": ["critical-service", "auth-service"],
        }

        result = await validator.check_safety_constraints(proposal)

        assert result["constraints_satisfied"] is False
        assert result["safety_score"] < 0.5
        assert len(result["constraint_violations"]) > 0

        # Check specific violations
        violations = result["constraint_violations"]
        violation_types = [v["type"] for v in violations]
        assert "high_risk_operation" in violation_types

    async def test_validate_governance_principles(self, validator, sample_proposal):
        """Test governance principles validation."""
        # Mock governance principles check
        with patch.object(validator, "_check_democratic_principles") as mock_democratic:
            mock_democratic.return_value = {"compliant": True, "score": 0.90, "issues": []}

            with patch.object(validator, "_check_transparency_requirements") as mock_transparency:
                mock_transparency.return_value = {"compliant": True, "score": 0.95, "issues": []}

                with patch.object(
                    validator, "_check_accountability_measures"
                ) as mock_accountability:
                    mock_accountability.return_value = {
                        "compliant": True,
                        "score": 0.88,
                        "issues": [],
                    }

                    result = await validator.validate_governance_principles(sample_proposal)

        assert result["overall_compliance"] is True
        assert result["overall_score"] >= 0.85
        assert "democratic_principles" in result
        assert "transparency_requirements" in result
        assert "accountability_measures" in result

    async def test_log_compliance_validation(self, validator):
        """Test compliance validation logging."""
        improvement_id = str(uuid4())
        validation_result = {
            "is_compliant": True,
            "compliance_score": 0.95,
            "constitutional_hash": "cdd01ef066bc6cf2",
            "violations": [],
            "recommendations": [],
        }

        with patch.object(validator, "_store_compliance_log") as mock_store:
            await validator.log_compliance_validation(improvement_id, "proposal", validation_result)

            mock_store.assert_called_once()
            call_args = mock_store.call_args[0]
            assert call_args[0] == improvement_id
            assert call_args[1] == "proposal"
            assert call_args[2] == validation_result

    async def test_get_compliance_history(self, validator):
        """Test retrieval of compliance history."""
        improvement_id = str(uuid4())

        # Mock database query
        with patch.object(validator, "_query_compliance_logs") as mock_query:
            mock_query.return_value = [
                {
                    "id": str(uuid4()),
                    "improvement_id": improvement_id,
                    "validation_type": "proposal",
                    "compliance_level": "HIGH",
                    "compliance_score": 0.95,
                    "created_at": datetime.utcnow(),
                },
                {
                    "id": str(uuid4()),
                    "improvement_id": improvement_id,
                    "validation_type": "execution",
                    "compliance_level": "HIGH",
                    "compliance_score": 0.92,
                    "created_at": datetime.utcnow(),
                },
            ]

            history = await validator.get_compliance_history(improvement_id)

        assert len(history) == 2
        assert all(log["improvement_id"] == improvement_id for log in history)
        assert any(log["validation_type"] == "proposal" for log in history)
        assert any(log["validation_type"] == "execution" for log in history)

    async def test_constitutional_hash_validation(self, validator):
        """Test constitutional hash validation."""
        current_hash = "cdd01ef066bc6cf2"

        # Test valid hash
        assert await validator.validate_constitutional_hash(current_hash) is True

        # Test invalid hash
        invalid_hash = "invalid_hash_123"
        assert await validator.validate_constitutional_hash(invalid_hash) is False

    async def test_compliance_score_calculation(self, validator):
        """Test compliance score calculation."""
        validation_results = {
            "safety_score": 0.90,
            "governance_score": 0.85,
            "transparency_score": 0.95,
            "accountability_score": 0.88,
        }

        overall_score = await validator.calculate_compliance_score(validation_results)

        assert 0.0 <= overall_score <= 1.0
        assert overall_score == pytest.approx(0.895, rel=1e-2)  # Weighted average

    async def test_violation_severity_assessment(self, validator):
        """Test violation severity assessment."""
        violations = [
            {
                "type": "minor_deviation",
                "description": "Minor formatting issue",
                "affected_principles": ["transparency"],
            },
            {
                "type": "safety_concern",
                "description": "Potential system instability",
                "affected_principles": ["safety", "stability"],
            },
            {
                "type": "unauthorized_access",
                "description": "Attempted access to restricted resources",
                "affected_principles": ["security", "accountability"],
            },
        ]

        assessed_violations = await validator.assess_violation_severity(violations)

        assert len(assessed_violations) == 3
        for violation in assessed_violations:
            assert "severity" in violation
            assert violation["severity"] in ["low", "medium", "high", "critical"]

        # Check that safety and security violations have higher severity
        safety_violation = next(v for v in assessed_violations if v["type"] == "safety_concern")
        security_violation = next(
            v for v in assessed_violations if v["type"] == "unauthorized_access"
        )

        assert safety_violation["severity"] in ["high", "critical"]
        assert security_violation["severity"] in ["high", "critical"]

    async def test_recommendation_generation(self, validator):
        """Test recommendation generation for violations."""
        violations = [
            {"type": "unsafe_modification", "severity": "high", "affected_principles": ["safety"]},
            {
                "type": "insufficient_transparency",
                "severity": "medium",
                "affected_principles": ["transparency"],
            },
        ]

        recommendations = await validator.generate_recommendations(violations)

        assert len(recommendations) >= len(violations)
        assert all("action" in rec for rec in recommendations)
        assert all("rationale" in rec for rec in recommendations)

        # Check for safety-specific recommendations
        safety_recs = [r for r in recommendations if "safety" in r["rationale"].lower()]
        assert len(safety_recs) > 0

    async def test_ac_service_integration_failure(self, validator, sample_proposal):
        """Test handling of AC service integration failure."""
        # Mock AC service failure
        validator.ac_service_client.validate_governance_compliance.side_effect = Exception(
            "AC Service unavailable"
        )

        # Should fall back to local validation
        result = await validator.validate_proposal(sample_proposal)

        # Should still return a result, but with lower confidence
        assert "is_compliant" in result
        assert "compliance_score" in result
        assert result["compliance_score"] < 0.8  # Lower confidence due to service failure

    async def test_batch_validation(self, validator):
        """Test batch validation of multiple proposals."""
        proposals = [
            {
                "id": str(uuid4()),
                "strategy": "performance_optimization",
                "risk_assessment": {"risk_level": "low"},
            },
            {
                "id": str(uuid4()),
                "strategy": "security_enhancement",
                "risk_assessment": {"risk_level": "medium"},
            },
            {
                "id": str(uuid4()),
                "strategy": "experimental_feature",
                "risk_assessment": {"risk_level": "high"},
            },
        ]

        # Mock AC service responses
        validator.ac_service_client.validate_governance_compliance.side_effect = [
            {"is_compliant": True, "compliance_score": 0.95},
            {"is_compliant": True, "compliance_score": 0.88},
            {"is_compliant": False, "compliance_score": 0.45},
        ]

        results = await validator.batch_validate_proposals(proposals)

        assert len(results) == 3
        assert results[0]["is_compliant"] is True
        assert results[1]["is_compliant"] is True
        assert results[2]["is_compliant"] is False

    @pytest.mark.slow
    async def test_performance_under_load(self, validator):
        """Test validator performance under load."""
        import asyncio
        import time

        # Create multiple concurrent validation requests
        proposals = [
            {"strategy": f"strategy_{i}", "risk_assessment": {"risk_level": "low"}}
            for i in range(50)
        ]

        # Mock AC service
        validator.ac_service_client.validate_governance_compliance.return_value = {
            "is_compliant": True,
            "compliance_score": 0.90,
        }

        start_time = time.time()

        tasks = [validator.validate_proposal(proposal) for proposal in proposals]
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        execution_time = end_time - start_time

        # Verify all validations completed
        assert len(results) == 50
        assert all(result["is_compliant"] for result in results)

        # Performance assertion (should handle 50 validations in reasonable time)
        assert execution_time < 10.0  # Should complete within 10 seconds
