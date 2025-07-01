"""
Event Subscriber for DGM Service.

Provides high-level event subscription capabilities with automatic
message parsing, error handling, and handler registration.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .message_types import EventType, get_subject_for_event
from .nats_client import NATSClient


@dataclass
class SubscriptionConfig:
    """Configuration for event subscription."""

    subject: str
    handler: Callable
    queue_group: str | None = None
    durable_name: str | None = None
    max_retries: int = 3
    retry_delay: float = 1.0
    dead_letter_subject: str | None = None


class EventSubscriber:
    """High-level event subscriber for DGM service events."""

    def __init__(self, nats_client: NATSClient):
        """Initialize event subscriber with NATS client."""
        self.nats_client = nats_client
        self.logger = logging.getLogger(__name__)

        # Subscription tracking
        self.subscriptions: dict[str, SubscriptionConfig] = {}
        self.handlers: dict[EventType, list[Callable]] = {}

        # Processing metrics
        self.metrics = {
            "messages_received": 0,
            "messages_processed": 0,
            "messages_failed": 0,
            "messages_retried": 0,
            "handlers_registered": 0,
            "active_subscriptions": 0,
        }

    async def subscribe_to_event(
        self,
        event_type: EventType,
        handler: Callable,
        queue_group: str | None = None,
        durable_name: str | None = None,
    ) -> bool:
        """Subscribe to specific event type with handler."""
        try:
            subject = get_subject_for_event(event_type)

            # Create wrapper handler for event processing
            async def event_handler(
                subject: str,
                data: dict[str, Any],
                headers: dict[str, str] | None = None,
            ):
                await self._process_event(event_type, handler, data, headers)

            # Subscribe to NATS subject
            success = await self.nats_client.subscribe(
                subject=subject,
                handler=event_handler,
                queue_group=queue_group,
                durable=durable_name,
            )

            if success:
                # Track subscription
                config = SubscriptionConfig(
                    subject=subject,
                    handler=handler,
                    queue_group=queue_group,
                    durable_name=durable_name,
                )
                self.subscriptions[subject] = config

                # Track handler
                if event_type not in self.handlers:
                    self.handlers[event_type] = []
                self.handlers[event_type].append(handler)

                self.metrics["handlers_registered"] += 1
                self.metrics["active_subscriptions"] += 1

                self.logger.info(f"Subscribed to {event_type.value} events")

            return success

        except Exception as e:
            self.logger.error(f"Failed to subscribe to {event_type.value}: {e}")
            return False

    async def subscribe_to_improvements(
        self, handler: Callable, queue_group: str = "dgm-improvements"
    ) -> bool:
        """Subscribe to all improvement-related events."""
        improvement_events = [
            EventType.IMPROVEMENT_PROPOSED,
            EventType.IMPROVEMENT_APPROVED,
            EventType.IMPROVEMENT_REJECTED,
            EventType.IMPROVEMENT_EXECUTED,
            EventType.IMPROVEMENT_COMPLETED,
            EventType.IMPROVEMENT_FAILED,
            EventType.IMPROVEMENT_ROLLED_BACK,
        ]

        success_count = 0
        for event_type in improvement_events:
            if await self.subscribe_to_event(event_type, handler, queue_group):
                success_count += 1

        self.logger.info(
            f"Subscribed to {success_count}/{len(improvement_events)} improvement events"
        )
        return success_count == len(improvement_events)

    async def subscribe_to_performance(
        self, handler: Callable, queue_group: str = "dgm-performance"
    ) -> bool:
        """Subscribe to all performance-related events."""
        performance_events = [
            EventType.PERFORMANCE_METRICS_UPDATED,
            EventType.PERFORMANCE_BASELINE_ESTABLISHED,
            EventType.PERFORMANCE_DEGRADATION_DETECTED,
            EventType.PERFORMANCE_IMPROVEMENT_DETECTED,
            EventType.PERFORMANCE_ALERT_TRIGGERED,
        ]

        success_count = 0
        for event_type in performance_events:
            if await self.subscribe_to_event(event_type, handler, queue_group):
                success_count += 1

        self.logger.info(
            f"Subscribed to {success_count}/{len(performance_events)} performance events"
        )
        return success_count == len(performance_events)

    async def subscribe_to_constitutional(
        self, handler: Callable, queue_group: str = "dgm-constitutional"
    ) -> bool:
        """Subscribe to all constitutional-related events."""
        constitutional_events = [
            EventType.CONSTITUTIONAL_ASSESSMENT_STARTED,
            EventType.CONSTITUTIONAL_ASSESSMENT_COMPLETED,
            EventType.CONSTITUTIONAL_VIOLATION_DETECTED,
            EventType.CONSTITUTIONAL_COMPLIANCE_VERIFIED,
            EventType.CONSTITUTIONAL_REMEDIATION_REQUIRED,
        ]

        success_count = 0
        for event_type in constitutional_events:
            if await self.subscribe_to_event(event_type, handler, queue_group):
                success_count += 1

        self.logger.info(
            f"Subscribed to {success_count}/{len(constitutional_events)} constitutional events"
        )
        return success_count == len(constitutional_events)

    async def subscribe_to_bandit(
        self, handler: Callable, queue_group: str = "dgm-bandit"
    ) -> bool:
        """Subscribe to all bandit algorithm events."""
        bandit_events = [
            EventType.BANDIT_ARM_SELECTED,
            EventType.BANDIT_REWARD_UPDATED,
            EventType.BANDIT_STATE_UPDATED,
            EventType.BANDIT_EXPLORATION_TRIGGERED,
            EventType.BANDIT_EXPLOITATION_TRIGGERED,
        ]

        success_count = 0
        for event_type in bandit_events:
            if await self.subscribe_to_event(event_type, handler, queue_group):
                success_count += 1

        self.logger.info(
            f"Subscribed to {success_count}/{len(bandit_events)} bandit events"
        )
        return success_count == len(bandit_events)

    async def subscribe_to_pattern(
        self,
        subject_pattern: str,
        handler: Callable,
        queue_group: str | None = None,
        durable_name: str | None = None,
    ) -> bool:
        """Subscribe to events matching a subject pattern."""
        try:
            # Create wrapper handler for pattern processing
            async def pattern_handler(
                subject: str,
                data: dict[str, Any],
                headers: dict[str, str] | None = None,
            ):
                await self._process_pattern_event(
                    subject_pattern, handler, subject, data, headers
                )

            # Subscribe to NATS pattern
            success = await self.nats_client.subscribe(
                subject=subject_pattern,
                handler=pattern_handler,
                queue_group=queue_group,
                durable=durable_name,
            )

            if success:
                config = SubscriptionConfig(
                    subject=subject_pattern,
                    handler=handler,
                    queue_group=queue_group,
                    durable_name=durable_name,
                )
                self.subscriptions[subject_pattern] = config

                self.metrics["handlers_registered"] += 1
                self.metrics["active_subscriptions"] += 1

                self.logger.info(f"Subscribed to pattern: {subject_pattern}")

            return success

        except Exception as e:
            self.logger.error(f"Failed to subscribe to pattern {subject_pattern}: {e}")
            return False

    async def _process_event(
        self,
        event_type: EventType,
        handler: Callable,
        data: dict[str, Any],
        headers: dict[str, str] | None = None,
    ):
        """Process individual event with error handling and retries."""
        self.metrics["messages_received"] += 1

        try:
            # Extract event data
            event_data = data.get("data", {})
            event_metadata = {
                "event_id": data.get("event_id"),
                "timestamp": data.get("timestamp"),
                "source": data.get("source"),
                "headers": headers or {},
            }

            # Call handler
            await handler(event_type, event_data, event_metadata)

            self.metrics["messages_processed"] += 1
            self.logger.debug(
                f"Processed {event_type.value} event: {event_metadata['event_id']}"
            )

        except Exception as e:
            self.metrics["messages_failed"] += 1
            self.logger.error(f"Error processing {event_type.value} event: {e}")

            # TODO: Implement retry logic and dead letter queue
            await self._handle_processing_error(event_type, data, e)

    async def _process_pattern_event(
        self,
        pattern: str,
        handler: Callable,
        subject: str,
        data: dict[str, Any],
        headers: dict[str, str] | None = None,
    ):
        """Process pattern-matched event."""
        self.metrics["messages_received"] += 1

        try:
            # Extract event data
            event_data = data.get("data", {})
            event_metadata = {
                "event_id": data.get("event_id"),
                "timestamp": data.get("timestamp"),
                "source": data.get("source"),
                "subject": subject,
                "pattern": pattern,
                "headers": headers or {},
            }

            # Call handler
            await handler(subject, event_data, event_metadata)

            self.metrics["messages_processed"] += 1
            self.logger.debug(
                f"Processed pattern event on {subject}: {event_metadata['event_id']}"
            )

        except Exception as e:
            self.metrics["messages_failed"] += 1
            self.logger.error(f"Error processing pattern event on {subject}: {e}")

            await self._handle_processing_error(pattern, data, e)

    async def _handle_processing_error(
        self, identifier: str, data: dict[str, Any], error: Exception
    ):
        """Handle event processing errors with retry logic."""
        try:
            # Log error details
            event_id = data.get("event_id", "unknown")
            self.logger.error(
                f"Processing error for {identifier} event {event_id}: {error}"
            )

            # TODO: Implement sophisticated error handling:
            # 1. Retry with exponential backoff
            # 2. Dead letter queue for failed messages
            # 3. Alert on repeated failures
            # 4. Circuit breaker pattern

            # For now, just log and continue
            pass

        except Exception as e:
            self.logger.error(f"Error in error handler: {e}")

    async def unsubscribe_from_event(self, event_type: EventType) -> bool:
        """Unsubscribe from specific event type."""
        try:
            subject = get_subject_for_event(event_type)

            if subject in self.subscriptions:
                # Remove from tracking
                del self.subscriptions[subject]

                if event_type in self.handlers:
                    del self.handlers[event_type]

                self.metrics["active_subscriptions"] -= 1

                self.logger.info(f"Unsubscribed from {event_type.value} events")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to unsubscribe from {event_type.value}: {e}")
            return False

    async def unsubscribe_all(self):
        """Unsubscribe from all events."""
        try:
            self.subscriptions.clear()
            self.handlers.clear()
            self.metrics["active_subscriptions"] = 0

            self.logger.info("Unsubscribed from all events")

        except Exception as e:
            self.logger.error(f"Error unsubscribing from all events: {e}")

    def get_metrics(self) -> dict[str, Any]:
        """Get subscription metrics."""
        return self.metrics.copy()

    def get_active_subscriptions(self) -> list[str]:
        """Get list of active subscription subjects."""
        return list(self.subscriptions.keys())
