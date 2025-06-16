"""
Advanced Database Performance Optimizer for ACGS-1 Phase A3
Implements enterprise-grade database optimizations for high-throughput governance operations
"""

import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil
import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from .database import async_engine

logger = structlog.get_logger(__name__)


class DatabasePerformanceOptimizer:
    """Advanced database performance optimizer for ACGS-1."""

    def __init__(self, database_url: str = None):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.database_url = database_url
        self.engine = async_engine if not database_url else create_async_engine(database_url)
        self.performance_metrics = {}
        self.slow_queries = []
        self.optimization_history = []

    async def initialize(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize the database optimizer."""
        try:
            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            logger.info("Database optimizer initialized successfully")
            return True
        except Exception as e:
            logger.error("Failed to initialize database optimizer", error=str(e))
            return False

    async def analyze_current_performance(self) -> Dict[str, Any]:
        """Analyze current database performance metrics."""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "connection_stats": {},
            "query_performance": {},
            "index_usage": {},
            "table_stats": {},
            "system_resources": {},
        }

        try:
            async with self.engine.begin() as conn:
                # Connection statistics
                conn_stats = await conn.execute(
                    text(
                        """
                    SELECT 
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections,
                        count(*) FILTER (WHERE state = 'idle') as idle_connections,
                        count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """
                    )
                )
                metrics["connection_stats"] = dict(conn_stats.fetchone()._mapping)

                # Query performance from pg_stat_statements (if available)
                try:
                    query_stats = await conn.execute(
                        text(
                            """
                        SELECT 
                            calls,
                            total_exec_time,
                            mean_exec_time,
                            max_exec_time,
                            rows,
                            100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                        FROM pg_stat_statements 
                        ORDER BY total_exec_time DESC 
                        LIMIT 10
                    """
                        )
                    )
                    metrics["query_performance"]["top_queries"] = [
                        dict(row._mapping) for row in query_stats.fetchall()
                    ]
                except Exception:
                    # pg_stat_statements not available
                    metrics["query_performance"]["top_queries"] = []

                # Index usage statistics
                index_stats = await conn.execute(
                    text(
                        """
                    SELECT 
                        schemaname,
                        tablename,
                        indexname,
                        idx_tup_read,
                        idx_tup_fetch,
                        idx_scan
                    FROM pg_stat_user_indexes 
                    ORDER BY idx_scan DESC 
                    LIMIT 20
                """
                    )
                )
                metrics["index_usage"] = [dict(row._mapping) for row in index_stats.fetchall()]

                # Table statistics
                table_stats = await conn.execute(
                    text(
                        """
                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins,
                        n_tup_upd,
                        n_tup_del,
                        n_live_tup,
                        n_dead_tup,
                        last_vacuum,
                        last_autovacuum,
                        last_analyze,
                        last_autoanalyze
                    FROM pg_stat_user_tables 
                    ORDER BY n_live_tup DESC
                """
                    )
                )
                metrics["table_stats"] = [dict(row._mapping) for row in table_stats.fetchall()]

                # Database size information
                db_size = await conn.execute(
                    text(
                        """
                    SELECT 
                        pg_size_pretty(pg_database_size(current_database())) as database_size,
                        pg_database_size(current_database()) as database_size_bytes
                """
                    )
                )
                metrics["database_size"] = dict(db_size.fetchone()._mapping)

        except Exception as e:
            logger.error("Error analyzing database performance", error=str(e))

        # System resource usage
        metrics["system_resources"] = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage("/").percent,
        }

        self.performance_metrics = metrics
        return metrics

    async def create_performance_indexes(self) -> Dict[str, Any]:
        """Create optimized indexes for ACGS-1 governance operations."""
        index_results = {"created": [], "failed": [], "skipped": []}

        # Define indexes for governance operations
        governance_indexes = [
            # User authentication and session management
            {
                "name": "idx_users_email_active",
                "table": "users",
                "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_active ON users(email) WHERE is_active = true",
            },
            {
                "name": "idx_users_username_active",
                "table": "users",
                "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username_active ON users(username) WHERE is_active = true",
            },
            {
                "name": "idx_users_role_active",
                "table": "users",
                "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role_active ON users(role, is_active)",
            },
            # Security events and audit logs
            {
                "name": "idx_security_events_user_timestamp",
                "table": "security_events",
                "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_security_events_user_timestamp ON security_events(user_id, timestamp DESC)",
            },
            {
                "name": "idx_security_events_event_type",
                "table": "security_events",
                "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_security_events_event_type ON security_events(event_type, timestamp DESC)",
            },
            {
                "name": "idx_audit_logs_resource_action",
                "table": "audit_logs",
                "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_resource_action ON audit_logs(resource_type, action, timestamp DESC)",
            },
            # Policy and governance operations
            {
                "name": "idx_policy_rules_name_active",
                "table": "policy_rules",
                "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policy_rules_name_active ON policy_rules(name) WHERE is_active = true",
            },
            {
                "name": "idx_policy_rules_category_priority",
                "table": "policy_rules",
                "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policy_rules_category_priority ON policy_rules(category, priority DESC) WHERE is_active = true",
            },
            # Constitutional principles and amendments
            {
                "name": "idx_principles_category_weight",
                "table": "principles",
                "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_principles_category_weight ON principles(category, priority_weight DESC) WHERE is_active = true",
            },
            {
                "name": "idx_ac_amendments_status_created",
                "table": "ac_amendments",
                "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ac_amendments_status_created ON ac_amendments(status, created_at DESC)",
            },
            # Multi-armed bandit optimization
            {
                "name": "idx_mab_arms_category_score",
                "table": "mab_arms",
                "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mab_arms_category_score ON mab_arms(category, composite_score DESC) WHERE is_active = true",
            },
            {
                "name": "idx_mab_results_arm_created",
                "table": "mab_results",
                "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mab_results_arm_created ON mab_results(arm_id, created_at DESC)",
            },
            # Performance optimization indexes
            {
                "name": "idx_users_created_at",
                "table": "users",
                "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created_at ON users(created_at DESC)",
            },
            {
                "name": "idx_security_events_ip_timestamp",
                "table": "security_events",
                "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_security_events_ip_timestamp ON security_events(ip_address, timestamp DESC)",
            },
        ]

        try:
            async with self.engine.begin() as conn:
                for index_def in governance_indexes:
                    try:
                        # Check if table exists first
                        table_check = await conn.execute(
                            text(
                                """
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables
                                WHERE table_name = :table_name
                            )
                        """
                            ),
                            {"table_name": index_def["table"]},
                        )

                        if not table_check.scalar():
                            index_results["skipped"].append(
                                {
                                    "name": index_def["name"],
                                    "reason": f"Table {index_def['table']} does not exist",
                                }
                            )
                            continue

                        # Create the index
                        await conn.execute(text(index_def["definition"]))
                        index_results["created"].append(index_def["name"])
                        logger.info(f"Created index: {index_def['name']}")

                    except Exception as e:
                        index_results["failed"].append({"name": index_def["name"], "error": str(e)})
                        logger.warning(f"Failed to create index {index_def['name']}", error=str(e))

        except Exception as e:
            logger.error("Error creating performance indexes", error=str(e))

        return index_results

    async def optimize_connection_pool(self) -> Dict[str, Any]:
        """Optimize database connection pool settings."""
        optimization_results = {
            "current_settings": {},
            "recommended_settings": {},
            "applied_changes": [],
        }

        try:
            async with self.engine.begin() as conn:
                # Get current PostgreSQL settings
                current_settings = await conn.execute(
                    text(
                        """
                    SELECT name, setting, unit, context 
                    FROM pg_settings 
                    WHERE name IN (
                        'max_connections',
                        'shared_buffers', 
                        'effective_cache_size',
                        'work_mem',
                        'maintenance_work_mem',
                        'checkpoint_completion_target',
                        'wal_buffers',
                        'default_statistics_target',
                        'random_page_cost',
                        'effective_io_concurrency'
                    )
                """
                    )
                )

                optimization_results["current_settings"] = {
                    row.name: {
                        "value": row.setting,
                        "unit": row.unit,
                        "context": row.context,
                    }
                    for row in current_settings.fetchall()
                }

                # Calculate recommended settings based on system resources
                memory_gb = psutil.virtual_memory().total / (1024**3)
                cpu_count = psutil.cpu_count()

                recommended = {
                    "max_connections": min(200, max(100, cpu_count * 25)),
                    "shared_buffers": f"{int(memory_gb * 0.25)}GB",
                    "effective_cache_size": f"{int(memory_gb * 0.75)}GB",
                    "work_mem": f"{max(4, int(memory_gb * 1024 / 200))}MB",
                    "maintenance_work_mem": f"{int(memory_gb * 0.1)}GB",
                    "checkpoint_completion_target": "0.9",
                    "wal_buffers": "32MB",
                    "default_statistics_target": "150",
                    "random_page_cost": "1.1",
                    "effective_io_concurrency": str(min(200, cpu_count * 50)),
                }

                optimization_results["recommended_settings"] = recommended

        except Exception as e:
            logger.error("Error optimizing connection pool", error=str(e))

        return optimization_results

    async def identify_slow_queries(self, threshold_ms: int = 1000) -> List[Dict[str, Any]]:
        """Identify and analyze slow queries."""
        slow_queries = []

        try:
            async with self.engine.begin() as conn:
                # Enable query logging if not already enabled
                await conn.execute(
                    text("SET log_min_duration_statement = :threshold"),
                    {"threshold": threshold_ms},
                )

                # Get slow queries from pg_stat_statements if available
                try:
                    query_stats = await conn.execute(
                        text(
                            """
                        SELECT
                            query,
                            calls,
                            total_exec_time,
                            mean_exec_time,
                            max_exec_time,
                            stddev_exec_time,
                            rows,
                            100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                        FROM pg_stat_statements
                        WHERE mean_exec_time > :threshold
                        ORDER BY total_exec_time DESC
                        LIMIT 20
                    """
                        ),
                        {"threshold": threshold_ms},
                    )

                    slow_queries = [dict(row._mapping) for row in query_stats.fetchall()]

                except Exception:
                    # pg_stat_statements not available, use alternative method
                    logger.warning("pg_stat_statements not available for slow query analysis")

        except Exception as e:
            logger.error("Error identifying slow queries", error=str(e))

        self.slow_queries = slow_queries
        return slow_queries

    async def vacuum_and_analyze(self) -> Dict[str, Any]:
        """Perform database maintenance operations."""
        maintenance_results = {
            "vacuum_results": [],
            "analyze_results": [],
            "reindex_results": [],
        }

        try:
            async with self.engine.begin() as conn:
                # Get list of user tables
                tables_query = await conn.execute(
                    text(
                        """
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                """
                    )
                )

                tables = [row.tablename for row in tables_query.fetchall()]

                # Vacuum and analyze each table
                for table in tables:
                    try:
                        # Vacuum - Note: Table names cannot be parameterized in VACUUM statements
                        # This is safe as table names come from pg_tables system catalog
                        await conn.execute(text(f"VACUUM ANALYZE {table}"))
                        maintenance_results["vacuum_results"].append(
                            {"table": table, "status": "success"}
                        )

                        logger.info(f"Vacuumed and analyzed table: {table}")

                    except Exception as e:
                        maintenance_results["vacuum_results"].append(
                            {"table": table, "status": "failed", "error": str(e)}
                        )

        except Exception as e:
            logger.error("Error during vacuum and analyze", error=str(e))

        return maintenance_results

    async def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "performance_metrics": await self.analyze_current_performance(),
            "slow_queries": await self.identify_slow_queries(),
            "recommendations": [],
            "optimization_score": 0,
        }

        # Generate recommendations based on analysis
        recommendations = []
        score = 100

        # Check connection usage
        conn_stats = report["performance_metrics"].get("connection_stats", {})
        if conn_stats.get("active_connections", 0) > 80:
            recommendations.append(
                {
                    "category": "connections",
                    "priority": "high",
                    "message": "High number of active connections detected",
                    "action": "Consider connection pooling optimization",
                }
            )
            score -= 15

        # Check for slow queries
        if len(report["slow_queries"]) > 5:
            recommendations.append(
                {
                    "category": "queries",
                    "priority": "medium",
                    "message": f"Found {len(report['slow_queries'])} slow queries",
                    "action": "Review and optimize slow queries",
                }
            )
            score -= 10

        # Check index usage
        index_usage = report["performance_metrics"].get("index_usage", [])
        unused_indexes = [idx for idx in index_usage if idx.get("idx_scan", 0) == 0]
        if len(unused_indexes) > 3:
            recommendations.append(
                {
                    "category": "indexes",
                    "priority": "low",
                    "message": f"Found {len(unused_indexes)} unused indexes",
                    "action": "Consider removing unused indexes",
                }
            )
            score -= 5

        report["recommendations"] = recommendations
        report["optimization_score"] = max(0, score)

        return report

    @asynccontextmanager
    async def performance_monitoring_session(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Context manager for performance monitoring during operations."""
        start_time = time.time()
        start_metrics = await self.analyze_current_performance()

        try:
            yield
        finally:
            end_time = time.time()
            end_metrics = await self.analyze_current_performance()

            # Log performance delta
            duration = end_time - start_time
            logger.info(
                "Performance monitoring session completed",
                duration_seconds=duration,
                start_connections=start_metrics.get("connection_stats", {}).get(
                    "active_connections", 0
                ),
                end_connections=end_metrics.get("connection_stats", {}).get(
                    "active_connections", 0
                ),
            )


# Global optimizer instance
_db_optimizer: Optional[DatabasePerformanceOptimizer] = None


async def get_database_optimizer() -> DatabasePerformanceOptimizer:
    """Get or create database optimizer instance."""
    global _db_optimizer
    if _db_optimizer is None:
        _db_optimizer = DatabasePerformanceOptimizer()
        await _db_optimizer.initialize()
    return _db_optimizer


# Performance monitoring decorators
def monitor_db_performance(operation_name: str):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Decorator to monitor database operation performance."""

    def decorator(func):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        if asyncio.iscoroutinefunction(func):

            async def async_wrapper(*args, **kwargs):
                # requires: Valid input parameters
                # ensures: Correct function execution
                # sha256: func_hash
                optimizer = await get_database_optimizer()
                async with optimizer.performance_monitoring_session():
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        duration = time.time() - start_time
                        logger.info(
                            f"Database operation completed: {operation_name}",
                            duration_seconds=duration,
                            success=True,
                        )
                        return result
                    except Exception as e:
                        duration = time.time() - start_time
                        logger.error(
                            f"Database operation failed: {operation_name}",
                            duration_seconds=duration,
                            error=str(e),
                            success=False,
                        )
                        raise

            return async_wrapper
        else:

            def sync_wrapper(*args, **kwargs):
                # requires: Valid input parameters
                # ensures: Correct function execution
                # sha256: func_hash
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    logger.info(
                        f"Database operation completed: {operation_name}",
                        duration_seconds=duration,
                        success=True,
                    )
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    logger.error(
                        f"Database operation failed: {operation_name}",
                        duration_seconds=duration,
                        error=str(e),
                        success=False,
                    )
                    raise

            return sync_wrapper

    return decorator
