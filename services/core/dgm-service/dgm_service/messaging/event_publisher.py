"""
Event Publisher for DGM Service.

Provides high-level event publishing capabilities with automatic
subject routing, message formatting, and delivery guarantees.
"""

import logging
from typing import Any

from .message_types import (
    DGMEvent,
    EventPriority,
    EventType,
    create_bandit_event,
    create_constitutional_event,
    create_improvement_event,
    create_performance_event,
    get_subject_for_event,
)
from .nats_client import NATSClient


class EventPublisher:
    """High-level event publisher for DGM service events."""

    def __init__(self, nats_client: NATSClient):
        """Initialize event publisher with NATS client."""
        self.nats_client = nats_client
        self.logger = logging.getLogger(__name__)

        # Publishing metrics
        self.metrics = {
            "events_published": 0,
            "events_failed": 0,
            "events_by_type": {},
            "events_by_priority": {},
        }

    async def publish_event(
        self, event: DGMEvent, headers: dict[str, str] | None = None
    ) -> bool:
        """Publish a DGM event to the appropriate NATS subject."""
        try:
            # Get subject for event type
            subject = get_subject_for_event(event.event_type)

            # Add standard headers
            event_headers = {
                "event-type": event.event_type.value,
                "priority": event.priority.value,
                "source": event.source_service,
                "timestamp": event.timestamp,
            }

            if event.correlation_id:
                event_headers["correlation-id"] = event.correlation_id

            if event.user_id:
                event_headers["user-id"] = event.user_id

            # Merge with custom headers
            if headers:
                event_headers.update(headers)

            # Publish to NATS
            success = await self.nats_client.publish(
                subject=subject, data=event.to_dict(), headers=event_headers
            )

            if success:
                self._update_metrics(event, success=True)
                self.logger.debug(
                    f"Published event {event.event_id}: {event.event_type.value}"
                )
            else:
                self._update_metrics(event, success=False)
                self.logger.error(f"Failed to publish event {event.event_id}")

            return success

        except Exception as e:
            self.logger.error(f"Error publishing event {event.event_id}: {e}")
            self._update_metrics(event, success=False)
            return False

    async def publish_improvement_proposed(
        self,
        improvement_id: str,
        strategy: str,
        target_services: list,
        expected_improvement: float,
        risk_level: str,
        **kwargs,
    ) -> bool:
        """Publish improvement proposed event."""
        event = create_improvement_event(
            event_type=EventType.IMPROVEMENT_PROPOSED,
            improvement_id=improvement_id,
            strategy=strategy,
            target_services=target_services,
            expected_improvement=expected_improvement,
            risk_level=risk_level,
            priority=EventPriority.HIGH,
            **kwargs,
        )

        return await self.publish_event(event)

    async def publish_improvement_executed(
        self,
        improvement_id: str,
        strategy: str,
        actual_improvement: float,
        execution_time: float,
        constitutional_compliance_score: float,
        **kwargs,
    ) -> bool:
        """Publish improvement executed event."""
        event = create_improvement_event(
            event_type=EventType.IMPROVEMENT_EXECUTED,
            improvement_id=improvement_id,
            strategy=strategy,
            actual_improvement=actual_improvement,
            execution_time=execution_time,
            constitutional_compliance_score=constitutional_compliance_score,
            priority=EventPriority.HIGH,
            **kwargs,
        )

        return await self.publish_event(event)

    async def publish_improvement_failed(
        self,
        improvement_id: str,
        strategy: str,
        error_message: str,
        rollback_available: bool,
        **kwargs,
    ) -> bool:
        """Publish improvement failed event."""
        event = create_improvement_event(
            event_type=EventType.IMPROVEMENT_FAILED,
            improvement_id=improvement_id,
            strategy=strategy,
            rollback_available=rollback_available,
            priority=EventPriority.CRITICAL,
            metadata={"error_message": error_message},
            **kwargs,
        )

        return await self.publish_event(event)

    async def publish_performance_metrics(
        self,
        metric_name: str,
        metric_value: float,
        service_name: str,
        baseline_value: float = None,
        improvement_percentage: float = None,
        **kwargs,
    ) -> bool:
        """Publish performance metrics updated event."""
        event = create_performance_event(
            event_type=EventType.PERFORMANCE_METRICS_UPDATED,
            metric_name=metric_name,
            metric_value=metric_value,
            service_name=service_name,
            baseline_value=baseline_value,
            improvement_percentage=improvement_percentage,
            priority=EventPriority.NORMAL,
            **kwargs,
        )

        return await self.publish_event(event)

    async def publish_performance_alert(
        self,
        metric_name: str,
        metric_value: float,
        service_name: str,
        alert_level: str,
        threshold_value: float,
        **kwargs,
    ) -> bool:
        """Publish performance alert event."""
        event = create_performance_event(
            event_type=EventType.PERFORMANCE_ALERT_TRIGGERED,
            metric_name=metric_name,
            metric_value=metric_value,
            service_name=service_name,
            alert_level=alert_level,
            threshold_value=threshold_value,
            priority=(
                EventPriority.HIGH
                if alert_level == "critical"
                else EventPriority.NORMAL
            ),
            **kwargs,
        )

        return await self.publish_event(event)

    async def publish_constitutional_assessment(
        self,
        improvement_id: str,
        compliance_score: float,
        constitutional_hash: str,
        assessment_type: str,
        violations: list = None,
        **kwargs,
    ) -> bool:
        """Publish constitutional assessment completed event."""
        event = create_constitutional_event(
            event_type=EventType.CONSTITUTIONAL_ASSESSMENT_COMPLETED,
            improvement_id=improvement_id,
            compliance_score=compliance_score,
            constitutional_hash=constitutional_hash,
            assessment_type=assessment_type,
            violations=violations or [],
            priority=EventPriority.HIGH,
            **kwargs,
        )

        return await self.publish_event(event)

    async def publish_constitutional_violation(
        self,
        improvement_id: str,
        compliance_score: float,
        violations: list,
        remediation_required: bool,
        **kwargs,
    ) -> bool:
        """Publish constitutional violation detected event."""
        event = create_constitutional_event(
            event_type=EventType.CONSTITUTIONAL_VIOLATION_DETECTED,
            improvement_id=improvement_id,
            compliance_score=compliance_score,
            violations=violations,
            remediation_required=remediation_required,
            priority=EventPriority.CRITICAL,
            **kwargs,
        )

        return await self.publish_event(event)

    async def publish_bandit_arm_selected(
        self,
        algorithm_type: str,
        arm_name: str,
        arm_pulls: int,
        confidence_bound: float,
        action_taken: str,
        **kwargs,
    ) -> bool:
        """Publish bandit arm selected event."""
        event = create_bandit_event(
            event_type=EventType.BANDIT_ARM_SELECTED,
            algorithm_type=algorithm_type,
            arm_name=arm_name,
            arm_pulls=arm_pulls,
            confidence_bound=confidence_bound,
            action_taken=action_taken,
            priority=EventPriority.NORMAL,
            **kwargs,
        )

        return await self.publish_event(event)

    async def publish_bandit_reward_updated(
        self,
        algorithm_type: str,
        arm_name: str,
        arm_rewards: float,
        arm_success_rate: float,
        total_pulls: int,
        average_reward: float,
        **kwargs,
    ) -> bool:
        """Publish bandit reward updated event."""
        event = create_bandit_event(
            event_type=EventType.BANDIT_REWARD_UPDATED,
            algorithm_type=algorithm_type,
            arm_name=arm_name,
            arm_rewards=arm_rewards,
            arm_success_rate=arm_success_rate,
            total_pulls=total_pulls,
            average_reward=average_reward,
            priority=EventPriority.NORMAL,
            **kwargs,
        )

        return await self.publish_event(event)

    def _update_metrics(self, event: DGMEvent, success: bool):
        """Update publishing metrics."""
        if success:
            self.metrics["events_published"] += 1
        else:
            self.metrics["events_failed"] += 1

        # Track by event type
        event_type = event.event_type.value
        if event_type not in self.metrics["events_by_type"]:
            self.metrics["events_by_type"][event_type] = {"published": 0, "failed": 0}

        if success:
            self.metrics["events_by_type"][event_type]["published"] += 1
        else:
            self.metrics["events_by_type"][event_type]["failed"] += 1

        # Track by priority
        priority = event.priority.value
        if priority not in self.metrics["events_by_priority"]:
            self.metrics["events_by_priority"][priority] = {"published": 0, "failed": 0}

        if success:
            self.metrics["events_by_priority"][priority]["published"] += 1
        else:
            self.metrics["events_by_priority"][priority]["failed"] += 1

    def get_metrics(self) -> dict[str, Any]:
        """Get publishing metrics."""
        return self.metrics.copy()
