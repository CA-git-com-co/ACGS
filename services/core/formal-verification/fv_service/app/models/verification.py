"""
Verification Data Models

Core data models for formal verification processes, proof obligations,
and verification results with constitutional compliance.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class VerificationStatus(str, Enum):
    """Status of verification processes."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ProofStatus(str, Enum):
    """Status of proof generation and validation."""

    UNPROVEN = "unproven"
    PROVEN = "proven"
    DISPROVEN = "disproven"
    UNKNOWN = "unknown"
    ERROR = "error"


class VerificationRequest(BaseModel):
    """Request for formal verification process."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    verification_type: str = Field(..., description="Type of verification")

    # Verification target
    target_system: str = Field(..., description="System or component to verify")
    properties: List[str] = Field(..., description="Properties to verify")
    constraints: List[str] = Field(
        default_factory=list, description="Verification constraints"
    )

    # Verification parameters
    timeout_seconds: int = Field(
        default=300, ge=1, le=3600, description="Verification timeout"
    )
    proof_depth: int = Field(
        default=10, ge=1, le=100, description="Maximum proof depth"
    )
    use_smt_solver: bool = Field(default=True, description="Use SMT solver")

    # Constitutional compliance
    constitutional_compliance_required: bool = Field(default=True)
    safety_critical: bool = Field(default=False)

    # Context and metadata
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Verification context"
    )
    requester_id: str = Field(..., description="ID of requesting user/service")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ProofObligation(BaseModel):
    """Proof obligation for formal verification."""

    obligation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    verification_request_id: str = Field(
        ..., description="Parent verification request ID"
    )

    # Obligation details
    property_name: str = Field(..., description="Property to prove")
    formula: str = Field(..., description="Logical formula to prove")
    preconditions: List[str] = Field(default_factory=list, description="Preconditions")
    postconditions: List[str] = Field(
        default_factory=list, description="Postconditions"
    )

    # Proof context
    proof_method: str = Field(default="smt", description="Proof method to use")
    complexity_estimate: int = Field(
        default=1, ge=1, le=10, description="Complexity estimate"
    )

    # Status
    status: ProofStatus = Field(default=ProofStatus.UNPROVEN)
    priority: int = Field(default=5, ge=1, le=10, description="Proof priority")

    # Constitutional compliance
    constitutional_relevance: bool = Field(default=False)
    safety_critical: bool = Field(default=False)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ProofResult(BaseModel):
    """Result of proof generation and validation."""

    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    obligation_id: str = Field(..., description="Proof obligation ID")
    verification_request_id: str = Field(..., description="Verification request ID")

    # Proof result
    status: ProofStatus = Field(..., description="Proof status")
    proof_valid: bool = Field(..., description="Whether proof is valid")
    proof_complete: bool = Field(..., description="Whether proof is complete")

    # Proof details
    proof_steps: List[str] = Field(default_factory=list, description="Proof steps")
    proof_trace: str = Field(default="", description="Detailed proof trace")
    counterexample: Optional[Dict[str, Any]] = Field(
        None, description="Counterexample if disproven"
    )

    # Verification metrics
    proof_time_ms: float = Field(
        ..., description="Proof generation time in milliseconds"
    )
    proof_size: int = Field(default=0, description="Proof size in steps")
    solver_calls: int = Field(default=0, description="Number of solver calls")

    # Constitutional compliance
    constitutional_compliance_verified: bool = Field(default=False)
    constitutional_violations: List[str] = Field(default_factory=list)

    # Quality metrics
    confidence_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Proof confidence"
    )
    completeness_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Proof completeness"
    )

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str = Field(..., description="Proof generator")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class VerificationResult(BaseModel):
    """Result of formal verification process."""

    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = Field(..., description="Verification request ID")

    # Verification result
    status: VerificationStatus = Field(..., description="Verification status")
    verification_successful: bool = Field(
        ..., description="Overall verification success"
    )
    properties_verified: List[str] = Field(
        default_factory=list, description="Successfully verified properties"
    )
    properties_failed: List[str] = Field(
        default_factory=list, description="Failed properties"
    )

    # Proof results
    proof_obligations: List[ProofObligation] = Field(default_factory=list)
    proof_results: List[ProofResult] = Field(default_factory=list)

    # Verification metrics
    total_time_ms: float = Field(..., description="Total verification time")
    proof_coverage: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Proof coverage"
    )
    verification_depth: int = Field(
        default=0, description="Verification depth achieved"
    )

    # Constitutional compliance
    constitutional_compliance_verified: bool = Field(default=False)
    constitutional_compliance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    constitutional_violations: List[str] = Field(default_factory=list)

    # Quality assessment
    verification_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    completeness_assessment: str = Field(
        default="", description="Completeness assessment"
    )

    # Error handling
    errors: List[str] = Field(default_factory=list, description="Verification errors")
    warnings: List[str] = Field(
        default_factory=list, description="Verification warnings"
    )

    # Metadata
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    verified_by: str = Field(..., description="Verification service/engine")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
