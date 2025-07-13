"""
Constitutional Verification Data Models

Data models for constitutional compliance verification, policy validation,
and constitutional proof generation with ACGS integration.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ConstitutionalPrincipleType(str, Enum):
    """Types of constitutional principles."""

    TRANSPARENCY = "transparency"
    FAIRNESS = "fairness"
    SAFETY = "safety"
    PRIVACY = "privacy"
    ACCOUNTABILITY = "accountability"
    HUMAN_AGENCY = "human_agency"
    ROBUSTNESS = "robustness"
    NON_MALEFICENCE = "non_maleficence"


class PolicyValidationType(str, Enum):
    """Types of policy validation."""

    SYNTAX_CHECK = "syntax_check"
    SEMANTIC_VALIDATION = "semantic_validation"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    SAFETY_VERIFICATION = "safety_verification"
    CONSISTENCY_CHECK = "consistency_check"


class ConstitutionalVerificationRequest(BaseModel):
    """Request for constitutional compliance verification."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    verification_type: str = Field(default="constitutional_compliance")

    # Target for verification
    target_policy: dict[str, Any] = Field(..., description="Policy to verify")
    target_system: str | None = Field(None, description="Target system identifier")

    # Constitutional requirements
    required_principles: list[ConstitutionalPrincipleType] = Field(
        default_factory=list, description="Required constitutional principles"
    )
    compliance_threshold: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Minimum compliance threshold"
    )

    # Verification parameters
    strict_mode: bool = Field(
        default=True, description="Strict constitutional compliance"
    )
    include_safety_verification: bool = Field(default=True)
    include_fairness_analysis: bool = Field(default=True)
    include_transparency_check: bool = Field(default=True)

    # Context
    verification_context: dict[str, Any] = Field(
        default_factory=dict, description="Verification context"
    )
    requester_id: str = Field(..., description="Requester ID")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class PolicyValidationRequest(BaseModel):
    """Request for policy validation."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    validation_type: PolicyValidationType = Field(..., description="Type of validation")

    # Policy details
    policy_content: str = Field(..., description="Policy content to validate")
    policy_format: str = Field(default="rego", description="Policy format")
    policy_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Policy metadata"
    )

    # Validation parameters
    validate_syntax: bool = Field(default=True)
    validate_semantics: bool = Field(default=True)
    validate_constitutional_compliance: bool = Field(default=True)
    validate_safety: bool = Field(default=True)

    # Constitutional requirements
    constitutional_principles: list[ConstitutionalPrincipleType] = Field(
        default_factory=list
    )

    # Context
    validation_context: dict[str, Any] = Field(default_factory=dict)
    requester_id: str = Field(..., description="Requester ID")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ConstitutionalProof(BaseModel):
    """Constitutional compliance proof."""

    proof_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    verification_request_id: str = Field(..., description="Verification request ID")

    # Proof details
    principle: ConstitutionalPrincipleType = Field(
        ..., description="Constitutional principle"
    )
    proof_statement: str = Field(..., description="What is being proven")
    proof_method: str = Field(..., description="Proof method used")

    # Proof content
    formal_proof: str = Field(..., description="Formal proof content")
    proof_steps: list[str] = Field(default_factory=list, description="Proof steps")
    assumptions: list[str] = Field(
        default_factory=list, description="Proof assumptions"
    )

    # Proof validation
    proof_valid: bool = Field(..., description="Whether proof is valid")
    proof_complete: bool = Field(..., description="Whether proof is complete")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)

    # Constitutional compliance
    constitutional_compliance_verified: bool = Field(default=False)
    compliance_score: float = Field(default=0.0, ge=0.0, le=1.0)

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str = Field(..., description="Proof generator")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ConstitutionalVerificationResult(BaseModel):
    """Result of constitutional compliance verification."""

    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = Field(..., description="Verification request ID")

    # Verification result
    verification_successful: bool = Field(
        ..., description="Overall verification success"
    )
    constitutional_compliant: bool = Field(
        ..., description="Constitutional compliance status"
    )
    compliance_score: float = Field(
        ..., ge=0.0, le=1.0, description="Overall compliance score"
    )

    # Principle-specific results
    principle_scores: dict[str, float] = Field(
        default_factory=dict, description="Scores per constitutional principle"
    )
    principle_proofs: list[ConstitutionalProof] = Field(
        default_factory=list, description="Constitutional proofs"
    )

    # Compliance analysis
    compliant_principles: list[ConstitutionalPrincipleType] = Field(
        default_factory=list
    )
    non_compliant_principles: list[ConstitutionalPrincipleType] = Field(
        default_factory=list
    )
    violations: list[str] = Field(
        default_factory=list, description="Constitutional violations"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Improvement recommendations"
    )

    # Verification metrics
    verification_time_ms: float = Field(..., description="Verification time")
    proof_coverage: float = Field(default=0.0, ge=0.0, le=1.0)

    # Quality assessment
    verification_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)

    # Error handling
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    # Metadata
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    verified_by: str = Field(..., description="Verification service")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class PolicyValidationResult(BaseModel):
    """Result of policy validation."""

    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = Field(..., description="Validation request ID")

    # Validation result
    validation_successful: bool = Field(..., description="Overall validation success")
    policy_valid: bool = Field(..., description="Policy validity status")

    # Validation details
    syntax_valid: bool = Field(default=True, description="Syntax validation result")
    semantics_valid: bool = Field(
        default=True, description="Semantics validation result"
    )
    constitutional_compliant: bool = Field(
        default=False, description="Constitutional compliance"
    )
    safety_verified: bool = Field(
        default=False, description="Safety verification result"
    )

    # Detailed results
    syntax_errors: list[str] = Field(default_factory=list)
    semantic_errors: list[str] = Field(default_factory=list)
    constitutional_violations: list[str] = Field(default_factory=list)
    safety_issues: list[str] = Field(default_factory=list)

    # Compliance scores
    constitutional_compliance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    safety_score: float = Field(default=0.0, ge=0.0, le=1.0)
    overall_quality_score: float = Field(default=0.0, ge=0.0, le=1.0)

    # Recommendations
    improvement_suggestions: list[str] = Field(default_factory=list)
    required_fixes: list[str] = Field(default_factory=list)

    # Metadata
    validation_time_ms: float = Field(..., description="Validation time")
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    validated_by: str = Field(..., description="Validation service")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
