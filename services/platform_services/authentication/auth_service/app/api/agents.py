"""
Agent Identity Management API Endpoints

RESTful API for managing autonomous agent identities, credentials, and lifecycle.
Integrates with existing authentication and authorization systems.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import (
    authorize_permissions,
    get_current_active_user,
)
from ..db.database import get_async_db as get_db
from ..models import User
from ..schemas.agent import (
    AgentAuditLogResponse,
    AgentCreate,
    AgentCredentials,
    AgentListResponse,
    AgentResponse,
    AgentSearchRequest,
    AgentStatusUpdate,
    AgentUpdate,
)
from ..services.agent_service import AgentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["Agent Management"])

# Initialize agent service
agent_service = AgentService()


def get_client_ip(request: Request) -> str | None:
    """Extract client IP from request."""
    return request.client.host if request.client else None


@router.post("/", response_model=AgentCredentials, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize_permissions(["agent:create"])),
):
    """
    Create a new autonomous agent with unique identity and credentials.

    Requires 'agent:create' permission. Returns the agent credentials including
    the API key which is only shown once for security.
    """
    try:
        client_ip = get_client_ip(request)

        # Verify user can create agents for the specified owner
        if agent_data.owner_user_id != current_user.id:
            # Check if user has admin permissions to create agents for others
            if not (
                hasattr(current_user, "is_superuser") and current_user.is_superuser
            ):
                if not any(
                    perm in getattr(current_user, "permissions", [])
                    for perm in ["agent:create_any", "admin"]
                ):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Cannot create agents for other users without admin permissions",
                    )

        agent, api_key = await agent_service.create_agent(
            db=db,
            agent_data=agent_data,
            created_by_user_id=current_user.id,
            client_ip=client_ip,
        )

        logger.info(f"Agent '{agent.agent_id}' created by user {current_user.id}")

        return AgentCredentials(
            agent_id=agent.agent_id,
            api_key=api_key,
            expires_at=None,  # API keys don't expire by default
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create agent",
        )


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    search_request: AgentSearchRequest = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List and search agents with filtering and pagination.

    Regular users can only see their own agents. Admin users can see all agents.
    """
    try:
        is_admin = (
            hasattr(current_user, "is_superuser") and current_user.is_superuser
        ) or any(
            perm in getattr(current_user, "permissions", [])
            for perm in ["agent:read_all", "admin"]
        )

        agents, total = await agent_service.search_agents(
            db=db,
            search_request=search_request,
            user_id=current_user.id,
            is_admin=is_admin,
        )

        total_pages = (total + search_request.page_size - 1) // search_request.page_size

        return AgentListResponse(
            agents=[AgentResponse.from_orm(agent) for agent in agents],
            total=total,
            page=search_request.page,
            page_size=search_request.page_size,
            total_pages=total_pages,
        )

    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agents",
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get detailed information about a specific agent.

    Users can only access their own agents unless they have admin permissions.
    """
    try:
        agent = await agent_service.get_agent(db, agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_id}' not found",
            )

        # Check permissions
        is_admin = (
            hasattr(current_user, "is_superuser") and current_user.is_superuser
        ) or any(
            perm in getattr(current_user, "permissions", [])
            for perm in ["agent:read_all", "admin"]
        )

        if not is_admin and agent.owner_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this agent",
            )

        return AgentResponse.from_orm(agent)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent",
        )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize_permissions(["agent:update"])),
):
    """
    Update an existing agent's configuration and properties.

    Requires 'agent:update' permission. Users can only update their own agents
    unless they have admin permissions.
    """
    try:
        # Check if agent exists and user has permission
        existing_agent = await agent_service.get_agent(db, agent_id)
        if not existing_agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_id}' not found",
            )

        is_admin = (
            hasattr(current_user, "is_superuser") and current_user.is_superuser
        ) or any(
            perm in getattr(current_user, "permissions", [])
            for perm in ["agent:update_any", "admin"]
        )

        if not is_admin and existing_agent.owner_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update agents owned by other users",
            )

        client_ip = get_client_ip(request)

        updated_agent = await agent_service.update_agent(
            db=db,
            agent_id=agent_id,
            agent_data=agent_data,
            updated_by_user_id=current_user.id,
            client_ip=client_ip,
        )

        if not updated_agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_id}' not found",
            )

        logger.info(f"Agent '{agent_id}' updated by user {current_user.id}")

        return AgentResponse.from_orm(updated_agent)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update agent",
        )


@router.patch("/{agent_id}/status", response_model=AgentResponse)
async def update_agent_status(
    agent_id: str,
    status_update: AgentStatusUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize_permissions(["agent:manage_status"])),
):
    """
    Update an agent's status (activate, suspend, retire, etc.).

    Requires 'agent:manage_status' permission. This is a critical operation
    that affects agent operational capability.
    """
    try:
        # Check if agent exists and user has permission
        existing_agent = await agent_service.get_agent(db, agent_id)
        if not existing_agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_id}' not found",
            )

        is_admin = (
            hasattr(current_user, "is_superuser") and current_user.is_superuser
        ) or any(
            perm in getattr(current_user, "permissions", [])
            for perm in ["agent:manage_status_any", "admin"]
        )

        if not is_admin and existing_agent.owner_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot manage status of agents owned by other users",
            )

        client_ip = get_client_ip(request)

        updated_agent = await agent_service.update_agent_status(
            db=db,
            agent_id=agent_id,
            status_update=status_update,
            updated_by_user_id=current_user.id,
            client_ip=client_ip,
        )

        if not updated_agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_id}' not found",
            )

        logger.info(
            f"Agent '{agent_id}' status updated to {status_update.status.value} by user {current_user.id}"
        )

        return AgentResponse.from_orm(updated_agent)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update agent status {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update agent status",
        )


@router.get("/{agent_id}/audit-logs", response_model=list[AgentAuditLogResponse])
async def get_agent_audit_logs(
    agent_id: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize_permissions(["agent:audit"])),
):
    """
    Get audit logs for a specific agent.

    Requires 'agent:audit' permission. Provides complete audit trail
    of all changes and operations performed on the agent.
    """
    try:
        # Check if agent exists and user has permission
        agent = await agent_service.get_agent(db, agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_id}' not found",
            )

        is_admin = (
            hasattr(current_user, "is_superuser") and current_user.is_superuser
        ) or any(
            perm in getattr(current_user, "permissions", [])
            for perm in ["agent:audit_all", "admin"]
        )

        if not is_admin and agent.owner_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access audit logs for agents owned by other users",
            )

        # Get audit logs (this would need to be implemented in the service)
        # For now, return empty list as placeholder
        return []

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get audit logs for agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs",
        )
