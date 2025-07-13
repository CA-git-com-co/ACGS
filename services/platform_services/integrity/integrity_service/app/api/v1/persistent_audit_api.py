"""
ACGS-2 Persistent Audit API Endpoints

REST API endpoints for the persistent audit logging system with hash chaining,
multi-tenant support, and constitutional compliance validation.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
from datetime import datetime, timezone
from typing import Any

from app.core.persistent_audit_logger import CONSTITUTIONAL_HASH, PersistentAuditLogger
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1/persistent-audit", tags=["Persistent Audit"])


# Pydantic models for API requests/responses
class AuditEventRequest(BaseModel):
    """Request model for logging audit events."""

    event_data: dict[str, Any] = Field(
        ...,
        description="Event data to log",
        example={
            "action": "user_login",
            "resource_type": "authentication",
            "resource_id": "user_123",
            "ip_address": "192.168.1.100",
        },
    )
    tenant_id: str | None = Field(
        None, description="Tenant ID for multi-tenant isolation"
    )
    user_id: str | None = Field(None, description="User ID who performed the action")
    service_name: str = Field(
        "integrity_service", description="Name of the service logging the event"
    )
    event_type: str = Field("audit_event", description="Type of event being logged")


class AuditEventResponse(BaseModel):
    """Response model for audit event logging."""

    success: bool = Field(..., description="Whether the operation succeeded")
    record_id: int | None = Field(None, description="Database record ID")
    current_hash: str | None = Field(None, description="Current hash in chain")
    prev_hash: str | None = Field(None, description="Previous hash in chain")
    insert_time_ms: float = Field(
        ..., description="Insert operation time in milliseconds"
    )
    constitutional_hash: str = Field(..., description="Constitutional compliance hash")
    timestamp: str | None = Field(None, description="Event timestamp")
    error: str | None = Field(None, description="Error message if failed")


class IntegrityVerificationResponse(BaseModel):
    """Response model for hash chain integrity verification."""

    integrity_verified: bool = Field(..., description="Whether integrity is verified")
    total_records: int = Field(..., description="Total records verified")
    integrity_violations: list[dict[str, Any]] = Field(
        default_factory=list, description="List of integrity violations found"
    )
    verification_time_ms: float = Field(
        ..., description="Verification time in milliseconds"
    )
    constitutional_hash: str = Field(..., description="Constitutional compliance hash")
    error: str | None = Field(None, description="Error message if failed")


class PerformanceMetricsResponse(BaseModel):
    """Response model for performance metrics."""

    avg_insert_time_ms: float = Field(
        ..., description="Average insert time in milliseconds"
    )
    p95_insert_time_ms: float = Field(..., description="95th percentile insert time")
    p99_insert_time_ms: float = Field(..., description="99th percentile insert time")
    total_operations: int = Field(..., description="Total operations performed")
    cache_hit_rate: float = Field(..., description="Cache hit rate percentage")
    cache_hits: int = Field(..., description="Total cache hits")
    cache_misses: int = Field(..., description="Total cache misses")
    constitutional_hash: str = Field(..., description="Constitutional compliance hash")


# Dependency to get the persistent audit logger from app state
async def get_persistent_audit_logger(request: Request) -> PersistentAuditLogger:
    """Get the persistent audit logger from app state."""
    if not hasattr(request.app.state, "persistent_audit_logger"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Persistent audit logger not initialized",
        )
    return request.app.state.persistent_audit_logger


@router.post("/events", response_model=AuditEventResponse)
async def log_audit_event(
    event_request: AuditEventRequest,
    audit_logger: PersistentAuditLogger = Depends(get_persistent_audit_logger),
) -> AuditEventResponse:
    """
    Log an audit event with hash chaining and constitutional compliance.

    This endpoint provides high-performance audit logging with:
    - Cryptographic hash chaining for tamper detection
    - Multi-tenant isolation via Row Level Security
    - Sub-5ms insert latency target
    - Constitutional compliance validation

    Args:
        event_request: Audit event data and metadata
        audit_logger: Persistent audit logger instance

    Returns:
        Audit event logging result with metadata
    """
    try:
        # Add constitutional hash to event data if not present
        if "constitutional_hash" not in event_request.event_data:
            event_request.event_data["constitutional_hash"] = CONSTITUTIONAL_HASH

        # Log the audit event
        result = await audit_logger.log_event(
            event_data=event_request.event_data,
            tenant_id=event_request.tenant_id,
            user_id=event_request.user_id,
            service_name=event_request.service_name,
            event_type=event_request.event_type,
        )

        return AuditEventResponse(**result)

    except Exception as e:
        logger.exception(f"Failed to log audit event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log audit event: {e!s}",
        )


@router.get("/verify-integrity", response_model=IntegrityVerificationResponse)
async def verify_hash_chain_integrity(
    tenant_id: str | None = None,
    limit: int = 1000,
    audit_logger: PersistentAuditLogger = Depends(get_persistent_audit_logger),
) -> IntegrityVerificationResponse:
    """
    Verify the integrity of the hash chain for tamper detection.

    This endpoint performs cryptographic verification of the audit log
    hash chain to detect any tampering or corruption.

    Args:
        tenant_id: Tenant ID to verify (None for all tenants)
        limit: Maximum number of records to verify
        audit_logger: Persistent audit logger instance

    Returns:
        Hash chain integrity verification result
    """
    try:
        result = await audit_logger.verify_hash_chain_integrity(
            tenant_id=tenant_id, limit=limit
        )

        return IntegrityVerificationResponse(**result)

    except Exception as e:
        logger.exception(f"Failed to verify hash chain integrity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify hash chain integrity: {e!s}",
        )


@router.get("/performance-metrics", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    audit_logger: PersistentAuditLogger = Depends(get_persistent_audit_logger),
) -> PerformanceMetricsResponse:
    """
    Get performance metrics for the audit logging system.

    This endpoint provides detailed performance metrics including:
    - Insert latency statistics (average, P95, P99)
    - Cache hit rates and statistics
    - Total operation counts
    - Constitutional compliance verification

    Args:
        audit_logger: Persistent audit logger instance

    Returns:
        Performance metrics and statistics
    """
    try:
        metrics = await audit_logger.get_performance_metrics()
        return PerformanceMetricsResponse(**metrics)

    except Exception as e:
        logger.exception(f"Failed to get performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {e!s}",
        )


@router.get("/health")
async def health_check(
    audit_logger: PersistentAuditLogger = Depends(get_persistent_audit_logger),
) -> dict[str, Any]:
    """
    Health check endpoint for the persistent audit logging system.

    Returns:
        Health status and basic system information
    """
    try:
        # Get basic performance metrics for health check
        metrics = await audit_logger.get_performance_metrics()

        # Determine health status based on performance
        is_healthy = True
        health_issues = []

        # Check if average insert time is within target (<5ms)
        if metrics["avg_insert_time_ms"] > 5.0:
            is_healthy = False
            health_issues.append(
                f"Average insert time {metrics['avg_insert_time_ms']:.2f}ms exceeds 5ms target"
            )

        # Check cache hit rate (should be >85%)
        if metrics["cache_hit_rate"] < 85.0 and metrics["total_operations"] > 10:
            health_issues.append(
                f"Cache hit rate {metrics['cache_hit_rate']:.1f}% below 85% target"
            )

        return {
            "status": "healthy" if is_healthy else "degraded",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "avg_insert_time_ms": metrics["avg_insert_time_ms"],
                "cache_hit_rate": metrics["cache_hit_rate"],
                "total_operations": metrics["total_operations"],
            },
            "issues": health_issues,
        }

    except Exception as e:
        logger.exception(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
        }


@router.post("/emergency-seal")
async def emergency_seal(
    reason: str,
    audit_logger: PersistentAuditLogger = Depends(get_persistent_audit_logger),
) -> dict[str, Any]:
    """
    Emergency seal endpoint to log critical security events.

    This endpoint is used for logging critical security events that require
    immediate attention and audit trail preservation.

    Args:
        reason: Reason for the emergency seal
        audit_logger: Persistent audit logger instance

    Returns:
        Emergency seal result
    """
    try:
        emergency_event = {
            "action": "emergency_seal",
            "resource_type": "security_event",
            "reason": reason,
            "severity": "critical",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        result = await audit_logger.log_event(
            event_data=emergency_event,
            service_name="integrity_service",
            event_type="emergency_seal",
        )

        if result["success"]:
            logger.critical(f"Emergency seal activated: {reason}")
            return {
                "sealed": True,
                "seal_id": result["record_id"],
                "seal_hash": result["current_hash"],
                "timestamp": result["timestamp"],
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        raise Exception(result.get("error", "Unknown error"))

    except Exception as e:
        logger.exception(f"Emergency seal failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Emergency seal failed: {e!s}",
        )
