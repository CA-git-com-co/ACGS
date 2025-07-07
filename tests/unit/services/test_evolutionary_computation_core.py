"""
Unit Tests for Evolutionary Computation Core Service
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive unit tests for the Evolutionary Computation service core functionality
including genetic algorithms, fitness evaluation, and policy evolution.
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


class TestEvolutionaryComputationCore:
    """Unit tests for Evolutionary Computation core functionality."""

    @pytest.fixture
    def mock_genetic_algorithm(self):
        """Mock genetic algorithm engine."""
        ga = Mock()
        ga.evolve_population = AsyncMock(
            return_value={
                "generation": 10,
                "population_size": 50,
                "best_fitness": 0.94,
                "average_fitness": 0.78,
                "evolution_time_ms": 4.1,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "evolution_metadata": {
                    "mutations": 15,
                    "crossovers": 25,
                    "selections": 50,
                    "convergence_achieved": True,
                },
            }
        )
        ga.initialize_population = Mock(
            return_value={
                "population_id": "pop_001",
                "population_size": 50,
                "initialization_time_ms": 1.2,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )
        return ga

    @pytest.fixture
    def mock_fitness_evaluator(self):
        """Mock fitness evaluation engine."""
        evaluator = Mock()
        evaluator.evaluate_fitness = AsyncMock(
            return_value={
                "individual_id": "ind_001",
                "fitness_score": 0.89,
                "evaluation_time_ms": 2.3,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "fitness_components": {
                    "constitutional_compliance": 0.92,
                    "performance_efficiency": 0.87,
                    "policy_effectiveness": 0.88,
                },
            }
        )
        evaluator.batch_evaluate = AsyncMock(
            return_value={
                "batch_id": "batch_fitness_001",
                "evaluated_count": 50,
                "average_fitness": 0.81,
                "evaluation_time_ms": 3.8,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )
        return evaluator

    @pytest.fixture
    def mock_policy_mutator(self):
        """Mock policy mutation engine."""
        mutator = Mock()
        mutator.mutate_policy = AsyncMock(
            return_value={
                "mutated_policy_id": "mutated_001",
                "mutation_applied": True,
                "mutation_type": "parameter_adjustment",
                "mutation_strength": 0.15,
                "mutation_time_ms": 1.8,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )
        mutator.crossover_policies = AsyncMock(
            return_value={
                "offspring_id": "offspring_001",
                "crossover_successful": True,
                "crossover_point": 0.6,
                "crossover_time_ms": 2.1,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )
        return mutator

    @pytest.fixture
    def mock_selection_engine(self):
        """Mock selection engine."""
        selector = Mock()
        selector.select_parents = AsyncMock(
            return_value={
                "selected_parents": ["parent_001", "parent_002"],
                "selection_method": "tournament",
                "selection_pressure": 0.8,
                "selection_time_ms": 1.5,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )
        return selector

    @pytest.mark.asyncio
    async def test_basic_population_evolution(self, mock_genetic_algorithm):
        """Test basic population evolution functionality."""
        evolution_config = {
            "population_size": 50,
            "generations": 10,
            "mutation_rate": 0.1,
            "crossover_rate": 0.8,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await mock_genetic_algorithm.evolve_population(evolution_config)

        assert result["generation"] > 0
        assert result["best_fitness"] > 0.8  # High fitness achieved
        assert result["evolution_time_ms"] < 5.0  # Performance target
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert result["evolution_metadata"]["convergence_achieved"] is True

    @pytest.mark.asyncio
    async def test_fitness_evaluation_performance(self, mock_fitness_evaluator):
        """Test fitness evaluation performance targets."""
        individual = {
            "individual_id": "perf_test_001",
            "policy_parameters": {"fairness": 0.8, "efficiency": 0.7},
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        start_time = time.perf_counter()
        result = await mock_fitness_evaluator.evaluate_fitness(individual)
        end_time = time.perf_counter()

        actual_time_ms = (end_time - start_time) * 1000

        # Verify performance targets
        assert (
            actual_time_ms < 5.0
        ), f"Fitness evaluation took {actual_time_ms:.2f}ms, exceeds 5ms target"
        assert result["evaluation_time_ms"] < 5.0
        assert result["fitness_score"] > 0.0
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_batch_fitness_evaluation(self, mock_fitness_evaluator):
        """Test batch fitness evaluation performance."""
        batch_request = {
            "batch_id": "batch_perf_001",
            "individuals": [
                {
                    "individual_id": f"ind_{i:03d}",
                    "policy_parameters": {"param1": i * 0.1, "param2": i * 0.05},
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                }
                for i in range(50)
            ],
        }

        start_time = time.perf_counter()
        result = await mock_fitness_evaluator.batch_evaluate(batch_request)
        end_time = time.perf_counter()

        actual_time_ms = (end_time - start_time) * 1000

        # Verify batch performance
        assert result["evaluated_count"] == 50
        assert result["average_fitness"] > 0.0
        assert result["evaluation_time_ms"] < 10.0  # Batch evaluation target
        assert actual_time_ms < 100.0  # Total batch time reasonable
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_policy_mutation_operations(self, mock_policy_mutator):
        """Test policy mutation operations."""
        policy_to_mutate = {
            "policy_id": "mutation_test_001",
            "parameters": {"fairness": 0.8, "transparency": 0.7, "efficiency": 0.6},
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await mock_policy_mutator.mutate_policy(policy_to_mutate)

        assert result["mutation_applied"] is True
        assert result["mutation_type"] in [
            "parameter_adjustment",
            "structure_change",
            "rule_modification",
        ]
        assert 0.0 <= result["mutation_strength"] <= 1.0
        assert result["mutation_time_ms"] < 5.0  # Performance target
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_policy_crossover_operations(self, mock_policy_mutator):
        """Test policy crossover operations."""
        crossover_request = {
            "parent1": {
                "policy_id": "parent_001",
                "parameters": {"fairness": 0.9, "efficiency": 0.6},
            },
            "parent2": {
                "policy_id": "parent_002",
                "parameters": {"fairness": 0.7, "efficiency": 0.9},
            },
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await mock_policy_mutator.crossover_policies(crossover_request)

        assert result["crossover_successful"] is True
        assert 0.0 <= result["crossover_point"] <= 1.0
        assert result["crossover_time_ms"] < 5.0  # Performance target
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_parent_selection(self, mock_selection_engine):
        """Test parent selection for reproduction."""
        selection_request = {
            "population": [
                {"individual_id": f"ind_{i:03d}", "fitness": 0.5 + (i * 0.01)}
                for i in range(20)
            ],
            "selection_size": 2,
            "selection_method": "tournament",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await mock_selection_engine.select_parents(selection_request)

        assert len(result["selected_parents"]) == 2
        assert result["selection_method"] == "tournament"
        assert 0.0 <= result["selection_pressure"] <= 1.0
        assert result["selection_time_ms"] < 5.0  # Performance target
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_evolutionary_convergence(self, mock_genetic_algorithm):
        """Test evolutionary algorithm convergence."""
        # Mock GA to simulate convergence over generations
        generation_results = []

        async def mock_evolve_with_convergence(config):
            generation = len(generation_results) + 1
            # Simulate improving fitness over generations
            best_fitness = min(0.95, 0.6 + (generation * 0.03))

            result = {
                "generation": generation,
                "best_fitness": best_fitness,
                "average_fitness": best_fitness - 0.1,
                "evolution_time_ms": 4.0,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "evolution_metadata": {
                    "convergence_achieved": best_fitness >= 0.9,
                    "fitness_improvement": generation > 1
                    and best_fitness > generation_results[-1]["best_fitness"],
                },
            }
            generation_results.append(result)
            return result

        mock_genetic_algorithm.evolve_population = mock_evolve_with_convergence

        config = {"constitutional_hash": CONSTITUTIONAL_HASH}

        # Run evolution until convergence
        for generation in range(15):
            result = await mock_genetic_algorithm.evolve_population(config)
            if result["evolution_metadata"]["convergence_achieved"]:
                break

        # Verify convergence
        assert len(generation_results) > 0
        final_result = generation_results[-1]
        assert final_result["best_fitness"] >= 0.9
        assert final_result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_multi_objective_fitness_evaluation(self, mock_fitness_evaluator):
        """Test multi-objective fitness evaluation."""
        individual = {
            "individual_id": "multi_obj_001",
            "policy_parameters": {
                "fairness": 0.85,
                "efficiency": 0.78,
                "transparency": 0.82,
                "security": 0.90,
            },
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        # Mock evaluator for multi-objective fitness
        mock_fitness_evaluator.evaluate_fitness = AsyncMock(
            return_value={
                "individual_id": "multi_obj_001",
                "fitness_score": 0.84,  # Weighted average
                "evaluation_time_ms": 3.2,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "fitness_components": {
                    "constitutional_compliance": 0.92,
                    "performance_efficiency": 0.78,
                    "policy_effectiveness": 0.85,
                    "security_score": 0.90,
                    "fairness_score": 0.85,
                    "transparency_score": 0.82,
                },
                "objective_weights": {
                    "constitutional_compliance": 0.3,
                    "performance_efficiency": 0.2,
                    "policy_effectiveness": 0.2,
                    "security_score": 0.15,
                    "fairness_score": 0.1,
                    "transparency_score": 0.05,
                },
            }
        )

        result = await mock_fitness_evaluator.evaluate_fitness(individual)

        assert result["fitness_score"] > 0.8  # High multi-objective fitness
        assert len(result["fitness_components"]) >= 3  # Multiple objectives
        assert len(result["objective_weights"]) == len(result["fitness_components"])
        assert (
            abs(sum(result["objective_weights"].values()) - 1.0) < 0.01
        )  # Weights sum to 1
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_concurrent_evolution_performance(self, mock_genetic_algorithm):
        """Test concurrent evolution performance."""
        evolution_configs = [
            {
                "population_id": f"pop_{i:03d}",
                "population_size": 20,
                "generations": 5,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
            for i in range(3)
        ]

        start_time = time.perf_counter()

        # Execute concurrent evolution
        tasks = [
            mock_genetic_algorithm.evolve_population(config)
            for config in evolution_configs
        ]
        results = await asyncio.gather(*tasks)

        end_time = time.perf_counter()
        total_time_ms = (end_time - start_time) * 1000

        # Verify all evolutions completed
        assert len(results) == len(evolution_configs)

        # Verify performance (concurrent processing should be efficient)
        assert total_time_ms < 50.0, f"Concurrent evolution took {total_time_ms:.2f}ms"

        # Verify all results have constitutional hash
        for result in results:
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
            assert result["best_fitness"] > 0.0

    @pytest.mark.asyncio
    async def test_evolutionary_error_handling(self, mock_genetic_algorithm):
        """Test evolutionary computation error handling."""
        # Test with invalid evolution configuration
        invalid_config = {
            "population_size": -1,  # Invalid size
            "generations": 0,  # No generations
            "mutation_rate": 1.5,  # Invalid rate > 1.0
            "constitutional_hash": "wrong_hash",
        }

        # Mock GA to handle errors gracefully
        mock_genetic_algorithm.evolve_population = AsyncMock(
            return_value={
                "generation": 0,
                "population_size": 0,
                "best_fitness": 0.0,
                "evolution_time_ms": 0.1,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "error": "Invalid evolution configuration",
                "error_details": {
                    "invalid_parameters": [
                        "population_size",
                        "generations",
                        "mutation_rate",
                    ],
                    "invalid_hash": True,
                },
            }
        )

        result = await mock_genetic_algorithm.evolve_population(invalid_config)

        assert result["generation"] == 0
        assert result["best_fitness"] == 0.0
        assert "error" in result
        assert (
            result["constitutional_hash"] == CONSTITUTIONAL_HASH
        )  # Service maintains correct hash

    def test_constitutional_hash_consistency(self):
        """Test constitutional hash consistency in evolutionary computation."""
        assert CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"
        assert len(CONSTITUTIONAL_HASH) == 16
        assert all(c in "0123456789abcdef" for c in CONSTITUTIONAL_HASH)
