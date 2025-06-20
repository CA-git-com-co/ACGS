"""
DGM Service Messaging Module.

Event-driven messaging infrastructure for the Darwin Gödel Machine Service
using NATS message broker for reliable, scalable communication.
"""

from .nats_client import NATSClient, NATSConfig
from .event_publisher import EventPublisher
from .event_subscriber import EventSubscriber
from .message_types import (
    DGMEvent, ImprovementEvent, PerformanceEvent, 
    ConstitutionalEvent, BanditEvent
)

__all__ = [
    "NATSClient",
    "NATSConfig", 
    "EventPublisher",
    "EventSubscriber",
    "DGMEvent",
    "ImprovementEvent",
    "PerformanceEvent",
    "ConstitutionalEvent",
    "BanditEvent"
]
