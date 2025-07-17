"""
Recommendation System Service API Routes
Constitutional Hash: cdd01ef066bc6cf2
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, List
import os

from ..models.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    UserInteraction,
    FeedbackRequest,
    ContentItem,
    VectorIndexRequest,
    RecommendationAnalytics,
    PersonalizationMetrics,
    HealthResponse,
    ErrorResponse,
    CONSTITUTIONAL_HASH
)
from ..agents.recommendation_agent import RecommendationAgent
from ..services.vector_service import VectorService
from ..services.collaborative_filtering import CollaborativeFilteringService

# Try to import shared services
try:
    from services.shared.middleware.tenant_middleware import get_tenant_context
    from services.shared.middleware.error_handling import setup_error_handlers
    MULTI_TENANT_AVAILABLE = True
except ImportError:
    MULTI_TENANT_AVAILABLE = False
    get_tenant_context = lambda: None

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/v1/recommendations",
    tags=["Recommendation System"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# Initialize services (lazy loading)
_recommendation_agent: RecommendationAgent = None
_vector_service: VectorService = None
_collaborative_service: CollaborativeFilteringService = None

def get_recommendation_agent() -> RecommendationAgent:
    """Get or initialize the recommendation agent."""
    global _recommendation_agent
    if _recommendation_agent is None:
        logger.info("Initializing RecommendationAgent...")
        _recommendation_agent = RecommendationAgent(
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            vector_redis_url=os.getenv("VECTOR_REDIS_URL", "redis://localhost:6379/1"),
            collab_redis_url=os.getenv("COLLAB_REDIS_URL", "redis://localhost:6379/2")
        )
    return _recommendation_agent

def get_vector_service() -> VectorService:
    """Get or initialize the vector service."""
    global _vector_service
    if _vector_service is None:
        logger.info("Initializing VectorService...")
        _vector_service = VectorService(
            redis_url=os.getenv("VECTOR_REDIS_URL", "redis://localhost:6379/1")
        )
    return _vector_service

def get_collaborative_service() -> CollaborativeFilteringService:
    """Get or initialize the collaborative filtering service."""
    global _collaborative_service
    if _collaborative_service is None:
        logger.info("Initializing CollaborativeFilteringService...")
        _collaborative_service = CollaborativeFilteringService(
            redis_url=os.getenv("COLLAB_REDIS_URL", "redis://localhost:6379/2")
        )
    return _collaborative_service

def validate_constitutional_hash(request_hash: str) -> bool:
    """Validate constitutional hash in requests."""
    return request_hash == CONSTITUTIONAL_HASH

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for the recommendation system service."""
    try:
        # Check if services can be initialized
        recommendation_agent = get_recommendation_agent()
        vector_service = get_vector_service()
        collaborative_service = get_collaborative_service()
        
        services_status = {
            "recommendation_agent": "healthy" if recommendation_agent else "unhealthy",
            "vector_service": "healthy" if vector_service else "unhealthy",
            "collaborative_service": "healthy" if collaborative_service else "unhealthy",
            "constitutional_validation": "enabled"
        }
        
        return HealthResponse(
            status="healthy",
            constitutional_hash=CONSTITUTIONAL_HASH,
            version="1.0.0",
            services=services_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Get personalized recommendations for a user.
    
    This endpoint provides:
    - Multiple recommendation strategies (collaborative, content-based, hybrid)
    - Constitutional compliance filtering
    - Vector similarity search
    - Personalization based on user interactions
    - Multi-tenant support
    """
    try:
        # Validate constitutional hash
        if not validate_constitutional_hash(request.constitutional_hash):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        
        # Log request (in background)
        if MULTI_TENANT_AVAILABLE and tenant_context:
            background_tasks.add_task(
                log_recommendation_request,
                request,
                tenant_context.get("tenant_id")
            )
        
        # Get recommendation agent and generate recommendations
        recommendation_agent = get_recommendation_agent()
        response = await recommendation_agent.get_recommendations(request)
        
        # Log response (in background)
        background_tasks.add_task(log_recommendation_response, response)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Recommendation generation failed",
                error_code="RECOMMENDATION_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.post("/interaction")
async def add_user_interaction(
    interaction: UserInteraction,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Add user interaction for learning and personalization.
    
    This endpoint provides:
    - User interaction tracking (views, likes, shares, ratings)
    - Constitutional compliance validation
    - Personalization improvement
    - Multi-tenant isolation
    """
    try:
        # Validate constitutional compliance
        if not interaction.constitutional_compliant:
            logger.warning(f"Non-compliant interaction: {interaction.id}")
        
        # Log interaction (in background)
        if MULTI_TENANT_AVAILABLE and tenant_context:
            background_tasks.add_task(
                log_user_interaction,
                interaction,
                tenant_context.get("tenant_id")
            )
        
        # Add to recommendation agent
        recommendation_agent = get_recommendation_agent()
        success = await recommendation_agent.add_user_interaction(interaction)
        
        return {
            "success": success,
            "interaction_id": interaction.id,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
    except Exception as e:
        logger.error(f"Failed to add user interaction: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to add interaction",
                error_code="INTERACTION_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.post("/feedback")
async def add_feedback(
    feedback: FeedbackRequest,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Add user feedback on recommendations.
    
    This endpoint provides:
    - Feedback collection for recommendation improvement
    - Constitutional compliance validation
    - Rating and comment support
    - Multi-tenant feedback isolation
    """
    try:
        # Validate constitutional hash
        if not validate_constitutional_hash(feedback.constitutional_hash):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        
        # Log feedback (in background)
        if MULTI_TENANT_AVAILABLE and tenant_context:
            background_tasks.add_task(
                log_user_feedback,
                feedback,
                tenant_context.get("tenant_id")
            )
        
        # TODO: Process feedback for model improvement
        
        return {
            "success": True,
            "feedback_id": feedback.recommendation_id,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to add feedback",
                error_code="FEEDBACK_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.post("/content/index")
async def index_content(
    content: ContentItem,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Index content for recommendations.
    
    This endpoint provides:
    - Content indexing with vector embeddings
    - Constitutional compliance scoring
    - Multi-tenant content isolation
    - Automatic embedding generation
    """
    try:
        # Log content indexing (in background)
        if MULTI_TENANT_AVAILABLE and tenant_context:
            background_tasks.add_task(
                log_content_indexing,
                content,
                tenant_context.get("tenant_id")
            )
        
        # Index content with vector service
        vector_service = get_vector_service()
        success = await vector_service.index_content(content)
        
        return {
            "success": success,
            "content_id": content.id,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
    except Exception as e:
        logger.error(f"Failed to index content: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to index content",
                error_code="INDEXING_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.get("/analytics/{user_id}", response_model=PersonalizationMetrics)
async def get_user_analytics(
    user_id: str,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Get personalization analytics for a user.
    
    This endpoint provides:
    - Personalization effectiveness metrics
    - Diversity and novelty scores
    - Constitutional alignment analysis
    - User satisfaction metrics
    """
    try:
        # Get analytics from recommendation agent
        recommendation_agent = get_recommendation_agent()
        analytics = await recommendation_agent.get_recommendation_analytics(user_id)
        
        return analytics
        
    except Exception as e:
        logger.error(f"Failed to get user analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to get analytics",
                error_code="ANALYTICS_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.get("/stats", response_model=Dict[str, Any])
async def get_system_stats(
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Get system statistics for the recommendation system.
    
    This endpoint provides:
    - Vector index statistics
    - Collaborative filtering statistics
    - Constitutional compliance metrics
    - Performance metrics
    """
    try:
        # Get stats from all services
        vector_service = get_vector_service()
        collaborative_service = get_collaborative_service()
        
        vector_stats = await vector_service.get_index_stats()
        collaborative_stats = await collaborative_service.get_collaborative_stats()
        
        return {
            "vector_stats": vector_stats,
            "collaborative_stats": collaborative_stats,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to get system stats",
                error_code="STATS_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.post("/train")
async def train_models(
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Train recommendation models.
    
    This endpoint provides:
    - Matrix factorization model training
    - Constitutional compliance model updates
    - Background training process
    - Performance improvement
    """
    try:
        # Start training in background
        background_tasks.add_task(train_recommendation_models)
        
        return {
            "success": True,
            "message": "Model training started in background",
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
    except Exception as e:
        logger.error(f"Failed to start model training: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to start training",
                error_code="TRAINING_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

# Background task functions for logging and processing

async def log_recommendation_request(request: RecommendationRequest, tenant_id: str = None):
    """Log recommendation request for audit trail."""
    try:
        logger.info(f"Recommendation request: user={request.user_id}, type={request.recommendation_type}, tenant={tenant_id}")
        # TODO: Send to audit aggregator service
    except Exception as e:
        logger.error(f"Failed to log recommendation request: {e}")

async def log_recommendation_response(response: RecommendationResponse):
    """Log recommendation response for audit trail."""
    try:
        logger.info(f"Recommendation response: user={response.user_id}, count={len(response.recommendations)}, score={response.personalization_score}")
        # TODO: Send to audit aggregator service
    except Exception as e:
        logger.error(f"Failed to log recommendation response: {e}")

async def log_user_interaction(interaction: UserInteraction, tenant_id: str = None):
    """Log user interaction for audit trail."""
    try:
        logger.info(f"User interaction: user={interaction.user_id}, content={interaction.content_id}, type={interaction.interaction_type}, tenant={tenant_id}")
        # TODO: Send to audit aggregator service
    except Exception as e:
        logger.error(f"Failed to log user interaction: {e}")

async def log_user_feedback(feedback: FeedbackRequest, tenant_id: str = None):
    """Log user feedback for audit trail."""
    try:
        logger.info(f"User feedback: user={feedback.user_id}, content={feedback.content_id}, type={feedback.feedback_type}, tenant={tenant_id}")
        # TODO: Send to audit aggregator service
    except Exception as e:
        logger.error(f"Failed to log user feedback: {e}")

async def log_content_indexing(content: ContentItem, tenant_id: str = None):
    """Log content indexing for audit trail."""
    try:
        logger.info(f"Content indexing: content={content.id}, type={content.content_type}, tenant={tenant_id}")
        # TODO: Send to audit aggregator service
    except Exception as e:
        logger.error(f"Failed to log content indexing: {e}")

async def train_recommendation_models():
    """Train recommendation models in background."""
    try:
        logger.info("Starting model training...")
        
        # Train collaborative filtering model
        collaborative_service = get_collaborative_service()
        await collaborative_service.train_matrix_factorization()
        
        logger.info("Model training completed")
        
    except Exception as e:
        logger.error(f"Model training failed: {e}")

# Error handlers
@router.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors."""
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error=str(exc),
            error_code="VALIDATION_ERROR",
            constitutional_hash=CONSTITUTIONAL_HASH
        ).dict()
    )

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            error_code="INTERNAL_ERROR",
            constitutional_hash=CONSTITUTIONAL_HASH
        ).dict()
    )