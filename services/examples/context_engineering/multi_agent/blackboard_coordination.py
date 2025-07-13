#!/usr/bin/env python3
"""
ACGS Blackboard Coordination Example

This example demonstrates how to integrate with the ACGS blackboard service
for multi-agent coordination using Context Engineering principles.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

import redis.asyncio as redis
from pydantic import BaseModel, Field

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
BLACKBOARD_SERVICE_URL = "http://localhost:8010"
REDIS_URL = "redis://localhost:6389/1"  # Blackboard Redis instance


# Agent types for coordination
class AgentType(str, Enum):
    ORCHESTRATOR = "orchestrator"
    DOMAIN_SPECIALIST = "domain_specialist"
    WORKER = "worker"
    ETHICS = "ethics"
    LEGAL = "legal"
    OPERATIONAL = "operational"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CoordinationMessage(BaseModel):
    """Message for blackboard-based agent coordination."""

    message_id: UUID = Field(default_factory=uuid4)
    from_agent: str = Field(..., description="Source agent identifier")
    to_agent: str | None = Field(
        default=None, description="Target agent (None for broadcast)"
    )
    message_type: str = Field(..., description="Type of coordination message")
    content: dict[str, Any] = Field(..., description="Message content")
    priority: int = Field(default=1, description="Message priority (1=low, 5=critical)")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = Field(default=None, description="Message expiration")


class CoordinationTask(BaseModel):
    """Task for multi-agent coordination."""

    task_id: UUID = Field(default_factory=uuid4)
    task_type: str = Field(..., description="Type of task")
    description: str = Field(..., description="Task description")
    assigned_agent: str | None = Field(default=None, description="Assigned agent")
    required_agents: list[AgentType] = Field(
        default_factory=list, description="Required agent types"
    )
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    progress: float = Field(default=0.0, description="Task progress (0.0-1.0)")
    result: dict[str, Any] | None = Field(default=None, description="Task result")
    constitutional_compliance: bool = Field(default=True)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deadline: datetime | None = Field(default=None, description="Task deadline")


class BlackboardCoordinator:
    """
    ACGS Blackboard Coordinator for multi-agent coordination.

    This class demonstrates Context Engineering patterns for:
    - Constitutional compliance in multi-agent systems
    - Performance-optimized coordination (sub-5ms targets)
    - Comprehensive audit logging
    - Error handling and recovery
    """

    def __init__(self, agent_id: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.redis_client: redis.Redis | None = None
        self.is_active = False
        self.subscribed_channels: list[str] = []

        # Performance tracking
        self.coordination_metrics = {
            "messages_sent": 0,
            "messages_received": 0,
            "tasks_assigned": 0,
            "tasks_completed": 0,
            "avg_coordination_latency_ms": 0.0,
        }

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"acgs.blackboard.{agent_id}")

    async def initialize(self) -> bool:
        """Initialize blackboard coordination with constitutional validation."""
        try:
            # Connect to Redis blackboard
            self.redis_client = redis.from_url(REDIS_URL)
            await self.redis_client.ping()

            # Register agent with constitutional compliance
            await self._register_agent()

            # Subscribe to coordination channels
            await self._setup_subscriptions()

            self.is_active = True
            self.logger.info(
                f"Agent {self.agent_id} initialized with blackboard coordination"
            )

            return True

        except Exception as e:
            self.logger.exception(f"Blackboard initialization failed: {e}")
            return False

    async def _register_agent(self):
        """Register agent in the blackboard with constitutional compliance."""
        agent_info = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "constitutional_hash": self.constitutional_hash,
            "capabilities": self._get_agent_capabilities(),
            "status": "active",
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "performance_metrics": self.coordination_metrics,
        }

        # Store agent registration
        await self.redis_client.hset(
            "acgs:agents:registry", self.agent_id, json.dumps(agent_info)
        )

        # Set agent status with TTL
        await self.redis_client.setex(
            f"acgs:agents:status:{self.agent_id}", 30, "active"  # 30 second heartbeat
        )

        self.logger.info(f"Agent {self.agent_id} registered in blackboard")

    async def _setup_subscriptions(self):
        """Setup Redis subscriptions for coordination channels."""
        # Subscribe to agent-specific channel
        agent_channel = f"acgs:coordination:agent:{self.agent_id}"

        # Subscribe to agent type channel
        type_channel = f"acgs:coordination:type:{self.agent_type.value}"

        # Subscribe to broadcast channel
        broadcast_channel = "acgs:coordination:broadcast"

        self.subscribed_channels = [agent_channel, type_channel, broadcast_channel]

        # Start background subscription handler
        asyncio.create_task(self._handle_subscriptions())

    async def _handle_subscriptions(self):
        """Handle incoming coordination messages from subscribed channels."""
        pubsub = self.redis_client.pubsub()

        try:
            # Subscribe to all channels
            for channel in self.subscribed_channels:
                await pubsub.subscribe(channel)

            self.logger.info(f"Subscribed to channels: {self.subscribed_channels}")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    await self._process_coordination_message(message)

        except Exception as e:
            self.logger.exception(f"Subscription handling failed: {e}")
        finally:
            await pubsub.close()

    async def _process_coordination_message(self, message: dict[str, Any]):
        """Process incoming coordination message with constitutional validation."""
        try:
            # Parse message
            message_data = json.loads(message["data"])
            coord_message = CoordinationMessage(**message_data)

            # Validate constitutional compliance
            if coord_message.constitutional_hash != CONSTITUTIONAL_HASH:
                self.logger.warning(
                    f"Message from {coord_message.from_agent} has invalid constitutional hash"
                )
                return

            # Update metrics
            self.coordination_metrics["messages_received"] += 1

            # Route message based on type
            await self._route_coordination_message(coord_message)

            # Generate audit event
            await self._log_coordination_event(
                "message_received",
                {
                    "from_agent": coord_message.from_agent,
                    "message_type": coord_message.message_type,
                    "channel": message["channel"].decode(),
                },
            )

        except Exception as e:
            self.logger.exception(f"Message processing failed: {e}")

    async def _route_coordination_message(self, message: CoordinationMessage):
        """Route coordination message to appropriate handler."""
        handlers = {
            "task_assignment": self._handle_task_assignment,
            "task_update": self._handle_task_update,
            "coordination_request": self._handle_coordination_request,
            "consensus_vote": self._handle_consensus_vote,
            "status_update": self._handle_status_update,
            "shutdown": self._handle_shutdown,
        }

        handler = handlers.get(message.message_type)
        if handler:
            await handler(message)
        else:
            self.logger.warning(f"Unknown message type: {message.message_type}")

    async def _handle_task_assignment(self, message: CoordinationMessage):
        """Handle task assignment from coordinator."""
        try:
            task_data = message.content.get("task")
            if not task_data:
                self.logger.error("Task assignment message missing task data")
                return

            task = CoordinationTask(**task_data)

            # Validate constitutional compliance
            if not task.constitutional_compliance:
                self.logger.error(
                    f"Task {task.task_id} violates constitutional compliance"
                )
                await self._reject_task(task, "constitutional_violation")
                return

            # Check if agent can handle task
            if not await self._can_handle_task(task):
                await self._reject_task(task, "capability_mismatch")
                return

            # Accept and start task
            await self._accept_task(task)

        except Exception as e:
            self.logger.exception(f"Task assignment handling failed: {e}")

    async def _can_handle_task(self, task: CoordinationTask) -> bool:
        """Check if agent can handle the assigned task."""
        # Check if agent type is in required agents
        if self.agent_type not in task.required_agents and task.required_agents:
            return False

        # Check agent capabilities
        capabilities = self._get_agent_capabilities()
        task_requirements = task.content.get("requirements", [])

        return all(requirement in capabilities for requirement in task_requirements)

    async def _accept_task(self, task: CoordinationTask):
        """Accept and start executing a task."""
        # Update task status
        task.status = TaskStatus.IN_PROGRESS
        task.assigned_agent = self.agent_id
        task.updated_at = datetime.now(timezone.utc)

        # Store task in blackboard
        await self.redis_client.hset(
            "acgs:tasks:active", str(task.task_id), task.json()
        )

        # Notify coordinator of acceptance
        await self.send_coordination_message(
            to_agent="coordinator",
            message_type="task_accepted",
            content={
                "task_id": str(task.task_id),
                "agent_id": self.agent_id,
                "estimated_completion": 30,  # seconds
            },
        )

        # Update metrics
        self.coordination_metrics["tasks_assigned"] += 1

        # Start task execution
        asyncio.create_task(self._execute_task(task))

        self.logger.info(f"Accepted task {task.task_id}: {task.description}")

    async def _execute_task(self, task: CoordinationTask):
        """Execute assigned task with constitutional compliance monitoring."""
        try:
            start_time = asyncio.get_event_loop().time()

            # Execute task based on type
            if task.task_type == "constitutional_analysis":
                result = await self._execute_constitutional_analysis(task)
            elif task.task_type == "performance_validation":
                result = await self._execute_performance_validation(task)
            elif task.task_type == "consensus_participation":
                result = await self._execute_consensus_participation(task)
            else:
                result = await self._execute_generic_task(task)

            # Update task with result
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.progress = 1.0
            task.updated_at = datetime.now(timezone.utc)

            # Calculate execution time
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000

            # Validate performance target (sub-5ms for coordination)
            if execution_time > 5.0:
                self.logger.warning(
                    f"Task execution exceeded 5ms target: {execution_time:.2f}ms"
                )

            # Store completed task
            await self.redis_client.hset(
                "acgs:tasks:completed", str(task.task_id), task.json()
            )

            # Remove from active tasks
            await self.redis_client.hdel("acgs:tasks:active", str(task.task_id))

            # Notify coordinator of completion
            await self.send_coordination_message(
                to_agent="coordinator",
                message_type="task_completed",
                content={
                    "task_id": str(task.task_id),
                    "agent_id": self.agent_id,
                    "execution_time_ms": execution_time,
                    "result": result,
                },
            )

            # Update metrics
            self.coordination_metrics["tasks_completed"] += 1

            self.logger.info(f"Completed task {task.task_id} in {execution_time:.2f}ms")

        except Exception as e:
            # Handle task failure
            task.status = TaskStatus.FAILED
            task.result = {"error": str(e)}
            task.updated_at = datetime.now(timezone.utc)

            await self.redis_client.hset(
                "acgs:tasks:failed", str(task.task_id), task.json()
            )

            await self.send_coordination_message(
                to_agent="coordinator",
                message_type="task_failed",
                content={
                    "task_id": str(task.task_id),
                    "agent_id": self.agent_id,
                    "error": str(e),
                },
            )

            self.logger.exception(f"Task {task.task_id} failed: {e}")

    async def _execute_constitutional_analysis(
        self, task: CoordinationTask
    ) -> dict[str, Any]:
        """Execute constitutional analysis task."""
        # Simulate constitutional analysis (placeholder)
        await asyncio.sleep(0.002)  # 2ms simulation

        return {
            "analysis_type": "constitutional_compliance",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "compliance_score": 0.97,
            "violations": [],
            "recommendations": ["Maintain current compliance level"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _execute_performance_validation(
        self, task: CoordinationTask
    ) -> dict[str, Any]:
        """Execute performance validation task."""
        # Simulate performance validation
        await asyncio.sleep(0.001)  # 1ms simulation

        return {
            "validation_type": "performance_metrics",
            "p99_latency_ms": 3.2,
            "throughput_rps": 120,
            "cache_hit_rate": 0.95,
            "meets_targets": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _execute_consensus_participation(
        self, task: CoordinationTask
    ) -> dict[str, Any]:
        """Execute consensus participation task."""
        # Simulate consensus participation
        await asyncio.sleep(0.003)  # 3ms simulation

        return {
            "consensus_type": "constitutional_priority",
            "vote": "approve",
            "confidence": 0.92,
            "reasoning": "Aligns with constitutional framework",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _execute_generic_task(self, task: CoordinationTask) -> dict[str, Any]:
        """Execute generic task."""
        # Simulate generic task execution
        await asyncio.sleep(0.002)  # 2ms simulation

        return {
            "task_type": task.task_type,
            "status": "completed",
            "agent_type": self.agent_type.value,
            "constitutional_compliant": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def send_coordination_message(
        self,
        message_type: str,
        content: dict[str, Any],
        to_agent: str | None = None,
        priority: int = 1,
    ) -> bool:
        """Send coordination message via blackboard."""
        try:
            message = CoordinationMessage(
                from_agent=self.agent_id,
                to_agent=to_agent,
                message_type=message_type,
                content=content,
                priority=priority,
            )

            # Determine target channel
            if to_agent:
                channel = f"acgs:coordination:agent:{to_agent}"
            else:
                channel = "acgs:coordination:broadcast"

            # Publish message
            await self.redis_client.publish(channel, message.json())

            # Update metrics
            self.coordination_metrics["messages_sent"] += 1

            # Log coordination event
            await self._log_coordination_event(
                "message_sent",
                {
                    "to_agent": to_agent or "broadcast",
                    "message_type": message_type,
                    "channel": channel,
                },
            )

            return True

        except Exception as e:
            self.logger.exception(f"Failed to send coordination message: {e}")
            return False

    async def _log_coordination_event(self, event_type: str, details: dict[str, Any]):
        """Log coordination event for audit trail."""
        event = {
            "event_type": f"blackboard_{event_type}",
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Store in audit log
        audit_key = f"audit:coordination:{datetime.now().strftime('%Y%m%d')}"
        await self.redis_client.lpush(audit_key, json.dumps(event))
        await self.redis_client.expire(audit_key, 86400 * 7)  # 7 day retention

    def _get_agent_capabilities(self) -> list[str]:
        """Get agent capabilities based on agent type."""
        capabilities_map = {
            AgentType.ORCHESTRATOR: [
                "task_coordination",
                "agent_management",
                "consensus_orchestration",
            ],
            AgentType.DOMAIN_SPECIALIST: [
                "domain_analysis",
                "specialized_validation",
                "expert_consultation",
            ],
            AgentType.WORKER: ["task_execution", "data_processing", "basic_validation"],
            AgentType.ETHICS: [
                "bias_assessment",
                "fairness_evaluation",
                "harm_assessment",
                "constitutional_analysis",
            ],
            AgentType.LEGAL: [
                "regulatory_compliance",
                "jurisdiction_analysis",
                "contractual_compliance",
                "constitutional_analysis",
            ],
            AgentType.OPERATIONAL: [
                "operational_validation",
                "performance_analysis",
                "implementation_planning",
                "constitutional_analysis",
            ],
        }

        return capabilities_map.get(self.agent_type, ["basic_coordination"])

    async def get_coordination_status(self) -> dict[str, Any]:
        """Get current coordination status and metrics."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "constitutional_hash": self.constitutional_hash,
            "is_active": self.is_active,
            "subscribed_channels": self.subscribed_channels,
            "metrics": self.coordination_metrics,
            "capabilities": self._get_agent_capabilities(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def shutdown(self):
        """Shutdown agent coordination gracefully."""
        try:
            # Notify other agents of shutdown
            await self.send_coordination_message(
                message_type="agent_shutdown",
                content={"agent_id": self.agent_id, "reason": "graceful_shutdown"},
            )

            # Remove from agent registry
            await self.redis_client.hdel("acgs:agents:registry", self.agent_id)
            await self.redis_client.delete(f"acgs:agents:status:{self.agent_id}")

            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()

            self.is_active = False
            self.logger.info(f"Agent {self.agent_id} shutdown completed")

        except Exception as e:
            self.logger.exception(f"Shutdown failed: {e}")


# Example usage and testing
async def main():
    """Example usage of blackboard coordination."""

    # Create ethics agent
    ethics_agent = BlackboardCoordinator("ethics-001", AgentType.ETHICS)
    await ethics_agent.initialize()

    # Create legal agent
    legal_agent = BlackboardCoordinator("legal-001", AgentType.LEGAL)
    await legal_agent.initialize()

    # Simulate coordination
    await ethics_agent.send_coordination_message(
        message_type="coordination_request",
        content={
            "request_type": "constitutional_analysis",
            "priority": "high",
            "deadline": (datetime.now(timezone.utc)).isoformat(),
        },
        to_agent="legal-001",
    )

    # Wait for coordination
    await asyncio.sleep(2)

    # Check coordination status
    await ethics_agent.get_coordination_status()
    await legal_agent.get_coordination_status()

    # Shutdown
    await ethics_agent.shutdown()
    await legal_agent.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
