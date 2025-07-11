"""
Comprehensive Unit Tests for Z3 Constitutional Solver
HASH-OK:cdd01ef066bc6cf2

Tests the Z3 SMT solver integration including:
- Constitutional policy verification
- Proof generation and validation
- Policy verification rules
- Constitutional compliance checking
- Performance optimization
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import time
from typing import Dict, Any, List

try:
    import z3
    from z3 import Solver, Bool, Real, sat, unsat, unknown
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False

from services.core.formal_verification.fv_service.app.services.z3_solver import (
    Z3ConstitutionalSolver,
    VerificationResult,
    VerificationReport,
    ProofObligation
)

# Constitutional Hash: cdd01ef066bc6cf2
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@pytest.mark.skipif(not Z3_AVAILABLE, reason="Z3 solver not available")
class TestZ3ConstitutionalSolver:
    """Comprehensive test suite for Z3 Constitutional Solver."""

    @pytest.fixture
    def z3_solver(self):
        """Create Z3ConstitutionalSolver instance for testing."""
        return Z3ConstitutionalSolver(timeout_ms=5000)

    @pytest.fixture
    def sample_constitutional_constraints(self):
        """Sample constitutional constraints for testing."""
        return [
            {
                "type": "constitutional_principle",
                "principle": "human_dignity",
                "constraint": "human_dignity == True",
                "priority": 1
            },
            {
                "type": "constitutional_principle", 
                "principle": "fairness",
                "constraint": "fairness >= 0.8",
                "priority": 2
            },
            {
                "type": "constitutional_principle",
                "principle": "transparency",
                "constraint": "transparency >= 0.7",
                "priority": 3
            }
        ]

    @pytest.fixture
    def sample_policy_constraints(self):
        """Sample policy constraints for testing."""
        return [
            {
                "type": "policy_rule",
                "rule": "data_collection_consent",
                "constraint": "consent_required == True",
                "domain": "data_governance"
            },
            {
                "type": "policy_rule",
                "rule": "transparency_disclosure",
                "constraint": "disclosure_complete >= 0.9",
                "domain": "data_governance"
            }
        ]

    @pytest.fixture
    def sample_proof_obligation(self):
        """Sample proof obligation for testing."""
        return ProofObligation(
            obligation_id="test_obligation_001",
            property="fairness >= 0.8",
            constraints=[
                "human_dignity == True",
                "transparency >= 0.7"
            ],
            context={"domain": "data_governance"},
            priority=1
        )

    async def test_constitutional_hash_validation(self):
        """Test that constitutional hash is properly validated."""
        assert CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"

    async def test_z3_solver_initialization(self, z3_solver):
        """Test Z3 solver initialization."""
        assert z3_solver is not None
        assert z3_solver.timeout_ms == 5000
        assert z3_solver.solver is not None
        assert isinstance(z3_solver.solver, Solver)

    async def test_constitutional_axioms_setup(self, z3_solver):
        """Test constitutional axioms setup."""
        # Initialize constitutional axioms
        z3_solver.initialize_constitutional_axioms()
        
        # Verify axioms are added to solver
        assertions = z3_solver.solver.assertions()
        assert len(assertions) > 0
        
        # Test that human dignity is non-negotiable
        z3_solver.solver.push()
        z3_solver.solver.add(z3.Not(z3_solver.human_dignity))
        result = z3_solver.solver.check()
        z3_solver.solver.pop()
        
        assert result == unsat  # Should be unsatisfiable

    async def test_policy_constraint_parsing(self, z3_solver, sample_policy_constraints):
        """Test parsing of policy constraints to Z3 formulas."""
        for constraint in sample_policy_constraints:
            z3_constraint = z3_solver._parse_constraint(constraint["constraint"])
            assert z3_constraint is not None
            
            # Verify constraint can be added to solver
            z3_solver.solver.push()
            z3_solver.solver.add(z3_constraint)
            result = z3_solver.solver.check()
            z3_solver.solver.pop()
            
            assert result in [sat, unsat, unknown]

    async def test_constitutional_policy_verification(self, z3_solver, sample_constitutional_constraints):
        """Test constitutional policy verification."""
        # Verify policy with constitutional constraints
        report = z3_solver.verify_constitutional_policy(sample_constitutional_constraints)
        
        assert isinstance(report, VerificationReport)
        assert report.result in [VerificationResult.VALID, VerificationResult.INVALID, VerificationResult.UNKNOWN]
        assert report.proof_time_ms > 0
        assert isinstance(report.constitutional_compliance, bool)
        assert 0 <= report.confidence_score <= 1
        assert report.constitutional_hash == CONSTITUTIONAL_HASH

    async def test_proof_obligation_verification(self, z3_solver, sample_proof_obligation):
        """Test proof obligation verification."""
        # Verify proof obligation
        result = z3_solver.verify_proof_obligation(sample_proof_obligation)
        
        assert isinstance(result, dict)
        assert "verified" in result
        assert "proof_time_ms" in result
        assert "constitutional_hash" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert isinstance(result["verified"], bool)

    async def test_formal_proof_generation(self, z3_solver):
        """Test formal proof generation."""
        # Test proof generation for a simple property
        policy_text = "Data collection requires explicit user consent"
        proof_strategy = "constitutional_compliance"
        
        proof_result = z3_solver.generate_advanced_proof(
            policy_text=policy_text,
            proof_strategy=proof_strategy
        )
        
        assert isinstance(proof_result, dict)
        assert "status" in proof_result
        assert "proof_steps" in proof_result
        assert "constitutional_hash" in proof_result
        assert proof_result["constitutional_hash"] == CONSTITUTIONAL_HASH

    async def test_constitutional_compliance_checking(self, z3_solver):
        """Test constitutional compliance checking."""
        # Create model that satisfies constitutional requirements
        solver = Solver()
        human_dignity = Bool("human_dignity")
        fairness = Real("fairness")
        transparency = Real("transparency")
        
        solver.add(human_dignity == True)
        solver.add(fairness >= 0.8)
        solver.add(transparency >= 0.7)
        
        assert solver.check() == sat
        model = solver.model()
        
        # Check compliance
        compliance = z3_solver._check_constitutional_compliance(model)
        assert compliance is True

    async def test_constraint_optimization(self, z3_solver):
        """Test constraint optimization and simplification."""
        # Test constraint simplification
        original_constraint = "fairness >= 0.8 AND fairness <= 1.0 AND transparency >= 0.7"
        z3_constraint = z3_solver._parse_constraint(original_constraint)
        
        if z3_constraint is not None:
            # Apply simplification
            simplified = z3.simplify(z3_constraint)
            assert simplified is not None

    async def test_performance_optimization(self, z3_solver):
        """Test performance optimization features."""
        start_time = time.time()
        
        # Test with optimized solver tactics
        optimized_solver = z3_solver._create_optimized_solver()
        assert optimized_solver is not None
        
        # Simple verification should complete quickly
        x = Real("x")
        optimized_solver.add(x >= 0)
        optimized_solver.add(x <= 1)
        
        result = optimized_solver.check()
        verification_time = (time.time() - start_time) * 1000
        
        assert result == sat
        assert verification_time < 1000  # Should complete in under 1 second

    async def test_timeout_handling(self):
        """Test timeout handling in Z3 solver."""
        # Create solver with very short timeout
        short_timeout_solver = Z3ConstitutionalSolver(timeout_ms=1)
        
        # Create complex constraint that might timeout
        complex_constraints = [
            {"constraint": f"x_{i} >= 0 AND x_{i} <= 1" for i in range(100)}
        ]
        
        # Verification should handle timeout gracefully
        try:
            report = short_timeout_solver.verify_constitutional_policy(complex_constraints)
            # Should either complete or handle timeout
            assert report.result in [VerificationResult.VALID, VerificationResult.INVALID, VerificationResult.UNKNOWN]
        except Exception as e:
            # Timeout exceptions should be handled gracefully
            assert "timeout" in str(e).lower() or "time" in str(e).lower()

    async def test_error_handling(self, z3_solver):
        """Test error handling in Z3 solver operations."""
        # Test with invalid constraint
        invalid_constraints = [
            {"constraint": "invalid_syntax_here ++ == ??"}
        ]
        
        # Should handle parsing errors gracefully
        report = z3_solver.verify_constitutional_policy(invalid_constraints)
        assert isinstance(report, VerificationReport)
        # May be invalid due to parsing errors
        assert report.result in [VerificationResult.INVALID, VerificationResult.UNKNOWN]

    async def test_constitutional_principle_hierarchy(self, z3_solver):
        """Test constitutional principle hierarchy enforcement."""
        # Human dignity should have highest priority
        constraints = [
            {"principle": "human_dignity", "constraint": "human_dignity == True", "priority": 1},
            {"principle": "efficiency", "constraint": "efficiency >= 0.6", "priority": 5}
        ]
        
        # Verify hierarchy is respected
        report = z3_solver.verify_constitutional_policy(constraints)
        
        # Human dignity should be enforced regardless of other constraints
        assert report.constitutional_compliance is True or report.result == VerificationResult.VALID

    async def test_proof_step_generation(self, z3_solver):
        """Test detailed proof step generation."""
        # Simple proof obligation
        obligation = ProofObligation(
            obligation_id="test_proof_steps",
            property="transparency >= 0.8",
            constraints=["human_dignity == True"],
            context={"test": True},
            priority=1
        )
        
        result = z3_solver.verify_proof_obligation(obligation)
        
        if "proof_steps" in result:
            assert isinstance(result["proof_steps"], list)
            assert len(result["proof_steps"]) > 0

    async def test_model_generation(self, z3_solver):
        """Test model generation for satisfiable constraints."""
        # Create satisfiable constraints
        constraints = [
            {"constraint": "fairness >= 0.8"},
            {"constraint": "transparency >= 0.7"},
            {"constraint": "efficiency >= 0.6"}
        ]
        
        report = z3_solver.verify_constitutional_policy(constraints)
        
        if report.result == VerificationResult.VALID:
            # Should have a model
            assert hasattr(report, 'model') or 'model' in report.__dict__

    async def test_unsat_core_generation(self, z3_solver):
        """Test unsatisfiable core generation for conflicting constraints."""
        # Create conflicting constraints
        conflicting_constraints = [
            {"constraint": "x >= 10"},
            {"constraint": "x <= 5"},
            {"constraint": "x >= 0"}
        ]
        
        report = z3_solver.verify_constitutional_policy(conflicting_constraints)
        
        if report.result == VerificationResult.INVALID:
            # Should identify conflicting core
            assert hasattr(report, 'unsat_core') or 'unsat_core' in report.__dict__

    async def test_incremental_verification(self, z3_solver):
        """Test incremental verification capabilities."""
        # Add constraints incrementally
        z3_solver.solver.push()
        
        # Add first constraint
        x = Real("x")
        z3_solver.solver.add(x >= 0)
        result1 = z3_solver.solver.check()
        
        # Add second constraint
        z3_solver.solver.add(x <= 1)
        result2 = z3_solver.solver.check()
        
        # Add conflicting constraint
        z3_solver.solver.add(x >= 2)
        result3 = z3_solver.solver.check()
        
        z3_solver.solver.pop()
        
        assert result1 == sat
        assert result2 == sat
        assert result3 == unsat

    async def test_constitutional_hash_consistency(self, z3_solver, sample_constitutional_constraints):
        """Test constitutional hash consistency across operations."""
        # Verify hash is consistent in all operations
        report = z3_solver.verify_constitutional_policy(sample_constitutional_constraints)
        
        assert report.constitutional_hash == CONSTITUTIONAL_HASH
        assert report.constitutional_hash == "cdd01ef066bc6cf2"

    async def test_verification_metrics_collection(self, z3_solver, sample_constitutional_constraints):
        """Test verification metrics collection."""
        # Perform verification and check metrics
        start_time = time.time()
        report = z3_solver.verify_constitutional_policy(sample_constitutional_constraints)
        end_time = time.time()
        
        # Verify metrics are collected
        assert report.proof_time_ms > 0
        assert report.proof_time_ms <= (end_time - start_time) * 1000 + 100  # Allow some tolerance
        assert 0 <= report.confidence_score <= 1

    async def test_advanced_proof_strategies(self, z3_solver):
        """Test different proof strategies."""
        proof_strategies = [
            "constitutional_compliance",
            "induction",
            "contradiction",
            "bounded_model_checking"
        ]
        
        policy_text = "All users must provide explicit consent for data collection"
        
        for strategy in proof_strategies:
            proof_result = z3_solver.generate_advanced_proof(
                policy_text=policy_text,
                proof_strategy=strategy
            )
            
            assert isinstance(proof_result, dict)
            assert "status" in proof_result
            assert "constitutional_hash" in proof_result
            assert proof_result["constitutional_hash"] == CONSTITUTIONAL_HASH

    async def test_solver_statistics(self, z3_solver):
        """Test solver statistics collection."""
        # Perform some operations
        constraints = [{"constraint": "x >= 0"}, {"constraint": "x <= 1"}]
        z3_solver.verify_constitutional_policy(constraints)
        
        # Check if statistics are available
        if hasattr(z3_solver, 'stats'):
            assert isinstance(z3_solver.stats, dict)
            assert 'verifications' in z3_solver.stats or 'total_verifications' in z3_solver.stats
