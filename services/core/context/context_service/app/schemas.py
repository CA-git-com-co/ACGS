"""
API Schemas for Context Service

Pydantic schemas for request/response models used in the REST API.
These schemas handle validation and serialization for the context service endpoints.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .models.context_models import (
    ContextMetadata,
    ContextPriority,
    ContextStatus,
    ContextType,
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Request Schemas


class ContextCreateRequest(BaseModel):
    """Request schema for creating new context."""

    context_type: ContextType = Field(description="Type of context to create")
    content: str = Field(description="Context content", min_length=1, max_length=100000)
    priority: ContextPriority = Field(
        default=ContextPriority.MEDIUM, description="Context priority"
    )

    # Optional fields based on context type
    conversation_id: str | None = Field(
        None, description="Conversation ID (for conversation context)"
    )
    domain: str | None = Field(None, description="Domain (for domain context)")
    principle_id: str | None = Field(
        None, description="Principle ID (for constitutional context)"
    )
    agent_id: str | None = Field(None, description="Agent ID (for agent context)")
    policy_id: str | None = Field(None, description="Policy ID (for policy context)")

    # Metadata
    keywords: list[str] = Field(default_factory=list, description="Context keywords")
    tags: list[str] = Field(default_factory=list, description="Context tags")
    parent_context_id: UUID | None = Field(None, description="Parent context ID")

    # Lifecycle
    custom_ttl_seconds: int | None = Field(None, description="Custom TTL in seconds")

    # Options
    generate_embedding: bool = Field(
        default=True, description="Generate vector embedding"
    )
    apply_wina_optimization: bool = Field(
        default=True, description="Apply WINA optimization"
    )


class ContextUpdateRequest(BaseModel):
    """Request schema for updating existing context."""

    content: str | None = Field(None, description="Updated content")
    priority: ContextPriority | None = Field(None, description="Updated priority")
    status: ContextStatus | None = Field(None, description="Updated status")

    keywords: list[str] | None = Field(None, description="Updated keywords")
    tags: list[str] | None = Field(None, description="Updated tags")

    extend_ttl_seconds: int | None = Field(None, description="Extend TTL by seconds")
    regenerate_embedding: bool = Field(
        default=False, description="Regenerate vector embedding"
    )


class ContextSearchRequest(BaseModel):
    """Request schema for context search."""

    query: str = Field(description="Search query", min_length=1, max_length=1000)
    context_types: list[ContextType] = Field(
        default_factory=list, description="Filter by context types"
    )

    # Search options
    semantic_search: bool = Field(default=True, description="Enable semantic search")
    keyword_search: bool = Field(default=True, description="Enable keyword search")
    similarity_threshold: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Minimum similarity"
    )

    # Filters
    priority_filter: ContextPriority | None = Field(
        None, description="Filter by priority"
    )
    status_filter: list[ContextStatus] = Field(
        default=[ContextStatus.ACTIVE], description="Filter by status"
    )
    created_after: datetime | None = Field(None, description="Created after timestamp")
    created_before: datetime | None = Field(
        None, description="Created before timestamp"
    )
    tags_filter: list[str] = Field(default_factory=list, description="Filter by tags")

    # Pagination
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results")
    offset: int = Field(default=0, ge=0, description="Result offset")

    # Optimization
    apply_wina_optimization: bool = Field(
        default=True, description="Apply WINA optimization"
    )
    use_cache: bool = Field(
        default=True, description="Use cached results when available"
    )


class ContextBatchCreateRequest(BaseModel):
    """Request schema for creating multiple contexts."""

    contexts: list[ContextCreateRequest] = Field(
        description="Contexts to create", max_items=100
    )
    transaction_mode: bool = Field(
        default=False, description="All-or-nothing transaction mode"
    )


class ContextExpirationRequest(BaseModel):
    """Request schema for context expiration management."""

    context_ids: list[UUID] = Field(description="Context IDs to expire", max_items=1000)
    expire_immediately: bool = Field(
        default=False, description="Expire immediately or mark for expiration"
    )


# Response Schemas


class ContextResponse(BaseModel):
    """Response schema for context operations."""

    model_config = ConfigDict(from_attributes=True)

    context_id: UUID = Field(description="Context identifier")
    context_type: ContextType = Field(description="Context type")
    priority: ContextPriority = Field(description="Context priority")
    status: ContextStatus = Field(description="Context status")

    content: str = Field(description="Context content")
    content_hash: str = Field(description="Content integrity hash")

    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    expires_at: datetime | None = Field(description="Expiration timestamp")
    accessed_at: datetime = Field(description="Last access timestamp")

    metadata: ContextMetadata = Field(description="Context metadata")
    keywords: list[str] = Field(description="Context keywords")

    # Hierarchical relationships
    parent_context_id: UUID | None = Field(description="Parent context ID")
    child_context_ids: list[UUID] = Field(description="Child context IDs")

    # Performance indicators
    retrieval_latency_ms: float | None = Field(None, description="Retrieval latency")
    storage_tier: str | None = Field(None, description="Storage tier used")
    cache_hit: bool | None = Field(None, description="Cache hit indicator")


class ContextSearchResponse(BaseModel):
    """Response schema for context search results."""

    results: list[dict[str, Any]] = Field(description="Search results")
    total_count: int = Field(description="Total matching contexts")
    query_latency_ms: float = Field(description="Query execution latency")

    # Search metadata
    semantic_search_used: bool = Field(description="Semantic search was used")
    keyword_search_used: bool = Field(description="Keyword search was used")
    wina_optimization_applied: bool = Field(description="WINA optimization was applied")

    # Pagination
    limit: int = Field(description="Result limit")
    offset: int = Field(description="Result offset")
    has_more: bool = Field(description="More results available")

    # Performance
    cache_hit_rate: float = Field(description="Cache hit rate for this query")
    storage_tiers_accessed: list[str] = Field(description="Storage tiers accessed")


class ContextStatsResponse(BaseModel):
    """Response schema for context statistics."""

    total_contexts: int = Field(description="Total contexts")
    contexts_by_type: dict[str, int] = Field(description="Contexts by type")
    contexts_by_status: dict[str, int] = Field(description="Contexts by status")

    # Storage metrics
    total_storage_bytes: int = Field(description="Total storage used")
    storage_by_tier: dict[str, int] = Field(description="Storage by tier")

    # Performance metrics
    average_retrieval_latency_ms: float = Field(description="Average retrieval latency")
    average_storage_latency_ms: float = Field(description="Average storage latency")
    overall_cache_hit_rate: float = Field(description="Overall cache hit rate")

    # Health indicators
    constitutional_compliance_rate: float = Field(
        description="Constitutional compliance rate"
    )
    wina_optimization_rate: float = Field(description="WINA optimization usage rate")
    expired_contexts_pending: int = Field(
        description="Expired contexts pending cleanup"
    )

    collection_time: datetime = Field(description="Statistics collection time")


class HealthCheckResponse(BaseModel):
    """Response schema for health check."""

    status: str = Field(description="Service status")
    timestamp: datetime = Field(description="Health check timestamp")

    # Service components
    redis_healthy: bool = Field(description="Redis cluster health")
    qdrant_healthy: bool = Field(description="Qdrant database health")
    postgresql_healthy: bool = Field(description="PostgreSQL health")
    streaming_healthy: bool = Field(description="Event streaming health")

    # Performance indicators
    average_response_time_ms: float = Field(description="Average response time")
    requests_per_second: float = Field(description="Current requests per second")

    # Resource utilization
    memory_usage_percent: float = Field(description="Memory usage percentage")
    cpu_usage_percent: float = Field(description="CPU usage percentage")

    # Operational metrics
    contexts_processed_last_hour: int = Field(
        description="Contexts processed in last hour"
    )
    errors_last_hour: int = Field(description="Errors in last hour")


class ErrorResponse(BaseModel):
    """Response schema for error conditions."""

    error_code: str = Field(description="Error code")
    error_message: str = Field(description="Human-readable error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error timestamp"
    )
    request_id: str | None = Field(None, description="Request identifier for tracing")

    # Context for debugging
    service_name: str = Field(default="context_service", description="Service name")
    service_version: str = Field(default="1.0.0", description="Service version")


# Batch Operation Schemas


class BatchOperationResponse(BaseModel):
    """Response schema for batch operations."""

    operation_id: UUID = Field(description="Batch operation identifier")
    total_items: int = Field(description="Total items in batch")
    successful_items: int = Field(description="Successfully processed items")
    failed_items: int = Field(description="Failed items")

    # Results
    results: list[dict[str, Any]] = Field(description="Individual operation results")
    errors: list[ErrorResponse] = Field(description="Errors encountered")

    # Performance
    total_processing_time_ms: float = Field(description="Total processing time")
    average_item_processing_time_ms: float = Field(description="Average time per item")

    # Status
    status: str = Field(description="Batch operation status")
    completed_at: datetime = Field(description="Completion timestamp")


# WebSocket Schemas


class ContextEventNotification(BaseModel):
    """Schema for real-time context event notifications."""

    event_type: str = Field(description="Event type")
    context_id: UUID = Field(description="Context identifier")
    timestamp: datetime = Field(description="Event timestamp")

    # Event data
    event_data: dict[str, Any] = Field(description="Event-specific data")

    # Metadata
    service_name: str = Field(description="Service that generated event")
    constitutional_compliant: bool = Field(
        description="Constitutional compliance status"
    )
