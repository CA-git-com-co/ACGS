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
    "ConcurrentAppendError",
    "EventSourcedRepository",
    # Event Store
    "EventStore",
    "EventStream",
    # Outbox Pattern
    "OutboxEntry",
    "OutboxPattern",
    "PostgreSQLEventStore",
    "PostgreSQLOutboxPattern",
    "PostgreSQLRepository",
    "PostgreSQLUnitOfWork",
    # Repositories
    "Repository",
    "RepositoryRegistry",
    "StreamVersion",
    # Unit of Work
    "UnitOfWork",
    "UnitOfWorkManager",
]
