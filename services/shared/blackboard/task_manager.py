"""
Task management functionality for the Blackboard service.

This module handles task creation, claiming, coordination, and completion
within the multi-agent governance system.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

import redis.asyncio as redis

from .models import TaskDefinition


class TaskManager:
    """
    Manages tasks on the blackboard system.

    Provides functionality for task lifecycle management including
    creation, claiming, execution tracking, and completion.
    """

    def __init__(self, redis_client: redis.Redis, spaces: dict[str, str]):
        self.redis_client = redis_client
        self.spaces = spaces
        self.logger = logging.getLogger(__name__)

    async def create_task(self, task: TaskDefinition) -> str:
        """
        Create a new task on the blackboard.

        Args:
            task: The task definition to create

        Returns:
            The ID of the created task

        Example:
            task_id = await manager.create_task(
                TaskDefinition(
                    task_type="ethical_analysis",
                    requirements={"domain": "healthcare"},
                    input_data={"proposal": "policy.json"}
                )
            )
        """
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

        # Add to priority queue
        priority_key = f"{self.spaces['tasks']}:priority"
        await self.redis_client.zadd(priority_key, {task.id: task.priority})

        # Add to status index
        status_key = f"{self.spaces['tasks']}:status:{task.status}"
        await self.redis_client.sadd(status_key, task.id)

        # Add to type index
        type_key = f"{self.spaces['tasks']}:type:{task.task_type}"
        await self.redis_client.sadd(type_key, task.id)

        self.logger.debug(f"Created task {task.id} of type {task.task_type}")
        return task.id

    async def get_task(self, task_id: str) -> TaskDefinition | None:
        """
        Retrieve a specific task.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            The task definition if found, None otherwise

        Example:
            task = await manager.get_task("task_12345")
        """
        key = f"{self.spaces['tasks']}:{task_id}"
        data = await self.redis_client.hget(key, "data")

        if not data:
            return None

        parsed_data = json.loads(data)
        parsed_data["created_at"] = datetime.fromisoformat(parsed_data["created_at"])
        if parsed_data.get("deadline"):
            parsed_data["deadline"] = datetime.fromisoformat(parsed_data["deadline"])
        if parsed_data.get("claimed_at"):
            parsed_data["claimed_at"] = datetime.fromisoformat(
                parsed_data["claimed_at"]
            )
        if parsed_data.get("completed_at"):
            parsed_data["completed_at"] = datetime.fromisoformat(
                parsed_data["completed_at"]
            )

        return TaskDefinition(**parsed_data)

    async def claim_task(self, task_id: str, agent_id: str) -> bool:
        """
        Claim a task for an agent.

        Args:
            task_id: The ID of the task to claim
            agent_id: The ID of the claiming agent

        Returns:
            True if successfully claimed, False otherwise

        Example:
            success = await manager.claim_task("task_12345", "ethics_agent")
        """
        task = await self.get_task(task_id)
        if not task or task.status != "pending":
            return False

        # Update task status and agent
        task.status = "claimed"
        task.agent_id = agent_id
        task.claimed_at = datetime.now(timezone.utc)

        # Save updated task
        await self._update_task(task)

        # Update status indices
        await self.redis_client.srem(f"{self.spaces['tasks']}:status:pending", task_id)
        await self.redis_client.sadd(f"{self.spaces['tasks']}:status:claimed", task_id)

        # Add to agent's task index
        agent_key = f"{self.spaces['agents']}:{agent_id}:tasks"
        await self.redis_client.sadd(agent_key, task_id)

        self.logger.debug(f"Task {task_id} claimed by agent {agent_id}")
        return True

    async def update_task_status(
        self,
        task_id: str,
        status: str,
        output_data: dict[str, Any] | None = None,
        error_details: dict[str, Any] | None = None,
    ) -> bool:
        """
        Update task status and results.

        Args:
            task_id: The ID of the task to update
            status: New status ('in_progress', 'completed', 'failed')
            output_data: Task output data (for completed tasks)
            error_details: Error information (for failed tasks)

        Returns:
            True if successfully updated, False otherwise

        Example:
            success = await manager.update_task_status(
                "task_12345",
                "completed",
                output_data={"result": "approved"}
            )
        """
        task = await self.get_task(task_id)
        if not task:
            return False

        old_status = task.status
        task.status = status

        if output_data:
            task.output_data = output_data
        if error_details:
            task.error_details = error_details

        if status == "completed":
            task.completed_at = datetime.now(timezone.utc)
        elif status == "failed":
            task.retries += 1

        # Save updated task
        await self._update_task(task)

        # Update status indices
        await self.redis_client.srem(
            f"{self.spaces['tasks']}:status:{old_status}", task_id
        )
        await self.redis_client.sadd(f"{self.spaces['tasks']}:status:{status}", task_id)

        self.logger.debug(f"Task {task_id} status updated to {status}")
        return True

    async def get_available_tasks(
        self, task_type: str | None = None, limit: int = 10
    ) -> list[TaskDefinition]:
        """
        Get available tasks for agents to claim.

        Args:
            task_type: Filter by task type
            limit: Maximum number of tasks to return

        Returns:
            List of available tasks

        Example:
            tasks = await manager.get_available_tasks("ethical_analysis")
        """
        if task_type:
            # Get tasks from type index
            type_key = f"{self.spaces['tasks']}:type:{task_type}"
            task_ids = await self.redis_client.sinter(
                type_key, f"{self.spaces['tasks']}:status:pending"
            )
        else:
            # Get all pending tasks
            task_ids = await self.redis_client.smembers(
                f"{self.spaces['tasks']}:status:pending"
            )

        # Convert to list and limit
        task_ids = list(task_ids)[:limit]

        tasks = []
        for task_id in task_ids:
            task = await self.get_task(task_id)
            if task:
                tasks.append(task)

        # Sort by priority (lower number = higher priority)
        tasks.sort(key=lambda t: t.priority)
        return tasks

    async def _update_task(self, task: TaskDefinition) -> None:
        """Update task data in Redis."""
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
