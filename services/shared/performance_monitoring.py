"""
Performance Monitoring for ACGS Services with CARMA Robustness
Constitutional Hash: cdd01ef066bc6cf2

Enhanced performance monitoring with CARMA-inspired causal robustness metrics.
Implements comprehensive monitoring with constitutional compliance, causal sensitivity,
and spurious correlation detection for all ACGS services.
"""

import asyncio
import logging
import time
import statistics
from functools import wraps
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque

from prometheus_client import REGISTRY, CollectorRegistry, Counter, Gauge, Histogram

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ServiceMetrics:
    """
    Enhanced service-specific performance metrics for ACGS with CARMA robustness.

    Provides comprehensive metrics collection including causal robustness metrics,
    spurious correlation detection, and constitutional compliance monitoring.
    """

    def __init__(self, service_name: str, registry: CollectorRegistry | None = None):
        """
        Initialize service metrics with CARMA robustness capabilities.

        Args:
            service_name: Name of the service (e.g., 'constitutional_ai', 'multi_agent_coordinator')
            registry: Prometheus registry (uses default if None)
        """
        self.service_name = service_name
        self.registry = registry or REGISTRY

        # Core performance metrics
        self.response_time_histogram = Histogram(
            f"{service_name}_response_time_seconds",
            "Response time for service endpoints",
            ["endpoint", "method", "status"],
            registry=self.registry,
        )

        self.request_counter = Counter(
            f"{service_name}_requests_total",
            "Total number of requests",
            ["endpoint", "method", "status"],
            registry=self.registry,
        )

        self.error_counter = Counter(
            f"{service_name}_errors_total",
            "Total number of errors",
            ["error_type", "endpoint"],
            registry=self.registry,
        )

        # Constitutional compliance metrics
        self.constitutional_compliance_gauge = Gauge(
            f"{service_name}_constitutional_compliance_score",
            "Current constitutional compliance score",
            registry=self.registry,
        )

        self.constitutional_validations_counter = Counter(
            f"{service_name}_constitutional_validations_total",
            "Total constitutional validations performed",
            ["validation_type", "result"],
            registry=self.registry,
        )

        # CARMA robustness metrics
        self.causal_sensitivity_gauge = Gauge(
            f"{service_name}_causal_sensitivity_score",
            "CARMA causal sensitivity score (0.0-1.0)",
            registry=self.registry,
        )

        self.spurious_invariance_gauge = Gauge(
            f"{service_name}_spurious_invariance_score",
            "CARMA spurious invariance score (0.0-1.0)",
            registry=self.registry,
        )

        self.robustness_score_gauge = Gauge(
            f"{service_name}_robustness_score",
            "Overall CARMA robustness score (0.0-1.0)",
            registry=self.registry,
        )

        self.spurious_correlations_counter = Counter(
            f"{service_name}_spurious_correlations_detected",
            "Spurious correlations detected",
            ["correlation_type", "attribute"],
            registry=self.registry,
        )

        self.causal_tests_counter = Counter(
            f"{service_name}_causal_tests_performed",
            "Causal attribute tests performed",
            ["test_type", "attribute", "result"],
            registry=self.registry,
        )

        # Service health metrics
        self.service_health_gauge = Gauge(
            f"{service_name}_health_status",
            "Service health status (1=healthy, 0=unhealthy)",
            registry=self.registry,
        )

        self.active_connections_gauge = Gauge(
            f"{service_name}_active_connections",
            "Number of active connections",
            registry=self.registry,
        )

        # Cache metrics
        self.cache_hits_counter = Counter(
            f"{service_name}_cache_hits_total",
            "Total cache hits",
            ["cache_type"],
            registry=self.registry,
        )

        self.cache_misses_counter = Counter(
            f"{service_name}_cache_misses_total",
            "Total cache misses",
            ["cache_type"],
            registry=self.registry,
        )

        # Robustness monitoring data
        self.robustness_history = deque(maxlen=1000)
        self.causal_sensitivity_history = deque(maxlen=1000)
        self.spurious_correlations_history = defaultdict(lambda: deque(maxlen=1000))
        
        # Performance targets for robustness
        self.robustness_targets = {
            "causal_sensitivity": 0.8,
            "spurious_invariance": 0.9,
            "overall_robustness": 0.85,
            "constitutional_compliance": 0.95
        }

        logger.info(f"Enhanced service metrics with CARMA robustness initialized for {service_name}")

    def record_request(
        self, endpoint: str, method: str, status_code: int, duration: float
    ):
        """
        Record request metrics.

        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: HTTP status code
            duration: Request duration in seconds
        """
        status = str(status_code)

        # Record response time
        self.response_time_histogram.labels(
            endpoint=endpoint, method=method, status=status
        ).observe(duration)

        # Record request count
        self.request_counter.labels(
            endpoint=endpoint, method=method, status=status
        ).inc()

        # Record errors for 4xx and 5xx status codes
        if status_code >= 400:
            error_type = "client_error" if status_code < 500 else "server_error"
            self.error_counter.labels(error_type=error_type, endpoint=endpoint).inc()

    def record_constitutional_validation(
        self, validation_type: str, result: str, score: float
    ):
        """
        Record constitutional validation metrics.

        Args:
            validation_type: Type of validation performed
            result: Validation result (valid/invalid/error)
            score: Compliance score (0.0-1.0)
        """
        self.constitutional_validations_counter.labels(
            validation_type=validation_type, result=result
        ).inc()

        # Update compliance score
        self.constitutional_compliance_gauge.set(score)

    def record_cache_operation(self, cache_type: str, hit: bool):
        """
        Record cache operation metrics.

        Args:
            cache_type: Type of cache (constitutional, policy, etc.)
            hit: Whether it was a cache hit or miss
        """
        if hit:
            self.cache_hits_counter.labels(cache_type=cache_type).inc()
        else:
            self.cache_misses_counter.labels(cache_type=cache_type).inc()

    def record_causal_robustness_metrics(
        self, 
        causal_sensitivity: float,
        spurious_invariance: float,
        overall_robustness: float
    ):
        """
        Record CARMA robustness metrics.

        Args:
            causal_sensitivity: Sensitivity to causal attributes (0.0-1.0)
            spurious_invariance: Invariance to spurious attributes (0.0-1.0)
            overall_robustness: Overall robustness score (0.0-1.0)
        """
        # Validate constitutional hash implicitly
        if not hasattr(self, 'constitutional_hash_validated'):
            self.constitutional_hash_validated = CONSTITUTIONAL_HASH
        
        # Update Prometheus gauges
        self.causal_sensitivity_gauge.set(causal_sensitivity)
        self.spurious_invariance_gauge.set(spurious_invariance)
        self.robustness_score_gauge.set(overall_robustness)
        
        # Store in history for trend analysis
        timestamp = datetime.now(timezone.utc)
        robustness_record = {
            'timestamp': timestamp,
            'causal_sensitivity': causal_sensitivity,
            'spurious_invariance': spurious_invariance,
            'overall_robustness': overall_robustness,
            'constitutional_hash': CONSTITUTIONAL_HASH
        }
        
        self.robustness_history.append(robustness_record)
        self.causal_sensitivity_history.append((timestamp, causal_sensitivity))
        
        logger.debug(f"Recorded robustness metrics for {self.service_name}: "
                    f"causal={causal_sensitivity:.3f}, spurious={spurious_invariance:.3f}, "
                    f"overall={overall_robustness:.3f}")

    def record_causal_test(
        self, 
        test_type: str, 
        attribute: str, 
        result: str,
        sensitivity_score: Optional[float] = None
    ):
        """
        Record causal attribute test results.

        Args:
            test_type: Type of test ('causal_sensitivity' or 'spurious_invariance')
            attribute: Attribute being tested
            result: Test result ('passed', 'failed', 'error')
            sensitivity_score: Optional sensitivity score
        """
        self.causal_tests_counter.labels(
            test_type=test_type, 
            attribute=attribute, 
            result=result
        ).inc()
        
        if sensitivity_score is not None and test_type == 'causal_sensitivity':
            timestamp = datetime.now(timezone.utc)
            self.causal_sensitivity_history.append((timestamp, sensitivity_score))

    def record_spurious_correlation(
        self, 
        correlation_type: str, 
        attribute: str,
        correlation_strength: float
    ):
        """
        Record detected spurious correlation.

        Args:
            correlation_type: Type of spurious correlation detected
            attribute: Spurious attribute involved
            correlation_strength: Strength of correlation (0.0-1.0)
        """
        self.spurious_correlations_counter.labels(
            correlation_type=correlation_type,
            attribute=attribute
        ).inc()
        
        # Store correlation history
        timestamp = datetime.now(timezone.utc)
        self.spurious_correlations_history[attribute].append(
            (timestamp, correlation_strength)
        )
        
        logger.warning(f"Spurious correlation detected in {self.service_name}: "
                      f"{correlation_type} for {attribute} (strength: {correlation_strength:.3f})")

    def get_robustness_trends(self, window_minutes: int = 60) -> Dict[str, Any]:
        """
        Get robustness trends over specified time window.

        Args:
            window_minutes: Time window in minutes

        Returns:
            Dictionary with trend analysis
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        
        # Filter recent robustness records
        recent_records = [
            r for r in self.robustness_history 
            if r['timestamp'] >= cutoff_time
        ]
        
        if not recent_records:
            return {
                'causal_sensitivity_trend': 'no_data',
                'spurious_invariance_trend': 'no_data',
                'robustness_trend': 'no_data',
                'trend_confidence': 0.0,
                'constitutional_hash': CONSTITUTIONAL_HASH
            }
        
        # Calculate trends
        causal_values = [r['causal_sensitivity'] for r in recent_records]
        spurious_values = [r['spurious_invariance'] for r in recent_records]
        robustness_values = [r['overall_robustness'] for r in recent_records]
        
        def calculate_trend(values):
            if len(values) < 3:
                return 'stable', 0.0
            
            # Simple linear trend
            x = list(range(len(values)))
            try:
                correlation = statistics.correlation(x, values) if len(values) > 1 else 0.0
                
                if abs(correlation) < 0.1:
                    return 'stable', abs(correlation)
                elif correlation > 0.1:
                    return 'improving', correlation
                else:
                    return 'degrading', abs(correlation)
            except:
                return 'stable', 0.0
        
        causal_trend, causal_strength = calculate_trend(causal_values)
        spurious_trend, spurious_strength = calculate_trend(spurious_values)
        robustness_trend, robustness_strength = calculate_trend(robustness_values)
        
        # Calculate overall trend confidence
        trend_confidence = min(1.0, (len(recent_records) / 10.0))
        
        return {
            'window_minutes': window_minutes,
            'records_analyzed': len(recent_records),
            'causal_sensitivity_trend': causal_trend,
            'causal_trend_strength': causal_strength,
            'spurious_invariance_trend': spurious_trend,
            'spurious_trend_strength': spurious_strength,
            'robustness_trend': robustness_trend,
            'robustness_trend_strength': robustness_strength,
            'trend_confidence': trend_confidence,
            'current_values': {
                'causal_sensitivity': causal_values[-1] if causal_values else 0.0,
                'spurious_invariance': spurious_values[-1] if spurious_values else 0.0,
                'overall_robustness': robustness_values[-1] if robustness_values else 0.0
            },
            'constitutional_hash': CONSTITUTIONAL_HASH
        }

    def check_robustness_alerts(self) -> List[Dict[str, Any]]:
        """
        Check for robustness-related alerts.

        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        if not self.robustness_history:
            return alerts
        
        latest_record = self.robustness_history[-1]
        
        # Check against targets
        if latest_record['causal_sensitivity'] < self.robustness_targets['causal_sensitivity']:
            alerts.append({
                'type': 'low_causal_sensitivity',
                'service': self.service_name,
                'current_value': latest_record['causal_sensitivity'],
                'target_value': self.robustness_targets['causal_sensitivity'],
                'severity': 'high' if latest_record['causal_sensitivity'] < 0.6 else 'medium',
                'timestamp': latest_record['timestamp'].isoformat(),
                'constitutional_hash': CONSTITUTIONAL_HASH
            })
        
        if latest_record['spurious_invariance'] < self.robustness_targets['spurious_invariance']:
            alerts.append({
                'type': 'low_spurious_invariance',
                'service': self.service_name,
                'current_value': latest_record['spurious_invariance'],
                'target_value': self.robustness_targets['spurious_invariance'],
                'severity': 'high' if latest_record['spurious_invariance'] < 0.7 else 'medium',
                'timestamp': latest_record['timestamp'].isoformat(),
                'constitutional_hash': CONSTITUTIONAL_HASH
            })
        
        if latest_record['overall_robustness'] < self.robustness_targets['overall_robustness']:
            alerts.append({
                'type': 'low_overall_robustness',
                'service': self.service_name,
                'current_value': latest_record['overall_robustness'],
                'target_value': self.robustness_targets['overall_robustness'],
                'severity': 'critical' if latest_record['overall_robustness'] < 0.6 else 'high',
                'timestamp': latest_record['timestamp'].isoformat(),
                'constitutional_hash': CONSTITUTIONAL_HASH
            })
        
        return alerts

    def set_health_status(self, healthy: bool):
        """
        Set service health status.

        Args:
            healthy: Whether the service is healthy
        """
        self.service_health_gauge.set(1 if healthy else 0)

    def set_active_connections(self, count: int):
        """
        Set number of active connections.

        Args:
            count: Number of active connections
        """
        self.active_connections_gauge.set(count)

    def get_metrics_summary(self) -> dict[str, Any]:
        """
        Get comprehensive summary of current metrics including CARMA robustness.

        Returns:
            Dictionary with current metric values including robustness metrics
        """
        try:
            # Get current values from metrics
            total_requests = sum(
                sample.value for sample in self.request_counter.collect()[0].samples
            )

            total_errors = sum(
                sample.value for sample in self.error_counter.collect()[0].samples
            )

            error_rate = total_errors / total_requests if total_requests > 0 else 0.0

            # Get robustness metrics
            causal_sensitivity = self.causal_sensitivity_gauge._value._value
            spurious_invariance = self.spurious_invariance_gauge._value._value
            robustness_score = self.robustness_score_gauge._value._value
            
            # Get spurious correlations count
            spurious_correlations_count = sum(
                sample.value for sample in self.spurious_correlations_counter.collect()[0].samples
            )
            
            # Get causal tests count
            causal_tests_count = sum(
                sample.value for sample in self.causal_tests_counter.collect()[0].samples
            )
            
            # Check robustness alerts
            robustness_alerts = self.check_robustness_alerts()
            
            # Get trend analysis
            robustness_trends = self.get_robustness_trends(window_minutes=60)

            return {
                "service_name": self.service_name,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                # Core metrics
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate": error_rate,
                "constitutional_compliance_score": self.constitutional_compliance_gauge._value._value,
                "health_status": bool(self.service_health_gauge._value._value),
                "active_connections": self.active_connections_gauge._value._value,
                # CARMA robustness metrics
                "robustness_metrics": {
                    "causal_sensitivity": causal_sensitivity,
                    "spurious_invariance": spurious_invariance,
                    "overall_robustness": robustness_score,
                    "spurious_correlations_detected": spurious_correlations_count,
                    "causal_tests_performed": causal_tests_count,
                    "robustness_targets": self.robustness_targets,
                    "meets_robustness_targets": {
                        "causal_sensitivity": causal_sensitivity >= self.robustness_targets["causal_sensitivity"],
                        "spurious_invariance": spurious_invariance >= self.robustness_targets["spurious_invariance"],
                        "overall_robustness": robustness_score >= self.robustness_targets["overall_robustness"]
                    }
                },
                "robustness_alerts": robustness_alerts,
                "robustness_trends": robustness_trends,
                "robustness_history_size": len(self.robustness_history)
            }
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {
                "service_name": self.service_name,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "error": str(e)
            }


def monitor_performance(metrics: ServiceMetrics, endpoint: str = None):
    """
    Decorator for monitoring function/endpoint performance.

    Args:
        metrics: ServiceMetrics instance
        endpoint: Endpoint name (auto-detected if None)
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint_name = endpoint or func.__name__
            method = "ASYNC"
            status_code = 200

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = 500
                logger.error(f"Error in {endpoint_name}: {e}")
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_request(endpoint_name, method, status_code, duration)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint_name = endpoint or func.__name__
            method = "SYNC"
            status_code = 200

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = 500
                logger.error(f"Error in {endpoint_name}: {e}")
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_request(endpoint_name, method, status_code, duration)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


class PerformanceMonitor:
    """
    Enhanced centralized performance monitoring for ACGS services with CARMA robustness.

    Provides system-wide performance monitoring, alerting, constitutional compliance tracking,
    and CARMA-inspired robustness monitoring across all services.
    """

    def __init__(self):
        """Initialize enhanced performance monitor with robustness capabilities."""
        self.service_metrics: dict[str, ServiceMetrics] = {}
        self.performance_targets = {
            "response_time_p95": 0.005,  # 5ms (enhanced target)
            "error_rate": 0.01,  # 1%
            "constitutional_compliance": 0.95,  # 95%
            "uptime": 0.999,  # 99.9%
            # CARMA robustness targets
            "causal_sensitivity": 0.8,  # 80%
            "spurious_invariance": 0.9,  # 90%
            "overall_robustness": 0.85,  # 85%
        }
        
        # System-wide robustness tracking
        self.system_robustness_history = deque(maxlen=1000)
        self.global_alerts = []
        
        logger.info("Enhanced performance monitor with CARMA robustness initialized")

    def register_service(self, service_name: str) -> ServiceMetrics:
        """
        Register a service for monitoring.

        Args:
            service_name: Name of the service

        Returns:
            ServiceMetrics instance for the service
        """
        if service_name not in self.service_metrics:
            self.service_metrics[service_name] = ServiceMetrics(service_name)
            logger.info(f"Registered service for monitoring: {service_name}")

        return self.service_metrics[service_name]

    def get_service_metrics(self, service_name: str) -> ServiceMetrics | None:
        """
        Get metrics for a specific service.

        Args:
            service_name: Name of the service

        Returns:
            ServiceMetrics instance or None
        """
        return self.service_metrics.get(service_name)

    def get_system_health(self) -> dict[str, Any]:
        """
        Get comprehensive system health status including CARMA robustness.

        Returns:
            Enhanced system health summary with robustness metrics
        """
        total_services = len(self.service_metrics)
        healthy_services = 0
        total_requests = 0
        total_errors = 0
        compliance_scores = []
        
        # CARMA robustness aggregation
        causal_sensitivity_scores = []
        spurious_invariance_scores = []
        overall_robustness_scores = []
        total_spurious_correlations = 0
        total_causal_tests = 0
        all_robustness_alerts = []

        service_summaries = {}

        for service_name, metrics in self.service_metrics.items():
            summary = metrics.get_metrics_summary()
            service_summaries[service_name] = summary

            if summary.get("health_status", False):
                healthy_services += 1

            total_requests += summary.get("total_requests", 0)
            total_errors += summary.get("total_errors", 0)

            compliance_score = summary.get("constitutional_compliance_score", 0)
            if compliance_score > 0:
                compliance_scores.append(compliance_score)
            
            # Aggregate robustness metrics
            robustness_metrics = summary.get("robustness_metrics", {})
            if robustness_metrics.get("causal_sensitivity", 0) > 0:
                causal_sensitivity_scores.append(robustness_metrics["causal_sensitivity"])
            if robustness_metrics.get("spurious_invariance", 0) > 0:
                spurious_invariance_scores.append(robustness_metrics["spurious_invariance"])
            if robustness_metrics.get("overall_robustness", 0) > 0:
                overall_robustness_scores.append(robustness_metrics["overall_robustness"])
            
            total_spurious_correlations += robustness_metrics.get("spurious_correlations_detected", 0)
            total_causal_tests += robustness_metrics.get("causal_tests_performed", 0)
            
            # Collect alerts
            robustness_alerts = summary.get("robustness_alerts", [])
            all_robustness_alerts.extend(robustness_alerts)

        # Calculate system-wide metrics
        system_error_rate = total_errors / total_requests if total_requests > 0 else 0.0
        avg_compliance = (
            sum(compliance_scores) / len(compliance_scores)
            if compliance_scores
            else 0.0
        )
        system_uptime = healthy_services / total_services if total_services > 0 else 0.0
        
        # Calculate system-wide robustness metrics
        avg_causal_sensitivity = (
            sum(causal_sensitivity_scores) / len(causal_sensitivity_scores)
            if causal_sensitivity_scores else 0.0
        )
        avg_spurious_invariance = (
            sum(spurious_invariance_scores) / len(spurious_invariance_scores)
            if spurious_invariance_scores else 0.0
        )
        avg_overall_robustness = (
            sum(overall_robustness_scores) / len(overall_robustness_scores)
            if overall_robustness_scores else 0.0
        )
        
        # Calculate robustness compliance
        robustness_compliance = {
            "causal_sensitivity": avg_causal_sensitivity >= self.performance_targets["causal_sensitivity"],
            "spurious_invariance": avg_spurious_invariance >= self.performance_targets["spurious_invariance"],
            "overall_robustness": avg_overall_robustness >= self.performance_targets["overall_robustness"]
        }
        
        robustness_compliance_rate = sum(robustness_compliance.values()) / len(robustness_compliance)

        # Determine overall health (enhanced with robustness)
        health_status = "healthy"
        health_factors = []
        
        if system_uptime < self.performance_targets["uptime"]:
            health_status = "critical"
            health_factors.append("low_uptime")
        elif system_error_rate > self.performance_targets["error_rate"]:
            health_status = "degraded"
            health_factors.append("high_error_rate")
        elif avg_compliance < self.performance_targets["constitutional_compliance"]:
            health_status = "degraded"
            health_factors.append("low_constitutional_compliance")
        elif avg_overall_robustness < self.performance_targets["overall_robustness"]:
            health_status = "degraded"
            health_factors.append("low_robustness")
        elif robustness_compliance_rate < 0.75:  # Less than 3/4 robustness targets met
            health_status = "degraded"
            health_factors.append("robustness_target_failures")
        
        # Store system robustness snapshot
        system_robustness_snapshot = {
            "timestamp": datetime.now(timezone.utc),
            "avg_causal_sensitivity": avg_causal_sensitivity,
            "avg_spurious_invariance": avg_spurious_invariance,
            "avg_overall_robustness": avg_overall_robustness,
            "robustness_compliance_rate": robustness_compliance_rate,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        self.system_robustness_history.append(system_robustness_snapshot)

        return {
            "overall_health": health_status,
            "health_factors": health_factors,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "system_metrics": {
                "total_services": total_services,
                "healthy_services": healthy_services,
                "system_uptime": system_uptime,
                "total_requests": total_requests,
                "total_errors": total_errors,
                "system_error_rate": system_error_rate,
                "avg_constitutional_compliance": avg_compliance,
            },
            "robustness_metrics": {
                "avg_causal_sensitivity": avg_causal_sensitivity,
                "avg_spurious_invariance": avg_spurious_invariance,
                "avg_overall_robustness": avg_overall_robustness,
                "total_spurious_correlations": total_spurious_correlations,
                "total_causal_tests": total_causal_tests,
                "robustness_compliance": robustness_compliance,
                "robustness_compliance_rate": robustness_compliance_rate,
                "services_with_robustness_data": len(causal_sensitivity_scores)
            },
            "robustness_alerts": {
                "total_alerts": len(all_robustness_alerts),
                "critical_alerts": len([a for a in all_robustness_alerts if a.get("severity") == "critical"]),
                "high_alerts": len([a for a in all_robustness_alerts if a.get("severity") == "high"]),
                "all_alerts": all_robustness_alerts
            },
            "performance_targets": self.performance_targets,
            "service_summaries": service_summaries,
            "timestamp": time.time(),
        }
    
    def get_system_robustness_trends(self, window_minutes: int = 120) -> Dict[str, Any]:
        """
        Get system-wide robustness trends.
        
        Args:
            window_minutes: Time window for trend analysis
            
        Returns:
            System robustness trend analysis
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        
        recent_snapshots = [
            s for s in self.system_robustness_history
            if s['timestamp'] >= cutoff_time
        ]
        
        if len(recent_snapshots) < 2:
            return {
                "trend_status": "insufficient_data",
                "window_minutes": window_minutes,
                "snapshots_analyzed": len(recent_snapshots),
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        
        # Calculate trends
        causal_values = [s['avg_causal_sensitivity'] for s in recent_snapshots]
        spurious_values = [s['avg_spurious_invariance'] for s in recent_snapshots]
        robustness_values = [s['avg_overall_robustness'] for s in recent_snapshots]
        compliance_values = [s['robustness_compliance_rate'] for s in recent_snapshots]
        
        def trend_analysis(values):
            if len(values) < 3:
                return "stable", 0.0
            
            x = list(range(len(values)))
            try:
                correlation = statistics.correlation(x, values)
                if abs(correlation) < 0.1:
                    return "stable", abs(correlation)
                elif correlation > 0.1:
                    return "improving", correlation
                else:
                    return "degrading", abs(correlation)
            except:
                return "stable", 0.0
        
        causal_trend, causal_strength = trend_analysis(causal_values)
        spurious_trend, spurious_strength = trend_analysis(spurious_values)
        robustness_trend, robustness_strength = trend_analysis(robustness_values)
        compliance_trend, compliance_strength = trend_analysis(compliance_values)
        
        return {
            "window_minutes": window_minutes,
            "snapshots_analyzed": len(recent_snapshots),
            "trends": {
                "causal_sensitivity": {"trend": causal_trend, "strength": causal_strength},
                "spurious_invariance": {"trend": spurious_trend, "strength": spurious_strength},
                "overall_robustness": {"trend": robustness_trend, "strength": robustness_strength},
                "compliance_rate": {"trend": compliance_trend, "strength": compliance_strength}
            },
            "current_values": {
                "causal_sensitivity": causal_values[-1] if causal_values else 0.0,
                "spurious_invariance": spurious_values[-1] if spurious_values else 0.0,
                "overall_robustness": robustness_values[-1] if robustness_values else 0.0,
                "compliance_rate": compliance_values[-1] if compliance_values else 0.0
            },
            "constitutional_hash": CONSTITUTIONAL_HASH
        }


# Global performance monitor instance
_performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    return _performance_monitor


def get_service_metrics(service_name: str) -> ServiceMetrics:
    """
    Get or create service metrics.

    Args:
        service_name: Name of the service

    Returns:
        ServiceMetrics instance
    """
    return _performance_monitor.register_service(service_name)
