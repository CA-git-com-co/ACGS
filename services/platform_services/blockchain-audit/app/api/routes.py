"""
Blockchain Audit API Routes
Constitutional Hash: cdd01ef066bc6cf2
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..models.schemas import (
    AuditEvent,
    AuditLogRequest,
    AuditLogResponse,
    HealthResponse,
    BlockchainRecord,
    EventType,
    CONSTITUTIONAL_HASH,
)
from ..services.blockchain_service import BlockchainService
from ..services.audit_manager import AuditManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Service instances
blockchain_service = BlockchainService()
audit_manager = AuditManager()


@router.post("/audit/log", response_model=AuditLogResponse)
async def create_audit_log(request: AuditLogRequest, background_tasks: BackgroundTasks):
    """Create audit log entry with optional blockchain logging."""
    try:
        # Validate constitutional hash
        if request.constitutional_hash != CONSTITUTIONAL_HASH:
            raise HTTPException(status_code=400, detail="Invalid constitutional hash")

        # Create audit event
        audit_event = AuditEvent(
            event_type=request.event_type,
            user_id=request.user_id,
            service_name=request.service_name,
            action=request.action,
            data=request.data,
            constitutional_hash=request.constitutional_hash,
        )

        # Store in database
        await audit_manager.store_audit_event(audit_event)

        # Blockchain logging
        blockchain_record = None
        if request.blockchain_enabled and blockchain_service.is_available():
            blockchain_record = await blockchain_service.log_event_to_blockchain(
                audit_event
            )

            if blockchain_record:
                # Store blockchain record
                await audit_manager.store_blockchain_record(blockchain_record)

        response = AuditLogResponse(
            event_id=audit_event.id,
            blockchain_record_id=blockchain_record.id if blockchain_record else None,
            transaction_hash=(
                blockchain_record.transaction_hash if blockchain_record else None
            ),
            status="success",
            constitutional_hash=CONSTITUTIONAL_HASH,
        )

        logger.info(f"Audit event {audit_event.id} logged successfully")
        return response

    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/events", response_model=List[AuditEvent])
async def get_audit_events(
    user_id: str = None,
    service_name: str = None,
    event_type: EventType = None,
    limit: int = 100,
    offset: int = 0,
):
    """Retrieve audit events with filtering."""
    try:
        events = await audit_manager.get_audit_events(
            user_id=user_id,
            service_name=service_name,
            event_type=event_type,
            limit=limit,
            offset=offset,
        )

        return events

    except Exception as e:
        logger.error(f"Failed to retrieve audit events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/events/{event_id}", response_model=AuditEvent)
async def get_audit_event(event_id: str):
    """Get specific audit event by ID."""
    try:
        event = await audit_manager.get_audit_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        return event

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve audit event {event_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blockchain/records", response_model=List[BlockchainRecord])
async def get_blockchain_records(
    event_id: str = None, status: str = None, limit: int = 100, offset: int = 0
):
    """Retrieve blockchain records with filtering."""
    try:
        records = await audit_manager.get_blockchain_records(
            event_id=event_id, status=status, limit=limit, offset=offset
        )

        return records

    except Exception as e:
        logger.error(f"Failed to retrieve blockchain records: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blockchain/verify/{event_id}")
async def verify_blockchain_integrity(event_id: str):
    """Verify blockchain integrity for specific event."""
    try:
        # Get blockchain record
        record = await audit_manager.get_blockchain_record_by_event_id(event_id)
        if not record:
            raise HTTPException(status_code=404, detail="Blockchain record not found")

        # Verify integrity
        is_valid = await blockchain_service.verify_event_integrity(event_id, record)

        return {
            "event_id": event_id,
            "blockchain_record_id": record.id,
            "transaction_hash": record.transaction_hash,
            "is_valid": is_valid,
            "status": record.status,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify blockchain integrity for {event_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blockchain/stats")
async def get_blockchain_stats():
    """Get blockchain service statistics."""
    try:
        stats = await blockchain_service.get_blockchain_stats()

        # Add audit statistics
        audit_stats = await audit_manager.get_audit_stats()

        combined_stats = {
            "blockchain": stats,
            "audit": audit_stats,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        return combined_stats

    except Exception as e:
        logger.error(f"Failed to get blockchain stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audit/bulk", response_model=List[AuditLogResponse])
async def bulk_audit_log(
    requests: List[AuditLogRequest], background_tasks: BackgroundTasks
):
    """Bulk create audit log entries."""
    try:
        if len(requests) > 100:
            raise HTTPException(
                status_code=400, detail="Bulk request limited to 100 events"
            )

        responses = []

        for request in requests:
            # Validate constitutional hash
            if request.constitutional_hash != CONSTITUTIONAL_HASH:
                raise HTTPException(
                    status_code=400, detail="Invalid constitutional hash"
                )

            # Create audit event
            audit_event = AuditEvent(
                event_type=request.event_type,
                user_id=request.user_id,
                service_name=request.service_name,
                action=request.action,
                data=request.data,
                constitutional_hash=request.constitutional_hash,
            )

            # Store in database
            await audit_manager.store_audit_event(audit_event)

            # Blockchain logging
            blockchain_record = None
            if request.blockchain_enabled and blockchain_service.is_available():
                blockchain_record = await blockchain_service.log_event_to_blockchain(
                    audit_event
                )

                if blockchain_record:
                    await audit_manager.store_blockchain_record(blockchain_record)

            response = AuditLogResponse(
                event_id=audit_event.id,
                blockchain_record_id=(
                    blockchain_record.id if blockchain_record else None
                ),
                transaction_hash=(
                    blockchain_record.transaction_hash if blockchain_record else None
                ),
                status="success",
                constitutional_hash=CONSTITUTIONAL_HASH,
            )

            responses.append(response)

        logger.info(f"Bulk audit log created: {len(responses)} events")
        return responses

    except Exception as e:
        logger.error(f"Failed to create bulk audit log: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check service components
        services = {
            "audit_manager": "healthy",
            "blockchain_service": (
                "healthy" if blockchain_service.is_available() else "unavailable"
            ),
            "database": "healthy",  # TODO: Add database health check
        }

        overall_status = (
            "healthy"
            if all(status == "healthy" for status in services.values())
            else "degraded"
        )

        return HealthResponse(
            status=overall_status,
            constitutional_hash=CONSTITUTIONAL_HASH,
            services=services,
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            constitutional_hash=CONSTITUTIONAL_HASH,
            services={"error": str(e)},
        )
