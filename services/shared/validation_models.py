"""
ACGS Shared Validation Models
Constitutional Hash: cdd01ef066bc6cf2

Provides common Pydantic models for validation across ACGS services.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class BaseACGSModel(BaseModel):
    """Base model with constitutional compliance."""

    constitutional_hash: str = Field(
        default=CONSTITUTIONAL_HASH, description="Constitutional compliance hash"
    )

    class Config:
        str_strip_whitespace = True
        validate_assignment = True
        extra = "forbid"


class SignatureRequest(BaseACGSModel):
    """Request model for digital signature operations."""

    content: str = Field(
        ..., description="Content to be signed", min_length=1, max_length=10000
    )
    algorithm: str = Field(default="SHA-256", description="Hash algorithm to use")
    key_id: Optional[str] = Field(None, description="Key ID for signing")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()

    @field_validator("algorithm")
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        allowed_algorithms = ["SHA-256", "SHA-512", "SHA3-256", "SHA3-512"]
        if v not in allowed_algorithms:
            raise ValueError(
                f"Algorithm must be one of: {', '.join(allowed_algorithms)}"
            )
        return v


class SignatureResponse(BaseACGSModel):
    """Response model for digital signature operations."""

    signature: str = Field(..., description="Generated digital signature")
    algorithm: str = Field(..., description="Hash algorithm used")
    key_id: str = Field(..., description="Key ID used for signing")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content_hash: str = Field(..., description="Hash of the signed content")


class VerificationRequest(BaseACGSModel):
    """Request model for signature verification."""

    content: str = Field(..., description="Original content", min_length=1)
    signature: str = Field(..., description="Signature to verify", min_length=1)
    key_id: str = Field(..., description="Key ID used for signing", min_length=1)
    algorithm: str = Field(default="SHA-256", description="Hash algorithm used")


class VerificationResponse(BaseACGSModel):
    """Response model for signature verification."""

    is_valid: bool = Field(..., description="Whether the signature is valid")
    key_id: str = Field(..., description="Key ID used for verification")
    algorithm: str = Field(..., description="Hash algorithm used")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    verification_details: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AuditLogEntry(BaseACGSModel):
    """Model for audit log entries."""

    event_type: str = Field(..., description="Type of event", min_length=1)
    user_id: Optional[str] = Field(
        None, description="User ID associated with the event"
    )
    service_name: str = Field(..., description="Name of the service", min_length=1)
    resource_type: Optional[str] = Field(None, description="Type of resource affected")
    resource_id: Optional[str] = Field(None, description="ID of the resource affected")
    action: str = Field(..., description="Action performed", min_length=1)
    details: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional details"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        allowed_types = [
            "authentication",
            "authorization",
            "data_access",
            "data_modification",
            "system_event",
            "security_event",
            "compliance_check",
            "error",
        ]
        if v not in allowed_types:
            raise ValueError(f"Event type must be one of: {', '.join(allowed_types)}")
        return v


class PolicyRule(BaseACGSModel):
    """Model for policy rules."""

    rule_id: str = Field(..., description="Unique rule identifier", min_length=1)
    name: str = Field(..., description="Human-readable rule name", min_length=1)
    description: str = Field(..., description="Rule description", min_length=1)
    rule_type: str = Field(..., description="Type of rule", min_length=1)
    conditions: Dict[str, Any] = Field(..., description="Rule conditions")
    actions: Dict[str, Any] = Field(
        ..., description="Actions to take when rule matches"
    )
    enabled: bool = Field(default=True, description="Whether the rule is enabled")
    priority: int = Field(
        default=100, description="Rule priority (lower = higher priority)"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: int) -> int:
        if v < 1 or v > 1000:
            raise ValueError("Priority must be between 1 and 1000")
        return v


class MultiModelConsensusRequest(BaseACGSModel):
    """Request model for multi-model consensus operations."""

    models: List[str] = Field(
        ..., description="List of model identifiers", min_length=1
    )
    input_data: Dict[str, Any] = Field(..., description="Input data for consensus")
    consensus_threshold: float = Field(
        default=0.7, description="Consensus threshold (0.0-1.0)"
    )
    timeout_seconds: int = Field(
        default=30, description="Timeout for consensus operation"
    )
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @field_validator("models")
    @classmethod
    def validate_models(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("At least one model must be specified")
        return v

    @field_validator("consensus_threshold")
    @classmethod
    def validate_threshold(cls, v: float) -> float:
        if v < 0.0 or v > 1.0:
            raise ValueError("Consensus threshold must be between 0.0 and 1.0")
        return v

    @field_validator("timeout_seconds")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        if v < 1 or v > 300:
            raise ValueError("Timeout must be between 1 and 300 seconds")
        return v


class ConsensusResponse(BaseACGSModel):
    """Response model for consensus operations."""

    consensus_reached: bool = Field(..., description="Whether consensus was reached")
    consensus_score: float = Field(..., description="Consensus score (0.0-1.0)")
    participating_models: List[str] = Field(..., description="Models that participated")
    result: Optional[Dict[str, Any]] = Field(None, description="Consensus result")
    individual_results: List[Dict[str, Any]] = Field(default_factory=list)
    processing_time_ms: float = Field(
        ..., description="Processing time in milliseconds"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrityCheckRequest(BaseACGSModel):
    """Request model for integrity checks."""

    resource_type: str = Field(
        ..., description="Type of resource to check", min_length=1
    )
    resource_id: str = Field(..., description="ID of the resource", min_length=1)
    check_type: str = Field(default="full", description="Type of integrity check")
    include_history: bool = Field(
        default=False, description="Include historical integrity data"
    )

    @field_validator("check_type")
    @classmethod
    def validate_check_type(cls, v: str) -> str:
        allowed_types = ["quick", "full", "deep", "cryptographic"]
        if v not in allowed_types:
            raise ValueError(f"Check type must be one of: {', '.join(allowed_types)}")
        return v


class IntegrityCheckResponse(BaseACGSModel):
    """Response model for integrity checks."""

    is_valid: bool = Field(..., description="Whether integrity check passed")
    resource_type: str = Field(..., description="Type of resource checked")
    resource_id: str = Field(..., description="ID of the resource checked")
    check_type: str = Field(..., description="Type of check performed")
    integrity_score: float = Field(..., description="Integrity score (0.0-1.0)")
    violations: List[str] = Field(
        default_factory=list, description="List of integrity violations"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations for fixes"
    )
    check_details: Dict[str, Any] = Field(
        default_factory=dict, description="Detailed check results"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaginationParams(BaseModel):
    """Model for pagination parameters."""

    page: int = Field(default=1, description="Page number (1-based)", ge=1)
    size: int = Field(default=20, description="Page size", ge=1, le=100)
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: str = Field(default="asc", description="Sort order")

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        if v not in ["asc", "desc"]:
            raise ValueError("Sort order must be 'asc' or 'desc'")
        return v


class PaginatedResponse(BaseACGSModel):
    """Model for paginated responses."""

    items: List[Any] = Field(..., description="List of items")
    total_count: int = Field(..., description="Total number of items", ge=0)
    page: int = Field(..., description="Current page number", ge=1)
    size: int = Field(..., description="Page size", ge=1)
    total_pages: int = Field(..., description="Total number of pages", ge=0)
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")


class HealthCheckRequest(BaseACGSModel):
    """Request model for health checks."""

    include_dependencies: bool = Field(
        default=True, description="Include dependency health"
    )
    include_metrics: bool = Field(
        default=True, description="Include performance metrics"
    )
    timeout_seconds: int = Field(default=10, description="Timeout for health check")

    @field_validator("timeout_seconds")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        if v < 1 or v > 60:
            raise ValueError("Timeout must be between 1 and 60 seconds")
        return v
