"""
Core Blackboard Service for Multi-Agent Coordination.

This module provides the main BlackboardService class that orchestrates
knowledge sharing, task coordination, and conflict resolution using
focused manager components.
"""

import logging
from typing import Any

import redis.asyncio as redis

from .conflict_manager import ConflictManager
from .event_publisher import EventPublisher
from .knowledge_manager import KnowledgeManager
from .models import ConflictItem, KnowledgeItem, TaskDefinition
from .task_manager import TaskManager

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class BlackboardService:
    """
    Redis-based blackboard service for multi-agent coordination.

    Implements knowledge sharing, task coordination, and conflict resolution
    through focused manager components for better maintainability.

    Example:
        service = BlackboardService("redis://localhost:6379")
        await service.initialize()

        # Add knowledge
        knowledge = KnowledgeItem(
            space="governance",
            agent_id="ethics_agent",
            knowledge_type="policy",
            content={"rule": "transparency"}
        )
        await service.add_knowledge(knowledge)
    """

    def __init__(self, redis_url: str = "redis://localhost:6379", db: int = 0):
        """
        Initialize the blackboard service.

        Args:
            redis_url: Redis connection URL
            db: Redis database number
        """
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

        # Manager instances (initialized in initialize())
        self.knowledge_manager: KnowledgeManager | None = None
        self.task_manager: TaskManager | None = None
        self.conflict_manager: ConflictManager | None = None
        self.event_publisher: EventPublisher | None = None

    async def initialize(self) -> None:
        """
        Initialize Redis connection and set up the blackboard.

        Example:
            await service.initialize()
        """
        self.redis_client = redis.from_url(
            self.redis_url, db=self.db, decode_responses=True
        )

        # Test connection
        await self.redis_client.ping()
        self.logger.info("Blackboard service initialized successfully")

        # Initialize manager components
        self.knowledge_manager = KnowledgeManager(self.redis_client, self.spaces)
        self.task_manager = TaskManager(self.redis_client, self.spaces)
        self.conflict_manager = ConflictManager(self.redis_client, self.spaces)
        self.event_publisher = EventPublisher(self.redis_client, self.channels)

        # Set up initial schemas and indices if needed
        await self._setup_indices()

    async def shutdown(self) -> None:
        """
        Cleanup and close Redis connection.

        Example:
            await service.shutdown()
        """
        if self.redis_client:
            await self.redis_client.close()
            self.logger.info("Blackboard service shut down")

    async def _setup_indices(self) -> None:
        """Set up Redis search indices for efficient querying."""
        # This would set up RediSearch indices in a production system
        # For now, we'll use basic Redis operations

    # Knowledge Management Delegation

    async def add_knowledge(self, knowledge: KnowledgeItem) -> str:
        """
        Add a knowledge item to the blackboard.

        Args:
            knowledge: The knowledge item to add

        Returns:
            The ID of the added knowledge item

        Example:
            knowledge_id = await service.add_knowledge(
                KnowledgeItem(
                    space="governance",
                    agent_id="ethics_agent",
                    knowledge_type="policy",
                    content={"rule": "transparency"}
                )
            )
        """
        if not self.knowledge_manager:
            raise RuntimeError("Service not initialized")

        knowledge_id = await self.knowledge_manager.add_knowledge(knowledge)

        # Publish notification
        await self.event_publisher.publish_knowledge_added(
            knowledge_id, knowledge.space, knowledge.agent_id, knowledge.knowledge_type
        )

        return knowledge_id

    async def get_knowledge(
        self, knowledge_id: str, space: str
    ) -> KnowledgeItem | None:
        """
        Retrieve a specific knowledge item.

        Args:
            knowledge_id: The ID of the knowledge to retrieve
            space: The knowledge space to search in

        Returns:
            The knowledge item if found, None otherwise
        """
        if not self.knowledge_manager:
            raise RuntimeError("Service not initialized")

        return await self.knowledge_manager.get_knowledge(knowledge_id, space)

    # Task Management Delegation

    async def create_task(self, task: TaskDefinition) -> str:
        """
        Create a new task on the blackboard.

        Args:
            task: The task definition to create

        Returns:
            The ID of the created task

        Example:
            task_id = await service.create_task(
                TaskDefinition(
                    task_type="ethical_analysis",
                    requirements={"domain": "healthcare"},
                    input_data={"proposal": "policy.json"}
                )
            )
        """
        if not self.task_manager:
            raise RuntimeError("Service not initialized")

        task_id = await self.task_manager.create_task(task)

        # Publish notification
        await self.event_publisher.publish_task_created(
            task_id, task.task_type, task.priority
        )

        return task_id

    async def claim_task(self, task_id: str, agent_id: str) -> bool:
        """
        Claim a task for an agent.

        Args:
            task_id: The ID of the task to claim
            agent_id: The ID of the claiming agent

        Returns:
            True if successfully claimed, False otherwise
        """
        if not self.task_manager:
            raise RuntimeError("Service not initialized")

        success = await self.task_manager.claim_task(task_id, agent_id)

        if success:
            await self.event_publisher.publish_task_claimed(task_id, agent_id)

        return success

    async def get_pending_tasks(self, limit: int = 50) -> list[TaskDefinition]:
        """
        Get all pending tasks ordered by priority.

        Args:
            limit: Maximum number of tasks to return

        Returns:
            List of pending tasks

        Example:
            pending_tasks = await service.get_pending_tasks(10)
        """
        if not self.task_manager:
            raise RuntimeError("Service not initialized")

        # Use get_available_tasks which returns pending tasks
        return await self.task_manager.get_available_tasks(task_type=None, limit=limit)

    async def get_task(self, task_id: str) -> TaskDefinition | None:
        """
        Retrieve a specific task.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            Task definition or None if not found

        Example:
            task = await service.get_task("task_12345")
        """
        if not self.task_manager:
            raise RuntimeError("Service not initialized")

        return await self.task_manager.get_task(task_id)

    async def update_task_status(
        self, task_id: str, status: str, output_data: dict[str, Any] | None = None
    ) -> bool:
        """
        Update task status and optionally add output data.

        Args:
            task_id: The ID of the task to update
            status: New status ('in_progress', 'completed', 'failed')
            output_data: Task output data (for completed tasks)

        Returns:
            True if successfully updated, False otherwise

        Example:
            success = await service.update_task_status(
                "task_12345",
                "completed",
                output_data={"result": "approved"}
            )
        """
        if not self.task_manager:
            raise RuntimeError("Service not initialized")

        return await self.task_manager.update_task_status(task_id, status, output_data)

    async def query_knowledge(
        self,
        space: str,
        knowledge_type: str | None = None,
        agent_id: str | None = None,
        tags: set[str] | None = None,
        limit: int = 100,
    ) -> list[KnowledgeItem]:
        """
        Query knowledge items with filters.

        Args:
            space: Knowledge space to search in
            knowledge_type: Filter by knowledge type
            agent_id: Filter by agent ID
            tags: Filter by tags (intersection)
            limit: Maximum number of results

        Returns:
            List of matching knowledge items

        Example:
            results = await service.query_knowledge(
                space="governance",
                knowledge_type="ethical_analysis",
                agent_id="ethics_agent_1"
            )
        """
        if not self.knowledge_manager:
            raise RuntimeError("Service not initialized")

        return await self.knowledge_manager.query_knowledge(
            space, knowledge_type, agent_id, tags, limit
        )

    # Conflict Management Delegation

    async def create_conflict(self, conflict: ConflictItem) -> str:
        """
        Create a new conflict entry.

        Args:
            conflict: The conflict definition to create

        Returns:
            The ID of the created conflict
        """
        if not self.conflict_manager:
            raise RuntimeError("Service not initialized")

        conflict_id = await self.conflict_manager.create_conflict(conflict)

        # Publish notification
        await self.event_publisher.publish_conflict_detected(
            conflict_id,
            conflict.conflict_type,
            conflict.involved_agents,
            conflict.severity,
        )

        return conflict_id

    async def get_metrics(self) -> dict[str, Any]:
        """
        Get blackboard performance metrics.

        Returns:
            Dictionary containing various metrics

        Example:
            metrics = await service.get_metrics()
            print(f"Pending tasks: {metrics['tasks']['pending']}")
        """
        if not self.redis_client:
            raise RuntimeError("Service not initialized")

        metrics = {
            "tasks": {
                "pending": await self.redis_client.scard(
                    f"{self.spaces['tasks']}:status:pending"
                ),
                "claimed": await self.redis_client.scard(
                    f"{self.spaces['tasks']}:status:claimed"
                ),
                "completed": await self.redis_client.scard(
                    f"{self.spaces['tasks']}:status:completed"
                ),
                "failed": await self.redis_client.scard(
                    f"{self.spaces['tasks']}:status:failed"
                ),
            },
            "conflicts": {
                "open": await self.redis_client.scard(
                    f"{self.spaces['conflicts']}:status:open"
                ),
                "resolved": await self.redis_client.scard(
                    f"{self.spaces['conflicts']}:status:resolved"
                ),
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

    # Agent Management Methods

    async def register_agent(
        self, agent_id: str, agent_type: str, capabilities: list[str]
    ) -> None:
        """
        Register an agent with the blackboard.

        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent (e.g., 'ethics_agent')
            capabilities: List of agent capabilities

        Example:
            await service.register_agent(
                "ethics_agent_1",
                "ethics_agent",
                ["bias_detection", "fairness_evaluation"]
            )
        """
        if not self.redis_client:
            raise RuntimeError("Service not initialized")

        import json
        from datetime import datetime, timezone

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
        """
        Update agent heartbeat.

        Args:
            agent_id: ID of the agent sending heartbeat

        Example:
            await service.agent_heartbeat("ethics_agent_1")
        """
        if not self.redis_client:
            raise RuntimeError("Service not initialized")

        from datetime import datetime, timezone

        agent_key = f"{self.spaces['agents']}:{agent_id}"

        # Update last heartbeat
        await self.redis_client.hset(
            agent_key, "last_heartbeat", datetime.now(timezone.utc).isoformat()
        )

    async def get_active_agents(self) -> list[str]:
        """
        Get list of active agent IDs.

        Returns:
            List of active agent IDs

        Example:
            active_agents = await service.get_active_agents()
        """
        if not self.redis_client:
            raise RuntimeError("Service not initialized")

        return list(await self.redis_client.smembers(f"{self.spaces['agents']}:active"))

    async def check_agent_timeouts(self, timeout_minutes: int = 5) -> list[str]:
        """
        Check for agents that haven't sent heartbeat within timeout period.

        Args:
            timeout_minutes: Timeout threshold in minutes

        Returns:
            List of timed out agent IDs

        Example:
            timed_out = await service.check_agent_timeouts(5)
        """
        if not self.redis_client:
            raise RuntimeError("Service not initialized")

        import json
        from datetime import datetime, timedelta, timezone

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
