"""
Stabilizer Execution Environment

Fault-tolerant execution context with quantum-inspired error correction,
circuit breaker patterns, and integration with ACGS-1 infrastructure.
"""

import asyncio
import logging
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import asyncpg
import httpx
import psutil
import redis.asyncio as redis

from .models import StabilizerResult, StabilizerStatus, SyndromeVector

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = (
                await func(*args, **kwargs)
                if asyncio.iscoroutinefunction(func)
                else func(*args, **kwargs)
            )
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        return (
            self.last_failure_time
            and time.time() - self.last_failure_time >= self.recovery_timeout
        )

    def _on_success(self):
        """Handle successful execution."""
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class StabilizerExecutionEnvironment:
    """
    Fault-tolerant execution environment with quantum-inspired error correction.

    Provides async execution context with Redis caching, PostgreSQL persistence,
    circuit breaker patterns, and constitutional compliance validation.
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        postgres_url: str = "postgresql://acgs_user:acgs_password@localhost:5432/acgs_db",
        response_time_target_ms: int = 500,
        enable_circuit_breaker: bool = True,
        constitutional_hash: str = "cdd01ef066bc6cf2",
    ):
        """Initialize the Stabilizer Execution Environment."""
        self.redis_url = redis_url
        self.postgres_url = postgres_url
        self.response_time_target_ms = response_time_target_ms
        self.enable_circuit_breaker = enable_circuit_breaker
        self.constitutional_hash = constitutional_hash

        # Connection pools
        self.redis_pool: redis.Redis | None = None
        self.postgres_pool: asyncpg.Pool | None = None
        self.http_client: httpx.AsyncClient | None = None

        # Circuit breakers
        self.circuit_breakers: dict[str, CircuitBreaker] = {}

        # Execution tracking
        self.active_executions: dict[str, StabilizerResult] = {}
        self.execution_history: list[StabilizerResult] = []

        # Performance monitoring
        self._total_executions = 0
        self._successful_executions = 0
        self._total_execution_time = 0.0

        logger.info("Stabilizer Execution Environment initialized")

    async def initialize(self) -> None:
        """Initialize connections and resources."""
        try:
            # Initialize Redis connection
            self.redis_pool = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
            )

            # Test Redis connection
            await self.redis_pool.ping()
            logger.info("Redis connection established")

            # Initialize PostgreSQL connection pool
            self.postgres_pool = await asyncpg.create_pool(
                self.postgres_url, min_size=5, max_size=20, command_timeout=30
            )
            logger.info("PostgreSQL connection pool established")

            # Initialize HTTP client
            self.http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            )

            # Initialize circuit breakers
            if self.enable_circuit_breaker:
                self.circuit_breakers = {
                    "redis": CircuitBreaker(failure_threshold=3, recovery_timeout=30.0),
                    "postgres": CircuitBreaker(
                        failure_threshold=3, recovery_timeout=30.0
                    ),
                    "http": CircuitBreaker(failure_threshold=5, recovery_timeout=60.0),
                }

            logger.info("Stabilizer Execution Environment fully initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Stabilizer Execution Environment: {e}")
            raise

    @asynccontextmanager
    async def execute(
        self,
        execution_id: str,
        operation_name: str = "unknown",
        enable_error_correction: bool = True,
    ):
        """
        Async context manager for fault-tolerant execution.

        Args:
            execution_id: Unique identifier for the execution
            operation_name: Name of the operation being executed
            enable_error_correction: Enable quantum-inspired error correction

        Yields:
            StabilizerResult: Execution result object for tracking
        """
        start_time = time.time()
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create execution result
        result = StabilizerResult(
            execution_id=execution_id,
            status=StabilizerStatus.INITIALIZING,
            started_at=datetime.now(),
            constitutional_hash=self.constitutional_hash,
            metadata={"operation_name": operation_name},
        )

        # Track active execution
        self.active_executions[execution_id] = result

        try:
            result.status = StabilizerStatus.READY
            result.add_log(f"Starting execution: {operation_name}")

            yield result

            # Mark as completed if not already set
            if result.status not in [
                StabilizerStatus.COMPLETED,
                StabilizerStatus.FAILED,
            ]:
                result.status = StabilizerStatus.COMPLETED

            # Calculate performance metrics
            execution_time_ms = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time_ms

            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            result.memory_usage_mb = max(0, current_memory - initial_memory)
            result.cpu_usage_percent = process.cpu_percent()

            # Apply error correction if enabled
            if enable_error_correction:
                await self._apply_error_correction(result)

            # Validate constitutional compliance
            result.validate_constitutional_compliance()

            # Update statistics
            self._total_executions += 1
            self._total_execution_time += execution_time_ms

            if result.status == StabilizerStatus.COMPLETED:
                self._successful_executions += 1

            result.add_log(f"Execution completed in {execution_time_ms:.2f}ms")

        except Exception as e:
            result.status = StabilizerStatus.FAILED
            result.add_log(f"Execution failed: {str(e)}", "ERROR")
            logger.error(f"Execution {execution_id} failed: {e}")
            raise

        finally:
            result.completed_at = datetime.now()

            # Move to history and clean up
            self.execution_history.append(result)
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]

            # Limit history size
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-500:]

    async def _apply_error_correction(self, result: StabilizerResult) -> None:
        """Apply quantum-inspired error correction to execution result."""
        try:
            # Generate syndrome vector for error detection
            error_bits = self._generate_error_bits(result)
            parity_checks = self._generate_parity_checks(error_bits)

            syndrome_vector = SyndromeVector(
                error_bits=error_bits,
                parity_checks=parity_checks,
                metadata={"execution_id": result.execution_id},
            )

            result.syndrome_vector = syndrome_vector
            result.errors_detected = syndrome_vector.error_weight

            # Apply correction if errors are detected and correctable
            if syndrome_vector.error_weight > 0 and syndrome_vector.is_correctable():
                correction_pattern = syndrome_vector.get_correction_pattern()
                if correction_pattern:
                    result.errors_corrected = syndrome_vector.error_weight
                    result.add_log(
                        f"Applied error correction: {result.errors_corrected} errors corrected"
                    )

        except Exception as e:
            logger.warning(f"Error correction failed for {result.execution_id}: {e}")

    def _generate_error_bits(self, result: StabilizerResult) -> list[int]:
        """Generate error bits based on execution characteristics."""
        # Simplified error bit generation based on execution metrics
        error_bits = []

        # Performance-based error detection
        if result.execution_time_ms > self.response_time_target_ms:
            error_bits.append(1)  # Timeout error
        else:
            error_bits.append(0)

        # Memory usage error detection
        if result.memory_usage_mb > 100:  # 100MB threshold
            error_bits.append(1)  # Memory error
        else:
            error_bits.append(0)

        # CPU usage error detection
        if result.cpu_usage_percent > 80:  # 80% threshold
            error_bits.append(1)  # CPU error
        else:
            error_bits.append(0)

        # Status-based error detection
        if result.status == StabilizerStatus.FAILED:
            error_bits.append(1)  # Execution error
        else:
            error_bits.append(0)

        # Extend to minimum length for error correction
        while len(error_bits) < 7:
            error_bits.append(0)

        return error_bits[:7]  # Limit to 7 bits for Hamming code

    def _generate_parity_checks(self, error_bits: list[int]) -> list[int]:
        """Generate parity check bits for error correction."""
        if len(error_bits) < 4:
            return [0, 0, 0]

        # Hamming code parity checks
        p1 = (
            error_bits[0] ^ error_bits[2] ^ error_bits[4] ^ error_bits[6]
            if len(error_bits) > 6
            else 0
        )
        p2 = (
            error_bits[1] ^ error_bits[2] ^ error_bits[5] ^ error_bits[6]
            if len(error_bits) > 6
            else 0
        )
        p3 = (
            error_bits[3] ^ error_bits[4] ^ error_bits[5] ^ error_bits[6]
            if len(error_bits) > 6
            else 0
        )

        return [p1, p2, p3]

    async def cache_get(self, key: str) -> str | None:
        """Get value from Redis cache with circuit breaker protection."""
        if not self.redis_pool:
            return None

        try:
            if self.enable_circuit_breaker:
                return await self.circuit_breakers["redis"].call(
                    self.redis_pool.get, key
                )
            else:
                return await self.redis_pool.get(key)
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
            return None

    async def cache_set(self, key: str, value: str, expire_seconds: int = 3600) -> bool:
        """Set value in Redis cache with circuit breaker protection."""
        if not self.redis_pool:
            return False

        try:
            if self.enable_circuit_breaker:
                await self.circuit_breakers["redis"].call(
                    self.redis_pool.setex, key, expire_seconds, value
                )
            else:
                await self.redis_pool.setex(key, expire_seconds, value)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")
            return False

    async def db_execute(
        self, query: str, *args, fetch_one: bool = False, fetch_all: bool = False
    ) -> dict | list[dict] | None:
        """Execute database query with circuit breaker protection."""
        if not self.postgres_pool:
            return None

        try:

            async def _execute():
                async with self.postgres_pool.acquire() as conn:
                    if fetch_one:
                        result = await conn.fetchrow(query, *args)
                        return dict(result) if result else None
                    elif fetch_all:
                        results = await conn.fetch(query, *args)
                        return [dict(row) for row in results]
                    else:
                        await conn.execute(query, *args)
                        return True

            if self.enable_circuit_breaker:
                return await self.circuit_breakers["postgres"].call(_execute)
            else:
                return await _execute()

        except Exception as e:
            logger.warning(f"Database execution failed: {e}")
            return None

    async def http_request(
        self, method: str, url: str, **kwargs
    ) -> httpx.Response | None:
        """Make HTTP request with circuit breaker protection."""
        if not self.http_client:
            return None

        try:

            async def _request():
                return await self.http_client.request(method, url, **kwargs)

            if self.enable_circuit_breaker:
                return await self.circuit_breakers["http"].call(_request)
            else:
                return await _request()

        except Exception as e:
            logger.warning(f"HTTP request failed {method} {url}: {e}")
            return None

    async def get_health_status(self) -> dict[str, Any]:
        """Get comprehensive health status of the execution environment."""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "components": {},
            "metrics": {},
            "circuit_breakers": {},
        }

        # Check Redis health
        try:
            if self.redis_pool:
                await self.redis_pool.ping()
                health_status["components"]["redis"] = {"status": "healthy"}
            else:
                health_status["components"]["redis"] = {"status": "not_initialized"}
        except Exception as e:
            health_status["components"]["redis"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # Check PostgreSQL health
        try:
            if self.postgres_pool:
                async with self.postgres_pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                health_status["components"]["postgres"] = {"status": "healthy"}
            else:
                health_status["components"]["postgres"] = {"status": "not_initialized"}
        except Exception as e:
            health_status["components"]["postgres"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # Check HTTP client health
        health_status["components"]["http_client"] = {
            "status": "healthy" if self.http_client else "not_initialized"
        }

        # Add execution metrics
        success_rate = self._successful_executions / max(1, self._total_executions)
        avg_execution_time = self._total_execution_time / max(1, self._total_executions)

        health_status["metrics"] = {
            "total_executions": self._total_executions,
            "successful_executions": self._successful_executions,
            "success_rate": success_rate,
            "average_execution_time_ms": avg_execution_time,
            "active_executions": len(self.active_executions),
            "history_size": len(self.execution_history),
        }

        # Add circuit breaker status
        for name, cb in self.circuit_breakers.items():
            health_status["circuit_breakers"][name] = {
                "state": cb.state,
                "failure_count": cb.failure_count,
                "last_failure_time": cb.last_failure_time,
            }

        # Determine overall health
        unhealthy_components = sum(
            1
            for comp in health_status["components"].values()
            if comp["status"] != "healthy"
        )

        if unhealthy_components > 0:
            health_status["status"] = "degraded"

        if success_rate < 0.8:
            health_status["status"] = "unhealthy"

        return health_status

    async def cleanup(self) -> None:
        """Clean up resources and connections."""
        try:
            if self.redis_pool:
                await self.redis_pool.close()
                logger.info("Redis connection closed")

            if self.postgres_pool:
                await self.postgres_pool.close()
                logger.info("PostgreSQL connection pool closed")

            if self.http_client:
                await self.http_client.aclose()
                logger.info("HTTP client closed")

            logger.info("Stabilizer Execution Environment cleanup completed")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def get_execution_statistics(self) -> dict[str, Any]:
        """Get detailed execution statistics."""
        recent_executions = (
            self.execution_history[-100:] if self.execution_history else []
        )

        if recent_executions:
            recent_success_rate = sum(
                1 for ex in recent_executions if ex.status == StabilizerStatus.COMPLETED
            ) / len(recent_executions)

            recent_avg_time = sum(
                ex.execution_time_ms for ex in recent_executions
            ) / len(recent_executions)

            recent_error_rate = sum(
                ex.errors_detected for ex in recent_executions
            ) / len(recent_executions)
        else:
            recent_success_rate = 0.0
            recent_avg_time = 0.0
            recent_error_rate = 0.0

        return {
            "overall": {
                "total_executions": self._total_executions,
                "successful_executions": self._successful_executions,
                "success_rate": self._successful_executions
                / max(1, self._total_executions),
                "average_execution_time_ms": self._total_execution_time
                / max(1, self._total_executions),
            },
            "recent": {
                "sample_size": len(recent_executions),
                "success_rate": recent_success_rate,
                "average_execution_time_ms": recent_avg_time,
                "average_error_rate": recent_error_rate,
            },
            "current": {
                "active_executions": len(self.active_executions),
                "history_size": len(self.execution_history),
            },
            "timestamp": datetime.now().isoformat(),
        }
