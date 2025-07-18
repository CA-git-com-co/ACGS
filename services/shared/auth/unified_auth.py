#!/usr/bin/env python3

"""
ACGS-2 Unified Authentication Library
Centralized authentication and authorization for all ACGS services
Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import hmac
import base64
import asyncio
from functools import wraps
import httpx
import uuid

import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from pydantic import BaseModel, Field
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Constitutional AI Service integration
CONSTITUTIONAL_AI_SERVICE_PORT = 8001
CONSTITUTIONAL_AI_SERVICE_URL = f"http://localhost:{CONSTITUTIONAL_AI_SERVICE_PORT}"

# Logger
logger = logging.getLogger(__name__)

# Security context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class AuthError(Exception):
    """Base authentication error"""
    pass


class ConstitutionalComplianceError(AuthError):
    """Constitutional compliance violation"""
    pass


class TokenValidationError(AuthError):
    """Token validation error"""
    pass


class PermissionDeniedError(AuthError):
    """Permission denied error"""
    pass


class ConstitutionalAIServiceError(AuthError):
    """Constitutional AI Service error"""
    pass


class ConstitutionalHashRotationError(AuthError):
    """Constitutional hash rotation error"""
    pass


class Role(str, Enum):
    """User roles"""
    ADMIN = "admin"
    USER = "user"
    SERVICE = "service"
    READONLY = "readonly"


class Permission(str, Enum):
    """System permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    CONSTITUTIONAL_READ = "constitutional_read"
    CONSTITUTIONAL_WRITE = "constitutional_write"
    CONSTITUTIONAL_ADMIN = "constitutional_admin"
    GOVERNANCE_READ = "governance_read"
    GOVERNANCE_WRITE = "governance_write"
    GOVERNANCE_ADMIN = "governance_admin"
    POLICY_READ = "policy_read"
    POLICY_WRITE = "policy_write"
    POLICY_ADMIN = "policy_admin"
    VERIFICATION_READ = "verification_read"
    VERIFICATION_EXECUTE = "verification_execute"
    VERIFICATION_ADMIN = "verification_admin"
    INTEGRITY_READ = "integrity_read"
    INTEGRITY_WRITE = "integrity_write"
    INTEGRITY_ADMIN = "integrity_admin"
    COMPUTATION_READ = "computation_read"
    COMPUTATION_EXECUTE = "computation_execute"
    COMPUTATION_ADMIN = "computation_admin"


class ConstitutionalComplianceLevel(str, Enum):
    """Constitutional compliance levels"""
    STRICT = "strict"      # Requires current hash only
    FLEXIBLE = "flexible"  # Allows hash rotation
    LEGACY = "legacy"      # Allows deprecated hashes


class ConstitutionalAuditEvent(str, Enum):
    """Constitutional audit events"""
    TOKEN_CREATED = "token_created"
    TOKEN_VALIDATED = "token_validated"
    TOKEN_REJECTED = "token_rejected"
    HASH_ROTATION = "hash_rotation"
    AI_SERVICE_VALIDATION = "ai_service_validation"
    COMPLIANCE_VIOLATION = "compliance_violation"


@dataclass
class UserClaims:
    """User claims structure"""
    user_id: str
    username: str
    email: str
    roles: List[Role]
    permissions: List[Permission]
    tenant_id: Optional[str] = None
    service_id: Optional[str] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH
    constitutional_compliance_level: ConstitutionalComplianceLevel = ConstitutionalComplianceLevel.STRICT
    constitutional_audit_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    issued_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    session_id: Optional[str] = None


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # user_id
    username: str
    email: str
    roles: List[str]
    permissions: List[str]
    tenant_id: Optional[str] = None
    service_id: Optional[str] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH
    constitutional_compliance_level: str = ConstitutionalComplianceLevel.STRICT.value
    constitutional_audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    iat: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    exp: int = Field(default_factory=lambda: int((datetime.utcnow() + timedelta(hours=24)).timestamp()))
    jti: Optional[str] = None  # JWT ID for session management


class AuthConfig:
    """Authentication configuration"""
    
    def __init__(self, **kwargs):
        self.secret_key = kwargs.get('secret_key', os.getenv('JWT_SECRET_KEY', 'dev-secret-key'))
        self.algorithm = kwargs.get('algorithm', 'HS256')
        self.access_token_expire_minutes = kwargs.get('access_token_expire_minutes', 30)
        self.refresh_token_expire_days = kwargs.get('refresh_token_expire_days', 7)
        self.constitutional_hash = kwargs.get('constitutional_hash', CONSTITUTIONAL_HASH)
        self.redis_url = kwargs.get('redis_url', os.getenv('REDIS_URL', 'redis://localhost:6379'))
        self.database_url = kwargs.get('database_url', os.getenv('DATABASE_URL'))
        self.require_constitutional_compliance = kwargs.get('require_constitutional_compliance', True)
        self.constitutional_compliance_level = kwargs.get('constitutional_compliance_level', ConstitutionalComplianceLevel.STRICT)
        self.enable_constitutional_ai_service = kwargs.get('enable_constitutional_ai_service', True)
        self.constitutional_ai_service_url = kwargs.get('constitutional_ai_service_url', CONSTITUTIONAL_AI_SERVICE_URL)
        self.enable_constitutional_audit = kwargs.get('enable_constitutional_audit', True)
        self.constitutional_hash_rotation_enabled = kwargs.get('constitutional_hash_rotation_enabled', False)
        self.constitutional_legacy_hashes = kwargs.get('constitutional_legacy_hashes', [])
        self.enable_tenant_context = kwargs.get('enable_tenant_context', True)
        self.enable_session_management = kwargs.get('enable_session_management', True)
        
        # Role-based permissions mapping
        self.role_permissions = {
            Role.ADMIN: list(Permission),
            Role.USER: [
                Permission.READ, Permission.WRITE,
                Permission.CONSTITUTIONAL_READ, Permission.GOVERNANCE_READ,
                Permission.POLICY_READ, Permission.VERIFICATION_READ,
                Permission.INTEGRITY_READ, Permission.COMPUTATION_READ
            ],
            Role.SERVICE: [
                Permission.READ, Permission.WRITE,
                Permission.CONSTITUTIONAL_READ, Permission.CONSTITUTIONAL_WRITE,
                Permission.GOVERNANCE_READ, Permission.GOVERNANCE_WRITE,
                Permission.POLICY_READ, Permission.POLICY_WRITE,
                Permission.VERIFICATION_READ, Permission.VERIFICATION_EXECUTE,
                Permission.INTEGRITY_READ, Permission.INTEGRITY_WRITE,
                Permission.COMPUTATION_READ, Permission.COMPUTATION_EXECUTE
            ],
            Role.READONLY: [
                Permission.READ, Permission.CONSTITUTIONAL_READ,
                Permission.GOVERNANCE_READ, Permission.POLICY_READ,
                Permission.VERIFICATION_READ, Permission.INTEGRITY_READ,
                Permission.COMPUTATION_READ
            ]
        }


class UnifiedAuthenticator:
    """Centralized authentication for all ACGS services"""
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self._setup_redis()
        
    def _setup_redis(self):
        """Setup Redis connection for session management"""
        if self.config.enable_session_management:
            try:
                self.redis_client = redis.from_url(self.config.redis_url)
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                self.redis_client = None
                
    async def _audit_constitutional_event(self, event: ConstitutionalAuditEvent, 
                                         user_id: str, details: dict) -> None:
        """Audit constitutional compliance events"""
        if not self.config.enable_constitutional_audit:
            return
            
        try:
            audit_entry = {
                'event': event.value,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'constitutional_hash': self.config.constitutional_hash,
                'details': details
            }
            
            # Store in Redis or database
            if self.redis_client:
                audit_key = f"constitutional_audit:{uuid.uuid4()}"
                await self.redis_client.setex(
                    audit_key, 
                    timedelta(days=30), 
                    json.dumps(audit_entry)
                )
            
            # Log the event
            logger.info(f"Constitutional audit: {event.value} for user {user_id}")
            
        except Exception as e:
            logger.warning(f"Constitutional audit failed: {e}")
            
    async def _validate_with_constitutional_ai_service(self, token_payload: dict) -> bool:
        """Validate token with Constitutional AI Service"""
        if not self.config.enable_constitutional_ai_service:
            return True
            
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.post(
                    f"{self.config.constitutional_ai_service_url}/validate_token",
                    json={
                        'constitutional_hash': token_payload.get('constitutional_hash'),
                        'compliance_level': token_payload.get('constitutional_compliance_level'),
                        'audit_id': token_payload.get('constitutional_audit_id'),
                        'user_id': token_payload.get('sub')
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('is_valid', False)
                else:
                    logger.warning(f"Constitutional AI Service validation failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.warning(f"Constitutional AI Service validation error: {e}")
            # Fail safe - allow validation to continue if service is unavailable
            return True
            
    async def _validate_constitutional_hash_rotation(self, token_hash: str) -> bool:
        """Validate constitutional hash with rotation support"""
        if not self.config.constitutional_hash_rotation_enabled:
            return token_hash == self.config.constitutional_hash
            
        # Check current hash
        if token_hash == self.config.constitutional_hash:
            return True
            
        # Check legacy hashes if rotation is enabled
        if token_hash in self.config.constitutional_legacy_hashes:
            return True
            
        return False
                
    async def _validate_constitutional_compliance(self, payload: dict) -> bool:
        """Validate constitutional compliance in token with enhanced features"""
        if not self.config.require_constitutional_compliance:
            return True
            
        token_hash = payload.get('constitutional_hash')
        user_id = payload.get('sub', 'unknown')
        
        # Validate constitutional hash with rotation support
        if not await self._validate_constitutional_hash_rotation(token_hash):
            await self._audit_constitutional_event(
                ConstitutionalAuditEvent.COMPLIANCE_VIOLATION,
                user_id,
                {
                    'reason': 'invalid_constitutional_hash',
                    'expected': self.config.constitutional_hash,
                    'received': token_hash
                }
            )
            raise ConstitutionalComplianceError(
                f"Constitutional compliance violation: expected {self.config.constitutional_hash}, "
                f"got {token_hash}"
            )
            
        # Validate with Constitutional AI Service
        if not await self._validate_with_constitutional_ai_service(payload):
            await self._audit_constitutional_event(
                ConstitutionalAuditEvent.COMPLIANCE_VIOLATION,
                user_id,
                {
                    'reason': 'constitutional_ai_service_validation_failed',
                    'audit_id': payload.get('constitutional_audit_id')
                }
            )
            raise ConstitutionalComplianceError(
                "Constitutional AI Service validation failed"
            )
            
        # Audit successful validation
        await self._audit_constitutional_event(
            ConstitutionalAuditEvent.TOKEN_VALIDATED,
            user_id,
            {
                'constitutional_hash': token_hash,
                'compliance_level': payload.get('constitutional_compliance_level'),
                'audit_id': payload.get('constitutional_audit_id')
            }
        )
            
        return True
        
    async def _validate_session(self, session_id: str, user_id: str) -> bool:
        """Validate session in Redis"""
        if not self.redis_client or not session_id:
            return True  # Skip if session management disabled
            
        try:
            session_key = f"session:{session_id}"
            session_data = await self.redis_client.get(session_key)
            
            if not session_data:
                return False
                
            session_info = json.loads(session_data)
            return session_info.get('user_id') == user_id
            
        except Exception as e:
            logger.warning(f"Session validation failed: {e}")
            return False
            
    async def _store_session(self, session_id: str, user_claims: UserClaims) -> None:
        """Store session in Redis"""
        if not self.redis_client or not session_id:
            return
            
        try:
            session_key = f"session:{session_id}"
            session_data = {
                'user_id': user_claims.user_id,
                'username': user_claims.username,
                'tenant_id': user_claims.tenant_id,
                'created_at': user_claims.issued_at.isoformat(),
                'constitutional_hash': user_claims.constitutional_hash
            }
            
            await self.redis_client.setex(
                session_key,
                timedelta(hours=self.config.access_token_expire_minutes/60),
                json.dumps(session_data)
            )
            
        except Exception as e:
            logger.warning(f"Session storage failed: {e}")
            
    async def _invalidate_session(self, session_id: str) -> None:
        """Invalidate session in Redis"""
        if not self.redis_client or not session_id:
            return
            
        try:
            session_key = f"session:{session_id}"
            await self.redis_client.delete(session_key)
        except Exception as e:
            logger.warning(f"Session invalidation failed: {e}")
            
    def _generate_session_id(self, user_id: str) -> str:
        """Generate unique session ID"""
        timestamp = str(int(datetime.utcnow().timestamp()))
        data = f"{user_id}:{timestamp}:{self.config.constitutional_hash}"
        return hashlib.sha256(data.encode()).hexdigest()
        
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
        
    def create_access_token(self, user_claims: UserClaims) -> str:
        """Create JWT access token with enhanced constitutional features"""
        session_id = self._generate_session_id(user_claims.user_id)
        
        expires_at = datetime.utcnow() + timedelta(minutes=self.config.access_token_expire_minutes)
        
        payload = TokenPayload(
            sub=user_claims.user_id,
            username=user_claims.username,
            email=user_claims.email,
            roles=[role.value for role in user_claims.roles],
            permissions=[perm.value for perm in user_claims.permissions],
            tenant_id=user_claims.tenant_id,
            service_id=user_claims.service_id,
            constitutional_hash=user_claims.constitutional_hash,
            constitutional_compliance_level=user_claims.constitutional_compliance_level.value,
            constitutional_audit_id=user_claims.constitutional_audit_id,
            exp=int(expires_at.timestamp()),
            jti=session_id
        )
        
        token = jwt.encode(payload.dict(), self.config.secret_key, algorithm=self.config.algorithm)
        
        # Store session asynchronously
        asyncio.create_task(self._store_session(session_id, user_claims))
        
        # Audit token creation
        asyncio.create_task(self._audit_constitutional_event(
            ConstitutionalAuditEvent.TOKEN_CREATED,
            user_claims.user_id,
            {
                'constitutional_hash': user_claims.constitutional_hash,
                'compliance_level': user_claims.constitutional_compliance_level.value,
                'audit_id': user_claims.constitutional_audit_id,
                'session_id': session_id
            }
        ))
        
        return token
        
    def create_refresh_token(self, user_claims: UserClaims) -> str:
        """Create JWT refresh token"""
        expires_at = datetime.utcnow() + timedelta(days=self.config.refresh_token_expire_days)
        
        payload = {
            'sub': user_claims.user_id,
            'type': 'refresh',
            'constitutional_hash': user_claims.constitutional_hash,
            'exp': int(expires_at.timestamp()),
            'iat': int(datetime.utcnow().timestamp())
        }
        
        return jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)
        
    async def validate_token(self, token: str) -> UserClaims:
        """Validate JWT token and return user claims"""
        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])
            
            # Validate constitutional compliance
            await self._validate_constitutional_compliance(payload)
            
            # Validate session if enabled
            session_id = payload.get('jti')
            if session_id:
                session_valid = await self._validate_session(session_id, payload['sub'])
                if not session_valid:
                    raise TokenValidationError("Session expired or invalid")
            
            # Create user claims with enhanced constitutional features
            user_claims = UserClaims(
                user_id=payload['sub'],
                username=payload['username'],
                email=payload['email'],
                roles=[Role(role) for role in payload['roles']],
                permissions=[Permission(perm) for perm in payload['permissions']],
                tenant_id=payload.get('tenant_id'),
                service_id=payload.get('service_id'),
                constitutional_hash=payload['constitutional_hash'],
                constitutional_compliance_level=ConstitutionalComplianceLevel(
                    payload.get('constitutional_compliance_level', ConstitutionalComplianceLevel.STRICT.value)
                ),
                constitutional_audit_id=payload.get('constitutional_audit_id', str(uuid.uuid4())),
                issued_at=datetime.fromtimestamp(payload['iat']),
                expires_at=datetime.fromtimestamp(payload['exp']),
                session_id=session_id
            )
            
            return user_claims
            
        except jwt.ExpiredSignatureError:
            raise TokenValidationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise TokenValidationError(f"Invalid token: {str(e)}")
        except Exception as e:
            raise TokenValidationError(f"Token validation failed: {str(e)}")
            
    async def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(refresh_token, self.config.secret_key, algorithms=[self.config.algorithm])
            
            if payload.get('type') != 'refresh':
                raise TokenValidationError("Invalid refresh token")
                
            # Validate constitutional compliance
            await self._validate_constitutional_compliance(payload)
            
            # Here you would typically fetch user data from database
            # For now, we'll create basic user claims
            user_claims = UserClaims(
                user_id=payload['sub'],
                username=payload['sub'],  # Would be fetched from DB
                email=f"{payload['sub']}@acgs.system",  # Would be fetched from DB
                roles=[Role.USER],  # Would be fetched from DB
                permissions=self.config.role_permissions[Role.USER],
                constitutional_hash=payload['constitutional_hash']
            )
            
            return self.create_access_token(user_claims)
            
        except jwt.ExpiredSignatureError:
            raise TokenValidationError("Refresh token has expired")
        except jwt.InvalidTokenError as e:
            raise TokenValidationError(f"Invalid refresh token: {str(e)}")
            
    async def logout(self, token: str) -> None:
        """Logout user by invalidating session"""
        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])
            session_id = payload.get('jti')
            
            if session_id:
                await self._invalidate_session(session_id)
                
        except Exception as e:
            logger.warning(f"Logout failed: {e}")
            
    def check_permission(self, user_claims: UserClaims, required_permission: Permission) -> bool:
        """Check if user has required permission"""
        return required_permission in user_claims.permissions
        
    def check_role(self, user_claims: UserClaims, required_role: Role) -> bool:
        """Check if user has required role"""
        return required_role in user_claims.roles
        
    def get_tenant_context(self, user_claims: UserClaims) -> Optional[str]:
        """Get tenant context for multi-tenant operations"""
        if not self.config.enable_tenant_context:
            return None
            
        return user_claims.tenant_id
        
    def create_constitutional_user_claims(self, user_id: str, username: str, email: str, 
                                         roles: List[Role], permissions: List[Permission] = None,
                                         tenant_id: str = None, service_id: str = None,
                                         compliance_level: ConstitutionalComplianceLevel = ConstitutionalComplianceLevel.STRICT) -> UserClaims:
        """Create user claims with constitutional compliance features"""
        if permissions is None:
            permissions = []
            for role in roles:
                permissions.extend(self.config.role_permissions.get(role, []))
            permissions = list(set(permissions))  # Remove duplicates
        
        return UserClaims(
            user_id=user_id,
            username=username,
            email=email,
            roles=roles,
            permissions=permissions,
            tenant_id=tenant_id,
            service_id=service_id,
            constitutional_hash=self.config.constitutional_hash,
            constitutional_compliance_level=compliance_level,
            constitutional_audit_id=str(uuid.uuid4())
        )
        
    async def rotate_constitutional_hash(self, new_hash: str) -> None:
        """Rotate constitutional hash with proper audit trail"""
        if not self.config.constitutional_hash_rotation_enabled:
            raise ConstitutionalHashRotationError("Constitutional hash rotation is disabled")
            
        old_hash = self.config.constitutional_hash
        
        # Add old hash to legacy hashes
        if old_hash not in self.config.constitutional_legacy_hashes:
            self.config.constitutional_legacy_hashes.append(old_hash)
        
        # Update to new hash
        self.config.constitutional_hash = new_hash
        
        # Audit the rotation
        await self._audit_constitutional_event(
            ConstitutionalAuditEvent.HASH_ROTATION,
            'system',
            {
                'old_hash': old_hash,
                'new_hash': new_hash,
                'legacy_hashes': self.config.constitutional_legacy_hashes
            }
        )
        
        logger.info(f"Constitutional hash rotated from {old_hash} to {new_hash}")
        
    async def get_constitutional_audit_trail(self, user_id: str = None, 
                                           event_type: ConstitutionalAuditEvent = None) -> List[dict]:
        """Get constitutional audit trail"""
        if not self.config.enable_constitutional_audit or not self.redis_client:
            return []
            
        try:
            # This is a simplified implementation - in production you'd want proper indexing
            audit_keys = await self.redis_client.keys("constitutional_audit:*")
            audit_entries = []
            
            for key in audit_keys:
                entry_data = await self.redis_client.get(key)
                if entry_data:
                    entry = json.loads(entry_data)
                    
                    # Filter by user_id if specified
                    if user_id and entry.get('user_id') != user_id:
                        continue
                        
                    # Filter by event type if specified
                    if event_type and entry.get('event') != event_type.value:
                        continue
                        
                    audit_entries.append(entry)
            
            # Sort by timestamp
            audit_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return audit_entries
            
        except Exception as e:
            logger.warning(f"Failed to retrieve constitutional audit trail: {e}")
            return []
        
    def create_service_token(self, service_id: str, permissions: List[Permission]) -> str:
        """Create service-to-service authentication token"""
        service_claims = UserClaims(
            user_id=f"service:{service_id}",
            username=service_id,
            email=f"{service_id}@acgs.system",
            roles=[Role.SERVICE],
            permissions=permissions,
            service_id=service_id,
            constitutional_hash=self.config.constitutional_hash
        )
        
        return self.create_access_token(service_claims)


# Global authenticator instance
_authenticator: Optional[UnifiedAuthenticator] = None


def get_authenticator() -> UnifiedAuthenticator:
    """Get global authenticator instance"""
    global _authenticator
    if _authenticator is None:
        config = AuthConfig()
        _authenticator = UnifiedAuthenticator(config)
    return _authenticator


def initialize_auth(config: AuthConfig) -> UnifiedAuthenticator:
    """Initialize authentication with custom config"""
    global _authenticator
    _authenticator = UnifiedAuthenticator(config)
    return _authenticator


# FastAPI dependencies
async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> UserClaims:
    """FastAPI dependency to get current authenticated user"""
    authenticator = get_authenticator()
    try:
        return await authenticator.validate_token(credentials.credentials)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))


def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user claims from kwargs or function signature
            user_claims = None
            for arg in args:
                if isinstance(arg, UserClaims):
                    user_claims = arg
                    break
            
            if not user_claims:
                for value in kwargs.values():
                    if isinstance(value, UserClaims):
                        user_claims = value
                        break
                        
            if not user_claims:
                raise HTTPException(status_code=401, detail="Authentication required")
                
            authenticator = get_authenticator()
            if not authenticator.check_permission(user_claims, permission):
                raise HTTPException(status_code=403, detail=f"Permission '{permission.value}' required")
                
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: Role):
    """Decorator to require specific role"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user claims from kwargs or function signature
            user_claims = None
            for arg in args:
                if isinstance(arg, UserClaims):
                    user_claims = arg
                    break
            
            if not user_claims:
                for value in kwargs.values():
                    if isinstance(value, UserClaims):
                        user_claims = value
                        break
                        
            if not user_claims:
                raise HTTPException(status_code=401, detail="Authentication required")
                
            authenticator = get_authenticator()
            if not authenticator.check_role(user_claims, role):
                raise HTTPException(status_code=403, detail=f"Role '{role.value}' required")
                
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_constitutional_compliance(func):
    """Decorator to ensure constitutional compliance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract user claims from kwargs or function signature
        user_claims = None
        for arg in args:
            if isinstance(arg, UserClaims):
                user_claims = arg
                break
        
        if not user_claims:
            for value in kwargs.values():
                if isinstance(value, UserClaims):
                    user_claims = value
                    break
                    
        if not user_claims:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        if user_claims.constitutional_hash != CONSTITUTIONAL_HASH:
            raise HTTPException(status_code=403, detail="Constitutional compliance violation")
            
        return await func(*args, **kwargs)
    return wrapper


# Middleware for constitutional compliance
class ConstitutionalComplianceMiddleware:
    """Middleware to ensure constitutional compliance on all requests"""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Add constitutional hash to response headers
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.append([b"X-Constitutional-Hash", CONSTITUTIONAL_HASH.encode()])
                    message["headers"] = headers
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


# Utility functions
def create_admin_user(username: str, password: str, email: str) -> UserClaims:
    """Create admin user claims"""
    return UserClaims(
        user_id=f"admin:{username}",
        username=username,
        email=email,
        roles=[Role.ADMIN],
        permissions=list(Permission),
        constitutional_hash=CONSTITUTIONAL_HASH
    )


def create_service_user(service_id: str, permissions: List[Permission]) -> UserClaims:
    """Create service user claims"""
    return UserClaims(
        user_id=f"service:{service_id}",
        username=service_id,
        email=f"{service_id}@acgs.system",
        roles=[Role.SERVICE],
        permissions=permissions,
        service_id=service_id,
        constitutional_hash=CONSTITUTIONAL_HASH
    )


# Export main components
__all__ = [
    'UnifiedAuthenticator',
    'AuthConfig',
    'UserClaims',
    'Role',
    'Permission',
    'AuthError',
    'ConstitutionalComplianceError',
    'TokenValidationError',
    'PermissionDeniedError',
    'get_authenticator',
    'initialize_auth',
    'get_current_user',
    'require_permission',
    'require_role',
    'require_constitutional_compliance',
    'ConstitutionalComplianceMiddleware',
    'create_admin_user',
    'create_service_user',
    'CONSTITUTIONAL_HASH'
]