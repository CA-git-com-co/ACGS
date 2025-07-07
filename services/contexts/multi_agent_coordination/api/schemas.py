"""
Multi-Agent Coordination API Schemas
Constitutional Hash: cdd01ef066bc6cf2

Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class AgentCapabilitySchema(BaseModel):
    """Schema for agent capability."""

    capability_type: str = Field(..., description="Type of capability")
    proficiency_level: float = Field(
        ..., ge=0.0, le=1.0, description="Proficiency level (0.0-1.0)"
    )
    domain_knowledge: List[str] = Field(
        ..., description="List of domain knowledge areas"
    )
    resource_requirements: Dict[str, Any] = Field(
        default_factory=dict, description="Resource requirements"
    )
    performance_indicators: Dict[str, float] = Field(
        default_factory=dict, description="Performance indicators"
    )


class TaskRequirementsSchema(BaseModel):
    """Schema for task requirements."""

    required_capabilities: List[str] = Field(..., description="Required capabilities")
    minimum_proficiency: float = Field(
        ..., ge=0.0, le=1.0, description="Minimum proficiency level"
    )
    estimated_duration_minutes: int = Field(
        ..., gt=0, description="Estimated duration in minutes"
    )
    resource_limits: Dict[str, Any] = Field(
        default_factory=dict, description="Resource limits"
    )
    priority_level: int = Field(..., ge=1, le=5, description="Priority level (1-5)")
    complexity_score: float = Field(
        ..., ge=0.0, le=1.0, description="Complexity score (0.0-1.0)"
    )


class CoordinationObjectiveSchema(BaseModel):
    """Schema for coordination objective."""

    objective_type: str = Field(..., description="Type of objective")
    description: str = Field(..., description="Objective description")
    success_criteria: List[str] = Field(..., description="Success criteria")
    quality_thresholds: Dict[str, float] = Field(
        default_factory=dict, description="Quality thresholds"
    )
    time_constraints: Dict[str, int] = Field(
        default_factory=dict, description="Time constraints in minutes"
    )
    stakeholder_requirements: List[str] = Field(
        default_factory=list, description="Stakeholder requirements"
    )


# Request Schemas


class AgentRegistrationRequest(BaseModel):
    """Request schema for agent registration."""

    agent_type: str = Field(..., description="Type of agent")
    capabilities: List[AgentCapabilitySchema] = Field(
        ..., description="Agent capabilities"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )

    @validator("agent_type")
    def validate_agent_type(cls, v):
        allowed_types = ["ethics", "legal", "operational", "specialist", "coordinator"]
        if v not in allowed_types:
            raise ValueError(f"Agent type must be one of: {allowed_types}")
        return v


class AgentStatusUpdateRequest(BaseModel):
    """Request schema for agent status update."""

    new_status: str = Field(..., description="New agent status")
    reason: str = Field(..., description="Reason for status change")

    @validator("new_status")
    def validate_status(cls, v):
        allowed_statuses = ["available", "busy", "offline", "maintenance"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v


class TaskAssignmentRequest(BaseModel):
    """Request schema for task assignment."""

    required_capabilities: List[str] = Field(..., description="Required capabilities")
    minimum_proficiency: float = Field(
        ..., ge=0.0, le=1.0, description="Minimum proficiency level"
    )
    estimated_duration_minutes: int = Field(
        ..., gt=0, description="Estimated duration in minutes"
    )
    resource_limits: Dict[str, Any] = Field(
        default_factory=dict, description="Resource limits"
    )
    priority_level: int = Field(..., ge=1, le=5, description="Priority level (1-5)")
    complexity_score: float = Field(
        ..., ge=0.0, le=1.0, description="Complexity score (0.0-1.0)"
    )


class TaskCompletionRequest(BaseModel):
    """Request schema for task completion."""

    result: Dict[str, Any] = Field(..., description="Task execution result")
    performance_score: float = Field(
        ..., ge=0.0, le=1.0, description="Performance score (0.0-1.0)"
    )


class CoordinationSessionRequest(BaseModel):
    """Request schema for starting coordination session."""

    objective: CoordinationObjectiveSchema = Field(
        ..., description="Coordination objective"
    )
    initiator_id: str = Field(..., description="ID of session initiator")
    required_agents: List[str] = Field(..., description="Required agent types")
    participating_agents: List[str] = Field(..., description="Participating agent IDs")

    @validator("participating_agents")
    def validate_participating_agents(cls, v):
        if not v:
            raise ValueError("At least one participating agent is required")
        return v


class SessionCompletionRequest(BaseModel):
    """Request schema for session completion."""

    final_results: Dict[str, Any] = Field(..., description="Final session results")


class ImpactAnalysisRequest(BaseModel):
    """Request schema for impact analysis."""

    subject_id: str = Field(..., description="ID of subject being analyzed")
    analysis_type: str = Field(..., description="Type of analysis")
    required_agents: List[str] = Field(..., description="Required agent types")
    context_data: Dict[str, Any] = Field(
        default_factory=dict, description="Analysis context data"
    )
    deadline: Optional[str] = Field(
        default=None, description="Analysis deadline (ISO format)"
    )

    @validator("analysis_type")
    def validate_analysis_type(cls, v):
        allowed_types = [
            "constitutional_impact",
            "policy_compliance",
            "risk_assessment",
            "ethical_review",
        ]
        if v not in allowed_types:
            raise ValueError(f"Analysis type must be one of: {allowed_types}")
        return v


# Response Schemas


class AgentResponse(BaseModel):
    """Response schema for agent operations."""

    agent_id: str = Field(..., description="Agent ID")
    agent_type: str = Field(..., description="Agent type")
    status: str = Field(..., description="Current status")
    capabilities: List[Dict[str, Any]] = Field(..., description="Agent capabilities")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class SessionResponse(BaseModel):
    """Response schema for coordination session."""

    session_id: str = Field(..., description="Session ID")
    objective: Dict[str, Any] = Field(..., description="Session objective")
    status: str = Field(..., description="Session status")
    participating_agents: List[str] = Field(..., description="Participating agent IDs")
    started_at: Optional[datetime] = Field(
        default=None, description="Session start time"
    )


class AnalysisResponse(BaseModel):
    """Response schema for impact analysis."""

    analysis_id: str = Field(..., description="Analysis ID")
    subject_id: str = Field(..., description="Subject ID")
    analysis_type: str = Field(..., description="Analysis type")
    result: Dict[str, Any] = Field(..., description="Analysis result")
    status: str = Field(..., description="Analysis status")


class TaskResponse(BaseModel):
    """Response schema for task operations."""

    task_id: str = Field(..., description="Task ID")
    agent_id: str = Field(..., description="Assigned agent ID")
    status: str = Field(..., description="Task status")
    requirements: TaskRequirementsSchema = Field(..., description="Task requirements")
    assigned_at: datetime = Field(..., description="Assignment timestamp")
    started_at: Optional[datetime] = Field(default=None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(
        default=None, description="Completion timestamp"
    )


class CoordinationMetricsResponse(BaseModel):
    """Response schema for coordination metrics."""

    session_id: str = Field(..., description="Session ID")
    efficiency_score: float = Field(..., description="Efficiency score")
    communication_overhead: float = Field(..., description="Communication overhead")
    resource_utilization: float = Field(..., description="Resource utilization")
    quality_score: float = Field(..., description="Quality score")
    collaboration_index: float = Field(..., description="Collaboration index")
    time_to_completion: int = Field(..., description="Time to completion in minutes")
    overall_score: float = Field(..., description="Overall coordination score")


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")
    constitutional_hash: str = Field(
        default="cdd01ef066bc6cf2", description="Constitutional hash"
    )


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    constitutional_hash: str = Field(..., description="Constitutional hash")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )
