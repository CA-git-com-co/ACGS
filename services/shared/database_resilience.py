"""
ACGS-1 Database Resilience Framework
Phase 2 - Enterprise Scalability & Performance

Implements retry mechanisms, circuit breakers, and fallback mechanisms
for database connections to achieve >99.9% availability.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar, Union
import random

import asyncpg
from sqlalchemy.exc import (
    DisconnectionError,
    OperationalError,
    TimeoutError as SQLTimeoutError,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class RetryConfig:
    """Configuration for retry mechanisms."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    
    # Retryable exceptions
    retryable_exceptions: tuple = (
        ConnectionError,
        TimeoutError,
        OperationalError,
        DisconnectionError,
        SQLTimeoutError,
        asyncpg.ConnectionDoesNotExistError,
        asyncpg.ConnectionFailureError,
        asyncpg.InterfaceError,
    )


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: tuple = (
        ConnectionError,
        TimeoutError,
        OperationalError,
        DisconnectionError,
        SQLTimeoutError,
    )
    
    # Half-open state configuration
    half_open_max_calls: int = 3
    success_threshold: int = 2


@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics."""
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    state_changes: int = 0
    total_calls: int = 0
    
    # Performance metrics
    avg_response_time: float = 0.0
    last_response_times: list = field(default_factory=lambda: [])


class CircuitBreaker:
    """Circuit breaker implementation for database operations."""
    
    def __init__(self, config: CircuitBreakerConfig, name: str = "default"):
        self.config = config
        self.name = name
        self.state = CircuitBreakerState.CLOSED
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()
        
        logger.info(f"Circuit breaker '{name}' initialized with config: {config}")
    
    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection."""
        async with self._lock:
            self.stats.total_calls += 1
            
            # Check if circuit is open
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is OPEN"
                    )
            
            # Execute the function
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                
                # Record success
                execution_time = time.time() - start_time
                await self._record_success(execution_time)
                
                return result
                
            except self.config.expected_exception as e:
                # Record failure
                execution_time = time.time() - start_time
                await self._record_failure(execution_time)
                raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        if self.stats.last_failure_time is None:
            return True
        
        time_since_failure = time.time() - self.stats.last_failure_time
        return time_since_failure >= self.config.recovery_timeout
    
    def _transition_to_half_open(self):
        """Transition circuit breaker to half-open state."""
        self.state = CircuitBreakerState.HALF_OPEN
        self.stats.state_changes += 1
        logger.info(f"Circuit breaker '{self.name}' transitioned to HALF_OPEN")
    
    async def _record_success(self, execution_time: float):
        """Record successful operation."""
        self.stats.success_count += 1
        self._update_response_time(execution_time)
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            if self.stats.success_count >= self.config.success_threshold:
                self._transition_to_closed()
        elif self.state == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            self.stats.failure_count = 0
    
    async def _record_failure(self, execution_time: float):
        """Record failed operation."""
        self.stats.failure_count += 1
        self.stats.last_failure_time = time.time()
        self._update_response_time(execution_time)
        
        if self.state == CircuitBreakerState.CLOSED:
            if self.stats.failure_count >= self.config.failure_threshold:
                self._transition_to_open()
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self._transition_to_open()
    
    def _transition_to_closed(self):
        """Transition circuit breaker to closed state."""
        self.state = CircuitBreakerState.CLOSED
        self.stats.failure_count = 0
        self.stats.success_count = 0
        self.stats.state_changes += 1
        logger.info(f"Circuit breaker '{self.name}' transitioned to CLOSED")
    
    def _transition_to_open(self):
        """Transition circuit breaker to open state."""
        self.state = CircuitBreakerState.OPEN
        self.stats.success_count = 0
        self.stats.state_changes += 1
        logger.error(f"Circuit breaker '{self.name}' transitioned to OPEN")
    
    def _update_response_time(self, execution_time: float):
        """Update average response time."""
        self.stats.last_response_times.append(execution_time)
        
        # Keep only last 100 response times
        if len(self.stats.last_response_times) > 100:
            self.stats.last_response_times.pop(0)
        
        # Calculate average
        if self.stats.last_response_times:
            self.stats.avg_response_time = sum(self.stats.last_response_times) / len(self.stats.last_response_times)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.stats.failure_count,
            "success_count": self.stats.success_count,
            "total_calls": self.stats.total_calls,
            "state_changes": self.stats.state_changes,
            "avg_response_time": self.stats.avg_response_time,
            "last_failure_time": self.stats.last_failure_time,
        }


class RetryMechanism:
    """Retry mechanism with exponential backoff and jitter."""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    async def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                return await func(*args, **kwargs)
            
            except self.config.retryable_exceptions as e:
                last_exception = e
                
                if attempt == self.config.max_attempts - 1:
                    # Last attempt failed
                    logger.error(
                        f"All {self.config.max_attempts} retry attempts failed. "
                        f"Last error: {e}"
                    )
                    raise e
                
                # Calculate delay with exponential backoff and jitter
                delay = self._calculate_delay(attempt)
                
                logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                
                await asyncio.sleep(delay)
            
            except Exception as e:
                # Non-retryable exception
                logger.error(f"Non-retryable exception: {e}")
                raise e
        
        # This should never be reached, but just in case
        if last_exception:
            raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and optional jitter."""
        delay = self.config.base_delay * (self.config.exponential_base ** attempt)
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            # Add jitter (±25% of delay)
            jitter_range = delay * 0.25
            jitter = random.uniform(-jitter_range, jitter_range)
            delay += jitter
        
        return max(0, delay)


class DatabaseResilienceManager:
    """Manages database resilience with circuit breakers and retry mechanisms."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.retry_config = RetryConfig()
        self.circuit_breaker_config = CircuitBreakerConfig()
        
        # Initialize components
        self.retry_mechanism = RetryMechanism(self.retry_config)
        self.circuit_breaker = CircuitBreaker(
            self.circuit_breaker_config, 
            name=f"{service_name}_db"
        )
        
        logger.info(f"Database resilience manager initialized for {service_name}")
    
    @asynccontextmanager
    async def resilient_connection(self, connection_factory: Callable):
        """Get database connection with resilience mechanisms."""
        async def get_connection():
            return await connection_factory()
        
        # Use circuit breaker and retry mechanism
        connection = await self.circuit_breaker.call(
            self.retry_mechanism.execute,
            get_connection
        )
        
        try:
            yield connection
        finally:
            # Ensure connection is properly closed
            try:
                if hasattr(connection, 'close'):
                    await connection.close()
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
    
    async def execute_with_resilience(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute database operation with full resilience."""
        return await self.circuit_breaker.call(
            self.retry_mechanism.execute,
            func,
            *args,
            **kwargs
        )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of resilience components."""
        return {
            "service": self.service_name,
            "circuit_breaker": self.circuit_breaker.get_stats(),
            "retry_config": {
                "max_attempts": self.retry_config.max_attempts,
                "base_delay": self.retry_config.base_delay,
                "max_delay": self.retry_config.max_delay,
            },
            "status": "healthy" if self.circuit_breaker.state == CircuitBreakerState.CLOSED else "degraded"
        }


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# Global resilience managers for each service
_resilience_managers: Dict[str, DatabaseResilienceManager] = {}


def get_resilience_manager(service_name: str) -> DatabaseResilienceManager:
    """Get or create resilience manager for a service."""
    if service_name not in _resilience_managers:
        _resilience_managers[service_name] = DatabaseResilienceManager(service_name)
    
    return _resilience_managers[service_name]


def get_all_resilience_stats() -> Dict[str, Any]:
    """Get resilience statistics for all services."""
    return {
        service_name: manager.get_health_status()
        for service_name, manager in _resilience_managers.items()
    }


# Enhanced database connection wrapper with resilience
class ResilientDatabaseConnection:
    """Database connection wrapper with built-in resilience."""

    def __init__(self, service_name: str, connection_factory: Callable[[], Any]):
        self.service_name = service_name
        self.connection_factory = connection_factory
        self.resilience_manager = get_resilience_manager(service_name)
        self._connection = None

    async def connect(self):
        """Establish resilient database connection."""
        async with self.resilience_manager.resilient_connection(
            self.connection_factory
        ) as connection:
            self._connection = connection
            return connection

    async def execute_query(self, query: str, *args, **kwargs):
        """Execute query with resilience."""
        async def _execute():
            if not self._connection:
                await self.connect()
            return await self._connection.execute(query, *args, **kwargs)

        return await self.resilience_manager.execute_with_resilience(_execute)

    async def fetch_one(self, query: str, *args, **kwargs):
        """Fetch one record with resilience."""
        async def _fetch():
            if not self._connection:
                await self.connect()
            return await self._connection.fetchrow(query, *args, **kwargs)

        return await self.resilience_manager.execute_with_resilience(_fetch)

    async def fetch_all(self, query: str, *args, **kwargs):
        """Fetch all records with resilience."""
        async def _fetch():
            if not self._connection:
                await self.connect()
            return await self._connection.fetch(query, *args, **kwargs)

        return await self.resilience_manager.execute_with_resilience(_fetch)

    async def close(self):
        """Close connection safely."""
        if self._connection:
            try:
                await self._connection.close()
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
            finally:
                self._connection = None
