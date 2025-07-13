"""
APGF Event Publisher

Integrates APGF workflows with the ACGS event streaming system for
real-time notifications, monitoring, and cross-service communication.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from services.shared.streaming.event_streaming_manager import (
    EventPriority,
    EventRoutingStrategy,
    EventStreamingManager,
    EventType,
    StreamingEvent,
)

logger = logging.getLogger(__name__)


class APGFEventPublisher:
    """
    Event publisher for APGF system events.

    Publishes workflow state changes, agent lifecycle events, policy generation
    events, and tool execution events to the ACGS event streaming infrastructure.
    """

    def __init__(self, event_streaming_manager: EventStreamingManager | None = None):
        self.event_streaming_manager = event_streaming_manager
        self.source_service = "apgf_service"

        # Initialize streaming manager if not provided
        if not self.event_streaming_manager:
            try:
                self.event_streaming_manager = EventStreamingManager()
                logger.info("Event streaming manager initialized for APGF")
            except Exception as e:
                logger.warning(f"Failed to initialize event streaming manager: {e!s}")
                self.event_streaming_manager = None

    async def initialize(self) -> None:
        """Initialize the event publisher"""
        if self.event_streaming_manager:
            try:
                await self.event_streaming_manager.initialize()
                logger.info("APGF event publisher initialized successfully")
            except Exception as e:
                logger.exception(f"Failed to initialize APGF event publisher: {e!s}")

    async def publish_workflow_initiated(
        self, workflow_id: str, workflow_data: dict[str, Any]
    ) -> None:
        """Publish workflow initiation event"""
        await self._publish_event(
            event_type=EventType.APGF_WORKFLOW_INITIATED,
            priority=EventPriority.MEDIUM,
            payload={
                "workflow_id": workflow_id,
                "workflow_name": workflow_data.get("name"),
                "coordination_strategy": workflow_data.get("coordination_strategy"),
                "requirements": workflow_data.get("requirements", {}),
                "estimated_duration_minutes": workflow_data.get(
                    "estimated_duration_minutes"
                ),
            },
            correlation_id=workflow_id,
        )

    async def publish_workflow_completed(
        self, workflow_id: str, workflow_data: dict[str, Any]
    ) -> None:
        """Publish workflow completion event"""
        await self._publish_event(
            event_type=EventType.APGF_WORKFLOW_COMPLETED,
            priority=EventPriority.MEDIUM,
            payload={
                "workflow_id": workflow_id,
                "workflow_name": workflow_data.get("name"),
                "execution_time_minutes": workflow_data.get("execution_time_minutes"),
                "policies_generated": workflow_data.get("policies_generated", 0),
                "agents_used": workflow_data.get("agents_used", 0),
                "success_metrics": workflow_data.get("success_metrics", {}),
            },
            correlation_id=workflow_id,
        )

    async def publish_workflow_failed(
        self, workflow_id: str, error_info: dict[str, Any]
    ) -> None:
        """Publish workflow failure event"""
        await self._publish_event(
            event_type=EventType.APGF_WORKFLOW_FAILED,
            priority=EventPriority.HIGH,
            payload={
                "workflow_id": workflow_id,
                "error_message": error_info.get("error_message"),
                "error_type": error_info.get("error_type"),
                "step_failed": error_info.get("step_failed"),
                "agents_affected": error_info.get("agents_affected", []),
            },
            correlation_id=workflow_id,
        )

    async def publish_workflow_cancelled(
        self, workflow_id: str, cancellation_reason: str
    ) -> None:
        """Publish workflow cancellation event"""
        await self._publish_event(
            event_type=EventType.APGF_WORKFLOW_CANCELLED,
            priority=EventPriority.MEDIUM,
            payload={
                "workflow_id": workflow_id,
                "cancellation_reason": cancellation_reason,
                "cancelled_by": "system",  # Could be enhanced to track user
            },
            correlation_id=workflow_id,
        )

    async def publish_agent_created(
        self, agent_id: str, agent_data: dict[str, Any]
    ) -> None:
        """Publish agent creation event"""
        await self._publish_event(
            event_type=EventType.APGF_AGENT_CREATED,
            priority=EventPriority.LOW,
            payload={
                "agent_id": agent_id,
                "agent_name": agent_data.get("name"),
                "role": agent_data.get("role"),
                "capabilities": agent_data.get("capabilities", []),
                "workflow_id": agent_data.get("workflow_id"),
                "resource_limits": agent_data.get("resource_limits", {}),
            },
            correlation_id=agent_data.get("workflow_id", agent_id),
        )

    async def publish_agent_terminated(
        self, agent_id: str, termination_data: dict[str, Any]
    ) -> None:
        """Publish agent termination event"""
        await self._publish_event(
            event_type=EventType.APGF_AGENT_TERMINATED,
            priority=EventPriority.LOW,
            payload={
                "agent_id": agent_id,
                "termination_reason": termination_data.get("reason", "normal_shutdown"),
                "uptime_seconds": termination_data.get("uptime_seconds"),
                "tasks_completed": termination_data.get("tasks_completed", 0),
                "tasks_failed": termination_data.get("tasks_failed", 0),
                "workflow_id": termination_data.get("workflow_id"),
            },
            correlation_id=termination_data.get("workflow_id", agent_id),
        )

    async def publish_policy_generated(
        self, policy_id: str, policy_data: dict[str, Any]
    ) -> None:
        """Publish policy generation event"""
        await self._publish_event(
            event_type=EventType.APGF_POLICY_GENERATED,
            priority=EventPriority.MEDIUM,
            payload={
                "policy_id": policy_id,
                "policy_type": policy_data.get("policy_type"),
                "scope": policy_data.get("scope"),
                "priority": policy_data.get("priority"),
                "constitutional_compliance_score": policy_data.get(
                    "constitutional_compliance_score"
                ),
                "generated_by": policy_data.get("generated_by"),
                "workflow_id": policy_data.get("workflow_id"),
                "llm_generated": policy_data.get("llm_generated", False),
            },
            correlation_id=policy_data.get("workflow_id", policy_id),
        )

    async def publish_policy_validated(
        self, policy_id: str, validation_data: dict[str, Any]
    ) -> None:
        """Publish policy validation event"""
        await self._publish_event(
            event_type=EventType.APGF_POLICY_VALIDATED,
            priority=EventPriority.MEDIUM,
            payload={
                "policy_id": policy_id,
                "validation_status": validation_data.get("status"),
                "constitutional_compliance": validation_data.get(
                    "constitutional_compliance"
                ),
                "safety_score": validation_data.get("safety_score"),
                "conflicts_detected": validation_data.get("conflicts_detected", 0),
                "approval_required": validation_data.get("approval_required", False),
                "workflow_id": validation_data.get("workflow_id"),
            },
            correlation_id=validation_data.get("workflow_id", policy_id),
        )

    async def publish_tool_executed(self, execution_data: dict[str, Any]) -> None:
        """Publish tool execution event"""
        priority = (
            EventPriority.HIGH
            if execution_data.get("status") == "failed"
            else EventPriority.LOW
        )

        await self._publish_event(
            event_type=EventType.APGF_TOOL_EXECUTED,
            priority=priority,
            payload={
                "request_id": execution_data.get("request_id"),
                "agent_id": execution_data.get("agent_id"),
                "tool_id": execution_data.get("tool_id"),
                "status": execution_data.get("status"),
                "execution_time_seconds": execution_data.get("execution_time_seconds"),
                "safety_level": execution_data.get("safety_level"),
                "resource_usage": execution_data.get("resource_usage", {}),
                "error_message": execution_data.get("error_message"),
            },
            correlation_id=execution_data.get(
                "workflow_id", execution_data.get("request_id")
            ),
        )

    async def publish_task_assigned(self, task_data: dict[str, Any]) -> None:
        """Publish task assignment event"""
        await self._publish_event(
            event_type=EventType.APGF_TASK_ASSIGNED,
            priority=EventPriority.LOW,
            payload={
                "task_id": task_data.get("task_id"),
                "agent_id": task_data.get("agent_id"),
                "task_type": task_data.get("task_type"),
                "priority": task_data.get("priority"),
                "required_tools": task_data.get("required_tools", []),
                "workflow_id": task_data.get("workflow_id"),
            },
            correlation_id=task_data.get("workflow_id", task_data.get("task_id")),
        )

    async def publish_task_completed(self, task_data: dict[str, Any]) -> None:
        """Publish task completion event"""
        priority = (
            EventPriority.MEDIUM
            if task_data.get("status") == "failed"
            else EventPriority.LOW
        )

        await self._publish_event(
            event_type=EventType.APGF_TASK_COMPLETED,
            priority=priority,
            payload={
                "task_id": task_data.get("task_id"),
                "agent_id": task_data.get("agent_id"),
                "status": task_data.get("status"),
                "execution_time_seconds": task_data.get("execution_time_seconds"),
                "tools_used": task_data.get("tools_used", []),
                "error_message": task_data.get("error_message"),
                "workflow_id": task_data.get("workflow_id"),
            },
            correlation_id=task_data.get("workflow_id", task_data.get("task_id")),
        )

    async def _publish_event(
        self,
        event_type: EventType,
        priority: EventPriority,
        payload: dict[str, Any],
        target_service: str | None = None,
        correlation_id: str | None = None,
    ) -> None:
        """Internal method to publish events"""
        if not self.event_streaming_manager:
            logger.warning(
                f"Event streaming not available, skipping {event_type.value} event"
            )
            return

        try:
            # Create streaming event
            event = StreamingEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                priority=priority,
                source_service=self.source_service,
                target_service=target_service,
                payload=payload,
                metadata={
                    "constitutional_hash": "cdd01ef066bc6cf2",
                    "apgf_version": "1.0.0",
                    "service": self.source_service,
                },
                routing_strategy=EventRoutingStrategy.HYBRID,
                constitutional_compliant=True,
                correlation_id=correlation_id,
                timestamp=datetime.utcnow(),
                ttl_seconds=3600,  # Events expire after 1 hour
            )

            # Publish event
            await self.event_streaming_manager.publish_event(event)

            logger.debug(f"Published {event_type.value} event: {event.event_id}")

        except Exception as e:
            logger.exception(f"Failed to publish {event_type.value} event: {e!s}")
            # Don't raise exception to avoid breaking workflow on event failure

    async def shutdown(self) -> None:
        """Shutdown the event publisher"""
        if self.event_streaming_manager:
            try:
                await self.event_streaming_manager.shutdown()
                logger.info("APGF event publisher shutdown successfully")
            except Exception as e:
                logger.exception(f"Error during APGF event publisher shutdown: {e!s}")
