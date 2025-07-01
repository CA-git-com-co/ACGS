"""
Advanced Database Optimization for ACGS-PGP v8

Implements connection pooling optimization, query performance monitoring,
and database-specific optimizations for production workloads.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import asyncpg
import psutil
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.pool import Pool

logger = logging.getLogger(__name__)


@dataclass
class ConnectionPoolMetrics:
    """Connection pool performance metrics."""

    pool_size: int = 0
    checked_out: int = 0
    overflow: int = 0
    checked_in: int = 0
    total_connections: int = 0
    avg_checkout_time: float = 0.0
    max_checkout_time: float = 0.0
    connection_errors: int = 0
    pool_timeouts: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QueryPerformanceMetrics:
    """Query performance tracking metrics."""

    query_hash: str
    query_type: str
    execution_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    last_executed: datetime = field(default_factory=datetime.utcnow)
    slow_query_count: int = 0
    error_count: int = 0


class DatabaseOptimizer:
    """Advanced database optimization and monitoring system."""

    def __init__(self, database_url: str, slow_query_threshold: float = 1.0):
        """
        Initialize database optimizer.

        Args:
            database_url: Database connection URL
            slow_query_threshold: Threshold in seconds for slow query detection
        """
        self.database_url = database_url
        self.slow_query_threshold = slow_query_threshold

        # Performance tracking
        self.pool_metrics: Dict[str, ConnectionPoolMetrics] = {}
        self.query_metrics: Dict[str, QueryPerformanceMetrics] = {}
        self.connection_checkout_times: Dict[int, float] = {}

        # Optimization settings
        self.optimized_settings = {
            # Connection pool optimization
            "pool_size": 25,  # Increased from 20
            "max_overflow": 40,  # Increased from 30
            "pool_timeout": 20,  # Reduced from 30 for faster failure
            "pool_recycle": 1800,  # Reduced from 3600 for fresher connections
            "pool_pre_ping": True,
            "pool_reset_on_return": "commit",
            # PostgreSQL-specific optimizations
            "connect_args": {
                "server_settings": {
                    "application_name": "acgs_pgp_v8_optimized",
                    "jit": "off",  # Disable JIT for consistent performance
                    "statement_timeout": "30s",
                    "idle_in_transaction_session_timeout": "60s",
                    "tcp_keepalives_idle": "300",
                    "tcp_keepalives_interval": "30",
                    "tcp_keepalives_count": "3",
                }
            },
        }

        logger.info("Database optimizer initialized")

    def setup_connection_monitoring(self, engine: Engine):
        """Setup connection pool monitoring for SQLAlchemy engine."""

        @event.listens_for(engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            """Handle new database connections."""
            connection_id = id(dbapi_connection)
            logger.debug(f"New database connection established: {connection_id}")

            # Set connection-specific optimizations
            if hasattr(dbapi_connection, "cursor"):
                cursor = dbapi_connection.cursor()
                try:
                    # Set session-level optimizations
                    cursor.execute("SET work_mem = '32MB'")
                    cursor.execute("SET random_page_cost = 1.1")
                    cursor.execute("SET effective_io_concurrency = 200")
                    cursor.execute("SET synchronous_commit = 'local'")
                    cursor.close()
                except Exception as e:
                    logger.warning(f"Failed to set connection optimizations: {e}")

        @event.listens_for(engine, "checkout")
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            """Track connection checkout times."""
            connection_id = id(dbapi_connection)
            self.connection_checkout_times[connection_id] = time.time()

        @event.listens_for(engine, "checkin")
        def on_checkin(dbapi_connection, connection_record):
            """Track connection checkin and calculate usage time."""
            connection_id = id(dbapi_connection)
            if connection_id in self.connection_checkout_times:
                checkout_time = self.connection_checkout_times.pop(connection_id)
                usage_time = time.time() - checkout_time

                # Update pool metrics
                self._update_pool_metrics(engine.pool, usage_time)

        @event.listens_for(engine, "invalidate")
        def on_invalidate(dbapi_connection, connection_record, exception):
            """Handle connection invalidation."""
            logger.warning(f"Database connection invalidated: {exception}")
            self._increment_connection_errors()

    def _update_pool_metrics(self, pool: Pool, checkout_time: float):
        """Update connection pool metrics."""
        pool_id = str(id(pool))

        if pool_id not in self.pool_metrics:
            self.pool_metrics[pool_id] = ConnectionPoolMetrics()

        metrics = self.pool_metrics[pool_id]
        metrics.pool_size = pool.size()
        metrics.checked_out = pool.checkedout()
        metrics.overflow = pool.overflow()
        metrics.checked_in = pool.checkedin()
        metrics.total_connections = metrics.checked_out + metrics.checked_in

        # Update checkout time statistics
        if checkout_time > 0:
            if metrics.avg_checkout_time == 0:
                metrics.avg_checkout_time = checkout_time
            else:
                metrics.avg_checkout_time = (
                    metrics.avg_checkout_time + checkout_time
                ) / 2

            metrics.max_checkout_time = max(metrics.max_checkout_time, checkout_time)

        metrics.timestamp = datetime.utcnow()

    def _increment_connection_errors(self):
        """Increment connection error count."""
        for metrics in self.pool_metrics.values():
            metrics.connection_errors += 1

    async def setup_query_monitoring(self, engine: AsyncEngine):
        """Setup query performance monitoring."""

        @event.listens_for(engine.sync_engine, "before_cursor_execute")
        def before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            """Track query execution start time."""
            context._query_start_time = time.time()
            context._query_statement = statement

        @event.listens_for(engine.sync_engine, "after_cursor_execute")
        def after_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            """Track query execution completion and performance."""
            if hasattr(context, "_query_start_time"):
                execution_time = time.time() - context._query_start_time
                self._track_query_performance(statement, execution_time)

    def _track_query_performance(self, statement: str, execution_time: float):
        """Track individual query performance."""
        # Create query hash for grouping similar queries
        query_hash = str(hash(statement.strip()[:200]))  # Use first 200 chars for hash
        query_type = self._classify_query(statement)

        if query_hash not in self.query_metrics:
            self.query_metrics[query_hash] = QueryPerformanceMetrics(
                query_hash=query_hash, query_type=query_type
            )

        metrics = self.query_metrics[query_hash]
        metrics.execution_count += 1
        metrics.total_time += execution_time
        metrics.avg_time = metrics.total_time / metrics.execution_count
        metrics.min_time = min(metrics.min_time, execution_time)
        metrics.max_time = max(metrics.max_time, execution_time)
        metrics.last_executed = datetime.utcnow()

        # Track slow queries
        if execution_time > self.slow_query_threshold:
            metrics.slow_query_count += 1
            logger.warning(
                f"Slow query detected ({execution_time:.3f}s): {statement[:100]}..."
            )

    def _classify_query(self, statement: str) -> str:
        """Classify query type for performance analysis."""
        statement_upper = statement.strip().upper()

        if statement_upper.startswith("SELECT"):
            return "SELECT"
        elif statement_upper.startswith("INSERT"):
            return "INSERT"
        elif statement_upper.startswith("UPDATE"):
            return "UPDATE"
        elif statement_upper.startswith("DELETE"):
            return "DELETE"
        elif statement_upper.startswith("CREATE"):
            return "CREATE"
        elif statement_upper.startswith("ALTER"):
            return "ALTER"
        else:
            return "OTHER"

    async def create_performance_indexes(self, connection_url: str):
        """Create performance-optimized indexes for ACGS-PGP v8."""
        indexes = [
            # Policy generation indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policy_generations_created_at ON policy_generations(created_at DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policy_generations_user_id_created ON policy_generations(user_id, created_at DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policy_generations_compliance_score ON policy_generations(constitutional_compliance_score DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policy_generations_semantic_hash ON policy_generations(semantic_hash);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policy_generations_constitutional_hash ON policy_generations(constitutional_hash);",
            # Stabilizer execution indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stabilizer_executions_status_created ON stabilizer_executions(status, created_at DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stabilizer_executions_execution_time ON stabilizer_executions(execution_time_ms);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stabilizer_executions_errors ON stabilizer_executions(errors_detected, errors_corrected);",
            # Syndrome diagnosis indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_syndrome_diagnoses_severity_timestamp ON syndrome_diagnoses(severity, diagnostic_timestamp DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_syndrome_diagnoses_category_confidence ON syndrome_diagnoses(error_category, confidence_score DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_syndrome_diagnoses_policy_generation ON syndrome_diagnoses(policy_generation_id);",
            # Composite indexes for common queries
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policy_generations_composite ON policy_generations(constitutional_hash, constitutional_compliance_score DESC, created_at DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stabilizer_executions_composite ON stabilizer_executions(constitutional_hash, status, execution_time_ms);",
        ]

        conn = await asyncpg.connect(connection_url)
        try:
            for index_sql in indexes:
                try:
                    logger.info(f"Creating index: {index_sql[:80]}...")
                    await conn.execute(index_sql)
                    logger.info("Index created successfully")
                except Exception as e:
                    logger.warning(f"Index creation failed (may already exist): {e}")
        finally:
            await conn.close()

    async def optimize_postgresql_settings(self, connection_url: str):
        """Apply PostgreSQL-specific optimizations."""
        optimizations = [
            # Memory optimizations for governance workload
            "ALTER SYSTEM SET shared_buffers = '512MB';",
            "ALTER SYSTEM SET effective_cache_size = '2GB';",
            "ALTER SYSTEM SET work_mem = '32MB';",
            "ALTER SYSTEM SET maintenance_work_mem = '128MB';",
            "ALTER SYSTEM SET wal_buffers = '32MB';",
            # Connection optimizations
            "ALTER SYSTEM SET max_connections = '300';",
            "ALTER SYSTEM SET max_worker_processes = '12';",
            "ALTER SYSTEM SET max_parallel_workers = '8';",
            "ALTER SYSTEM SET max_parallel_workers_per_gather = '4';",
            # Query optimization
            "ALTER SYSTEM SET random_page_cost = '1.1';",
            "ALTER SYSTEM SET effective_io_concurrency = '300';",
            "ALTER SYSTEM SET default_statistics_target = '150';",
            "ALTER SYSTEM SET constraint_exclusion = 'partition';",
            # Checkpoint and WAL optimizations
            "ALTER SYSTEM SET checkpoint_completion_target = '0.9';",
            "ALTER SYSTEM SET checkpoint_timeout = '15min';",
            "ALTER SYSTEM SET max_wal_size = '2GB';",
            "ALTER SYSTEM SET min_wal_size = '512MB';",
            # Logging for monitoring
            "ALTER SYSTEM SET log_min_duration_statement = '1000';",
            "ALTER SYSTEM SET log_checkpoints = 'on';",
            "ALTER SYSTEM SET log_lock_waits = 'on';",
            "ALTER SYSTEM SET log_temp_files = '100MB';",
            # Performance optimizations
            "ALTER SYSTEM SET synchronous_commit = 'local';",
            "ALTER SYSTEM SET commit_delay = '100';",
            "ALTER SYSTEM SET commit_siblings = '10';",
        ]

        conn = await asyncpg.connect(connection_url)
        try:
            for setting in optimizations:
                try:
                    logger.info(f"Applying setting: {setting}")
                    await conn.execute(setting)
                except Exception as e:
                    logger.warning(f"Setting failed: {e}")

            # Reload configuration
            await conn.execute("SELECT pg_reload_conf();")
            logger.info("PostgreSQL configuration reloaded")

        finally:
            await conn.close()

    async def analyze_table_statistics(self, connection_url: str):
        """Update table statistics for query optimization."""
        tables = ["policy_generations", "stabilizer_executions", "syndrome_diagnoses"]

        conn = await asyncpg.connect(connection_url)
        try:
            for table in tables:
                logger.info(f"Analyzing table: {table}")
                await conn.execute(f"ANALYZE {table};")

            # Update global statistics
            await conn.execute("ANALYZE;")
            logger.info("Database statistics updated")

        finally:
            await conn.close()

    def get_pool_metrics(self) -> Dict[str, ConnectionPoolMetrics]:
        """Get current connection pool metrics."""
        return self.pool_metrics.copy()

    def get_query_metrics(self) -> Dict[str, QueryPerformanceMetrics]:
        """Get current query performance metrics."""
        return self.query_metrics.copy()

    def get_slow_queries(self, limit: int = 10) -> List[QueryPerformanceMetrics]:
        """Get slowest queries by average execution time."""
        sorted_queries = sorted(
            self.query_metrics.values(), key=lambda x: x.avg_time, reverse=True
        )
        return sorted_queries[:limit]

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        total_queries = sum(m.execution_count for m in self.query_metrics.values())
        total_time = sum(m.total_time for m in self.query_metrics.values())
        slow_queries = sum(m.slow_query_count for m in self.query_metrics.values())

        return {
            "total_queries": total_queries,
            "total_execution_time": total_time,
            "average_query_time": total_time / max(1, total_queries),
            "slow_query_count": slow_queries,
            "slow_query_percentage": (slow_queries / max(1, total_queries)) * 100,
            "query_types": {
                qtype: len(
                    [m for m in self.query_metrics.values() if m.query_type == qtype]
                )
                for qtype in ["SELECT", "INSERT", "UPDATE", "DELETE", "OTHER"]
            },
            "pool_metrics_count": len(self.pool_metrics),
            "timestamp": datetime.utcnow(),
        }

    async def cleanup(self):
        """Cleanup optimizer resources."""
        self.pool_metrics.clear()
        self.query_metrics.clear()
        self.connection_checkout_times.clear()
        logger.info("Database optimizer cleanup completed")
