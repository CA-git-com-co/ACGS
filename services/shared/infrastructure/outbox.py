"""
Outbox Pattern Implementation for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Reliable event publishing using the transactional outbox pattern.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Callable
from uuid import UUID, uuid4
import json
import logging
import asyncio
import asyncpg

from services.shared.domain.base import TenantId, CONSTITUTIONAL_HASH
from services.shared.domain.events import DomainEvent, EventPublisher

logger = logging.getLogger(__name__)


@dataclass
class OutboxEntry:
    """Represents an entry in the outbox for reliable event publishing."""
    id: str
    tenant_id: TenantId
    event_id: str
    event_type: str
    event_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    processed: bool = False
    processed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    @classmethod
    def from_domain_event(
        cls,
        event: DomainEvent,
        tenant_id: TenantId
    ) -> 'OutboxEntry':
        """Create outbox entry from domain event."""
        return cls(
            id=str(uuid4()),
            tenant_id=tenant_id,
            event_id=str(event.event_id),
            event_type=event.event_type,
            event_data=event.get_event_data(),
            metadata=event.metadata.to_dict() if event.metadata else None,
            created_at=event.occurred_at
        )
    
    def mark_as_processed(self) -> None:
        """Mark entry as successfully processed."""
        self.processed = True
        self.processed_at = datetime.utcnow()
    
    def record_error(self, error: str) -> None:
        """Record processing error and increment retry count."""
        self.retry_count += 1
        self.last_error = error
    
    def can_retry(self) -> bool:
        """Check if entry can be retried."""
        return self.retry_count < self.max_retries
    
    def should_retry(self, retry_delay_minutes: int = 5) -> bool:
        """Check if enough time has passed for retry."""
        if not self.can_retry():
            return False
        
        if self.retry_count == 0:
            return True
        
        retry_threshold = self.created_at + timedelta(
            minutes=retry_delay_minutes * (2 ** (self.retry_count - 1))
        )
        return datetime.utcnow() >= retry_threshold


class OutboxPattern(ABC):
    """Abstract interface for outbox pattern implementation."""
    
    @abstractmethod
    async def add_events(
        self,
        events: List[DomainEvent],
        tenant_id: TenantId,
        transaction_context: Optional[Any] = None
    ) -> None:
        """
        Add events to outbox within a transaction.
        
        Args:
            events: Domain events to add
            tenant_id: Tenant owning the events
            transaction_context: Optional transaction context
        """
        pass
    
    @abstractmethod
    async def get_unprocessed_entries(
        self,
        tenant_id: Optional[TenantId] = None,
        limit: int = 100
    ) -> List[OutboxEntry]:
        """
        Get unprocessed outbox entries.
        
        Args:
            tenant_id: Optional tenant filter
            limit: Maximum number of entries to return
            
        Returns:
            List of unprocessed outbox entries
        """
        pass
    
    @abstractmethod
    async def mark_as_processed(
        self,
        entry_ids: List[str]
    ) -> None:
        """
        Mark entries as processed.
        
        Args:
            entry_ids: List of outbox entry IDs to mark as processed
        """
        pass
    
    @abstractmethod
    async def update_retry_info(
        self,
        entry_id: str,
        error: str
    ) -> None:
        """
        Update retry information for failed processing.
        
        Args:
            entry_id: Outbox entry ID
            error: Error message
        """
        pass
    
    @abstractmethod
    async def cleanup_old_entries(
        self,
        older_than_days: int = 30
    ) -> int:
        """
        Clean up old processed entries.
        
        Args:
            older_than_days: Remove entries older than this many days
            
        Returns:
            Number of entries cleaned up
        """
        pass


class PostgreSQLOutboxPattern(OutboxPattern):
    """PostgreSQL implementation of outbox pattern with multi-tenant support."""
    
    def __init__(self, connection_pool: asyncpg.Pool):
        """Initialize with database connection pool."""
        self.pool = connection_pool
    
    async def initialize(self) -> None:
        """Initialize database schema for outbox."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS outbox (
                    id UUID PRIMARY KEY,
                    tenant_id UUID NOT NULL,
                    event_id UUID NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data JSONB NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    processed BOOLEAN NOT NULL DEFAULT FALSE,
                    processed_at TIMESTAMPTZ,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    max_retries INTEGER NOT NULL DEFAULT 3,
                    last_error TEXT,
                    constitutional_hash TEXT NOT NULL DEFAULT 'cdd01ef066bc6cf2'
                );
                
                -- Enable RLS for multi-tenant isolation
                ALTER TABLE outbox ENABLE ROW LEVEL SECURITY;
                
                -- RLS policy for tenant isolation
                DROP POLICY IF EXISTS outbox_tenant_isolation ON outbox;
                CREATE POLICY outbox_tenant_isolation ON outbox
                    FOR ALL TO application_role
                    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
                
                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_outbox_unprocessed 
                    ON outbox (tenant_id, processed, created_at) 
                    WHERE NOT processed;
                
                CREATE INDEX IF NOT EXISTS idx_outbox_retry 
                    ON outbox (tenant_id, retry_count, created_at) 
                    WHERE NOT processed AND retry_count < max_retries;
                
                CREATE INDEX IF NOT EXISTS idx_outbox_cleanup 
                    ON outbox (processed, processed_at) 
                    WHERE processed;
                
                -- Constitutional hash constraint
                ALTER TABLE outbox 
                ADD CONSTRAINT outbox_constitutional_hash_check 
                CHECK (constitutional_hash = 'cdd01ef066bc6cf2');
            """)
    
    async def add_events(
        self,
        events: List[DomainEvent],
        tenant_id: TenantId,
        transaction_context: Optional[asyncpg.Connection] = None
    ) -> None:
        """Add events to outbox within transaction."""
        if not events:
            return
        
        # Convert events to outbox entries
        entries = [
            OutboxEntry.from_domain_event(event, tenant_id)
            for event in events
        ]
        
        # Determine connection to use
        if transaction_context:
            await self._insert_entries(transaction_context, entries, tenant_id)
        else:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    await self._insert_entries(conn, entries, tenant_id)
    
    async def _insert_entries(
        self,
        conn: asyncpg.Connection,
        entries: List[OutboxEntry],
        tenant_id: TenantId
    ) -> None:
        """Insert outbox entries using provided connection."""
        # Set tenant context for RLS
        await conn.execute(
            "SELECT set_config('app.current_tenant_id', $1, true)",
            str(tenant_id)
        )
        
        # Prepare data for batch insert
        entry_data = []
        for entry in entries:
            entry_data.append((
                UUID(entry.id),
                UUID(str(tenant_id)),
                UUID(entry.event_id),
                entry.event_type,
                json.dumps(entry.event_data),
                json.dumps(entry.metadata) if entry.metadata else None,
                entry.created_at,
                entry.processed,
                entry.processed_at,
                entry.retry_count,
                entry.max_retries,
                entry.last_error,
                entry.constitutional_hash
            ))
        
        # Batch insert
        await conn.executemany("""
            INSERT INTO outbox (
                id, tenant_id, event_id, event_type, event_data, metadata,
                created_at, processed, processed_at, retry_count, max_retries,
                last_error, constitutional_hash
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        """, entry_data)
        
        logger.debug(f"Added {len(entries)} events to outbox for tenant {tenant_id}")
    
    async def get_unprocessed_entries(
        self,
        tenant_id: Optional[TenantId] = None,
        limit: int = 100
    ) -> List[OutboxEntry]:
        """Get unprocessed outbox entries."""
        async with self.pool.acquire() as conn:
            # Build query based on tenant filter
            if tenant_id:
                # Set tenant context for RLS
                await conn.execute(
                    "SELECT set_config('app.current_tenant_id', $1, true)",
                    str(tenant_id)
                )
                
                query = """
                    SELECT id, tenant_id, event_id, event_type, event_data, metadata,
                           created_at, processed, processed_at, retry_count, max_retries,
                           last_error, constitutional_hash
                    FROM outbox 
                    WHERE tenant_id = $1 AND NOT processed 
                          AND retry_count < max_retries
                    ORDER BY created_at ASC
                    LIMIT $2
                """
                params = [str(tenant_id), limit]
            else:
                # Global query (for background processors)
                query = """
                    SELECT id, tenant_id, event_id, event_type, event_data, metadata,
                           created_at, processed, processed_at, retry_count, max_retries,
                           last_error, constitutional_hash
                    FROM outbox 
                    WHERE NOT processed AND retry_count < max_retries
                    ORDER BY created_at ASC
                    LIMIT $1
                """
                params = [limit]
            
            rows = await conn.fetch(query, *params)
            
            # Convert rows to outbox entries
            entries = []
            for row in rows:
                entry = OutboxEntry(
                    id=str(row['id']),
                    tenant_id=TenantId(row['tenant_id']),
                    event_id=str(row['event_id']),
                    event_type=row['event_type'],
                    event_data=json.loads(row['event_data']),
                    metadata=json.loads(row['metadata']) if row['metadata'] else None,
                    created_at=row['created_at'],
                    processed=row['processed'],
                    processed_at=row['processed_at'],
                    retry_count=row['retry_count'],
                    max_retries=row['max_retries'],
                    last_error=row['last_error'],
                    constitutional_hash=row['constitutional_hash']
                )
                entries.append(entry)
            
            return entries
    
    async def mark_as_processed(self, entry_ids: List[str]) -> None:
        """Mark entries as processed."""
        if not entry_ids:
            return
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE outbox 
                SET processed = TRUE, processed_at = NOW()
                WHERE id = ANY($1::uuid[])
            """, entry_ids)
            
            logger.debug(f"Marked {len(entry_ids)} outbox entries as processed")
    
    async def update_retry_info(self, entry_id: str, error: str) -> None:
        """Update retry information for failed processing."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE outbox 
                SET retry_count = retry_count + 1, 
                    last_error = $2
                WHERE id = $1
            """, UUID(entry_id), error)
            
            logger.debug(f"Updated retry info for outbox entry {entry_id}")
    
    async def cleanup_old_entries(self, older_than_days: int = 30) -> int:
        """Clean up old processed entries."""
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
        
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM outbox 
                WHERE processed = TRUE 
                      AND processed_at < $1
            """, cutoff_date)
            
            # Extract number of deleted rows from result
            deleted_count = int(result.split()[-1])
            
            logger.info(f"Cleaned up {deleted_count} old outbox entries")
            return deleted_count


class OutboxEventPublisher:
    """Event publisher that uses outbox pattern for reliable publishing."""
    
    def __init__(
        self,
        outbox: OutboxPattern,
        event_publisher: EventPublisher,
        batch_size: int = 50,
        processing_interval: float = 1.0
    ):
        """
        Initialize outbox event publisher.
        
        Args:
            outbox: Outbox pattern implementation
            event_publisher: Underlying event publisher
            batch_size: Number of events to process in each batch
            processing_interval: Seconds between processing cycles
        """
        self.outbox = outbox
        self.event_publisher = event_publisher
        self.batch_size = batch_size
        self.processing_interval = processing_interval
        self._processing_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
    
    async def publish_events_via_outbox(
        self,
        events: List[DomainEvent],
        tenant_id: TenantId,
        transaction_context: Optional[Any] = None
    ) -> None:
        """
        Publish events via outbox pattern.
        
        Events are first stored in the outbox within the same transaction
        as the aggregate changes, then published asynchronously.
        """
        await self.outbox.add_events(events, tenant_id, transaction_context)
        logger.debug(f"Added {len(events)} events to outbox for tenant {tenant_id}")
    
    async def start_background_processing(self) -> None:
        """Start background task to process outbox entries."""
        if self._processing_task and not self._processing_task.done():
            logger.warning("Background processing already started")
            return
        
        self._shutdown_event.clear()
        self._processing_task = asyncio.create_task(self._process_outbox_continuously())
        logger.info("Started outbox background processing")
    
    async def stop_background_processing(self) -> None:
        """Stop background processing gracefully."""
        if not self._processing_task or self._processing_task.done():
            return
        
        self._shutdown_event.set()
        
        try:
            await asyncio.wait_for(self._processing_task, timeout=10.0)
        except asyncio.TimeoutError:
            logger.warning("Background processing shutdown timed out, canceling task")
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped outbox background processing")
    
    async def _process_outbox_continuously(self) -> None:
        """Continuously process outbox entries."""
        while not self._shutdown_event.is_set():
            try:
                await self._process_outbox_batch()
                await asyncio.sleep(self.processing_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in outbox processing: {e}", exc_info=True)
                await asyncio.sleep(self.processing_interval * 2)  # Back off on error
    
    async def _process_outbox_batch(self) -> None:
        """Process a batch of outbox entries."""
        entries = await self.outbox.get_unprocessed_entries(limit=self.batch_size)
        
        if not entries:
            return
        
        logger.debug(f"Processing {len(entries)} outbox entries")
        
        successful_ids = []
        
        for entry in entries:
            try:
                # Reconstruct domain event from outbox entry
                event = await self._reconstruct_domain_event(entry)
                
                if event:
                    # Publish the event
                    await self.event_publisher.publish(event)
                    successful_ids.append(entry.id)
                    
                    logger.debug(f"Successfully published event {entry.event_id}")
                
            except Exception as e:
                logger.error(
                    f"Failed to publish event {entry.event_id}: {e}",
                    exc_info=True
                )
                
                # Update retry info
                await self.outbox.update_retry_info(entry.id, str(e))
        
        # Mark successful entries as processed
        if successful_ids:
            await self.outbox.mark_as_processed(successful_ids)
            logger.debug(f"Marked {len(successful_ids)} entries as processed")
    
    async def _reconstruct_domain_event(self, entry: OutboxEntry) -> Optional[DomainEvent]:
        """Reconstruct domain event from outbox entry."""
        try:
            # This is simplified - in practice, you'd have a registry
            # of event types and their reconstruction methods
            
            from services.shared.domain.events import DomainEvent, EventMetadata
            
            # Reconstruct metadata
            metadata = None
            if entry.metadata:
                metadata = EventMetadata(
                    correlation_id=UUID(entry.metadata['correlation_id']),
                    causation_id=UUID(entry.metadata['causation_id']),
                    user_id=entry.metadata.get('user_id'),
                    tenant_id=entry.tenant_id,
                    ip_address=entry.metadata.get('ip_address'),
                    user_agent=entry.metadata.get('user_agent')
                )
            
            # Create generic event for publishing
            class ReconstructedEvent(DomainEvent):
                def __init__(self, entry: OutboxEntry, **kwargs):
                    super().__init__(**kwargs)
                    self.event_type = entry.event_type
                    self._event_data = entry.event_data
                
                def _get_event_version(self) -> str:
                    return "1.0"
                
                def get_event_data(self) -> Dict[str, Any]:
                    return self._event_data
            
            from services.shared.domain.base import EntityId
            
            event = ReconstructedEvent(
                entry=entry,
                aggregate_id=EntityId(UUID(entry.event_id)),
                occurred_at=entry.created_at,
                metadata=metadata
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Failed to reconstruct event from outbox entry: {e}")
            return None


# Global outbox instances
_outbox_pattern: Optional[OutboxPattern] = None
_outbox_publisher: Optional[OutboxEventPublisher] = None


def get_outbox_pattern() -> OutboxPattern:
    """Get global outbox pattern instance."""
    if _outbox_pattern is None:
        raise RuntimeError("Outbox pattern not initialized")
    return _outbox_pattern


def get_outbox_publisher() -> OutboxEventPublisher:
    """Get global outbox publisher instance."""
    if _outbox_publisher is None:
        raise RuntimeError("Outbox publisher not initialized")
    return _outbox_publisher


def set_outbox_pattern(outbox: OutboxPattern) -> None:
    """Set global outbox pattern instance."""
    global _outbox_pattern
    _outbox_pattern = outbox


def set_outbox_publisher(publisher: OutboxEventPublisher) -> None:
    """Set global outbox publisher instance."""
    global _outbox_publisher
    _outbox_publisher = publisher