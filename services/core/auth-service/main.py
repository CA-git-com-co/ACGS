"""
Authentication and Authorization Service
Constitutional Hash: cdd01ef066bc6cf2

FastAPI service for user authentication, authorization, and access control
across all ACGS-2 services with constitutional compliance.
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import jwt
import bcrypt
import os
import uuid
from passlib.context import CryptContext

from .models import (
    User, UserRole, Permission, Role, AuthToken, RefreshToken,
    LoginRequest, RegisterRequest, TokenResponse, UserResponse,
    PermissionCheck, RoleAssignment, SessionInfo, AuditLog,
    CONSTITUTIONAL_HASH
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
JWT_SECRET = os.getenv("JWT_SECRET", "acgs_auth_secret_key")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
security = HTTPBearer()

# Global storage
auth_storage = {
    "users": {},
    "roles": {},
    "permissions": {},
    "active_tokens": {},
    "refresh_tokens": {},
    "sessions": {},
    "audit_logs": []
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting Authentication Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Initialize default roles and permissions
    await initialize_default_permissions()
    await initialize_default_roles()
    await create_default_admin_user()
    
    # Start background tasks
    asyncio.create_task(cleanup_expired_tokens())
    asyncio.create_task(session_maintenance())
    
    yield
    
    logger.info("Shutting down Authentication Service")

app = FastAPI(
    title="Authentication Service",
    description="User authentication and authorization for ACGS-2",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def initialize_default_permissions():
    """Initialize default system permissions"""
    default_permissions = [
        Permission(
            name="system:read",
            description="Read system information",
            resource="system",
            action="read"
        ),
        Permission(
            name="system:write",
            description="Modify system configuration",
            resource="system",
            action="write"
        ),
        Permission(
            name="users:read",
            description="View user information",
            resource="users",
            action="read"
        ),
        Permission(
            name="users:write",
            description="Manage users",
            resource="users",
            action="write"
        ),
        Permission(
            name="constitutional:read",
            description="View constitutional documents",
            resource="constitutional",
            action="read"
        ),
        Permission(
            name="constitutional:write",
            description="Modify constitutional documents",
            resource="constitutional",
            action="write"
        ),
        Permission(
            name="consensus:participate",
            description="Participate in consensus decisions",
            resource="consensus",
            action="participate"
        ),
        Permission(
            name="consensus:propose",
            description="Propose consensus items",
            resource="consensus",
            action="propose"
        ),
        Permission(
            name="services:read",
            description="View service status",
            resource="services",
            action="read"
        ),
        Permission(
            name="services:manage",
            description="Manage services",
            resource="services",
            action="manage"
        ),
        Permission(
            name="audit:read",
            description="View audit logs",
            resource="audit",
            action="read"
        ),
        Permission(
            name="emergency:override",
            description="Emergency system override",
            resource="emergency",
            action="override"
        )
    ]
    
    for perm in default_permissions:
        auth_storage["permissions"][perm.permission_id] = perm
    
    logger.info(f"Initialized {len(default_permissions)} default permissions")

async def initialize_default_roles():
    """Initialize default system roles"""
    # Define role-permission mappings
    role_permissions = {
        "super_admin": [
            "system:read", "system:write", "users:read", "users:write",
            "constitutional:read", "constitutional:write", "consensus:participate",
            "consensus:propose", "services:read", "services:manage",
            "audit:read", "emergency:override"
        ],
        "admin": [
            "system:read", "users:read", "users:write", "constitutional:read",
            "consensus:participate", "consensus:propose", "services:read",
            "services:manage", "audit:read"
        ],
        "constitutional_expert": [
            "system:read", "constitutional:read", "constitutional:write",
            "consensus:participate", "consensus:propose", "audit:read"
        ],
        "operator": [
            "system:read", "services:read", "services:manage",
            "consensus:participate", "audit:read"
        ],
        "auditor": [
            "system:read", "users:read", "constitutional:read",
            "services:read", "audit:read"
        ],
        "user": [
            "system:read", "constitutional:read", "consensus:participate"
        ],
        "observer": [
            "system:read", "constitutional:read"
        ]
    }
    
    # Get permission objects
    permission_objects = {p.name: p for p in auth_storage["permissions"].values()}
    
    for role_name, perm_names in role_permissions.items():
        permissions = []
        for perm_name in perm_names:
            if perm_name in permission_objects:
                permissions.append(permission_objects[perm_name].permission_id)
        
        role = Role(
            name=role_name,
            description=f"Default {role_name.replace('_', ' ').title()} role",
            permissions=permissions,
            constitutional_level=get_constitutional_level(role_name)
        )
        
        auth_storage["roles"][role.role_id] = role
    
    logger.info(f"Initialized {len(role_permissions)} default roles")

def get_constitutional_level(role_name: str) -> int:
    """Get constitutional authority level for role"""
    levels = {
        "super_admin": 10,
        "admin": 8,
        "constitutional_expert": 9,
        "operator": 5,
        "auditor": 6,
        "user": 3,
        "observer": 1
    }
    return levels.get(role_name, 1)

async def create_default_admin_user():
    """Create default admin user if none exists"""
    admin_users = [
        user for user in auth_storage["users"].values()
        if any(role.name == "super_admin" for role in get_user_roles(user))
    ]
    
    if not admin_users:
        # Find super_admin role
        super_admin_role = None
        for role in auth_storage["roles"].values():
            if role.name == "super_admin":
                super_admin_role = role
                break
        
        if super_admin_role:
            admin_user = User(
                username="admin",
                email="admin@acgs-2.ai",
                full_name="System Administrator",
                password_hash=pwd_context.hash("admin123"),
                roles=[super_admin_role.role_id],
                constitutional_clearance=10,
                is_active=True
            )
            
            auth_storage["users"][admin_user.user_id] = admin_user
            logger.info("Created default admin user (username: admin, password: admin123)")

def get_user_roles(user: User) -> List[Role]:
    """Get role objects for user"""
    return [
        auth_storage["roles"][role_id]
        for role_id in user.roles
        if role_id in auth_storage["roles"]
    ]

async def cleanup_expired_tokens():
    """Clean up expired tokens"""
    while True:
        try:
            current_time = datetime.utcnow()
            
            # Clean up expired access tokens
            expired_tokens = [
                token_id for token_id, token in auth_storage["active_tokens"].items()
                if token.expires_at <= current_time
            ]
            
            for token_id in expired_tokens:
                del auth_storage["active_tokens"][token_id]
            
            # Clean up expired refresh tokens
            expired_refresh = [
                token_id for token_id, token in auth_storage["refresh_tokens"].items()
                if token.expires_at <= current_time
            ]
            
            for token_id in expired_refresh:
                del auth_storage["refresh_tokens"][token_id]
            
            if expired_tokens or expired_refresh:
                logger.info(f"Cleaned up {len(expired_tokens)} access tokens and {len(expired_refresh)} refresh tokens")
            
            await asyncio.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            logger.error(f"Token cleanup error: {e}")
            await asyncio.sleep(300)

async def session_maintenance():
    """Maintain active sessions"""
    while True:
        try:
            current_time = datetime.utcnow()
            
            # Clean up expired sessions
            expired_sessions = [
                session_id for session_id, session in auth_storage["sessions"].items()
                if session.expires_at <= current_time
            ]
            
            for session_id in expired_sessions:
                del auth_storage["sessions"][session_id]
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
            await asyncio.sleep(600)  # Check every 10 minutes
            
        except Exception as e:
            logger.error(f"Session maintenance error: {e}")
            await asyncio.sleep(600)

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = auth_storage["users"].get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    return user

async def check_permission(user: User, permission: str) -> bool:
    """Check if user has specific permission"""
    user_roles = get_user_roles(user)
    
    for role in user_roles:
        for perm_id in role.permissions:
            perm = auth_storage["permissions"].get(perm_id)
            if perm and perm.name == permission:
                return True
    
    return False

def require_permission(permission: str):
    """Decorator for requiring specific permission"""
    async def permission_dependency(user: User = Depends(get_current_user)):
        if not await check_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {permission} required"
            )
        return user
    return permission_dependency

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    total_users = len(auth_storage["users"])
    active_users = sum(1 for u in auth_storage["users"].values() if u.is_active)
    active_tokens = len(auth_storage["active_tokens"])
    
    return {
        "status": "healthy",
        "service": "auth-service",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.utcnow().isoformat(),
        "statistics": {
            "total_users": total_users,
            "active_users": active_users,
            "active_tokens": active_tokens,
            "total_roles": len(auth_storage["roles"]),
            "total_permissions": len(auth_storage["permissions"])
        }
    }

# Authentication endpoints
@app.post("/api/v1/auth/register", response_model=UserResponse)
async def register_user(request: RegisterRequest):
    """Register new user"""
    
    # Check if username or email already exists
    existing_user = None
    for user in auth_storage["users"].values():
        if user.username == request.username or user.email == request.email:
            existing_user = user
            break
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    
    # Find default user role
    user_role = None
    for role in auth_storage["roles"].values():
        if role.name == "user":
            user_role = role
            break
    
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default user role not found"
        )
    
    # Create new user
    new_user = User(
        username=request.username,
        email=request.email,
        full_name=request.full_name,
        password_hash=pwd_context.hash(request.password),
        roles=[user_role.role_id],
        constitutional_clearance=1,
        is_active=True
    )
    
    auth_storage["users"][new_user.user_id] = new_user
    
    # Create audit log
    audit_log = AuditLog(
        action="user_registered",
        user_id=new_user.user_id,
        details={"username": request.username, "email": request.email},
        constitutional_impact=False
    )
    auth_storage["audit_logs"].append(audit_log)
    
    logger.info(f"New user registered: {request.username}")
    
    return UserResponse(
        user_id=new_user.user_id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        roles=[role.name for role in get_user_roles(new_user)],
        constitutional_clearance=new_user.constitutional_clearance,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )

@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user and return tokens"""
    
    # Find user by username
    user = None
    for u in auth_storage["users"].values():
        if u.username == request.username:
            user = u
            break
    
    if not user or not pwd_context.verify(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
    
    # Create tokens
    token_data = {
        "sub": user.user_id,
        "username": user.username,
        "constitutional_hash": CONSTITUTIONAL_HASH
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Store tokens
    auth_token = AuthToken(
        user_id=user.user_id,
        token_hash=access_token[:32],  # Store partial hash
        expires_at=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    auth_storage["active_tokens"][auth_token.token_id] = auth_token
    
    refresh_token_obj = RefreshToken(
        user_id=user.user_id,
        token_hash=refresh_token[:32],
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    auth_storage["refresh_tokens"][refresh_token_obj.token_id] = refresh_token_obj
    
    # Create session
    session = SessionInfo(
        user_id=user.user_id,
        ip_address=request.ip_address if hasattr(request, 'ip_address') else "unknown",
        user_agent=request.user_agent if hasattr(request, 'user_agent') else "unknown",
        expires_at=datetime.utcnow() + timedelta(hours=8)
    )
    auth_storage["sessions"][session.session_id] = session
    
    # Update user last login
    user.last_login = datetime.utcnow()
    
    # Create audit log
    audit_log = AuditLog(
        action="user_login",
        user_id=user.user_id,
        details={"username": user.username},
        constitutional_impact=False
    )
    auth_storage["audit_logs"].append(audit_log)
    
    logger.info(f"User logged in: {user.username}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            roles=[role.name for role in get_user_roles(user)],
            constitutional_clearance=user.constitutional_clearance,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )

@app.post("/api/v1/auth/refresh", response_model=TokenResponse)
async def refresh_access_token(refresh_token: str):
    """Refresh access token using refresh token"""
    
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        user = auth_storage["users"].get(user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        token_data = {
            "sub": user.user_id,
            "username": user.username,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        new_access_token = create_access_token(token_data)
        
        # Store new token
        auth_token = AuthToken(
            user_id=user.user_id,
            token_hash=new_access_token[:32],
            expires_at=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        auth_storage["active_tokens"][auth_token.token_id] = auth_token
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                roles=[role.name for role in get_user_roles(user)],
                constitutional_clearance=user.constitutional_clearance,
                is_active=user.is_active,
                created_at=user.created_at
            )
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@app.post("/api/v1/auth/logout")
async def logout(user: User = Depends(get_current_user)):
    """Logout user and invalidate tokens"""
    
    # Invalidate user's tokens
    user_tokens = [
        token_id for token_id, token in auth_storage["active_tokens"].items()
        if token.user_id == user.user_id
    ]
    
    for token_id in user_tokens:
        del auth_storage["active_tokens"][token_id]
    
    # Invalidate user's sessions
    user_sessions = [
        session_id for session_id, session in auth_storage["sessions"].items()
        if session.user_id == user.user_id
    ]
    
    for session_id in user_sessions:
        del auth_storage["sessions"][session_id]
    
    # Create audit log
    audit_log = AuditLog(
        action="user_logout",
        user_id=user.user_id,
        details={"username": user.username},
        constitutional_impact=False
    )
    auth_storage["audit_logs"].append(audit_log)
    
    logger.info(f"User logged out: {user.username}")
    
    return {"message": "Successfully logged out"}

# User management endpoints
@app.get("/api/v1/users/me", response_model=UserResponse)
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        roles=[role.name for role in get_user_roles(user)],
        constitutional_clearance=user.constitutional_clearance,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login
    )

@app.get("/api/v1/users", response_model=List[UserResponse])
async def list_users(user: User = Depends(require_permission("users:read"))):
    """List all users (requires users:read permission)"""
    users = []
    for u in auth_storage["users"].values():
        users.append(UserResponse(
            user_id=u.user_id,
            username=u.username,
            email=u.email,
            full_name=u.full_name,
            roles=[role.name for role in get_user_roles(u)],
            constitutional_clearance=u.constitutional_clearance,
            is_active=u.is_active,
            created_at=u.created_at,
            last_login=u.last_login
        ))
    
    return users

@app.post("/api/v1/auth/check-permission")
async def check_user_permission(
    request: PermissionCheck,
    user: User = Depends(get_current_user)
):
    """Check if current user has specific permission"""
    has_permission = await check_permission(user, request.permission)
    
    return {
        "user_id": user.user_id,
        "permission": request.permission,
        "has_permission": has_permission,
        "constitutional_clearance": user.constitutional_clearance
    }

# Role management endpoints
@app.get("/api/v1/roles", response_model=List[Role])
async def list_roles(user: User = Depends(require_permission("users:read"))):
    """List all roles"""
    return list(auth_storage["roles"].values())

@app.get("/api/v1/permissions", response_model=List[Permission])
async def list_permissions(user: User = Depends(require_permission("users:read"))):
    """List all permissions"""
    return list(auth_storage["permissions"].values())

# Audit endpoints
@app.get("/api/v1/audit/logs", response_model=List[AuditLog])
async def get_audit_logs(
    limit: int = 100,
    user: User = Depends(require_permission("audit:read"))
):
    """Get audit logs"""
    logs = sorted(auth_storage["audit_logs"], key=lambda x: x.timestamp, reverse=True)
    return logs[:limit]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8013))
    uvicorn.run(app, host="0.0.0.0", port=port)