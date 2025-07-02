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
