"""
Event Bus implementation for ACGS multi-agent coordination.

Provides a simple, async event bus for decoupled communication between
agents and services.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class Event(BaseModel):
    """Represents an event in the system"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    source: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: str | None = None


class EventHandler:
    """Base class for event handlers"""

    def __init__(self, handler_id: str, event_types: list[str]):
        self.handler_id = handler_id
        self.event_types = set(event_types)

    async def handle(self, event: Event) -> None:
        """Handle an event. Override in subclasses."""

    def can_handle(self, event_type: str) -> bool:
        """Check if this handler can handle the given event type"""
        return event_type in self.event_types


class EventBus:
    """
    Simple async event bus for ACGS multi-agent coordination.

    Provides publish/subscribe functionality with support for:
    - Event filtering by type
    - Async event handling
    - Error isolation between handlers
    - Event history (limited)
    """

    def __init__(self, max_history: int = 1000):
        self.handlers: dict[str, EventHandler] = {}
        self.event_history: list[Event] = []
        self.max_history = max_history
        self.logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()

    async def subscribe_async(self, handler: EventHandler) -> None:
        """Subscribe an event handler to the bus (async version)"""
        async with self._lock:
            self.handlers[handler.handler_id] = handler
            self.logger.info(
                f"Handler {handler.handler_id} subscribed for events: {handler.event_types}"
            )

    async def unsubscribe(self, handler_id: str) -> None:
        """Unsubscribe an event handler from the bus"""
        async with self._lock:
            if handler_id in self.handlers:
                del self.handlers[handler_id]
                self.logger.info(f"Handler {handler_id} unsubscribed")

    async def publish_async(self, event: Event) -> None:
        """Publish an event to all interested handlers (async version)"""
        # Add to history
        async with self._lock:
            self.event_history.append(event)
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)

        # Find handlers for this event type
        interested_handlers = []
        async with self._lock:
            interested_handlers.extend(
                handler
                for handler in self.handlers.values()
                if handler.can_handle(event.event_type)
            )

        # Handle event asynchronously
        if interested_handlers:
            await self._dispatch_to_handlers(event, interested_handlers)

        self.logger.debug(
            f"Published event {event.event_type} from {event.source} to {len(interested_handlers)} handlers"
        )

    async def _dispatch_to_handlers(
        self, event: Event, handlers: list[EventHandler]
    ) -> None:
        """Dispatch event to handlers with error isolation"""
        tasks = []
        for handler in handlers:
            task = asyncio.create_task(self._safe_handle(handler, event))
            tasks.append(task)

        # Wait for all handlers to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_handle(self, handler: EventHandler, event: Event) -> None:
        """Safely handle an event, catching and logging any exceptions"""
        try:
            await handler.handle(event)
        except Exception as e:
            self.logger.exception(
                f"Error in handler {handler.handler_id} processing event {event.event_type}: {e}"
            )

    async def get_recent_events(
        self, event_type: str | None = None, limit: int = 100
    ) -> list[Event]:
        """Get recent events, optionally filtered by type"""
        async with self._lock:
            events = self.event_history.copy()

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events[-limit:] if limit else events

    async def clear_history(self) -> None:
        """Clear event history"""
        async with self._lock:
            self.event_history.clear()
        self.logger.info("Event history cleared")

    def get_handler_count(self) -> int:
        """Get number of registered handlers"""
        return len(self.handlers)

    def get_registered_handlers(self) -> list[str]:
        """Get list of registered handler IDs"""
        return list(self.handlers.keys())

    # Synchronous methods for test compatibility
    def subscribe(self, event_type: str, handler_func) -> None:
        """Synchronous subscribe method for test compatibility"""
        # Create a simple handler wrapper
        class SimpleHandler(EventHandler):
            def __init__(self, handler_id: str, event_type: str, func):
                super().__init__(handler_id, [event_type])
                self.func = func

            async def handle(self, event: Event) -> None:
                # Call the function with the event data
                self.func(event.data)

        handler_id = f"test_handler_{len(self.handlers)}"
        handler = SimpleHandler(handler_id, event_type, handler_func)

        # Store handler synchronously
        self.handlers[handler.handler_id] = handler

    def publish(self, event_type: str, event_data: dict) -> None:
        """Synchronous publish method for test compatibility"""
        # Create event
        event = Event(
            event_type=event_type,
            source="test_source",
            data=event_data
        )

        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)

        # Find handlers for this event type
        interested_handlers = [
            handler
            for handler in self.handlers.values()
            if handler.can_handle(event.event_type)
        ]

        # Handle event synchronously for tests
        for handler in interested_handlers:
            try:
                # Call handler function directly for test compatibility
                if hasattr(handler, 'func'):
                    handler.func(event_data)
            except Exception as e:
                self.logger.exception(f"Error in handler {handler.handler_id}: {e}")


# Global event bus instance
_global_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def set_event_bus(event_bus: EventBus) -> None:
    """Set the global event bus instance (useful for testing)"""
    global _global_event_bus
    _global_event_bus = event_bus


# Convenience functions
async def publish_event(
    event_type: str,
    source: str,
    data: dict[str, Any],
    correlation_id: str | None = None,
) -> None:
    """Convenience function to publish an event"""
    event = Event(
        event_type=event_type, source=source, data=data, correlation_id=correlation_id
    )
    await get_event_bus().publish(event)


async def subscribe_handler(handler: EventHandler) -> None:
    """Convenience function to subscribe a handler"""
    await get_event_bus().subscribe(handler)


async def unsubscribe_handler(handler_id: str) -> None:
    """Convenience function to unsubscribe a handler"""
    await get_event_bus().unsubscribe(handler_id)
