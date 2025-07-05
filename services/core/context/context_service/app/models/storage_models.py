"""
Storage Layer Data Models

Defines data structures for the multi-tier storage architecture
supporting Redis, Qdrant, and PostgreSQL storage tiers.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class StorageTier(str, Enum):
    """Storage tiers in the multi-tier architecture."""
    
    L1_CACHE = "l1_cache"        # Redis - sub-1ms retrieval
    L2_VECTOR = "l2_vector"      # Qdrant - sub-10ms semantic search
    L3_ARCHIVE = "l3_archive"    # PostgreSQL - long-term storage


class VectorDocument(BaseModel):
    """Document model for vector database storage."""
    
    document_id: str = Field(description="Unique document identifier")
    context_id: UUID = Field(description="Associated context ID")
    
    # Vector data
    embedding_vector: List[float] = Field(description="Dense embedding vector")
    sparse_vector: Optional[Dict[int, float]] = Field(None, description="Sparse vector for keywords")
    
    # Content
    content: str = Field(description="Document content")
    content_type: str = Field(description="Content type (text, json, etc.)")
    
    # Metadata for filtering
    metadata: Dict[str, Any] = Field(description="Document metadata")
    
    # Timestamps
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    # Search optimization
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    language: str = Field(default="en", description="Content language")
    
    # Performance tracking
    access_count: int = Field(default=0, description="Number of times accessed")
    last_accessed: datetime = Field(description="Last access timestamp")


class ContextEmbedding(BaseModel):
    """Embedding model for context vectors."""
    
    context_id: UUID = Field(description="Associated context ID")
    embedding_model: str = Field(description="Model used for embedding")
    embedding_version: str = Field(description="Embedding model version")
    
    # Vector data
    dense_vector: List[float] = Field(description="Dense embedding vector")
    sparse_vector: Optional[Dict[int, float]] = Field(None, description="Sparse vector")
    vector_dimension: int = Field(description="Vector dimension")
    
    # Embedding metadata
    input_text: str = Field(description="Original text used for embedding")
    preprocessing_steps: List[str] = Field(default_factory=list, description="Applied preprocessing")
    
    # Quality metrics
    embedding_confidence: Optional[float] = Field(None, description="Embedding quality confidence")
    semantic_density: Optional[float] = Field(None, description="Semantic information density")
    
    # WINA optimization
    wina_optimized: bool = Field(default=False, description="WINA optimization applied")
    wina_compression_ratio: Optional[float] = Field(None, description="WINA compression ratio")
    
    created_at: datetime = Field(description="Embedding creation time")


class StorageMetrics(BaseModel):
    """Metrics for storage tier performance."""
    
    tier: StorageTier = Field(description="Storage tier")
    
    # Capacity metrics
    total_capacity_bytes: int = Field(description="Total storage capacity")
    used_capacity_bytes: int = Field(description="Used storage capacity")
    available_capacity_bytes: int = Field(description="Available storage capacity")
    utilization_percentage: float = Field(description="Storage utilization percentage")
    
    # Performance metrics
    average_read_latency_ms: float = Field(description="Average read latency")
    average_write_latency_ms: float = Field(description="Average write latency")
    throughput_ops_per_second: float = Field(description="Operations per second")
    
    # Quality metrics
    cache_hit_rate: Optional[float] = Field(None, description="Cache hit rate (for L1)")
    index_efficiency: Optional[float] = Field(None, description="Index efficiency (for L2)")
    query_success_rate: float = Field(description="Query success rate")
    
    # Usage statistics
    total_operations: int = Field(description="Total operations performed")
    read_operations: int = Field(description="Read operations")
    write_operations: int = Field(description="Write operations")
    delete_operations: int = Field(description="Delete operations")
    
    # Error tracking
    failed_operations: int = Field(description="Failed operations")
    error_rate: float = Field(description="Error rate percentage")
    
    # Timestamp
    measurement_time: datetime = Field(default_factory=datetime.utcnow, description="Measurement timestamp")
    measurement_period_seconds: int = Field(description="Measurement period in seconds")


class CacheEntry(BaseModel):
    """Model for Redis cache entries."""
    
    cache_key: str = Field(description="Cache key")
    context_id: UUID = Field(description="Associated context ID")
    
    # Cached data
    cached_data: Dict[str, Any] = Field(description="Cached context data")
    data_type: str = Field(description="Type of cached data")
    
    # Cache metadata
    ttl_seconds: int = Field(description="Time to live in seconds")
    priority: int = Field(default=1, description="Cache priority (1-10)")
    
    # Access tracking
    hit_count: int = Field(default=0, description="Number of cache hits")
    miss_count: int = Field(default=0, description="Number of cache misses")
    last_hit: Optional[datetime] = Field(None, description="Last cache hit time")
    
    # Timestamps
    created_at: datetime = Field(description="Cache entry creation time")
    expires_at: datetime = Field(description="Cache expiration time")


class ArchiveEntry(BaseModel):
    """Model for PostgreSQL archive entries."""
    
    archive_id: UUID = Field(description="Archive entry ID")
    context_id: UUID = Field(description="Original context ID")
    
    # Archived data
    archived_content: str = Field(description="Archived context content")
    content_compression: str = Field(default="none", description="Compression method used")
    content_encryption: bool = Field(default=False, description="Content encryption status")
    
    # Archive metadata
    archive_reason: str = Field(description="Reason for archival")
    retention_period_days: Optional[int] = Field(None, description="Retention period")
    access_restrictions: List[str] = Field(default_factory=list, description="Access restrictions")
    
    # Compliance
    constitutional_compliant: bool = Field(description="Constitutional compliance status")
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list, description="Audit trail")
    
    # Timestamps
    archived_at: datetime = Field(description="Archival timestamp")
    original_created_at: datetime = Field(description="Original context creation time")
    scheduled_deletion_at: Optional[datetime] = Field(None, description="Scheduled deletion time")


class StorageOperation(BaseModel):
    """Model for tracking storage operations."""
    
    operation_id: UUID = Field(description="Operation identifier")
    operation_type: str = Field(description="Type of operation (read, write, delete, etc.)")
    tier: StorageTier = Field(description="Storage tier")
    
    # Operation details
    context_id: UUID = Field(description="Target context ID")
    data_size_bytes: int = Field(description="Data size in bytes")
    
    # Performance metrics
    latency_ms: float = Field(description="Operation latency")
    success: bool = Field(description="Operation success status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # WINA optimization
    wina_optimization_applied: bool = Field(default=False, description="WINA optimization used")
    optimization_savings_ms: Optional[float] = Field(None, description="Latency savings from optimization")
    
    # Timestamps
    started_at: datetime = Field(description="Operation start time")
    completed_at: datetime = Field(description="Operation completion time")
    
    # Context
    service_name: str = Field(description="Service that performed operation")
    user_id: Optional[str] = Field(None, description="User who initiated operation")