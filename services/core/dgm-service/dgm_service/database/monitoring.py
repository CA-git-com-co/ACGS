"""
DGM Database Monitoring and Alerting

Comprehensive database performance monitoring with real-time alerts,
metrics collection, and automated optimization recommendations.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from prometheus_client import Counter, Gauge, Histogram
from sqlalchemy import text

from .connection import get_database_manager

logger = logging.getLogger(__name__)


@dataclass
class DatabaseAlert:
    """Database alert definition."""

    name: str
    severity: str  # critical, warning, info
    message: str
    metric_value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False


@dataclass
class MonitoringConfig:
    """Configuration for database monitoring."""

    # Performance thresholds
    slow_query_threshold_ms: float = 200.0
    connection_utilization_threshold: float = 0.8
    cache_hit_ratio_threshold: float = 0.9
    lock_wait_threshold_ms: float = 1000.0

    # Storage thresholds
    disk_usage_threshold: float = 0.85
    table_bloat_threshold: float = 0.3
    index_bloat_threshold: float = 0.3

    # Monitoring intervals
    metrics_collection_interval: int = 60  # seconds
    alert_check_interval: int = 30  # seconds
    health_check_interval: int = 300  # seconds

    # Alert settings
    alert_cooldown_minutes: int = 15
    max_alerts_per_hour: int = 10


class DGMDatabaseMonitor:
    """
    Comprehensive database monitoring for DGM service.

    Features:
    - Real-time performance metrics collection
    - Automated alerting and notifications
    - Query performance analysis
    - Resource utilization monitoring
    - Constitutional compliance tracking
    """

    def __init__(self, config: MonitoringConfig | None = None):
        """Initialize database monitor."""
        self.config = config or MonitoringConfig()
        self.db_manager = None
        self.active_alerts: list[DatabaseAlert] = []
        self.alert_history: list[DatabaseAlert] = []
        self.monitoring_active = False

        # Prometheus metrics
        self._setup_prometheus_metrics()

    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for database monitoring."""
        self.db_connections_gauge = Gauge(
            "dgm_db_connections_total", "Total database connections", ["state"]
        )

        self.db_query_duration_histogram = Histogram(
            "dgm_db_query_duration_seconds",
            "Database query duration",
            ["operation", "table"],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
        )

        self.db_cache_hit_ratio_gauge = Gauge(
            "dgm_db_cache_hit_ratio", "Database cache hit ratio", ["table"]
        )

        self.db_table_size_gauge = Gauge(
            "dgm_db_table_size_bytes", "Database table size in bytes", ["table"]
        )

        self.db_slow_queries_counter = Counter(
            "dgm_db_slow_queries_total", "Total slow queries", ["table"]
        )

        self.db_alerts_counter = Counter(
            "dgm_db_alerts_total", "Total database alerts", ["severity", "alert_type"]
        )

    async def initialize(self):
        """Initialize database monitoring."""
        try:
            self.db_manager = get_database_manager()
            if not self.db_manager:
                raise RuntimeError("Database manager not available")

            # Create monitoring tables and views
            await self._create_monitoring_infrastructure()

            # Start monitoring tasks
            self.monitoring_active = True

            logger.info("✅ DGM database monitoring initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize database monitoring: {e}")
            raise

    async def start_monitoring(self):
        """Start continuous database monitoring."""
        if not self.monitoring_active:
            await self.initialize()

        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._metrics_collection_loop()),
            asyncio.create_task(self._alert_check_loop()),
            asyncio.create_task(self._health_check_loop()),
        ]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")
            self.monitoring_active = False

    async def stop_monitoring(self):
        """Stop database monitoring."""
        self.monitoring_active = False
        logger.info("🛑 Database monitoring stopped")

    async def _create_monitoring_infrastructure(self):
        """Create monitoring tables and views."""
        try:
            async with self.db_manager.get_session() as session:
                # Create monitoring schema
                await session.execute(
                    text("CREATE SCHEMA IF NOT EXISTS dgm_monitoring")
                )

                # Create query performance log table
                await session.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS dgm_monitoring.query_performance_log (
                        id SERIAL PRIMARY KEY,
                        query_hash VARCHAR(64) NOT NULL,
                        query_text TEXT,
                        execution_time_ms DECIMAL(10,3) NOT NULL,
                        rows_examined INTEGER,
                        rows_returned INTEGER,
                        table_name VARCHAR(255),
                        operation_type VARCHAR(50),
                        timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        constitutional_hash VARCHAR(64) DEFAULT 'cdd01ef066bc6cf2'
                    )
                """
                    )
                )

                # Create alert log table
                await session.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS dgm_monitoring.alert_log (
                        id SERIAL PRIMARY KEY,
                        alert_name VARCHAR(255) NOT NULL,
                        severity VARCHAR(20) NOT NULL,
                        message TEXT NOT NULL,
                        metric_value DECIMAL(15,6),
                        threshold_value DECIMAL(15,6),
                        triggered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        resolved_at TIMESTAMPTZ,
                        constitutional_hash VARCHAR(64) DEFAULT 'cdd01ef066bc6cf2'
                    )
                """
                    )
                )

                # Create performance summary view
                await session.execute(
                    text(
                        """
                    CREATE OR REPLACE VIEW dgm_monitoring.performance_summary AS
                    SELECT 
                        DATE_TRUNC('hour', timestamp) as hour,
                        table_name,
                        operation_type,
                        COUNT(*) as query_count,
                        AVG(execution_time_ms) as avg_execution_time,
                        MAX(execution_time_ms) as max_execution_time,
                        SUM(rows_examined) as total_rows_examined,
                        SUM(rows_returned) as total_rows_returned
                    FROM dgm_monitoring.query_performance_log
                    WHERE timestamp > NOW() - INTERVAL '24 hours'
                    GROUP BY DATE_TRUNC('hour', timestamp), table_name, operation_type
                    ORDER BY hour DESC, avg_execution_time DESC
                """
                    )
                )

                await session.commit()
                logger.info("✅ Monitoring infrastructure created")

        except Exception as e:
            logger.error(f"❌ Failed to create monitoring infrastructure: {e}")

    async def _metrics_collection_loop(self):
        """Continuous metrics collection loop."""
        while self.monitoring_active:
            try:
                await self._collect_database_metrics()
                await asyncio.sleep(self.config.metrics_collection_interval)
            except Exception as e:
                logger.error(f"❌ Metrics collection error: {e}")
                await asyncio.sleep(self.config.metrics_collection_interval)

    async def _alert_check_loop(self):
        """Continuous alert checking loop."""
        while self.monitoring_active:
            try:
                await self._check_alerts()
                await asyncio.sleep(self.config.alert_check_interval)
            except Exception as e:
                logger.error(f"❌ Alert check error: {e}")
                await asyncio.sleep(self.config.alert_check_interval)

    async def _health_check_loop(self):
        """Continuous health check loop."""
        while self.monitoring_active:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.config.health_check_interval)
            except Exception as e:
                logger.error(f"❌ Health check error: {e}")
                await asyncio.sleep(self.config.health_check_interval)

    async def _collect_database_metrics(self):
        """Collect comprehensive database metrics."""
        try:
            async with self.db_manager.get_session() as session:
                # Connection metrics
                result = await session.execute(
                    text(
                        """
                    SELECT 
                        state,
                        COUNT(*) as count
                    FROM pg_stat_activity 
                    GROUP BY state
                """
                    )
                )

                for row in result.fetchall():
                    self.db_connections_gauge.labels(state=row[0] or "unknown").set(
                        row[1]
                    )

                # Cache hit ratios
                result = await session.execute(
                    text(
                        """
                    SELECT 
                        schemaname,
                        tablename,
                        CASE 
                            WHEN heap_blks_hit + heap_blks_read = 0 THEN 0
                            ELSE heap_blks_hit::float / (heap_blks_hit + heap_blks_read)
                        END as cache_hit_ratio
                    FROM pg_statio_user_tables 
                    WHERE schemaname = 'dgm'
                """
                    )
                )

                for row in result.fetchall():
                    if row[2] is not None:
                        self.db_cache_hit_ratio_gauge.labels(table=row[1]).set(row[2])

                # Table sizes
                result = await session.execute(
                    text(
                        """
                    SELECT 
                        tablename,
                        pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                    FROM pg_tables 
                    WHERE schemaname = 'dgm'
                """
                    )
                )

                for row in result.fetchall():
                    self.db_table_size_gauge.labels(table=row[0]).set(row[1])

                # Slow queries
                result = await session.execute(
                    text(
                        rf"""
                    SELECT 
                        COALESCE(
                            CASE 
                                WHEN query LIKE '%dgm.%' THEN 
                                    SUBSTRING(query FROM 'dgm\.([a-zA-Z_]+)')
                                ELSE 'unknown'
                            END, 
                            'unknown'
                        ) as table_name,
                        COUNT(*) as slow_query_count
                    FROM pg_stat_statements 
                    WHERE mean_time > {self.config.slow_query_threshold_ms}
                    AND query LIKE '%dgm.%'
                    GROUP BY table_name
                """
                    )
                )

                for row in result.fetchall():
                    self.db_slow_queries_counter.labels(table=row[0]).inc(row[1])

        except Exception as e:
            logger.warning(f"⚠️ Metrics collection warning: {e}")

    async def _check_alerts(self):
        """Check for alert conditions."""
        try:
            async with self.db_manager.get_session() as session:
                alerts_to_trigger = []

                # Check slow query threshold
                result = await session.execute(
                    text(
                        f"""
                    SELECT 
                        COUNT(*) as slow_query_count,
                        AVG(mean_time) as avg_time
                    FROM pg_stat_statements 
                    WHERE mean_time > {self.config.slow_query_threshold_ms}
                    AND query LIKE '%dgm.%'
                """
                    )
                )

                row = result.fetchone()
                if row and row[0] > 10:  # More than 10 slow queries
                    alerts_to_trigger.append(
                        DatabaseAlert(
                            name="high_slow_query_count",
                            severity="warning",
                            message=f"High number of slow queries: {row[0]} queries averaging {row[1]:.2f}ms",
                            metric_value=row[0],
                            threshold=10,
                            timestamp=datetime.utcnow(),
                        )
                    )

                # Check connection utilization
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
                if row and row[0] > 0:
                    utilization = row[1] / row[0]
                    if utilization > self.config.connection_utilization_threshold:
                        alerts_to_trigger.append(
                            DatabaseAlert(
                                name="high_connection_utilization",
                                severity="warning",
                                message=f"High connection utilization: {utilization:.2%}",
                                metric_value=utilization,
                                threshold=self.config.connection_utilization_threshold,
                                timestamp=datetime.utcnow(),
                            )
                        )

                # Check cache hit ratios
                result = await session.execute(
                    text(
                        """
                    SELECT 
                        tablename,
                        CASE 
                            WHEN heap_blks_hit + heap_blks_read = 0 THEN 1
                            ELSE heap_blks_hit::float / (heap_blks_hit + heap_blks_read)
                        END as cache_hit_ratio
                    FROM pg_statio_user_tables 
                    WHERE schemaname = 'dgm'
                    AND heap_blks_hit + heap_blks_read > 1000
                """
                    )
                )

                for row in result.fetchall():
                    if row[1] < self.config.cache_hit_ratio_threshold:
                        alerts_to_trigger.append(
                            DatabaseAlert(
                                name="low_cache_hit_ratio",
                                severity="warning",
                                message=f"Low cache hit ratio for table {row[0]}: {row[1]:.2%}",
                                metric_value=row[1],
                                threshold=self.config.cache_hit_ratio_threshold,
                                timestamp=datetime.utcnow(),
                            )
                        )

                # Process alerts
                for alert in alerts_to_trigger:
                    await self._process_alert(alert)

        except Exception as e:
            logger.warning(f"⚠️ Alert check warning: {e}")

    async def _process_alert(self, alert: DatabaseAlert):
        """Process and log an alert."""
        try:
            # Check if this alert is already active (avoid spam)
            existing_alert = next(
                (
                    a
                    for a in self.active_alerts
                    if a.name == alert.name and not a.resolved
                ),
                None,
            )

            if existing_alert:
                # Update existing alert
                existing_alert.metric_value = alert.metric_value
                existing_alert.timestamp = alert.timestamp
            else:
                # New alert
                self.active_alerts.append(alert)
                self.alert_history.append(alert)

                # Log to database
                async with self.db_manager.get_session() as session:
                    await session.execute(
                        text(
                            """
                        INSERT INTO dgm_monitoring.alert_log 
                        (alert_name, severity, message, metric_value, threshold_value)
                        VALUES (:name, :severity, :message, :metric_value, :threshold)
                    """
                        ),
                        {
                            "name": alert.name,
                            "severity": alert.severity,
                            "message": alert.message,
                            "metric_value": alert.metric_value,
                            "threshold": alert.threshold,
                        },
                    )
                    await session.commit()

                # Update Prometheus metrics
                self.db_alerts_counter.labels(
                    severity=alert.severity, alert_type=alert.name
                ).inc()

                logger.warning(
                    f"🚨 Database Alert [{alert.severity.upper()}]: {alert.message}"
                )

        except Exception as e:
            logger.error(f"❌ Alert processing error: {e}")

    async def _perform_health_check(self):
        """Perform comprehensive database health check."""
        try:
            health_status = {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": "healthy",
                "checks": {},
            }

            async with self.db_manager.get_session() as session:
                # Connection test
                try:
                    await session.execute(text("SELECT 1"))
                    health_status["checks"]["connection"] = "healthy"
                except Exception as e:
                    health_status["checks"]["connection"] = f"unhealthy: {e}"
                    health_status["overall_status"] = "unhealthy"

                # Schema existence check
                try:
                    result = await session.execute(
                        text(
                            """
                        SELECT COUNT(*) FROM information_schema.schemata 
                        WHERE schema_name = 'dgm'
                    """
                        )
                    )
                    if result.scalar() > 0:
                        health_status["checks"]["schema"] = "healthy"
                    else:
                        health_status["checks"][
                            "schema"
                        ] = "unhealthy: DGM schema not found"
                        health_status["overall_status"] = "degraded"
                except Exception as e:
                    health_status["checks"]["schema"] = f"unhealthy: {e}"
                    health_status["overall_status"] = "unhealthy"

                # Table accessibility check
                dgm_tables = [
                    "dgm_archive",
                    "performance_metrics",
                    "bandit_states",
                    "constitutional_compliance_logs",
                    "improvement_workspaces",
                ]

                accessible_tables = 0
                for table in dgm_tables:
                    try:
                        await session.execute(
                            text(f"SELECT 1 FROM dgm.{table} LIMIT 1")
                        )
                        accessible_tables += 1
                    except Exception:
                        pass

                if accessible_tables == len(dgm_tables):
                    health_status["checks"]["tables"] = "healthy"
                elif accessible_tables > 0:
                    health_status["checks"][
                        "tables"
                    ] = f"degraded: {accessible_tables}/{len(dgm_tables)} tables accessible"
                    health_status["overall_status"] = "degraded"
                else:
                    health_status["checks"][
                        "tables"
                    ] = "unhealthy: no tables accessible"
                    health_status["overall_status"] = "unhealthy"

            # Log health status
            if health_status["overall_status"] != "healthy":
                logger.warning(
                    f"⚠️ Database health check: {health_status['overall_status']}"
                )

        except Exception as e:
            logger.error(f"❌ Health check error: {e}")

    async def get_monitoring_report(self) -> dict[str, Any]:
        """Generate comprehensive monitoring report."""
        try:
            report = {
                "generated_at": datetime.utcnow().isoformat(),
                "monitoring_status": "active" if self.monitoring_active else "inactive",
                "active_alerts": [
                    {
                        "name": alert.name,
                        "severity": alert.severity,
                        "message": alert.message,
                        "metric_value": alert.metric_value,
                        "threshold": alert.threshold,
                        "timestamp": alert.timestamp.isoformat(),
                    }
                    for alert in self.active_alerts
                    if not alert.resolved
                ],
                "alert_summary": {
                    "total_alerts": len(self.alert_history),
                    "active_alerts": len(
                        [a for a in self.active_alerts if not a.resolved]
                    ),
                    "critical_alerts": len(
                        [
                            a
                            for a in self.active_alerts
                            if a.severity == "critical" and not a.resolved
                        ]
                    ),
                    "warning_alerts": len(
                        [
                            a
                            for a in self.active_alerts
                            if a.severity == "warning" and not a.resolved
                        ]
                    ),
                },
                "constitutional_compliance": {
                    "hash": "cdd01ef066bc6cf2",
                    "monitoring_enabled": True,
                },
            }

            return report

        except Exception as e:
            logger.error(f"❌ Could not generate monitoring report: {e}")
            return {"error": str(e), "generated_at": datetime.utcnow().isoformat()}


# Global database monitor instance
_database_monitor: DGMDatabaseMonitor | None = None


def get_database_monitor() -> DGMDatabaseMonitor | None:
    """Get global database monitor instance."""
    return _database_monitor


async def initialize_database_monitor(
    config: MonitoringConfig | None = None,
) -> DGMDatabaseMonitor:
    """Initialize global database monitor."""
    global _database_monitor

    _database_monitor = DGMDatabaseMonitor(config)
    await _database_monitor.initialize()

    return _database_monitor
