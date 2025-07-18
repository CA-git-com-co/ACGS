#!/usr/bin/env python3

"""
ACGS-2 Unified Monitoring and Metrics Library
Centralized monitoring, metrics collection, and observability for all ACGS services
Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import time
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
from contextlib import contextmanager
from enum import Enum
import threading
from collections import defaultdict, deque

# Prometheus metrics
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info, Enum as PrometheusEnum,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)
import prometheus_client

# OpenTelemetry
try:
    from opentelemetry import trace, metrics as otel_metrics
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

# Logging
logger = logging.getLogger(__name__)

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class MetricType(str, Enum):
    """Metric types"""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    SUMMARY = "summary"
    INFO = "info"


class AlertLevel(str, Enum):
    """Alert levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PerformanceTarget:
    """Performance target definition"""
    name: str
    target_value: float
    unit: str
    comparison: str = "lt"  # lt, gt, eq, ne, le, ge
    description: str = ""
    constitutional_requirement: bool = False


@dataclass
class MetricDefinition:
    """Metric definition"""
    name: str
    metric_type: MetricType
    description: str
    labels: List[str] = field(default_factory=list)
    buckets: Optional[List[float]] = None  # For histograms
    constitutional_metric: bool = False


@dataclass
class Alert:
    """Alert definition"""
    name: str
    level: AlertLevel
    message: str
    metric_name: str
    threshold: float
    comparison: str
    description: str = ""
    constitutional_alert: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ConstitutionalMetrics:
    """Constitutional compliance metrics"""
    
    # Performance targets from audit
    PERFORMANCE_TARGETS = {
        'p99_latency_ms': PerformanceTarget(
            name='p99_latency_ms',
            target_value=5.0,
            unit='milliseconds',
            comparison='lt',
            description='P99 latency must be less than 5ms',
            constitutional_requirement=True
        ),
        'throughput_rps': PerformanceTarget(
            name='throughput_rps',
            target_value=100.0,
            unit='requests/second',
            comparison='gt',
            description='Throughput must be greater than 100 RPS',
            constitutional_requirement=True
        ),
        'cache_hit_rate': PerformanceTarget(
            name='cache_hit_rate',
            target_value=0.85,
            unit='ratio',
            comparison='gt',
            description='Cache hit rate must be greater than 85%',
            constitutional_requirement=True
        ),
        'constitutional_compliance_rate': PerformanceTarget(
            name='constitutional_compliance_rate',
            target_value=1.0,
            unit='ratio',
            comparison='eq',
            description='Constitutional compliance must be 100%',
            constitutional_requirement=True
        )
    }
    
    # Standard metrics for all services
    STANDARD_METRICS = [
        MetricDefinition(
            name='acgs_http_requests_total',
            metric_type=MetricType.COUNTER,
            description='Total number of HTTP requests',
            labels=['service', 'method', 'endpoint', 'status_code'],
            constitutional_metric=True
        ),
        MetricDefinition(
            name='acgs_http_request_duration_seconds',
            metric_type=MetricType.HISTOGRAM,
            description='HTTP request duration in seconds',
            labels=['service', 'method', 'endpoint'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0],
            constitutional_metric=True
        ),
        MetricDefinition(
            name='acgs_constitutional_compliance_rate',
            metric_type=MetricType.GAUGE,
            description='Constitutional compliance rate',
            labels=['service', 'component'],
            constitutional_metric=True
        ),
        MetricDefinition(
            name='acgs_service_health',
            metric_type=MetricType.GAUGE,
            description='Service health status (1=healthy, 0=unhealthy)',
            labels=['service', 'component'],
            constitutional_metric=True
        ),
        MetricDefinition(
            name='acgs_database_connections',
            metric_type=MetricType.GAUGE,
            description='Active database connections',
            labels=['service', 'database'],
            constitutional_metric=False
        ),
        MetricDefinition(
            name='acgs_cache_operations_total',
            metric_type=MetricType.COUNTER,
            description='Total cache operations',
            labels=['service', 'operation', 'cache_type'],
            constitutional_metric=False
        ),
        MetricDefinition(
            name='acgs_cache_hit_rate',
            metric_type=MetricType.GAUGE,
            description='Cache hit rate',
            labels=['service', 'cache_type'],
            constitutional_metric=True
        ),
        MetricDefinition(
            name='acgs_errors_total',
            metric_type=MetricType.COUNTER,
            description='Total errors',
            labels=['service', 'error_type', 'severity'],
            constitutional_metric=True
        ),
        MetricDefinition(
            name='acgs_processing_time_seconds',
            metric_type=MetricType.HISTOGRAM,
            description='Processing time in seconds',
            labels=['service', 'operation'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0],
            constitutional_metric=True
        )
    ]


class UnifiedMetricsCollector:
    """Unified metrics collector for all ACGS services"""
    
    def __init__(self, service_name: str, registry: Optional[CollectorRegistry] = None):
        self.service_name = service_name
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.registry = registry or CollectorRegistry()
        self.metrics: Dict[str, Any] = {}
        self.alerts: List[Alert] = []
        self.performance_targets = ConstitutionalMetrics.PERFORMANCE_TARGETS.copy()
        
        # Initialize OpenTelemetry if available
        self.tracer = None
        self.meter = None
        if OPENTELEMETRY_AVAILABLE:
            self._setup_opentelemetry()
            
        # Performance tracking
        self._performance_data = defaultdict(deque)
        self._performance_lock = threading.Lock()
        
        # Initialize standard metrics
        self._initialize_standard_metrics()
        
        logger.info(f"Initialized metrics collector for service: {service_name}")
        
    def _setup_opentelemetry(self):
        """Setup OpenTelemetry tracing and metrics"""
        try:
            # Setup tracing
            trace.set_tracer_provider(TracerProvider())
            
            # Setup Jaeger exporter if configured
            jaeger_endpoint = os.getenv('JAEGER_ENDPOINT', 'http://jaeger:14268/api/traces')
            if jaeger_endpoint:
                jaeger_exporter = JaegerExporter(
                    agent_host_name=os.getenv('JAEGER_AGENT_HOST', 'jaeger-agent'),
                    agent_port=int(os.getenv('JAEGER_AGENT_PORT', '6831'))
                )
                span_processor = BatchSpanProcessor(jaeger_exporter)
                trace.get_tracer_provider().add_span_processor(span_processor)
                
            self.tracer = trace.get_tracer(__name__)
            
            # Setup metrics
            reader = PrometheusMetricReader()
            provider = MeterProvider(metric_readers=[reader])
            otel_metrics.set_meter_provider(provider)
            self.meter = otel_metrics.get_meter(__name__)
            
            logger.info("OpenTelemetry initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize OpenTelemetry: {e}")
            
    def _initialize_standard_metrics(self):
        """Initialize standard metrics for the service"""
        for metric_def in ConstitutionalMetrics.STANDARD_METRICS:
            self._create_metric(metric_def)
            
        # Create constitutional compliance info metric
        self.constitutional_info = Info(
            'acgs_constitutional_info',
            'Constitutional compliance information',
            registry=self.registry
        )
        self.constitutional_info.info({
            'hash': self.constitutional_hash,
            'service': self.service_name,
            'version': '2.0.0'
        })
        
    def _create_metric(self, metric_def: MetricDefinition):
        """Create a Prometheus metric"""
        metric_name = metric_def.name
        
        if metric_def.metric_type == MetricType.COUNTER:
            metric = Counter(
                metric_name,
                metric_def.description,
                labelnames=metric_def.labels,
                registry=self.registry
            )
        elif metric_def.metric_type == MetricType.HISTOGRAM:
            metric = Histogram(
                metric_name,
                metric_def.description,
                labelnames=metric_def.labels,
                buckets=metric_def.buckets,
                registry=self.registry
            )
        elif metric_def.metric_type == MetricType.GAUGE:
            metric = Gauge(
                metric_name,
                metric_def.description,
                labelnames=metric_def.labels,
                registry=self.registry
            )
        elif metric_def.metric_type == MetricType.SUMMARY:
            metric = Summary(
                metric_name,
                metric_def.description,
                labelnames=metric_def.labels,
                registry=self.registry
            )
        elif metric_def.metric_type == MetricType.INFO:
            metric = Info(
                metric_name,
                metric_def.description,
                registry=self.registry
            )
        else:
            raise ValueError(f"Unknown metric type: {metric_def.metric_type}")
            
        self.metrics[metric_name] = metric
        
    def get_metric(self, name: str) -> Optional[Any]:
        """Get a metric by name"""
        return self.metrics.get(name)
        
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        metric = self.get_metric(name)
        if metric and hasattr(metric, 'inc'):
            if labels:
                metric.labels(**labels).inc(value)
            else:
                metric.inc(value)
        else:
            logger.warning(f"Counter metric not found: {name}")
            
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Observe a histogram metric"""
        metric = self.get_metric(name)
        if metric and hasattr(metric, 'observe'):
            if labels:
                metric.labels(**labels).observe(value)
            else:
                metric.observe(value)
        else:
            logger.warning(f"Histogram metric not found: {name}")
            
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric value"""
        metric = self.get_metric(name)
        if metric and hasattr(metric, 'set'):
            if labels:
                metric.labels(**labels).set(value)
            else:
                metric.set(value)
        else:
            logger.warning(f"Gauge metric not found: {name}")
            
    def track_performance(self, operation: str, duration: float, status: str = "success"):
        """Track performance metrics"""
        labels = {
            'service': self.service_name,
            'operation': operation,
            'status': status
        }
        
        # Record in processing time histogram
        self.observe_histogram('acgs_processing_time_seconds', duration, labels)
        
        # Store for performance analysis
        with self._performance_lock:
            self._performance_data[operation].append({
                'timestamp': time.time(),
                'duration': duration,
                'status': status
            })
            
            # Keep only last 1000 entries
            while len(self._performance_data[operation]) > 1000:
                self._performance_data[operation].popleft()
                
    def track_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Track HTTP request metrics"""
        labels = {
            'service': self.service_name,
            'method': method,
            'endpoint': endpoint,
            'status_code': str(status_code)
        }
        
        # Increment request counter
        self.increment_counter('acgs_http_requests_total', 1.0, labels)
        
        # Record request duration
        duration_labels = {
            'service': self.service_name,
            'method': method,
            'endpoint': endpoint
        }
        self.observe_histogram('acgs_http_request_duration_seconds', duration, duration_labels)
        
    def track_cache_operation(self, operation: str, cache_type: str, hit: bool = None):
        """Track cache operation metrics"""
        labels = {
            'service': self.service_name,
            'operation': operation,
            'cache_type': cache_type
        }
        
        # Increment cache operations counter
        self.increment_counter('acgs_cache_operations_total', 1.0, labels)
        
        # Update cache hit rate if applicable
        if hit is not None:
            hit_rate_labels = {
                'service': self.service_name,
                'cache_type': cache_type
            }
            # This would need to be calculated based on recent hits/misses
            # For now, just record the individual hit/miss
            self.increment_counter('acgs_cache_hits_total' if hit else 'acgs_cache_misses_total', 1.0, hit_rate_labels)
            
    def track_error(self, error_type: str, severity: str = "error", message: str = ""):
        """Track error metrics"""
        labels = {
            'service': self.service_name,
            'error_type': error_type,
            'severity': severity
        }
        
        self.increment_counter('acgs_errors_total', 1.0, labels)
        
        # Create alert if critical
        if severity == "critical":
            alert = Alert(
                name=f"{self.service_name}_critical_error",
                level=AlertLevel.CRITICAL,
                message=f"Critical error in {self.service_name}: {message}",
                metric_name='acgs_errors_total',
                threshold=1.0,
                comparison='gt',
                constitutional_alert=True
            )
            self.alerts.append(alert)
            
    def update_health_status(self, component: str, healthy: bool):
        """Update service health status"""
        labels = {
            'service': self.service_name,
            'component': component
        }
        
        self.set_gauge('acgs_service_health', 1.0 if healthy else 0.0, labels)
        
    def update_constitutional_compliance(self, component: str, compliance_rate: float):
        """Update constitutional compliance rate"""
        labels = {
            'service': self.service_name,
            'component': component
        }
        
        self.set_gauge('acgs_constitutional_compliance_rate', compliance_rate, labels)
        
        # Check if compliance meets constitutional requirements
        target = self.performance_targets.get('constitutional_compliance_rate')
        if target and compliance_rate < target.target_value:
            alert = Alert(
                name=f"{self.service_name}_compliance_violation",
                level=AlertLevel.CRITICAL,
                message=f"Constitutional compliance violation: {compliance_rate*100:.1f}% < {target.target_value*100:.1f}%",
                metric_name='acgs_constitutional_compliance_rate',
                threshold=target.target_value,
                comparison='lt',
                constitutional_alert=True
            )
            self.alerts.append(alert)
            
    def get_performance_summary(self, operation: str = None) -> Dict[str, Any]:
        """Get performance summary for operations"""
        with self._performance_lock:
            if operation:
                data = list(self._performance_data.get(operation, []))
            else:
                data = []
                for op_data in self._performance_data.values():
                    data.extend(op_data)
                    
        if not data:
            return {}
            
        durations = [d['duration'] for d in data]
        durations.sort()
        
        n = len(durations)
        if n == 0:
            return {}
            
        return {
            'operation': operation or 'all',
            'sample_count': n,
            'min_duration': min(durations),
            'max_duration': max(durations),
            'mean_duration': sum(durations) / n,
            'median_duration': durations[n // 2],
            'p95_duration': durations[int(n * 0.95)] if n > 0 else 0,
            'p99_duration': durations[int(n * 0.99)] if n > 0 else 0,
            'success_rate': sum(1 for d in data if d['status'] == 'success') / n if n > 0 else 0
        }
        
    def check_performance_targets(self) -> Dict[str, Dict[str, Any]]:
        """Check if performance targets are being met"""
        results = {}
        
        # Get current performance summary
        summary = self.get_performance_summary()
        
        if summary:
            # Check P99 latency
            p99_target = self.performance_targets.get('p99_latency_ms')
            if p99_target:
                p99_ms = summary.get('p99_duration', 0) * 1000  # Convert to ms
                results['p99_latency_ms'] = {
                    'target': p99_target.target_value,
                    'actual': p99_ms,
                    'meets_target': p99_ms < p99_target.target_value,
                    'constitutional_requirement': p99_target.constitutional_requirement
                }
                
        return results
        
    def get_metrics_output(self) -> str:
        """Get Prometheus metrics output"""
        return generate_latest(self.registry)
        
    def get_alerts(self, level: AlertLevel = None) -> List[Alert]:
        """Get active alerts"""
        if level:
            return [alert for alert in self.alerts if alert.level == level]
        return self.alerts.copy()
        
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
        
    @contextmanager
    def track_operation(self, operation: str):
        """Context manager to track operation performance"""
        start_time = time.time()
        status = "success"
        
        try:
            yield
        except Exception as e:
            status = "error"
            self.track_error(f"{operation}_error", "error", str(e))
            raise
        finally:
            duration = time.time() - start_time
            self.track_performance(operation, duration, status)
            
    def trace_operation(self, operation: str):
        """Decorator to trace operation with OpenTelemetry"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if self.tracer:
                    with self.tracer.start_as_current_span(operation) as span:
                        span.set_attribute("service.name", self.service_name)
                        span.set_attribute("constitutional.hash", self.constitutional_hash)
                        
                        start_time = time.time()
                        try:
                            result = await func(*args, **kwargs)
                            span.set_attribute("operation.status", "success")
                            return result
                        except Exception as e:
                            span.set_attribute("operation.status", "error")
                            span.set_attribute("error.message", str(e))
                            self.track_error(f"{operation}_error", "error", str(e))
                            raise
                        finally:
                            duration = time.time() - start_time
                            span.set_attribute("operation.duration", duration)
                            self.track_performance(operation, duration, "success")
                else:
                    with self.track_operation(operation):
                        return await func(*args, **kwargs)
                        
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if self.tracer:
                    with self.tracer.start_as_current_span(operation) as span:
                        span.set_attribute("service.name", self.service_name)
                        span.set_attribute("constitutional.hash", self.constitutional_hash)
                        
                        start_time = time.time()
                        try:
                            result = func(*args, **kwargs)
                            span.set_attribute("operation.status", "success")
                            return result
                        except Exception as e:
                            span.set_attribute("operation.status", "error")
                            span.set_attribute("error.message", str(e))
                            self.track_error(f"{operation}_error", "error", str(e))
                            raise
                        finally:
                            duration = time.time() - start_time
                            span.set_attribute("operation.duration", duration)
                            self.track_performance(operation, duration, "success")
                else:
                    with self.track_operation(operation):
                        return func(*args, **kwargs)
                        
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator


# Global metrics collector
_metrics_collector: Optional[UnifiedMetricsCollector] = None


def get_metrics_collector() -> UnifiedMetricsCollector:
    """Get global metrics collector"""
    global _metrics_collector
    if _metrics_collector is None:
        service_name = os.getenv('SERVICE_NAME', 'unknown')
        _metrics_collector = UnifiedMetricsCollector(service_name)
    return _metrics_collector


def initialize_metrics(service_name: str, registry: Optional[CollectorRegistry] = None) -> UnifiedMetricsCollector:
    """Initialize metrics collector"""
    global _metrics_collector
    _metrics_collector = UnifiedMetricsCollector(service_name, registry)
    return _metrics_collector


# Convenience functions
def track_operation(operation: str):
    """Decorator to track operation performance"""
    return get_metrics_collector().track_operation(operation)


def trace_operation(operation: str):
    """Decorator to trace operation with OpenTelemetry"""
    return get_metrics_collector().trace_operation(operation)


def track_http_request(method: str, endpoint: str, status_code: int, duration: float):
    """Track HTTP request metrics"""
    get_metrics_collector().track_http_request(method, endpoint, status_code, duration)


def track_error(error_type: str, severity: str = "error", message: str = ""):
    """Track error metrics"""
    get_metrics_collector().track_error(error_type, severity, message)


def update_health_status(component: str, healthy: bool):
    """Update service health status"""
    get_metrics_collector().update_health_status(component, healthy)


def update_constitutional_compliance(component: str, compliance_rate: float):
    """Update constitutional compliance rate"""
    get_metrics_collector().update_constitutional_compliance(component, compliance_rate)


# FastAPI middleware
class MetricsMiddleware:
    """FastAPI middleware for automatic metrics collection"""
    
    def __init__(self, app):
        self.app = app
        self.metrics_collector = get_metrics_collector()
        
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            status_code = 200
            
            async def send_wrapper(message):
                nonlocal status_code
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                    
                    # Add constitutional hash header
                    headers = list(message.get("headers", []))
                    headers.append([b"X-Constitutional-Hash", CONSTITUTIONAL_HASH.encode()])
                    headers.append([b"X-Metrics-Service", self.metrics_collector.service_name.encode()])
                    message["headers"] = headers
                    
                await send(message)
                
            await self.app(scope, receive, send_wrapper)
            
            # Record metrics
            duration = time.time() - start_time
            method = scope["method"]
            path = scope["path"]
            
            self.metrics_collector.track_http_request(method, path, status_code, duration)
            
        else:
            await self.app(scope, receive, send)


# Export main components
__all__ = [
    'UnifiedMetricsCollector',
    'MetricType',
    'AlertLevel',
    'PerformanceTarget',
    'MetricDefinition',
    'Alert',
    'ConstitutionalMetrics',
    'get_metrics_collector',
    'initialize_metrics',
    'track_operation',
    'trace_operation',
    'track_http_request',
    'track_error',
    'update_health_status',
    'update_constitutional_compliance',
    'MetricsMiddleware',
    'CONSTITUTIONAL_HASH'
]