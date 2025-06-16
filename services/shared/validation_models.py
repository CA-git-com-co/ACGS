"""
ACGS-1 Phase A3: Comprehensive Input Validation Models

This module provides production-grade Pydantic models for input validation
across all ACGS-1 services, ensuring consistent validation, error handling,
and API documentation.
"""

import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, validator
from pydantic.types import SecretStr


# Base validation model with common configuration
class BaseValidationModel(BaseModel):
    """Base model with common validation configuration."""

    class Config:
        # Enable validation on assignment
        validate_assignment = True
        # Use enum values instead of names
        use_enum_values = True
        # Allow population by field name or alias
        allow_population_by_field_name = True
        # Generate schema with examples
        schema_extra = {}


# Common enums for validation
class ServiceType(str, Enum):
    """Service types in ACGS-1 system."""

    AUTH = "auth_service"
    AC = "ac_service"
    INTEGRITY = "integrity_service"
    FV = "fv_service"
    GS = "gs_service"
    PGC = "pgc_service"
    EC = "ec_service"


class PolicyType(str, Enum):
    """Policy types for governance."""

    STANDARD = "STANDARD"
    CONSTITUTIONAL = "CONSTITUTIONAL"
    REGULATORY = "REGULATORY"
    EMERGENCY = "EMERGENCY"


class Priority(str, Enum):
    """Priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(str, Enum):
    """General status values."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Authentication and User Models
class UserCreateRequest(BaseValidationModel):
    """User creation request validation."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        regex=r"^[a-zA-Z0-9_-]+$",
        description="Username (alphanumeric, underscore, hyphen only)",
        example="john_doe",
    )
    email: EmailStr = Field(..., description="Valid email address", example="john.doe@example.com")
    password: SecretStr = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (minimum 8 characters)",
        example="SecurePass123!",
    )
    full_name: Optional[str] = Field(
        None, max_length=255, description="Full name", example="John Doe"
    )
    role: str = Field(
        "user",
        regex=r"^(user|admin|auditor|policy_manager|constitutional_council)$",
        description="User role",
        example="user",
    )

    @validator("password")
    def validate_password_strength(cls, v):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Validate password strength."""
        password = v.get_secret_value()

        # Check for at least one uppercase letter
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")

        # Check for at least one lowercase letter
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")

        # Check for at least one digit
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit")

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain at least one special character")

        return v

    @validator("username")
    def validate_username_not_reserved(cls, v):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Ensure username is not reserved."""
        reserved_usernames = {"admin", "root", "system", "api", "service"}
        if v.lower() in reserved_usernames:
            raise ValueError(f'Username "{v}" is reserved')
        return v


class LoginRequest(BaseValidationModel):
    """Login request validation."""

    username: str = Field(
        ..., min_length=3, max_length=50, description="Username", example="john_doe"
    )
    password: SecretStr = Field(..., description="Password", example="SecurePass123!")
    remember_me: bool = Field(
        False, description="Remember login for extended session", example=False
    )


class TokenRefreshRequest(BaseValidationModel):
    """Token refresh request validation."""

    refresh_token: str = Field(
        ...,
        min_length=10,
        description="Valid refresh token",
        example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    )


# Policy and Governance Models
class PolicyCreateRequest(BaseValidationModel):
    """Policy creation request validation."""

    title: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Policy title",
        example="Environmental Protection Policy",
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Policy description",
        example="This policy governs environmental protection standards...",
    )
    policy_type: PolicyType = Field(..., description="Type of policy", example=PolicyType.STANDARD)
    content: str = Field(
        ...,
        min_length=50,
        max_length=10000,
        description="Policy content in Datalog or natural language",
        example="policy_rule(X) :- environmental_standard(X), compliance_check(X).",
    )
    tags: List[str] = Field(
        default_factory=list,
        max_items=10,
        description="Policy tags for categorization",
        example=["environment", "compliance", "standards"],
    )
    effective_date: datetime = Field(
        ...,
        description="When the policy becomes effective",
        example="2024-01-01T00:00:00Z",
    )
    expiry_date: Optional[datetime] = Field(
        None,
        description="When the policy expires (optional)",
        example="2025-01-01T00:00:00Z",
    )
    priority: Priority = Field(
        Priority.MEDIUM, description="Policy priority level", example=Priority.HIGH
    )

    @validator("title")
    def validate_title_format(cls, v):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Validate title format."""
        if not v[0].isupper():
            raise ValueError("Title must start with a capital letter")

        # Check for reasonable title format
        if not re.match(r"^[A-Z][a-zA-Z0-9\s\-_()]+$", v):
            raise ValueError("Title contains invalid characters")

        return v

    @validator("tags")
    def validate_tags_format(cls, v):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Validate tags format."""
        for tag in v:
            if not re.match(r"^[a-z0-9_-]+$", tag):
                raise ValueError(
                    f'Tag "{tag}" must be lowercase alphanumeric with underscores/hyphens only'
                )
            if len(tag) < 2 or len(tag) > 30:
                raise ValueError(f'Tag "{tag}" must be between 2 and 30 characters')

        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Tags must be unique")

        return v

    @validator("expiry_date")
    def validate_expiry_after_effective(cls, v, values):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Ensure expiry date is after effective date."""
        if v and "effective_date" in values:
            if v <= values["effective_date"]:
                raise ValueError("Expiry date must be after effective date")
        return v


class PolicyUpdateRequest(BaseValidationModel):
    """Policy update request validation."""

    title: Optional[str] = Field(
        None, min_length=5, max_length=200, description="Updated policy title"
    )
    description: Optional[str] = Field(
        None, min_length=10, max_length=2000, description="Updated policy description"
    )
    content: Optional[str] = Field(
        None, min_length=50, max_length=10000, description="Updated policy content"
    )
    tags: Optional[List[str]] = Field(None, max_items=10, description="Updated policy tags")
    priority: Optional[Priority] = Field(None, description="Updated policy priority")
    status: Optional[Status] = Field(None, description="Updated policy status")

    @validator("tags")
    def validate_tags_format(cls, v):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Validate tags format if provided."""
        if v is not None:
            for tag in v:
                if not re.match(r"^[a-z0-9_-]+$", tag):
                    raise ValueError(
                        f'Tag "{tag}" must be lowercase alphanumeric with underscores/hyphens only'
                    )

            # Check for duplicates
            if len(v) != len(set(v)):
                raise ValueError("Tags must be unique")

        return v


# Constitutional and Governance Models
class PrincipleCreateRequest(BaseValidationModel):
    """Constitutional principle creation request."""

    name: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Principle name",
        example="Transparency and Accountability",
    )
    content: str = Field(
        ...,
        min_length=20,
        max_length=5000,
        description="Principle content",
        example="All governance decisions must be transparent and accountable to stakeholders...",
    )
    category: str = Field(
        ...,
        regex=r"^(fundamental|procedural|substantive|enforcement)$",
        description="Principle category",
        example="fundamental",
    )
    weight: float = Field(
        1.0,
        ge=0.1,
        le=10.0,
        description="Principle weight for conflict resolution",
        example=1.5,
    )

    @validator("name")
    def validate_name_format(cls, v):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Validate principle name format."""
        if not v[0].isupper():
            raise ValueError("Principle name must start with a capital letter")
        return v


# Cryptographic and Integrity Models
class SignatureRequest(BaseValidationModel):
    """Digital signature request validation."""

    content: str = Field(
        ...,
        min_length=1,
        max_length=1000000,  # 1MB limit
        description="Content to be signed",
        example="Policy content to be digitally signed",
    )
    key_id: Optional[str] = Field(
        None,
        regex=r"^[a-fA-F0-9]{8,64}$",
        description="Key ID for signing (hex format)",
        example="a1b2c3d4e5f6",
    )
    algorithm: str = Field(
        "RSA-SHA256",
        regex=r"^(RSA-SHA256|ECDSA-SHA256|EdDSA)$",
        description="Signature algorithm",
        example="RSA-SHA256",
    )


class VerificationRequest(BaseValidationModel):
    """Signature verification request validation."""

    content: str = Field(
        ...,
        min_length=1,
        max_length=1000000,
        description="Original content",
        example="Policy content that was signed",
    )
    signature: str = Field(
        ...,
        min_length=10,
        description="Digital signature to verify",
        example="MEUCIQDxyz...",
    )
    public_key: Optional[str] = Field(
        None,
        description="Public key for verification",
        example="-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",
    )


# Query and Search Models
class SearchRequest(BaseValidationModel):
    """Search request validation."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Search query",
        example="environmental policy",
    )
    filters: Optional[Dict[str, Any]] = Field(
        None,
        description="Search filters",
        example={"policy_type": "STANDARD", "status": "active"},
    )
    sort_by: Optional[str] = Field(
        "created_at",
        regex=r"^(created_at|updated_at|title|priority)$",
        description="Sort field",
        example="created_at",
    )
    sort_order: str = Field("desc", regex=r"^(asc|desc)$", description="Sort order", example="desc")
    page: int = Field(1, ge=1, le=1000, description="Page number", example=1)
    size: int = Field(20, ge=1, le=100, description="Items per page", example=20)


# Monitoring and Performance Models
class PerformanceMetricsRequest(BaseValidationModel):
    """Performance metrics request validation."""

    service: Optional[ServiceType] = Field(
        None, description="Specific service to get metrics for", example=ServiceType.GS
    )
    start_time: Optional[datetime] = Field(
        None, description="Start time for metrics range", example="2024-01-01T00:00:00Z"
    )
    end_time: Optional[datetime] = Field(
        None, description="End time for metrics range", example="2024-01-02T00:00:00Z"
    )
    metrics: List[str] = Field(
        default_factory=lambda: ["response_time", "throughput", "error_rate"],
        max_items=20,
        description="Specific metrics to retrieve",
        example=["response_time", "throughput", "error_rate"],
    )

    @validator("end_time")
    def validate_time_range(cls, v, values):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Validate time range."""
        if v and "start_time" in values and values["start_time"]:
            if v <= values["start_time"]:
                raise ValueError("End time must be after start time")

            # Limit range to 30 days
            time_diff = v - values["start_time"]
            if time_diff.days > 30:
                raise ValueError("Time range cannot exceed 30 days")

        return v


# Formal Verification Models
class FormalVerificationRequest(BaseValidationModel):
    """Formal verification request validation."""

    policy_content: str = Field(
        ...,
        min_length=10,
        max_length=50000,
        description="Policy content to verify",
        example="policy_rule(X) :- condition(X), constraint(Y).",
    )
    verification_type: str = Field(
        ...,
        regex=r"^(safety|liveness|fairness|consistency|completeness)$",
        description="Type of verification to perform",
        example="safety",
    )
    properties: List[str] = Field(
        ...,
        min_items=1,
        max_items=20,
        description="Properties to verify",
        example=["no_deadlock", "mutual_exclusion", "progress"],
    )
    timeout_seconds: int = Field(
        300, ge=10, le=3600, description="Verification timeout in seconds", example=300
    )
    solver_options: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional solver options",
        example={"max_iterations": 1000, "precision": "high"},
    )

    @validator("properties")
    def validate_properties_format(cls, v):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Validate properties format."""
        for prop in v:
            if not re.match(r"^[a-z_][a-z0-9_]*$", prop):
                raise ValueError(f'Property "{prop}" must be lowercase with underscores only')
        return v


class BiasDetectionRequest(BaseValidationModel):
    """Bias detection request validation."""

    content: str = Field(
        ...,
        min_length=10,
        max_length=10000,
        description="Content to analyze for bias",
        example="Policy text to analyze for potential bias",
    )
    bias_types: List[str] = Field(
        default_factory=lambda: ["gender", "racial", "age", "socioeconomic"],
        max_items=15,
        description="Types of bias to detect",
        example=["gender", "racial", "age"],
    )
    sensitivity_level: str = Field(
        "medium",
        regex=r"^(low|medium|high)$",
        description="Sensitivity level for bias detection",
        example="high",
    )

    @validator("bias_types")
    def validate_bias_types(cls, v):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Validate bias types."""
        valid_types = {
            "gender",
            "racial",
            "age",
            "socioeconomic",
            "religious",
            "political",
            "cultural",
            "linguistic",
            "disability",
            "sexual_orientation",
            "nationality",
            "educational",
        }
        for bias_type in v:
            if bias_type not in valid_types:
                raise ValueError(f"Invalid bias type: {bias_type}")
        return v


# Governance Synthesis Models
class SynthesisRequest(BaseValidationModel):
    """Policy synthesis request validation."""

    principles: List[str] = Field(
        ...,
        min_items=1,
        max_items=50,
        description="Constitutional principles to synthesize from",
        example=["transparency", "accountability", "fairness"],
    )
    context: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Context for policy synthesis",
        example="Environmental protection in urban areas",
    )
    synthesis_type: str = Field(
        "standard",
        regex=r"^(standard|enhanced_validation|multi_model_consensus|human_review)$",
        description="Type of synthesis strategy",
        example="multi_model_consensus",
    )
    target_format: str = Field(
        "datalog",
        regex=r"^(datalog|natural_language|hybrid)$",
        description="Target format for synthesized policy",
        example="datalog",
    )
    complexity_level: str = Field(
        "medium",
        regex=r"^(simple|medium|complex|expert)$",
        description="Complexity level of synthesized policy",
        example="medium",
    )
    constraints: Optional[List[str]] = Field(
        None,
        max_items=20,
        description="Additional constraints for synthesis",
        example=["no_retroactive_application", "stakeholder_consultation_required"],
    )


class MultiModelConsensusRequest(BaseValidationModel):
    """Multi-model consensus request validation."""

    input_data: str = Field(
        ...,
        min_length=10,
        max_length=20000,
        description="Input data for consensus analysis",
        example="Policy proposal for environmental regulations",
    )
    models: List[str] = Field(
        ...,
        min_items=2,
        max_items=10,
        description="Models to use for consensus",
        example=["gpt-4", "claude-3", "gemini-pro"],
    )
    consensus_threshold: float = Field(
        0.7,
        ge=0.5,
        le=1.0,
        description="Minimum consensus threshold (0.5-1.0)",
        example=0.8,
    )
    max_iterations: int = Field(
        3, ge=1, le=10, description="Maximum consensus iterations", example=5
    )

    @validator("models")
    def validate_models(cls, v):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Validate model names."""
        valid_models = {
            "gpt-4",
            "gpt-3.5-turbo",
            "claude-3",
            "claude-2",
            "gemini-pro",
            "palm-2",
            "llama-2",
            "mistral-7b",
        }
        for model in v:
            if model not in valid_models:
                raise ValueError(f"Invalid model: {model}")

        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Models must be unique")

        return v
