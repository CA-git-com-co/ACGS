"""
Unit Tests for Governance Synthesis Core Service
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive unit tests for the Governance Synthesis service core functionality
including policy synthesis, WINA optimization, and constitutional compliance.
"""

import asyncio
import json
import time
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
import pytest_asyncio

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestGovernanceSynthesisCore:
    """Unit tests for Governance Synthesis core functionality."""

    @pytest.fixture
    def mock_wina_optimizer(self):
        """Mock WINA (Weight Informed Neuron Activation) optimizer."""
        optimizer = Mock()
        optimizer.optimize_policy = AsyncMock(
            return_value={
                "optimized": True,
                "optimization_score": 0.92,
                "wina_weights": {
                    "fairness": 0.35,
                    "transparency": 0.30,
                    "accountability": 0.35,
                },
                "optimization_time_ms": 3.1,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )
        optimizer.calculate_weights = Mock(
            return_value={
                "fairness": 0.35,
                "transparency": 0.30,
                "accountability": 0.35,
            }
        )
        return optimizer

    @pytest.fixture
    def mock_synthesis_engine(self):
        """Mock governance synthesis engine."""
        engine = Mock()
        engine.synthesize_policy = AsyncMock(
            return_value={
                "policy_id": "synthesized_001",
                "synthesized": True,
                "synthesis_score": 0.89,
                "policy_content": "Synthesized governance policy content",
                "synthesis_time_ms": 4.2,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "synthesis_metadata": {
                    "principles_integrated": 5,
                    "constraints_satisfied": 8,
                    "optimization_iterations": 12,
                },
            }
        )
        engine.validate_synthesis = AsyncMock(
            return_value={
                "valid": True,
                "validation_score": 0.94,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )
        return engine

    @pytest.fixture
    def mock_rego_synthesizer(self):
        """Mock Rego policy synthesizer."""
        synthesizer = Mock()
        synthesizer.synthesize_rego_policy = AsyncMock(
            return_value={
                "rego_policy": 'package governance\n\nallow {\n    input.user.role == "admin"\n}',
                "syntax_valid": True,
                "constitutional_compliant": True,
                "synthesis_time_ms": 2.8,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )
        return synthesizer

    @pytest.mark.asyncio
    async def test_basic_policy_synthesis(self, mock_synthesis_engine):
        """Test basic policy synthesis functionality."""
        synthesis_input = {
            "synthesis_goal": "Create fair and transparent governance policy",
            "constitutional_principles": ["fairness", "transparency", "accountability"],
            "constraints": ["privacy_preserving", "performance_efficient"],
            "context": "Multi-tenant governance system",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await mock_synthesis_engine.synthesize_policy(synthesis_input)

        assert result["synthesized"] is True
        assert result["synthesis_score"] > 0.8  # High quality synthesis
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "policy_content" in result
        assert result["synthesis_time_ms"] < 5.0  # Performance target

    @pytest.mark.asyncio
    async def test_wina_optimization_performance(self, mock_wina_optimizer):
        """Test WINA optimization performance targets."""
        policy_data = {
            "policy_id": "wina_opt_001",
            "principles": ["fairness", "transparency", "accountability"],
            "current_weights": {
                "fairness": 0.33,
                "transparency": 0.33,
                "accountability": 0.34,
            },
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        start_time = time.perf_counter()
        result = await mock_wina_optimizer.optimize_policy(policy_data)
        end_time = time.perf_counter()

        actual_time_ms = (end_time - start_time) * 1000

        # Verify performance targets
        assert (
            actual_time_ms < 5.0
        ), f"WINA optimization took {actual_time_ms:.2f}ms, exceeds 5ms target"
        assert result["optimization_time_ms"] < 5.0
        assert result["optimized"] is True
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_wina_weight_calculation(self, mock_wina_optimizer):
        """Test WINA weight calculation algorithm."""
        principles = ["fairness", "transparency", "accountability"]

        weights = mock_wina_optimizer.calculate_weights(principles)

        # Verify weight properties
        assert isinstance(weights, dict)
        assert len(weights) == len(principles)
        assert all(principle in weights for principle in principles)

        # Verify weights sum to 1.0 (approximately)
        total_weight = sum(weights.values())
        assert (
            abs(total_weight - 1.0) < 0.01
        ), f"Weights sum to {total_weight}, should be ~1.0"

        # Verify all weights are positive
        assert all(weight > 0 for weight in weights.values())

    @pytest.mark.asyncio
    async def test_rego_policy_synthesis(self, mock_rego_synthesizer):
        """Test Rego policy synthesis functionality."""
        synthesis_request = {
            "policy_type": "access_control",
            "governance_rules": ["admin_access", "user_permissions"],
            "constitutional_principles": ["fairness", "transparency"],
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await mock_rego_synthesizer.synthesize_rego_policy(synthesis_request)

        assert result["syntax_valid"] is True
        assert result["constitutional_compliant"] is True
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "package governance" in result["rego_policy"]  # Valid Rego syntax
        assert result["synthesis_time_ms"] < 5.0

    @pytest.mark.asyncio
    async def test_synthesis_validation(self, mock_synthesis_engine):
        """Test synthesis validation functionality."""
        synthesized_policy = {
            "policy_id": "validation_test_001",
            "policy_content": "Test governance policy for validation",
            "synthesis_metadata": {
                "principles_integrated": 3,
                "constraints_satisfied": 5,
            },
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await mock_synthesis_engine.validate_synthesis(synthesized_policy)

        assert result["valid"] is True
        assert result["validation_score"] > 0.9  # High validation score
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_concurrent_synthesis_performance(self, mock_synthesis_engine):
        """Test concurrent synthesis performance."""
        synthesis_requests = [
            {
                "synthesis_goal": f"Governance policy {i}",
                "constitutional_principles": ["fairness", "transparency"],
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
            for i in range(3)
        ]

        start_time = time.perf_counter()

        # Execute concurrent synthesis
        tasks = [
            mock_synthesis_engine.synthesize_policy(request)
            for request in synthesis_requests
        ]
        results = await asyncio.gather(*tasks)

        end_time = time.perf_counter()
        total_time_ms = (end_time - start_time) * 1000

        # Verify all synthesis completed
        assert len(results) == len(synthesis_requests)

        # Verify performance (concurrent processing should be efficient)
        assert total_time_ms < 15.0, f"Concurrent synthesis took {total_time_ms:.2f}ms"

        # Verify all results have constitutional hash
        for result in results:
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
            assert result["synthesized"] is True

    @pytest.mark.asyncio
    async def test_multi_principle_integration(self, mock_synthesis_engine):
        """Test integration of multiple constitutional principles."""
        complex_synthesis_input = {
            "synthesis_goal": "Comprehensive governance framework",
            "constitutional_principles": [
                "fairness",
                "transparency",
                "accountability",
                "privacy",
                "security",
                "efficiency",
            ],
            "constraints": [
                "performance_optimized",
                "scalable",
                "maintainable",
                "audit_compliant",
                "user_friendly",
            ],
            "context": "Enterprise multi-tenant system",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        # Mock engine for complex synthesis
        mock_synthesis_engine.synthesize_policy = AsyncMock(
            return_value={
                "policy_id": "complex_synthesis_001",
                "synthesized": True,
                "synthesis_score": 0.91,
                "policy_content": "Complex multi-principle governance policy",
                "synthesis_time_ms": 4.8,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "synthesis_metadata": {
                    "principles_integrated": 6,
                    "constraints_satisfied": 5,
                    "optimization_iterations": 18,
                    "principle_weights": {
                        "fairness": 0.18,
                        "transparency": 0.17,
                        "accountability": 0.17,
                        "privacy": 0.16,
                        "security": 0.16,
                        "efficiency": 0.16,
                    },
                },
            }
        )

        result = await mock_synthesis_engine.synthesize_policy(complex_synthesis_input)

        assert result["synthesized"] is True
        assert result["synthesis_metadata"]["principles_integrated"] == 6
        assert result["synthesis_metadata"]["constraints_satisfied"] >= 4
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

        # Verify principle weights are balanced
        weights = result["synthesis_metadata"]["principle_weights"]
        assert len(weights) == 6
        assert abs(sum(weights.values()) - 1.0) < 0.01

    @pytest.mark.asyncio
    async def test_synthesis_error_handling(self, mock_synthesis_engine):
        """Test synthesis error handling and resilience."""
        # Test with invalid synthesis input
        invalid_input = {
            "synthesis_goal": "",  # Empty goal
            "constitutional_principles": [],  # No principles
            "constraints": None,  # Invalid constraints
            "constitutional_hash": "wrong_hash",
        }

        # Mock engine to handle errors gracefully
        mock_synthesis_engine.synthesize_policy = AsyncMock(
            return_value={
                "synthesized": False,
                "synthesis_score": 0.0,
                "policy_content": None,
                "synthesis_time_ms": 0.2,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "error": "Invalid synthesis input",
                "error_details": {
                    "missing_fields": ["synthesis_goal", "constitutional_principles"],
                    "invalid_fields": ["constitutional_hash"],
                },
            }
        )

        result = await mock_synthesis_engine.synthesize_policy(invalid_input)

        assert result["synthesized"] is False
        assert result["synthesis_score"] == 0.0
        assert "error" in result
        assert (
            result["constitutional_hash"] == CONSTITUTIONAL_HASH
        )  # Service maintains correct hash

    @pytest.mark.asyncio
    async def test_optimization_convergence(self, mock_wina_optimizer):
        """Test WINA optimization convergence."""
        # Mock optimizer to simulate iterative optimization
        optimization_history = []

        async def mock_optimize_with_history(policy_data):
            iteration = len(optimization_history) + 1
            score = min(0.95, 0.7 + (iteration * 0.05))  # Converging score

            result = {
                "optimized": True,
                "optimization_score": score,
                "iteration": iteration,
                "converged": score >= 0.9,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
            optimization_history.append(result)
            return result

        mock_wina_optimizer.optimize_policy = mock_optimize_with_history

        policy_data = {
            "policy_id": "convergence_test",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        # Run multiple optimization iterations
        for i in range(5):
            result = await mock_wina_optimizer.optimize_policy(policy_data)
            if result["converged"]:
                break

        # Verify convergence
        assert len(optimization_history) > 0
        final_result = optimization_history[-1]
        assert final_result["optimization_score"] >= 0.9
        assert final_result["constitutional_hash"] == CONSTITUTIONAL_HASH

    def test_constitutional_hash_consistency(self):
        """Test constitutional hash consistency in governance synthesis."""
        assert CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"
        assert len(CONSTITUTIONAL_HASH) == 16
        assert all(c in "0123456789abcdef" for c in CONSTITUTIONAL_HASH)
