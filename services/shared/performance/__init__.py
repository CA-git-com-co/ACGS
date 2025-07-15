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
try:
    from .caching import (
        CacheManager,
        CacheStrategy,
        MemoryCache,
        MultiLevelCache,
        RedisCache,
        cache_result,
        invalidate_cache,
    )
except ImportError:
    # Create stub classes if caching module is not available
    class CacheManager:
        pass
    
    class CacheStrategy:
        pass
    
    class MemoryCache:
        pass
    
    class MultiLevelCache:
        pass
    
    class RedisCache:
        pass
    
    def cache_result(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def invalidate_cache(*args, **kwargs):
        pass
try:
    from .connection_pool import (
        ConnectionPoolManager,
        PostgreSQLPoolManager,
        RedisPoolManager,
        get_connection_pool,
    )
except ImportError:
    # Create stub classes if connection_pool module is not available
    class ConnectionPoolManager:
        pass
    
    class PostgreSQLPoolManager:
        pass
    
    class RedisPoolManager:
        pass
    
    def get_connection_pool(*args, **kwargs):
        return None
try:
    from .metrics import (
        LatencyTracker,
        MetricsCollector,
        PerformanceMetrics,
        ThroughputTracker,
    )
except ImportError:
    # Create stub classes if metrics module is not available
    class LatencyTracker:
        pass
    
    class MetricsCollector:
        pass
    
    class PerformanceMetrics:
        pass
    
    class ThroughputTracker:
        pass
try:
    from .query_optimizer import IndexAnalyzer, QueryOptimizer, QueryPlan, optimize_query
except ImportError:
    # Create stub classes if query_optimizer module is not available
    class IndexAnalyzer:
        pass
    
    class QueryOptimizer:
        pass
    
    class QueryPlan:
        pass
    
    def optimize_query(*args, **kwargs):
        return None

__all__ = [
    "BatchConfig",
    # Batch Processing
    "BatchProcessor",
    # Caching
    "CacheManager",
    "CacheStrategy",
    # Connection Pooling
    "ConnectionPoolManager",
    "DatabaseBatchProcessor",
    "EventBatchProcessor",
    "IndexAnalyzer",
    "LatencyTracker",
    "MemoryCache",
    "MetricsCollector",
    "MultiLevelCache",
    # Metrics
    "PerformanceMetrics",
    "PostgreSQLPoolManager",
    # Query Optimization
    "QueryOptimizer",
    "QueryPlan",
    "RedisCache",
    "RedisPoolManager",
    "ThroughputTracker",
    "cache_result",
    "get_connection_pool",
    "invalidate_cache",
    "optimize_query",
]
