"""
Unit of Work Pattern Implementation for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Manages transactions and coordinates changes across multiple repositories.
"""

import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncContextManager, Dict, List, Optional

import asyncpg

from services.shared.domain.base import CONSTITUTIONAL_HASH, AggregateRoot, TenantId
from services.shared.domain.events import DomainEvent

from .outbox import OutboxPattern, get_outbox_pattern

logger = logging.getLogger(__name__)


class UnitOfWork(ABC):
    """Abstract unit of work for managing transactions and aggregate changes."""

    def __init__(self, tenant_id: TenantId):
        """Initialize unit of work for specific tenant."""
        self.tenant_id = tenant_id
        self._new_aggregates: List[AggregateRoot] = []
        self._dirty_aggregates: List[AggregateRoot] = []
        self._removed_aggregates: List[AggregateRoot] = []
        self._committed = False

    def register_new(self, aggregate: AggregateRoot) -> None:
        """Register new aggregate for insertion."""
        aggregate.ensure_same_tenant(self.tenant_id)
        self._new_aggregates.append(aggregate)
        logger.debug(f"Registered new aggregate: {type(aggregate).__name__}")

    def register_dirty(self, aggregate: AggregateRoot) -> None:
        """Register modified aggregate for update."""
        aggregate.ensure_same_tenant(self.tenant_id)
        if aggregate not in self._dirty_aggregates:
            self._dirty_aggregates.append(aggregate)
        logger.debug(f"Registered dirty aggregate: {type(aggregate).__name__}")

    def register_removed(self, aggregate: AggregateRoot) -> None:
        """Register aggregate for removal."""
        aggregate.ensure_same_tenant(self.tenant_id)
        self._removed_aggregates.append(aggregate)
        logger.debug(f"Registered removed aggregate: {type(aggregate).__name__}")

    def register_clean(self, aggregate: AggregateRoot) -> None:
        """Mark aggregate as clean (no changes)."""
        if aggregate in self._dirty_aggregates:
            self._dirty_aggregates.remove(aggregate)

    @abstractmethod
    async def commit(self) -> None:
        """
        Commit all changes within a transaction.

        This should:
        1. Start transaction
        2. Validate all aggregates
        3. Save all changes
        4. Collect and publish domain events
        5. Commit transaction
        6. Mark as committed
        """
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback all changes."""
        pass

    def _collect_domain_events(self) -> List[DomainEvent]:
        """Collect all domain events from modified aggregates."""
        events = []

        for aggregate in self._new_aggregates + self._dirty_aggregates:
            events.extend(aggregate.uncommitted_events)

        logger.debug(f"Collected {len(events)} domain events")
        return events

    def _mark_events_as_committed(self) -> None:
        """Mark all domain events as committed."""
        for aggregate in self._new_aggregates + self._dirty_aggregates:
            aggregate.mark_events_as_committed()

    def _validate_all_aggregates(self) -> None:
        """Validate invariants for all aggregates."""
        for aggregate in self._new_aggregates + self._dirty_aggregates:
            aggregate.validate_invariants()

            # Validate constitutional hash
            aggregate_hash = aggregate.get_aggregate_hash()
            if not aggregate_hash:
                raise ValueError(f"Aggregate {aggregate.id} has invalid hash")

    @property
    def has_changes(self) -> bool:
        """Check if there are any pending changes."""
        return bool(
            self._new_aggregates or self._dirty_aggregates or self._removed_aggregates
        )

    @property
    def is_committed(self) -> bool:
        """Check if unit of work has been committed."""
        return self._committed


class PostgreSQLUnitOfWork(UnitOfWork):
    """PostgreSQL implementation of unit of work with multi-tenant support."""

    def __init__(
        self,
        tenant_id: TenantId,
        connection_pool: asyncpg.Pool,
        repository_registry: "RepositoryRegistry",
        outbox: Optional[OutboxPattern] = None,
    ):
        """
        Initialize PostgreSQL unit of work.

        Args:
            tenant_id: Tenant identifier
            connection_pool: Database connection pool
            repository_registry: Registry of repositories
            outbox: Optional outbox for reliable event publishing
        """
        super().__init__(tenant_id)
        self.pool = connection_pool
        self.repository_registry = repository_registry
        self.outbox = outbox or get_outbox_pattern()
        self._connection: Optional[asyncpg.Connection] = None
        self._transaction: Optional[asyncpg.Transaction] = None

    async def __aenter__(self) -> "PostgreSQLUnitOfWork":
        """Async context manager entry."""
        self._connection = await self.pool.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        try:
            if exc_type is None and not self._committed:
                # Auto-commit if no exception and not already committed
                await self.commit()
            elif exc_type is not None:
                # Rollback on exception
                await self.rollback()
        finally:
            if self._connection:
                await self.pool.release(self._connection)
                self._connection = None

    async def commit(self) -> None:
        """Commit all changes within a transaction."""
        if self._committed:
            logger.warning("Unit of work already committed")
            return

        if not self.has_changes:
            logger.debug("No changes to commit")
            self._committed = True
            return

        if not self._connection:
            raise RuntimeError("No database connection available")

        try:
            # Start transaction
            self._transaction = self._connection.transaction()
            await self._transaction.start()

            # Set tenant context for RLS
            await self._connection.execute(
                "SELECT set_config('app.current_tenant_id', $1, true)",
                str(self.tenant_id),
            )

            logger.info(f"Starting transaction for tenant {self.tenant_id}")

            # Validate all aggregates before persisting
            self._validate_all_aggregates()

            # Collect domain events before saving
            domain_events = self._collect_domain_events()

            # Save all changes using repositories
            await self._save_new_aggregates()
            await self._save_dirty_aggregates()
            await self._remove_aggregates()

            # Add domain events to outbox within same transaction
            if domain_events and self.outbox:
                await self.outbox.add_events(
                    domain_events, self.tenant_id, self._connection
                )
                logger.debug(f"Added {len(domain_events)} events to outbox")

            # Commit transaction
            await self._transaction.commit()

            # Mark events as committed
            self._mark_events_as_committed()

            # Clear aggregate lists
            self._clear_aggregates()

            self._committed = True

            logger.info(
                f"Successfully committed transaction for tenant {self.tenant_id} "
                f"with {len(domain_events)} events"
            )

        except Exception as e:
            logger.error(f"Failed to commit transaction: {e}")
            await self.rollback()
            raise
        finally:
            self._transaction = None

    async def rollback(self) -> None:
        """Rollback all changes."""
        if self._transaction:
            try:
                await self._transaction.rollback()
                logger.info(f"Rolled back transaction for tenant {self.tenant_id}")
            except Exception as e:
                logger.error(f"Failed to rollback transaction: {e}")
            finally:
                self._transaction = None

        # Clear aggregate lists without marking events as committed
        self._clear_aggregates()

    async def _save_new_aggregates(self) -> None:
        """Save new aggregates using their repositories."""
        for aggregate in self._new_aggregates:
            repository = self.repository_registry.get_repository(type(aggregate))

            if hasattr(repository, "set_connection"):
                repository.set_connection(self._connection)

            await repository.save(aggregate)
            aggregate.increment_version()

            logger.debug(
                f"Saved new aggregate: {type(aggregate).__name__}({aggregate.id})"
            )

    async def _save_dirty_aggregates(self) -> None:
        """Save modified aggregates using their repositories."""
        for aggregate in self._dirty_aggregates:
            repository = self.repository_registry.get_repository(type(aggregate))

            if hasattr(repository, "set_connection"):
                repository.set_connection(self._connection)

            await repository.save(aggregate)
            aggregate.increment_version()

            logger.debug(
                f"Saved dirty aggregate: {type(aggregate).__name__}({aggregate.id})"
            )

    async def _remove_aggregates(self) -> None:
        """Remove aggregates using their repositories."""
        for aggregate in self._removed_aggregates:
            repository = self.repository_registry.get_repository(type(aggregate))

            if hasattr(repository, "set_connection"):
                repository.set_connection(self._connection)

            await repository.remove(aggregate.id)

            logger.debug(
                f"Removed aggregate: {type(aggregate).__name__}({aggregate.id})"
            )

    def _clear_aggregates(self) -> None:
        """Clear all aggregate lists."""
        self._new_aggregates.clear()
        self._dirty_aggregates.clear()
        self._removed_aggregates.clear()


class UnitOfWorkManager:
    """Manager for creating and managing units of work."""

    def __init__(
        self,
        connection_pool: asyncpg.Pool,
        repository_registry: "RepositoryRegistry",
        outbox: Optional[OutboxPattern] = None,
    ):
        """
        Initialize unit of work manager.

        Args:
            connection_pool: Database connection pool
            repository_registry: Registry of repositories
            outbox: Optional outbox for reliable event publishing
        """
        self.pool = connection_pool
        self.repository_registry = repository_registry
        self.outbox = outbox

    @asynccontextmanager
    async def start(self, tenant_id: TenantId) -> AsyncContextManager[UnitOfWork]:
        """
        Start a new unit of work for the specified tenant.

        Args:
            tenant_id: Tenant identifier

        Returns:
            Unit of work context manager
        """
        uow = PostgreSQLUnitOfWork(
            tenant_id=tenant_id,
            connection_pool=self.pool,
            repository_registry=self.repository_registry,
            outbox=self.outbox,
        )

        async with uow:
            yield uow

    def create(self, tenant_id: TenantId) -> PostgreSQLUnitOfWork:
        """
        Create a new unit of work for manual management.

        Args:
            tenant_id: Tenant identifier

        Returns:
            New unit of work instance
        """
        return PostgreSQLUnitOfWork(
            tenant_id=tenant_id,
            connection_pool=self.pool,
            repository_registry=self.repository_registry,
            outbox=self.outbox,
        )


class TransactionalService:
    """Base class for application services using unit of work pattern."""

    def __init__(self, uow_manager: UnitOfWorkManager):
        """Initialize with unit of work manager."""
        self.uow_manager = uow_manager

    @asynccontextmanager
    async def transaction(self, tenant_id: TenantId) -> AsyncContextManager[UnitOfWork]:
        """
        Start a transactional operation.

        Args:
            tenant_id: Tenant identifier

        Returns:
            Unit of work for the transaction
        """
        async with self.uow_manager.start(tenant_id) as uow:
            yield uow


# Example usage with constitutional governance domain
class ConstitutionalGovernanceUnitOfWork(PostgreSQLUnitOfWork):
    """
    Specialized unit of work for constitutional governance domain.

    Adds constitutional-specific validation and logging.
    """

    def _validate_all_aggregates(self) -> None:
        """Enhanced validation for constitutional aggregates."""
        super()._validate_all_aggregates()

        # Additional constitutional validation
        for aggregate in self._new_aggregates + self._dirty_aggregates:
            # Validate constitutional hash in domain events
            for event in aggregate.uncommitted_events:
                if event.constitutional_hash != CONSTITUTIONAL_HASH:
                    raise ValueError(
                        f"Event {event.event_id} has invalid constitutional hash: "
                        f"{event.constitutional_hash}"
                    )

            # Validate aggregate constitutional compliance
            if hasattr(aggregate, "constitutional_hash"):
                if aggregate.constitutional_hash.value != CONSTITUTIONAL_HASH:
                    raise ValueError(
                        f"Aggregate {aggregate.id} has invalid constitutional hash"
                    )

    async def commit(self) -> None:
        """Enhanced commit with constitutional logging."""
        events_count = len(self._collect_domain_events())

        logger.info(
            f"Committing constitutional changes for tenant {self.tenant_id}: "
            f"{len(self._new_aggregates)} new, "
            f"{len(self._dirty_aggregates)} modified, "
            f"{len(self._removed_aggregates)} removed aggregates, "
            f"{events_count} events"
        )

        # Ensure constitutional compliance
        self._ensure_constitutional_compliance()

        await super().commit()

        logger.info(
            f"Constitutional governance transaction committed successfully "
            f"for tenant {self.tenant_id}"
        )

    def _ensure_constitutional_compliance(self) -> None:
        """Ensure all changes comply with constitutional requirements."""
        # Check that constitutional hash is present in all domain events
        for event in self._collect_domain_events():
            if not hasattr(event, "constitutional_hash"):
                raise ValueError(
                    f"Event {event.event_type} missing constitutional hash"
                )

        # Additional constitutional checks could be added here
        logger.debug("Constitutional compliance verified for all changes")


# Global unit of work manager instance
_uow_manager: Optional[UnitOfWorkManager] = None


def get_unit_of_work_manager() -> UnitOfWorkManager:
    """Get global unit of work manager instance."""
    if _uow_manager is None:
        raise RuntimeError("Unit of work manager not initialized")
    return _uow_manager


def set_unit_of_work_manager(manager: UnitOfWorkManager) -> None:
    """Set global unit of work manager instance."""
    global _uow_manager
    _uow_manager = manager
