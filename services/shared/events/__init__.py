"""
Event-Driven Architecture for ACGS-PGP Services

This module provides event-driven communication patterns to replace direct
service calls and reduce coupling between microservices.
"""

from .bus import Event, EventBus, EventHandler, get_event_bus
from .decorators import event_handler, event_publisher
from .middleware import EventMiddleware, LoggingMiddleware, MetricsMiddleware
from .store import DatabaseEventStore, EventStore, InMemoryEventStore
from .types import EventPriority, EventStatus, EventType

__all__ = [
    "EventBus",
    "Event",
    "EventHandler",
    "get_event_bus",
    "event_handler",
    "event_publisher",
    "EventMiddleware",
    "LoggingMiddleware",
    "MetricsMiddleware",
    "EventStore",
    "InMemoryEventStore",
    "DatabaseEventStore",
    "EventType",
    "EventPriority",
    "EventStatus",
]
