"""
Audit Manager - Handles database operations for audit events
Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Integer, select, func, and_, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..models.schemas import (
    AuditEvent,
    BlockchainRecord,
    EventType,
    BlockchainNetwork,
    CONSTITUTIONAL_HASH
)

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

class AuditEventTable(Base):
    __tablename__ = "audit_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False)
    user_id = Column(String(255), nullable=False)
    service_name = Column(String(255), nullable=False)
    action = Column(String(255), nullable=False)
    data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    constitutional_hash = Column(String(50), nullable=False)
    tenant_id = Column(String(255), nullable=True)  # Multi-tenant support

class BlockchainRecordTable(Base):
    __tablename__ = "blockchain_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    blockchain_network = Column(String(50), nullable=False)
    transaction_hash = Column(String(255), nullable=False)
    block_number = Column(Integer, nullable=True)
    contract_address = Column(String(255), nullable=True)
    gas_used = Column(Integer, nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    constitutional_hash = Column(String(50), nullable=False)
    tenant_id = Column(String(255), nullable=True)  # Multi-tenant support

class AuditManager:
    """Manager for audit event database operations."""
    
    def __init__(self, database_url: str = "postgresql+asyncpg://postgres:test_password@localhost:5439/acgs_audit"):
        self.database_url = database_url
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        self.constitutional_hash = CONSTITUTIONAL_HASH
    
    async def initialize_database(self):
        """Initialize database tables."""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def store_audit_event(self, event: AuditEvent) -> bool:
        """Store audit event in database."""
        try:
            async with self.async_session() as session:
                db_event = AuditEventTable(
                    id=event.id,
                    event_type=event.event_type.value,
                    user_id=event.user_id,
                    service_name=event.service_name,
                    action=event.action,
                    data=event.data,
                    timestamp=event.timestamp,
                    constitutional_hash=event.constitutional_hash
                )
                
                session.add(db_event)
                await session.commit()
                
                logger.info(f"Stored audit event {event.id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to store audit event {event.id}: {e}")
            return False
    
    async def store_blockchain_record(self, record: BlockchainRecord) -> bool:
        """Store blockchain record in database."""
        try:
            async with self.async_session() as session:
                db_record = BlockchainRecordTable(
                    id=record.id,
                    event_id=record.event_id,
                    blockchain_network=record.blockchain_network.value,
                    transaction_hash=record.transaction_hash,
                    block_number=record.block_number,
                    contract_address=record.contract_address,
                    gas_used=record.gas_used,
                    status=record.status,
                    created_at=record.created_at,
                    constitutional_hash=record.constitutional_hash
                )
                
                session.add(db_record)
                await session.commit()
                
                logger.info(f"Stored blockchain record {record.id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to store blockchain record {record.id}: {e}")
            return False
    
    async def get_audit_events(
        self,
        user_id: str = None,
        service_name: str = None,
        event_type: EventType = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditEvent]:
        """Retrieve audit events with filtering."""
        try:
            async with self.async_session() as session:
                query = select(AuditEventTable)
                
                # Apply filters
                conditions = []
                if user_id:
                    conditions.append(AuditEventTable.user_id == user_id)
                if service_name:
                    conditions.append(AuditEventTable.service_name == service_name)
                if event_type:
                    conditions.append(AuditEventTable.event_type == event_type.value)
                
                if conditions:
                    query = query.where(and_(*conditions))
                
                # Add ordering and pagination
                query = query.order_by(AuditEventTable.timestamp.desc())
                query = query.offset(offset).limit(limit)
                
                result = await session.execute(query)
                db_events = result.scalars().all()
                
                # Convert to Pydantic models
                events = []
                for db_event in db_events:
                    event = AuditEvent(
                        id=str(db_event.id),
                        event_type=EventType(db_event.event_type),
                        user_id=db_event.user_id,
                        service_name=db_event.service_name,
                        action=db_event.action,
                        data=db_event.data or {},
                        timestamp=db_event.timestamp,
                        constitutional_hash=db_event.constitutional_hash
                    )
                    events.append(event)
                
                return events
                
        except Exception as e:
            logger.error(f"Failed to retrieve audit events: {e}")
            return []
    
    async def get_audit_event_by_id(self, event_id: str) -> Optional[AuditEvent]:
        """Get specific audit event by ID."""
        try:
            async with self.async_session() as session:
                query = select(AuditEventTable).where(AuditEventTable.id == event_id)
                result = await session.execute(query)
                db_event = result.scalar_one_or_none()
                
                if not db_event:
                    return None
                
                event = AuditEvent(
                    id=str(db_event.id),
                    event_type=EventType(db_event.event_type),
                    user_id=db_event.user_id,
                    service_name=db_event.service_name,
                    action=db_event.action,
                    data=db_event.data or {},
                    timestamp=db_event.timestamp,
                    constitutional_hash=db_event.constitutional_hash
                )
                
                return event
                
        except Exception as e:
            logger.error(f"Failed to retrieve audit event {event_id}: {e}")
            return None
    
    async def get_blockchain_records(
        self,
        event_id: str = None,
        status: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[BlockchainRecord]:
        """Retrieve blockchain records with filtering."""
        try:
            async with self.async_session() as session:
                query = select(BlockchainRecordTable)
                
                # Apply filters
                conditions = []
                if event_id:
                    conditions.append(BlockchainRecordTable.event_id == event_id)
                if status:
                    conditions.append(BlockchainRecordTable.status == status)
                
                if conditions:
                    query = query.where(and_(*conditions))
                
                # Add ordering and pagination
                query = query.order_by(BlockchainRecordTable.created_at.desc())
                query = query.offset(offset).limit(limit)
                
                result = await session.execute(query)
                db_records = result.scalars().all()
                
                # Convert to Pydantic models
                records = []
                for db_record in db_records:
                    record = BlockchainRecord(
                        id=str(db_record.id),
                        event_id=str(db_record.event_id),
                        blockchain_network=BlockchainNetwork(db_record.blockchain_network),
                        transaction_hash=db_record.transaction_hash,
                        block_number=db_record.block_number,
                        contract_address=db_record.contract_address,
                        gas_used=db_record.gas_used,
                        status=db_record.status,
                        created_at=db_record.created_at,
                        constitutional_hash=db_record.constitutional_hash
                    )
                    records.append(record)
                
                return records
                
        except Exception as e:
            logger.error(f"Failed to retrieve blockchain records: {e}")
            return []
    
    async def get_blockchain_record_by_event_id(self, event_id: str) -> Optional[BlockchainRecord]:
        """Get blockchain record by event ID."""
        try:
            async with self.async_session() as session:
                query = select(BlockchainRecordTable).where(BlockchainRecordTable.event_id == event_id)
                result = await session.execute(query)
                db_record = result.scalar_one_or_none()
                
                if not db_record:
                    return None
                
                record = BlockchainRecord(
                    id=str(db_record.id),
                    event_id=str(db_record.event_id),
                    blockchain_network=BlockchainNetwork(db_record.blockchain_network),
                    transaction_hash=db_record.transaction_hash,
                    block_number=db_record.block_number,
                    contract_address=db_record.contract_address,
                    gas_used=db_record.gas_used,
                    status=db_record.status,
                    created_at=db_record.created_at,
                    constitutional_hash=db_record.constitutional_hash
                )
                
                return record
                
        except Exception as e:
            logger.error(f"Failed to retrieve blockchain record for event {event_id}: {e}")
            return None
    
    async def get_audit_stats(self) -> Dict[str, Any]:
        """Get audit statistics."""
        try:
            async with self.async_session() as session:
                # Total events
                total_events_query = select(func.count(AuditEventTable.id))
                total_events_result = await session.execute(total_events_query)
                total_events = total_events_result.scalar()
                
                # Events by type
                events_by_type_query = select(
                    AuditEventTable.event_type,
                    func.count(AuditEventTable.id).label('count')
                ).group_by(AuditEventTable.event_type)
                events_by_type_result = await session.execute(events_by_type_query)
                events_by_type = {row.event_type: row.count for row in events_by_type_result}
                
                # Blockchain records
                total_blockchain_query = select(func.count(BlockchainRecordTable.id))
                total_blockchain_result = await session.execute(total_blockchain_query)
                total_blockchain = total_blockchain_result.scalar()
                
                # Blockchain status
                blockchain_status_query = select(
                    BlockchainRecordTable.status,
                    func.count(BlockchainRecordTable.id).label('count')
                ).group_by(BlockchainRecordTable.status)
                blockchain_status_result = await session.execute(blockchain_status_query)
                blockchain_status = {row.status: row.count for row in blockchain_status_result}
                
                stats = {
                    "total_events": total_events or 0,
                    "events_by_type": events_by_type,
                    "total_blockchain_records": total_blockchain or 0,
                    "blockchain_status": blockchain_status,
                    "constitutional_hash": self.constitutional_hash
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get audit stats: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_records(self, days_old: int = 90) -> int:
        """Clean up old audit records."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            async with self.async_session() as session:
                # Delete old audit events
                audit_delete_query = delete(AuditEventTable).where(
                    AuditEventTable.timestamp < cutoff_date
                )
                
                # Delete old blockchain records
                blockchain_delete_query = delete(BlockchainRecordTable).where(
                    BlockchainRecordTable.created_at < cutoff_date
                )
                
                audit_result = await session.execute(audit_delete_query)
                blockchain_result = await session.execute(blockchain_delete_query)
                
                await session.commit()
                
                total_deleted = audit_result.rowcount + blockchain_result.rowcount
                logger.info(f"Cleaned up {total_deleted} old records")
                
                return total_deleted
                
        except Exception as e:
            logger.error(f"Failed to cleanup old records: {e}")
            return 0
    
    async def health_check(self) -> bool:
        """Check database health."""
        try:
            async with self.async_session() as session:
                # Simple query to check connection
                result = await session.execute(select(1))
                result.scalar()
                return True
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False