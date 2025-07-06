"""
Evolution API Schemas

Request and response schemas for evolutionary computation API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ..models.evolution import EvolutionStatus, EvolutionType, FitnessMetrics

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class EvolutionRequestCreate(BaseModel):
    """Schema for creating evolution requests."""
    
    evolution_type: EvolutionType = Field(..., description="Type of evolution")
    
    # Request parameters
    target_fitness: float = Field(default=0.9, ge=0.0, le=1.0, description="Target fitness score")
    max_generations: int = Field(default=100, ge=1, le=1000, description="Maximum generations")
    population_size: int = Field(default=50, ge=10, le=500, description="Population size")
    
    # Initial configuration
    initial_genotype: Optional[Dict[str, Any]] = Field(None, description="Initial genetic configuration")
    evolution_parameters: Dict[str, Any] = Field(default_factory=dict, description="Evolution parameters")
    
    # Constitutional requirements
    constitutional_compliance_required: bool = Field(default=True, description="Require constitutional compliance")
    safety_critical: bool = Field(default=False, description="Safety critical evolution")
    human_oversight_required: bool = Field(default=False, description="Require human oversight")
    
    # Metadata
    description: str = Field(default="", description="Evolution description")
    tags: List[str] = Field(default_factory=list, description="Evolution tags")


class EvolutionRequestResponse(BaseModel):
    """Schema for evolution request responses."""
    
    evolution_id: str = Field(..., description="Evolution request ID")
    evolution_type: EvolutionType = Field(..., description="Type of evolution")
    status: EvolutionStatus = Field(..., description="Current status")
    
    # Request parameters
    target_fitness: float = Field(..., description="Target fitness score")
    max_generations: int = Field(..., description="Maximum generations")
    population_size: int = Field(..., description="Population size")
    
    # Progress
    current_generation: int = Field(default=0, description="Current generation")
    best_fitness: float = Field(default=0.0, description="Best fitness achieved")
    average_fitness: float = Field(default=0.0, description="Average population fitness")
    
    # Constitutional compliance
    constitutional_compliance_required: bool = Field(..., description="Constitutional compliance required")
    constitutional_compliance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Metadata
    requester_id: str = Field(..., description="Requester ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FitnessEvaluationRequest(BaseModel):
    """Schema for fitness evaluation requests."""
    
    genotype: Dict[str, Any] = Field(..., description="Genetic representation to evaluate")
    evaluation_type: str = Field(default="comprehensive", description="Type of evaluation")
    
    # Evaluation parameters
    include_constitutional_compliance: bool = Field(default=True, description="Include constitutional compliance")
    include_safety_assessment: bool = Field(default=True, description="Include safety assessment")
    include_performance_metrics: bool = Field(default=True, description="Include performance metrics")
    
    # Context
    evolution_context: Dict[str, Any] = Field(default_factory=dict, description="Evolution context")


class FitnessEvaluationResponse(BaseModel):
    """Schema for fitness evaluation responses."""
    
    evaluation_id: str = Field(..., description="Evaluation ID")
    fitness_metrics: FitnessMetrics = Field(..., description="Comprehensive fitness metrics")
    
    # Evaluation details
    evaluation_time_ms: float = Field(..., description="Evaluation time in milliseconds")
    evaluation_successful: bool = Field(..., description="Evaluation success status")
    
    # Constitutional compliance
    constitutional_compliance_verified: bool = Field(..., description="Constitutional compliance verified")
    safety_validated: bool = Field(..., description="Safety validation passed")
    
    # Metadata
    evaluated_at: datetime = Field(..., description="Evaluation timestamp")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PopulationResponse(BaseModel):
    """Schema for population responses."""
    
    population_id: str = Field(..., description="Population ID")
    generation: int = Field(..., description="Generation number")
    size: int = Field(..., description="Population size")
    
    # Statistics
    average_fitness: float = Field(..., description="Average fitness")
    best_fitness: float = Field(..., description="Best fitness")
    worst_fitness: float = Field(..., description="Worst fitness")
    diversity_score: float = Field(..., description="Population diversity")
    
    # Constitutional compliance
    constitutional_compliance_rate: float = Field(..., ge=0.0, le=1.0, description="Compliance rate")
    safety_validation_rate: float = Field(..., ge=0.0, le=1.0, description="Safety validation rate")
    
    # Top individuals (limited for performance)
    top_individuals: List[Dict[str, Any]] = Field(default_factory=list, description="Top performing individuals")
    
    # Metadata
    created_at: datetime = Field(..., description="Creation timestamp")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EvolutionResultResponse(BaseModel):
    """Schema for evolution result responses."""
    
    evolution_id: str = Field(..., description="Evolution request ID")
    status: EvolutionStatus = Field(..., description="Final status")
    
    # Results summary
    generations_completed: int = Field(..., description="Generations completed")
    final_best_fitness: float = Field(..., description="Final best fitness")
    target_fitness_reached: bool = Field(..., description="Target fitness reached")
    convergence_achieved: bool = Field(..., description="Convergence achieved")
    
    # Performance metrics
    execution_time_seconds: float = Field(..., description="Total execution time")
    average_generation_time_ms: float = Field(..., description="Average generation time")
    
    # Constitutional compliance
    constitutional_compliance_verified: bool = Field(..., description="Constitutional compliance verified")
    safety_validation_passed: bool = Field(..., description="Safety validation passed")
    final_compliance_score: float = Field(..., ge=0.0, le=1.0, description="Final compliance score")
    
    # Best individual summary
    best_individual_summary: Optional[Dict[str, Any]] = Field(None, description="Best individual summary")
    
    # Metadata
    completed_at: datetime = Field(..., description="Completion timestamp")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
