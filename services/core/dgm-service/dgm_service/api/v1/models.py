"""
Pydantic models for DGM Service API.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Service version")
    uptime: float = Field(..., description="Service uptime in seconds")
    dependencies: Dict[str, bool] = Field(..., description="Dependency health status")


class ImprovementRequest(BaseModel):
    """Request model for triggering improvements."""
    description: str = Field(..., description="Description of the improvement")
    target_services: List[str] = Field(default=[], description="Target services for improvement")
    priority: str = Field(default="normal", description="Improvement priority")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    
    @validator("priority")
    def validate_priority(cls, v):
        if v not in ["low", "normal", "high", "critical"]:
            raise ValueError("Priority must be one of: low, normal, high, critical")
        return v


class ImprovementResponse(BaseModel):
    """Response model for improvement operations."""
    improvement_id: UUID = Field(..., description="Unique improvement identifier")
    status: str = Field(..., description="Improvement status")
    description: str = Field(..., description="Improvement description")
    created_at: datetime = Field(..., description="Creation timestamp")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")


class ArchiveEntry(BaseModel):
    """Archive entry model."""
    id: UUID = Field(..., description="Archive entry ID")
    improvement_id: UUID = Field(..., description="Improvement ID")
    timestamp: datetime = Field(..., description="Archive timestamp")
    description: str = Field(..., description="Improvement description")
    status: str = Field(..., description="Improvement status")
    constitutional_compliance_score: float = Field(..., description="Compliance score")
    performance_before: Dict[str, Any] = Field(..., description="Performance before improvement")
    performance_after: Dict[str, Any] = Field(..., description="Performance after improvement")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class ArchiveListResponse(BaseModel):
    """Response model for archive listing."""
    entries: List[ArchiveEntry] = Field(..., description="Archive entries")
    total: int = Field(..., description="Total number of entries")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    has_next: bool = Field(..., description="Whether there are more pages")


class PerformanceMetric(BaseModel):
    """Performance metric model."""
    timestamp: datetime = Field(..., description="Metric timestamp")
    service_name: str = Field(..., description="Service name")
    metric_name: str = Field(..., description="Metric name")
    metric_value: float = Field(..., description="Metric value")
    metric_unit: Optional[str] = Field(None, description="Metric unit")
    tags: Dict[str, str] = Field(default={}, description="Metric tags")


class PerformanceReport(BaseModel):
    """Performance report model."""
    period_start: datetime = Field(..., description="Report period start")
    period_end: datetime = Field(..., description="Report period end")
    metrics: List[PerformanceMetric] = Field(..., description="Performance metrics")
    summary: Dict[str, Any] = Field(..., description="Performance summary")
    trends: Dict[str, Any] = Field(..., description="Performance trends")


class ConstitutionalValidationRequest(BaseModel):
    """Request model for constitutional validation."""
    improvement_data: Dict[str, Any] = Field(..., description="Improvement data to validate")
    principles: List[str] = Field(default=[], description="Specific principles to check")
    strict_mode: bool = Field(default=False, description="Enable strict validation mode")


class ConstitutionalValidationResponse(BaseModel):
    """Response model for constitutional validation."""
    is_compliant: bool = Field(..., description="Whether the improvement is compliant")
    compliance_score: float = Field(..., description="Compliance score (0-1)")
    violations: List[str] = Field(default=[], description="List of violations")
    warnings: List[str] = Field(default=[], description="List of warnings")
    recommendations: List[str] = Field(default=[], description="Improvement recommendations")
    details: Dict[str, Any] = Field(default={}, description="Detailed validation results")


class RollbackRequest(BaseModel):
    """Request model for rollback operations."""
    improvement_id: UUID = Field(..., description="Improvement ID to rollback")
    reason: str = Field(..., description="Reason for rollback")
    force: bool = Field(default=False, description="Force rollback even if risky")


class RollbackResponse(BaseModel):
    """Response model for rollback operations."""
    success: bool = Field(..., description="Whether rollback was successful")
    rollback_id: UUID = Field(..., description="Rollback operation ID")
    message: str = Field(..., description="Rollback result message")
    restored_state: Dict[str, Any] = Field(default={}, description="Restored system state")


class BanditArmStats(BaseModel):
    """Bandit algorithm arm statistics."""
    arm_id: str = Field(..., description="Arm identifier")
    description: str = Field(..., description="Arm description")
    total_pulls: int = Field(..., description="Total number of pulls")
    total_reward: float = Field(..., description="Total reward accumulated")
    average_reward: float = Field(..., description="Average reward per pull")
    confidence_bound: Optional[float] = Field(None, description="Upper confidence bound")
    last_pulled: Optional[datetime] = Field(None, description="Last pull timestamp")


class BanditReport(BaseModel):
    """Bandit algorithm performance report."""
    algorithm_type: str = Field(..., description="Bandit algorithm type")
    total_pulls: int = Field(..., description="Total pulls across all arms")
    best_arm: str = Field(..., description="Currently best performing arm")
    exploration_rate: float = Field(..., description="Current exploration rate")
    arms: List[BanditArmStats] = Field(..., description="Individual arm statistics")
    performance_history: List[Dict[str, Any]] = Field(..., description="Performance history")


class SystemStatus(BaseModel):
    """System status model."""
    service_name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    status: str = Field(..., description="Overall system status")
    uptime: float = Field(..., description="System uptime in seconds")
    active_improvements: int = Field(..., description="Number of active improvements")
    total_improvements: int = Field(..., description="Total improvements processed")
    average_compliance_score: float = Field(..., description="Average compliance score")
    last_improvement: Optional[datetime] = Field(None, description="Last improvement timestamp")
    system_health: Dict[str, Any] = Field(..., description="Detailed system health")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    timestamp: datetime = Field(..., description="Error timestamp")
