#!/usr/bin/env python3
"""
Comprehensive Test Suite for Formal Verification Service

Tests the enhanced Z3 formal verification with:
- Advanced proof generation strategies
- Temporal logic verification
- Proof certificate generation
- Constitutional constraint validation
- Performance benchmarks

Constitutional Hash: cdd01ef066bc6cf2
"""

import os

# Add service path
import sys
import time

import pytest
import z3

sys.path.append(
    os.path.join(os.path.dirname(__file__), "../../services/core/formal-verification")
)

from advanced_proof_engine import (
    AdvancedProofEngine,
    ConstitutionalPrinciple,
    ProofCertificate,
)
from advanced_proof_engine import ProofObligation as AdvancedProofObligation
from advanced_proof_engine import (
    ProofStrategy,
    PropertyType,
    TemporalOperator,
)

# Create a ProofStatus enum since it's not in the actual implementation
from enum import Enum

class ProofStatus(Enum):
    """Proof status for testing compatibility."""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    TIMEOUT = "timeout"
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "services", "core", "formal-verification"))
from fv_service.app.services.z3_solver import (
    FormalVerificationEngine,
    ProofObligation,
    VerificationResult,
    Z3ConstitutionalSolver,
)


class TestAdvancedProofEngine:
    """Test suite for Advanced Proof Engine."""

    @pytest.fixture
    def proof_engine(self):
        """Create proof engine instance."""
        return AdvancedProofEngine(timeout_seconds=30)

    @pytest.fixture
    def sample_obligation(self):
        """Create sample proof obligation."""
        return AdvancedProofObligation(
            id="test_proof_001",
            name="Test Constitutional Compliance",
            description="Verify policy satisfies constitutional requirements",
            property_type=PropertyType.CONSTITUTIONAL,
            formal_statement="constitutional_compliant",
            premises=["human_dignity", "fairness", "transparency or accountability"],
            conclusions=["policy_valid"],
            strategy=ProofStrategy.DIRECT_PROOF,
            timeout_seconds=10,
            context={"policy_id": "policy_123"},
            constitutional_relevance=1.0,
        )

    @pytest.fixture
    def temporal_obligation(self):
        """Create temporal property obligation."""
        return AdvancedProofObligation(
            id="temporal_001",
            name="Temporal Safety Property",
            description="Verify safety property always holds",
            property_type=PropertyType.SAFETY,
            formal_statement="always(safety_condition)",
            premises=["initial_safe_state"],
            strategy=ProofStrategy.TEMPORAL_VERIFICATION,
            timeout_seconds=20,
        )

    # Basic Proof Generation Tests

    def test_proof_engine_initialization(self, proof_engine):
        """Test proof engine initialization."""
        assert proof_engine is not None
        assert proof_engine.timeout_seconds == 30
        assert proof_engine.constitutional_hash == "cdd01ef066bc6cf2"
        assert len(proof_engine.proof_cache) == 0

    def test_direct_proof_generation(self, proof_engine, sample_obligation):
        """Test direct proof generation."""
        result = proof_engine.generate_proof(sample_obligation)

        assert result is not None
        assert result.proof_id is not None
        assert result.status in [
            ProofStatus.PROVED,
            ProofStatus.DISPROVED,
            ProofStatus.UNKNOWN,
        ]
        assert len(result.proof_steps) > 0
        assert result.verification_time_ms > 0

        if result.status == ProofStatus.PROVED:
            assert result.constitutional_compliance is True
            assert result.confidence_score > 0.7

    def test_proof_by_contradiction(self, proof_engine):
        """Test proof by contradiction strategy."""
        obligation = AdvancedProofObligation(
            id="contra_001",
            name="Contradiction Test",
            description="Prove by contradiction",
            property_type=PropertyType.INVARIANT,
            formal_statement="not(violation_possible)",
            premises=["safety_mechanisms_active"],
            strategy=ProofStrategy.PROOF_BY_CONTRADICTION,
        )

        result = proof_engine.generate_proof(obligation)

        assert result.strategy_used == ProofStrategy.PROOF_BY_CONTRADICTION

        # Check for contradiction detection in proof steps
        if result.status == ProofStatus.PROVED:
            assert any(
                "contradiction" in step.rule_applied.lower()
                for step in result.proof_steps
            )

    def test_proof_by_induction(self, proof_engine):
        """Test proof by induction strategy."""
        obligation = AdvancedProofObligation(
            id="induct_001",
            name="Inductive Proof",
            description="Prove property holds for all states",
            property_type=PropertyType.INVARIANT,
            formal_statement="forall n. property(n)",
            premises=["base_case", "inductive_hypothesis"],
            strategy=ProofStrategy.PROOF_BY_INDUCTION,
        )

        result = proof_engine.generate_proof(obligation)

        assert result.strategy_used == ProofStrategy.PROOF_BY_INDUCTION

        # Should have base case and inductive step
        if result.status == ProofStatus.PROVED:
            proof_rules = [step.rule_applied for step in result.proof_steps]
            assert any("base" in rule.lower() for rule in proof_rules)
            assert any("induct" in rule.lower() for rule in proof_rules)

    # Temporal Logic Verification Tests

    def test_temporal_always_property(self, proof_engine, temporal_obligation):
        """Test verification of 'always' temporal property."""
        property_spec = "always(human_dignity_respected)"

        result = proof_engine.verify_temporal_property(
            temporal_obligation, property_spec
        )

        assert result is not None
        assert result.temporal_property == property_spec
        assert result.operator_type == TemporalOperator.ALWAYS

        if result.status == ProofStatus.PROVED:
            assert result.holds_for_all_traces is True

    def test_temporal_eventually_property(self, proof_engine):
        """Test verification of 'eventually' temporal property."""
        obligation = AdvancedProofObligation(
            id="eventually_001",
            name="Liveness Property",
            description="Verify something good eventually happens",
            property_type=PropertyType.LIVENESS,
            formal_statement="eventually(goal_achieved)",
            strategy=ProofStrategy.TEMPORAL_VERIFICATION,
        )

        property_spec = "eventually(fairness_achieved)"
        result = proof_engine.verify_temporal_property(obligation, property_spec)

        assert result.operator_type == TemporalOperator.EVENTUALLY

        if result.status == ProofStatus.DISPROVED:
            assert result.counterexample is not None
            assert "trace" in result.counterexample

    def test_temporal_until_property(self, proof_engine):
        """Test verification of 'until' temporal property."""
        property_spec = "privacy_maintained until consent_revoked"

        obligation = AdvancedProofObligation(
            id="until_001",
            name="Until Property",
            description="Verify property holds until condition",
            property_type=PropertyType.SAFETY,
            formal_statement=property_spec,
            strategy=ProofStrategy.TEMPORAL_VERIFICATION,
        )

        result = proof_engine.verify_temporal_property(obligation, property_spec)

        assert result.operator_type == TemporalOperator.UNTIL
        assert result.verification_time_ms > 0

    # Bounded Model Checking Tests

    def test_bounded_model_checking(self, proof_engine):
        """Test bounded model checking strategy."""
        obligation = AdvancedProofObligation(
            id="bmc_001",
            name="Bounded Verification",
            description="Verify property within bounded steps",
            property_type=PropertyType.REACHABILITY,
            formal_statement="reachable(safe_state)",
            strategy=ProofStrategy.BOUNDED_MODEL_CHECKING,
            context={"bound": 10},
        )

        result = proof_engine.generate_proof(obligation)

        assert result.strategy_used == ProofStrategy.BOUNDED_MODEL_CHECKING
        assert "bound" in result.metadata

        if result.status == ProofStatus.DISPROVED:
            assert result.counterexample is not None
            assert len(result.counterexample.get("trace", [])) <= 10

    # Constitutional Principle Tests

    def test_constitutional_principle_modeling(self, proof_engine):
        """Test constitutional principle constraint modeling."""
        principles = [
            ConstitutionalPrinciple(
                name="human_dignity",
                description="Respect for human dignity",
                formal_specification="forall person. respected(person)",
                priority=1,
            ),
            ConstitutionalPrinciple(
                name="fairness",
                description="Fair treatment",
                formal_specification="forall x,y. equal_treatment(x,y)",
                priority=2,
            ),
        ]

        # Model principles as Z3 constraints
        for principle in principles:
            constraint = principle.to_z3_constraint()
            assert constraint is not None
            assert isinstance(constraint, z3.BoolRef)

    def test_constitutional_compliance_proof(self, proof_engine):
        """Test comprehensive constitutional compliance proof."""
        obligation = AdvancedProofObligation(
            id="const_comp_001",
            name="Full Constitutional Compliance",
            description="Verify all constitutional principles satisfied",
            property_type=PropertyType.CONSTITUTIONAL,
            formal_statement="all_principles_satisfied",
            premises=[
                "human_dignity",
                "fairness",
                "transparency",
                "accountability",
                "privacy",
            ],
            strategy=ProofStrategy.DIRECT_PROOF,
            constitutional_relevance=1.0,
        )

        result = proof_engine.generate_proof(obligation)

        assert result.constitutional_compliance in [True, False]
        assert result.confidence_score >= 0

        if result.status == ProofStatus.PROVED:
            assert result.constitutional_compliance is True
            assert result.confidence_score > 0.8

    # Proof Certificate Tests

    def test_proof_certificate_generation(self, proof_engine, sample_obligation):
        """Test cryptographic proof certificate generation."""
        result = proof_engine.generate_proof(sample_obligation)

        if result.status == ProofStatus.PROVED and result.certificate:
            cert = result.certificate

            assert cert.certificate_id is not None
            assert cert.obligation_id == sample_obligation.id
            assert cert.policy_hash is not None
            assert cert.proof_hash is not None
            assert cert.constitutional_compliance is True
            assert cert.signature is not None
            assert len(cert.signature) == 64  # SHA256 hex

            # Verify certificate
            is_valid = proof_engine.verify_certificate(cert)
            assert is_valid is True

    def test_certificate_tampering_detection(self, proof_engine):
        """Test detection of tampered certificates."""
        # Generate valid certificate
        obligation = AdvancedProofObligation(
            id="cert_tamper_001",
            name="Certificate Test",
            description="Test certificate integrity",
            property_type=PropertyType.SAFETY,
            formal_statement="safety_holds",
            strategy=ProofStrategy.DIRECT_PROOF,
        )

        result = proof_engine.generate_proof(obligation)

        if result.certificate:
            # Tamper with certificate
            tampered_cert = ProofCertificate(
                certificate_id=result.certificate.certificate_id,
                obligation_id=result.certificate.obligation_id,
                policy_hash="tampered_hash",  # Changed
                proof_hash=result.certificate.proof_hash,
                timestamp=result.certificate.timestamp,
                constitutional_compliance=result.certificate.constitutional_compliance,
                signature=result.certificate.signature,  # Original signature
            )

            # Should detect tampering
            is_valid = proof_engine.verify_certificate(tampered_cert)
            assert is_valid is False

    # Conflict Resolution Tests

    def test_constraint_conflict_detection(self, proof_engine):
        """Test detection of conflicting constraints."""
        obligation = AdvancedProofObligation(
            id="conflict_001",
            name="Conflicting Constraints",
            description="Test conflict detection",
            property_type=PropertyType.INVARIANT,
            formal_statement="p and not_p",  # Obvious conflict
            premises=["p", "not p"],
            strategy=ProofStrategy.DIRECT_PROOF,
        )

        result = proof_engine.generate_proof(obligation)

        assert result.status in [ProofStatus.DISPROVED, ProofStatus.UNKNOWN]
        assert result.conflicts_detected > 0

        if result.conflict_resolution:
            assert result.conflict_resolution.strategy is not None

    # Performance Tests

    @pytest.mark.performance
    def test_proof_generation_performance(self, proof_engine):
        """Test proof generation performance."""
        obligations = []
        for i in range(50):
            obligations.append(
                AdvancedProofObligation(
                    id=f"perf_{i}",
                    name=f"Performance Test {i}",
                    description="Performance testing",
                    property_type=PropertyType.SAFETY,
                    formal_statement=f"property_{i}",
                    premises=[f"premise_{j}" for j in range(3)],
                    strategy=ProofStrategy.DIRECT_PROOF,
                    timeout_seconds=5,
                )
            )

        start_time = time.time()
        results = [proof_engine.generate_proof(obl) for obl in obligations]
        end_time = time.time()

        total_time = end_time - start_time
        avg_time = total_time / len(obligations)

        assert all(r is not None for r in results)
        assert avg_time < 0.2  # Less than 200ms per proof

        print(f"Average proof generation time: {avg_time * 1000:.2f}ms")

    @pytest.mark.performance
    def test_proof_cache_effectiveness(self, proof_engine, sample_obligation):
        """Test proof caching effectiveness."""
        # First proof (no cache)
        start1 = time.time()
        result1 = proof_engine.generate_proof(sample_obligation)
        time1 = time.time() - start1

        # Second proof (should use cache)
        start2 = time.time()
        result2 = proof_engine.generate_proof(sample_obligation)
        time2 = time.time() - start2

        assert result1.proof_id == result2.proof_id  # Same proof
        assert time2 < time1 * 0.1  # Cache hit should be much faster
        assert proof_engine.cache_metrics["hits"] > 0


class TestZ3ConstitutionalSolver:
    """Test suite for Z3 Constitutional Solver."""

    @pytest.fixture
    def z3_solver(self):
        """Create Z3 solver instance."""
        return Z3ConstitutionalSolver(timeout_ms=10000)

    @pytest.fixture
    def sample_constraints(self):
        """Create sample policy constraints."""
        return [
            "human_dignity",
            "fairness",
            "transparency or accountability",
            "privacy",
            "non_discrimination",
        ]

    # Basic Z3 Solver Tests

    def test_solver_initialization(self, z3_solver):
        """Test Z3 solver initialization."""
        assert z3_solver is not None
        assert z3_solver.timeout_ms == 10000
        assert z3_solver.advanced_proof_engine is not None

        # Check constitutional axioms
        assertions = z3_solver.solver.assertions()
        assert len(assertions) > 0  # Should have axioms

    def test_constitutional_axioms(self, z3_solver):
        """Test constitutional axiom setup."""
        # Human dignity is non-negotiable
        z3_solver.solver.push()
        z3_solver.solver.add(z3.Not(z3_solver.human_dignity))
        result = z3_solver.solver.check()
        z3_solver.solver.pop()

        assert result == z3.unsat  # Should be unsatisfiable

    def test_policy_verification(self, z3_solver, sample_constraints):
        """Test basic policy verification."""
        report = z3_solver.verify_constitutional_policy(sample_constraints)

        assert report is not None
        assert report.result in [VerificationResult.VALID, VerificationResult.INVALID]
        assert report.proof_time_ms > 0
        assert isinstance(report.constitutional_compliance, bool)
        assert 0 <= report.confidence_score <= 1

    def test_constraint_parsing(self, z3_solver):
        """Test constraint parsing capabilities."""
        # Simple constraints
        assert z3_solver._parse_constraint("human_dignity") == z3_solver.human_dignity
        assert z3_solver._parse_constraint("fairness") == z3_solver.fairness

        # Negation
        not_privacy = z3_solver._parse_constraint("not privacy")
        assert z3.is_not(not_privacy)

        # Conjunction
        and_constraint = z3_solver._parse_constraint("fairness and transparency")
        assert z3.is_and(and_constraint)

        # Disjunction
        or_constraint = z3_solver._parse_constraint("transparency or accountability")
        assert z3.is_or(or_constraint)

        # Implication
        impl_constraint = z3_solver._parse_constraint(
            "fairness implies non_discrimination"
        )
        assert z3.is_implies(impl_constraint)

    def test_proof_obligation_verification(self, z3_solver):
        """Test proof obligation verification."""
        obligation = ProofObligation(
            id="z3_obl_001",
            description="Test obligation",
            property="constitutional_compliant",
            constraints=["human_dignity", "fairness", "privacy"],
            context={"test": True},
        )

        report = z3_solver.verify_proof_obligation(obligation)

        assert report.obligation_id == obligation.id
        assert report.result != VerificationResult.ERROR

        if report.result == VerificationResult.INVALID:
            assert report.counterexample is not None

    # Advanced Proof Integration Tests

    def test_advanced_proof_generation(self, z3_solver):
        """Test advanced proof generation integration."""
        policy_text = "All citizens shall have equal rights and fair treatment"

        proof_result = z3_solver.generate_advanced_proof(
            policy_text, proof_strategy="direct_proof"
        )

        assert proof_result is not None
        assert "proof_id" in proof_result
        assert "status" in proof_result
        assert "proof_steps" in proof_result
        assert len(proof_result["proof_steps"]) > 0
        assert proof_result["constitutional_compliance"] in [True, False]

    def test_temporal_property_verification(self, z3_solver):
        """Test temporal property verification integration."""
        policy_text = "Privacy must be maintained at all times"
        temporal_properties = [
            "always(privacy)",
            "eventually(consent_checked)",
            "privacy until data_deletion",
        ]

        result = z3_solver.verify_temporal_properties(policy_text, temporal_properties)

        assert "temporal_verification_results" in result
        assert len(result["temporal_verification_results"]) == 3

        for prop_result in result["temporal_verification_results"]:
            assert "property" in prop_result
            assert "verification_result" in prop_result
            assert "proof_time_ms" in prop_result

    def test_proof_certificate_generation(self, z3_solver):
        """Test proof certificate generation integration."""
        policy_text = "Democratic governance with transparency and accountability"

        cert_result = z3_solver.generate_proof_certificate(policy_text)

        assert "valid" in cert_result

        if cert_result["valid"]:
            assert "certificate_id" in cert_result
            assert "policy_hash" in cert_result
            assert "proof_hash" in cert_result
            assert "signature" in cert_result
            assert "constitutional_compliance" in cert_result

    # Compliance Checking Tests

    def test_constitutional_compliance_checking(self, z3_solver):
        """Test constitutional compliance checking."""
        # Create model that satisfies requirements
        solver = z3.Solver()
        solver.add(z3_solver.human_dignity == True)
        solver.add(z3_solver.fairness == True)
        solver.add(z3_solver.privacy == True)
        solver.add(z3_solver.transparency == True)

        assert solver.check() == z3.sat
        model = solver.model()

        compliance = z3_solver._check_constitutional_compliance(model)
        assert compliance is True

    def test_confidence_score_calculation(self, z3_solver):
        """Test confidence score calculation."""
        # Create model with mixed principle satisfaction
        solver = z3.Solver()
        solver.add(z3_solver.human_dignity == True)
        solver.add(z3_solver.fairness == True)
        solver.add(z3_solver.transparency == False)
        solver.add(z3_solver.accountability == True)
        solver.add(z3_solver.privacy == True)

        assert solver.check() == z3.sat
        model = solver.model()

        confidence = z3_solver._calculate_confidence(model)
        assert 0 < confidence < 1  # Partial satisfaction

    # Error Handling Tests

    def test_invalid_constraint_handling(self, z3_solver):
        """Test handling of invalid constraints."""
        invalid_constraints = [
            "invalid_constraint",
            "malformed and",
            "missing_operand or",
            "",
        ]

        report = z3_solver.verify_constitutional_policy(invalid_constraints)

        # Should handle gracefully
        assert report is not None
        assert report.result in [VerificationResult.INVALID, VerificationResult.UNKNOWN]

    def test_timeout_handling(self):
        """Test solver timeout handling."""
        # Create solver with very short timeout
        solver = Z3ConstitutionalSolver(timeout_ms=1)  # 1ms timeout

        # Complex constraint that takes time
        complex_constraints = [f"constraint_{i}" for i in range(1000)]

        report = solver.verify_constitutional_policy(complex_constraints)

        # Should timeout gracefully
        assert report.result in [VerificationResult.TIMEOUT, VerificationResult.UNKNOWN]


class TestFormalVerificationEngine:
    """Test suite for high-level Formal Verification Engine."""

    @pytest.fixture
    def verification_engine(self):
        """Create verification engine instance."""
        return FormalVerificationEngine(timeout_ms=20000)

    @pytest.fixture
    async def policy_content(self):
        """Sample policy content for testing."""
        return """
        This policy ensures:
        1. Human dignity is respected in all operations
        2. Fair and equitable treatment for all users
        3. Transparent decision-making processes
        4. Strong privacy protections
        5. Democratic participation in governance
        """

    async def test_policy_verification(self, verification_engine, policy_content):
        """Test high-level policy verification."""
        report = await verification_engine.verify_policy_constitutional_compliance(
            policy_content, {"domain": "governance", "version": "1.0"}
        )

        assert report is not None
        assert report.result != VerificationResult.ERROR
        assert report.constitutional_compliance in [True, False]
        assert report.confidence_score > 0

    async def test_proof_obligation_generation(
        self, verification_engine, policy_content
    ):
        """Test automatic proof obligation generation."""
        reports = await verification_engine.verify_proof_obligations(policy_content)

        assert len(reports) > 0  # Should generate obligations

        for report in reports:
            assert report.obligation_id is not None
            assert report.result in [r.value for r in VerificationResult]
            assert report.proof_time_ms >= 0

    async def test_constraint_extraction(self, verification_engine):
        """Test constraint extraction from policy text."""
        test_policies = [
            (
                "Policy ensures human dignity and fairness",
                ["human_dignity", "fairness"],
            ),
            (
                "Transparent and accountable governance",
                ["transparency", "accountability"],
            ),
            ("Privacy-preserving data processing", ["privacy"]),
            ("Non-discriminatory access", ["non_discrimination"]),
        ]

        for policy_text, expected_constraints in test_policies:
            constraints = verification_engine._extract_constraints_from_policy(
                policy_text
            )

            for expected in expected_constraints:
                assert expected in constraints


# Integration Tests


class TestFormalVerificationIntegration:
    """Integration tests for formal verification service."""

    @pytest.fixture
    async def mock_verification_request(self):
        """Mock verification request."""
        return {
            "policy_content": (
                "All AI agents must respect human dignity and ensure fairness"
            ),
            "policy_metadata": {
                "id": "policy_001",
                "version": "1.0",
                "domain": "ai_governance",
            },
            "constraints": ["human_dignity", "fairness", "transparency"],
        }

    async def test_end_to_end_verification(self, mock_verification_request):
        """Test end-to-end verification flow."""
        engine = FormalVerificationEngine()

        # Verify policy
        report = await engine.verify_policy_constitutional_compliance(
            mock_verification_request["policy_content"],
            mock_verification_request["policy_metadata"],
        )

        assert report.constitutional_compliance is True
        assert report.confidence_score > 0.7

        # Generate proof obligations
        obligations = await engine.verify_proof_obligations(
            mock_verification_request["policy_content"]
        )

        assert len(obligations) >= 1
        assert all(o.constitutional_compliance for o in obligations)


# Performance Benchmarks


class TestVerificationPerformance:
    """Performance tests for formal verification."""

    @pytest.mark.benchmark
    def test_z3_solving_performance(self, benchmark):
        """Benchmark Z3 constraint solving."""
        solver = Z3ConstitutionalSolver()

        constraints = [
            "human_dignity",
            "fairness",
            "transparency or accountability",
            "privacy",
            "not discrimination",
        ]

        result = benchmark(solver.verify_constitutional_policy, constraints)
        assert result.result != VerificationResult.ERROR

    @pytest.mark.benchmark
    def test_proof_generation_performance(self, benchmark):
        """Benchmark proof generation."""
        engine = AdvancedProofEngine()

        obligation = AdvancedProofObligation(
            id="bench_001",
            name="Benchmark",
            description="Performance test",
            property_type=PropertyType.SAFETY,
            formal_statement="safety_property",
            premises=["p1", "p2", "p3"],
            strategy=ProofStrategy.DIRECT_PROOF,
        )

        result = benchmark(engine.generate_proof, obligation)
        assert result is not None


# Pytest configuration


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    config.addinivalue_line("markers", "benchmark: mark test as a benchmark")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
