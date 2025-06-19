"""
QEC-SFT Integration Tests

Comprehensive tests for Quantum Error Correction - Semantic Fault Tolerance system
including LSU validation, stabilizer execution, and syndrome diagnosis.
"""

import asyncio
import json
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from services.core.generation_engine.models import (
    LogicalSemanticUnit,
    LSUDomain,
    LSUConstraint,
    ConstraintType,
)
from services.core.see.environment import StabilizerExecutionEnvironment
from services.core.see.models import Stabilizer, StabilizerResult, StabilizerStatus
from services.core.sde.engine import SyndromeDiagnosticEngine
from services.core.sde.models import DiagnosticResult, ErrorSeverity


class TestQECSFTIntegration:
    """Test suite for QEC-SFT integration."""

    @pytest.fixture
    async def stabilizer_env(self):
        """Create a test stabilizer execution environment."""
        env = StabilizerExecutionEnvironment(
            redis_url="redis://localhost:6379/0",
            postgres_url="postgresql://test:test@localhost:5432/test_db",
            constitutional_hash="cdd01ef066bc6cf2",
        )

        # Mock the initialization to avoid actual connections
        with patch.object(env, "initialize") as mock_init:
            mock_init.return_value = None
            await env.initialize()

        return env

    @pytest.fixture
    async def diagnostic_engine(self, stabilizer_env):
        """Create a test syndrome diagnostic engine."""
        engine = SyndromeDiagnosticEngine(
            stabilizer_env=stabilizer_env,
            constitutional_hash="cdd01ef066bc6cf2",
        )

        # Mock the initialization
        with patch.object(engine, "initialize") as mock_init:
            mock_init.return_value = None
            await engine.initialize()

        return engine

    @pytest.fixture
    def sample_lsu(self):
        """Create a sample Logical Semantic Unit for testing."""
        return LogicalSemanticUnit(
            id="LSU-123456",
            description="Test policy for democratic governance validation",
            domain=LSUDomain.POLICY,
            constraints=[
                LSUConstraint(
                    type=ConstraintType.SECURITY,
                    value="high",
                    description="High security requirement",
                ),
                LSUConstraint(
                    type=ConstraintType.PERFORMANCE,
                    value="<500ms",
                    description="Response time requirement",
                ),
            ],
            content={
                "title": "Test Democratic Policy",
                "description": "A test policy for democratic governance",
                "stakeholders": ["citizens", "government"],
                "constitutional_principles": ["transparency", "accountability"],
            },
            constitutional_hash="cdd01ef066bc6cf2",
            compliance_validated=True,
        )

    @pytest.fixture
    def sample_stabilizer(self):
        """Create a sample stabilizer for testing."""
        return Stabilizer(
            id="STAB-TEST001",
            name="Test Constitutional Stabilizer",
            description="Test stabilizer for constitutional compliance",
            image="test/constitutional-stabilizer:latest",
            domains=["policy", "governance"],
            timeout=30,
            config={
                "memory_limit": "256MB",
                "cpu_limit": 0.5,
                "environment_variables": {"COMPLIANCE_THRESHOLD": "0.8"},
            },
            constitutional_compliance={
                "required_hash": "cdd01ef066bc6cf2",
                "compliance_checks": ["transparency", "accountability"],
                "minimum_compliance_score": 0.8,
            },
        )

    @pytest.mark.asyncio
    async def test_lsu_creation_and_validation(self, sample_lsu):
        """Test LSU creation and basic validation."""
        # Test LSU properties
        assert sample_lsu.id == "LSU-123456"
        assert sample_lsu.domain == LSUDomain.POLICY
        assert len(sample_lsu.constraints) == 2
        assert sample_lsu.constitutional_hash == "cdd01ef066bc6cf2"

        # Test constraint validation
        assert sample_lsu.validate_constraints()

        # Test constitutional compliance
        assert sample_lsu.compliance_validated
        assert sample_lsu.is_valid()

    @pytest.mark.asyncio
    async def test_stabilizer_registry_loading(self, stabilizer_env, sample_stabilizer):
        """Test stabilizer registry loading and management."""
        # Add stabilizer to registry
        stabilizer_env.stabilizer_registry[sample_stabilizer.id] = sample_stabilizer

        # Test registry access
        assert sample_stabilizer.id in stabilizer_env.stabilizer_registry
        retrieved_stabilizer = stabilizer_env.stabilizer_registry[sample_stabilizer.id]
        assert retrieved_stabilizer.name == "Test Constitutional Stabilizer"
        assert retrieved_stabilizer.is_applicable_to_domain("policy")
        assert not retrieved_stabilizer.is_applicable_to_domain("security")

    @pytest.mark.asyncio
    async def test_stabilizer_execution_mock(self, stabilizer_env, sample_lsu, sample_stabilizer):
        """Test stabilizer execution with mocked container."""
        # Add stabilizer to registry
        stabilizer_env.stabilizer_registry[sample_stabilizer.id] = sample_stabilizer

        # Mock the container execution
        mock_result = {
            "success": True,
            "constitutional_compliance_score": 0.9,
            "validation_results": {
                "transparency": True,
                "accountability": True,
            },
            "execution_time_ms": 250,
        }

        with patch.object(stabilizer_env, "_run_stabilizer_container") as mock_run:
            mock_run.return_value = mock_result

            # Execute stabilizer
            result = await stabilizer_env.execute_stabilizer(sample_stabilizer.id, sample_lsu)

            # Verify results
            assert result.status == StabilizerStatus.COMPLETED
            assert result.execution_time_ms > 0
            assert result.result_data == mock_result
            assert result.constitutional_hash == "cdd01ef066bc6cf2"

    @pytest.mark.asyncio
    async def test_syndrome_diagnosis(self, diagnostic_engine, sample_lsu):
        """Test syndrome diagnosis with stabilizer results."""
        # Create mock stabilizer results
        stabilizer_results = [
            StabilizerResult(
                execution_id="test_exec_1",
                status=StabilizerStatus.COMPLETED,
                execution_time_ms=200,
                compliance_score=0.9,
                compliance_validated=True,
                constitutional_hash="cdd01ef066bc6cf2",
                metadata={"stabilizer_id": "STAB-TEST001"},
            ),
            StabilizerResult(
                execution_id="test_exec_2",
                status=StabilizerStatus.FAILED,
                execution_time_ms=5500,  # Exceeds threshold
                compliance_score=0.6,
                compliance_validated=False,
                constitutional_hash="cdd01ef066bc6cf2",
                metadata={"stabilizer_id": "STAB-TEST002"},
            ),
        ]

        # Perform diagnosis
        diagnostic_result = await diagnostic_engine.diagnose_lsu_stabilizer_results(
            sample_lsu, stabilizer_results, include_recommendations=True
        )

        # Verify diagnostic results
        assert diagnostic_result.target_system == f"LSU-{sample_lsu.id}"
        assert diagnostic_result.error_count > 0  # Should detect errors from failed stabilizer
        assert diagnostic_result.critical_error_count > 0  # Constitutional violation
        assert len(diagnostic_result.recommendations) > 0
        assert not diagnostic_result.is_system_healthy()
        assert diagnostic_result.requires_immediate_attention()

    @pytest.mark.asyncio
    async def test_end_to_end_qec_sft_workflow(
        self, stabilizer_env, diagnostic_engine, sample_lsu, sample_stabilizer
    ):
        """Test complete QEC-SFT workflow from LSU to diagnosis."""
        # Setup
        stabilizer_env.stabilizer_registry[sample_stabilizer.id] = sample_stabilizer

        # Mock successful stabilizer execution
        mock_result = {
            "success": True,
            "constitutional_compliance_score": 0.95,
            "validation_results": {"transparency": True, "accountability": True},
            "execution_time_ms": 300,
        }

        with patch.object(stabilizer_env, "_run_stabilizer_container") as mock_run:
            mock_run.return_value = mock_result

            # Step 1: Execute all stabilizers
            stabilizer_results = await stabilizer_env.execute_all_stabilizers(sample_lsu)

            # Step 2: Perform syndrome diagnosis
            diagnostic_result = await diagnostic_engine.diagnose_lsu_stabilizer_results(
                sample_lsu, stabilizer_results, include_recommendations=True
            )

            # Verify end-to-end results
            assert len(stabilizer_results) == 1  # One applicable stabilizer
            assert stabilizer_results[0].status == StabilizerStatus.COMPLETED
            assert diagnostic_result.is_system_healthy()
            assert diagnostic_result.constitutional_compliance_score >= 0.8

    @pytest.mark.asyncio
    async def test_error_correction_and_recovery(self, diagnostic_engine, sample_lsu):
        """Test error correction and recovery recommendations."""
        # Create stabilizer results with various error conditions
        stabilizer_results = [
            StabilizerResult(
                execution_id="test_exec_perf",
                status=StabilizerStatus.COMPLETED,
                execution_time_ms=6000,  # Performance issue
                errors_detected=2,
                errors_corrected=1,  # Partial correction
                compliance_score=0.7,
                compliance_validated=True,
                constitutional_hash="cdd01ef066bc6cf2",
                metadata={"stabilizer_id": "STAB-PERF001"},
            ),
            StabilizerResult(
                execution_id="test_exec_const",
                status=StabilizerStatus.FAILED,
                compliance_score=0.4,
                compliance_validated=False,
                constitutional_hash="cdd01ef066bc6cf2",
                metadata={"stabilizer_id": "STAB-CONST001"},
            ),
        ]

        # Perform diagnosis
        diagnostic_result = await diagnostic_engine.diagnose_lsu_stabilizer_results(
            sample_lsu, stabilizer_results, include_recommendations=True
        )

        # Verify error detection and recommendations
        assert diagnostic_result.error_count >= 2
        assert len(diagnostic_result.recommendations) > 0

        # Check for specific recommendation types
        recommendation_strategies = [
            rec.strategy.value for rec in diagnostic_result.recommendations
        ]
        assert (
            "manual_intervention" in recommendation_strategies
            or "automatic_retry" in recommendation_strategies
        )

        # Verify auto-executable recommendations
        auto_recs = [rec for rec in diagnostic_result.recommendations if rec.is_safe_to_execute()]
        assert diagnostic_result.auto_executable_recommendations == len(auto_recs)

    @pytest.mark.asyncio
    async def test_constitutional_compliance_validation(self, sample_lsu):
        """Test constitutional compliance validation across the system."""
        # Test valid constitutional hash
        assert sample_lsu.constitutional_hash == "cdd01ef066bc6cf2"
        assert sample_lsu.compliance_validated

        # Test invalid constitutional hash
        invalid_lsu = LogicalSemanticUnit(
            id="LSU-999999",
            description="Invalid LSU with wrong constitutional hash",
            domain=LSUDomain.POLICY,
            constraints=[],
            constitutional_hash="invalid_hash",
            compliance_validated=False,
        )

        assert not invalid_lsu.is_valid()
        assert invalid_lsu.constitutional_hash != "cdd01ef066bc6cf2"

    def test_stabilizer_configuration_validation(self, sample_stabilizer):
        """Test stabilizer configuration and validation."""
        # Test memory limit parsing
        assert sample_stabilizer.get_memory_limit_mb() == 256

        # Test CPU limit
        assert sample_stabilizer.get_cpu_limit() == 0.5

        # Test constitutional compliance validation
        assert sample_stabilizer.validate_constitutional_compliance("cdd01ef066bc6cf2")
        assert not sample_stabilizer.validate_constitutional_compliance("invalid_hash")

        # Test domain applicability
        assert sample_stabilizer.is_applicable_to_domain("policy")
        assert sample_stabilizer.is_applicable_to_domain("governance")
        assert not sample_stabilizer.is_applicable_to_domain("security")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
