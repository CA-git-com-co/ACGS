"""
Prometheus Metrics Manager for ACGS-PGP v8

Comprehensive metrics collection and monitoring for all system components.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps

from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)

logger = logging.getLogger(__name__)


class MetricsManager:
    """
    Prometheus metrics manager for ACGS-PGP v8 system monitoring.
    
    Provides comprehensive metrics collection for policy generation,
    execution environment, diagnostic engine, and system health.
    """
    
    def __init__(self, constitutional_hash: str = "cdd01ef066bc6cf2"):
        """Initialize metrics manager with Prometheus collectors."""
        self.constitutional_hash = constitutional_hash
        self.registry = CollectorRegistry()
        
        # System information
        self.system_info = Info(
            'acgs_pgp_v8_system_info',
            'ACGS-PGP v8 system information',
            registry=self.registry
        )
        
        # Policy Generation Metrics
        self.policy_generation_requests = Counter(
            'acgs_pgp_v8_policy_generation_requests_total',
            'Total number of policy generation requests',
            ['status', 'priority'],
            registry=self.registry
        )
        
        self.policy_generation_duration = Histogram(
            'acgs_pgp_v8_policy_generation_duration_seconds',
            'Time spent generating policies',
            ['priority'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        self.constitutional_compliance_score = Histogram(
            'acgs_pgp_v8_constitutional_compliance_score',
            'Constitutional compliance scores for generated policies',
            buckets=[0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0],
            registry=self.registry
        )
        
        self.policy_confidence_score = Histogram(
            'acgs_pgp_v8_policy_confidence_score',
            'Confidence scores for generated policies',
            buckets=[0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0],
            registry=self.registry
        )
        
        # Stabilizer Execution Environment Metrics
        self.execution_requests = Counter(
            'acgs_pgp_v8_execution_requests_total',
            'Total number of execution requests',
            ['operation', 'status'],
            registry=self.registry
        )
        
        self.execution_duration = Histogram(
            'acgs_pgp_v8_execution_duration_seconds',
            'Time spent in execution environment',
            ['operation'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            registry=self.registry
        )
        
        self.circuit_breaker_state = Gauge(
            'acgs_pgp_v8_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half-open)',
            ['service'],
            registry=self.registry
        )
        
        self.error_correction_events = Counter(
            'acgs_pgp_v8_error_correction_events_total',
            'Total number of error correction events',
            ['error_type', 'corrected'],
            registry=self.registry
        )
        
        # Syndrome Diagnostic Engine Metrics
        self.diagnostic_requests = Counter(
            'acgs_pgp_v8_diagnostic_requests_total',
            'Total number of diagnostic requests',
            ['target_system', 'status'],
            registry=self.registry
        )
        
        self.diagnostic_duration = Histogram(
            'acgs_pgp_v8_diagnostic_duration_seconds',
            'Time spent on system diagnostics',
            ['target_system'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        self.errors_detected = Counter(
            'acgs_pgp_v8_errors_detected_total',
            'Total number of errors detected',
            ['severity', 'category'],
            registry=self.registry
        )
        
        self.recovery_recommendations = Counter(
            'acgs_pgp_v8_recovery_recommendations_total',
            'Total number of recovery recommendations generated',
            ['strategy', 'auto_executable'],
            registry=self.registry
        )
        
        # Cache Performance Metrics
        self.cache_operations = Counter(
            'acgs_pgp_v8_cache_operations_total',
            'Total number of cache operations',
            ['operation', 'cache_type', 'result'],
            registry=self.registry
        )
        
        self.cache_hit_rate = Gauge(
            'acgs_pgp_v8_cache_hit_rate',
            'Cache hit rate percentage',
            ['cache_type'],
            registry=self.registry
        )
        
        self.cache_operation_duration = Histogram(
            'acgs_pgp_v8_cache_operation_duration_seconds',
            'Time spent on cache operations',
            ['operation', 'cache_type'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25],
            registry=self.registry
        )
        
        # System Health Metrics
        self.component_health = Gauge(
            'acgs_pgp_v8_component_health',
            'Component health status (1=healthy, 0=unhealthy)',
            ['component'],
            registry=self.registry
        )
        
        self.system_uptime = Gauge(
            'acgs_pgp_v8_system_uptime_seconds',
            'System uptime in seconds',
            registry=self.registry
        )
        
        self.active_connections = Gauge(
            'acgs_pgp_v8_active_connections',
            'Number of active connections',
            ['connection_type'],
            registry=self.registry
        )
        
        # Constitutional Governance Metrics
        self.constitutional_validations = Counter(
            'acgs_pgp_v8_constitutional_validations_total',
            'Total number of constitutional validations',
            ['result'],
            registry=self.registry
        )
        
        self.constitutional_hash_mismatches = Counter(
            'acgs_pgp_v8_constitutional_hash_mismatches_total',
            'Total number of constitutional hash mismatches',
            registry=self.registry
        )
        
        # Performance Summary Metrics
        self.response_time_summary = Summary(
            'acgs_pgp_v8_response_time_seconds',
            'Response time summary for all endpoints',
            ['endpoint', 'method'],
            registry=self.registry
        )
        
        # Initialize system info
        self._initialize_system_info()
        
        # Track initialization time
        self.start_time = time.time()
        
        logger.info("Prometheus metrics manager initialized")
    
    def _initialize_system_info(self):
        """Initialize system information metrics."""
        self.system_info.info({
            'version': '8.0.0',
            'service': 'acgs-pgp-v8',
            'constitutional_hash': self.constitutional_hash,
            'description': 'Quantum-Inspired Semantic Fault Tolerance System'
        })
    
    def record_policy_generation(
        self,
        duration_seconds: float,
        status: str,
        priority: str,
        compliance_score: float,
        confidence_score: float
    ):
        """Record policy generation metrics."""
        self.policy_generation_requests.labels(status=status, priority=priority).inc()
        self.policy_generation_duration.labels(priority=priority).observe(duration_seconds)
        self.constitutional_compliance_score.observe(compliance_score)
        self.policy_confidence_score.observe(confidence_score)
        
        logger.debug(f"Recorded policy generation metrics: {status}, {priority}, {duration_seconds}s")
    
    def record_execution(
        self,
        operation: str,
        duration_seconds: float,
        status: str,
        errors_detected: int = 0,
        errors_corrected: int = 0
    ):
        """Record stabilizer execution metrics."""
        self.execution_requests.labels(operation=operation, status=status).inc()
        self.execution_duration.labels(operation=operation).observe(duration_seconds)
        
        if errors_detected > 0:
            self.error_correction_events.labels(
                error_type="detected",
                corrected=str(errors_corrected > 0)
            ).inc(errors_detected)
        
        if errors_corrected > 0:
            self.error_correction_events.labels(
                error_type="corrected",
                corrected="true"
            ).inc(errors_corrected)
        
        logger.debug(f"Recorded execution metrics: {operation}, {status}, {duration_seconds}s")
    
    def record_diagnostic(
        self,
        target_system: str,
        duration_seconds: float,
        status: str,
        errors_by_severity: Dict[str, int],
        recommendations_count: int,
        auto_executable_count: int
    ):
        """Record diagnostic engine metrics."""
        self.diagnostic_requests.labels(target_system=target_system, status=status).inc()
        self.diagnostic_duration.labels(target_system=target_system).observe(duration_seconds)
        
        # Record errors by severity
        for severity, count in errors_by_severity.items():
            if count > 0:
                self.errors_detected.labels(severity=severity, category="general").inc(count)
        
        # Record recommendations
        if recommendations_count > 0:
            self.recovery_recommendations.labels(
                strategy="general",
                auto_executable=str(auto_executable_count > 0)
            ).inc(recommendations_count)
        
        logger.debug(f"Recorded diagnostic metrics: {target_system}, {status}, {duration_seconds}s")
    
    def record_cache_operation(
        self,
        operation: str,
        cache_type: str,
        duration_seconds: float,
        result: str,
        hit_rate: Optional[float] = None
    ):
        """Record cache operation metrics."""
        self.cache_operations.labels(
            operation=operation,
            cache_type=cache_type,
            result=result
        ).inc()
        
        self.cache_operation_duration.labels(
            operation=operation,
            cache_type=cache_type
        ).observe(duration_seconds)
        
        if hit_rate is not None:
            self.cache_hit_rate.labels(cache_type=cache_type).set(hit_rate)
        
        logger.debug(f"Recorded cache operation: {operation}, {cache_type}, {result}")
    
    def update_component_health(self, component: str, is_healthy: bool):
        """Update component health status."""
        self.component_health.labels(component=component).set(1 if is_healthy else 0)
        logger.debug(f"Updated component health: {component} = {'healthy' if is_healthy else 'unhealthy'}")
    
    def update_circuit_breaker_state(self, service: str, state: int):
        """Update circuit breaker state (0=closed, 1=open, 2=half-open)."""
        self.circuit_breaker_state.labels(service=service).set(state)
        logger.debug(f"Updated circuit breaker state: {service} = {state}")
    
    def update_active_connections(self, connection_type: str, count: int):
        """Update active connection count."""
        self.active_connections.labels(connection_type=connection_type).set(count)
        logger.debug(f"Updated active connections: {connection_type} = {count}")
    
    def record_constitutional_validation(self, is_valid: bool):
        """Record constitutional validation result."""
        result = "valid" if is_valid else "invalid"
        self.constitutional_validations.labels(result=result).inc()
        
        if not is_valid:
            self.constitutional_hash_mismatches.inc()
        
        logger.debug(f"Recorded constitutional validation: {result}")
    
    def record_response_time(self, endpoint: str, method: str, duration_seconds: float):
        """Record API response time."""
        self.response_time_summary.labels(endpoint=endpoint, method=method).observe(duration_seconds)
        logger.debug(f"Recorded response time: {method} {endpoint} = {duration_seconds}s")
    
    def update_system_uptime(self):
        """Update system uptime metric."""
        uptime_seconds = time.time() - self.start_time
        self.system_uptime.set(uptime_seconds)
    
    def get_metrics_data(self) -> str:
        """Get Prometheus metrics data in text format."""
        self.update_system_uptime()
        return generate_latest(self.registry).decode('utf-8')
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary for health checks."""
        self.update_system_uptime()
        
        return {
            "constitutional_hash": self.constitutional_hash,
            "system_uptime_seconds": time.time() - self.start_time,
            "metrics_collected": True,
            "registry_collectors": len(self.registry._collector_to_names),
            "timestamp": datetime.utcnow().isoformat()
        }


# Decorator for automatic metrics collection
def monitor_performance(endpoint: str, method: str = "POST"):
    """Decorator to automatically monitor function performance."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Get metrics manager if available
                try:
                    metrics_manager = get_metrics_manager()
                    metrics_manager.record_response_time(endpoint, method, duration)
                except:
                    pass  # Metrics manager not available
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # Record error metrics
                try:
                    metrics_manager = get_metrics_manager()
                    metrics_manager.record_response_time(f"{endpoint}_error", method, duration)
                except:
                    pass
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Get metrics manager if available
                try:
                    metrics_manager = get_metrics_manager()
                    metrics_manager.record_response_time(endpoint, method, duration)
                except:
                    pass
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # Record error metrics
                try:
                    metrics_manager = get_metrics_manager()
                    metrics_manager.record_response_time(f"{endpoint}_error", method, duration)
                except:
                    pass
                
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global metrics manager instance
_metrics_manager: Optional[MetricsManager] = None


def initialize_metrics_manager(constitutional_hash: str = "cdd01ef066bc6cf2") -> MetricsManager:
    """Initialize global metrics manager."""
    global _metrics_manager
    _metrics_manager = MetricsManager(constitutional_hash=constitutional_hash)
    return _metrics_manager


def get_metrics_manager() -> MetricsManager:
    """Get global metrics manager instance."""
    global _metrics_manager
    if _metrics_manager is None:
        _metrics_manager = initialize_metrics_manager()
    return _metrics_manager
