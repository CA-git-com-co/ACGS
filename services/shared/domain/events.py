"""
Domain Events Infrastructure for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Provides domain event base classes and handlers for event-driven architecture.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar
from uuid import UUID
import asyncio
import logging

from .base import EntityId, TenantId, CONSTITUTIONAL_HASH

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='DomainEvent')


@dataclass(frozen=True)
class EventMetadata:
    """Metadata for domain events."""
    correlation_id: UUID
    causation_id: UUID
    user_id: Optional[str] = None
    tenant_id: Optional[TenantId] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "correlation_id": str(self.correlation_id),
            "causation_id": str(self.causation_id),
            "user_id": self.user_id,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent
        }


class DomainEvent(ABC):
    """Enhanced base class for domain events with metadata support."""
    
    def __init__(
        self,
        aggregate_id: EntityId,
        occurred_at: Optional[datetime] = None,
        metadata: Optional[EventMetadata] = None
    ):
        """Initialize domain event with metadata."""
        self.event_id = EntityId.generate()
        self.aggregate_id = aggregate_id
        self.occurred_at = occurred_at or datetime.utcnow()
        self.event_type = self.__class__.__name__
        self.event_version = self._get_event_version()
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.metadata = metadata
    
    @abstractmethod
    def _get_event_version(self) -> str:
        """Get the event version. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_event_data(self) -> Dict[str, Any]:
        """Get event-specific data. Must be implemented by subclasses."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": str(self.event_id),
            "aggregate_id": str(self.aggregate_id),
            "occurred_at": self.occurred_at.isoformat(),
            "event_type": self.event_type,
            "event_version": self.event_version,
            "constitutional_hash": self.constitutional_hash,
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "data": self.get_event_data()
        }
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Reconstruct event from dictionary.
        Subclasses should override to handle specific data.
        """
        raise NotImplementedError("Subclasses must implement from_dict")


class DomainEventHandler(ABC):
    """Base class for domain event handlers."""
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Handle a domain event. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def can_handle(self, event: DomainEvent) -> bool:
        """Check if this handler can handle the given event."""
        pass


class EventHandlerRegistry:
    """Registry for domain event handlers."""
    
    def __init__(self):
        """Initialize handler registry."""
        self._handlers: Dict[str, List[DomainEventHandler]] = {}
        self._type_handlers: Dict[Type[DomainEvent], List[DomainEventHandler]] = {}
    
    def register_handler(
        self,
        event_type: Type[DomainEvent],
        handler: DomainEventHandler
    ) -> None:
        """Register a handler for an event type."""
        event_name = event_type.__name__
        
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)
        
        if event_type not in self._type_handlers:
            self._type_handlers[event_type] = []
        self._type_handlers[event_type].append(handler)
        
        logger.info(f"Registered handler {handler.__class__.__name__} for event {event_name}")
    
    def register_handler_function(
        self,
        event_type: Type[DomainEvent],
        handler_func: Callable[[DomainEvent], None]
    ) -> None:
        """Register a handler function for an event type."""
        handler = FunctionEventHandler(event_type, handler_func)
        self.register_handler(event_type, handler)
    
    async def handle_event(self, event: DomainEvent) -> None:
        """Handle a domain event by routing to registered handlers."""
        event_name = event.__class__.__name__
        handlers = self._handlers.get(event_name, [])
        
        if not handlers:
            logger.warning(f"No handlers registered for event {event_name}")
            return
        
        # Execute handlers concurrently
        tasks = []
        for handler in handlers:
            if handler.can_handle(event):
                tasks.append(self._execute_handler(handler, event))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_handler(
        self,
        handler: DomainEventHandler,
        event: DomainEvent
    ) -> None:
        """Execute a single handler with error handling."""
        try:
            await handler.handle(event)
            logger.debug(
                f"Handler {handler.__class__.__name__} successfully processed "
                f"event {event.__class__.__name__}"
            )
        except Exception as e:
            logger.error(
                f"Handler {handler.__class__.__name__} failed to process "
                f"event {event.__class__.__name__}: {e}",
                exc_info=True
            )
            # Continue processing other handlers even if one fails
    
    def get_handlers_for_event(self, event_type: Type[DomainEvent]) -> List[DomainEventHandler]:
        """Get all handlers for a specific event type."""
        return self._type_handlers.get(event_type, [])


class FunctionEventHandler(DomainEventHandler):
    """Adapter to use functions as event handlers."""
    
    def __init__(
        self,
        event_type: Type[DomainEvent],
        handler_func: Callable[[DomainEvent], None]
    ):
        """Initialize function handler."""
        self._event_type = event_type
        self._handler_func = handler_func
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle event using the function."""
        if asyncio.iscoroutinefunction(self._handler_func):
            await self._handler_func(event)
        else:
            self._handler_func(event)
    
    def can_handle(self, event: DomainEvent) -> bool:
        """Check if this handler can handle the event."""
        return isinstance(event, self._event_type)


class EventPublisher:
    """Publisher for domain events."""
    
    def __init__(self, handler_registry: EventHandlerRegistry):
        """Initialize event publisher."""
        self._handler_registry = handler_registry
        self._middleware: List[Callable] = []
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to process events before publishing."""
        self._middleware.append(middleware)
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
        # Apply middleware
        processed_event = event
        for middleware in self._middleware:
            processed_event = await self._apply_middleware(middleware, processed_event)
        
        # Handle the event
        await self._handler_registry.handle_event(processed_event)
    
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """Publish multiple domain events."""
        tasks = [self.publish(event) for event in events]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _apply_middleware(
        self,
        middleware: Callable,
        event: DomainEvent
    ) -> DomainEvent:
        """Apply middleware to an event."""
        if asyncio.iscoroutinefunction(middleware):
            return await middleware(event)
        else:
            return middleware(event)


# Singleton instances for global access
_handler_registry = EventHandlerRegistry()
_event_publisher = EventPublisher(_handler_registry)


def get_event_handler_registry() -> EventHandlerRegistry:
    """Get the global event handler registry."""
    return _handler_registry


def get_event_publisher() -> EventPublisher:
    """Get the global event publisher."""
    return _event_publisher


# Decorator for registering event handlers
def handles(event_type: Type[DomainEvent]):
    """Decorator to register a class as a handler for an event type."""
    def decorator(handler_class: Type[DomainEventHandler]):
        instance = handler_class()
        _handler_registry.register_handler(event_type, instance)
        return handler_class
    return decorator


# Middleware for constitutional compliance validation
async def constitutional_compliance_middleware(event: DomainEvent) -> DomainEvent:
    """Middleware to ensure all events have constitutional compliance."""
    if event.constitutional_hash != CONSTITUTIONAL_HASH:
        logger.error(
            f"Event {event.__class__.__name__} has invalid constitutional hash: "
            f"{event.constitutional_hash}"
        )
        raise ValueError(f"Invalid constitutional hash in event {event.__class__.__name__}")
    return event


# Register the constitutional compliance middleware by default
_event_publisher.add_middleware(constitutional_compliance_middleware)