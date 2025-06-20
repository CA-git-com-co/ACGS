"""
ACGS Auth Service client for DGM Service.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import settings
from .models import User, UserRole, Permission

logger = logging.getLogger(__name__)


class AuthClient:
    """
    Client for ACGS Auth Service integration.
    
    Handles JWT token validation, user information retrieval,
    and permission checking with the central auth service.
    """
    
    def __init__(self):
        self.auth_service_url = settings.AUTH_SERVICE_URL
        self.timeout = httpx.Timeout(30.0)
        
        # Token cache to reduce auth service calls
        self.token_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(minutes=5)
        
        # User cache
        self.user_cache: Dict[str, User] = {}
        self.user_cache_ttl = timedelta(minutes=10)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token with ACGS Auth Service.
        
        Args:
            token: JWT token to validate
            
        Returns:
            Dict containing validation result and user info
        """
        try:
            # Check cache first
            if token in self.token_cache:
                cached_data = self.token_cache[token]
                if datetime.utcnow() - cached_data["cached_at"] < self.cache_ttl:
                    return cached_data["data"]
            
            # Validate with auth service
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.auth_service_url}/api/v1/auth/validate",
                    json={"token": token},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Cache the result
                    self.token_cache[token] = {
                        "data": result,
                        "cached_at": datetime.utcnow()
                    }
                    
                    return result
                
                elif response.status_code == 401:
                    return {"valid": False, "error": "Invalid token"}
                
                else:
                    logger.error(f"Auth service error: {response.status_code}")
                    return {"valid": False, "error": "Auth service error"}
        
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return {"valid": False, "error": str(e)}
    
    async def get_user_info(self, user_id: str) -> Optional[User]:
        """
        Get detailed user information.
        
        Args:
            user_id: User ID to lookup
            
        Returns:
            User object or None if not found
        """
        try:
            # Check cache first
            if user_id in self.user_cache:
                cached_user = self.user_cache[user_id]
                if datetime.utcnow() - cached_user.cached_at < self.user_cache_ttl:
                    return cached_user
            
            # Fetch from auth service
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.auth_service_url}/api/v1/users/{user_id}",
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    
                    # Create User object
                    user = User(
                        id=user_data["id"],
                        username=user_data["username"],
                        email=user_data.get("email"),
                        full_name=user_data.get("full_name"),
                        roles=[UserRole(name=role["name"], permissions=role.get("permissions", [])) 
                               for role in user_data.get("roles", [])],
                        permissions=[Permission(name=perm["name"], description=perm.get("description"))
                                   for perm in user_data.get("permissions", [])],
                        is_active=user_data.get("is_active", True),
                        created_at=datetime.fromisoformat(user_data.get("created_at", datetime.utcnow().isoformat())),
                        cached_at=datetime.utcnow()
                    )
                    
                    # Cache the user
                    self.user_cache[user_id] = user
                    
                    return user
                
                elif response.status_code == 404:
                    return None
                
                else:
                    logger.error(f"Failed to get user info: {response.status_code}")
                    return None
        
        except Exception as e:
            logger.error(f"Get user info failed: {e}")
            return None
    
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """
        Get user permissions list.
        
        Args:
            user_id: User ID
            
        Returns:
            List of permission names
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.auth_service_url}/api/v1/users/{user_id}/permissions",
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("permissions", [])
                
                else:
                    logger.error(f"Failed to get user permissions: {response.status_code}")
                    return []
        
        except Exception as e:
            logger.error(f"Get user permissions failed: {e}")
            return []
    
    async def check_permission(self, user_id: str, permission: str) -> bool:
        """
        Check if user has specific permission.
        
        Args:
            user_id: User ID
            permission: Permission name to check
            
        Returns:
            True if user has permission, False otherwise
        """
        try:
            permissions = await self.get_user_permissions(user_id)
            return permission in permissions
        
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False
    
    async def create_service_token(self, service_name: str, permissions: List[str]) -> Optional[str]:
        """
        Create a service-to-service authentication token.
        
        Args:
            service_name: Name of the service requesting token
            permissions: List of permissions needed
            
        Returns:
            Service token or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.auth_service_url}/api/v1/auth/service-token",
                    json={
                        "service_name": service_name,
                        "permissions": permissions
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("token")
                
                else:
                    logger.error(f"Failed to create service token: {response.status_code}")
                    return None
        
        except Exception as e:
            logger.error(f"Service token creation failed: {e}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Refresh an expired JWT token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Dict with new access and refresh tokens, or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.auth_service_url}/api/v1/auth/refresh",
                    json={"refresh_token": refresh_token},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return response.json()
                
                else:
                    logger.error(f"Token refresh failed: {response.status_code}")
                    return None
        
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None
    
    async def logout_user(self, token: str) -> bool:
        """
        Logout user and invalidate token.
        
        Args:
            token: JWT token to invalidate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.auth_service_url}/api/v1/auth/logout",
                    json={"token": token},
                    headers={"Content-Type": "application/json"}
                )
                
                # Remove from cache
                if token in self.token_cache:
                    del self.token_cache[token]
                
                return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False
    
    def clear_cache(self):
        """Clear all cached data."""
        self.token_cache.clear()
        self.user_cache.clear()
        logger.info("Auth cache cleared")
    
    async def health_check(self) -> bool:
        """Check if auth service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                response = await client.get(f"{self.auth_service_url}/health")
                return response.status_code == 200
        
        except Exception:
            return False
