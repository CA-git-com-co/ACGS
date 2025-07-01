"""
Agent Authentication Middleware

Middleware for authenticating autonomous agents across ACGS services.
Integrates with the agent identity management system.
"""

import logging
import os
from typing import Optional, Dict, Any, Callable
from datetime import datetime

import redis.asyncio as aioredis

import httpx
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.agent import Agent
from ..services.agent_service import AgentService

logger = logging.getLogger(__name__)

class AgentAuthenticationMiddleware:
    """
    Middleware for authenticating agents across ACGS services.
    
    Provides:
    - API key validation
    - Agent identity verification
    - IP whitelist checking
    - Rate limiting enforcement
    - Session management
    """
    
    def __init__(self, auth_service_url: str = "http://localhost:8006", redis_url: Optional[str] = None):
        self.auth_service_url = auth_service_url
        self.agent_service = AgentService()
        self.http_client = httpx.AsyncClient(timeout=10.0)
        self.security = HTTPBearer(auto_error=False)
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client: aioredis.Redis | None = None
    
    async def authenticate_agent(
        self, 
        request: Request,
        db: AsyncSession,
        require_active: bool = True
    ) -> Optional[Agent]:
        """
        Authenticate an agent from the request.
        
        Returns:
            Agent object if authentication successful, None otherwise
        """
        try:
            # Extract credentials
            credentials = await self._extract_credentials(request)
            if not credentials:
                return None
            
            agent_id = credentials.get("agent_id")
            api_key = credentials.get("api_key")
            
            if not agent_id or not api_key:
                logger.warning("Missing agent_id or api_key in request")
                return None
            
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Authenticate agent
            agent = await self.agent_service.authenticate_agent(
                db=db,
                agent_id=agent_id,
                api_key=api_key,
                client_ip=client_ip
            )
            
            if not agent:
                logger.warning(f"Authentication failed for agent {agent_id}")
                return None
            
            if require_active and not agent.is_active():
                logger.warning(f"Inactive agent attempted access: {agent_id}")
                return None
            
            # Check rate limits
            if not await self._check_rate_limits(agent, request):
                logger.warning(f"Rate limit exceeded for agent {agent_id}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            # Log successful authentication
            logger.info(f"Agent {agent_id} authenticated successfully")
            
            # Store agent in request state for use in endpoints
            request.state.agent = agent
            request.state.authenticated_via = "agent_api_key"
            
            return agent
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Agent authentication error: {e}")
            return None
    
    async def require_agent_authentication(
        self, 
        request: Request, 
        db: AsyncSession
    ) -> Agent:
        """
        Require agent authentication, raise HTTPException if failed.
        
        Returns:
            Authenticated Agent object
        """
        agent = await self.authenticate_agent(request, db)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Agent authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return agent
    
    async def require_agent_permissions(
        self,
        request: Request,
        db: AsyncSession,
        required_permissions: list[str]
    ) -> Agent:
        """
        Require agent authentication with specific permissions.
        
        Args:
            required_permissions: List of permission strings required
            
        Returns:
            Authenticated Agent object with required permissions
        """
        agent = await self.require_agent_authentication(request, db)
        
        # Check if agent has required permissions
        agent_permissions = agent.permissions or []
        missing_permissions = set(required_permissions) - set(agent_permissions)
        
        if missing_permissions:
            logger.warning(
                f"Agent {agent.agent_id} missing permissions: {missing_permissions}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(missing_permissions)}"
            )
        
        return agent
    
    async def require_operation_authorization(
        self,
        request: Request,
        db: AsyncSession,
        operation_type: str,
        operation_context: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """
        Require agent authentication and operation-specific authorization.
        
        This integrates with the HITL system for operation approval.
        """
        agent = await self.require_agent_authentication(request, db)
        
        # Check if operation is allowed for this agent
        allowed_operations = agent.allowed_operations or []
        if operation_type not in allowed_operations and "*" not in allowed_operations:
            logger.warning(
                f"Agent {agent.agent_id} not authorized for operation: {operation_type}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation '{operation_type}' not authorized for this agent"
            )
        
        # For high-risk operations, integrate with HITL service
        if operation_context and self._is_high_risk_operation(operation_type, operation_context):
            await self._request_hitl_approval(agent, operation_type, operation_context)
        
        return agent
    
    async def _extract_credentials(self, request: Request) -> Optional[Dict[str, str]]:
        """Extract agent credentials from request."""
        credentials = {}
        
        # Try Authorization header first (Bearer token)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            credentials["api_key"] = auth_header[7:]  # Remove "Bearer "
        
        # Try X-API-Key header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            credentials["api_key"] = api_key
        
        # Try X-Agent-ID header
        agent_id = request.headers.get("X-Agent-ID")
        if agent_id:
            credentials["agent_id"] = agent_id
        
        # If no agent_id in headers, try to extract from API key
        if "api_key" in credentials and "agent_id" not in credentials:
            # API keys are in format: acgs_agent_{random_string}
            # Agent ID might be passed separately or embedded
            pass
        
        return credentials if credentials else None
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Get client IP address from request."""
        # Check X-Forwarded-For header first (for proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection IP
        return request.client.host if request.client else None

    async def _get_redis(self) -> aioredis.Redis:
        """Lazily initialize and return Redis client."""
        if not self.redis_client:
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            try:
                await self.redis_client.ping()
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                self.redis_client = None
                raise
        return self.redis_client
    
    async def _check_rate_limits(self, agent: Agent, request: Request) -> bool:
        """Check if agent is within rate limits using Redis counters."""
        max_requests = agent.max_requests_per_minute or 100

        try:
            redis = await self._get_redis()
        except Exception:
            # If Redis is unavailable fail open
            return True

        key = f"agent_rl:{agent.agent_id}"
        try:
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, 60)
            return count <= max_requests
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True
    
    def _is_high_risk_operation(
        self, operation_type: str, operation_context: Dict[str, Any]
    ) -> bool:
        """Determine if operation requires HITL approval."""
        high_risk_operations = {
            "code_execution",
            "code_modification", 
            "policy_update",
            "system_command",
            "database_modification",
            "production_deployment"
        }
        
        if operation_type in high_risk_operations:
            return True
        
        # Check context for risk indicators
        if operation_context:
            if operation_context.get("affects_production", False):
                return True
            if operation_context.get("irreversible", False):
                return True
            if operation_context.get("affects_multiple_services", False):
                return True
        
        return False
    
    async def _request_hitl_approval(
        self,
        agent: Agent,
        operation_type: str,
        operation_context: Dict[str, Any]
    ) -> None:
        """Request HITL approval for high-risk operation."""
        try:
            # Call Agent HITL service for evaluation
            response = await self.http_client.post(
                "http://localhost:8008/api/v1/reviews/evaluate",
                json={
                    "agent_id": agent.agent_id,
                    "agent_type": agent.agent_type,
                    "operation_type": operation_type,
                    "operation_description": f"High-risk operation: {operation_type}",
                    "operation_context": operation_context,
                },
                timeout=30.0
            )
            
            if response.status_code == 201:
                result = response.json()
                
                # If not auto-approved, block the operation
                if result["status"] != "auto_approved":
                    raise HTTPException(
                        status_code=status.HTTP_202_ACCEPTED,
                        detail={
                            "message": "Operation requires human approval",
                            "review_id": result["review_id"],
                            "escalation_level": result["escalation_level"],
                            "status": result["status"]
                        }
                    )
            else:
                logger.error(f"HITL service error: {response.status_code}")
                # Fail safe - require manual approval
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Human oversight service unavailable - operation blocked"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"HITL approval request failed: {e}")
            # Fail safe - block operation
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to verify operation safety - operation blocked"
            )
    
    async def close(self):
        """Clean up resources."""
        await self.http_client.aclose()
        if self.redis_client:
            await self.redis_client.close()


# FastAPI dependency functions
agent_auth = AgentAuthenticationMiddleware()

async def get_current_agent(request: Request, db: AsyncSession) -> Agent:
    """FastAPI dependency to get current authenticated agent."""
    return await agent_auth.require_agent_authentication(request, db)

async def require_agent_perms(permissions: list[str]):
    """FastAPI dependency factory for requiring specific agent permissions."""
    async def dependency(request: Request, db: AsyncSession) -> Agent:
        return await agent_auth.require_agent_permissions(request, db, permissions)
    return dependency

async def require_operation_auth(operation_type: str, operation_context: Optional[Dict[str, Any]] = None):
    """FastAPI dependency factory for operation-specific authorization."""
    async def dependency(request: Request, db: AsyncSession) -> Agent:
        return await agent_auth.require_operation_authorization(
            request, db, operation_type, operation_context
        )
    return dependency