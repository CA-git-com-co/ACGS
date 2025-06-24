"""
DGM Service Messaging Module.

Event-driven messaging infrastructure for the Darwin Gödel Machine Service
using NATS message broker for reliable, scalable communication.
"""

from .event_publisher import EventPublisher
from .event_subscriber import EventSubscriber
from .message_types import (
    BanditEvent,
    ConstitutionalEvent,
    DGMEvent,
    ImprovementEvent,
    PerformanceEvent,
)
from .nats_client import NATSClient, NATSConfig

__all__ = [
    "NATSClient",
    "NATSConfig",
    "EventPublisher",
    "EventSubscriber",
    "DGMEvent",
    "ImprovementEvent",
    "PerformanceEvent",
    "ConstitutionalEvent",
    "BanditEvent",
]
