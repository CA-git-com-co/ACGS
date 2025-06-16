"""
Metrics Collector for ACGS-1 Advanced Governance Workflows.

This module implements comprehensive metrics collection with Prometheus
integration, OpenTelemetry tracing, and performance analytics.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    from prometheus_client import Counter, Histogram, Gauge, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = Histogram = Gauge = None

logger = logging.getLogger(__name__)


@dataclass
class MetricData:
    """Metric data structure."""
    metric_name: str
    metric_type: str  # counter, gauge, histogram
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = ""


class MetricsCollector:
    """
    Comprehensive metrics collector for governance workflows.
    
    This collector provides Prometheus metrics, OpenTelemetry integration,
    and custom analytics for governance workflow performance monitoring.
    """
    
    def __init__(self, settings):
        self.settings = settings
        
        # Configuration
        self.prometheus_enabled = settings.PROMETHEUS_ENABLED
        self.prometheus_port = settings.PROMETHEUS_PORT
        self.export_interval = settings.METRICS_EXPORT_INTERVAL_SECONDS
        
        # Metrics storage
        self.metrics_buffer: List[MetricData] = []
        self.prometheus_metrics: Dict[str, Any] = {}
        
        # Prometheus metrics (if available)
        if PROMETHEUS_AVAILABLE and self.prometheus_enabled:
            self._initialize_prometheus_metrics()
        
        # Collection statistics
        self.collection_stats = {
            "total_metrics_collected": 0,
            "metrics_exported": 0,
            "collection_errors": 0,
            "last_export_time": None,
        }
        
        logger.info("Metrics collector initialized")
    
    async def initialize(self):
        """Initialize the metrics collector."""
        try:
            # Start Prometheus HTTP server if enabled
            if PROMETHEUS_AVAILABLE and self.prometheus_enabled:
                start_http_server(self.prometheus_port)
                logger.info(f"Prometheus metrics server started on port {self.prometheus_port}")
            
            # Start background collection tasks
            asyncio.create_task(self._periodic_metrics_export())
            asyncio.create_task(self._metrics_cleanup())
            
            logger.info("✅ Metrics collector initialization complete")
            
        except Exception as e:
            logger.error(f"❌ Metrics collector initialization failed: {e}")
            raise
    
    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics."""
        try:
            # Workflow metrics
            self.prometheus_metrics["workflow_total"] = Counter(
                "governance_workflow_total",
                "Total number of governance workflows",
                ["workflow_type", "status"]
            )
            
            self.prometheus_metrics["workflow_duration"] = Histogram(
                "governance_workflow_duration_seconds",
                "Duration of governance workflows",
                ["workflow_type"],
                buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0]
            )
            
            self.prometheus_metrics["workflow_active"] = Gauge(
                "governance_workflow_active",
                "Number of active governance workflows",
                ["workflow_type"]
            )
            
            # Performance metrics
            self.prometheus_metrics["response_time"] = Histogram(
                "governance_response_time_seconds",
                "Response time for governance operations",
                ["operation", "service"],
                buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
            )
            
            self.prometheus_metrics["availability"] = Gauge(
                "governance_availability_percent",
                "Availability percentage for governance services",
                ["service"]
            )
            
            # Constitutional compliance metrics
            self.prometheus_metrics["compliance_checks"] = Counter(
                "governance_compliance_checks_total",
                "Total number of constitutional compliance checks",
                ["result"]
            )
            
            self.prometheus_metrics["compliance_accuracy"] = Gauge(
                "governance_compliance_accuracy_percent",
                "Constitutional compliance accuracy percentage"
            )
            
            # WINA oversight metrics
            self.prometheus_metrics["wina_optimizations"] = Counter(
                "governance_wina_optimizations_total",
                "Total number of WINA optimizations",
                ["optimization_type", "result"]
            )
            
            self.prometheus_metrics["wina_performance_improvement"] = Gauge(
                "governance_wina_performance_improvement_percent",
                "WINA performance improvement percentage"
            )
            
            # Service integration metrics
            self.prometheus_metrics["service_requests"] = Counter(
                "governance_service_requests_total",
                "Total number of service requests",
                ["service", "endpoint", "status"]
            )
            
            self.prometheus_metrics["service_response_time"] = Histogram(
                "governance_service_response_time_seconds",
                "Service response time",
                ["service", "endpoint"],
                buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
            )
            
            logger.info("Prometheus metrics initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Prometheus metrics: {e}")
    
    async def record_workflow_metric(
        self,
        workflow_type: str,
        metric_type: str,
        value: float,
        labels: Dict[str, str] = None
    ):
        """Record a workflow-related metric."""
        try:
            # Create metric data
            metric = MetricData(
                metric_name=f"workflow_{metric_type}",
                metric_type="counter" if metric_type in ["started", "completed", "failed"] else "gauge",
                value=value,
                labels={"workflow_type": workflow_type, **(labels or {})},
                description=f"Workflow {metric_type} metric",
            )
            
            # Add to buffer
            self.metrics_buffer.append(metric)
            self.collection_stats["total_metrics_collected"] += 1
            
            # Update Prometheus metrics if available
            if PROMETHEUS_AVAILABLE and self.prometheus_enabled:
                if metric_type in ["started", "completed", "failed"]:
                    self.prometheus_metrics["workflow_total"].labels(
                        workflow_type=workflow_type,
                        status=metric_type
                    ).inc(value)
                elif metric_type == "duration":
                    self.prometheus_metrics["workflow_duration"].labels(
                        workflow_type=workflow_type
                    ).observe(value)
                elif metric_type == "active":
                    self.prometheus_metrics["workflow_active"].labels(
                        workflow_type=workflow_type
                    ).set(value)
            
            logger.debug(f"Recorded workflow metric: {workflow_type}/{metric_type} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to record workflow metric: {e}")
            self.collection_stats["collection_errors"] += 1
    
    async def record_performance_metric(
        self,
        operation: str,
        service: str,
        response_time_ms: float,
        success: bool = True
    ):
        """Record a performance metric."""
        try:
            # Create metric data
            metric = MetricData(
                metric_name="performance_response_time",
                metric_type="histogram",
                value=response_time_ms / 1000,  # Convert to seconds
                labels={"operation": operation, "service": service, "success": str(success)},
                description="Performance response time metric",
            )
            
            # Add to buffer
            self.metrics_buffer.append(metric)
            self.collection_stats["total_metrics_collected"] += 1
            
            # Update Prometheus metrics if available
            if PROMETHEUS_AVAILABLE and self.prometheus_enabled:
                self.prometheus_metrics["response_time"].labels(
                    operation=operation,
                    service=service
                ).observe(response_time_ms / 1000)
            
            logger.debug(f"Recorded performance metric: {operation}/{service} = {response_time_ms}ms")
            
        except Exception as e:
            logger.error(f"Failed to record performance metric: {e}")
            self.collection_stats["collection_errors"] += 1
    
    async def record_compliance_metric(
        self,
        check_result: str,
        accuracy_percent: float = None
    ):
        """Record a constitutional compliance metric."""
        try:
            # Record compliance check
            check_metric = MetricData(
                metric_name="compliance_check",
                metric_type="counter",
                value=1.0,
                labels={"result": check_result},
                description="Constitutional compliance check metric",
            )
            
            self.metrics_buffer.append(check_metric)
            self.collection_stats["total_metrics_collected"] += 1
            
            # Record accuracy if provided
            if accuracy_percent is not None:
                accuracy_metric = MetricData(
                    metric_name="compliance_accuracy",
                    metric_type="gauge",
                    value=accuracy_percent,
                    labels={},
                    description="Constitutional compliance accuracy metric",
                )
                
                self.metrics_buffer.append(accuracy_metric)
                self.collection_stats["total_metrics_collected"] += 1
            
            # Update Prometheus metrics if available
            if PROMETHEUS_AVAILABLE and self.prometheus_enabled:
                self.prometheus_metrics["compliance_checks"].labels(
                    result=check_result
                ).inc()
                
                if accuracy_percent is not None:
                    self.prometheus_metrics["compliance_accuracy"].set(accuracy_percent)
            
            logger.debug(f"Recorded compliance metric: {check_result}, accuracy: {accuracy_percent}%")
            
        except Exception as e:
            logger.error(f"Failed to record compliance metric: {e}")
            self.collection_stats["collection_errors"] += 1
    
    async def record_wina_metric(
        self,
        optimization_type: str,
        result: str,
        improvement_percent: float = None
    ):
        """Record a WINA oversight metric."""
        try:
            # Record optimization
            optimization_metric = MetricData(
                metric_name="wina_optimization",
                metric_type="counter",
                value=1.0,
                labels={"optimization_type": optimization_type, "result": result},
                description="WINA optimization metric",
            )
            
            self.metrics_buffer.append(optimization_metric)
            self.collection_stats["total_metrics_collected"] += 1
            
            # Record improvement if provided
            if improvement_percent is not None:
                improvement_metric = MetricData(
                    metric_name="wina_performance_improvement",
                    metric_type="gauge",
                    value=improvement_percent,
                    labels={"optimization_type": optimization_type},
                    description="WINA performance improvement metric",
                )
                
                self.metrics_buffer.append(improvement_metric)
                self.collection_stats["total_metrics_collected"] += 1
            
            # Update Prometheus metrics if available
            if PROMETHEUS_AVAILABLE and self.prometheus_enabled:
                self.prometheus_metrics["wina_optimizations"].labels(
                    optimization_type=optimization_type,
                    result=result
                ).inc()
                
                if improvement_percent is not None:
                    self.prometheus_metrics["wina_performance_improvement"].set(improvement_percent)
            
            logger.debug(f"Recorded WINA metric: {optimization_type}/{result}, improvement: {improvement_percent}%")
            
        except Exception as e:
            logger.error(f"Failed to record WINA metric: {e}")
            self.collection_stats["collection_errors"] += 1
    
    async def record_service_metric(
        self,
        service: str,
        endpoint: str,
        response_time_ms: float,
        status_code: int
    ):
        """Record a service integration metric."""
        try:
            status = "success" if 200 <= status_code < 300 else "error"
            
            # Record service request
            request_metric = MetricData(
                metric_name="service_request",
                metric_type="counter",
                value=1.0,
                labels={"service": service, "endpoint": endpoint, "status": status},
                description="Service request metric",
            )
            
            # Record response time
            response_time_metric = MetricData(
                metric_name="service_response_time",
                metric_type="histogram",
                value=response_time_ms / 1000,  # Convert to seconds
                labels={"service": service, "endpoint": endpoint},
                description="Service response time metric",
            )
            
            self.metrics_buffer.extend([request_metric, response_time_metric])
            self.collection_stats["total_metrics_collected"] += 2
            
            # Update Prometheus metrics if available
            if PROMETHEUS_AVAILABLE and self.prometheus_enabled:
                self.prometheus_metrics["service_requests"].labels(
                    service=service,
                    endpoint=endpoint,
                    status=status
                ).inc()
                
                self.prometheus_metrics["service_response_time"].labels(
                    service=service,
                    endpoint=endpoint
                ).observe(response_time_ms / 1000)
            
            logger.debug(f"Recorded service metric: {service}/{endpoint} = {response_time_ms}ms ({status_code})")
            
        except Exception as e:
            logger.error(f"Failed to record service metric: {e}")
            self.collection_stats["collection_errors"] += 1
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics collection summary."""
        try:
            # Calculate recent metrics statistics
            recent_metrics = [
                m for m in self.metrics_buffer
                if (datetime.now(timezone.utc) - m.timestamp).total_seconds() < 3600  # Last hour
            ]
            
            # Group metrics by type
            metrics_by_type = {}
            for metric in recent_metrics:
                if metric.metric_name not in metrics_by_type:
                    metrics_by_type[metric.metric_name] = []
                metrics_by_type[metric.metric_name].append(metric)
            
            return {
                "collection_statistics": self.collection_stats,
                "prometheus_enabled": self.prometheus_enabled,
                "prometheus_port": self.prometheus_port if self.prometheus_enabled else None,
                "metrics_buffer_size": len(self.metrics_buffer),
                "recent_metrics_count": len(recent_metrics),
                "metrics_by_type": {
                    metric_type: len(metrics)
                    for metric_type, metrics in metrics_by_type.items()
                },
                "export_interval_seconds": self.export_interval,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the metrics collector."""
        try:
            health_status = {
                "healthy": True,
                "timestamp": time.time(),
                "checks": {},
            }
            
            # Check Prometheus availability
            health_status["checks"]["prometheus"] = {
                "healthy": PROMETHEUS_AVAILABLE if self.prometheus_enabled else True,
                "enabled": self.prometheus_enabled,
                "available": PROMETHEUS_AVAILABLE,
                "port": self.prometheus_port if self.prometheus_enabled else None,
            }
            
            if self.prometheus_enabled and not PROMETHEUS_AVAILABLE:
                health_status["healthy"] = False
            
            # Check metrics collection
            collection_error_rate = (
                (self.collection_stats["collection_errors"] / max(self.collection_stats["total_metrics_collected"], 1)) * 100
            )
            
            health_status["checks"]["metrics_collection"] = {
                "healthy": collection_error_rate < 5,  # Less than 5% error rate
                "error_rate_percent": round(collection_error_rate, 2),
                "total_collected": self.collection_stats["total_metrics_collected"],
                "collection_errors": self.collection_stats["collection_errors"],
            }
            
            if collection_error_rate >= 5:
                health_status["healthy"] = False
            
            # Check buffer size
            buffer_size = len(self.metrics_buffer)
            health_status["checks"]["buffer_management"] = {
                "healthy": buffer_size < 10000,  # Arbitrary limit
                "buffer_size": buffer_size,
                "buffer_limit": 10000,
            }
            
            if buffer_size >= 10000:
                health_status["healthy"] = False
            
            return health_status
            
        except Exception as e:
            logger.error(f"Metrics collector health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": time.time(),
            }
    
    async def shutdown(self):
        """Shutdown the metrics collector gracefully."""
        try:
            logger.info("Shutting down metrics collector...")
            
            # Export final metrics
            await self._export_metrics()
            
            logger.info("✅ Metrics collector shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during metrics collector shutdown: {e}")
    
    # Private helper methods will be added in the next part...
