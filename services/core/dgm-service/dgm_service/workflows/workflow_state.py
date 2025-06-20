"""
Workflow state management for DGM Service.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum
from dataclasses import dataclass, field


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class WorkflowState:
    """
    Workflow state container.
    
    Tracks the complete state of a workflow execution including
    input data, progress, results, and metadata.
    """
    
    # Core identifiers
    workflow_id: UUID
    workflow_type: 'WorkflowType'
    
    # Status and timing
    status: WorkflowStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout: timedelta = field(default_factory=lambda: timedelta(hours=2))
    
    # Data and results
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # Execution control
    priority: int = 5  # 1-10, higher = more priority
    retry_count: int = 0
    max_retries: int = 3
    
    # Progress tracking
    current_step: Optional[str] = None
    completed_steps: List[str] = field(default_factory=list)
    total_steps: Optional[int] = None
    progress_percentage: float = 0.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Runtime references (not persisted)
    execution_task: Optional[asyncio.Task] = field(default=None, init=False)
    
    def get_elapsed_time(self) -> Optional[timedelta]:
        """Get elapsed execution time."""
        if not self.started_at:
            return None
        
        end_time = self.completed_at or datetime.utcnow()
        return end_time - self.started_at
    
    def get_remaining_time(self) -> Optional[timedelta]:
        """Get remaining execution time before timeout."""
        if not self.started_at:
            return self.timeout
        
        elapsed = self.get_elapsed_time()
        if elapsed is None:
            return self.timeout
        
        remaining = self.timeout - elapsed
        return remaining if remaining.total_seconds() > 0 else timedelta(0)
    
    def is_timed_out(self) -> bool:
        """Check if workflow has timed out."""
        remaining = self.get_remaining_time()
        return remaining is not None and remaining.total_seconds() <= 0
    
    def is_terminal_status(self) -> bool:
        """Check if workflow is in a terminal status."""
        return self.status in [
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED
        ]
    
    def can_retry(self) -> bool:
        """Check if workflow can be retried."""
        return (
            self.status == WorkflowStatus.FAILED and
            self.retry_count < self.max_retries
        )
    
    def update_progress(self, step_name: str, percentage: Optional[float] = None):
        """Update workflow progress."""
        self.current_step = step_name
        
        if step_name not in self.completed_steps:
            self.completed_steps.append(step_name)
        
        if percentage is not None:
            self.progress_percentage = max(0.0, min(100.0, percentage))
        elif self.total_steps:
            self.progress_percentage = (len(self.completed_steps) / self.total_steps) * 100
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata entry."""
        self.metadata[key] = value
    
    def add_tag(self, tag: str):
        """Add a tag."""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "workflow_id": str(self.workflow_id),
            "workflow_type": self.workflow_type.value if hasattr(self.workflow_type, 'value') else str(self.workflow_type),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "timeout_seconds": self.timeout.total_seconds(),
            "input_data": self.input_data,
            "output_data": self.output_data,
            "result": self.result,
            "error": self.error,
            "priority": self.priority,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "current_step": self.current_step,
            "completed_steps": self.completed_steps,
            "total_steps": self.total_steps,
            "progress_percentage": self.progress_percentage,
            "metadata": self.metadata,
            "tags": self.tags,
            "elapsed_time_seconds": self.get_elapsed_time().total_seconds() if self.get_elapsed_time() else None,
            "remaining_time_seconds": self.get_remaining_time().total_seconds() if self.get_remaining_time() else None,
            "is_timed_out": self.is_timed_out(),
            "is_terminal": self.is_terminal_status(),
            "can_retry": self.can_retry()
        }


class WorkflowStep:
    """
    Base class for workflow steps.
    
    Provides structure for implementing individual workflow steps
    with progress tracking and error handling.
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        self.result: Optional[Dict[str, Any]] = None
    
    async def execute(self, workflow_state: WorkflowState) -> Dict[str, Any]:
        """Execute the workflow step."""
        self.started_at = datetime.utcnow()
        workflow_state.update_progress(self.name)
        
        try:
            result = await self._execute_step(workflow_state)
            self.result = result
            self.completed_at = datetime.utcnow()
            return result
            
        except Exception as e:
            self.error = str(e)
            self.completed_at = datetime.utcnow()
            raise
    
    async def _execute_step(self, workflow_state: WorkflowState) -> Dict[str, Any]:
        """Override this method to implement step logic."""
        raise NotImplementedError("Subclasses must implement _execute_step")
    
    def get_duration(self) -> Optional[timedelta]:
        """Get step execution duration."""
        if not self.started_at or not self.completed_at:
            return None
        return self.completed_at - self.started_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.get_duration().total_seconds() if self.get_duration() else None,
            "error": self.error,
            "result": self.result
        }
