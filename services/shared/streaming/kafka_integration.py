"""
Apache Kafka Integration

Production-ready Kafka integration for enterprise-scale event streaming,
implementing the ACGE technical validation recommendations for replacing
plugin-based asyncio with enterprise streaming architecture.

Key Features:
- High-performance Kafka producers and consumers
- Automatic retry and error handling mechanisms
- Message serialization and compression
- Dead letter queue support
- Integration with existing ACGS monitoring systems
- Constitutional compliance for message processing
"""

import asyncio
import json
import logging
import pickle
import uuid
from collections.abc import AsyncGenerator, Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional, Union

# Kafka imports (would be installed via pip install kafka-python-ng or confluent-kafka)
try:
    from kafka import KafkaConsumer as PyKafkaConsumer
    from kafka import KafkaProducer as PyKafkaProducer
    from kafka.errors import KafkaError, KafkaTimeoutError
    from kafka.structs import TopicPartition

    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    logging.warning("Kafka not available, using fallback implementations")

from services.shared.monitoring.intelligent_alerting_system import IntelligentAlertingSystem
from services.shared.security.enhanced_audit_logging import EnhancedAuditLogger

logger = logging.getLogger(__name__)


class MessageFormat(Enum):
    """Message serialization formats"""

    JSON = "json"
    PICKLE = "pickle"
    AVRO = "avro"
    PROTOBUF = "protobuf"


class CompressionType(Enum):
    """Message compression types"""

    NONE = "none"
    GZIP = "gzip"
    SNAPPY = "snappy"
    LZ4 = "lz4"
    ZSTD = "zstd"


class DeliveryGuarantee(Enum):
    """Message delivery guarantees"""

    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


@dataclass
class KafkaMessage:
    """Kafka message structure"""

    topic: str
    key: Optional[str]
    value: Any
    headers: Optional[dict[str, str]]
    partition: Optional[int]
    offset: Optional[int]
    timestamp: Optional[datetime]
    message_id: str
    constitutional_compliant: bool = True


@dataclass
class ProducerMetrics:
    """Producer performance metrics"""

    messages_sent: int
    messages_failed: int
    total_bytes_sent: int
    avg_latency_ms: float
    error_rate: float
    throughput_msgs_per_sec: float
    last_reset: datetime


@dataclass
class ConsumerMetrics:
    """Consumer performance metrics"""

    messages_consumed: int
    messages_processed: int
    messages_failed: int
    processing_lag_ms: float
    error_rate: float
    throughput_msgs_per_sec: float
    last_reset: datetime


class KafkaProducer:
    """
    High-performance Kafka producer with enterprise features
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.alerting = IntelligentAlertingSystem()
        self.audit_logger = EnhancedAuditLogger()

        # Producer configuration
        self.bootstrap_servers = config.get("bootstrap_servers", ["localhost:9092"])
        self.message_format = MessageFormat(config.get("message_format", "json"))
        self.compression_type = CompressionType(config.get("compression_type", "gzip"))
        self.delivery_guarantee = DeliveryGuarantee(
            config.get("delivery_guarantee", "at_least_once")
        )

        # Performance configuration
        self.batch_size = config.get("batch_size", 16384)
        self.linger_ms = config.get("linger_ms", 5)
        self.buffer_memory = config.get("buffer_memory", 33554432)  # 32MB
        self.max_request_size = config.get("max_request_size", 1048576)  # 1MB
        self.retry_backoff_ms = config.get("retry_backoff_ms", 100)
        self.request_timeout_ms = config.get("request_timeout_ms", 30000)

        # Constitutional compliance
        self.constitutional_validation_enabled = config.get(
            "constitutional_validation", True
        )
        self.constitutional_principles = config.get(
            "constitutional_principles",
            ["data_minimization", "purpose_limitation", "transparency"],
        )

        # Producer instance and metrics
        self.producer = None
        self.metrics = ProducerMetrics(
            messages_sent=0,
            messages_failed=0,
            total_bytes_sent=0,
            avg_latency_ms=0.0,
            error_rate=0.0,
            throughput_msgs_per_sec=0.0,
            last_reset=datetime.utcnow(),
        )

        # Dead letter queue configuration
        self.dlq_enabled = config.get("dlq_enabled", True)
        self.dlq_topic = config.get("dlq_topic", "dead-letter-queue")

    async def initialize(self) -> bool:
        """Initialize Kafka producer"""
        if not KAFKA_AVAILABLE:
            logger.warning("Kafka not available, using fallback producer")
            return await self._initialize_fallback()

        try:
            # Configure producer settings
            producer_config = {
                "bootstrap_servers": self.bootstrap_servers,
                "batch_size": self.batch_size,
                "linger_ms": self.linger_ms,
                "buffer_memory": self.buffer_memory,
                "max_request_size": self.max_request_size,
                "retry_backoff_ms": self.retry_backoff_ms,
                "request_timeout_ms": self.request_timeout_ms,
                "value_serializer": self._get_serializer(),
                "key_serializer": lambda x: x.encode("utf-8") if x else None,
                "compression_type": self._get_compression_type(),
                "acks": self._get_acks_config(),
                "retries": 3,
                "max_in_flight_requests_per_connection": (
                    1
                    if self.delivery_guarantee == DeliveryGuarantee.EXACTLY_ONCE
                    else 5
                ),
            }

            # Add security configuration if available
            security_config = self.config.get("security", {})
            if security_config:
                producer_config.update(security_config)

            self.producer = PyKafkaProducer(**producer_config)

            logger.info("Kafka producer initialized successfully")

            # Log initialization
            await self.audit_logger.log_streaming_event({
                "event_type": "kafka_producer_initialized",
                "bootstrap_servers": self.bootstrap_servers,
                "delivery_guarantee": self.delivery_guarantee.value,
                "compression_type": self.compression_type.value,
                "timestamp": datetime.utcnow().isoformat(),
            })

            return True

        except Exception as e:
            logger.error(f"Kafka producer initialization failed: {e}")
            return await self._initialize_fallback()

    async def _initialize_fallback(self) -> bool:
        """Initialize fallback producer when Kafka is unavailable"""
        try:
            self.producer = FallbackProducer()
            logger.info("Fallback producer initialized")
            return True
        except Exception as e:
            logger.error(f"Fallback producer initialization failed: {e}")
            return False

    def _get_serializer(self) -> Callable:
        """Get appropriate message serializer"""
        if self.message_format == MessageFormat.JSON:
            return lambda x: json.dumps(x, default=str).encode("utf-8")
        elif self.message_format == MessageFormat.PICKLE:
            return pickle.dumps
        else:
            return lambda x: str(x).encode("utf-8")

    def _get_compression_type(self) -> Optional[str]:
        """Get Kafka compression type"""
        compression_map = {
            CompressionType.NONE: None,
            CompressionType.GZIP: "gzip",
            CompressionType.SNAPPY: "snappy",
            CompressionType.LZ4: "lz4",
            CompressionType.ZSTD: "zstd",
        }
        return compression_map.get(self.compression_type)

    def _get_acks_config(self) -> Union[str, int]:
        """Get acknowledgment configuration"""
        if self.delivery_guarantee == DeliveryGuarantee.AT_MOST_ONCE:
            return 0
        elif self.delivery_guarantee == DeliveryGuarantee.AT_LEAST_ONCE:
            return 1
        else:  # EXACTLY_ONCE
            return "all"

    async def validate_constitutional_compliance(self, message: KafkaMessage) -> bool:
        """Validate message for constitutional compliance"""
        if not self.constitutional_validation_enabled:
            return True

        try:
            # Check for sensitive data
            message_str = json.dumps(message.value, default=str).lower()

            # Basic checks for sensitive information
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
                pattern in message_str for pattern in sensitive_patterns
            )

            if has_sensitive_data:
                logger.warning(
                    f"Message contains potentially sensitive data: {message.message_id}"
                )
                return False

            # Check message size for data minimization
            message_size = len(json.dumps(message.value, default=str))
            if message_size > self.max_request_size:
                logger.warning(f"Message exceeds size limit: {message.message_id}")
                return False

            return True

        except Exception as e:
            logger.error(f"Constitutional compliance validation failed: {e}")
            return False

    async def send_message(
        self,
        topic: str,
        value: Any,
        key: Optional[str] = None,
        headers: Optional[dict[str, str]] = None,
        partition: Optional[int] = None,
    ) -> bool:
        """
        Send message to Kafka topic

        Args:
            topic: Kafka topic name
            value: Message value
            key: Optional message key
            headers: Optional message headers
            partition: Optional specific partition

        Returns:
            Success status
        """
        start_time = datetime.utcnow()
        message_id = str(uuid.uuid4())

        try:
            # Create message object
            message = KafkaMessage(
                topic=topic,
                key=key,
                value=value,
                headers=headers,
                partition=partition,
                offset=None,
                timestamp=start_time,
                message_id=message_id,
            )

            # Validate constitutional compliance
            if not await self.validate_constitutional_compliance(message):
                message.constitutional_compliant = False
                await self._send_to_dlq(message, "constitutional_compliance_violation")
                return False

            # Send message
            if KAFKA_AVAILABLE and hasattr(self.producer, "send"):
                future = self.producer.send(
                    topic=topic,
                    value=value,
                    key=key,
                    headers=headers,
                    partition=partition,
                )

                # Get result with timeout
                record_metadata = future.get(timeout=self.request_timeout_ms / 1000)

                # Update message with metadata
                message.partition = record_metadata.partition
                message.offset = record_metadata.offset

            else:
                # Fallback producer
                await self.producer.send(topic, value, key, headers)

            # Update metrics
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            await self._update_producer_metrics(
                True, latency, len(json.dumps(value, default=str))
            )

            # Log successful send
            await self.audit_logger.log_streaming_event({
                "event_type": "message_sent",
                "topic": topic,
                "message_id": message_id,
                "partition": message.partition,
                "offset": message.offset,
                "latency_ms": latency,
                "timestamp": datetime.utcnow().isoformat(),
            })

            return True

        except KafkaTimeoutError as e:
            logger.warning(f"Kafka timeout sending message {message_id}: {e}")
            await self._handle_send_failure(message, str(e))
            return False

        except KafkaError as e:
            logger.error(f"Kafka error sending message {message_id}: {e}")
            await self._handle_send_failure(message, str(e))
            return False

        except Exception as e:
            logger.error(f"Unexpected error sending message {message_id}: {e}")
            await self._handle_send_failure(message, str(e))
            return False

    async def send_batch(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Send batch of messages efficiently

        Args:
            messages: List of message dictionaries with 'topic', 'value', optional 'key', 'headers'

        Returns:
            Batch result summary
        """
        start_time = datetime.utcnow()
        successful_sends = 0
        failed_sends = 0

        try:
            send_tasks = []

            for msg_dict in messages:
                task = self.send_message(
                    topic=msg_dict["topic"],
                    value=msg_dict["value"],
                    key=msg_dict.get("key"),
                    headers=msg_dict.get("headers"),
                    partition=msg_dict.get("partition"),
                )
                send_tasks.append(task)

            # Execute batch with concurrency limit
            results = await asyncio.gather(*send_tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    failed_sends += 1
                elif result:
                    successful_sends += 1
                else:
                    failed_sends += 1

            total_time = (datetime.utcnow() - start_time).total_seconds()

            # Log batch result
            await self.audit_logger.log_streaming_event({
                "event_type": "batch_sent",
                "total_messages": len(messages),
                "successful_sends": successful_sends,
                "failed_sends": failed_sends,
                "batch_time_seconds": total_time,
                "timestamp": datetime.utcnow().isoformat(),
            })

            return {
                "total_messages": len(messages),
                "successful_sends": successful_sends,
                "failed_sends": failed_sends,
                "success_rate": successful_sends / len(messages) if messages else 0,
                "batch_time_seconds": total_time,
            }

        except Exception as e:
            logger.error(f"Batch send failed: {e}")
            return {
                "total_messages": len(messages),
                "successful_sends": 0,
                "failed_sends": len(messages),
                "success_rate": 0.0,
                "error": str(e),
            }

    async def _send_to_dlq(self, message: KafkaMessage, reason: str):
        """Send failed message to dead letter queue"""
        if not self.dlq_enabled:
            return

        try:
            dlq_message = {
                "original_topic": message.topic,
                "original_message": message.value,
                "failure_reason": reason,
                "message_id": message.message_id,
                "timestamp": message.timestamp.isoformat(),
                "constitutional_compliant": message.constitutional_compliant,
            }

            await self.send_message(
                self.dlq_topic, dlq_message, key=f"dlq_{message.message_id}"
            )

        except Exception as e:
            logger.error(f"Failed to send message to DLQ: {e}")

    async def _handle_send_failure(self, message: KafkaMessage, error: str):
        """Handle message send failure"""
        await self._update_producer_metrics(False, 0, 0)
        await self._send_to_dlq(message, error)

        # Send alert for high error rates
        if self.metrics.error_rate > 0.1:  # 10% error rate threshold
            await self.alerting.send_alert(
                "high_kafka_producer_error_rate",
                f"Producer error rate: {self.metrics.error_rate:.2%}",
                severity="high",
            )

    async def _update_producer_metrics(
        self, success: bool, latency_ms: float, message_size: int
    ):
        """Update producer performance metrics"""
        if success:
            self.metrics.messages_sent += 1
            self.metrics.total_bytes_sent += message_size

            # Update rolling average latency
            total_messages = self.metrics.messages_sent
            current_avg = self.metrics.avg_latency_ms
            self.metrics.avg_latency_ms = (
                current_avg * (total_messages - 1) + latency_ms
            ) / total_messages
        else:
            self.metrics.messages_failed += 1

        # Calculate error rate
        total_attempts = self.metrics.messages_sent + self.metrics.messages_failed
        self.metrics.error_rate = self.metrics.messages_failed / max(1, total_attempts)

        # Calculate throughput
        time_elapsed = (datetime.utcnow() - self.metrics.last_reset).total_seconds()
        if time_elapsed > 0:
            self.metrics.throughput_msgs_per_sec = total_attempts / time_elapsed

    async def flush(self, timeout: Optional[float] = None) -> bool:
        """Flush pending messages"""
        try:
            if KAFKA_AVAILABLE and hasattr(self.producer, "flush"):
                self.producer.flush(timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"Producer flush failed: {e}")
            return False

    async def close(self):
        """Close producer connection"""
        try:
            if self.producer and hasattr(self.producer, "close"):
                self.producer.close()
            logger.info("Kafka producer closed successfully")
        except Exception as e:
            logger.error(f"Error closing Kafka producer: {e}")

    def get_metrics(self) -> dict[str, Any]:
        """Get producer performance metrics"""
        return asdict(self.metrics)


class KafkaConsumer:
    """
    High-performance Kafka consumer with enterprise features
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.alerting = IntelligentAlertingSystem()
        self.audit_logger = EnhancedAuditLogger()

        # Consumer configuration
        self.bootstrap_servers = config.get("bootstrap_servers", ["localhost:9092"])
        self.group_id = config.get("group_id", "acgs-consumer-group")
        self.topics = config.get("topics", [])
        self.auto_offset_reset = config.get("auto_offset_reset", "latest")
        self.enable_auto_commit = config.get("enable_auto_commit", False)
        self.max_poll_records = config.get("max_poll_records", 500)
        self.session_timeout_ms = config.get("session_timeout_ms", 30000)
        self.heartbeat_interval_ms = config.get("heartbeat_interval_ms", 3000)

        # Message processing
        self.message_format = MessageFormat(config.get("message_format", "json"))
        self.max_processing_time_ms = config.get("max_processing_time_ms", 30000)
        self.constitutional_validation_enabled = config.get(
            "constitutional_validation", True
        )

        # Consumer instance and metrics
        self.consumer = None
        self.metrics = ConsumerMetrics(
            messages_consumed=0,
            messages_processed=0,
            messages_failed=0,
            processing_lag_ms=0.0,
            error_rate=0.0,
            throughput_msgs_per_sec=0.0,
            last_reset=datetime.utcnow(),
        )

        self.running = False
        self.message_handler = None

    async def initialize(self) -> bool:
        """Initialize Kafka consumer"""
        if not KAFKA_AVAILABLE:
            logger.warning("Kafka not available, using fallback consumer")
            return await self._initialize_fallback()

        try:
            # Configure consumer settings
            consumer_config = {
                "bootstrap_servers": self.bootstrap_servers,
                "group_id": self.group_id,
                "auto_offset_reset": self.auto_offset_reset,
                "enable_auto_commit": self.enable_auto_commit,
                "max_poll_records": self.max_poll_records,
                "session_timeout_ms": self.session_timeout_ms,
                "heartbeat_interval_ms": self.heartbeat_interval_ms,
                "value_deserializer": self._get_deserializer(),
                "key_deserializer": lambda x: x.decode("utf-8") if x else None,
            }

            # Add security configuration if available
            security_config = self.config.get("security", {})
            if security_config:
                consumer_config.update(security_config)

            self.consumer = PyKafkaConsumer(*self.topics, **consumer_config)

            logger.info(f"Kafka consumer initialized for topics: {self.topics}")

            # Log initialization
            await self.audit_logger.log_streaming_event({
                "event_type": "kafka_consumer_initialized",
                "group_id": self.group_id,
                "topics": self.topics,
                "bootstrap_servers": self.bootstrap_servers,
                "timestamp": datetime.utcnow().isoformat(),
            })

            return True

        except Exception as e:
            logger.error(f"Kafka consumer initialization failed: {e}")
            return await self._initialize_fallback()

    async def _initialize_fallback(self) -> bool:
        """Initialize fallback consumer when Kafka is unavailable"""
        try:
            self.consumer = FallbackConsumer(self.topics)
            logger.info("Fallback consumer initialized")
            return True
        except Exception as e:
            logger.error(f"Fallback consumer initialization failed: {e}")
            return False

    def _get_deserializer(self) -> Callable:
        """Get appropriate message deserializer"""
        if self.message_format == MessageFormat.JSON:
            return lambda x: json.loads(x.decode("utf-8")) if x else None
        elif self.message_format == MessageFormat.PICKLE:
            return lambda x: pickle.loads(x) if x else None
        else:
            return lambda x: x.decode("utf-8") if x else None

    def set_message_handler(self, handler: Callable[[KafkaMessage], bool]):
        """Set message processing handler"""
        self.message_handler = handler

    async def start_consuming(self):
        """Start consuming messages"""
        if not self.consumer:
            raise RuntimeError("Consumer not initialized")

        if not self.message_handler:
            raise RuntimeError("Message handler not set")

        self.running = True
        logger.info("Starting Kafka message consumption")

        try:
            while self.running:
                if KAFKA_AVAILABLE and hasattr(self.consumer, "poll"):
                    # Kafka consumer
                    message_batch = self.consumer.poll(timeout_ms=1000)

                    for topic_partition, messages in message_batch.items():
                        for message in messages:
                            await self._process_message(message, topic_partition)
                else:
                    # Fallback consumer
                    async for message in self.consumer.consume():
                        await self._process_message(message, None)

                await asyncio.sleep(0.01)  # Prevent tight loop

        except Exception as e:
            logger.error(f"Consumer error: {e}")
            await self.alerting.send_alert(
                "kafka_consumer_error", f"Consumer failed: {e!s}", severity="high"
            )
        finally:
            self.running = False

    async def _process_message(self, raw_message: Any, topic_partition: Optional[Any]):
        """Process individual message"""
        start_time = datetime.utcnow()

        try:
            # Convert to KafkaMessage format
            if KAFKA_AVAILABLE and hasattr(raw_message, "topic"):
                kafka_message = KafkaMessage(
                    topic=raw_message.topic,
                    key=raw_message.key,
                    value=raw_message.value,
                    headers=dict(raw_message.headers) if raw_message.headers else None,
                    partition=raw_message.partition,
                    offset=raw_message.offset,
                    timestamp=(
                        datetime.fromtimestamp(raw_message.timestamp / 1000)
                        if raw_message.timestamp
                        else start_time
                    ),
                    message_id=f"{raw_message.topic}_{raw_message.partition}_{raw_message.offset}",
                )
            else:
                # Fallback message format
                kafka_message = KafkaMessage(
                    topic=raw_message.get("topic", "unknown"),
                    key=raw_message.get("key"),
                    value=raw_message.get("value"),
                    headers=raw_message.get("headers"),
                    partition=raw_message.get("partition"),
                    offset=raw_message.get("offset"),
                    timestamp=start_time,
                    message_id=str(uuid.uuid4()),
                )

            # Constitutional compliance validation
            if self.constitutional_validation_enabled:
                kafka_message.constitutional_compliant = (
                    await self._validate_message_compliance(kafka_message)
                )

            # Process message with handler
            success = await self._call_message_handler(kafka_message)

            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            await self._update_consumer_metrics(success, processing_time)

            # Commit offset if auto-commit is disabled
            if not self.enable_auto_commit and success and KAFKA_AVAILABLE:
                try:
                    self.consumer.commit()
                except Exception as e:
                    logger.warning(f"Offset commit failed: {e}")

            # Log processing
            await self.audit_logger.log_streaming_event({
                "event_type": "message_processed",
                "topic": kafka_message.topic,
                "message_id": kafka_message.message_id,
                "processing_time_ms": processing_time,
                "success": success,
                "constitutional_compliant": kafka_message.constitutional_compliant,
                "timestamp": datetime.utcnow().isoformat(),
            })

        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            await self._update_consumer_metrics(False, 0)

    async def _validate_message_compliance(self, message: KafkaMessage) -> bool:
        """Validate message for constitutional compliance"""
        try:
            # Basic compliance checks
            if not message.value:
                return False

            # Check for proper message structure
            if not message.topic or not message.message_id:
                return False

            # Check timestamp validity
            if message.timestamp and (datetime.utcnow() - message.timestamp).days > 30:
                logger.warning(f"Message timestamp too old: {message.message_id}")
                return False

            return True

        except Exception as e:
            logger.error(f"Message compliance validation failed: {e}")
            return False

    async def _call_message_handler(self, message: KafkaMessage) -> bool:
        """Call user-defined message handler with timeout"""
        try:
            # Execute handler with timeout
            return await asyncio.wait_for(
                self.message_handler(message),
                timeout=self.max_processing_time_ms / 1000,
            )
        except asyncio.TimeoutError:
            logger.warning(f"Message handler timeout: {message.message_id}")
            return False
        except Exception as e:
            logger.error(f"Message handler error: {e}")
            return False

    async def _update_consumer_metrics(self, success: bool, processing_time_ms: float):
        """Update consumer performance metrics"""
        self.metrics.messages_consumed += 1

        if success:
            self.metrics.messages_processed += 1

            # Update rolling average processing lag
            total_processed = self.metrics.messages_processed
            current_avg = self.metrics.processing_lag_ms
            self.metrics.processing_lag_ms = (
                current_avg * (total_processed - 1) + processing_time_ms
            ) / total_processed
        else:
            self.metrics.messages_failed += 1

        # Calculate error rate
        self.metrics.error_rate = self.metrics.messages_failed / max(
            1, self.metrics.messages_consumed
        )

        # Calculate throughput
        time_elapsed = (datetime.utcnow() - self.metrics.last_reset).total_seconds()
        if time_elapsed > 0:
            self.metrics.throughput_msgs_per_sec = (
                self.metrics.messages_consumed / time_elapsed
            )

    async def stop_consuming(self):
        """Stop consuming messages"""
        self.running = False
        logger.info("Kafka consumer stopped")

    async def close(self):
        """Close consumer connection"""
        try:
            self.running = False
            if self.consumer and hasattr(self.consumer, "close"):
                self.consumer.close()
            logger.info("Kafka consumer closed successfully")
        except Exception as e:
            logger.error(f"Error closing Kafka consumer: {e}")

    def get_metrics(self) -> dict[str, Any]:
        """Get consumer performance metrics"""
        return asdict(self.metrics)


class KafkaStreamProcessor:
    """
    Stream processing engine for real-time data processing
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.alerting = IntelligentAlertingSystem()
        self.audit_logger = EnhancedAuditLogger()

        # Stream processing configuration
        self.window_size_ms = config.get("window_size_ms", 60000)  # 1 minute
        self.slide_interval_ms = config.get("slide_interval_ms", 10000)  # 10 seconds
        self.watermark_delay_ms = config.get("watermark_delay_ms", 5000)  # 5 seconds

        # Processing state
        self.windows = {}
        self.processors = {}
        self.running = False

    def register_processor(self, name: str, processor_func: Callable):
        """Register a stream processor function"""
        self.processors[name] = processor_func

    async def start_processing(self):
        """Start stream processing"""
        self.running = True
        logger.info("Starting stream processing")

        # Start window management
        asyncio.create_task(self._manage_windows())

    async def _manage_windows(self):
        """Manage sliding windows for stream processing"""
        while self.running:
            try:
                current_time = datetime.utcnow()

                # Clean up expired windows
                cutoff_time = current_time - timedelta(
                    milliseconds=self.window_size_ms * 2
                )
                expired_windows = [
                    window_id
                    for window_id, window in self.windows.items()
                    if window["end_time"] < cutoff_time
                ]

                for window_id in expired_windows:
                    del self.windows[window_id]

                await asyncio.sleep(self.slide_interval_ms / 1000)

            except Exception as e:
                logger.error(f"Window management error: {e}")

    async def process_stream_message(self, message: KafkaMessage) -> bool:
        """Process message in streaming context"""
        try:
            # Determine window for message
            window_id = self._get_window_id(message.timestamp or datetime.utcnow())

            # Add message to window
            if window_id not in self.windows:
                self.windows[window_id] = {
                    "messages": [],
                    "start_time": message.timestamp,
                    "end_time": message.timestamp + timedelta(
                        milliseconds=self.window_size_ms
                    ),
                }

            self.windows[window_id]["messages"].append(message)

            # Process window if ready
            if self._is_window_ready(window_id):
                await self._process_window(window_id)

            return True

        except Exception as e:
            logger.error(f"Stream message processing failed: {e}")
            return False

    def _get_window_id(self, timestamp: datetime) -> str:
        """Get window ID for timestamp"""
        window_start = timestamp.replace(microsecond=0)
        return f"window_{int(window_start.timestamp() * 1000)}"

    def _is_window_ready(self, window_id: str) -> bool:
        """Check if window is ready for processing"""
        if window_id not in self.windows:
            return False

        window = self.windows[window_id]
        current_time = datetime.utcnow()
        watermark_time = current_time - timedelta(milliseconds=self.watermark_delay_ms)

        return window["end_time"] <= watermark_time

    async def _process_window(self, window_id: str):
        """Process completed window"""
        try:
            window = self.windows[window_id]
            messages = window["messages"]

            # Execute registered processors
            for processor_name, processor_func in self.processors.items():
                try:
                    await processor_func(messages, window_id)
                except Exception as e:
                    logger.error(f"Processor {processor_name} failed: {e}")

            # Log window processing
            await self.audit_logger.log_streaming_event({
                "event_type": "window_processed",
                "window_id": window_id,
                "message_count": len(messages),
                "timestamp": datetime.utcnow().isoformat(),
            })

        except Exception as e:
            logger.error(f"Window processing failed: {e}")

    async def stop_processing(self):
        """Stop stream processing"""
        self.running = False
        logger.info("Stream processing stopped")


# Fallback implementations for when Kafka is unavailable
class FallbackProducer:
    """Fallback producer using local queue"""

    def __init__(self):
        self.queue = asyncio.Queue()

    async def send(
        self,
        topic: str,
        value: Any,
        key: Optional[str] = None,
        headers: Optional[dict] = None,
    ):
        """Send message to local queue"""
        message = {
            "topic": topic,
            "value": value,
            "key": key,
            "headers": headers,
            "timestamp": datetime.utcnow(),
        }
        await self.queue.put(message)


class FallbackConsumer:
    """Fallback consumer using local queue"""

    def __init__(self, topics: list[str]):
        self.topics = topics
        self.queue = asyncio.Queue()

    async def consume(self) -> AsyncGenerator[dict[str, Any], None]:
        """Consume messages from local queue"""
        while True:
            try:
                message = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                yield message
            except asyncio.TimeoutError:
                continue


# Example usage
async def example_usage():
    """Example of how to use the Kafka integration"""

    # Producer configuration
    producer_config = {
        "bootstrap_servers": ["localhost:9092"],
        "message_format": "json",
        "compression_type": "gzip",
        "delivery_guarantee": "at_least_once",
        "constitutional_validation": True,
    }

    # Consumer configuration
    consumer_config = {
        "bootstrap_servers": ["localhost:9092"],
        "group_id": "test-group",
        "topics": ["test-topic"],
        "message_format": "json",
        "constitutional_validation": True,
    }

    # Initialize producer
    producer = KafkaProducer(producer_config)
    await producer.initialize()

    # Send messages
    success = await producer.send_message("test-topic", {"message": "Hello, Kafka!"})
    print(f"Message sent: {success}")

    # Initialize consumer
    consumer = KafkaConsumer(consumer_config)
    await consumer.initialize()

    # Set message handler
    async def handle_message(message: KafkaMessage) -> bool:
        print(f"Received: {message.value}")
        return True

    consumer.set_message_handler(handle_message)

    # Start consuming (in background)
    consume_task = asyncio.create_task(consumer.start_consuming())

    # Wait a bit then stop
    await asyncio.sleep(5)
    await consumer.stop_consuming()
    await consumer.close()
    await producer.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
