"""
Enhanced Async Task Scheduler for ACGS

This module provides advanced async task scheduling with:
- Dynamic load balancing
- Intelligent task prioritization
- Concurrent task execution with limits
- Task dependency management
- Performance monitoring and optimization
"""

import asyncio
import contextlib
import heapq
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import structlog
from services.shared.redis_client import ACGSRedisClient

logger = structlog.get_logger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TaskPriority(Enum):
    """Task priority levels."""

    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class TaskDefinition:
    """Enhanced task definition with scheduling metadata."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    task_type: str = ""
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float | None = None
    dependencies: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    # Task data
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    error_info: dict[str, Any] | None = None

    # Execution metadata
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    retry_count: int = 0
    execution_time: float | None = None

    # Agent assignment
    assigned_agent: str | None = None
    agent_capabilities: list[str] = field(default_factory=list)


@dataclass
class TaskExecutionResult:
    """Result of task execution."""

    task_id: str
    success: bool
    output_data: dict[str, Any] = field(default_factory=dict)
    error_info: dict[str, Any] | None = None
    execution_time: float = 0.0
    memory_usage: int | None = None


@dataclass
class WorkerCapabilities:
    """Worker/agent capabilities definition."""

    worker_id: str
    task_types: list[str]
    max_concurrent_tasks: int = 5
    cpu_weight: float = 1.0
    memory_weight: float = 1.0
    specializations: list[str] = field(default_factory=list)


class EnhancedTaskScheduler:
    """Enhanced task scheduler with intelligent load balancing and optimization."""

    def __init__(
        self,
        redis_client: ACGSRedisClient,
        max_concurrent_tasks: int = 100,
        task_timeout_default: float = 300.0,  # 5 minutes
        cleanup_interval: float = 60.0,  # 1 minute
    ):
        self.redis_client = redis_client
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_timeout_default = task_timeout_default
        self.cleanup_interval = cleanup_interval

        # Task management
        self.pending_tasks: list[tuple[float, TaskDefinition]] = []  # Priority queue
        self.running_tasks: dict[str, TaskDefinition] = {}
        self.completed_tasks: dict[str, TaskDefinition] = {}
        self.failed_tasks: dict[str, TaskDefinition] = {}

        # Worker management
        self.workers: dict[str, WorkerCapabilities] = {}
        self.worker_loads: dict[str, int] = defaultdict(int)
        self.worker_task_history: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )

        # Task dependencies
        self.task_dependencies: dict[str, set[str]] = {}
        self.dependency_graph: dict[str, set[str]] = {}

        # Performance tracking
        self.performance_metrics = {
            "total_tasks_submitted": 0,
            "total_tasks_completed": 0,
            "total_tasks_failed": 0,
            "average_execution_time": 0.0,
            "throughput_per_minute": 0.0,
            "worker_utilization": 0.0,
            "queue_length": 0,
            "retry_rate": 0.0,
        }

        # Background tasks
        self._scheduler_task: asyncio.Task | None = None
        self._cleanup_task: asyncio.Task | None = None
        self._metrics_task: asyncio.Task | None = None
        self._running = False

        # Lock for thread safety
        self._lock = asyncio.Lock()

    async def start(self):
        """Start the task scheduler."""
        if self._running:
            return

        self._running = True

        # Start background tasks
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._metrics_task = asyncio.create_task(self._metrics_loop())

        logger.info(
            "Enhanced task scheduler started",
            max_concurrent=self.max_concurrent_tasks,
            constitutional_hash=CONSTITUTIONAL_HASH,
        )

    async def stop(self):
        """Stop the task scheduler gracefully."""
        self._running = False

        # Cancel background tasks
        for task in [self._scheduler_task, self._cleanup_task, self._metrics_task]:
            if task and not task.done():
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

        # Wait for running tasks to complete (with timeout)
        if self.running_tasks:
            logger.info(
                f"Waiting for {len(self.running_tasks)} running tasks to complete..."
            )
            await asyncio.sleep(5)  # Give tasks time to finish

        logger.info("Enhanced task scheduler stopped")

    async def submit_task(
        self, task: TaskDefinition, preferred_worker: str | None = None
    ) -> str:
        """Submit a task for execution."""
        async with self._lock:
            # Validate dependencies
            if task.dependencies:
                for dep_id in task.dependencies:
                    if dep_id not in self.completed_tasks:
                        logger.warning(
                            "Task dependency not met",
                            task_id=task.id,
                            dependency=dep_id,
                        )

            # Add to dependency graph
            if task.dependencies:
                self.task_dependencies[task.id] = set(task.dependencies)
                for dep_id in task.dependencies:
                    if dep_id not in self.dependency_graph:
                        self.dependency_graph[dep_id] = set()
                    self.dependency_graph[dep_id].add(task.id)

            # Calculate priority score (lower is higher priority)
            priority_score = self._calculate_priority_score(task, preferred_worker)

            # Add to priority queue
            heapq.heappush(self.pending_tasks, (priority_score, task))

            # Store in Redis for persistence
            await self._persist_task(task)

            self.performance_metrics["total_tasks_submitted"] += 1
            self.performance_metrics["queue_length"] = len(self.pending_tasks)

            logger.debug(
                "Task submitted",
                task_id=task.id,
                task_type=task.task_type,
                priority=task.priority.name,
                dependencies=len(task.dependencies),
            )

            return task.id

    def _calculate_priority_score(
        self, task: TaskDefinition, preferred_worker: str | None = None
    ) -> float:
        """Calculate priority score for task scheduling."""
        base_score = task.priority.value

        # Constitutional tasks get priority boost
        if CONSTITUTIONAL_HASH in str(task.input_data) or "constitutional" in task.tags:
            base_score *= 0.5  # Higher priority (lower score)

        # Urgent tasks based on creation time
        age_minutes = (datetime.now() - task.created_at).total_seconds() / 60
        age_factor = min(age_minutes / 60, 2.0)  # Max 2x boost after 1 hour

        # Worker affinity bonus
        worker_factor = 1.0
        if preferred_worker and preferred_worker in self.workers:
            worker_load = self.worker_loads[preferred_worker]
            worker_capacity = self.workers[preferred_worker].max_concurrent_tasks
            if worker_load < worker_capacity:
                worker_factor = 0.8  # Slight priority boost

        # Dependency factor (prioritize tasks with no dependencies)
        dependency_factor = 1.0 + (len(task.dependencies) * 0.1)

        return base_score * dependency_factor * worker_factor / (1 + age_factor)

    async def register_worker(self, capabilities: WorkerCapabilities):
        """Register a worker with its capabilities."""
        async with self._lock:
            self.workers[capabilities.worker_id] = capabilities
            self.worker_loads[capabilities.worker_id] = 0

            logger.info(
                "Worker registered",
                worker_id=capabilities.worker_id,
                task_types=capabilities.task_types,
                max_concurrent=capabilities.max_concurrent_tasks,
            )

    async def unregister_worker(self, worker_id: str):
        """Unregister a worker."""
        async with self._lock:
            if worker_id in self.workers:
                del self.workers[worker_id]
                del self.worker_loads[worker_id]
                if worker_id in self.worker_task_history:
                    del self.worker_task_history[worker_id]

                logger.info("Worker unregistered", worker_id=worker_id)

    async def get_task_status(self, task_id: str) -> TaskStatus | None:
        """Get the current status of a task."""
        if task_id in self.running_tasks:
            return TaskStatus.RUNNING
        if task_id in self.completed_tasks:
            return TaskStatus.COMPLETED
        if task_id in self.failed_tasks:
            return TaskStatus.FAILED
        # Check if in pending queue
        for _, task in self.pending_tasks:
            if task.id == task_id:
                return TaskStatus.PENDING

        return None

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        async with self._lock:
            # Check if task is pending
            for i, (_, task) in enumerate(self.pending_tasks):
                if task.id == task_id:
                    # Remove from pending queue
                    del self.pending_tasks[i]
                    heapq.heapify(self.pending_tasks)

                    task.status = TaskStatus.CANCELLED
                    task.completed_at = datetime.now()

                    await self._persist_task(task)

                    logger.info("Task cancelled from pending queue", task_id=task_id)
                    return True

            # Check if task is running
            if task_id in self.running_tasks:
                task = self.running_tasks[task_id]
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.now()

                # Note: Actual task cancellation depends on implementation
                # This marks it as cancelled but may not stop execution immediately

                await self._persist_task(task)

                logger.info("Task marked for cancellation", task_id=task_id)
                return True

        return False

    async def _scheduler_loop(self):
        """Main scheduler loop for task assignment."""
        try:
            while self._running:
                async with self._lock:
                    await self._schedule_tasks()

                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info("Scheduler loop cancelled")
        except Exception as e:
            logger.exception("Error in scheduler loop", error=str(e))

    async def _schedule_tasks(self):
        """Schedule pending tasks to available workers."""
        if (
            not self.pending_tasks
            or len(self.running_tasks) >= self.max_concurrent_tasks
        ):
            return

        # Get ready tasks (dependencies satisfied)
        ready_tasks = []
        while self.pending_tasks:
            priority_score, task = heapq.heappop(self.pending_tasks)

            if self._are_dependencies_satisfied(task):
                ready_tasks.append((priority_score, task))
            else:
                # Put back in queue
                heapq.heappush(self.pending_tasks, (priority_score, task))
                break

        # Schedule ready tasks
        for priority_score, task in ready_tasks:
            if len(self.running_tasks) >= self.max_concurrent_tasks:
                # Put back in queue
                heapq.heappush(self.pending_tasks, (priority_score, task))
                break

            # Find suitable worker
            worker_id = self._find_best_worker(task)

            if worker_id:
                # Assign task to worker
                await self._assign_task_to_worker(task, worker_id)
            else:
                # No available worker, put back in queue
                heapq.heappush(self.pending_tasks, (priority_score, task))
                break

    def _are_dependencies_satisfied(self, task: TaskDefinition) -> bool:
        """Check if all task dependencies are satisfied."""
        if not task.dependencies:
            return True

        return all(dep_id in self.completed_tasks for dep_id in task.dependencies)

    def _find_best_worker(self, task: TaskDefinition) -> str | None:
        """Find the best available worker for a task."""
        best_worker = None
        best_score = float("inf")

        for worker_id, capabilities in self.workers.items():
            # Check if worker can handle this task type
            if task.task_type not in capabilities.task_types:
                continue

            # Check if worker has capacity
            current_load = self.worker_loads[worker_id]
            if current_load >= capabilities.max_concurrent_tasks:
                continue

            # Calculate worker score (lower is better)
            load_factor = current_load / capabilities.max_concurrent_tasks

            # Specialization bonus
            specialization_bonus = 0.0
            if any(spec in task.tags for spec in capabilities.specializations):
                specialization_bonus = -0.2  # Lower score (better)

            # Historical performance
            history = self.worker_task_history[worker_id]
            avg_execution_time = 0.0
            if history:
                avg_execution_time = sum(h.execution_time for h in history) / len(
                    history
                )

            performance_factor = avg_execution_time / 100.0  # Normalize

            score = load_factor + performance_factor + specialization_bonus

            if score < best_score:
                best_score = score
                best_worker = worker_id

        return best_worker

    async def _assign_task_to_worker(self, task: TaskDefinition, worker_id: str):
        """Assign a task to a specific worker."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        task.assigned_agent = worker_id

        # Update tracking
        self.running_tasks[task.id] = task
        self.worker_loads[worker_id] += 1

        # Persist updated task
        await self._persist_task(task)

        # Create execution coroutine
        asyncio.create_task(self._execute_task(task, worker_id))

        logger.debug(
            "Task assigned to worker",
            task_id=task.id,
            worker_id=worker_id,
            current_load=self.worker_loads[worker_id],
        )

    async def _execute_task(self, task: TaskDefinition, worker_id: str):
        """Execute a task and handle results."""
        start_time = time.time()

        try:
            # Simulate task execution (replace with actual task execution logic)
            result = await self._simulate_task_execution(task)

            execution_time = time.time() - start_time
            task.execution_time = execution_time

            if result.success:
                # Task completed successfully
                task.status = TaskStatus.COMPLETED
                task.output_data = result.output_data
                task.completed_at = datetime.now()

                # Move to completed tasks
                async with self._lock:
                    if task.id in self.running_tasks:
                        del self.running_tasks[task.id]
                    self.completed_tasks[task.id] = task
                    self.worker_loads[worker_id] -= 1

                # Update performance metrics
                self.performance_metrics["total_tasks_completed"] += 1

                # Record worker performance
                self.worker_task_history[worker_id].append(result)

                # Trigger dependent tasks
                await self._trigger_dependent_tasks(task.id)

                logger.debug(
                    "Task completed successfully",
                    task_id=task.id,
                    execution_time=execution_time,
                    worker_id=worker_id,
                )

            else:
                # Task failed
                await self._handle_task_failure(task, worker_id, result.error_info)

        except asyncio.TimeoutError:
            await self._handle_task_timeout(task, worker_id)
        except Exception as e:
            error_info = {"error": str(e), "type": type(e).__name__}
            await self._handle_task_failure(task, worker_id, error_info)

        finally:
            # Persist final task state
            await self._persist_task(task)

    async def _simulate_task_execution(
        self, task: TaskDefinition
    ) -> TaskExecutionResult:
        """Simulate task execution (replace with actual implementation)."""
        # Apply timeout if specified
        timeout = task.timeout or self.task_timeout_default

        try:
            # Simulate work with delay
            await asyncio.wait_for(
                asyncio.sleep(0.1), timeout=timeout  # Simulated processing time
            )

            # Simulate success/failure based on task type
            success_rate = 0.95  # 95% success rate
            if "constitutional" in task.tags:
                success_rate = 0.99  # Higher success rate for constitutional tasks

            import random

            success = random.random() < success_rate

            if success:
                return TaskExecutionResult(
                    task_id=task.id,
                    success=True,
                    output_data={"result": f"Task {task.id} completed"},
                    execution_time=0.1,
                )
            return TaskExecutionResult(
                task_id=task.id,
                success=False,
                error_info={"error": "Simulated task failure"},
                execution_time=0.1,
            )

        except asyncio.TimeoutError:
            raise

    async def _handle_task_failure(
        self, task: TaskDefinition, worker_id: str, error_info: dict[str, Any] | None
    ):
        """Handle task failure with retry logic."""
        task.error_info = error_info
        task.retry_count += 1

        async with self._lock:
            # Remove from running tasks
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
            self.worker_loads[worker_id] -= 1

        if task.retry_count <= task.max_retries:
            # Retry the task
            task.status = TaskStatus.RETRYING

            # Add delay before retry
            await asyncio.sleep(task.retry_delay * task.retry_count)

            # Add back to pending queue with higher priority
            priority_score = (
                self._calculate_priority_score(task) * 0.5
            )  # Higher priority

            async with self._lock:
                heapq.heappush(self.pending_tasks, (priority_score, task))

            self.performance_metrics["retry_rate"] += 1

            logger.warning(
                "Task failed, retrying",
                task_id=task.id,
                retry_count=task.retry_count,
                max_retries=task.max_retries,
                error=error_info,
            )
        else:
            # Task failed permanently
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()

            async with self._lock:
                self.failed_tasks[task.id] = task

            self.performance_metrics["total_tasks_failed"] += 1

            logger.error(
                "Task failed permanently",
                task_id=task.id,
                retry_count=task.retry_count,
                error=error_info,
            )

    async def _handle_task_timeout(self, task: TaskDefinition, worker_id: str):
        """Handle task timeout."""
        error_info = {
            "error": "Task execution timeout",
            "timeout": task.timeout or self.task_timeout_default,
        }

        await self._handle_task_failure(task, worker_id, error_info)

    async def _trigger_dependent_tasks(self, completed_task_id: str):
        """Trigger tasks that depend on the completed task."""
        if completed_task_id in self.dependency_graph:
            dependent_task_ids = self.dependency_graph[completed_task_id]

            for _task_id in dependent_task_ids:
                # Check if all dependencies are now satisfied
                # The scheduler loop will pick up these tasks
                pass

    async def _cleanup_loop(self):
        """Background cleanup of old tasks and metrics."""
        try:
            while self._running:
                await asyncio.sleep(self.cleanup_interval)

                async with self._lock:
                    await self._cleanup_old_tasks()

        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled")
        except Exception as e:
            logger.exception("Error in cleanup loop", error=str(e))

    async def _cleanup_old_tasks(self):
        """Clean up old completed and failed tasks."""
        cutoff_time = datetime.now() - timedelta(hours=24)  # Keep tasks for 24 hours

        # Clean completed tasks
        to_remove = [
            task_id
            for task_id, task in self.completed_tasks.items()
            if task.completed_at and task.completed_at < cutoff_time
        ]

        for task_id in to_remove:
            del self.completed_tasks[task_id]

        # Clean failed tasks
        to_remove = [
            task_id
            for task_id, task in self.failed_tasks.items()
            if task.completed_at and task.completed_at < cutoff_time
        ]

        for task_id in to_remove:
            del self.failed_tasks[task_id]

        if to_remove:
            logger.debug(f"Cleaned up {len(to_remove)} old tasks")

    async def _metrics_loop(self):
        """Background metrics calculation."""
        try:
            while self._running:
                await asyncio.sleep(60)  # Update metrics every minute

                await self._update_performance_metrics()

        except asyncio.CancelledError:
            logger.info("Metrics loop cancelled")
        except Exception as e:
            logger.exception("Error in metrics loop", error=str(e))

    async def _update_performance_metrics(self):
        """Update performance metrics."""
        # Calculate average execution time
        if self.completed_tasks:
            total_time = sum(
                task.execution_time or 0 for task in self.completed_tasks.values()
            )
            self.performance_metrics["average_execution_time"] = total_time / len(
                self.completed_tasks
            )

        # Calculate worker utilization
        if self.workers:
            total_capacity = sum(w.max_concurrent_tasks for w in self.workers.values())
            total_load = sum(self.worker_loads.values())
            self.performance_metrics["worker_utilization"] = (
                total_load / total_capacity if total_capacity > 0 else 0.0
            )

        # Update queue length
        self.performance_metrics["queue_length"] = len(self.pending_tasks)

    async def _persist_task(self, task: TaskDefinition):
        """Persist task to Redis for durability."""
        try:
            key = f"acgs:scheduler:task:{task.id}"
            task_data = {
                "id": task.id,
                "name": task.name,
                "task_type": task.task_type,
                "priority": task.priority.name,
                "status": task.status.name,
                "created_at": task.created_at.isoformat(),
                "input_data": task.input_data,
                "output_data": task.output_data,
                "error_info": task.error_info,
                "retry_count": task.retry_count,
                "assigned_agent": task.assigned_agent,
            }

            if task.started_at:
                task_data["started_at"] = task.started_at.isoformat()
            if task.completed_at:
                task_data["completed_at"] = task.completed_at.isoformat()

            await self.redis_client.set_json(key, task_data, ttl=86400)  # 24 hours

        except Exception as e:
            logger.exception("Failed to persist task", task_id=task.id, error=str(e))

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get current performance metrics."""
        return {
            **self.performance_metrics,
            "running_tasks_count": len(self.running_tasks),
            "pending_tasks_count": len(self.pending_tasks),
            "completed_tasks_count": len(self.completed_tasks),
            "failed_tasks_count": len(self.failed_tasks),
            "registered_workers": len(self.workers),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    def get_worker_status(self) -> dict[str, Any]:
        """Get status of all workers."""
        worker_status = {}

        for worker_id, capabilities in self.workers.items():
            load = self.worker_loads[worker_id]
            utilization = load / capabilities.max_concurrent_tasks

            history = self.worker_task_history[worker_id]
            avg_execution_time = 0.0
            success_rate = 0.0

            if history:
                avg_execution_time = sum(h.execution_time for h in history) / len(
                    history
                )
                success_rate = sum(1 for h in history if h.success) / len(history)

            worker_status[worker_id] = {
                "capabilities": {
                    "task_types": capabilities.task_types,
                    "max_concurrent": capabilities.max_concurrent_tasks,
                    "specializations": capabilities.specializations,
                },
                "current_load": load,
                "utilization": utilization,
                "performance": {
                    "avg_execution_time": avg_execution_time,
                    "success_rate": success_rate,
                    "tasks_completed": len(history),
                },
            }

        return worker_status
