"""
Monitoring and Telemetry for Gemini CLI
"""
# Constitutional Hash: cdd01ef066bc6cf2

import json
import logging
import os
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# OpenTelemetry imports (optional)
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
        OTLPMetricExporter,
    )
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

# Prometheus client (optional)
try:
    from prometheus_client import Counter, Gauge, Histogram, start_http_server

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class OperationMetrics:
    """Metrics for a single operation"""

    operation_id: str
    operation_type: str
    start_time: float
    end_time: float | None = None
    status: str = "running"
    error: str | None = None
    agent_id: str | None = None
    duration_ms: float | None = None

    def complete(self, status: str = "completed", error: str | None = None):
        """Mark operation as complete"""
        self.end_time = time.time()
        self.status = status
        self.error = error
        self.duration_ms = (self.end_time - self.start_time) * 1000


class GeminiCLIMonitoring:
    """Monitoring and telemetry system for Gemini CLI"""

    def __init__(self, config=None):
        self.config = config
        self.enabled = config.telemetry_enabled if config else True
        self.metrics_storage = {}
        self.active_operations = {}
        self.session_stats = {
            "start_time": time.time(),
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "agents_created": 0,
            "policies_verified": 0,
            "code_executions": 0,
        }

        # Initialize monitoring systems
        self._setup_prometheus()
        self._setup_opentelemetry()
        self._setup_file_logging()

        # Start background tasks
        self._start_metrics_collector()

    def _setup_prometheus(self):
        """Set up Prometheus metrics"""
        if not PROMETHEUS_AVAILABLE or not self.enabled:
            self.prometheus_enabled = False
            return

        try:
            # Define metrics
            self.operation_counter = Counter(
                "gemini_cli_operations_total",
                "Total number of operations",
                ["operation_type", "status", "agent_id"],
            )

            self.operation_duration = Histogram(
                "gemini_cli_operation_duration_seconds",
                "Operation duration in seconds",
                ["operation_type"],
            )

            self.active_operations_gauge = Gauge(
                "gemini_cli_active_operations", "Number of active operations"
            )

            self.session_metrics = Gauge(
                "gemini_cli_session_info", "Session information", ["metric_type"]
            )

            # Start Prometheus server
            prometheus_port = int(os.environ.get("PROMETHEUS_PORT", "9090"))
            start_http_server(prometheus_port)
            logger.info(f"Prometheus metrics server started on port {prometheus_port}")
            self.prometheus_enabled = True

        except Exception as e:
            logger.warning(f"Failed to setup Prometheus: {e}")
            self.prometheus_enabled = False

    def _setup_opentelemetry(self):
        """Set up OpenTelemetry"""
        if not OTEL_AVAILABLE or not self.enabled:
            self.otel_enabled = False
            return

        try:
            # Configure tracer
            self.tracer = trace.get_tracer(__name__)

            # Configure metrics
            otlp_exporter = OTLPMetricExporter(
                endpoint=os.environ.get(
                    "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"
                )
            )
            reader = PeriodicExportingMetricReader(otlp_exporter)
            provider = MeterProvider(metric_readers=[reader])
            self.meter = provider.get_meter(__name__)

            # Create instruments
            self.otel_operation_counter = self.meter.create_counter(
                name="gemini_cli_operations",
                description="Number of operations executed",
            )

            self.otel_operation_duration = self.meter.create_histogram(
                name="gemini_cli_operation_duration",
                description="Duration of operations in milliseconds",
            )

            logger.info("OpenTelemetry configured successfully")
            self.otel_enabled = True

        except Exception as e:
            logger.warning(f"Failed to setup OpenTelemetry: {e}")
            self.otel_enabled = False

    def _setup_file_logging(self):
        """Set up file-based metrics logging"""
        if not self.enabled:
            return

        try:
            # Create metrics directory
            metrics_dir = Path.home() / ".gemini_cli" / "metrics"
            metrics_dir.mkdir(parents=True, exist_ok=True)

            # Set up metrics file
            self.metrics_file = (
                metrics_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.jsonl"
            )

            logger.info(f"Metrics logging to: {self.metrics_file}")

        except Exception as e:
            logger.warning(f"Failed to setup file logging: {e}")
            self.metrics_file = None

    def _start_metrics_collector(self):
        """Start background metrics collection"""
        if not self.enabled:
            return

        def collect_metrics():
            while True:
                try:
                    self._collect_system_metrics()
                    time.sleep(60)  # Collect every minute
                except Exception as e:
                    logger.error(f"Error collecting metrics: {e}")
                    time.sleep(60)

        thread = threading.Thread(target=collect_metrics, daemon=True)
        thread.start()
        logger.info("Started background metrics collector")

    def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            import psutil

            # System metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            metrics = {
                "timestamp": datetime.now().isoformat(),
                "type": "system_metrics",
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / 1024 / 1024,
                "disk_usage_percent": disk.percent,
                "active_operations": len(self.active_operations),
            }

            # Update Prometheus metrics
            if self.prometheus_enabled:
                self.session_metrics.labels(metric_type="cpu_percent").set(cpu_percent)
                self.session_metrics.labels(metric_type="memory_percent").set(
                    memory.percent
                )
                self.active_operations_gauge.set(len(self.active_operations))

            # Log to file
            self._log_metrics(metrics)

        except ImportError:
            # psutil not available
            pass
        except Exception as e:
            logger.debug(f"Error collecting system metrics: {e}")

    def _log_metrics(self, metrics: dict[str, Any]):
        """Log metrics to file"""
        if not self.metrics_file:
            return

        try:
            with open(self.metrics_file, "a") as f:
                f.write(json.dumps(metrics) + "\n")
        except Exception as e:
            logger.debug(f"Error writing metrics to file: {e}")

    def start_operation(
        self, operation_id: str, operation_type: str, agent_id: str | None = None
    ) -> OperationMetrics:
        """Start tracking an operation"""
        if not self.enabled:
            return None

        metrics = OperationMetrics(
            operation_id=operation_id,
            operation_type=operation_type,
            start_time=time.time(),
            agent_id=agent_id,
        )

        self.active_operations[operation_id] = metrics
        self.session_stats["total_operations"] += 1

        # Update specific counters
        if operation_type == "agent_creation":
            self.session_stats["agents_created"] += 1
        elif operation_type == "policy_verification":
            self.session_stats["policies_verified"] += 1
        elif operation_type == "code_execution":
            self.session_stats["code_executions"] += 1

        logger.debug(f"Started tracking operation: {operation_id} ({operation_type})")
        return metrics

    def complete_operation(
        self, operation_id: str, status: str = "completed", error: str | None = None
    ):
        """Complete an operation"""
        if not self.enabled or operation_id not in self.active_operations:
            return

        metrics = self.active_operations.pop(operation_id)
        metrics.complete(status, error)

        # Update session stats
        if status == "completed":
            self.session_stats["successful_operations"] += 1
        else:
            self.session_stats["failed_operations"] += 1

        # Store completed metrics
        self.metrics_storage[operation_id] = metrics

        # Update Prometheus metrics
        if self.prometheus_enabled:
            self.operation_counter.labels(
                operation_type=metrics.operation_type,
                status=status,
                agent_id=metrics.agent_id or "unknown",
            ).inc()

            if metrics.duration_ms:
                self.operation_duration.labels(
                    operation_type=metrics.operation_type
                ).observe(metrics.duration_ms / 1000)

        # Update OpenTelemetry metrics
        if self.otel_enabled:
            self.otel_operation_counter.add(
                1, {"operation_type": metrics.operation_type, "status": status}
            )

            if metrics.duration_ms:
                self.otel_operation_duration.record(
                    metrics.duration_ms, {"operation_type": metrics.operation_type}
                )

        # Log metrics
        log_data = asdict(metrics)
        log_data["timestamp"] = datetime.now().isoformat()
        log_data["type"] = "operation_completed"
        self._log_metrics(log_data)

        logger.debug(f"Completed operation: {operation_id} ({status})")

    def get_operation_metrics(self, operation_id: str) -> OperationMetrics | None:
        """Get metrics for a specific operation"""
        return self.metrics_storage.get(operation_id) or self.active_operations.get(
            operation_id
        )

    def get_session_stats(self) -> dict[str, Any]:
        """Get current session statistics"""
        stats = self.session_stats.copy()
        stats["uptime_seconds"] = time.time() - stats["start_time"]
        stats["active_operations"] = len(self.active_operations)
        stats["success_rate"] = stats["successful_operations"] / max(
            stats["total_operations"], 1
        )
        return stats

    def get_performance_summary(
        self, operation_type: str | None = None
    ) -> dict[str, Any]:
        """Get performance summary"""
        completed_ops = [
            m
            for m in self.metrics_storage.values()
            if m.status == "completed"
            and (not operation_type or m.operation_type == operation_type)
        ]

        if not completed_ops:
            return {"error": "No completed operations found"}

        durations = [op.duration_ms for op in completed_ops if op.duration_ms]

        if not durations:
            return {"error": "No duration data available"}

        durations.sort()
        count = len(durations)

        return {
            "operation_type": operation_type or "all",
            "count": count,
            "avg_duration_ms": sum(durations) / count,
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "p50_duration_ms": durations[count // 2],
            "p95_duration_ms": durations[int(count * 0.95)],
            "p99_duration_ms": durations[int(count * 0.99)],
        }

    def export_metrics(self, format_type: str = "json") -> str:
        """Export metrics in specified format"""
        data = {
            "session_stats": self.get_session_stats(),
            "completed_operations": len(self.metrics_storage),
            "active_operations": len(self.active_operations),
            "export_timestamp": datetime.now().isoformat(),
        }

        if format_type == "json":
            return json.dumps(data, indent=2)
        return str(data)

    def cleanup(self):
        """Cleanup monitoring resources"""
        if self.enabled:
            logger.info("Cleaning up monitoring resources")
            # Could add cleanup for exporters, etc.


# Global monitoring instance
_monitoring_instance = None


def get_monitoring(config=None) -> GeminiCLIMonitoring:
    """Get global monitoring instance"""
    global _monitoring_instance
    if _monitoring_instance is None:
        _monitoring_instance = GeminiCLIMonitoring(config)
    return _monitoring_instance


def monitor_operation(operation_type: str, agent_id: str | None = None):
    """Decorator for monitoring operations"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            monitoring = get_monitoring()
            operation_id = f"{operation_type}_{int(time.time() * 1000)}"

            metrics = monitoring.start_operation(operation_id, operation_type, agent_id)

            try:
                result = func(*args, **kwargs)
                monitoring.complete_operation(operation_id, "completed")
                return result
            except Exception as e:
                monitoring.complete_operation(operation_id, "failed", str(e))
                raise

        return wrapper

    return decorator
