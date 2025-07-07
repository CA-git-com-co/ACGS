"""
Event Store Implementation for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Event sourcing infrastructure for storing and retrieving domain events.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any, AsyncIterator
from uuid import UUID
import json
import logging
import asyncpg

from services.shared.domain.base import EntityId, TenantId, CONSTITUTIONAL_HASH
from services.shared.domain.events import DomainEvent

logger = logging.getLogger(__name__)


class ConcurrentAppendError(Exception):
    """Raised when there's a concurrent modification conflict during event append."""
    pass


@dataclass
class StreamVersion:
    """Version information for an event stream."""
    value: int
    
    def increment(self) -> 'StreamVersion':
        """Create next version."""
        return StreamVersion(self.value + 1)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, int):
            return self.value == other
        return isinstance(other, StreamVersion) and self.value == other.value
    
    def __int__(self) -> int:
        return self.value


@dataclass
class EventStream:
    """Represents a stream of domain events for an aggregate."""
    stream_id: str
    tenant_id: TenantId
    current_version: StreamVersion
    events: List[DomainEvent]
    
    def append_event(self, event: DomainEvent) -> None:
        """Append an event to the stream."""
        self.events.append(event)
        self.current_version = self.current_version.increment()


@dataclass
class StoredEvent:
    """Represents a stored event with metadata."""
    event_id: str
    stream_id: str
    tenant_id: str
    event_type: str
    event_version: str
    event_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]
    stream_version: int
    created_at: datetime
    constitutional_hash: str


class EventStore(ABC):
    """Abstract interface for event stores."""
    
    @abstractmethod
    async def append_events(
        self,
        stream_id: str,
        tenant_id: TenantId,
        events: List[DomainEvent],
        expected_version: Optional[StreamVersion] = None
    ) -> StreamVersion:
        """
        Append events to a stream with optimistic concurrency control.
        
        Args:
            stream_id: Unique identifier for the event stream
            tenant_id: Tenant owning the stream
            events: List of domain events to append
            expected_version: Expected current version for optimistic locking
            
        Returns:
            New stream version after append
            
        Raises:
            ConcurrentAppendError: If expected version doesn't match current
        """
        pass
    
    @abstractmethod
    async def get_events(
        self,
        stream_id: str,
        tenant_id: TenantId,
        from_version: Optional[StreamVersion] = None,
        to_version: Optional[StreamVersion] = None
    ) -> List[DomainEvent]:
        """
        Get events from a stream within version range.
        
        Args:
            stream_id: Stream identifier
            tenant_id: Tenant owning the stream
            from_version: Starting version (inclusive)
            to_version: Ending version (inclusive)
            
        Returns:
            List of domain events in order
        """
        pass
    
    @abstractmethod
    async def get_stream_version(
        self,
        stream_id: str,
        tenant_id: TenantId
    ) -> StreamVersion:
        """
        Get current version of a stream.
        
        Args:
            stream_id: Stream identifier
            tenant_id: Tenant owning the stream
            
        Returns:
            Current stream version
        """
        pass
    
    @abstractmethod
    async def stream_exists(
        self,
        stream_id: str,
        tenant_id: TenantId
    ) -> bool:
        """
        Check if a stream exists.
        
        Args:
            stream_id: Stream identifier
            tenant_id: Tenant owning the stream
            
        Returns:
            True if stream exists
        """
        pass
    
    @abstractmethod
    async def get_all_events_since(
        self,
        tenant_id: TenantId,
        since: datetime,
        event_types: Optional[List[str]] = None
    ) -> AsyncIterator[DomainEvent]:
        """
        Get all events since a specific timestamp.
        
        Args:
            tenant_id: Tenant filter
            since: Timestamp to start from
            event_types: Optional filter by event types
            
        Yields:
            Domain events in chronological order
        """
        pass


class PostgreSQLEventStore(EventStore):
    """PostgreSQL implementation of event store with multi-tenant support."""
    
    def __init__(self, connection_pool: asyncpg.Pool):
        """Initialize with database connection pool."""
        self.pool = connection_pool
    
    async def initialize(self) -> None:
        """Initialize database schema for event store."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS event_store (
                    id BIGSERIAL PRIMARY KEY,
                    event_id UUID NOT NULL UNIQUE,
                    stream_id TEXT NOT NULL,
                    tenant_id UUID NOT NULL,
                    event_type TEXT NOT NULL,
                    event_version TEXT NOT NULL,
                    event_data JSONB NOT NULL,
                    metadata JSONB,
                    stream_version INTEGER NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    constitutional_hash TEXT NOT NULL DEFAULT 'cdd01ef066bc6cf2',
                    
                    -- Unique constraint for optimistic concurrency
                    UNIQUE(stream_id, tenant_id, stream_version)
                );
                
                -- Enable RLS for multi-tenant isolation
                ALTER TABLE event_store ENABLE ROW LEVEL SECURITY;
                
                -- RLS policy for tenant isolation
                DROP POLICY IF EXISTS event_store_tenant_isolation ON event_store;
                CREATE POLICY event_store_tenant_isolation ON event_store
                    FOR ALL TO application_role
                    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
                
                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_event_store_stream 
                    ON event_store (stream_id, tenant_id, stream_version);
                
                CREATE INDEX IF NOT EXISTS idx_event_store_tenant_time 
                    ON event_store (tenant_id, created_at);
                
                CREATE INDEX IF NOT EXISTS idx_event_store_event_type 
                    ON event_store (tenant_id, event_type, created_at);
                
                -- Constitutional hash constraint
                ALTER TABLE event_store 
                ADD CONSTRAINT constitutional_hash_check 
                CHECK (constitutional_hash = 'cdd01ef066bc6cf2');
            """)
    
    async def append_events(
        self,
        stream_id: str,
        tenant_id: TenantId,
        events: List[DomainEvent],
        expected_version: Optional[StreamVersion] = None
    ) -> StreamVersion:
        """Append events with optimistic concurrency control."""
        if not events:
            current_version = await self.get_stream_version(stream_id, tenant_id)
            return current_version
        
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Set tenant context for RLS
                await conn.execute(
                    "SELECT set_config('app.current_tenant_id', $1, true)",
                    str(tenant_id)
                )
                
                # Get current stream version
                current_version = await self._get_stream_version_in_transaction(
                    conn, stream_id, tenant_id
                )
                
                # Check optimistic concurrency
                if expected_version is not None and current_version != expected_version:
                    raise ConcurrentAppendError(
                        f"Expected version {expected_version.value}, "
                        f"but current version is {current_version.value}"
                    )
                
                # Prepare events for insertion
                new_version = current_version
                event_rows = []
                
                for event in events:
                    new_version = new_version.increment()
                    
                    # Validate constitutional hash
                    if event.constitutional_hash != CONSTITUTIONAL_HASH:
                        raise ValueError(
                            f"Invalid constitutional hash in event: {event.constitutional_hash}"
                        )
                    
                    event_data = event.get_event_data()
                    metadata = event.metadata.to_dict() if event.metadata else None
                    
                    event_rows.append((
                        str(event.event_id),
                        stream_id,
                        str(tenant_id),
                        event.event_type,
                        event.event_version,
                        json.dumps(event_data),
                        json.dumps(metadata) if metadata else None,
                        new_version.value,
                        event.occurred_at,
                        event.constitutional_hash
                    ))
                
                # Insert events in batch
                await conn.executemany("""
                    INSERT INTO event_store (
                        event_id, stream_id, tenant_id, event_type, event_version,
                        event_data, metadata, stream_version, created_at, constitutional_hash
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, event_rows)
                
                logger.info(
                    f"Appended {len(events)} events to stream {stream_id} "
                    f"for tenant {tenant_id}, new version: {new_version.value}"
                )
                
                return new_version
    
    async def get_events(
        self,
        stream_id: str,
        tenant_id: TenantId,
        from_version: Optional[StreamVersion] = None,
        to_version: Optional[StreamVersion] = None
    ) -> List[DomainEvent]:
        """Get events from stream within version range."""
        async with self.pool.acquire() as conn:
            # Set tenant context for RLS
            await conn.execute(
                "SELECT set_config('app.current_tenant_id', $1, true)",
                str(tenant_id)
            )
            
            # Build query with version filters
            query = """
                SELECT event_id, event_type, event_version, event_data, 
                       metadata, stream_version, created_at, constitutional_hash
                FROM event_store 
                WHERE stream_id = $1 AND tenant_id = $2
            """
            params = [stream_id, str(tenant_id)]
            
            if from_version is not None:
                query += " AND stream_version >= $3"
                params.append(from_version.value)
                
                if to_version is not None:
                    query += " AND stream_version <= $4"
                    params.append(to_version.value)
            elif to_version is not None:
                query += " AND stream_version <= $3"
                params.append(to_version.value)
            
            query += " ORDER BY stream_version ASC"
            
            rows = await conn.fetch(query, *params)
            
            # Convert rows to domain events
            events = []
            for row in rows:
                event = await self._row_to_domain_event(row)
                if event:
                    events.append(event)
            
            logger.debug(f"Retrieved {len(events)} events from stream {stream_id}")
            return events
    
    async def get_stream_version(
        self,
        stream_id: str,
        tenant_id: TenantId
    ) -> StreamVersion:
        """Get current version of stream."""
        async with self.pool.acquire() as conn:
            return await self._get_stream_version_in_transaction(conn, stream_id, tenant_id)
    
    async def _get_stream_version_in_transaction(
        self,
        conn: asyncpg.Connection,
        stream_id: str,
        tenant_id: TenantId
    ) -> StreamVersion:
        """Get stream version within a transaction."""
        # Set tenant context for RLS
        await conn.execute(
            "SELECT set_config('app.current_tenant_id', $1, true)",
            str(tenant_id)
        )
        
        row = await conn.fetchrow("""
            SELECT COALESCE(MAX(stream_version), 0) as current_version
            FROM event_store 
            WHERE stream_id = $1 AND tenant_id = $2
        """, stream_id, str(tenant_id))
        
        return StreamVersion(row['current_version'])
    
    async def stream_exists(
        self,
        stream_id: str,
        tenant_id: TenantId
    ) -> bool:
        """Check if stream exists."""
        async with self.pool.acquire() as conn:
            # Set tenant context for RLS
            await conn.execute(
                "SELECT set_config('app.current_tenant_id', $1, true)",
                str(tenant_id)
            )
            
            row = await conn.fetchrow("""
                SELECT EXISTS(
                    SELECT 1 FROM event_store 
                    WHERE stream_id = $1 AND tenant_id = $2
                )
            """, stream_id, str(tenant_id))
            
            return row[0]
    
    async def get_all_events_since(
        self,
        tenant_id: TenantId,
        since: datetime,
        event_types: Optional[List[str]] = None
    ) -> AsyncIterator[DomainEvent]:
        """Get all events since timestamp."""
        async with self.pool.acquire() as conn:
            # Set tenant context for RLS
            await conn.execute(
                "SELECT set_config('app.current_tenant_id', $1, true)",
                str(tenant_id)
            )
            
            query = """
                SELECT event_id, event_type, event_version, event_data, 
                       metadata, stream_version, created_at, constitutional_hash
                FROM event_store 
                WHERE tenant_id = $1 AND created_at >= $2
            """
            params = [str(tenant_id), since]
            
            if event_types:
                query += " AND event_type = ANY($3)"
                params.append(event_types)
            
            query += " ORDER BY created_at ASC"
            
            async with conn.transaction():
                async for row in conn.cursor(query, *params):
                    event = await self._row_to_domain_event(row)
                    if event:
                        yield event
    
    async def _row_to_domain_event(self, row) -> Optional[DomainEvent]:
        """Convert database row to domain event."""
        try:
            # This is a simplified conversion - in practice, you'd have
            # a registry of event types and their reconstruction methods
            
            event_type = row['event_type']
            event_data = json.loads(row['event_data'])
            metadata_dict = json.loads(row['metadata']) if row['metadata'] else None
            
            # For now, create a generic event wrapper
            # In practice, you'd reconstruct the specific event type
            from services.shared.domain.events import DomainEvent, EventMetadata
            
            metadata = None
            if metadata_dict:
                metadata = EventMetadata(
                    correlation_id=UUID(metadata_dict['correlation_id']),
                    causation_id=UUID(metadata_dict['causation_id']),
                    user_id=metadata_dict.get('user_id'),
                    tenant_id=TenantId.from_string(metadata_dict['tenant_id']) if metadata_dict.get('tenant_id') else None,
                    ip_address=metadata_dict.get('ip_address'),
                    user_agent=metadata_dict.get('user_agent')
                )
            
            # Create a generic event for reconstruction
            class GenericDomainEvent(DomainEvent):
                def __init__(self, event_type: str, event_data: Dict[str, Any], **kwargs):
                    super().__init__(**kwargs)
                    self.event_type = event_type
                    self._event_data = event_data
                
                def _get_event_version(self) -> str:
                    return "1.0"
                
                def get_event_data(self) -> Dict[str, Any]:
                    return self._event_data
            
            event = GenericDomainEvent(
                event_type=event_type,
                event_data=event_data,
                aggregate_id=EntityId(UUID(event_data.get('aggregate_id', str(UUID('00000000-0000-0000-0000-000000000000'))))),
                occurred_at=row['created_at'],
                metadata=metadata
            )
            
            # Verify constitutional hash
            if row['constitutional_hash'] != CONSTITUTIONAL_HASH:
                logger.warning(
                    f"Event {row['event_id']} has invalid constitutional hash: "
                    f"{row['constitutional_hash']}"
                )
                return None
            
            return event
            
        except Exception as e:
            logger.error(f"Failed to reconstruct event from row: {e}")
            return None


class EventStoreSnapshot:
    """Snapshot functionality for event store optimization."""
    
    def __init__(self, event_store: EventStore):
        """Initialize with event store."""
        self.event_store = event_store
    
    async def save_snapshot(
        self,
        stream_id: str,
        tenant_id: TenantId,
        aggregate_data: Dict[str, Any],
        stream_version: StreamVersion
    ) -> None:
        """Save aggregate snapshot for performance optimization."""
        # Implementation would save aggregate state snapshot
        # to avoid replaying all events
        pass
    
    async def get_snapshot(
        self,
        stream_id: str,
        tenant_id: TenantId
    ) -> Optional[tuple[Dict[str, Any], StreamVersion]]:
        """Get latest snapshot for aggregate."""
        # Implementation would retrieve latest snapshot
        return None


# Global event store instance
_event_store: Optional[EventStore] = None


def get_event_store() -> EventStore:
    """Get global event store instance."""
    if _event_store is None:
        raise RuntimeError("Event store not initialized")
    return _event_store


def set_event_store(event_store: EventStore) -> None:
    """Set global event store instance."""
    global _event_store
    _event_store = event_store