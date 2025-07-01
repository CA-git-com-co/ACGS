"""
Agent Identity Management Schemas

Pydantic schemas for agent identity management API requests and responses.
Provides validation, serialization, and documentation for agent-related operations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field, validator, EmailStr

from ..models.agent import AgentStatus, AgentType


class AgentBase(BaseModel):
    """Base agent schema with common fields."""
    
    agent_id: str = Field(..., min_length=3, max_length=100, description="Unique human-readable agent identifier")
    name: str = Field(..., min_length=1, max_length=255, description="Agent display name")
    description: Optional[str] = Field(None, max_length=1000, description="Agent description")
    agent_type: AgentType = Field(default=AgentType.CODING_AGENT, description="Agent type classification")
    version: str = Field(default="1.0.0", description="Agent version")


class AgentCreate(AgentBase):
    """Schema for creating a new agent."""
    
    # Ownership
    owner_user_id: int = Field(..., description="ID of the user who owns this agent")
    responsible_team: Optional[str] = Field(None, max_length=100, description="Team responsible for agent")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email for agent issues")
    
    # Capabilities and permissions
    capabilities: List[str] = Field(default_factory=list, description="List of agent capabilities")
    permissions: List[str] = Field(default_factory=list, description="Specific permissions granted to agent")
    role_assignments: List[str] = Field(default_factory=list, description="Roles assigned to agent")
    
    # Access control
    allowed_services: List[str] = Field(default_factory=list, description="Services agent can access")
    allowed_operations: List[str] = Field(default_factory=list, description="Operations agent can perform")
    ip_whitelist: Optional[List[str]] = Field(None, description="Allowed IP addresses")
    
    # Resource limits
    max_requests_per_minute: int = Field(default=100, ge=1, le=10000, description="Rate limit per minute")
    max_concurrent_operations: int = Field(default=5, ge=1, le=100, description="Max concurrent operations")
    resource_quota: Optional[Dict[str, Any]] = Field(None, description="Resource quotas (CPU, memory, etc.)")
    
    # Constitutional compliance
    compliance_level: str = Field(default="standard", description="Compliance level: standard, high, critical")
    requires_human_approval: bool = Field(default=True, description="Whether agent actions require human approval")
    
    # Configuration and metadata
    configuration: Optional[Dict[str, Any]] = Field(None, description="Agent-specific configuration")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    
    @validator('agent_id')
    def validate_agent_id(cls, v):
        """Validate agent ID format."""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Agent ID must contain only alphanumeric characters, hyphens, and underscores')
        return v.lower()
    
    @validator('compliance_level')
    def validate_compliance_level(cls, v):
        """Validate compliance level."""
        if v not in ['standard', 'high', 'critical']:
            raise ValueError('Compliance level must be one of: standard, high, critical')
        return v


class AgentUpdate(BaseModel):
    """Schema for updating an existing agent."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    agent_type: Optional[AgentType] = None
    version: Optional[str] = None
    
    # Ownership
    responsible_team: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[EmailStr] = None
    
    # Capabilities and permissions
    capabilities: Optional[List[str]] = None
    permissions: Optional[List[str]] = None
    role_assignments: Optional[List[str]] = None
    
    # Access control
    allowed_services: Optional[List[str]] = None
    allowed_operations: Optional[List[str]] = None
    ip_whitelist: Optional[List[str]] = None
    
    # Resource limits
    max_requests_per_minute: Optional[int] = Field(None, ge=1, le=10000)
    max_concurrent_operations: Optional[int] = Field(None, ge=1, le=100)
    resource_quota: Optional[Dict[str, Any]] = None
    
    # Constitutional compliance
    compliance_level: Optional[str] = None
    requires_human_approval: Optional[bool] = None
    
    # Configuration and metadata
    configuration: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    @validator('compliance_level')
    def validate_compliance_level(cls, v):
        """Validate compliance level."""
        if v is not None and v not in ['standard', 'high', 'critical']:
            raise ValueError('Compliance level must be one of: standard, high, critical')
        return v


class AgentResponse(AgentBase):
    """Schema for agent response data."""
    
    id: str = Field(..., description="Agent UUID")
    status: AgentStatus = Field(..., description="Current agent status")
    
    # Timestamps
    created_at: datetime
    activated_at: Optional[datetime] = None
    suspended_at: Optional[datetime] = None
    retired_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    
    # Ownership
    owner_user_id: int
    responsible_team: Optional[str] = None
    contact_email: Optional[str] = None
    
    # Capabilities and permissions
    capabilities: List[str]
    permissions: List[str]
    role_assignments: List[str]
    
    # Access control
    allowed_services: List[str]
    allowed_operations: List[str]
    ip_whitelist: Optional[List[str]] = None
    
    # Resource limits
    max_requests_per_minute: int
    max_concurrent_operations: int
    resource_quota: Optional[Dict[str, Any]] = None
    
    # Constitutional compliance
    constitutional_hash: str
    compliance_level: str
    requires_human_approval: bool
    
    # Monitoring and metrics
    total_operations: int
    successful_operations: int
    failed_operations: int
    last_error: Optional[str] = None
    last_error_at: Optional[datetime] = None
    
    # Configuration and metadata
    configuration: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: List[str]
    
    class Config:
        from_attributes = True


class AgentStatusUpdate(BaseModel):
    """Schema for updating agent status."""
    
    status: AgentStatus = Field(..., description="New agent status")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change")
    
    @validator('status')
    def validate_status_transition(cls, v):
        """Validate status transition is allowed."""
        # Add business logic for valid status transitions
        return v


class AgentCredentials(BaseModel):
    """Schema for agent credentials response."""
    
    agent_id: str
    api_key: str = Field(..., description="API key for agent authentication")
    expires_at: Optional[datetime] = Field(None, description="API key expiration")
    
    class Config:
        # Don't include this in logs or responses by default
        json_encoders = {
            str: lambda v: "***" if len(v) > 20 else v  # Mask long strings (likely API keys)
        }


class AgentSessionResponse(BaseModel):
    """Schema for agent session information."""
    
    id: str
    agent_id: str
    started_at: datetime
    last_activity_at: datetime
    expires_at: datetime
    ended_at: Optional[datetime] = None
    client_ip: Optional[str] = None
    is_active: bool
    termination_reason: Optional[str] = None
    
    class Config:
        from_attributes = True


class AgentAuditLogResponse(BaseModel):
    """Schema for agent audit log entries."""
    
    id: str
    agent_id: str
    event_type: str
    event_description: str
    performed_by_user_id: Optional[int] = None
    performed_by_system: Optional[str] = None
    timestamp: datetime
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    constitutional_hash: str
    compliance_verified: bool
    
    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    """Schema for paginated agent list response."""
    
    agents: List[AgentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AgentSearchRequest(BaseModel):
    """Schema for agent search request."""
    
    query: Optional[str] = Field(None, description="Search query")
    status: Optional[List[AgentStatus]] = Field(None, description="Filter by status")
    agent_type: Optional[List[AgentType]] = Field(None, description="Filter by agent type")
    owner_user_id: Optional[int] = Field(None, description="Filter by owner")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    capabilities: Optional[List[str]] = Field(None, description="Filter by capabilities")
    compliance_level: Optional[List[str]] = Field(None, description="Filter by compliance level")
    
    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    # Sorting
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order: asc or desc")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        """Validate sort order."""
        if v not in ['asc', 'desc']:
            raise ValueError('Sort order must be asc or desc')
        return v


class AgentOperationRequest(BaseModel):
    """Schema for agent operation requests."""
    
    operation: str = Field(..., description="Operation to perform")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Operation parameters")
    context: Optional[Dict[str, Any]] = Field(None, description="Operation context")
    requires_approval: Optional[bool] = Field(None, description="Override approval requirement")


class AgentOperationResponse(BaseModel):
    """Schema for agent operation responses."""
    
    operation_id: str
    agent_id: str
    operation: str
    status: str  # pending, approved, rejected, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    approved_by: Optional[int] = None  # User ID who approved
    
    class Config:
        from_attributes = True
