"""
DGM operations endpoints.

Comprehensive API for Darwin Gödel Machine self-improvement operations,
bandit algorithms, performance monitoring, and constitutional compliance.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from ...cache import get_cache_manager
from ...core.archive_manager import ArchiveManager
from ...core.bandit_algorithms import BanditAlgorithmManager
from ...core.dgm_engine import DGMEngine
from ...core.performance_monitor import PerformanceMonitor
from ...database.performance_optimizer import get_performance_optimizer
from ...storage.archive_manager import ArchiveManager as StorageArchiveManager
from .models import (
    ArchiveListResponse,
    BanditReport,
    ErrorResponse,
    ImprovementRequest,
    ImprovementResponse,
    PerformanceReport,
    RollbackRequest,
    RollbackResponse,
)


# Additional Request/Response Models
class BanditActionRequest(BaseModel):
    """Request model for bandit algorithm actions."""

    context_key: str = Field(
        ..., description="Context identifier for the bandit problem"
    )
    algorithm_type: str = Field(
        default="conservative_bandit", description="Type of bandit algorithm"
    )
    exploration_rate: Optional[float] = Field(
        default=0.1, ge=0.0, le=1.0, description="Exploration rate"
    )
    safety_threshold: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Safety threshold"
    )

    @validator("algorithm_type")
    def validate_algorithm_type(cls, v):
        allowed_types = [
            "epsilon_greedy",
            "ucb1",
            "thompson_sampling",
            "conservative_bandit",
            "safe_exploration",
        ]
        if v not in allowed_types:
            raise ValueError(f"algorithm_type must be one of {allowed_types}")
        return v


class BanditActionResponse(BaseModel):
    """Response model for bandit algorithm actions."""

    selected_arm: str
    confidence: float
    expected_reward: float
    exploration_factor: float
    safety_validated: bool
    constitutional_compliance: bool


class RewardFeedbackRequest(BaseModel):
    """Request model for providing reward feedback."""

    context_key: str = Field(..., description="Context identifier")
    arm_id: str = Field(..., description="Arm identifier that was selected")
    reward: float = Field(..., description="Reward value received")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )


class DGMStatusResponse(BaseModel):
    """Response model for DGM system status."""

    status: str
    version: str
    uptime_seconds: float
    active_improvements: int
    total_improvements: int
    success_rate: float
    constitutional_compliance_score: float
    performance_metrics: Dict[str, Any]
    system_health: Dict[str, Any]
    last_optimization: Optional[datetime]


class PerformanceMetricsRequest(BaseModel):
    """Request model for performance metrics query."""

    metric_name: str = Field(..., description="Name of the metric")
    start_time: datetime = Field(..., description="Start time for metrics query")
    end_time: datetime = Field(..., description="End time for metrics query")
    aggregation: str = Field(default="avg", description="Aggregation type")
    service_filter: Optional[str] = Field(None, description="Filter by service name")

    @validator("aggregation")
    def validate_aggregation(cls, v):
        allowed_aggregations = ["avg", "sum", "min", "max", "count", "raw"]
        if v not in allowed_aggregations:
            raise ValueError(f"aggregation must be one of {allowed_aggregations}")
        return v


router = APIRouter()
logger = logging.getLogger(__name__)


async def get_dgm_engine() -> DGMEngine:
    """Dependency to get DGM engine."""
    # In production, this would be injected from the app state
    return DGMEngine()


async def get_archive_manager() -> StorageArchiveManager:
    """Dependency to get archive manager."""
    return StorageArchiveManager()


async def get_performance_monitor() -> PerformanceMonitor:
    """Dependency to get performance monitor."""
    return PerformanceMonitor()


async def get_bandit_manager() -> BanditAlgorithmManager:
    """Dependency to get bandit algorithm manager."""
    return BanditAlgorithmManager()


# Enhanced Status Endpoint
@router.get("/status", response_model=DGMStatusResponse)
async def get_dgm_status(
    dgm_engine: DGMEngine = Depends(get_dgm_engine),
    performance_monitor: PerformanceMonitor = Depends(get_performance_monitor),
    archive_manager: StorageArchiveManager = Depends(get_archive_manager),
):
    """
    Get comprehensive DGM system status.

    Returns detailed information about the DGM system including:
    - Current operational status
    - Performance metrics
    - Constitutional compliance status
    - Active improvements
    - System health indicators
    """
    try:
        # Get system status from DGM engine
        engine_status = await dgm_engine.get_status()

        # Get performance metrics
        perf_metrics = await performance_monitor.get_current_metrics()

        # Get archive statistics
        archive_stats = await archive_manager.get_statistics()

        # Calculate success rate
        total_improvements = archive_stats.get("total_improvements", 0)
        successful_improvements = archive_stats.get("successful_improvements", 0)
        success_rate = (
            (successful_improvements / total_improvements * 100)
            if total_improvements > 0
            else 0.0
        )

        return DGMStatusResponse(
            status=engine_status.get("status", "operational"),
            version="1.0.0",
            uptime_seconds=engine_status.get("uptime_seconds", 0),
            active_improvements=engine_status.get("active_improvements", 0),
            total_improvements=total_improvements,
            success_rate=success_rate,
            constitutional_compliance_score=engine_status.get(
                "constitutional_compliance_score", 1.0
            ),
            performance_metrics=perf_metrics,
            system_health=engine_status.get("system_health", {}),
            last_optimization=engine_status.get("last_optimization"),
        )

    except Exception as e:
        logger.error(f"Error getting DGM status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get DGM status: {str(e)}",
        )


# Bandit Algorithm Endpoints
@router.post("/bandit/select-arm", response_model=BanditActionResponse)
async def select_bandit_arm(
    request: BanditActionRequest,
    bandit_manager: BanditAlgorithmManager = Depends(get_bandit_manager),
):
    """
    Select an arm using bandit algorithm.

    Uses multi-armed bandit algorithms to select the best action
    for a given context while balancing exploration and exploitation.
    """
    try:
        result = await bandit_manager.select_arm(
            context_key=request.context_key,
            algorithm_type=request.algorithm_type,
            exploration_rate=request.exploration_rate,
            safety_threshold=request.safety_threshold,
        )

        return BanditActionResponse(
            selected_arm=result["selected_arm"],
            confidence=result["confidence"],
            expected_reward=result["expected_reward"],
            exploration_factor=result["exploration_factor"],
            safety_validated=result["safety_validated"],
            constitutional_compliance=result["constitutional_compliance"],
        )

    except Exception as e:
        logger.error(f"Error selecting bandit arm: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to select bandit arm: {str(e)}",
        )


@router.post("/bandit/reward-feedback")
async def provide_reward_feedback(
    request: RewardFeedbackRequest,
    bandit_manager: BanditAlgorithmManager = Depends(get_bandit_manager),
):
    """
    Provide reward feedback for bandit algorithm learning.

    Updates the bandit algorithm's understanding of arm performance
    based on observed rewards.
    """
    try:
        result = await bandit_manager.update_reward(
            context_key=request.context_key,
            arm_id=request.arm_id,
            reward=request.reward,
            metadata=request.metadata,
        )

        return JSONResponse(
            content={
                "success": result["success"],
                "message": "Reward feedback processed successfully",
                "updated_stats": result.get("updated_stats", {}),
            }
        )

    except Exception as e:
        logger.error(f"Error processing reward feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process reward feedback: {str(e)}",
        )


# Performance Metrics Endpoints
@router.post("/metrics/query")
async def query_performance_metrics(
    request: PerformanceMetricsRequest,
    performance_monitor: PerformanceMonitor = Depends(get_performance_monitor),
):
    """
    Query performance metrics for a specific time range.

    Retrieves performance metrics with flexible filtering and aggregation
    options for analysis and monitoring.
    """
    try:
        metrics = await performance_monitor.query_metrics(
            metric_name=request.metric_name,
            start_time=request.start_time,
            end_time=request.end_time,
            aggregation=request.aggregation,
            service_filter=request.service_filter,
        )

        return JSONResponse(
            content={
                "metric_name": request.metric_name,
                "time_range": {
                    "start": request.start_time.isoformat(),
                    "end": request.end_time.isoformat(),
                },
                "aggregation": request.aggregation,
                "data_points": metrics.get("data_points", []),
                "summary": metrics.get("summary", {}),
                "constitutional_compliance": True,
            }
        )

    except Exception as e:
        logger.error(f"Error querying performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query performance metrics: {str(e)}",
        )


@router.get("/metrics/summary")
async def get_metrics_summary(
    hours: int = Query(24, ge=1, le=168, description="Hours to include in summary"),
    service_name: Optional[str] = Query(None, description="Filter by service name"),
    performance_monitor: PerformanceMonitor = Depends(get_performance_monitor),
):
    """
    Get performance metrics summary for the specified time period.

    Provides aggregated performance metrics and trends for monitoring
    and alerting purposes.
    """
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        summary = await performance_monitor.get_metrics_summary(
            start_time=start_time, end_time=end_time, service_name=service_name
        )

        return JSONResponse(
            content={
                "time_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "hours": hours,
                },
                "service_filter": service_name,
                "metrics": summary.get("metrics", {}),
                "trends": summary.get("trends", {}),
                "alerts": summary.get("alerts", []),
                "constitutional_compliance_score": summary.get(
                    "constitutional_compliance_score", 1.0
                ),
            }
        )

    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics summary: {str(e)}",
        )


# Database Optimization Endpoints
@router.post("/optimize/database")
async def optimize_database():
    """
    Trigger database performance optimization.

    Runs comprehensive database optimization including indexing,
    partitioning, and query optimization.
    """
    try:
        optimizer = get_performance_optimizer()
        if not optimizer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database optimizer not available",
            )

        result = await optimizer.optimize_database()

        return JSONResponse(
            content={
                "optimization_id": str(uuid4()),
                "status": result.get("status", "completed"),
                "optimizations_applied": result.get("optimizations_applied", []),
                "performance_improvement": result.get("performance_improvement", {}),
                "recommendations": result.get("recommendations", []),
                "duration_seconds": result.get("duration_seconds", 0),
                "constitutional_compliance": True,
            }
        )

    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize database: {str(e)}",
        )


@router.get("/optimize/database/report")
async def get_database_optimization_report():
    """
    Get database performance optimization report.

    Provides detailed analysis of database performance including
    slow queries, index usage, and optimization recommendations.
    """
    try:
        optimizer = get_performance_optimizer()
        if not optimizer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database optimizer not available",
            )

        report = await optimizer.get_performance_report()

        return JSONResponse(content=report)

    except Exception as e:
        logger.error(f"Error getting database optimization report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database optimization report: {str(e)}",
        )


# Cache Management Endpoints
@router.get("/cache/stats")
async def get_cache_statistics():
    """
    Get cache performance statistics.

    Provides detailed cache performance metrics including hit rates,
    memory usage, and operational statistics.
    """
    try:
        cache_manager = get_cache_manager()
        if not cache_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cache manager not available",
            )

        stats = await cache_manager.get_stats()

        return JSONResponse(content=stats)

    except Exception as e:
        logger.error(f"Error getting cache statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache statistics: {str(e)}",
        )


@router.post("/cache/clear")
async def clear_cache(
    pattern: Optional[str] = Query(None, description="Pattern to match cache keys")
):
    """
    Clear cache entries.

    Clears cache entries matching the specified pattern or all entries
    if no pattern is provided.
    """
    try:
        cache_manager = get_cache_manager()
        if not cache_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cache manager not available",
            )

        cleared_count = await cache_manager.clear(pattern=pattern)

        return JSONResponse(
            content={
                "success": True,
                "message": f"Cleared {cleared_count} cache entries",
                "pattern": pattern,
                "cleared_count": cleared_count,
            }
        )

    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}",
        )


@router.post("/improve", response_model=ImprovementResponse)
async def trigger_improvement(
    request: ImprovementRequest, dgm_engine: DGMEngine = Depends(get_dgm_engine)
):
    """
    Trigger a new improvement cycle.

    This endpoint initiates a Darwin Gödel Machine improvement cycle
    with constitutional compliance validation.
    """
    try:
        improvement_id = uuid4()

        # Start improvement process
        result = await dgm_engine.start_improvement(
            improvement_id=improvement_id,
            description=request.description,
            target_services=request.target_services,
            priority=request.priority,
            metadata=request.metadata,
        )

        return ImprovementResponse(
            improvement_id=improvement_id,
            status=result.get("status", "pending"),
            description=request.description,
            created_at=datetime.utcnow(),
            estimated_completion=result.get("estimated_completion"),
        )

    except Exception as e:
        logger.error(f"Failed to trigger improvement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger improvement: {str(e)}",
        )


@router.get("/improvements/{improvement_id}", response_model=ImprovementResponse)
async def get_improvement_status(
    improvement_id: UUID, dgm_engine: DGMEngine = Depends(get_dgm_engine)
):
    """Get the status of a specific improvement."""
    try:
        improvement = await dgm_engine.get_improvement_status(improvement_id)

        if not improvement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Improvement {improvement_id} not found",
            )

        return ImprovementResponse(
            improvement_id=improvement_id,
            status=improvement.get("status", "unknown"),
            description=improvement.get("description", ""),
            created_at=improvement.get("created_at", datetime.utcnow()),
            estimated_completion=improvement.get("estimated_completion"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get improvement status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get improvement status: {str(e)}",
        )


@router.get("/archive", response_model=ArchiveListResponse)
async def list_archive_entries(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Page size"),
    status: Optional[str] = Query(None, description="Filter by status"),
    min_compliance_score: Optional[float] = Query(
        None, ge=0, le=1, description="Minimum compliance score"
    ),
    archive_manager: StorageArchiveManager = Depends(get_archive_manager),
):
    """
    List improvement archive entries with pagination and filtering.
    """
    try:
        offset = (page - 1) * page_size

        # Convert status string to enum if provided
        status_filter = None
        if status:
            from ...models.archive import ImprovementStatus

            try:
                status_filter = ImprovementStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status}",
                )

        # Get archive entries
        entries = await archive_manager.list_improvements(
            limit=page_size + 1,  # Get one extra to check if there are more
            offset=offset,
            status=status_filter,
            min_compliance_score=min_compliance_score,
        )

        # Check if there are more entries
        has_next = len(entries) > page_size
        if has_next:
            entries = entries[:-1]  # Remove the extra entry

        # Convert to response models
        from .models import ArchiveEntry

        archive_entries = []
        for entry in entries:
            archive_entries.append(
                ArchiveEntry(
                    id=entry.id,
                    improvement_id=entry.improvement_id,
                    timestamp=entry.timestamp,
                    description=entry.description,
                    status=entry.status.value,
                    constitutional_compliance_score=float(
                        entry.constitutional_compliance_score
                    ),
                    performance_before=entry.performance_before or {},
                    performance_after=entry.performance_after or {},
                    metadata=entry.metadata or {},
                )
            )

        # Get total count (this could be optimized with a separate count query)
        total = len(archive_entries) + offset
        if has_next:
            total += 1  # At least one more page

        return ArchiveListResponse(
            entries=archive_entries,
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list archive entries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list archive entries: {str(e)}",
        )


@router.get("/performance", response_model=PerformanceReport)
async def get_performance_report(
    days: int = Query(7, ge=1, le=365, description="Number of days to include"),
    service_name: Optional[str] = Query(None, description="Filter by service name"),
    performance_monitor: PerformanceMonitor = Depends(get_performance_monitor),
):
    """
    Get performance report for the specified time period.
    """
    try:
        report = await performance_monitor.generate_report(
            days=days, service_name=service_name
        )

        return PerformanceReport(
            period_start=report["period_start"],
            period_end=report["period_end"],
            metrics=report["metrics"],
            summary=report["summary"],
            trends=report["trends"],
        )

    except Exception as e:
        logger.error(f"Failed to generate performance report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate performance report: {str(e)}",
        )


@router.post("/rollback", response_model=RollbackResponse)
async def rollback_improvement(
    request: RollbackRequest, dgm_engine: DGMEngine = Depends(get_dgm_engine)
):
    """
    Rollback a specific improvement.

    This endpoint safely reverts a previous improvement to its
    pre-improvement state.
    """
    try:
        rollback_id = uuid4()

        result = await dgm_engine.rollback_improvement(
            improvement_id=request.improvement_id,
            rollback_id=rollback_id,
            reason=request.reason,
            force=request.force,
        )

        return RollbackResponse(
            success=result.get("success", False),
            rollback_id=rollback_id,
            message=result.get("message", "Rollback completed"),
            restored_state=result.get("restored_state", {}),
        )

    except Exception as e:
        logger.error(f"Failed to rollback improvement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rollback improvement: {str(e)}",
        )


@router.get("/bandit/report", response_model=BanditReport)
async def get_bandit_report(dgm_engine: DGMEngine = Depends(get_dgm_engine)):
    """
    Get bandit algorithm performance report.

    Shows the performance of different improvement strategies
    and exploration vs exploitation statistics.
    """
    try:
        report = await dgm_engine.get_bandit_report()

        return BanditReport(
            algorithm_type=report["algorithm_type"],
            total_pulls=report["total_pulls"],
            best_arm=report["best_arm"],
            exploration_rate=report["exploration_rate"],
            arms=report["arms"],
            performance_history=report["performance_history"],
        )

    except Exception as e:
        logger.error(f"Failed to get bandit report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get bandit report: {str(e)}",
        )


@router.delete("/improvements/{improvement_id}")
async def cancel_improvement(
    improvement_id: UUID, dgm_engine: DGMEngine = Depends(get_dgm_engine)
):
    """
    Cancel a running improvement.

    This endpoint safely cancels an in-progress improvement.
    """
    try:
        result = await dgm_engine.cancel_improvement(improvement_id)

        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to cancel improvement"),
            )

        return JSONResponse(
            content={
                "message": "Improvement cancelled successfully",
                "improvement_id": str(improvement_id),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel improvement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel improvement: {str(e)}",
        )
