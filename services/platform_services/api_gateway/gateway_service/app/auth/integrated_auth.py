"""
Integrated Authentication Module for API Gateway
Constitutional Hash: cdd01ef066bc6cf2

This module provides direct authentication capabilities within the API Gateway,
reducing the need for a separate authentication service for most operations.
"""

import asyncio
import hashlib
import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import bcrypt
import jwt
from fastapi import HTTPException, Request, status
from pydantic import BaseModel

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TokenData(BaseModel):
    """Token data model."""
    user_id: str
    username: str
    tenant_id: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    exp: int
    iat: int
    constitutional_hash: str


class UserCredentials(BaseModel):
    """User credentials model."""
    username: str
    password: str
    tenant_id: Optional[str] = None


class AuthenticationResult(BaseModel):
    """Authentication result model."""
    success: bool
    access_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = 3600
    user_id: Optional[str] = None
    username: Optional[str] = None
    tenant_id: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    constitutional_hash: str = CONSTITUTIONAL_HASH
    error: Optional[str] = None


class IntegratedAuthManager:
    """
    Integrated authentication manager that provides core auth functionality
    directly within the API Gateway, reducing dependency on external auth service.
    """
    
    def __init__(self):
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "acgs-gateway-secret-key-2024")
        self.jwt_algorithm = "HS256"
        self.token_expire_minutes = 60
        self.refresh_token_expire_days = 30
        
        # In-memory user store for demo (replace with database in production)
        self.users_db = {
            "admin": {
                "user_id": "admin_001",
                "username": "admin",
                "password_hash": self._hash_password("admin123"),
                "tenant_id": "system",
                "roles": ["admin", "user"],
                "permissions": ["read", "write", "admin", "constitutional_access"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            "user": {
                "user_id": "user_001",
                "username": "user",
                "password_hash": self._hash_password("user123"),
                "tenant_id": "default",
                "roles": ["user"],
                "permissions": ["read"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            "constitutional_expert": {
                "user_id": "const_001",
                "username": "constitutional_expert",
                "password_hash": self._hash_password("const123"),
                "tenant_id": "system",
                "roles": ["constitutional_expert", "user"],
                "permissions": ["read", "write", "constitutional_review", "policy_synthesis"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        # Token blacklist for logout functionality
        self.token_blacklist = set()
        
        # Rate limiting for authentication attempts
        self.auth_attempts = {}
        self.max_attempts = 5
        self.lockout_duration = 300  # 5 minutes
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            return False
    
    def _check_rate_limit(self, identifier: str) -> bool:
        """Check if authentication rate limit is exceeded."""
        current_time = time.time()
        
        if identifier not in self.auth_attempts:
            self.auth_attempts[identifier] = []
        
        # Clean old attempts
        self.auth_attempts[identifier] = [
            attempt_time for attempt_time in self.auth_attempts[identifier]
            if current_time - attempt_time < self.lockout_duration
        ]
        
        # Check if rate limit exceeded
        if len(self.auth_attempts[identifier]) >= self.max_attempts:
            return False
        
        # Record this attempt
        self.auth_attempts[identifier].append(current_time)
        return True
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=self.token_expire_minutes)
        
        payload = {
            "user_id": user_data["user_id"],
            "username": user_data["username"],
            "tenant_id": user_data.get("tenant_id"),
            "roles": user_data.get("roles", []),
            "permissions": user_data.get("permissions", []),
            "exp": int(expires.timestamp()),
            "iat": int(now.timestamp()),
            "jti": secrets.token_urlsafe(32),  # JWT ID for revocation
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token."""
        try:
            # Check if token is blacklisted
            if token in self.token_blacklist:
                return None
            
            # Decode token
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Verify constitutional hash
            if payload.get("constitutional_hash") != CONSTITUTIONAL_HASH:
                return None
            
            # Check expiration
            if datetime.fromtimestamp(payload["exp"], timezone.utc) < datetime.now(timezone.utc):
                return None
            
            return TokenData(**payload)
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None
    
    async def authenticate_user(self, credentials: UserCredentials) -> AuthenticationResult:
        """Authenticate user with username/password."""
        try:
            # Rate limiting check
            rate_limit_key = f"{credentials.username}:{getattr(credentials, 'tenant_id', 'default')}"
            if not self._check_rate_limit(rate_limit_key):
                return AuthenticationResult(
                    success=False,
                    error="Too many authentication attempts. Please try again later."
                )
            
            # Find user
            user = self.users_db.get(credentials.username)
            if not user:
                return AuthenticationResult(
                    success=False,
                    error="Invalid username or password"
                )
            
            # Check if user is active
            if not user.get("is_active", False):
                return AuthenticationResult(
                    success=False,
                    error="User account is disabled"
                )
            
            # Verify password
            if not self._verify_password(credentials.password, user["password_hash"]):
                return AuthenticationResult(
                    success=False,
                    error="Invalid username or password"
                )
            
            # Check tenant access (if specified)
            if credentials.tenant_id and user.get("tenant_id") != credentials.tenant_id:
                return AuthenticationResult(
                    success=False,
                    error="Access denied for specified tenant"
                )
            
            # Create access token
            access_token = self.create_access_token(user)
            
            return AuthenticationResult(
                success=True,
                access_token=access_token,
                token_type="bearer",
                expires_in=self.token_expire_minutes * 60,
                user_id=user["user_id"],
                username=user["username"],
                tenant_id=user.get("tenant_id"),
                roles=user.get("roles", []),
                permissions=user.get("permissions", []),
                constitutional_hash=CONSTITUTIONAL_HASH
            )
            
        except Exception as e:
            return AuthenticationResult(
                success=False,
                error=f"Authentication failed: {str(e)}"
            )
    
    async def validate_request_auth(self, request: Request) -> Optional[TokenData]:
        """Validate authentication for incoming request."""
        try:
            # Get Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return None
            
            # Extract token
            if not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header[7:]  # Remove "Bearer " prefix
            
            # Verify token
            token_data = self.verify_token(token)
            if not token_data:
                return None
            
            # Additional security checks
            user = self.users_db.get(token_data.username)
            if not user or not user.get("is_active", False):
                return None
            
            return token_data
            
        except Exception:
            return None
    
    async def logout_user(self, token: str) -> bool:
        """Logout user by blacklisting token."""
        try:
            # Verify token first
            token_data = self.verify_token(token)
            if not token_data:
                return False
            
            # Add to blacklist
            self.token_blacklist.add(token)
            
            # Clean up old blacklisted tokens periodically
            await self._cleanup_blacklist()
            
            return True
            
        except Exception:
            return False
    
    async def _cleanup_blacklist(self):
        """Clean up expired tokens from blacklist."""
        try:
            current_time = datetime.now(timezone.utc)
            tokens_to_remove = []
            
            for token in self.token_blacklist:
                try:
                    payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm], options={"verify_exp": False})
                    exp_time = datetime.fromtimestamp(payload["exp"], timezone.utc)
                    if exp_time < current_time:
                        tokens_to_remove.append(token)
                except Exception:
                    # If we can't decode it, remove it
                    tokens_to_remove.append(token)
            
            for token in tokens_to_remove:
                self.token_blacklist.discard(token)
                
        except Exception:
            pass  # Cleanup is best effort
    
    def check_permission(self, token_data: TokenData, required_permission: str) -> bool:
        """Check if user has required permission."""
        return required_permission in token_data.permissions or "admin" in token_data.roles
    
    def check_role(self, token_data: TokenData, required_role: str) -> bool:
        """Check if user has required role."""
        return required_role in token_data.roles
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information by ID."""
        for user in self.users_db.values():
            if user["user_id"] == user_id:
                # Return user info without sensitive data
                return {
                    "user_id": user["user_id"],
                    "username": user["username"],
                    "tenant_id": user.get("tenant_id"),
                    "roles": user.get("roles", []),
                    "permissions": user.get("permissions", []),
                    "is_active": user.get("is_active", False),
                    "created_at": user.get("created_at"),
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }
        return None
    
    async def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user (admin only)."""
        try:
            username = user_data["username"]
            if username in self.users_db:
                return False
            
            self.users_db[username] = {
                "user_id": f"user_{int(time.time())}",
                "username": username,
                "password_hash": self._hash_password(user_data["password"]),
                "tenant_id": user_data.get("tenant_id", "default"),
                "roles": user_data.get("roles", ["user"]),
                "permissions": user_data.get("permissions", ["read"]),
                "is_active": user_data.get("is_active", True),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            return True
            
        except Exception:
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for authentication module."""
        return {
            "healthy": True,
            "users_count": len(self.users_db),
            "blacklisted_tokens": len(self.token_blacklist),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Global instance
auth_manager = IntegratedAuthManager()


def get_auth_manager() -> IntegratedAuthManager:
    """Get the authentication manager instance."""
    return auth_manager