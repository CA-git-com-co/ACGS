"""
Evolution Data Models

Core data models for evolutionary computation processes, including evolution requests,
individuals, populations, and fitness metrics with constitutional compliance.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class EvolutionType(str, Enum):
    """Types of evolutionary computation processes."""

    POLICY_OPTIMIZATION = "policy_optimization"
    AGENT_IMPROVEMENT = "agent_improvement"
    CONSTITUTIONAL_REFINEMENT = "constitutional_refinement"
    PERFORMANCE_TUNING = "performance_tuning"
    SAFETY_ENHANCEMENT = "safety_enhancement"


class EvolutionStatus(str, Enum):
    """Status of evolution requests."""

    PENDING = "pending"
    EVALUATING = "evaluating"
    HUMAN_REVIEW = "human_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


class FitnessMetrics(BaseModel):
    """Comprehensive fitness metrics for evolutionary evaluation."""

    constitutional_compliance: float = Field(
        ..., ge=0.0, le=1.0, description="Constitutional compliance score"
    )
    performance_score: float = Field(
        ..., ge=0.0, le=1.0, description="Performance optimization score"
    )
    safety_score: float = Field(
        ..., ge=0.0, le=1.0, description="Safety evaluation score"
    )
    fairness_score: float = Field(
        ..., ge=0.0, le=1.0, description="Fairness assessment score"
    )
    efficiency_score: float = Field(
        ..., ge=0.0, le=1.0, description="Efficiency optimization score"
    )
    robustness_score: float = Field(
        ..., ge=0.0, le=1.0, description="Robustness evaluation score"
    )
    transparency_score: float = Field(
        ..., ge=0.0, le=1.0, description="Transparency assessment score"
    )
    user_satisfaction: float = Field(
        ..., ge=0.0, le=1.0, description="User satisfaction score"
    )
    overall_fitness: float = Field(
        ..., ge=0.0, le=1.0, description="Weighted overall fitness score"
    )

    # Metadata
    evaluation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Individual(BaseModel):
    """Individual in evolutionary computation with constitutional compliance."""

    individual_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    genotype: Dict[str, Any] = Field(..., description="Genetic representation")
    phenotype: Optional[Dict[str, Any]] = Field(None, description="Expressed traits")
    fitness_metrics: Optional[FitnessMetrics] = None
    generation: int = Field(default=0, description="Generation number")
    parent_ids: List[str] = Field(
        default_factory=list, description="Parent individual IDs"
    )

    # Constitutional compliance
    constitutional_compliance: float = Field(default=0.0, ge=0.0, le=1.0)
    safety_validated: bool = Field(default=False)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    def total_fitness(self) -> float:
        """Calculate total fitness score."""
        if self.fitness_metrics:
            return self.fitness_metrics.overall_fitness
        return 0.0

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Population(BaseModel):
    """Population of individuals in evolutionary computation."""

    population_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    individuals: List[Individual] = Field(..., description="Population individuals")
    generation: int = Field(default=0, description="Current generation")
    size: int = Field(..., description="Population size")

    # Statistics
    average_fitness: float = Field(
        default=0.0, description="Average population fitness"
    )
    best_fitness: float = Field(default=0.0, description="Best individual fitness")
    diversity_score: float = Field(default=0.0, description="Population diversity")

    # Constitutional compliance
    constitutional_compliance_rate: float = Field(default=0.0, ge=0.0, le=1.0)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    def update_statistics(self) -> None:
        """Update population statistics."""
        if not self.individuals:
            return

        fitness_scores = [ind.total_fitness() for ind in self.individuals]
        self.average_fitness = sum(fitness_scores) / len(fitness_scores)
        self.best_fitness = max(fitness_scores)

        # Calculate constitutional compliance rate
        compliant_count = sum(
            1 for ind in self.individuals if ind.constitutional_compliance >= 0.8
        )
        self.constitutional_compliance_rate = compliant_count / len(self.individuals)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class EvolutionRequest(BaseModel):
    """Request for evolutionary computation process."""

    evolution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evolution_type: EvolutionType = Field(..., description="Type of evolution")
    status: EvolutionStatus = Field(default=EvolutionStatus.PENDING)

    # Request parameters
    initial_population: Optional[Population] = None
    target_fitness: float = Field(default=0.9, ge=0.0, le=1.0)
    max_generations: int = Field(default=100, ge=1, le=1000)
    population_size: int = Field(default=50, ge=10, le=500)

    # Constitutional requirements
    constitutional_compliance_required: bool = Field(default=True)
    safety_critical: bool = Field(default=False)
    human_oversight_required: bool = Field(default=False)

    # Metadata
    requester_id: str = Field(..., description="ID of requesting user/service")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class EvolutionResult(BaseModel):
    """Result of evolutionary computation process."""

    evolution_id: str = Field(..., description="Evolution request ID")
    status: EvolutionStatus = Field(..., description="Final status")

    # Results
    final_population: Optional[Population] = None
    best_individual: Optional[Individual] = None
    generations_completed: int = Field(default=0)

    # Performance metrics
    execution_time_seconds: float = Field(default=0.0)
    convergence_achieved: bool = Field(default=False)
    target_fitness_reached: bool = Field(default=False)

    # Constitutional compliance
    constitutional_compliance_verified: bool = Field(default=False)
    safety_validation_passed: bool = Field(default=False)

    # Metadata
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
