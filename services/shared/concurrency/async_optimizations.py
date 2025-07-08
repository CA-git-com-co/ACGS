"""
Async Optimizations for High Throughput
Constitutional hash: cdd01ef066bc6cf2

High-performance async patterns with:
- asyncio.gather for concurrent operations
- HTTPX connection pooling optimization
- Request batching and rate limiting
- Circuit breaker pattern
"""

import asyncio
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

import httpx
import structlog
from httpx import Limits, Timeout

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = structlog.get_logger()


@dataclass
class ThroughputMetrics:
    """Throughput performance metrics."""
    requests_completed: int = 0
    requests_failed: int = 0
    total_latency: float = 0.0
    max_latency: float = 0.0
    min_latency: float = float("inf")
    start_time: float = 0.0
    constitutional_hash: str = CONSTITUTIONAL_HASH

    def record_request(self, latency: float, success: bool = True):
        """Record a request completion."""
        if success:
            self.requests_completed += 1
        else:
            self.requests_failed += 1

        self.total_latency += latency
        self.max_latency = max(self.max_latency, latency)
        self.min_latency = min(self.min_latency, latency)

    def get_stats(self) -> dict[str, Any]:
        """Get throughput statistics."""
        total_requests = self.requests_completed + self.requests_failed
        elapsed_time = time.time() - self.start_time

        return {
            "total_requests": total_requests,
            "successful_requests": self.requests_completed,
            "failed_requests": self.requests_failed,
            "success_rate": (
                (self.requests_completed / total_requests * 100)
                if total_requests > 0 else 0
            ),
            "avg_latency": (
                (self.total_latency / total_requests)
                if total_requests > 0 else 0
            ),
            "max_latency": self.max_latency if self.max_latency != 0 else 0,
            "min_latency": self.min_latency if self.min_latency != float("inf") else 0,
            "throughput_rps": (
                (total_requests / elapsed_time)
                if elapsed_time > 0 else 0
            ),
            "constitutional_hash": self.constitutional_hash
        }


class OptimizedHTTPXClient:
    """Optimized HTTPX client with connection pooling."""

    def __init__(
        self,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: int = 5,
        timeout: float = 30.0,
        retries: int = 3
    ):
        self.max_connections = max_connections
        self.max_keepalive_connections = max_keepalive_connections
        self.keepalive_expiry = keepalive_expiry
        self.timeout = timeout
        self.retries = retries
        self.constitutional_hash = CONSTITUTIONAL_HASH

        # Configure optimized limits
        self.limits = Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry
        )

        # Configure timeout
        self.timeout_config = Timeout(
            connect=5.0,
            read=timeout,
            write=timeout,
            pool=timeout
        )

        self.client: httpx.AsyncClient | None = None
        self.metrics = ThroughputMetrics()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def initialize(self):
        """Initialize the optimized HTTP client."""

        self.client = httpx.AsyncClient(
            limits=self.limits,
            timeout=self.timeout_config,
            headers={
                "User-Agent": f"ACGS-Optimized/{CONSTITUTIONAL_HASH}",
                "X-Constitutional-Hash": self.constitutional_hash
            },
            # HTTP/2 support for better performance
            http2=True,
            # Keep connections alive
            verify=True
        )

        self.metrics.start_time = time.time()

        logger.info(
            "Optimized HTTPX client initialized",
            max_connections=self.max_connections,
            constitutional_hash=self.constitutional_hash
        )

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()

        logger.info(
            "HTTPX client closed",
            constitutional_hash=self.constitutional_hash
        )

    async def request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request with retry logic."""

        for attempt in range(self.retries + 1):
            start_time = time.time()

            try:
                response = await self.client.request(method, url, **kwargs)
                latency = time.time() - start_time

                # Record successful request
                self.metrics.record_request(latency, success=True)

                # Check for HTTP errors
                response.raise_for_status()

                return response

            except httpx.HTTPStatusError as e:
                latency = time.time() - start_time
                self.metrics.record_request(latency, success=False)

                if attempt == self.retries:
                    logger.error(
                        "HTTP request failed after retries",
                        url=url,
                        status_code=e.response.status_code,
                        constitutional_hash=self.constitutional_hash
                    )
                    raise

                await asyncio.sleep(2 ** attempt)  # Exponential backoff

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                latency = time.time() - start_time
                self.metrics.record_request(latency, success=False)

                if attempt == self.retries:
                    logger.error(
                        "HTTP connection failed after retries",
                        url=url,
                        error=str(e),
                        constitutional_hash=self.constitutional_hash
                    )
                    raise

                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """GET request with optimization."""
        return await self.request_with_retry("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        """POST request with optimization."""
        return await self.request_with_retry("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> httpx.Response:
        """PUT request with optimization."""
        return await self.request_with_retry("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """DELETE request with optimization."""
        return await self.request_with_retry("DELETE", url, **kwargs)

    def get_metrics(self) -> dict[str, Any]:
        """Get client performance metrics."""
        return self.metrics.get_stats()


class ConcurrentRequestBatcher:
    """Batch and execute concurrent requests efficiently."""

    def __init__(
        self,
        max_concurrent: int = 50,
        batch_size: int = 100,
        rate_limit_rps: float | None = None
    ):
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.rate_limit_rps = rate_limit_rps
        self.constitutional_hash = CONSTITUTIONAL_HASH

        # Rate limiting
        self.last_request_time = 0.0
        self.request_interval = 1.0 / rate_limit_rps if rate_limit_rps else 0.0

        # Semaphore for concurrency control
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def _rate_limited_request(self, request_func: Callable) -> Any:
        """Execute request with rate limiting."""

        # Rate limiting
        if self.request_interval > 0:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time

            if time_since_last < self.request_interval:
                await asyncio.sleep(self.request_interval - time_since_last)

            self.last_request_time = time.time()

        # Concurrency limiting
        async with self.semaphore:
            return await request_func()

    async def execute_batch(
        self,
        request_functions: list[Callable],
        return_exceptions: bool = True
    ) -> list[Any]:
        """Execute batch of requests concurrently."""

        start_time = time.time()

        # Create rate-limited tasks
        tasks = [
            self._rate_limited_request(func)
            for func in request_functions
        ]

        # Execute with asyncio.gather for optimal concurrency
        results = await asyncio.gather(*tasks, return_exceptions=return_exceptions)

        execution_time = time.time() - start_time

        logger.info(
            "Concurrent batch executed",
            batch_size=len(request_functions),
            execution_time=execution_time,
            throughput=len(request_functions) / execution_time,
            constitutional_hash=self.constitutional_hash
        )

        return results

    async def execute_batches(
        self,
        request_functions: list[Callable],
        return_exceptions: bool = True
    ) -> list[Any]:
        """Execute large list of requests in optimized batches."""

        all_results = []

        # Process in batches
        for i in range(0, len(request_functions), self.batch_size):
            batch = request_functions[i:i + self.batch_size]
            batch_results = await self.execute_batch(batch, return_exceptions)
            all_results.extend(batch_results)

        return all_results


class CircuitBreaker:
    """Circuit breaker pattern for resilient async operations."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.constitutional_hash = CONSTITUTIONAL_HASH

        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker."""

        # Check if circuit is open
        if self.state == "OPEN":
            if time.time() - self.last_failure_time < self.recovery_timeout:
                raise Exception(f"Circuit breaker OPEN - {self.constitutional_hash}")
            self.state = "HALF_OPEN"

        try:
            result = await func(*args, **kwargs)

            # Success - reset circuit
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0

            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.warning(
                    "Circuit breaker opened",
                    failure_count=self.failure_count,
                    constitutional_hash=self.constitutional_hash
                )

            raise e


class AsyncTaskManager:
    """Manage and optimize async task execution."""

    def __init__(
        self,
        max_concurrent_tasks: int = 100,
        task_timeout: float = 30.0
    ):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_timeout = task_timeout
        self.constitutional_hash = CONSTITUTIONAL_HASH

        self.active_tasks: list[asyncio.Task] = []
        self.completed_tasks = 0
        self.failed_tasks = 0

    async def execute_tasks(
        self,
        task_functions: list[Callable],
        return_exceptions: bool = True
    ) -> list[Any]:
        """Execute tasks with optimal concurrency management."""

        start_time = time.time()

        # Create tasks with timeout
        tasks = []
        for func in task_functions:
            task = asyncio.create_task(
                asyncio.wait_for(func(), timeout=self.task_timeout)
            )
            tasks.append(task)

        # Limit concurrent tasks
        semaphore = asyncio.Semaphore(self.max_concurrent_tasks)

        async def run_with_semaphore(task):
            async with semaphore:
                return await task

        # Execute with concurrency control
        limited_tasks = [run_with_semaphore(task) for task in tasks]
        results = await asyncio.gather(*limited_tasks, return_exceptions=return_exceptions)

        # Count successes and failures
        for result in results:
            if isinstance(result, Exception):
                self.failed_tasks += 1
            else:
                self.completed_tasks += 1

        execution_time = time.time() - start_time

        logger.info(
            "Task batch completed",
            total_tasks=len(task_functions),
            completed_tasks=self.completed_tasks,
            failed_tasks=self.failed_tasks,
            execution_time=execution_time,
            constitutional_hash=self.constitutional_hash
        )

        return results

    async def execute_with_progress(
        self,
        task_functions: list[Callable],
        progress_callback: Callable[[int, int], None] | None = None
    ) -> list[Any]:
        """Execute tasks with progress reporting."""

        results = []
        completed = 0

        # Process in smaller batches for progress reporting
        batch_size = min(self.max_concurrent_tasks, 20)

        for i in range(0, len(task_functions), batch_size):
            batch = task_functions[i:i + batch_size]
            batch_results = await self.execute_tasks(batch)
            results.extend(batch_results)

            completed += len(batch)
            if progress_callback:
                progress_callback(completed, len(task_functions))

        return results


# Utility functions for common async patterns
async def gather_with_concurrency_limit(
    awaitables: list[Callable],
    limit: int = 50,
    return_exceptions: bool = True
) -> list[Any]:
    """Execute awaitables with concurrency limit using asyncio.gather."""

    semaphore = asyncio.Semaphore(limit)

    async def run_with_limit(awaitable):
        async with semaphore:
            return await awaitable()

    limited_awaitables = [run_with_limit(aw) for aw in awaitables]
    return await asyncio.gather(*limited_awaitables, return_exceptions=return_exceptions)


async def batch_process_with_gather(
    items: list[Any],
    processor: Callable,
    batch_size: int = 100,
    max_concurrent: int = 50
) -> list[Any]:
    """Process items in batches with optimal concurrency."""

    all_results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]

        # Create processing tasks for batch
        tasks = [lambda item=item: processor(item) for item in batch]

        # Execute batch with concurrency limit
        batch_results = await gather_with_concurrency_limit(
            tasks,
            limit=max_concurrent
        )

        all_results.extend(batch_results)

    return all_results


@asynccontextmanager
async def optimized_http_session(
    max_connections: int = 100,
    **kwargs
):
    """Context manager for optimized HTTP session."""

    async with OptimizedHTTPXClient(
        max_connections=max_connections,
        **kwargs
    ) as client:
        yield client


# Performance testing utilities
async def benchmark_concurrent_requests(
    urls: list[str],
    max_concurrent: int = 50,
    client: OptimizedHTTPXClient | None = None
) -> dict[str, Any]:
    """Benchmark concurrent HTTP requests."""

    start_time = time.time()

    # Use provided client or create new one
    if client is None:
        async with OptimizedHTTPXClient(max_connections=max_concurrent) as test_client:
            return await benchmark_concurrent_requests(urls, max_concurrent, test_client)

    # Create request tasks
    async def make_request(url):
        try:
            response = await client.get(url)
            return response.status_code
        except Exception as e:
            return f"Error: {e!s}"

    request_tasks = [lambda url=url: make_request(url) for url in urls]

    # Execute with concurrency limit
    results = await gather_with_concurrency_limit(
        request_tasks,
        limit=max_concurrent,
        return_exceptions=True
    )

    execution_time = time.time() - start_time

    # Analyze results
    successful_requests = sum(1 for r in results if isinstance(r, int) and 200 <= r < 300)
    failed_requests = len(results) - successful_requests

    return {
        "total_requests": len(urls),
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "success_rate": (successful_requests / len(urls)) * 100,
        "execution_time": execution_time,
        "throughput_rps": len(urls) / execution_time,
        "constitutional_hash": CONSTITUTIONAL_HASH
    }


if __name__ == "__main__":
    print("🚀 ACGS Async Optimization Suite")
    print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 60)
    print("Features:")
    print("- Optimized HTTPX connection pooling")
    print("- asyncio.gather concurrency patterns")
    print("- Request batching and rate limiting")
    print("- Circuit breaker for resilience")
    print("- Performance monitoring")
    print("- Constitutional compliance tracking")
