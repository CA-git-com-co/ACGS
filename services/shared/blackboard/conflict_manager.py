"""
Conflict management functionality for the Blackboard service.

This module handles detection, tracking, and resolution of conflicts
between agents and decisions in the governance system.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

import redis.asyncio as redis

from .models import ConflictItem

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ConflictManager:
    """
    Manages conflicts on the blackboard system.

    Provides functionality for conflict detection, tracking,
    and resolution coordination between agents.
    """

    def __init__(self, redis_client: redis.Redis, spaces: dict[str, str]):
        self.redis_client = redis_client
        self.spaces = spaces
        self.logger = logging.getLogger(__name__)

    async def create_conflict(self, conflict: ConflictItem) -> str:
        """
        Create a new conflict entry.

        Args:
            conflict: The conflict definition to create

        Returns:
            The ID of the created conflict

        Example:
            conflict_id = await manager.create_conflict(
                ConflictItem(
                    conflict_type="decision_conflict",
                    involved_agents=["ethics_agent", "legal_agent"],
                    description="Policy interpretation disagreement"
                )
            )
        """
        key = f"{self.spaces['conflicts']}:{conflict.id}"

        # Convert to dict and handle datetime serialization
        data = conflict.model_dump()
        data["created_at"] = data["created_at"].isoformat()
        if data.get("resolved_at"):
            data["resolved_at"] = data["resolved_at"].isoformat()

        await self.redis_client.hset(key, mapping={"data": json.dumps(data)})

        # Add to severity index
        severity_key = f"{self.spaces['conflicts']}:severity:{conflict.severity}"
        await self.redis_client.sadd(severity_key, conflict.id)

        # Add to status index
        status_key = f"{self.spaces['conflicts']}:status:{conflict.status}"
        await self.redis_client.sadd(status_key, conflict.id)

        # Add to agent indices
        for agent_id in conflict.involved_agents:
            agent_key = f"{self.spaces['agents']}:{agent_id}:conflicts"
            await self.redis_client.sadd(agent_key, conflict.id)

        self.logger.warning(f"Created conflict {conflict.id}: {conflict.description}")
        return conflict.id

    async def get_conflict(self, conflict_id: str) -> ConflictItem | None:
        """
        Retrieve a specific conflict.

        Args:
            conflict_id: The ID of the conflict to retrieve

        Returns:
            The conflict item if found, None otherwise

        Example:
            conflict = await manager.get_conflict("conflict_12345")
        """
        key = f"{self.spaces['conflicts']}:{conflict_id}"
        data = await self.redis_client.hget(key, "data")

        if not data:
            return None

        parsed_data = json.loads(data)
        parsed_data["created_at"] = datetime.fromisoformat(parsed_data["created_at"])
        if parsed_data.get("resolved_at"):
            parsed_data["resolved_at"] = datetime.fromisoformat(
                parsed_data["resolved_at"]
            )

        return ConflictItem(**parsed_data)

    async def update_conflict_status(
        self,
        conflict_id: str,
        status: str,
        resolution_strategy: str | None = None,
        resolution_data: dict[str, Any] | None = None,
    ) -> bool:
        """
        Update conflict status and resolution information.

        Args:
            conflict_id: The ID of the conflict to update
            status: New status ('in_resolution', 'resolved', 'escalated')
            resolution_strategy: Strategy used for resolution
            resolution_data: Additional resolution data

        Returns:
            True if successfully updated, False otherwise

        Example:
            success = await manager.update_conflict_status(
                "conflict_12345",
                "resolved",
                resolution_strategy="consensus_voting",
                resolution_data={"winner": "ethics_agent"}
            )
        """
        conflict = await self.get_conflict(conflict_id)
        if not conflict:
            return False

        old_status = conflict.status
        conflict.status = status

        if resolution_strategy:
            conflict.resolution_strategy = resolution_strategy
        if resolution_data:
            conflict.resolution_data = resolution_data

        if status == "resolved":
            conflict.resolved_at = datetime.now(timezone.utc)

        # Save updated conflict
        await self._update_conflict(conflict)

        # Update status indices
        await self.redis_client.srem(
            f"{self.spaces['conflicts']}:status:{old_status}", conflict_id
        )
        await self.redis_client.sadd(
            f"{self.spaces['conflicts']}:status:{status}", conflict_id
        )

        self.logger.info(f"Conflict {conflict_id} status updated to {status}")
        return True

    async def get_open_conflicts(
        self, severity: str | None = None, agent_id: str | None = None
    ) -> list[ConflictItem]:
        """
        Get open conflicts, optionally filtered by severity or agent.

        Args:
            severity: Filter by severity level
            agent_id: Filter by involved agent

        Returns:
            List of open conflicts

        Example:
            conflicts = await manager.get_open_conflicts(severity="high")
        """
        if severity:
            # Get conflicts by severity and status
            conflict_ids = await self.redis_client.sinter(
                f"{self.spaces['conflicts']}:severity:{severity}",
                f"{self.spaces['conflicts']}:status:open",
            )
        elif agent_id:
            # Get conflicts by agent and status
            conflict_ids = await self.redis_client.sinter(
                f"{self.spaces['agents']}:{agent_id}:conflicts",
                f"{self.spaces['conflicts']}:status:open",
            )
        else:
            # Get all open conflicts
            conflict_ids = await self.redis_client.smembers(
                f"{self.spaces['conflicts']}:status:open"
            )

        conflicts = []
        for conflict_id in conflict_ids:
            conflict = await self.get_conflict(conflict_id)
            if conflict:
                conflicts.append(conflict)

        # Sort by severity (critical > high > medium > low)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        conflicts.sort(key=lambda c: severity_order.get(c.severity, 4))

        return conflicts

    async def detect_decision_conflict(
        self, task_id: str, agent_decisions: dict[str, Any]
    ) -> str | None:
        """
        Detect if agent decisions conflict on a task.

        Args:
            task_id: The task ID where conflict occurred
            agent_decisions: Dictionary of agent_id -> decision

        Returns:
            Conflict ID if conflict detected, None otherwise

        Example:
            conflict_id = await manager.detect_decision_conflict(
                "task_12345",
                {
                    "ethics_agent": {"approve": False},
                    "legal_agent": {"approve": True}
                }
            )
        """
        if len(agent_decisions) < 2:
            return None

        # Simple conflict detection: check if decisions differ
        decisions = list(agent_decisions.values())
        first_decision = decisions[0]

        # Check if all decisions are the same
        if all(d == first_decision for d in decisions):
            return None

        # Create conflict
        conflict = ConflictItem(
            conflict_type="decision_conflict",
            involved_agents=list(agent_decisions.keys()),
            involved_tasks=[task_id],
            description=f"Conflicting decisions on task {task_id}",
            severity="medium",
        )

        return await self.create_conflict(conflict)

    async def _update_conflict(self, conflict: ConflictItem) -> None:
        """Update conflict data in Redis."""
        key = f"{self.spaces['conflicts']}:{conflict.id}"

        # Convert to dict and handle datetime serialization
        data = conflict.model_dump()
        data["created_at"] = data["created_at"].isoformat()
        if data.get("resolved_at"):
            data["resolved_at"] = data["resolved_at"].isoformat()

        await self.redis_client.hset(key, mapping={"data": json.dumps(data)})
