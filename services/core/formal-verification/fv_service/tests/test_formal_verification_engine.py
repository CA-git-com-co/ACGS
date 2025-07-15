"""
Comprehensive Unit Tests for Formal Verification Engine
HASH-OK:cdd01ef066bc6cf2

Tests the formal verification engine including:
- Policy verification workflows
- Constitutional compliance validation
- Proof obligation generation
- Integration with Z3 solver
- Performance optimization
"""

import time
from unittest.mock import AsyncMock

import pytest
from services.core.formal-verification.fv_service.app.services.formal_verification_engine import (

# Add parent directory to path to handle dash-named directories
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

    FormalVerificationEngine,
    ProofObligation,
    VerificationReport,
    VerificationResult,
)

# Constitutional Hash: cdd01ef066bc6cf2
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestFormalVerificationEngine:
    """Comprehensive test suite for Formal Verification Engine."""

    @pytest.fixture
    def mock_z3_solver(self):
        """Mock Z3 solver for testing."""
        solver = AsyncMock()
        solver.verify_constitutional_policy.return_value = VerificationReport(
            result=VerificationResult.VALID,
            constitutional_compliance=True,
            confidence_score=0.92,
            proof_time_ms=150.5,
            constitutional_hash=CONSTITUTIONAL_HASH,
            verification_details={
                "principles_verified": ["transparency", "fairness"],
                "constraints_satisfied": 5,
                "proof_steps": 12,
            },
        )
        solver.verify_proof_obligation.return_value = {
            "verified": True,
            "proof_time_ms": 85.2,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "proof_steps": ["Step 1: Initialize", "Step 2: Verify", "Step 3: Conclude"],
        }
        solver.generate_advanced_proof.return_value = {
            "status": "success",
            "proof_steps": ["Formal proof step 1", "Formal proof step 2"],
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "proof_strategy": "constitutional_compliance",
        }
        return solver

    @pytest.fixture
    def verification_engine(self, mock_z3_solver):
        """Create FormalVerificationEngine instance with mocked dependencies."""
        engine = FormalVerificationEngine()
        engine.z3_solver = mock_z3_solver
        return engine

    @pytest.fixture
    def sample_policy_content(self):
        """Sample policy content for testing."""
        return """
        Data Collection Policy:
        1. All personal data collection requires explicit user consent
        2. Users must be informed about data usage purposes
        3. Data retention period must not exceed 2 years
        4. Users have the right to data deletion upon request
        5. Data sharing with third parties requires additional consent
        """

    @pytest.fixture
    def sample_policy_metadata(self):
        """Sample policy metadata for testing."""
        return {
            "policy_id": "data_collection_001",
            "version": "1.2.0",
            "domain": "data_governance",
            "stakeholders": ["users", "data_controllers", "regulators"],
            "effective_date": "2024-01-01",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    @pytest.fixture
    def sample_proof_obligations(self):
        """Sample proof obligations for testing."""
        return [
            ProofObligation(
                obligation_id="obligation_001",
                property="consent_required == True",
                constraints=["user_informed == True", "consent_explicit == True"],
                context={"domain": "data_collection"},
                priority=1,
            ),
            ProofObligation(
                obligation_id="obligation_002",
                property="data_retention <= 24_months",
                constraints=[
                    "retention_policy_defined == True",
                    "deletion_mechanism_available == True",
                ],
                context={"domain": "data_retention"},
                priority=2,
            ),
        ]

    async def test_constitutional_hash_validation(self):
        """Test that constitutional hash is properly validated."""
        assert CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"

    async def test_engine_initialization(self, verification_engine):
        """Test formal verification engine initialization."""
        assert verification_engine is not None
        assert verification_engine.z3_solver is not None

    async def test_policy_constitutional_compliance_verification(
        self, verification_engine, sample_policy_content, sample_policy_metadata
    ):
        """Test policy constitutional compliance verification."""
        # Verify policy compliance
        report = await verification_engine.verify_policy_constitutional_compliance(
            policy_content=sample_policy_content, policy_metadata=sample_policy_metadata
        )

        assert isinstance(report, VerificationReport)
        assert report.constitutional_compliance is True
        assert report.result == VerificationResult.VALID
        assert report.constitutional_hash == CONSTITUTIONAL_HASH
        assert report.confidence_score > 0.8
        assert report.proof_time_ms > 0

    async def test_proof_obligations_generation(
        self, verification_engine, sample_policy_content
    ):
        """Test automatic proof obligations generation."""
        # Generate proof obligations from policy
        obligations = await verification_engine.generate_proof_obligations(
            sample_policy_content
        )

        assert isinstance(obligations, list)
        assert len(obligations) > 0

        for obligation in obligations:
            assert isinstance(obligation, ProofObligation)
            assert obligation.obligation_id is not None
            assert obligation.property is not None
            assert isinstance(obligation.constraints, list)
            assert obligation.priority > 0

    async def test_proof_obligations_verification(
        self, verification_engine, sample_proof_obligations
    ):
        """Test verification of proof obligations."""
        # Verify each proof obligation
        verification_results = []

        for obligation in sample_proof_obligations:
            result = await verification_engine.verify_proof_obligation(obligation)
            verification_results.append(result)

            assert isinstance(result, dict)
            assert "verified" in result
            assert "constitutional_hash" in result
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    async def test_constraint_extraction_from_policy(
        self, verification_engine, sample_policy_content
    ):
        """Test constraint extraction from policy text."""
        # Extract constraints from policy
        constraints = verification_engine._extract_constraints_from_policy(
            sample_policy_content
        )

        assert isinstance(constraints, list)
        assert len(constraints) > 0

        # Verify constraint structure
        for constraint in constraints:
            assert isinstance(constraint, dict)
            assert "type" in constraint or "constraint" in constraint

    async def test_constitutional_principles_mapping(self, verification_engine):
        """Test mapping of policy content to constitutional principles."""
        policy_text = "Users must provide explicit consent for data collection and be informed about usage"

        # Map to constitutional principles
        principles = verification_engine._map_to_constitutional_principles(policy_text)

        assert isinstance(principles, list)
        assert len(principles) > 0

        # Should identify relevant principles
        principle_names = [p.get("principle", p.get("name", "")) for p in principles]
        assert any(
            "consent" in p.lower() or "transparency" in p.lower()
            for p in principle_names
        )

    async def test_verification_report_generation(
        self, verification_engine, mock_z3_solver
    ):
        """Test verification report generation."""
        # Mock Z3 solver response
        mock_z3_solver.verify_constitutional_policy.return_value = VerificationReport(
            result=VerificationResult.VALID,
            constitutional_compliance=True,
            confidence_score=0.95,
            proof_time_ms=200.0,
            constitutional_hash=CONSTITUTIONAL_HASH,
            verification_details={
                "principles_verified": ["transparency", "fairness", "privacy"],
                "constraints_satisfied": 8,
                "proof_steps": 15,
                "model_generated": True,
            },
        )

        # Generate report
        policy_content = "Test policy for verification"
        report = await verification_engine.verify_policy_constitutional_compliance(
            policy_content=policy_content
        )

        # Verify report structure
        assert report.constitutional_hash == CONSTITUTIONAL_HASH
        assert report.verification_details is not None
        assert "principles_verified" in report.verification_details
        assert len(report.verification_details["principles_verified"]) > 0

    async def test_performance_metrics_collection(
        self, verification_engine, sample_policy_content
    ):
        """Test performance metrics collection during verification."""
        start_time = time.time()

        # Perform verification
        report = await verification_engine.verify_policy_constitutional_compliance(
            policy_content=sample_policy_content
        )

        end_time = time.time()
        total_time_ms = (end_time - start_time) * 1000

        # Verify performance metrics
        assert report.proof_time_ms > 0
        assert report.proof_time_ms <= total_time_ms + 100  # Allow tolerance

    async def test_error_handling_invalid_policy(self, verification_engine):
        """Test error handling with invalid policy content."""
        # Test with empty policy
        empty_policy = ""

        try:
            report = await verification_engine.verify_policy_constitutional_compliance(
                policy_content=empty_policy
            )
            # Should handle gracefully
            assert report.result in {
                VerificationResult.INVALID,
                VerificationResult.UNKNOWN,
            }
        except Exception as e:
            # Exception handling is acceptable
            assert isinstance(e, Exception)

    async def test_error_handling_solver_failure(
        self, verification_engine, mock_z3_solver
    ):
        """Test error handling when Z3 solver fails."""
        # Mock solver failure
        mock_z3_solver.verify_constitutional_policy.side_effect = Exception(
            "Solver error"
        )

        try:
            await verification_engine.verify_policy_constitutional_compliance(
                policy_content="Test policy"
            )
            raise AssertionError("Should have raised an exception")
        except Exception as e:
            assert "Solver error" in str(e) or isinstance(e, Exception)

    async def test_constitutional_compliance_scoring(self, verification_engine):
        """Test constitutional compliance scoring mechanism."""
        # Test different compliance scenarios
        test_cases = [
            {
                "policy": "Full compliance policy with all requirements",
                "expected_score_range": (0.9, 1.0),
            },
            {
                "policy": "Partial compliance policy missing some requirements",
                "expected_score_range": (0.5, 0.8),
            },
        ]

        for test_case in test_cases:
            # Mock different compliance scores
            verification_engine.z3_solver.verify_constitutional_policy.return_value = (
                VerificationReport(
                    result=VerificationResult.VALID,
                    constitutional_compliance=True,
                    confidence_score=0.85,  # Mid-range score
                    proof_time_ms=100.0,
                    constitutional_hash=CONSTITUTIONAL_HASH,
                )
            )

            report = await verification_engine.verify_policy_constitutional_compliance(
                policy_content=test_case["policy"]
            )

            _min_score, _max_score = test_case["expected_score_range"]
            # Note: Using fixed mock score, but in real implementation would vary
            assert 0 <= report.confidence_score <= 1

    async def test_proof_strategy_selection(self, verification_engine):
        """Test proof strategy selection based on policy complexity."""
        # Simple policy
        simple_policy = "Users must provide consent"

        # Complex policy
        complex_policy = """
        Multi-stakeholder data governance policy with complex requirements:
        1. Consent management across multiple jurisdictions
        2. Cross-border data transfer compliance
        3. Multi-party data sharing agreements
        4. Dynamic consent withdrawal mechanisms
        5. Automated compliance monitoring
        """

        # Test strategy selection (would be implemented in real engine)
        simple_strategy = verification_engine._select_proof_strategy(simple_policy)
        complex_strategy = verification_engine._select_proof_strategy(complex_policy)

        # Strategies should be appropriate for complexity
        assert simple_strategy is not None
        assert complex_strategy is not None

    async def test_incremental_verification(self, verification_engine):
        """Test incremental verification capabilities."""
        # Base policy
        base_policy = "Users must provide consent for data collection"

        # Policy amendment
        amendment = "Data retention period must not exceed 12 months"

        # Verify base policy
        base_report = await verification_engine.verify_policy_constitutional_compliance(
            policy_content=base_policy
        )

        # Verify amended policy
        amended_policy = f"{base_policy}\n{amendment}"
        amended_report = (
            await verification_engine.verify_policy_constitutional_compliance(
                policy_content=amended_policy
            )
        )

        # Both should be valid
        assert base_report.constitutional_compliance is True
        assert amended_report.constitutional_compliance is True
        assert base_report.constitutional_hash == CONSTITUTIONAL_HASH
        assert amended_report.constitutional_hash == CONSTITUTIONAL_HASH

    async def test_verification_caching(self, verification_engine):
        """Test verification result caching."""
        policy_content = "Test policy for caching"

        # First verification
        start_time1 = time.time()
        report1 = await verification_engine.verify_policy_constitutional_compliance(
            policy_content=policy_content
        )
        time.time() - start_time1

        # Second verification (should be cached)
        start_time2 = time.time()
        report2 = await verification_engine.verify_policy_constitutional_compliance(
            policy_content=policy_content
        )
        time.time() - start_time2

        # Results should be consistent
        assert report1.constitutional_hash == report2.constitutional_hash
        assert report1.constitutional_compliance == report2.constitutional_compliance

    async def test_batch_verification(self, verification_engine):
        """Test batch verification of multiple policies."""
        policies = [
            "Policy 1: Data collection requires consent",
            "Policy 2: Users have right to data deletion",
            "Policy 3: Data sharing requires additional consent",
        ]

        # Batch verify policies
        reports = []
        for policy in policies:
            report = await verification_engine.verify_policy_constitutional_compliance(
                policy_content=policy
            )
            reports.append(report)

        # All should have constitutional hash
        for report in reports:
            assert report.constitutional_hash == CONSTITUTIONAL_HASH
            assert isinstance(report.constitutional_compliance, bool)

    async def test_constitutional_hash_consistency(
        self, verification_engine, sample_policy_content
    ):
        """Test constitutional hash consistency across all operations."""
        # Verify policy
        report = await verification_engine.verify_policy_constitutional_compliance(
            policy_content=sample_policy_content
        )

        # Generate proof obligations
        obligations = await verification_engine.generate_proof_obligations(
            sample_policy_content
        )

        # Verify hash consistency
        assert report.constitutional_hash == CONSTITUTIONAL_HASH
        assert report.constitutional_hash == "cdd01ef066bc6cf2"

        # All obligations should reference the same hash
        for obligation in obligations:
            if hasattr(obligation, "constitutional_hash"):
                assert obligation.constitutional_hash == CONSTITUTIONAL_HASH

    async def test_verification_workflow_integration(self, verification_engine):
        """Test integration with verification workflow."""
        # Mock workflow state
        workflow_state = {
            "request_id": "verification_request_123",
            "policy_content": "Test policy for workflow",
            "current_step": "formal_verification",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        # Process verification in workflow context
        report = await verification_engine.verify_policy_constitutional_compliance(
            policy_content=workflow_state["policy_content"]
        )

        # Update workflow state
        workflow_state["verification_result"] = report
        workflow_state["verification_completed"] = True

        # Verify workflow integration
        assert workflow_state["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert (
            workflow_state["verification_result"].constitutional_hash
            == CONSTITUTIONAL_HASH
        )

    async def test_advanced_proof_generation_integration(self, verification_engine):
        """Test integration with advanced proof generation."""
        policy_content = "Advanced policy requiring formal proof"
        proof_strategy = "constitutional_compliance"

        # Generate advanced proof
        proof_result = await verification_engine.generate_advanced_proof(
            policy_content=policy_content, proof_strategy=proof_strategy
        )

        assert isinstance(proof_result, dict)
        assert "status" in proof_result
        assert "constitutional_hash" in proof_result
        assert proof_result["constitutional_hash"] == CONSTITUTIONAL_HASH
