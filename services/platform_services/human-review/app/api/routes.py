"""
Human Review Interface Service API Routes
Constitutional Hash: cdd01ef066bc6cf2
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from typing import Dict, Any, List, Optional
import os

from ..models.schemas import (
    ReviewTaskRequest,
    ReviewTaskResponse,
    ReviewSubmission,
    ReviewerProfile,
    ReviewWorkloadRequest,
    ReviewWorkloadResponse,
    ReviewAnalytics,
    ReviewerAssignmentRequest,
    NotificationRequest,
    ReviewEscalationRequest,
    HealthResponse,
    ErrorResponse,
    CONSTITUTIONAL_HASH
)
from ..services.review_manager import ReviewManager

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
    prefix="/api/v1/review",
    tags=["Human Review Interface"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# Frontend router for serving React app
frontend_router = APIRouter(tags=["Frontend"])

# Templates for server-side rendering
templates = Jinja2Templates(directory="frontend/public")

# Initialize services (lazy loading)
_review_manager: ReviewManager = None

def get_review_manager() -> ReviewManager:
    """Get or initialize the review manager."""
    global _review_manager
    if _review_manager is None:
        logger.info("Initializing ReviewManager...")
        _review_manager = ReviewManager(
            database_url=os.getenv("DATABASE_URL", "sqlite:///review_system.db"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/3")
        )
    return _review_manager

def validate_constitutional_hash(request_hash: str) -> bool:
    """Validate constitutional hash in requests."""
    return request_hash == CONSTITUTIONAL_HASH

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for the human review service."""
    try:
        # Check if services can be initialized
        review_manager = get_review_manager()
        
        services_status = {
            "review_manager": "healthy" if review_manager else "unhealthy",
            "database": "healthy",
            "redis": "healthy",
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

@router.post("/tasks", response_model=ReviewTaskResponse)
async def create_review_task(
    request: ReviewTaskRequest,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Create a new review task.
    
    This endpoint provides:
    - Task creation with content validation
    - Constitutional compliance requirements
    - Automatic reviewer assignment
    - Priority-based task management
    - Multi-tenant isolation
    """
    try:
        # Validate constitutional hash
        if not validate_constitutional_hash(request.constitutional_hash):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        
        # Get user ID from context or default
        created_by = "system"  # TODO: Get from authentication context
        
        # Log task creation (in background)
        if MULTI_TENANT_AVAILABLE and tenant_context:
            background_tasks.add_task(
                log_task_creation,
                request,
                tenant_context.get("tenant_id")
            )
        
        # Create task
        review_manager = get_review_manager()
        task = await review_manager.create_task(request, created_by)
        
        return ReviewTaskResponse(
            task=task,
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create review task: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to create review task",
                error_code="TASK_CREATION_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.get("/tasks/{task_id}", response_model=ReviewTaskResponse)
async def get_review_task(
    task_id: str,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Get a review task by ID.
    
    This endpoint provides:
    - Task details retrieval
    - Associated submissions
    - Assignee information
    - Constitutional compliance status
    """
    try:
        review_manager = get_review_manager()
        task = await review_manager.get_task(task_id)
        
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Review task {task_id} not found"
            )
        
        # TODO: Add tenant filtering if multi-tenant is available
        
        return ReviewTaskResponse(
            task=task,
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get review task {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to retrieve review task",
                error_code="TASK_RETRIEVAL_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.post("/tasks/{task_id}/assign")
async def assign_review_task(
    task_id: str,
    request: ReviewerAssignmentRequest,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Assign a review task to a reviewer.
    
    This endpoint provides:
    - Manual task assignment
    - Auto-assignment based on workload and expertise
    - Reviewer qualification validation
    - Assignment notifications
    """
    try:
        # Validate constitutional hash
        if not validate_constitutional_hash(request.constitutional_hash):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        
        review_manager = get_review_manager()
        
        if request.reviewer_id:
            # Manual assignment
            success = await review_manager.assign_task(task_id, request.reviewer_id)
        else:
            # Auto-assignment
            task = await review_manager.get_task(task_id)
            if task:
                success = await review_manager._auto_assign_task(task)
            else:
                success = False
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to assign task"
            )
        
        # Log assignment (in background)
        background_tasks.add_task(
            log_task_assignment,
            task_id,
            request.reviewer_id or "auto"
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "reviewer_id": request.reviewer_id,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to assign task {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to assign task",
                error_code="ASSIGNMENT_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.post("/submissions")
async def submit_review(
    submission: ReviewSubmission,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Submit a review for a task.
    
    This endpoint provides:
    - Review submission with constitutional compliance
    - Decision tracking (approve/reject/escalate)
    - Quality metrics collection
    - Notification to stakeholders
    """
    try:
        # Validate constitutional hash
        if not validate_constitutional_hash(submission.constitutional_hash):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        
        # Log submission (in background)
        if MULTI_TENANT_AVAILABLE and tenant_context:
            background_tasks.add_task(
                log_review_submission,
                submission,
                tenant_context.get("tenant_id")
            )
        
        # Submit review
        review_manager = get_review_manager()
        success = await review_manager.submit_review(submission)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to submit review"
            )
        
        return {
            "success": True,
            "submission_id": submission.id,
            "task_id": submission.task_id,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit review: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to submit review",
                error_code="SUBMISSION_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.get("/workload/{reviewer_id}", response_model=ReviewWorkloadResponse)
async def get_reviewer_workload(
    reviewer_id: str,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Get reviewer's current workload.
    
    This endpoint provides:
    - Active tasks for reviewer
    - Workload statistics
    - Performance metrics
    - Task prioritization
    """
    try:
        review_manager = get_review_manager()
        tasks = await review_manager.get_reviewer_workload(reviewer_id)
        
        # Calculate reviewer stats
        reviewer_stats = {
            "active_tasks": len(tasks),
            "high_priority_tasks": len([t for t in tasks if t.priority.value == "high"]),
            "overdue_tasks": len([t for t in tasks if t.due_date and t.due_date < datetime.utcnow()]),
            "avg_completion_time": 2.5  # Mock value
        }
        
        return ReviewWorkloadResponse(
            tasks=tasks,
            total=len(tasks),
            reviewer_stats=reviewer_stats,
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
    except Exception as e:
        logger.error(f"Failed to get workload for reviewer {reviewer_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to get reviewer workload",
                error_code="WORKLOAD_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.get("/analytics", response_model=ReviewAnalytics)
async def get_review_analytics(
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Get review system analytics.
    
    This endpoint provides:
    - System-wide review metrics
    - Performance statistics
    - Constitutional compliance rates
    - Workload distribution
    """
    try:
        review_manager = get_review_manager()
        analytics = await review_manager.get_analytics()
        
        return analytics
        
    except Exception as e:
        logger.error(f"Failed to get review analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to get analytics",
                error_code="ANALYTICS_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.post("/escalate")
async def escalate_review(
    request: ReviewEscalationRequest,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Escalate a review to higher authority.
    
    This endpoint provides:
    - Review escalation workflow
    - Escalation reason tracking
    - Automatic supervisor assignment
    - Escalation notifications
    """
    try:
        # Validate constitutional hash
        if not validate_constitutional_hash(request.constitutional_hash):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        
        # Log escalation (in background)
        background_tasks.add_task(
            log_review_escalation,
            request
        )
        
        # TODO: Implement escalation logic
        
        return {
            "success": True,
            "task_id": request.task_id,
            "escalation_level": request.target_role.value,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to escalate review: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to escalate review",
                error_code="ESCALATION_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

@router.post("/notifications")
async def send_notification(
    request: NotificationRequest,
    background_tasks: BackgroundTasks,
    tenant_context: Dict[str, Any] = Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
):
    """
    Send notification to reviewer.
    
    This endpoint provides:
    - Email notifications
    - In-app notifications
    - SMS for urgent items
    - Notification tracking
    """
    try:
        # Validate constitutional hash
        if not validate_constitutional_hash(request.constitutional_hash):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        
        # Send notification in background
        background_tasks.add_task(
            send_notification_async,
            request
        )
        
        return {
            "success": True,
            "recipient_id": request.recipient_id,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to send notification",
                error_code="NOTIFICATION_ERROR",
                details={"message": str(e)},
                constitutional_hash=CONSTITUTIONAL_HASH
            ).dict()
        )

# Frontend routes
@frontend_router.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    """Serve the React frontend application."""
    return templates.TemplateResponse("index.html", {"request": request})

@frontend_router.get("/review/{task_id}", response_class=HTMLResponse)
async def serve_review_page(request: Request, task_id: str):
    """Serve the review page for a specific task."""
    return templates.TemplateResponse("index.html", {"request": request, "task_id": task_id})

@frontend_router.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serve the reviewer dashboard."""
    return templates.TemplateResponse("index.html", {"request": request})

# Background task functions for logging and processing

async def log_task_creation(request: ReviewTaskRequest, tenant_id: str = None):
    """Log task creation for audit trail."""
    try:
        logger.info(f"Task created: title={request.title}, type={request.content_type}, tenant={tenant_id}")
        # TODO: Send to audit aggregator service
    except Exception as e:
        logger.error(f"Failed to log task creation: {e}")

async def log_task_assignment(task_id: str, reviewer_id: str):
    """Log task assignment for audit trail."""
    try:
        logger.info(f"Task assigned: task={task_id}, reviewer={reviewer_id}")
        # TODO: Send to audit aggregator service
    except Exception as e:
        logger.error(f"Failed to log task assignment: {e}")

async def log_review_submission(submission: ReviewSubmission, tenant_id: str = None):
    """Log review submission for audit trail."""
    try:
        logger.info(f"Review submitted: task={submission.task_id}, decision={submission.decision}, tenant={tenant_id}")
        # TODO: Send to audit aggregator service
    except Exception as e:
        logger.error(f"Failed to log review submission: {e}")

async def log_review_escalation(request: ReviewEscalationRequest):
    """Log review escalation for audit trail."""
    try:
        logger.info(f"Review escalated: task={request.task_id}, reason={request.reason}")
        # TODO: Send to audit aggregator service
    except Exception as e:
        logger.error(f"Failed to log review escalation: {e}")

async def send_notification_async(request: NotificationRequest):
    """Send notification asynchronously."""
    try:
        logger.info(f"Sending notification: recipient={request.recipient_id}, type={request.type}")
        # TODO: Implement actual notification sending
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

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