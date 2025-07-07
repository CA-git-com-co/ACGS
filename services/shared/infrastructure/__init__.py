"""
Infrastructure Layer for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Infrastructure components for DDD implementation including event sourcing,
repositories, and cross-cutting concerns.
"""

from .event_store import (
    ConcurrentAppendError,
    EventStore,
    EventStream,
    PostgreSQLEventStore,
    StreamVersion,
)
from .outbox import OutboxEntry, OutboxPattern, PostgreSQLOutboxPattern
from .repositories import (
    EventSourcedRepository,
    PostgreSQLRepository,
    Repository,
    RepositoryRegistry,
)
from .unit_of_work import PostgreSQLUnitOfWork, UnitOfWork, UnitOfWorkManager

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
    "PostgreSQLOutboxPattern",
]
