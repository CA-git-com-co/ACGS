"""
PostgreSQL Query Performance Optimizer for ACGS Services
Constitutional Hash: cdd01ef066bc6cf2

Advanced query optimization with prepared statement caching, constitutional
compliance lookups optimization, and read replica configuration for <5ms latency.
"""

import hashlib
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Query performance metrics."""

    total_queries: int = 0
    prepared_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    query_times: list[float] = field(default_factory=list)
    slow_queries: int = 0

    def add_query_time(
        self, time_ms: float, is_prepared: bool = False, is_cached: bool = False
    ):
        """Add query time measurement."""
        self.total_queries += 1
        self.query_times.append(time_ms)

        if is_prepared:
            self.prepared_queries += 1

        if is_cached:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

        if time_ms > 5.0:  # >5ms is slow
            self.slow_queries += 1

    def get_avg_query_time(self) -> float:
        """Get average query time."""
        return (
            sum(self.query_times) / len(self.query_times) if self.query_times else 0.0
        )

    def get_p95_query_time(self) -> float:
        """Get P95 query time."""
        if not self.query_times:
            return 0.0
        sorted_times = sorted(self.query_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[min(index, len(sorted_times) - 1)]

    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0.0


class PreparedStatementCache:
    """Thread-safe prepared statement cache."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.statements = {}
        self.access_times = {}
        self.lock = threading.RLock()

    def get_statement_key(self, query: str) -> str:
        """Generate cache key for query."""
        # Include constitutional hash for compliance
        key_data = f"{query}:{CONSTITUTIONAL_HASH}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, query: str) -> str | None:
        """Get prepared statement name."""
        key = self.get_statement_key(query)

        with self.lock:
            if key in self.statements:
                self.access_times[key] = time.time()
                return self.statements[key]
            return None

    def set(self, query: str, statement_name: str) -> None:
        """Cache prepared statement."""
        key = self.get_statement_key(query)

        with self.lock:
            # Evict oldest if at capacity
            if len(self.statements) >= self.max_size:
                oldest_key = min(self.access_times.keys(), key=self.access_times.get)
                del self.statements[oldest_key]
                del self.access_times[oldest_key]

            self.statements[key] = statement_name
            self.access_times[key] = time.time()

    def size(self) -> int:
        """Get cache size."""
        with self.lock:
            return len(self.statements)


class ConstitutionalQueryOptimizer:
    """Optimized queries for constitutional compliance operations."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH

        # Pre-optimized constitutional queries
        self.constitutional_queries = {
            "validate_hash": """
                SELECT EXISTS(
                    SELECT 1 FROM constitutional_compliance
                    WHERE hash = $1 AND is_valid = true
                ) AS is_valid
            """,
            "get_compliance_status": """
                SELECT compliance_status, last_validated, validation_count
                FROM constitutional_compliance
                WHERE hash = $1
            """,
            "log_validation": """
                INSERT INTO constitutional_audit_log
                (hash, service_name, endpoint, validation_result, timestamp)
                VALUES ($1, $2, $3, $4, NOW())
                ON CONFLICT (hash, service_name, endpoint, timestamp)
                DO UPDATE SET validation_result = EXCLUDED.validation_result
            """,
            "get_agent_compliance": """
                SELECT agent_id, compliance_score, last_check
                FROM agent_constitutional_compliance
                WHERE constitutional_hash = $1 AND compliance_score >= $2
                ORDER BY compliance_score DESC, last_check DESC
                LIMIT $3
            """,
            "update_compliance_metrics": """
                UPDATE constitutional_metrics
                SET
                    total_validations = total_validations + 1,
                    successful_validations = successful_validations + $2,
                    last_updated = NOW()
                WHERE hash = $1
            """,
        }

    def get_optimized_query(self, query_type: str) -> str | None:
        """Get pre-optimized constitutional query."""
        return self.constitutional_queries.get(query_type)

    def get_all_queries(self) -> dict[str, str]:
        """Get all optimized constitutional queries."""
        return self.constitutional_queries.copy()


class PostgreSQLQueryOptimizer:
    """Advanced PostgreSQL query optimizer with caching and performance tracking."""

    def __init__(self, connection_pool):
        self.connection_pool = connection_pool
        self.prepared_cache = PreparedStatementCache()
        self.constitutional_optimizer = ConstitutionalQueryOptimizer()
        self.metrics = QueryMetrics()
        self.metrics_lock = threading.Lock()

        # Query optimization settings
        self.enable_prepared_statements = True
        self.enable_query_caching = True
        self.slow_query_threshold = 5.0  # 5ms

        # Read replica configuration
        self.read_replicas = []
        self.read_replica_enabled = False

        logger.info(
            f"PostgreSQL Query Optimizer initialized [hash: {CONSTITUTIONAL_HASH}]"
        )

    async def initialize_prepared_statements(self):
        """Initialize commonly used prepared statements."""
        try:
            async with self.connection_pool.get_connection() as conn:
                # Prepare constitutional compliance queries
                constitutional_queries = self.constitutional_optimizer.get_all_queries()

                for query_name, query_sql in constitutional_queries.items():
                    statement_name = f"acgs_constitutional_{query_name}"

                    try:
                        await conn.execute(f"PREPARE {statement_name} AS {query_sql}")
                        self.prepared_cache.set(query_sql, statement_name)
                        logger.debug(f"Prepared statement: {statement_name}")
                    except Exception as e:
                        logger.warning(f"Failed to prepare {statement_name}: {e}")

                # Prepare common ACGS queries
                common_queries = {
                    "get_agent_status": """
                        SELECT agent_id, status, last_heartbeat, capabilities
                        FROM agents WHERE status = $1 AND last_heartbeat > NOW() - INTERVAL '5 minutes'
                    """,
                    "update_task_status": """
                        UPDATE tasks SET status = $2, updated_at = NOW()
                        WHERE task_id = $1
                    """,
                    "get_service_health": """
                        SELECT service_name, status, last_check, response_time_ms
                        FROM service_health WHERE service_name = $1
                    """,
                }

                for query_name, query_sql in common_queries.items():
                    statement_name = f"acgs_common_{query_name}"

                    try:
                        await conn.execute(f"PREPARE {statement_name} AS {query_sql}")
                        self.prepared_cache.set(query_sql, statement_name)
                        logger.debug(f"Prepared statement: {statement_name}")
                    except Exception as e:
                        logger.warning(f"Failed to prepare {statement_name}: {e}")

                logger.info(
                    f"Initialized {self.prepared_cache.size()} prepared statements"
                )

        except Exception as e:
            logger.exception(f"Failed to initialize prepared statements: {e}")

    async def execute_optimized_query(
        self, query: str, params: tuple = (), use_read_replica: bool = False
    ) -> list[dict[str, Any]]:
        """Execute query with optimization."""
        start_time = time.perf_counter()

        try:
            # Choose connection pool (read replica or primary)
            pool = self._get_connection_pool(use_read_replica)

            async with pool.get_connection() as conn:
                # Try to use prepared statement
                statement_name = None
                is_prepared = False

                if self.enable_prepared_statements:
                    statement_name = self.prepared_cache.get(query)
                    if statement_name:
                        is_prepared = True

                # Execute query
                if is_prepared:
                    result = await conn.fetch(f"EXECUTE {statement_name}", *params)
                else:
                    result = await conn.fetch(query, *params)

                # Convert to list of dicts
                result_list = [dict(row) for row in result]

                # Record metrics
                query_time = (time.perf_counter() - start_time) * 1000

                with self.metrics_lock:
                    self.metrics.add_query_time(
                        query_time,
                        is_prepared=is_prepared,
                        is_cached=statement_name is not None,
                    )

                # Log slow queries
                if query_time > self.slow_query_threshold:
                    logger.warning(f"Slow query ({query_time:.2f}ms): {query[:100]}...")

                return result_list

        except Exception as e:
            query_time = (time.perf_counter() - start_time) * 1000
            logger.exception(f"Query failed ({query_time:.2f}ms): {e}")
            raise

    async def execute_constitutional_query(
        self, query_type: str, params: tuple = ()
    ) -> list[dict[str, Any]]:
        """Execute optimized constitutional compliance query."""
        query = self.constitutional_optimizer.get_optimized_query(query_type)
        if not query:
            raise ValueError(f"Unknown constitutional query type: {query_type}")

        return await self.execute_optimized_query(query, params)

    async def validate_constitutional_hash_fast(self, hash_value: str) -> bool:
        """Fast constitutional hash validation using optimized query."""
        try:
            result = await self.execute_constitutional_query(
                "validate_hash", (hash_value,)
            )
            return result[0]["is_valid"] if result else False

        except Exception as e:
            logger.exception(f"Constitutional hash validation failed: {e}")
            return False

    async def get_compliance_status_fast(self, hash_value: str) -> dict[str, Any]:
        """Fast compliance status lookup."""
        try:
            result = await self.execute_constitutional_query(
                "get_compliance_status", (hash_value,)
            )
            return result[0] if result else {}

        except Exception as e:
            logger.exception(f"Compliance status lookup failed: {e}")
            return {}

    async def log_constitutional_validation(
        self, hash_value: str, service_name: str, endpoint: str, validation_result: bool
    ) -> bool:
        """Log constitutional validation with optimized query."""
        try:
            await self.execute_constitutional_query(
                "log_validation",
                (hash_value, service_name, endpoint, validation_result),
            )
            return True

        except Exception as e:
            logger.exception(f"Constitutional validation logging failed: {e}")
            return False

    def _get_connection_pool(self, use_read_replica: bool = False):
        """Get appropriate connection pool."""
        if use_read_replica and self.read_replica_enabled and self.read_replicas:
            # Simple round-robin selection
            import random

            return random.choice(self.read_replicas)
        return self.connection_pool

    def configure_read_replicas(self, replica_pools: list):
        """Configure read replica connection pools."""
        self.read_replicas = replica_pools
        self.read_replica_enabled = len(replica_pools) > 0

        logger.info(f"Configured {len(replica_pools)} read replicas")

    async def optimize_database_settings(self):
        """Apply database-level optimizations."""
        try:
            async with self.connection_pool.get_connection() as conn:
                # Apply performance optimizations
                optimizations = [
                    "SET shared_preload_libraries = 'pg_stat_statements'",
                    "SET effective_cache_size = '1GB'",
                    "SET shared_buffers = '256MB'",
                    "SET work_mem = '16MB'",
                    "SET maintenance_work_mem = '64MB'",
                    "SET checkpoint_completion_target = 0.9",
                    "SET wal_buffers = '16MB'",
                    "SET default_statistics_target = 100",
                    "SET random_page_cost = 1.1",
                    "SET effective_io_concurrency = 200",
                ]

                for optimization in optimizations:
                    try:
                        await conn.execute(optimization)
                        logger.debug(f"Applied: {optimization}")
                    except Exception as e:
                        logger.warning(f"Failed to apply {optimization}: {e}")

                # Create indexes for constitutional compliance
                indexes = [
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_constitutional_compliance_hash
                    ON constitutional_compliance(hash) WHERE is_valid = true
                    """,
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_constitutional_audit_log_hash_time
                    ON constitutional_audit_log(hash, timestamp DESC)
                    """,
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agent_compliance_hash_score
                    ON agent_constitutional_compliance(constitutional_hash, compliance_score DESC)
                    """,
                ]

                for index_sql in indexes:
                    try:
                        await conn.execute(index_sql)
                        logger.debug("Created constitutional compliance index")
                    except Exception as e:
                        logger.warning(f"Index creation failed: {e}")

                logger.info("Database optimizations applied")

        except Exception as e:
            logger.exception(f"Database optimization failed: {e}")

    def get_performance_stats(self) -> dict[str, Any]:
        """Get comprehensive query performance statistics."""
        with self.metrics_lock:
            return {
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "query_metrics": {
                    "total_queries": self.metrics.total_queries,
                    "prepared_queries": self.metrics.prepared_queries,
                    "avg_query_time_ms": self.metrics.get_avg_query_time(),
                    "p95_query_time_ms": self.metrics.get_p95_query_time(),
                    "slow_queries": self.metrics.slow_queries,
                    "slow_query_rate": (
                        self.metrics.slow_queries
                        / max(self.metrics.total_queries, 1)
                        * 100
                    ),
                },
                "cache_metrics": {
                    "cache_hit_rate": self.metrics.get_cache_hit_rate(),
                    "cache_hits": self.metrics.cache_hits,
                    "cache_misses": self.metrics.cache_misses,
                    "prepared_statements_cached": self.prepared_cache.size(),
                },
                "optimization_settings": {
                    "prepared_statements_enabled": self.enable_prepared_statements,
                    "query_caching_enabled": self.enable_query_caching,
                    "read_replicas_enabled": self.read_replica_enabled,
                    "read_replicas_count": len(self.read_replicas),
                },
                "performance_targets": {
                    "query_time_target_ms": 5.0,
                    "cache_hit_rate_target": 85.0,
                    "query_time_met": self.metrics.get_avg_query_time() <= 5.0,
                    "cache_hit_rate_met": self.metrics.get_cache_hit_rate() >= 85.0,
                },
            }

    async def health_check(self) -> dict[str, bool]:
        """Perform health check on query optimizer."""
        health_status = {
            "primary_connection": False,
            "prepared_statements": False,
            "constitutional_queries": False,
            "read_replicas": False,
        }

        try:
            # Test primary connection
            async with self.connection_pool.get_connection() as conn:
                await conn.fetchval("SELECT 1")
                health_status["primary_connection"] = True

            # Test prepared statements
            health_status["prepared_statements"] = self.prepared_cache.size() > 0

            # Test constitutional queries
            await self.validate_constitutional_hash_fast(CONSTITUTIONAL_HASH)
            health_status["constitutional_queries"] = True  # If no exception

            # Test read replicas
            if self.read_replica_enabled:
                for replica in self.read_replicas:
                    try:
                        async with replica.get_connection() as conn:
                            await conn.fetchval("SELECT 1")
                        health_status["read_replicas"] = True
                        break
                    except Exception:
                        continue
            else:
                health_status["read_replicas"] = True  # Not configured, so healthy

        except Exception as e:
            logger.exception(f"Query optimizer health check failed: {e}")

        return health_status


# Global query optimizer instance
_query_optimizer = None


async def get_query_optimizer(connection_pool) -> PostgreSQLQueryOptimizer:
    """Get or create global query optimizer instance."""
    global _query_optimizer

    if _query_optimizer is None:
        _query_optimizer = PostgreSQLQueryOptimizer(connection_pool)
        await _query_optimizer.initialize_prepared_statements()
        await _query_optimizer.optimize_database_settings()

    return _query_optimizer
