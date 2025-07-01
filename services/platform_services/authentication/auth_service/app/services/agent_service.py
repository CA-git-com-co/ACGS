"""
Agent Identity Management Service

Business logic layer for agent identity management operations.
Handles agent lifecycle, permissions, and integration with existing auth systems.
"""

import secrets
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any

from sqlalchemy import and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from ..core.security import get_password_hash, verify_password
from ..models.agent import Agent, AgentSession, AgentAuditLog, AgentStatus, AgentType
from ..models import User
from ..schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentSearchRequest,
    AgentStatusUpdate,
)


class AgentService:
    """Service class for agent identity management operations."""
    
    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
    
    async def create_agent(
        self,
        db: AsyncSession,
        agent_data: AgentCreate,
        created_by_user_id: int,
        client_ip: Optional[str] = None
    ) -> Tuple[Agent, str]:
        """
        Create a new agent with unique identity and credentials.
        
        Returns:
            Tuple of (Agent, api_key) - the api_key is only returned once
        """
        # Verify owner exists
        owner_result = await db.execute(select(User).where(User.id == agent_data.owner_user_id))
        owner = owner_result.scalar_one_or_none()
        if not owner:
            raise ValueError(f"Owner user with ID {agent_data.owner_user_id} not found")
        
        # Check if agent_id is unique
        existing_result = await db.execute(select(Agent).where(Agent.agent_id == agent_data.agent_id))
        if existing_result.scalar_one_or_none():
            raise ValueError(f"Agent with ID '{agent_data.agent_id}' already exists")
        
        # Generate API key for agent authentication
        api_key = self._generate_api_key()
        api_key_hash = get_password_hash(api_key)
        
        # Create agent instance
        agent = Agent(
            agent_id=agent_data.agent_id,
            name=agent_data.name,
            description=agent_data.description,
            agent_type=agent_data.agent_type.value,
            version=agent_data.version,
            status=AgentStatus.PENDING.value,
            owner_user_id=agent_data.owner_user_id,
            responsible_team=agent_data.responsible_team,
            contact_email=agent_data.contact_email,
            capabilities=agent_data.capabilities,
            permissions=agent_data.permissions,
            role_assignments=agent_data.role_assignments,
            api_key_hash=api_key_hash,
            allowed_services=agent_data.allowed_services,
            allowed_operations=agent_data.allowed_operations,
            ip_whitelist=agent_data.ip_whitelist,
            max_requests_per_minute=agent_data.max_requests_per_minute,
            max_concurrent_operations=agent_data.max_concurrent_operations,
            resource_quota=agent_data.resource_quota,
            constitutional_hash=self.constitutional_hash,
            compliance_level=agent_data.compliance_level,
            requires_human_approval=agent_data.requires_human_approval,
            configuration=agent_data.configuration,
            metadata=agent_data.metadata,
            tags=agent_data.tags,
        )
        
        db.add(agent)
        await db.flush()  # Get the agent ID
        
        # Create audit log entry
        await self._create_audit_log(
            db=db,
            agent_id=agent.id,
            event_type="created",
            event_description=f"Agent '{agent.agent_id}' created",
            performed_by_user_id=created_by_user_id,
            new_values={
                "agent_id": agent.agent_id,
                "name": agent.name,
                "agent_type": agent.agent_type,
                "owner_user_id": agent.owner_user_id,
                "status": agent.status,
            },
            client_ip=client_ip,
        )
        
        await db.commit()
        return agent, api_key
    
    async def get_agent(self, db: AsyncSession, agent_id: str) -> Optional[Agent]:
        """Get agent by agent_id."""
        result = await db.execute(
            select(Agent)
            .options(selectinload(Agent.owner))
            .where(Agent.agent_id == agent_id)
        )
        return result.scalar_one_or_none()
    
    async def get_agent_by_uuid(self, db: AsyncSession, uuid: uuid.UUID) -> Optional[Agent]:
        """Get agent by UUID."""
        result = await db.execute(
            select(Agent)
            .options(selectinload(Agent.owner))
            .where(Agent.id == uuid)
        )
        return result.scalar_one_or_none()
    
    async def update_agent(
        self,
        db: AsyncSession,
        agent_id: str,
        agent_data: AgentUpdate,
        updated_by_user_id: int,
        client_ip: Optional[str] = None
    ) -> Optional[Agent]:
        """Update an existing agent."""
        agent = await self.get_agent(db, agent_id)
        if not agent:
            return None
        
        # Store old values for audit
        old_values = {
            "name": agent.name,
            "description": agent.description,
            "agent_type": agent.agent_type,
            "version": agent.version,
            "capabilities": agent.capabilities,
            "permissions": agent.permissions,
            "allowed_services": agent.allowed_services,
            "allowed_operations": agent.allowed_operations,
        }
        
        # Update fields
        update_data = agent_data.dict(exclude_unset=True)
        new_values = {}
        
        for field, value in update_data.items():
            if hasattr(agent, field) and getattr(agent, field) != value:
                new_values[field] = value
                setattr(agent, field, value)
        
        if new_values:
            # Create audit log entry
            await self._create_audit_log(
                db=db,
                agent_id=agent.id,
                event_type="updated",
                event_description=f"Agent '{agent.agent_id}' updated",
                performed_by_user_id=updated_by_user_id,
                old_values=old_values,
                new_values=new_values,
                client_ip=client_ip,
            )
            
            await db.commit()
        
        return agent
    
    async def update_agent_status(
        self,
        db: AsyncSession,
        agent_id: str,
        status_update: AgentStatusUpdate,
        updated_by_user_id: int,
        client_ip: Optional[str] = None
    ) -> Optional[Agent]:
        """Update agent status with proper lifecycle management."""
        agent = await self.get_agent(db, agent_id)
        if not agent:
            return None
        
        old_status = agent.status
        new_status = status_update.status.value
        
        # Validate status transition
        if not self._is_valid_status_transition(old_status, new_status):
            raise ValueError(f"Invalid status transition from {old_status} to {new_status}")
        
        # Update status and related timestamps
        agent.status = new_status
        now = datetime.now(timezone.utc)
        
        if new_status == AgentStatus.ACTIVE.value:
            agent.activated_at = now
        elif new_status == AgentStatus.SUSPENDED.value:
            agent.suspended_at = now
        elif new_status == AgentStatus.RETIRED.value:
            agent.retired_at = now
        
        # Create audit log entry
        await self._create_audit_log(
            db=db,
            agent_id=agent.id,
            event_type="status_changed",
            event_description=f"Agent '{agent.agent_id}' status changed from {old_status} to {new_status}. Reason: {status_update.reason or 'Not specified'}",
            performed_by_user_id=updated_by_user_id,
            old_values={"status": old_status},
            new_values={"status": new_status, "reason": status_update.reason},
            client_ip=client_ip,
        )
        
        await db.commit()
        return agent
    
    async def search_agents(
        self,
        db: AsyncSession,
        search_request: AgentSearchRequest,
        user_id: Optional[int] = None,
        is_admin: bool = False
    ) -> Tuple[List[Agent], int]:
        """Search agents with filtering and pagination."""
        query = select(Agent).options(selectinload(Agent.owner))
        
        # Apply filters
        conditions = []
        
        if search_request.query:
            search_term = f"%{search_request.query}%"
            conditions.append(
                or_(
                    Agent.agent_id.ilike(search_term),
                    Agent.name.ilike(search_term),
                    Agent.description.ilike(search_term),
                )
            )
        
        if search_request.status:
            status_values = [s.value for s in search_request.status]
            conditions.append(Agent.status.in_(status_values))
        
        if search_request.agent_type:
            type_values = [t.value for t in search_request.agent_type]
            conditions.append(Agent.agent_type.in_(type_values))
        
        if search_request.owner_user_id:
            conditions.append(Agent.owner_user_id == search_request.owner_user_id)
        elif not is_admin and user_id:
            # Non-admin users can only see their own agents
            conditions.append(Agent.owner_user_id == user_id)
        
        if search_request.tags:
            # PostgreSQL JSON contains operator
            for tag in search_request.tags:
                conditions.append(Agent.tags.contains([tag]))
        
        if search_request.capabilities:
            for capability in search_request.capabilities:
                conditions.append(Agent.capabilities.contains([capability]))
        
        if search_request.compliance_level:
            conditions.append(Agent.compliance_level.in_(search_request.compliance_level))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting
        sort_column = getattr(Agent, search_request.sort_by, Agent.created_at)
        if search_request.sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (search_request.page - 1) * search_request.page_size
        query = query.offset(offset).limit(search_request.page_size)
        
        result = await db.execute(query)
        agents = result.scalars().all()
        
        return list(agents), total
    
    async def authenticate_agent(
        self,
        db: AsyncSession,
        agent_id: str,
        api_key: str,
        client_ip: Optional[str] = None
    ) -> Optional[Agent]:
        """Authenticate agent using API key."""
        agent = await self.get_agent(db, agent_id)
        if not agent or not agent.is_active():
            return None
        
        # Verify API key
        if not agent.api_key_hash or not verify_password(api_key, agent.api_key_hash):
            return None
        
        # Check IP whitelist if configured
        if agent.ip_whitelist and client_ip:
            if client_ip not in agent.ip_whitelist:
                return None
        
        # Update last activity
        agent.last_activity_at = datetime.now(timezone.utc)
        await db.commit()
        
        return agent
    
    def _generate_api_key(self) -> str:
        """Generate a secure API key for agent authentication."""
        return f"acgs_agent_{secrets.token_urlsafe(32)}"
    
    def _is_valid_status_transition(self, from_status: str, to_status: str) -> bool:
        """Validate if a status transition is allowed."""
        valid_transitions = {
            AgentStatus.PENDING.value: [AgentStatus.ACTIVE.value, AgentStatus.RETIRED.value],
            AgentStatus.ACTIVE.value: [AgentStatus.SUSPENDED.value, AgentStatus.RETIRED.value, AgentStatus.COMPROMISED.value],
            AgentStatus.SUSPENDED.value: [AgentStatus.ACTIVE.value, AgentStatus.RETIRED.value, AgentStatus.COMPROMISED.value],
            AgentStatus.COMPROMISED.value: [AgentStatus.RETIRED.value],
            AgentStatus.RETIRED.value: [],  # Terminal state
        }
        
        return to_status in valid_transitions.get(from_status, [])
    
    async def _create_audit_log(
        self,
        db: AsyncSession,
        agent_id: uuid.UUID,
        event_type: str,
        event_description: str,
        performed_by_user_id: Optional[int] = None,
        performed_by_system: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        client_ip: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentAuditLog:
        """Create an audit log entry for agent operations."""
        audit_log = AgentAuditLog(
            agent_id=agent_id,
            event_type=event_type,
            event_description=event_description,
            performed_by_user_id=performed_by_user_id,
            performed_by_system=performed_by_system,
            old_values=old_values,
            new_values=new_values,
            client_ip=client_ip,
            constitutional_hash=self.constitutional_hash,
            compliance_verified=True,  # Could be enhanced with actual compliance checking
            metadata=metadata,
        )
        
        db.add(audit_log)
        return audit_log
