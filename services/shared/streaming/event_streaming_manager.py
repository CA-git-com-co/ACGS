"""
Event Streaming Manager

High-level orchestration layer for enterprise event streaming,
implementing the ACGE technical validation recommendations for
scalable, reliable, and constitutional-compliant event processing.

Key Features:
- Unified streaming orchestration across multiple topics and services
- Event routing and transformation pipelines
- Dead letter queue management and error recovery
- Constitutional compliance validation for all events
- Real-time monitoring and alerting
- Integration with existing NATS for lightweight events
- Graceful degradation and circuit breaker patterns
"""

# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import json
import logging
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from services.shared.monitoring.intelligent_alerting_system import (
    IntelligentAlertingSystem,
)
from services.shared.security.enhanced_audit_logging import EnhancedAuditLogger

from .kafka_config_manager import EnvironmentType, KafkaConfigManager
from .kafka_integration import (
    KafkaConsumer,
    KafkaMessage,
    KafkaProducer,
    KafkaStreamProcessor,
)

# NATS integration for lightweight messaging
try:
    import nats
    from nats.aio.client import Client as NATSClient

    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False
    logging.warning("NATS not available, using Kafka-only mode")

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events in the system"""

    CONSTITUTIONAL_DECISION = "constitutional_decision"
    POLICY_SYNTHESIS = "policy_synthesis"
    GOVERNANCE_ACTION = "governance_action"
    AUDIT_EVENT = "audit_event"
    METRIC_EVENT = "metric_event"
    ALERT_EVENT = "alert_event"
    COMPLIANCE_EVENT = "compliance_event"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    # APGF-specific event types
    APGF_WORKFLOW_INITIATED = "apgf_workflow_initiated"
    APGF_WORKFLOW_COMPLETED = "apgf_workflow_completed"
    APGF_WORKFLOW_FAILED = "apgf_workflow_failed"
    APGF_WORKFLOW_CANCELLED = "apgf_workflow_cancelled"
    APGF_AGENT_CREATED = "apgf_agent_created"
    APGF_AGENT_TERMINATED = "apgf_agent_terminated"
    APGF_POLICY_GENERATED = "apgf_policy_generated"
    APGF_POLICY_VALIDATED = "apgf_policy_validated"
    APGF_TOOL_EXECUTED = "apgf_tool_executed"
    APGF_TASK_ASSIGNED = "apgf_task_assigned"
    APGF_TASK_COMPLETED = "apgf_task_completed"
    # Context service event types
    CONTEXT_STORED = "context_stored"
    CONTEXT_RETRIEVED = "context_retrieved"
    CONTEXT_UPDATED = "context_updated"
    CONTEXT_EXPIRED = "context_expired"
    CONTEXT_SEARCHED = "context_searched"
    CONTEXT_ARCHIVED = "context_archived"
    CONTEXT_DELETED = "context_deleted"


class EventPriority(Enum):
    """Event priority levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EventRoutingStrategy(Enum):
    """Event routing strategies"""

    KAFKA_ONLY = "kafka_only"
    NATS_ONLY = "nats_only"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"


@dataclass
class StreamingEvent:
    """Unified streaming event structure"""

    event_id: str
    event_type: EventType
    priority: EventPriority
    source_service: str
    target_service: str | None
    payload: dict[str, Any]
    metadata: dict[str, Any]
    routing_strategy: EventRoutingStrategy
    constitutional_compliant: bool
    correlation_id: str | None
    timestamp: datetime
    ttl_seconds: int | None = None


@dataclass
class StreamingMetrics:
    """Streaming system metrics"""

    total_events_sent: int
    total_events_received: int
    events_failed: int
    events_in_dlq: int
    avg_processing_latency_ms: float
    avg_routing_latency_ms: float
    kafka_throughput_msgs_per_sec: float
    nats_throughput_msgs_per_sec: float
    constitutional_violations: int
    circuit_breaker_trips: int
    last_reset: datetime


@dataclass
class TopicMapping:
    """Topic mapping configuration"""

    event_type: EventType
    kafka_topic: str
    nats_subject: str | None
    partitioning_key: str | None
    priority_routing: bool
    dlq_enabled: bool
    retention_hours: int


class EventStreamingManager:
    """
    Production-ready event streaming orchestration manager
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Core components
        self.config_manager = KafkaConfigManager()
        self.alerting = IntelligentAlertingSystem()
        self.audit_logger = EnhancedAuditLogger()

        # Streaming infrastructure
        self.kafka_producers = {}
        self.kafka_consumers = {}
        self.kafka_stream_processors = {}
        self.nats_client = None

        # Configuration
        self.cluster_id = config.get("cluster_id", "acgs-main")
        self.environment = EnvironmentType(config.get("environment", "development"))
        self.default_routing_strategy = EventRoutingStrategy(
            config.get("default_routing_strategy", "hybrid")
        )

        # Topic mappings
        self.topic_mappings = self._initialize_topic_mappings()

        # Event handlers and processors
        self.event_handlers = {}
        self.event_transformers = {}
        self.routing_rules = {}

        # Circuit breaker and health monitoring
        self.circuit_breakers = {}
        self.health_status = {
            "kafka_healthy": False,
            "nats_healthy": False,
            "overall_healthy": False,
        }

        # Performance metrics
        self.metrics = StreamingMetrics(
            total_events_sent=0,
            total_events_received=0,
            events_failed=0,
            events_in_dlq=0,
            avg_processing_latency_ms=0.0,
            avg_routing_latency_ms=0.0,
            kafka_throughput_msgs_per_sec=0.0,
            nats_throughput_msgs_per_sec=0.0,
            constitutional_violations=0,
            circuit_breaker_trips=0,
            last_reset=datetime.utcnow(),
        )

        # Event processing state
        self.running = False
        self.shutdown_timeout = config.get("shutdown_timeout_seconds", 30)

    def _initialize_topic_mappings(self) -> dict[EventType, TopicMapping]:
        """Initialize default topic mappings"""
        return {
            EventType.CONSTITUTIONAL_DECISION: TopicMapping(
                event_type=EventType.CONSTITUTIONAL_DECISION,
                kafka_topic="constitutional-decisions",
                nats_subject="acgs.constitutional.decisions",
                partitioning_key="decision_id",
                priority_routing=True,
                dlq_enabled=True,
                retention_hours=168,  # 7 days
            ),
            EventType.POLICY_SYNTHESIS: TopicMapping(
                event_type=EventType.POLICY_SYNTHESIS,
                kafka_topic="policy-synthesis",
                nats_subject="acgs.policy.synthesis",
                partitioning_key="policy_id",
                priority_routing=True,
                dlq_enabled=True,
                retention_hours=72,  # 3 days
            ),
            EventType.GOVERNANCE_ACTION: TopicMapping(
                event_type=EventType.GOVERNANCE_ACTION,
                kafka_topic="governance-actions",
                nats_subject="acgs.governance.actions",
                partitioning_key="action_id",
                priority_routing=False,
                dlq_enabled=True,
                retention_hours=24,  # 1 day
            ),
            EventType.AUDIT_EVENT: TopicMapping(
                event_type=EventType.AUDIT_EVENT,
                kafka_topic="audit-events",
                nats_subject="acgs.audit.events",
                partitioning_key="user_id",
                priority_routing=False,
                dlq_enabled=False,
                retention_hours=720,  # 30 days
            ),
            EventType.METRIC_EVENT: TopicMapping(
                event_type=EventType.METRIC_EVENT,
                kafka_topic="metrics",
                nats_subject="acgs.metrics",
                partitioning_key="metric_type",
                priority_routing=False,
                dlq_enabled=False,
                retention_hours=24,  # 1 day
            ),
            EventType.ALERT_EVENT: TopicMapping(
                event_type=EventType.ALERT_EVENT,
                kafka_topic="alerts",
                nats_subject="acgs.alerts",
                partitioning_key="alert_type",
                priority_routing=True,
                dlq_enabled=True,
                retention_hours=72,  # 3 days
            ),
            EventType.COMPLIANCE_EVENT: TopicMapping(
                event_type=EventType.COMPLIANCE_EVENT,
                kafka_topic="compliance-events",
                nats_subject="acgs.compliance.events",
                partitioning_key="compliance_type",
                priority_routing=True,
                dlq_enabled=True,
                retention_hours=2160,  # 90 days
            ),
            EventType.USER_ACTION: TopicMapping(
                event_type=EventType.USER_ACTION,
                kafka_topic="user-actions",
                nats_subject="acgs.user.actions",
                partitioning_key="user_id",
                priority_routing=False,
                dlq_enabled=True,
                retention_hours=168,  # 7 days
            ),
            EventType.SYSTEM_EVENT: TopicMapping(
                event_type=EventType.SYSTEM_EVENT,
                kafka_topic="system-events",
                nats_subject="acgs.system.events",
                partitioning_key="service_name",
                priority_routing=False,
                dlq_enabled=True,
                retention_hours=48,  # 2 days
            ),
            # Context service event mappings
            EventType.CONTEXT_STORED: TopicMapping(
                event_type=EventType.CONTEXT_STORED,
                kafka_topic="context-operations",
                nats_subject="acgs.context.stored",
                partitioning_key="context_id",
                priority_routing=False,
                dlq_enabled=True,
                retention_hours=24,  # 1 day
            ),
            EventType.CONTEXT_RETRIEVED: TopicMapping(
                event_type=EventType.CONTEXT_RETRIEVED,
                kafka_topic="context-operations",
                nats_subject="acgs.context.retrieved",
                partitioning_key="context_id",
                priority_routing=False,
                dlq_enabled=False,  # High volume, no DLQ needed
                retention_hours=12,  # 12 hours
            ),
            EventType.CONTEXT_UPDATED: TopicMapping(
                event_type=EventType.CONTEXT_UPDATED,
                kafka_topic="context-operations",
                nats_subject="acgs.context.updated",
                partitioning_key="context_id",
                priority_routing=False,
                dlq_enabled=True,
                retention_hours=24,  # 1 day
            ),
            EventType.CONTEXT_EXPIRED: TopicMapping(
                event_type=EventType.CONTEXT_EXPIRED,
                kafka_topic="context-lifecycle",
                nats_subject="acgs.context.expired",
                partitioning_key="context_type",
                priority_routing=False,
                dlq_enabled=True,
                retention_hours=72,  # 3 days
            ),
            EventType.CONTEXT_SEARCHED: TopicMapping(
                event_type=EventType.CONTEXT_SEARCHED,
                kafka_topic="context-analytics",
                nats_subject="acgs.context.searched",
                partitioning_key="query_hash",
                priority_routing=False,
                dlq_enabled=False,  # Analytics data, no DLQ needed
                retention_hours=24,  # 1 day
            ),
            EventType.CONTEXT_ARCHIVED: TopicMapping(
                event_type=EventType.CONTEXT_ARCHIVED,
                kafka_topic="context-lifecycle",
                nats_subject="acgs.context.archived",
                partitioning_key="context_type",
                priority_routing=False,
                dlq_enabled=True,
                retention_hours=168,  # 7 days
            ),
            EventType.CONTEXT_DELETED: TopicMapping(
                event_type=EventType.CONTEXT_DELETED,
                kafka_topic="context-lifecycle",
                nats_subject="acgs.context.deleted",
                partitioning_key="context_type",
                priority_routing=True,  # Important for audit
                dlq_enabled=True,
                retention_hours=720,  # 30 days for audit trail
            ),
        }

    async def initialize(self) -> bool:
        """
        Initialize the event streaming manager

        Returns:
            Success status
        """
        try:
            logger.info(
                f"Initializing Event Streaming Manager for {selfconfig/environments/development.environment.value}"
            )

            # Initialize Kafka infrastructure
            kafka_success = await self._initialize_kafka()

            # Initialize NATS infrastructure
            nats_success = await self._initialize_nats()

            # Update health status
            self.health_status = {
                "kafka_healthy": kafka_success,
                "nats_healthy": nats_success,
                "overall_healthy": (
                    kafka_success or nats_success
                ),  # At least one must work
            }

            if not self.health_status["overall_healthy"]:
                logger.error("Failed to initialize any streaming infrastructure")
                return False

            # Initialize circuit breakers
            await self._initialize_circuit_breakers()

            # Start health monitoring
            asyncio.create_task(self._health_monitor())

            # Start metrics collection
            asyncio.create_task(self._metrics_collector())

            self.running = True

            # Log initialization
            await self.audit_logger.log_streaming_event(
                {
                    "event_type": "streaming_manager_initialized",
                    "cluster_id": self.cluster_id,
                    "environment": selfconfig/environments/development.environment.value,
                    "kafka_healthy": kafka_success,
                    "nats_healthy": nats_success,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            logger.info("Event Streaming Manager initialized successfully")
            return True

        except Exception as e:
            logger.exception(f"Event Streaming Manager initialization failed: {e}")
            return False

    async def _initialize_kafka(self) -> bool:
        """Initialize Kafka producers and consumers"""
        try:
            # Get producer configuration
            producer_config = await self.config_manager.get_producer_config(
                self.cluster_id, selfconfig/environments/development.environment
            )

            # Initialize Kafka producer
            self.kafka_producers["main"] = KafkaProducer(producer_config)
            producer_success = await self.kafka_producers["main"].initialize()

            if not producer_success:
                logger.warning("Kafka producer initialization failed")
                return False

            # Initialize stream processor
            stream_config = {
                "window_size_ms": 60000,  # 1 minute
                "slide_interval_ms": 10000,  # 10 seconds
                "watermark_delay_ms": 5000,  # 5 seconds
            }
            self.kafka_stream_processors["main"] = KafkaStreamProcessor(stream_config)

            # Register default stream processors
            await self._register_stream_processors()

            logger.info("Kafka infrastructure initialized successfully")
            return True

        except Exception as e:
            logger.exception(f"Kafka initialization failed: {e}")
            return False

    async def _initialize_nats(self) -> bool:
        """Initialize NATS client"""
        if not NATS_AVAILABLE:
            logger.info("NATS not available, skipping NATS initialization")
            return False

        try:
            self.nats_client = nats.NATS()

            # NATS server configuration
            nats_servers = self.config.get("nats_servers", ["nats://localhost:4222"])

            await self.nats_client.connect(
                servers=nats_servers,
                reconnect_time_wait=5,
                max_reconnect_attempts=10,
                ping_interval=30,
                max_outstanding_pings=2,
            )

            logger.info("NATS client initialized successfully")
            return True

        except Exception as e:
            logger.exception(f"NATS initialization failed: {e}")
            return False

    async def _initialize_circuit_breakers(self):
        """Initialize circuit breakers for different event types"""
        for event_type in EventType:
            self.circuit_breakers[event_type] = {
                "state": "closed",  # closed, open, half_open
                "failure_count": 0,
                "failure_threshold": 5,
                "recovery_timeout": 60,  # seconds
                "last_failure": None,
                "last_success": datetime.utcnow(),
            }

    async def publish_event(self, event: StreamingEvent) -> bool:
        """
        Publish event to appropriate streaming infrastructure

        Args:
            event: Streaming event to publish

        Returns:
            Success status
        """
        start_time = datetime.utcnow()

        try:
            # Validate constitutional compliance
            if not await self._validate_event_compliance(event):
                self.metrics.constitutional_violations += 1
                await self._send_to_dlq(event, "constitutional_compliance_violation")
                return False

            # Check circuit breaker
            if not await self._check_circuit_breaker(event.event_type):
                self.metrics.circuit_breaker_trips += 1
                await self._send_to_dlq(event, "circuit_breaker_open")
                return False

            # Determine routing strategy
            routing_strategy = self._determine_routing_strategy(event)

            # Route event based on strategy
            success = False
            if routing_strategy == EventRoutingStrategy.KAFKA_ONLY:
                success = await self._publish_to_kafka(event)
            elif routing_strategy == EventRoutingStrategy.NATS_ONLY:
                success = await self._publish_to_nats(event)
            elif routing_strategy == EventRoutingStrategy.HYBRID:
                # Try both, succeed if either works
                kafka_success = await self._publish_to_kafka(event)
                nats_success = await self._publish_to_nats(event)
                success = kafka_success or nats_success
            elif routing_strategy == EventRoutingStrategy.ADAPTIVE:
                # Try primary, fallback to secondary
                success = await self._publish_adaptive(event)

            # Update metrics
            routing_latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            await self._update_publishing_metrics(success, routing_latency)

            # Update circuit breaker
            await self._update_circuit_breaker(event.event_type, success)

            if success:
                # Log successful event publication
                await self.audit_logger.log_streaming_event(
                    {
                        "event_type": "event_published",
                        "streaming_event_id": event.event_id,
                        "streaming_event_type": event.event_type.value,
                        "routing_strategy": routing_strategy.value,
                        "routing_latency_ms": routing_latency,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            else:
                # Handle publication failure
                await self._handle_publication_failure(event, "routing_failed")

            return success

        except Exception as e:
            logger.exception(f"Event publication failed: {e}")
            await self._handle_publication_failure(event, str(e))
            return False

    async def _publish_to_kafka(self, event: StreamingEvent) -> bool:
        """Publish event to Kafka"""
        try:
            if "main" not in self.kafka_producers:
                return False

            # Get topic mapping
            topic_mapping = self.topic_mappings.get(event.event_type)
            if not topic_mapping:
                logger.warning(f"No topic mapping for event type: {event.event_type}")
                return False

            # Prepare message
            message_value = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "priority": event.priority.value,
                "source_service": event.source_service,
                "target_service": event.target_service,
                "payload": event.payload,
                "metadata": event.metadata,
                "correlation_id": event.correlation_id,
                "timestamp": event.timestamp.isoformat(),
                "ttl_seconds": event.ttl_seconds,
                "constitutional_compliant": event.constitutional_compliant,
            }

            # Determine partition key
            partition_key = None
            if (
                topic_mapping.partitioning_key
                and topic_mapping.partitioning_key in event.payload
            ):
                partition_key = str(event.payload[topic_mapping.partitioning_key])
            else:
                partition_key = event.event_id

            # Publish to Kafka
            return await self.kafka_producers["main"].send_message(
                topic=topic_mapping.kafka_topic,
                value=message_value,
                key=partition_key,
                headers={
                    "event_type": event.event_type.value,
                    "priority": event.priority.value,
                },
            )

        except Exception as e:
            logger.exception(f"Kafka publication failed: {e}")
            return False

    async def _publish_to_nats(self, event: StreamingEvent) -> bool:
        """Publish event to NATS"""
        try:
            if not self.nats_client or not self.nats_client.is_connected:
                return False

            # Get topic mapping
            topic_mapping = self.topic_mappings.get(event.event_type)
            if not topic_mapping or not topic_mapping.nats_subject:
                return False

            # Prepare message
            message_data = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "priority": event.priority.value,
                "source_service": event.source_service,
                "target_service": event.target_service,
                "payload": event.payload,
                "metadata": event.metadata,
                "correlation_id": event.correlation_id,
                "timestamp": event.timestamp.isoformat(),
                "ttl_seconds": event.ttl_seconds,
                "constitutional_compliant": event.constitutional_compliant,
            }

            # Publish to NATS
            await self.nats_client.publish(
                topic_mapping.nats_subject,
                json.dumps(message_data, default=str).encode("utf-8"),
            )

            return True

        except Exception as e:
            logger.exception(f"NATS publication failed: {e}")
            return False

    async def _publish_adaptive(self, event: StreamingEvent) -> bool:
        """Adaptive publishing with intelligent fallback"""
        try:
            # Determine primary and secondary based on current health
            if (
                self.health_status["kafka_healthy"]
                and self.health_status["nats_healthy"]
            ):
                # Both healthy - choose based on event characteristics
                if event.priority in {EventPriority.CRITICAL, EventPriority.HIGH}:
                    primary, secondary = "kafka", "nats"
                else:
                    primary, secondary = "nats", "kafka"
            elif self.health_status["kafka_healthy"]:
                primary, secondary = "kafka", None
            elif self.health_status["nats_healthy"]:
                primary, secondary = "nats", None
            else:
                return False

            # Try primary
            if primary == "kafka":
                success = await self._publish_to_kafka(event)
            else:
                success = await self._publish_to_nats(event)

            if success or not secondary:
                return success

            # Try secondary
            if secondary == "kafka":
                return await self._publish_to_kafka(event)
            return await self._publish_to_nats(event)

        except Exception as e:
            logger.exception(f"Adaptive publishing failed: {e}")
            return False

    def _determine_routing_strategy(
        self, event: StreamingEvent
    ) -> EventRoutingStrategy:
        """Determine optimal routing strategy for event"""
        # Use event-specific strategy if set
        if event.routing_strategy != EventRoutingStrategy.ADAPTIVE:
            return event.routing_strategy

        # Adaptive strategy based on event characteristics
        if event.priority == EventPriority.CRITICAL:
            return EventRoutingStrategy.HYBRID  # Redundancy for critical events
        if event.event_type in {EventType.METRIC_EVENT, EventType.SYSTEM_EVENT}:
            return EventRoutingStrategy.NATS_ONLY  # Lightweight for metrics
        if event.event_type in {
            EventType.CONSTITUTIONAL_DECISION,
            EventType.AUDIT_EVENT,
        }:
            return EventRoutingStrategy.KAFKA_ONLY  # Durability for important events
        return self.default_routing_strategy

    async def subscribe_to_events(
        self,
        event_type: EventType,
        handler: Callable[[StreamingEvent], bool],
        group_id: str | None = None,
    ) -> bool:
        """
        Subscribe to events of a specific type

        Args:
            event_type: Type of events to subscribe to
            handler: Event handler function
            group_id: Consumer group ID (for Kafka)

        Returns:
            Success status
        """
        try:
            # Register event handler
            self.event_handlers[event_type] = handler

            # Get topic mapping
            topic_mapping = self.topic_mappings.get(event_type)
            if not topic_mapping:
                logger.error(f"No topic mapping for event type: {event_type}")
                return False

            # Subscribe to Kafka topic
            if self.health_status["kafka_healthy"]:
                await self._subscribe_kafka(event_type, topic_mapping, group_id)

            # Subscribe to NATS subject
            if self.health_status["nats_healthy"] and topic_mapping.nats_subject:
                await self._subscribe_nats(event_type, topic_mapping)

            logger.info(f"Subscribed to events of type: {event_type.value}")
            return True

        except Exception as e:
            logger.exception(f"Event subscription failed: {e}")
            return False

    async def _subscribe_kafka(
        self,
        event_type: EventType,
        topic_mapping: TopicMapping,
        group_id: str | None,
    ):
        """Subscribe to Kafka topic"""
        try:
            # Get consumer configuration
            consumer_group = group_id or f"acgs-{event_type.value}-group"
            consumer_config = await self.config_manager.get_consumer_config(
                self.cluster_id, selfconfig/environments/development.environment, consumer_group
            )
            consumer_config["topics"] = [topic_mapping.kafka_topic]

            # Create consumer
            consumer = KafkaConsumer(consumer_config)
            await consumer.initialize()

            # Set message handler
            async def kafka_message_handler(kafka_message: KafkaMessage) -> bool:
                try:
                    # Convert Kafka message to StreamingEvent
                    streaming_event = await self._kafka_message_to_streaming_event(
                        kafka_message
                    )

                    # Call user handler
                    handler = self.event_handlers.get(event_type)
                    if handler:
                        return await handler(streaming_event)
                    return True
                except Exception as e:
                    logger.exception(f"Kafka message handler failed: {e}")
                    return False

            consumer.set_message_handler(kafka_message_handler)

            # Store consumer
            self.kafka_consumers[event_type] = consumer

            # Start consuming in background
            asyncio.create_task(consumer.start_consuming())

        except Exception as e:
            logger.exception(f"Kafka subscription failed: {e}")

    async def _subscribe_nats(self, event_type: EventType, topic_mapping: TopicMapping):
        """Subscribe to NATS subject"""
        try:

            async def nats_message_handler(msg):
                try:
                    # Parse NATS message
                    message_data = json.loads(msg.data.decode("utf-8"))

                    # Convert to StreamingEvent
                    streaming_event = StreamingEvent(
                        event_id=message_data["event_id"],
                        event_type=EventType(message_data["event_type"]),
                        priority=EventPriority(message_data["priority"]),
                        source_service=message_data["source_service"],
                        target_service=message_data.get("target_service"),
                        payload=message_data["payload"],
                        metadata=message_data["metadata"],
                        routing_strategy=EventRoutingStrategy.NATS_ONLY,
                        constitutional_compliant=message_data.get(
                            "constitutional_compliant", True
                        ),
                        correlation_id=message_data.get("correlation_id"),
                        timestamp=datetime.fromisoformat(message_data["timestamp"]),
                        ttl_seconds=message_data.get("ttl_seconds"),
                    )

                    # Call user handler
                    handler = self.event_handlers.get(event_type)
                    if handler:
                        await handler(streaming_event)

                except Exception as e:
                    logger.exception(f"NATS message handler failed: {e}")

            # Subscribe to NATS subject
            await self.nats_client.subscribe(
                topic_mapping.nats_subject, cb=nats_message_handler
            )

        except Exception as e:
            logger.exception(f"NATS subscription failed: {e}")

    async def _kafka_message_to_streaming_event(
        self, kafka_message: KafkaMessage
    ) -> StreamingEvent:
        """Convert Kafka message to StreamingEvent"""
        message_value = kafka_message.value

        return StreamingEvent(
            event_id=message_value["event_id"],
            event_type=EventType(message_value["event_type"]),
            priority=EventPriority(message_value["priority"]),
            source_service=message_value["source_service"],
            target_service=message_value.get("target_service"),
            payload=message_value["payload"],
            metadata=message_value["metadata"],
            routing_strategy=EventRoutingStrategy.KAFKA_ONLY,
            constitutional_compliant=message_value.get(
                "constitutional_compliant", True
            ),
            correlation_id=message_value.get("correlation_id"),
            timestamp=datetime.fromisoformat(message_value["timestamp"]),
            ttl_seconds=message_value.get("ttl_seconds"),
        )

    async def _validate_event_compliance(self, event: StreamingEvent) -> bool:
        """Validate event for constitutional compliance"""
        try:
            # Check for sensitive data in payload
            payload_str = json.dumps(event.payload, default=str).lower()

            sensitive_patterns = [
                "password",
                "ssn",
                "social_security",
                "credit_card",
                "api_key",
                "secret",
                "token",
                "private_key",
            ]

            has_sensitive_data = any(
                pattern in payload_str for pattern in sensitive_patterns
            )
            if has_sensitive_data:
                logger.warning(f"Event contains sensitive data: {event.event_id}")
                return False

            # Check event metadata for compliance markers
            if event.metadata.get("compliance_required", False):
                if not event.metadata.get("compliance_validated", False):
                    logger.warning(
                        f"Event requires compliance validation: {event.event_id}"
                    )
                    return False

            # Validate TTL
            if event.ttl_seconds and event.ttl_seconds < 60:  # Minimum 1 minute
                logger.warning(f"Event TTL too short: {event.event_id}")
                return False

            return True

        except Exception as e:
            logger.exception(f"Event compliance validation failed: {e}")
            return False

    async def _check_circuit_breaker(self, event_type: EventType) -> bool:
        """Check circuit breaker state for event type"""
        try:
            breaker = self.circuit_breakers.get(event_type)
            if not breaker:
                return True

            current_time = datetime.utcnow()

            if breaker["state"] == "closed":
                return True
            if breaker["state"] == "open":
                # Check if recovery timeout has passed
                if breaker["last_failure"]:
                    time_since_failure = (
                        current_time - breaker["last_failure"]
                    ).total_seconds()
                    if time_since_failure >= breaker["recovery_timeout"]:
                        breaker["state"] = "half_open"
                        return True
                return False
            return breaker["state"] == "half_open"

        except Exception as e:
            logger.exception(f"Circuit breaker check failed: {e}")
            return True  # Fail open

    async def _update_circuit_breaker(self, event_type: EventType, success: bool):
        """Update circuit breaker state based on operation result"""
        try:
            breaker = self.circuit_breakers.get(event_type)
            if not breaker:
                return

            current_time = datetime.utcnow()

            if success:
                breaker["failure_count"] = 0
                breaker["last_success"] = current_time
                if breaker["state"] == "half_open":
                    breaker["state"] = "closed"
            else:
                breaker["failure_count"] += 1
                breaker["last_failure"] = current_time

                if breaker["failure_count"] >= breaker["failure_threshold"]:
                    breaker["state"] = "open"

                    # Send alert
                    await self.alerting.send_alert(
                        f"circuit_breaker_open_{event_type.value}",
                        f"Circuit breaker opened for {event_type.value} after"
                        f" {breaker['failure_count']} failures",
                        severity="high",
                    )

        except Exception as e:
            logger.exception(f"Circuit breaker update failed: {e}")

    async def _send_to_dlq(self, event: StreamingEvent, reason: str):
        """Send failed event to dead letter queue"""
        try:
            dlq_event = {
                "original_event": asdict(event),
                "failure_reason": reason,
                "failed_at": datetime.utcnow().isoformat(),
                "retry_count": event.metadata.get("retry_count", 0) + 1,
            }

            # Send to DLQ topic
            if "main" in self.kafka_producers:
                await self.kafka_producers["main"].send_message(
                    topic="dead-letter-queue",
                    value=dlq_event,
                    key=f"dlq_{event.event_id}",
                )

            self.metrics.events_in_dlq += 1

        except Exception as e:
            logger.exception(f"Failed to send event to DLQ: {e}")

    async def _handle_publication_failure(self, event: StreamingEvent, error: str):
        """Handle event publication failure"""
        self.metrics.events_failed += 1
        await self._send_to_dlq(event, error)

        # Log failure
        await self.audit_logger.log_streaming_event(
            {
                "event_type": "event_publication_failed",
                "streaming_event_id": event.event_id,
                "streaming_event_type": event.event_type.value,
                "error": error,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    async def _update_publishing_metrics(
        self, success: bool, routing_latency_ms: float
    ):
        """Update publishing metrics"""
        self.metrics.total_events_sent += 1

        if success:
            # Update rolling average routing latency
            total_events = self.metrics.total_events_sent
            current_avg = self.metrics.avg_routing_latency_ms
            self.metrics.avg_routing_latency_ms = (
                current_avg * (total_events - 1) + routing_latency_ms
            ) / total_events

    async def _register_stream_processors(self):
        """Register default stream processors"""
        try:
            # Register constitutional compliance validator
            async def compliance_processor(
                messages: list[KafkaMessage], window_id: str
            ):
                violations = 0
                for message in messages:
                    if not message.constitutional_compliant:
                        violations += 1

                if violations > len(messages) * 0.1:  # 10% violation threshold
                    await self.alerting.send_alert(
                        "high_constitutional_violations",
                        f"High constitutional violation rate in window {window_id}:"
                        f" {violations}/{len(messages)}",
                        severity="high",
                    )

            self.kafka_stream_processors["main"].register_processor(
                "compliance_validator", compliance_processor
            )

            # Register performance monitor
            async def performance_processor(
                messages: list[KafkaMessage], window_id: str
            ):
                if len(messages) > 1000:  # High throughput window
                    logger.info(
                        f"High throughput window {window_id}: {len(messages)} messages"
                    )

            self.kafka_stream_processors["main"].register_processor(
                "performance_monitor", performance_processor
            )

        except Exception as e:
            logger.exception(f"Stream processor registration failed: {e}")

    async def _health_monitor(self):
        """Monitor health of streaming infrastructure"""
        while self.running:
            try:
                # Check Kafka health
                if "main" in self.kafka_producers:
                    kafka_healthy = await self.config_manager.test_connection(
                        self.cluster_id, selfconfig/environments/development.environment
                    )
                    self.health_status["kafka_healthy"] = kafka_healthy

                # Check NATS health
                if self.nats_client:
                    nats_healthy = self.nats_client.is_connected
                    self.health_status["nats_healthy"] = nats_healthy

                # Update overall health
                self.health_status["overall_healthy"] = (
                    self.health_status["kafka_healthy"]
                    or self.health_status["nats_healthy"]
                )

                # Alert on health issues
                if not self.health_status["overall_healthy"]:
                    await self.alerting.send_alert(
                        "streaming_infrastructure_unhealthy",
                        "All streaming infrastructure is unhealthy",
                        severity="critical",
                    )

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.exception(f"Health monitoring failed: {e}")
                await asyncio.sleep(60)  # Longer sleep on error

    async def _metrics_collector(self):
        """Collect and report streaming metrics"""
        while self.running:
            try:
                # Calculate throughput
                time_elapsed = (
                    datetime.utcnow() - self.metrics.last_reset
                ).total_seconds()
                if time_elapsed > 0:
                    total_events = (
                        self.metrics.total_events_sent
                        + self.metrics.total_events_received
                    )
                    overall_throughput = total_events / time_elapsed

                    # Update individual throughputs (simplified calculation)
                    self.metrics.kafka_throughput_msgs_per_sec = (
                        overall_throughput * 0.7
                    )  # Assume 70% Kafka
                    self.metrics.nats_throughput_msgs_per_sec = (
                        overall_throughput * 0.3
                    )  # Assume 30% NATS

                # Log metrics periodically
                if time_elapsed > 300:  # Every 5 minutes
                    await self.audit_logger.log_streaming_event(
                        {
                            "event_type": "streaming_metrics",
                            "metrics": asdict(self.metrics),
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

                    # Reset metrics for next period
                    self.metrics.last_reset = datetime.utcnow()

                await asyncio.sleep(60)  # Collect every minute

            except Exception as e:
                logger.exception(f"Metrics collection failed: {e}")
                await asyncio.sleep(120)  # Longer sleep on error

    async def shutdown(self):
        """Gracefully shutdown the streaming manager"""
        try:
            logger.info("Shutting down Event Streaming Manager")
            self.running = False

            # Stop consumers
            for consumer in self.kafka_consumers.values():
                await consumer.stop_consuming()
                await consumer.close()

            # Flush and close producers
            for producer in self.kafka_producers.values():
                await producer.flush()
                await producer.close()

            # Close NATS connection
            if self.nats_client and self.nats_client.is_connected:
                await self.nats_client.close()

            # Stop stream processors
            for processor in self.kafka_stream_processors.values():
                await processor.stop_processing()

            logger.info("Event Streaming Manager shutdown complete")

        except Exception as e:
            logger.exception(f"Shutdown failed: {e}")

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get comprehensive metrics summary"""
        return {
            "streaming_metrics": asdict(self.metrics),
            "health_status": self.health_status,
            "circuit_breaker_status": {
                event_type.value: breaker["state"]
                for event_type, breaker in self.circuit_breakers.items()
            },
            "active_producers": len(self.kafka_producers),
            "active_consumers": len(self.kafka_consumers),
            "active_processors": len(self.kafka_stream_processors),
            "topic_mappings": len(self.topic_mappings),
            "event_handlers": len(self.event_handlers),
        }


# Example usage
async def example_usage():
    """Example of how to use the Event Streaming Manager"""
    # Initialize streaming manager
    config = {
        "cluster_id": "acgs-main",
        "environment": "development",
        "default_routing_strategy": "hybrid",
    }

    streaming_manager = EventStreamingManager(config)

    # Initialize
    success = await streaming_manager.initialize()
    if not success:
        return

    # Define event handler
    async def governance_event_handler(event: StreamingEvent) -> bool:
        return True

    # Subscribe to events
    await streaming_manager.subscribe_to_events(
        EventType.GOVERNANCE_ACTION, governance_event_handler
    )

    # Publish test event
    test_event = StreamingEvent(
        event_id=str(uuid.uuid4()),
        event_type=EventType.GOVERNANCE_ACTION,
        priority=EventPriority.MEDIUM,
        source_service="test-service",
        target_service=None,
        payload={"action": "test_action", "value": 42},
        metadata={"test": True},
        routing_strategy=EventRoutingStrategy.HYBRID,
        constitutional_compliant=True,
        correlation_id=None,
        timestamp=datetime.utcnow(),
    )

    await streaming_manager.publish_event(test_event)

    # Wait for processing
    await asyncio.sleep(5)

    # Get metrics
    streaming_manager.get_metrics_summary()

    # Shutdown
    await streaming_manager.shutdown()


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
