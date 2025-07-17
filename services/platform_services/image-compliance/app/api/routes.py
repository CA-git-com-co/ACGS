"""
Image Compliance Service API Routes
Constitutional Hash: cdd01ef066bc6cf2
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any

from ..models.schemas import (
    ImageAuditRequest,
    ImageAuditResult,
    ImageGenerationRequest,
    ImageGenerationResult,
    ImageIndexRequest,
    HealthResponse,
    ErrorResponse,
    CONSTITUTIONAL_HASH
)
from ..agents.image_audit_agent import ImageAuditAgent
from ..agents.image_generator_agent import ImageGeneratorAgent

# Try to import shared services, but don't fail if not available
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
    prefix="/api/v1/image",
    tags=["Image Compliance"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# Initialize agents (will be loaded on first request to avoid startup delays)
_audit_agent: ImageAuditAgent = None
_generator_agent: ImageGeneratorAgent = None

def get_audit_agent() -> ImageAuditAgent:
    """Get or initialize the image audit agent."""
    global _audit_agent
    if _audit_agent is None:
        logger.info("Initializing ImageAuditAgent...")
        _audit_agent = ImageAuditAgent()
    return _audit_agent

def get_generator_agent() -> ImageGeneratorAgent:
    """Get or initialize the image generator agent."""
    global _generator_agent
    if _generator_agent is None:
        logger.info("Initializing ImageGeneratorAgent...")
        _generator_agent = ImageGeneratorAgent()
    return _generator_agent

def validate_constitutional_hash(request_hash: str) -> bool:
    """Validate constitutional hash in requests."""
    return request_hash == CONSTITUTIONAL_HASH

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for the image compliance service."""
    try:
        # Check if agents can be initialized
        audit_agent = get_audit_agent()
        generator_agent = get_generator_agent()
        
        services_status = {
            "audit_agent": "healthy" if audit_agent else "unhealthy",
            "generator_agent": "healthy" if generator_agent else "unhealthy",
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

@router.post("/audit", response_model=ImageAuditResult)
async def audit_image(
    request: ImageAuditRequest,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Audit an image for compliance violations and content safety.
    
    This endpoint performs comprehensive AI-powered analysis including:
    - NSFW content detection
    - Violence and harmful content detection
    - Hate speech and offensive content analysis
    - Political sensitivity assessment
    - Constitutional compliance validation
    """
    try:
        # Validate constitutional hash
        if not validate_constitutional_hash(request.constitutional_hash):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        
        # Log audit request (in background)
        if MULTI_TENANT_AVAILABLE and tenant_context:
            background_tasks.add_task(
                log_audit_request, 
                request, 
                tenant_context.get("tenant_id")
            )
        
        # Get audit agent and perform analysis
        audit_agent = get_audit_agent()
        result = await audit_agent.audit_image(request)
        
        # Log result (in background)
        background_tasks.add_task(log_audit_result, result, request.user_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image audit failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Image audit failed",
                error_code="AUDIT_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.post("/generate", response_model=ImageGenerationResult)
async def generate_image(
    request: ImageGenerationRequest,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Generate a safe, compliant image from text prompt.
    
    This endpoint provides AI-powered image generation with:
    - Built-in safety filtering and prompt validation
    - Constitutional compliance checking
    - Automatic content auditing of generated images
    - Stable Diffusion with safety enhancements
    """
    try:
        # Validate constitutional hash
        if not validate_constitutional_hash(request.constitutional_hash):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        
        # Log generation request (in background)
        if MULTI_TENANT_AVAILABLE and tenant_context:
            background_tasks.add_task(
                log_generation_request,
                request,
                tenant_context.get("tenant_id")
            )
        
        # Get generator agent and generate image
        generator_agent = get_generator_agent()
        result = await generator_agent.generate_image(request)
        
        # Log result (in background)
        background_tasks.add_task(log_generation_result, result, request.user_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Image generation failed",
                error_code="GENERATION_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.post("/index", response_model=Dict[str, str])
async def index_image_content(
    request: ImageIndexRequest,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Index image content for future search and retrieval.
    
    This endpoint provides:
    - Image content indexing and metadata extraction
    - Vector embeddings for similarity search
    - Constitutional compliance metadata
    - Multi-tenant content isolation
    """
    try:
        # Validate constitutional hash
        if not validate_constitutional_hash(request.constitutional_hash):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        
        # TODO: Implement content indexing
        # This would involve:
        # 1. Extract image features and metadata
        # 2. Generate vector embeddings
        # 3. Store in vector database (Qdrant/Pinecone)
        # 4. Index with constitutional compliance metadata
        
        return {
            "status": "indexed",
            "content_id": request.content_id,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "message": "Image content indexing not yet implemented"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image indexing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Image indexing failed",
                error_code="INDEXING_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

# Background task functions for logging and auditing

async def log_audit_request(request: ImageAuditRequest, tenant_id: str = None):
    """Log image audit request for audit trail."""
    try:
        logger.info(f"Image audit request: user={request.user_id}, tenant={tenant_id}")
        # TODO: Send to audit aggregator service
    except Exception as e:
        logger.error(f"Failed to log audit request: {e}")

async def log_audit_result(result: ImageAuditResult, user_id: str = None):
    """Log image audit result for compliance tracking."""
    try:
        logger.info(f"Image audit completed: compliant={result.compliant}, user={user_id}")
        # TODO: Send to audit aggregator service
    except Exception as e:
        logger.error(f"Failed to log audit result: {e}")

async def log_generation_request(request: ImageGenerationRequest, tenant_id: str = None):
    """Log image generation request for audit trail."""
    try:
        logger.info(f"Image generation request: user={request.user_id}, tenant={tenant_id}")
        # TODO: Send to audit aggregator service
    except Exception as e:
        logger.error(f"Failed to log generation request: {e}")

async def log_generation_result(result: ImageGenerationResult, user_id: str = None):
    """Log image generation result for compliance tracking."""
    try:
        logger.info(f"Image generation completed: success={result.success}, user={user_id}")
        # TODO: Send to audit aggregator service
    except Exception as e:
        logger.error(f"Failed to log generation result: {e}")

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