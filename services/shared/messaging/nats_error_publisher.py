"""
NATS Error Event Publisher for ACGS
Publishes error events to NATS message broker for distributed error tracking and analysis.
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

import nats
from nats.aio.client import Client as NATS
from nats.js.api import ConsumerConfig, StreamConfig
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)


@dataclass
class ErrorEvent:
    """Error event data structure."""

    event_id: str
    timestamp: str
    service_name: str
    service_port: int
    error_type: str
    error_code: str
    error_message: str
    severity: str  # critical, high, medium, low

    # Optional fields
    request_id: str | None = None
    user_id: str | None = None
    endpoint: str | None = None
    response_time_ms: float | None = None
    constitutional_compliance_score: float | None = None
    stack_trace: str | None = None
    context: dict[str, Any] | None = None

    # Metadata
    constitutional_hash: str = "cdd01ef066bc6cf2"
    environment: str = "production"


@dataclass
class ErrorPattern:
    """Error pattern data structure."""

    pattern_id: str
    pattern_type: str
    services_affected: list[str]
    frequency: int
    first_seen: str
    last_seen: str
    root_cause_hypothesis: str
    suggested_remediation: list[str]
    constitutional_impact: float


class NATSErrorPublisher:
    """NATS-based error event publisher."""

    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.nats_url = nats_url
        self.nc: NATS | None = None
        self.js = None

        # Stream and subject configuration
        self.error_stream = "ACGS_ERRORS"
        self.error_subject = "acgs.errors"
        self.pattern_subject = "acgs.error_patterns"
        self.remediation_subject = "acgs.remediation"

        self.setup_metrics()

        logger.info("NATS Error Publisher initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics."""
        self.events_published_total = Counter(
            "nats_error_events_published_total",
            "Total error events published to NATS",
            ["service", "error_type", "severity"],
        )

        self.publish_duration = Histogram(
            "nats_error_publish_duration_seconds",
            "Duration of error event publishing",
            ["event_type"],
        )

        self.publish_failures_total = Counter(
            "nats_error_publish_failures_total",
            "Total failed error event publications",
            ["error_type"],
        )

    async def connect(self):
        """Connect to NATS server and setup JetStream."""
        try:
            self.nc = await nats.connect(self.nats_url)
            self.js = self.nc.jetstream()

            # Create or update the error stream
            await self.setup_error_stream()

            logger.info(f"Connected to NATS at {self.nats_url}")

        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            raise

    async def setup_error_stream(self):
        """Setup NATS JetStream for error events."""
        try:
            # Define stream configuration
            stream_config = StreamConfig(
                name=self.error_stream,
                subjects=[
                    f"{self.error_subject}.*",
                    f"{self.pattern_subject}.*",
                    f"{self.remediation_subject}.*",
                ],
                retention="limits",
                max_msgs=1000000,  # Keep up to 1M messages
                max_age=7 * 24 * 3600,  # Keep for 7 days
                storage="file",
                replicas=1,
            )

            # Create or update stream
            try:
                await self.js.add_stream(stream_config)
                logger.info(f"Created NATS stream: {self.error_stream}")
            except Exception as e:
                if "stream name already in use" in str(e).lower():
                    await self.js.update_stream(stream_config)
                    logger.info(f"Updated NATS stream: {self.error_stream}")
                else:
                    raise

        except Exception as e:
            logger.error(f"Failed to setup error stream: {e}")
            raise

    async def publish_error_event(self, error_event: ErrorEvent):
        """Publish an error event to NATS."""
        if not self.nc or not self.js:
            await self.connect()

        start_time = asyncio.get_event_loop().time()

        try:
            # Convert error event to JSON
            event_data = asdict(error_event)
            event_json = json.dumps(event_data, default=str)

            # Determine subject based on service and error type
            subject = f"{self.error_subject}.{error_event.service_name}.{error_event.error_type.lower()}"

            # Publish to NATS JetStream
            ack = await self.js.publish(
                subject,
                event_json.encode(),
                headers={
                    "service": error_event.service_name,
                    "error_type": error_event.error_type,
                    "severity": error_event.severity,
                    "constitutional_hash": error_event.constitutional_hash,
                },
            )

            # Record metrics
            duration = asyncio.get_event_loop().time() - start_time

            self.events_published_total.labels(
                service=error_event.service_name,
                error_type=error_event.error_type,
                severity=error_event.severity,
            ).inc()

            self.publish_duration.labels(event_type="error").observe(duration)

            logger.debug(
                f"Published error event {error_event.event_id} to {subject} "
                f"(seq: {ack.seq})"
            )

        except Exception as e:
            self.publish_failures_total.labels(error_type="error").inc()
            logger.error(f"Failed to publish error event: {e}")
            raise

    async def publish_error_pattern(self, error_pattern: ErrorPattern):
        """Publish an error pattern to NATS."""
        if not self.nc or not self.js:
            await self.connect()

        start_time = asyncio.get_event_loop().time()

        try:
            # Convert error pattern to JSON
            pattern_data = asdict(error_pattern)
            pattern_json = json.dumps(pattern_data, default=str)

            # Publish to NATS JetStream
            subject = f"{self.pattern_subject}.{error_pattern.pattern_type.lower()}"

            ack = await self.js.publish(
                subject,
                pattern_json.encode(),
                headers={
                    "pattern_type": error_pattern.pattern_type,
                    "services_affected": ",".join(error_pattern.services_affected),
                    "frequency": str(error_pattern.frequency),
                },
            )

            # Record metrics
            duration = asyncio.get_event_loop().time() - start_time
            self.publish_duration.labels(event_type="pattern").observe(duration)

            logger.info(
                f"Published error pattern {error_pattern.pattern_id} to {subject} "
                f"(seq: {ack.seq})"
            )

        except Exception as e:
            self.publish_failures_total.labels(error_type="pattern").inc()
            logger.error(f"Failed to publish error pattern: {e}")
            raise

    async def publish_remediation_action(self, action_data: dict[str, Any]):
        """Publish a remediation action to NATS."""
        if not self.nc or not self.js:
            await self.connect()

        start_time = asyncio.get_event_loop().time()

        try:
            # Convert action data to JSON
            action_json = json.dumps(action_data, default=str)

            # Publish to NATS JetStream
            subject = f"{self.remediation_subject}.{action_data.get('action_type', 'unknown')}"

            ack = await self.js.publish(
                subject,
                action_json.encode(),
                headers={
                    "action_type": action_data.get("action_type", "unknown"),
                    "target_service": action_data.get("target_service", "unknown"),
                    "priority": str(action_data.get("priority", 3)),
                },
            )

            # Record metrics
            duration = asyncio.get_event_loop().time() - start_time
            self.publish_duration.labels(event_type="remediation").observe(duration)

            logger.info(
                f"Published remediation action {action_data.get('action_id')} to {subject} "
                f"(seq: {ack.seq})"
            )

        except Exception as e:
            self.publish_failures_total.labels(error_type="remediation").inc()
            logger.error(f"Failed to publish remediation action: {e}")
            raise

    async def subscribe_to_error_events(
        self, callback, service_filter: str | None = None
    ):
        """Subscribe to error events with optional service filtering."""
        if not self.nc or not self.js:
            await self.connect()

        try:
            # Determine subscription subject
            if service_filter:
                subject = f"{self.error_subject}.{service_filter}.*"
            else:
                subject = f"{self.error_subject}.*"

            # Create consumer configuration
            consumer_config = ConsumerConfig(
                durable_name=f"error_subscriber_{service_filter or 'all'}",
                deliver_policy="new",
                ack_policy="explicit",
            )

            # Subscribe to the stream
            psub = await self.js.pull_subscribe(
                subject, durable=consumer_config.durable_name, config=consumer_config
            )

            logger.info(f"Subscribed to error events: {subject}")

            # Process messages
            while True:
                try:
                    msgs = await psub.fetch(batch=10, timeout=1.0)

                    for msg in msgs:
                        try:
                            # Parse error event
                            event_data = json.loads(msg.data.decode())

                            # Call the callback function
                            await callback(event_data, msg.headers)

                            # Acknowledge the message
                            await msg.ack()

                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            await msg.nak()

                except Exception as e:
                    if "timeout" not in str(e).lower():
                        logger.error(f"Error fetching messages: {e}")
                    await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Failed to subscribe to error events: {e}")
            raise

    async def get_error_statistics(self, time_window_hours: int = 24) -> dict[str, Any]:
        """Get error statistics from NATS stream."""
        if not self.nc or not self.js:
            await self.connect()

        try:
            # Get stream info
            stream_info = await self.js.stream_info(self.error_stream)

            # Calculate basic statistics
            stats = {
                "total_messages": stream_info.state.messages,
                "total_bytes": stream_info.state.bytes,
                "first_seq": stream_info.state.first_seq,
                "last_seq": stream_info.state.last_seq,
                "consumer_count": stream_info.state.consumer_count,
                "subjects": stream_info.config.subjects,
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get error statistics: {e}")
            return {}

    async def disconnect(self):
        """Disconnect from NATS server."""
        if self.nc:
            await self.nc.close()
            logger.info("Disconnected from NATS")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Global NATS error publisher instance
nats_error_publisher = NATSErrorPublisher()


# Convenience functions
async def publish_error(
    service_name: str,
    error_type: str,
    error_message: str,
    severity: str = "medium",
    **kwargs,
):
    """Convenience function to publish an error event."""
    error_event = ErrorEvent(
        event_id=f"{service_name}_{int(datetime.now().timestamp())}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        service_name=service_name,
        service_port=kwargs.get("service_port", 0),
        error_type=error_type,
        error_code=kwargs.get("error_code", "UNKNOWN"),
        error_message=error_message,
        severity=severity,
        **{k: v for k, v in kwargs.items() if k not in ["service_port", "error_code"]},
    )

    await nats_error_publisher.publish_error_event(error_event)


async def publish_pattern(
    pattern_id: str,
    pattern_type: str,
    services_affected: list[str],
    frequency: int,
    root_cause: str,
    remediation: list[str],
):
    """Convenience function to publish an error pattern."""
    error_pattern = ErrorPattern(
        pattern_id=pattern_id,
        pattern_type=pattern_type,
        services_affected=services_affected,
        frequency=frequency,
        first_seen=datetime.now(timezone.utc).isoformat(),
        last_seen=datetime.now(timezone.utc).isoformat(),
        root_cause_hypothesis=root_cause,
        suggested_remediation=remediation,
        constitutional_impact=0.0,
    )

    await nats_error_publisher.publish_error_pattern(error_pattern)
