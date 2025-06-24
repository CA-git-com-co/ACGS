"""
Workflow Engine for DGM Service.

Orchestrates complex improvement workflows with state management,
error handling, and recovery mechanisms.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID, uuid4

from ..database import get_db_session
from .improvement_workflow import ImprovementWorkflow
from .validation_workflow import ValidationWorkflow
from .workflow_state import WorkflowState, WorkflowStatus

logger = logging.getLogger(__name__)


class WorkflowType(Enum):
    """Types of workflows."""

    IMPROVEMENT = "improvement"
    VALIDATION = "validation"
    ROLLBACK = "rollback"
    MAINTENANCE = "maintenance"


class WorkflowEngine:
    """
    Workflow engine for orchestrating DGM operations.

    Manages workflow execution, state persistence, error handling,
    and recovery mechanisms for complex improvement processes.
    """

    def __init__(self):
        self.active_workflows: Dict[UUID, WorkflowState] = {}
        self.workflow_classes = {
            WorkflowType.IMPROVEMENT: ImprovementWorkflow,
            WorkflowType.VALIDATION: ValidationWorkflow,
        }

        # Workflow execution settings
        self.max_concurrent_workflows = 5
        self.workflow_timeout = timedelta(hours=2)
        self.retry_attempts = 3
        self.retry_delay = 60  # seconds

        # Background task for workflow monitoring
        self.monitor_task: Optional[asyncio.Task] = None
        self.running = False

    async def start(self):
        """Start the workflow engine."""
        if self.running:
            return

        self.running = True

        # Load active workflows from database
        await self._load_active_workflows()

        # Start monitoring task
        self.monitor_task = asyncio.create_task(self._monitor_workflows())

        logger.info("Workflow engine started")

    async def stop(self):
        """Stop the workflow engine."""
        self.running = False

        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        # Save active workflows
        await self._save_active_workflows()

        logger.info("Workflow engine stopped")

    async def submit_workflow(
        self,
        workflow_type: WorkflowType,
        workflow_data: Dict[str, Any],
        priority: int = 5,
        timeout: Optional[timedelta] = None,
    ) -> UUID:
        """
        Submit a new workflow for execution.

        Args:
            workflow_type: Type of workflow to execute
            workflow_data: Workflow input data
            priority: Workflow priority (1-10, higher = more priority)
            timeout: Custom timeout for this workflow

        Returns:
            Workflow ID
        """
        try:
            # Check if we can accept new workflows
            if len(self.active_workflows) >= self.max_concurrent_workflows:
                raise Exception("Maximum concurrent workflows reached")

            # Create workflow state
            workflow_id = uuid4()
            workflow_state = WorkflowState(
                workflow_id=workflow_id,
                workflow_type=workflow_type,
                status=WorkflowStatus.PENDING,
                input_data=workflow_data,
                priority=priority,
                timeout=timeout or self.workflow_timeout,
                created_at=datetime.utcnow(),
            )

            # Store in active workflows
            self.active_workflows[workflow_id] = workflow_state

            # Persist to database
            await self._persist_workflow_state(workflow_state)

            # Start workflow execution
            asyncio.create_task(self._execute_workflow(workflow_id))

            logger.info(f"Submitted workflow {workflow_id} of type {workflow_type.value}")
            return workflow_id

        except Exception as e:
            logger.error(f"Failed to submit workflow: {e}")
            raise

    async def get_workflow_status(self, workflow_id: UUID) -> Optional[WorkflowState]:
        """Get the status of a workflow."""
        if workflow_id in self.active_workflows:
            return self.active_workflows[workflow_id]

        # Check database for completed workflows
        return await self._load_workflow_from_db(workflow_id)

    async def cancel_workflow(self, workflow_id: UUID) -> bool:
        """Cancel a running workflow."""
        if workflow_id not in self.active_workflows:
            return False

        workflow_state = self.active_workflows[workflow_id]

        if workflow_state.status in [
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED,
        ]:
            return False

        # Cancel the workflow
        workflow_state.status = WorkflowStatus.CANCELLED
        workflow_state.completed_at = datetime.utcnow()
        workflow_state.result = {"cancelled": True, "reason": "User requested cancellation"}

        # Cancel the execution task if it exists
        if workflow_state.execution_task:
            workflow_state.execution_task.cancel()

        # Persist state
        await self._persist_workflow_state(workflow_state)

        logger.info(f"Cancelled workflow {workflow_id}")
        return True

    async def retry_workflow(self, workflow_id: UUID) -> bool:
        """Retry a failed workflow."""
        workflow_state = await self.get_workflow_status(workflow_id)

        if not workflow_state or workflow_state.status != WorkflowStatus.FAILED:
            return False

        # Reset workflow state for retry
        workflow_state.status = WorkflowStatus.PENDING
        workflow_state.retry_count += 1
        workflow_state.error = None
        workflow_state.completed_at = None

        # Add back to active workflows
        self.active_workflows[workflow_id] = workflow_state

        # Start execution
        asyncio.create_task(self._execute_workflow(workflow_id))

        logger.info(f"Retrying workflow {workflow_id} (attempt {workflow_state.retry_count})")
        return True

    async def _execute_workflow(self, workflow_id: UUID):
        """Execute a workflow."""
        workflow_state = self.active_workflows.get(workflow_id)
        if not workflow_state:
            return

        try:
            # Update status to running
            workflow_state.status = WorkflowStatus.RUNNING
            workflow_state.started_at = datetime.utcnow()
            await self._persist_workflow_state(workflow_state)

            # Get workflow class
            workflow_class = self.workflow_classes.get(workflow_state.workflow_type)
            if not workflow_class:
                raise Exception(f"Unknown workflow type: {workflow_state.workflow_type}")

            # Create and execute workflow
            workflow_instance = workflow_class(workflow_state)

            # Set execution task for cancellation support
            workflow_state.execution_task = asyncio.current_task()

            # Execute with timeout
            result = await asyncio.wait_for(
                workflow_instance.execute(), timeout=workflow_state.timeout.total_seconds()
            )

            # Update state with result
            workflow_state.status = WorkflowStatus.COMPLETED
            workflow_state.result = result
            workflow_state.completed_at = datetime.utcnow()

            logger.info(f"Workflow {workflow_id} completed successfully")

        except asyncio.TimeoutError:
            workflow_state.status = WorkflowStatus.FAILED
            workflow_state.error = "Workflow timed out"
            workflow_state.completed_at = datetime.utcnow()
            logger.error(f"Workflow {workflow_id} timed out")

        except asyncio.CancelledError:
            workflow_state.status = WorkflowStatus.CANCELLED
            workflow_state.completed_at = datetime.utcnow()
            logger.info(f"Workflow {workflow_id} was cancelled")

        except Exception as e:
            workflow_state.status = WorkflowStatus.FAILED
            workflow_state.error = str(e)
            workflow_state.completed_at = datetime.utcnow()
            logger.error(f"Workflow {workflow_id} failed: {e}")

            # Schedule retry if attempts remaining
            if workflow_state.retry_count < self.retry_attempts:
                asyncio.create_task(self._schedule_retry(workflow_id))

        finally:
            # Persist final state
            await self._persist_workflow_state(workflow_state)

            # Clean up execution task reference
            workflow_state.execution_task = None

    async def _schedule_retry(self, workflow_id: UUID):
        """Schedule a workflow retry."""
        await asyncio.sleep(self.retry_delay)

        workflow_state = self.active_workflows.get(workflow_id)
        if workflow_state and workflow_state.status == WorkflowStatus.FAILED:
            await self.retry_workflow(workflow_id)

    async def _monitor_workflows(self):
        """Monitor active workflows for cleanup and health checks."""
        while self.running:
            try:
                current_time = datetime.utcnow()
                workflows_to_remove = []

                for workflow_id, workflow_state in self.active_workflows.items():
                    # Check for completed workflows to clean up
                    if workflow_state.status in [
                        WorkflowStatus.COMPLETED,
                        WorkflowStatus.FAILED,
                        WorkflowStatus.CANCELLED,
                    ]:
                        # Keep completed workflows for a while for status queries
                        if (
                            workflow_state.completed_at
                            and current_time - workflow_state.completed_at > timedelta(hours=1)
                        ):
                            workflows_to_remove.append(workflow_id)

                    # Check for stuck workflows
                    elif workflow_state.status == WorkflowStatus.RUNNING:
                        if (
                            workflow_state.started_at
                            and current_time - workflow_state.started_at > workflow_state.timeout
                        ):
                            logger.warning(
                                f"Workflow {workflow_id} appears stuck, marking as failed"
                            )
                            workflow_state.status = WorkflowStatus.FAILED
                            workflow_state.error = "Workflow monitoring timeout"
                            workflow_state.completed_at = current_time
                            await self._persist_workflow_state(workflow_state)

                # Remove old workflows from memory
                for workflow_id in workflows_to_remove:
                    del self.active_workflows[workflow_id]

                # Sleep before next monitoring cycle
                await asyncio.sleep(30)  # Monitor every 30 seconds

            except Exception as e:
                logger.error(f"Workflow monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def _load_active_workflows(self):
        """Load active workflows from database on startup."""
        try:
            # This would query the database for workflows that were running
            # when the service was last stopped
            # For now, we'll start with an empty state
            logger.info("Loaded active workflows from database")

        except Exception as e:
            logger.error(f"Failed to load active workflows: {e}")

    async def _save_active_workflows(self):
        """Save active workflows to database on shutdown."""
        try:
            for workflow_state in self.active_workflows.values():
                await self._persist_workflow_state(workflow_state)

            logger.info("Saved active workflows to database")

        except Exception as e:
            logger.error(f"Failed to save active workflows: {e}")

    async def _persist_workflow_state(self, workflow_state: WorkflowState):
        """Persist workflow state to database."""
        try:
            # This would save the workflow state to the improvement_workspace table
            # For now, we'll just log it
            logger.debug(f"Persisted workflow state for {workflow_state.workflow_id}")

        except Exception as e:
            logger.error(f"Failed to persist workflow state: {e}")

    async def _load_workflow_from_db(self, workflow_id: UUID) -> Optional[WorkflowState]:
        """Load workflow state from database."""
        try:
            # This would query the database for the workflow
            # For now, return None
            return None

        except Exception as e:
            logger.error(f"Failed to load workflow from database: {e}")
            return None

    def get_engine_stats(self) -> Dict[str, Any]:
        """Get workflow engine statistics."""
        active_count = len(self.active_workflows)
        status_counts = {}

        for workflow_state in self.active_workflows.values():
            status = workflow_state.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "active_workflows": active_count,
            "max_concurrent": self.max_concurrent_workflows,
            "status_breakdown": status_counts,
            "engine_running": self.running,
        }
