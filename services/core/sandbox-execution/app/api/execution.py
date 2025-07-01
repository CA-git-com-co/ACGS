"""
Sandbox Execution API Endpoints

RESTful API for secure code execution in isolated environments.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.config import settings
from ..models.execution import SandboxExecution, ExecutionStatus, ExecutionEnvironment
from ..services.sandbox_manager import SandboxManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/executions", tags=["Sandbox Execution"])

# Initialize sandbox manager
sandbox_manager = SandboxManager()


# Pydantic models for API
class ExecutionRequest(BaseModel):
    """Request model for code execution."""

    agent_id: str = Field(..., description="ID of the requesting agent")
    agent_type: str = Field(..., description="Type of agent")
    environment: str = Field(
        ..., description="Execution environment (python, bash, node)"
    )
    code: str = Field(..., description="Code to execute")
    language: str = Field(..., description="Programming language")

    # Optional execution parameters
    execution_context: Optional[Dict[str, Any]] = Field(
        default=None, description="Execution context"
    )
    input_files: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Input files"
    )
    environment_variables: Optional[Dict[str, str]] = Field(
        default=None, description="Environment variables"
    )

    # Resource limits (optional overrides)
    memory_limit_mb: Optional[int] = Field(
        default=None, description="Memory limit in MB"
    )
    timeout_seconds: Optional[int] = Field(
        default=None, description="Execution timeout"
    )
    network_enabled: Optional[bool] = Field(
        default=False, description="Enable network access"
    )

    # Request metadata
    request_id: Optional[str] = Field(default=None, description="Request ID")
    session_id: Optional[str] = Field(default=None, description="Session ID")


class ExecutionResponse(BaseModel):
    """Response model for execution."""

    execution_id: str
    agent_id: str
    environment: str
    language: str
    status: str
    exit_code: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]
    execution_time_ms: Optional[int]
    memory_usage_mb: Optional[float]
    cpu_usage_percent: Optional[float]
    policy_violations: List[str]
    security_violations: List[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class ExecutionListResponse(BaseModel):
    """Response model for execution list."""

    executions: List[ExecutionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ExecutionStatsResponse(BaseModel):
    """Response model for execution statistics."""

    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_execution_time_ms: float
    environments: Dict[str, int]
    agents: Dict[str, int]


# Mock database dependency (replace with actual database session)
async def get_db() -> AsyncSession:
    """Get database session - placeholder implementation."""
    # This should be replaced with actual database connection
    pass


def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP from request."""
    return request.client.host if request.client else None


@router.post("/", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
async def create_execution(
    execution_request: ExecutionRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Create and execute code in a secure sandbox environment.

    This endpoint creates a new execution session and runs the provided code
    in an isolated container with security restrictions.
    """
    try:
        client_ip = get_client_ip(request)

        # Prepare request metadata
        request_metadata = {
            "request_id": execution_request.request_id,
            "session_id": execution_request.session_id,
            "client_ip": client_ip,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Validate environment
        if execution_request.environment not in [e.value for e in ExecutionEnvironment]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported environment: {execution_request.environment}",
            )

        # Create execution
        execution = await sandbox_manager.create_execution(
            db=db,
            agent_id=execution_request.agent_id,
            agent_type=execution_request.agent_type,
            environment=execution_request.environment,
            code=execution_request.code,
            language=execution_request.language,
            execution_context=execution_request.execution_context,
            input_files=execution_request.input_files,
            environment_variables=execution_request.environment_variables,
            request_metadata=request_metadata,
        )

        # Apply resource limit overrides if provided
        if execution_request.memory_limit_mb:
            execution.memory_limit_mb = execution_request.memory_limit_mb
        if execution_request.timeout_seconds:
            execution.timeout_seconds = execution_request.timeout_seconds
        if execution_request.network_enabled is not None:
            execution.network_enabled = execution_request.network_enabled

        await db.commit()

        # Execute code in background if no policy violations
        if not execution.policy_violations:
            background_tasks.add_task(execute_code_background, db, execution.id)

        logger.info(
            f"Execution created for agent {execution_request.agent_id}: {execution.execution_id}"
        )

        return ExecutionResponse(
            execution_id=execution.execution_id,
            agent_id=execution.agent_id,
            environment=execution.environment,
            language=execution.language,
            status=execution.status,
            exit_code=execution.exit_code,
            stdout=execution.stdout,
            stderr=execution.stderr,
            execution_time_ms=execution.execution_time_ms,
            memory_usage_mb=execution.memory_usage_mb,
            cpu_usage_percent=execution.cpu_usage_percent,
            policy_violations=execution.policy_violations or [],
            security_violations=execution.security_violations or [],
            created_at=execution.created_at.isoformat(),
            started_at=(
                execution.started_at.isoformat() if execution.started_at else None
            ),
            completed_at=(
                execution.completed_at.isoformat() if execution.completed_at else None
            ),
            error_message=execution.error_message,
        )

    except Exception as e:
        logger.error(f"Failed to create execution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create execution",
        )


@router.get("/", response_model=ExecutionListResponse)
async def list_executions(
    agent_id: Optional[str] = None,
    environment: Optional[str] = None,
    status_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """
    List executions with optional filtering and pagination.

    Supports filtering by agent_id, environment, and status.
    """
    try:
        # Build query with filters
        query = select(SandboxExecution)

        if agent_id:
            query = query.where(SandboxExecution.agent_id == agent_id)

        if environment:
            query = query.where(SandboxExecution.environment == environment)

        if status_filter:
            query = query.where(SandboxExecution.status == status_filter)

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(SandboxExecution.created_at.desc())

        # Execute query
        result = await db.execute(query)
        executions = result.scalars().all()

        # Get total count (simplified - in production use a count query)
        total = len(executions)  # Placeholder
        total_pages = (total + page_size - 1) // page_size

        return ExecutionListResponse(
            executions=[
                ExecutionResponse(
                    execution_id=execution.execution_id,
                    agent_id=execution.agent_id,
                    environment=execution.environment,
                    language=execution.language,
                    status=execution.status,
                    exit_code=execution.exit_code,
                    stdout=execution.stdout,
                    stderr=execution.stderr,
                    execution_time_ms=execution.execution_time_ms,
                    memory_usage_mb=execution.memory_usage_mb,
                    cpu_usage_percent=execution.cpu_usage_percent,
                    policy_violations=execution.policy_violations or [],
                    security_violations=execution.security_violations or [],
                    created_at=execution.created_at.isoformat(),
                    started_at=(
                        execution.started_at.isoformat()
                        if execution.started_at
                        else None
                    ),
                    completed_at=(
                        execution.completed_at.isoformat()
                        if execution.completed_at
                        else None
                    ),
                    error_message=execution.error_message,
                )
                for execution in executions
            ],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    except Exception as e:
        logger.error(f"Failed to list executions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve executions",
        )


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific execution."""
    try:
        result = await db.execute(
            select(SandboxExecution).where(
                SandboxExecution.execution_id == execution_id
            )
        )
        execution = result.scalar_one_or_none()

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution '{execution_id}' not found",
            )

        return ExecutionResponse(
            execution_id=execution.execution_id,
            agent_id=execution.agent_id,
            environment=execution.environment,
            language=execution.language,
            status=execution.status,
            exit_code=execution.exit_code,
            stdout=execution.stdout,
            stderr=execution.stderr,
            execution_time_ms=execution.execution_time_ms,
            memory_usage_mb=execution.memory_usage_mb,
            cpu_usage_percent=execution.cpu_usage_percent,
            policy_violations=execution.policy_violations or [],
            security_violations=execution.security_violations or [],
            created_at=execution.created_at.isoformat(),
            started_at=(
                execution.started_at.isoformat() if execution.started_at else None
            ),
            completed_at=(
                execution.completed_at.isoformat() if execution.completed_at else None
            ),
            error_message=execution.error_message,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get execution {execution_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve execution",
        )


@router.post("/{execution_id}/kill", status_code=status.HTTP_200_OK)
async def kill_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Kill a running execution.

    This forcefully terminates a running execution and its container.
    """
    try:
        # Get the execution
        result = await db.execute(
            select(SandboxExecution).where(
                SandboxExecution.execution_id == execution_id
            )
        )
        execution = result.scalar_one_or_none()

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution '{execution_id}' not found",
            )

        if execution.status not in [
            ExecutionStatus.RUNNING.value,
            ExecutionStatus.PENDING.value,
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Execution is not in a killable state (current status: {execution.status})",
            )

        # Kill the execution
        killed = await sandbox_manager.kill_execution(execution_id)

        if killed:
            # Update execution status
            execution.status = ExecutionStatus.KILLED.value
            execution.completed_at = datetime.utcnow()
            execution.error_message = "Execution killed by user request"
            await db.commit()

            logger.info(f"Execution {execution_id} killed")

            return {"message": f"Execution {execution_id} killed successfully"}
        else:
            return {
                "message": f"Execution {execution_id} could not be killed (may already be finished)"
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to kill execution {execution_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to kill execution",
        )


@router.get("/stats/summary", response_model=ExecutionStatsResponse)
async def get_execution_statistics(
    agent_id: Optional[str] = None,
    days: int = 7,
    db: AsyncSession = Depends(get_db),
):
    """Get execution statistics and metrics."""
    try:
        # This is a simplified implementation
        # In production, you would use proper aggregation queries

        # Get executions from the last N days
        cutoff_date = datetime.utcnow().date() - timedelta(days=days)

        query = select(SandboxExecution).where(
            SandboxExecution.created_at >= cutoff_date
        )

        if agent_id:
            query = query.where(SandboxExecution.agent_id == agent_id)

        result = await db.execute(query)
        executions = result.scalars().all()

        # Calculate statistics
        total_executions = len(executions)
        successful_executions = len(
            [e for e in executions if e.status == ExecutionStatus.COMPLETED.value]
        )
        failed_executions = len(
            [
                e
                for e in executions
                if e.status
                in [ExecutionStatus.FAILED.value, ExecutionStatus.ERROR.value]
            ]
        )

        # Calculate average execution time
        execution_times = [
            e.execution_time_ms for e in executions if e.execution_time_ms
        ]
        avg_execution_time_ms = (
            sum(execution_times) / len(execution_times) if execution_times else 0
        )

        # Count by environment
        environments = {}
        for execution in executions:
            env = execution.environment
            environments[env] = environments.get(env, 0) + 1

        # Count by agent
        agents = {}
        for execution in executions:
            agent = execution.agent_id
            agents[agent] = agents.get(agent, 0) + 1

        return ExecutionStatsResponse(
            total_executions=total_executions,
            successful_executions=successful_executions,
            failed_executions=failed_executions,
            avg_execution_time_ms=avg_execution_time_ms,
            environments=environments,
            agents=agents,
        )

    except Exception as e:
        logger.error(f"Failed to get execution statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics",
        )


async def execute_code_background(db: AsyncSession, execution_id: str):
    """Background task to execute code."""
    try:
        # Get execution from database
        result = await db.execute(
            select(SandboxExecution).where(SandboxExecution.id == execution_id)
        )
        execution = result.scalar_one_or_none()

        if execution:
            await sandbox_manager.execute_code(db, execution)
    except Exception as e:
        logger.error(f"Background execution failed for {execution_id}: {e}")
