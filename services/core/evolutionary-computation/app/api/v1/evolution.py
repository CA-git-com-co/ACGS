"""
Evolution API Router

API endpoints for evolutionary computation operations with constitutional compliance
and ACGS integration.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from ...models.evolution import EvolutionRequest, EvolutionStatus, EvolutionType, Individual
from ...schemas.evolution import (
    EvolutionRequestCreate,
    EvolutionRequestResponse,
    EvolutionResultResponse,
    FitnessEvaluationRequest,
    FitnessEvaluationResponse,
)
from ...schemas.responses import ErrorResponse, SuccessResponse
from ...services.evolution_service import EvolutionService
from ...services.fitness_service import FitnessService

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/evolution", tags=["evolution"])

# Service dependencies (would be injected in production)
evolution_service = EvolutionService()
fitness_service = FitnessService()


@router.post("/requests", response_model=EvolutionRequestResponse)
async def create_evolution_request(
    request_data: EvolutionRequestCreate,
    requester_id: str = "api_user"  # Would come from authentication
) -> EvolutionRequestResponse:
    """
    Create a new evolution request with constitutional compliance validation.
    
    Creates an evolution request for processing with comprehensive constitutional
    compliance checking and ACGS integration.
    """
    try:
        # Create evolution request
        evolution_request = await evolution_service.create_evolution_request(
            evolution_type=request_data.evolution_type,
            requester_id=requester_id,
            target_fitness=request_data.target_fitness,
            max_generations=request_data.max_generations,
            population_size=request_data.population_size,
            constitutional_compliance_required=request_data.constitutional_compliance_required,
            safety_critical=request_data.safety_critical,
            human_oversight_required=request_data.human_oversight_required,
            description=request_data.description
        )
        
        # Convert to response model
        response = EvolutionRequestResponse(
            evolution_id=evolution_request.evolution_id,
            evolution_type=evolution_request.evolution_type,
            status=evolution_request.status,
            target_fitness=evolution_request.target_fitness,
            max_generations=evolution_request.max_generations,
            population_size=evolution_request.population_size,
            constitutional_compliance_required=evolution_request.constitutional_compliance_required,
            requester_id=evolution_request.requester_id,
            created_at=evolution_request.created_at,
            updated_at=evolution_request.updated_at,
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
        logger.info(f"Evolution request created: {evolution_request.evolution_id}")
        return response
        
    except Exception as e:
        logger.error(f"Failed to create evolution request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create evolution request: {str(e)}"
        )


@router.post("/requests/{evolution_id}/submit", response_model=SuccessResponse)
async def submit_evolution_request(evolution_id: str) -> SuccessResponse:
    """
    Submit evolution request for processing.
    
    Submits an existing evolution request to the evolution engine for processing
    with constitutional compliance validation.
    """
    try:
        # Get evolution request
        evolution_request = await evolution_service.get_evolution_status(evolution_id)
        if not evolution_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evolution request not found: {evolution_id}"
            )
        
        # Submit for processing
        submitted_id = await evolution_service.submit_evolution_request(evolution_request)
        
        return SuccessResponse(
            message=f"Evolution request submitted successfully",
            data={
                "evolution_id": submitted_id,
                "status": "submitted",
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit evolution request {evolution_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit evolution request: {str(e)}"
        )


@router.get("/requests/{evolution_id}", response_model=EvolutionRequestResponse)
async def get_evolution_request(evolution_id: str) -> EvolutionRequestResponse:
    """
    Get evolution request status and details.
    
    Retrieves the current status and details of an evolution request with
    O(1) lookup performance.
    """
    try:
        # Get evolution request with O(1) lookup
        evolution_request = await evolution_service.get_evolution_status(evolution_id)
        if not evolution_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evolution request not found: {evolution_id}"
            )
        
        # Convert to response model
        response = EvolutionRequestResponse(
            evolution_id=evolution_request.evolution_id,
            evolution_type=evolution_request.evolution_type,
            status=evolution_request.status,
            target_fitness=evolution_request.target_fitness,
            max_generations=evolution_request.max_generations,
            population_size=evolution_request.population_size,
            constitutional_compliance_required=evolution_request.constitutional_compliance_required,
            requester_id=evolution_request.requester_id,
            created_at=evolution_request.created_at,
            updated_at=evolution_request.updated_at,
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get evolution request {evolution_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get evolution request: {str(e)}"
        )


@router.get("/requests", response_model=List[EvolutionRequestResponse])
async def list_evolution_requests(
    status_filter: Optional[EvolutionStatus] = None,
    evolution_type_filter: Optional[EvolutionType] = None,
    limit: int = 100
) -> List[EvolutionRequestResponse]:
    """
    List evolution requests with optional filtering.
    
    Retrieves a list of evolution requests with optional filtering by status
    and evolution type.
    """
    try:
        # This would typically query a database
        # For now, return empty list as placeholder
        return []
        
    except Exception as e:
        logger.error(f"Failed to list evolution requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list evolution requests: {str(e)}"
        )


@router.post("/fitness/evaluate", response_model=FitnessEvaluationResponse)
async def evaluate_fitness(
    request_data: FitnessEvaluationRequest
) -> FitnessEvaluationResponse:
    """
    Evaluate fitness for a genetic representation.
    
    Performs comprehensive fitness evaluation with constitutional compliance
    validation and automated scoring.
    """
    try:
        # Create individual from genotype
        individual = Individual(
            genotype=request_data.genotype,
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
        # Evaluate fitness
        evaluated_individual = await evolution_service.evaluate_individual_fitness(individual)
        
        if not evaluated_individual.fitness_metrics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Fitness evaluation failed"
            )
        
        # Create response
        response = FitnessEvaluationResponse(
            evaluation_id=evaluated_individual.individual_id,
            fitness_metrics=evaluated_individual.fitness_metrics,
            evaluation_time_ms=0.0,  # Would be measured in production
            evaluation_successful=True,
            constitutional_compliance_verified=evaluated_individual.safety_validated,
            safety_validated=evaluated_individual.safety_validated,
            evaluated_at=evaluated_individual.fitness_metrics.evaluation_timestamp,
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to evaluate fitness: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate fitness: {str(e)}"
        )


@router.post("/fitness/quick-evaluate")
async def quick_evaluate_fitness(
    request_data: FitnessEvaluationRequest
) -> JSONResponse:
    """
    Perform quick fitness evaluation for performance-critical scenarios.
    
    Provides rapid fitness evaluation with sub-5ms P99 latency targets
    for real-time evolutionary computation scenarios.
    """
    try:
        # Create individual from genotype
        individual = Individual(
            genotype=request_data.genotype,
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
        # Quick fitness evaluation
        quick_fitness = await fitness_service.evaluate_quick_fitness(individual)
        
        return JSONResponse(
            content={
                "fitness_score": quick_fitness,
                "evaluation_type": "quick",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": individual.created_at.isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to perform quick fitness evaluation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform quick fitness evaluation: {str(e)}"
        )


@router.get("/health")
async def evolution_health_check() -> JSONResponse:
    """
    Health check endpoint for evolution service.
    
    Provides health status for the evolution service components with
    constitutional compliance validation.
    """
    try:
        health_status = await evolution_service.get_service_health()
        
        return JSONResponse(
            content={
                "status": "healthy",
                "service": "evolution_api",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "evolution_service": health_status,
                "timestamp": health_status["timestamp"]
            }
        )
        
    except Exception as e:
        logger.error(f"Evolution health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "evolution_api",
                "error": str(e),
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        )
