"""
Enhanced Circuit Breaker for LLM Operations

This module provides advanced circuit breaker patterns specifically designed
for LLM operations with adaptive thresholds, predictive failure detection,
and intelligent recovery mechanisms.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

try:
    from prometheus_client import Counter, Gauge, Histogram
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, requests blocked
    HALF_OPEN = "half_open"  # Testing recovery


class FailureType(Enum):
    """Types of LLM failures."""
    TIMEOUT = "timeout"
    API_ERROR = "api_error"
    RATE_LIMIT = "rate_limit"
    INVALID_RESPONSE = "invalid_response"
    BIAS_DETECTED = "bias_detected"
    LOW_CONFIDENCE = "low_confidence"
    SEMANTIC_FAILURE = "semantic_failure"


@dataclass
class CircuitBreakerConfig:
    """Configuration for LLM circuit breaker."""
    
    # Basic thresholds
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    success_threshold: int = 3  # for half-open state
    
    # Advanced thresholds
    timeout_threshold: float = 30.0  # seconds
    error_rate_threshold: float = 0.5  # 50% error rate
    confidence_threshold: float = 0.8  # minimum confidence
    
    # Adaptive behavior
    adaptive_thresholds: bool = True
    learning_window: int = 100  # requests to consider for adaptation
    max_failure_threshold: int = 20
    min_failure_threshold: int = 2
    
    # Recovery strategies
    exponential_backoff: bool = True
    max_backoff_time: int = 300  # 5 minutes
    jitter_enabled: bool = True


@dataclass
class FailureRecord:
    """Record of a failure event."""
    
    timestamp: datetime
    failure_type: FailureType
    model_name: str
    error_message: str
    response_time: float
    confidence_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CircuitMetrics:
    """Metrics for circuit breaker performance."""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    blocked_requests: int = 0
    
    # Timing metrics
    average_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    
    # Failure analysis
    failure_by_type: Dict[FailureType, int] = field(default_factory=dict)
    recent_failures: List[FailureRecord] = field(default_factory=list)
    
    # State transitions
    state_transitions: List[Dict[str, Any]] = field(default_factory=list)
    time_in_open_state: float = 0.0
    time_in_half_open_state: float = 0.0


class LLMCircuitBreaker:
    """Advanced circuit breaker for LLM operations."""
    
    def __init__(self, model_name: str, config: CircuitBreakerConfig):
        self.model_name = model_name
        self.config = config
        self.state = CircuitState.CLOSED
        self.metrics = CircuitMetrics()
        
        # State management
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state_changed_at = datetime.utcnow()
        
        # Adaptive thresholds
        self.current_failure_threshold = config.failure_threshold
        self.response_times: List[float] = []
        
        # Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            self._setup_prometheus_metrics()
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for monitoring."""
        self.request_counter = Counter(
            f"llm_circuit_breaker_requests_total",
            "Total requests through circuit breaker",
            ["model", "state", "result"]
        )
        
        self.state_gauge = Gauge(
            f"llm_circuit_breaker_state",
            "Current circuit breaker state (0=closed, 1=half_open, 2=open)",
            ["model"]
        )
        
        self.failure_rate_gauge = Gauge(
            f"llm_circuit_breaker_failure_rate",
            "Current failure rate",
            ["model"]
        )
        
        self.response_time_histogram = Histogram(
            f"llm_circuit_breaker_response_time_seconds",
            "Response time through circuit breaker",
            ["model"]
        )
    
    async def call(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation through circuit breaker."""
        start_time = time.time()
        
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if not self._should_attempt_reset():
                self.metrics.blocked_requests += 1
                if PROMETHEUS_AVAILABLE:
                    self.request_counter.labels(
                        model=self.model_name, 
                        state="open", 
                        result="blocked"
                    ).inc()
                raise CircuitBreakerOpenError(f"Circuit breaker open for {self.model_name}")
            else:
                # Transition to half-open
                await self._transition_to_half_open()
        
        # Execute operation
        try:
            result = await operation(*args, **kwargs)
            response_time = time.time() - start_time
            
            # Record success
            await self._record_success(response_time)
            
            # Check if we should close the circuit (if half-open)
            if self.state == CircuitState.HALF_OPEN:
                if self.success_count >= self.config.success_threshold:
                    await self._transition_to_closed()
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            
            # Classify failure type
            failure_type = self._classify_failure(e, response_time)
            
            # Record failure
            await self._record_failure(failure_type, str(e), response_time)
            
            # Check if we should open the circuit
            if self._should_open_circuit():
                await self._transition_to_open()
            
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt to reset."""
        if not self.last_failure_time:
            return True
        
        # Calculate backoff time
        backoff_time = self.config.recovery_timeout
        if self.config.exponential_backoff:
            # Exponential backoff based on consecutive failures
            backoff_time = min(
                self.config.recovery_timeout * (2 ** min(self.failure_count, 10)),
                self.config.max_backoff_time
            )
        
        # Add jitter if enabled
        if self.config.jitter_enabled:
            import random
            jitter = random.uniform(0.8, 1.2)
            backoff_time *= jitter
        
        time_since_failure = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return time_since_failure >= backoff_time
    
    def _classify_failure(self, exception: Exception, response_time: float) -> FailureType:
        """Classify the type of failure."""
        error_message = str(exception).lower()
        
        if response_time > self.config.timeout_threshold:
            return FailureType.TIMEOUT
        elif "rate limit" in error_message or "429" in error_message:
            return FailureType.RATE_LIMIT
        elif "api" in error_message or "http" in error_message:
            return FailureType.API_ERROR
        elif "bias" in error_message:
            return FailureType.BIAS_DETECTED
        elif "confidence" in error_message:
            return FailureType.LOW_CONFIDENCE
        elif "semantic" in error_message:
            return FailureType.SEMANTIC_FAILURE
        else:
            return FailureType.INVALID_RESPONSE
    
    async def _record_success(self, response_time: float):
        """Record a successful operation."""
        self.metrics.total_requests += 1
        self.metrics.successful_requests += 1
        self.success_count += 1
        self.failure_count = 0  # Reset failure count on success
        
        # Update response time metrics
        self.response_times.append(response_time)
        if len(self.response_times) > self.config.learning_window:
            self.response_times.pop(0)
        
        self._update_response_time_metrics()
        
        # Update Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            self.request_counter.labels(
                model=self.model_name, 
                state=self.state.value, 
                result="success"
            ).inc()
            self.response_time_histogram.labels(model=self.model_name).observe(response_time)
        
        # Adaptive threshold adjustment
        if self.config.adaptive_thresholds:
            await self._adjust_thresholds()
    
    async def _record_failure(self, failure_type: FailureType, error_message: str, response_time: float):
        """Record a failed operation."""
        self.metrics.total_requests += 1
        self.metrics.failed_requests += 1
        self.failure_count += 1
        self.success_count = 0  # Reset success count on failure
        self.last_failure_time = datetime.utcnow()
        
        # Record failure details
        failure_record = FailureRecord(
            timestamp=datetime.utcnow(),
            failure_type=failure_type,
            model_name=self.model_name,
            error_message=error_message,
            response_time=response_time
        )
        
        self.metrics.recent_failures.append(failure_record)
        if len(self.metrics.recent_failures) > 50:  # Keep last 50 failures
            self.metrics.recent_failures.pop(0)
        
        # Update failure type counts
        if failure_type not in self.metrics.failure_by_type:
            self.metrics.failure_by_type[failure_type] = 0
        self.metrics.failure_by_type[failure_type] += 1
        
        # Update Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            self.request_counter.labels(
                model=self.model_name, 
                state=self.state.value, 
                result="failure"
            ).inc()
            
            failure_rate = self.metrics.failed_requests / self.metrics.total_requests
            self.failure_rate_gauge.labels(model=self.model_name).set(failure_rate)
        
        logger.warning(f"LLM Circuit Breaker failure for {self.model_name}: {failure_type.value} - {error_message}")
    
    def _should_open_circuit(self) -> bool:
        """Determine if circuit should be opened."""
        # Check failure count threshold
        if self.failure_count >= self.current_failure_threshold:
            return True
        
        # Check error rate threshold
        if self.metrics.total_requests >= 10:  # Minimum requests for rate calculation
            error_rate = self.metrics.failed_requests / self.metrics.total_requests
            if error_rate >= self.config.error_rate_threshold:
                return True
        
        return False
    
    async def _transition_to_open(self):
        """Transition circuit to open state."""
        old_state = self.state
        self.state = CircuitState.OPEN
        self.state_changed_at = datetime.utcnow()
        
        self.metrics.state_transitions.append({
            "from": old_state.value,
            "to": self.state.value,
            "timestamp": self.state_changed_at.isoformat(),
            "failure_count": self.failure_count
        })
        
        if PROMETHEUS_AVAILABLE:
            self.state_gauge.labels(model=self.model_name).set(2)  # 2 = open
        
        logger.warning(f"Circuit breaker OPENED for {self.model_name} after {self.failure_count} failures")
    
    async def _transition_to_half_open(self):
        """Transition circuit to half-open state."""
        old_state = self.state
        self.state = CircuitState.HALF_OPEN
        self.state_changed_at = datetime.utcnow()
        self.success_count = 0
        
        self.metrics.state_transitions.append({
            "from": old_state.value,
            "to": self.state.value,
            "timestamp": self.state_changed_at.isoformat()
        })
        
        if PROMETHEUS_AVAILABLE:
            self.state_gauge.labels(model=self.model_name).set(1)  # 1 = half-open
        
        logger.info(f"Circuit breaker HALF-OPEN for {self.model_name}, testing recovery")
    
    async def _transition_to_closed(self):
        """Transition circuit to closed state."""
        old_state = self.state
        self.state = CircuitState.CLOSED
        self.state_changed_at = datetime.utcnow()
        self.failure_count = 0
        
        self.metrics.state_transitions.append({
            "from": old_state.value,
            "to": self.state.value,
            "timestamp": self.state_changed_at.isoformat(),
            "success_count": self.success_count
        })
        
        if PROMETHEUS_AVAILABLE:
            self.state_gauge.labels(model=self.model_name).set(0)  # 0 = closed
        
        logger.info(f"Circuit breaker CLOSED for {self.model_name}, normal operation resumed")
    
    async def _adjust_thresholds(self):
        """Adaptively adjust failure thresholds based on performance."""
        if len(self.response_times) < 20:  # Need sufficient data
            return
        
        # Calculate performance metrics
        avg_response_time = sum(self.response_times) / len(self.response_times)
        recent_error_rate = self.metrics.failed_requests / max(self.metrics.total_requests, 1)
        
        # Adjust failure threshold based on performance
        if avg_response_time < 5.0 and recent_error_rate < 0.1:
            # Good performance, can be more tolerant
            self.current_failure_threshold = min(
                self.current_failure_threshold + 1,
                self.config.max_failure_threshold
            )
        elif avg_response_time > 15.0 or recent_error_rate > 0.3:
            # Poor performance, be more strict
            self.current_failure_threshold = max(
                self.current_failure_threshold - 1,
                self.config.min_failure_threshold
            )
    
    def _update_response_time_metrics(self):
        """Update response time percentile metrics."""
        if not self.response_times:
            return
        
        sorted_times = sorted(self.response_times)
        n = len(sorted_times)
        
        self.metrics.average_response_time = sum(sorted_times) / n
        self.metrics.p95_response_time = sorted_times[int(n * 0.95)] if n > 0 else 0
        self.metrics.p99_response_time = sorted_times[int(n * 0.99)] if n > 0 else 0
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status of the circuit breaker."""
        return {
            "model_name": self.model_name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "current_failure_threshold": self.current_failure_threshold,
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "success_rate": self.metrics.successful_requests / max(self.metrics.total_requests, 1),
                "average_response_time": self.metrics.average_response_time,
                "p95_response_time": self.metrics.p95_response_time,
                "recent_failures": len(self.metrics.recent_failures)
            },
            "last_state_change": self.state_changed_at.isoformat()
        }


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class LLMCircuitBreakerManager:
    """Manager for multiple LLM circuit breakers."""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, LLMCircuitBreaker] = {}
        self.default_config = CircuitBreakerConfig()
    
    def get_circuit_breaker(self, model_name: str, config: Optional[CircuitBreakerConfig] = None) -> LLMCircuitBreaker:
        """Get or create circuit breaker for a model."""
        if model_name not in self.circuit_breakers:
            breaker_config = config or self.default_config
            self.circuit_breakers[model_name] = LLMCircuitBreaker(model_name, breaker_config)
        
        return self.circuit_breakers[model_name]
    
    def get_all_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all circuit breakers."""
        return {
            model_name: breaker.get_health_status()
            for model_name, breaker in self.circuit_breakers.items()
        }
    
    async def reset_circuit_breaker(self, model_name: str):
        """Manually reset a circuit breaker."""
        if model_name in self.circuit_breakers:
            breaker = self.circuit_breakers[model_name]
            await breaker._transition_to_closed()
            logger.info(f"Manually reset circuit breaker for {model_name}")


# Global circuit breaker manager
_circuit_breaker_manager: Optional[LLMCircuitBreakerManager] = None


def get_circuit_breaker_manager() -> LLMCircuitBreakerManager:
    """Get the global circuit breaker manager."""
    global _circuit_breaker_manager
    if _circuit_breaker_manager is None:
        _circuit_breaker_manager = LLMCircuitBreakerManager()
    return _circuit_breaker_manager
