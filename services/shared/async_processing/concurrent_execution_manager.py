"""
Concurrent Execution Manager for ACGS

This module provides advanced concurrent execution capabilities with:
- Dynamic concurrency control
- Resource-aware execution limits
- Deadlock prevention
- Performance optimization
"""

import asyncio
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import psutil
import structlog

logger = structlog.get_logger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class ExecutionConfig:
    """Configuration for concurrent execution."""

    max_concurrent: int = 50
    max_memory_percent: float = 80.0  # Max memory usage percentage
    max_cpu_percent: float = 80.0  # Max CPU usage percentage
    batch_size: int = 10
    timeout: float = 300.0  # Default timeout in seconds
    enable_backpressure: bool = True
    enable_circuit_breaker: bool = True


@dataclass
class ExecutionMetrics:
    """Metrics for execution monitoring."""

    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time: float = 0.0
    current_concurrency: int = 0
    max_concurrency_reached: int = 0
    memory_usage_percent: float = 0.0
    cpu_usage_percent: float = 0.0
    backpressure_events: int = 0
    circuit_breaker_trips: int = 0


class CircuitBreaker:
    """Circuit breaker for preventing cascade failures."""

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
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func):
        """Decorator for circuit breaker functionality."""

        async def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e

        return wrapper

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        if not self.last_failure_time:
            return True

        return (
            datetime.now() - self.last_failure_time
        ).total_seconds() > self.recovery_timeout

    def _on_success(self):
        """Handle successful execution."""
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class ResourceMonitor:
    """Monitor system resources for dynamic concurrency control."""

    def __init__(self, check_interval: float = 1.0):
        self.check_interval = check_interval
        self.cpu_history = deque(maxlen=60)  # Last 60 measurements
        self.memory_history = deque(maxlen=60)
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None

    async def start_monitoring(self):
        """Start resource monitoring."""
        if self._monitoring:
            return

        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Resource monitoring started")

    async def stop_monitoring(self):
        """Stop resource monitoring."""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Resource monitoring stopped")

    async def _monitor_loop(self):
        """Main monitoring loop."""
        try:
            while self._monitoring:
                # Get current resource usage
                cpu_percent = psutil.cpu_percent(interval=None)
                memory_percent = psutil.virtual_memory().percent

                self.cpu_history.append(cpu_percent)
                self.memory_history.append(memory_percent)

                await asyncio.sleep(self.check_interval)

        except asyncio.CancelledError:
            logger.info("Resource monitoring loop cancelled")

    def get_current_usage(self) -> Tuple[float, float]:
        """Get current CPU and memory usage."""
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory().percent
        return cpu, memory

    def get_average_usage(self, window_seconds: int = 10) -> Tuple[float, float]:
        """Get average CPU and memory usage over time window."""
        samples = min(window_seconds, len(self.cpu_history))

        if samples == 0:
            return self.get_current_usage()

        avg_cpu = sum(list(self.cpu_history)[-samples:]) / samples
        avg_memory = sum(list(self.memory_history)[-samples:]) / samples

        return avg_cpu, avg_memory

    def should_reduce_concurrency(self, config: ExecutionConfig) -> bool:
        """Check if concurrency should be reduced based on resource usage."""
        avg_cpu, avg_memory = self.get_average_usage()

        return (
            avg_cpu > config.max_cpu_percent or avg_memory > config.max_memory_percent
        )


class ConcurrentExecutionManager:
    """Advanced concurrent execution manager with resource awareness."""

    def __init__(self, config: Optional[ExecutionConfig] = None):
        self.config = config or ExecutionConfig()
        self.metrics = ExecutionMetrics()
        self.resource_monitor = ResourceMonitor()
        self.circuit_breaker = CircuitBreaker()

        # Execution tracking
        self.active_executions: Set[str] = set()
        self.execution_queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent)

        # Performance tracking
        self.execution_times = deque(maxlen=1000)
        self.last_metrics_update = datetime.now()

        # Background tasks
        self._executor_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start the concurrent execution manager."""
        if self._running:
            return

        self._running = True

        # Start resource monitoring
        await self.resource_monitor.start_monitoring()

        # Start background tasks
        self._executor_task = asyncio.create_task(self._executor_loop())
        self._metrics_task = asyncio.create_task(self._metrics_loop())

        logger.info(
            "Concurrent execution manager started",
            max_concurrent=self.config.max_concurrent,
            constitutional_hash=CONSTITUTIONAL_HASH,
        )

    async def stop(self):
        """Stop the concurrent execution manager."""
        self._running = False

        # Stop background tasks
        for task in [self._executor_task, self._metrics_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Stop resource monitoring
        await self.resource_monitor.stop_monitoring()

        logger.info("Concurrent execution manager stopped")

    @asynccontextmanager
    async def execute_with_limit(self, execution_id: Optional[str] = None):
        """Context manager for resource-limited execution."""
        if not execution_id:
            execution_id = f"exec_{int(time.time() * 1000)}"

        # Check if we should apply backpressure
        if self.config.enable_backpressure and self._should_apply_backpressure():
            self.metrics.backpressure_events += 1
            logger.warning("Applying backpressure due to resource constraints")
            await asyncio.sleep(0.1)  # Brief delay

        # Acquire semaphore
        async with self.semaphore:
            self.active_executions.add(execution_id)
            self.metrics.current_concurrency = len(self.active_executions)
            self.metrics.max_concurrency_reached = max(
                self.metrics.max_concurrency_reached, self.metrics.current_concurrency
            )

            start_time = time.time()

            try:
                yield execution_id

                # Record successful execution
                execution_time = time.time() - start_time
                self.execution_times.append(execution_time)
                self.metrics.successful_executions += 1

            except Exception as e:
                self.metrics.failed_executions += 1
                logger.error(f"Execution {execution_id} failed", error=str(e))
                raise

            finally:
                self.active_executions.discard(execution_id)
                self.metrics.current_concurrency = len(self.active_executions)
                self.metrics.total_executions += 1

    async def execute_batch(
        self,
        tasks: List[Callable],
        batch_size: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> List[Any]:
        """Execute a batch of tasks concurrently with resource management."""
        batch_size = batch_size or self.config.batch_size
        timeout = timeout or self.config.timeout

        results = []

        # Process tasks in batches
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i : i + batch_size]

            # Execute batch concurrently
            batch_tasks = []
            for task in batch:
                batch_tasks.append(self._execute_single_task(task, timeout))

            try:
                batch_results = await asyncio.wait_for(
                    asyncio.gather(*batch_tasks, return_exceptions=True),
                    timeout=timeout,
                )
                results.extend(batch_results)

            except asyncio.TimeoutError:
                logger.error(f"Batch execution timeout after {timeout}s")
                # Cancel remaining tasks
                for task in batch_tasks:
                    if not task.done():
                        task.cancel()
                results.extend([None] * len(batch))

        return results

    async def _execute_single_task(self, task: Callable, timeout: float) -> Any:
        """Execute a single task with resource management."""
        async with self.execute_with_limit() as execution_id:
            if self.config.enable_circuit_breaker:
                # Apply circuit breaker
                task = self.circuit_breaker.call(task)

            try:
                if asyncio.iscoroutinefunction(task):
                    result = await asyncio.wait_for(task(), timeout=timeout)
                else:
                    # Run sync function in thread pool
                    result = await asyncio.get_event_loop().run_in_executor(None, task)

                return result

            except asyncio.TimeoutError:
                logger.warning(f"Task execution timeout: {execution_id}")
                raise
            except Exception as e:
                logger.error(f"Task execution failed: {execution_id}", error=str(e))
                raise

    def _should_apply_backpressure(self) -> bool:
        """Check if backpressure should be applied."""
        # Check current concurrency
        if len(self.active_executions) >= self.config.max_concurrent * 0.9:
            return True

        # Check resource usage
        if self.resource_monitor.should_reduce_concurrency(self.config):
            return True

        # Check error rate
        if self.metrics.total_executions > 0:
            error_rate = self.metrics.failed_executions / self.metrics.total_executions
            if error_rate > 0.1:  # 10% error rate threshold
                return True

        return False

    async def _executor_loop(self):
        """Main executor loop for processing queued tasks."""
        try:
            while self._running:
                try:
                    # Get task from queue with timeout
                    task_data = await asyncio.wait_for(
                        self.execution_queue.get(), timeout=1.0
                    )

                    # Execute task
                    await self._execute_single_task(
                        task_data["task"], task_data.get("timeout", self.config.timeout)
                    )

                except asyncio.TimeoutError:
                    # No tasks in queue, continue
                    continue
                except Exception as e:
                    logger.error("Error in executor loop", error=str(e))

        except asyncio.CancelledError:
            logger.info("Executor loop cancelled")

    async def _metrics_loop(self):
        """Background metrics update loop."""
        try:
            while self._running:
                await asyncio.sleep(10)  # Update every 10 seconds
                await self._update_metrics()

        except asyncio.CancelledError:
            logger.info("Metrics loop cancelled")

    async def _update_metrics(self):
        """Update performance metrics."""
        # Update average execution time
        if self.execution_times:
            self.metrics.average_execution_time = sum(self.execution_times) / len(
                self.execution_times
            )

        # Update resource usage
        cpu, memory = self.resource_monitor.get_current_usage()
        self.metrics.cpu_usage_percent = cpu
        self.metrics.memory_usage_percent = memory

        # Update circuit breaker trips
        if self.circuit_breaker.state == "OPEN":
            self.metrics.circuit_breaker_trips += 1

        # Adjust concurrency based on resource usage
        await self._adjust_concurrency()

    async def _adjust_concurrency(self):
        """Dynamically adjust concurrency based on resource usage."""
        if not self.config.enable_backpressure:
            return

        avg_cpu, avg_memory = self.resource_monitor.get_average_usage()

        # Reduce concurrency if resources are stressed
        if (
            avg_cpu > self.config.max_cpu_percent
            or avg_memory > self.config.max_memory_percent
        ):

            new_limit = max(1, int(self.config.max_concurrent * 0.8))
            if new_limit < self.semaphore._value:
                # Reduce semaphore limit
                for _ in range(self.semaphore._value - new_limit):
                    try:
                        self.semaphore.acquire_nowait()
                    except ValueError:
                        break

                logger.info(
                    "Reduced concurrency due to resource pressure",
                    new_limit=new_limit,
                    cpu_usage=avg_cpu,
                    memory_usage=avg_memory,
                )

        # Increase concurrency if resources are available
        elif (
            avg_cpu < self.config.max_cpu_percent * 0.6
            and avg_memory < self.config.max_memory_percent * 0.6
        ):

            new_limit = min(self.config.max_concurrent, self.semaphore._value + 5)
            if new_limit > self.semaphore._value:
                # Increase semaphore limit
                for _ in range(new_limit - self.semaphore._value):
                    self.semaphore.release()

                logger.debug(
                    "Increased concurrency due to available resources",
                    new_limit=new_limit,
                    cpu_usage=avg_cpu,
                    memory_usage=avg_memory,
                )

    async def queue_task(self, task: Callable, timeout: Optional[float] = None):
        """Queue a task for execution."""
        await self.execution_queue.put(
            {"task": task, "timeout": timeout or self.config.timeout}
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get current execution metrics."""
        cpu, memory = self.resource_monitor.get_current_usage()

        return {
            "execution_metrics": {
                "total_executions": self.metrics.total_executions,
                "successful_executions": self.metrics.successful_executions,
                "failed_executions": self.metrics.failed_executions,
                "success_rate": (
                    self.metrics.successful_executions
                    / max(1, self.metrics.total_executions)
                ),
                "average_execution_time": self.metrics.average_execution_time,
                "current_concurrency": self.metrics.current_concurrency,
                "max_concurrency_reached": self.metrics.max_concurrency_reached,
                "backpressure_events": self.metrics.backpressure_events,
                "circuit_breaker_trips": self.metrics.circuit_breaker_trips,
            },
            "resource_usage": {
                "cpu_percent": cpu,
                "memory_percent": memory,
                "avg_cpu_10s": self.resource_monitor.get_average_usage(10)[0],
                "avg_memory_10s": self.resource_monitor.get_average_usage(10)[1],
            },
            "configuration": {
                "max_concurrent": self.config.max_concurrent,
                "max_cpu_percent": self.config.max_cpu_percent,
                "max_memory_percent": self.config.max_memory_percent,
                "enable_backpressure": self.config.enable_backpressure,
                "enable_circuit_breaker": self.config.enable_circuit_breaker,
            },
            "circuit_breaker": {
                "state": self.circuit_breaker.state,
                "failure_count": self.circuit_breaker.failure_count,
                "failure_threshold": self.circuit_breaker.failure_threshold,
            },
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    async def execute_constitutional_batch(
        self, tasks: List[Callable], priority_boost: bool = True
    ) -> List[Any]:
        """Execute constitutional tasks with priority handling."""
        if priority_boost:
            # Temporarily increase concurrency for constitutional tasks
            original_limit = self.config.max_concurrent
            self.config.max_concurrent = min(original_limit * 2, 200)

            # Release additional semaphore permits
            additional_permits = self.config.max_concurrent - original_limit
            for _ in range(additional_permits):
                self.semaphore.release()

        try:
            results = await self.execute_batch(
                tasks,
                batch_size=min(
                    len(tasks), 20
                ),  # Larger batches for constitutional tasks
                timeout=self.config.timeout * 2,  # Longer timeout
            )

            logger.info(
                "Constitutional batch execution completed",
                task_count=len(tasks),
                constitutional_hash=CONSTITUTIONAL_HASH,
            )

            return results

        finally:
            if priority_boost:
                # Restore original concurrency limit
                self.config.max_concurrent = original_limit

                # Acquire excess permits
                for _ in range(additional_permits):
                    try:
                        self.semaphore.acquire_nowait()
                    except ValueError:
                        break
