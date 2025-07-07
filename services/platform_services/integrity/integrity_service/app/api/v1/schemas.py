"""
Pydantic schemas for ACGS Integrity Service API endpoints.
Constitutional Hash: cdd01ef066bc6cf2
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class BaseACGSSchema(BaseModel):
    """Base schema with constitutional compliance."""

    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        str_strip_whitespace = True
        validate_assignment = True
        extra = "forbid"


# Cryptographic schemas
class CryptoKeyCreate(BaseACGSSchema):
    """Schema for creating cryptographic keys."""

    key_type: str = Field(..., description="Type of key (RSA, ECDSA, etc.)")
    key_size: int = Field(default=2048, description="Key size in bits")
    purpose: str = Field(..., description="Purpose of the key")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CryptoKey(BaseACGSSchema):
    """Schema for cryptographic key information."""

    key_id: str = Field(..., description="Unique key identifier")
    key_type: str = Field(..., description="Type of key")
    key_size: int = Field(..., description="Key size in bits")
    purpose: str = Field(..., description="Purpose of the key")
    public_key: str = Field(..., description="Public key data")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    is_active: bool = Field(default=True, description="Whether key is active")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CryptoKeyList(BaseACGSSchema):
    """Schema for listing cryptographic keys."""

    keys: List[CryptoKey] = Field(..., description="List of keys")
    total_count: int = Field(..., description="Total number of keys")


class SignatureRequest(BaseACGSSchema):
    """Schema for signature requests."""

    content: str = Field(..., description="Content to sign", min_length=1)
    key_id: str = Field(..., description="Key ID to use for signing")
    algorithm: str = Field(default="SHA-256", description="Hash algorithm")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SignatureResponse(BaseACGSSchema):
    """Schema for signature responses."""

    signature: str = Field(..., description="Generated signature")
    key_id: str = Field(..., description="Key ID used")
    algorithm: str = Field(..., description="Hash algorithm used")
    content_hash: str = Field(..., description="Hash of signed content")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SignatureVerification(BaseACGSSchema):
    """Schema for signature verification requests."""

    content: str = Field(..., description="Original content")
    signature: str = Field(..., description="Signature to verify")
    key_id: str = Field(..., description="Key ID used for signing")
    algorithm: str = Field(default="SHA-256", description="Hash algorithm")


class SignatureVerificationResult(BaseACGSSchema):
    """Schema for signature verification results."""

    is_valid: bool = Field(..., description="Whether signature is valid")
    key_id: str = Field(..., description="Key ID used")
    algorithm: str = Field(..., description="Hash algorithm")
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Optional[Dict[str, Any]] = Field(default_factory=dict)


# Merkle tree schemas
class MerkleTreeBuild(BaseACGSSchema):
    """Schema for building Merkle trees."""

    data_items: List[str] = Field(..., description="Data items for tree", min_length=1)
    hash_algorithm: str = Field(default="SHA-256", description="Hash algorithm")


class MerkleTreeResult(BaseACGSSchema):
    """Schema for Merkle tree results."""

    root_hash: str = Field(..., description="Root hash of the tree")
    tree_id: str = Field(..., description="Unique tree identifier")
    leaf_count: int = Field(..., description="Number of leaves")
    depth: int = Field(..., description="Tree depth")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MerkleProof(BaseACGSSchema):
    """Schema for Merkle proof requests."""

    tree_id: str = Field(..., description="Tree identifier")
    leaf_data: str = Field(..., description="Leaf data to prove")


class MerkleProofResult(BaseACGSSchema):
    """Schema for Merkle proof results."""

    is_valid: bool = Field(..., description="Whether proof is valid")
    proof_path: List[str] = Field(..., description="Proof path hashes")
    leaf_index: int = Field(..., description="Index of the leaf")
    root_hash: str = Field(..., description="Root hash")


class MerkleProofVerification(BaseACGSSchema):
    """Schema for Merkle proof verification."""

    leaf_data: str = Field(..., description="Leaf data")
    proof_path: List[str] = Field(..., description="Proof path")
    root_hash: str = Field(..., description="Expected root hash")
    leaf_index: int = Field(..., description="Leaf index")


# Timestamp schemas
class TimestampRequest(BaseACGSSchema):
    """Schema for timestamp requests."""

    data: str = Field(..., description="Data to timestamp")
    hash_algorithm: str = Field(default="SHA-256", description="Hash algorithm")


class TimestampResponse(BaseACGSSchema):
    """Schema for timestamp responses."""

    timestamp: datetime = Field(..., description="Timestamp")
    data_hash: str = Field(..., description="Hash of timestamped data")
    timestamp_token: str = Field(..., description="Timestamp token")
    authority: str = Field(..., description="Timestamp authority")


class TimestampVerification(BaseACGSSchema):
    """Schema for timestamp verification."""

    data: str = Field(..., description="Original data")
    timestamp_token: str = Field(..., description="Timestamp token")
    expected_timestamp: Optional[datetime] = Field(
        None, description="Expected timestamp"
    )


class TimestampVerificationResult(BaseACGSSchema):
    """Schema for timestamp verification results."""

    is_valid: bool = Field(..., description="Whether timestamp is valid")
    timestamp: datetime = Field(..., description="Verified timestamp")
    data_hash: str = Field(..., description="Data hash")
    authority: str = Field(..., description="Timestamp authority")
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Integrity verification schemas
class IntegrityCheckRequest(BaseACGSSchema):
    """Schema for integrity check requests."""

    resource_type: str = Field(..., description="Type of resource")
    resource_id: str = Field(..., description="Resource identifier")
    check_type: str = Field(default="full", description="Type of check")
    include_history: bool = Field(default=False, description="Include history")


class IntegrityCheckResult(BaseACGSSchema):
    """Schema for integrity check results."""

    is_valid: bool = Field(..., description="Whether integrity is valid")
    resource_type: str = Field(..., description="Resource type")
    resource_id: str = Field(..., description="Resource ID")
    integrity_score: float = Field(..., description="Integrity score (0-1)")
    violations: List[str] = Field(default_factory=list, description="Violations found")
    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations"
    )
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Audit schemas
class AuditLogEntry(BaseACGSSchema):
    """Schema for audit log entries."""

    event_type: str = Field(..., description="Type of event")
    service_name: str = Field(..., description="Service name")
    action: str = Field(..., description="Action performed")
    user_id: Optional[str] = Field(None, description="User ID")
    resource_type: Optional[str] = Field(None, description="Resource type")
    resource_id: Optional[str] = Field(None, description="Resource ID")
    details: Dict[str, Any] = Field(default_factory=dict, description="Event details")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLogResponse(BaseACGSSchema):
    """Schema for audit log responses."""

    log_id: str = Field(..., description="Log entry ID")
    event_type: str = Field(..., description="Event type")
    service_name: str = Field(..., description="Service name")
    action: str = Field(..., description="Action")
    timestamp: datetime = Field(..., description="Timestamp")
    signature: Optional[str] = Field(None, description="Digital signature")
    hash_chain_position: Optional[int] = Field(
        None, description="Position in hash chain"
    )


# Health and status schemas
class ServiceHealth(BaseACGSSchema):
    """Schema for service health information."""

    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    uptime_seconds: float = Field(..., description="Uptime in seconds")
    dependencies: Dict[str, str] = Field(
        default_factory=dict, description="Dependency status"
    )
    performance_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Performance metrics"
    )


class ServiceStatus(BaseACGSSchema):
    """Schema for service status information."""

    api_version: str = Field(..., description="API version")
    service: str = Field(..., description="Service name")
    status: str = Field(..., description="Service status")
    phase: str = Field(..., description="Development phase")
    routers_available: bool = Field(..., description="Whether routers are available")
    endpoints: Dict[str, List[str]] = Field(
        default_factory=dict, description="Available endpoints"
    )
    capabilities: Dict[str, Any] = Field(
        default_factory=dict, description="Service capabilities"
    )
