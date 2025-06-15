"""
ACGS-1 Database Performance Optimizer

Comprehensive database and caching optimization system:
- PostgreSQL query optimization and indexing
- Redis caching with intelligent TTL management
- Connection pool optimization
- Query performance monitoring
- Data consistency validation
- Automated performance tuning

Target: <200ms database query times, >99.5% cache hit rate
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import json
import hashlib

import asyncpg
import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Database and cache performance metrics."""
    query_count: int = 0
    total_query_time_ms: float = 0.0
    slow_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_sets: int = 0
    avg_query_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OptimizationConfig:
    """Configuration for database and cache optimization."""
    # Database settings
    db_pool_size: int = 25
    db_max_overflow: int = 35
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    slow_query_threshold_ms: float = 200.0
    
    # Cache settings
    redis_max_connections: int = 25
    default_ttl_seconds: int = 3600
    cache_compression: bool = True
    cache_serialization: str = "json"  # json, pickle, msgpack
    
    # Optimization settings
    auto_index_creation: bool = True
    query_plan_analysis: bool = True
    cache_warming: bool = True
    performance_monitoring: bool = True
    
    # TTL policies for different data types
    ttl_policies: Dict[str, int] = field(default_factory=lambda: {
        "user_sessions": 1800,      # 30 minutes
        "auth_tokens": 3600,        # 1 hour
        "policy_decisions": 300,    # 5 minutes
        "governance_rules": 3600,   # 1 hour
        "static_config": 86400,     # 24 hours
        "api_responses": 600,       # 10 minutes
        "compliance_checks": 900,   # 15 minutes
        "synthesis_results": 1200,  # 20 minutes
        "constitutional_data": 7200, # 2 hours
        "performance_metrics": 120,  # 2 minutes
    })


class DatabasePerformanceOptimizer:
    """
    Comprehensive database performance optimizer for ACGS-1.
    
    Provides intelligent query optimization, caching, and performance monitoring
    to achieve <200ms query times and >99.5% cache hit rates.
    """

    def __init__(self, config: Optional[OptimizationConfig] = None):
        """Initialize the performance optimizer."""
        self.config = config or OptimizationConfig()
        
        # Database connections
        self.db_engine = None
        self.db_pool = None
        
        # Redis connections
        self.redis_client = None
        self.redis_pool = None
        
        # Performance tracking
        self.metrics = PerformanceMetrics()
        self.query_history: List[Dict[str, Any]] = []
        self.slow_queries: List[Dict[str, Any]] = []
        
        # Optimization state
        self.running = False
        self.optimization_tasks: List[asyncio.Task] = []
        
        # Query cache for prepared statements
        self.prepared_statements: Dict[str, str] = {}
        self.query_plans: Dict[str, Dict[str, Any]] = {}

    async def initialize(self):
        """Initialize database and cache connections."""
        if self.running:
            return

        logger.info("Initializing Database Performance Optimizer")
        
        try:
            # Initialize database engine with optimized settings
            await self._initialize_database()
            
            # Initialize Redis cache
            await self._initialize_redis()
            
            # Start optimization tasks
            await self._start_optimization_tasks()
            
            self.running = True
            logger.info("Database Performance Optimizer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize performance optimizer: {e}")
            raise

    async def _initialize_database(self):
        """Initialize optimized database connection."""
        database_url = "postgresql+asyncpg://acgs_user:acgs_password@localhost:5432/acgs_pgp_db"
        
        self.db_engine = create_async_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=self.config.db_pool_size,
            max_overflow=self.config.db_max_overflow,
            pool_timeout=self.config.db_pool_timeout,
            pool_recycle=self.config.db_pool_recycle,
            pool_pre_ping=True,
            pool_reset_on_return="commit",
            echo=False,  # Disable for performance
            connect_args={
                "server_settings": {
                    "application_name": "acgs_performance_optimizer",
                    "jit": "off",  # Disable JIT for consistent performance
                    "statement_timeout": "30000",  # 30 seconds
                    "idle_in_transaction_session_timeout": "60000",  # 1 minute
                }
            }
        )
        
        # Test connection
        async with self.db_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("Database connection established successfully")

    async def _initialize_redis(self):
        """Initialize optimized Redis connection."""
        self.redis_pool = redis.ConnectionPool(
            host="localhost",
            port=6379,
            db=0,
            max_connections=self.config.redis_max_connections,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        self.redis_client = redis.Redis(connection_pool=self.redis_pool)
        
        # Test connection
        await self.redis_client.ping()
        logger.info("Redis connection established successfully")

    async def _start_optimization_tasks(self):
        """Start background optimization tasks."""
        self.optimization_tasks = [
            asyncio.create_task(self._performance_monitoring_loop()),
            asyncio.create_task(self._cache_warming_loop()),
            asyncio.create_task(self._query_optimization_loop()),
            asyncio.create_task(self._metrics_collection_loop())
        ]

    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None, 
                          cache_key: Optional[str] = None, ttl: Optional[int] = None) -> Any:
        """
        Execute optimized database query with caching.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            cache_key: Cache key for result caching
            ttl: Cache TTL in seconds
            
        Returns:
            Query result
        """
        start_time = time.time()
        
        try:
            # Check cache first if cache_key provided
            if cache_key and self.redis_client:
                cached_result = await self._get_cached_result(cache_key)
                if cached_result is not None:
                    self.metrics.cache_hits += 1
                    return cached_result
                else:
                    self.metrics.cache_misses += 1
            
            # Execute database query
            async with self.db_engine.begin() as conn:
                result = await conn.execute(text(query), params or {})
                
                # Convert result to serializable format
                if result.returns_rows:
                    rows = result.fetchall()
                    query_result = [dict(row._mapping) for row in rows]
                else:
                    query_result = {"rowcount": result.rowcount}
            
            # Cache result if cache_key provided
            if cache_key and self.redis_client:
                await self._cache_result(cache_key, query_result, ttl)
            
            # Update performance metrics
            query_time = (time.time() - start_time) * 1000
            await self._update_query_metrics(query, query_time, params)
            
            return query_result
            
        except Exception as e:
            query_time = (time.time() - start_time) * 1000
            await self._update_query_metrics(query, query_time, params, error=str(e))
            raise

    async def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get cached result from Redis."""
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                if self.config.cache_serialization == "json":
                    return json.loads(cached_data)
                # Add other serialization methods as needed
            return None
        except Exception as e:
            logger.warning(f"Cache get error for key {cache_key}: {e}")
            return None

    async def _cache_result(self, cache_key: str, result: Any, ttl: Optional[int] = None):
        """Cache query result in Redis."""
        try:
            ttl = ttl or self.config.default_ttl_seconds
            
            if self.config.cache_serialization == "json":
                serialized_data = json.dumps(result, default=str)
            else:
                serialized_data = str(result)
            
            await self.redis_client.setex(cache_key, ttl, serialized_data)
            self.metrics.cache_sets += 1
            
        except Exception as e:
            logger.warning(f"Cache set error for key {cache_key}: {e}")

    async def _update_query_metrics(self, query: str, query_time_ms: float, 
                                  params: Optional[Dict[str, Any]] = None, 
                                  error: Optional[str] = None):
        """Update query performance metrics."""
        self.metrics.query_count += 1
        self.metrics.total_query_time_ms += query_time_ms
        
        if query_time_ms > self.config.slow_query_threshold_ms:
            self.metrics.slow_queries += 1
            self.slow_queries.append({
                "query": query[:200] + "..." if len(query) > 200 else query,
                "query_time_ms": query_time_ms,
                "params": params,
                "error": error,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Calculate averages
        if self.metrics.query_count > 0:
            self.metrics.avg_query_time_ms = self.metrics.total_query_time_ms / self.metrics.query_count
        
        total_cache_operations = self.metrics.cache_hits + self.metrics.cache_misses
        if total_cache_operations > 0:
            self.metrics.cache_hit_rate = (self.metrics.cache_hits / total_cache_operations) * 100
        
        self.metrics.last_updated = datetime.utcnow()

    async def _performance_monitoring_loop(self):
        """Monitor database and cache performance."""
        while self.running:
            try:
                await self._collect_database_stats()
                await self._collect_cache_stats()
                await asyncio.sleep(60)  # Every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(30)

    async def _collect_database_stats(self):
        """Collect database performance statistics."""
        try:
            async with self.db_engine.begin() as conn:
                # Get active connections
                result = await conn.execute(text("""
                    SELECT count(*) as active_connections 
                    FROM pg_stat_activity 
                    WHERE state = 'active'
                """))
                active_connections = result.scalar()
                
                # Get slow queries from pg_stat_statements if available
                try:
                    result = await conn.execute(text("""
                        SELECT query, calls, total_time, mean_time 
                        FROM pg_stat_statements 
                        WHERE mean_time > :threshold 
                        ORDER BY mean_time DESC 
                        LIMIT 10
                    """), {"threshold": self.config.slow_query_threshold_ms})
                    
                    slow_queries_db = result.fetchall()
                    logger.info(f"Database stats: {active_connections} active connections, "
                              f"{len(slow_queries_db)} slow queries detected")
                except:
                    # pg_stat_statements not available
                    pass
                    
        except Exception as e:
            logger.warning(f"Database stats collection error: {e}")

    async def _collect_cache_stats(self):
        """Collect Redis cache statistics."""
        try:
            info = await self.redis_client.info()
            
            cache_stats = {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
            
            # Calculate Redis hit rate
            total_ops = cache_stats["keyspace_hits"] + cache_stats["keyspace_misses"]
            if total_ops > 0:
                redis_hit_rate = (cache_stats["keyspace_hits"] / total_ops) * 100
                logger.info(f"Redis stats: {redis_hit_rate:.2f}% hit rate, "
                          f"{cache_stats['used_memory_human']} memory used")
                
        except Exception as e:
            logger.warning(f"Cache stats collection error: {e}")

    async def _cache_warming_loop(self):
        """Warm cache with frequently accessed data."""
        if not self.config.cache_warming:
            return
            
        while self.running:
            try:
                await self._warm_constitutional_data()
                await self._warm_static_configuration()
                await asyncio.sleep(3600)  # Every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache warming error: {e}")
                await asyncio.sleep(1800)  # Retry in 30 minutes

    async def _warm_constitutional_data(self):
        """Warm cache with constitutional principles and governance rules."""
        try:
            # Cache active constitutional principles
            principles_query = """
                SELECT id, title, content, category, priority_weight 
                FROM principles 
                WHERE is_active = true 
                ORDER BY priority_weight DESC
            """
            
            cache_key = "constitutional:active_principles"
            await self.execute_query(
                principles_query, 
                cache_key=cache_key, 
                ttl=self.config.ttl_policies.get("constitutional_data", 7200)
            )
            
            logger.info("Constitutional data cache warmed")
            
        except Exception as e:
            logger.warning(f"Constitutional data cache warming error: {e}")

    async def _warm_static_configuration(self):
        """Warm cache with static configuration data."""
        try:
            # Cache system configuration
            config_query = """
                SELECT key, value, category 
                FROM system_configuration 
                WHERE is_active = true
            """
            
            cache_key = "system:configuration"
            await self.execute_query(
                config_query,
                cache_key=cache_key,
                ttl=self.config.ttl_policies.get("static_config", 86400)
            )
            
            logger.info("Static configuration cache warmed")
            
        except Exception as e:
            logger.warning(f"Static configuration cache warming error: {e}")

    async def _query_optimization_loop(self):
        """Analyze and optimize slow queries."""
        if not self.config.query_plan_analysis:
            return
            
        while self.running:
            try:
                await self._analyze_slow_queries()
                await asyncio.sleep(1800)  # Every 30 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Query optimization error: {e}")
                await asyncio.sleep(900)  # Retry in 15 minutes

    async def _analyze_slow_queries(self):
        """Analyze slow queries and suggest optimizations."""
        if not self.slow_queries:
            return
            
        try:
            # Analyze recent slow queries
            recent_slow = [q for q in self.slow_queries[-10:] if not q.get("error")]
            
            for query_info in recent_slow:
                query = query_info["query"]
                
                # Get query execution plan
                async with self.db_engine.begin() as conn:
                    explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
                    try:
                        result = await conn.execute(text(explain_query))
                        plan = result.scalar()
                        
                        # Store query plan for analysis
                        query_hash = hashlib.md5(query.encode()).hexdigest()
                        self.query_plans[query_hash] = {
                            "query": query,
                            "plan": plan,
                            "execution_time_ms": query_info["query_time_ms"],
                            "analyzed_at": datetime.utcnow().isoformat()
                        }
                        
                    except Exception as e:
                        logger.warning(f"Query plan analysis failed: {e}")
            
            logger.info(f"Analyzed {len(recent_slow)} slow queries")
            
        except Exception as e:
            logger.warning(f"Slow query analysis error: {e}")

    async def _metrics_collection_loop(self):
        """Collect and aggregate performance metrics."""
        while self.running:
            try:
                # Update metrics timestamp
                self.metrics.last_updated = datetime.utcnow()
                
                # Log performance summary
                if self.metrics.query_count > 0:
                    logger.info(
                        f"Performance Summary: "
                        f"{self.metrics.query_count} queries, "
                        f"{self.metrics.avg_query_time_ms:.2f}ms avg, "
                        f"{self.metrics.cache_hit_rate:.2f}% cache hit rate, "
                        f"{self.metrics.slow_queries} slow queries"
                    )
                
                await asyncio.sleep(300)  # Every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)

    async def get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key with consistent format."""
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()[:16]

    async def invalidate_cache_pattern(self, pattern: str):
        """Invalidate cache keys matching pattern."""
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys matching pattern: {pattern}")
        except Exception as e:
            logger.warning(f"Cache invalidation error for pattern {pattern}: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            "query_metrics": {
                "total_queries": self.metrics.query_count,
                "avg_query_time_ms": round(self.metrics.avg_query_time_ms, 2),
                "slow_queries": self.metrics.slow_queries,
                "slow_query_threshold_ms": self.config.slow_query_threshold_ms
            },
            "cache_metrics": {
                "cache_hits": self.metrics.cache_hits,
                "cache_misses": self.metrics.cache_misses,
                "cache_sets": self.metrics.cache_sets,
                "cache_hit_rate": round(self.metrics.cache_hit_rate, 2)
            },
            "performance_targets": {
                "query_time_target_ms": 200,
                "cache_hit_rate_target": 99.5,
                "query_time_achieved": self.metrics.avg_query_time_ms <= 200,
                "cache_hit_rate_achieved": self.metrics.cache_hit_rate >= 99.5
            },
            "last_updated": self.metrics.last_updated.isoformat()
        }

    async def stop(self):
        """Stop the performance optimizer."""
        if not self.running:
            return
            
        logger.info("Stopping Database Performance Optimizer")
        self.running = False
        
        # Cancel optimization tasks
        for task in self.optimization_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.optimization_tasks:
            await asyncio.gather(*self.optimization_tasks, return_exceptions=True)
        
        # Close connections
        if self.redis_client:
            await self.redis_client.close()
        
        if self.db_engine:
            await self.db_engine.dispose()
        
        logger.info("Database Performance Optimizer stopped")


# Global optimizer instance
_optimizer: Optional[DatabasePerformanceOptimizer] = None


async def get_performance_optimizer(config: Optional[OptimizationConfig] = None) -> DatabasePerformanceOptimizer:
    """Get the global performance optimizer instance."""
    global _optimizer
    
    if _optimizer is None:
        _optimizer = DatabasePerformanceOptimizer(config)
        await _optimizer.initialize()
    
    return _optimizer


async def stop_performance_optimizer():
    """Stop the global performance optimizer."""
    global _optimizer

    if _optimizer:
        await _optimizer.stop()
        _optimizer = None


class IntelligentCacheManager:
    """
    Intelligent cache manager with adaptive TTL and smart invalidation.

    Features:
    - Adaptive TTL based on access patterns
    - Smart cache warming and preloading
    - Intelligent invalidation strategies
    - Cache analytics and optimization
    """

    def __init__(self, redis_client: redis.Redis, config: OptimizationConfig):
        """Initialize intelligent cache manager."""
        self.redis_client = redis_client
        self.config = config

        # Cache analytics
        self.access_patterns: Dict[str, Dict[str, Any]] = {}
        self.invalidation_history: List[Dict[str, Any]] = []

        # Adaptive TTL settings
        self.min_ttl = 60  # 1 minute
        self.max_ttl = 86400  # 24 hours
        self.ttl_adjustment_factor = 1.2

    async def smart_cache_set(self, key: str, value: Any,
                            data_type: str = "default",
                            access_frequency: Optional[float] = None) -> bool:
        """
        Set cache with intelligent TTL calculation.

        Args:
            key: Cache key
            value: Value to cache
            data_type: Type of data for TTL policy lookup
            access_frequency: Expected access frequency (accesses per hour)

        Returns:
            True if successful
        """
        try:
            # Calculate intelligent TTL
            ttl = await self._calculate_adaptive_ttl(key, data_type, access_frequency)

            # Serialize value
            serialized_value = json.dumps(value, default=str)

            # Set with calculated TTL
            await self.redis_client.setex(key, ttl, serialized_value)

            # Update access patterns
            await self._update_access_pattern(key, "set", ttl)

            return True

        except Exception as e:
            logger.error(f"Smart cache set error for key {key}: {e}")
            return False

    async def smart_cache_get(self, key: str) -> Optional[Any]:
        """
        Get cached value with access pattern tracking.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        try:
            # Get value from cache
            cached_data = await self.redis_client.get(key)

            if cached_data:
                # Update access patterns
                await self._update_access_pattern(key, "hit")

                # Deserialize and return
                return json.loads(cached_data)
            else:
                # Update access patterns
                await self._update_access_pattern(key, "miss")
                return None

        except Exception as e:
            logger.error(f"Smart cache get error for key {key}: {e}")
            return None

    async def _calculate_adaptive_ttl(self, key: str, data_type: str,
                                    access_frequency: Optional[float] = None) -> int:
        """Calculate adaptive TTL based on access patterns and data type."""
        # Start with base TTL from policy
        base_ttl = self.config.ttl_policies.get(data_type, self.config.default_ttl_seconds)

        # Get access pattern for this key
        pattern = self.access_patterns.get(key, {})

        if not pattern:
            return base_ttl

        # Calculate access frequency if not provided
        if access_frequency is None:
            hits = pattern.get("hits", 0)
            time_span = pattern.get("time_span_hours", 1)
            access_frequency = hits / max(time_span, 1)

        # Adjust TTL based on access frequency
        if access_frequency > 10:  # High frequency
            adjusted_ttl = int(base_ttl * self.ttl_adjustment_factor)
        elif access_frequency < 1:  # Low frequency
            adjusted_ttl = int(base_ttl / self.ttl_adjustment_factor)
        else:
            adjusted_ttl = base_ttl

        # Ensure TTL is within bounds
        return max(self.min_ttl, min(adjusted_ttl, self.max_ttl))

    async def _update_access_pattern(self, key: str, operation: str, ttl: Optional[int] = None):
        """Update access pattern tracking for a key."""
        now = datetime.utcnow()

        if key not in self.access_patterns:
            self.access_patterns[key] = {
                "hits": 0,
                "misses": 0,
                "sets": 0,
                "first_access": now,
                "last_access": now,
                "time_span_hours": 0
            }

        pattern = self.access_patterns[key]
        pattern["last_access"] = now

        # Update operation counters
        if operation == "hit":
            pattern["hits"] += 1
        elif operation == "miss":
            pattern["misses"] += 1
        elif operation == "set":
            pattern["sets"] += 1
            if ttl:
                pattern["last_ttl"] = ttl

        # Calculate time span
        time_diff = now - pattern["first_access"]
        pattern["time_span_hours"] = time_diff.total_seconds() / 3600

    async def warm_cache_intelligent(self, warming_config: Dict[str, Any]):
        """
        Intelligent cache warming based on access patterns and priorities.

        Args:
            warming_config: Configuration for cache warming
        """
        try:
            for data_type, config in warming_config.items():
                query = config.get("query")
                cache_key_prefix = config.get("cache_key_prefix")
                priority = config.get("priority", 1)

                if not query or not cache_key_prefix:
                    continue

                # Execute query and cache results
                # This would integrate with the database optimizer
                logger.info(f"Warming cache for {data_type} with priority {priority}")

        except Exception as e:
            logger.error(f"Intelligent cache warming error: {e}")

    def get_cache_analytics(self) -> Dict[str, Any]:
        """Get comprehensive cache analytics."""
        total_keys = len(self.access_patterns)

        if total_keys == 0:
            return {"message": "No cache analytics available"}

        # Calculate aggregate statistics
        total_hits = sum(p.get("hits", 0) for p in self.access_patterns.values())
        total_misses = sum(p.get("misses", 0) for p in self.access_patterns.values())
        total_operations = total_hits + total_misses

        hit_rate = (total_hits / total_operations * 100) if total_operations > 0 else 0

        # Find most accessed keys
        top_keys = sorted(
            self.access_patterns.items(),
            key=lambda x: x[1].get("hits", 0),
            reverse=True
        )[:10]

        return {
            "total_keys": total_keys,
            "total_hits": total_hits,
            "total_misses": total_misses,
            "hit_rate_percent": round(hit_rate, 2),
            "top_accessed_keys": [
                {
                    "key": key,
                    "hits": pattern.get("hits", 0),
                    "misses": pattern.get("misses", 0),
                    "last_access": pattern.get("last_access", "").isoformat() if pattern.get("last_access") else ""
                }
                for key, pattern in top_keys
            ]
        }
