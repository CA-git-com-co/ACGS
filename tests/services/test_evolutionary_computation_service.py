#!/usr/bin/env python3
"""
Comprehensive Test Suite for Evolutionary Computation Service

Tests the enhanced evolutionary algorithms with:
- Genetic algorithm implementation
- Multi-objective optimization (NSGA-II)
- Constitutional compliance in evolution
- Performance benchmarks
- Edge cases and error handling

Constitutional Hash: cdd01ef066bc6cf2
"""

import os

# Add service path
import sys
import time
from datetime import datetime, timezone
from unittest.mock import patch

import numpy as np
import pytest

# Add service paths to Python path
project_root = os.path.join(os.path.dirname(__file__), "../..")
sys.path.insert(0, project_root)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Try to import real service components
try:
    # Import from the actual evolutionary computation service
    from services.core.evolutionary_computation.app.core.evolution_engine import (
        EvolutionEngine,
    )
    from services.core.evolutionary_computation.app.services.evolution_service import (
        EvolutionService,
    )
    from services.core.evolutionary_computation.app.services.fitness_service import (
        FitnessService,
    )
    from services.core.evolutionary_computation.app.services.hitl_service import (
        HITLService,
    )

    print("✅ Successfully imported real Evolutionary Computation service components")
    REAL_SERVICE_AVAILABLE = True

except ImportError as e:
    print(f"⚠️  Could not import real service components: {e}")
    print("Creating fallback implementations for testing...")
    REAL_SERVICE_AVAILABLE = False

    # Fallback implementations for testing
    class EvolutionService:
        def __init__(self):
            self.constitutional_hash = CONSTITUTIONAL_HASH

        async def evaluate_fitness(self, individual):
            await asyncio.sleep(0.001)
            return {
                "fitness_score": 0.85,
                "constitutional_hash": self.constitutional_hash,
                "metrics": {"performance": 0.9, "compliance": 0.8},
            }

        async def evolve_population(self, population):
            await asyncio.sleep(0.005)
            return {
                "evolved_population": population,
                "generation": 1,
                "constitutional_hash": self.constitutional_hash,
            }

    class FitnessService:
        def __init__(self):
            self.constitutional_hash = CONSTITUTIONAL_HASH

        async def calculate_fitness(self, individual):
            await asyncio.sleep(0.001)
            return 0.85

    class HITLService:
        def __init__(self):
            self.constitutional_hash = CONSTITUTIONAL_HASH

        async def request_human_oversight(self, decision):
            await asyncio.sleep(0.001)
            return {"approved": True, "constitutional_hash": self.constitutional_hash}

    class EvolutionEngine:
        def __init__(self):
            self.constitutional_hash = CONSTITUTIONAL_HASH

        async def run_evolution(self, config):
            await asyncio.sleep(0.010)
            return {
                "success": True,
                "generations": 10,
                "best_fitness": 0.95,
                "constitutional_hash": self.constitutional_hash,
            }


# Create test data structures
class Individual:
    def __init__(self, genes=None, fitness=None):
        self.genes = genes or [0.5, 0.7, 0.3, 0.9]
        self.fitness = fitness or 0.0
        self.constitutional_hash = CONSTITUTIONAL_HASH


class Population:
    def __init__(self, individuals=None, size=50):
        self.individuals = individuals or [Individual() for _ in range(size)]
        self.size = size
        self.constitutional_hash = CONSTITUTIONAL_HASH


class EvolutionConfig:
    def __init__(self, population_size=50, generations=100, mutation_rate=0.1):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.constitutional_hash = CONSTITUTIONAL_HASH


class ConstitutionalConstraint:
    def __init__(self, name, constraint_func):
        self.name = name
        self.constraint_func = constraint_func
        self.constitutional_hash = CONSTITUTIONAL_HASH


class OptimizationObjective:
    def __init__(self, name, objective_func, weight=1.0):
        self.name = name
        self.objective_func = objective_func
        self.weight = weight
        self.constitutional_hash = CONSTITUTIONAL_HASH


class TestGeneticAlgorithm:
    """Test suite for Genetic Algorithm implementation."""

    @pytest.fixture
    def evolution_config(self):
        """Create evolution configuration."""
        return EvolutionConfig(
            population_size=50,
            generations=100,
            mutation_rate=0.1,
            crossover_rate=0.8,
            elite_size=5,
            constitutional_weight=0.3,
        )

    @pytest.fixture
    def genetic_algorithm(self, evolution_config):
        """Create genetic algorithm instance."""
        return GeneticAlgorithm(evolution_config)

    @pytest.fixture
    def sample_population(self):
        """Create sample population for testing."""
        individuals = []
        for i in range(20):
            individual = Individual(
                genome=np.random.rand(10),
                fitness_scores={
                    "performance": np.random.rand(),
                    "efficiency": np.random.rand(),
                    "constitutional_compliance": 0.8 + np.random.rand() * 0.2,
                },
            )
            individuals.append(individual)
        return Population(individuals)

    # Basic Genetic Algorithm Tests

    def test_initialization(self, genetic_algorithm):
        """Test genetic algorithm initialization."""
        assert genetic_algorithm is not None
        assert genetic_algorithm.config.population_size == 50
        assert genetic_algorithm.config.mutation_rate == 0.1
        assert genetic_algorithm.config.constitutional_weight == 0.3

    def test_population_generation(self, genetic_algorithm):
        """Test initial population generation."""
        population = genetic_algorithm.generate_initial_population(genome_size=10)

        assert len(population.individuals) == 50
        assert all(len(ind.genome) == 10 for ind in population.individuals)
        assert all(
            0 <= val <= 1 for ind in population.individuals for val in ind.genome
        )

    def test_fitness_evaluation(self, genetic_algorithm, sample_population):
        """Test fitness evaluation."""

        # Define fitness function
        def fitness_func(genome):
            return {
                "performance": np.mean(genome),
                "efficiency": 1.0 - np.std(genome),
                "constitutional_compliance": 0.9,
            }

        genetic_algorithm.evaluate_fitness(sample_population, fitness_func)

        for individual in sample_population.individuals:
            assert "performance" in individual.fitness_scores
            assert "efficiency" in individual.fitness_scores
            assert "constitutional_compliance" in individual.fitness_scores

    def test_selection_mechanisms(self, genetic_algorithm, sample_population):
        """Test different selection mechanisms."""
        # Tournament selection
        selected = genetic_algorithm.tournament_selection(
            sample_population, tournament_size=3
        )
        assert len(selected) == len(sample_population.individuals)

        # Roulette wheel selection
        selected = genetic_algorithm.roulette_wheel_selection(sample_population)
        assert len(selected) == len(sample_population.individuals)

        # Rank selection
        selected = genetic_algorithm.rank_selection(sample_population)
        assert len(selected) == len(sample_population.individuals)

    def test_crossover_operations(self, genetic_algorithm):
        """Test crossover operations."""
        parent1 = Individual(genome=np.array([1, 2, 3, 4, 5]))
        parent2 = Individual(genome=np.array([6, 7, 8, 9, 10]))

        # Single-point crossover
        child1, child2 = genetic_algorithm.single_point_crossover(parent1, parent2)
        assert len(child1.genome) == len(parent1.genome)
        assert len(child2.genome) == len(parent2.genome)

        # Two-point crossover
        child1, child2 = genetic_algorithm.two_point_crossover(parent1, parent2)
        assert len(child1.genome) == len(parent1.genome)

        # Uniform crossover
        child1, child2 = genetic_algorithm.uniform_crossover(parent1, parent2)
        assert all(
            val in [parent1.genome[i], parent2.genome[i]]
            for i, val in enumerate(child1.genome)
        )

    def test_mutation_operations(self, genetic_algorithm):
        """Test mutation operations."""
        individual = Individual(genome=np.array([0.5] * 10))

        # Gaussian mutation
        mutated = genetic_algorithm.gaussian_mutation(individual, mutation_rate=1.0)
        assert not np.array_equal(individual.genome, mutated.genome)
        assert len(mutated.genome) == len(individual.genome)

        # Uniform mutation
        mutated = genetic_algorithm.uniform_mutation(individual, mutation_rate=1.0)
        assert not np.array_equal(individual.genome, mutated.genome)

        # Polynomial mutation
        mutated = genetic_algorithm.polynomial_mutation(individual, mutation_rate=1.0)
        assert not np.array_equal(individual.genome, mutated.genome)

    def test_elitism(self, genetic_algorithm, sample_population):
        """Test elitism preservation."""
        # Get elite individuals
        elite = genetic_algorithm.get_elite_individuals(sample_population, elite_size=5)

        assert len(elite) == 5

        # Elite should be the best individuals
        population_sorted = sorted(
            sample_population.individuals,
            key=genetic_algorithm.calculate_overall_fitness,
            reverse=True,
        )

        elite_fitness = [
            genetic_algorithm.calculate_overall_fitness(ind) for ind in elite
        ]
        top_fitness = [
            genetic_algorithm.calculate_overall_fitness(ind)
            for ind in population_sorted[:5]
        ]

        assert elite_fitness == top_fitness

    # Constitutional Compliance Tests

    def test_constitutional_constraints(self, genetic_algorithm):
        """Test constitutional constraint enforcement."""
        constraint = ConstitutionalConstraint(
            principle="human_dignity", min_score=0.8, weight=0.3
        )

        # Valid individual
        valid_individual = Individual(
            genome=np.random.rand(10),
            fitness_scores={"constitutional_compliance": 0.85},
        )
        assert genetic_algorithm.satisfies_constraint(valid_individual, constraint)

        # Invalid individual
        invalid_individual = Individual(
            genome=np.random.rand(10), fitness_scores={"constitutional_compliance": 0.7}
        )
        assert not genetic_algorithm.satisfies_constraint(
            invalid_individual, constraint
        )

    def test_constitutional_fitness_weighting(self, genetic_algorithm):
        """Test constitutional compliance in fitness calculation."""
        individual1 = Individual(
            genome=np.random.rand(10),
            fitness_scores={
                "performance": 0.9,
                "efficiency": 0.8,
                "constitutional_compliance": 0.6,  # Low compliance
            },
        )

        individual2 = Individual(
            genome=np.random.rand(10),
            fitness_scores={
                "performance": 0.7,
                "efficiency": 0.7,
                "constitutional_compliance": 0.95,  # High compliance
            },
        )

        fitness1 = genetic_algorithm.calculate_overall_fitness(individual1)
        fitness2 = genetic_algorithm.calculate_overall_fitness(individual2)

        # Individual 2 should have higher fitness due to constitutional compliance
        assert fitness2 > fitness1

    # Evolution Process Tests

    async def test_complete_evolution_cycle(self, genetic_algorithm):
        """Test complete evolution cycle."""

        # Define optimization problem
        def fitness_function(genome):
            # Maximize sum while maintaining diversity
            return {
                "performance": np.sum(genome),
                "efficiency": 1.0 / (1.0 + np.std(genome)),
                "constitutional_compliance": min(0.95, np.mean(genome) + 0.5),
            }

        # Run evolution
        initial_population = genetic_algorithm.generate_initial_population(
            genome_size=10
        )

        best_individual, final_population = await genetic_algorithm.evolve(
            initial_population, fitness_function, generations=20
        )

        assert best_individual is not None
        assert final_population is not None
        assert len(final_population.individuals) == 50

        # Check improvement
        initial_best = max(
            initial_population.individuals,
            key=genetic_algorithm.calculate_overall_fitness,
        )

        assert genetic_algorithm.calculate_overall_fitness(
            best_individual
        ) >= genetic_algorithm.calculate_overall_fitness(initial_best)

    @pytest.mark.performance
    async def test_evolution_performance(self, genetic_algorithm):
        """Test evolution performance."""

        def simple_fitness(genome):
            return {"performance": np.mean(genome), "constitutional_compliance": 0.9}

        population = genetic_algorithm.generate_initial_population(genome_size=50)

        start_time = time.time()
        best, final_pop = await genetic_algorithm.evolve(
            population, simple_fitness, generations=50
        )
        end_time = time.time()

        evolution_time = end_time - start_time
        assert evolution_time < 10.0  # Should complete in under 10 seconds

        print(f"Evolution completed in {evolution_time:.2f} seconds")
        print(f"Best fitness: {genetic_algorithm.calculate_overall_fitness(best):.4f}")


class TestMultiObjectiveEvolution:
    """Test suite for Multi-Objective Evolution (NSGA-II)."""

    @pytest.fixture
    def multi_objective_algorithm(self):
        """Create multi-objective evolution instance."""
        config = EvolutionConfig(
            population_size=100, generations=50, mutation_rate=0.1, crossover_rate=0.9
        )
        return MultiObjectiveEvolution(config)

    @pytest.fixture
    def multi_objective_population(self):
        """Create population with multiple objectives."""
        individuals = []
        for i in range(50):
            individual = Individual(
                genome=np.random.rand(10),
                fitness_scores={
                    OptimizationObjective.PERFORMANCE.value: np.random.rand(),
                    OptimizationObjective.CONSTITUTIONAL_COMPLIANCE.value: (
                        0.7 + np.random.rand() * 0.3
                    ),
                    OptimizationObjective.RESOURCE_EFFICIENCY.value: np.random.rand(),
                    OptimizationObjective.SAFETY.value: 0.8 + np.random.rand() * 0.2,
                    OptimizationObjective.EXPLAINABILITY.value: np.random.rand(),
                    OptimizationObjective.ROBUSTNESS.value: np.random.rand(),
                    OptimizationObjective.ADAPTABILITY.value: np.random.rand(),
                },
            )
            individuals.append(individual)
        return Population(individuals)

    def test_dominance_calculation(self, multi_objective_algorithm):
        """Test Pareto dominance calculation."""
        # Individual 1 dominates Individual 2
        ind1 = Individual(
            genome=np.random.rand(5),
            fitness_scores={
                OptimizationObjective.PERFORMANCE.value: 0.9,
                OptimizationObjective.SAFETY.value: 0.8,
            },
        )

        ind2 = Individual(
            genome=np.random.rand(5),
            fitness_scores={
                OptimizationObjective.PERFORMANCE.value: 0.7,
                OptimizationObjective.SAFETY.value: 0.6,
            },
        )

        assert multi_objective_algorithm.dominates(ind1, ind2)
        assert not multi_objective_algorithm.dominates(ind2, ind1)

    def test_non_dominated_sorting(
        self, multi_objective_algorithm, multi_objective_population
    ):
        """Test non-dominated sorting (NSGA-II)."""
        fronts = multi_objective_algorithm.non_dominated_sort(
            multi_objective_population
        )

        assert len(fronts) > 0
        assert len(fronts[0]) > 0  # First front should have at least one individual

        # All individuals should be assigned to a front
        total_individuals = sum(len(front) for front in fronts)
        assert total_individuals == len(multi_objective_population.individuals)

        # Verify dominance relationships
        for i, front in enumerate(fronts[:-1]):
            next_front = fronts[i + 1]
            for ind1 in front:
                for ind2 in next_front:
                    # No individual in next front should dominate any in current front
                    assert not multi_objective_algorithm.dominates(ind2, ind1)

    def test_crowding_distance(self, multi_objective_algorithm):
        """Test crowding distance calculation."""
        # Create individuals with known positions
        individuals = []
        positions = [(0, 0), (1, 0), (0, 1), (0.5, 0.5), (1, 1)]

        for i, (x, y) in enumerate(positions):
            ind = Individual(
                genome=np.array([x, y]), fitness_scores={"obj1": x, "obj2": y}
            )
            individuals.append(ind)

        distances = multi_objective_algorithm.calculate_crowding_distance(individuals)

        assert len(distances) == len(individuals)
        # Corner individuals should have infinite distance
        assert distances[0] == float("inf") or distances[0] > 1000
        assert distances[4] == float("inf") or distances[4] > 1000

    def test_pareto_front_extraction(
        self, multi_objective_algorithm, multi_objective_population
    ):
        """Test Pareto front extraction."""
        pareto_front = multi_objective_algorithm.get_pareto_front(
            multi_objective_population
        )

        assert len(pareto_front) > 0

        # No individual in Pareto front should be dominated by any other
        for i, ind1 in enumerate(pareto_front):
            for j, ind2 in enumerate(pareto_front):
                if i != j:
                    assert not multi_objective_algorithm.dominates(ind2, ind1)

    async def test_multi_objective_evolution(self, multi_objective_algorithm):
        """Test complete multi-objective evolution."""

        # Define multi-objective problem
        def multi_objective_fitness(genome):
            # Conflicting objectives
            return {
                OptimizationObjective.PERFORMANCE.value: np.sum(genome),  # Maximize
                OptimizationObjective.RESOURCE_EFFICIENCY.value: 1.0
                / (1.0 + np.sum(genome)),  # Minimize resource use
                OptimizationObjective.CONSTITUTIONAL_COMPLIANCE.value: 0.9,
                OptimizationObjective.SAFETY.value: 1.0
                - np.std(genome),  # Minimize variance
                OptimizationObjective.EXPLAINABILITY.value: 1.0 / (1.0 + len(genome)),
            }

        initial_population = multi_objective_algorithm.generate_initial_population(
            genome_size=10
        )

        (
            pareto_front,
            final_population,
        ) = await multi_objective_algorithm.evolve_multi_objective(
            initial_population, multi_objective_fitness, generations=20
        )

        assert len(pareto_front) > 0
        assert len(final_population.individuals) == 100

        # Verify diversity in Pareto front
        objectives = [ind.fitness_scores for ind in pareto_front]
        performance_values = [
            obj[OptimizationObjective.PERFORMANCE.value] for obj in objectives
        ]
        efficiency_values = [
            obj[OptimizationObjective.RESOURCE_EFFICIENCY.value] for obj in objectives
        ]

        assert max(performance_values) > min(
            performance_values
        )  # Diversity in performance
        assert max(efficiency_values) > min(
            efficiency_values
        )  # Diversity in efficiency

    def test_objective_weights(self, multi_objective_algorithm):
        """Test objective weight configurations."""
        weights = multi_objective_algorithm.get_objective_weights()

        assert OptimizationObjective.CONSTITUTIONAL_COMPLIANCE.value in weights
        assert (
            weights[OptimizationObjective.CONSTITUTIONAL_COMPLIANCE.value] >= 0.2
        )  # High importance

        # Test custom weights
        custom_weights = {
            OptimizationObjective.PERFORMANCE.value: 0.3,
            OptimizationObjective.SAFETY.value: 0.4,
            OptimizationObjective.CONSTITUTIONAL_COMPLIANCE.value: 0.3,
        }

        multi_objective_algorithm.set_objective_weights(custom_weights)
        assert multi_objective_algorithm.get_objective_weights() == custom_weights


class TestEvolutionConstraints:
    """Test suite for evolution constraints and safety mechanisms."""

    @pytest.fixture
    def constrained_algorithm(self):
        """Create algorithm with constraints."""
        config = EvolutionConfig(
            population_size=30,
            generations=10,
            mutation_rate=0.05,
            safety_threshold=0.8,
            constitutional_threshold=0.85,
        )
        return GeneticAlgorithm(config)

    def test_safety_constraints(self, constrained_algorithm):
        """Test safety constraint enforcement."""
        # Safe individual
        safe_ind = Individual(
            genome=np.random.rand(10),
            fitness_scores={"safety": 0.85, "performance": 0.9},
        )
        assert constrained_algorithm.is_safe(safe_ind)

        # Unsafe individual
        unsafe_ind = Individual(
            genome=np.random.rand(10),
            fitness_scores={"safety": 0.7, "performance": 0.95},
        )
        assert not constrained_algorithm.is_safe(unsafe_ind)

    def test_constitutional_compliance_constraints(self, constrained_algorithm):
        """Test constitutional compliance constraints."""
        # Compliant individual
        compliant_ind = Individual(
            genome=np.random.rand(10), fitness_scores={"constitutional_compliance": 0.9}
        )
        assert constrained_algorithm.is_constitutionally_compliant(compliant_ind)

        # Non-compliant individual
        non_compliant_ind = Individual(
            genome=np.random.rand(10), fitness_scores={"constitutional_compliance": 0.8}
        )
        assert not constrained_algorithm.is_constitutionally_compliant(
            non_compliant_ind
        )

    async def test_constrained_evolution(self, constrained_algorithm):
        """Test evolution with constraints."""

        def constrained_fitness(genome):
            return {
                "performance": np.mean(genome),
                "safety": 0.7 + np.random.rand() * 0.3,  # Variable safety
                "constitutional_compliance": 0.8 + np.random.rand() * 0.2,
            }

        population = constrained_algorithm.generate_initial_population(genome_size=10)

        best, final_pop = await constrained_algorithm.evolve_with_constraints(
            population, constrained_fitness, generations=10
        )

        # Best individual should satisfy all constraints
        assert constrained_algorithm.is_safe(best)
        assert constrained_algorithm.is_constitutionally_compliant(best)


class TestEvolutionaryServiceIntegration:
    """Integration tests for the evolutionary computation service."""

    @pytest.fixture
    async def mock_agent_request(self):
        """Create mock agent optimization request."""
        return {
            "agent_id": "agent_123",
            "optimization_type": "capability_enhancement",
            "objectives": [
                "performance",
                "constitutional_compliance",
                "safety",
                "resource_efficiency",
            ],
            "constraints": {
                "min_constitutional_compliance": 0.85,
                "min_safety": 0.8,
                "max_resource_usage": 0.7,
            },
            "current_metrics": {
                "performance": 0.7,
                "safety": 0.85,
                "constitutional_compliance": 0.9,
            },
        }

    @patch("evolutionary_algorithms.agent_repository")
    async def test_agent_optimization_request(self, mock_repo, mock_agent_request):
        """Test agent optimization request handling."""
        # Mock agent data
        mock_repo.get_agent.return_value = {
            "id": "agent_123",
            "genome": np.random.rand(50).tolist(),
            "capabilities": ["reasoning", "planning"],
        }

        # Create service handler
        from unified_main import optimize_agent_evolutionary

        # Process request
        result = await optimize_agent_evolutionary(mock_agent_request)

        assert result is not None
        assert "optimization_id" in result
        assert result["status"] == "started"
        assert result["agent_id"] == "agent_123"

    async def test_optimization_result_tracking(self):
        """Test tracking of optimization results."""
        # Create optimization tracker
        from evolutionary_algorithms import OptimizationTracker

        tracker = OptimizationTracker()

        # Track optimization
        optimization_id = "opt_123"
        tracker.start_optimization(
            optimization_id,
            {
                "agent_id": "agent_123",
                "start_time": datetime.now(timezone.utc),
                "objectives": ["performance", "safety"],
            },
        )

        # Update progress
        tracker.update_progress(
            optimization_id,
            {"generation": 10, "best_fitness": 0.85, "population_diversity": 0.6},
        )

        # Complete optimization
        tracker.complete_optimization(
            optimization_id,
            {
                "best_genome": np.random.rand(10).tolist(),
                "final_fitness": 0.9,
                "improvements": {"performance": 0.2, "safety": 0.05},
            },
        )

        # Verify tracking
        status = tracker.get_optimization_status(optimization_id)
        assert status["status"] == "completed"
        assert status["final_fitness"] == 0.9


# Performance Benchmarks


class TestEvolutionPerformance:
    """Performance benchmarks for evolutionary algorithms."""

    @pytest.mark.benchmark
    def test_large_population_performance(self, benchmark):
        """Benchmark large population handling."""
        config = EvolutionConfig(population_size=1000, generations=1, mutation_rate=0.1)
        algorithm = GeneticAlgorithm(config)

        def setup():
            return algorithm.generate_initial_population(genome_size=100)

        def evolution_step(population):
            # Simulate one generation
            algorithm.evaluate_fitness(population, lambda g: {"fitness": np.mean(g)})
            selected = algorithm.tournament_selection(population)
            return selected

        result = benchmark.pedantic(evolution_step, setup=setup, rounds=10)
        assert result is not None

    @pytest.mark.benchmark
    def test_complex_fitness_performance(self, benchmark):
        """Benchmark complex fitness evaluation."""

        def complex_fitness(genome):
            # Simulate complex computation
            return {
                "obj1": np.sum(genome**2),
                "obj2": np.prod(1 + genome),
                "obj3": np.linalg.norm(genome),
                "obj4": np.std(genome),
                "obj5": 1.0 / (1.0 + np.sum(np.abs(genome - 0.5))),
            }

        genome = np.random.rand(100)
        result = benchmark(complex_fitness, genome)
        assert len(result) == 5


# Pytest configuration


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    config.addinivalue_line("markers", "stress: mark test as a stress test")
    config.addinivalue_line("markers", "benchmark: mark test as a benchmark")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
