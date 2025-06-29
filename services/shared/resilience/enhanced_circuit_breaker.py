"""
Enhanced Circuit Breaker Implementation for ACGS
Provides advanced circuit breaker patterns with constitutional compliance integration.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import numpy as np
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_max_calls: int = 3
    success_threshold: int = 2
    timeout: float = 30.0
    
    # Advanced configuration
    failure_rate_threshold: float = 0.5  # 50% failure rate
    minimum_requests: int = 10
    sliding_window_size: int = 100
    constitutional_compliance_threshold: float = 0.95

@dataclass
class CallResult:
    """Result of a circuit breaker call."""
    success: bool
    duration: float
    error: Optional[Exception] = None
    constitutional_compliance_score: Optional[float] = None
    timestamp: float = field(default_factory=time.time)

class EnhancedCircuitBreaker:
    """Enhanced circuit breaker with constitutional compliance integration."""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        
        # State tracking
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        self.half_open_calls = 0
        
        # Sliding window for failure rate calculation
        self.call_results: List[CallResult] = []
        
        # Metrics
        self.setup_metrics()
        
        logger.info(f"Enhanced circuit breaker '{name}' initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics."""
        self.calls_total = Counter(
            'circuit_breaker_calls_total',
            'Total circuit breaker calls',
            ['name', 'state', 'result']
        )
        
        self.state_gauge = Gauge(
            'circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half_open)',
            ['name']
        )
        
        self.failure_rate = Gauge(
            'circuit_breaker_failure_rate',
            'Circuit breaker failure rate',
            ['name']
        )
        
        self.call_duration = Histogram(
            'circuit_breaker_call_duration_seconds',
            'Circuit breaker call duration',
            ['name', 'result']
        )

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if not self.can_execute():
            self.calls_total.labels(
                name=self.name, 
                state=self.state.value, 
                result='rejected'
            ).inc()
            raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is open")
        
        start_time = time.time()
        
        try:
            # Execute the function with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs) if asyncio.iscoroutinefunction(func) 
                else func(*args, **kwargs),
                timeout=self.config.timeout
            )
            
            duration = time.time() - start_time
            
            # Check constitutional compliance if result has compliance score
            compliance_score = None
            if hasattr(result, 'constitutional_compliance_score'):
                compliance_score = result.constitutional_compliance_score
            
            call_result = CallResult(
                success=True,
                duration=duration,
                constitutional_compliance_score=compliance_score
            )
            
            await self.on_success(call_result)
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            call_result = CallResult(
                success=False,
                duration=duration,
                error=e
            )
            
            await self.on_failure(call_result)
            raise

    def can_execute(self) -> bool:
        """Check if the circuit breaker allows execution."""
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                self.update_state_metrics()
                logger.info(f"Circuit breaker '{self.name}' moved to HALF_OPEN")
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.config.half_open_max_calls
        
        return False

    async def on_success(self, call_result: CallResult):
        """Handle successful call."""
        self.call_results.append(call_result)
        self.trim_call_results()
        
        # Update metrics
        self.calls_total.labels(
            name=self.name, 
            state=self.state.value, 
            result='success'
        ).inc()
        
        self.call_duration.labels(
            name=self.name, 
            result='success'
        ).observe(call_result.duration)
        
        # Check constitutional compliance
        if (call_result.constitutional_compliance_score is not None and
            call_result.constitutional_compliance_score < self.config.constitutional_compliance_threshold):
            logger.warning(
                f"Constitutional compliance violation in circuit breaker '{self.name}': "
                f"{call_result.constitutional_compliance_score:.2%}"
            )
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            self.half_open_calls += 1
            
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.update_state_metrics()
                logger.info(f"Circuit breaker '{self.name}' moved to CLOSED")
        else:
            self.failure_count = 0
        
        self.update_failure_rate()

    async def on_failure(self, call_result: CallResult):
        """Handle failed call."""
        self.call_results.append(call_result)
        self.trim_call_results()
        
        # Update metrics
        self.calls_total.labels(
            name=self.name, 
            state=self.state.value, 
            result='failure'
        ).inc()
        
        self.call_duration.labels(
            name=self.name, 
            result='failure'
        ).observe(call_result.duration)
        
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.half_open_calls = 0
            self.update_state_metrics()
            logger.warning(f"Circuit breaker '{self.name}' moved to OPEN (half-open failure)")
        elif self.should_open():
            self.state = CircuitState.OPEN
            self.update_state_metrics()
            logger.warning(f"Circuit breaker '{self.name}' moved to OPEN")
        
        self.update_failure_rate()

    def should_open(self) -> bool:
        """Determine if circuit breaker should open."""
        # Check failure count threshold
        if self.failure_count >= self.config.failure_threshold:
            return True
        
        # Check failure rate threshold
        if len(self.call_results) >= self.config.minimum_requests:
            failure_rate = self.calculate_failure_rate()
            if failure_rate >= self.config.failure_rate_threshold:
                return True
        
        return False

    def calculate_failure_rate(self) -> float:
        """Calculate current failure rate."""
        if not self.call_results:
            return 0.0
        
        recent_results = self.call_results[-self.config.minimum_requests:]
        failures = sum(1 for result in recent_results if not result.success)
        
        return failures / len(recent_results)

    def trim_call_results(self):
        """Trim call results to sliding window size."""
        if len(self.call_results) > self.config.sliding_window_size:
            self.call_results = self.call_results[-self.config.sliding_window_size:]

    def update_state_metrics(self):
        """Update state metrics."""
        state_values = {
            CircuitState.CLOSED: 0,
            CircuitState.OPEN: 1,
            CircuitState.HALF_OPEN: 2
        }
        self.state_gauge.labels(name=self.name).set(state_values[self.state])

    def update_failure_rate(self):
        """Update failure rate metric."""
        failure_rate = self.calculate_failure_rate()
        self.failure_rate.labels(name=self.name).set(failure_rate)

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'failure_rate': self.calculate_failure_rate(),
            'total_calls': len(self.call_results),
            'last_failure_time': self.last_failure_time,
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'recovery_timeout': self.config.recovery_timeout,
                'failure_rate_threshold': self.config.failure_rate_threshold,
                'constitutional_compliance_threshold': self.config.constitutional_compliance_threshold
            }
        }

    def reset(self):
        """Reset circuit breaker to closed state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
        self.call_results.clear()
        self.update_state_metrics()
        self.update_failure_rate()
        logger.info(f"Circuit breaker '{self.name}' reset to CLOSED")

class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass

class CircuitBreakerManager:
    """Manages multiple circuit breakers."""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, EnhancedCircuitBreaker] = {}
        
    def get_circuit_breaker(self, name: str, 
                          config: Optional[CircuitBreakerConfig] = None) -> EnhancedCircuitBreaker:
        """Get or create circuit breaker."""
        if name not in self.circuit_breakers:
            if config is None:
                config = CircuitBreakerConfig()
            self.circuit_breakers[name] = EnhancedCircuitBreaker(name, config)
        
        return self.circuit_breakers[name]
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers."""
        return {name: cb.get_stats() for name, cb in self.circuit_breakers.items()}
    
    def reset_all(self):
        """Reset all circuit breakers."""
        for cb in self.circuit_breakers.values():
            cb.reset()

# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()
