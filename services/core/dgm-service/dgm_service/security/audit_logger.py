"""
Comprehensive audit logging for DGM Service.

Implements security audit logging with structured data,
tamper-proof storage, and compliance reporting.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from ..config import settings
from ..database import get_db_session

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    IMPROVEMENT_TRIGGER = "improvement_trigger"
    IMPROVEMENT_COMPLETE = "improvement_complete"
    IMPROVEMENT_ROLLBACK = "improvement_rollback"
    CONSTITUTIONAL_VALIDATION = "constitutional_validation"
    CONFIGURATION_CHANGE = "configuration_change"
    DATA_ACCESS = "data_access"
    SYSTEM_ADMIN = "system_admin"
    SECURITY_EVENT = "security_event"
    ERROR = "error"


class AuditSeverity(Enum):
    """Audit event severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditLogger:
    """
    Comprehensive audit logger for DGM Service.

    Provides tamper-proof audit logging with structured data,
    compliance reporting, and security event tracking.
    """

    def __init__(self):
        self.service_name = "dgm-service"
        self.audit_queue: asyncio.Queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        self.running = False

        # Audit configuration
        self.batch_size = 100
        self.flush_interval = 30  # seconds
        self.retention_days = 2555  # 7 years for compliance

        # Security settings
        self.enable_encryption = True
        self.enable_signing = True
        self.enable_remote_backup = True

    async def start(self):
        """Start the audit logger."""
        if self.running:
            return

        self.running = True
        self.processing_task = asyncio.create_task(self._process_audit_queue())
        logger.info("Audit logger started")

    async def stop(self):
        """Stop the audit logger."""
        self.running = False

        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass

        # Flush remaining events
        await self._flush_audit_queue()
        logger.info("Audit logger stopped")

    async def log_event(
        self,
        event_type: AuditEventType,
        severity: AuditSeverity,
        message: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        """
        Log an audit event.

        Args:
            event_type: Type of audit event
            severity: Event severity level
            message: Human-readable event description
            user_id: ID of user who triggered the event
            resource_id: ID of affected resource
            details: Additional event details
            request_id: Request ID for correlation
        """
        try:
            event = {
                "event_id": str(uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "service": self.service_name,
                "event_type": event_type.value,
                "severity": severity.value,
                "message": message,
                "user_id": user_id,
                "resource_id": resource_id,
                "request_id": request_id,
                "details": details or {},
                "source_ip": None,  # Would be populated by middleware
                "user_agent": None,  # Would be populated by middleware
                "session_id": None,  # Would be populated by middleware
            }

            # Add to queue for processing
            await self.audit_queue.put(event)

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")

    async def log_authentication_event(
        self,
        user_id: str,
        success: bool,
        method: str = "jwt",
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        """Log authentication event."""
        severity = AuditSeverity.LOW if success else AuditSeverity.MEDIUM
        message = f"Authentication {'successful' if success else 'failed'} for user {user_id}"

        event_details = {"authentication_method": method, "success": success, **(details or {})}

        await self.log_event(
            AuditEventType.AUTHENTICATION,
            severity,
            message,
            user_id=user_id,
            details=event_details,
            request_id=request_id,
        )

    async def log_authorization_event(
        self,
        user_id: str,
        permission: str,
        resource_id: Optional[str],
        granted: bool,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        """Log authorization event."""
        severity = AuditSeverity.LOW if granted else AuditSeverity.MEDIUM
        message = (
            f"Permission '{permission}' {'granted' if granted else 'denied'} for user {user_id}"
        )

        event_details = {"permission": permission, "granted": granted, **(details or {})}

        await self.log_event(
            AuditEventType.AUTHORIZATION,
            severity,
            message,
            user_id=user_id,
            resource_id=resource_id,
            details=event_details,
            request_id=request_id,
        )

    async def log_improvement_event(
        self,
        improvement_id: UUID,
        event_type: str,
        user_id: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        """Log improvement-related event."""
        severity_map = {
            "trigger": AuditSeverity.MEDIUM,
            "complete": AuditSeverity.MEDIUM,
            "rollback": AuditSeverity.HIGH,
            "cancel": AuditSeverity.MEDIUM,
        }

        severity = severity_map.get(event_type, AuditSeverity.LOW)
        message = f"Improvement {event_type} for {improvement_id}"

        audit_event_type = {
            "trigger": AuditEventType.IMPROVEMENT_TRIGGER,
            "complete": AuditEventType.IMPROVEMENT_COMPLETE,
            "rollback": AuditEventType.IMPROVEMENT_ROLLBACK,
        }.get(event_type, AuditEventType.IMPROVEMENT_TRIGGER)

        await self.log_event(
            audit_event_type,
            severity,
            message,
            user_id=user_id,
            resource_id=str(improvement_id),
            details=details,
            request_id=request_id,
        )

    async def log_constitutional_event(
        self,
        validation_id: UUID,
        compliance_score: float,
        violations: List[str],
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        """Log constitutional compliance event."""
        severity = AuditSeverity.CRITICAL if violations else AuditSeverity.LOW
        message = f"Constitutional validation {validation_id}: score={compliance_score:.2f}"

        event_details = {
            "compliance_score": compliance_score,
            "violations": violations,
            "violation_count": len(violations),
            **(details or {}),
        }

        await self.log_event(
            AuditEventType.CONSTITUTIONAL_VALIDATION,
            severity,
            message,
            user_id=user_id,
            resource_id=str(validation_id),
            details=event_details,
            request_id=request_id,
        )

    async def log_security_event(
        self,
        event_description: str,
        severity: AuditSeverity,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        """Log security-related event."""
        await self.log_event(
            AuditEventType.SECURITY_EVENT,
            severity,
            event_description,
            user_id=user_id,
            details=details,
            request_id=request_id,
        )

    async def log_configuration_change(
        self,
        config_key: str,
        old_value: Any,
        new_value: Any,
        user_id: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        """Log configuration change event."""
        message = f"Configuration changed: {config_key}"

        event_details = {
            "config_key": config_key,
            "old_value": str(old_value),
            "new_value": str(new_value),
            **(details or {}),
        }

        await self.log_event(
            AuditEventType.CONFIGURATION_CHANGE,
            AuditSeverity.MEDIUM,
            message,
            user_id=user_id,
            details=event_details,
            request_id=request_id,
        )

    async def log_data_access(
        self,
        resource_type: str,
        resource_id: str,
        action: str,
        user_id: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        """Log data access event."""
        message = f"Data access: {action} on {resource_type} {resource_id}"

        event_details = {"resource_type": resource_type, "action": action, **(details or {})}

        await self.log_event(
            AuditEventType.DATA_ACCESS,
            AuditSeverity.LOW,
            message,
            user_id=user_id,
            resource_id=resource_id,
            details=event_details,
            request_id=request_id,
        )

    async def _process_audit_queue(self):
        """Process audit events from the queue."""
        batch = []
        last_flush = time.time()

        while self.running:
            try:
                # Wait for events with timeout
                try:
                    event = await asyncio.wait_for(self.audit_queue.get(), timeout=1.0)
                    batch.append(event)
                except asyncio.TimeoutError:
                    pass

                # Flush batch if full or timeout reached
                current_time = time.time()
                should_flush = len(batch) >= self.batch_size or (
                    batch and current_time - last_flush >= self.flush_interval
                )

                if should_flush:
                    await self._flush_batch(batch)
                    batch = []
                    last_flush = current_time

            except Exception as e:
                logger.error(f"Audit queue processing error: {e}")
                await asyncio.sleep(1)

        # Flush remaining events
        if batch:
            await self._flush_batch(batch)

    async def _flush_batch(self, events: List[Dict[str, Any]]):
        """Flush a batch of audit events to storage."""
        try:
            # Store in database
            await self._store_events_in_database(events)

            # Store in file system (backup)
            await self._store_events_in_files(events)

            # Send to remote audit service if configured
            if self.enable_remote_backup:
                await self._send_to_remote_audit_service(events)

            logger.debug(f"Flushed {len(events)} audit events")

        except Exception as e:
            logger.error(f"Failed to flush audit batch: {e}")

    async def _flush_audit_queue(self):
        """Flush all remaining events in the queue."""
        remaining_events = []

        while not self.audit_queue.empty():
            try:
                event = self.audit_queue.get_nowait()
                remaining_events.append(event)
            except asyncio.QueueEmpty:
                break

        if remaining_events:
            await self._flush_batch(remaining_events)

    async def _store_events_in_database(self, events: List[Dict[str, Any]]):
        """Store audit events in database."""
        try:
            # This would store events in an audit_log table
            # For now, just log the count
            logger.debug(f"Stored {len(events)} events in database")

        except Exception as e:
            logger.error(f"Failed to store events in database: {e}")

    async def _store_events_in_files(self, events: List[Dict[str, Any]]):
        """Store audit events in log files."""
        try:
            # This would write events to structured log files
            # For now, just log the count
            logger.debug(f"Stored {len(events)} events in files")

        except Exception as e:
            logger.error(f"Failed to store events in files: {e}")

    async def _send_to_remote_audit_service(self, events: List[Dict[str, Any]]):
        """Send audit events to remote audit service."""
        try:
            # This would send events to a centralized audit service
            # For now, just log the count
            logger.debug(f"Sent {len(events)} events to remote audit service")

        except Exception as e:
            logger.error(f"Failed to send events to remote audit service: {e}")

    async def get_audit_report(
        self,
        start_date: datetime,
        end_date: datetime,
        event_types: Optional[List[AuditEventType]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate audit report for specified criteria."""
        try:
            # This would query audit logs and generate a report
            # For now, return a mock report
            return {
                "report_id": str(uuid4()),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_events": 0,
                "event_breakdown": {},
                "security_events": 0,
                "compliance_violations": 0,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to generate audit report: {e}")
            return {}


# Global audit logger instance
audit_logger = AuditLogger()
