"""
Background Processor for ACGS-1 Self-Evolving AI Architecture Foundation.

This module implements Celery/Redis background processing for asynchronous
task execution within the self-evolving AI architecture.

Key Features:
- Celery task queue management
- Redis broker integration
- Asynchronous task execution
- Task monitoring and status tracking
- Error handling and retry mechanisms
- Integration with evolution workflows
"""

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

try:
    from celery import Celery
    from celery.result import AsyncResult

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    Celery = None
    AsyncResult = None

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status enumeration."""

    PENDING = "pending"
    STARTED = "started"
    RETRY = "retry"
    FAILURE = "failure"
    SUCCESS = "success"
    REVOKED = "revoked"


class TaskPriority(Enum):
    """Task priority enumeration."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BackgroundTask:
    """Background task data structure."""

    task_id: str
    task_name: str
    task_type: str
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    result: Any | None = None
    error_message: str | None = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BackgroundProcessor:
    """
    Background processor for asynchronous task execution.

    This processor manages background tasks using Celery and Redis,
    providing reliable asynchronous execution for evolution workflows.
    """

    def __init__(self, settings):
        self.settings = settings

        # Celery configuration
        self.celery_broker_url = settings.CELERY_BROKER_URL
        self.celery_result_backend = settings.CELERY_RESULT_BACKEND

        # Redis configuration
        self.redis_url = settings.REDIS_URL
        self.redis_password = settings.REDIS_PASSWORD
        self.redis_db = settings.REDIS_DB

        # Task tracking
        self.active_tasks: dict[str, BackgroundTask] = {}
        self.task_history: list[BackgroundTask] = []
        self.task_metrics: dict[str, Any] = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "active_tasks": 0,
            "average_execution_time": 0,
        }

        # Celery app
        self.celery_app: Celery | None = None

        # Redis client
        self.redis_client: redis.Redis | None = None

        # Task registry
        self.task_registry: dict[str, Callable] = {}

        logger.info("Background processor initialized with Celery/Redis")

    async def initialize(self):
        """Initialize the background processor."""
        try:
            # Initialize Redis client
            await self._initialize_redis_client()

            # Initialize Celery app
            await self._initialize_celery_app()

            # Register default tasks
            await self._register_default_tasks()

            # Start task monitoring
            asyncio.create_task(self._monitor_task_health())

            logger.info("✅ Background processor initialization complete")

        except Exception as e:
            logger.error(f"❌ Background processor initialization failed: {e}")
            raise

    async def submit_task(
        self,
        task_name: str,
        task_type: str,
        args: list[Any] = None,
        kwargs: dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
    ) -> str:
        """
        Submit a background task for execution.

        Args:
            task_name: Name of the task to execute
            task_type: Type/category of the task
            args: Positional arguments for the task
            kwargs: Keyword arguments for the task
            priority: Task priority level
            max_retries: Maximum number of retry attempts

        Returns:
            Task ID
        """
        try:
            # Create task
            task = BackgroundTask(
                task_id=f"task_{int(time.time())}_{len(self.active_tasks)}",
                task_name=task_name,
                task_type=task_type,
                priority=priority,
                args=args or [],
                kwargs=kwargs or {},
                max_retries=max_retries,
            )

            # Add to active tasks
            self.active_tasks[task.task_id] = task

            # Submit to Celery if available
            if CELERY_AVAILABLE and self.celery_app:
                celery_result = self.celery_app.send_task(
                    task_name,
                    args=task.args,
                    kwargs=task.kwargs,
                    task_id=task.task_id,
                    priority=self._get_celery_priority(priority),
                    retry=True,
                    retry_policy={
                        "max_retries": max_retries,
                        "interval_start": 1,
                        "interval_step": 2,
                        "interval_max": 30,
                    },
                )
                task.metadata["celery_task_id"] = celery_result.id
            else:
                # Execute locally if Celery not available
                asyncio.create_task(self._execute_task_locally(task))

            # Update metrics
            self.task_metrics["total_tasks"] += 1
            self.task_metrics["active_tasks"] += 1

            logger.info(f"Task submitted: {task.task_id} ({task_name})")

            return task.task_id

        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            raise

    async def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """
        Get the status of a background task.

        Args:
            task_id: Task identifier

        Returns:
            Task status information or None if not found
        """
        try:
            # Check active tasks
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]

                # Update status from Celery if available
                if CELERY_AVAILABLE and "celery_task_id" in task.metadata:
                    celery_result = AsyncResult(
                        task.metadata["celery_task_id"], app=self.celery_app
                    )
                    task.status = TaskStatus(celery_result.status.lower())
                    if celery_result.ready():
                        if celery_result.successful():
                            task.result = celery_result.result
                            task.completed_at = datetime.now(timezone.utc)
                        else:
                            task.error_message = str(celery_result.info)

                return {
                    "task_id": task.task_id,
                    "task_name": task.task_name,
                    "task_type": task.task_type,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "created_at": task.created_at.isoformat(),
                    "started_at": (
                        task.started_at.isoformat() if task.started_at else None
                    ),
                    "completed_at": (
                        task.completed_at.isoformat() if task.completed_at else None
                    ),
                    "retry_count": task.retry_count,
                    "max_retries": task.max_retries,
                    "result": task.result,
                    "error_message": task.error_message,
                }

            # Check task history
            for task in self.task_history:
                if task.task_id == task_id:
                    return {
                        "task_id": task.task_id,
                        "task_name": task.task_name,
                        "task_type": task.task_type,
                        "status": task.status.value,
                        "priority": task.priority.value,
                        "created_at": task.created_at.isoformat(),
                        "started_at": (
                            task.started_at.isoformat() if task.started_at else None
                        ),
                        "completed_at": (
                            task.completed_at.isoformat() if task.completed_at else None
                        ),
                        "retry_count": task.retry_count,
                        "result": task.result,
                        "error_message": task.error_message,
                    }

            return None

        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            return {"error": str(e)}

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a background task.

        Args:
            task_id: Task identifier

        Returns:
            True if task was cancelled, False otherwise
        """
        try:
            if task_id not in self.active_tasks:
                return False

            task = self.active_tasks[task_id]

            # Cancel Celery task if available
            if CELERY_AVAILABLE and "celery_task_id" in task.metadata:
                celery_result = AsyncResult(
                    task.metadata["celery_task_id"], app=self.celery_app
                )
                celery_result.revoke(terminate=True)

            # Update task status
            task.status = TaskStatus.REVOKED
            task.completed_at = datetime.now(timezone.utc)

            # Move to history
            self.task_history.append(task)
            del self.active_tasks[task_id]

            # Update metrics
            self.task_metrics["active_tasks"] -= 1

            logger.info(f"Task cancelled: {task_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to cancel task: {e}")
            return False

    async def get_processor_status(self) -> dict[str, Any]:
        """Get current background processor status."""
        try:
            # Check Redis connectivity
            redis_health = await self._check_redis_health()

            # Check Celery status
            celery_health = await self._check_celery_health()

            return {
                "redis_integration": {
                    "url": self.redis_url,
                    "health": redis_health,
                },
                "celery_integration": {
                    "broker_url": self.celery_broker_url,
                    "result_backend": self.celery_result_backend,
                    "available": CELERY_AVAILABLE,
                    "health": celery_health,
                },
                "tasks": {
                    "active_tasks": len(self.active_tasks),
                    "task_history_size": len(self.task_history),
                    "registered_tasks": len(self.task_registry),
                },
                "metrics": self.task_metrics,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get processor status: {e}")
            return {"error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Perform health check for the background processor."""
        try:
            health_status = {
                "healthy": True,
                "timestamp": time.time(),
                "checks": {},
            }

            # Check Redis connectivity
            redis_health = await self._check_redis_health()
            health_status["checks"]["redis_connectivity"] = {
                "healthy": redis_health.get("healthy", False),
                "url": self.redis_url,
                "response_time_ms": redis_health.get("response_time_ms", "unknown"),
            }
            if not redis_health.get("healthy", False):
                health_status["healthy"] = False

            # Check Celery availability
            celery_health = await self._check_celery_health()
            health_status["checks"]["celery_availability"] = {
                "healthy": celery_health.get("healthy", False),
                "available": CELERY_AVAILABLE,
                "broker_url": self.celery_broker_url,
            }
            if not celery_health.get("healthy", False):
                health_status["healthy"] = False

            # Check task processing
            health_status["checks"]["task_processing"] = {
                "healthy": True,
                "active_tasks": len(self.active_tasks),
                "registered_tasks": len(self.task_registry),
            }

            return health_status

        except Exception as e:
            logger.error(f"Background processor health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": time.time(),
            }

    async def shutdown(self):
        """Shutdown the background processor gracefully."""
        try:
            logger.info("Shutting down background processor...")

            # Cancel active tasks
            for task_id in list(self.active_tasks.keys()):
                await self.cancel_task(task_id)

            # Close Redis client
            if self.redis_client:
                await self.redis_client.close()

            logger.info("✅ Background processor shutdown complete")

        except Exception as e:
            logger.error(f"Error during background processor shutdown: {e}")

    # Private helper methods
    async def _initialize_redis_client(self):
        """Initialize Redis client."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                password=self.redis_password,
                db=self.redis_db,
                decode_responses=True,
            )

            # Test Redis connectivity
            await self.redis_client.ping()

            logger.info(f"Redis client initialized: {self.redis_url}")

        except Exception as e:
            logger.error(f"Redis client initialization failed: {e}")
            raise

    async def _initialize_celery_app(self):
        """Initialize Celery application."""
        try:
            if not CELERY_AVAILABLE:
                logger.warning("Celery not available - tasks will run locally")
                return

            self.celery_app = Celery(
                "acgs_self_evolving_ai",
                broker=self.celery_broker_url,
                backend=self.celery_result_backend,
            )

            # Configure Celery
            self.celery_app.conf.update(
                task_serializer=self.settings.CELERY_TASK_SERIALIZER,
                result_serializer=self.settings.CELERY_RESULT_SERIALIZER,
                accept_content=self.settings.CELERY_ACCEPT_CONTENT,
                timezone=self.settings.CELERY_TIMEZONE,
                enable_utc=self.settings.CELERY_ENABLE_UTC,
                task_routes={
                    "acgs.evolution.*": {"queue": "evolution"},
                    "acgs.security.*": {"queue": "security"},
                    "acgs.policy.*": {"queue": "policy"},
                },
                task_default_queue="default",
                task_default_exchange="default",
                task_default_routing_key="default",
            )

            logger.info("Celery app initialized")

        except Exception as e:
            logger.error(f"Celery app initialization failed: {e}")
            raise

    async def _register_default_tasks(self):
        """Register default background tasks."""
        try:
            # Evolution tasks
            self.task_registry["evolution_analysis"] = self._evolution_analysis_task
            self.task_registry["evolution_execution"] = self._evolution_execution_task
            self.task_registry["evolution_validation"] = self._evolution_validation_task

            # Security tasks
            self.task_registry["security_assessment"] = self._security_assessment_task
            self.task_registry["threat_mitigation"] = self._threat_mitigation_task

            # Policy tasks
            self.task_registry["policy_compilation"] = self._policy_compilation_task
            self.task_registry["policy_validation"] = self._policy_validation_task

            # Monitoring tasks
            self.task_registry["health_monitoring"] = self._health_monitoring_task
            self.task_registry["metrics_collection"] = self._metrics_collection_task

            logger.info(f"Registered {len(self.task_registry)} default tasks")

        except Exception as e:
            logger.error(f"Failed to register default tasks: {e}")
            raise

    def _get_celery_priority(self, priority: TaskPriority) -> int:
        """Convert TaskPriority to Celery priority."""
        priority_map = {
            TaskPriority.LOW: 1,
            TaskPriority.NORMAL: 5,
            TaskPriority.HIGH: 8,
            TaskPriority.CRITICAL: 10,
        }
        return priority_map.get(priority, 5)

    async def _execute_task_locally(self, task: BackgroundTask):
        """Execute task locally when Celery is not available."""
        try:
            task.status = TaskStatus.STARTED
            task.started_at = datetime.now(timezone.utc)

            # Get task function
            task_function = self.task_registry.get(task.task_name)
            if not task_function:
                raise ValueError(f"Unknown task: {task.task_name}")

            # Execute task
            result = await task_function(*task.args, **task.kwargs)

            # Update task
            task.status = TaskStatus.SUCCESS
            task.result = result
            task.completed_at = datetime.now(timezone.utc)

            # Move to history
            self.task_history.append(task)
            del self.active_tasks[task.task_id]

            # Update metrics
            self.task_metrics["successful_tasks"] += 1
            self.task_metrics["active_tasks"] -= 1

            logger.info(f"Task completed locally: {task.task_id}")

        except Exception as e:
            # Handle task failure
            task.status = TaskStatus.FAILURE
            task.error_message = str(e)
            task.completed_at = datetime.now(timezone.utc)

            # Move to history
            self.task_history.append(task)
            del self.active_tasks[task.task_id]

            # Update metrics
            self.task_metrics["failed_tasks"] += 1
            self.task_metrics["active_tasks"] -= 1

            logger.error(f"Task failed locally: {task.task_id} - {e}")

    async def _check_redis_health(self) -> dict[str, Any]:
        """Check Redis server health."""
        try:
            if not self.redis_client:
                return {"healthy": False, "error": "Redis client not initialized"}

            start_time = time.time()
            await self.redis_client.ping()
            response_time_ms = (time.time() - start_time) * 1000

            return {
                "healthy": True,
                "response_time_ms": round(response_time_ms, 2),
            }

        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"healthy": False, "error": str(e)}

    async def _check_celery_health(self) -> dict[str, Any]:
        """Check Celery health."""
        try:
            if not CELERY_AVAILABLE:
                return {"healthy": False, "error": "Celery not available"}

            if not self.celery_app:
                return {"healthy": False, "error": "Celery app not initialized"}

            # Check Celery broker connectivity
            try:
                inspect = self.celery_app.control.inspect()
                stats = inspect.stats()
                if stats:
                    return {"healthy": True, "workers": len(stats)}
                return {"healthy": False, "error": "No Celery workers available"}
            except Exception as e:
                return {
                    "healthy": False,
                    "error": f"Celery inspection failed: {e!s}",
                }

        except Exception as e:
            logger.error(f"Celery health check failed: {e}")
            return {"healthy": False, "error": str(e)}

    async def _monitor_task_health(self):
        """Background task to monitor task health."""
        while True:
            try:
                # Update task statuses
                await self._update_task_statuses()

                # Clean up old tasks
                await self._cleanup_old_tasks()

                # Update metrics
                await self._update_task_metrics()

                # Sleep for monitoring interval
                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Task health monitoring error: {e}")
                await asyncio.sleep(30)

    async def _update_task_statuses(self):
        """Update statuses of active tasks."""
        try:
            if not CELERY_AVAILABLE or not self.celery_app:
                return

            for task in list(self.active_tasks.values()):
                if "celery_task_id" in task.metadata:
                    celery_result = AsyncResult(
                        task.metadata["celery_task_id"], app=self.celery_app
                    )

                    if celery_result.ready():
                        if celery_result.successful():
                            task.status = TaskStatus.SUCCESS
                            task.result = celery_result.result
                            task.completed_at = datetime.now(timezone.utc)

                            # Move to history
                            self.task_history.append(task)
                            del self.active_tasks[task.task_id]

                            # Update metrics
                            self.task_metrics["successful_tasks"] += 1
                            self.task_metrics["active_tasks"] -= 1

                        else:
                            task.status = TaskStatus.FAILURE
                            task.error_message = str(celery_result.info)
                            task.completed_at = datetime.now(timezone.utc)

                            # Move to history
                            self.task_history.append(task)
                            del self.active_tasks[task.task_id]

                            # Update metrics
                            self.task_metrics["failed_tasks"] += 1
                            self.task_metrics["active_tasks"] -= 1

        except Exception as e:
            logger.error(f"Task status update failed: {e}")

    async def _cleanup_old_tasks(self):
        """Clean up old tasks from history."""
        try:
            current_time = datetime.now(timezone.utc)
            old_tasks = []

            for task in self.task_history:
                # Remove tasks older than 24 hours
                if (
                    task.completed_at
                    and (current_time - task.completed_at).total_seconds() > 86400
                ):
                    old_tasks.append(task)

            for task in old_tasks:
                self.task_history.remove(task)

            if old_tasks:
                logger.info(f"Cleaned up {len(old_tasks)} old tasks")

        except Exception as e:
            logger.error(f"Task cleanup failed: {e}")

    async def _update_task_metrics(self):
        """Update task processing metrics."""
        try:
            # Calculate average execution time
            completed_tasks = [
                task
                for task in self.task_history
                if task.completed_at and task.started_at
            ]

            if completed_tasks:
                total_time = sum(
                    (task.completed_at - task.started_at).total_seconds()
                    for task in completed_tasks
                )
                self.task_metrics["average_execution_time"] = total_time / len(
                    completed_tasks
                )

        except Exception as e:
            logger.error(f"Task metrics update failed: {e}")

    # Default task implementations
    async def _evolution_analysis_task(
        self, evolution_id: str, analysis_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Default evolution analysis task."""
        logger.info(f"Executing evolution analysis for {evolution_id}")
        # Simulate analysis work
        await asyncio.sleep(2)
        return {"analysis_complete": True, "evolution_id": evolution_id}

    async def _evolution_execution_task(
        self, evolution_id: str, execution_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Default evolution execution task."""
        logger.info(f"Executing evolution changes for {evolution_id}")
        # Simulate execution work
        await asyncio.sleep(5)
        return {"execution_complete": True, "evolution_id": evolution_id}

    async def _evolution_validation_task(
        self, evolution_id: str, validation_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Default evolution validation task."""
        logger.info(f"Validating evolution results for {evolution_id}")
        # Simulate validation work
        await asyncio.sleep(3)
        return {"validation_complete": True, "evolution_id": evolution_id}

    async def _security_assessment_task(
        self, assessment_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Default security assessment task."""
        logger.info("Executing security assessment")
        # Simulate security assessment work
        await asyncio.sleep(1)
        return {"assessment_complete": True, "threat_level": "low"}

    async def _threat_mitigation_task(
        self, threat_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Default threat mitigation task."""
        logger.info("Executing threat mitigation")
        # Simulate mitigation work
        await asyncio.sleep(2)
        return {"mitigation_complete": True, "threat_mitigated": True}

    async def _policy_compilation_task(
        self, policy_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Default policy compilation task."""
        logger.info("Executing policy compilation")
        # Simulate compilation work
        await asyncio.sleep(1)
        return {"compilation_complete": True, "policies_compiled": True}

    async def _policy_validation_task(
        self, validation_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Default policy validation task."""
        logger.info("Executing policy validation")
        # Simulate validation work
        await asyncio.sleep(1)
        return {"validation_complete": True, "policies_valid": True}

    async def _health_monitoring_task(self) -> dict[str, Any]:
        """Default health monitoring task."""
        logger.info("Executing health monitoring")
        # Simulate monitoring work
        await asyncio.sleep(0.5)
        return {"monitoring_complete": True, "system_healthy": True}

    async def _metrics_collection_task(self) -> dict[str, Any]:
        """Default metrics collection task."""
        logger.info("Executing metrics collection")
        # Simulate metrics collection work
        await asyncio.sleep(0.5)
        return {"collection_complete": True, "metrics_collected": True}
