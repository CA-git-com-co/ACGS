"""
Redis-based Blackboard Service for Multi-Agent Coordination
Implements the Hybrid Hierarchical-Blackboard Policy for ACGS governance.
"""

import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import redis.asyncio as redis
from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class KnowledgeItem(BaseModel):
    """Represents a piece of knowledge on the blackboard"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    space: str  # 'governance', 'compliance', 'performance', 'coordination'
    agent_id: str
    task_id: str | None = None
    knowledge_type: str  # 'task', 'result', 'policy', 'metric', 'conflict'
    content: dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    priority: int = Field(default=1, ge=1, le=5)  # 1=highest, 5=lowest
    expires_at: datetime | None = None
    dependencies: list[str] = Field(default_factory=list)
    tags: set[str] = Field(default_factory=set)


class TaskDefinition(BaseModel):
    """Represents a governance task on the blackboard"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    task_type: str  # 'ethical_analysis', 'legal_compliance', 'operational_validation'
    status: str = Field(
        default="pending"
    )  # 'pending', 'claimed', 'in_progress', 'completed', 'failed'
    agent_id: str | None = None  # Agent that claimed the task
    priority: int = Field(default=1, ge=1, le=5)
    requirements: dict[str, Any]
    input_data: dict[str, Any]
    output_data: dict[str, Any] | None = None
    error_details: dict[str, Any] | None = None
    dependencies: list[str] = Field(default_factory=list)
    deadline: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    claimed_at: datetime | None = None
    completed_at: datetime | None = None
    retries: int = 0
    max_retries: int = 3


class ConflictItem(BaseModel):
    """Represents a conflict between agents or decisions"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    conflict_type: str  # 'decision_conflict', 'resource_conflict', 'policy_conflict'
    involved_agents: list[str]
    involved_tasks: list[str]
    description: str
    severity: str = "medium"  # 'low', 'medium', 'high', 'critical'
    status: str = "open"  # 'open', 'in_resolution', 'resolved', 'escalated'
    resolution_strategy: str | None = None
    resolution_data: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: datetime | None = None


class BlackboardService:
    """
    Redis-based blackboard service for multi-agent coordination.
    Implements knowledge sharing, task coordination, and conflict resolution.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379", db: int = 0):
        self.redis_url = redis_url
        self.db = db
        self.redis_client: redis.Redis | None = None
        self.logger = logging.getLogger(__name__)

        # Knowledge spaces - separate Redis key namespaces
        self.spaces = {
            "governance": "bb:governance",
            "compliance": "bb:compliance",
            "performance": "bb:performance",
            "coordination": "bb:coordination",
            "tasks": "bb:tasks",
            "conflicts": "bb:conflicts",
            "agents": "bb:agents",
        }

        # Event channels for notifications
        self.channels = {
            "task_created": "events:task_created",
            "task_claimed": "events:task_claimed",
            "task_completed": "events:task_completed",
            "conflict_detected": "events:conflict_detected",
            "knowledge_added": "events:knowledge_added",
            "agent_status": "events:agent_status",
        }

    async def initialize(self) -> None:
        """Initialize Redis connection and set up the blackboard"""
        self.redis_client = redis.from_url(
            self.redis_url, db=self.db, decode_responses=True
        )

        # Test connection
        await self.redis_client.ping()
        self.logger.info("Blackboard service initialized successfully")

        # Set up initial schemas and indices if needed
        await self._setup_indices()

    async def shutdown(self) -> None:
        """Cleanup and close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self.logger.info("Blackboard service shut down")

    async def _setup_indices(self) -> None:
        """Set up Redis search indices for efficient querying"""
        # This would set up RediSearch indices in a production system
        # For now, we'll use basic Redis operations

    # Knowledge Management Methods

    async def add_knowledge(self, knowledge: KnowledgeItem) -> str:
        """Add a knowledge item to the blackboard"""
        key = f"{self.spaces[knowledge.space]}:knowledge:{knowledge.id}"

        # Convert to dict and handle datetime serialization
        data = knowledge.model_dump()
        data["timestamp"] = data["timestamp"].isoformat()
        if data.get("expires_at"):
            data["expires_at"] = data["expires_at"].isoformat()
        data["tags"] = list(data["tags"])  # Convert set to list for JSON

        await self.redis_client.hset(key, mapping={"data": json.dumps(data)})

        # Set expiration if specified
        if knowledge.expires_at:
            # Handle both timezone-aware and naive datetimes
            current_time = datetime.now(timezone.utc)
            expires_at = knowledge.expires_at

            # Convert naive datetime to timezone-aware if needed
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            expire_seconds = int((expires_at - current_time).total_seconds())
            if expire_seconds > 0:
                await self.redis_client.expire(key, expire_seconds)

        # Add to priority queue for the space
        priority_key = f"{self.spaces[knowledge.space]}:priority"
        await self.redis_client.zadd(priority_key, {knowledge.id: knowledge.priority})

        # Add to agent's knowledge index
        agent_key = f"{self.spaces['agents']}:{knowledge.agent_id}:knowledge"
        await self.redis_client.sadd(agent_key, knowledge.id)

        # Publish notification
        await self._publish_event(
            "knowledge_added",
            {
                "knowledge_id": knowledge.id,
                "space": knowledge.space,
                "agent_id": knowledge.agent_id,
                "knowledge_type": knowledge.knowledge_type,
            },
        )

        self.logger.debug(
            f"Added knowledge item {knowledge.id} to space {knowledge.space}"
        )
        return knowledge.id

    async def get_knowledge(
        self, knowledge_id: str, space: str
    ) -> KnowledgeItem | None:
        """Retrieve a specific knowledge item"""
        key = f"{self.spaces[space]}:knowledge:{knowledge_id}"
        data = await self.redis_client.hget(key, "data")

        if not data:
            return None

        parsed_data = json.loads(data)
        parsed_data["timestamp"] = datetime.fromisoformat(parsed_data["timestamp"])
        if parsed_data.get("expires_at"):
            parsed_data["expires_at"] = datetime.fromisoformat(
                parsed_data["expires_at"]
            )
        parsed_data["tags"] = set(parsed_data["tags"])  # Convert list back to set

        return KnowledgeItem(**parsed_data)

    async def query_knowledge(
        self,
        space: str,
        knowledge_type: str | None = None,
        agent_id: str | None = None,
        tags: set[str] | None = None,
        limit: int = 100,
    ) -> list[KnowledgeItem]:
        """Query knowledge items with filters"""
        priority_key = f"{self.spaces[space]}:priority"

        # Get items by priority (lower score = higher priority)
        knowledge_ids = await self.redis_client.zrange(priority_key, 0, limit - 1)

        results = []
        for knowledge_id in knowledge_ids:
            knowledge = await self.get_knowledge(knowledge_id, space)
            if not knowledge:
                continue

            # Apply filters
            if knowledge_type and knowledge.knowledge_type != knowledge_type:
                continue
            if agent_id and knowledge.agent_id != agent_id:
                continue
            if tags and not tags.intersection(knowledge.tags):
                continue

            results.append(knowledge)

        return results

    # Task Management Methods

    async def create_task(self, task: TaskDefinition) -> str:
        """Create a new task on the blackboard"""
        key = f"{self.spaces['tasks']}:{task.id}"

        # Convert to dict and handle datetime serialization
        data = task.model_dump()
        data["created_at"] = data["created_at"].isoformat()
        if data.get("deadline"):
            data["deadline"] = data["deadline"].isoformat()
        if data.get("claimed_at"):
            data["claimed_at"] = data["claimed_at"].isoformat()
        if data.get("completed_at"):
            data["completed_at"] = data["completed_at"].isoformat()

        await self.redis_client.hset(key, mapping={"data": json.dumps(data)})

        # Add to task queues
        await self._add_to_task_queues(task)

        # Publish notification
        await self._publish_event(
            "task_created",
            {
                "task_id": task.id,
                "task_type": task.task_type,
                "priority": task.priority,
            },
        )

        self.logger.info(f"Created task {task.id} of type {task.task_type}")
        return task.id

    async def claim_task(self, task_id: str, agent_id: str) -> bool:
        """Attempt to claim a task for an agent"""
        key = f"{self.spaces['tasks']}:{task_id}"

        # Use Redis transaction to ensure atomicity
        async with self.redis_client.pipeline(transaction=True) as pipe:
            while True:
                try:
                    # Watch the task key
                    await pipe.watch(key)

                    # Get current task data
                    data = await pipe.hget(key, "data")
                    if not data:
                        return False

                    task_data = json.loads(data)
                    if task_data["status"] != "pending":
                        return False  # Task already claimed or completed

                    # Start transaction
                    pipe.multi()

                    # Update task status and agent
                    task_data["status"] = "claimed"
                    task_data["agent_id"] = agent_id
                    task_data["claimed_at"] = datetime.now(timezone.utc).isoformat()

                    await pipe.hset(key, "data", json.dumps(task_data))

                    # Remove from pending queue, add to claimed queue
                    pending_key = f"{self.spaces['tasks']}:pending:priority"
                    claimed_key = f"{self.spaces['tasks']}:claimed:priority"
                    await pipe.zrem(pending_key, task_id)
                    await pipe.zadd(claimed_key, {task_id: task_data["priority"]})

                    # Add to agent's task list
                    agent_tasks_key = f"{self.spaces['agents']}:{agent_id}:tasks"
                    await pipe.sadd(agent_tasks_key, task_id)

                    # Execute transaction
                    await pipe.execute()

                    # Publish notification
                    await self._publish_event(
                        "task_claimed",
                        {
                            "task_id": task_id,
                            "agent_id": agent_id,
                            "task_type": task_data["task_type"],
                        },
                    )

                    self.logger.info(f"Task {task_id} claimed by agent {agent_id}")
                    return True

                except redis.WatchError:
                    # Another client modified the task, retry
                    continue
                finally:
                    await pipe.reset()

    async def update_task_status(
        self, task_id: str, status: str, output_data: dict[str, Any] | None = None
    ) -> bool:
        """Update task status and optionally add output data"""
        key = f"{self.spaces['tasks']}:{task_id}"

        data = await self.redis_client.hget(key, "data")
        if not data:
            return False

        task_data = json.loads(data)
        old_status = task_data["status"]
        task_data["status"] = status

        if output_data:
            task_data["output_data"] = output_data

        if status == "completed":
            task_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        elif status == "in_progress" and old_status == "claimed":
            # Task moved from claimed to in_progress
            pass

        await self.redis_client.hset(key, "data", json.dumps(task_data))

        # Update task queues
        await self._update_task_queues(
            task_id, old_status, status, task_data["priority"]
        )

        # Publish notification
        if status == "completed":
            await self._publish_event(
                "task_completed",
                {
                    "task_id": task_id,
                    "agent_id": task_data.get("agent_id"),
                    "task_type": task_data["task_type"],
                    "output_data": output_data,
                },
            )

        self.logger.info(f"Task {task_id} status updated from {old_status} to {status}")
        return True

    async def get_available_tasks(
        self, task_types: list[str] | None = None, limit: int = 10
    ) -> list[TaskDefinition]:
        """Get available tasks for claiming"""
        pending_key = f"{self.spaces['tasks']}:pending:priority"

        # Get highest priority pending tasks
        task_ids = await self.redis_client.zrange(pending_key, 0, limit - 1)

        tasks = []
        for task_id in task_ids:
            task = await self.get_task(task_id)
            if not task:
                continue

            # Filter by task types if specified
            if task_types and task.task_type not in task_types:
                continue

            tasks.append(task)

        return tasks

    async def get_task(self, task_id: str) -> TaskDefinition | None:
        """Retrieve a specific task"""
        key = f"{self.spaces['tasks']}:{task_id}"
        data = await self.redis_client.hget(key, "data")

        if not data:
            return None

        task_data = json.loads(data)
        task_data["created_at"] = datetime.fromisoformat(task_data["created_at"])
        if task_data.get("deadline"):
            task_data["deadline"] = datetime.fromisoformat(task_data["deadline"])
        if task_data.get("claimed_at"):
            task_data["claimed_at"] = datetime.fromisoformat(task_data["claimed_at"])
        if task_data.get("completed_at"):
            task_data["completed_at"] = datetime.fromisoformat(
                task_data["completed_at"]
            )

        return TaskDefinition(**task_data)

    async def complete_task(
        self, task_id: str, agent_id: str, result: dict[str, Any]
    ) -> bool:
        """Complete a task with results"""
        key = f"{self.spaces['tasks']}:{task_id}"

        # Use Redis transaction to ensure atomicity
        async with self.redis_client.pipeline(transaction=True) as pipe:
            while True:
                try:
                    # Watch the task key
                    await pipe.watch(key)

                    # Get current task data
                    data = await pipe.hget(key, "data")
                    if not data:
                        return False

                    task_data = json.loads(data)

                    # Verify task is assigned to this agent
                    if task_data.get("agent_id") != agent_id:
                        return False

                    # Verify task is in a completable state
                    if task_data["status"] not in ["claimed", "in_progress"]:
                        return False

                    # Start transaction
                    pipe.multi()

                    # Update task status and completion data
                    old_status = task_data["status"]
                    task_data["status"] = "completed"
                    task_data["output_data"] = result
                    task_data["completed_at"] = datetime.now(timezone.utc).isoformat()

                    await pipe.hset(key, "data", json.dumps(task_data))

                    # Update task queues
                    if old_status in ["claimed", "in_progress"]:
                        old_queue = f"{self.spaces['tasks']}:{old_status}:priority"
                        await pipe.zrem(old_queue, task_id)

                    # Add to completed queue with timestamp
                    completed_queue = f"{self.spaces['tasks']}:completed:timestamp"
                    await pipe.zadd(completed_queue, {task_id: int(time.time())})

                    # Execute transaction
                    await pipe.execute()

                    # Publish notification
                    await self._publish_event(
                        "task_completed",
                        {
                            "task_id": task_id,
                            "agent_id": agent_id,
                            "task_type": task_data["task_type"],
                            "output_data": result,
                        },
                    )

                    self.logger.info(f"Task {task_id} completed by agent {agent_id}")
                    return True

                except redis.WatchError:
                    # Another client modified the task, retry
                    continue
                finally:
                    await pipe.reset()

    async def fail_task(
        self, task_id: str, agent_id: str, error_details: dict[str, Any]
    ) -> bool:
        """Mark a task as failed with error details"""
        key = f"{self.spaces['tasks']}:{task_id}"

        # Use Redis transaction to ensure atomicity
        async with self.redis_client.pipeline(transaction=True) as pipe:
            while True:
                try:
                    # Watch the task key
                    await pipe.watch(key)

                    # Get current task data
                    data = await pipe.hget(key, "data")
                    if not data:
                        return False

                    task_data = json.loads(data)

                    # Verify task is assigned to this agent
                    if task_data.get("agent_id") != agent_id:
                        return False

                    # Verify task is in a failable state
                    if task_data["status"] not in ["claimed", "in_progress"]:
                        return False

                    # Start transaction
                    pipe.multi()

                    # Update task status and error data
                    old_status = task_data["status"]
                    task_data["status"] = "failed"
                    task_data["error_details"] = error_details
                    task_data["completed_at"] = datetime.now(
                        timezone.utc
                    ).isoformat()  # Failed tasks also get completion timestamp

                    await pipe.hset(key, "data", json.dumps(task_data))

                    # Update task queues
                    if old_status in ["claimed", "in_progress"]:
                        old_queue = f"{self.spaces['tasks']}:{old_status}:priority"
                        await pipe.zrem(old_queue, task_id)

                    # Add to failed queue with timestamp
                    failed_queue = f"{self.spaces['tasks']}:failed:timestamp"
                    await pipe.zadd(failed_queue, {task_id: int(time.time())})

                    # Execute transaction
                    await pipe.execute()

                    # Publish notification
                    await self._publish_event(
                        "task_failed",
                        {
                            "task_id": task_id,
                            "agent_id": agent_id,
                            "task_type": task_data["task_type"],
                            "error_details": error_details,
                        },
                    )

                    self.logger.warning(
                        f"Task {task_id} failed by agent {agent_id}: {error_details}"
                    )
                    return True

                except redis.WatchError:
                    # Another client modified the task, retry
                    continue
                finally:
                    await pipe.reset()

    async def get_pending_tasks(self, limit: int = 50) -> list[TaskDefinition]:
        """Get all pending tasks ordered by priority"""
        pending_key = f"{self.spaces['tasks']}:pending:priority"

        # Get highest priority pending tasks
        task_ids = await self.redis_client.zrange(pending_key, 0, limit - 1)

        tasks = []
        for task_id in task_ids:
            task = await self.get_task(task_id)
            if task and task.status == "pending":
                tasks.append(task)

        return tasks

    async def get_agent_tasks(
        self, agent_id: str, statuses: list[str] | None = None
    ) -> list[TaskDefinition]:
        """Get all tasks assigned to a specific agent, optionally filtered by status"""
        # Get task IDs from agent's task set
        agent_tasks_key = f"{self.spaces['agents']}:{agent_id}:tasks"
        task_ids = await self.redis_client.smembers(agent_tasks_key)

        tasks = []
        for task_id in task_ids:
            task = await self.get_task(task_id)
            if not task:
                # Clean up stale reference
                await self.redis_client.srem(agent_tasks_key, task_id)
                continue

            # Filter by status if specified
            if statuses and task.status not in statuses:
                continue

            tasks.append(task)

        # Sort by priority (higher priority first) then by creation time
        tasks.sort(key=lambda t: (-t.priority, t.created_at))
        return tasks

    # Conflict Management Methods

    async def report_conflict(self, conflict: ConflictItem) -> str:
        """Report a conflict to the blackboard"""
        key = f"{self.spaces['conflicts']}:{conflict.id}"

        # Convert to dict and handle datetime serialization
        data = conflict.model_dump()
        data["created_at"] = data["created_at"].isoformat()
        if data.get("resolved_at"):
            data["resolved_at"] = data["resolved_at"].isoformat()

        await self.redis_client.hset(key, mapping={"data": json.dumps(data)})

        # Add to conflict priority queue based on severity
        severity_priority = {"critical": 1, "high": 2, "medium": 3, "low": 4}
        priority = severity_priority.get(conflict.severity, 3)

        conflicts_key = f"{self.spaces['conflicts']}:open:priority"
        await self.redis_client.zadd(conflicts_key, {conflict.id: priority})

        # Publish notification
        await self._publish_event(
            "conflict_detected",
            {
                "conflict_id": conflict.id,
                "conflict_type": conflict.conflict_type,
                "severity": conflict.severity,
                "involved_agents": conflict.involved_agents,
            },
        )

        self.logger.warning(
            f"Conflict {conflict.id} reported: {conflict.conflict_type} (severity: {conflict.severity})"
        )
        return conflict.id

    async def get_open_conflicts(self, limit: int = 20) -> list[ConflictItem]:
        """Get open conflicts ordered by priority"""
        conflicts_key = f"{self.spaces['conflicts']}:open:priority"
        conflict_ids = await self.redis_client.zrange(conflicts_key, 0, limit - 1)

        conflicts = []
        for conflict_id in conflict_ids:
            conflict = await self.get_conflict(conflict_id)
            if conflict and conflict.status == "open":
                conflicts.append(conflict)

        return conflicts

    async def get_conflict(self, conflict_id: str) -> ConflictItem | None:
        """Retrieve a specific conflict"""
        key = f"{self.spaces['conflicts']}:{conflict_id}"
        data = await self.redis_client.hget(key, "data")

        if not data:
            return None

        conflict_data = json.loads(data)
        conflict_data["created_at"] = datetime.fromisoformat(
            conflict_data["created_at"]
        )
        if conflict_data.get("resolved_at"):
            conflict_data["resolved_at"] = datetime.fromisoformat(
                conflict_data["resolved_at"]
            )

        return ConflictItem(**conflict_data)

    async def resolve_conflict(
        self,
        conflict_id: str,
        resolution_strategy: str,
        resolution_data: dict[str, Any],
    ) -> bool:
        """Mark a conflict as resolved"""
        key = f"{self.spaces['conflicts']}:{conflict_id}"

        data = await self.redis_client.hget(key, "data")
        if not data:
            return False

        conflict_data = json.loads(data)
        conflict_data["status"] = "resolved"
        conflict_data["resolution_strategy"] = resolution_strategy
        conflict_data["resolution_data"] = resolution_data
        conflict_data["resolved_at"] = datetime.now(timezone.utc).isoformat()

        await self.redis_client.hset(key, "data", json.dumps(conflict_data))

        # Remove from open conflicts queue
        open_key = f"{self.spaces['conflicts']}:open:priority"
        resolved_key = f"{self.spaces['conflicts']}:resolved:priority"
        await self.redis_client.zrem(open_key, conflict_id)
        await self.redis_client.zadd(resolved_key, {conflict_id: int(time.time())})

        self.logger.info(
            f"Conflict {conflict_id} resolved using strategy: {resolution_strategy}"
        )
        return True

    # Agent Management Methods

    async def register_agent(
        self, agent_id: str, agent_type: str, capabilities: list[str]
    ) -> None:
        """Register an agent with the blackboard"""
        agent_key = f"{self.spaces['agents']}:{agent_id}"

        agent_data = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "capabilities": capabilities,
            "status": "active",
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "last_heartbeat": datetime.now(timezone.utc).isoformat(),
        }

        await self.redis_client.hset(
            agent_key, mapping={"data": json.dumps(agent_data)}
        )

        # Add to active agents set
        await self.redis_client.sadd(f"{self.spaces['agents']}:active", agent_id)

        self.logger.info(f"Agent {agent_id} registered with type {agent_type}")

    async def agent_heartbeat(self, agent_id: str) -> None:
        """Update agent heartbeat"""
        agent_key = f"{self.spaces['agents']}:{agent_id}"

        # Update last heartbeat
        await self.redis_client.hset(
            agent_key, "last_heartbeat", datetime.now(timezone.utc).isoformat()
        )

    async def get_active_agents(self) -> list[str]:
        """Get list of active agent IDs"""
        return await self.redis_client.smembers(f"{self.spaces['agents']}:active")

    async def check_agent_timeouts(self, timeout_minutes: int = 5) -> list[str]:
        """Check for agents that haven't sent heartbeat within timeout period"""
        timed_out_agents = []
        active_agents = await self.get_active_agents()

        current_time = datetime.now(timezone.utc)
        timeout_threshold = current_time - timedelta(minutes=timeout_minutes)

        # Create a copy of the list to avoid modification during iteration
        for agent_id in list(active_agents):
            agent_key = f"{self.spaces['agents']}:{agent_id}"
            agent_data_raw = await self.redis_client.hget(agent_key, "data")

            if agent_data_raw:
                try:
                    agent_data = json.loads(agent_data_raw)
                    last_heartbeat_str = agent_data.get("last_heartbeat")

                    if last_heartbeat_str:
                        last_heartbeat = datetime.fromisoformat(
                            last_heartbeat_str.replace("Z", "+00:00")
                        )
                        if last_heartbeat < timeout_threshold:
                            timed_out_agents.append(agent_id)
                            # Remove from active agents
                            await self.redis_client.srem(
                                f"{self.spaces['agents']}:active", agent_id
                            )
                except (json.JSONDecodeError, ValueError) as e:
                    self.logger.warning(f"Error parsing agent data for {agent_id}: {e}")

        return timed_out_agents

    # Event and Notification Methods

    async def subscribe_to_events(
        self, agent_id: str, event_types: list[str]
    ) -> redis.Redis:
        """Subscribe to specific event types"""
        # Create a separate Redis connection for pub/sub
        subscriber = redis.from_url(self.redis_url, db=self.db, decode_responses=True)

        channels = [
            self.channels[event_type]
            for event_type in event_types
            if event_type in self.channels
        ]
        if channels:
            await subscriber.subscribe(*channels)

        return subscriber

    async def _publish_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Publish an event to the appropriate channel"""
        if event_type in self.channels:
            event_data = {
                "event_type": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data,
            }
            await self.redis_client.publish(
                self.channels[event_type], json.dumps(event_data)
            )

    # Helper Methods

    async def _add_to_task_queues(self, task: TaskDefinition) -> None:
        """Add task to appropriate priority queues"""
        if task.status == "pending":
            queue_key = f"{self.spaces['tasks']}:pending:priority"
            await self.redis_client.zadd(queue_key, {task.id: task.priority})
        elif task.status == "claimed":
            queue_key = f"{self.spaces['tasks']}:claimed:priority"
            await self.redis_client.zadd(queue_key, {task.id: task.priority})

    async def _update_task_queues(
        self, task_id: str, old_status: str, new_status: str, priority: int
    ) -> None:
        """Update task queues when status changes"""
        # Remove from old queue
        if old_status in ["pending", "claimed", "in_progress"]:
            old_queue = f"{self.spaces['tasks']}:{old_status}:priority"
            await self.redis_client.zrem(old_queue, task_id)

        # Add to new queue
        if new_status in ["pending", "claimed", "in_progress"]:
            new_queue = f"{self.spaces['tasks']}:{new_status}:priority"
            await self.redis_client.zadd(new_queue, {task_id: priority})
        elif new_status in ["completed", "failed"]:
            archive_queue = f"{self.spaces['tasks']}:{new_status}:timestamp"
            await self.redis_client.zadd(archive_queue, {task_id: int(time.time())})

    async def get_metrics(self) -> dict[str, Any]:
        """Get blackboard performance metrics"""
        metrics = {
            "tasks": {
                "pending": await self.redis_client.zcard(
                    f"{self.spaces['tasks']}:pending:priority"
                ),
                "claimed": await self.redis_client.zcard(
                    f"{self.spaces['tasks']}:claimed:priority"
                ),
                "in_progress": await self.redis_client.zcard(
                    f"{self.spaces['tasks']}:in_progress:priority"
                ),
                "completed": await self.redis_client.zcard(
                    f"{self.spaces['tasks']}:completed:timestamp"
                ),
                "failed": await self.redis_client.zcard(
                    f"{self.spaces['tasks']}:failed:timestamp"
                ),
            },
            "conflicts": {
                "open": await self.redis_client.zcard(
                    f"{self.spaces['conflicts']}:open:priority"
                ),
                "resolved": await self.redis_client.zcard(
                    f"{self.spaces['conflicts']}:resolved:priority"
                ),
            },
            "agents": {
                "active": await self.redis_client.scard(
                    f"{self.spaces['agents']}:active"
                )
            },
            "knowledge_items": {},
        }

        # Count knowledge items by space
        for space_name in ["governance", "compliance", "performance", "coordination"]:
            priority_key = f"{self.spaces[space_name]}:priority"
            metrics["knowledge_items"][space_name] = await self.redis_client.zcard(
                priority_key
            )

        return metrics

    async def cleanup_expired_items(self) -> int:
        """Clean up expired knowledge items and old tasks"""
        cleaned_count = 0

        # This would implement cleanup logic for expired items
        # For now, Redis TTL handles most expiration automatically

        return cleaned_count
