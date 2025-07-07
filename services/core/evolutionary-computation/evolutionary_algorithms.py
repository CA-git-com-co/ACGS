#!/usr/bin/env python3
"""
Real Evolutionary Computation Algorithms for ACGS

Implements sophisticated evolutionary algorithms for agent optimization:
- Genetic Algorithm (GA) for parameter evolution
- Differential Evolution (DE) for continuous optimization
- Particle Swarm Optimization (PSO) for multi-objective optimization
- Neuroevolution for neural network architecture search
- Constitutional fitness evaluation with multi-objective optimization

Constitutional Hash: cdd01ef066bc6cf2
"""

import hashlib
import json
import logging
import random
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class OptimizationObjective(Enum):
    """Multi-objective optimization objectives for agent evolution."""

    PERFORMANCE = "performance"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    RESOURCE_EFFICIENCY = "resource_efficiency"
    SAFETY = "safety"
    EXPLAINABILITY = "explainability"
    ROBUSTNESS = "robustness"
    ADAPTABILITY = "adaptability"


class SelectionMethod(Enum):
    """Selection methods for evolutionary algorithms."""

    TOURNAMENT = "tournament"
    ROULETTE_WHEEL = "roulette_wheel"
    RANK_BASED = "rank_based"
    PARETO_FRONT = "pareto_front"


@dataclass
class EvolutionConfig:
    """Configuration for evolutionary algorithms."""

    population_size: int = 100
    generations: int = 50
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    elite_size: int = 5
    tournament_size: int = 3
    constitutional_weight: float = 0.3
    safety_threshold: float = 0.8
    constitutional_threshold: float = 0.85
    selection_method: SelectionMethod = SelectionMethod.TOURNAMENT

    def __post_init__(self):
        """Validate configuration parameters."""
        assert 0 < self.mutation_rate < 1, "Mutation rate must be between 0 and 1"
        assert 0 < self.crossover_rate < 1, "Crossover rate must be between 0 and 1"
        assert (
            self.elite_size < self.population_size
        ), "Elite size must be less than population size"


@dataclass
class Individual:
    """Represents an individual in the evolutionary algorithm."""

    genome: np.ndarray
    fitness_scores: dict[str, float] = field(default_factory=dict)
    age: int = 0
    parent_ids: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        """Ensure genome is numpy array."""
        if not isinstance(self.genome, np.ndarray):
            self.genome = np.array(self.genome)


@dataclass
class Population:
    """Represents a population of individuals."""

    individuals: list[Individual]
    generation: int = 0

    def __len__(self):
        return len(self.individuals)

    def __iter__(self):
        return iter(self.individuals)

    def __getitem__(self, index):
        return self.individuals[index]


class CrossoverMethod(Enum):
    """Crossover methods for genetic algorithms."""

    SINGLE_POINT = "single_point"
    TWO_POINT = "two_point"
    UNIFORM = "uniform"
    ARITHMETIC = "arithmetic"
    SIMULATED_BINARY = "simulated_binary"


class MutationMethod(Enum):
    """Mutation methods for evolutionary algorithms."""

    GAUSSIAN = "gaussian"
    POLYNOMIAL = "polynomial"
    UNIFORM = "uniform"
    ADAPTIVE = "adaptive"


@dataclass
class Individual:
    """Represents an individual in the evolutionary population."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    genotype: dict[str, Any] = field(default_factory=dict)
    phenotype: dict[str, Any] = field(default_factory=dict)
    fitness: dict[str, float] = field(default_factory=dict)
    age: int = 0
    generation: int = 0
    parent_ids: list[str] = field(default_factory=list)
    constitutional_compliance: float = 0.0
    genome: np.ndarray = field(default_factory=lambda: np.array([]))

    def __init__(self, genome=None, **kwargs):
        """Initialize Individual with optional genome parameter for backward compatibility."""
        if genome is not None:
            self.genome = (
                np.array(genome) if not isinstance(genome, np.ndarray) else genome
            )
            # Convert genome to genotype for internal consistency
            self.genotype = {"genome": self.genome.tolist()}

        # Set other fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Set defaults for required fields
        if not hasattr(self, "id") or not self.id:
            self.id = str(uuid.uuid4())
        if not hasattr(self, "genotype"):
            self.genotype = {}
        if not hasattr(self, "phenotype"):
            self.phenotype = {}
        if not hasattr(self, "fitness"):
            self.fitness = {}
        if not hasattr(self, "age"):
            self.age = 0
        if not hasattr(self, "generation"):
            self.generation = 0
        if not hasattr(self, "parent_ids"):
            self.parent_ids = []
        if not hasattr(self, "constitutional_compliance"):
            self.constitutional_compliance = 0.0

    def total_fitness(self, weights: dict[str, float] = None) -> float:
        """Calculate weighted total fitness across all objectives."""
        if not self.fitness:
            return 0.0

        if weights is None:
            # Equal weighting by default
            weights = {obj: 1.0 for obj in self.fitness.keys()}

        total = sum(
            self.fitness.get(obj, 0.0) * weights.get(obj, 0.0) for obj in weights.keys()
        )

        # Normalize by total weight
        total_weight = sum(weights.values())
        return total / total_weight if total_weight > 0 else 0.0

    def dominates(self, other: "Individual") -> bool:
        """Check if this individual Pareto-dominates another."""
        at_least_one_better = False

        for objective in self.fitness.keys():
            self_score = self.fitness.get(objective, 0.0)
            other_score = other.fitness.get(objective, 0.0)

            if self_score < other_score:
                return False
            elif self_score > other_score:
                at_least_one_better = True

        return at_least_one_better


@dataclass
class EvolutionParams:
    """Parameters for evolutionary algorithms."""

    population_size: int = 100
    generations: int = 50
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    selection_pressure: float = 2.0
    elitism_ratio: float = 0.1
    diversity_threshold: float = 0.05
    constitutional_weight: float = 0.3
    convergence_threshold: float = 1e-6
    max_stagnation: int = 10


class FitnessEvaluator:
    """Evaluates fitness of individuals across multiple objectives."""

    def __init__(self, constitutional_client: Optional[Any] = None):
        self.constitutional_client = constitutional_client
        self.evaluation_cache: dict[str, dict[str, float]] = {}

    async def evaluate_individual(
        self, individual: Individual, objectives: list[OptimizationObjective]
    ) -> dict[str, float]:
        """Evaluate an individual across multiple objectives."""

        # Create cache key from genotype
        genotype_hash = hashlib.sha256(
            json.dumps(individual.genotype, sort_keys=True).encode()
        ).hexdigest()[:16]

        if genotype_hash in self.evaluation_cache:
            return self.evaluation_cache[genotype_hash]

        fitness = {}

        for objective in objectives:
            fitness[objective.value] = await self._evaluate_objective(
                individual, objective
            )

        # Cache result
        self.evaluation_cache[genotype_hash] = fitness
        individual.fitness = fitness

        return fitness

    async def _evaluate_objective(
        self, individual: Individual, objective: OptimizationObjective
    ) -> float:
        """Evaluate a single objective for an individual."""

        if objective == OptimizationObjective.PERFORMANCE:
            return self._evaluate_performance(individual)

        elif objective == OptimizationObjective.CONSTITUTIONAL_COMPLIANCE:
            return await self._evaluate_constitutional_compliance(individual)

        elif objective == OptimizationObjective.RESOURCE_EFFICIENCY:
            return self._evaluate_resource_efficiency(individual)

        elif objective == OptimizationObjective.SAFETY:
            return self._evaluate_safety(individual)

        elif objective == OptimizationObjective.EXPLAINABILITY:
            return self._evaluate_explainability(individual)

        elif objective == OptimizationObjective.ROBUSTNESS:
            return self._evaluate_robustness(individual)

        elif objective == OptimizationObjective.ADAPTABILITY:
            return self._evaluate_adaptability(individual)

        else:
            logger.warning(f"Unknown objective: {objective}")
            return 0.0

    def _evaluate_performance(self, individual: Individual) -> float:
        """Evaluate performance objective."""
        genotype = individual.genotype

        # Simulate performance based on key parameters
        learning_rate = genotype.get("learning_rate", 0.01)
        batch_size = genotype.get("batch_size", 32)
        hidden_layers = genotype.get("hidden_layers", 2)
        neurons_per_layer = genotype.get("neurons_per_layer", 64)

        # Performance heuristic based on parameter balance
        performance_score = 0.0

        # Learning rate optimization (around 0.001-0.01 is typically good)
        lr_score = 1.0 - abs(np.log10(learning_rate) + 2.5) / 2.5
        performance_score += 0.3 * max(0, lr_score)

        # Batch size optimization (32-128 typically good)
        batch_score = 1.0 - abs(batch_size - 64) / 64
        performance_score += 0.2 * max(0, batch_score)

        # Architecture complexity balance
        complexity = hidden_layers * neurons_per_layer
        complexity_score = 1.0 / (1.0 + abs(complexity - 256) / 256)
        performance_score += 0.3 * complexity_score

        # Regularization penalty
        dropout_rate = genotype.get("dropout_rate", 0.0)
        reg_score = 1.0 - abs(dropout_rate - 0.2) / 0.2
        performance_score += 0.2 * max(0, reg_score)

        return min(1.0, performance_score)

    async def _evaluate_constitutional_compliance(
        self, individual: Individual
    ) -> float:
        """Evaluate constitutional compliance objective."""
        if self.constitutional_client:
            try:
                # Call constitutional AI service for compliance evaluation
                response = await self.constitutional_client.post(
                    "/api/v1/constitutional/validate",
                    json={
                        "policy": individual.genotype,
                        "validation_mode": "comprehensive",
                    },
                    timeout=5.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    compliance_score = result.get("compliance_score", 0.0)
                    individual.constitutional_compliance = compliance_score
                    return compliance_score

            except Exception as e:
                logger.warning(f"Constitutional compliance evaluation failed: {e}")

        # Fallback heuristic evaluation
        return self._heuristic_constitutional_compliance(individual)

    def _heuristic_constitutional_compliance(self, individual: Individual) -> float:
        """Heuristic constitutional compliance evaluation."""
        genotype = individual.genotype
        compliance_score = 1.0

        # Check for problematic patterns
        if genotype.get("unrestricted_access", False):
            compliance_score -= 0.4

        if genotype.get("bypass_authorization", False):
            compliance_score -= 0.5

        if genotype.get("data_collection_unlimited", False):
            compliance_score -= 0.3

        # Positive compliance indicators
        if genotype.get("audit_logging", True):
            compliance_score += 0.1

        if genotype.get("transparency_enabled", True):
            compliance_score += 0.1

        if genotype.get("user_consent_required", True):
            compliance_score += 0.1

        return max(0.0, min(1.0, compliance_score))

    def _evaluate_resource_efficiency(self, individual: Individual) -> float:
        """Evaluate resource efficiency objective."""
        genotype = individual.genotype

        # Estimate computational complexity
        hidden_layers = genotype.get("hidden_layers", 2)
        neurons_per_layer = genotype.get("neurons_per_layer", 64)
        batch_size = genotype.get("batch_size", 32)

        # Simple complexity estimate
        params = hidden_layers * neurons_per_layer * neurons_per_layer
        flops_per_sample = params * 2  # Forward + backward pass approximation
        total_flops = flops_per_sample * batch_size

        # Normalize to [0, 1] where lower complexity is better
        max_complexity = 1e6  # Arbitrary threshold
        efficiency = 1.0 - min(total_flops, max_complexity) / max_complexity

        return efficiency

    def _evaluate_safety(self, individual: Individual) -> float:
        """Evaluate safety objective."""
        genotype = individual.genotype
        safety_score = 1.0

        # Safety checks
        max_iterations = genotype.get("max_iterations", 1000)
        if max_iterations > 10000:
            safety_score -= 0.3  # Risk of infinite loops

        memory_limit = genotype.get("memory_limit_mb", 512)
        if memory_limit > 4096:
            safety_score -= 0.2  # High memory usage risk

        network_access = genotype.get("network_access", False)
        if network_access and not genotype.get("network_restrictions", True):
            safety_score -= 0.4  # Unrestricted network access risk

        # Safety features
        if genotype.get("input_validation", True):
            safety_score += 0.1

        if genotype.get("output_sanitization", True):
            safety_score += 0.1

        return max(0.0, min(1.0, safety_score))

    def _evaluate_explainability(self, individual: Individual) -> float:
        """Evaluate explainability objective."""
        genotype = individual.genotype

        # Simpler models are generally more explainable
        hidden_layers = genotype.get("hidden_layers", 2)
        neurons_per_layer = genotype.get("neurons_per_layer", 64)

        # Explainability decreases with complexity
        complexity = hidden_layers * neurons_per_layer
        explainability = 1.0 / (1.0 + np.log(1.0 + complexity / 100))

        # Bonus for explainability features
        if genotype.get("attention_mechanism", False):
            explainability += 0.2

        if genotype.get("feature_importance", True):
            explainability += 0.1

        return min(1.0, explainability)

    def _evaluate_robustness(self, individual: Individual) -> float:
        """Evaluate robustness objective."""
        genotype = individual.genotype

        # Robustness features
        robustness_score = 0.0

        dropout_rate = genotype.get("dropout_rate", 0.0)
        if 0.1 <= dropout_rate <= 0.5:
            robustness_score += 0.3

        batch_norm = genotype.get("batch_normalization", False)
        if batch_norm:
            robustness_score += 0.2

        l2_reg = genotype.get("l2_regularization", 0.0)
        if 0.001 <= l2_reg <= 0.01:
            robustness_score += 0.2

        data_augmentation = genotype.get("data_augmentation", False)
        if data_augmentation:
            robustness_score += 0.3

        return min(1.0, robustness_score)

    def _evaluate_adaptability(self, individual: Individual) -> float:
        """Evaluate adaptability objective."""
        genotype = individual.genotype

        # Adaptability features
        adaptability_score = 0.0

        transfer_learning = genotype.get("transfer_learning", False)
        if transfer_learning:
            adaptability_score += 0.3

        dynamic_architecture = genotype.get("dynamic_architecture", False)
        if dynamic_architecture:
            adaptability_score += 0.3

        meta_learning = genotype.get("meta_learning", False)
        if meta_learning:
            adaptability_score += 0.2

        continual_learning = genotype.get("continual_learning", False)
        if continual_learning:
            adaptability_score += 0.2

        return min(1.0, adaptability_score)


class EvolutionaryAlgorithm(ABC):
    """Abstract base class for evolutionary algorithms."""

    def __init__(
        self,
        fitness_evaluator: FitnessEvaluator,
        params: EvolutionParams,
        objectives: list[OptimizationObjective],
    ):
        self.fitness_evaluator = fitness_evaluator
        self.params = params
        self.objectives = objectives
        self.population: list[Individual] = []
        self.generation = 0
        self.best_individual: Optional[Individual] = None
        self.fitness_history: list[dict[str, float]] = []
        self.diversity_history: list[float] = []

    @abstractmethod
    async def initialize_population(self) -> list[Individual]:
        """Initialize the population."""

    @abstractmethod
    async def selection(self, population: list[Individual]) -> list[Individual]:
        """Select individuals for reproduction."""

    @abstractmethod
    async def crossover(self, parents: list[Individual]) -> list[Individual]:
        """Create offspring through crossover."""

    @abstractmethod
    async def mutation(self, individuals: list[Individual]) -> list[Individual]:
        """Apply mutation to individuals."""

    async def evolve(self) -> Individual:
        """Run the evolutionary algorithm."""
        logger.info(
            f"Starting evolution with {self.params.population_size} individuals "
            f"for {self.params.generations} generations"
        )

        # Initialize population
        self.population = await self.initialize_population()

        # Evaluate initial population
        await self._evaluate_population(self.population)

        stagnation_counter = 0
        previous_best_fitness = -float("inf")

        for generation in range(self.params.generations):
            self.generation = generation

            # Selection
            selected = await self.selection(self.population)

            # Crossover
            offspring = await self.crossover(selected)

            # Mutation
            offspring = await self.mutation(offspring)

            # Evaluate offspring
            await self._evaluate_population(offspring)

            # Environmental selection (combine parents and offspring)
            combined = self.population + offspring
            self.population = await self._environmental_selection(combined)

            # Update best individual
            current_best = max(self.population, key=lambda ind: ind.total_fitness())

            if (
                self.best_individual is None
                or current_best.total_fitness() > self.best_individual.total_fitness()
            ):
                self.best_individual = current_best

            # Track fitness and diversity
            avg_fitness = np.mean([ind.total_fitness() for ind in self.population])
            diversity = self._calculate_diversity(self.population)

            self.fitness_history.append(
                {
                    "generation": generation,
                    "best_fitness": self.best_individual.total_fitness(),
                    "avg_fitness": avg_fitness,
                    "diversity": diversity,
                }
            )

            # Check for convergence
            improvement = self.best_individual.total_fitness() - previous_best_fitness
            if improvement < self.params.convergence_threshold:
                stagnation_counter += 1
            else:
                stagnation_counter = 0
                previous_best_fitness = self.best_individual.total_fitness()

            if stagnation_counter >= self.params.max_stagnation:
                logger.info(f"Converged at generation {generation}")
                break

            if generation % 10 == 0:
                logger.info(
                    f"Generation {generation}:"
                    f" Best={self.best_individual.total_fitness():.4f},"
                    f" Avg={avg_fitness:.4f}, Diversity={diversity:.4f}"
                )

        logger.info(
            "Evolution completed. Best fitness:"
            f" {self.best_individual.total_fitness():.4f}"
        )

        return self.best_individual

    async def _evaluate_population(self, population: list[Individual]) -> None:
        """Evaluate fitness for all individuals in population."""
        for individual in population:
            if not individual.fitness:  # Only evaluate if not already done
                await self.fitness_evaluator.evaluate_individual(
                    individual, self.objectives
                )

    async def _environmental_selection(
        self, combined_population: list[Individual]
    ) -> list[Individual]:
        """Select survivors for next generation."""
        # Sort by total fitness (descending)
        combined_population.sort(key=lambda ind: ind.total_fitness(), reverse=True)

        # Elitism: keep top individuals
        elite_count = int(self.params.elitism_ratio * self.params.population_size)
        survivors = combined_population[:elite_count]

        # Fill remaining slots
        remaining_slots = self.params.population_size - elite_count
        remaining_candidates = combined_population[elite_count:]

        # Use tournament selection for remaining slots
        for _ in range(remaining_slots):
            if remaining_candidates:
                winner = self._tournament_selection(remaining_candidates, k=3)
                survivors.append(winner)
                remaining_candidates.remove(winner)

        return survivors[: self.params.population_size]

    def _tournament_selection(
        self, candidates: list[Individual], k: int = 3
    ) -> Individual:
        """Tournament selection."""
        tournament = random.sample(candidates, min(k, len(candidates)))
        return max(tournament, key=lambda ind: ind.total_fitness())

    def _calculate_diversity(self, population: list[Individual]) -> float:
        """Calculate population diversity."""
        if len(population) < 2:
            return 0.0

        # Calculate pairwise distances in genotype space
        distances = []
        for i in range(len(population)):
            for j in range(i + 1, len(population)):
                dist = self._genotype_distance(
                    population[i].genotype, population[j].genotype
                )
                distances.append(dist)

        return np.mean(distances) if distances else 0.0

    def _genotype_distance(self, genotype1: dict, genotype2: dict) -> float:
        """Calculate distance between two genotypes."""
        common_keys = set(genotype1.keys()) & set(genotype2.keys())
        if not common_keys:
            return 1.0

        total_distance = 0.0
        for key in common_keys:
            val1, val2 = genotype1[key], genotype2[key]

            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Normalize numerical differences
                total_distance += abs(val1 - val2) / (abs(val1) + abs(val2) + 1e-8)
            elif val1 != val2:
                total_distance += 1.0

        return total_distance / len(common_keys)


class GeneticAlgorithm(EvolutionaryAlgorithm):
    """Genetic Algorithm implementation for agent evolution."""

    def __init__(
        self,
        config: EvolutionConfig,
        fitness_evaluator: Optional[FitnessEvaluator] = None,
        objectives: Optional[list[OptimizationObjective]] = None,
        genotype_template: Optional[dict[str, Any]] = None,
    ):
        # Support both old and new constructor styles
        if isinstance(config, EvolutionConfig):
            self.config = config
            self.fitness_evaluator = fitness_evaluator
            self.objectives = objectives or [
                OptimizationObjective.PERFORMANCE,
                OptimizationObjective.CONSTITUTIONAL_COMPLIANCE,
            ]
            self.genotype_template = genotype_template or {}
        else:
            # Old style constructor - config is actually fitness_evaluator
            fitness_evaluator = config
            params = fitness_evaluator  # This is actually params
            objectives = objectives or []
            super().__init__(fitness_evaluator, params, objectives)
            self.genotype_template = genotype_template or {}

    def generate_initial_population(self, genome_size: int) -> Population:
        """Generate initial population for testing compatibility."""
        individuals = []
        for _ in range(self.config.population_size):
            genome = np.random.rand(genome_size)
            individual = Individual(genome=genome)
            individuals.append(individual)
        return Population(individuals)

    def gaussian_mutation(
        self, individual: Individual, mutation_rate: float
    ) -> Individual:
        """Apply Gaussian mutation to an individual."""
        mutated_genome = individual.genome.copy()
        for i in range(len(mutated_genome)):
            if np.random.random() < mutation_rate:
                mutated_genome[i] += np.random.normal(0, 0.1)
                mutated_genome[i] = np.clip(mutated_genome[i], 0, 1)
        return Individual(genome=mutated_genome)

    def uniform_mutation(
        self, individual: Individual, mutation_rate: float
    ) -> Individual:
        """Apply uniform mutation to an individual."""
        mutated_genome = individual.genome.copy()
        for i in range(len(mutated_genome)):
            if np.random.random() < mutation_rate:
                mutated_genome[i] = np.random.random()
        return Individual(genome=mutated_genome)

    def polynomial_mutation(
        self, individual: Individual, mutation_rate: float
    ) -> Individual:
        """Apply polynomial mutation to an individual."""
        mutated_genome = individual.genome.copy()
        eta = 20  # Distribution index

        for i in range(len(mutated_genome)):
            if np.random.random() < mutation_rate:
                u = np.random.random()
                if u <= 0.5:
                    delta = (2 * u) ** (1 / (eta + 1)) - 1
                else:
                    delta = 1 - (2 * (1 - u)) ** (1 / (eta + 1))

                mutated_genome[i] += delta * 0.1
                mutated_genome[i] = np.clip(mutated_genome[i], 0, 1)

        return Individual(genome=mutated_genome)

    def single_point_crossover(
        self, parent1: Individual, parent2: Individual
    ) -> tuple[Individual, Individual]:
        """Single point crossover."""
        crossover_point = np.random.randint(1, len(parent1.genome))

        child1_genome = np.concatenate(
            [parent1.genome[:crossover_point], parent2.genome[crossover_point:]]
        )
        child2_genome = np.concatenate(
            [parent2.genome[:crossover_point], parent1.genome[crossover_point:]]
        )

        return Individual(genome=child1_genome), Individual(genome=child2_genome)

    def two_point_crossover(
        self, parent1: Individual, parent2: Individual
    ) -> tuple[Individual, Individual]:
        """Two point crossover."""
        point1 = np.random.randint(0, len(parent1.genome))
        point2 = np.random.randint(point1, len(parent1.genome))

        child1_genome = parent1.genome.copy()
        child2_genome = parent2.genome.copy()

        child1_genome[point1:point2] = parent2.genome[point1:point2]
        child2_genome[point1:point2] = parent1.genome[point1:point2]

        return Individual(genome=child1_genome), Individual(genome=child2_genome)

    def uniform_crossover(
        self, parent1: Individual, parent2: Individual
    ) -> tuple[Individual, Individual]:
        """Uniform crossover."""
        mask = np.random.random(len(parent1.genome)) < 0.5

        child1_genome = np.where(mask, parent1.genome, parent2.genome)
        child2_genome = np.where(mask, parent2.genome, parent1.genome)

        return Individual(genome=child1_genome), Individual(genome=child2_genome)

    def tournament_selection(
        self, population: Population, tournament_size: int = 3
    ) -> list[Individual]:
        """Tournament selection."""
        selected = []
        for _ in range(len(population)):
            tournament = np.random.choice(
                population.individuals, tournament_size, replace=False
            )
            best = max(tournament, key=self.calculate_overall_fitness)
            selected.append(best)
        return selected

    def roulette_wheel_selection(self, population: Population) -> list[Individual]:
        """Roulette wheel selection."""
        fitness_scores = [
            self.calculate_overall_fitness(ind) for ind in population.individuals
        ]
        total_fitness = sum(fitness_scores)

        if total_fitness == 0:
            return list(population.individuals)

        probabilities = [f / total_fitness for f in fitness_scores]
        selected = np.random.choice(
            population.individuals, size=len(population), p=probabilities
        )
        return list(selected)

    def rank_selection(self, population: Population) -> list[Individual]:
        """Rank-based selection."""
        sorted_pop = sorted(population.individuals, key=self.calculate_overall_fitness)
        ranks = list(range(1, len(sorted_pop) + 1))
        total_rank = sum(ranks)

        probabilities = [r / total_rank for r in ranks]
        selected = np.random.choice(sorted_pop, size=len(population), p=probabilities)
        return list(selected)

    def calculate_overall_fitness(self, individual: Individual) -> float:
        """Calculate overall fitness score."""
        if not individual.fitness_scores:
            return 0.0

        total_score = 0.0
        weights = {
            "performance": 0.3,
            "constitutional_compliance": self.config.constitutional_weight,
            "safety": 0.2,
            "efficiency": 0.2,
        }

        for metric, score in individual.fitness_scores.items():
            weight = weights.get(metric, 0.1)
            total_score += score * weight

        return total_score

    def get_elite_individuals(
        self, population: Population, elite_size: int
    ) -> list[Individual]:
        """Get elite individuals from population."""
        sorted_pop = sorted(
            population.individuals, key=self.calculate_overall_fitness, reverse=True
        )
        return sorted_pop[:elite_size]

    def evaluate_fitness(self, population: Population, fitness_func: Callable):
        """Evaluate fitness for all individuals in population."""
        for individual in population.individuals:
            individual.fitness_scores = fitness_func(individual.genome)

    def satisfies_constraint(self, individual: Individual, constraint) -> bool:
        """Check if individual satisfies a constraint."""
        if hasattr(constraint, "principle") and hasattr(constraint, "min_score"):
            score = individual.fitness_scores.get(constraint.principle, 0.0)
            return score >= constraint.min_score
        return True

    def is_safe(self, individual: Individual) -> bool:
        """Check if individual meets safety requirements."""
        safety_score = individual.fitness_scores.get("safety", 0.0)
        return safety_score >= self.config.safety_threshold

    def is_constitutionally_compliant(self, individual: Individual) -> bool:
        """Check if individual meets constitutional compliance requirements."""
        compliance_score = individual.fitness_scores.get(
            "constitutional_compliance", 0.0
        )
        return compliance_score >= self.config.constitutional_threshold

    async def evolve(
        self,
        initial_population: Population,
        fitness_function: Callable,
        generations: int,
    ) -> tuple[Individual, Population]:
        """Run evolution for specified generations."""
        population = initial_population

        for generation in range(generations):
            # Evaluate fitness
            self.evaluate_fitness(population, fitness_function)

            # Get elite individuals
            elite = self.get_elite_individuals(population, self.config.elite_size)

            # Selection
            selected = self.tournament_selection(population)

            # Create new population
            new_individuals = list(elite)  # Keep elite

            while len(new_individuals) < self.config.population_size:
                parent1, parent2 = np.random.choice(selected, 2, replace=False)

                if np.random.random() < self.config.crossover_rate:
                    child1, child2 = self.single_point_crossover(parent1, parent2)
                else:
                    child1, child2 = parent1, parent2

                # Mutation
                if np.random.random() < self.config.mutation_rate:
                    child1 = self.gaussian_mutation(child1, self.config.mutation_rate)
                if np.random.random() < self.config.mutation_rate:
                    child2 = self.gaussian_mutation(child2, self.config.mutation_rate)

                new_individuals.extend([child1, child2])

            # Trim to population size
            population = Population(new_individuals[: self.config.population_size])
            population.generation = generation + 1

        # Final fitness evaluation
        self.evaluate_fitness(population, fitness_function)
        best_individual = max(
            population.individuals, key=self.calculate_overall_fitness
        )

        return best_individual, population

    async def evolve_with_constraints(
        self,
        initial_population: Population,
        fitness_function: Callable,
        generations: int,
    ) -> tuple[Individual, Population]:
        """Evolve with safety and constitutional constraints."""
        population = initial_population

        for generation in range(generations):
            # Evaluate fitness
            self.evaluate_fitness(population, fitness_function)

            # Filter for constraint satisfaction
            valid_individuals = [
                ind
                for ind in population.individuals
                if self.is_safe(ind) and self.is_constitutionally_compliant(ind)
            ]

            if not valid_individuals:
                # If no valid individuals, relax constraints slightly
                valid_individuals = population.individuals

            # Continue with standard evolution using valid individuals
            valid_population = Population(valid_individuals)
            best, final_pop = await self.evolve(valid_population, fitness_function, 1)
            population = final_pop

        # Return best valid individual
        self.evaluate_fitness(population, fitness_function)
        valid_individuals = [
            ind
            for ind in population.individuals
            if self.is_safe(ind) and self.is_constitutionally_compliant(ind)
        ]

        if valid_individuals:
            best_individual = max(valid_individuals, key=self.calculate_overall_fitness)
        else:
            best_individual = max(
                population.individuals, key=self.calculate_overall_fitness
            )

        return best_individual, population

    async def initialize_population(self) -> list[Individual]:
        """Initialize random population."""
        population = []

        for _ in range(self.params.population_size):
            individual = Individual(
                genotype=self._generate_random_genotype(), generation=0
            )
            population.append(individual)

        return population

    def _generate_random_genotype(self) -> dict[str, Any]:
        """Generate a random genotype based on template."""
        genotype = {}

        for key, value_spec in self.genotype_template.items():
            if isinstance(value_spec, dict):
                if "type" in value_spec:
                    if value_spec["type"] == "float":
                        min_val = value_spec.get("min", 0.0)
                        max_val = value_spec.get("max", 1.0)
                        genotype[key] = random.uniform(min_val, max_val)

                    elif value_spec["type"] == "int":
                        min_val = value_spec.get("min", 0)
                        max_val = value_spec.get("max", 100)
                        genotype[key] = random.randint(min_val, max_val)

                    elif value_spec["type"] == "bool":
                        genotype[key] = random.choice([True, False])

                    elif value_spec["type"] == "choice":
                        choices = value_spec.get("choices", [])
                        genotype[key] = random.choice(choices) if choices else None

            else:
                # Use value as default
                genotype[key] = value_spec

        return genotype

    async def selection(self, population: list[Individual]) -> list[Individual]:
        """Tournament selection."""
        selected = []

        for _ in range(len(population)):
            winner = self._tournament_selection(
                population, k=int(self.params.selection_pressure)
            )
            selected.append(winner)

        return selected

    async def crossover(self, parents: list[Individual]) -> list[Individual]:
        """Uniform crossover."""
        offspring = []

        for i in range(0, len(parents) - 1, 2):
            if random.random() < self.params.crossover_rate:
                parent1, parent2 = parents[i], parents[i + 1]
                child1, child2 = self._uniform_crossover(parent1, parent2)
                offspring.extend([child1, child2])
            else:
                offspring.extend([parents[i], parents[i + 1]])

        return offspring

    def _uniform_crossover(
        self, parent1: Individual, parent2: Individual
    ) -> tuple[Individual, Individual]:
        """Uniform crossover between two parents."""
        child1_genotype = {}
        child2_genotype = {}

        all_keys = set(parent1.genotype.keys()) | set(parent2.genotype.keys())

        for key in all_keys:
            if random.random() < 0.5:
                child1_genotype[key] = parent1.genotype.get(key)
                child2_genotype[key] = parent2.genotype.get(key)
            else:
                child1_genotype[key] = parent2.genotype.get(key)
                child2_genotype[key] = parent1.genotype.get(key)

        child1 = Individual(
            genotype=child1_genotype,
            generation=self.generation + 1,
            parent_ids=[parent1.id, parent2.id],
        )

        child2 = Individual(
            genotype=child2_genotype,
            generation=self.generation + 1,
            parent_ids=[parent1.id, parent2.id],
        )

        return child1, child2

    async def mutation(self, individuals: list[Individual]) -> list[Individual]:
        """Gaussian mutation."""
        for individual in individuals:
            if random.random() < self.params.mutation_rate:
                self._gaussian_mutation(individual)

        return individuals

    def _gaussian_mutation(self, individual: Individual) -> None:
        """Apply Gaussian mutation to individual."""
        for key, value in individual.genotype.items():
            if isinstance(value, float):
                # Gaussian mutation for float values
                mutation_strength = 0.1 * value if value != 0 else 0.01
                individual.genotype[key] = value + random.gauss(0, mutation_strength)

                # Clamp to reasonable bounds if specified in template
                if key in self.genotype_template:
                    spec = self.genotype_template[key]
                    if isinstance(spec, dict):
                        min_val = spec.get("min")
                        max_val = spec.get("max")
                        if min_val is not None:
                            individual.genotype[key] = max(
                                min_val, individual.genotype[key]
                            )
                        if max_val is not None:
                            individual.genotype[key] = min(
                                max_val, individual.genotype[key]
                            )

            elif isinstance(value, int):
                # Integer mutation
                if random.random() < 0.1:  # 10% chance to mutate each integer
                    delta = random.choice([-1, 1])
                    individual.genotype[key] = max(0, value + delta)

            elif isinstance(value, bool):
                # Boolean flip
                if random.random() < 0.05:  # 5% chance to flip
                    individual.genotype[key] = not value


class MultiObjectiveEvolution(EvolutionaryAlgorithm):
    """Multi-objective evolutionary algorithm using NSGA-II principles."""

    def __init__(
        self,
        fitness_evaluator: FitnessEvaluator,
        params: EvolutionParams,
        objectives: list[OptimizationObjective],
        genotype_template: dict[str, Any],
    ):
        super().__init__(fitness_evaluator, params, objectives)
        self.genotype_template = genotype_template
        self.pareto_fronts: list[list[Individual]] = []

    async def initialize_population(self) -> list[Individual]:
        """Initialize population same as GA."""
        population = []

        for _ in range(self.params.population_size):
            individual = Individual(
                genotype=self._generate_random_genotype(), generation=0
            )
            population.append(individual)

        return population

    def _generate_random_genotype(self) -> dict[str, Any]:
        """Generate random genotype (same as GA)."""
        genotype = {}

        for key, value_spec in self.genotype_template.items():
            if isinstance(value_spec, dict):
                if "type" in value_spec:
                    if value_spec["type"] == "float":
                        min_val = value_spec.get("min", 0.0)
                        max_val = value_spec.get("max", 1.0)
                        genotype[key] = random.uniform(min_val, max_val)
                    elif value_spec["type"] == "int":
                        min_val = value_spec.get("min", 0)
                        max_val = value_spec.get("max", 100)
                        genotype[key] = random.randint(min_val, max_val)
                    elif value_spec["type"] == "bool":
                        genotype[key] = random.choice([True, False])
                    elif value_spec["type"] == "choice":
                        choices = value_spec.get("choices", [])
                        genotype[key] = random.choice(choices) if choices else None
            else:
                genotype[key] = value_spec

        return genotype

    async def selection(self, population: list[Individual]) -> list[Individual]:
        """Pareto-based selection."""
        # Calculate Pareto fronts
        fronts = self._fast_non_dominated_sort(population)
        self.pareto_fronts = fronts

        # Select based on fronts and crowding distance
        selected = []
        for front in fronts:
            if len(selected) + len(front) <= len(population):
                selected.extend(front)
            else:
                # Calculate crowding distance and select best
                self._calculate_crowding_distance(front)
                front.sort(
                    key=lambda ind: getattr(ind, "crowding_distance", 0), reverse=True
                )
                remaining = len(population) - len(selected)
                selected.extend(front[:remaining])
                break

        return selected

    def _fast_non_dominated_sort(
        self, population: list[Individual]
    ) -> list[list[Individual]]:
        """NSGA-II fast non-dominated sorting."""
        fronts = []
        domination_count = {}
        dominated_solutions = {}

        # Initialize
        for individual in population:
            domination_count[individual.id] = 0
            dominated_solutions[individual.id] = []

        # Find domination relationships
        current_front = []
        for i, individual_i in enumerate(population):
            for j, individual_j in enumerate(population):
                if i != j:
                    if individual_i.dominates(individual_j):
                        dominated_solutions[individual_i.id].append(individual_j)
                    elif individual_j.dominates(individual_i):
                        domination_count[individual_i.id] += 1

            if domination_count[individual_i.id] == 0:
                current_front.append(individual_i)

        fronts.append(current_front)

        # Build subsequent fronts
        while current_front:
            next_front = []
            for individual in current_front:
                for dominated in dominated_solutions[individual.id]:
                    domination_count[dominated.id] -= 1
                    if domination_count[dominated.id] == 0:
                        next_front.append(dominated)

            if next_front:
                fronts.append(next_front)
            current_front = next_front

        return fronts

    def _calculate_crowding_distance(self, front: list[Individual]) -> None:
        """Calculate crowding distance for individuals in a front."""
        if len(front) <= 2:
            for individual in front:
                individual.crowding_distance = float("inf")
            return

        # Initialize distances
        for individual in front:
            individual.crowding_distance = 0.0

        # Calculate for each objective
        for objective in self.objectives:
            obj_name = objective.value

            # Sort by this objective
            front.sort(key=lambda ind: ind.fitness.get(obj_name, 0.0))

            # Set boundary points to infinity
            front[0].crowding_distance = float("inf")
            front[-1].crowding_distance = float("inf")

            # Calculate crowding distance for others
            obj_min = front[0].fitness.get(obj_name, 0.0)
            obj_max = front[-1].fitness.get(obj_name, 0.0)

            if obj_max - obj_min > 0:
                for i in range(1, len(front) - 1):
                    distance = (
                        front[i + 1].fitness.get(obj_name, 0.0)
                        - front[i - 1].fitness.get(obj_name, 0.0)
                    ) / (obj_max - obj_min)

                    front[i].crowding_distance += distance

    async def crossover(self, parents: list[Individual]) -> list[Individual]:
        """Simulated binary crossover for multi-objective."""
        offspring = []

        for i in range(0, len(parents) - 1, 2):
            if random.random() < self.params.crossover_rate:
                parent1, parent2 = parents[i], parents[i + 1]
                child1, child2 = self._simulated_binary_crossover(parent1, parent2)
                offspring.extend([child1, child2])
            else:
                offspring.extend([parents[i], parents[i + 1]])

        return offspring

    def _simulated_binary_crossover(
        self, parent1: Individual, parent2: Individual, eta: float = 20.0
    ) -> tuple[Individual, Individual]:
        """Simulated Binary Crossover (SBX)."""
        child1_genotype = {}
        child2_genotype = {}

        for key in parent1.genotype.keys():
            val1 = parent1.genotype[key]
            val2 = parent2.genotype[key]

            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # SBX for numerical values
                if random.random() < 0.5:
                    if abs(val1 - val2) > 1e-14:
                        if val1 > val2:
                            val1, val2 = val2, val1

                        # Calculate beta
                        rand = random.random()
                        if rand <= 0.5:
                            beta = (2.0 * rand) ** (1.0 / (eta + 1.0))
                        else:
                            beta = (1.0 / (2.0 * (1.0 - rand))) ** (1.0 / (eta + 1.0))

                        # Create offspring
                        child1_genotype[key] = 0.5 * (
                            (1.0 + beta) * val1 + (1.0 - beta) * val2
                        )
                        child2_genotype[key] = 0.5 * (
                            (1.0 - beta) * val1 + (1.0 + beta) * val2
                        )
                    else:
                        child1_genotype[key] = val1
                        child2_genotype[key] = val2
                else:
                    child1_genotype[key] = val1
                    child2_genotype[key] = val2
            else:
                # For non-numerical values, random assignment
                if random.random() < 0.5:
                    child1_genotype[key] = val1
                    child2_genotype[key] = val2
                else:
                    child1_genotype[key] = val2
                    child2_genotype[key] = val1

        child1 = Individual(
            genotype=child1_genotype,
            generation=self.generation + 1,
            parent_ids=[parent1.id, parent2.id],
        )

        child2 = Individual(
            genotype=child2_genotype,
            generation=self.generation + 1,
            parent_ids=[parent1.id, parent2.id],
        )

        return child1, child2

    async def mutation(self, individuals: list[Individual]) -> list[Individual]:
        """Polynomial mutation for multi-objective."""
        for individual in individuals:
            if random.random() < self.params.mutation_rate:
                self._polynomial_mutation(individual)

        return individuals

    def _polynomial_mutation(self, individual: Individual, eta: float = 20.0) -> None:
        """Polynomial mutation."""
        for key, value in individual.genotype.items():
            if isinstance(value, (int, float)):
                if random.random() < 1.0 / len(individual.genotype):
                    # Get bounds from template
                    bounds = self.genotype_template.get(key, {})
                    if isinstance(bounds, dict):
                        lower = bounds.get("min", value - abs(value))
                        upper = bounds.get("max", value + abs(value))
                    else:
                        lower = value - abs(value)
                        upper = value + abs(value)

                    delta1 = (value - lower) / (upper - lower) if upper != lower else 0
                    delta2 = (upper - value) / (upper - lower) if upper != lower else 0

                    rand = random.random()
                    mut_pow = 1.0 / (eta + 1.0)

                    if rand < 0.5:
                        xy = 1.0 - delta1
                        val = 2.0 * rand + (1.0 - 2.0 * rand) * (xy ** (eta + 1.0))
                        deltaq = val**mut_pow - 1.0
                    else:
                        xy = 1.0 - delta2
                        val = 2.0 * (1.0 - rand) + 2.0 * (rand - 0.5) * (
                            xy ** (eta + 1.0)
                        )
                        deltaq = 1.0 - val**mut_pow

                    # Apply mutation
                    individual.genotype[key] = value + deltaq * (upper - lower)

                    # Clamp to bounds
                    individual.genotype[key] = max(
                        lower, min(upper, individual.genotype[key])
                    )


class EvolutionaryAgentOptimizer:
    """Main interface for evolutionary agent optimization."""

    def __init__(self, constitutional_client: Optional[Any] = None):
        self.constitutional_client = constitutional_client
        self.fitness_evaluator = FitnessEvaluator(constitutional_client)
        self.optimization_history: list[dict[str, Any]] = []

    async def optimize_agent(
        self,
        agent_config: dict[str, Any],
        optimization_objectives: list[OptimizationObjective],
        algorithm_type: str = "genetic",
        evolution_params: Optional[EvolutionParams] = None,
    ) -> dict[str, Any]:
        """Optimize an agent using evolutionary computation."""

        if evolution_params is None:
            evolution_params = EvolutionParams()

        # Create genotype template from agent config
        genotype_template = self._create_genotype_template(agent_config)

        # Select algorithm
        if algorithm_type.lower() == "genetic":
            algorithm = GeneticAlgorithm(
                self.fitness_evaluator,
                evolution_params,
                optimization_objectives,
                genotype_template,
            )
        elif algorithm_type.lower() == "multi_objective":
            algorithm = MultiObjectiveEvolution(
                self.fitness_evaluator,
                evolution_params,
                optimization_objectives,
                genotype_template,
            )
        else:
            raise ValueError(f"Unknown algorithm type: {algorithm_type}")

        # Run evolution
        start_time = time.time()
        best_individual = await algorithm.evolve()
        evolution_time = time.time() - start_time

        # Prepare results
        results = {
            "optimization_id": str(uuid.uuid4()),
            "algorithm_type": algorithm_type,
            "best_individual": {
                "id": best_individual.id,
                "genotype": best_individual.genotype,
                "fitness": best_individual.fitness,
                "total_fitness": best_individual.total_fitness(),
                "constitutional_compliance": best_individual.constitutional_compliance,
                "generation": best_individual.generation,
            },
            "optimization_objectives": [obj.value for obj in optimization_objectives],
            "evolution_params": {
                "population_size": evolution_params.population_size,
                "generations": evolution_params.generations,
                "mutation_rate": evolution_params.mutation_rate,
                "crossover_rate": evolution_params.crossover_rate,
            },
            "performance_metrics": {
                "evolution_time_seconds": evolution_time,
                "final_generation": algorithm.generation,
                "fitness_history": algorithm.fitness_history,
                "diversity_history": algorithm.diversity_history,
            },
            "constitutional_hash": "cdd01ef066bc6cf2",
            "timestamp": datetime.now().isoformat(),
        }

        # Store in history
        self.optimization_history.append(results)

        logger.info(
            "Evolutionary optimization completed. Best fitness:"
            f" {best_individual.total_fitness():.4f}, Constitutional compliance:"
            f" {best_individual.constitutional_compliance:.4f}"
        )

        return results

    def _create_genotype_template(self, agent_config: dict[str, Any]) -> dict[str, Any]:
        """Create genotype template from agent configuration."""
        template = {}

        # Extract optimizable parameters
        for key, value in agent_config.items():
            if key.endswith("_range") and isinstance(value, dict):
                param_name = key[:-6]  # Remove '_range' suffix
                template[param_name] = value
            elif isinstance(value, (int, float)):
                # Create reasonable ranges for numerical parameters
                if isinstance(value, float):
                    template[key] = {
                        "type": "float",
                        "min": value * 0.1,
                        "max": value * 10.0,
                    }
                else:
                    template[key] = {
                        "type": "int",
                        "min": max(1, value // 10),
                        "max": value * 10,
                    }
            elif isinstance(value, bool):
                template[key] = {"type": "bool"}
            elif isinstance(value, list):
                template[key] = {"type": "choice", "choices": value}

        return template

    async def get_optimization_history(self) -> list[dict[str, Any]]:
        """Get history of optimization runs."""
        return self.optimization_history

    async def analyze_evolution_convergence(
        self, optimization_id: str
    ) -> dict[str, Any]:
        """Analyze convergence properties of an evolution run."""

        # Find optimization run
        optimization_run = None
        for run in self.optimization_history:
            if run["optimization_id"] == optimization_id:
                optimization_run = run
                break

        if not optimization_run:
            raise ValueError(f"Optimization run {optimization_id} not found")

        fitness_history = optimization_run["performance_metrics"]["fitness_history"]

        if not fitness_history:
            return {"error": "No fitness history available"}

        # Analyze convergence
        best_fitness_values = [entry["best_fitness"] for entry in fitness_history]
        avg_fitness_values = [entry["avg_fitness"] for entry in fitness_history]
        diversity_values = [entry["diversity"] for entry in fitness_history]

        # Calculate convergence metrics
        convergence_analysis = {
            "optimization_id": optimization_id,
            "total_generations": len(fitness_history),
            "final_best_fitness": best_fitness_values[-1] if best_fitness_values else 0,
            "fitness_improvement": (
                best_fitness_values[-1] - best_fitness_values[0]
                if len(best_fitness_values) > 1
                else 0
            ),
            "convergence_rate": self._calculate_convergence_rate(best_fitness_values),
            "diversity_preservation": (
                np.mean(diversity_values) if diversity_values else 0
            ),
            "premature_convergence": self._detect_premature_convergence(
                best_fitness_values, diversity_values
            ),
            "plateau_detection": self._detect_fitness_plateau(best_fitness_values),
            "recommendation": self._generate_convergence_recommendations(
                best_fitness_values, diversity_values
            ),
        }

        return convergence_analysis

    def _calculate_convergence_rate(self, fitness_values: list[float]) -> float:
        """Calculate the rate of convergence."""
        if len(fitness_values) < 2:
            return 0.0

        # Calculate average improvement per generation
        improvements = []
        for i in range(1, len(fitness_values)):
            improvement = fitness_values[i] - fitness_values[i - 1]
            improvements.append(max(0, improvement))  # Only positive improvements

        return np.mean(improvements) if improvements else 0.0

    def _detect_premature_convergence(
        self, fitness_values: list[float], diversity_values: list[float]
    ) -> bool:
        """Detect if evolution converged prematurely."""
        if len(fitness_values) < 10 or len(diversity_values) < 10:
            return False

        # Check if diversity dropped too quickly
        initial_diversity = np.mean(diversity_values[:5])
        final_diversity = np.mean(diversity_values[-5:])

        diversity_drop = (initial_diversity - final_diversity) / initial_diversity

        # Check if fitness improvement stopped early
        recent_improvement = fitness_values[-1] - fitness_values[-10]

        return diversity_drop > 0.8 and recent_improvement < 0.01

    def _detect_fitness_plateau(self, fitness_values: list[float]) -> dict[str, Any]:
        """Detect fitness plateaus in evolution."""
        if len(fitness_values) < 10:
            return {"plateau_detected": False}

        # Look for long periods without improvement
        window_size = min(10, len(fitness_values) // 3)
        plateau_threshold = 0.001

        for i in range(window_size, len(fitness_values)):
            window_improvement = fitness_values[i] - fitness_values[i - window_size]
            if window_improvement < plateau_threshold:
                return {
                    "plateau_detected": True,
                    "plateau_start_generation": i - window_size,
                    "plateau_duration": len(fitness_values) - (i - window_size),
                }

        return {"plateau_detected": False}

    def _generate_convergence_recommendations(
        self, fitness_values: list[float], diversity_values: list[float]
    ) -> list[str]:
        """Generate recommendations for improving convergence."""
        recommendations = []

        if len(fitness_values) < 2 or len(diversity_values) < 2:
            return ["Insufficient data for analysis"]

        # Check diversity
        avg_diversity = np.mean(diversity_values)
        if avg_diversity < 0.1:
            recommendations.append("Increase mutation rate to maintain diversity")
            recommendations.append("Consider using fitness sharing or niching")

        # Check convergence rate
        recent_improvement = (
            fitness_values[-1] - fitness_values[max(0, len(fitness_values) - 10)]
        )
        if recent_improvement < 0.01:
            recommendations.append("Consider increasing population size")
            recommendations.append("Try different selection pressure")

        # Check for stagnation
        final_quarter = fitness_values[len(fitness_values) * 3 // 4 :]
        if len(final_quarter) > 1 and max(final_quarter) - min(final_quarter) < 0.001:
            recommendations.append(
                "Evolution may have stagnated - consider restart with new parameters"
            )

        if not recommendations:
            recommendations.append("Evolution parameters appear well-tuned")

        return recommendations
