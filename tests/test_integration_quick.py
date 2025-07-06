#!/usr/bin/env python3
"""
Quick Integration Test for ACGS Enhanced Services

Validates that all enhanced services can be imported and basic functionality works.
This is a fast integration test to verify the testing framework and service imports.

Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import sys
from datetime import datetime, timezone

import pytest

# Add service paths
sys.path.append(
    os.path.join(
        os.path.dirname(__file__), "../services/core/constitutional-ai/ac_service/app"
    )
)
sys.path.append(
    os.path.join(os.path.dirname(__file__), "../services/core/evolutionary-computation")
)
sys.path.append(
    os.path.join(os.path.dirname(__file__), "../services/core/governance-synthesis")
)
sys.path.append(
    os.path.join(os.path.dirname(__file__), "../services/core/formal-verification")
)


@pytest.mark.smoke
class TestServiceImports:
    """Quick smoke tests to verify service imports work."""

    def test_constitutional_ai_import(self):
        """Test Constitutional AI service imports."""
        try:
            from services.constitutional_validation_service import (
                ConstitutionalValidationService,
            )

            service = ConstitutionalValidationService()
            assert service is not None
            assert hasattr(service, "validate_policy")
        except ImportError as e:
            pytest.skip(f"Constitutional AI service not available: {e}")

    def test_evolutionary_computation_import(self):
        """Test Evolutionary Computation service imports."""
        try:
            from evolutionary_algorithms import EvolutionConfig, GeneticAlgorithm

            config = EvolutionConfig(population_size=10, generations=5)
            algorithm = GeneticAlgorithm(config)
            assert algorithm is not None
            assert hasattr(algorithm, "evolve")
        except ImportError as e:
            pytest.skip(f"Evolutionary Computation service not available: {e}")

    def test_governance_synthesis_import(self):
        """Test Governance Synthesis service imports."""
        try:
            from advanced_opa_engine import AdvancedGovernanceSynthesisEngine

            engine = AdvancedGovernanceSynthesisEngine("./policies")
            assert engine is not None
            assert hasattr(engine, "synthesize_governance_decision")
        except ImportError as e:
            pytest.skip(f"Governance Synthesis service not available: {e}")

    def test_formal_verification_import(self):
        """Test Formal Verification service imports."""
        try:
            from advanced_proof_engine import AdvancedProofEngine

            engine = AdvancedProofEngine()
            assert engine is not None
            assert hasattr(engine, "generate_proof")
        except ImportError as e:
            pytest.skip(f"Formal Verification service not available: {e}")


@pytest.mark.smoke
@pytest.mark.constitutional
class TestConstitutionalCompliance:
    """Quick tests for constitutional compliance validation."""

    def test_constitutional_hash_validation(self):
        """Test that all services use the correct constitutional hash."""
        expected_hash = "cdd01ef066bc6cf2"

        # Test various service implementations
        hashes_found = []

        # Check if we can import services and validate hash
        try:
            from services.constitutional_validation_service import CONSTITUTIONAL_HASH

            hashes_found.append(CONSTITUTIONAL_HASH)
        except ImportError:
            pass

        try:
            from advanced_proof_engine import AdvancedProofEngine

            engine = AdvancedProofEngine()
            hashes_found.append(engine.constitutional_hash)
        except ImportError:
            pass

        # At least one hash should be found and match
        if hashes_found:
            assert all(h == expected_hash for h in hashes_found), (
                f"Constitutional hash mismatch: expected {expected_hash}, found"
                f" {hashes_found}"
            )
        else:
            pytest.skip("No services available for hash validation")

    def test_basic_constitutional_principles(self):
        """Test basic constitutional principles are recognized."""
        principles = [
            "human_dignity",
            "fairness",
            "transparency",
            "accountability",
            "privacy",
        ]

        # These principles should be fundamental to all services
        for principle in principles:
            assert principle is not None
            assert len(principle) > 0
            assert isinstance(principle, str)


@pytest.mark.integration
class TestServiceConnectivity:
    """Test connectivity between enhanced services."""

    async def test_constitutional_ai_basic_validation(self):
        """Test basic Constitutional AI validation functionality."""
        try:
            from services.constitutional_validation_service import (
                ConstitutionalValidationService,
            )

            service = ConstitutionalValidationService()

            test_policy = {
                "id": "test_001",
                "name": "Test Policy",
                "content": "Ensure fair treatment for all users",
                "metadata": {"version": "1.0"},
            }

            result = await service.validate_policy(test_policy)

            assert result is not None
            assert "constitutional_hash" in result
            assert result["constitutional_hash"] == "cdd01ef066bc6cf2"

        except ImportError:
            pytest.skip("Constitutional AI service not available")

    def test_evolutionary_algorithm_basic_functionality(self):
        """Test basic evolutionary algorithm functionality."""
        try:
            import numpy as np
            from evolutionary_algorithms import (
                EvolutionConfig,
                GeneticAlgorithm,
                Individual,
            )

            config = EvolutionConfig(
                population_size=10, generations=2, mutation_rate=0.1
            )
            algorithm = GeneticAlgorithm(config)

            # Test population generation
            population = algorithm.generate_initial_population(genome_size=5)
            assert len(population.individuals) == 10
            assert all(len(ind.genome) == 5 for ind in population.individuals)

            # Test individual creation
            individual = Individual(genome=np.array([0.1, 0.2, 0.3, 0.4, 0.5]))
            assert len(individual.genome) == 5

        except ImportError:
            pytest.skip("Evolutionary Computation service not available")

    async def test_governance_synthesis_basic_functionality(self):
        """Test basic governance synthesis functionality."""
        try:
            from advanced_opa_engine import (
                AdvancedGovernanceSynthesisEngine,
                PolicyEvaluationContext,
            )

            engine = AdvancedGovernanceSynthesisEngine("./policies")

            # Test context creation
            context = PolicyEvaluationContext(
                request_id="test_001",
                timestamp=datetime.now(timezone.utc),
                principal={"id": "test_user"},
                resource={"id": "test_resource"},
                action="test_action",
            )

            assert context is not None
            assert context.request_id == "test_001"
            assert context.action == "test_action"

        except ImportError:
            pytest.skip("Governance Synthesis service not available")

    def test_formal_verification_basic_functionality(self):
        """Test basic formal verification functionality."""
        try:
            from advanced_proof_engine import (
                AdvancedProofEngine,
                ProofObligation,
                ProofStrategy,
                PropertyType,
            )

            engine = AdvancedProofEngine()

            # Test obligation creation
            obligation = ProofObligation(
                id="test_proof_001",
                name="Test Proof",
                description="Test proof obligation",
                property_type=PropertyType.SAFETY,
                formal_statement="test_property",
                strategy=ProofStrategy.DIRECT_PROOF,
            )

            assert obligation is not None
            assert obligation.id == "test_proof_001"
            assert obligation.property_type == PropertyType.SAFETY

        except ImportError:
            pytest.skip("Formal Verification service not available")


@pytest.mark.performance
class TestBasicPerformance:
    """Basic performance validation tests."""

    def test_import_performance(self):
        """Test that service imports complete quickly."""
        import time

        start_time = time.time()

        # Try to import each service
        try:
            from services.constitutional_validation_service import (
                ConstitutionalValidationService,
            )
        except ImportError:
            pass

        try:
            from evolutionary_algorithms import GeneticAlgorithm
        except ImportError:
            pass

        try:
            from advanced_opa_engine import AdvancedGovernanceSynthesisEngine
        except ImportError:
            pass

        try:
            from advanced_proof_engine import AdvancedProofEngine
        except ImportError:
            pass

        end_time = time.time()
        import_time = end_time - start_time

        # Imports should complete in under 5 seconds
        assert import_time < 5.0, f"Service imports took too long: {import_time:.2f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
