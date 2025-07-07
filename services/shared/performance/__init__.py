"""
Performance Optimization Components for ACGS
Constitutional Hash: cdd01ef066bc6cf2

High-performance caching, connection pooling, and optimization utilities.
"""

from .batch_processor import (
    BatchConfig,
    BatchProcessor,
    DatabaseBatchProcessor,
    EventBatchProcessor,
)
from .caching import (
    CacheManager,
    CacheStrategy,
    MemoryCache,
    MultiLevelCache,
    RedisCache,
    cache_result,
    invalidate_cache,
)
from .connection_pool import (
    ConnectionPoolManager,
    PostgreSQLPoolManager,
    RedisPoolManager,
    get_connection_pool,
)
from .metrics import (
    LatencyTracker,
    MetricsCollector,
    PerformanceMetrics,
    ThroughputTracker,
)
from .query_optimizer import IndexAnalyzer, QueryOptimizer, QueryPlan, optimize_query

__all__ = [
    # Caching
    "CacheManager",
    "RedisCache",
    "MemoryCache",
    "MultiLevelCache",
    "CacheStrategy",
    "cache_result",
    "invalidate_cache",
    # Connection Pooling
    "ConnectionPoolManager",
    "PostgreSQLPoolManager",
    "RedisPoolManager",
    "get_connection_pool",
    # Batch Processing
    "BatchProcessor",
    "BatchConfig",
    "DatabaseBatchProcessor",
    "EventBatchProcessor",
    # Query Optimization
    "QueryOptimizer",
    "QueryPlan",
    "IndexAnalyzer",
    "optimize_query",
    # Metrics
    "PerformanceMetrics",
    "MetricsCollector",
    "LatencyTracker",
    "ThroughputTracker",
]
