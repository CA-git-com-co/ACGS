"""
Event publishing functionality for the Blackboard service.

This module handles publishing events and notifications across the
multi-agent system for real-time coordination.
"""

import json
import logging
from typing import Any

import redis.asyncio as redis


class EventPublisher:
    """
    Publishes events for blackboard notifications.

    Handles publishing various types of events to Redis channels
    for real-time agent coordination and monitoring.
    """

    def __init__(self, redis_client: redis.Redis, channels: dict[str, str]):
        self.redis_client = redis_client
        self.channels = channels
        self.logger = logging.getLogger(__name__)

    async def publish_event(self, event_type: str, data: dict[str, Any]) -> int:
        """
        Publish an event to the appropriate channel.

        Args:
            event_type: Type of event to publish
            data: Event data to include

        Returns:
            Number of subscribers that received the event

        Example:
            subscribers = await publisher.publish_event(
                "task_created",
                {"task_id": "12345", "task_type": "ethical_analysis"}
            )
        """
        if event_type not in self.channels:
            self.logger.warning(f"Unknown event type: {event_type}")
            return 0

        channel = self.channels[event_type]
        event_data = {
            "event_type": event_type,
            "timestamp": data.get("timestamp", ""),
            "data": data,
        }

        try:
            subscribers = await self.redis_client.publish(
                channel, json.dumps(event_data)
            )

            self.logger.debug(
                f"Published {event_type} event to {subscribers} subscribers"
            )
            return subscribers

        except Exception as e:
            self.logger.error(f"Failed to publish event {event_type}: {e}")
            return 0

    async def publish_task_created(
        self, task_id: str, task_type: str, priority: int
    ) -> int:
        """
        Publish task creation event.

        Args:
            task_id: ID of the created task
            task_type: Type of the task
            priority: Task priority

        Returns:
            Number of subscribers notified

        Example:
            await publisher.publish_task_created(
                "task_12345",
                "ethical_analysis",
                1
            )
        """
        return await self.publish_event(
            "task_created",
            {"task_id": task_id, "task_type": task_type, "priority": priority},
        )

    async def publish_task_claimed(self, task_id: str, agent_id: str) -> int:
        """
        Publish task claimed event.

        Args:
            task_id: ID of the claimed task
            agent_id: ID of the claiming agent

        Returns:
            Number of subscribers notified
        """
        return await self.publish_event(
            "task_claimed", {"task_id": task_id, "agent_id": agent_id}
        )

    async def publish_task_completed(
        self, task_id: str, agent_id: str, success: bool
    ) -> int:
        """
        Publish task completion event.

        Args:
            task_id: ID of the completed task
            agent_id: ID of the completing agent
            success: Whether task completed successfully

        Returns:
            Number of subscribers notified
        """
        return await self.publish_event(
            "task_completed",
            {"task_id": task_id, "agent_id": agent_id, "success": success},
        )

    async def publish_conflict_detected(
        self, conflict_id: str, conflict_type: str, involved_agents: list, severity: str
    ) -> int:
        """
        Publish conflict detection event.

        Args:
            conflict_id: ID of the detected conflict
            conflict_type: Type of conflict
            involved_agents: List of involved agent IDs
            severity: Conflict severity

        Returns:
            Number of subscribers notified
        """
        return await self.publish_event(
            "conflict_detected",
            {
                "conflict_id": conflict_id,
                "conflict_type": conflict_type,
                "involved_agents": involved_agents,
                "severity": severity,
            },
        )

    async def publish_knowledge_added(
        self, knowledge_id: str, space: str, agent_id: str, knowledge_type: str
    ) -> int:
        """
        Publish knowledge addition event.

        Args:
            knowledge_id: ID of the added knowledge
            space: Knowledge space
            agent_id: ID of the contributing agent
            knowledge_type: Type of knowledge

        Returns:
            Number of subscribers notified
        """
        return await self.publish_event(
            "knowledge_added",
            {
                "knowledge_id": knowledge_id,
                "space": space,
                "agent_id": agent_id,
                "knowledge_type": knowledge_type,
            },
        )

    async def publish_agent_status(
        self, agent_id: str, status: str, details: dict[str, Any] | None = None
    ) -> int:
        """
        Publish agent status change event.

        Args:
            agent_id: ID of the agent
            status: New status ('online', 'offline', 'busy', 'idle')
            details: Additional status details

        Returns:
            Number of subscribers notified
        """
        event_data = {"agent_id": agent_id, "status": status}
        if details:
            event_data["details"] = details

        return await self.publish_event("agent_status", event_data)
