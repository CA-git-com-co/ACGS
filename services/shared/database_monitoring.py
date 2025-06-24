"""
ACGS-1 Database Monitoring and Metrics
Phase 2 - Enterprise Scalability & Performance

Comprehensive monitoring for database connections, performance metrics,
and resilience components to achieve >99.9% availability targets.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .database_resilience import get_all_resilience_stats
from .enhanced_database_client import _database_clients

logger = logging.getLogger(__name__)


@dataclass
class DatabaseMetrics:
    """Database performance and health metrics."""

    # Connection metrics
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0

    # Performance metrics
    avg_query_time: float = 0.0
    slow_queries: int = 0
    total_queries: int = 0
    queries_per_second: float = 0.0

    # Resilience metrics
    circuit_breaker_trips: int = 0
    retry_attempts: int = 0
    successful_retries: int = 0

    # Health metrics
    uptime_percentage: float = 100.0
    last_health_check: Optional[float] = None
    health_check_failures: int = 0

    # Timestamp
    timestamp: float = field(default_factory=time.time)


class DatabaseMonitor:
    """Monitors database health and performance across all services."""

    def __init__(self, monitoring_interval: int = 30):
        self.monitoring_interval = monitoring_interval
        self.metrics_history: List[DatabaseMetrics] = []
        self.max_history_size = 1000  # Keep last 1000 metrics snapshots
        self.is_monitoring = False
        self._monitoring_task = None

        # Performance thresholds
        self.thresholds = {
            "max_query_time": 500.0,  # 500ms
            "max_connection_failures": 5,
            "min_uptime_percentage": 99.9,
            "max_circuit_breaker_trips": 3,
        }

        logger.info("Database monitor initialized")

    async def start_monitoring(self):
        """Start continuous database monitoring."""
        if self.is_monitoring:
            logger.warning("Database monitoring is already running")
            return

        self.is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Database monitoring started")

    async def stop_monitoring(self):
        """Stop database monitoring."""
        self.is_monitoring = False

        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("Database monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                # Collect metrics
                metrics = await self.collect_metrics()

                # Store metrics
                self._store_metrics(metrics)

                # Check thresholds and alert if necessary
                await self._check_thresholds(metrics)

                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def collect_metrics(self) -> DatabaseMetrics:
        """Collect comprehensive database metrics."""
        metrics = DatabaseMetrics()

        try:
            # Collect metrics from all database clients
            total_connections = 0
            active_connections = 0
            idle_connections = 0
            failed_connections = 0
            total_queries = 0
            query_times = []

            for service_name, client in _database_clients.items():
                try:
                    health_status = await client.health_check()

                    # Connection pool metrics
                    for pool_name, pool_info in health_status.get("connection_pools", {}).items():
                        if pool_info.get("status") == "healthy":
                            total_connections += pool_info.get("pool_size", 0)
                            active_connections += pool_info.get("checked_out", 0)
                            idle_connections += pool_info.get("free_connections", 0)
                        else:
                            failed_connections += 1

                except Exception as e:
                    logger.warning(f"Failed to collect metrics from {service_name}: {e}")
                    failed_connections += 1

            # Collect resilience metrics
            resilience_stats = get_all_resilience_stats()
            circuit_breaker_trips = 0
            retry_attempts = 0
            successful_retries = 0

            for service_stats in resilience_stats.values():
                cb_stats = service_stats.get("circuit_breaker", {})
                circuit_breaker_trips += cb_stats.get("state_changes", 0)
                # Note: retry metrics would need to be added to resilience framework

            # Update metrics
            metrics.total_connections = total_connections
            metrics.active_connections = active_connections
            metrics.idle_connections = idle_connections
            metrics.failed_connections = failed_connections
            metrics.circuit_breaker_trips = circuit_breaker_trips
            metrics.retry_attempts = retry_attempts
            metrics.successful_retries = successful_retries

            # Calculate uptime percentage
            if self.metrics_history:
                recent_metrics = self.metrics_history[-10:]  # Last 10 measurements
                healthy_count = sum(1 for m in recent_metrics if m.failed_connections == 0)
                metrics.uptime_percentage = (healthy_count / len(recent_metrics)) * 100

            metrics.last_health_check = time.time()

        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
            metrics.health_check_failures += 1

        return metrics

    def _store_metrics(self, metrics: DatabaseMetrics):
        """Store metrics in history."""
        self.metrics_history.append(metrics)

        # Trim history if too large
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size :]

    async def _check_thresholds(self, metrics: DatabaseMetrics):
        """Check metrics against thresholds and generate alerts."""
        alerts = []

        # Check query time threshold
        if metrics.avg_query_time > self.thresholds["max_query_time"]:
            alerts.append(
                {
                    "type": "performance",
                    "severity": "warning",
                    "message": f"Average query time ({metrics.avg_query_time:.2f}ms) exceeds threshold ({self.thresholds['max_query_time']}ms)",
                    "metric": "avg_query_time",
                    "value": metrics.avg_query_time,
                    "threshold": self.thresholds["max_query_time"],
                }
            )

        # Check connection failures
        if metrics.failed_connections > self.thresholds["max_connection_failures"]:
            alerts.append(
                {
                    "type": "availability",
                    "severity": "critical",
                    "message": f"Connection failures ({metrics.failed_connections}) exceed threshold ({self.thresholds['max_connection_failures']})",
                    "metric": "failed_connections",
                    "value": metrics.failed_connections,
                    "threshold": self.thresholds["max_connection_failures"],
                }
            )

        # Check uptime percentage
        if metrics.uptime_percentage < self.thresholds["min_uptime_percentage"]:
            alerts.append(
                {
                    "type": "availability",
                    "severity": "critical",
                    "message": f"Uptime percentage ({metrics.uptime_percentage:.2f}%) below threshold ({self.thresholds['min_uptime_percentage']}%)",
                    "metric": "uptime_percentage",
                    "value": metrics.uptime_percentage,
                    "threshold": self.thresholds["min_uptime_percentage"],
                }
            )

        # Check circuit breaker trips
        if metrics.circuit_breaker_trips > self.thresholds["max_circuit_breaker_trips"]:
            alerts.append(
                {
                    "type": "resilience",
                    "severity": "warning",
                    "message": f"Circuit breaker trips ({metrics.circuit_breaker_trips}) exceed threshold ({self.thresholds['max_circuit_breaker_trips']})",
                    "metric": "circuit_breaker_trips",
                    "value": metrics.circuit_breaker_trips,
                    "threshold": self.thresholds["max_circuit_breaker_trips"],
                }
            )

        # Log alerts
        for alert in alerts:
            if alert["severity"] == "critical":
                logger.error(f"CRITICAL ALERT: {alert['message']}")
            else:
                logger.warning(f"WARNING ALERT: {alert['message']}")

    def get_current_metrics(self) -> Optional[DatabaseMetrics]:
        """Get the most recent metrics."""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_metrics_summary(self, last_n: int = 10) -> Dict[str, Any]:
        """Get summary of recent metrics."""
        if not self.metrics_history:
            return {"status": "no_data"}

        recent_metrics = self.metrics_history[-last_n:]

        return {
            "status": ("healthy" if recent_metrics[-1].failed_connections == 0 else "degraded"),
            "total_measurements": len(recent_metrics),
            "avg_connections": sum(m.total_connections for m in recent_metrics)
            / len(recent_metrics),
            "avg_uptime": sum(m.uptime_percentage for m in recent_metrics) / len(recent_metrics),
            "total_failures": sum(m.failed_connections for m in recent_metrics),
            "total_circuit_breaker_trips": sum(m.circuit_breaker_trips for m in recent_metrics),
            "last_check": recent_metrics[-1].last_health_check,
            "monitoring_interval": self.monitoring_interval,
        }

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        if format == "json":
            metrics_data = []
            for metric in self.metrics_history:
                metrics_data.append(
                    {
                        "timestamp": metric.timestamp,
                        "total_connections": metric.total_connections,
                        "active_connections": metric.active_connections,
                        "idle_connections": metric.idle_connections,
                        "failed_connections": metric.failed_connections,
                        "avg_query_time": metric.avg_query_time,
                        "uptime_percentage": metric.uptime_percentage,
                        "circuit_breaker_trips": metric.circuit_breaker_trips,
                    }
                )

            return json.dumps(metrics_data, indent=2)

        else:
            raise ValueError(f"Unsupported export format: {format}")

    async def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        current_metrics = self.get_current_metrics()
        metrics_summary = self.get_metrics_summary()
        resilience_stats = get_all_resilience_stats()

        # Collect database client health
        client_health = {}
        for service_name, client in _database_clients.items():
            try:
                client_health[service_name] = await client.health_check()
            except Exception as e:
                client_health[service_name] = {"status": "error", "error": str(e)}

        return {
            "timestamp": time.time(),
            "overall_status": metrics_summary.get("status", "unknown"),
            "current_metrics": current_metrics.__dict__ if current_metrics else None,
            "metrics_summary": metrics_summary,
            "resilience_stats": resilience_stats,
            "client_health": client_health,
            "thresholds": self.thresholds,
            "monitoring_config": {
                "interval": self.monitoring_interval,
                "history_size": len(self.metrics_history),
                "max_history_size": self.max_history_size,
            },
        }


# Global database monitor instance
_database_monitor: Optional[DatabaseMonitor] = None


def get_database_monitor() -> DatabaseMonitor:
    """Get or create global database monitor."""
    global _database_monitor
    if _database_monitor is None:
        _database_monitor = DatabaseMonitor()
    return _database_monitor


async def start_database_monitoring():
    """Start global database monitoring."""
    monitor = get_database_monitor()
    await monitor.start_monitoring()


async def stop_database_monitoring():
    """Stop global database monitoring."""
    if _database_monitor:
        await _database_monitor.stop_monitoring()
