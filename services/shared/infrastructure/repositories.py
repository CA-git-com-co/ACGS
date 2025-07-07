"""
Repository Pattern Implementation for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Abstract repository interfaces and PostgreSQL implementations with DDD support.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

import asyncpg

from services.shared.domain.base import (
    CONSTITUTIONAL_HASH,
    AggregateRoot,
    Entity,
    EntityId,
    TenantId,
)
from services.shared.domain.specifications import Specification

from .event_store import EventStore, get_event_store

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=AggregateRoot)


class Repository(ABC, Generic[T]):
    """Abstract repository interface for domain aggregates."""

    @abstractmethod
    async def get_by_id(self, entity_id: EntityId, tenant_id: TenantId) -> Optional[T]:
        """
        Get aggregate by ID.

        Args:
            entity_id: Unique identifier
            tenant_id: Tenant owning the aggregate

        Returns:
            Aggregate instance or None if not found
        """
        pass

    @abstractmethod
    async def save(self, aggregate: T) -> None:
        """
        Save aggregate.

        Args:
            aggregate: Aggregate to save
        """
        pass

    @abstractmethod
    async def remove(self, entity_id: EntityId) -> None:
        """
        Remove aggregate.

        Args:
            entity_id: ID of aggregate to remove
        """
        pass

    @abstractmethod
    async def find_by_specification(
        self,
        specification: Specification[T],
        tenant_id: TenantId,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[T]:
        """
        Find aggregates matching specification.

        Args:
            specification: Domain specification to match
            tenant_id: Tenant filter
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of matching aggregates
        """
        pass

    async def exists(self, entity_id: EntityId, tenant_id: TenantId) -> bool:
        """
        Check if aggregate exists.

        Args:
            entity_id: Unique identifier
            tenant_id: Tenant owning the aggregate

        Returns:
            True if aggregate exists
        """
        aggregate = await self.get_by_id(entity_id, tenant_id)
        return aggregate is not None


class EventSourcedRepository(Repository[T], ABC):
    """Repository for event-sourced aggregates."""

    def __init__(self, event_store: Optional[EventStore] = None):
        """Initialize with event store."""
        self.event_store = event_store or get_event_store()

    @abstractmethod
    def _get_stream_id(self, entity_id: EntityId) -> str:
        """
        Get event stream ID for aggregate.

        Args:
            entity_id: Aggregate ID

        Returns:
            Stream identifier
        """
        pass

    @abstractmethod
    async def _create_empty_aggregate(
        self, entity_id: EntityId, tenant_id: TenantId
    ) -> T:
        """
        Create empty aggregate for event replay.

        Args:
            entity_id: Aggregate ID
            tenant_id: Tenant ID

        Returns:
            Empty aggregate instance
        """
        pass

    async def get_by_id(self, entity_id: EntityId, tenant_id: TenantId) -> Optional[T]:
        """Get aggregate by replaying events from event store."""
        stream_id = self._get_stream_id(entity_id)

        # Check if stream exists
        if not await self.event_store.stream_exists(stream_id, tenant_id):
            return None

        # Get all events for the aggregate
        events = await self.event_store.get_events(stream_id, tenant_id)

        if not events:
            return None

        # Create empty aggregate and replay events
        aggregate = await self._create_empty_aggregate(entity_id, tenant_id)
        aggregate.load_from_history(events)

        logger.debug(f"Loaded aggregate {entity_id} from {len(events)} events")
        return aggregate

    async def save(self, aggregate: T) -> None:
        """Save aggregate by storing its uncommitted events."""
        if not aggregate.uncommitted_events:
            logger.debug(f"No events to save for aggregate {aggregate.id}")
            return

        stream_id = self._get_stream_id(aggregate.id)

        # Append events to event store
        await self.event_store.append_events(
            stream_id=stream_id,
            tenant_id=aggregate.tenant_id,
            events=aggregate.uncommitted_events,
            expected_version=None,  # Could use aggregate version for optimistic locking
        )

        logger.debug(
            f"Saved {len(aggregate.uncommitted_events)} events "
            f"for aggregate {aggregate.id}"
        )

    async def remove(self, entity_id: EntityId) -> None:
        """Remove aggregate (event-sourced aggregates are typically not deleted)."""
        # In event sourcing, aggregates are usually not deleted
        # Instead, a "deleted" event is added to mark them as removed
        raise NotImplementedError(
            "Event-sourced aggregates should use domain events for deletion"
        )


class PostgreSQLRepository(Repository[T], ABC):
    """PostgreSQL implementation of repository with multi-tenant support."""

    def __init__(
        self, connection_pool: asyncpg.Pool, table_name: str, aggregate_type: Type[T]
    ):
        """
        Initialize PostgreSQL repository.

        Args:
            connection_pool: Database connection pool
            table_name: Name of the database table
            aggregate_type: Type of aggregate this repository manages
        """
        self.pool = connection_pool
        self.table_name = table_name
        self.aggregate_type = aggregate_type
        self._connection: Optional[asyncpg.Connection] = None

    def set_connection(self, connection: asyncpg.Connection) -> None:
        """Set specific connection for transaction management."""
        self._connection = connection

    async def _get_connection(self) -> asyncpg.Connection:
        """Get database connection."""
        if self._connection:
            return self._connection
        return await self.pool.acquire()

    async def _release_connection(self, conn: asyncpg.Connection) -> None:
        """Release database connection if not using a specific one."""
        if self._connection is None:
            await self.pool.release(conn)

    @abstractmethod
    async def _row_to_aggregate(self, row: asyncpg.Record, tenant_id: TenantId) -> T:
        """
        Convert database row to aggregate.

        Args:
            row: Database row
            tenant_id: Tenant ID

        Returns:
            Aggregate instance
        """
        pass

    @abstractmethod
    async def _aggregate_to_row(self, aggregate: T) -> Dict[str, Any]:
        """
        Convert aggregate to database row data.

        Args:
            aggregate: Aggregate instance

        Returns:
            Dictionary of column values
        """
        pass

    async def get_by_id(self, entity_id: EntityId, tenant_id: TenantId) -> Optional[T]:
        """Get aggregate by ID with tenant isolation."""
        conn = await self._get_connection()

        try:
            # Set tenant context for RLS
            await conn.execute(
                "SELECT set_config('app.current_tenant_id', $1, true)", str(tenant_id)
            )

            # Query for the aggregate
            row = await conn.fetchrow(
                f"SELECT * FROM {self.table_name} WHERE id = $1 AND tenant_id = $2",
                str(entity_id),
                str(tenant_id),
            )

            if not row:
                return None

            aggregate = await self._row_to_aggregate(row, tenant_id)
            logger.debug(f"Retrieved aggregate {entity_id} from {self.table_name}")
            return aggregate

        finally:
            await self._release_connection(conn)

    async def save(self, aggregate: T) -> None:
        """Save aggregate with upsert logic."""
        conn = await self._get_connection()

        try:
            # Set tenant context for RLS
            await conn.execute(
                "SELECT set_config('app.current_tenant_id', $1, true)",
                str(aggregate.tenant_id),
            )

            # Convert aggregate to row data
            row_data = await self._aggregate_to_row(aggregate)

            # Add constitutional hash validation
            row_data["constitutional_hash"] = CONSTITUTIONAL_HASH

            # Build upsert query
            columns = list(row_data.keys())
            placeholders = [f"${i+1}" for i in range(len(columns))]
            values = [row_data[col] for col in columns]

            # Create conflict resolution for upsert
            update_sets = [
                f"{col} = EXCLUDED.{col}"
                for col in columns
                if col not in ("id", "tenant_id", "created_at")
            ]

            query = f"""
                INSERT INTO {self.table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                ON CONFLICT (id, tenant_id) 
                DO UPDATE SET {', '.join(update_sets)}
            """

            await conn.execute(query, *values)

            logger.debug(f"Saved aggregate {aggregate.id} to {self.table_name}")

        finally:
            await self._release_connection(conn)

    async def remove(self, entity_id: EntityId) -> None:
        """Remove aggregate by ID."""
        conn = await self._get_connection()

        try:
            result = await conn.execute(
                f"DELETE FROM {self.table_name} WHERE id = $1", str(entity_id)
            )

            # Check if any rows were affected
            rows_affected = int(result.split()[-1])
            if rows_affected == 0:
                logger.warning(f"No aggregate found to remove: {entity_id}")
            else:
                logger.debug(f"Removed aggregate {entity_id} from {self.table_name}")

        finally:
            await self._release_connection(conn)

    async def find_by_specification(
        self,
        specification: Specification[T],
        tenant_id: TenantId,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[T]:
        """Find aggregates matching specification."""
        conn = await self._get_connection()

        try:
            # Set tenant context for RLS
            await conn.execute(
                "SELECT set_config('app.current_tenant_id', $1, true)", str(tenant_id)
            )

            # Build query with tenant filter
            query = f"SELECT * FROM {self.table_name} WHERE tenant_id = $1"
            params = [str(tenant_id)]

            # Add pagination
            if limit:
                query += f" LIMIT ${len(params) + 1}"
                params.append(limit)

            if offset:
                query += f" OFFSET ${len(params) + 1}"
                params.append(offset)

            rows = await conn.fetch(query, *params)

            # Convert rows to aggregates and filter by specification
            aggregates = []
            for row in rows:
                aggregate = await self._row_to_aggregate(row, tenant_id)
                if specification.is_satisfied_by(aggregate):
                    aggregates.append(aggregate)

            logger.debug(
                f"Found {len(aggregates)} aggregates matching specification "
                f"in {self.table_name}"
            )
            return aggregates

        finally:
            await self._release_connection(conn)


class RepositoryRegistry:
    """Registry for managing repository instances by aggregate type."""

    def __init__(self):
        """Initialize empty registry."""
        self._repositories: Dict[Type[AggregateRoot], Repository] = {}

    def register(
        self, aggregate_type: Type[AggregateRoot], repository: Repository
    ) -> None:
        """
        Register repository for aggregate type.

        Args:
            aggregate_type: Aggregate class
            repository: Repository instance
        """
        self._repositories[aggregate_type] = repository
        logger.debug(f"Registered repository for {aggregate_type.__name__}")

    def get_repository(self, aggregate_type: Type[AggregateRoot]) -> Repository:
        """
        Get repository for aggregate type.

        Args:
            aggregate_type: Aggregate class

        Returns:
            Repository instance

        Raises:
            KeyError: If no repository registered for type
        """
        if aggregate_type not in self._repositories:
            raise KeyError(f"No repository registered for {aggregate_type.__name__}")

        return self._repositories[aggregate_type]

    def has_repository(self, aggregate_type: Type[AggregateRoot]) -> bool:
        """
        Check if repository is registered for aggregate type.

        Args:
            aggregate_type: Aggregate class

        Returns:
            True if repository is registered
        """
        return aggregate_type in self._repositories

    def get_all_repositories(self) -> Dict[Type[AggregateRoot], Repository]:
        """Get all registered repositories."""
        return self._repositories.copy()


# Specialized repository implementations for constitutional governance
class ConstitutionRepository(EventSourcedRepository):
    """Event-sourced repository for Constitution aggregates."""

    def _get_stream_id(self, entity_id: EntityId) -> str:
        """Get stream ID for constitution."""
        return f"constitution-{entity_id}"

    async def _create_empty_aggregate(self, entity_id: EntityId, tenant_id: TenantId):
        """Create empty constitution for event replay."""
        from services.contexts.constitutional_governance.domain.entities import (
            Constitution,
        )
        from services.contexts.constitutional_governance.domain.value_objects import (
            VersionNumber,
        )

        return Constitution(
            constitution_id=entity_id,
            tenant_id=tenant_id,
            version=VersionNumber(0, 0, 0),
            principles=[],
            meta_rules=[],
        )


class AmendmentProposalRepository(EventSourcedRepository):
    """Event-sourced repository for AmendmentProposal aggregates."""

    def _get_stream_id(self, entity_id: EntityId) -> str:
        """Get stream ID for amendment proposal."""
        return f"amendment-{entity_id}"

    async def _create_empty_aggregate(self, entity_id: EntityId, tenant_id: TenantId):
        """Create empty amendment proposal for event replay."""
        from services.contexts.constitutional_governance.domain.entities import (
            AmendmentProposal,
        )
        from services.contexts.constitutional_governance.domain.value_objects import (
            AmendmentJustification,
        )

        return AmendmentProposal(
            proposal_id=entity_id,
            tenant_id=tenant_id,
            proposer_id="",
            amendments=[],
            justification=AmendmentJustification(
                rationale="",
                problem_statement="",
                proposed_solution="",
                expected_benefits=[],
                potential_risks=[],
                evidence_links=[],
            ),
        )


# Global repository registry instance
_repository_registry: Optional[RepositoryRegistry] = None


def get_repository_registry() -> RepositoryRegistry:
    """Get global repository registry instance."""
    if _repository_registry is None:
        raise RuntimeError("Repository registry not initialized")
    return _repository_registry


def set_repository_registry(registry: RepositoryRegistry) -> None:
    """Set global repository registry instance."""
    global _repository_registry
    _repository_registry = registry


def setup_constitutional_repositories(
    connection_pool: asyncpg.Pool, event_store: EventStore
) -> RepositoryRegistry:
    """
    Set up repositories for constitutional governance domain.

    Args:
        connection_pool: Database connection pool
        event_store: Event store instance

    Returns:
        Configured repository registry
    """
    registry = RepositoryRegistry()

    # Register event-sourced repositories
    from services.contexts.constitutional_governance.domain.entities import (
        AmendmentProposal,
        Constitution,
    )

    constitution_repo = ConstitutionRepository(event_store)
    amendment_repo = AmendmentProposalRepository(event_store)

    registry.register(Constitution, constitution_repo)
    registry.register(AmendmentProposal, amendment_repo)

    logger.info("Set up constitutional governance repositories")
    return registry
