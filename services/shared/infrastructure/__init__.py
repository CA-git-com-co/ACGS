"""
Infrastructure Layer for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Infrastructure components for DDD implementation including event sourcing,
repositories, and cross-cutting concerns.
"""

from .event_store import (
    EventStore,
    PostgreSQLEventStore,
    EventStream,
    StreamVersion,
    ConcurrentAppendError
)

from .unit_of_work import (
    UnitOfWork,
    PostgreSQLUnitOfWork,
    UnitOfWorkManager
)

from .repositories import (
    Repository,
    EventSourcedRepository,
    PostgreSQLRepository,
    RepositoryRegistry
)

from .outbox import (
    OutboxEntry,
    OutboxPattern,
    PostgreSQLOutboxPattern
)

__all__ = [
    # Event Store
    "EventStore",
    "PostgreSQLEventStore", 
    "EventStream",
    "StreamVersion",
    "ConcurrentAppendError",
    
    # Unit of Work
    "UnitOfWork",
    "PostgreSQLUnitOfWork",
    "UnitOfWorkManager",
    
    # Repositories
    "Repository",
    "EventSourcedRepository",
    "PostgreSQLRepository",
    "RepositoryRegistry",
    
    # Outbox Pattern
    "OutboxEntry",
    "OutboxPattern",
    "PostgreSQLOutboxPattern"
]