"""
Constitutional Governance Repository Implementations
Constitutional Hash: cdd01ef066bc6cf2

Repository implementations for constitutional governance domain entities
with event sourcing and constitutional compliance validation.
"""

import json
import logging
from typing import Any
from uuid import UUID

import asyncpg

from services.shared.domain.base import CONSTITUTIONAL_HASH, EntityId, TenantId
from services.shared.domain.specifications import Specification
from services.shared.infrastructure.repositories import (
    EventSourcedRepository,
    PostgreSQLRepository,
)

from ..domain.entities import AmendmentProposal, Constitution, Principle

logger = logging.getLogger(__name__)


class ConstitutionRepository(EventSourcedRepository[Constitution]):
    """Event-sourced repository for Constitution aggregates."""

    def __init__(self):
        """Initialize constitution repository."""
        super().__init__(aggregate_type=Constitution)

    def _get_stream_id(self, aggregate_id: EntityId) -> str:
        """Generate stream ID for constitution aggregate."""
        return f"constitution-{aggregate_id}"

    async def get_current_constitution(self, tenant_id: TenantId) -> Constitution | None:
        """Get the current active constitution for a tenant."""
        # In a real implementation, this would query for the active constitution
        # For now, we'll use the event store to rebuild the latest constitution
        try:
            # This is a simplified implementation - in practice you'd have
            # a specific stream for the current constitution
            stream_id = f"constitution-current-{tenant_id}"
            events = await self.event_store.get_events(stream_id, tenant_id)
            
            if not events:
                return None
                
            constitution = Constitution.create_new(tenant_id=tenant_id)
            constitution.load_from_history(events)
            return constitution
            
        except Exception as e:
            logger.error(f"Error loading current constitution: {e}")
            return None


class AmendmentProposalRepository(EventSourcedRepository[AmendmentProposal]):
    """Event-sourced repository for AmendmentProposal aggregates."""

    def __init__(self):
        """Initialize amendment proposal repository."""
        super().__init__(aggregate_type=AmendmentProposal)

    def _get_stream_id(self, aggregate_id: EntityId) -> str:
        """Generate stream ID for amendment proposal aggregate."""
        return f"amendment-proposal-{aggregate_id}"

    async def find_by_status(
        self, tenant_id: TenantId, status: str
    ) -> list[AmendmentProposal]:
        """Find amendment proposals by status."""
        # This would typically use a read model or projection
        # For now, we'll return an empty list as a placeholder
        logger.info(f"Finding amendment proposals with status: {status}")
        return []

    async def find_active_proposals(self, tenant_id: TenantId) -> list[AmendmentProposal]:
        """Find all active amendment proposals for a tenant."""
        return await self.find_by_status(tenant_id, "active")


class PrincipleRepository(PostgreSQLRepository[Principle]):
    """PostgreSQL repository for Principle entities."""

    def __init__(self, connection_pool: asyncpg.Pool):
        """Initialize principle repository."""
        super().__init__(
            connection_pool=connection_pool,
            table_name="constitutional_principles",
            aggregate_type=Principle,
        )

    async def _aggregate_to_row(self, aggregate: Principle) -> dict[str, Any]:
        """Convert Principle aggregate to database row."""
        return {
            "id": str(aggregate.id),
            "tenant_id": str(aggregate.tenant_id),
            "name": aggregate.name,
            "description": aggregate.description,
            "category": aggregate.category,
            "priority": aggregate.priority,
            "is_active": aggregate.is_active,
            "version": aggregate.version,
            "created_at": aggregate.created_at,
            "updated_at": aggregate.updated_at,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    async def _row_to_aggregate(self, row: dict[str, Any]) -> Principle:
        """Convert database row to Principle aggregate."""
        return Principle(
            entity_id=EntityId(UUID(row["id"])),
            tenant_id=TenantId(UUID(row["tenant_id"])),
            name=row["name"],
            description=row["description"],
            category=row["category"],
            priority=row["priority"],
            is_active=row["is_active"],
        )

    async def find_by_category(
        self, tenant_id: TenantId, category: str
    ) -> list[Principle]:
        """Find principles by category."""
        conn = await self._get_connection()
        
        try:
            # Set tenant context
            await conn.execute(
                "SELECT set_config('app.current_tenant_id', $1, true)",
                str(tenant_id),
            )
            
            rows = await conn.fetch(
                f"""
                SELECT * FROM {self.table_name}
                WHERE category = $1 AND is_active = true
                ORDER BY priority DESC, name
                """,
                category,
            )
            
            return [await self._row_to_aggregate(dict(row)) for row in rows]
            
        finally:
            await self._release_connection(conn)

    async def find_active_principles(self, tenant_id: TenantId) -> list[Principle]:
        """Find all active principles for a tenant."""
        conn = await self._get_connection()
        
        try:
            # Set tenant context
            await conn.execute(
                "SELECT set_config('app.current_tenant_id', $1, true)",
                str(tenant_id),
            )
            
            rows = await conn.fetch(
                f"""
                SELECT * FROM {self.table_name}
                WHERE is_active = true
                ORDER BY priority DESC, category, name
                """
            )
            
            return [await self._row_to_aggregate(dict(row)) for row in rows]
            
        finally:
            await self._release_connection(conn)


# Repository factory functions for dependency injection
def create_constitution_repository() -> ConstitutionRepository:
    """Create constitution repository instance."""
    return ConstitutionRepository()


def create_amendment_proposal_repository() -> AmendmentProposalRepository:
    """Create amendment proposal repository instance."""
    return AmendmentProposalRepository()


def create_principle_repository(connection_pool: asyncpg.Pool) -> PrincipleRepository:
    """Create principle repository instance."""
    return PrincipleRepository(connection_pool)
