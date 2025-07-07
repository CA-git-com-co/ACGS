"""
Saga Pattern Implementation for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Orchestrates complex workflows across multiple bounded contexts with compensation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Type, Union
from uuid import UUID, uuid4
import json
import logging
import asyncio
import asyncpg

from services.shared.domain.base import EntityId, TenantId, CONSTITUTIONAL_HASH
from services.shared.domain.events import DomainEvent, EventPublisher

logger = logging.getLogger(__name__)


class SagaStatus(str, Enum):
    """Status of a saga execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class StepStatus(str, Enum):
    """Status of individual saga steps."""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"


@dataclass
class SagaStep:
    """Represents a single step in a saga workflow."""
    step_id: str
    step_name: str
    action: str  # Action to execute (command type)
    action_data: Dict[str, Any]
    compensation_action: Optional[str] = None
    compensation_data: Optional[Dict[str, Any]] = None
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    
    def mark_started(self) -> None:
        """Mark step as started."""
        self.status = StepStatus.RUNNING
        self.started_at = datetime.utcnow()
    
    def mark_completed(self) -> None:
        """Mark step as completed."""
        self.status = StepStatus.COMPLETED
        self.completed_at = datetime.utcnow()
    
    def mark_failed(self, error: str) -> None:
        """Mark step as failed."""
        self.status = StepStatus.FAILED
        self.error_message = error
        self.retry_count += 1
    
    def mark_compensated(self) -> None:
        """Mark step as compensated."""
        self.status = StepStatus.COMPENSATED
    
    def can_retry(self) -> bool:
        """Check if step can be retried."""
        return self.retry_count < self.max_retries
    
    def is_timed_out(self) -> bool:
        """Check if step has timed out."""
        if not self.started_at:
            return False
        
        elapsed = datetime.utcnow() - self.started_at
        return elapsed.total_seconds() > self.timeout_seconds


@dataclass
class SagaDefinition:
    """Defines the structure and steps of a saga."""
    saga_type: str
    steps: List[SagaStep]
    description: str
    max_duration_minutes: int = 60
    
    def get_step_by_id(self, step_id: str) -> Optional[SagaStep]:
        """Get step by ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None


@dataclass
class SagaInstance:
    """Runtime instance of a saga execution."""
    saga_id: str
    tenant_id: TenantId
    saga_type: str
    status: SagaStatus
    steps: List[SagaStep]
    current_step_index: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    initiator: Optional[str] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    @classmethod
    def create(
        cls,
        saga_definition: SagaDefinition,
        tenant_id: TenantId,
        context_data: Dict[str, Any],
        correlation_id: Optional[str] = None,
        initiator: Optional[str] = None
    ) -> 'SagaInstance':
        """Create new saga instance from definition."""
        return cls(
            saga_id=str(uuid4()),
            tenant_id=tenant_id,
            saga_type=saga_definition.saga_type,
            status=SagaStatus.PENDING,
            steps=saga_definition.steps.copy(),
            current_step_index=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            context_data=context_data,
            correlation_id=correlation_id,
            initiator=initiator
        )
    
    def get_current_step(self) -> Optional[SagaStep]:
        """Get current step to execute."""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    def advance_to_next_step(self) -> bool:
        """Advance to next step. Returns False if no more steps."""
        self.current_step_index += 1
        self.updated_at = datetime.utcnow()
        return self.current_step_index < len(self.steps)
    
    def mark_completed(self) -> None:
        """Mark saga as completed."""
        self.status = SagaStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_failed(self) -> None:
        """Mark saga as failed."""
        self.status = SagaStatus.FAILED
        self.updated_at = datetime.utcnow()
    
    def start_compensation(self) -> None:
        """Start compensation process."""
        self.status = SagaStatus.COMPENSATING
        self.updated_at = datetime.utcnow()
    
    def mark_compensated(self) -> None:
        """Mark saga as compensated."""
        self.status = SagaStatus.COMPENSATED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def get_completed_steps(self) -> List[SagaStep]:
        """Get all completed steps (for compensation)."""
        return [
            step for step in self.steps 
            if step.status == StepStatus.COMPLETED
        ]
    
    def is_expired(self, max_duration_minutes: int = 60) -> bool:
        """Check if saga has expired."""
        elapsed = datetime.utcnow() - self.created_at
        return elapsed.total_seconds() > (max_duration_minutes * 60)


class SagaCommand(ABC):
    """Base class for saga commands."""
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the command.
        
        Args:
            context: Execution context data
            
        Returns:
            Result data to be added to context
        """
        pass
    
    @abstractmethod
    async def compensate(self, context: Dict[str, Any]) -> None:
        """
        Compensate for the command execution.
        
        Args:
            context: Execution context data
        """
        pass


class SagaOrchestrator:
    """Orchestrates saga execution across multiple services."""
    
    def __init__(
        self,
        saga_store: 'SagaStore',
        command_dispatcher: 'CommandDispatcher',
        event_publisher: EventPublisher
    ):
        """Initialize saga orchestrator."""
        self.saga_store = saga_store
        self.command_dispatcher = command_dispatcher
        self.event_publisher = event_publisher
        self._running_sagas: Dict[str, asyncio.Task] = {}
    
    async def start_saga(
        self,
        saga_definition: SagaDefinition,
        tenant_id: TenantId,
        context_data: Dict[str, Any],
        correlation_id: Optional[str] = None,
        initiator: Optional[str] = None
    ) -> str:
        """
        Start a new saga instance.
        
        Args:
            saga_definition: Definition of the saga workflow
            tenant_id: Tenant owning the saga
            context_data: Initial context data
            correlation_id: Optional correlation ID
            initiator: Optional initiator identifier
            
        Returns:
            Saga instance ID
        """
        # Create saga instance
        saga = SagaInstance.create(
            saga_definition=saga_definition,
            tenant_id=tenant_id,
            context_data=context_data,
            correlation_id=correlation_id,
            initiator=initiator
        )
        
        # Save to store
        await self.saga_store.save_saga(saga)
        
        # Start execution
        task = asyncio.create_task(self._execute_saga(saga.saga_id))
        self._running_sagas[saga.saga_id] = task
        
        logger.info(f"Started saga {saga.saga_id} of type {saga.saga_type}")
        
        # Publish saga started event
        await self._publish_saga_event("SagaStarted", saga)
        
        return saga.saga_id
    
    async def _execute_saga(self, saga_id: str) -> None:
        """Execute saga steps sequentially."""
        try:
            saga = await self.saga_store.get_saga(saga_id)
            if not saga:
                logger.error(f"Saga {saga_id} not found")
                return
            
            saga.status = SagaStatus.RUNNING
            await self.saga_store.save_saga(saga)
            
            logger.info(f"Executing saga {saga_id} with {len(saga.steps)} steps")
            
            # Execute steps sequentially
            while True:
                current_step = saga.get_current_step()
                if not current_step:
                    # All steps completed
                    saga.mark_completed()
                    await self.saga_store.save_saga(saga)
                    await self._publish_saga_event("SagaCompleted", saga)
                    logger.info(f"Saga {saga_id} completed successfully")
                    break
                
                # Execute current step
                success = await self._execute_step(saga, current_step)
                
                if success:
                    # Move to next step
                    saga.advance_to_next_step()
                    await self.saga_store.save_saga(saga)
                else:
                    # Step failed, start compensation
                    logger.error(f"Step {current_step.step_name} failed in saga {saga_id}")
                    await self._compensate_saga(saga)
                    break
        
        except Exception as e:
            logger.error(f"Error executing saga {saga_id}: {e}", exc_info=True)
            
            # Mark saga as failed and try compensation
            saga = await self.saga_store.get_saga(saga_id)
            if saga:
                saga.mark_failed()
                await self.saga_store.save_saga(saga)
                await self._compensate_saga(saga)
        
        finally:
            # Remove from running sagas
            self._running_sagas.pop(saga_id, None)
    
    async def _execute_step(self, saga: SagaInstance, step: SagaStep) -> bool:
        """
        Execute a single saga step.
        
        Returns True if step succeeded, False if failed.
        """
        logger.info(f"Executing step {step.step_name} in saga {saga.saga_id}")
        
        step.mark_started()
        await self.saga_store.save_saga(saga)
        
        try:
            # Prepare command context
            command_context = {
                **saga.context_data,
                "saga_id": saga.saga_id,
                "tenant_id": str(saga.tenant_id),
                "step_id": step.step_id,
                "correlation_id": saga.correlation_id
            }
            
            # Execute the command
            result = await self.command_dispatcher.dispatch(
                command_type=step.action,
                command_data=step.action_data,
                context=command_context,
                timeout=step.timeout_seconds
            )
            
            # Update context with result
            if result:
                saga.context_data.update(result)
            
            step.mark_completed()
            await self.saga_store.save_saga(saga)
            
            logger.info(f"Step {step.step_name} completed in saga {saga.saga_id}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Step {step.step_name} failed in saga {saga.saga_id}: {error_msg}")
            
            step.mark_failed(error_msg)
            await self.saga_store.save_saga(saga)
            
            # Check if we can retry
            if step.can_retry():
                logger.info(f"Retrying step {step.step_name} (attempt {step.retry_count + 1})")
                return await self._execute_step(saga, step)
            
            return False
    
    async def _compensate_saga(self, saga: SagaInstance) -> None:
        """Compensate saga by reversing completed steps."""
        logger.info(f"Starting compensation for saga {saga.saga_id}")
        
        saga.start_compensation()
        await self.saga_store.save_saga(saga)
        await self._publish_saga_event("SagaCompensationStarted", saga)
        
        # Get completed steps in reverse order
        completed_steps = saga.get_completed_steps()
        completed_steps.reverse()
        
        compensation_failed = False
        
        for step in completed_steps:
            if not step.compensation_action:
                logger.warning(f"No compensation action for step {step.step_name}")
                continue
            
            try:
                logger.info(f"Compensating step {step.step_name} in saga {saga.saga_id}")
                
                # Prepare compensation context
                compensation_context = {
                    **saga.context_data,
                    "saga_id": saga.saga_id,
                    "tenant_id": str(saga.tenant_id),
                    "step_id": step.step_id,
                    "correlation_id": saga.correlation_id,
                    "original_action_data": step.action_data
                }
                
                # Execute compensation
                await self.command_dispatcher.dispatch(
                    command_type=step.compensation_action,
                    command_data=step.compensation_data or {},
                    context=compensation_context,
                    timeout=step.timeout_seconds
                )
                
                step.mark_compensated()
                await self.saga_store.save_saga(saga)
                
                logger.info(f"Compensated step {step.step_name} in saga {saga.saga_id}")
                
            except Exception as e:
                logger.error(
                    f"Failed to compensate step {step.step_name} in saga {saga.saga_id}: {e}",
                    exc_info=True
                )
                compensation_failed = True
                # Continue with other compensations
        
        if compensation_failed:
            logger.error(f"Compensation partially failed for saga {saga.saga_id}")
            await self._publish_saga_event("SagaCompensationFailed", saga)
        else:
            saga.mark_compensated()
            await self.saga_store.save_saga(saga)
            await self._publish_saga_event("SagaCompensated", saga)
            logger.info(f"Saga {saga.saga_id} compensated successfully")
    
    async def _publish_saga_event(self, event_type: str, saga: SagaInstance) -> None:
        """Publish saga lifecycle event."""
        try:
            # Create a generic saga event
            from services.shared.domain.events import DomainEvent
            
            class SagaEvent(DomainEvent):
                def __init__(self, event_type: str, saga: SagaInstance, **kwargs):
                    super().__init__(**kwargs)
                    self.event_type = event_type
                    self.saga_data = {
                        "saga_id": saga.saga_id,
                        "saga_type": saga.saga_type,
                        "status": saga.status.value,
                        "tenant_id": str(saga.tenant_id),
                        "correlation_id": saga.correlation_id,
                        "current_step_index": saga.current_step_index,
                        "total_steps": len(saga.steps)
                    }
                
                def _get_event_version(self) -> str:
                    return "1.0"
                
                def get_event_data(self) -> Dict[str, Any]:
                    return self.saga_data
            
            event = SagaEvent(
                event_type=event_type,
                saga=saga,
                aggregate_id=EntityId(UUID(saga.saga_id)),
                occurred_at=datetime.utcnow()
            )
            
            await self.event_publisher.publish(event)
            
        except Exception as e:
            logger.error(f"Failed to publish saga event {event_type}: {e}")
    
    async def get_saga_status(self, saga_id: str) -> Optional[SagaStatus]:
        """Get current status of a saga."""
        saga = await self.saga_store.get_saga(saga_id)
        return saga.status if saga else None
    
    async def cancel_saga(self, saga_id: str, reason: str) -> bool:
        """Cancel a running saga."""
        # Cancel running task
        if saga_id in self._running_sagas:
            task = self._running_sagas[saga_id]
            task.cancel()
        
        # Mark saga as failed and compensate
        saga = await self.saga_store.get_saga(saga_id)
        if saga and saga.status in [SagaStatus.PENDING, SagaStatus.RUNNING]:
            saga.mark_failed()
            await self.saga_store.save_saga(saga)
            await self._compensate_saga(saga)
            
            logger.info(f"Cancelled saga {saga_id}: {reason}")
            return True
        
        return False
    
    async def cleanup_expired_sagas(self, max_age_hours: int = 24) -> int:
        """Clean up expired sagas."""
        expired_sagas = await self.saga_store.get_expired_sagas(max_age_hours)
        cleanup_count = 0
        
        for saga in expired_sagas:
            try:
                await self.cancel_saga(saga.saga_id, "Expired due to timeout")
                cleanup_count += 1
            except Exception as e:
                logger.error(f"Failed to cleanup expired saga {saga.saga_id}: {e}")
        
        logger.info(f"Cleaned up {cleanup_count} expired sagas")
        return cleanup_count


class SagaStore(ABC):
    """Abstract interface for saga persistence."""
    
    @abstractmethod
    async def save_saga(self, saga: SagaInstance) -> None:
        """Save saga instance."""
        pass
    
    @abstractmethod
    async def get_saga(self, saga_id: str) -> Optional[SagaInstance]:
        """Get saga by ID."""
        pass
    
    @abstractmethod
    async def get_sagas_by_status(
        self,
        status: SagaStatus,
        tenant_id: Optional[TenantId] = None
    ) -> List[SagaInstance]:
        """Get sagas by status."""
        pass
    
    @abstractmethod
    async def get_expired_sagas(self, max_age_hours: int) -> List[SagaInstance]:
        """Get expired sagas for cleanup."""
        pass


class PostgreSQLSagaStore(SagaStore):
    """PostgreSQL implementation of saga store."""
    
    def __init__(self, connection_pool: asyncpg.Pool):
        """Initialize with database connection pool."""
        self.pool = connection_pool
    
    async def initialize(self) -> None:
        """Initialize database schema for saga store."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS sagas (
                    saga_id UUID PRIMARY KEY,
                    tenant_id UUID NOT NULL,
                    saga_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    current_step_index INTEGER NOT NULL DEFAULT 0,
                    context_data JSONB NOT NULL DEFAULT '{}',
                    correlation_id TEXT,
                    initiator TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    completed_at TIMESTAMPTZ,
                    constitutional_hash TEXT NOT NULL DEFAULT 'cdd01ef066bc6cf2'
                );
                
                CREATE TABLE IF NOT EXISTS saga_steps (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    saga_id UUID NOT NULL REFERENCES sagas(saga_id) ON DELETE CASCADE,
                    step_id TEXT NOT NULL,
                    step_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    action_data JSONB NOT NULL DEFAULT '{}',
                    compensation_action TEXT,
                    compensation_data JSONB,
                    status TEXT NOT NULL DEFAULT 'pending',
                    started_at TIMESTAMPTZ,
                    completed_at TIMESTAMPTZ,
                    error_message TEXT,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    max_retries INTEGER NOT NULL DEFAULT 3,
                    timeout_seconds INTEGER NOT NULL DEFAULT 300,
                    
                    UNIQUE(saga_id, step_id)
                );
                
                -- Enable RLS for multi-tenant isolation
                ALTER TABLE sagas ENABLE ROW LEVEL SECURITY;
                ALTER TABLE saga_steps ENABLE ROW LEVEL SECURITY;
                
                -- RLS policies
                DROP POLICY IF EXISTS saga_tenant_isolation ON sagas;
                CREATE POLICY saga_tenant_isolation ON sagas
                    FOR ALL TO application_role
                    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
                
                DROP POLICY IF EXISTS saga_steps_tenant_isolation ON saga_steps;
                CREATE POLICY saga_steps_tenant_isolation ON saga_steps
                    FOR ALL TO application_role
                    USING (
                        saga_id IN (
                            SELECT saga_id FROM sagas 
                            WHERE tenant_id = current_setting('app.current_tenant_id')::uuid
                        )
                    );
                
                -- Indexes
                CREATE INDEX IF NOT EXISTS idx_sagas_status_tenant 
                    ON sagas (tenant_id, status, created_at);
                
                CREATE INDEX IF NOT EXISTS idx_sagas_correlation 
                    ON sagas (correlation_id) WHERE correlation_id IS NOT NULL;
                
                CREATE INDEX IF NOT EXISTS idx_saga_steps_saga 
                    ON saga_steps (saga_id, step_id);
                
                -- Constitutional hash constraints
                ALTER TABLE sagas 
                ADD CONSTRAINT saga_constitutional_hash_check 
                CHECK (constitutional_hash = 'cdd01ef066bc6cf2');
            """)
    
    async def save_saga(self, saga: SagaInstance) -> None:
        """Save saga instance with all steps."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Set tenant context
                await conn.execute(
                    "SELECT set_config('app.current_tenant_id', $1, true)",
                    str(saga.tenant_id)
                )
                
                # Upsert saga
                await conn.execute("""
                    INSERT INTO sagas (
                        saga_id, tenant_id, saga_type, status, current_step_index,
                        context_data, correlation_id, initiator, created_at, 
                        updated_at, completed_at, constitutional_hash
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    ON CONFLICT (saga_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        current_step_index = EXCLUDED.current_step_index,
                        context_data = EXCLUDED.context_data,
                        updated_at = EXCLUDED.updated_at,
                        completed_at = EXCLUDED.completed_at
                """, 
                    UUID(saga.saga_id),
                    UUID(str(saga.tenant_id)),
                    saga.saga_type,
                    saga.status.value,
                    saga.current_step_index,
                    json.dumps(saga.context_data),
                    saga.correlation_id,
                    saga.initiator,
                    saga.created_at,
                    saga.updated_at,
                    saga.completed_at,
                    saga.constitutional_hash
                )
                
                # Delete existing steps
                await conn.execute(
                    "DELETE FROM saga_steps WHERE saga_id = $1",
                    UUID(saga.saga_id)
                )
                
                # Insert steps
                if saga.steps:
                    step_rows = []
                    for step in saga.steps:
                        step_rows.append((
                            UUID(saga.saga_id),
                            step.step_id,
                            step.step_name,
                            step.action,
                            json.dumps(step.action_data),
                            step.compensation_action,
                            json.dumps(step.compensation_data) if step.compensation_data else None,
                            step.status.value,
                            step.started_at,
                            step.completed_at,
                            step.error_message,
                            step.retry_count,
                            step.max_retries,
                            step.timeout_seconds
                        ))
                    
                    await conn.executemany("""
                        INSERT INTO saga_steps (
                            saga_id, step_id, step_name, action, action_data,
                            compensation_action, compensation_data, status,
                            started_at, completed_at, error_message, retry_count,
                            max_retries, timeout_seconds
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                    """, step_rows)
    
    async def get_saga(self, saga_id: str) -> Optional[SagaInstance]:
        """Get saga by ID with all steps."""
        async with self.pool.acquire() as conn:
            # Get saga
            saga_row = await conn.fetchrow(
                "SELECT * FROM sagas WHERE saga_id = $1",
                UUID(saga_id)
            )
            
            if not saga_row:
                return None
            
            # Set tenant context
            await conn.execute(
                "SELECT set_config('app.current_tenant_id', $1, true)",
                str(saga_row['tenant_id'])
            )
            
            # Get steps
            step_rows = await conn.fetch(
                "SELECT * FROM saga_steps WHERE saga_id = $1 ORDER BY step_id",
                UUID(saga_id)
            )
            
            # Convert to saga instance
            steps = []
            for step_row in step_rows:
                step = SagaStep(
                    step_id=step_row['step_id'],
                    step_name=step_row['step_name'],
                    action=step_row['action'],
                    action_data=json.loads(step_row['action_data']),
                    compensation_action=step_row['compensation_action'],
                    compensation_data=json.loads(step_row['compensation_data']) if step_row['compensation_data'] else None,
                    status=StepStatus(step_row['status']),
                    started_at=step_row['started_at'],
                    completed_at=step_row['completed_at'],
                    error_message=step_row['error_message'],
                    retry_count=step_row['retry_count'],
                    max_retries=step_row['max_retries'],
                    timeout_seconds=step_row['timeout_seconds']
                )
                steps.append(step)
            
            return SagaInstance(
                saga_id=str(saga_row['saga_id']),
                tenant_id=TenantId(saga_row['tenant_id']),
                saga_type=saga_row['saga_type'],
                status=SagaStatus(saga_row['status']),
                steps=steps,
                current_step_index=saga_row['current_step_index'],
                created_at=saga_row['created_at'],
                updated_at=saga_row['updated_at'],
                completed_at=saga_row['completed_at'],
                context_data=json.loads(saga_row['context_data']),
                correlation_id=saga_row['correlation_id'],
                initiator=saga_row['initiator'],
                constitutional_hash=saga_row['constitutional_hash']
            )
    
    async def get_sagas_by_status(
        self,
        status: SagaStatus,
        tenant_id: Optional[TenantId] = None
    ) -> List[SagaInstance]:
        """Get sagas by status."""
        async with self.pool.acquire() as conn:
            if tenant_id:
                await conn.execute(
                    "SELECT set_config('app.current_tenant_id', $1, true)",
                    str(tenant_id)
                )
                
                rows = await conn.fetch(
                    "SELECT saga_id FROM sagas WHERE status = $1 AND tenant_id = $2",
                    status.value,
                    UUID(str(tenant_id))
                )
            else:
                rows = await conn.fetch(
                    "SELECT saga_id FROM sagas WHERE status = $1",
                    status.value
                )
            
            sagas = []
            for row in rows:
                saga = await self.get_saga(str(row['saga_id']))
                if saga:
                    sagas.append(saga)
            
            return sagas
    
    async def get_expired_sagas(self, max_age_hours: int) -> List[SagaInstance]:
        """Get expired sagas for cleanup."""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT saga_id FROM sagas 
                WHERE created_at < $1 
                      AND status IN ('pending', 'running')
            """, cutoff_time)
            
            sagas = []
            for row in rows:
                saga = await self.get_saga(str(row['saga_id']))
                if saga:
                    sagas.append(saga)
            
            return sagas


class CommandDispatcher(ABC):
    """Abstract interface for dispatching commands to services."""
    
    @abstractmethod
    async def dispatch(
        self,
        command_type: str,
        command_data: Dict[str, Any],
        context: Dict[str, Any],
        timeout: int = 300
    ) -> Optional[Dict[str, Any]]:
        """
        Dispatch command to appropriate service.
        
        Args:
            command_type: Type of command to execute
            command_data: Command parameters
            context: Execution context
            timeout: Timeout in seconds
            
        Returns:
            Command execution result
        """
        pass


# Global saga instances
_saga_orchestrator: Optional[SagaOrchestrator] = None
_saga_store: Optional[SagaStore] = None


def get_saga_orchestrator() -> SagaOrchestrator:
    """Get global saga orchestrator instance."""
    if _saga_orchestrator is None:
        raise RuntimeError("Saga orchestrator not initialized")
    return _saga_orchestrator


def get_saga_store() -> SagaStore:
    """Get global saga store instance."""
    if _saga_store is None:
        raise RuntimeError("Saga store not initialized")
    return _saga_store


def set_saga_orchestrator(orchestrator: SagaOrchestrator) -> None:
    """Set global saga orchestrator instance."""
    global _saga_orchestrator
    _saga_orchestrator = orchestrator


def set_saga_store(store: SagaStore) -> None:
    """Set global saga store instance."""
    global _saga_store
    _saga_store = store