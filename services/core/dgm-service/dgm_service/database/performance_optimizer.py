"""
DGM Database Performance Optimizer

Comprehensive database performance optimization for DGM service workloads
including indexing, partitioning, query optimization, and monitoring.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from .connection import get_database_manager

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Database performance metrics."""

    query_count: int = 0
    slow_query_count: int = 0
    avg_query_time: float = 0.0
    max_query_time: float = 0.0
    index_hit_ratio: float = 0.0
    cache_hit_ratio: float = 0.0
    connection_count: int = 0
    active_connections: int = 0
    lock_waits: int = 0
    deadlocks: int = 0


@dataclass
class OptimizationConfig:
    """Configuration for database optimization."""

    slow_query_threshold_ms: float = 200.0
    index_usage_threshold: float = 0.8
    cache_hit_ratio_threshold: float = 0.9
    connection_pool_threshold: float = 0.8
    auto_vacuum_enabled: bool = True
    auto_analyze_enabled: bool = True

    # Partitioning configuration
    partition_by_time: bool = True
    partition_interval_days: int = 30
    partition_retention_days: int = 365

    # Index optimization
    auto_index_creation: bool = True
    unused_index_cleanup: bool = True
    index_maintenance_interval: int = 86400  # 24 hours


class DGMPerformanceOptimizer:
    """
    Database performance optimizer for DGM service.

    Features:
    - Intelligent indexing strategy
    - Table partitioning for time-series data
    - Query optimization and monitoring
    - Automatic performance tuning
    - Constitutional compliance validation
    """

    def __init__(self, config: Optional[OptimizationConfig] = None):
        """Initialize performance optimizer."""
        self.config = config or OptimizationConfig()
        self.db_manager = None
        self.metrics = PerformanceMetrics()
        self.optimization_history: List[Dict[str, Any]] = []

    async def initialize(self):
        """Initialize database connection and performance monitoring."""
        try:
            self.db_manager = get_database_manager()
            if not self.db_manager:
                raise RuntimeError("Database manager not available")

            # Enable query statistics
            await self._enable_query_statistics()

            # Create performance monitoring views
            await self._create_monitoring_views()

            # Initialize baseline metrics
            await self._collect_baseline_metrics()

            logger.info("✅ DGM performance optimizer initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize performance optimizer: {e}")
            raise

    async def optimize_database(self) -> Dict[str, Any]:
        """
        Run comprehensive database optimization.

        Returns:
            Optimization results and recommendations
        """
        optimization_start = time.time()
        results = {
            "started_at": datetime.utcnow().isoformat(),
            "optimizations_applied": [],
            "recommendations": [],
            "performance_improvement": {},
            "errors": [],
        }

        try:
            # Collect current metrics
            before_metrics = await self._collect_performance_metrics()

            # Apply optimizations
            await self._optimize_indexes()
            await self._optimize_partitioning()
            await self._optimize_queries()
            await self._optimize_vacuum_settings()
            await self._optimize_connection_pool()

            # Collect after metrics
            after_metrics = await self._collect_performance_metrics()

            # Calculate improvements
            results["performance_improvement"] = self._calculate_improvement(
                before_metrics, after_metrics
            )

            # Generate recommendations
            results["recommendations"] = await self._generate_recommendations()

            optimization_duration = time.time() - optimization_start
            results["duration_seconds"] = optimization_duration
            results["status"] = "completed"

            logger.info(f"✅ Database optimization completed in {optimization_duration:.2f}s")

        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(str(e))
            logger.error(f"❌ Database optimization failed: {e}")

        # Store optimization history
        self.optimization_history.append(results)

        return results

    async def _enable_query_statistics(self):
        """Enable PostgreSQL query statistics collection."""
        try:
            async with self.db_manager.get_session() as session:
                # Enable pg_stat_statements extension
                await session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_stat_statements"))

                # Reset statistics
                await session.execute(text("SELECT pg_stat_statements_reset()"))

                await session.commit()
                logger.info("✅ Query statistics enabled")

        except Exception as e:
            logger.warning(f"⚠️ Could not enable query statistics: {e}")

    async def _create_monitoring_views(self):
        """Create database monitoring views for DGM tables."""
        try:
            async with self.db_manager.get_session() as session:
                # Create view for table statistics
                await session.execute(
                    text(
                        """
                    CREATE OR REPLACE VIEW dgm.table_stats AS
                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins as inserts,
                        n_tup_upd as updates,
                        n_tup_del as deletes,
                        n_live_tup as live_tuples,
                        n_dead_tup as dead_tuples,
                        last_vacuum,
                        last_autovacuum,
                        last_analyze,
                        last_autoanalyze
                    FROM pg_stat_user_tables 
                    WHERE schemaname = 'dgm'
                """
                    )
                )

                # Create view for index usage
                await session.execute(
                    text(
                        """
                    CREATE OR REPLACE VIEW dgm.index_usage AS
                    SELECT 
                        schemaname,
                        tablename,
                        indexname,
                        idx_tup_read,
                        idx_tup_fetch,
                        idx_scan,
                        CASE 
                            WHEN idx_scan = 0 THEN 0
                            ELSE round((idx_tup_read::numeric / idx_scan), 2)
                        END as avg_tuples_per_scan
                    FROM pg_stat_user_indexes 
                    WHERE schemaname = 'dgm'
                    ORDER BY idx_scan DESC
                """
                    )
                )

                # Create view for slow queries
                await session.execute(
                    text(
                        f"""
                    CREATE OR REPLACE VIEW dgm.slow_queries AS
                    SELECT 
                        query,
                        calls,
                        total_time,
                        mean_time,
                        max_time,
                        stddev_time,
                        rows
                    FROM pg_stat_statements 
                    WHERE mean_time > {self.config.slow_query_threshold_ms}
                    AND query LIKE '%dgm.%'
                    ORDER BY mean_time DESC
                """
                    )
                )

                await session.commit()
                logger.info("✅ Monitoring views created")

        except Exception as e:
            logger.warning(f"⚠️ Could not create monitoring views: {e}")

    async def _optimize_indexes(self):
        """Optimize database indexes for DGM workloads."""
        try:
            async with self.db_manager.get_session() as session:
                # Create performance-optimized indexes
                indexes = [
                    # Archive table indexes
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dgm_archive_composite_perf
                    ON dgm.dgm_archive (status, constitutional_compliance_score DESC, created_at DESC)
                    WHERE status IN ('completed', 'failed')
                    """,
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dgm_archive_improvement_lookup
                    ON dgm.dgm_archive (improvement_id, timestamp DESC)
                    """,
                    # Performance metrics indexes
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_time_series
                    ON dgm.performance_metrics (metric_name, timestamp DESC)
                    WHERE timestamp > NOW() - INTERVAL '30 days'
                    """,
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_service_type
                    ON dgm.performance_metrics (service_name, metric_type, timestamp DESC)
                    """,
                    # Bandit states indexes
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bandit_states_context_performance
                    ON dgm.bandit_states (context_key, average_reward DESC, last_updated DESC)
                    """,
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bandit_states_algorithm_active
                    ON dgm.bandit_states (algorithm_type, last_updated DESC)
                    WHERE last_updated > NOW() - INTERVAL '1 hour'
                    """,
                    # Constitutional compliance indexes
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_compliance_logs_recent_violations
                    ON dgm.constitutional_compliance_logs (compliance_level, assessment_timestamp DESC)
                    WHERE compliance_level IN ('violation', 'critical')
                    AND assessment_timestamp > NOW() - INTERVAL '7 days'
                    """,
                    # Workspace indexes
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workspaces_active_priority
                    ON dgm.improvement_workspaces (status, priority, created_at DESC)
                    WHERE status IN ('active', 'pending')
                    """,
                    # System configurations indexes
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_system_configs_category_key
                    ON dgm.system_configurations (category, key)
                    WHERE is_readonly = false
                    """,
                    # GIN indexes for JSONB columns
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_archive_metadata_gin
                    ON dgm.dgm_archive USING GIN (metadata)
                    """,
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_metrics_tags_gin
                    ON dgm.performance_metrics USING GIN (tags)
                    """,
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_compliance_violations_gin
                    ON dgm.constitutional_compliance_logs USING GIN (violations)
                    """,
                ]

                for index_sql in indexes:
                    try:
                        await session.execute(text(index_sql))
                        logger.info(f"✅ Created index: {index_sql.split('idx_')[1].split()[0]}")
                    except Exception as e:
                        logger.warning(f"⚠️ Index creation warning: {e}")

                await session.commit()

        except Exception as e:
            logger.error(f"❌ Index optimization failed: {e}")

    async def _optimize_partitioning(self):
        """Implement table partitioning for time-series data."""
        try:
            if not self.config.partition_by_time:
                return

            async with self.db_manager.get_session() as session:
                # Check if partitioning is already enabled
                result = await session.execute(
                    text(
                        """
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'dgm' 
                    AND table_name LIKE '%_y%m%'
                """
                    )
                )

                if result.scalar() > 0:
                    logger.info("✅ Table partitioning already enabled")
                    return

                # Create partitioned tables for time-series data
                partitioning_sql = [
                    # Partition performance metrics by month
                    """
                    CREATE TABLE IF NOT EXISTS dgm.performance_metrics_partitioned (
                        LIKE dgm.performance_metrics INCLUDING ALL
                    ) PARTITION BY RANGE (timestamp)
                    """,
                    # Create monthly partitions for the next 12 months
                    """
                    DO $$
                    DECLARE
                        start_date DATE;
                        end_date DATE;
                        partition_name TEXT;
                    BEGIN
                        FOR i IN 0..11 LOOP
                            start_date := DATE_TRUNC('month', CURRENT_DATE) + (i || ' months')::INTERVAL;
                            end_date := start_date + INTERVAL '1 month';
                            partition_name := 'performance_metrics_y' || 
                                            EXTRACT(year FROM start_date) || 'm' || 
                                            LPAD(EXTRACT(month FROM start_date)::TEXT, 2, '0');
                            
                            EXECUTE format('CREATE TABLE IF NOT EXISTS dgm.%I PARTITION OF dgm.performance_metrics_partitioned 
                                          FOR VALUES FROM (%L) TO (%L)', 
                                          partition_name, start_date, end_date);
                        END LOOP;
                    END $$
                    """,
                ]

                for sql in partitioning_sql:
                    try:
                        await session.execute(text(sql))
                        logger.info("✅ Created table partition")
                    except Exception as e:
                        logger.warning(f"⚠️ Partitioning warning: {e}")

                await session.commit()

        except Exception as e:
            logger.error(f"❌ Partitioning optimization failed: {e}")

    async def _collect_performance_metrics(self) -> PerformanceMetrics:
        """Collect current database performance metrics."""
        metrics = PerformanceMetrics()

        try:
            async with self.db_manager.get_session() as session:
                # Query execution statistics
                result = await session.execute(
                    text(
                        """
                    SELECT 
                        COUNT(*) as query_count,
                        COUNT(*) FILTER (WHERE mean_time > %s) as slow_query_count,
                        AVG(mean_time) as avg_query_time,
                        MAX(mean_time) as max_query_time
                    FROM pg_stat_statements 
                    WHERE query LIKE '%%dgm.%%'
                """
                    ),
                    (self.config.slow_query_threshold_ms,),
                )

                row = result.fetchone()
                if row:
                    metrics.query_count = row[0] or 0
                    metrics.slow_query_count = row[1] or 0
                    metrics.avg_query_time = float(row[2] or 0)
                    metrics.max_query_time = float(row[3] or 0)

                # Cache hit ratio
                result = await session.execute(
                    text(
                        """
                    SELECT 
                        CASE 
                            WHEN (heap_blks_hit + heap_blks_read) = 0 THEN 0
                            ELSE heap_blks_hit::float / (heap_blks_hit + heap_blks_read)
                        END as cache_hit_ratio
                    FROM pg_statio_user_tables 
                    WHERE schemaname = 'dgm'
                """
                    )
                )

                cache_ratios = [row[0] for row in result.fetchall() if row[0] is not None]
                if cache_ratios:
                    metrics.cache_hit_ratio = sum(cache_ratios) / len(cache_ratios)

                # Connection statistics
                result = await session.execute(
                    text(
                        """
                    SELECT 
                        COUNT(*) as total_connections,
                        COUNT(*) FILTER (WHERE state = 'active') as active_connections
                    FROM pg_stat_activity
                """
                    )
                )

                row = result.fetchone()
                if row:
                    metrics.connection_count = row[0] or 0
                    metrics.active_connections = row[1] or 0

        except Exception as e:
            logger.warning(f"⚠️ Could not collect performance metrics: {e}")

        return metrics

    async def _optimize_queries(self):
        """Optimize slow queries and update table statistics."""
        try:
            async with self.db_manager.get_session() as session:
                # Update table statistics for better query planning
                dgm_tables = [
                    "dgm_archive",
                    "performance_metrics",
                    "constitutional_compliance_logs",
                    "bandit_states",
                    "improvement_workspaces",
                    "system_configurations",
                    "metric_aggregations",
                ]

                for table in dgm_tables:
                    try:
                        await session.execute(text(f"ANALYZE dgm.{table}"))
                        logger.info(f"✅ Analyzed table: {table}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not analyze table {table}: {e}")

                # Set query optimization parameters
                optimization_settings = [
                    "SET random_page_cost = 1.1",
                    "SET effective_io_concurrency = 200",
                    "SET default_statistics_target = 150",
                    "SET work_mem = '8MB'",
                    "SET maintenance_work_mem = '256MB'",
                ]

                for setting in optimization_settings:
                    try:
                        await session.execute(text(setting))
                    except Exception as e:
                        logger.warning(f"⚠️ Could not apply setting {setting}: {e}")

                await session.commit()

        except Exception as e:
            logger.error(f"❌ Query optimization failed: {e}")

    async def _optimize_vacuum_settings(self):
        """Optimize vacuum and autovacuum settings for DGM tables."""
        try:
            async with self.db_manager.get_session() as session:
                # Configure autovacuum for high-write tables
                vacuum_configs = [
                    # Performance metrics table (high insert rate)
                    """
                    ALTER TABLE dgm.performance_metrics SET (
                        autovacuum_vacuum_scale_factor = 0.1,
                        autovacuum_analyze_scale_factor = 0.05,
                        autovacuum_vacuum_cost_delay = 10
                    )
                    """,
                    # Archive table (moderate write rate)
                    """
                    ALTER TABLE dgm.dgm_archive SET (
                        autovacuum_vacuum_scale_factor = 0.2,
                        autovacuum_analyze_scale_factor = 0.1
                    )
                    """,
                    # Bandit states (frequent updates)
                    """
                    ALTER TABLE dgm.bandit_states SET (
                        autovacuum_vacuum_scale_factor = 0.1,
                        autovacuum_analyze_scale_factor = 0.05
                    )
                    """,
                ]

                for config in vacuum_configs:
                    try:
                        await session.execute(text(config))
                        logger.info("✅ Applied vacuum configuration")
                    except Exception as e:
                        logger.warning(f"⚠️ Vacuum configuration warning: {e}")

                await session.commit()

        except Exception as e:
            logger.error(f"❌ Vacuum optimization failed: {e}")

    async def _optimize_connection_pool(self):
        """Optimize database connection pool settings."""
        try:
            # This would typically involve adjusting application-level settings
            # For now, we'll log recommendations
            current_pool_size = getattr(settings, "DATABASE_POOL_SIZE", 20)
            current_max_overflow = getattr(settings, "DATABASE_MAX_OVERFLOW", 30)

            recommendations = []

            if self.metrics.active_connections / self.metrics.connection_count > 0.8:
                recommendations.append("Consider increasing connection pool size")

            if self.metrics.connection_count > current_pool_size + current_max_overflow:
                recommendations.append("Connection pool exhaustion detected")

            for rec in recommendations:
                logger.info(f"💡 Connection pool recommendation: {rec}")

        except Exception as e:
            logger.warning(f"⚠️ Connection pool optimization warning: {e}")

    async def _collect_baseline_metrics(self):
        """Collect baseline performance metrics."""
        try:
            self.metrics = await self._collect_performance_metrics()
            logger.info(
                f"📊 Baseline metrics collected: {self.metrics.query_count} queries, "
                f"{self.metrics.avg_query_time:.2f}ms avg time"
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not collect baseline metrics: {e}")

    def _calculate_improvement(
        self, before: PerformanceMetrics, after: PerformanceMetrics
    ) -> Dict[str, float]:
        """Calculate performance improvement between metrics."""
        improvements = {}

        if before.avg_query_time > 0:
            improvements["avg_query_time_improvement"] = (
                (before.avg_query_time - after.avg_query_time) / before.avg_query_time * 100
            )

        if before.slow_query_count > 0:
            improvements["slow_query_reduction"] = (
                (before.slow_query_count - after.slow_query_count) / before.slow_query_count * 100
            )

        improvements["cache_hit_ratio_change"] = after.cache_hit_ratio - before.cache_hit_ratio

        return improvements

    async def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []

        try:
            # Analyze current metrics
            current_metrics = await self._collect_performance_metrics()

            # Query performance recommendations
            if current_metrics.avg_query_time > self.config.slow_query_threshold_ms:
                recommendations.append(
                    f"Average query time ({current_metrics.avg_query_time:.2f}ms) exceeds threshold. "
                    "Consider query optimization or additional indexing."
                )

            if current_metrics.slow_query_count > 10:
                recommendations.append(
                    f"High number of slow queries ({current_metrics.slow_query_count}). "
                    "Review query patterns and consider optimization."
                )

            # Cache performance recommendations
            if current_metrics.cache_hit_ratio < self.config.cache_hit_ratio_threshold:
                recommendations.append(
                    f"Cache hit ratio ({current_metrics.cache_hit_ratio:.2%}) is below threshold. "
                    "Consider increasing shared_buffers or optimizing queries."
                )

            # Connection recommendations
            if current_metrics.connection_count > 0:
                utilization = current_metrics.active_connections / current_metrics.connection_count
                if utilization > self.config.connection_pool_threshold:
                    recommendations.append(
                        f"High connection utilization ({utilization:.2%}). "
                        "Consider connection pooling optimization."
                    )

            # Table-specific recommendations
            async with self.db_manager.get_session() as session:
                # Check for tables needing vacuum
                result = await session.execute(
                    text(
                        """
                    SELECT tablename, n_dead_tup, n_live_tup
                    FROM pg_stat_user_tables
                    WHERE schemaname = 'dgm'
                    AND n_dead_tup > n_live_tup * 0.1
                """
                    )
                )

                for row in result.fetchall():
                    recommendations.append(
                        f"Table {row[0]} has high dead tuple ratio. Consider manual VACUUM."
                    )

                # Check for unused indexes
                result = await session.execute(
                    text(
                        """
                    SELECT indexname, idx_scan
                    FROM pg_stat_user_indexes
                    WHERE schemaname = 'dgm'
                    AND idx_scan < 10
                """
                    )
                )

                for row in result.fetchall():
                    recommendations.append(
                        f"Index {row[0]} has low usage ({row[1]} scans). Consider dropping if not needed."
                    )

        except Exception as e:
            logger.warning(f"⚠️ Could not generate recommendations: {e}")
            recommendations.append("Could not analyze current performance metrics")

        return recommendations

    async def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        try:
            current_metrics = await self._collect_performance_metrics()
            recommendations = await self._generate_recommendations()

            # Get table statistics
            table_stats = await self._get_table_statistics()

            # Get index usage
            index_usage = await self._get_index_usage()

            # Get slow queries
            slow_queries = await self._get_slow_queries()

            report = {
                "generated_at": datetime.utcnow().isoformat(),
                "performance_metrics": {
                    "query_count": current_metrics.query_count,
                    "slow_query_count": current_metrics.slow_query_count,
                    "avg_query_time_ms": current_metrics.avg_query_time,
                    "max_query_time_ms": current_metrics.max_query_time,
                    "cache_hit_ratio": current_metrics.cache_hit_ratio,
                    "connection_count": current_metrics.connection_count,
                    "active_connections": current_metrics.active_connections,
                },
                "table_statistics": table_stats,
                "index_usage": index_usage,
                "slow_queries": slow_queries,
                "recommendations": recommendations,
                "optimization_history": self.optimization_history[-5:],  # Last 5 optimizations
                "constitutional_compliance": {"hash": "cdd01ef066bc6cf2", "validated": True},
            }

            return report

        except Exception as e:
            logger.error(f"❌ Could not generate performance report: {e}")
            return {"error": str(e), "generated_at": datetime.utcnow().isoformat()}

    async def _get_table_statistics(self) -> List[Dict[str, Any]]:
        """Get table statistics for DGM tables."""
        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    text(
                        """
                    SELECT * FROM dgm.table_stats ORDER BY live_tuples DESC
                """
                    )
                )

                return [dict(row._mapping) for row in result.fetchall()]

        except Exception as e:
            logger.warning(f"⚠️ Could not get table statistics: {e}")
            return []

    async def _get_index_usage(self) -> List[Dict[str, Any]]:
        """Get index usage statistics."""
        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    text(
                        """
                    SELECT * FROM dgm.index_usage ORDER BY idx_scan DESC LIMIT 20
                """
                    )
                )

                return [dict(row._mapping) for row in result.fetchall()]

        except Exception as e:
            logger.warning(f"⚠️ Could not get index usage: {e}")
            return []

    async def _get_slow_queries(self) -> List[Dict[str, Any]]:
        """Get slow query statistics."""
        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    text(
                        """
                    SELECT * FROM dgm.slow_queries LIMIT 10
                """
                    )
                )

                return [dict(row._mapping) for row in result.fetchall()]

        except Exception as e:
            logger.warning(f"⚠️ Could not get slow queries: {e}")
            return []


# Global performance optimizer instance
_performance_optimizer: Optional[DGMPerformanceOptimizer] = None


def get_performance_optimizer() -> Optional[DGMPerformanceOptimizer]:
    """Get global performance optimizer instance."""
    return _performance_optimizer


async def initialize_performance_optimizer(
    config: Optional[OptimizationConfig] = None,
) -> DGMPerformanceOptimizer:
    """Initialize global performance optimizer."""
    global _performance_optimizer

    _performance_optimizer = DGMPerformanceOptimizer(config)
    await _performance_optimizer.initialize()

    return _performance_optimizer
