"""
Dashboard Metrics Aggregation for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive dashboard data aggregation for monitoring and observability.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import psutil
from shared.performance.caching import get_cache_manager
from shared.performance.connection_pool import get_connection_pool_registry
from shared.resilience.circuit_breaker import get_circuit_breaker_registry

from .alerts import AlertSeverity, get_alert_manager
from .health_checks import get_health_registry
from .metrics import get_metrics_collector

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System-level metrics for dashboard."""

    timestamp: datetime = field(default_factory=datetime.utcnow)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    memory_total_gb: float = 0.0
    memory_available_gb: float = 0.0
    disk_usage: float = 0.0
    disk_total_gb: float = 0.0
    disk_free_gb: float = 0.0
    load_average: tuple[float, float, float] = (0.0, 0.0, 0.0)
    uptime_seconds: float = 0.0
    process_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "memory_total_gb": self.memory_total_gb,
            "memory_available_gb": self.memory_available_gb,
            "disk_usage": self.disk_usage,
            "disk_total_gb": self.disk_total_gb,
            "disk_free_gb": self.disk_free_gb,
            "load_average": list(self.load_average),
            "uptime_seconds": self.uptime_seconds,
            "process_count": self.process_count,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


@dataclass
class PerformanceMetrics:
    """Performance metrics for dashboard."""

    timestamp: datetime = field(default_factory=datetime.utcnow)
    http_requests_per_second: float = 0.0
    http_avg_response_time: float = 0.0
    http_p95_response_time: float = 0.0
    http_error_rate: float = 0.0
    database_queries_per_second: float = 0.0
    database_avg_query_time: float = 0.0
    database_connection_pool_usage: float = 0.0
    cache_hit_rate: float = 0.0
    cache_operations_per_second: float = 0.0
    circuit_breaker_open_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "http_requests_per_second": self.http_requests_per_second,
            "http_avg_response_time": self.http_avg_response_time,
            "http_p95_response_time": self.http_p95_response_time,
            "http_error_rate": self.http_error_rate,
            "database_queries_per_second": self.database_queries_per_second,
            "database_avg_query_time": self.database_avg_query_time,
            "database_connection_pool_usage": self.database_connection_pool_usage,
            "cache_hit_rate": self.cache_hit_rate,
            "cache_operations_per_second": self.cache_operations_per_second,
            "circuit_breaker_open_count": self.circuit_breaker_open_count,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


@dataclass
class BusinessMetrics:
    """Business-level metrics for dashboard."""

    timestamp: datetime = field(default_factory=datetime.utcnow)
    constitutional_validations_per_hour: float = 0.0
    constitutional_compliance_rate: float = 100.0
    governance_decisions_per_hour: float = 0.0
    policy_evaluations_per_hour: float = 0.0
    multi_agent_coordination_sessions: int = 0
    worker_agent_utilization: float = 0.0
    consensus_operations_per_hour: float = 0.0
    audit_trail_entries_per_hour: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "constitutional_validations_per_hour": self.constitutional_validations_per_hour,
            "constitutional_compliance_rate": self.constitutional_compliance_rate,
            "governance_decisions_per_hour": self.governance_decisions_per_hour,
            "policy_evaluations_per_hour": self.policy_evaluations_per_hour,
            "multi_agent_coordination_sessions": self.multi_agent_coordination_sessions,
            "worker_agent_utilization": self.worker_agent_utilization,
            "consensus_operations_per_hour": self.consensus_operations_per_hour,
            "audit_trail_entries_per_hour": self.audit_trail_entries_per_hour,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


@dataclass
class HealthSummary:
    """Health status summary for dashboard."""

    timestamp: datetime = field(default_factory=datetime.utcnow)
    overall_status: str = "unknown"
    healthy_checks: int = 0
    degraded_checks: int = 0
    unhealthy_checks: int = 0
    unknown_checks: int = 0
    total_checks: int = 0
    critical_failures: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "overall_status": self.overall_status,
            "healthy_checks": self.healthy_checks,
            "degraded_checks": self.degraded_checks,
            "unhealthy_checks": self.unhealthy_checks,
            "unknown_checks": self.unknown_checks,
            "total_checks": self.total_checks,
            "critical_failures": self.critical_failures,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


@dataclass
class AlertSummary:
    """Alert summary for dashboard."""

    timestamp: datetime = field(default_factory=datetime.utcnow)
    active_alerts: int = 0
    critical_alerts: int = 0
    error_alerts: int = 0
    warning_alerts: int = 0
    info_alerts: int = 0
    recent_alerts: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "active_alerts": self.active_alerts,
            "critical_alerts": self.critical_alerts,
            "error_alerts": self.error_alerts,
            "warning_alerts": self.warning_alerts,
            "info_alerts": self.info_alerts,
            "recent_alerts": self.recent_alerts,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


class DashboardMetrics:
    """Central dashboard metrics aggregation system."""

    def __init__(self, name: str = "acgs_dashboard"):
        self.name = name
        self._metrics_history: list[tuple[datetime, dict[str, Any]]] = []
        self._max_history_size = 1000
        self._last_collection_time = datetime.utcnow()

        # Component references
        self._metrics_collector = get_metrics_collector()
        self._health_registry = get_health_registry()
        self._alert_manager = get_alert_manager()
        self._cache_manager = get_cache_manager()
        self._pool_registry = get_connection_pool_registry()
        self._circuit_breaker_registry = get_circuit_breaker_registry()

    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect system-level metrics."""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)

            # Memory info
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            memory_total_gb = memory.total / (1024**3)
            memory_available_gb = memory.available / (1024**3)

            # Disk info
            disk = psutil.disk_usage("/")
            disk_usage = disk.percent
            disk_total_gb = disk.total / (1024**3)
            disk_free_gb = disk.free / (1024**3)

            # Load average (Unix-like systems)
            try:
                load_average = psutil.getloadavg()
            except AttributeError:
                load_average = (0.0, 0.0, 0.0)  # Windows doesn't have load average

            # Boot time and uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time

            # Process count
            process_count = len(psutil.pids())

            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                memory_total_gb=memory_total_gb,
                memory_available_gb=memory_available_gb,
                disk_usage=disk_usage,
                disk_total_gb=disk_total_gb,
                disk_free_gb=disk_free_gb,
                load_average=load_average,
                uptime_seconds=uptime_seconds,
                process_count=process_count,
            )

        except Exception as e:
            logger.exception(f"Error collecting system metrics: {e}")
            return SystemMetrics()

    async def collect_performance_metrics(self) -> PerformanceMetrics:
        """Collect performance metrics."""
        try:
            # Get current metrics
            metrics = self._metrics_collector.collect_all()
            metrics_dict = {m.name: m.value for m in metrics}

            # HTTP metrics
            http_requests_total = metrics_dict.get("http_requests_total", 0)
            http_request_duration = metrics_dict.get("http_request_duration", {})

            # Calculate rates (simplified - in production, use proper time series)
            now = datetime.utcnow()
            time_diff = (now - self._last_collection_time).total_seconds()
            time_diff = max(time_diff, 1)  # Avoid division by zero

            http_requests_per_second = (
                http_requests_total / time_diff
                if isinstance(http_requests_total, (int, float))
                else 0
            )

            # Extract HTTP timing info
            if isinstance(http_request_duration, dict):
                http_avg_response_time = http_request_duration.get("average", 0)
                percentiles = http_request_duration.get("percentiles", {})
                http_p95_response_time = percentiles.get("p95", 0)
            else:
                http_avg_response_time = 0
                http_p95_response_time = 0

            # Database metrics
            database_queries_total = metrics_dict.get("database_queries_total", 0)
            database_query_duration = metrics_dict.get("database_query_duration", {})

            database_queries_per_second = (
                database_queries_total / time_diff
                if isinstance(database_queries_total, (int, float))
                else 0
            )

            if isinstance(database_query_duration, dict):
                database_avg_query_time = database_query_duration.get("average", 0)
            else:
                database_avg_query_time = 0

            # Connection pool usage
            pool_status = await self._pool_registry.get_global_status()
            database_connection_pool_usage = 0
            if "pools" in pool_status:
                for pool_info in pool_status["pools"].values():
                    if isinstance(pool_info, dict) and "metrics" in pool_info:
                        pool_metrics = pool_info["metrics"]
                        utilization = pool_metrics.get("utilization_rate", 0)
                        database_connection_pool_usage = max(
                            database_connection_pool_usage, utilization
                        )

            # Cache metrics
            cache_hits = metrics_dict.get("cache_hits_total", 0)
            cache_misses = metrics_dict.get("cache_misses_total", 0)
            total_cache_ops = cache_hits + cache_misses
            cache_hit_rate = (
                cache_hits / max(total_cache_ops, 1)
                if isinstance(cache_hits, (int, float))
                and isinstance(cache_misses, (int, float))
                else 0
            )
            cache_operations_per_second = (
                total_cache_ops / time_diff
                if isinstance(total_cache_ops, (int, float))
                else 0
            )

            # Circuit breaker status
            cb_health = await self._circuit_breaker_registry.health_check()
            circuit_breaker_open_count = cb_health.get("open_breakers", 0)

            return PerformanceMetrics(
                http_requests_per_second=http_requests_per_second,
                http_avg_response_time=http_avg_response_time,
                http_p95_response_time=http_p95_response_time,
                http_error_rate=0,  # TODO: Calculate from error metrics
                database_queries_per_second=database_queries_per_second,
                database_avg_query_time=database_avg_query_time,
                database_connection_pool_usage=database_connection_pool_usage,
                cache_hit_rate=cache_hit_rate,
                cache_operations_per_second=cache_operations_per_second,
                circuit_breaker_open_count=circuit_breaker_open_count,
            )

        except Exception as e:
            logger.exception(f"Error collecting performance metrics: {e}")
            return PerformanceMetrics()

    async def collect_business_metrics(self) -> BusinessMetrics:
        """Collect business-level metrics."""
        try:
            # Get current metrics
            metrics = self._metrics_collector.collect_all()
            metrics_dict = {m.name: m.value for m in metrics}

            # Calculate rates (simplified)
            now = datetime.utcnow()
            time_diff_hours = (now - self._last_collection_time).total_seconds() / 3600
            time_diff_hours = max(time_diff_hours, 1 / 3600)  # At least 1 second

            # Constitutional metrics
            constitutional_validations = metrics_dict.get(
                "constitutional_validations_total", 0
            )
            constitutional_violations = metrics_dict.get(
                "constitutional_violations_total", 0
            )

            constitutional_validations_per_hour = (
                constitutional_validations / time_diff_hours
                if isinstance(constitutional_validations, (int, float))
                else 0
            )

            # Calculate compliance rate
            total_constitutional_checks = (
                constitutional_validations + constitutional_violations
            )
            if (
                isinstance(constitutional_validations, (int, float))
                and isinstance(constitutional_violations, (int, float))
                and total_constitutional_checks > 0
            ):
                constitutional_compliance_rate = (
                    constitutional_validations / total_constitutional_checks
                ) * 100
            else:
                constitutional_compliance_rate = 100.0

            # Governance metrics (placeholder - would come from actual services)
            governance_decisions_per_hour = 0
            policy_evaluations_per_hour = 0
            multi_agent_coordination_sessions = 0
            worker_agent_utilization = 0
            consensus_operations_per_hour = 0
            audit_trail_entries_per_hour = 0

            return BusinessMetrics(
                constitutional_validations_per_hour=constitutional_validations_per_hour,
                constitutional_compliance_rate=constitutional_compliance_rate,
                governance_decisions_per_hour=governance_decisions_per_hour,
                policy_evaluations_per_hour=policy_evaluations_per_hour,
                multi_agent_coordination_sessions=multi_agent_coordination_sessions,
                worker_agent_utilization=worker_agent_utilization,
                consensus_operations_per_hour=consensus_operations_per_hour,
                audit_trail_entries_per_hour=audit_trail_entries_per_hour,
            )

        except Exception as e:
            logger.exception(f"Error collecting business metrics: {e}")
            return BusinessMetrics()

    async def collect_health_summary(self) -> HealthSummary:
        """Collect health status summary."""
        try:
            health_data = await self._health_registry.get_overall_health()

            overall_status = health_data.get("status", "unknown")
            summary = health_data.get("summary", {})

            healthy_checks = summary.get("healthy", 0)
            degraded_checks = summary.get("degraded", 0)
            unhealthy_checks = summary.get("unhealthy", 0)
            unknown_checks = summary.get("unknown", 0)
            total_checks = summary.get("total_checks", 0)

            # Find critical failures
            checks = health_data.get("checks", [])
            critical_failures = [
                check.get("name", "unknown")
                for check in checks
                if check.get("status") == "unhealthy"
            ]

            return HealthSummary(
                overall_status=overall_status,
                healthy_checks=healthy_checks,
                degraded_checks=degraded_checks,
                unhealthy_checks=unhealthy_checks,
                unknown_checks=unknown_checks,
                total_checks=total_checks,
                critical_failures=critical_failures,
            )

        except Exception as e:
            logger.exception(f"Error collecting health summary: {e}")
            return HealthSummary()

    async def collect_alert_summary(self) -> AlertSummary:
        """Collect alert summary."""
        try:
            active_alerts = self._alert_manager.get_active_alerts()

            # Count by severity
            critical_alerts = sum(
                1 for a in active_alerts if a.severity == AlertSeverity.CRITICAL
            )
            error_alerts = sum(
                1 for a in active_alerts if a.severity == AlertSeverity.ERROR
            )
            warning_alerts = sum(
                1 for a in active_alerts if a.severity == AlertSeverity.WARNING
            )
            info_alerts = sum(
                1 for a in active_alerts if a.severity == AlertSeverity.INFO
            )

            # Get recent alerts (last 10)
            alert_history = self._alert_manager.get_alert_history(10)
            recent_alerts = [
                {
                    "name": alert.name,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "status": alert.status.value,
                }
                for alert in alert_history[-10:]
            ]

            return AlertSummary(
                active_alerts=len(active_alerts),
                critical_alerts=critical_alerts,
                error_alerts=error_alerts,
                warning_alerts=warning_alerts,
                info_alerts=info_alerts,
                recent_alerts=recent_alerts,
            )

        except Exception as e:
            logger.exception(f"Error collecting alert summary: {e}")
            return AlertSummary()

    async def collect_all_metrics(self) -> dict[str, Any]:
        """Collect all dashboard metrics."""
        try:
            # Collect all metric types in parallel
            system_task = self.collect_system_metrics()
            performance_task = self.collect_performance_metrics()
            business_task = self.collect_business_metrics()
            health_task = self.collect_health_summary()
            alert_task = self.collect_alert_summary()

            (
                system_metrics,
                performance_metrics,
                business_metrics,
                health_summary,
                alert_summary,
            ) = await asyncio.gather(
                system_task, performance_task, business_task, health_task, alert_task
            )

            # Combine all metrics
            dashboard_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "system": system_metrics.to_dict(),
                "performance": performance_metrics.to_dict(),
                "business": business_metrics.to_dict(),
                "health": health_summary.to_dict(),
                "alerts": alert_summary.to_dict(),
                "constitutional_hash": "cdd01ef066bc6cf2",
            }

            # Store in history
            self._store_metrics_history(dashboard_data)
            self._last_collection_time = datetime.utcnow()

            return dashboard_data

        except Exception as e:
            logger.exception(f"Error collecting dashboard metrics: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "constitutional_hash": "cdd01ef066bc6cf2",
            }

    def _store_metrics_history(self, metrics: dict[str, Any]) -> None:
        """Store metrics in history for trending."""
        timestamp = datetime.utcnow()
        self._metrics_history.append((timestamp, metrics))

        # Trim history if too large
        if len(self._metrics_history) > self._max_history_size:
            self._metrics_history = self._metrics_history[-self._max_history_size :]

    def get_metrics_history(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get metrics history for specified hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        return [
            metrics
            for timestamp, metrics in self._metrics_history
            if timestamp >= cutoff_time
        ]

    def get_dashboard_summary(self) -> dict[str, Any]:
        """Get dashboard summary information."""
        return {
            "dashboard_name": self.name,
            "history_size": len(self._metrics_history),
            "last_collection": self._last_collection_time.isoformat(),
            "max_history_size": self._max_history_size,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


# Global dashboard metrics instance
_global_dashboard = DashboardMetrics()


def get_dashboard_metrics() -> DashboardMetrics:
    """Get the global dashboard metrics instance."""
    return _global_dashboard


async def get_dashboard_data() -> dict[str, Any]:
    """Convenience function to get current dashboard data."""
    return await _global_dashboard.collect_all_metrics()


# Real-time dashboard endpoint helper
class DashboardWebSocketHandler:
    """WebSocket handler for real-time dashboard updates."""

    def __init__(self, update_interval: float = 5.0):
        self.update_interval = update_interval
        self._dashboard = get_dashboard_metrics()
        self._websockets: list[Any] = []  # WebSocket connections

    def add_websocket(self, websocket: Any) -> None:
        """Add WebSocket connection."""
        self._websockets.append(websocket)

    def remove_websocket(self, websocket: Any) -> None:
        """Remove WebSocket connection."""
        if websocket in self._websockets:
            self._websockets.remove(websocket)

    async def broadcast_updates(self) -> None:
        """Broadcast dashboard updates to all connected WebSockets."""
        while True:
            try:
                # Collect dashboard data
                dashboard_data = await self._dashboard.collect_all_metrics()

                # Broadcast to all connected WebSockets
                if self._websockets:
                    import json

                    message = json.dumps(dashboard_data)

                    disconnected = []
                    for websocket in self._websockets:
                        try:
                            await websocket.send_text(message)
                        except Exception:
                            disconnected.append(websocket)

                    # Remove disconnected WebSockets
                    for ws in disconnected:
                        self.remove_websocket(ws)

                # Wait for next update
                await asyncio.sleep(self.update_interval)

            except Exception as e:
                logger.exception(f"Error broadcasting dashboard updates: {e}")
                await asyncio.sleep(self.update_interval)
