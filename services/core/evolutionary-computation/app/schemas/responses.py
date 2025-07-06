"""
Common API Response Schemas

Standard response schemas for the evolutionary computation service API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class SuccessResponse(BaseModel):
    """Standard success response schema."""
    
    success: bool = Field(default=True, description="Success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    
    success: bool = Field(default=False, description="Success status")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    
    # Error context
    error_code: Optional[str] = Field(None, description="Error code")
    request_id: Optional[str] = Field(None, description="Request ID")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StatusResponse(BaseModel):
    """Service status response schema."""
    
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    
    # Health indicators
    healthy: bool = Field(..., description="Health status")
    uptime_seconds: float = Field(..., description="Service uptime")
    
    # Performance metrics
    active_evolutions: int = Field(default=0, description="Active evolution processes")
    pending_reviews: int = Field(default=0, description="Pending human reviews")
    total_requests: int = Field(default=0, description="Total requests processed")
    
    # Constitutional compliance
    constitutional_compliance_enabled: bool = Field(default=True, description="Constitutional compliance enabled")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    # Dependencies
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Dependency status")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Status timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthResponse(BaseModel):
    """Health check response schema."""
    
    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    
    # Health checks
    database_healthy: bool = Field(default=True, description="Database health")
    redis_healthy: bool = Field(default=True, description="Redis health")
    external_services_healthy: bool = Field(default=True, description="External services health")
    
    # Performance indicators
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    memory_usage_mb: float = Field(..., description="Memory usage in MB")
    cpu_usage_percent: float = Field(..., description="CPU usage percentage")
    
    # Constitutional compliance
    constitutional_compliance_active: bool = Field(default=True, description="Constitutional compliance active")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    # Service-specific health
    evolution_engine_healthy: bool = Field(default=True, description="Evolution engine health")
    oversight_system_healthy: bool = Field(default=True, description="Oversight system health")
    wina_coordinator_healthy: bool = Field(default=True, description="WINA coordinator health")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
