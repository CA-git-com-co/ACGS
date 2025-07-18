"""
Human-in-the-Loop Models
Constitutional Hash: cdd01ef066bc6cf2

Data models for human oversight, intervention, and collaboration
in AI governance systems.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
import uuid

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class InterventionType(str, Enum):
    """Types of human intervention"""

    APPROVAL_REQUIRED = "approval_required"
    CONSTITUTIONAL_REVIEW = "constitutional_review"
    EMERGENCY_OVERRIDE = "emergency_override"
    POLICY_GUIDANCE = "policy_guidance"
    EXPERT_CONSULTATION = "expert_consultation"
    ETHICAL_REVIEW = "ethical_review"
    SAFETY_CHECK = "safety_check"
    QUALITY_ASSURANCE = "quality_assurance"


class InterventionStatus(str, Enum):
    """Status of intervention requests"""

    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    TIMEOUT = "timeout"
    CONSTITUTIONAL_OVERRIDE = "constitutional_override"


class UserRole(str, Enum):
    """Human user roles in the system"""

    ADMINISTRATOR = "administrator"
    CONSTITUTIONAL_EXPERT = "constitutional_expert"
    DOMAIN_EXPERT = "domain_expert"
    OPERATOR = "operator"
    AUDITOR = "auditor"
    EMERGENCY_RESPONDER = "emergency_responder"
    OBSERVER = "observer"


class InterventionRequest(BaseModel):
    """Request for human intervention"""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requesting_service: str
    intervention_type: InterventionType
    priority: int = Field(ge=1, le=10, default=5)
    title: str
    description: str
    context: Dict[str, Any]
    proposed_action: Optional[Dict[str, Any]] = None
    constitutional_impact: bool = False
    emergency: bool = False
    timeout_minutes: int = Field(ge=5, default=60)
    required_roles: List[UserRole] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH


class InterventionResponse(BaseModel):
    """Human response to intervention request"""

    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    responder_id: str
    responder_role: UserRole
    status: InterventionStatus
    decision: Optional[bool] = None
    reasoning: str
    suggested_modifications: Optional[Dict[str, Any]] = None
    constitutional_basis: Optional[str] = None
    response_time: datetime = Field(default_factory=datetime.utcnow)
    confidence_level: float = Field(ge=0.0, le=1.0, default=1.0)


class User(BaseModel):
    """Human user in the system"""

    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    full_name: str
    role: UserRole
    specializations: List[str] = []
    active: bool = True
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    intervention_count: int = 0
    approval_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    constitutional_expertise: float = Field(ge=0.0, le=1.0, default=0.5)


class WorkflowStep(BaseModel):
    """Step in human oversight workflow"""

    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    step_name: str
    required_role: UserRole
    parallel: bool = False
    optional: bool = False
    timeout_minutes: int = 30
    escalation_rules: Dict[str, Any] = {}


class OversightWorkflow(BaseModel):
    """Workflow for human oversight"""

    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    trigger_conditions: List[str]
    steps: List[WorkflowStep]
    constitutional_requirements: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = True
