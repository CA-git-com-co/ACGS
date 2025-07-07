"""
Policy governance models with constitutional compliance.
Constitutional Hash: cdd01ef066bc6cf2
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import Field

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "shared"))

from validation.constitutional_validator import (
    ConstitutionalRequest, 
    ConstitutionalResponse
)


class PolicyType(str, Enum):
    """Policy types for governance."""
    SECURITY = "security"
    COMPLIANCE = "compliance"
    OPERATIONAL = "operational"
    GOVERNANCE = "governance"


class PolicyValidationRequest(ConstitutionalRequest):
    """Request model for policy validation with constitutional compliance."""
    
    policy_id: str = Field(..., description="Unique policy identifier")
    policy_type: PolicyType = Field(..., description="Type of policy")
    policy_content: Dict[str, Any] = Field(..., description="Policy content to validate")
    validation_level: str = Field(default="strict", description="Validation strictness level")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class PolicyValidationResponse(ConstitutionalResponse):
    """Response model for policy validation with constitutional compliance."""
    
    policy_id: str = Field(..., description="Policy identifier")
    validation_result: bool = Field(..., description="Overall validation result")
    validation_details: List[Dict[str, Any]] = Field(default_factory=list, description="Detailed validation results")
    compliance_score: float = Field(..., description="Compliance score (0-100)", ge=0, le=100)
    violations: List[str] = Field(default_factory=list, description="List of violations found")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")


class PolicyCreateRequest(ConstitutionalRequest):
    """Request model for creating policies with constitutional compliance."""
    
    policy_name: str = Field(..., description="Policy name", min_length=1, max_length=255)
    policy_type: PolicyType = Field(..., description="Type of policy")
    policy_content: Dict[str, Any] = Field(..., description="Policy content")
    description: Optional[str] = Field(None, description="Policy description", max_length=1000)
    tags: List[str] = Field(default_factory=list, description="Policy tags")
    enabled: bool = Field(default=True, description="Whether policy is enabled")


class PolicyCreateResponse(ConstitutionalResponse):
    """Response model for policy creation with constitutional compliance."""
    
    policy_id: str = Field(..., description="Created policy identifier")
    policy_name: str = Field(..., description="Policy name")
    status: str = Field(..., description="Creation status")
    validation_passed: bool = Field(..., description="Whether initial validation passed")


class PolicyUpdateRequest(ConstitutionalRequest):
    """Request model for updating policies with constitutional compliance."""
    
    policy_id: str = Field(..., description="Policy identifier to update")
    policy_content: Optional[Dict[str, Any]] = Field(None, description="Updated policy content")
    description: Optional[str] = Field(None, description="Updated description")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    enabled: Optional[bool] = Field(None, description="Updated enabled status")


class PolicyUpdateResponse(ConstitutionalResponse):
    """Response model for policy updates with constitutional compliance."""
    
    policy_id: str = Field(..., description="Updated policy identifier")
    status: str = Field(..., description="Update status")
    validation_passed: bool = Field(..., description="Whether validation passed")
    changes_applied: List[str] = Field(default_factory=list, description="List of changes applied")


class PolicyRetrieveResponse(ConstitutionalResponse):
    """Response model for policy retrieval with constitutional compliance."""
    
    policy_id: str = Field(..., description="Policy identifier")
    policy_name: str = Field(..., description="Policy name")
    policy_type: PolicyType = Field(..., description="Policy type")
    policy_content: Dict[str, Any] = Field(..., description="Policy content")
    description: Optional[str] = Field(None, description="Policy description")
    tags: List[str] = Field(default_factory=list, description="Policy tags")
    enabled: bool = Field(..., description="Whether policy is enabled")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    version: int = Field(..., description="Policy version")


class PolicyListResponse(ConstitutionalResponse):
    """Response model for policy listing with constitutional compliance."""
    
    policies: List[PolicyRetrieveResponse] = Field(default_factory=list, description="List of policies")
    total_count: int = Field(..., description="Total number of policies", ge=0)
    page: int = Field(..., description="Current page number", ge=1)
    page_size: int = Field(..., description="Page size", ge=1, le=100)
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")
