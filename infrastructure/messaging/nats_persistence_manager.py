#!/usr/bin/env python3
"""
ACGS NATS Event Persistence & Replay Manager
Comprehensive event persistence, replay, and recovery system for NATS JetStream.
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Callable

import nats
from nats.aio.client import Client as NATS
from nats.js import JetStreamContext
from nats.js.api import StreamConfig, ConsumerConfig, RetentionPolicy, StorageType
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    start_http_server,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class EventMetadata:
    """Event metadata for persistence and replay."""

    event_id: str
    event_type: str
    subject: str
    timestamp: datetime
    source_service: str
    constitutional_hash: str = CONSTITUTIONAL_HASH

    # Persistence metadata
    stream_name: str = ""
    sequence_number: int = 0
    replay_count: int = 0

    # Processing metadata
    processing_status: str = "pending"  # pending, processing, completed, failed
    retry_count: int = 0
    last_error: Optional[str] = None


@dataclass
class ReplayConfiguration:
    """Configuration for event replay."""

    replay_id: str
    stream_name: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    start_sequence: Optional[int] = None
    end_sequence: Optional[int] = None

    # Replay options
    replay_speed: float = 1.0  # 1.0 = real-time, 2.0 = 2x speed, etc.
    filter_subjects: List[str] = field(default_factory=list)
    filter_event_types: List[str] = field(default_factory=list)

    # Target configuration
    target_subjects: List[str] = field(default_factory=list)
    replay_to_original_subjects: bool = True

    # Constitutional compliance
    constitutional_hash: str = CONSTITUTIONAL_HASH


class NATSPersistenceManager:
    """NATS event persistence and replay manager."""

    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.nats_url = nats_url
        self.nc: Optional[NATS] = None
        self.js: Optional[JetStreamContext] = None

        # Metrics
        self.registry = CollectorRegistry()
        self.setup_metrics()

        # Stream configurations
        self.stream_configs = self.setup_stream_configurations()

        # Event handlers
        self.event_handlers: Dict[str, Callable] = {}

        # Replay management
        self.active_replays: Dict[str, ReplayConfiguration] = {}

        logger.info("NATS Persistence Manager initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics."""
        self.events_persisted = Counter(
            "acgs_nats_events_persisted_total",
            "Total events persisted to NATS streams",
            ["stream", "subject", "event_type"],
            registry=self.registry,
        )

        self.events_replayed = Counter(
            "acgs_nats_events_replayed_total",
            "Total events replayed from NATS streams",
            ["stream", "replay_id"],
            registry=self.registry,
        )

        self.stream_size_bytes = Gauge(
            "acgs_nats_stream_size_bytes",
            "Size of NATS streams in bytes",
            ["stream"],
            registry=self.registry,
        )

        self.stream_message_count = Gauge(
            "acgs_nats_stream_message_count",
            "Number of messages in NATS streams",
            ["stream"],
            registry=self.registry,
        )

        self.replay_duration = Histogram(
            "acgs_nats_replay_duration_seconds",
            "Duration of event replays",
            ["replay_id"],
            registry=self.registry,
        )

        self.constitutional_compliance_events = Counter(
            "acgs_nats_constitutional_compliance_events_total",
            "Events with constitutional compliance validation",
            ["stream", "compliance_status"],
            registry=self.registry,
        )

    def setup_stream_configurations(self) -> Dict[str, StreamConfig]:
        """Setup NATS stream configurations."""
        return {
            "acgs-events": StreamConfig(
                name="acgs-events",
                subjects=["acgs.events.>"],
                retention=RetentionPolicy.LIMITS,
                max_age=timedelta(days=30),  # Keep events for 30 days
                max_bytes=10 * 1024 * 1024 * 1024,  # 10GB max
                max_msgs=10_000_000,  # 10M messages max
                storage=StorageType.FILE,
                replicas=1,
                description="ACGS general events stream",
            ),
            "acgs-evolution": StreamConfig(
                name="acgs-evolution",
                subjects=["acgs.evolution.>"],
                retention=RetentionPolicy.LIMITS,
                max_age=timedelta(days=90),  # Keep evolution events longer
                max_bytes=5 * 1024 * 1024 * 1024,  # 5GB max
                max_msgs=1_000_000,  # 1M messages max
                storage=StorageType.FILE,
                replicas=1,
                description="ACGS evolution events stream",
            ),
            "acgs-constitutional": StreamConfig(
                name="acgs-constitutional",
                subjects=["acgs.constitutional.>"],
                retention=RetentionPolicy.LIMITS,
                max_age=timedelta(days=365),  # Keep constitutional events for 1 year
                max_bytes=2 * 1024 * 1024 * 1024,  # 2GB max
                max_msgs=500_000,  # 500K messages max
                storage=StorageType.FILE,
                replicas=1,
                description="ACGS constitutional compliance events stream",
            ),
            "acgs-audit": StreamConfig(
                name="acgs-audit",
                subjects=["acgs.audit.>"],
                retention=RetentionPolicy.LIMITS,
                max_age=timedelta(days=2555),  # Keep audit events for 7 years
                max_bytes=20 * 1024 * 1024 * 1024,  # 20GB max
                max_msgs=50_000_000,  # 50M messages max
                storage=StorageType.FILE,
                replicas=1,
                description="ACGS audit events stream",
            ),
        }

    async def start(self):
        """Start the NATS persistence manager."""
        logger.info("Starting NATS Persistence Manager...")

        # Connect to NATS
        self.nc = await nats.connect(self.nats_url)
        self.js = self.nc.jetstream()

        # Setup streams
        await self.setup_streams()

        # Start metrics server
        start_http_server(8097, registry=self.registry)
        logger.info("NATS persistence metrics server started on port 8097")

        # Start monitoring tasks
        asyncio.create_task(self.stream_monitoring_loop())

        logger.info("NATS Persistence Manager started successfully")

    async def stop(self):
        """Stop the NATS persistence manager."""
        logger.info("Stopping NATS Persistence Manager...")

        if self.nc:
            await self.nc.close()

        logger.info("NATS Persistence Manager stopped")

    async def setup_streams(self):
        """Setup NATS JetStream streams."""
        for stream_name, config in self.stream_configs.items():
            try:
                # Try to get existing stream
                try:
                    stream_info = await self.js.stream_info(stream_name)
                    logger.info(f"Stream {stream_name} already exists")
                except:
                    # Create new stream
                    await self.js.add_stream(config)
                    logger.info(f"Created stream {stream_name}")

            except Exception as e:
                logger.error(f"Failed to setup stream {stream_name}: {e}")

    async def publish_event(
        self,
        subject: str,
        event_data: Dict[str, Any],
        event_type: str,
        source_service: str,
        metadata: Optional[Dict] = None,
    ) -> EventMetadata:
        """Publish an event to NATS with persistence."""

        # Create event metadata
        event_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)

        event_metadata = EventMetadata(
            event_id=event_id,
            event_type=event_type,
            subject=subject,
            timestamp=timestamp,
            source_service=source_service,
        )

        # Prepare event payload
        event_payload = {
            "metadata": {
                "event_id": event_id,
                "event_type": event_type,
                "timestamp": timestamp.isoformat(),
                "source_service": source_service,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                **(metadata or {}),
            },
            "data": event_data,
        }

        try:
            # Publish to NATS JetStream
            ack = await self.js.publish(
                subject,
                json.dumps(event_payload).encode(),
                headers={"event-id": event_id, "event-type": event_type},
            )

            # Update metadata with stream information
            event_metadata.stream_name = ack.stream
            event_metadata.sequence_number = ack.seq

            # Record metrics
            stream_name = self.get_stream_for_subject(subject)
            self.events_persisted.labels(
                stream=stream_name, subject=subject, event_type=event_type
            ).inc()

            # Record constitutional compliance
            self.constitutional_compliance_events.labels(
                stream=stream_name, compliance_status="validated"
            ).inc()

            logger.debug(f"Published event {event_id} to {subject}")

            return event_metadata

        except Exception as e:
            logger.error(f"Failed to publish event {event_id}: {e}")
            raise

    async def subscribe_to_events(
        self,
        subject: str,
        handler: Callable,
        consumer_name: Optional[str] = None,
        durable: bool = True,
    ):
        """Subscribe to events with persistence support."""

        if not consumer_name:
            consumer_name = f"consumer_{subject.replace('.', '_')}_{int(time.time())}"

        stream_name = self.get_stream_for_subject(subject)

        try:
            # Create consumer configuration
            consumer_config = ConsumerConfig(
                durable_name=consumer_name if durable else None,
                ack_policy="explicit",
                max_deliver=3,
                ack_wait=30,  # 30 seconds
            )

            # Subscribe to stream
            subscription = await self.js.subscribe(
                subject, consumer=consumer_name, config=consumer_config
            )

            # Process messages
            async def message_handler(msg):
                try:
                    # Parse event
                    event_payload = json.loads(msg.data.decode())

                    # Extract metadata
                    metadata = event_payload.get("metadata", {})
                    event_data = event_payload.get("data", {})

                    # Validate constitutional compliance
                    if metadata.get("constitutional_hash") != CONSTITUTIONAL_HASH:
                        logger.warning(
                            f"Constitutional hash mismatch in event {metadata.get('event_id')}"
                        )
                        self.constitutional_compliance_events.labels(
                            stream=stream_name, compliance_status="mismatch"
                        ).inc()

                    # Call handler
                    await handler(event_data, metadata)

                    # Acknowledge message
                    await msg.ack()

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await msg.nak()

            # Start message processing
            asyncio.create_task(
                self.process_subscription(subscription, message_handler)
            )

            logger.info(f"Subscribed to {subject} with consumer {consumer_name}")

        except Exception as e:
            logger.error(f"Failed to subscribe to {subject}: {e}")
            raise

    async def process_subscription(self, subscription, handler):
        """Process subscription messages."""
        async for msg in subscription.messages:
            await handler(msg)

    async def start_replay(self, config: ReplayConfiguration) -> str:
        """Start event replay from stream."""
        logger.info(
            f"Starting replay {config.replay_id} from stream {config.stream_name}"
        )

        self.active_replays[config.replay_id] = config

        try:
            # Create replay consumer
            consumer_name = f"replay_{config.replay_id}"

            consumer_config = ConsumerConfig(
                durable_name=consumer_name,
                ack_policy="explicit",
                deliver_policy="by_start_sequence" if config.start_sequence else "all",
                opt_start_seq=config.start_sequence,
                max_deliver=1,
            )

            # Subscribe to stream for replay
            subscription = await self.js.subscribe(
                f"{config.stream_name}.>",
                consumer=consumer_name,
                config=consumer_config,
            )

            # Start replay processing
            asyncio.create_task(self.process_replay(config, subscription))

            logger.info(f"Replay {config.replay_id} started successfully")
            return config.replay_id

        except Exception as e:
            logger.error(f"Failed to start replay {config.replay_id}: {e}")
            if config.replay_id in self.active_replays:
                del self.active_replays[config.replay_id]
            raise

    async def process_replay(self, config: ReplayConfiguration, subscription):
        """Process replay messages."""
        start_time = time.time()
        messages_replayed = 0

        try:
            async for msg in subscription.messages:
                # Parse message
                event_payload = json.loads(msg.data.decode())
                metadata = event_payload.get("metadata", {})

                # Apply filters
                if config.filter_subjects and msg.subject not in config.filter_subjects:
                    await msg.ack()
                    continue

                if (
                    config.filter_event_types
                    and metadata.get("event_type") not in config.filter_event_types
                ):
                    await msg.ack()
                    continue

                # Check time bounds
                if config.start_time or config.end_time:
                    event_time = datetime.fromisoformat(metadata.get("timestamp", ""))

                    if config.start_time and event_time < config.start_time:
                        await msg.ack()
                        continue

                    if config.end_time and event_time > config.end_time:
                        break

                # Apply replay speed (delay if needed)
                if config.replay_speed < 1.0:
                    delay = (
                        1.0 - config.replay_speed
                    ) * 0.1  # Simplified delay calculation
                    await asyncio.sleep(delay)

                # Republish event
                if config.replay_to_original_subjects:
                    target_subject = msg.subject
                else:
                    target_subject = (
                        config.target_subjects[0]
                        if config.target_subjects
                        else msg.subject
                    )

                await self.js.publish(target_subject, msg.data)

                # Record metrics
                self.events_replayed.labels(
                    stream=config.stream_name, replay_id=config.replay_id
                ).inc()

                messages_replayed += 1
                await msg.ack()

                # Check sequence bounds
                if config.end_sequence and msg.metadata.sequence >= config.end_sequence:
                    break

            # Record replay duration
            duration = time.time() - start_time
            self.replay_duration.labels(replay_id=config.replay_id).observe(duration)

            logger.info(
                f"Replay {config.replay_id} completed: {messages_replayed} messages in {duration:.2f}s"
            )

        except Exception as e:
            logger.error(f"Error in replay {config.replay_id}: {e}")
        finally:
            # Clean up
            if config.replay_id in self.active_replays:
                del self.active_replays[config.replay_id]

    async def stop_replay(self, replay_id: str):
        """Stop an active replay."""
        if replay_id in self.active_replays:
            del self.active_replays[replay_id]
            logger.info(f"Stopped replay {replay_id}")
        else:
            logger.warning(f"Replay {replay_id} not found")

    async def get_stream_info(self, stream_name: str) -> Dict:
        """Get information about a stream."""
        try:
            stream_info = await self.js.stream_info(stream_name)

            return {
                "name": stream_info.config.name,
                "subjects": stream_info.config.subjects,
                "messages": stream_info.state.messages,
                "bytes": stream_info.state.bytes,
                "first_seq": stream_info.state.first_seq,
                "last_seq": stream_info.state.last_seq,
                "consumer_count": stream_info.state.consumer_count,
                "created": (
                    stream_info.created.isoformat() if stream_info.created else None
                ),
            }

        except Exception as e:
            logger.error(f"Failed to get stream info for {stream_name}: {e}")
            return {}

    async def backup_stream(self, stream_name: str, backup_path: str):
        """Backup stream data to file."""
        logger.info(f"Starting backup of stream {stream_name} to {backup_path}")

        try:
            # Create consumer for backup
            consumer_name = f"backup_{stream_name}_{int(time.time())}"

            consumer_config = ConsumerConfig(
                durable_name=consumer_name, ack_policy="explicit", deliver_policy="all"
            )

            subscription = await self.js.subscribe(
                f"{stream_name}.>", consumer=consumer_name, config=consumer_config
            )

            # Write backup file
            import os

            os.makedirs(os.path.dirname(backup_path), exist_ok=True)

            with open(backup_path, "w") as f:
                message_count = 0

                async for msg in subscription.messages:
                    backup_entry = {
                        "subject": msg.subject,
                        "data": msg.data.decode(),
                        "headers": dict(msg.headers) if msg.headers else {},
                        "metadata": {
                            "sequence": msg.metadata.sequence,
                            "timestamp": (
                                msg.metadata.timestamp.isoformat()
                                if msg.metadata.timestamp
                                else None
                            ),
                        },
                    }

                    f.write(json.dumps(backup_entry) + "\n")
                    message_count += 1

                    await msg.ack()

            logger.info(
                f"Backup completed: {message_count} messages written to {backup_path}"
            )

        except Exception as e:
            logger.error(f"Failed to backup stream {stream_name}: {e}")
            raise

    async def restore_stream(self, stream_name: str, backup_path: str):
        """Restore stream data from backup file."""
        logger.info(f"Starting restore of stream {stream_name} from {backup_path}")

        try:
            with open(backup_path, "r") as f:
                message_count = 0

                for line in f:
                    backup_entry = json.loads(line.strip())

                    # Republish message
                    await self.js.publish(
                        backup_entry["subject"],
                        backup_entry["data"].encode(),
                        headers=backup_entry.get("headers"),
                    )

                    message_count += 1

            logger.info(
                f"Restore completed: {message_count} messages restored to {stream_name}"
            )

        except Exception as e:
            logger.error(f"Failed to restore stream {stream_name}: {e}")
            raise

    def get_stream_for_subject(self, subject: str) -> str:
        """Get the appropriate stream name for a subject."""
        if subject.startswith("acgs.evolution."):
            return "acgs-evolution"
        elif subject.startswith("acgs.constitutional."):
            return "acgs-constitutional"
        elif subject.startswith("acgs.audit."):
            return "acgs-audit"
        else:
            return "acgs-events"

    async def stream_monitoring_loop(self):
        """Monitor stream metrics."""
        while True:
            try:
                for stream_name in self.stream_configs.keys():
                    try:
                        stream_info = await self.js.stream_info(stream_name)

                        # Update metrics
                        self.stream_size_bytes.labels(stream=stream_name).set(
                            stream_info.state.bytes
                        )
                        self.stream_message_count.labels(stream=stream_name).set(
                            stream_info.state.messages
                        )

                    except Exception as e:
                        logger.warning(
                            f"Failed to get metrics for stream {stream_name}: {e}"
                        )

                await asyncio.sleep(60)  # Update every minute

            except Exception as e:
                logger.error(f"Error in stream monitoring loop: {e}")
                await asyncio.sleep(60)

    def get_persistence_summary(self) -> Dict:
        """Get persistence system summary."""
        return {
            "active_replays": len(self.active_replays),
            "configured_streams": len(self.stream_configs),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "nats_url": self.nats_url,
            "connected": self.nc is not None and not self.nc.is_closed,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global persistence manager instance
persistence_manager = NATSPersistenceManager()


async def create_replay_from_config(
    stream_name: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    replay_speed: float = 1.0,
    filter_subjects: Optional[List[str]] = None,
) -> str:
    """Create and start a replay from configuration parameters."""

    replay_config = ReplayConfiguration(
        replay_id=f"replay_{int(time.time())}_{stream_name}",
        stream_name=stream_name,
        start_time=datetime.fromisoformat(start_time) if start_time else None,
        end_time=datetime.fromisoformat(end_time) if end_time else None,
        replay_speed=replay_speed,
        filter_subjects=filter_subjects or [],
    )

    return await persistence_manager.start_replay(replay_config)


if __name__ == "__main__":

    async def main():
        await persistence_manager.start()

        try:
            # Keep running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            await persistence_manager.stop()

    asyncio.run(main())
