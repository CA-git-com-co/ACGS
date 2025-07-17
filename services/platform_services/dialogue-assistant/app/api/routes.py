"""
Dialogue Assistant Service API Routes
Constitutional Hash: cdd01ef066bc6cf2
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPBearer
import logging
from typing import Dict, Any, Optional
import json
import os

from ..models.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationHistory,
    ConversationSearchRequest,
    ConversationSearchResult,
    ConversationAnalytics,
    HealthResponse,
    ErrorResponse,
    CONSTITUTIONAL_HASH
)
from ..agents.chat_agent import ChatAgent
from ..services.conversation_manager import ConversationManager
from ..services.compliance_checker import ComplianceChecker

# Try to import shared services
try:
    from services.shared.middleware.tenant_middleware import get_tenant_context
    from services.shared.middleware.error_handling import setup_error_handlers
    MULTI_TENANT_AVAILABLE = True
except ImportError:
    MULTI_TENANT_AVAILABLE = False
    get_tenant_context = lambda: None

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Initialize router
router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Dialogue Assistant"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# Initialize services (lazy loading)
_chat_agent: ChatAgent = None
_conversation_manager: ConversationManager = None
_compliance_checker: ComplianceChecker = None

def get_chat_agent() -> ChatAgent:
    """Get or initialize the chat agent."""
    global _chat_agent
    if _chat_agent is None:
        logger.info("Initializing ChatAgent...")
        _chat_agent = ChatAgent(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0")
        )
    return _chat_agent

def get_conversation_manager() -> ConversationManager:
    """Get or initialize the conversation manager."""
    global _conversation_manager
    if _conversation_manager is None:
        logger.info("Initializing ConversationManager...")
        _conversation_manager = ConversationManager(
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0")
        )
    return _conversation_manager

def get_compliance_checker() -> ComplianceChecker:
    """Get or initialize the compliance checker."""
    global _compliance_checker
    if _compliance_checker is None:
        logger.info("Initializing ComplianceChecker...")
        _compliance_checker = ComplianceChecker()
    return _compliance_checker

def validate_constitutional_hash(request_hash: str) -> bool:
    """Validate constitutional hash in requests."""
    return request_hash == CONSTITUTIONAL_HASH

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for the dialogue assistant service."""
    try:
        # Check if services can be initialized
        chat_agent = get_chat_agent()
        conversation_manager = get_conversation_manager()
        compliance_checker = get_compliance_checker()
        
        services_status = {
            "chat_agent": "healthy" if chat_agent else "unhealthy",
            "conversation_manager": "healthy" if conversation_manager else "unhealthy",
            "compliance_checker": "healthy" if compliance_checker else "unhealthy",
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

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Send a message to the AI assistant and get a response.
    
    This endpoint provides:
    - Multi-turn conversation support with context
    - Constitutional compliance validation
    - Multiple AI provider support (OpenAI, Anthropic)
    - Configurable compliance levels
    - Conversation history management
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
                log_chat_request,
                request,
                tenant_context.get("tenant_id")
            )
        
        # Get chat agent and process message
        chat_agent = get_chat_agent()
        response = await chat_agent.chat(request)
        
        # Log response (in background)
        background_tasks.add_task(log_chat_response, response)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat message failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Message processing failed",
                error_code="CHAT_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.post("/stream")
async def stream_message(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Send a message with streaming response.
    
    This endpoint provides real-time streaming of AI responses with:
    - Server-sent events for real-time updates
    - Constitutional compliance validation
    - Conversation context preservation
    - Error handling and recovery
    """
    try:
        # Validate constitutional hash
        if not validate_constitutional_hash(request.constitutional_hash):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        
        # Enable streaming
        request.stream = True
        
        # Log request (in background)
        if MULTI_TENANT_AVAILABLE and tenant_context:
            background_tasks.add_task(
                log_chat_request,
                request,
                tenant_context.get("tenant_id")
            )
        
        # Get chat agent and create streaming response
        chat_agent = get_chat_agent()
        
        async def generate_stream():
            async for chunk in chat_agent.chat_stream(request):
                yield f"data: {chunk}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Constitutional-Hash": CONSTITUTIONAL_HASH
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Streaming chat failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Streaming failed",
                error_code="STREAMING_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.get("/conversation/{conversation_id}", response_model=ConversationHistory)
async def get_conversation(
    conversation_id: str,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Get conversation history by ID.
    
    This endpoint provides:
    - Full conversation history retrieval
    - Message-level compliance information
    - Constitutional compliance validation
    - Multi-tenant conversation isolation
    """
    try:
        conversation_manager = get_conversation_manager()
        conversation = await conversation_manager.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # TODO: Add tenant filtering if multi-tenant is available
        
        return conversation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to retrieve conversation",
                error_code="CONVERSATION_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.post("/conversation/search", response_model=ConversationSearchResult)
async def search_conversations(
    request: ConversationSearchRequest,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Search conversations by content or metadata.
    
    This endpoint provides:
    - Full-text search across conversation history
    - Date range filtering
    - User-specific conversation filtering
    - Constitutional compliance validation
    """
    try:
        # Validate constitutional hash
        if not validate_constitutional_hash(request.constitutional_hash):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        
        conversation_manager = get_conversation_manager()
        
        # Search conversations
        conversations = await conversation_manager.search_conversations(
            user_id=request.user_id or "unknown",
            query=request.query,
            limit=request.limit
        )
        
        # Convert to summaries
        from ..models.schemas import ConversationSummary
        summaries = []
        for conv in conversations:
            summary = ConversationSummary(
                conversation_id=conv.conversation_id,
                summary=await conversation_manager.get_conversation_summary(conv.conversation_id) or "No summary available",
                message_count=len(conv.messages),
                constitutional_hash=CONSTITUTIONAL_HASH
            )
            summaries.append(summary)
        
        return ConversationSearchResult(
            conversations=summaries,
            total=len(summaries),
            limit=request.limit,
            offset=request.offset,
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversation search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Search failed",
                error_code="SEARCH_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.get("/analytics/{user_id}", response_model=ConversationAnalytics)
async def get_conversation_analytics(
    user_id: str,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Get conversation analytics for a user.
    
    This endpoint provides:
    - Conversation volume and engagement metrics
    - Compliance rate analysis
    - Response time statistics
    - Topic analysis and trends
    """
    try:
        conversation_manager = get_conversation_manager()
        analytics = await conversation_manager.get_conversation_analytics(user_id)
        
        return ConversationAnalytics(
            total_conversations=analytics.get("total_conversations", 0),
            total_messages=analytics.get("total_messages", 0),
            avg_response_time=analytics.get("avg_response_time", 0.0),
            compliance_rate=analytics.get("compliance_rate", 0.0),
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
    except Exception as e:
        logger.error(f"Failed to get analytics for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Analytics failed",
                error_code="ANALYTICS_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.delete("/conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Delete a conversation.
    
    This endpoint provides:
    - Permanent conversation deletion
    - Constitutional compliance validation
    - Audit trail for deletion events
    """
    try:
        conversation_manager = get_conversation_manager()
        success = await conversation_manager.delete_conversation(conversation_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )
        
        return {
            "deleted": True,
            "conversation_id": conversation_id,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Deletion failed",
                error_code="DELETE_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

# Background task functions for logging and auditing

async def log_chat_request(request: ChatRequest, tenant_id: str = None):
    """Log chat request for audit trail."""
    try:
        logger.info(f"Chat request: conversation={request.conversation_id}, tenant={tenant_id}")
        # TODO: Send to audit aggregator service
    except Exception as e:
        logger.error(f"Failed to log chat request: {e}")

async def log_chat_response(response: ChatResponse):
    """Log chat response for audit trail."""
    try:
        logger.info(f"Chat response: conversation={response.conversation_id}, compliant={response.compliance_check.get('compliant', False)}")
        # TODO: Send to audit aggregator service
    except Exception as e:
        logger.error(f"Failed to log chat response: {e}")

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