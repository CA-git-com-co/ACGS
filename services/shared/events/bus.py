"""
Event Bus implementation for ACGS multi-agent coordination.

Provides a simple, async event bus for decoupled communication between
agents and services.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Set
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



class Event(BaseModel):
    """Represents an event in the system"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    source: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


class EventHandler:
    """Base class for event handlers"""
    
    def __init__(self, handler_id: str, event_types: List[str]):
        self.handler_id = handler_id
        self.event_types = set(event_types)
    
    async def handle(self, event: Event) -> None:
        """Handle an event. Override in subclasses."""
        pass
    
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
        self.handlers: Dict[str, EventHandler] = {}
        self.event_history: List[Event] = []
        self.max_history = max_history
        self.logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()
    
    async def subscribe(self, handler: EventHandler) -> None:
        """Subscribe an event handler to the bus"""
        async with self._lock:
            self.handlers[handler.handler_id] = handler
            self.logger.info(f"Handler {handler.handler_id} subscribed for events: {handler.event_types}")
    
    async def unsubscribe(self, handler_id: str) -> None:
        """Unsubscribe an event handler from the bus"""
        async with self._lock:
            if handler_id in self.handlers:
                del self.handlers[handler_id]
                self.logger.info(f"Handler {handler_id} unsubscribed")
    
    async def publish(self, event: Event) -> None:
        """Publish an event to all interested handlers"""
        # Add to history
        async with self._lock:
            self.event_history.append(event)
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)
        
        # Find handlers for this event type
        interested_handlers = []
        async with self._lock:
            for handler in self.handlers.values():
                if handler.can_handle(event.event_type):
                    interested_handlers.append(handler)
        
        # Handle event asynchronously
        if interested_handlers:
            await self._dispatch_to_handlers(event, interested_handlers)
        
        self.logger.debug(f"Published event {event.event_type} from {event.source} to {len(interested_handlers)} handlers")
    
    async def _dispatch_to_handlers(self, event: Event, handlers: List[EventHandler]) -> None:
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
            self.logger.error(f"Error in handler {handler.handler_id} processing event {event.event_type}: {e}")
    
    async def get_recent_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[Event]:
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
    
    def get_registered_handlers(self) -> List[str]:
        """Get list of registered handler IDs"""
        return list(self.handlers.keys())


# Global event bus instance
_global_event_bus: Optional[EventBus] = None


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
async def publish_event(event_type: str, source: str, data: Dict[str, Any], correlation_id: Optional[str] = None) -> None:
    """Convenience function to publish an event"""
    event = Event(
        event_type=event_type,
        source=source,
        data=data,
        correlation_id=correlation_id
    )
    await get_event_bus().publish(event)


async def subscribe_handler(handler: EventHandler) -> None:
    """Convenience function to subscribe a handler"""
    await get_event_bus().subscribe(handler)


async def unsubscribe_handler(handler_id: str) -> None:
    """Convenience function to unsubscribe a handler"""
    await get_event_bus().unsubscribe(handler_id)
