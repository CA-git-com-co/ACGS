"""
Knowledge management functionality for the Blackboard service.

This module handles storing, retrieving, and querying knowledge items
on the blackboard system.
"""

import json
import logging
from datetime import datetime, timezone

import redis.asyncio as redis

from .models import KnowledgeItem

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



class KnowledgeManager:
    """
    Manages knowledge items on the blackboard.

    Handles storage, retrieval, and querying of knowledge items
    with proper serialization and Redis operations.
    """

    def __init__(self, redis_client: redis.Redis, spaces: dict[str, str]):
        self.redis_client = redis_client
        self.spaces = spaces
        self.logger = logging.getLogger(__name__)

    async def add_knowledge(self, knowledge: KnowledgeItem) -> str:
        """
        Add a knowledge item to the blackboard.

        Args:
            knowledge: The knowledge item to add

        Returns:
            The ID of the added knowledge item

        Example:
            knowledge_id = await manager.add_knowledge(
                KnowledgeItem(
                    space="governance",
                    agent_id="ethics_agent",
                    knowledge_type="policy",
                    content={"rule": "transparency"}
                )
            )
        """
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
            expire_seconds = int(
                (knowledge.expires_at - datetime.now(timezone.utc)).total_seconds()
            )
            if expire_seconds > 0:
                await self.redis_client.expire(key, expire_seconds)

        # Add to priority queue for the space
        priority_key = f"{self.spaces[knowledge.space]}:priority"
        await self.redis_client.zadd(priority_key, {knowledge.id: knowledge.priority})

        # Add to agent's knowledge index
        agent_key = f"{self.spaces['agents']}:{knowledge.agent_id}:knowledge"
        await self.redis_client.sadd(agent_key, knowledge.id)

        self.logger.debug(
            f"Added knowledge item {knowledge.id} to space {knowledge.space}"
        )
        return knowledge.id

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

        Example:
            knowledge = await manager.get_knowledge("12345", "governance")
        """
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
        """
        Query knowledge items with filters.

        Args:
            space: The knowledge space to search
            knowledge_type: Filter by knowledge type
            agent_id: Filter by agent ID
            tags: Filter by tags (must have all specified tags)
            limit: Maximum number of results

        Returns:
            List of matching knowledge items

        Example:
            results = await manager.query_knowledge(
                space="governance",
                knowledge_type="policy",
                tags={"ethics", "transparency"}
            )
        """
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
            if tags and not tags.issubset(knowledge.tags):
                continue

            results.append(knowledge)

        return results

    async def remove_knowledge(self, knowledge_id: str, space: str) -> bool:
        """
        Remove a knowledge item from the blackboard.

        Args:
            knowledge_id: The ID of the knowledge to remove
            space: The knowledge space

        Returns:
            True if removed, False if not found

        Example:
            success = await manager.remove_knowledge("12345", "governance")
        """
        key = f"{self.spaces[space]}:knowledge:{knowledge_id}"

        # Get the knowledge first to find the agent
        knowledge = await self.get_knowledge(knowledge_id, space)
        if not knowledge:
            return False

        # Remove from Redis
        await self.redis_client.delete(key)

        # Remove from priority queue
        priority_key = f"{self.spaces[space]}:priority"
        await self.redis_client.zrem(priority_key, knowledge_id)

        # Remove from agent's knowledge index
        agent_key = f"{self.spaces['agents']}:{knowledge.agent_id}:knowledge"
        await self.redis_client.srem(agent_key, knowledge_id)

        self.logger.debug(f"Removed knowledge item {knowledge_id} from space {space}")
        return True
