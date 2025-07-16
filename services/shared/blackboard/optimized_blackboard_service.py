"""
Optimized Redis-based Blackboard Service for Multi-Agent Coordination
Constitutional Hash: cdd01ef066bc6cf2

High-performance implementation with connection pooling, batch operations,
and atomic Redis operations for <5ms P99 latency targets.
"""

import asyncio
import json
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

import redis.asyncio as redis
from pydantic import BaseModel, Field

# Import original models
from .blackboard_service import KnowledgeItem, TaskDefinition, ConflictItem

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Lua scripts for atomic operations
CLAIM_TASK_SCRIPT = """
local task_key = KEYS[1]
local agent_id = ARGV[1]
local claim_time = ARGV[2]

local task_data = redis.call('HGET', task_key, 'data')
if not task_data then
    return nil
end

local task = cjson.decode(task_data)
if task.status ~= 'pending' then
    return nil
end

task.status = 'claimed'
task.agent_id = agent_id
task.claimed_at = claim_time

redis.call('HSET', task_key, 'data', cjson.encode(task))
return task_data
"""

BATCH_ADD_KNOWLEDGE_SCRIPT = """
local space_prefix = ARGV[1]
local agent_prefix = ARGV[2]

for i = 2, #KEYS do
    local knowledge_data = ARGV[i]
    local knowledge = cjson.decode(knowledge_data)
    
    -- Set main knowledge data
    local key = space_prefix .. ':knowledge:' .. knowledge.id
    redis.call('HSET', key, 'data', knowledge_data)
    
    -- Add to priority queue
    local priority_key = space_prefix .. ':priority'
    redis.call('ZADD', priority_key, knowledge.priority, knowledge.id)
    
    -- Add to agent index
    local agent_key = agent_prefix .. ':' .. knowledge.agent_id .. ':knowledge'
    redis.call('SADD', agent_key, knowledge.id)
    
    -- Set expiration if specified
    if knowledge.expires_at then
        local expire_seconds = tonumber(ARGV[#ARGV])
        if expire_seconds > 0 then
            redis.call('EXPIRE', key, expire_seconds)
        end
    end
end

return #KEYS - 1
"""


class LRUCache:
    """Simple LRU cache implementation for agent capabilities."""
    
    def __init__(self, maxsize: int = 1000):
        self.maxsize = maxsize
        self.cache: Dict[str, Any] = {}
        self.access_order: List[str] = []
    
    def get(self, key: str) -> Any:
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value: Any) -> None:
        if key in self.cache:
            # Update existing
            self.access_order.remove(key)
        elif len(self.cache) >= self.maxsize:
            # Remove least recently used
            lru_key = self.access_order.pop(0)
            del self.cache[lru_key]
        
        self.cache[key] = value
        self.access_order.append(key)


class PerformanceMonitor:
    """Lightweight performance monitoring for blackboard operations."""
    
    def __init__(self):
        self.operation_count = 0
        self.total_latency = 0.0
        self.error_count = 0
        self.last_reset = time.time()
        self.p99_latency = 0.0
        self.latency_samples = []
        self.max_samples = 1000
    
    def record_operation(self, latency: float, success: bool = True) -> None:
        """Record operation with minimal overhead."""
        self.operation_count += 1
        self.total_latency += latency
        
        if not success:
            self.error_count += 1
        
        # Track P99 latency efficiently
        self.latency_samples.append(latency)
        if len(self.latency_samples) > self.max_samples:
            self.latency_samples.pop(0)
            
        # Update P99 every 100 operations
        if self.operation_count % 100 == 0:
            self._update_p99()
    
    def _update_p99(self) -> None:
        """Update P99 latency calculation."""
        if self.latency_samples:
            sorted_samples = sorted(self.latency_samples)
            idx = int(0.99 * len(sorted_samples))
            self.p99_latency = sorted_samples[min(idx, len(sorted_samples) - 1)]
    
    def get_metrics(self) -> Dict[str, float]:
        """Get current performance metrics."""
        elapsed = time.time() - self.last_reset
        if elapsed == 0 or self.operation_count == 0:
            return {"rps": 0.0, "avg_latency": 0.0, "p99_latency": 0.0, "error_rate": 0.0}
        
        return {
            "rps": self.operation_count / elapsed,
            "avg_latency": self.total_latency / self.operation_count,
            "p99_latency": self.p99_latency,
            "error_rate": self.error_count / self.operation_count
        }


class OptimizedBlackboardService:
    """
    High-performance Redis-based blackboard service for multi-agent coordination.
    
    Optimizations:
    - Connection pooling for reduced latency
    - Batch operations to minimize Redis round-trips
    - Lua scripts for atomic operations
    - Local caching for frequent lookups
    - Lightweight performance monitoring
    """
    
    def __init__(self, 
                 redis_url: str = "redis://localhost:6379",
                 db: int = 0,
                 pool_size: int = 20,
                 cache_size: int = 1000):
        self.redis_url = redis_url
        self.db = db
        self.pool_size = pool_size
        
        # Connection pool for better performance
        self.connection_pool: Optional[redis.ConnectionPool] = None
        self.redis_client: Optional[redis.Redis] = None
        self.logger = logging.getLogger(__name__)
        
        # Local caches for performance
        self.agent_capabilities_cache = LRUCache(cache_size)
        self.task_assignment_cache = LRUCache(cache_size)
        
        # Performance monitoring
        self.perf_monitor = PerformanceMonitor()
        
        # Precompiled Lua scripts
        self.claim_task_script = None
        self.batch_add_knowledge_script = None
        
        # Knowledge spaces
        self.spaces = {
            "governance": "bb:governance",
            "compliance": "bb:compliance", 
            "performance": "bb:performance",
            "coordination": "bb:coordination",
            "tasks": "bb:tasks",
            "conflicts": "bb:conflicts",
            "agents": "bb:agents",
        }
        
        # Event channels
        self.channels = {
            "task_created": "events:task_created",
            "task_claimed": "events:task_claimed", 
            "task_completed": "events:task_completed",
            "conflict_detected": "events:conflict_detected",
            "knowledge_added": "events:knowledge_added",
            "agent_status": "events:agent_status",
        }
    
    async def initialize(self) -> None:
        """Initialize optimized Redis connection with pooling."""
        start_time = time.time()
        
        try:
            # Create connection pool
            self.connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                db=self.db,
                max_connections=self.pool_size,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                decode_responses=True
            )
            
            # Create Redis client with pool
            self.redis_client = redis.Redis(
                connection_pool=self.connection_pool,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self.redis_client.ping()
            
            # Load Lua scripts
            await self._load_lua_scripts()
            
            latency = (time.time() - start_time) * 1000
            self.perf_monitor.record_operation(latency)
            
            self.logger.info(
                f"Optimized blackboard service initialized in {latency:.2f}ms "
                f"with pool size {self.pool_size}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize blackboard service: {e}")
            raise
    
    async def _load_lua_scripts(self) -> None:
        """Load and register Lua scripts for atomic operations."""
        self.claim_task_script = self.redis_client.register_script(CLAIM_TASK_SCRIPT)
        self.batch_add_knowledge_script = self.redis_client.register_script(BATCH_ADD_KNOWLEDGE_SCRIPT)
    
    async def shutdown(self) -> None:
        """Cleanup and close Redis connections."""
        if self.redis_client:
            await self.redis_client.close()
        if self.connection_pool:
            await self.connection_pool.disconnect()
        
        self.logger.info("Optimized blackboard service shut down")
    
    # High-Performance Knowledge Management
    
    async def batch_add_knowledge(self, knowledge_items: List[KnowledgeItem]) -> List[str]:
        """Add multiple knowledge items in a single optimized operation."""
        start_time = time.time()
        
        try:
            if not knowledge_items:
                return []
            
            # Group by space for efficient processing
            space_groups = defaultdict(list)
            for item in knowledge_items:
                space_groups[item.space].append(item)
            
            all_knowledge_ids = []
            
            # Process each space group
            for space, items in space_groups.items():
                knowledge_ids = await self._batch_add_knowledge_to_space(space, items)
                all_knowledge_ids.extend(knowledge_ids)
            
            # Batch publish notifications
            await self._batch_publish_knowledge_events(knowledge_items)
            
            latency = (time.time() - start_time) * 1000
            self.perf_monitor.record_operation(latency)
            
            self.logger.debug(f"Batch added {len(knowledge_items)} knowledge items in {latency:.2f}ms")
            return all_knowledge_ids
            
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.perf_monitor.record_operation(latency, success=False)
            self.logger.error(f"Batch add knowledge failed: {e}")
            raise
    
    async def _batch_add_knowledge_to_space(self, space: str, items: List[KnowledgeItem]) -> List[str]:
        """Add knowledge items to specific space using pipeline."""
        pipe = self.redis_client.pipeline()
        knowledge_ids = []
        
        for knowledge in items:
            # Prepare data
            data = knowledge.model_dump()
            data["timestamp"] = data["timestamp"].isoformat()
            if data.get("expires_at"):
                data["expires_at"] = data["expires_at"].isoformat()
            data["tags"] = list(data["tags"])
            
            # Use pipeline for batch operations
            key = f"{self.spaces[space]}:knowledge:{knowledge.id}"
            pipe.hset(key, mapping={"data": json.dumps(data)})
            
            # Add to priority queue
            priority_key = f"{self.spaces[space]}:priority"
            pipe.zadd(priority_key, {knowledge.id: knowledge.priority})
            
            # Add to agent index
            agent_key = f"{self.spaces['agents']}:{knowledge.agent_id}:knowledge"
            pipe.sadd(agent_key, knowledge.id)
            
            # Set expiration if needed
            if knowledge.expires_at:
                current_time = datetime.now(timezone.utc)
                expires_at = knowledge.expires_at
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                
                expire_seconds = int((expires_at - current_time).total_seconds())
                if expire_seconds > 0:
                    pipe.expire(key, expire_seconds)
            
            knowledge_ids.append(knowledge.id)
        
        # Execute all operations in pipeline
        await pipe.execute()
        return knowledge_ids
    
    async def _batch_publish_knowledge_events(self, knowledge_items: List[KnowledgeItem]) -> None:
        """Batch publish knowledge events for better performance."""
        if not knowledge_items:
            return
        
        # Group events and publish in batch
        events = []
        for knowledge in knowledge_items:
            event_data = {
                "knowledge_id": knowledge.id,
                "space": knowledge.space,
                "agent_id": knowledge.agent_id,
                "knowledge_type": knowledge.knowledge_type,
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
            events.append(json.dumps(event_data))
        
        # Publish all events in pipeline
        pipe = self.redis_client.pipeline()
        for event in events:
            pipe.publish(self.channels["knowledge_added"], event)
        
        await pipe.execute()
    
    # Optimized Task Management
    
    async def claim_task_atomic(self, task_id: str, agent_id: str) -> Optional[TaskDefinition]:
        """Atomically claim a task using Lua script for consistency."""
        start_time = time.time()
        
        try:
            task_key = f"{self.spaces['tasks']}:{task_id}"
            claim_time = datetime.now(timezone.utc).isoformat()
            
            # Use Lua script for atomic claim operation
            result = await self.claim_task_script(
                keys=[task_key],
                args=[agent_id, claim_time]
            )
            
            latency = (time.time() - start_time) * 1000
            self.perf_monitor.record_operation(latency)
            
            if result:
                # Parse and return claimed task
                task_data = json.loads(result)
                task_data["created_at"] = datetime.fromisoformat(task_data["created_at"])
                if task_data.get("deadline"):
                    task_data["deadline"] = datetime.fromisoformat(task_data["deadline"])
                if task_data.get("claimed_at"):
                    task_data["claimed_at"] = datetime.fromisoformat(task_data["claimed_at"])
                
                task = TaskDefinition(**task_data)
                
                # Cache successful assignment
                self.task_assignment_cache.put(f"{agent_id}:{task_id}", task)
                
                # Publish event
                await self._publish_event("task_claimed", {
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "constitutional_hash": CONSTITUTIONAL_HASH
                })
                
                self.logger.debug(f"Agent {agent_id} claimed task {task_id} in {latency:.2f}ms")
                return task
            
            return None
            
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.perf_monitor.record_operation(latency, success=False)
            self.logger.error(f"Atomic task claim failed: {e}")
            raise
    
    # Agent Capability Management
    
    async def register_agent_capabilities(self, agent_id: str, capabilities: List[str]) -> None:
        """Register agent capabilities for efficient task routing."""
        start_time = time.time()
        
        try:
            pipe = self.redis_client.pipeline()
            
            # Index agent by each capability
            for capability in capabilities:
                capability_key = f"capabilities:{capability}"
                pipe.sadd(capability_key, agent_id)
            
            # Store agent capabilities list
            agent_cap_key = f"{self.spaces['agents']}:{agent_id}:capabilities"
            pipe.delete(agent_cap_key)  # Clear existing
            pipe.sadd(agent_cap_key, *capabilities)
            
            await pipe.execute()
            
            # Cache capabilities
            self.agent_capabilities_cache.put(agent_id, set(capabilities))
            
            latency = (time.time() - start_time) * 1000
            self.perf_monitor.record_operation(latency)
            
            self.logger.debug(f"Registered {len(capabilities)} capabilities for agent {agent_id}")
            
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.perf_monitor.record_operation(latency, success=False)
            self.logger.error(f"Failed to register agent capabilities: {e}")
            raise
    
    async def get_capable_agents(self, task_type: str) -> List[str]:
        """Get agents capable of handling specific task type."""
        start_time = time.time()
        
        try:
            capability_key = f"capabilities:{task_type}"
            agents = await self.redis_client.smembers(capability_key)
            
            latency = (time.time() - start_time) * 1000
            self.perf_monitor.record_operation(latency)
            
            return list(agents) if agents else []
            
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.perf_monitor.record_operation(latency, success=False)
            self.logger.error(f"Failed to get capable agents: {e}")
            return []
    
    # Performance Monitoring
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        metrics = self.perf_monitor.get_metrics()
        
        # Add Redis connection pool stats
        if self.connection_pool:
            metrics["pool_created_connections"] = self.connection_pool.created_connections
            metrics["pool_available_connections"] = len(self.connection_pool._available_connections)
            metrics["pool_in_use_connections"] = len(self.connection_pool._in_use_connections)
        
        # Add cache stats
        metrics["capability_cache_size"] = len(self.agent_capabilities_cache.cache)
        metrics["assignment_cache_size"] = len(self.task_assignment_cache.cache)
        
        metrics["constitutional_hash"] = CONSTITUTIONAL_HASH
        return metrics
    
    async def _publish_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish event notification."""
        try:
            channel = self.channels.get(event_type)
            if channel:
                await self.redis_client.publish(channel, json.dumps(data))
        except Exception as e:
            self.logger.warning(f"Failed to publish event {event_type}: {e}")


# Factory function for easy integration
async def create_optimized_blackboard_service(
    redis_url: str = "redis://localhost:6379",
    db: int = 0,
    pool_size: int = 20
) -> OptimizedBlackboardService:
    """Create and initialize optimized blackboard service."""
    service = OptimizedBlackboardService(redis_url, db, pool_size)
    await service.initialize()
    return service