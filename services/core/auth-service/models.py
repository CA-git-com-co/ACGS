"""
Authentication Service Models
Constitutional Hash: cdd01ef066bc6cf2

Data models for user authentication, authorization, and access control.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
import uuid

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class UserRole(str, Enum):
    """User roles in the system"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    CONSTITUTIONAL_EXPERT = "constitutional_expert"
    OPERATOR = "operator"
    AUDITOR = "auditor"
    USER = "user"
    OBSERVER = "observer"

class Permission(BaseModel):
    """System permission"""
    permission_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    resource: str
    action: str
    constitutional_level: int = Field(ge=0, le=10, default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Role(BaseModel):
    """User role with permissions"""
    role_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    permissions: List[str] = []  # Permission IDs
    constitutional_level: int = Field(ge=0, le=10, default=1)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class User(BaseModel):
    """System user"""
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    full_name: str
    password_hash: str
    roles: List[str] = []  # Role IDs
    constitutional_clearance: int = Field(ge=0, le=10, default=1)
    is_active: bool = True
    is_verified: bool = False
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    last_login: Optional[datetime] = None
    last_password_change: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = CONSTITUTIONAL_HASH

class AuthToken(BaseModel):
    """Authentication token"""
    token_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    token_hash: str
    token_type: str = "bearer"
    expires_at: datetime
    revoked: bool = False
    revoked_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RefreshToken(BaseModel):
    """Refresh token for renewing access tokens"""
    token_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    token_hash: str
    expires_at: datetime
    revoked: bool = False
    revoked_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SessionInfo(BaseModel):
    """User session information"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    ip_address: str
    user_agent: str
    expires_at: datetime
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AuditLog(BaseModel):
    """Audit log entry"""
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str
    user_id: Optional[str] = None
    resource: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    constitutional_impact: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Request/Response Models
class LoginRequest(BaseModel):
    """Login request"""
    username: str
    password: str
    remember_me: bool = False

class RegisterRequest(BaseModel):
    """User registration request"""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=128)

class UserResponse(BaseModel):
    """User response model"""
    user_id: str
    username: str
    email: str
    full_name: str
    roles: List[str]
    constitutional_clearance: int
    is_active: bool
    is_verified: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime

class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse

class PermissionCheck(BaseModel):
    """Permission check request"""
    permission: str
    resource: Optional[str] = None

class RoleAssignment(BaseModel):
    """Role assignment request"""
    user_id: str
    role_ids: List[str]

class PasswordChangeRequest(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)

class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(min_length=8, max_length=128)

class UserUpdateRequest(BaseModel):
    """User update request"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    constitutional_clearance: Optional[int] = Field(None, ge=0, le=10)

class RoleCreateRequest(BaseModel):
    """Role creation request"""
    name: str = Field(min_length=2, max_length=50)
    description: str
    permissions: List[str] = []
    constitutional_level: int = Field(ge=0, le=10, default=1)

class PermissionCreateRequest(BaseModel):
    """Permission creation request"""
    name: str = Field(min_length=2, max_length=100)
    description: str
    resource: str
    action: str
    constitutional_level: int = Field(ge=0, le=10, default=1)