"""
Enterprise Streaming Infrastructure

Apache Kafka integration for high-scale event streaming,
implementing the ACGE technical validation recommendations for
enterprise-grade streaming architecture.

Key Components:
- Apache Kafka producer and consumer clients
- Stream processing with error handling and monitoring
- Integration with existing NATS for lightweight messaging
- Event sourcing and message persistence
- Production-ready configuration and management
"""

from .event_streaming_manager import EventStreamingManager
from .kafka_config_manager import KafkaConfigManager
from .kafka_integration import KafkaConsumer, KafkaProducer, KafkaStreamProcessor

__all__ = [
    "KafkaProducer",
    "KafkaConsumer",
    "KafkaStreamProcessor",
    "EventStreamingManager",
    "KafkaConfigManager",
]
