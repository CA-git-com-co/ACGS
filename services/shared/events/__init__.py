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
    "DatabaseEventStore",
    "Event",
    "EventBus",
    "EventHandler",
    "EventMiddleware",
    "EventPriority",
    "EventStatus",
    "EventStore",
    "EventType",
    "InMemoryEventStore",
    "LoggingMiddleware",
    "MetricsMiddleware",
    "event_handler",
    "event_publisher",
    "get_event_bus",
]
